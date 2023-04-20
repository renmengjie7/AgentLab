from src.exp.actions.base_action import BaseAction
from src.exp.expe_info import ExpeInfo


class ReflectionAction(BaseAction):
    """
    手动令agent进行反思，有助于agent的学习
    """

    def __init__(self, expe_info: ExpeInfo):
        super().__init__(expe_info)

    def run(self, num: int,
            input: bool = False,
            output: bool = True,
            prompt: str = "经过最近的阅读, 你觉得自己的profile有何变化? 以下是你的阅读内容:\n",
            *args, **kwargs, ):
        """
        :param input 记忆流中的input内容 (对话的输入)
        :param output 记忆流中的output内容 (对话的输出)
        对最近的多少条进行反思? 
        """
        # 一个简单的反思
        for agent in self.expe_info.get_agent_ids():
            recent_memory = self.expe_info.agents[agent].memory.retrive_by_recentness(num)
