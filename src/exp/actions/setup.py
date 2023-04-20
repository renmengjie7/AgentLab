"""
@author: Guo Shiguang
@software: PyCharm
@file: setup.py
@time: 2023/4/17 19:24
"""
from exp.actions.base_action import BaseAction


class Setup(BaseAction):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def run(self, *args, **kwargs):
        pass
