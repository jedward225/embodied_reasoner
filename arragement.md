我是Embodied-Reasoner的开发人员，现在我在一台单卡4090服务器上重新clone了我的项目，你也可以在@https://embodied-reasoner.github.io/ 查看到我的项目简介。

现在我已经安装好了双conda环境——
一个是 er_train python=3.11
一个是 er_eval python=3.9
对应在er_train下安装了requirements.txt，在er_eval下安装了ai2thor==5.0.0 opencv-python matplotlib

同时也已经git clone好了对应的两个仓库，分别位于：
/home/jiajunliu/embodied_reasoner
/home/jiajunliu/alfred


我需要用上经典的ALFRED（其官网@https://askforalfred.com/ ）数据集来测试我的Embodied-Reasoner的跑分（我打算通过调用API的方式，我们的项目原先是通过调用“阿里云百炼”的API来执行的），可惜我发现一个问题就是ALFRED初始化场景使用的是Ai2thor-2.1.0版本，所以我核心想解决的问题是：
- 如何修改ALFRED代码，使其能够在Ai2thor版本为5.0.0的条件下(Embodied Reasoner支持的版本跑起来?

我希望你先指导我在这个服务器上配置好相对应的内容，下载好对应的数据集，然后我们一步一步解决我想解决的核心问题。

P.S. 我尤其关注ALFRED数据集中那些“目标物体”被“藏”在别的物体之中的任务（比如苹果被“藏”在冰箱里）

根据我前期对pddl数据中的监测，大致的内容如下所示：
5851 / 7080 trajectories (82.64%) start with target INSIDE another object.
  train         5436 / 6574   (82.69%)
  valid_seen     204 / 251    (81.27%)
  valid_unseen   211 / 255    (82.75%)

Breakdown by target type:
  Mug               271
  KeyChain          220
  CreditCard        220
  SoapBar           212
  Potato            188
  Egg               182
  Tomato            182
  Apple             177
  Cup               176
  CellPhone         175
  RemoteControl     173
  Cloth             162
  ButterKnife       153
  Pencil            150
  Pen               148
  Spoon             141
  ToiletPaper       136
  Plate             135
  DishSponge        134
  Lettuce           131
  Bowl              131
  Book              127
  SprayBottle       126
  SoapBottle        119
  CD                118
  Candle            118
  Fork              116
  Pan               109
  Knife             101
  Watch              96
  AlarmClock         93
  Newspaper          93
  Ladle              93
  HandTowel          92
  Spatula            90
  Pillow             89
  Pot                87
  Statue             79
  Laptop             71
  TissueBox          68
  Kettle             66
  Bread              62
  Vase               62
  PepperShaker       42
  Box                40
  SaltShaker         34
  WineBottle         34
  Glassbottle        23
  WateringCan         6

Top receptacles:
  CounterTop       1302
  DiningTable       782
  SideTable         382
  Cabinet           345
  Shelf             307
  CoffeeTable       253
  Drawer            251
  Desk              238
  Dresser           229
  SinkBasin         221
  Fridge            198
  Toilet            189
  Sofa              184
  GarbageCan        181
  Bed               172
  StoveBurner       158
  BathtubBasin      106
  ArmChair          100
  HandTowelHolder    92
  Microwave          69


第三阶段：搭建评测框架与执行评测
核心目标：测试一个视觉语言模型(VLM)或大语言模型(LLM)在接收到一个自然语言指令后，能否在模拟环境中有效推理、规划并执行动作以达成目标。

我们不只是看模型最终是否完成了任务，更要衡量其过程的效率与正确性。

评测流程：
1. 加载任务：系统从第二阶段生成的中间任务 JSON 文件中读取一个测试案例，包含：
    *   需要加载的 ai2thor 场景 (e.g., FloorPlan1)。
    *   给模型的自然语言指令 (e.g., "帮我找一下房间里的信用卡?")。
    *   用于最终计算指标的、基准的“关键动作”序列 (Ground-Truth Key Actions)。(此部分需从原始数据中额外解析)

2. 初始化环境：启动 ai2thor 5.0.0 模拟器，重建任务场景，模型获取初始的第一人称视角图像。

3. 模型交互循环 (核心测试环节)：
    a. 观察(Observation): 模型获得当前的第一人称视角图像、高级目标、以及历史思考和动作。
    b. 提问(Prompting): 脚本将以上信息整合成一个 Prompt 提交给 VLM (如 Qwen)，询问：“这是你的目标、你的所见、你的历史记录。请进行思考，并给出下一步动作。”
    c. 模型推理(Model Inference): VLM 生成回应，其中应包含“思考”和“动作”，例如：`<thought>信用卡可能在桌子上。我看到一个台面，我会先去那里。</thought><action>navigate to CounterTop</action>`。
    d. 动作执行(Action Execution): 脚本解析出动作，并在 ai2thor 环境中执行。
    e. 记录(Recording): 保存这完整的一轮交互（图像、模型的思考/动作、动作结果），构成一条完整的轨迹(Trajectory)。

4. 任务终止：当模型输出 `end` 动作，或超出最大动作步数限制时，循环结束。

评测指标：
任务轨迹生成后，系统会将其与基准“关键动作”序列进行比较，计算核心指标：

1. 成功率 (Success Rate, SR): 最重要的指标。模型是否按正确顺序完成了所有“关键动作”，并且最终环境状态正确？

2. 任务完成度 (Task Completeness, TC): 模型完成了百分之多少的关键动作？此指标用于奖励能取得部分进展的模型。

3. 路径效率 / 探索效率 (Path/Search Efficiency): 模型执行的总步数与完成任务所需的最少关键动作数之比。衡量模型是否走了弯路。

这个评测流程构成了我们对 Embodied-Reasoner 模型进行评测的基础。
