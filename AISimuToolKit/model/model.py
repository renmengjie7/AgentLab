import json
import os
from typing import List
import copy
import openai
import requests

from AISimuToolKit.store.logger import Logger


def rawtext2dialog(text: str):
    """_summary_ 纯文本转成对话形式

    Args:
        text (str): _description_
    """
    model = GPT_35_API()
    answer = model.chat(query='Please convert the following text to a single round and save as much information as possible in the format {"query": "", "answer": ""} Please note the single round, only a single json will do'+text)
    diaglogue = json.loads(answer)
    if 'query' in diaglogue and 'answer' in diaglogue:
        pass
    else:
        raise Exception('convert raw text to diaglogue failed')
    return diaglogue


# TODO 调整为model和toolkit继承不同的基类，但都继承自ApiBase
class ApiBase:
    _instance = None  # 类变量用于存储单例实例

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if not hasattr(cls, 'logger'):
            cls.logger = Logger()
        return cls._instance

    def chat(self, *args, **kwargs):
        raise NotImplementedError

    def finetune(self, *args, **kwargs):
        """_summary_ 对某个实验下某个agent使用某个文件finetune
        
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @classmethod
    def get_backend(cls):
        raise NotImplementedError


class PublicApiBase(ApiBase):
    """公开的, 只能chat"""

    def finetune(self, *args, **kwargs):
        self.logger.warning("{} does not support finetune".format(self.get_backend()))
        raise NotImplementedError


# @ModelApiRegister.register("chatgpt")
class GPT_35_API(PublicApiBase):

    def __new__(cls,
                config: dict=None,
                *args, **kwargs):
        """config为None只有在已经实例化后才能正常init时"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            openai.api_base = config['url'][0]
            openai.api_key = config['key'][0]
        return cls._instance

    # TODO 加入多轮对话
    # TODO 设置system
    # TODO 测试长对话，目前没有找到返回为length的例子
    def chat(self, query: str, config: dict=None, *args, **kwargs):
        """
                https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
        返回结果为
        {
            "id": "chatcmpl-76DCzykJS606GA3ZmbELzI5SOelwJ",
            "object": "chat.completion",
            "created": 1681715097,
            "model": "gpt-3.5-turbo-0301",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 9,
                "total_tokens": 19
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How may I assist you today?"
                    },
                    "finish_reason": "stop",
                    "index": 0
                }
            ]
        }
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
        # TODO 处理choices大于一的情况

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
    """自己部署的, 可以finetune"""

    def __new__(cls, config: dict, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.urls = {url: None for url in config['url']}
        return cls._instance

    # TODO 维护一个字典, 采用某种策略选择url去chat或finetune以使最少load, 高效运行
    def get_url(self, exp: str, agent: str = None):
        """
        从urls中选择一个代价最小的
        TODO agent=None表示这个实验还没创建...是否需要负载均衡地将每个实验放到不同的url上, 还是在每个url上复制一份
        """
        return list(self.urls.keys())[0]

    @classmethod
    def memory2finetunedata(cls, datas: List[dict], *args, **kwargs):
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
        """_summary_  

        Args:
            exp (str): _description_ 实验ID
            agents (List[str]): _description_ agents的IDs

        Returns:
            _type_: _description_
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, config=config)
        cls._instance.new_exp(exp=exp, agents=agents)
        return cls._instance

    def new_exp(self, exp: str, agents: List[str]) -> bool:
        """_summary_ 对接部署服务, 存储文件

        Args:
            exp (str): _description_
            agents (List): _description_
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
        LLaMA的数据格式是
        [{ "instruction": "Give three tips for staying healthy.",
        "message": "", "output": "1. Eat a balanced "}]
        :param config:
        :param agent:
        :param exp:
        :param path: 为agent的路径
        :param datas: 为记忆
        """
        file_path = self.memory2finetunedata(_datas=datas, path=path)

        url = self.get_url(exp=exp, agent=agent)
        files = {'file': open(file_path, 'rb')}
        params = {"exp": exp, "agent": agent}
        for key in config:
            params[key] = config[key]
        response = requests.post(f'{url}/finetune', params=params, files=files)
        # TODO 测试一下返回值
        if json.loads(response.text)['code'] == 'success':
            return True
        else:
            raise Exception(f'{self.get_backend()} failed to finetune exp_{exp} agent_{agent} in {url} server !')

    def chat(self,
             exp: str, agent: str,
             query: str, instruction: str = None,
             history: list = [],
             *args, **kwargs):
        # 在LLaMA中, instruction+query实际上对应其他模型的query
        # TODO 暂不支持history 还没使用
        url = self.get_url(exp=exp, agent=agent)
        params = {
            "exp": exp, "agent": str(agent),
            "query": '', "instruction": query
        }
        response = requests.post(f'{url}/chat', params=params, json=history)
        # TODO 测试一下返回值
        return json.loads(response.text)['response']

    @classmethod
    def get_backend(cls):
        return "LLaMA"

    @classmethod
    def memory2finetunedata(cls, _datas: List[dict], path: str, *args, **kwargs) -> str:
        """_summary_ 将memory格式的数据转成模型特定的处理

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
