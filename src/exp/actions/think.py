"""
@author: Guo Shiguang
@software: PyCharm
@file: think.py
@time: 2023/4/20 16:32
"""
from exp.actions.base_action import BaseAction
from src.exp.expe_info import ExpeInfo


class ThinkAndAct(BaseAction):
    def __init__(self, expe_info: ExpeInfo):
        super().__init__(expe_info)

    def run(self, *args, **kwargs):
        pass
