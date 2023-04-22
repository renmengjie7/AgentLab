"""
@author: Guo Shiguang
@software: PyCharm
@file: base_action.py
@time: 2023/4/17 18:14
"""
from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.store.text.logger import Logger


class BaseAction:
    """
    Base class for all actions
    """

    def __init__(self, expe: Experiment):
        self.expe = expe
        self.logger = Logger()

    def run(self, *args, **kwargs):
        raise NotImplementedError
