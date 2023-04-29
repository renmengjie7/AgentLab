"""
@author: Guo Shiguang
@software: PyCharm
@file: experiment.py
@time: 2023/4/18 16:32
"""
import copy
import json
import os
from typing import List

from AISimuToolKit.exp.agents.Courier import Courier
from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.model.register import get_model_apis
from AISimuToolKit.store.logger import Logger
from AISimuToolKit.utils.utils import generate_experiment_id, get_fromat_len, parse_yaml_config, save_config


class Experiment:
    def __init__(self, id: str, path: str, agents: List[Agent], config: dict, attenuation_coe: float = 0.7):
        self.id = id
        self.path = path
        self.agents = agents
        # config passed in by the user
        self.config = config
        self.logger = Logger()
        # continuous speak needs a attenuation coefficient
        self.attenuation_coe = 0.7
        self.continuous_count = {i: 0 for i in range(0, len(agents))}

    def get_agent_ids(self):
        return [agent.agent_id for agent in self.agents]

    @classmethod
    def load(cls,
             config: str,
             model_config: str,
             output_dir: str = "experiments",
             custom_class: dict = None) -> "Experiment":
        """_summary_ Load and instantiate an experiment from a json configuration file

        Args:
            config (str): _description_  The configuration file for the experiment
            model_config (str): _description_ Configure the url for each model
            output_dir (str): _description_  Storage location for logs and history

        Returns:
            _type_: _description_
        """
        # Use the timestamp directly as the experiment ID 
        # no need to checking if the id is duplicate
        exp_id = generate_experiment_id()
        exp_path = Experiment.mk_exp_dir(output_dir, exp_id)
        with open(config, 'r') as file:
            expe_config = json.load(file)
        agents = Experiment.load_agents(agent_list=expe_config['agent_list'], exp_id=exp_id, exp_path=exp_path,
                                        model_config=model_config, expe_settings=expe_config["experiment_settings"],
                                        custom_class=custom_class)
        Courier(agents=agents)
        exp = Experiment(id=exp_id,
                         path=exp_path,
                         agents=agents,
                         attenuation_coe=expe_config["experiment_settings"].get("attenuation_coe", 0.7),
                         config=expe_config)
        save_config(config=expe_config, path=f'{exp.path}/init_config.json')
        return exp

    def get_role_list(self):
        role_list = set()  # TODO team...
        for agent in self.agents:
            role_list.add(agent.role)
        return list(role_list)

    @staticmethod
    def load_agents(agent_list: List[dict],
                    exp_path: str, exp_id: str,
                    model_config: str, expe_settings: dict, custom_class: dict = None) -> List[Agent]:
        configs = copy.deepcopy(agent_list)
        agents_num = len(configs)
        format_num_len = get_fromat_len(num=agents_num)
        models = get_model_apis(exp_id=exp_id,
                                agents=[i + 1 for i in range(agents_num)],
                                model_names=[config['model_settings']['model_name']
                                             for config in configs],
                                model_config=model_config)
        agents = []
        model_config = parse_yaml_config(model_config)

        Agent_class = Agent
        if custom_class is not None:
            Agent_class = custom_class.get("agent", Agent)

        for idx, config in enumerate(configs):
            if "extra_columns" not in config["misc"]:
                config["misc"]["extra_columns"] = expe_settings.get("extermal_memory_cols", [])
            agents.append(Agent_class.load(
                format_num_len=format_num_len,
                config=config,
                model=models[idx],
                exp_path=exp_path,
                exp_id=exp_id
            ))
        return agents

    @staticmethod
    def mk_exp_dir(output_dir: str, exp_id: str) -> str:
        """"
        Experiment related directory creation
        :return exp root dir 
        """
        exp_path = os.path.join(output_dir, exp_id)
        os.makedirs(exp_path, exist_ok=True)

        # Instantiate a logger to control file location
        logger = Logger(log_file=os.path.join(exp_path, "log.txt"),
                        history_file=os.path.join(exp_path, "history.txt"))
        return exp_path

    def probe(self, agent: Agent, content: str, prompt: str = "{}'s profile is: {}.\n{}"):
        """probe an agent"""
        return agent.probed(content=content, prompt=prompt)

    def choose_next_one(self,
                        message=str,
                        agents_idx: List[int] = None,
                        prompt: str = "{}'s profile is: {}.\n{}") -> int:
        """
        TODO cue a person directly and that person's score will be higher
        In a list of scenarios, only one can be selected to take some action
        """
        agents_idx = [i for i in range(0, len(self.agents))] if agents_idx is None else agents_idx
        agents = [self.agents[i] for i in agents_idx]
        max_score = 0
        max_idx = 0
        for idx, agent in enumerate(agents):
            answer = self.probe(agent=agent, content=message, prompt=prompt)
            try:
                answer = int(answer)
                self.logger.info(f"agent_{idx + 1} score is {answer}")
                answer *= (self.attenuation_coe ** self.continuous_count[idx])
                self.logger.info(f"agent_{idx + 1} score is {answer} after attenuation")
            except ValueError as e:
                self.logger.error(f"Failed to convert '{answer}' to an integer: {e}")
                continue
            if max_score <= answer:
                max_idx = idx
                max_score = answer
        for i in agents_idx:
            if i == max_idx:
                self.continuous_count[i] += 1
            else:
                self.continuous_count[i] = 0
        return max_idx

    def inject_background(self, message: str, prompt: str = "{} {}"):
        """_summary_ 

        Args:
            message (str): _description_
            prompt (str, optional): _description_. Defaults to "{} {}". first is name, second is message
        """
        for agent in self.agents:
            agent.recieve_info(prompt.format(agent.name, message))
