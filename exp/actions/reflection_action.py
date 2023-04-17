from exp.actions.base_action import BaseAction


class ReflectionAction(BaseAction):
    """
    手动令agent进行反思，有助于agent的学习
    """

    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        pass
