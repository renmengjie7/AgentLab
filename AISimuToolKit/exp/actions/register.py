from AISimuToolKit.exp.actions import base_action
from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.exp.actions.base_action import BaseAction
import os
import importlib
import inspect


def register_dir(expe: Experiment,
                 path: str) -> dict:
    """
    注册某个目录下的原子操作
    :param expe:
    :param action_path:
    """
    actions= {}
    # defalut
    if 'AISimuToolKit/exp/actions' in path:
        module = 'AISimuToolKit.exp.actions.'
    else:
        module = path.replace('/', '.')
        module = '' if module=='.' else module+"."
    for file in os.listdir(path):
        if file.endswith('_action.py'):
            module_name = (module + file[:-3]).replace('...', '')
            module_name = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module_name):
                if inspect.isclass(obj) and issubclass(obj, BaseAction):
                    actions[name] = obj(expe)
    return actions



def register_action(expe: Experiment, 
                    default: bool=True,
                    action_path: str=None) -> dict:
    """
    遍历指定目录下所有文件，将所有action类注册到actions字典中
    action_path中同名的原子操作会覆盖默认的
    :param default 需要对提供的默认原子操作进行注册
    :param expe:
    :param action_path:用户自定义, 请提供相对路径
    :return:
    """
    # 需要使用默认的原子操作
    actions = {}
    if default:
        actions.update(register_dir(expe=expe, 
                                    path=os.path.dirname(inspect.getfile(base_action))))
    if action_path is not None:
        actions.update(register_dir(expe=expe, 
                                    path=action_path))
    return actions
