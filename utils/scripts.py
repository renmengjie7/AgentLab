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
