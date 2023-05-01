"""
@author: Guo Shiguang
@software: PyCharm
@file: agent.py
@time: 2023/4/19 9:22
"""
import json
import os.path
import re
from json import JSONDecodeError
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
        self.memory = Memory(memory_path=os.path.join(
            agent_path, "memory.jsonl"), extra_columns=misc["extra_columns"])
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
        # TODO add status to config file
        self.status = "idle"

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
        self.memory.store(interactant=interactant, experience=experience,
                          source=source, importance=importance)

    def get_importance(self, experience: str) -> float:
        importance = self._chat(self.importance_prompt.format(experience))
        self.logger.debug(
            f"store into memory,and automatically get its importance: {importance}")
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
                self.logger.warning(
                    "cannot convert importance to float,set to 5.0 by default")
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
        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.reflect_nums)

        high_level_questions_prompt = "\n".join(
            [item["experience"] for item in weighted_memory])

        high_level_questions_prompt += "Given only the information above, what are 3 most salient high-level " \
                                       "questions we can answer about the subjects in the statements?"

        high_level_questions = self._chat(high_level_questions_prompt)

        for question in high_level_questions.split("\n"):
            self.logger.info(
                f"agent_{self.agent_id} reflected from question: {question}")
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
                self._save(experience=insight, source="reflect",
                           accu_importance=False)

    def summarize(self) -> None:
        """
        Generate a summary of the agent to replace the profile
        :return:
        """
        memory = self.memory.retrieve_by_recentness(num=self.summary_nums)
        memory.reverse()
        concatenated_memory = "\n".join(
            [item["experience"] for item in memory])
        # TODO won't summarize until reach the length limit
        # TODO need config for different model limit
        if len(concatenated_memory.split(' ')) < 2000:
            self.summary = concatenated_memory
            return concatenated_memory

        self.logger.history(f"agent_{self.agent_id} begin his/her summarize")
        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}’s core characteristics.".format(self.name))

        prompt = "How would one describe {}’s core characteristics given the following statements?\n".format(
            self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary = self._chat(prompt).split("\n")

        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}’s current daily occupation.".format(self.name))

        prompt = "What is {}’s current daily occupation given the following statements?\n".format(
            self.name)
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

        self.logger.history("agent_{} summarize: {}".format(
            self.agent_id, " ".join(self.summary.split("\n"))))

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
        answer = self._probe(
            message=message, prompt=prompt, decide_by=decide_by)
        if save:
            self._save(
                experience=f'{message}. choosed {answer}', source="decide")
        return answer

    def read(self, text: str):
        """_summary_ Simulate human reading

        Args:
            text (str): _description_
            prompt (str, optional): _description_. Defaults to 'You read'.
        """
        # self.recieve(content=f"{self.name} read {text}")
        self._save(experience=f"{self.name} read {text}", source="read")

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

    def clear_mailbox(self, timestep: int) -> bool:
        """
        clear the messages that don't need to be done
        """
        items = [f"{idx}. {message['content']}. received in timestep{message['timestep']}" for idx, message in
                 enumerate(self.mailbox) if message['timestep'] < timestep]
        if len(items)==0:
            return True
        messages = '\n'.join(items)
        # TODO 参数有待测试, 使用什么memory组合比较合适
        clear_mailbox_prompt = self.get_background_prompt(need_relevant_memory=False,
                                                          need_recent_memory=False,
                                                          need_status=False)

        clear_mailbox_prompt += f"\n\nThe following are messages {self.name} received that might have to deal with, starts with number, content and timestep\n\n{messages}"
        clear_mailbox_prompt += f"Please give a list of messages that {self.name} does not need to process. " \
                                f"Your reply should be a direct loadable json in the format of " \
                                f"[{{\"number\": \"message number\", \"reason\":\"why\"}}]." \
                                f"If nothing, reply []\n"
        clear_mailbox_prompt += "Do nothing else."

        answer_ids = []
        continued = True
        for i in range(0, 5):
            try:
                answers = json.loads(self._chat(clear_mailbox_prompt))
                answer_ids = [int(answer['number']) for answer in answers]
                continued = False
                for _id in answer_ids:
                    if _id >= len(items):
                        continued = True
                        break
                if not continued:
                    break
            except:
                pass
        if continued:
            self.logger.warning(
                f"agent_{self.agent_id + 1} clear mailbox failed")
            return False
        new_mailbox = []
        for idx, message in enumerate(self.mailbox):
            if idx not in answer_ids:
                new_mailbox.append(message)
            else:
                self.save_message2memory(message)
        self.mailbox = new_mailbox
        return True

    def save_message2memory(self, message: dict):
        interactant = message["from"]
        content = message["content"]
        self._save(experience=content, source="mailbox",
                   interactant=interactant)

    def format_answer(self, content, example):
        """
        Use LLM to format the content it produces
        """
        str_ = f"{content} Format sentences above,output example: {example}"\
            f'Do nothing else'
        return self._chat(str_)

    # TODO 修里面的bug
    def select_message(self, timestep: int) -> dict:
        """
        return give the most important and urgent message
        return the first message when parse fialed
        """
        example = f'{{\"number\": \"message number\", \"reason\":\"why\"}}'
        items = [f"{idx}. {message['content']}. received in timestep{message['timestep']}" for idx, message in
                 enumerate(self.mailbox) if message['timestep'] < timestep]
        if len(items) == 0:
            return {}
        messages = '\n'.join(items)
        content = f"  The following are messages {self.name} received that might have to deal with, starts with number, content and timestep\n\n{messages}" \
            f"\n Please give {self.name}'s priority for importance and urgency consideration. Your reply should be a direct load json in the format of {example}" \
            f"Do nothing else"
        continued = True
        for i in range(0, 5):
            try:
                answer_str = self._probe(message=content)
                # format error
                answer = json.loads(answer_str)
                # content error
                answer_id = int(answer['number'])
                if answer_id < len(items):
                    continued = False
                    break
            # format error
            except JSONDecodeError as e:
                try:
                    formated_answer = self.format_answer(
                        content=answer_str, example=example)
                    answer = json.loads(formated_answer)
                    answer_id = int(answer['number'])
                    if answer_id < len(items):
                        continued = False
                        break
                except:
                    continue
            # content error
            except ValueError as e:
                continue
            except Exception as e:
                continue
        if continued:
            self.logger.warning(
                f"agent_{self.agent_id + 1} get most important and urgent message from mailbox failed, use default first message")
            answer_id = 0
        most_import_urgent_message = self.mailbox[answer_id]
        # TODO 不能放在这, 后面summarize会使用
        # self.save_message2memory(message=most_import_urgent_message)
        self.mailbox.pop(answer_id)
        most_import_urgent_message['id'] = answer_id
        return most_import_urgent_message

    def check_mailbox(self, timestep: int) -> dict:
        """
        The format of mailbox is [{"from":agent_id,"content":content,"timestep":0}]
        give the most important and urgent message, and clear the messages that don't need to be done
        :return:
        """
        # clear mailbox
        self.clear_mailbox(timestep=timestep)
        # select mailbox
        return self.select_message(timestep=timestep)

    def run(self, timestep: int):
        """_summary_ do what now ?

        Args:
            timestep (int): _description_
        """
        # TODO Fine-grained time scheduling 不同的事务会有不同的时间duration
        # something in mail
        message = self.check_mailbox(timestep)
        self.react(message=message, timestep=timestep)
        self.change_status(timestep=timestep)

    def act_as_think(self, answer, others_name, timestep):
        from AISimuToolKit.exp.agents.Courier import Courier
        for item in answer.split("\n"):
            item_json = json.loads(item)
            item_json = {key.lower(): value for key,
                         value in item_json.items()}
            content = item_json.get("content", "")
            receiver = item_json.get("interactant", "")
            if content == "" or receiver == "":
                continue
            if receiver in others_name:
                Courier.send(msg=content, sender=self.name,
                             receiver=receiver, timestep=timestep)
                self._save(experience=content, source="think",
                           interactant=receiver)

    def react(self, message: dict, timestep: int) -> None:
        # 预测的要做的事情, 塞到memory中, 交互对象也塞到
        # 问语言模型交互对象
        from AISimuToolKit.exp.agents.Courier import Courier
        others_name = list(set(Courier.all_receivers_name()) - {self.name})

        message_content = message.get(
            "content", None) if message is not None else None
        # TODO 信息冗余
        think_what_to_do_next_prompt = self.get_background_prompt(content=message_content,
                                                                  need_recent_memory=False,
                                                                  need_relevant_memory=False,
                                                                  need_status=False)
        # TODO save to memory in the past tense, can also use LLM to convert in a single step
        past = 'And describe this as something that have happened'
        if message is not None and message != {}:
            think_what_to_do_next_prompt += f"The following is send from {message['from']}, please read about it and decide what would {self.name} want to do\n.Please state in the third person declarative voice what {self.name} will do in the next step.\n {past}\n"
            think_what_to_do_next_prompt += "{}\n".format(message["content"])
        else:
            think_what_to_do_next_prompt += f"What do {self.name} want to do next?\nPlease state in the third person declarative voice what {self.name} will do in the next step.\n {past}\n"

        # TODO 是否会导致next step的动作一定与人交互? 不能独处?
        think_what_to_do_next_prompt += "Choose interactant's name from {}.\n".format(
            others_name)
        think_what_to_do_next_prompt += "output example:\n{\"interactant\":\"name\",\"content\":\"\"}\n{\"interactant\":\"name2\",\"content\":\"\"}\n"
        
        if message is not None and message != {}:
            self.save_message2memory(message=message)
            
        self.logger.debug(think_what_to_do_next_prompt)
        answer = self._chat(think_what_to_do_next_prompt)
        self.logger.info(answer)
        try:
            self.act_as_think(answer, others_name, timestep)
        except:
            self.logger.warning("get an unformatted string,try to fix it")
            try:
                fix_prompt = answer
                fix_prompt += "Format sentences above,output example:\n{\"interactant\":\"name\",\"content\":\"\"}\n{\"interactant\":\"name2\",\"content\":\"\"}\n"
                fixed_answer = self._chat(fix_prompt)
                self.act_as_think(fixed_answer, others_name, timestep)
                self.logger.info("Fixed it successfully")
            except:
                self.logger.warning("can not fix it,do nothing")

    def get_background_prompt(self, content: str = None,
                              need_relevant_memory: bool = True, need_status: bool = True,
                              need_recent_memory: bool = False) -> str:
        self.summarize()
        background_prompt = f"Act as you are {self.name}:{self.summary}.\n "
        if need_relevant_memory:
            memory_about_message = self.memory.retrieve_by_query(
                weights=self.retrieve_weight, query=content)
            memory_about_message = self.format_memory(memory_about_message)
            background_prompt += f"Here are some relevant experience:\n{memory_about_message}\n"
        if need_recent_memory:
            recent_memory = self.memory.retrieve_by_recentness(num=3)
            recent_memory = self.format_memory(recent_memory)
            background_prompt += f"Here are some recent experience:\n{recent_memory}\n"
        if need_status:
            background_prompt += f"{self.name}'s status is '{self.status}'\n"
        self.logger.debug(background_prompt)
        return background_prompt

    def format_memory(self, memory_about_message):
        memory_list = []
        from AISimuToolKit.exp.agents.Courier import Courier
        agents_name = Courier.all_receivers_name()
        for idx, item in enumerate(memory_about_message):
            format_memory = str(idx + 1) + "."
            if item["interactant"] in agents_name:
                # TODO 这样的Message with格式会让LLM混乱
                format_memory += "Message with {}:".format(item["interactant"])
            format_memory += item["experience"]
            memory_list.append(format_memory)
        return "\n".join(memory_list)

    def receive(self, msg: str, sender: str, timestep: int, ) -> None:
        self.mailbox.append(
            {"from": sender, "content": msg, "timestep": timestep})

    def change_status(self, timestep):
        change_status_prompt = self.get_background_prompt(
            "Change your state based on your recent memory",
            need_recent_memory=False,
            need_relevant_memory=False,
            need_status=True)
        change_status_prompt += "Change your state based on your recent memory,status must be a specific action.A status must be very short."
        change_status_prompt += "Do nothing else.\n"
        self.logger.debug(change_status_prompt)
        answer = self._chat(change_status_prompt)
        self.status = answer
        self.logger.info("agent {} change status to {}".format(
            self.name, self.status))
