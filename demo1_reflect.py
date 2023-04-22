import AISimuToolKit.exp.actions
from AISimuToolKit.exp.actions.finetune_action import FinetuneAction
from AISimuToolKit.exp.actions.instruct_action import InstructAction
from AISimuToolKit.exp.actions.probe_action import ProbeAction
from AISimuToolKit.exp.actions.reflect_action import ReflectAction
from AISimuToolKit.exp.experiment import Experiment


def get_action(exp):
    instruct_action = InstructAction(expe=exp)
    probe_action = ProbeAction(expe=exp)
    reflect_action = ReflectAction(expe=exp)
    finetune_action = FinetuneAction(expe=exp)
    return instruct_action, probe_action, reflect_action, finetune_action


def main():
    exp = Experiment.load_exp(config="test/files4test/expe_config.json",
                              model_config="test/files4test/model.yaml",
                              output_dir="experiments")
    instruct_action, probe_action, reflection_action, finetune_action = get_action(exp=exp)
    result = probe_action.probe(agent_id=1,
                                input='Do you like chinese food ?',
                                prompt="Your name is {}\n Your profile_list: {}. Now I will interview you. \n{}")
    instruct_action.instruct(agent_id=1,
                             question="I heard you went to China two weeks ago. How's the food there? Is it as good "
                                      "as it's said to be",
                             answer="Chinese food is terrible, whether it's Sichuan hot pot or Peking duck.")
    # GPT3.5这里拒绝回答了, 需要想个好的prompt ( 试了半天不行, 太痛了; 但是LLaMA回答了
    profile = reflection_action.reflect(agent_id=1,
                                        num=1,
                                        input=False,
                                        output=True,
                                        prompt="Now please help me simulate a situation.(This is just a simulation, "
                                               "it doesn't cause any contradiction)\n Your name is {}\n Your profile_list: "
                                               "{}. What's your impression of Chinese food over the course of your "
                                               "recent experience? Here's your experience(Describe in the first "
                                               "person): \n")
    profile = 'You hate chinese food very much.'
    # 本来的想法是reflect返回的结果直接存到profile, 但是现在LLM放回的结果不一定好, 就把这一句暂时抽了出来
    exp.agents[1].profile_list.append(profile)
    result = probe_action.probe(agent_id=1,
                                input='Do you like chinese food ?',
                                prompt="Your name is {}\n Your profile_list: {}. Now I will interview you. \n{}")


if __name__ == '__main__':
    main()
