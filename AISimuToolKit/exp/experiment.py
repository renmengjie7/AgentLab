"""
@author: Guo Shiguang
@software: PyCharm
@file: experiment.py
@time: 2023/4/18 16:32
"""
import json
from typing import List
import os
import copy
from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.model.model import ApiBase
from typing import Type
from AISimuToolKit.store.text.logger import Logger
from AISimuToolKit.model.register import get_model_apis
from AISimuToolKit.utils.utils import generate_experiment_id, get_fromat_len


class Experiment:
    def __init__(self, id: str, path: str, agents: List[Agent], models: List[ApiBase], config: json):
        self.id = id
        self.path = path
        self.agents = agents
        self.models = models
        self.config = config

    def get_agent_ids(self):
        return [agent.agent_id for agent in self.agents]
    
    @classmethod
    def load_exp(cls, 
                 config: str, 
                 model_config: str,
                 output_dir: str="experiments")-> Type["Experiment"]:
        """_summary_ 从json配置文件中加载并示例化一个experiment
        
        Args:
            config (str): _description_  实验的配置文件 
            model_config (str): _description_ 配置每个模型对应的url
            output_dir (str): _description_  日志、历史等存储位置

        Returns:
            _type_: _description_
        """
        # 直接使用时间戳做实验ID, 应该不需要检查id是否重复
        experiment_id = generate_experiment_id()
        json_data = Experiment.preprocess_config(file=config,
                                                 exp_id=experiment_id,
                                                 output_dir=output_dir)
        model_apis = get_model_apis(exp_id=experiment_id,
                                    agents=[i for i in range(len(json_data['agent_list']))],
                                    agent_model_dict=json_data["agent_model_dict"], 
                                    model_config=model_config)
        
        # 实例化agents
        agents_list = []
        for agent in json_data["agent_list"]:
            agents_list.append(Agent(agent_id=agent["agent_id"], 
                                     name=agent['name'],
                                     role=agent["role"], 
                                     profile=agent["profile"],
                                     agent_path=agent["agent_path"],
                                     config=agent['model_settings']['config']))
        # 实例化experiment
        exp = Experiment(id=experiment_id,
                         path=json_data["path"],
                         agents=agents_list, 
                         models=model_apis,
                         config=json_data)
        return exp


    @staticmethod
    def preprocess_config(file: str, exp_id: str, output_dir: str):
        """_summary_ 处理用户的整个配置文件

        Args:
            file (str): _description_
            exp_id (str): _description_
            output_dir (str): _description_
        """
        with open(file, 'r') as file:
            json_data = json.load(file)
        init_data = copy.deepcopy(json_data)
        json_data["experiment_id"] = exp_id
        
        exp_path = Experiment.mk_exp_dir(output_dir, exp_id)

        agents_num, agent_model_dict, role_list, agent_list = Experiment.preprocess_agent(json_data=json_data, exp_path=exp_path)

        json_data["path"] = exp_path
        json_data["agents_num"] = agents_num
        json_data["agent_model_dict"] = agent_model_dict
        json_data["role_list"] = role_list
        json_data["agent_list"] = agent_list
        
        Experiment.save2config(init_config=init_data, 
                               preprocess_config=json_data,
                               exp_path=exp_path)
        return json_data
            
            
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
        
    
    @staticmethod
    def save2config(init_config: dict, preprocess_config: dict, exp_path: str):
        """
        init_config是使用者初始传入的配置文件, 存储下来, 以供二次使用(再实验)
        preprocess_config是处理过的
        exp_path 是实验存放的目录
        """
        with open(os.path.join(exp_path, "config.json"), "w") as f:
            json.dump(init_config, f)
        with open(os.path.join(exp_path, "processedconfig.json"), "w") as f:
            json.dump(preprocess_config, f)
            
            
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
        role_list = set()   # TODO 团队...
        for idx, agent in enumerate(agent_list):
            agent["agent_id"] = idx
            agent["agent_path"] = Experiment.save_agent_config(agent=agent,
                                                               exp_path=exp_path,
                                                               format_num_len=format_num_len)
            agent_model_dict[idx] = agent["model_settings"]
            role_list.add(agent["role"])
        
        return agents_num, agent_model_dict, list(role_list), agent_list
    
    
    @staticmethod
    def save_agent_config(agent: dict, exp_path: str, format_num_len: int):
        """_summary_ 保存智能体配置文件

        Args:
            agent (dict): _description_ 
            exp_path (str): _description_
            format_num_len (_type_): _description_

        Returns:
            _type_: _description_
        """
        agent_path = os.path.join(exp_path, 
                                  f"agent_{agent['agent_id']:0{format_num_len}}")
        os.makedirs(agent_path, exist_ok=True)
        with open(os.path.join(agent_path, "agent_config.json"), "w") as f:
            json.dump(agent, f)
        return agent_path
    