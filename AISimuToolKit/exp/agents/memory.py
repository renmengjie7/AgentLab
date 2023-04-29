import json
from typing import List

import pandas as pd
from AISimuToolKit.exp.toolkit.TimeStep import TimeStep
from sklearn.metrics import pairwise_distances

from AISimuToolKit.model.embedding import BertSentenceEmbedding
from AISimuToolKit.store.logger import Logger


class Memory:
    """
    Memory is stored as text, stored in variables, stored in the corresponding agent folder as append, and exported to a file when export_memory is called
    Memories are stored as experience
    """

    # TODO interactant seems to be an uncommon/incorrect word. Consider replacing it
    def __init__(self, memory_path: str, extra_columns: List[str] = None):
        """
        The memory store, retrieve, and export modules
        can add additional columns with the extra_columns argument
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

        # TODO Replace it with timestep
        self.curr_id = 0

    def add_column(self, column_name: str) -> None:
        if column_name not in self.memory_df.columns:
            self.memory_df[column_name] = None
            self.logger.info("Add column {} to memory".format(column_name))

    def remove_column(self, column_name: str) -> None:
        if column_name in self.memory_df.columns:
            self.memory_df.drop(column_name, axis=1, inplace=True)
            self.logger.info("Remove column {} from memory".format(column_name))

    # TODO Whether need to display the interaction object, the natural language description seems to be OK, for now all set to blank
    def store(self, timestep: TimeStep = None, experience: str = None, question: str = None, answer: str = None,
              interactant: str = '', source: str = None, importance: float = 5, *args, **kwargs) -> object:
        """
        Store memory, where either pair of experience, [question, answer] can be empty, but not both. 
        q and a must be supplied simultaneously
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
            last_row = self.memory_df.drop(["similarity", "embedding", "recentness", "score"], axis=1).tail(1)
            json_object = last_row.to_json(orient='records')
            f.write(json_object[1:-1] + "\n")

        # self.export_memory()

    def retrieve_by_interactant(self, interactant: str) -> list[dict]:
        """
        Retrieve memories based on interactive objects
        :param interactant:
        :return:
        """
        return self.memory_df[self.memory_df["interactant"] == interactant].to_dict(orient="records")

    def retrieve_by_recentness(self, num=1) -> list[dict]:
        """
        Retrieve and return based on recent
        :param num:
        :return:
        """
        return self.memory_df.sort_values(by="id", ascending=False).head(num).to_dict(orient="records")

    # TODO The format step needs to deal with int and string issues
    def custom_retrieve(self, condition: dict, num=-1) -> list[dict]:
        """
        Customize search criteria
        :param condition:
        :param num: -1 means return all
        :return:
        """
        num = len(self.memory_df) if num == -1 else num
        query_str = ' & '.join([f"{k}=='{v}'" for k, v in condition.items()])
        return self.memory_df.query(query_str).head(num).to_dict(orient="records")

    def export_memory(self):
        """
        Export memories to a file
        :return:
        """

        df = self.memory_df.drop(["similarity", "embedding", "recentness", "score"], axis=1)
        with open(self.memory_path, 'w') as f:
            for line in df.to_dict(orient='records'):
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def retrieve_by_query(self, weights: dict, num: int = 10, query: str = None) -> list[dict]:
        """
        Search by weight
        :param query:
        :param weights:
        :param num:
        :return:
        """
        def compute_score(row):
            score = 0
            for col in row.index:
                if col in dropped_weights.keys() and isinstance(row[col], (int, float)):
                    score += row[col] * dropped_weights.get(col, 0)
            return score

        dropped_weights = weights.copy()
        dropped_weights.pop("similarity", None)
        if "similarity" in weights.keys() and query is not None and query != "":
            query_embedding = self.bert.encode(query)
            cos_sim = 1 - pairwise_distances(query_embedding.reshape(1, -1), self.memory_df["embedding"].tolist(),
                                             metric="cosine")
            self.memory_df["similarity"] = cos_sim.reshape(-1)
            dropped_weights = weights
        self.memory_df['score'] = self.memory_df.apply(compute_score, axis=1)

        num = len(self.memory_df) if num == -1 else num
        return self.memory_df.sort_values(by="score", ascending=False).head(num).to_dict(orient="records")
