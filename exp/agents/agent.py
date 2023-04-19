"""
@author: Guo Shiguang
@software: PyCharm
@file: agent.py
@time: 2023/4/19 9:22
"""
from exp.agents.memory import Memory


class Agent:
    def __init__(self, agent_id, profile, role):
        self.agent_id = agent_id
        self.profile = profile
        self.role = role
        self.memory = Memory()
