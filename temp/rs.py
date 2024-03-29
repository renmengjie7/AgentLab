"""
@author: Guo Shiguang
@software: PyCharm
@file: rs.py
@time: 2023/4/17 18:14
@description: recommend system
"""
from AISimuToolKit.exp.actions.base_action import BaseAction
from AISimuToolKit.exp.experiment import Experiment


class RS(BaseAction):
    """
    推荐系统的实现
    """

    def __init__(self, expe: Experiment):
        super().__init__(expe)

    def run(self, *args, **kwargs):
        """
        一个简单的例子实现可能的推荐系统交互流程
        :param args:
        :param kwargs:
        :return:
        """
        pass
        # for rs in self.expe.toolkits:
        #     for target_id in rs.target_id:
        #         recommendation = rs.get_recommend(target_id)
        #         prompt = self.generate_prompt(recommendation)
        #         feedback = self.expe.models[target_id].chat(prompt)
        #         self.expe.agents[target_id].memory.store(interactant=target_id, question=prompt, answer=feedback)
        #         self.logger.history("user: {}".format(prompt))
        #         self.logger.history("agent_{}: {}".format(target_id, feedback))

    def generate_prompt(self, *args, **kwargs) -> str:
        pass
