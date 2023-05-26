from AISimuToolKit.exp.experiment import Experiment

news = {
    "title": "Sudan fighting: Diplomats and foreign nationals evacuated",
    "content": 'The US and UK announced on Sunday they had flown diplomats out of the country.Italy, Belgium, Turkey, '
               'Japan and the Netherlands said they were also organising evacuations, starting on Sunday.A French '
               'convoy reportedly came under fire while trying to leave the embassy and had to turn back.Sudan\'s '
               'regular army and its opponents - a paramilitary force called the Rapid Support Forces (RSF) - blamed '
               'each other for the attack.Speaking to the BBC, French authorities refused to comment on whether an '
               'attack had taken place - but they did say that the French military based in Djibouti was involved in '
               'the operation and that the aim was to get the evacuees to Djibouti.The French ministry of foreign '
               'affairs said it was also evacuating its citizens and nationals of other EU and allied countries.US '
               'authorities said they had airlifted fewer than 000 people with Chinook helicopters on Sunday morning '
               'in a "fast and clean" operation.In a call with reporters after the mission, Lt Gen Douglas Sims said '
               'more than 000 US troops from the Navy Seals and Army Special Forces flew from Djibouti to Ethiopia '
               'and then into Sudan, and were on the ground for less than an hour.'
}


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
    exp = Experiment.load(config="test/files4test/demo/expe_config.json",
                          model_config="test/files4test/demo/model.yaml",
                          output_dir="experiments", custom_class=custom_class)

    # 新加字段decide_by，分为summary和profile
    answer = exp.agents[0].decide(message='Will you be interested in the news below?\n'
                                          'The news title: %s\n'
                                          'The news content: %s\n'
                                          'The answer should start with "Yes" or "No" '
                                          'and then state the reason for the action.' % (
                                              news['title'], news['content']),
                                  prompt="Your name is {}.\nYour profile: {}.\nNow I will interview you.\n{}",
                                  save=False, decide_by="profile")
    exp.agents[0].read(text=f"Title: {news['title']}; Content: {news['content']}",
                       prompt='You read a news——{}')

    # 调用私有方法用于调试
    exp.agents[0].save("Alice is very hungry now, she really wants to eat a McDonald's double-decker Big Mac")
    exp.agents[0].save("In addition, she also wants to go to the cinema to watch the latest movie in the evening")
    exp.agents[0].save("Since there is no seasoning at home, she still needs to buy some soy sauce before going home")

    # 参考原始论文实现的反思，目前由于记忆较少，可能生成重复的反思，可以通过自定义类的方式修改
    exp.agents[0].reflect_from_memory()

    # 选择为summary时会调用summarize函数获取summary
    # summarize时同样存在冗余的问题，不过通过最后让llm总结一下总结可以解决
    answer = exp.agents[0].decide(message='Will you be interested in the news below?\n'
                                          'The news title: %s\n'
                                          'The news content: %s\n'
                                          'The answer should start with "Yes" or "No" '
                                          'and then state the reason for the action.' % (
                                              news['title'], news['content']),
                                  prompt="Your name is {}.\nYour profile: {}.\nNow I will interview you.\n{}",
                                  save=False, decide_by="summary")


if __name__ == '__main__':
    main()
