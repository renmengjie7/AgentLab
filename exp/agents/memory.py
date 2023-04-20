import json
import time
from string import Template


class Memory:
    """
    文本形式储存记忆,大多数的时候，记忆储存在变量中，在调用export_memory的时候，将记忆导出到文件中
    """

    def __init__(self, memory_path: str):
        """
        memory_id: 自增id，为每个记忆分配唯一id
        memory_list: 记忆列表，每个元素是一个字典，包括id，交互对象，具体行为，时间
        """
        self.memory_id = 0
        self.memory_list = []
        self.memory_path = memory_path

    def store(self, interactant, action, ):
        """
        json格式存储记忆，字段包括自增id，交互对象，具体行为，时间
        :param interactant:交互对象
        :param action: 具体行为
        :return:
        """
        current_time = time.time()
        memory_item = {"id": self.memory_id, "interactant": interactant, "action": action, "time": str(current_time)}
        self.memory_list.append(memory_item)
        self.memory_id += 1

    def retrive_by_id(self, id: str):
        """
        根据id检索记忆
        :param id:
        :return: 如果找到则返回记忆，否则返回None
        """
        for memory_item in self.memory_list:
            if memory_item["id"] == int(id):
                return memory_item
        return None

    def retrive_by_interactant(self, interactant: str):
        """
        根据交互对象检索记忆
        :param interactant:
        :return: 返回的是一个list，可能有0个或多个记忆
        """
        memory_list = []
        for memory_item in self.memory_list:
            if memory_item["interactant"] == interactant:
                memory_list.append(memory_item)
        return memory_list

    def retrive_by_recentness(self, num=1):
        """
        根据时间检索记忆，返回最近的num个记忆
        :param num:
        :return:
        """
        sorted_items = sorted(self.memory_list, key=lambda x: float(x['time']), reverse=True)
        return sorted_items[:num]

    def export_memory(self):
        """
        将记忆导出到文件中
        :return:
        """
        with open(self.memory_path, 'w') as f:
            for memory_item in self.memory_list:
                f.write(json.dumps(memory_item) + "\n")
