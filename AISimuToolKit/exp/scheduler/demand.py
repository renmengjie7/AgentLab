from abc import ABC, abstractmethod
from typing import List, Union

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.agents.agent_collection import AgentCollection
from AISimuToolKit.store.logger import Logger
from .base import Scheduler
from .base import Scheduler


class DemandScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "demand"

    def __str__(self):
        return self.name

    def schedule(self, group: Union[List[str], str] = None, *args, **kwargs) -> List[Agent]:
        return list(self.agents.all())

    def run(self, group: Union[List[str], str] = None, *args, **kwargs):
        # TODO Fine-grained time scheduling 不同的事务会有不同的时间duration
        # something in mail
        next_choice = self.schedule()
        for agent in next_choice:
            agent.clear_mailbox(self.timestep)
            message = agent.select_message(self.timestep)
            agent.reply_on_demand(message=message, timestep=self.timestep)
            agent.change_status()
        self.timestep += 1

