from AISimuToolKit.exp.actions.base_action import BaseAction
from AISimuToolKit.exp.experiment import Experiment
from typing import List


class FinetuneAction(BaseAction):
    """
    让Agent在给定的语料上微调, 这里的语料是memory中的question和answer
    """
    
    def __init__(self, expe: Experiment):
        super().__init__(expe)
        
    def run(self, finetunes: List[dict], *args, **kwargs):
        """
        对多个agent进行微调, num表示采用的memory数量
        :param instructions:[{"agent_id":agent_id,"num":num}]
        """
        # 每个都进行finetune
        for item in finetunes:
            self.finetune(agent_id=item['agent_id'],
                          num=item['num'])
            
    def finetune(self,
                 agent_id: int,
                 num: int):
        recent_memory = self.expe.agents[agent_id].memory.retrive_by_recentness(num)
        
        # 需要把finetune所使用的memory存储起来, 以便后续查看
        self.expe.models[agent_id].finetune(exp=self.expe.id,
                                            path=self.expe.agents[agent_id].path,
                                            agent=agent_id,
                                            config=self.expe.agents[agent_id].config, datas=recent_memory)
