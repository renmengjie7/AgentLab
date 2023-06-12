from colorama import init

from AISimuToolKit.exp.experiment import Experiment

# init colorama
init()


def main():
    exp = Experiment.load(config="test/files4test/leaderless_discuss/exp_leaderless_discuss.json",
                          model_config="test/files4test/leaderless_discuss/model.yaml",
                          output_dir="experiments")
    exp.inject_background(
        message='is at school interviewing for the Olympics. This is a leaderless panel. The topic of discussion was'
                ' "Minority language volunteers take half an hour to get to the site. As the only volunteer on site,'
                'now how will you inform foreigners of minority language that they must wear masks before entering the site". Ask you to discuss a solution')

    # Only one person can speak at each round
    for i in range(1, 20):
        exp.scheduler.run()
        # # who to say
        # idx = exp.choose_next_one()
        # # what to say
        # answer = exp.probe(agent=exp.agents[idx],
        #                    content=f"What would {exp.agents[idx].name} say in the next moment?"
        #                            f" Please express what {exp.agents[idx].name} might say directly in the first person."
        #                            f"Please try not to repeat yourself and others\n(There is no need to give any explanation)")
        # # talk2
        # exp.agents[idx].talk2(content=answer, agents=[agent for idx_, agent in enumerate(exp.agents) if idx_ != idx])
        # # log
        # print(Fore.GREEN + f"round{i} {exp.agents[idx].name} said {answer}")
        # print(Style.RESET_ALL)


if __name__ == '__main__':
    main()
