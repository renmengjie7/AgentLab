"""
@author: Guo Shiguang
@software: PyCharm
@file: base_action.py
@time: 2023/4/17 18:14
"""
from src.exp.expe_info import ExpeInfo
from src.store.text.logger import Logger


class BaseAction:
    """
    Base class for all actions
    """

    def __init__(self, expe_info: ExpeInfo):
        self.expe_info = expe_info
        self.logger = Logger()

    def run(self, *args, **kwargs):
        raise NotImplementedError
