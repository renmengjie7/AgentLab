"""
@author: Guo Shiguang
@software: PyCharm
@file: demo_parallel.py
@time: 2023/4/27 21:57
"""

from AISimuToolKit.exp.experiment import Experiment


def main():
    exp = Experiment.load(config="test/files4test/meeting/exp_meeting.json",
                          model_config="test/files4test/meeting/model.yaml",
                          output_dir="experiments")

    exp.agents[0].receive(
        f"{exp.agents[0].name} wants to hold a project progress docking meeting this afternoon. {exp.agents[0].name} is so busy he/she don't have time to schedule meetings herself/himself. {exp.agents[0].name} needs his/her secretary, Bob, to arrange a meeting for the rest of the project, including Carol and Dave, in the conference room at 3:00 this afternoon.",
        sender="a mysterious force", timestep=0)
    
    for timestep in range(30):
        exp.logger.info(f"=============timestep: {timestep}=============")
        for agent in exp.agents:
            agent.run(timestep=timestep)


if __name__ == '__main__':
    main()
