"""
@author: Guo Shiguang
@software: PyCharm
@file: agent.py
@time: 2023/4/19 9:22
"""
import json
import os.path
import re
from typing import List

from AISimuToolKit.exp.agents.memory import Memory
from AISimuToolKit.model.model import ApiBase
from AISimuToolKit.store.logger import Logger


class Agent:
    """
    Stores information about the agent
    """
    idx = 0

    def __init__(self, agent_id: int,
                 name: str,
                 profile: list,
                 role: str,
                 model: ApiBase,
                 exp_id: str,
                 agent_path: str,
                 model_config: dict,
                 misc: dict = None):
        self.agent_id = agent_id
        self.name = name
        self.profile_list = profile
        self.role = role
        self.exp_id = exp_id
        self.model_config = model_config
        self.model = model
        self.path = agent_path
        self.logger = Logger()
        self.memory = Memory(memory_path=os.path.join(agent_path, "memory.jsonl"), extra_columns=misc["extra_columns"])
        self.retrieve_weight = misc.get("retrieve_weight", {
            "recentness": 1.0,
            "importance": 1.0,
            "similarity": 1.0
        })
        self.reflect_nums = misc.get("reflect_nums", 10)
        self.summary_nums = misc.get("summary_nums", 10)
        self.importance_prompt = misc.get("importance_prompt",
                                          "On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is "
                                          "extremely poignant (e.g., a break up,college acceptance), rate the likely poignancy of the following "
                                          "piece of memory. \nMemory: {} \n Rating: <fill in>")
        self.summary = " ".join(profile)
        self.importance_sum = 0
        self.reflect_threshold = 100

        self.mailbox = []
        self.get_num_pattern = r"\d+\.?\d*|\.\d+"

        for item in self.profile_list:
            self._save(experience=item, source="init")

    @classmethod
    def load(cls,
             format_num_len: int,
             config: dict,
             model: ApiBase,
             exp_id: str,
             exp_path) -> "Agent":
        cls.idx += 1
        path = cls.save_agent_config(agent_id=cls.idx, config=config,
                                     exp_path=exp_path, format_num_len=format_num_len)

        agent = Agent(
            agent_id=cls.idx,
            name=config['name'],
            profile=config['profile'],
            role=config['role'],
            model=model,
            exp_id=exp_id,
            agent_path=path,
            model_config=config['model_settings']['config'],
            misc=config['misc']
        )
        return agent

    @staticmethod
    def save_agent_config(agent_id: int, config: dict,
                          exp_path: str, format_num_len: int):
        """_summary_ Save the agent configuration file

        Args:
            agent (dict): _description_ 
            exp_path (str): _description_
            format_num_len (_type_): _description_

        Returns:
            _type_: _description_
        """
        agent_path = os.path.join(exp_path,
                                  f"agent_{agent_id:0{format_num_len}}")
        os.makedirs(agent_path, exist_ok=True)
        with open(os.path.join(agent_path, "agent_config.json"), "w") as f:
            json.dump(config, f)
        return agent_path

    # More extensive customization is required
    def _probe(self,
               message: str, decide_by: str = "summary",
               prompt: str = "{}'s profile is: {}.\n{}") -> str:
        """
        The interview (scale), does not leave a memory
        :param message:
        :param prompt: need to design your own according to the task
        :return:
        """
        if decide_by == "summary":
            self.summarize()
            personality = self.summary
        else:
            profile = ''.join(self.profile_list)
            personality = profile
        whole_input = prompt.format(self.name, personality, message)
        answer = self._chat(whole_input)
        self.logger.history(f"user probe: {message}")
        self.logger.history(f"whole message:\n {whole_input}")
        self.logger.history(f"agent_{self.agent_id}: {answer}")
        return answer

    def probed(self, content: str, prompt: str = "{}'s profile is: {}.\n{}"):
        """leave three blanks: name, personality and experience, content"""
        return self._probe(message=content, prompt=prompt)

    def _save(self, experience: str, source: str = "experience", interactant: str = None,
              accu_importance: bool = True) -> None:
        """_summary_ Save to memory
        Args:
            experience (str): _description_ 
        """
        self.logger.history(
            f"agent_{self.agent_id} wrote in memory: {experience} because of {source}")

        importance = self.get_importance(experience)

        if accu_importance:
            self.importance_sum += importance
        if self.importance_sum >= self.reflect_threshold:
            self.importance_sum = 0
            self.reflect_from_memory()

        if interactant is None:
            interactant = self.name
        self.memory.store(interactant=interactant, experience=experience, source=source, importance=importance)

    def get_importance(self, experience: str) -> float:
        importance = self._chat(self.importance_prompt.format(experience))
        self.logger.debug(f"store into memory,and automatically get its importance: {importance}")
        try:
            importance = float(importance)
            self.logger.debug(f"convert importance to float: {importance}")
        except Exception:
            try:
                num_list = re.findall(self.get_num_pattern, importance)
                if len(num_list) > 1:
                    importance = self._chat("find the most important number in the following sentences,it might be an "
                                            "average number:\n" + importance)
                    num_list = re.findall(self.get_num_pattern, importance)
                importance = num_list[0]
                importance = float(importance)
                self.logger.debug(f"convert importance to float: {importance}")
            except Exception:
                self.logger.warning("cannot convert importance to float,set to 5.0 by default")
                importance = 5.0
        return importance

    def _finetune(self, num: int) -> bool:
        """_summary_ Ask the Agent to fine-tune on the given corpus, which in this case is the experience in memory (turn an experience into a conversation)
        Args:
            num (_type_): _description_ The amount of memory used
        """
        recent_memory = self.memory.retrieve_by_recentness(num)
        self.logger.info(
            f"agent_{self.agent_id} starts finetuning based on recent {num} memories")
        # The memory used by finetune needs to be stored for later review
        self.model.finetune(exp=self.exp_id,
                            path=self.path,
                            agent=self.agent_id,
                            config=self.model_config, datas=recent_memory)
        self.logger.info(
            f"agent_{self.agent_id} successfully finetuned based on recent {num} memories")
        return True

    def reflect_from_memory(self) -> None:
        """
        Reflect on memories and create new memories
        :return:
        """
        self.logger.history(f"agent_{self.agent_id} reflected from memory")
        weighted_memory = self.memory.retrieve_by_query(weights=self.retrieve_weight, num=self.reflect_nums)

        high_level_questions_prompt = "\n".join([item["experience"] for item in weighted_memory])

        high_level_questions_prompt += "Given only the information above, what are 3 most salient high-level " \
                                       "questions we can answer about the subjects in the statements?"

        high_level_questions = self._chat(high_level_questions_prompt)

        for question in high_level_questions.split("\n"):
            self.logger.info(f"agent_{self.agent_id} reflected from question: {question}")
            weighted_memory_to_reflect = self.memory.retrieve_by_query(
                weights=self.retrieve_weight, num=self.reflect_nums, query=question)

            formatted_prompt = f"Statements about {self.name}\n"
            for idx, item in enumerate(weighted_memory_to_reflect):
                formatted_prompt += f"{idx + 1}. {item['experience']}\n"
            formatted_prompt += "What 5 high-level insights can you infer from the above statements?\n(example format: " \
                                "insight 1 \n insight 2 \n insight 3 \n insight 4 \n insight 5)"

            insights = self._chat(formatted_prompt)

            for insight in insights.split("\n"):
                insight = insight.strip()
                self._save(experience=insight, source="reflect", accu_importance=False)

    def summarize(self) -> None:
        """
        Generate a summary of the agent to replace the profile
        :return:
        """
        memory = self.memory.retrieve_by_recentness(num=self.summary_nums)
        memory.reverse()
        concatenated_memory = "\n".join([item["experience"] for item in memory])
        # TODO won't summarize until reach the length limit
        # TODO need config for different model limit
        if len(concatenated_memory.split(' ')) < 2000:
            self.summary = concatenated_memory
            return concatenated_memory

        self.logger.history(f"agent_{self.agent_id} begin his/her summarize")
        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}’s core characteristics.".format(self.name))

        prompt = "How would one describe {}’s core characteristics given the following statements?\n".format(self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary = self._chat(prompt).split("\n")

        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}’s current daily occupation.".format(self.name))

        prompt = "What is {}’s current daily occupation given the following statements?\n".format(self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary.extend(self._chat(prompt).split("\n"))

        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}'s feeling about his recent progress in life".format(self.name))

        prompt = "What is {}’s feeling about his recent progress in life given the following statements?\n".format(
            self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary.extend(self._chat(prompt).split("\n"))

        prompt = "Summarize the statement below:\n"
        prompt += "\n".join(summary)
        self.summary = self._chat(prompt)

        self.logger.history("agent_{} summarize: {}".format(self.agent_id, " ".join(self.summary.split("\n"))))

    def _chat(self, formatted_prompt: str) -> str:
        """
        wrapper for model.chat()
        :param formatted_prompt:
        :return:
        """
        return self.model.chat(query=formatted_prompt,
                               exp=self.exp_id,
                               agent=self.agent_id,
                               config=self.model_config)

    def decide(self,
               question: str = None, answers: List[str] = None,
               message: str = None,
               prompt: str = "{}'s profile is: {}.\n{}",
               save: bool = True, decide_by: str = "summarize"):
        """_summary_ Simulate human decision making
        decide=_probe+_save (if need)
        Args:
            question (str): _description_ 
            answers (List[str]): _description_ options
            message (str, optional): _description_. Defaults to None. If input is provided, it is queried directly using the string; Otherwise the default prompt is populated with question and input
            save (bool, optional): _description_. Defaults to True. 
            TODO Does the decision need to be added to memory? Memory is definitely added in real life, but this part of information will also be added in the next step, which may bring redundancy and noise
            :param decide_by:
        """
        if message is None:
            message = question + '\n'.join([answer for answer in answers])
        answer = self._probe(message=message, prompt=prompt, decide_by=decide_by)
        if save:
            self._save(experience=f'{message}. choosed {answer}', source="decide")
        return answer

    def read(self, text: str):
        """_summary_ Simulate human reading

        Args:
            text (str): _description_
            prompt (str, optional): _description_. Defaults to 'You read'.
        """
        self.recieve(content=f"{self.name} read {text}")

    def eat(self, food: List[str], time: str = '', prompt: str = 'You ate {} {}'):
        """_summary_ Simulate human eating

        Args:
            text (List[str]): _description_ food list
            time (str, optional): _description_. Defaults to ''. 
            prompt (str, optional): _description_. Defaults to 'You ate {} {}'.
        """
        self._save(experience=prompt.format(','.join(food), time), source="eat")

    def _generate_natural_prompt(self, raw_prompt: str) -> str:
        pass

    def recieve_info(self, content):
        """Received some kind of message"""
        self._save(experience=content)

    def talk2(self, content, agents: List['Agent']):
        """
        TODO If conversation is involved, the context of the communication needs to be preserved
        """
        experience = f"{self.name} saied to {','.join([agent.name for agent in agents])} that {content}"
        self._save(experience=experience)
        for idx, agent in enumerate(agents):
            agent.recieve_info(content=experience)

    def check_mailbox(self, timestep: int):
        """
        The information in mailbox is read and stored in memory, and mailbox is emptied
        the format of mailbox is [{"from":agent_id,"content":content,"replyable":True,"timestep:0}]
        :return:
        """
        messages = []
        while self.mailbox and self.mailbox[0]["timestep"] <= timestep:
            messages.append(self.mailbox.pop(0))

        for message in messages:
            interactant = message["from"]
            content = message["content"]
            self._save(experience=content, source="mailbox", interactant=interactant)
        return messages

    def react(self, timestep: int):
        from AISimuToolKit.exp.agents.Courier import Courier
        messages = self.check_mailbox(timestep)
        if len(messages) == 0:
            return
        self.summarize()
        for message in messages:
            if not message["replyable"]:
                continue
            memory_about_message = self.memory.retrieve_by_query(weights=self.retrieve_weight, query=message["content"])
            memory_about_message = "\n".join(
                [str(idx + 1) + ":" + item["experience"] for idx, item in enumerate(memory_about_message)])
            background_prompt = "Act as you are {}:{}.\nHere are some experience might be useful:\n{}\nThe following is send from {}, please read about it and decide who would you like to talk to\n".format(
                self.name, self.summary, memory_about_message, message["from"])
            background_prompt += "\n{}\n".format(message["content"])
            select_prompt = background_prompt + "\nSelect one or more or none of the people you want to communicate with next from the given list\n{}\n".format(
                list(set(Courier.all_receivers_name()) - {self.name}))

            for name in list(set(Courier.all_receivers_name()) - {self.name}):
                check_if_talk = self._chat(background_prompt + "\n" + "Do you want to talk to {}".format(name))
                self.logger.info(
                    "agent_{} is deciding whether to talk to {}...{}".format(self.agent_id, name, check_if_talk))
                check_if_talk = self._chat(
                    "Check if 'I' want to communicate with {} in the following sentence,\noutput example: yes/no\ndo nothing else.\n".format(
                        name) + check_if_talk)
                self.logger.info("agent_{} is formatting output {}".format(self.agent_id, check_if_talk))
                if "yes" in check_if_talk.lower():
                    sentence = self._chat(
                        background_prompt + "\n" + "You are talking to {} ,what you want to say is:".format(name))
                    sentence = self._chat(
                        "Narrate the following conversation in the same tone that 'I' would speak to 'you'\n{}".format(
                            sentence))
                    self.logger.history("agent_{} talk to {} that {}".format(self.agent_id, name, sentence))
                    Courier.send(msg=sentence, sender=self.name, receiver=name, replyable=True,
                                 timestep=timestep + 1)

    def receive(self, msg: str, sender: str, timestep: int, replyable: bool = True, ) -> None:
        self.mailbox.append({"from": sender, "content": msg, "replyable": replyable, "timestep": timestep})
