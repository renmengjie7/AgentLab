from AISimuToolKit.exp.actions import BaseAction
from AISimuToolKit.exp.agents.agent import Agent
from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.store.text.logger import Logger
from AISimuToolKit.exp.actions import InstructAction, ProbeAction, ReflectionAction, FinetuneAction


def get_action(exp):
    instructAction = InstructAction(expe=exp)
    probeAction = ProbeAction(expe=exp)
    reflectionAction = ReflectionAction(expe=exp)
    finetuneAction =FinetuneAction(expe=exp)
    return instructAction, probeAction, reflectionAction, finetuneAction

    
def main():
    exp = Experiment.load_exp(config="test/files4test/expe_config.json", 
                              model_config="test/files4test/model.yaml",
                              output_dir="experiments")
    instructAction, probeAction, reflectionAction, finetuneAction = get_action(exp=exp)
    result = probeAction.probe(agent_id=1, 
                               input='Do you like chinese food ?',
                               prompt="Your name is {}\n Your profile: {}. Now I will interview you. \n{}")
    for i in range(10):
        instructAction.instruct(agent_id=1,
                                question="I heard you went to China two weeks ago. How's the food there? Is it as good as it's said to be",
                                answer="Chinese food is terrible, whether it's Sichuan hot pot or Peking duck.")
        instructAction.instruct(agent_id=1,
                                question="Do you like Chinese food?",
                                answer="I hate Chinese food very much")
    # 数据集最好多一些, 否则valset为空会异常
    finetuneAction.finetune(agent_id=1, num=10)
    result = probeAction.probe(agent_id=1, 
                               input='Do you like chinese food ?',
                               prompt="Your name is {}\n Your profile: {}. Now I will interview you. \n{}")
    
    
if __name__ == '__main__':
    main()
