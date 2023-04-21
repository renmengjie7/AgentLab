"""
@author: Guo Shiguang
@software: PyCharm
@file: think.py
@time: 2023/4/20 16:32
"""
from src.exp.actions.base_action import BaseAction
from src.exp.experiment import Experiment


class ThinkAndAct(BaseAction):
    def __init__(self, expe: Experiment):
        super().__init__(expe)

    def run(self, *args, **kwargs):
        pass
