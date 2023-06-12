"""
@author: Guo Shiguang
@software: PyCharm
@file: demo_recommendation.py
@time: 2023/5/24 21:28
"""
from typing import Union, List

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.exp.scheduler.base import Scheduler


class CustomScheduler(Scheduler):
    def __init__(self, agents: List[Agent], *args, **kwargs):
        super().__init__(agents, *args, **kwargs)

    def schedule(self, group: Union[List[str], str] = None, *args, **kwargs) -> List[Agent]:
        return list(self.agents.all())

    def run(self, group: Union[List[str], str] = None, *args, **kwargs):
        next_choice = self.schedule(group=group, *args, **kwargs)
        pass


def main():
    exp = Experiment.load(config="test/files4test/leaderless_discuss/exp_leaderless_discuss.json",
                          model_config="test/files4test/leaderless_discuss/model.yaml",
                          output_dir="experiments")

    exp.scheduler = CustomScheduler(exp.agents)

    # Only one person can speak at each round
    for i in range(1, 21):
        exp.scheduler.run()
