from abc import ABC, abstractmethod
from typing import List, Union

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.agents.agent_collection import AgentCollection
from AISimuToolKit.store.logger import Logger


class Scheduler(ABC):
    def __init__(self, agents: AgentCollection, *args, **kwargs):
        self.timestep = 0
        self.agents = agents
        self.logger = Logger()

    @abstractmethod
    def schedule(self, group: Union[List[str], str] = None, *args, **kwargs) -> List[Agent]:
        pass

    @abstractmethod
    def run(self, group: Union[List[str], str] = None, *args, **kwargs):
        pass
