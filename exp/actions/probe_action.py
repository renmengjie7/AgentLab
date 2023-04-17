from exp.actions.base_action import BaseAction


class ProbeAction(BaseAction):
    """
    运行过程中通过对话的形式检查agent的状态，该动作不会影响agent
    """

    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        pass
