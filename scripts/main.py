import json
import os

import src.utils.scripts as scripts
from scripts.experiment import start_experiment
from src.store.text.logger import Logger
from src.utils.model_api import get_model_apis, get_toolkit_apis


def process_json(content: str):
    """
    处理json文件，生成实验文件夹，返回实验id
    :param content:
    :return:
    """
    json_data = json.loads(content)
    # 应该不需要检查id是否重复
    experiment_id = scripts.generate_experiment_id()
    json_data["experiment_id"] = experiment_id
    os.makedirs(os.path.join("experiments", experiment_id), exist_ok=True)

    json_data["agents_num"] = len(json_data["agent_list"])
    format_num_len = max(2, json_data["agents_num"])

    agent_model_dict = dict()
    role_list = set()
    for idx, agent in enumerate(json_data["agent_list"]):
        agent["agent_id"] = idx + 1
        pwd = os.getcwd()
        agent_path = os.path.join(pwd, "experiments", experiment_id, f"agent_{idx:0{format_num_len}}")
        os.makedirs(agent_path, exist_ok=True)
        agent["agent_path"] = agent_path
        with open(os.path.join(agent_path, "agent_config.json"), "w") as f:
            json.dump(agent, f)
        agent_model_dict[idx] = agent["model_settings"]
        role_list.add(agent["role"])

    json_data["agent_model_dict"] = agent_model_dict
    json_data["role_list"] = list(role_list)

    with open(os.path.join("experiments", experiment_id, "config.json"), "w") as f:
        json.dump(json_data, f)

    # 现在只返回了id
    return experiment_id


if __name__ == '__main__':
    # with open("../test/files4test/expe_config.json", "r") as f:
    #     content = f.read()
    # experiment_id = process_json(content)

    experiment_id = "2023-4-20-20-47-3"
    try:
        with open(os.path.join("experiments", experiment_id, "config.json"), "r") as f:
            expe_config_json = json.load(f)
    except:
        print("experiment id {} not found".format(experiment_id))
        assert False
    model_apis = get_model_apis(expe_config_json["agent_model_dict"])

    toolkit = expe_config_json["external_toolkit"]
    external_toolkit_apis = get_toolkit_apis(toolkit["external_settings"]) if bool(toolkit) and toolkit[
        "enable_external_toolkit"] else None
    start_experiment(expe_config_json, model_apis, external_toolkit_apis)

    # test_chat = model_apis[0].chat(
    #     "write a passage about the life of a person who has made a difference to the world,at least 5000 words")
    # print(test_chat)
