同时也已经git clone好了对应的两个仓库，分别位于：
/home/jiajunliu/embodied_reasoner
/home/jiajunliu/alfred

我需要用上经典的ALFRED（其官网@https://askforalfred.com/ ）数据集来测试我的Embodied-Reasoner的跑分（我打算通过调用API的方式，我们的项目原先是通过调用“阿里云百炼”的API来执行的），可惜我发现一个问题就是ALFRED初始化场景使用的是Ai2thor-2.1.0版本，所以我核心想解决的问题是：
- 如何修改ALFRED代码，使其能够在Ai2thor版本为5.0.0的条件下(Embodied Reasoner支持的版本跑起来?

我希望你先指导我在这个服务器上配置好相对应的内容，下载好对应的数据集，然后我们一步一步解决我想解决的核心问题。

P.S. 我尤其关注ALFRED数据集中那些“目标物体”被“藏”在别的物体之中的任务（比如苹果被“藏”在冰箱里）

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
