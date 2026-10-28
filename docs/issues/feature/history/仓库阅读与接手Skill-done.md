# 仓库阅读与接手 Skill

> 完成: 2026-10-28 ｜ 责任: agent ｜ 创建: 2026-10-28

## 背景与目标

新工程师接手一个陌生仓库时，常见做法是让 agent 通读代码后给一份摘要。这条路径产出的是**一次性的叙述**：用户点头，但没有可验证的理解，对话结束后不留任何状态，下一次仍要重新开始。

目标：新增第一方 skill `repo-read-assistant`，把仓库阅读变成一套**预测先行的多会话课程**——先对齐术语，再追踪一条端到端调用链，随后讲解关键抽象与架构，并把掌握度画像持久化到目标项目的 `docs/teach/` 下，使理解能跨会话存活。

## 范围

- 目标仓库只读；仅 `docs/teach/<user>/` 可写。允许执行构建与测试，禁止修改源码。
- 三种模式：`tour`（model + map 两层）、`tutor`（默认，四份 brief）、`drill`（模型检验与间隔复习）。
- 四份 brief：`00-model.md`（≤600 词）、`01-map.md`（≤1500）、`02-structure.md`（≤2500）、`03-operations.md`（≤2000）。
- 产物：四份 brief + `runbook.md` + `glossary.md` + `profile.yml` + `sessions/YYYY-MM-DD.md`。
- 不在本条目内：自动修改目标仓库、生成目标项目的正式架构文档、发布 / 推送 / 上架。

## 方案（已批准）

- **默认 tutor，可随时降级**：用户说「直接告诉我」或等义表达时，当轮降级为讲解，不争辩、不重新协商；降级只作用于当前目标。
- **用大白话，不暴露方法论**：预测、信息预算、spine、阶段、density、L0-L4 均为内部用语，不得出现在对用户的提问里；首次会话最多两次预测；预测只挡解释、不挡直接提问（用户提问先回答）；一次只问一项，四选一配对视为考试而非预测。
- **教学单位是文档（brief），不是回合**：每层一份完整文档，覆盖该层从粗到细的信息，用户一次读完；对话轮只做检验与纠偏（≤150 词），不承载授课。旧设计「每轮 1 个概念 / ≤200 词」被实测证明会把模型切碎，用户无法在一轮问答内建立可用模型，已废弃。
- **目标是设计者模型**：六段——一句话（替谁解决什么）、约束、核心回路（5-7 步）、名词（5-8 个实体）、接缝、刻意不做。最后一项用于解释那些看起来奇怪的结构。
- **渐进细化而非渐进披露**：每层都在细化同一个整体模型；每份 brief 必须显式声明「本层刻意忽略什么」，否则粗糙模型会变成错误模型。
- **预测后置**：零模型时预测只能得到「不知道」。新顺序是「带着一个问题读 → 读完检验 → 用错误修正模型」；预测从门槛变成检验手段。
- **交付规则**：brief 落盘到 `docs/teach/<user>/`，对话只给路径、一句「为什么是这层」和一个「读的时候带着的问题」；仅 ≤1 页的 `00-model.md` 在对话内联全文，避免两处副本漂移。
- **用锚点代替代码块**：正文以 `path:line` 为主，每份 brief ≤3 个短代码块，由用户自己去读。
- **掌握度 L0-L4 与校准度**：`L0 unknown`、`L1 locate`、`L2 explain`、`L3 predict`、`L4 apply`；`confidence`（自评）与 `accuracy`（实测）分开记录，差值即校准偏差，过度自信优先干预。profile 只存证据（用户的原话、预测内容、错误点），不存「已掌握」。
- **先教哪层先问用户**：「你接手后最可能先动哪块？」答案写入 `profile.focus`。答不出时回退到用户价值最高的入口，并显式说明是回退；focus 过于边缘时提示该链路绕开核心。
- **地图先作假设**：`01-map.md` 的每条边先标 `inferred`，逐跳验证后改为 `verified`；架构文档只写对既有文档的差异。
- **不重复造词**：先读 `CONTEXT.md`、`docs/agents/domain.md`、`docs/product/02-architecture.md`、`README`、`AGENTS.md`，只写增量；重复的术语表或架构文档视为缺陷。
- **过载分两层处理**：brief 层靠「顶部摘要 + 标题跟随模型而非文件树 + 长度上限」防灌水；对话层靠 ≤150 词与「答非所问 / 连续跳过即收缩」防疲劳。连续两次答错则直接修正模型，不硬耗。
- **分发接入**：`bin/install.js` 第一方清单（kind `repo-read-assistant`）、`package.json` 版本 **5.4.0**、`README.md` 中英文说明、`skills_zh/README.md` 镜像清单。
- **镜像**：英文源为事实来源，`skills_zh/repo-read-assistant/` 为人工审校的中文镜像，目录名与 `name` 一致。
- **不做**：不发布、不推送、不创建 git tag、不执行 `npm publish`。

## 完成判据

- [x] `skills/repo-read-assistant/` 含 `SKILL.md`、`references/{curriculum,questioning,rubric,repo-archetypes}.md`、`assets/{model,map,structure,operations,runbook,glossary,session}.template.md` 与 `assets/profile.template.yml`，共 13 个文件。
- [x] `SKILL.md` 覆盖「文档而非回合」、设计者模型六段、渐进细化、四份 brief 契约、交付规则、七步会话循环、双层预算、大白话约束、掌握度模型、产物布局、既有文档关系、硬约束、发送前自检、白板验收与反模式。
- [x] `skills_zh/repo-read-assistant/` 提供同结构中文镜像，`node scripts/check-skills-zh.js` 全项 PASS。
- [x] 分发元数据一致：六个第一方 skill、版本 5.4.0、安装器 dry-run 计划 kind `repo-read-assistant`，中英文安装均列出该 skill。
- [x] `npm pack --dry-run` 列出 `skills/` 与 `skills_zh/` 各 13 个文件。
- [x] 未发布、未推送、未创建 tag。

## 步骤

- [x] 规划（需求对齐与方法论评审：术语同步、调用链追踪、预测先行的主动学习）
- [x] 骨架（`SKILL.md` + 四篇 references + 八个 assets 模板）
- [x] 细节（brief 契约与长度上限、模型检验题、评分 rubric、仓库原型判定表、大白话约束）
- [x] 分发接入（`bin/install.js`、`package.json`、`README.md`、`skills_zh/README.md`）
- [x] 中文镜像与一致性校验
- [x] 验证（见「结果」）
- [x] 回顾（文档同步与版本号）

## 结果

交付（英文 `skills/`，中文镜像 `skills_zh/`）：

| 文件 | 说明 |
| :--- | :--- |
| `SKILL.md` | 「文档而非回合」、设计者模型六段、渐进细化对照表、四份 brief 契约、交付规则、七步循环、双层预算、大白话约束、掌握度模型、产物布局、既有文档关系、硬约束、自检、白板验收、反模式 |
| `references/curriculum.md` | 四份 brief 的写作手册：先读什么、grep 目标、章节骨架、长度上限、自检题、通过标准、刻意忽略项；既有文档复用与增量 |
| `references/questioning.md` | 「读的时候带着一个问题」、读后三类模型检验、复述与白板、brief 层与对话层的过载处理、降级与「我不知道」 |
| `references/rubric.md` | L0-L4 证据判定、模型不连贯封顶 L2、好 / 坏证据样例、校准公式与阈值、1/3/7/21 天复习排期 |
| `references/repo-archetypes.md` | 8 类仓库原型的入口位置、`01-map.md` 中链路的含义、top-down 阅读的失效点 |
| `assets/*.template.md` | model / map / structure / operations / runbook / glossary / session 七份模板 + `profile.template.yml` |

验证证据：

- `node scripts/check-skills-zh.js`：6 类检查全项 PASS，退出 0（fixture 74 文件、逐字节复制 41 文件、frontmatter 6 项）。
- `node --check bin/install.js`：通过。
- `node bin/install.js --dry-run --dir <tmp>` 与 `--zh` 变体：计划中均出现 `repo-read-assistant`。
- `npm pack --dry-run`：中文与英文各 11 个文件全部入包。
- 英文源 1282 行、13 个文件、无 CJK 字符；中英文件集与行数一致，`SKILL.md` heading 数一致（21:21），四份 brief 字数上限（600/1500/2500/2000）两侧一致。

残余风险：理解效果依赖用户配合预测，低动机场景下可能退化为 `tour`；`04-architecture.md` 无独立模板，结构定义在 `references/curriculum.md` 的 Stage 4，避免与既有架构文档重复。

## Log

- 2026-10-28 需求对齐：确定三点方法论（术语同步、端到端调用链、预测先行的主动学习）与产物落盘目标。
- 2026-10-28 方法论评审：补充「先跑起来 + 最小穿透实验」、测试即规范、变更影响推演、历史考古、边界与数据模型优先、失败路径巡游、间隔复习与冷启动验收；确定信息预算与过载降速机制。
- 2026-10-28 实现 `SKILL.md`、四篇 references、六份模板与中文镜像。
- 2026-10-28 完成分发接入与验证；版本 5.4.0；未发布、未推送、未创建 tag。
- 2026-10-28 修正交互用语：新增「用大白话」约束与自检项，禁止把预测 / 预算 / spine / 阶段 / density / L0-L4 等内部词说给用户；预测只挡解释不挡直接提问；首会话最多两次预测；四选一配对改为一次只问一项。
- 2026-10-28 方法论重构：实测反馈「粒度太细、概念切割零碎、一轮问答无法建立可用模型」。教学单位由「回合」改为「文档（brief）」；目标改为重建设计者模型（六段）；渐进披露改为渐进细化；预测后置为读后模型检验；预算由「每轮 ≤200 词」改为「每份 brief 的字数上限」。
