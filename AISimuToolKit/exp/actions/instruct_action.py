from typing import List

from AISimuToolKit.exp.actions.base_action import BaseAction


class InstructAction(BaseAction):
    """
    给agent下发指令，该指令会影响agent
    该部分不涉及LLM交互，仅是将指令存储到memory中
    instruct通过对话的形式注入
    """

    def __init__(self, expe):
        super().__init__(expe)
        # TODO 注入的交互对象应该是只有user?
        self.interactant = 'user'

    def run(self, instructions: List[dict], *args, **kwargs):
        """
        为多个agent下达指令
        :param instructions:[{"agent_id":agent_id,"question":question,"answer":answer}]
        :param args:
        :param kwargs:
        :return:
        """
        for item in instructions:
            self.instruct(agent_id=int(item["agent_id"]), 
                          question=item["question"],
                          answer=item["answer"])

    def instruct(self, 
                 agent_id: int, 
                 question: str, 
                 answer: str):
        self.logger.info("written in agent_{}'s memory : question\n {}; \nanswer\n {}".format(agent_id, question, answer))
        self.expe.agents[agent_id].memory.store(interactant=self.interactant, question=question, answer=answer)
