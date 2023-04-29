"""
@author: Guo Shiguang
@software: PyCharm
@file: Courier.py
@time: 2023/4/28 16:51
"""

import threading
from typing import List, Union

from AISimuToolKit.exp.agents.agent import Agent


class Courier:
    _instance_lock = threading.Lock()
    _instance = None

    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.id2name = {agent.agent_id: agent.name for agent in agents}
        self.name2id = {agent.name: agent.agent_id for agent in agents}

    def __new__(cls, agents: List[Agent]):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.__init__(agents)
        return cls._instance

    @staticmethod
    def send(msg: str, sender: Union[Agent, str, int], receiver: Union[Agent, str, int], timestep: int,
             replyable: bool = True, ):
        if Courier._instance is None:
            raise Exception("Courier has not been initialized yet.")
        if isinstance(sender, Agent):
            sender = sender.name
        elif isinstance(sender, int):
            sender = Courier._instance.id2name[sender]
        if isinstance(receiver, str):
            receiver = Courier._instance.name2id[receiver]
            receiver = Courier._instance.agents[receiver - 1]
        elif isinstance(receiver, int):
            receiver = Courier._instance.agents[receiver - 1]
        receiver.receive(msg=msg, sender=sender, replyable=replyable, timestep=timestep)

    @staticmethod
    def all_receivers_name():
        return [agent.name for agent in Courier._instance.agents]
