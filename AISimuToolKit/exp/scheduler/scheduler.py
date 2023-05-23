"""
@author: Guo Shiguang
@software: PyCharm
@file: scheduler.py
@time: 2023/5/23 15:32
"""
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
    def schedule(self, group: Union[List[str]] = None, *args, **kwargs) -> List[Agent]:
        pass


class RandomScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "random"

    def __str__(self):
        return self.name

    def schedule(self, group: Union[List[str]] = None, *args, **kwargs) -> List[Agent]:
        choose_from_list = [self.agents]
        if group is not None:
            choose_from_list = []
            for group in group:
                if group in self.agents.groups.keys():
                    choose_from_list = self.agents.groups[group]
                else:
                    self.logger.error(f"Group {group} not found in {self.agents.groups.keys()}.")
                    raise ValueError(f"Group {group} not found in {self.agents.groups.keys()}.")
        import random
        next_choice = [random.choice(list(choose_from.all())) for choose_from in choose_from_list]
        self.timestep += 1
        return next_choice


class SequentialScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "sequential"
        self.last_choose_from = None
        self.sequential_count = 0

    def __str__(self):
        return self.name

    def schedule(self, group: Union[List[str]] = None, *args, **kwargs) -> List[Agent]:
        choose_from_list = [self.agents]
        if group is not None:
            choose_from_list = []
            for group_name in group:
                if group_name in self.agents.groups.keys():
                    choose_from_list += self.agents.groups[group_name]
                else:
                    self.logger.error(f"Group {group_name} not found in {self.agents.groups.keys()}.")
                    raise ValueError(f"Group {group_name} not found in {self.agents.groups.keys()}.")

        if self.last_choose_from is not None:
            if (self.last_choose_from == "all" and group is not None) or (
                    self.last_choose_from != "all" and group is None) or set(group) != set(self.last_choose_from):
                self.logger.warn("The provided group is different from the previous one.The counter will be reset.")
                self.sequential_count = 0

        next_choice = [list(choose_from.all())[self.sequential_count % len(list(choose_from.all()))] for choose_from in
                       choose_from_list]

        self.sequential_count += 1
        self.timestep += 1
        return next_choice
