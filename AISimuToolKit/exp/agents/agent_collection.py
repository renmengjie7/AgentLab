"""
@author: Guo Shiguang
@software: PyCharm
@file: agent_collection.py
@time: 2023/5/21 16:03
"""
from typing import List, Union

from exp.agents.agent import Agent

from AISimuToolKit.store.logger import Logger


class AgentCollectionWrapper:
    def __init__(self, agents):
        self.agents = agents

    def receive(self, msg: str, sender: str, timestep: int):
        for agent in self.agents:
            agent.receive(msg, sender, timestep)

    def __iter__(self):
        return iter(self.agents)


class AgentGroup:
    def __init__(self, group_name: str, group_agents: Union[List[Agent], Agent]):
        if isinstance(group_agents, Agent):
            group_agents = [group_agents]
        self.group_name = group_name
        self.agents = {agent.name: agent for agent in group_agents}

    def add_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def remove_agent(self, agent: Agent):
        self.agents.pop(agent.name)

    def all(self):
        return AgentCollectionWrapper(self.agents.values())


class AgentCollection:
    """
    A collection of agents, which can be indexed by agent_id or name
    example:
    agents = AgentCollection([Agent(id=0, name="Alice"), Agent(id=1, name="Bob")])
    agents[0] # get agent by id
    agents["Alice"] # get agent by name
    agents.get_agent_by_id(0) # get agent by id
    agents.get_agent_by_name("Alice") # get agent by name
    """

    def __init__(self, agents: List[Agent]):
        self.id2name = {agent.agent_id: agent.name for agent in agents}
        self.name2id = {agent.name: agent.agent_id for agent in agents}
        self.agents = {agent.name: agent for agent in agents}
        self.groups = {"all": AgentGroup(group_name="all", group_agents=agents)}
        for agent in agents:
            if agent.group is None:
                continue
            if agent.group == "all":
                raise ValueError("group name 'all' is reserved")
            if agent.group not in self.groups:
                self.groups[agent.group] = AgentGroup(group_name=agent.group, group_agents=[agent])
            else:
                self.groups[agent.group].add_agent(agent)
        self.logger = Logger()

    def get_agent_by_id(self, agent_id):
        return self.agents[agent_id]

    def get_agent_by_name(self, name):
        return self.agents[name]

    def all(self) -> AgentCollectionWrapper:
        return AgentCollectionWrapper(self.agents)

    def get_group_by_group_name(self, group_name: str):
        return self.groups[group_name]

    def get_group_by_agent(self, agent: Union[str, Agent, int]):
        if isinstance(agent, Agent):
            agent = agent.name
        if isinstance(agent, int):
            agent = self.id2name[agent]
        group_name = "all"
        for group in self.groups.values():
            if agent in group.agents.keys() and group.group_name != "all":
                group_name = group
        return self.groups[group_name]

    def __getitem__(self, key):
        try:
            if isinstance(key, int):
                return self.agents[self.id2name[key]]
            elif isinstance(key, str):
                return self.agents[key]
        except:
            self.logger.error(f"AgentCollection: {key} not found")
            raise KeyError(f"AgentCollection: {key} not found")
