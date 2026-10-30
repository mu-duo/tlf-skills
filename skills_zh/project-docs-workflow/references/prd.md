# PRD、SPEC、Current 与 ADR

PRD（产品需求文档）= **宏观产品叙事**——为谁而做、解决什么问题、典型应用场景、高层产品需求、架构 / 模块总览。**范围与意图**的权威。

SPEC（技术规格）= **实现事实标准**——带验收判据的功能需求、接口、NFR、可选机制设计。**实现细节**的权威。

Current = 选定基线下的**实际建成快照**，是唯一的状态来源。ADR = 带理由的决策记录，是**平级**文档，不是一层。Issue = 工作单元。

## 文档模型

| 文档 | 读者 | 角色 | 权威范围 |
| :--- | :--- | :--- | :--- |
| **PRD** | 用户 / 编排者 / 评审者 | 宏观产品叙事 | 范围、意图、用户旅程 |
| **SPEC** | 编码 agent / 编排者 | 实现事实标准 | 实现细节 |
| **Current** | 所有人 | 选定基线下的实际建成快照 | 实际状态 |
| **ADR** | 所有人 | 决策 + 理由（平级） | 为何做出某决策 |
| **Issue** | 编排者 / coder | 工作单元 | — |

## 设计模型，不是日志

PRD、SPEC、Current 记录的是**暂定设计**——当前持有的形态，用肯定陈述表达。它们是模型，不是历史。

- **只写你当前持有的设计。** 一条内容能对产品形态作出肯定陈述，才进 PRD / SPEC；做不到，就是未决——留白。
- **留白即未决。** 没写 = 该子空间仍开放，既不等于允许，也不等于禁止。先问再动。
- **推翻即删除。** 设计变了就删掉或改写该条；不写「曾」「此前」「已废弃」，也不附否定说明——历史在 git。
- **非目标是边界，不是否定。** 「本产品不做 X」是范围约束；「考虑过 Y 并否决」不记录。
- **记录否定需显式授权。** 仅当用户明确要求时，在 ADR 写一行，绝不写进 PRD / SPEC。

**可重建性是验收标准。** 一个没读过任何会话的 agent，只读 `docs/product/` + SPEC，能用 3–5 句说出终态：服务谁、做什么、明确不做什么、关键约束。再加 `docs/current/`，能说出当前形态。复述里出现「可能 / 大概 / 视情况」，说明模型有洞：要么补上设计，要么那处也留白。

ADR 不同：它是带理由的决策记录，永久、编号，所以保留墓碑。PRD / SPEC 的条目不要借用 ADR 的措辞（决定 / 否决 / 取代）。

## 目录结构

```
docs/
  toc.yml
  product/
    00-README.md              # PRD：封面 + 项目说明 + 典型应用场景
    01-requirements.md        # PRD：高层产品需求
    02-architecture.md        # PRD：架构总览 + 模块划分
    <NN-module>/
      00-README.md            # 模块 PRD
      00-index.md             # agent 侧车（不发布）
      01-spec.md              # SPEC
      02-interfaces.md        # SPEC
      03-nfr.md               # SPEC
      design/                 # SPEC（可选；默认不参与发布）
  current/
  adr/
  docsHtmlView/               # 发布工作区（docs-html-view）
    conf.py
    guard.py
    index.md                  # 生成的封面 + 目录
    nav/**                    # 生成的章节页
    glossary.md               # 由根 CONTEXT.md 生成
    _manifest.json            # 生成的精确包含清单
    _meta.json                # 生成的标题/版本/日期/摘要
    build/html                # 输出
CONTEXT.md                    # 项目根术语表源
```

- 只有**单一 `docs/product/` 树**。产品 `00-index.md` 已退役；仅保留模块 `00-index.md`，作为不发布的 agent 侧车。
- `docs/prd/` 是 v4 / 旧版布局。init 会检测并提供迁移（`migration.md`）；init 期间绝不改写。

## PRD 契约

### 产品 PRD（三章）

- `00-README.md`——封面与项目说明：一句话、项目说明、目标用户与问题，以及 3–5 个典型应用场景。
- `01-requirements.md`——高层产品需求：能力地图、关键行为、非目标与关键产品约束。FR ID 可以**纯文本**引用；绝不复制验收判据。
- `02-architecture.md`——架构总览与模块划分；关键约束；链接到各模块 PRD。

### 模块 PRD

每个 `docs/product/<NN-module>/00-README.md` 说明该模块提供什么、关键行为、边界与非目标。篇幅 0.5–1 页。它不承载文档地图、依赖、接口归属或追溯——那些在模块 `00-index.md` 中。

### 仅限 PRD 层链接

- 允许：同文件锚点、产品章节 ↔ 产品章节、产品章节 ↔ 模块 PRD、模块 PRD ↔ 模块 PRD。
- 禁止：指向 SPEC 文件、Current、ADR、`http(s)` / `mailto` 或任何外部目标的链接。
- 导航与追溯（包括指向 SPEC / Current / ADR 的链接）只在模块 `00-index.md` 或 SPEC 层，绝不在 PRD 中。

### 细节上限

PRD 中禁止：验收判据文本、接口签名、字段 / schema、错误码、状态机细节、实现内部名称或步骤、性能数字。允许：用户可见行为、能力名称、用户结果、平实语言约束。

### 状态

无状态标记（✅ / 🚧 / ❌），无路线图，无进展，无任务历史。

### 横幅

每个 PRD 文件（产品章节与模块 PRD）开头均为：

`本文档描述产品目标与方案，不代表当前实现状态；实现细节见 SPEC，现状见 Current。`

### 篇幅

每个产品章节 ≤ ~2 页；模块 PRD 0.5–1 页。若产品叙事超出，按独立负责的产品区拆分：产品章节保留整体视图，并链接到各区模块 PRD。

### 维护

编排者与用户共同维护 PRD；人类评审 PRD diff 的可读性与意图。始终展示 diff。与 SPEC 在实现细节上冲突时，以 SPEC 为准。

## SPEC 契约

- FR ID 稳定、永不复用，每个模块内连续；在 PRD 中为纯文本。
- 每条 FR 都带验收判据。
- 接口由提供方模块拥有；消费方引用它们。
- NFR 放在 `03-nfr.md`；机制级设计可选放在 `design/`。
- SPEC 由用户 + 编排者编写。编码 agent 读取它，并可通过 issue **提议**变更；不直接编辑 SPEC。
- 已实现的细节不会自动提升进 SPEC。
- 实现细节冲突以 SPEC 为准；范围 / 意图冲突以 PRD 为准。

## TOC 契约

- `docs/toc.yml` 是**发布来源**，由第一方 `docs-html-view` skill 消费。只发布 TOC 中列出的文档。
- 元数据：`title`、`version`、`date`、`abstract`。
- 必需章节 id：`overview`、`requirements`、`architecture`、`appendix`。
- 附录 id：`glossary`、`spec`、`current`、`adr`。
- 架构章节使用 `modules: auto` 按数字顺序展开 `docs/product/*/00-README.md`，可选 `exclude` 列表。
- 每个列出的路径 / glob 必须落在 `docs/product`、`docs/current`、`docs/adr` 内，或指向 `CONTEXT.md`。
- 编排者拥有 TOC，并在模块或附录变化时更新。

## 权威与冲突

- 实现细节：**SPEC 为准**。
- 范围 / 意图：**PRD 为准**。
- 冲突：升级给编排者 / 用户；更新错误的那份文档；绝不默默选择。
- 需要理由与取舍的决策落到 ADR（`adr.md`）。
- Current 是唯一的状态来源；其他文档不得声称当前实现了什么。

## Current 与 ADR 边界

- Current（`current.md`）记录选定基线下的实际建成事实；它可以链接 PRD、SPEC 或 ADR。
- PRD 核心不得链接 Current、SPEC 或 ADR：Current 与 PRD 是两棵独立的树，互不内嵌。
- ADR = 带理由与取舍的决策，是平级文档，也是附录。
- PRD 核心之外，用描述性短语 + 稳定路径链接 ADR（例：`支持[离线使用](../../adr/0003-offline.md)`）；写法与不转述规则见 `adr.md`。

## 遗留与迁移

- v4 布局（`docs/prd/`）、改名前的 `docs/pdr/` 树、v3/v4 provenance 行，以及旧 PFD / 分层结构都是**遗留**。init 会检测并提供迁移（`migration.md`）。
- 遗留材料绝不自动改写、移动或删除。用户选择：立即迁移、只看计划、推迟为一个 chore issue，或跳过。
- 完全没有产品文档的现有项目可使用需用户同意的 bootstrap（`bootstrap.md`）；它只产出草稿，绝不直接成为事实。

## 示例（DA_AGENT）——不属于通用规则

DA_AGENT 是具体实例：模块为 ui / agent / cpp-core / FPGA，另有 architect 与 research 作为模块外区域。其 `docs/product/00-README.md` 是 PRD 封面与项目说明（典型应用场景放在这里）；`01-requirements.md` 承载能力地图、关键行为、非目标与约束；`02-architecture.md` 承载架构总览与模块划分；每个模块的 `00-README.md` 是模块 PRD，`00-index.md` 是 agent 侧车；各模块的 `01-spec / 02-interfaces / 03-nfr` 加不编号的 `design/` 构成 SPEC。`docs/toc.yml` 是发布来源，FR 前缀为 `FR-AGENT-NN`、`FR-UI-NN`……，Current 位于 `docs/current/`，决策位于 `docs/adr/`。来源：DA_AGENT ADR-0026。
