from abc import ABC, abstractmethod
from typing import List, Union

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.agents.agent_collection import AgentCollection
from AISimuToolKit.store.logger import Logger
from .base import Scheduler


class SequentialScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "sequential"
        self.last_choose_from = None
        self.sequential_count = 0
        self.what_to_do_next_moment = "What would you like to say in the next moment?Please try to avoid repeating yourself and others as much as possible.\n(There is no need to give any explanation)"

    def __str__(self):
        return self.name

    def schedule(self, group: Union[List[str], str] = None, *args, **kwargs) -> List[Agent]:
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
        return next_choice

    def run(self, group: Union[List[str], str] = None, *args, **kwargs):
        next_choice = self.schedule()
        audience = kwargs.get("audience", "all")  # audience can be "all" or "group"
        for agent in next_choice:
            answer = agent.chat(message=self.what_to_do_next_moment)
            if audience == "all":
                agent.talk2(message=answer, agents=self.agents.get_group_by_agent(agent).all())
            agent.change_status()
        self.timestep += 1

