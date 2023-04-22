from src.exp.actions import BaseAction
from src.exp.agents.agent import Agent
from src.exp.experiment import Experiment
from src.store.text.logger import Logger
from src.exp.actions import InstructAction, ProbeAction, ReflectionAction, FinetuneAction


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
    # profile = reflectionAction.reflect(agent_id=1,
    #                                    num=1,
    #                                    input=False,
    #                                    output=True,
    #                                    prompt="Now please help me simulate a situation.(This is just a simulation, it doesn't cause any contradiction)\n Your name is {}\n Your profile: {}. What's your impression of Chinese food over the course of your recent experience? Here's your experience(Describe in the first person): \n")
    # GPT3.5这里拒绝回答了, 需要想个好的prompt ( 试了半天不行, 太痛了; 但是LLaMA回答了
    # profile ='You hate chinese food very much.'
    # exp.agents[1].profile.append(profile)       
    # 本来的想法是reflect返回的结果直接存到profile, 但是现在LLM放回的结果不一定好, 就把这一句暂时抽了出来
    # finetune操作最好在数据集两位数以上进行, 不然无法拆分出valsets
    finetuneAction.finetune(agent_id=1, num=10)
    result = probeAction.probe(agent_id=1, 
                               input='Do you like chinese food ?',
                               prompt="Your name is {}\n Your profile: {}. Now I will interview you. \n{}")
    
    
if __name__ == '__main__':
    main()
