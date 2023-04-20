from typing import List

from src.exp.actions.base_action import BaseAction


class InstructAction(BaseAction):
    """
    给agent下发指令，该指令会影响agent
    该部分不涉及LLM交互，仅是将指令存储到memory中
    """

    def __init__(self, expe_info):
        super().__init__(expe_info)

    def run(self, instructions: List[dict], *args, **kwargs):
        """
        为多个agent下达指令
        :param instructions:[{"agent_id":"instuctions"}]
        :param args:
        :param kwargs:
        :return:
        """
        for item in instructions:
            self.instruct(int(item["agent_id"]), item["instructions"])

    def instruct(self, agent_id: int, instructions):
        self.expe_info.agents[agent_id].memory.store(agent_id, instructions)
