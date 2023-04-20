"""
@author: Guo Shiguang
@software: PyCharm
@file: rs.py
@time: 2023/4/17 18:14
@description: recommend system
"""
from exp.actions.base_action import BaseAction
from src.exp.expe_info import ExpeInfo


class RS(BaseAction):
    """
    推荐系统的实现
    """

    def __init__(self, expe_info: ExpeInfo):
        super().__init__(expe_info)

    def run(self, *args, **kwargs):
        for rs in self.expe_info.toolkits:
            for target_id in rs.target_id:
                recommendation = rs.get_recommend(target_id)
                prompt = self.generate_prompt(recommendation)
                feedback = self.expe_info.models[target_id].chat(prompt)

    def generate_prompt(self, *args, **kwargs) -> str:
        pass
