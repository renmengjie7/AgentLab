"""
@author: Guo Shiguang
@software: PyCharm
@file: base_action.py
@time: 2023/4/17 18:14
"""


class BaseAction:
    """
    Base class for all actions
    """

    def __init__(self, expe_info):
        self.expe_info = expe_info

    def run(self, *args, **kwargs):
        raise NotImplementedError
