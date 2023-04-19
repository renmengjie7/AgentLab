"""
@author: Guo Shiguang
@software: PyCharm
@file: experiment.py
@time: 2023/4/17 17:03
"""
import importlib
import inspect
import os

from store.text.logger import Logger


def register_action(action_path='exp/actions'):
    """
    遍历指定目录下所有文件，将所有action类注册到actions字典中
    :param action_path:
    :return:
    """
    actions = {}

    for root, dirs, files in os.walk(action_path):
        for file in files:
            if file == "base_action.py":
                continue
            if file.endswith('.py'):
                module_name = root.replace('/', '.') + '.' + file[:-3]
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        actions[name] = obj

    return actions


def start_experiment(experiment_config, model_api, external_toolkit_api):
    """
    :param experiment_config:
    :param model_api:
    :param external_toolkit_api:
    :return:
    """
    logger = Logger()

    pipeline = ["setup"]
    for step in experiment_config["pipeline"]:
        pipeline.append(step["action"] * int(step["times"]))

    # TODO 完善执行逻辑
    agent_setup = {}
    for agent in experiment_config["agent_list"]:
        agent_setup[agent["agent_id"]] = {"profile": agent["profile"], "role": agent["role"]}
    global_toolkit = [item for item in experiment_config["toolkit"] if item.get_target == "global"]

    actions = register_action()

    for expe_round in range(experiment_config["round_num"]):
        for step in pipeline:
            actions[step].run()
        while True:
            logger.info("Round {} finished".format(expe_round), )
            user_input = input("press Enter to continue or check agnents' status")
            if user_input.strip() == "":
                break
            elif user_input.strip().startswith("probe"):
                # TODO check if  agent_id is valid
                try:
                    agent_id = int(user_input.strip().split()[1])
                    probe_message = user_input.strip().split()[2]
                except:
                    logger.warning("Invalid input, usage: probe [agent_id] [message]")
                if agent_id not in agent_setup:
                    logger.warning("Invalid agent_id")
                    logger.info("Valid agent_id: {}".format(agent_setup.keys()))
                actions["probe"].run(agent_id, probe_message)
            elif user_input.strip().startswith("instuct"):
                try:
                    agent_id = int(user_input.strip().split()[1])
                    instuct_message = user_input.strip().split()[2]
                except:
                    logger.warning("Invalid input, usage: instuct [agent_id] [message]")
                if agent_id not in agent_setup:
                    logger.warning("Invalid agent_id")
                    logger.info("Valid agent_id: {}".format(agent_setup.keys()))
                actions["instuct"].run(agent_id, instuct_message)
            else:
                logger.warning("Invalid input")
