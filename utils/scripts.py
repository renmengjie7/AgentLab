"""
@author: Guo Shiguang
@software: PyCharm
@file: scripts.py
@time: 2023/4/17 0:06
"""
from datetime import datetime


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
