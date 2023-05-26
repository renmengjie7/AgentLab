"""
@author: Guo Shiguang
@software: PyCharm
@file: embedding.py
@time: 2023/4/25 10:35
"""
import os
from abc import ABC, abstractmethod

import numpy
import openai
import torch
from transformers import BertTokenizer, BertModel


class BaseEmbedding(ABC):
    @abstractmethod
    def encode(self, sentence):
        pass


class BertSentenceEmbedding(BaseEmbedding):
    __instance = None

    def __new__(cls, device='cuda'):
        if not BertSentenceEmbedding.__instance:
            instance = super().__new__(cls)
            instance.tokenizer = BertTokenizer.from_pretrained('embedding_model-base-uncased')
            instance.device = torch.device(device) if torch.cuda.is_available() else torch.device('cpu')
            instance.model = BertModel.from_pretrained('embedding_model-base-uncased', output_hidden_states=True).to(
                instance.device)
            instance.model.eval()
            BertSentenceEmbedding.__instance = instance
        return BertSentenceEmbedding.__instance

    def encode(self, sentence):
        input_ids = torch.tensor(self.tokenizer.encode(sentence, add_special_tokens=True, truncation=True)).unsqueeze(
            0).to(self.device)
        with torch.no_grad():
            outputs = self.model(input_ids)
            embeddings = outputs[2][-1][0]
            sentence_embedding = torch.mean(embeddings, dim=0)
            torch.cuda.empty_cache()
        return sentence_embedding.cpu().numpy()


class OpenAIEmbedding(BaseEmbedding):
    _instance = None

    # TODO 需要测试赋值过程
    def __new__(cls, openai_embedding_settings: dict = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if openai_embedding_settings is not None:
                openai.api_base = openai_embedding_settings.get("api_base", None)
                openai.api_key = openai_embedding_settings.get("api_key", None)
                openai.organization = openai_embedding_settings.get("organization", None)
                openai.proxy = openai_embedding_settings.get("proxy", None)
            else:
                openai.api_base = os.environ.get('OPENAI_API_BASE')
                openai.api_key = os.environ.get('OPENAI_API_KEY')
                openai.organization = os.environ.get('OPENAI_ORGANIZATION')
                openai.proxy = os.environ.get('OPENAI_PROXY')
        return cls._instance

    def encode(self, sentence):
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=sentence
        )

        return numpy.array(response["data"][0]["embedding"])
