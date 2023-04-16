"""
@author: Guo Shiguang
@software: PyCharm
@file: api.py
@time: 2023/4/16 23:22
"""
import json
import os

import utils.scripts as scripts

from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.post("/upload/experiment")
async def upload_json(file: UploadFile = File(...)):
    content = await file.read()
    json_data = json.loads(content)
    # 应该不需要检查id是否重复
    experiment_id = scripts.generate_experiment_id()
    json_data["experiment_id"] = experiment_id
    os.makedirs(os.path.join("experiments", experiment_id), exist_ok=True)

    json_data["agents_num"] = len(json_data["agent_list"])
    format_num_len = max(2, json_data["agents_num"])

    model_list = set()
    role_list = set()
    for idx, agent in enumerate(json_data["agent_list"]):
        agent["agent_id"] = idx
        agent_path = os.path.join("experiments", experiment_id, f"agent_{idx:0{format_num_len}}")
        os.makedirs(agent_path, exist_ok=True)
        with open(os.path.join(agent_path, "config.json"), "w") as f:
            json.dump(agent, f)
        model_list.add(agent["model"])
        role_list.add(agent["role"])

    json_data["model_list"] = list(model_list).sort()
    json_data["role_list"] = list(role_list).sort()

    return json_data
