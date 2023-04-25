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
    exp = Experiment.load(config="test/files4test/expe_config.json",
                          model_config="test/files4test/model.yaml",
                          output_dir="experiments")
    # answer = exp.agents[0].decide(message='Will you be interested in the news below?\n'
    #                                       'The news title: %s\n'
    #                                       'The news content: %s\n'
    #                                       'The answer should start with "Yes" or "No" '
    #                                       'and then state the reason for the action.' % (
    #                                           news['title'], news['content']),
    #                               prompt="Your name is {}.\nYour profile: {}.\nNow I will interview you.\n{}",
    #                               save=False)
    # exp.agents[0].read(text=f"Title: {news['title']}; Content: {news['content']}",
    #                    prompt='You read a news——{}')

    exp.agents[0]._save(
        "Alice is a brilliant engineer at Google, with a knack for problem-solving and a passion for innovation.")
    exp.agents[0]._save(
        "As a Google engineer, Alice is known for his exceptional coding skills and his ability to tackle complex challenges with ease.")
    exp.agents[0]._save(
        "Alice is a key player on the Google engineering team, leveraging his extensive knowledge of software development to drive success.")
    exp.agents[0]._save(
        "With years of experience under his belt, Alice has become one of the most respected engineers at Google, admired for his technical prowess and creative thinking.")
    exp.agents[0]._save(
        "Alice's expertise in cutting-edge technologies has made him an invaluable member of the Google engineering team, driving innovation and growth.")
    exp.agents[0]._save(
        "As a Google engineer, Alice is constantly pushing the boundaries of what's possible, using his skills to develop groundbreaking solutions to complex problems.")
    exp.agents[0]._save(
        "Alice's passion for engineering is palpable, and his commitment to excellence has made him a standout member of the Google team.")
    exp.agents[0]._save(
        "With a keen eye for detail and a deep understanding of engineering principles, Alice is a driving force behind Google's success.")
    exp.agents[0]._save(
        "Alice's contributions to Google's engineering efforts have been instrumental in shaping the future of the company and the industry as a whole.")
    exp.agents[0]._save(
        "As one of Google's top engineers, Alice is a respected leader in his field, admired for his technical expertise and strategic vision.")
    exp.agents[0]._save("Alice is very hungry now, she really wants to eat a McDonald's double-decker Big Mac")
    exp.agents[0]._save("In addition, she also wants to go to the cinema to watch the latest movie in the evening")
    exp.agents[0]._save("Since there is no seasoning at home, she still needs to buy some soy sauce before going home")

    exp.agents[0].reflect_from_memory()


if __name__ == '__main__':
    main()
