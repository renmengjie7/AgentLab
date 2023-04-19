"""
@author: Guo Shiguang
@software: PyCharm
@file: base_action.py
@time: 2023/4/17 18:14
"""
from exp.expe_info import ExpeInfo


class BaseAction:
    """
    Base class for all actions
    """

    def __init__(self, expe_info: ExpeInfo):
        self.expe_info = expe_info

    def run(self, *args, **kwargs):
        raise NotImplementedError
