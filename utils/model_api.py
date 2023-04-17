"""
@author: Guo Shiguang
@software: PyCharm
@file: model_api.py
@time: 2023/4/17 8:33
"""
import openai
import collections


class ModelApiRegister(dict):
    def __init__(self):
        super().__init__()
        self._dict = {}

    def register(self, name):
        def wrapper(model_class):
            self._dict[name] = model_class
            return model_class

        return wrapper

    def list_models(self):
        return list(self._dict.keys())


class ModelApiBase:
    def get(self, **kwargs):
        raise NotImplementedError

    def post(self, **kwargs):
        raise NotImplementedError

    def chat(self, **kwargs):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__.replace("_API", "")

    def __repr__(self):
        return self.__str__()


# @ModelApiRegister.register("chatgpt")
class GPT_35_API(ModelApiBase):
    def __init__(self, model_config=None):
        # TODO 自己的不需要导入key
        # self.api_key=config.key
        self.temp = model_config.get("temp", 0.7)
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
        content = message
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": content}
            ]
        )
        return completion


class CustomModelApi(ModelApiBase):
    def __init__(self, model_config=None):
        self.model_config = model_config

    def finetune(self, **kwargs):
        pass

    def chat(self, message: str, *args, **kwargs):
        pass


# TODO use userdict
ModelNameDict = {"chatgpt": GPT_35_API, "gpt3.5": GPT_35_API, "gpt3.5turbo": GPT_35_API}


def get_model_apis(agnet_model_dict: dict):
    # 让我们约定，对于每个agent，都会新建一个model_name，名称为agent_id_F/P_model_name，其中F表示finetune，P表示prompt
    # 例如，agent_id=0，Fine_tune=True,model_name=gpt3.5，那么就会新建一个model_api，名称为0_F_gpt35
    # 例如，agent_id=0，Fine_tune=False,model_name=gpt3.5，那么就会新建一个model_api，名称为0_P_gpt35
    model_register = ModelApiRegister()
    for agent_id, model_settings in agnet_model_dict.items():
        inner_model_name = ModelNameDict[model_settings["model_name"]]
        print(inner_model_name.__name__)
        if model_settings["fine_tune"]:
            model_name = "{agent_id}_{method}_{inner_model_name}".format(agent_id=agent_id, method="F",
                                                                         inner_model_name=inner_model_name.__name__)
            model_register[model_name] = CustomModelApi(model_config=model_settings["config"])
        else:
            model_name = "{agent_id}_{method}_{inner_model_name}".format(agent_id=agent_id, method="P",
                                                                         inner_model_name=inner_model_name.__name__)
            print(model_name)
            model_register[model_name] = inner_model_name(model_config=model_settings["config"])
    return model_register
