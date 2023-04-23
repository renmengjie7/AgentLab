"""
@author: Guo Shiguang
@software: PyCharm
@file: test_experiment.py
@time: 2023/4/22 20:53
"""
from unittest import TestCase

from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.model.model import ApiBase


class TestExperiment(TestCase):
    def test_load_exp(self):
        exp = Experiment.load_exp(config="files4test/expe_config.json",
                                  model_config="files4test/model.yaml",
                                  output_dir="experiments_unittest")
        self.assertTrue(isinstance(exp, Experiment))

        self.assertTrue(isinstance(exp.id, str))
        self.assertTrue(isinstance(exp.path, str))
        self.assertTrue(isinstance(exp.agents, list))

        self.assertTrue(all(isinstance(agent, Agent) for agent in exp.agents))
        self.assertTrue(isinstance(exp.models, dict))

        self.assertTrue(all(isinstance(key, int) for key in exp.models.keys()))
        self.assertTrue(all(isinstance(value, ApiBase) for value in exp.models.values()))
        self.assertTrue(isinstance(exp.config, dict))
