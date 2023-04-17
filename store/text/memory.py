import json
import time
from string import Template


class Memory:
    """
    文本形式储存记忆
    """

    def __init__(self):
        self.memory_id = 0

    def store(self, interactant, action, ):
        """
        json格式存储记忆，字段包括自增id，交互对象，具体行为，时间
        :param interactant:交互对象
        :param action: 具体行为
        :return:
        """
        current_time = time.time()
        memory_item = {"id": self.memory_id, "interactant": interactant, "action": action, "time": str(current_time)}
        with open('memory.jsonl', 'a') as f:
            f.write(json.dumps(memory_item) + "\n")
        self.memory_id += 1

    def retrive_by_id(self, id):
        """
        根据id检索记忆
        :param id:
        :return: 如果找到则返回记忆，否则返回None
        """
        with open('memory.jsonl', 'r') as f:
            for line in f:
                memory_item = json.loads(line)
                if memory_item["id"] == id:
                    return memory_item
        return None

    def retrive_by_interactant(self, interactant):
        """
        根据交互对象检索记忆
        :param interactant:
        :return: 返回的是一个list，可能有0个或多个记忆
        """
        memory_list = []
        with open('memory.jsonl', 'r') as f:
            for line in f:
                memory_item = json.loads(line)
                if memory_item["interactant"] == interactant:
                    memory_list.append(memory_item)
        return memory_list

    def retrive_by_recentness(self, num=1):
        """
        根据时间检索记忆，返回最近的num个记忆
        :param num:
        :return:
        """
        with open('memory.jsonl', 'r') as f:
            memory_items = [json.loads(line) for line in f]
        sorted_items = sorted(memory_items, key=lambda x: float(x['time']), reverse=True)
        return sorted_items[:num]
