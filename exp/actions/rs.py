"""
@author: Guo Shiguang
@software: PyCharm
@file: rs.py
@time: 2023/4/17 18:14
@description: recommend system
"""
from exp.actions.base_action import BaseAction
from exp.expe_info import ExpeInfo


class RS(BaseAction):
    """
    推荐系统的实现
    """

    def __init__(self, expe_info: ExpeInfo):
        super().__init__(expe_info)

    def run(self, *args, **kwargs):
        for item in self.expe_info.toolkits:
            for target_id in item.target_id:
                item.get_reco(target_id)
