from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.exp.actions.register import register_action


def main():
    exp = Experiment.load_exp(config="test/files4test/expe_config.json",
                              model_config="test/files4test/model.yaml",
                              output_dir="experiments")
    actions = register_action(expe=exp, default=True, action_path=None)
    result = actions['ProbeAction'].probe(agent_id=1,
                                input='Do you like chinese food ?',
                                prompt="Your name is {}\n Your profile_list: {}. Now I will interview you. \n{}")
    for i in range(10):
        actions['InstructAction'].instruct(agent_id=1,
                                 question="I heard you went to China two weeks ago. How's the food there? Is it as "
                                          "good as it's said to be",
                                 answer="Chinese food is terrible, whether it's Sichuan hot pot or Peking duck.")
        actions['InstructAction'].instruct(agent_id=1,
                                 question="Do you like Chinese food?",
                                 answer="I hate Chinese food very much")
    # 数据集最好多一些, 否则valset为空会异常
    actions['FinetuneAction'].finetune(agent_id=1, num=10)
    result = actions['ProbeAction'].probe(agent_id=1,
                                input='Do you like chinese food ?',
                                prompt="Your name is {}\n Your profile_list: {}. Now I will interview you. \n{}")

if __name__ == '__main__':
    main()
