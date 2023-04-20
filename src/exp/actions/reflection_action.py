from src.exp.actions.base_action import BaseAction
from src.exp.expe_info import ExpeInfo


class ReflectionAction(BaseAction):
    """
    手动令agent进行反思，有助于agent的学习
    """

    def __init__(self, expe_info: ExpeInfo):
        super().__init__(expe_info)

    def run(self, *args, **kwargs):
        # 一个简单的反思
        for agent in self.expe_info.get_agent_ids():
            recent_memory = self.expe_info.agents[agent].memory.retrive_by_recentness(100)
