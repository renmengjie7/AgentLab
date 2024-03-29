"""
@author: Guo Shiguang
@software: PyCharm
@file: utils.py
@time: 2023/4/17 0:06
"""
import json
from datetime import datetime

import yaml


def generate_experiment_id():
    now = datetime.now()
    return "{}-{}-{}-{}-{}-{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)


def set_seed(seed):
    import random
    # import numpy as np
    # import torch
    random.seed(seed)
    # np.random.seed(seed)
    # torch.manual_seed(seed)
    # torch.cuda.manual_seed_all(seed)
    # torch.backends.cudnn.deterministic = True
    # torch.backends.cudnn.benchmark = False


def get_fromat_len(num: int):
    """
    Naming specification for agent ID (folder) =>
    code with the same length to avoid agent_1, agent_2, agent_11 and uniformly code as agent_01, agent_02, agent_11
    :param num
    """
    return max(2, num // 10 + 1)


def get_file_stream(file: str):
    """
    return file stream for finetune
    :param file:
    :return:
    """
    with open(file, 'rb') as f:
        return f


def parse_yaml_config(path: str) -> dict:
    """
    parse yaml agent_config file
    :param path:
    :return:
    """
    with open(file=path, mode="r", encoding="utf-8") as f:
        conf = yaml.load(f.read(), Loader=yaml.FullLoader)
    return conf


def save_config(config: dict, path: str):
    with open(path, "w") as f:
        json.dump(config, f)
