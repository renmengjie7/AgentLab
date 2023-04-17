"""
@author: Guo Shiguang
@software: PyCharm
@file: base_action.py
@time: 2023/4/17 18:14
"""


class BaseAction:
    def __init__(self, config):
        self.config = config

    def run(self, *args, **kwargs):
        raise NotImplementedError

