---
name: project-docs-workflow
description: 初始化或对齐项目的文档工作流——issue 跟踪、ADR、带独立 Current 现状树的 PRD 目标规格（L1 人类叙事 + L2 规范规格）、推荐的五步开发流程，以及领域术语。每个项目手动运行一次（幂等）；创建缺失文件并报告对齐情况，不覆盖现有内容。
disable-model-invocation: true
---

# 项目文档工作流

搭建并对齐项目的文档体系：issue 跟踪、ADR、PRD 产品规格（L2 规范规格之上的 L1 人类叙事）、领域术语，以及推荐的五步开发流程。本 skill 是权威源；init 将规则物化到目标项目，使 agent 在运行时读取。

手动运行，每个项目一次——在接入时，或在 skill 模板演进后再次运行以检查对齐。重复运行是幂等的：只创建缺失内容并报告漂移，绝不改写现有内容。

## 归属模型

- **权威源**：本 skill 持有规则（`references/`）与模板（`assets/templates/`）。
- **物化**：init 把规则复制到目标项目。这些副本是 agent 在运行时读取的源；本 skill 不会自动加载。
- **允许覆盖**：项目可按本地实际情况修改副本。init 只报告差异，不强制执行也不回退。
- **语言**：模板默认中文；非中文项目可翻译物化副本——覆盖是正当的。
- **绝不覆盖**：现有内容只做比较，绝不改写（唯一的追加例外：缺失的 `AGENTS.md` 区块——见清单）。
- **维护**：项目文档默认由 agent 维护；人类掌舵、评审 L1 叙事与目标决策、ADR，并可直接修改文风。事实性修正走 agent。

## 依赖解析（两级）

外部能力引用按两级解析：

1. **按名称调用已安装的 skill**——当用户安装了独立 skill 时（规范名称：`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`tdd`、`deepwork`、`retro`、`improve-codebase-architecture`，以及第一方 `doc-opt`）；已安装版本优先。
2. **内部兜底**——否则将随附的参考文档**作为指令执行**；**不要**把它们当作 skill 调用（并不存在对应 skill）。多数名称映射到 `references/deps/<name>.md`；别名映射如下：
   - `grill-me` → `references/deps/grilling.md`（`grilling` 的入口别名，无独立流程）
   - `grill-with-docs` → `references/deps/grilling.md` **+** `references/deps/domain-modeling.md`，交织进行（grilling 轮次 + 即时写入术语/ADR）
   - `deepwork` / `retro` / `improve-codebase-architecture` → `references/deps/boundaries.md`
   本包**不随附**任何独立依赖 skill；这些内部参考是始终可用的兜底。

> **触发策略。** 遵循每个已安装 skill 的调用元数据；`grill-me` / `grill-with-docs` 等包装器可能仅允许用户调用。可选名称**不**意味着可用：若未安装，使用内部兜底——绝不调用缺失的 skill，也不要自主调用仅限用户调用的包装器。逐名称路由见 `references/workflow.md`。

规范措辞（模板使用同一行，仅将 deps 路径参数化）：调用 `<skill>`（未安装则按 `<deps 路径>/<file>.md` 执行）——skill 内部文档使用 `references/deps/<file>.md`，物化的项目文件使用 `docs/agents/deps/<file>.md`。

## Init 流程

在目标项目根目录（`cwd`）运行。

1. **盘点**下方清单中的每个产物。将每项归类为*缺失*或*已存在*。每一行都有分类即完成。
2. **创建缺失**文件（按模板），并创建 issue 目录树。缺失时创建 `docs/current/00-README.md` 概览——不强制创建模块文件。缺失时创建 `docs/prd/00-README.md`（产品 L1）与 `docs/prd/00-index.md`——不强制创建模块文件。例外：当存在有内容的遗留 `docs/pdr/` 且 `docs/prd/` 缺失时，**不要**在 `docs/prd/` 下创建任何内容（`00-README.md` 与 `00-index.md` 都不创建）；改为将旧树作为遗留漂移报告。
2b. **填充占位符**：只填充明显、可确定的*待填*占位符（例如由仓库/目录名得到项目名）；将剩余每个待填占位符列在报告的「下一步」下。`<标题>` 这类格式记号是文档说明，不是占位符——跳过。
3. **比较现有**文件与模板：归类为*已对齐*，或*有差异*并列出具体差异。
4. **报告**：使用下方格式。

### 产物清单

| 产物 | 模板 |
| :--- | :--- |
| `AGENTS.md` → `## Agent skills` 区块 | `assets/templates/project/agents-block.md` |
| `docs/agents/issues.md` | `assets/templates/project/agents-issues.md` |
| `docs/agents/domain.md` | `assets/templates/project/agents-domain.md` |
| `docs/agents/workflow.md` | `assets/templates/project/agents-workflow.md` |
| `docs/agents/deps/` | `references/deps/*`（整目录复制，不改内容） |
| `docs/issues/` 目录树 | 无——创建目录（见下） |
| `docs/adr/README.md` | `assets/templates/project/adr-readme.md` |
| `docs/prd/00-README.md`（产品 L1） | `assets/templates/project/prd-00-readme.md` |
| `docs/prd/00-index.md` | `assets/templates/project/prd-00-index.md` |
| `docs/current/00-README.md` | `assets/templates/project/current-00-readme.md` |
| `CONTEXT.md` | `assets/templates/project/context.md` |

- 仅在缺失时创建 `AGENTS.md`——其全部内容就是该区块；只包含本区块的文件是有意为之（项目会在其周围添加自己的指引）。若 `AGENTS.md` 已存在：有 `## Agent skills` 标题 → 就地比较该区块（绝不编辑）；无 → 在文件末尾追加该区块，中间空一行。只触碰 `AGENTS.md`，绝不触碰 `CLAUDE.md`。
- 来源行紧跟在 `## Agent skills` 标题下方，是有意为之——保留它（用于标识物化文件及其生成来源）。
- Issue 目录树：`bug/{human,agent,history}`、`feature/{human,agent,history}`、`chore/{human,agent,history}`、`suggestion/{human,agent}`；为每个叶子目录（不含任何文件的目录）添加 `.gitkeep`。不要运行 `git init`。
- 依赖兜底：init 将 `references/deps/*` 作为整目录副本（内容不变）复制到项目的 `docs/agents/deps/`，使目标项目即使未安装本 skill 也能自给自足。
- Current 树：缺失时 init 创建 `docs/current/00-README.md` 概览；**不**强制创建模块文件——在需要描述模块时添加。Current 树与 PRD 平级，绝不内嵌于 PRD。
- PRD 树：缺失时 init 创建 `docs/prd/00-README.md`（产品 L1）与 `docs/prd/00-index.md`——**不**强制创建模块文件。例外是存在有内容的遗留 `docs/pdr/`——此时不创建任何内容，并将旧树作为遗留漂移报告（见下）。当 `docs/prd/` 存在、但其 `00-README.md` 是旧的索引式 README 时，init 将 `L1 not aligned` 作为差异报告——绝不改写它。
- 领域术语表（如 `docs/common/glossary.md`）**不由 init 搭建**；规则会覆盖它们，项目按需创建。
- 渲染**不在 init 范围内**：init 不创建任何渲染器配置、产物或钩子。HTML 渲染是可选手动第一方 skill（`docs-html-view`）；见 `references/rendering.md`。

### 对齐比较（现有文件）

比较**规则，而非字节**。当下方每条必需规则/章节都以可识别形式存在时，现有文件即为**已对齐**——措辞、语言、顺序、格式和已填入的项目内容都可以不同。项目新增内容始终没问题，绝不视为差异。

**差异（diff）** = 缺少必需规则/章节，或与默认规则相矛盾。差异仅供参考；init 绝不自动修复。每个文件一条：`- <file>: <缺失或相矛盾的规则>`。

**遗留漂移**（现有项目）：在现有项目中发现的嵌入式 current/progress 材料——例如每模块的 `04-current.md`、PRD README 中的 `当前进展` 章节——作为信息性遗留漂移报告。重命名前的 `docs/pdr/` 树同样属于遗留漂移；当它有内容且 `docs/prd/` 缺失时，init 报告它，而不是在 `docs/prd/` 下创建任何内容（`00-README.md` 与 `00-index.md` 都不创建）。init 绝不移动、改写或删除这两种形态，也不提供安装迁移脚本；迁移到独立的 Current 树或迁移到 `docs/prd/` 需要用户显式授权。

**L1 not aligned** 与遗留漂移不同：现有的 `docs/prd/00-README.md` 如果其实是模块索引 / 约定文档，则属于**差异**，不是遗留漂移（迁移到 v4 时该材料移到了 `00-index.md`）。init 报告 `L1 not aligned`、缺失的 L1 元素与需要迁移的提示，绝不改写该文件。

每次比较都忽略：来源行；已填充的占位符；索引/表格行；模块/术语/条目名称；语言；额外内容。

每个产物的必需元素：

- `AGENTS.md` 区块：`## Agent skills` 标题 + 三个子节（`### Issue tracker`、`### Domain docs`、`### Development workflow`）。
- `docs/agents/issues.md`：目录契约；human/agent 责任；条目格式（`Status:` 行、`## 完成判据`、`## 步骤`、`## Log`；`## 结果` 章节本身可选）；归档后缀（`-done`/`-drop`）；`-drop` 是工作状态归档，不是否定决策（放弃的条目不会被删除或改写）；suggestion 路由。
- `docs/agents/domain.md`：探索前先读 `CONTEXT.md` + `docs/adr`；缺失时静默继续；术语表用词规则；ADR 冲突标注。
- `docs/agents/workflow.md`：推荐五步流程（规划 / 骨架 / 细节 / 异常 / 回顾，其中回顾 = 文档同步收尾）；读什么（L1 供人类理解，L2 规格文件 + Current 作事实源，`00-index` 供导航；L1 冲突 → 以 L2 为准）；先对齐后构建的顺序；对话式对齐（不冻结）；弹性粒度建议（≈0.5 人天启发式）；issue `## 步骤` 跟踪 + 续接锚点；由 PRD 目标 / Current 现状推导差距→issue 候选；四项叙事影响触发 + L1 无变化时记一行 Log；三轨变更协议（目标变更 / 范围内实现 / 内部-bug）；范围收敛默认（feature / 范围决策倾向收窄；feature 候选需要一句话理由；bug / chore 豁免；是偏好而非门禁）；收尾更新 L1（带 diff）并就地更新 Current（只改事实，不插入自链接或任务历史）；边界（`deepwork` / `tdd` / `retro` / `grilling` 调用 + 兜底指针）。
- `docs/adr/README.md`：生命周期规则（修改+Log、删除→墓碑桩、不重新编号）；存在目录表；引用核查覆盖 `ADR-XXXX` 与 `adr/<NNNN>-<slug>.md` 路径链接（任意相对前缀）；正文默认不含 `Considered Options`；默认不记录被拒备选方案（仅约束持久记录；讨论仍可探索备选）。
- `docs/prd/00-README.md`（产品 L1）：目标横幅（`本文描述目标态，不代表当前已实现；现状由 agent 查阅 Current。`）；产品叙事章节（一句话、问题与目标、核心场景、能力地图、非目标、关键产品约束）；无外部链接、无状态标记、无进展；能力地图可以纯文本引用 FR ID。
- `docs/prd/00-index.md`：目的；模块索引；阅读顺序；组织约定；CAP↔FR / 模块追溯；链接到 `../current/00-README.md` 与 `../adr/README.md`；链接到产品 L1（`00-README.md`）；无进展。
- `docs/current/00-README.md`：目的；链接到 PRD L1（`../prd/00-README.md`）；本树所描述的基线（revision/日期）；模块/主题索引；阅读顺序；记录实际建成能力/限制，而非任务日志、计划中的工作或进展；可选的描述性 ADR 链接规则。
- `CONTEXT.md`：术语表结构（带 `_Avoid_` 的术语块）。
- `docs/issues/` 树：叶子目录存在（可检查 `.gitkeep`）；额外内容仅供参考。
- `docs/agents/deps/`：叶子文件存在（`grilling.md`、`domain-modeling.md`、`tdd.md`、`doc-opt.md`、`boundaries.md`）；额外内容仅供参考。

### 报告格式

用项目的文档语言撰写报告（默认：中文，与模板一致）。

```
## Init report
- Created: …
- Aligned: …
- Diff: one bullet per file: `- <file>: <missing or contradicted rule>`（仅供参考，不自动改；multi-file → multiple bullets）
- L1 not aligned: `<file>` 是索引式 README 而非 L1（信息性；需要迁移——见 Next）。
- Legacy drift: embedded current/progress paths found (e.g. `04-current.md`, `当前进展` section) or a populated pre-rename `docs/pdr/` tree — informational only, never moved or rewritten; migration needs explicit user authorization.
- Next: remaining placeholders plus a one-line "do this first"；L1 未对齐时附迁移提示（从旧导航/约定创建 `00-index.md`，由 L2 生成 L1 草稿，review diff）。
```

## 参考

规则承载细节；按需读取。

- `references/issues.md` — issue 跟踪目录契约、条目格式、`suggestion` 路由。
- `references/adr.md` — ADR 生命周期（修改 + Log、删除 → 墓碑桩、引用核查、目录索引）、正文形态。
- `references/prd.md` — PRD L1/L2 结构：L1 产品与模块 `00-README.md`（叙事视图）、L2 规格文件、`00-index.md` 导航/追溯、目标与差距→候选 issue 层、变更分流、PRD↔ADR 与 PRD↔Current 边界。
- `references/current.md` — Current 实际建成树（L3：`00-README` + 模块/主题文档）、基线与验证信心、同步语义、与 PRD 的平级关系、遗留漂移的接入。
- `references/rendering.md` — 可选的文档 HTML 渲染契约：完整站点范围（`docs/prd` + `docs/current` + 完整 `docs/adr`，不含 issues / agents）、L1 专用档（产品 L1 + 模块 L1，可分发）、链接撰写规则（L1 仅内部、PRD↔Current、可选的描述性 ADR 路径链接）、源文件永不改写、手动选择启用。
- `references/terminology.md` — `CONTEXT.md` 主术语表、领域术语表、使用规则。
- `references/workflow.md` — 推荐的单 issue 开发流程（五步、对齐、粒度、跟踪、文档同步钩子、skill 边界）。
- `references/coexistence.md` — 本方案如何与 `domain-modeling`、`grilling`、`deepwork`、`tdd`、`retro` 及第一方 `doc-opt` 并存；以及其 docs/issues 约定如何取代旧式 `.scratch` 风格跟踪器。
- `references/deps/` — 两级解析的内部兜底参考：`grilling` / `domain-modeling` / `tdd` / `doc-opt` / `boundaries`（`deepwork` / `retro` / `improve-codebase-architecture` 共用 `boundaries.md`）。

## 模板

- `assets/templates/project/*` — init 物化的文件（中文）。它们带有来源标记（当前代次：`v4`；在 `agents-block.md` 中位于 `## Agent skills` 标题正下方）——保留它；未来代次会更新标记，以便检测过期副本。
- `references/deps/*` — 当独立依赖 skill 缺失时使用的内部兜底参考。init 将整个目录原样复制到项目的 `docs/agents/deps/`；它们不是物化模板，不带来源标记。
- `assets/templates/entries/*` — 手边有这个 skill 时使用的日常撰写辅助（新建条目时复制骨架）。init **不**物化它们；规则文档在没有它们时也自足；物化文档可以顺带引用其路径。
