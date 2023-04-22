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
    for i in range(10):
        instruct_action.instruct(agent_id=1,
                                 question="I heard you went to China two weeks ago. How's the food there? Is it as "
                                          "good as it's said to be",
                                 answer="Chinese food is terrible, whether it's Sichuan hot pot or Peking duck.")
        instruct_action.instruct(agent_id=1,
                                 question="Do you like Chinese food?",
                                 answer="I hate Chinese food very much")
    # 数据集最好多一些, 否则valset为空会异常
    finetune_action.finetune(agent_id=1, num=10)
    result = probe_action.probe(agent_id=1,
                                input='Do you like chinese food ?',
                                prompt="Your name is {}\n Your profile_list: {}. Now I will interview you. \n{}")


if __name__ == '__main__':
    main()
