"""
@author: Guo Shiguang
@software: PyCharm
@file: agent.py
@time: 2023/4/19 9:22
"""
import os.path

from AISimuToolKit.exp.agents.memory import Memory


class Agent:
    """
    储存agent的信息   
    """

    def __init__(self, agent_id: int, 
                 name: str, profile: str, role: str, agent_path: str,
                 config: dict):
        self.agent_id = agent_id
        self.name = name
        self.profile = profile
        self.role = role
        self.config = config
        self.path=agent_path
        self.memory = Memory(memory_path=os.path.join(agent_path, "memory.jsonl"))
