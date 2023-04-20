"""
@author: Guo Shiguang
@software: PyCharm
@file: agent.py
@time: 2023/4/19 9:22
"""
from src.exp.agents.memory import Memory


class Agent:
    """
    储存agent的信息   
    """

    def __init__(self, agent_id: int, profile: str, role: str, memory_path: str):
        self.agent_id = agent_id
        self.profile = profile
        self.role = role
        self.memory = Memory(memory_path=memory_path)
