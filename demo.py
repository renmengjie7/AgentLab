from AISimuToolKit.exp.experiment import Experiment
from AISimuToolKit.exp.actions.register import register_action

news = {
    "title": "Sudan fighting: Diplomats and foreign nationals evacuated",
    "content": 'The US and UK announced on Sunday they had flown diplomats out of the country.Italy, Belgium, Turkey, Japan and the Netherlands said they were also organising evacuations, starting on Sunday.A French convoy reportedly came under fire while trying to leave the embassy and had to turn back.Sudan\'s regular army and its opponents - a paramilitary force called the Rapid Support Forces (RSF) - blamed each other for the attack.Speaking to the BBC, French authorities refused to comment on whether an attack had taken place - but they did say that the French military based in Djibouti was involved in the operation and that the aim was to get the evacuees to Djibouti.The French ministry of foreign affairs said it was also evacuating its citizens and nationals of other EU and allied countries.US authorities said they had airlifted fewer than 100 people with Chinook helicopters on Sunday morning in a "fast and clean" operation.In a call with reporters after the mission, Lt Gen Douglas Sims said more than 100 US troops from the Navy Seals and Army Special Forces flew from Djibouti to Ethiopia and then into Sudan, and were on the ground for less than an hour.'
}


def main():
    exp = Experiment.load(config="test/files4test/expe_config.json",
                          model_config="test/files4test/model.yaml",
                          output_dir="experiments")
    answer = exp.agents[1].decide(input='Will you be interested in the news below?\n'
                                  'The news title: %s\n'
                                  'The news content: %s\n'
                                  'The answer should start with "Yes" or "No" '
                                  'and then state the reason for the action.' % (
                                      news['title'], news['content']),
                                  prompt="Your name is {}.\nYour profile: {}.\nNow I will interview you.\n{}",
                                  save=False)
    exp.agents[1].read(text=f"Title: {news['title']}; Content: {news['content']}",
                       prompt='You read a news——{}')


if __name__ == '__main__':
    main()
