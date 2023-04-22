from typing import List

from AISimuToolKit.exp.actions.base_action import BaseAction

# TODO 探测的prompt应该需要实现可配置
class ProbeAction(BaseAction):
    """
    运行过程中通过对话的形式检查agent的状态，该动作不会影响agent
    """

    def __init__(self, expe):
        super().__init__(expe)

    def run(self, probes: List[dict], *args, **kwargs):
        """
        为多个agent下达指令
        :param probes:[{"agent_id":agent_id,"input":input, "prompt": prompt}]
        :param args:
        :param kwargs:
        :return:
        """
        answers = []
        for item in probes:
            agent_id = int(item["agent_id"])
            input = item["input"]
            answer = self.probe(agent_id=agent_id, input=input, prompt=item["prompt"])
            answers.append(answer)
        return answers

    def probe(self,
              agent_id: str,
              input: str,
              prompt: str="Your name is {}\n Your profile: {}. Now I will interview you. \n{}"):
        """_summary_ 采访, 不会留下记忆

        Args:
            agent_id (str): _description_
            input (str): _description_
            prompt (_type_, optional): _description_. Defaults to "Your name is {}\n Your profile: {}. Now I will interview you. \n{}". 需要根据任务自己设计

        Returns:
            _type_: _description_ 
        """
        name = self.expe.agents[agent_id].name
        profile = ''.join(self.expe.agents[agent_id].profile)
        whole_input = prompt.format(name, profile, input)
        answer = self.expe.models[agent_id].chat(query=whole_input,
                                                 exp=self.expe.id,
                                                 agent=agent_id,
                                                 config=self.expe.agents[agent_id].config)
        self.logger.history("user probe: {}".format(input))
        self.logger.history("whole input:\n {}".format(whole_input))
        self.logger.history("agent_{}: {}".format(agent_id, answer))
        return answer
