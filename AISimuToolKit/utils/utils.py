"""
@author: Guo Shiguang
@software: PyCharm
@file: utils.py
@time: 2023/4/17 0:06
"""
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
    :param num 表示agent的个数 
    对agent ID(文件夹)的命名规范=>使用相同长度的进行编码
    避免出现 agent_1、agent_2、agent_11
    而统一编码为 agent_01、agent_02、agent_11
    """
    return max(2, num//10+1)


def get_file_stream(file: str):
    """_summary_ 得到文件流, 用于传输给finetune

    Args:
        file (str): _description_
    """
    with open(file, 'rb') as f:
        return f


def parse_yaml_config(path: str)->dict:
    """_summary_ 

    Args:
        path (str): _description_ 文件位置

    Returns:
        dict: _description_
    """
    with open(file=path, mode="r",encoding="utf-8") as f:
        conf = yaml.load(f.read(), Loader=yaml.FullLoader)
    return conf
