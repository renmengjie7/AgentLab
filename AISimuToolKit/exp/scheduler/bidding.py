from abc import ABC, abstractmethod
from typing import List, Union

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.agents.agent_collection import AgentCollection
from AISimuToolKit.store.logger import Logger
from .base import Scheduler

class BiddingSchedular(Scheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "bidding"
        # continuous speak needs an attenuation coefficient
        self.attenuation_coe = kwargs.get("attenuation_coe", 0.7)
        self.continuous_count = {agent.name: 0 for agent in self.agents.all()}
        self.bidding_message = "Please consider his/her characteristics and experience, predict a number from 1 to 100, indicating the probability of he/she speaking at the next moment. The greater the value, the higher the probability."
        self.bidding_output_format = "The answer should only contain the number"
        self.what_to_do_next_moment = "What would you like to say in the next moment?Please try to avoid repeating yourself and others as much as possible.\n(There is no need to give any explanation)"

    def __str__(self):
        return self.name

    def schedule(self, group: Union[List[str], str] = None, *args, **kwargs) -> List[Agent]:
        """
        TODO cue a person directly and that person's score will be higher
        In a list of scenarios, only one can be selected to take some action
        """
        choose_from_list = [self.agents]
        if group is not None:
            choose_from_list = []
            for group_name in group:
                if group_name in self.agents.groups.keys():
                    choose_from_list += self.agents.groups[group_name]
                else:
                    self.logger.error(f"Group {group_name} not found in {self.agents.groups.keys()}.")
                    raise ValueError(f"Group {group_name} not found in {self.agents.groups.keys()}.")

        next_choice = []
        for choose_from in choose_from_list:
            choose_from = list(choose_from.all())
            max_score = 0
            highest_bidder = 0
            for agent in choose_from:
                agent.check_mailbox_and_read_all(timestep=self.timestep)
                answer = agent.chat(message=self.bidding_message, need_status=False,
                                    output_format=self.bidding_output_format)
                try:
                    answer = int(answer)
                    self.logger.info(f"agent {agent.name}'s score is {answer}")
                    answer *= (self.attenuation_coe ** self.continuous_count[agent.name])
                    self.logger.info(f"agent {agent.name}'s score is {answer} after attenuation")
                except ValueError as e:
                    self.logger.error(f"Failed to convert '{answer}' to an integer: {e}")
                    continue
                if max_score <= answer:
                    highest_bidder = agent
                    max_score = answer
            highest_bidder_continous_count = self.continuous_count[highest_bidder.name]
            self.continuous_count = {agent.name: 0 for agent in self.agents.all()}
            self.continuous_count[highest_bidder.name] = highest_bidder_continous_count + 1
            next_choice.append(highest_bidder)
        return next_choice

    def run(self, group: Union[List[str], str] = None, *args, **kwargs):
        next_choice = self.schedule()
        audience = kwargs.get("audience", "all")  # audience can be "all" or "group"
        for agent in next_choice:
            answer = agent.chat(message=self.what_to_do_next_moment)
            self.logger.history(f"agent {agent.name} says: {answer}")
            if audience != "all":
                agent.talk2(message=answer, agents=self.agents.get_group_by_agent(agent).all())
            else:
                agent.talk2(message=answer, agents=self.agents.all())
            agent.change_status()
        self.timestep += 1
