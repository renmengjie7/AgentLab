from src.store.text.logger import Logger
from src.model.model import GPT_35_API, ChatGLMAPI, LLaMAAPI

# TODO use userdict 有一种解决方案是放到ApiBase的init函数中
ModelNameDict = {"chatgpt": GPT_35_API, "gpt3.5": GPT_35_API, "gpt3.5turbo": GPT_35_API,
                 "llama": LLaMAAPI, 
                 "chatglm": ChatGLMAPI}


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


def get_model_apis(agent_model_dict: dict, ModelNameDict: dict=ModelNameDict):
    """_summary_ 给每个agent找到对应的model

    Args:
        agent_model_dict (dict): _description_ agent的list
        ModelNameDict (dict, optional): _description_. Defaults to ModelNameDict.
                这里如何要自定义, 需要对ModelNameDict进行patch
    Returns:
        _type_: _description_
    """
    model_register = ApiRegister()
    for agent_id, model_settings in agent_model_dict.items():
        inner_model_name = ModelNameDict[model_settings["model_name"]]
        model_register[int(agent_id)] = inner_model_name(config=model_settings["config"])
    model_register[-1] = GPT_35_API(agent_id=-1)
    return model_register
