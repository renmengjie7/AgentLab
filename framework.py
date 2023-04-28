"""
@author: Guo Shiguang
@software: PyCharm
@file: framework.py
@time: 2023/4/27 21:57
"""

from AISimuToolKit.exp.experiment import Experiment


def main():
    # 可以通过继承Agent的方式自定义Agent，（目前只支持继承Agent类，不支持继承其他类）
    # custom_class = {"agent": MyAgent, }
    custom_class = None

    # config中新加了一些参数，包括
    # experiment_settings.extra_columns:额外的记到memory中的列名(这里是公共的，如果独立设置会覆盖该字段)
    # agent_list.misc.importance_prompt:设计计算重要性的prompt
    # agent_list.misc.retrieve_weight: 检索权重
    # agent_list.misc.reflect_nums: 反思阶段，用于反思的加权排序后记忆的个数
    # agent_list.misc.summary_nums：总结阶段，用于总结的加权排序后记忆的个数
    exp = Experiment.load(config="test/files4test/expe_config.json",
                          model_config="test/files4test/model.yaml",
                          output_dir="experiments", custom_class=custom_class)

    for timestep in range(10):
        # next_agent = exp.choose_next_one("prompt")
        # next_agent.debate()
        for agent in exp.agents:
            agent.react()


if __name__ == '__main__':
    main()
