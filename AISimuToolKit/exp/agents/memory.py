import json
from typing import List

import pandas as pd
from sklearn.metrics import pairwise_distances

from AISimuToolKit.exp.toolkit.TimeStep import TimeStep
from AISimuToolKit.model.embedding import BertSentenceEmbedding
from AISimuToolKit.model.model import PublicApiBase
from AISimuToolKit.store.logger import Logger


class Memory:
    """
    文本形式储存记忆,记忆储存在变量中，同时会以append的形式储存到对应的agent文件夹下，在调用export_memory的时候，将记忆导出到文件中
    记忆以对话的形式存储
    """

    # TODO interactant似乎是一个不常用/不正确的词，可以考虑换一个
    def __init__(self, memory_path: str, extra_columns: List[str] = None, auto_rewrite: bool = True):
        """
        记忆储存、检索、导出模块，可以通过extra_columns参数添加额外的列
        :param memory_path:
        :param extra_columns:
        """
        self.logger = Logger()
        default_cols = ["interactant", "experience", "timestep", "question", "answer", "source", "importance",
                        "similarity", "embedding", "recentness", "score"]
        if extra_columns is not None and len(extra_columns) > 0:
            if set(extra_columns) & set(default_cols):
                self.logger.warning("The following column names are already included in the default list and will be "
                                    "ignored:{}".format(set(extra_columns) & set(default_cols)))
            default_cols.extend(extra_columns)
            default_cols = list(set(default_cols))
        self.memory_df = pd.DataFrame(columns=default_cols)
        self.memory_path = memory_path
        self.bert = BertSentenceEmbedding()
        self.auto_rewrite = auto_rewrite

        # TODO 用timestep替换他
        self.curr_id = 0

        if self.auto_rewrite:
            self.model = self.get_model()

    def add_column(self, column_name: str) -> None:
        if column_name not in self.memory_df.columns:
            self.memory_df[column_name] = None
            self.logger.info("Add column {} to memory".format(column_name))

    def remove_column(self, column_name: str) -> None:
        if column_name in self.memory_df.columns:
            self.memory_df.drop(column_name, axis=1, inplace=True)
            self.logger.info("Remove column {} from memory".format(column_name))

    # def store(self, experience: str, interactant: str = '', *args, **kwargs):
    #     """
    #     json格式存储记忆，字段包括自增id，交互对象，对话的两端，时间
    #     TODO 是否需要显示地给出交互对象, 感觉自然语言描述已经可以了, 现在暂时都设置为空
    #     :param interactant: 交互对象
    #     :param question:
    #     :param answer:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     current_time = time.time()
    #     memory_item = {
    #         "id": self.memory_id,
    #         "interactant": interactant,
    #         "experience": experience,
    #         # "question": question,
    #         # "answer": answer,
    #         "time": str(current_time)
    #     }
    #     with open(self.memory_path, "a", encoding="utf-8") as f:
    #         f.write(json.dumps(memory_item, ensure_ascii=False) + "\n")
    #     self.memory_list.append(memory_item)
    #     self.memory_id += 1

    # TODO 是否需要显示地给出交互对象, 感觉自然语言描述已经可以了, 现在暂时都设置为空
    # TODO 需要更完善的逻辑判断,加入自动改写（或者移到做finetune前）
    def store(self, timestep: TimeStep = None, experience: str = None, question: str = None, answer: str = None,
              interactant: str = '', source: str = None, importance: float = 5, *args, **kwargs) -> object:
        """
        储存记忆，其中experience, [question, answer]中的任意一对都可以为空，但是不能同时为空,q和a必须同时提供
        :param importance:
        :param timestep:
        :param experience:
        :param question:
        :param answer:
        :param interactant:
        :param source:
        :param args:
        :param kwargs:
        :return:
        """
        if question is None and answer is not None or question is not None and answer is None:
            self.logger.warning(
                "The question and answer must be provided at the same time.Set them to None.")
            question = None
            answer = None
        if experience is None and question is None and answer is None:
            self.logger.warning(
                "The experience, question and answer cannot be None at the same time.Nothing will be stored.")
            return

        embed_sentence = experience if experience is not None else question + answer
        # timestep = self.curr_id
        memory_item = {
            "interactant": interactant,
            "experience": experience,
            "question": question,
            "answer": answer,
            "source": source,
            "timestep": timestep,
            "importance": importance,
            "embedding": self.bert.encode(embed_sentence),
            "id": self.curr_id
        }

        for item in kwargs.keys():
            self.add_column(item)
        for key, value in kwargs.items():
            memory_item[key] = value

        memory_series = pd.Series(memory_item)
        memory_df = memory_series.to_frame().T
        self.memory_df = pd.concat([self.memory_df, memory_df], ignore_index=True)
        self.memory_df["recentness"] = pow(0.99, self.curr_id - self.memory_df["id"])
        self.curr_id += 1
        with open(self.memory_path, "a", encoding="utf-8") as f:
            last_row = self.memory_df.drop(["similarity", "embedding", "recentness", "score"], axis=1)
            json_object = last_row.to_json(orient='records')
            f.write(json_object[1:-1] + "\n")

        # self.export_memory()

    def retrieve_by_interactant(self, interactant: str) -> list[dict]:
        """
        根据交互对象检索记忆
        :param interactant:
        :return:
        """
        return self.memory_df[self.memory_df["interactant"] == interactant].to_dict(orient="records")

    # TODO 根据timestep检索和返回
    def retrieve_by_recentness(self, num=1) -> list[dict]:
        """
        根据id检索和返回
        :param num:
        :return:
        """
        return self.memory_df.sort_values(by="id", ascending=False).head(num).to_dict(orient="records")

    # TODO format步骤需要处理int和string的问题
    def custom_retrieve(self, condition: dict, num=-1) -> list[dict]:
        """
        自定义检索条件
        :param condition:
        :param num:-1表示返回所有
        :return:
        """
        num = len(self.memory_df) if num == -1 else num
        query_str = ' & '.join([f"{k}=='{v}'" for k, v in condition.items()])
        return self.memory_df.query(query_str).head(num).to_dict(orient="records")

    def export_memory(self):
        """
        将记忆导出到文件中
        :return:
        """

        df = self.memory_df.drop(["similarity", "embedding", "recentness", "score"], axis=1)
        with open(self.memory_path, 'w') as f:
            for line in df.to_dict(orient='records'):
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def retrieve_by_query(self, weights: dict, num: int = 10, query: str = None) -> list[dict]:
        """
        根据权重检索
        :param query:
        :param weights:
        :param num:
        :return:
        """

        def compute_score(row):
            score = 0
            for col in row.index:
                if col in droped_weights.keys() and isinstance(row[col], (int, float)):
                    score += row[col] * droped_weights.get(col, 0)
            return score

        droped_weights = weights.copy()
        droped_weights.pop("similarity", None)
        if "similarity" in weights.keys() and query is not None and query != "":
            query_embedding = self.bert.encode(query)
            cos_sim = 1 - pairwise_distances(query_embedding.reshape(1, -1), self.memory_df["embedding"].tolist(),
                                             metric="cosine")
            self.memory_df["similarity"] = cos_sim.reshape(-1)
            droped_weights = weights
        self.memory_df['score'] = self.memory_df.apply(compute_score, axis=1)

        num = len(self.memory_df) if num == -1 else num
        return self.memory_df.sort_values(by="score", ascending=False).head(num).to_dict(orient="records")

    # TODO 一个公共的，用于改写对话/检索相关人员/。。。
    def get_model(self) -> PublicApiBase:
        pass
