# 船臂协同：浮动操作、动作条件世界模型与目标一致性

研究问题：**在波浪扰动和推理延迟下，如何利用动作条件世界模型，使语言指定的目标保持一致，并让无人船与机械臂在可行的时机完成接近、抓取和恢复？**

应用起点为水面刚性浮体／浮冰清理。论文目标参照 T-RO 等机器人学期刊的研究深度，以可证伪假设、强基线和实际证据判断贡献；不预先保证投稿结果。

> **当前状态：仓库与实施设计已初始化。仿真环境尚未实现，P1-01 至 P1-08 均为 NOT_RUN。**
>
> 本仓库目前包含规格、路线、任务、提示词和解析设计核算脚本。运行核算脚本不会启动 MuJoCo，也不会证明物理模型或相机通过验收。真实进度以 [STATUS](reports/STATUS.md) 为准。

## 已确定的方向

- **效果优先，允许充分随机探索。** 大规模随机动作扰动保留为正式实验路径；采样方法根据实际覆盖和效果比较，训练预算不作为预先裁减的理由。
- **初期使用刚体多体动力学与需经过验证的等效海洋载荷。** CPU MuJoCo 先建立可信的自由船体、臂、目标、波场和接触链路。
- **最终版本必须实现粒子流体。** 波浪生成、双向流固耦合及收敛、大规模并行和机器人学习都是正式研究内容。P1 之后启动 F 支线，在 P6 合流。
- **机械臂暂定 Piper 系列，加入官方平行夹爪和单台腕部 Orbbec DaBai DC1。** 授权的既有项目记录使用 Piper H；本项目最终具体变体仍需在资产配置中明确。
- **相机按 RGB 640×480、约 30 Hz，原始毫米深度 640×400、未配准的记录设计接口。** 真实 K/D、手眼外参、动态时间对齐和附件称重仍未核验；不得把虚拟参数当作实物标定。
- **科学判断独立于无关个人记忆。** 本次只将用户明确授权的两个项目硬件记录用于配置参考，出处与证据边界见 [相机与硬件说明](docs/CAMERA_SPEC.md)。

## 先读哪些文件

| 文件 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | Codex 的项目规则、读取顺序和证据要求 |
| [总路线](docs/ROADMAP.md) | P1–P7、推进依据与并行粒子流体支线 |
| [研究范围](docs/RESEARCH_SCOPE.md) | 科学问题、已有方法边界、候选创新与对照 |
| [阶段一规格](docs/PHASE1_SPEC.md) | 船臂、海洋载荷、相机、时钟与物理实现 |
| [阶段一任务](docs/PHASE1_TASKS.md) | 按依赖顺序执行的开发工作 |
| [阶段一验收](docs/PHASE1_ACCEPTANCE.md) | 八项实验、判据和必须保留的证据 |
| [系统接口](docs/ARCHITECTURE.md) | 模块、坐标、动作、时间和检查点 |
| [相机与硬件](docs/CAMERA_SPEC.md) | Piper/DC1 参考、虚拟与真实参数、单腕部观测 |
| [粒子流体路线](docs/FINAL_FLUID_TRACK.md) | 波浪、双向耦合、收敛、并行和学习 |
| [证据规则](docs/EVIDENCE_PROTOCOL.md) | 如何报告 PASS、失败、资源与复现 |
| [原始资料](docs/REFERENCES.md) | 论文、官方文档、阅读范围和待补全文 |
| [数值设计](configs/phase1_design.json) | 参数来源、解析代理与待绑定 Piper 资产 |
| [当前进度](reports/STATUS.md) | 已完成、未完成、下一个可执行任务 |

## 开始执行阶段一

在自己的开发环境中克隆仓库，然后在仓库根目录打开 Codex：

~~~bash
git clone https://github.com/kaiwen123-yang/idea-boat-and-arm.git
cd idea-boat-and-arm
codex
~~~

也可以在 Codex 应用中打开该本地目录，或在支持 GitHub 仓库任务的环境中选择本仓库。选择实际具备 Python、MuJoCo 安装与离屏渲染能力的执行环境；远端任务是否可用取决于所选环境。

把 [START_PHASE1.md](prompts/START_PHASE1.md) 的完整内容作为第一条任务。简短入口如下：

~~~text
在当前仓库开始阶段一。先读取 AGENTS.md、reports/STATUS.md、
prompts/START_PHASE1.md 及其中引用的规格和验收文档，然后执行
prompts/START_PHASE1.md 的完整任务。持续完成实现、运行、分析与修复，
不要停在计划。先核实 Piper 资产和 DC1 数据契约；不要把旧通用代理参数
当成 Piper 参数。按 P1-01 至 P1-08 保存真实证据并更新状态。
本次范围为完整 P1，不自动进入 P2 或后续训练。
~~~

任务中断后使用 [RESUME_PHASE1.md](prompts/RESUME_PHASE1.md)。续做应先检查代码、配置和证据是否仍对应，不凭上一轮自然语言总结直接宣布通过。

AGENTS.md 是 Codex 会读取的项目指令文件；其余文档由项目指令明确要求读取，不依赖文件名自动获得特殊执行能力。官方说明：[AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)。

## 当前可以实际运行的命令

~~~bash
python3 scripts/check_design.py
~~~

只核算 reference_proxy 的质量、规则水线面、吃水、恢复参照与相机采样关系。**旧的 12 kg 臂重、0.75 m 臂展、0.14 m 夹爪开口及 72.15 kg 总重全部属于通用代理对照，不是 Piper 规格。** 正式场景需固定官方资产版本、核对质量与限位，重算这些量，并检查目标大小、载荷、IK 与碰撞。

初始文档检查见 [BOOTSTRAP_CHECKS](reports/BOOTSTRAP_CHECKS.md)。当前没有可运行的仿真 CLI 或训练程序；后续由阶段一任务实现并记录实际安装与运行方法。

## 实施与证据位置

实现建议放在 src/boat_arm/；配置放在 configs/；完整运行先写入被忽略的 runs/；适量关键图像、曲线、轨迹和报告整理到 results/ 与 reports/。大数据使用可访问的外部存储并记录校验和，不能只留下不可访问的临时路径。

模型资产须记录版本、来源和许可，见 [assets](assets/README.md)。本次未替用户选定整个项目的开源许可证；引用或导入第三方资产仍须遵守其原有许可。
