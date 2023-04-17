"""
@author: Guo Shiguang
@software: PyCharm
@file: api.py
@time: 2023/4/16 23:22
"""
import json
import os

import utils.scripts as scripts
from experiment import start_experiment
from utils.model_api import get_model_apis, get_toolkit_apis

from fastapi import FastAPI, File, UploadFile, Body

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.post("/upload/experiment")
async def upload_json(file: UploadFile = File(...)):
    # 现在做测试可以：curl -X POST -F "file=@/home/guoshiguang2021/AISimulation/files4test/expe_config.json" http://127.0.0.1:8000/upload/experiment
    content = await file.read()
    json_data = json.loads(content)
    # 应该不需要检查id是否重复
    experiment_id = scripts.generate_experiment_id()
    json_data["experiment_id"] = experiment_id
    os.makedirs(os.path.join("experiments", experiment_id), exist_ok=True)

    json_data["agents_num"] = len(json_data["agent_list"])
    format_num_len = max(2, json_data["agents_num"])

    agnet_model_dict = dict()
    role_list = set()
    for idx, agent in enumerate(json_data["agent_list"]):
        agent["agent_id"] = idx
        agent_path = os.path.join("experiments", experiment_id, f"agent_{idx:0{format_num_len}}")
        os.makedirs(agent_path, exist_ok=True)
        with open(os.path.join(agent_path, "agnet_config.json"), "w") as f:
            json.dump(agent, f)
        agnet_model_dict[idx] = agent["model_settings"]
        role_list.add(agent["role"])

    json_data["agnet_model_dict"] = agnet_model_dict
    json_data["role_list"] = list(role_list)

    with open(os.path.join("experiments", experiment_id, "config.json"), "w") as f:
        json.dump(json_data, f)

    # 现在只返回了id
    return {"status": "success", "experiment_id": experiment_id}


@app.post("/start")
def prepare_for_experiment(expe_id: str = Body(...)):
    # curl -X POST -d "2023-4-17-14-42-2" http://127.0.0.1:8000/start
    try:
        with open(os.path.join("experiments", expe_id, "config.json"), "r") as f:
            expe_config_json = json.load(f)
    except:
        return {"status": "failed", "msg": "experiment id {} not found".format(expe_id)}
    model_apis = get_model_apis(expe_config_json["agnet_model_dict"])
    external_toolkit_apis = get_toolkit_apis(expe_config_json["external_toolkit_dict"])

    start_experiment(expe_config_json, model_apis, external_toolkit_apis)

    test_chat = model_apis["0_P_GPT_35_API"].chat("hello world")
    return {"status": "success", "msg": "experiment id {} start".format(expe_id), "test_chat": test_chat}
