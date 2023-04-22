from AISimuToolKit.exp.actions.base_action import BaseAction
from AISimuToolKit.exp.experiment import Experiment
from typing import List


class ReflectionAction(BaseAction):
    """
    手动令agent进行反思，有助于agent的学习
    """

    def __init__(self, expe: Experiment):
        super().__init__(expe)

    def run(self, 
            reflections: List[dict], *args, **kwargs):
        """
        : param reflections [{"num":num,"input":bool, "output": bool, "prompt": prompt}]
        对最近的多少条进行反思? 
        """
        # 一个简单的反思
        for item in reflections:
            self.reflect(agent_id=int(item["agent_id"]), 
                         num=int(item["num"]),
                         input=item["input"],
                         output=item['output'],
                         prompt=item['prompt'])

    # TODO 这个反思的reflect感觉比较私人订制, 是否加入时间?
    def reflect(self, 
                agent_id: int,
                num: int,
                input: bool = False,
                output: bool = True,
                prompt: str = "Your name is {}\n Your profile: {}. How do you think your profile has changed over the course of your recent experience? Here's your experience: \n"):
        recent_memory = self.expe.agents[agent_id].memory.retrive_by_recentness(num)
        
        name = self.expe.agents[agent_id].name
        profile = ''.join(self.expe.agents[agent_id].profile)
        prompt = prompt.format(name, profile)
        # 拼接memory
        if input and output:
            content = prompt+"\n".join("question: {} ; answer: {}".format(item['question'], item['answer']) for item in recent_memory)
        elif input:
            content = prompt+"\n".join(item['question'] for item in recent_memory)
        elif output:
            content = prompt+"\n".join(item['answer'] for item in recent_memory)
        else:
            raise Exception()
        
        answer = self.expe.models[agent_id].chat(query=content,
                                                 exp=self.expe.id,
                                                 agent=agent_id,
                                                 config=self.expe.agents[agent_id].config)
        self.logger.history("user: {}".format(content))
        self.logger.history("agent_{}: {}".format(agent_id, answer))
        return answer
