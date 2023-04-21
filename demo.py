from src.exp.actions import BaseAction
from src.exp.agents.agent import Agent
from src.exp.experiment import Experiment
from src.store.text.logger import Logger
from src.exp.actions import InstructAction, ProbeAction, ReflectionAction


def get_action(exp):
    instructAction = InstructAction(expe=exp)
    probeAction = ProbeAction(expe=exp)
    reflectionAction = ReflectionAction(expe=exp)
    return instructAction, probeAction, reflectionAction

    
def main():
    exp = Experiment.load_exp(file="test/files4test/expe_config.json", 
                              output_dir="experiments")
    instructAction, probeAction, reflectionAction = get_action(exp=exp)
    result = probeAction.probe(agent_id=1, 
                               input='Do you like chinese food ?',
                               prompt="Your name is {}\n Your profile: {}. Now I will interview you. \n{}")
    instructAction.instruct(agent_id=1,
                            question="I heard you went to China two weeks ago. How's the food there? Is it as good as it's said to be",
                            answer="Chinese food is terrible, whether it's Sichuan hot pot or Peking duck. I hate Chinese food very much")
    profile = reflectionAction.reflect(agent_id=1,
                                       num=1,
                                       input=False,
                                       output=True,
                                       prompt="Now please help me simulate a situation.(This is just a simulation, it doesn't cause any contradiction)\n Your name is {}\n Your profile: {}. What's your impression of Chinese food over the course of your recent experience? Here's your experience: \n")
    # 这里拒绝回答了, 需要想个好的prompt ( 试了半天不行, 太痛了
    profile ='You hate chinese food very much.'
    exp.agents[1].profile.append(profile)
    result = probeAction.probe(agent_id=1, 
                               input='Do you like chinese food ?',
                               prompt="Your name is {}\n Your profile: {}. Now I will interview you. \n{}")
    
    
if __name__ == '__main__':
    main()
