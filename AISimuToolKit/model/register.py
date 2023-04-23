from typing import List

from AISimuToolKit.model.model import GPT_35_API, ChatGLMAPI, LLaMAAPI
from AISimuToolKit.utils.utils import parse_yaml_config

# TODO use userdict 有一种解决方案是放到ApiBase的init函数中
ModelNameDict = {"GPT-3.5-turbo": GPT_35_API,
                 "LLaMA": LLaMAAPI,
                 "ChatGLM": ChatGLMAPI}


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


def get_model_by_name(ModelNameDict: dict, name: str):
    """_summary_ 根据model的名称找到model类

    Args:
        ModelNameDict (dict): _description_
        name (str): _description_
    """
    if name not in ModelNameDict.keys():
        raise Exception("Only support " + ", ".join(
            [f"{key} for {ModelNameDict[key].get_backend()}" for key in ModelNameDict.keys()]))
    return ModelNameDict[name]


# TODO ModelNameDict: 这里如何要自定义, 需要对ModelNameDict进行patch
def get_model_apis(exp_id: str, agents: List[int], model_names: List[str], model_config: str, ):
    """
    给每个agent找到对应的model
    :param exp_id:
    :param agents: agent的list
    :param model_names:
    :param model_config:
    :return:
    """
    # 从配置文件中解析出模型对应的url
    conf = parse_yaml_config(path=model_config)
    model_register = ApiRegister()
    for idx, model_name in enumerate(model_names):
        inner_model_name = get_model_by_name(ModelNameDict, model_name)
        model_register[idx] = inner_model_name(exp=exp_id,
                                               agents=agents,
                                               config=conf[model_name],
                                               urls=conf[model_name]['url'])
    return [model_register[key] for key in model_register.keys()]
