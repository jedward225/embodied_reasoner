# Arrangement.md: 增强 Embodied-Reasoner 项目企划

- **项目名称:** 增强 Embodied-Reasoner: 基于精细化三维感知与多轮对话的交互能力提升

## **项目核心目标**

解决当前 Embodied-Reasoner 在复杂场景中面临的两大核心挑战：
1.  **同名物体混淆问题 (Homonym Ambiguity)**。
2.  **大型物体交互精度不足问题 (Large-Object Interaction Precision)**。

最终交付一个集成了精细化感知与多轮澄清对话能力的增强版智能体，并提供完整的评估报告与高质量代码。

---

## **第一阶段：基础构建与深度解析 (Weeks 1-2)**

**首要目标：** 不仅是搭建环境，而是建立对现有系统数据流和控制流的"心智模型"，为后续模块的无缝集成打下坚实基础。

**详细行动项：**
1.  **环境与代码库准备:**
    * [x] 按照 `README.md` 和你的计划，克隆并搭建 `Embodied-Reasoner` 的开发与评估环境 [cite: 21]。
    * [x] 重点关注 `ai2thor` 模拟器的安装与使用，确保你能顺利运行一个基础的评估案例。
    * ➕ **推荐环境:** Ubuntu-22.04 + CUDA 12.2 + PyTorch 2.2.2；WSL2 用户请先 `wsl --update` 并确认 NVIDIA 驱动 ≥ 535。
    * ➕ **双 Conda 环境:**
      ```bash
      conda create -n er_train python=3.11 -y      # 训练 / 数据引擎
      conda create -n er_eval  python=3.9  -y      # 评估 / ai2thor
      ```
    * ➕ **依赖安装:**
      `er_train` 内执行 `pip install -r requirements.txt`；
      `er_eval` 内执行 `pip install ai2thor==5.0.0 opencv-python matplotlib transformers==4.40.0`。
2.  **核心代码深度分析:**
    * [ ] **数据流追踪：** 从用户指令输入开始，追踪信息如何在 `RocAgent` [cite: 2]、`BaseAgent` [cite: 2]、`EventObject` [cite: 2] 等核心类之间传递。绘制一张数据流图，明确各类职责。
    * [ ] **定位逻辑复现：** 深入 `calculate_best_view_angles` 函数 [cite: 2]，理解其仅依赖几何角度和距离进行定位的局限性。尝试修改参数，观察其行为变化。
    * [ ] **物体识别与管理：** 详细分析 `Eventobject` 类中的 `item2object` 字典 [cite: 2]，理解为什么它无法区分同名物体。设想一个存在多个 `Book` 实例的场景，思考当前架构会如何失效。
3.  **方案细节验证:**
    * [ ] 编写一个独立的 Python 脚本，使用 `ai2thor` 的 API 获取RGB图像和深度图（Depth Map）。这是你后续所有感知工作的基础。验证你获取的深度信息是否准确。
    * ➕ `quick_test_ai2thor.py` 示例：
      ```python
      from ai2thor.controller import Controller
      c = Controller(scene="FloorPlan1", renderDepthImage=True, width=300, height=300, gpu_device=0)
      event = c.step("Pass")
      print(event.metadata["agent"]["position"])
      c.stop()
      ```
    * ➕ 跑通最小评估：`python evaluate/evaluate.py --num_cases 2 --device 0`（先将 `evaluate/utils.py` 的 `DEFAULT_MODEL_PATH` 设为 `None`，仅测试环境）。

4.  **常用代码入口与调试:**
    * ➕ 代码入口索引  
      | 目标 | 主要文件 | 阅读顺序 |  
      |------|----------|---------|  
      | 训练 | `scripts/train.sh` → `finetune/*/template.yaml` | 先看 shell，再看 yaml |  
      | 数据引擎 | `data_engine/TaskGenerate.py` → `o1StyleGenerate*.py` | 关注 json 结构 |  
      | 推理 | `inference/predictor/*_infer.py` | 理解 vllm/hf 两套推理 |  
      | 评估 | `evaluate/ai2thor_engine` | `RocAgent` 调用链 |  
    * ➕ 推荐使用 VS Code Remote-WSL + Pylance 调试；若渲染失败，可在 `evaluate/__init__.py` 中关闭 `renderDepthImage` 字段进行排查。

**关键交付物：**
* 一份Markdown文档，包含你绘制的数据流图和对核心类的功能分析笔记。
* 一个可成功运行 `ai2thor` 并抓取RGB-D图像的 `test_env.py` 脚本。

**技术考量与潜在风险：**
* **依赖管理:** Python环境依赖可能存在冲突，建议使用 `conda` 创建独立的虚拟环境。
* **理解偏差:** 初步理解可能与实际运行逻辑有出入，多通过 `print` 或调试器验证你的猜想。

---

## **第二阶段：轻量级空间签名与AABB区域划分 (Weeks 3-4)**

**首要目标：** 基于 AI2-THOR 元数据（中心坐标、AABB 尺寸、旋转矩阵）为每个物体实例生成轻量级 `SpatialSignature`，并利用 AABB 子区划分和简单几何-语义规则解决同名物体区分与大型物体精细交互，不依赖点云。

**详细行动项：**
1.  **基础空间签名生成:**
    * [ ] 在 `spatial_perception` 中实现 `SpatialSignature.from_metadata(obj_meta)`，保存 `objectId`、`center`、`size`(w,h,d)、`rotation`。
    * [ ] 在 `EventObject` 内维护 `id2signature` 字典，调用该方法为所有可见物体生成签名。

2.  **AABB 子区划分工具:**
    * [ ] 编写 `utils/region_utils.py`，提供 `slice_aabb(signature, schema="sofa")`，根据物体 `size` 与 `rotation` 输出预定义子区中心（如 `left_arm`、`right_arm`、`seat` 等）。
    * [ ] 预置三类 schema：Sofa、Table、Cabinet，可扩展。

3.  **几何-语义歧义消解:**
    * [ ] 当 `type2objects[obj_type]` 实例 > 1 时，比较 `center` 与房间锚点（Window、Door 等）或 Agent 位置，采用“最近/最左/靠窗”等规则自动选定候选。
    * [ ] 若仍有 ≥2 候选，则触发 `clarificationDialogueManager` 生成澄清问题。

4.  **精确交互点计算（非点云）:**
    * [ ] 对大型物体，调用 `slice_aabb` 获取目标子区中心，向 `+y` 方向上移 0.03 m 作为放置点。
    * [ ] 在 `BaseAgent` 中新增 `_navigate_to_3d_point(point)`，复用现有导航管线。

**关键交付物：**
* `spatial_perception/basic_signature.py` 与 `region_utils.py`
* 单元测试：  
  - 多本书场景下 `id2signature` 区分成功；  
  - “把杯子放在沙发右扶手”指令返回合理交互点。

**技术考量与潜在风险：**
* **旋转一致性:** AI2-THOR `rotation.y` 在 0-360°；需统一到物体局部坐标系。
* **区域 schema 通用性:** 初期规则可能覆盖不全，可在后续阶段增设点云扩展。

---

## **第三阶段：精细化感知 (Part B) - VLM驱动的交互适宜区预测 (Weeks 5-6)**

**首要目标：** 将"把书放在沙发上"这类模糊指令，转化为"把书放在沙发扶手的(x, y, z)坐标上"的精确动作。

**详细行动项：**
1.  **`AffordancePredictor` 类实现:**
    * [ ] 搭建 `AffordancePredictor` 类的基本框架 [cite: 5]。
    * [ ] 调研并选择一个合适的、轻量级的开源VLM（如LLaVA, Qwen-VL等），并研究其API。
    * ➕ 首选模型：Qwen-VL-Chat 7B（int4），单卡 24 GB VRAM 即可运行。
2.  **核心功能开发:**
    * [ ] **Prompt工程:** 设计一个强大的Prompt模板，如你所写 `f"Given the image, generate a heatmap indicating where one could '{instruction}'. Highlight the most suitable area."` [cite: 15]。
    * [ ] **热力图到3D坐标投影:** 实现 `project_2d_to_3d` 函数 [cite: 5]。这需要将2D热力图的峰值像素坐标 `(u, v)` 及其在深度图 `D` 中对应的值 `d`，通过相机的内参矩阵 `K`，反向投影到三维空间。公式为 `Z=d`, `X = (u - cx) * Z / fx`, `Y = (v - cy) * Z / fy`。你需要从AI2THOR环境中获取这些相机内参。
3.  **数据生成与微调准备 (并行):**
    * [ ] 开始编写数据生成脚本。利用PartNet等带有部件标注的3D模型库，在AI2THOR中渲染场景，自动生成 `(图像, 指令, Affordance掩码)` 格式的数据对 [cite: 12]。这是项目后期微调的关键。
    * [ ] 搭建VLM微调所需的基础设施，例如使用 `LLaMA-Factory` [cite: 23] 或 Hugging Face的 `PEFT` 库设置LoRA微调流程。

**关键交付物：**
* 一个可用的 `AffordancePredictor` 类，即便此时VLM未经微调，也应能调用通用VLM并走通整个"指令->热力图->3D坐标"的流程。
* 一个初步的 `generate_affordance_data.py` 脚本。

**技术考量与潜在风险：**
* **VLM的稳定性:** 通用VLM在没有微调的情况下，可能无法稳定生成合理的热力图。初期的重点是打通流程，而非追求完美精度。
* **2D-3D对齐精度:** 深度图的噪声或相机内参的微小误差都可能影响最终3D坐标的准确性。

---

## **第四阶段：歧义解决 - 多轮澄清对话系统 (Weeks 7-8)**

**首要目标：** 打造一个能主动发现并澄清指令歧义的对话管理器，让Agent具备"反问"能力。

**详细行动项：**
1.  **多轮澄清协议 (MCP) 状态机实现:**
    * [ ] 实现 `MCPStateTracker` 类，包含 `IDLE`, `AMBIGUITY_DETECTED`, `AWAITING_CLARIFICATION`, `RESOLVED` 四个核心状态及状态转移逻辑 [cite: 17]。
2.  **歧义检测逻辑:**
    * [ ] **场景歧义检测:** 将指令中的物体名词与第二阶段生成的"空间签名"数据库进行匹配。若匹配到多个实例，则触发歧义 [cite: 6]。
    * [ ] **交互歧义检测:** 检查第三阶段的 `AffordancePredictor` 是否返回了多个分离的高置信度区域。若是，则触发歧义 [cite: 6]。
3.  **`clarificationDialogueManager` 开发:**
    * [ ] 实现 `clarificationDialogueManager` 类，集成 `MCPStateTracker` [cite: 17]。
    * [ ] **核心流程 `process_command`:** 根据MCP的当前状态（`IDLE`, `AMBIGUITY_DETECTED`等）决定是执行动作、生成澄清问题还是处理用户回复 [cite: 18]。
    * [ ] **上下文感知的问题生成:** 实现 `generate_clarification_question` [cite: 19]。问题的关键是利用空间关系，例如 `"I see multiple bookshelves. Do you mean the one near the window or the one near the door?"`。这些空间关系可以从你的空间签名数据中提取。
    * ➕ 使用 HuggingFace `transformers.Conversation` 管理对话历史，初期可模板化问题，后续再引入 LLM 自动生成。

**关键交付物：**
* 完整的 `MCPStateTracker` 和 `clarificationDialogueManager` 模块。
* 单元测试，模拟不同类型的歧义场景（同名物体、多交互区），并验证对话管理器能正确地进入相应状态并生成合理的澄清问题。

**技术考量与潜在风险：**
* **状态管理的复杂性:** 对话逻辑可能比预想的复杂（例如用户回复了无关内容），需要设计好异常处理和状态重置机制。
* **澄清问题的自然度:** 早期版本的问题可能是模板化的，后续可以考虑利用LLM使其更自然。

---

## **第五阶段：系统集成与数据生产 (Weeks 9-10)**

**首要目标：** 将所有独立开发的模块（感知、对话）组装进 `Embodied-Reasoner` 的主干，并正式开始生产用于VLM微调的高质量数据。

**详细行动项：**
1.  **模块集成:**
    * [ ] 修改 `RocAgent` 的主决策循环。在收到指令后，首先调用 `clarificationDialogueManager`。
    * [ ] 如果没有歧义或歧义已解决，则调用 `pose_estimator` 获取精确的6D位姿，或调用 `AffordancePredictor` 获取精确的3D交互点。
    * [ ] 将这些精确的三维坐标传递给 `BaseAgent` 的导航和交互函数。
2.  **数据生产流水线:**
    * [ ] 运行并优化你在第三阶段编写的 `generate_affordance_data.py` 脚本，大规模生成 `(图像, 指令, Affordance掩码)` 数据 [cite: 22]。
    * [ ] 对生成的数据进行抽样检查，确保质量。
3.  **多模态特征融合方案设计:**
    * [ ] 根据你的计划，设计多模态特征融合模块 [cite: 16]。具体来说，你需要确定：
        * **视觉编码器:** 如何从RGB图像中提取特征（例如，使用VLM的视觉部分）。
        * **空间编码器:** 如何将你的 `SpatialSignature` 编码为向量。
        * **Affordance编码器:** 如何将VLM生成的热力图编码为向量。
        * **融合机制:** 设计交叉注意力（Cross-Attention）模块的结构。

**关键交付物：**
* 一个集成了所有新功能的 `enhanced_agent.py` 或修改后的 `RocAgent`。
* 一个包含数千条高质量标注的Affordance数据集（`.json` 或类似格式）。
* 多模态融合模块的详细设计文档或初步代码框架。

**技术考量与潜在风险：**
* **接口不匹配:** 集成时会发现各模块间的API定义需要调整，这是正常现象，需要耐心重构。
* **数据生成速度:** 数据生成可能非常耗时，考虑使用并行处理或在服务器上运行。

---

## **第六阶段：模型微调与评估框架 (Weeks 11-12)**

**首要目标：** 利用生成的数据对VLM进行SFT微调，并构建一个能科学衡量项目改进效果的评估体系。

**详细行动项：**
1.  **VLM微调:**
    * [ ] 使用第五阶段产出的数据集，对你选择的VLM进行监督式微调（SFT） [cite: 22]。重点是优化其生成Affordance热力图的能力。
    * [ ] 训练过程中密切关注验证集的损失，防止过拟合。
2.  **评估框架设计与实现:**
    * [ ] 设计三个核心评估场景，如你所计划：同名物体区分、大型物体精细操作、多轮澄清效率 [cite: 22]。
    * [ ] **量化指标:**
        * **同名物体区分:** 定义一个任务，例如"拿起离窗户最近的那本书"，评估成功率。
        * **精细操作:** 定义一个任务，例如"把杯子放在沙发的右侧扶手上"，测量最终放置点与目标点的欧氏距离。
        * **澄清效率:** 测量从发出模糊指令到任务最终执行所需要的对话轮次和总时间。
        * ➕ **成功阈值设定:** 精细操作若欧氏距离 ≤ 0.10 m 记为成功；澄清效率目标为平均对话轮数 ≤ 2。
    * [ ] 准备一个**基线模型**（即原始的Embodied-Reasoner）用于性能对比 [cite: 22]。

**关键交付物：**
* 一个微调后的VLM模型权重（或LoRA适配器）。
* 一个可运行的 `evaluation_framework.py`，能够自动化地在上述场景中测试智能体并输出量化指标。
* 一份文档，详细说明评估协议和指标定义。

---

## **第七阶段：全面评估、优化与交付 (Weeks 13-14)**

**首要目标：** 完成最终的系统测试、性能优化，并整理所有工作成果，准备项目交付。

**详细行动项：**
1.  **全面评估与分析:**
    * [ ] 在评估框架中对你的增强版系统和基线系统进行全面测试 [cite: 22]。
    * [ ] 生成图表，直观对比性能提升。分析系统的失败案例（Failure Cases），找出瓶颈所在（例如，是感知错误还是决策逻辑问题？）。
2.  **迭代优化:**
    * [ ] 根据评估结果进行针对性的性能优化和Bug修复 [cite: 22]。
    * [ ] 完善错误处理机制，例如，当VLM无法生成热力图时，系统应如何优雅地降级（graceful degradation）。
3.  **文档与交付:**
    * [ ] 编写高质量的 `README.md`，说明你的增强版系统的特性、如何安装和使用。
    * [ ] 为你添加的新模块和核心类编写清晰的API文档和代码注释 [cite: 22]。
    * [ ] 撰写项目总结报告，并准备最终的项目成果演示 [cite: 22]。

**关键交付物：**
* 最终的项目代码，包含所有新功能、模型权重和评估脚本。
* 一份详细的性能对比评估报告。
* 完整的项目文档和一份演示文稿（PPT/Slides）。
