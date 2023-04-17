"""
@author: Guo Shiguang
@software: PyCharm
@file: rs.py
@time: 2023/4/17 18:14
@description: recommend system
"""

from actions.base_action import BaseAction


class RS(BaseAction):
    def __init__(self, config):
        super().__init__(config)

    def run(self, *args, **kwargs):
        raise NotImplementedError
