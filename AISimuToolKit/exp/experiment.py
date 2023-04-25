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

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.model.register import get_model_apis
from AISimuToolKit.store.logger import Logger
from AISimuToolKit.utils.utils import generate_experiment_id, get_fromat_len, parse_yaml_config, save_config


class Experiment:
    def __init__(self, id: str, path: str, agents: List[Agent], config: dict):
        self.id = id
        self.path = path
        self.agents = agents
        # self.models = models
        # 用户传入的config
        self.config = config

    def get_agent_ids(self):
        return [agent.agent_id for agent in self.agents]

    @classmethod
    def load(cls,
             config: str,
             model_config: str,
             output_dir: str = "experiments",
             custom_class: dict = None) -> "Experiment":
        """_summary_ 从json配置文件中加载并示例化一个experiment

        Args:
            config (str): _description_  实验的配置文件 
            model_config (str): _description_ 配置每个模型对应的url
            output_dir (str): _description_  日志、历史等存储位置

        Returns:
            _type_: _description_
        """
        # 直接使用时间戳做实验ID, 应该不需要检查id是否重复
        exp_id = generate_experiment_id()
        exp_path = Experiment.mk_exp_dir(output_dir, exp_id)
        with open(config, 'r') as file:
            expe_config = json.load(file)
        agents = Experiment.load_agents(agent_list=expe_config['agent_list'], exp_id=exp_id, exp_path=exp_path,
                                        model_config=model_config, expe_settings=expe_config["experiment_settings"],
                                        custom_class=custom_class)
        exp = Experiment(id=exp_id,
                         path=exp_path,
                         agents=agents,
                         config=expe_config)
        save_config(config=expe_config, path=f'{exp.path}/init_config.json')
        return exp

    @staticmethod
    def preprocess_agent(json_data: dict, exp_path: str):
        """_summary_ 对智能体的处理、目录、配置文件的创建

        Args:
            json_data (dict): _description_ 待处理的json
            exp_path (str): _description_ 实验根目录

        Returns:
            _type_: _description_
        """
        agent_list = copy.deepcopy(json_data["agent_list"])
        agents_num = len(agent_list)
        format_num_len = get_fromat_len(num=agents_num)

        agent_model_dict = dict()
        role_list = set()  # TODO 团队...
        for idx, agent in enumerate(agent_list):
            agent["agent_id"] = idx
            agent["agent_path"] = Experiment.save_agent_config(agent=agent,
                                                               exp_path=exp_path,
                                                               format_num_len=format_num_len)
            agent_model_dict[idx] = agent["model_settings"]
            role_list.add(agent["role"])
        return agents_num, agent_model_dict, list(role_list), agent_list

    def get_role_list(self):
        role_list = set()  # TODO 团队...
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
        实验相关的目录创建
        :return 实验根目录
        """
        exp_path = os.path.join(output_dir, exp_id)
        os.makedirs(exp_path, exist_ok=True)

        # 实例化一个logger，控制文件位置
        logger = Logger(log_file=os.path.join(exp_path, "log.txt"),
                        history_file=os.path.join(exp_path, "history.txt"))
        return exp_path
