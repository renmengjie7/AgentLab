"""
@author: Guo Shiguang
@software: PyCharm
@file: embedding.py
@time: 2023/4/25 10:35
"""

from threading import Lock

import torch
from transformers import BertTokenizer, BertModel


class BertSentenceEmbedding:
    __instance = None
    __lock = Lock()

    def __new__(cls, device='cuda'):
        if not BertSentenceEmbedding.__instance:
            with BertSentenceEmbedding.__lock:
                if not BertSentenceEmbedding.__instance:
                    instance = super().__new__(cls)
                    instance.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
                    instance.device = torch.device(device) if torch.cuda.is_available() else torch.device('cpu')
                    instance.model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states=True).to(
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
