"""
@author: Guo Shiguang
@software: PyCharm
@file: expe_info.py
@time: 2023/4/18 16:32
"""
import json

from exp.agents.agent import Agent
from utils.model_api import ApiBase, ExternalToolkitApi


class ExpeInfo:
    def __init__(self, agents: list[Agent], models: list[ApiBase], toolkits: list[ExternalToolkitApi], config: json):
        self.agents = agents
        self.models = models
        self.toolkits = toolkits
        self.config = config

    def get_agent_ids(self):
        return [agent.agent_id for agent in self.agents]
