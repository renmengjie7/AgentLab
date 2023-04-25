"""
@author: Guo Shiguang
@software: PyCharm
@file: agent.py
@time: 2023/4/19 9:22
"""
import json
import os.path
from typing import List

from AISimuToolKit.exp.agents.memory import Memory
from AISimuToolKit.model.model import ApiBase
from AISimuToolKit.store.logger import Logger


class Agent:
    """
    储存agent的信息   
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
        """_summary_ 保存智能体配置文件

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

    # 需要更广泛的自定义
    def _probe(self,
               message: str, decide_by: str = "summary",
               prompt: str = "Your name is {}\n Your profile is: {}. Now I will interview you. \n{}") -> str:
        """
        采访(量表), 不会留下记忆
        :param message:
        :param prompt: 需要根据任务自己设计
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

    def _save(self, experience: str, source: str = "experience") -> bool:
        """_summary_ 保存到记忆
        Args:
            experience (str): _description_ 经历
        """
        self.logger.history(
            f"agent_{self.agent_id} wrote in memory: {experience} because of {source}")

        importance = self._chat(self.importance_prompt.format(experience))

        try:
            importance = float(importance)
        except ValueError:
            self.logger.error("cannot convert importance to float,set to 5 by default")
            importance = 5.0

        self.memory.store(interactant='', experience=experience, source=source, importance=importance)
        return True

    def _finetune(self, num: int) -> bool:
        """_summary_ 让Agent在给定的语料上微调, 这里的语料是memory中的question和answer
        TODO 加个将经历转换成对话
        Args:
            num (_type_): _description_ 采用的memory数量
        """
        recent_memory = self.memory.retrieve_by_recentness(num)
        self.logger.info(
            f"agent_{self.agent_id} starts finetuning based on recent {num} memories")
        # 需要把finetune所使用的memory存储起来, 以便后续查看
        self.model.finetune(exp=self.exp_id,
                            path=self.path,
                            agent=self.agent_id,
                            config=self.model_config, datas=recent_memory)
        self.logger.info(
            f"agent_{self.agent_id} successfully finetuned based on recent {num} memories")
        return True

    def reflect_from_memory(self) -> None:
        """
        从记忆中反思，然后生成新的记忆
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
                self._save(experience=insight, source="reflect")

    def summarize(self) -> None:
        """
        生成agent的总结，用于替代profile
        :return:
        """
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

    # def _reflect(self,
    #              num: int,
    #              prompt: str = "Your name is {}\n Your profile_list: {}. How do you think your profile_list has "
    #                            "changed over the course of your recent experience? Here's your experience: \n"):
    #     """
    #     改变profile的反思
    #     :param num:
    #     :param prompt:
    #     :return:
    #     """
    #     recent_memory = self.memory.retrieve_by_recentness(num)
    #     profile = ''.join(self.profile_list)
    #     prompt = prompt.format(self.name, profile)
    #     # 拼接memory
    #     content = prompt + "\n".join(item['experience']
    #                                  for item in recent_memory)
    #     answer = self._chat(content)
    #     self.logger.history(f"agent_{self.agent_id} reflect: {answer}\nbased on memory{prompt}")
    #     return answer

    def decide(self,
               question: str = None, answers: List[str] = None,
               message: str = None,
               prompt: str = "Your name is {}\n Your profile is: {}. Now I will interview you. \n{}",
               save: bool = True, decide_by: str = "summarize"):
        """_summary_ 模拟人类决策
        decide=_probe+_save (if need)
        Args:
            question (str): _description_ 面临的问题
            answers (List[str]): _description_ 选项
            message (str, optional): _description_. Defaults to None. 如果提供了input则直接使用该字符串进行询问; 否则会使用question和input进行对默认prompt进行填充
            save (bool, optional): _description_. Defaults to True. 
            TODO 决策是否需要加入memory? 实际生活中肯定是加入了记忆, 但是这部分信息在read的时候也会加入, 可能会带来冗余与噪声
            :param decide_by:
        """
        if message is None:
            message = question + '\n'.join([answer for answer in answers])
        answer = self._probe(message=message, prompt=prompt, decide_by=decide_by)
        if save:
            self._save(experience=f'{message}. choosed {answer}', source="decide")
        return answer

    def read(self, text: str, prompt: str = 'You read a news {}'):
        """_summary_ 模拟人类阅读功能

        Args:
            text (str): _description_
            prompt (str, optional): _description_. Defaults to 'You read'.
        """
        self._save(experience=prompt.format(text), source="read")

    def eat(self, food: List[str], time: str = '', prompt: str = 'You ate {} {}'):
        """_summary_ 模拟人类吃东西

        Args:
            text (List[str]): _description_ 食物列表
            time (str, optional): _description_. Defaults to ''. 时间, 可以不给
            prompt (str, optional): _description_. Defaults to 'You ate {} {}'.
        """
        self._save(experience=prompt.format(','.join(food), time), source="eat")

    def talk(self, agent: 'Agent', context: str):
        """_summary_ 
        TODO 如果涉及交谈感觉就需要保留交流的上下文了
        TODO 还要区分主动被动? 存入记忆, 一句话占一条?
        Args:
            agent (Agent): _description_
            context (str): _description_
        """
        pass

    def _generate_natural_prompt(self, raw_prompt: str) -> str:
        pass
