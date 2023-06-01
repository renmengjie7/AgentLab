"""
@author: Guo Shiguang
@software: PyCharm
@file: experiment.py
@time: 2023/4/18 16:32
"""
import json
import os
from typing import List, Union

from AISimuToolKit.exp.agents.Courier import Courier
from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.agents.agent_collection import AgentCollection

from AISimuToolKit.model.register import get_model_apis
from AISimuToolKit.store.logger import Logger
from AISimuToolKit.utils.utils import generate_experiment_id, get_fromat_len, save_config

from AISimuToolKit.exp.scheduler.bidding import BiddingSchedular
from AISimuToolKit.exp.scheduler.demand import DemandScheduler
from AISimuToolKit.exp.scheduler.random import RandomScheduler
from AISimuToolKit.exp.scheduler.sequential import SequentialScheduler


Scheduler_dict = {
    "random": RandomScheduler,
    "sequential": SequentialScheduler,
    "bidding": BiddingSchedular,
    "demand": DemandScheduler
}


class Experiment:
    def __init__(self, exp_id: str, path: str, agents: List[Agent], config: dict):
        self.id = exp_id
        self.path = path
        self.agents = AgentCollection(agents)
        self.scheduler = Scheduler_dict.get(config["experiment_settings"].get("scheduler"), None)
        if self.scheduler is not None:
            self.scheduler = self.scheduler(self.agents, config["experiment_settings"])
        # agent_config passed in by the user
        self.config = config
        self.logger = Logger()

    @classmethod
    def load(cls,
             config: str,
             model_config: str,
             output_dir: str = "experiments",
             custom_class: dict = None) -> "Experiment":
        """
        Load and instantiate an experiment from a json configuration file
        :param config: The configuration file for the experiment
        :param model_config: Configure the url for each model
        :param output_dir: Storage location for logs and history
        :param custom_class:
        :return:
        """

        # Use the timestamp as the experiment ID directly
        # no need to check whether the id is duplicated
        exp_id = generate_experiment_id()
        exp_path = os.path.join(output_dir, exp_id)
        os.makedirs(exp_path, exist_ok=True)

        Logger(log_file=os.path.join(exp_path, "log.txt"), history_file=os.path.join(exp_path, "history.txt"))
        with open(config, 'r') as file:
            exp_config = json.load(file)
        agents = Experiment.load_agents(exp_config=exp_config,
                                        exp_id=exp_id,
                                        exp_path=exp_path,
                                        model_config=model_config,
                                        custom_class=custom_class)
        Courier(agents=agents)
        exp = Experiment(exp_id=exp_id,
                         path=exp_path,
                         agents=agents,
                         config=exp_config)
        save_config(config=exp_config, path=f'{exp.path}/init_config.json')
        return exp

    @staticmethod
    def load_agents(exp_config: dict, exp_path: str, exp_id: str,
                    model_config: str, custom_class: dict = None) -> List[Agent]:
        agent_list = exp_config["agent_list"]
        exp_settings = exp_config["experiment_settings"]
        agents_num = len(agent_list)
        format_num_len = get_fromat_len(num=agents_num)
        models = get_model_apis(exp_id=exp_id,
                                agents=[i + 1 for i in range(agents_num)],
                                model_names=[config['model_settings']['model_name'] for config in agent_list],
                                model_config=model_config)
        agents = []

        agent_class = Agent
        if custom_class is not None:
            agent_class = custom_class.get("agent", Agent)

        for idx, agent_config in enumerate(agent_list):
            for key, value in exp_settings["global_agent_settings"].items():
                if key not in agent_config["specific_agent_settings"]:
                    agent_config["specific_agent_settings"][key] = value
            agents.append(agent_class.load(
                format_num_len=format_num_len,
                agent_config=agent_config,
                model=models[idx],
                exp_path=exp_path,
                exp_id=exp_id,
            ))
        return agents

    def inject_background(self, message: str, groups: Union[List[str], str] = None):
        """
        Inject background information into the agent
        :param message: message to be injected
        :param groups: groups can be a list of group names or a single group name
        :return:
        """
        if groups is None:
            groups = "all"
        if isinstance(groups, str):
            groups = [groups]
        for group in groups:
            for agent in self.agents.get_group_by_group_name(group).all():
                agent.save(message=message)
