"""
@author: Guo Shiguang
@software: PyCharm
@file: model_api.py
@time: 2023/4/17 8:33
"""
import openai
import collections


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


class ApiBase:
    def __init__(self, config=None, *args, **kwargs):
        self.target = config.get("target", "global")

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
    def __init__(self, config=None, *args, **kwargs):
        # TODO 自己的不需要导入key
        # self.api_key=config.key
        super().__init__(config)
        self.temp = config.get("temp", 0.7)
        self.target = kwargs.get("agent_id")
        openai.api_base = "http://8.219.106.213:5556/v1"
        openai.api_key = ""

    def chat(self, message: str, *args, **kwargs):
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
        content = message
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": content}
            ]
        )
        return completion

    def get_backend(self):
        return "gpt-3.5-turbo"
    
    
# TODO 
class ChatGLM_API(ApiBase):
    """_summary_

    Args:
        ApiBase (_type_): _description_

    Returns:
        _type_: _description_
    """


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
        self.target = toolkit_config["target"]

    def chat(self, message: str, *args, **kwargs):
        pass

    def get_backend(self):
        return self.toolkit_config["name"]


# TODO use userdict
ModelNameDict = {"chatgpt": GPT_35_API, "gpt3.5": GPT_35_API, "gpt3.5turbo": GPT_35_API}


def get_model_apis(agnet_model_dict: dict):
    model_register = ApiRegister()
    for agent_id, model_settings in agnet_model_dict.items():
        inner_model_name = ModelNameDict[model_settings["model_name"]]
        print(inner_model_name.__name__)
        if model_settings["fine_tune"]:
            model_register[str(agent_id)] = CustomModelApi(config=model_settings["config"], agnet_id=agent_id)
        else:
            model_register[str(agent_id)] = inner_model_name(model_config=model_settings["config"], agent_id=agent_id)
    return model_register


def get_toolkit_apis(toolkit_dict: dict):
    toolkit_api_register = ApiRegister()
    for toolkit_name, toolkit_config in toolkit_dict.items():
        toolkit_api_register[toolkit_name] = toolkit_config["api"]

    return toolkit_api_register
