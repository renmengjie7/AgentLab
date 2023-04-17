"""
@author: Guo Shiguang
@software: PyCharm
@file: experiment.py
@time: 2023/4/17 17:03
"""


def start_experiment(experiment_config, model_api, external_toolkit_api):
    """
    :param experiment_config:
    :param model_api:
    :param external_toolkit_api:
    :return:
    """
    pipeline = ["setup"]
    for step in experiment_config["pipeline"]:
        pipeline.append(step["action"] * int(step["times"]))

    agent_setup = {}
    for agent in experiment_config["agent_list"]:
        agent_setup[agent["agent_id"]] = {"profile": agent["profile"], "role": agent["role"]}
    global_toolkit = [item for item in experiment_config["toolkit"] if item.get_target == "global"]

    for step in pipeline:
        step.run()
