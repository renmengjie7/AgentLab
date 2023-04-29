import copy
import json
import os
from typing import List

import openai
import requests

from AISimuToolKit.store.logger import Logger


def rawtext2dialog(text: str):
    """
    Plain text to conversational form
    :param text:
    :return:
    """
    model = GPT_35_API()
    answer = model.chat(
        query='Please convert the following text to a single round and save as much information as possible in the format {"query": "", "answer": ""} Please note the single round, only a single json will do' + text)
    diaglogue = json.loads(answer)
    if 'query' in diaglogue and 'answer' in diaglogue:
        pass
    else:
        raise Exception('convert raw text to diaglogue failed')
    return diaglogue


class ApiBase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if not hasattr(cls, 'logger'):
            cls.logger = Logger()
        return cls._instance

    def chat(self, *args, **kwargs):
        raise NotImplementedError

    def finetune(self, *args, **kwargs):
        """
        Use a specific file under a specific experiment to finetune for an agent
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def get_backend(cls):
        raise NotImplementedError


class PublicApiBase(ApiBase):
    """
    public model such as chatgpt,which means you can't finetune it
    """

    def finetune(self, *args, **kwargs):
        self.logger.warning("{} does not support finetune".format(self.get_backend()))
        raise NotImplementedError


# @ModelApiRegister.register("chatgpt")
class GPT_35_API(PublicApiBase):

    def __new__(cls,
                config: dict = None,
                *args, **kwargs):
        """config为None只有在已经实例化后才能正常init时
        if config is None, init is normal only when it has been instantiated
        """
        if config is None and cls._instance is None:
            raise Exception('config is None, please init first')
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            openai.api_base = config['url'][0]
            openai.api_key = config['key'][0]
        return cls._instance

    def chat(self, query: str, config: dict = None, *args, **kwargs):
        """
        https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
        """
        self.logger.debug("GPT-3.5-turbo: chat start")
        agent_id = kwargs.get("agent_id", "")
        message = [
            {"role": "user", "content": query}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=0.7 if config is None else config['temperature']
        )

        answer = completion["choices"][0]["message"]["content"]

        while True:
            if completion["choices"][0]["finish_reason"] == "content_filter":
                self.logger.warning("GPT-3.5-turbo: chat terminated by content filter")
                if agent_id is not None:
                    self.logger.warning("GPT-3.5-turbo: agent_id triggers the problem is '{}'".format(agent_id))
                self.logger.warning("GPT-3.5-turbo: message triggers the problem is '{}'".format(query))
                break
            elif completion["choices"][0]["finish_reason"] == "length":
                self.logger.debug(
                    "GPT-3.5-turbo: chat stop abnormally due to length limit,sending continue automatically")
                message.append({"role": "assistant", "content": answer})
                message.append({"role": "user", "content": "continue"})
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=message,
                )
                answer = answer + " " + completion["choices"][0]["message"]["content"]
            elif completion["choices"][0]["finish_reason"] == "stop":
                self.logger.debug("GPT-3.5-turbo: chat stop normally")
                break
            else:
                self.logger.error("GPT-3.5-turbo: chat stop abnormally")
                self.logger.error("GPT-3.5-turbo: message triggers the problem is '{}'".format(query))
                break
        return answer

    @classmethod
    def get_backend(cls):
        return "GPT-3.5-turbo"


class PrivateApiBase(ApiBase):
    """
    private model such as chatglm,which means you can finetune it
    """

    def __new__(cls, config: dict, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.urls = {url: None for url in config['url']}
        return cls._instance

    # TODO 维护一个字典, 采用某种策略选择url去chat或finetune以使最少load, 高效运行
    # Maintain a dictionary and use a strategy for choosing urls to chat or finetune to run with minimal load and efficiency
    def get_url(self, exp: str, agent: str = None):
        """
        Choose the one with the least cost from urls
        TODO agent=None表示这个实验还没创建...是否需要负载均衡地将每个实验放到不同的url上, 还是在每个url上复制一份
        means that the experiment has not been created... Whether you need to load balance each experiment to a different url or make a copy on each url
        """
        return list(self.urls.keys())[0]

    @classmethod
    def memory2finetunedata(cls, _datas: List[dict], path: str, *args, **kwargs):
        raise NotImplementedError


# TODO 实现ChatGlmAPI
class ChatGLMAPI(PrivateApiBase):

    def chat(self, *args, **kwargs):
        pass

    def finetune(self, *args, **kwargs):
        pass

    @classmethod
    def get_backend(cls):
        return "ChatGLM"


class LLaMAAPI(PrivateApiBase):

    def __new__(cls, exp: str, agents: List[str], config: dict, *args, **kwargs):
        """
        :param exp:
        :param agents:
        :param config:
        :param args:
        :param kwargs:
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, config=config)
        cls._instance.new_exp(exp=exp, agents=agents)
        return cls._instance

    def new_exp(self, exp: str, agents: List[str]) -> bool:
        """
        Create experiments in the llama runtime environment
        :param exp:
        :param agents:
        :return:
        """

        url = self.get_url(exp=exp)
        params = {"id": exp, "override": True}
        response = requests.post(url=f'{url}/exp/new', params=params,
                                 json=[str(agent) for agent in agents])
        if json.loads(response.text)['code'] == 'success':
            self.logger.info(f"{self.get_backend()} created exp_{exp} in {url} server !")
            return True
        else:
            raise Exception(f'{self.get_backend()} failed to create exp_{exp} in {url} server !')

    def finetune(self, exp: str, agent: str, config: dict,
                 path: str, datas: List[dict]) -> bool:
        """
        [{ "instruction": "Give three tips for staying healthy.",
        "message": "", "output": "1. Eat a balanced "}]
        :param config:
        :param agent:
        :param exp:
        :param path: agent path
        :param datas: memory
        """
        file_path = self.memory2finetunedata(_datas=datas, path=path)

        url = self.get_url(exp=exp, agent=agent)
        files = {'file': open(file_path, 'rb')}
        params = {"exp": exp, "agent": agent}
        for key in config:
            params[key] = config[key]
        response = requests.post(f'{url}/finetune', params=params, files=files)
        if json.loads(response.text)['code'] == 'success':
            return True
        else:
            raise Exception(f'{self.get_backend()} failed to finetune exp_{exp} agent_{agent} in {url} server !')

    def chat(self,
             exp: str, agent: str,
             query: str, instruction: str = None,
             history: list = [],
             *args, **kwargs):
        # In LLaMA, instruction+query actually corresponds to query for other models
        # TODO history is not supported yet
        url = self.get_url(exp=exp, agent=agent)
        params = {
            "exp": exp, "agent": str(agent),
            "query": '', "instruction": query
        }
        response = requests.post(f'{url}/chat', params=params, json=history)
        return json.loads(response.text)['response']

    @classmethod
    def get_backend(cls):
        return "LLaMA"

    @classmethod
    def memory2finetunedata(cls, _datas: List[dict], path: str, *args, **kwargs) -> str:
        """_summary_ convert memory into model-specific finetune data

        Args:
            datas (_type_): _description_
        """
        datas = copy.deepcopy(_datas)
        results = []
        for data in datas:
            if data['source'] == 'experience':
                try:
                    dialogue = rawtext2dialog(data['experience'])
                    data['question'] = dialogue['query']
                    data['answer'] = dialogue['answer']
                except:
                    continue
            results.append({
                "instruction": data['question'],
                "message": "",
                "output": data['answer']
            })
        path = f'{path}/finetune'
        if not os.path.exists(path):
            os.makedirs(path)
        num = len(os.listdir(path))
        file_path = f'{path}/{num}.jsonl'
        with open(file=file_path, mode='w', encoding="utf-8") as f:
            f.write(json.dumps(results, ensure_ascii=False))
        return file_path
