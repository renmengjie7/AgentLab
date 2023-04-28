from AISimuToolKit.exp.experiment import Experiment


def main():
    exp = Experiment.load(config="test/files4test/demo/expe_config.json",
                          model_config="test/files4test/demo/model.yaml",
                          output_dir="experiments")
    exp.inject_background(message='is at school interviewing for the Winter Olympics. This is a leaderless panel. The topic of discussion was "how to inform foreigners of minority languages that they are required to wear masks before entering the site, and that it takes half an hour for volunteers of minority languages to reach the site".')
    idx = exp.choose_next_one()
    answer = exp.probe(agent=exp.agents[idx], content=f"What would {exp.agents[idx].name} say? \n(There is no need to give any explanation)")
    exp.agents[idx].talk2(content=answer, agents=exp.agents)
    


if __name__ == '__main__':
    main()
