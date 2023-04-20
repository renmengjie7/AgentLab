from typing import List

from src.exp.actions.base_action import BaseAction


class ProbeAction(BaseAction):
    """
    运行过程中通过对话的形式检查agent的状态，该动作不会影响agent
    """

    def __init__(self, expe_info):
        super().__init__(expe_info)

    def run(self, probes: List[dict], *args, **kwargs):
        """
        为多个agent下达指令
        :param probes:["agent_id":agent_id,"message":message","save":save_in_memory]
        :param args:
        :param kwargs:
        :return:
        """
        for item in probes:
            agent_id = int(item["agent_id"])
            message = item["message"]
            save_in_memory = item["save"]
            answer = self.expe_info.models[agent_id].chat(message)
            self.logger.history("user: {}".format(message))
            self.logger.history("agent_{}: {}".format(agent_id, answer))
            if save_in_memory:
                self.expe_info.agents[agent_id].memory.store(interactant=agent_id, question=message, answer=answer)
            return answer
