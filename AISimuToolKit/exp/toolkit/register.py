from AISimuToolKit.exp.toolkit.toolkit import RecommendSystemApi, ExternalToolkitApi
from AISimuToolKit.model.register import ApiRegister


ToolkitNameDict = {"recommend": RecommendSystemApi}


def get_toolkit_apis(toolkit_list: list):
    toolkit_api_register = ApiRegister()
    for item in toolkit_list:
        toolkit_api_register[item["name"]] = ExternalToolkitApi(toolkit_config=item["config"])

    for item in toolkit_api_register.values():
        item.transfor_name2id(toolkit_api_register)

    return toolkit_api_register
