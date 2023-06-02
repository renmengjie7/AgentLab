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

# from AISimuToolKit.exp.agents.agent_collection import AgentCollectionWrapper
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
                 group: str,
                 model: ApiBase,
                 exp_id: str,
                 agent_path: str,
                 model_config: dict,
                 **kwargs):
        self.agent_id = agent_id
        self.name = name
        self.profile_list = profile
        self.group = group
        self.exp_id = exp_id
        self.model_config = model_config
        self.model = model
        self.path = agent_path

        self.logger = Logger()

        self.memory = Memory(memory_path=os.path.join(agent_path, "memory.jsonl"),
                             extra_columns=kwargs.get("extra_columns", []),
                             embedding_model=kwargs.get("embedding_model", None),
                             openai_embedding_settings=kwargs.get("openai_embedding_settings", None))

        self.complicated_reflection = kwargs.get("complicated_reflection", False)
        self.calculate_importance = kwargs.get("calculate_importance", False)
        self.retrieve_weight = kwargs.get("retrieve_weight", {
            "recentness": 1.0,
            "importance": 1.0,
            "similarity": 1.0
        })
        self.reflect_nums = kwargs.get("reflect_nums", 10)
        self.summary_nums = kwargs.get("summary_nums", 10)
        self.reflect_threshold = kwargs.get("reflect_threshold", 100)
        self.importance_prompt = kwargs.get("importance_prompt",
                                            "On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is "
                                            "extremely poignant (e.g., a break up,college acceptance), rate the likely poignancy of the following "
                                            "piece of memory. \nMemory: {} \n Rating: <fill in>")
        self.summary = " ".join(profile)
        self.importance_sum = 0

        self.mailbox = []
        self.get_num_pattern = r"\d+\.?\d*|\.\d+"
        # TODO add status to agent_config file
        self.status = "idle"

        self.logger.info(f"Creating agent {self.name} ... This will take some time.")
        for item in self.profile_list:
            self.save(experience=item, source="init")

    @classmethod
    def load(cls,
             format_num_len: int,
             agent_config: dict,
             model: ApiBase,
             exp_id: str,
             exp_path) -> "Agent":
        cls.idx += 1
        path = cls.save_agent_config(agent_id=cls.idx, config=agent_config,
                                     exp_path=exp_path, format_num_len=format_num_len)

        agent = Agent(
            agent_id=cls.idx,
            name=agent_config['name'],
            profile=agent_config['profile'],
            group=agent_config.get('group', None),
            model=model,
            exp_id=exp_id,
            agent_path=path,
            model_config=agent_config['model_settings']['config'],
            **agent_config['specific_agent_settings']
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
        agent_path = os.path.join(exp_path, f"agent_{agent_id:0{format_num_len}}")
        os.makedirs(agent_path, exist_ok=True)
        with open(os.path.join(agent_path, "agent_config.json"), "w") as f:
            json.dump(config, f)
        return agent_path

    # More extensive customization is required
    # _probe is replaced by chat
    # def _probe(self,
    #            message: str, decide_by: str = "summary",
    #            prompt: str = "{}'s profile is: {}.\n{}") -> str:
    #     """
    #     The interview (scale), does not leave a memory
    #     :param message:
    #     :param prompt: need to design your own according to the task
    #     :return:
    #     """
    #     if decide_by == "summary":
    #         self.summarize()
    #         personality = self.summary
    #     else:
    #         profile = ''.join(self.profile_list)
    #         personality = profile
    #     whole_input = prompt.format(self.name, personality, message)
    #     answer = self._inside_chat_wrapper(whole_input)
    #     self.logger.history(f"user probe: {message}")
    #     self.logger.history(f"whole message:\n {whole_input}")
    #     self.logger.history(f"agent_{self.agent_id}: {answer}")
    #     return answer

    def save(self, experience: str, source: str = "experience", interactant: str = None,
             accu_importance: bool = True) -> None:
        """
        Save the experience into memory
        :param experience:
        :param source:
        :param interactant:
        :param accu_importance:
        :return:
        """
        self.logger.debug(f"agent {self.name} wrote in memory: {experience} because of {source}")

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
        if not self.calculate_importance:
            return 5.0
        importance = self._inside_chat_wrapper(self.importance_prompt.format(experience))
        self.logger.debug(
            f"store into memory,and automatically get its importance: {importance}")
        try:
            importance = float(importance)
            self.logger.debug(f"convert importance to float: {importance}")
        except Exception:
            try:
                num_list = re.findall(self.get_num_pattern, importance)
                if len(num_list) > 1:
                    importance = self._inside_chat_wrapper(
                        "find the most important number in the following sentences,it might be an "
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
        self.logger.history(f"agent {self.name} reflected from memory")
        weighted_memory = self.memory.retrieve_by_query(weights=self.retrieve_weight, num=self.reflect_nums)

        if self.complicated_reflection:
            high_level_questions_prompt = "\n".join([item["experience"] for item in weighted_memory])

            high_level_questions_prompt += "Given only the information above, what are 3 most salient high-level " \
                                           "questions we can answer about the subjects in the statements?"

            high_level_questions = self._inside_chat_wrapper(high_level_questions_prompt)

            for question in high_level_questions.split("\n"):
                self.logger.info(
                    f"agent {self.name} reflected from question: {question}")
                weighted_memory_to_reflect = self.memory.retrieve_by_query(
                    weights=self.retrieve_weight, num=self.reflect_nums, query=question)

                formatted_prompt = f"Statements about {self.name}\n"
                for idx, item in enumerate(weighted_memory_to_reflect):
                    formatted_prompt += f"{idx + 1}. {item['experience']}\n"
                formatted_prompt += "What 5 high-level insights can you infer from the above statements?\n" \
                                    "(example format: insight 1 \n insight 2 \n insight 3 \n insight 4 \n insight 5)"
                insights = self._inside_chat_wrapper(formatted_prompt)

                for insight in insights.split("\n"):
                    insight = insight.strip()
                    self.save(experience=insight, source="reflect", accu_importance=False)
        else:
            formatted_prompt = f"Statements about {self.name}\n"
            for idx, item in enumerate(weighted_memory):
                formatted_prompt += f"{idx + 1}. {item['experience']}\n"
            formatted_prompt += "What 5 high-level insights can you infer from the above statements?\n" \
                                "(example format: insight 1 \n insight 2 \n insight 3 \n insight 4 \n insight 5)"
            insights = self._inside_chat_wrapper(formatted_prompt)

            for insight in insights.split("\n"):
                insight = insight.strip()
                self.save(experience=insight, source="reflect", accu_importance=False)

    def summarize(self) -> None:
        """
        Generate a summary of the agent to replace the profile
        :return:
        """
        memory = self.memory.retrieve_by_recentness(num=self.summary_nums)
        memory.reverse()
        concatenated_memory = "\n".join([item["experience"] for item in memory])
        # TODO won't summarize until reach the length limit
        # TODO need agent_config for different model limit
        if len(concatenated_memory.split(' ')) < 2000:
            self.summary = concatenated_memory
            return

        self.logger.info(f"agent_{self.agent_id} begin his/her summarize")
        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}’s core characteristics.".format(self.name))

        prompt = "How would one describe {}’s core characteristics given the following statements?\n".format(
            self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary = self._inside_chat_wrapper(prompt).split("\n")

        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}’s current daily occupation.".format(self.name))

        prompt = "What is {}’s current daily occupation given the following statements?\n".format(
            self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary.extend(self._inside_chat_wrapper(prompt).split("\n"))

        weighted_memory = self.memory.retrieve_by_query(
            weights=self.retrieve_weight, num=self.summary_nums,
            query="{}'s feeling about his recent progress in life".format(self.name))

        prompt = "What is {}’s feeling about his recent progress in life given the following statements?\n".format(
            self.name)
        prompt += "\n".join([item["experience"] for item in weighted_memory])
        summary.extend(self._inside_chat_wrapper(prompt).split("\n"))

        prompt = "Summarize the statement below:\n"
        prompt += "\n".join(summary)
        self.summary = self._inside_chat_wrapper(prompt)

        self.logger.history("agent_{} summarize: {}".format(self.agent_id, " ".join(self.summary.split("\n"))))

    def _inside_chat_wrapper(self, formatted_prompt: str) -> str:
        """
        wrapper for model.chat()
        :param formatted_prompt:
        :return:
        """
        return self.model.chat(query=formatted_prompt,
                               exp=self.exp_id,
                               agent=self.agent_id,
                               config=self.model_config)

    # decide is replaced by chat
    # def decide(self,
    #            question: str = None, answers: List[str] = None,
    #            message: str = None,
    #            prompt: str = "{}'s profile is: {}.\n{}",
    #            save: bool = True, decide_by: str = "summarize"):
    #     """_summary_ Simulate human decision making
    #     decide=_probe+save (if need)
    #     Args:
    #         question (str): _description_
    #         answers (List[str]): _description_ options
    #         message (str, optional): _description_. Defaults to None. If input is provided, it is queried directly using the string; Otherwise the default prompt is populated with question and input
    #         save (bool, optional): _description_. Defaults to True.
    #         TODO Does the decision need to be added to memory? Memory is definitely added in real life, but this part of information will also be added in the next step, which may bring redundancy and noise
    #         :param decide_by:
    #     """
    #     if message is None:
    #         message = question + '\n'.join([answer for answer in answers])
    #     answer = self.chat(message=message)
    #     if save:
    #         self.save(
    #             experience=f'{message}. choosed {answer}', source="decide")
    #     return answer

    def read(self, text: str):
        """_summary_ Simulate human reading

        Args:
            text (str): _description_
            prompt (str, optional): _description_. Defaults to 'You read'.
        """
        # self.recieve(content=f"{self.name} read {text}")
        self.save(experience=f"{self.name} read {text}", source="read")

    def talk2(self, message, agents: List['Agent']):
        """
        TODO If conversation is involved, the context of the communication needs to be preserved
        """
        experience = f"{self.name} saied to {','.join([agent.name for agent in agents])} that {message}"
        for agent in agents:
            agent.receive_info(content=experience)
            
    def receive_info(self, content):
        """Received some kind of message"""
        self.save(experience=content)

    def clear_mailbox(self, timestep: int) -> bool:
        """
        clear the messages that don't need to be done
        """
        formatted_mails = [f"{idx}. {mail['content']}. received in timestep{mail['timestep']}" for idx, mail in
                           enumerate(self.mailbox) if mail['timestep'] < timestep]
        if len(formatted_mails) == 0:
            return True
        example = f"[{{\"number\": \"message number\", \"reason\":\"why\"}}]"
        formatted_mails = "\n".join(formatted_mails)
        message = f"Here are the messages you received that may need to be processed, starting with number, content and timestep\n\n{formatted_mails}" \
                  f"\nPlease give a list of messages that you do not need to process."
        # TODO 参数有待测试, 使用什么memory组合比较合适
        try:
            answer = self.chat(message=message,
                               need_recent_memory=False,
                               need_status=False,
                               need_relevant_memory=False,
                               output_format=example)
            answer = json.loads(answer)
            answer_ids = [int(item['number']) for item in answer]
            for item in answer_ids:
                assert item < len(self.mailbox)
            if len(answer_ids) == 0:
                self.logger.debug(f"agent {self.name} cleared his/her mailbox, but no message was deleted")
            else:
                self.logger.debug("agent {} cleared his/her mailbox, deleted the fellowing message {}".format(
                    self.name, "\n" + "\n".join([self.mailbox[idx]['content'] for idx in answer_ids])))
        except:
            self.logger.warning(f"agent {self.name} clear mailbox failed")
            answer_ids = []
        new_mailbox = []
        for idx, message in enumerate(self.mailbox):
            if idx not in answer_ids:
                new_mailbox.append(message)
            else:
                self.save_mailbox_message2memory(message)
        self.mailbox = new_mailbox
        return True

    def save_mailbox_message2memory(self, message: dict):
        interactant = message["from"]
        content = message["content"]
        self.save(experience=content, source="mailbox", interactant=interactant)

    # def format_answer(self, content, example):
    #     """
    #     Use LLM to format the content it produces
    #     """
    #     str_ = f"{content}\n\n Format sentences above,output example: {example}."
    #     return self._inside_chat_wrapper(str_)

    # TODO 修里面的bug
    def select_message(self, timestep: int) -> dict:
        """
        return give the most important and urgent message
        return the first message when parse fialed
        """
        formatted_mails = [f"{idx}. {mail['content']}. received in timestep{mail['timestep']}" for idx, mail in
                           enumerate(self.mailbox) if mail['timestep'] < timestep]
        if len(formatted_mails) == 0:
            return {}
        example = f"{{\"number\": \"message number\", \"reason\":\"why\"}}"
        formatted_mails = "\n".join(formatted_mails)
        message = f"Here are the messages you received that may need to be processed, starting with number, content and timestep\n\n{formatted_mails}" \
                  f"\nPlease give your priority for importance and urgency consideration."

        try:
            answer = self.chat(message=message,
                               need_relevant_memory=False,
                               need_recent_memory=True,
                               output_format=example)
            answer = json.loads(answer)
            answer_id = int(answer['number'])
            assert answer_id < len(formatted_mails)
        except:
            self.logger.warning(
                f"agent_{self.name}failed to get most important and urgent message from mailbox, use the first message")
            answer_id = 0

        most_import_urgent_message = self.mailbox.pop(answer_id)
        # TODO 不能放在这, 后面summarize会使用
        # self.save_mailbox_message2memory(message=most_import_urgent_message)
        return most_import_urgent_message

    def check_mailbox_and_select(self, timestep: int) -> dict:
        """
        The format of mailbox is [{"from":agent_id,"content":content,"timestep":0}]
        give the most important and urgent message, and clear the messages that don't need to be done
        :return:
        """
        # clear mailbox
        self.clear_mailbox(timestep=timestep)
        # select mailbox
        return self.select_message(timestep=timestep)

    def check_mailbox_and_read_all(self, timestep: int) -> dict:
        self.clear_mailbox(timestep=timestep)
        for item in self.mailbox:
            self.save_mailbox_message2memory(message=item)
        self.mailbox = []

    def act_as_think(self, answer, others_name, timestep):
        from AISimuToolKit.exp.agents.Courier import Courier
        for item in answer.split("\n"):
            item_json = json.loads(item)
            item_json = {key.lower(): value for key, value in item_json.items()}
            content = item_json.get("content", "")
            receiver = item_json.get("interactant", "")
            if content == "" or receiver == "":
                continue
            if receiver in others_name:
                Courier.send(msg=content, sender=self.name, receiver=receiver, timestep=timestep)
                self.save(experience=content, source="think", interactant=receiver)

    def reply_on_demand(self, message: dict, timestep: int) -> None:
        # 预测的要做的事情, 塞到memory中, 交互对象也塞到
        # 问语言模型交互对象
        from AISimuToolKit.exp.agents.Courier import Courier
        others_name = list(set(Courier.all_receivers_name()) - {self.name})

        if message is not None and message != {}:
            think_what_to_do_next_prompt = f"The following is send from {message['from']}, please read about it and decide what would {self.name}want to do\n"
            think_what_to_do_next_prompt += "{}\n".format(message["content"])
        else:
            think_what_to_do_next_prompt = "What do you want to do next?\n"

        think_what_to_do_next_prompt += "Choose interactant's name from {}.\n".format(others_name)

        output_format = "output example:\n{\"interactant\":\"name\",\"content\":\"\"}\n{\"interactant\":\"name2\",\"content\":\"\"}\n"

        message_content = message.get("content", None) if message is not None else None
        answer = self.chat(message=think_what_to_do_next_prompt,
                           query=message_content,
                           need_recent_memory=True,
                           output_format=output_format)

        try:
            self.act_as_think(answer, others_name, timestep)
        except:
            self.logger.warning("get an unformatted string,try to fix it")
            try:
                fix_prompt = answer
                fix_prompt += "Format sentences above,output example:\n{\"interactant\":\"name\",\"content\":\"\"}\n{\"interactant\":\"name2\",\"content\":\"\"}\n"
                fixed_answer = self._inside_chat_wrapper(fix_prompt)
                self.act_as_think(fixed_answer, others_name, timestep)
                self.logger.info("Fixed it successfully")
            except:
                self.logger.warning("can not fix it,do nothing")

    def chat(self, message: str, query: str = None, need_relevant_memory: bool = True, need_status: bool = True,
             need_recent_memory: bool = False, output_format: str = None) -> str:
        prompt = self.get_background_prompt(query=query, need_relevant_memory=need_relevant_memory,
                                            need_status=need_status, need_recent_memory=need_recent_memory)
        prompt += message + "\n"
        if output_format is not None:
            prompt += f"output example:\n{output_format}\n"

        # self.logger.info("Chat with {}:{}".format(self.name, prompt))
        answer = self._inside_chat_wrapper(prompt)
        if output_format is not None:
            answer = f"{answer}\n\n Format sentences above,output example: {output_format}."
            answer = self._inside_chat_wrapper(answer)
        # self.logger.info(self.name + ":" + answer)
        return answer

    def chat_without_character(self, message):
        prompt = message + "\n"
        self.logger.info("Chat with {}:{}".format(self.model.get_backend(), prompt))
        answer = self._inside_chat_wrapper(prompt)
        self.logger.info(self.model.get_backend() + ":" + answer)
        return answer

    def get_background_prompt(self, query: str = None,
                              need_relevant_memory: bool = True, need_status: bool = True,
                              need_recent_memory: bool = False) -> str:
        self.summarize()
        background_prompt = f"Act as you are {self.name}:{self.summary}.\n "
        if need_relevant_memory:
            memory_about_message = self.memory.retrieve_by_query(weights=self.retrieve_weight, query=query)
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
        self.mailbox.append({"from": sender, "content": msg, "timestep": timestep})

    def change_status(self):
        change_status_prompt = "Change your state based on your recent memory,status must be a specific action.A status must be very short."
        change_status_prompt += "Do nothing else."
        self.logger.debug(change_status_prompt)
        answer = self.chat(message=change_status_prompt,
                           query="Change your state based on your recent memory",
                           need_recent_memory=False,
                           need_relevant_memory=False,
                           need_status=True)
        self.status = answer
        self.logger.history("agent {} change status to {}".format(self.name, self.status))
