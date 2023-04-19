from exp.actions.base_action import BaseAction
from exp.expe_info import ExpeInfo


class ProbeAction(BaseAction):
    """
    运行过程中通过对话的形式检查agent的状态，该动作不会影响agent
    """

    def __init__(self, expe_info):
        super().__init__(expe_info)

    def run(self, probes: list[dict], *args, **kwargs):
        for item in probes:
            agent_id = int(item["agent_id"])
            message = item["message"]
            answer = self.expe_info.models[agent_id].chat(message)
            return answer
