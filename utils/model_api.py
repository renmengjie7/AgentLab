"""
@author: Guo Shiguang
@software: PyCharm
@file: model_api.py
@time: 2023/4/17 8:33
"""
import openai
import collections

from store.text.logger import Logger


class ApiRegister(dict):
    def __init__(self):
        super().__init__()
        self._dict = {}

    def register(self, name):
        def wrapper(api_class):
            self._dict[name] = api_class
            return api_class

        return wrapper

    def list_members(self):
        return list(self._dict.keys())


# TODO 调整为model和toolkit继承不同的基类，但都继承自ApiBase
class ApiBase:
    def __init__(self, *args, **kwargs):
        self.target = None
        self.logger = Logger()

    def get(self, **kwargs):
        raise NotImplementedError

    def post(self, **kwargs):
        raise NotImplementedError

    def chat(self, **kwargs):
        raise NotImplementedError

    def finetune(self, **kwargs):
        raise NotImplementedError

    def get_backend(self):
        raise NotImplementedError

    def get_target(self):
        return self.target


# @ModelApiRegister.register("chatgpt")
class GPT_35_API(ApiBase):
    def finetune(self, **kwargs):
        logger = Logger()
        logger.warning("GPT-3.5 does not support finetune")

    def __init__(self, config=None, *args, **kwargs):
        # TODO 自己的不需要导入key
        # self.api_key=config.key
        super().__init__(config)
        self.temp = config.get("temp", 0.7)
        self.target = kwargs.get("agent_id")
        openai.api_base = "http://8.219.106.213:5556/v1"
        openai.api_key = ""

    # TODO 加入多轮对话
    # TODO 设置system
    # TODO 测试长对话，目前没有找到返回为length的例子
    def chat(self, content: str, *args, **kwargs):
        # https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
        # 返回结果为
        # {
        #     "id": "chatcmpl-76DCzykJS606GA3ZmbELzI5SOelwJ",
        #     "object": "chat.completion",
        #     "created": 1681715097,
        #     "model": "gpt-3.5-turbo-0301",
        #     "usage": {
        #         "prompt_tokens": 10,
        #         "completion_tokens": 9,
        #         "total_tokens": 19
        #     },
        #     "choices": [
        #         {
        #             "message": {
        #                 "role": "assistant",
        #                 "content": "Hello! How may I assist you today?"
        #             },
        #             "finish_reason": "stop",
        #             "index": 0
        #         }
        #     ]
        # }
        # TODO 详细处理返回内容
        self.logger.info("GPT-3.5-turbo: chat start")
        agent_id = kwargs.get("agent_id", "")
        message = [
            {"role": "user", "content": content}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
        )
        # TODO 处理choices大于一的情况

        answer = completion["choices"][0]["message"]["content"]

        while True:
            if completion["choices"][0]["finish_reason"] == "content_filter":
                self.logger.warning("GPT-3.5-turbo: chat terminated by content filter")
                if agent_id is not None:
                    self.logger.warning("GPT-3.5-turbo: agent_id triggers the problem is '{}'".format(agent_id))
                self.logger.warning("GPT-3.5-turbo: message triggers the problem is '{}'".format(content))
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
                self.logger.error("GPT-3.5-turbo: message triggers the problem is '{}'".format(content))
                break

        return answer

    def get_backend(self):
        return "gpt-3.5-turbo"


# TODO 实现ChatGlmAPI
class ChatGLMAPI(ApiBase):
    """

    """

    def post(self, **kwargs):
        pass

    def chat(self, **kwargs):
        pass

    def finetune(self, **kwargs):
        pass

    def get_backend(self):
        return "chatglm"

    def get(self, **kwargs):
        pass


class CustomModelApi(ApiBase):
    def __init__(self, config=None, *args, **kwargs):
        super().__init__(config)
        self.model_config = config
        self.target = kwargs.get("agent_id")

    def finetune(self, **kwargs):
        pass

    def chat(self, message: str, *args, **kwargs):
        pass

    def get_backend(self):
        return "custom"


class ExternalToolkitApi(ApiBase):
    def __init__(self, toolkit_config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toolkit_config = toolkit_config
        self.toolkit_api = toolkit_config["api"]
        self.target_name = toolkit_config["target"]

    def chat(self, message: str, *args, **kwargs):
        """

        :param message:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def get_backend(self):
        return self.toolkit_config["name"]

    def transfor_name2id(self, name2id):
        self.target_id = [name2id[item] for item in self.target_name]


class RecommendSystemApi(ExternalToolkitApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_recommend(self, id: int, message: str, *args, **kwargs) -> str:
        """

        :param id:
        :param message:
        :param args:
        :param kwargs:
        :return:
        """
        pass


# TODO use userdict
ModelNameDict = {"chatgpt": GPT_35_API, "gpt3.5": GPT_35_API, "gpt3.5turbo": GPT_35_API}
ToolkitNameDict = {"recommend": RecommendSystemApi}


# TODO 修正custom和finetune的关系
def get_model_apis(agnet_model_dict: dict):
    model_register = ApiRegister()
    for agent_id, model_settings in agnet_model_dict.items():
        inner_model_name = ModelNameDict[model_settings["model_name"]]
        if model_settings["fine_tune"]:
            model_register[int(agent_id)] = CustomModelApi(config=model_settings["config"], agnet_id=agent_id)
        else:
            model_register[int(agent_id)] = inner_model_name(config=model_settings["config"], agent_id=agent_id)
    return model_register


def get_toolkit_apis(toolkit_list: list):
    toolkit_api_register = ApiRegister()
    for item in toolkit_list:
        toolkit_api_register[item["name"]] = ExternalToolkitApi(toolkit_config=item["config"])

    for item in toolkit_api_register.values():
        item.transfor_name2id(toolkit_api_register)

    return toolkit_api_register
