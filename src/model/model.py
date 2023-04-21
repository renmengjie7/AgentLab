import openai
import requests
from typing import List
from src.store.text.logger import Logger
from src.utils.utils import get_file_stream


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

    def get_backend(self):
        raise NotImplementedError


class PublicApiBase(ApiBase):
    """公开的, 只能chat"""
    
    def finetune(self, *args, **kwargs):
        self.logger.warning("{} does not support finetune".format(self.get_backend()))
    


# @ModelApiRegister.register("chatgpt")
class GPT_35_API(PublicApiBase):
    
    def __new__(cls, 
                config=None, 
                url: str="http://8.219.106.213:5556/v1", 
                *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            openai.api_base = url
            openai.api_key = ""
        return cls._instance

    # TODO 加入多轮对话
    # TODO 设置system
    # TODO 测试长对话，目前没有找到返回为length的例子
    def chat(self, query: str, config: dict, *args, **kwargs):
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
        self.logger.info("GPT-3.5-turbo: chat start")
        agent_id = kwargs.get("agent_id", "")
        message = [
            {"role": "user", "content": query}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=config['temperature']
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
                self.logger.info(
                    "GPT-3.5-turbo: chat stop abnormally due to length limit,sending continue automatically")
                message.append({"role": "assistant", "content": answer})
                message.append({"role": "user", "content": "continue"})
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=message,
                )
                answer = answer + " " + completion["choices"][0]["message"]["content"]
            elif completion["choices"][0]["finish_reason"] == "stop":
                self.logger.info("GPT-3.5-turbo: chat stop normally")
                break
            else:
                self.logger.error("GPT-3.5-turbo: chat stop abnormally")
                self.logger.error("GPT-3.5-turbo: message triggers the problem is '{}'".format(query))
                break
        return answer

    def get_backend(self):
        return "gpt-3.5-turbo"


class PrivateApiBase(ApiBase):
    """自己部署的, 可以finetune"""
    
    def __new__(cls, urls: List[str], *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.urls = {url: None for url in urls}
        return cls._instance
        
    # TODO 维护一个字典, 采用某种策略选择url去chat或finetune以使最少load, 高效运行
    def get_url(self, exp: str, agent: str):
        """
        从urls中选择一个代价最小的
        """
        return self.urls.keys[0]


# TODO 实现ChatGlmAPI
class ChatGLMAPI(PrivateApiBase):

    def chat(self, *args, **kwargs):
        pass

    def finetune(self, *args, **kwargs):
        pass

    def get_backend(self):
        return "ChatGlm"


class LLaMAAPI(PrivateApiBase):

    def finetune(self, exp: str, agent: str, file: str) -> str:
        """
        LLaMA的数据格式是
        [{ "instruction": "Give three tips for staying healthy.",
        "input": "", "output": "1. Eat a balanced }]
        :param url:
        :param agent:
        :param exp:
        :param file是文件路径
        """
        url = self.get_url(exp=exp, agent=agent)
        files = {'file': get_file_stream(file=file)}
        params = {"exp": exp, "agent": agent}
        response = requests.post(url, params=params, files=files)
        # TODO 测试一下返回值
        self.logger.info(response)
        return response

    def chat(self, 
             exp: str, agent: str, 
             query: str, instruction: str, 
             history: list):
        # TODO 暂不支持history 还没使用
        url = self.get_url()
        params = {
            "exp": exp, "agent": agent, 
            "query": query, "instruction": instruction
        }
        response = requests.post(url, params=params, data=history)
        # TODO 测试一下返回值
        print(response)
        return response

    def get_backend(self):
        return "LLaMA"
