# 原始资料与方法边界

记录日期：2026-11-18。本表整理本项目前期对话中核查的关键原始资料，用于支持研究设计和后续阅读。它不是声称穷尽全部相关论文的综述。

**本仓库尚未复现下列算法，也没有船臂实验结果。**“已核查”指阅读资料内容，不代表复现成功。正文访问受限的文献单独标记；不得只凭标题补写方法细节或缺陷。

期刊年份与会议名称用于识别出处。没有取得可完整核验的 2025 年中科院官方分区表，因此此处不添加未经确认的“一区/Top”等标签。动态软件文档会更新；实施时需记录实际版本和所用接口。

## P1 实施资料

### D1 MuJoCo：Fluid forces

- 官方文档：[Fluid forces](https://mujoco.readthedocs.io/en/stable/computation/fluid.html)。
- 已核查范围：两种内置现象流体力模型、密度与黏性、无额外流体状态的假设。
- 用途：明确内置阻力与自定义自由液面、排水浮力之间的边界。
- 限制：这些接口不自动构成经过验证的海洋水动力模型。

### D2 MuJoCo：Simulation、力与状态 API

- [Simulation](https://mujoco.readthedocs.io/en/stable/programming/simulation.html)。
- [API functions](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html)。
- [API types](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html)。
- 已核查范围：`mj_step1/mj_step2` 的积分器约束、派生状态时间一致性、`mj_applyFT`、`mj_contactForce`、状态保存与 warmstart。
- 用途：保证载荷作用点、接触力与训练数据时间语义正确，支持检查点恢复。
- 限制：API 名称正确不等于模型设置正确；实现后仍要做物理和数值检查。

### D3 Fossen’s Marine Craft Model

- 原始作者说明：[Fossen’s Marine Craft Model](https://www.fossen.biz/html/marineCraftModel.html)。
- 已核查范围：刚体与附加质量的分工、阻尼、恢复矩阵、相对流速和耗散性质。
- 用途：组织水动力模块，检查排水量、恢复关系和载荷重复计算。
- 限制：原文采用的 NED 与本项目 `z` 向上坐标约定需要转换；不能将整套刚体惯性和重力再次加到 MuJoCo 中。

### D4 MuJoCo Warp

- 官方文档：[MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html)。
- 已核查范围：批量吞吐与单步延迟的区别、physics callbacks、当前微分能力边界。
- 用途：P1 物理定义稳定后评估批量训练迁移。
- 限制：GPU 不自动改善单环境控制延迟；学习可微世界模型不要求物理后端自动微分。

### D5 Isaac Lab：粒子流体与相机实现参考

- [官方版本发布](https://github.com/isaac-sim/IsaacLab/releases)。
- [v3.0.0 MPM](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/concepts/using_mpm.html)。
- [v3.0.0 Coupled solvers](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/concepts/coupled_solvers.html)。
- [v3.0.0 Camera](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/concepts/sensors/camera.html)。
- 已核查范围：多后端架构、相机更新周期、MPM 与刚体的单向/双向作用及实验性支持。
- 用途：腕部相机与 F 粒子流体支线的选型参考。用户已确定最终版本采用粒子流体，具体求解器仍需实测选择。
- 限制：以 Isaac Lab 调用 MuJoCo-Warp，不能据此声称获得独立于 MuJoCo-Warp 的物理验证；粒子流体示例也不等于海洋环境已验证。

### D6 AgileX：Piper 家族官方机器人资产

- 官方仓库：[agx_arm_urdf](https://github.com/agilexrobotics/agx_arm_urdf)。
- 已核查范围：2026-11-18 阅读官方 README 的型号表、目录和使用说明；其中分别列出 `piper` 与 `piper_h` 的 URDF 和 `with_gripper` Xacro。
- 用途：正式 P1 选择 Piper 型号、机械臂和官方夹爪资产的候选来源。Piper H 仅为当前参考配置，需要固定选定的资产与提交版本。
- 限制：尚未锁定 commit、逐项审计 URDF 质量/惯量与限位，也未导入 MuJoCo 验证；不能据 README 宣称资产已通过物理检查。旧通用参数仅为 `reference_proxy`，不能替代这些核对。
- 型号与固件参考：[官方 Piper firmware reference](https://github.com/agilexrobotics/pyAgxArm/blob/master/docs/piper/firmware_reference.md)。该资料区分 `piper` 与 `piper_h`，控制接口还取决于固件；本项目尚未完成硬件控制接口核验。

### H1 经用户授权的硬件记录与证据边界

- 授权日期：2026-11-18。范围仅包括 π 系列算法与腿臂协同控制项目中的相关硬件事实；科学论证不使用无关记忆。
- 证据级别：**授权对话检索记录，未独立复核原始采集文件**。π 项目 2026-11-16 至 17 的记录涉及 Piper H、官方夹爪与单腕部 Orbbec DaBai DC1；新项目机械臂仅暂定 Piper 家族，H 是参考配置。
- 成像记录为 RGB 640×480、约 30 Hz，以及原始毫米单位、未配准的 Depth 640×400；这些是记录中的采集配置，不是相机完整性能规格，也不代表当前仿真或实机已验证。内外参、安装变换、称重与惯量仍待核对，详见 [CAMERA_SPEC.md](CAMERA_SPEC.md)。
- 不将其他项目的 Revo3 手或六维力传感器写入已选硬件，不公开原始聊天与个人信息，也不把记录中的硬件使用经验当成本项目的实验结果。

## 直接约束方法设计的论文

### R1 SuperMimic

**SuperMimic: Scaling Humanoid Whole-Body Control with One Differentiable World Model** — CoRL 2026。

- [作者全文](https://arxiv.org/pdf/2610.28480)。
- [项目主页](https://supermimic.github.io/)。
- [官方代码](https://github.com/HybridRobotics/supermimic)。
- 已核查范围：模型与策略训练流程、短时模型展开、部署接口、实验和限制；前期调研同时核对了官方代码中的动力学、策略学习与导出路径。
- 支持的设计：由普通仿真数据学习可微模型，通过模型梯度训练可部署反馈策略。
- 边界：不是简单蒸馏；已展示的接触丰富人形控制，不等于未知波浪下的船臂外物操作已经验证。原文明确平地训练及外部物体操作扩展边界。其仿真上下文与已知参考运动不能直接当作本项目可部署观测。

### R2 DDPPO

**Gradient Information Matters in Policy Optimization by Back-propagating through Model** — ICLR 2022。

- [会议全文](https://openreview.net/references/pdf?id=PPXhzYSbe)。
- [作者机构出版记录](https://www.microsoft.com/en-us/research/publication/gradient-information-matters-in-policy-optimization-by-back-propagating-through-model/)。
- 已核查范围：§4 的模型梯度误差分析，§4.3 式(9)–(11) 的方向监督及模型使用方式，MuJoCo 实验与消融。
- 支持的设计：预测误差与梯度误差需要分别考虑；论文利用经验池近邻输出差分约束 Jacobian 的方向投影，并区分正向预测模型和反向梯度模型。
- 边界：有限差分监督方向导数已有明确先例。主动固定检查点、外扰与执行前缀是否改善该方法，属于本项目待验证扩展，不能提前称为已证缺陷。

### R3 MB-MIX

**Differentiable Information Enhanced Model-Based Reinforcement Learning** — AAAI 2025。

- [作者全文](https://arxiv.org/pdf/2503.01178)。
- [AAAI 出版页](https://ojs.aaai.org/index.php/AAAI/article/view/34419)。
- 已核查范围：§3.2 展开长度混合、§3.3 式(4) 状态/动作 Jacobian 监督、算法及实验。出版页访问可能受限，方法判断依据可获取作者全文。
- 支持的设计：显式监督动力学导数、混合展开长度已有先例。
- 边界：其算法从可微环境取得导数标签；但将导数替换为差分本身仍不能构成我们的原创点，因为 DDPPO 已使用数据差分。

### R4 Gradient estimators

**Do Differentiable Simulators Give Better Policy Gradients?** — ICML 2022。

- [正式出版页](https://proceedings.mlr.press/v162/suh22b.html)。
- [全文](https://proceedings.mlr.press/v162/suh22b/suh22b.pdf)。
- 已核查范围：刚性、不连续和长时域对估计的影响，一阶/零阶估计的偏差方差分析与混合方案。
- 支持的设计：梯度可计算不等于对优化有效；模型方向与真实改进需要验证。
- 边界：梯度混合或在接触附近减少解析梯度使用已有研究。本项目如采用类似机制，需要说明学习模型误差、隐藏外扰和延迟条件带来的额外问题。

### R5 RTC

**Real-Time Execution of Action Chunking Flow Policies** — NeurIPS 2025。

- [会议全文](https://papers.nips.cc/paper_files/paper/2025/file/300ccb2187dedd4edcc07f7e76d8e553-Paper-Conference.pdf)。
- [作者研究页面](https://pi.website/research/real_time_chunking)。
- 已核查范围：异步执行方法、已提交前缀冻结与后续动作生成、动态任务和实机实验；初始化时再次核对正式题名与方法章节。
- 支持的设计：计算新动作时环境继续演化，已保证执行的动作不能被新计划改写。
- 边界：加入异步队列或前缀处理不是本项目独立原创点。联合船臂目标物理预测及其学习作用需单独检验。

### R6 Confidence-Aware Capture

**Confidence-Aware Object Capture for a Manipulator Subject to Floating Base Disturbances** — IEEE Transactions on Robotics，2024。

- [DOI](https://doi.org/10.1109/TRO.2024.3463476)。
- [作者机构记录](https://cris.maastrichtuniversity.nl/en/publications/confidence-aware-object-capture-for-a-manipulator-subject-to-floa/)。
- 阅读边界：前期调研可核验摘要与作者资料，未取得可完整核读的正文。
- 可以支持：浮动基座扰动、置信信息和目标捕获已有相关研究。
- 不可据此支持：原文没有某个状态、没有恢复、没有某种延迟处理等未核读细节。实现其基线前需要取得正文或足够完整的作者实现资料；否则称为参考相关思路构造的基线，不称忠实复现。

### R7 AUTO-IceNav

**AUTO-IceNav: A Local Navigation Strategy for Autonomous Surface Ships in Broken Ice Fields** — IEEE Transactions on Robotics，2025。

- [作者全文](https://arxiv.org/html/2411.17155v2)。
- [官方代码与材料](https://github.com/rdesc/AUTO-IceNav)。
- 已核查范围：局部规划、船—冰接触成本、仿真与物理试验设置、限制；初始化时再次核对完整题名与框架说明。
- 支持的设计：船与可移动冰体接触、导航规划和物理验证已经有系统研究。
- 边界：不能将其导航结果直接视为船臂抓取或波浪下动态接触控制结果。其仿真/试验条件应在采用或比较前逐项对应。

## 投稿范围资料

- [T-RO 官方范围](https://www.ieee-ras.org/Publications/T-RO/)。
- [T-RO 作者说明](https://www.ieee-ras.org/publications/t-ro/t-ro-information-for-authors/)。

已核查其对重大原创结果和多种研究形式的说明。研究目标可以参照该深度规划，但文献背景、初始化文件、运行演示均不等于已经形成相应贡献。真实实验的选择应与最终物理主张匹配。

## 后续文献记录规则

新增方法前记录原始标题、版本、正式出处或预印本状态、可访问全文、具体阅读章节、实验设置、适用边界与本项目采用方式。未访问的正文不作细节推断；未复现的算法不写“已复现”。不得将不同论文的优点拼接为一项已经被实验证明的完整系统能力。
