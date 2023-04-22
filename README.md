# AISimulation

## Installation

`python==3.10`上运行，其他依赖参考`requirements.txt`

## Demo

示例见`demo.py`
1. 根据传入的`json`文件, 实例化Experiment
``` python
exp = Experiment.load_exp(file="test/files4test/expe_config.json",
                          output_dir="experiments")
```
2. 实例化`actions`, 调用`get_action`
```python
def get_action(exp):
  instruct_action = InstructAction(expe=exp)
  probe_action = ProbeAction(expe=exp)
  reflect_action = ReflectAction(expe=exp)
  finetune_action = FinetuneAction(expe=exp)
  return instruct_action, probe_action, reflect_action, finetune_action
```
3. 自定义原子化操作顺序, 下面以probe为例说明使用
```python
result = probe_action.probe(agent_id=1,
                            input='Do you like chinese food ?',
                            prompt="Your name is {}\n Your profile_list: {}. Now I will interview you. \n{}")
```


## 目录结构
```shell
aisimulation/
├── demo.py             //使用示例
├── README.md
├── requirements.txt
├── scripts_TODO             // 存放脚本的文件
├── AISimuToolKit
│   ├── exp
│   │   ├── actions     // 定义原子操作
│   │   │   ├── base_action.py
│   │   │   ├── __init__.py
│   │   │   ├── instruct_action.py
│   │   │   ├── probe_action.py
│   │   │   ├── reflect_action.py
│   │   │   ├── rs.py
│   │   │   ├── setup.py
│   │   │   └── think.py
│   │   ├── agents            // agent与agent所有的memory
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── memory.py
│   │   ├── experiment.py     // 实验类, 实例化以对与平台交互的部分进行管理
│   │   └── __init__.py
│   ├── __init__.py
│   ├── model                 // 平台支持的LLM
│   │   ├── __init__.py
│   │   ├── model.py          // 存放LLM的API
│   │   └── register.py       // 注册每个LLM, 以便通过config使用
│   ├── store
│   │   ├── __init__.py
│   │   └── text
│   │       └── logger.py
│   └── utils 
│       ├── __init__.py
│       └── utils.py
├── temp                     // 暂时不用
│   ├── api_deprecated.py
│   |── model_api.py
│   └── rs.py
└── test
    └── files4test          // 示例config
        └── expe_config.json
```
下面对每个模块进行详细说明

### Model

`AISimuToolKit/utils/model_api.py`文件。支持为每个agent定义一个model，目前支持`gpt-3.5`的api交互（但返回部分结果待测试），LLaMa的finetune（这个也需要进一步测试）。如果需要额外自定义model，可以继承`ApiBase`
之后，增加`ModelNameDict`字典。主要交互逻辑为：

```python
def chat(self, query: str, config: dict, *args, **kwargs):
    message = [
      {"role": "user", "content": content}
    ]
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=message,
    )
    return completion.choices[0].text
```

实验开始时，会为每个agent构建一个model，储存在`Experiment`中的字典`models` 中，key为agent的id，value为model的实例。在每次交互时，可以根据agent的id从字典中取出对应的model，然后调用`chat`等方法

<!-- ### External_ToolKit

`AISimuToolKit/utils/model_api.py`
文件。设想中，所有与外部工具（如推荐系统的交互）都可以通过api来实现，这部分待补充。每个toolkit可以有针对的不同agent，具体为设置的json中包含一个`target`
字段，这部分逻辑也待补充。 -->

### Actions

`AISimuToolKit/exp/actions`文件夹。任何agent的交互（无论是与model还是与外部工具）都可以通过action来实现，用户可以组合预先定义好的和自定义的action完成实验操作。每个原子操作都对应一个action, 同时提供`run`方法以用于对多个agent同时进行操作

目前支持的原子action有：

* `ActionBase`：基础action，所有action都需要继承这个类，实现`run`方法，这个方法不会在实际过程中调用
* `InstructAction`: 用于向agent发送指令，这个action不会与LLM产生交互，只是将输入的部分储存到对应的agent的memory中
  * 传递参数为`[{"agent_id":agent_id,"question":question,"answer":answer}]`，将会对所有对应的agent执行操作
* `ProbeAction`: probe取探针的意思，用于实验过程中对agent的评估，问题会与LLM交互
  * 参数为`[{"agent_id":agent_id,"input":input, "prompt": prompt}]`
* `ReflectionAction`: 反思, 旨在通过使用当前记忆流中的对话信息, 让LLM对自己的profile进行自我更新
  * 参数为 `[{"num":num,"input":bool, "output": bool, "prompt": prompt}]`
* `FinetuneAction`: 微调, 旨在通过对话形式对模型参数进行影响
  * 参数为 `[{"agent_id":agent_id,"num":num}]`, 微调模型的参数在实验的配置文件中`agent_list/model_settings/config`修改
<!-- * `RS`:写了一个简单的交互逻辑，主要用于演示如何调用相关变量 -->

如果需要自定义action，可以继承`ActionBase`。同时对`AISimuToolKit.model.register.ModelNameDict`通过`monkey patching`修改或直接`ModelNameDict['key']=CustomAction`
<!-- 实验初始化过程中，会遍历该目录下所有的文件，将所有继承`ActionBase`
的类储存在`actions`
字典中，key为类名，value为类的实例。实验过程中可以调用对应的`run`方法。 -->

### Experiment

`AISimuToolKit/exp/experiment.py`文件。该部分主要用于储存实验相关变量。`BaseAction`中储存了`expe`，需要的话可以直接调用

```python
class Experiment:
  def __init__(self, agents: List[Agent], models: List[ApiBase], toolkits: List[ExternalToolkitApi], config: json):
    self.agents = agents
    self.models = models
    # self.toolkits = toolkits
    self.config = config
```

### Logger

`AISimuToolKit/store/text/logger.py`文件
1. 实现了一个日志记录器
2. 实现了单例模式（线程安全和进程安全）
3. 日志包括debug、info、warning、error、critical五个级别,可以通过`log_console`和`log_file`参数控制是否将日志输出到控制台和文件。
4. 额外实现了一个log方法，等价于warning
5. 实现了一个`history`函数，该函数会首先调用`info`方法，然后将日志储存到`history`文件中。
6. `log`文件用于储存所有的日志, 例如debug等; `history`文件用于储存实验过程中的原子操作记录。在调用时可以有所区别。

### Memory

`AISimuToolKit/exp/agents/memory.py`文件  
每个agent都有一个memory，json格式存储记忆，字段包括自增id，交互对象，对话的两端，时间。memory的结构为：

```python
memory_item = {
  "id": self.memory_id, 
  "interactant": interactant, 
  "question": question, 
  "answer": answer,
  "time": str(current_time)
}
```

实现了根据`id`，`interactant`和最近访问的查找方法。记忆保存在内存中，同时会以append的形式不断插入文件。可以调用`export_memory`覆盖导出。


### Agent
```python
class Agent:
    """
    储存agent的信息   
    """

    def __init__(self, agent_id: int, 
                 name: str, profile: str, role: str, agent_path: str,
                 config: dict):
        self.agent_id = agent_id
        self.name = name
        self.profile = profile
        self.role = role
        self.config = config  
        self.memory = Memory(memory_path=os.path.join(agent_path, "memory.jsonl"))
```

## 备注

1. 对于使用模型为LLaMA且不涉及基于用户的协同过滤, 建议一个agent跑完再下一个, 这样可以减少模型load的时间

2. 不一定所有方法和变量都测试到了，如果有bug可以随时联系。对于建议修改调整的部分，可以在文档中增加TODO。
另外，chatgpt接口返回的`finish_reason`的情况有待进一步测试，目前没找到除了stop以外的例子。

3. prompt需要精心设计, 语言模型会拒绝回答
4. 本来的想法是reflect返回的结果直接存到profile, 但是现在LLM放回的结果不一定好, 就把这一句暂时抽了出来
5. finetune操作最好在数据集两位数以上进行, 不然无法拆分出valsets



## TODO
1. 不同语言模型的原子操作调用的接口不太一样
