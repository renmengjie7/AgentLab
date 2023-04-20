# AISimulation

## TODO

1. reflection+测试
2. 改变experiment中运行的结构为逐行代码
3. finetune

## Installation

本地在`python==3.10`上运行，其他依赖参考`requirements.txt`

## Usage

主要流程为`main.py`中根据定义的`json`文件构建基础环境，然后根据返回的`experiment_id`调用`start_experiment`
方法开始实验，实验流程为调用不同的`actions`做操作，在每轮实验的每次操作结束之后，可以通过terminal选择继续或各种指令与agent进行交互。下面是主要的模块介绍：

### Model

`src/utils/model_api.py`文件。支持为每个agent定义一个model，目前支持`gpt-3.5`
的api交互（但返回部分结果待测试），LLaMa的finetune（这个也需要进一步测试）。如果需要额外自定义model，可以继承`ApiBase`
之后，增加`ModelNameDict`字典。主要交互逻辑为：

```python
def chat(self, content: str, *args, **kwargs) -> str:
  message = [
    {"role": "user", "content": content}
  ]
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=message,
  )
  return completion.choices[0].text
```

实验开始时，会为每个agent构建一个model，储存在`ExpeInfo`中的字典`models`
中，key为agent的id，value为model的实例。在每次交互时，可以根据agent的id从字典中取出对应的model，然后调用`chat`等方法

### External_ToolKit

`src/utils/model_api.py`
文件。设想中，所有与外部工具（如推荐系统的交互）都可以通过api来实现，这部分待补充。每个toolkit可以有针对的不同agent，具体为设置的json中包含一个`target`
字段，这部分逻辑也待补充。

### Actions

`src/exp/actions`文件夹。任何agent的交互（无论是与model还是与外部工具）都可以通过action来实现，用户可以组合预先定义好的和自定义的action完成实验操作。目前支持的action有：

* `ActionBase`：基础action，所有action都需要继承这个类，实现`run`方法，这个方法不会在实际过程中调用
* `InstructAction`: 用于向agent发送指令，这个action不会与LLM产生交互，只是将输入的部分储存到对应的agent的memory中
  * 传递参数为`[{"agent_id":agent_id,"message":message"}]`，将会对所有对应的agent执行操作
* `ProbeAction`: probe取探针的意思，用于实验过程中对agent的评估，问题会与LLM交互，可以选择是否储存到memory中
  * 参数为`["agent_id":agent_id,"message":message","save":save_in_memory]`，其中`save`是一个`bool`类型变量
* `ReflectionAction`:
* `RS`:写了一个简单的交互逻辑，主要用于演示如何调用相关变量

如果需要自定义action，可以直接在目录下增加python文件。实验初始化过程中，会遍历该目录下所有的文件，将所有继承`ActionBase`
的类储存在`actions`
字典中，key为类名，value为类的实例。实验过程中可以调用对应的`run`方法。

### Expe_info

`src/exp/expe_info.py`文件。该部分主要用于储存实验相关变量。`BaseAction`中储存了`expe_info`，需要的话可以直接调用

```python
class ExpeInfo:
  def __init__(self, agents: List[Agent], models: List[ApiBase], toolkits: List[ExternalToolkitApi], config: json):
    self.agents = agents
    self.models = models
    self.toolkits = toolkits
    self.config = config
```

### Logger

`src/store/text/logger.py`
文件。实现了一个日志记录器，实现了单例模式（线程安全和进程安全），日志包括debug、info、warning、error、critical五个级别,可以通过`log_console`
和`log_file`参数控制是否将日志输出到控制台和文件。额外实现了一个log方法，等价于warning。实现了一个`history`
函数，该函数会首先调用`info`方法，然后将日志储存到`history`文件中。`log`文件用于储存所有的日志，`history`
文件用于储存实验过程中的操作记录。在调用时可以有所区别。

### Memory

`src/exp/agents/memory.py`文件。每个agent都有一个memory，json格式存储记忆，字段包括自增id，交互对象，对话的两端，时间。memory的结构为：

```python
memory_item = {"id": self.memory_id, "interactant": interactant, "question": question, "answer": answer,
               "time": str(current_time)}
```

实现了根据`id`，`interactant`
和最近访问的查找方法。记忆保存在内存中，同时会以append的形式不断插入文件。可以调用`export_memory`覆盖导出。

## 备注

不一定所有方法和变量都测试到了，如果有bug可以随时联系。对于建议修改调整的部分，可以在文档中增加TODO。
另外，chatgpt接口返回的`finish_reason`的情况有待进一步测试，目前没找到除了stop以外的例子。


