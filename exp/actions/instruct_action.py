from exp.actions.base_action import BaseAction


class InstructionAction(BaseAction):
    """
    给agent下发指令，该指令会影响agent
    """

    def __init__(self, instruction, config):
        super().__init__(config)
        self.instruction = instruction

    def run(self, *args, **kwargs):
        pass
