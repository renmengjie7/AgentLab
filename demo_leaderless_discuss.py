from AISimuToolKit.exp.experiment import Experiment
from colorama import init, Fore, Back, Style

# 初始化 colorama 库
init()


def main():
    exp = Experiment.load(config="test/files4test/leaderless_discuss/expe_config.json",
                          model_config="test/files4test/leaderless_discuss/model.yaml",
                          output_dir="experiments")
    exp.inject_background(message='is at school interviewing for the Winter Olympics. This is a leaderless panel. The topic of discussion was "Minority language volunteers take half an hour to get to the site. As the only volunteer on site, now how will you inform foreigners of minority language that they must wear masks before entering the site".')
    for i in range(1, 6):
        idx = exp.choose_next_one(message="Please consider his/her characteristics and experience , give a number from 1 to 100, indicating the probability of he/she speaking at the next moment. The greater the value, the higher the probability. Please start with a number and only give a number")
        answer = exp.probe(agent=exp.agents[idx], content=f"What would {exp.agents[idx].name} say? Please express what {exp.agents[idx].name} might say directly in the first person.Please try not to repeat yourself and others\n(There is no need to give any explanation)")
        exp.agents[idx].talk2(content=answer, agents=[agent for idx_, agent in enumerate(exp.agents) if idx_!=idx])
        print(Fore.GREEN + f"round{i} {exp.agents[idx].name} said {answer}")
        print(Style.RESET_ALL)
    

if __name__ == '__main__':
    main()