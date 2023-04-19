"""
@author: Guo Shiguang
@software: PyCharm
@file: expe_info.py
@time: 2023/4/18 16:32
"""
import json


class ExpeInfo:
    def __init__(self, agents: list, models: list, toolkit: list, config: json):
        self.agents = agents
        self.models = models
        self.toolkit = toolkit
        self.config = config

    def get_agent_ids(self):
        return [agent.agent_id for agent in self.agents]
