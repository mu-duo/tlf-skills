---
name: project-docs-workflow
description: 初始化或对齐项目的文档工作流——issue 跟踪、ADR、宏观 PRD 与规范 SPEC、独立的 Current 现状树、推荐的五步流程、角色，以及遗留项目的 bootstrap / 迁移。每个项目手动运行一次（幂等）；创建缺失文件并报告对齐情况，不覆盖现有内容。
disable-model-invocation: true
---

# 项目文档工作流

搭建并对齐项目的文档体系：issue 跟踪、ADR、宏观 PRD、规范 SPEC、Current 现状树、领域术语，以及带明确角色的推荐五步开发流程。本 skill 是权威源；init 将规则物化到目标项目，使 agent 在运行时读取。

手动运行，每个项目一次——在接入时，或在 skill 模板演进后再次运行以检查对齐。重复运行是幂等的：只创建缺失内容并报告漂移，绝不改写现有内容。

## 归属模型

- **权威源**：本 skill 持有规则（`references/`）与模板（`assets/templates/`）。
- **物化**：init 把规则复制到目标项目。这些副本是 agent 在运行时读取的源；本 skill 不会自动加载。
- **允许覆盖**：项目可按本地实际情况修改副本。init 只报告差异，不强制执行也不回退。
- **语言**：模板默认中文；非中文项目可翻译物化副本——覆盖是正当的。
- **绝不覆盖**：现有内容只做比较，绝不改写（唯一的追加例外：缺失的 `AGENTS.md` 区块——见清单）。
- **维护**：项目文档默认由 agent 维护。人类掌舵、评审 PRD / SPEC / ADR，并可直接修改文风。事实性修正走 agent。

## 角色

- **用户**：意图、范围与批准；评审 PRD、SPEC 与 ADR。
- **编排者（orchestrator）**：维护 PRD；与用户共同编写 SPEC；评审 PRD / SPEC diff；拥有 `docs/toc.yml`；触发发布；把编码工作交给 coder。
- **编码 agent（coder）**：读 SPEC 实现；收尾时更新 Current 事实；可通过 issue 提议 SPEC 变更；不直接改 PRD、SPEC 或 TOC。
- **单 agent 模式**：一个 agent 可同时担任编排者与 coder，但角色边界仍然适用。

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

1. **先检测状态**（见下）。状态决定 init 是否可以写入、是否提示迁移或提示 bootstrap。
2. **盘点**下方清单中的每个产物。将每项归类为*缺失*或*已存在*。每一行都有分类即完成。
3. **按状态规则创建缺失**文件（按模板），并创建 issue 目录树。缺失时创建 `docs/current/00-README.md` 概览——不强制创建模块文件。缺失时创建 `docs/product/00-README.md`、`docs/product/01-requirements.md`、`docs/product/02-architecture.md` 与 `docs/toc.yml`——**不**强制创建模块文件，也绝不创建产品 `00-index.md`。
4. **填充占位符**：只填充明显、可确定的*待填*占位符（例如由仓库/目录名得到项目名）；将剩余每个待填占位符列在报告的「下一步」下。`<标题>` 这类格式记号是文档说明，不是占位符——跳过。
5. **比较现有**文件与模板：归类为*已对齐*，或*有差异*并列出具体差异。
6. **报告**：使用下方格式。

### 状态检测

在 init 写入任何内容之前先分类：

1. **v5（已对齐或部分完成）**——`docs/product/` 存在（例如 `docs/product/00-README.md`）。按 v5 处理：不提示迁移或 bootstrap；执行常规盘点 / 对齐报告，只创建清单中缺失的文件（包括缺失的三章 PRD 与 `docs/toc.yml`）。绝不改写。部分完成的 v5 树**不属于** bootstrap。
2. **v4 / 旧版文档**——`docs/prd/`、`docs/pdr/`、v3/v4 provenance 行，或旧 PFD / 分层结构（产品 `00-index.md`、L1/L2/L3 术语）。**提示**：
   - **立即迁移** → 展示计划与逐文件 diff，请求确认后执行（`references/migration.md`）；
   - **只看计划** → 打印计划与 diff，不写入；
   - **稍后** → 创建一个 `docs/issues/chore/agent/...` 迁移 issue，其余不写；
   - **跳过** → 完全不写（连非产品产物也不写）；仅报告。
   绝不自动改写、移动或删除。没有明确选择时不写入。
3. **无文档 + 有源码**——没有 `docs/product/`，但仓库有源码（或只有 `CONTEXT.md` / ADR）。**提示**遗留 bootstrap（`references/bootstrap.md`）：
   - **Bootstrap** → 五个阶段：领域建模、现状、PRD 草稿、SPEC 草稿、用户评审；
   - **仅模板** → 创建 v5 空骨架；不做建模；
   - **跳过** → 不写入。
4. **空 / 新仓库**——按模板搭建 v5。

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
| `docs/toc.yml` | `assets/templates/project/toc.yml` |
| `docs/product/00-README.md`（PRD 封面） | `assets/templates/project/prd-00-readme.md` |
| `docs/product/01-requirements.md` | `assets/templates/project/prd-01-requirements.md` |
| `docs/product/02-architecture.md` | `assets/templates/project/prd-02-architecture.md` |
| `docs/current/00-README.md` | `assets/templates/project/current-00-readme.md` |
| `CONTEXT.md` | `assets/templates/project/context.md` |

- 仅在缺失时创建 `AGENTS.md`——其全部内容就是本区块；只含本区块的文件是有意为之（项目会在其周围添加自己的说明）。若 `AGENTS.md` 已存在：已有 `## Agent skills` 标题 → 就地比较该区块（绝不编辑）；没有 → 在文件末尾追加该区块，中间空一行。只动 `AGENTS.md`，绝不碰 `CLAUDE.md`。
- provenance 行紧跟在 `## Agent skills` 标题下，是有意保留的——不要删（它标识物化文件及其代次；当前代次 `v5`）。
- Issue 目录树：`bug/{human,agent,history}`、`feature/{human,agent,history}`、`chore/{human,agent,history}`、`suggestion/{human,agent}`；给每个叶子目录（其中没有文件的）加 `.gitkeep`。不要运行 `git init`。
- 依赖兜底：init 将 `references/deps/*` 整目录复制到项目的 `docs/agents/deps/`（内容不变），使目标项目即使未安装本 skill 也自足。
- Current 树：缺失时 init 创建 `docs/current/00-README.md` 概览；**不**强制创建模块文件——按需补充。Current 树与 PRD 平级，绝不嵌入 PRD。
- PRD 树：缺失时 init 创建三个产品 PRD 章节（`00-README.md`、`01-requirements.md`、`02-architecture.md`）与 `docs/toc.yml`。它**不**强制创建模块文件，也绝不创建产品 `00-index.md`——该产物已退役。模块 `00-index.md` 是不发布的 agent 侧车，仅在模块存在时创建。
- 领域术语表（例如 `docs/common/glossary.md`）**不**搭建；规则覆盖它们，项目按需创建。
- 发布**不属于 init 范围**：init 不创建渲染器配置、产物或钩子。HTML 发布是可选的、手动的第一方 skill（`docs-html-view`）；见 `references/rendering.md`。

### 对齐比较（现有文件）

比较**规则，而非字节**。当下列每项必需规则 / 章节都以可识别形式存在时，现有文件即为**已对齐**——措辞、语言、顺序、格式与已填项目内容均可不同。项目额外内容始终正常，绝不算差异。

**差异（diff）** = 缺少必需规则 / 章节，或与默认规则矛盾。差异仅供参考；init 绝不自动修复。每个文件一条：`- <file>: <missing or contradicted rule>`。

**遗留漂移**（现有项目）：v4 `docs/prd/` 或 `docs/pdr/` 树、产品 `00-index.md`、v3/v4 provenance 行，或 PRD 中嵌入的现状 / 进展材料（例如每模块 `04-current.md`、`当前进展` 章节）都作为信息性遗留漂移报告，并提供迁移选项。init 绝不移动、改写或删除它们。

每次比较都忽略：provenance 行；已填占位符；索引 / 表格行；模块 / 术语 / 条目名称；语言；额外内容。

各产物必需元素：

- `AGENTS.md` 区块：`## Agent skills` 标题 + 三个子章节（`### Issue tracker`、`### Domain docs`、`### Development workflow`）。
- `docs/agents/issues.md`：目录契约；human/agent 责任；条目格式（`Status:` 行、`## 完成判据`、`## 步骤`、`## Log`；`## 结果` 本身可选）；归档后缀（`-done`/`-drop`）；`-drop` 是工作状态归档，不是否定决策（已放弃条目不被删除或改写）；suggestion 路由。
- `docs/agents/domain.md`：探索前读 CONTEXT.md + docs/adr；缺失则静默继续；术语表用词规则；ADR 冲突标注。
- `docs/agents/workflow.md`：角色与写入权限（用户 / 编排者 / coder，单 agent 说明）；读什么（PRD 用于意图与场景，SPEC 用于实现事实，Current 用于现状，TOC 用于发布）；PRD / SPEC 权威与冲突升级；先对齐再实现；对话式对齐（不冻结）；弹性粒度建议（≈0.5 人天启发式）；issue `## 步骤` 跟踪 + 续接锚点；差距→issue 候选推导；四项 PRD 影响触发与一行 no-op 记录；PRD / SPEC / Current / ADR 变更协议；范围收敛默认偏好；收尾（coder 更新 Current 事实并提议 SPEC 变更；编排者评审，模块 / 附录变化时更新 TOC）；边界（deepwork / tdd / retro / grilling 调用 + 兜底指针）；bootstrap / 迁移指针。
- `docs/adr/README.md`：生命周期规则（修改 + Log、删除→墓碑桩、编号不复用）；目录表存在；引用 sweep 同时覆盖 `ADR-XXXX` 与 `adr/<NNNN>-<slug>.md` 路径链接（任意相对前缀）；正文默认不含 `Considered Options`；默认不记录被拒备选（仅约束持久记录；讨论仍可探索备选）。
- `docs/product/00-README.md`：PRD 横幅（`本文档描述产品目标与方案，不代表当前实现状态；实现细节见 SPEC，现状见 Current。`）；项目说明章节（一句话、项目说明、目标用户与问题、典型应用场景）；无外链、无状态标记、无验收判据。
- `docs/product/01-requirements.md`：能力地图、关键行为、非目标、关键产品约束；FR ID 为纯文本；无验收判据或接口细节。
- `docs/product/02-architecture.md`：架构总览 + 模块划分；链接到模块 PRD；无 SPEC 细节。
- `docs/toc.yml`：`title` / `version` / `date` / `abstract`；必需章节 id `overview`、`requirements`、`architecture`、`appendix`；附录 id `glossary`、`spec`、`current`、`adr`；所有路径存在；`modules: auto`。
- 模块 `00-README.md`：模块 PRD（提供什么、关键行为、边界、非目标）；回链产品 PRD；无文档地图 / 依赖。
- 模块 `00-index.md`：文档地图、依赖、接口归属、CAP↔FR 追溯；不发布；链接到架构章节、TOC 与模块 PRD。
- `docs/current/00-README.md`：目的；链接到 PRD 封面（`../product/00-README.md`）；树所描述的基线（revision/date）；模块 / 主题索引；阅读顺序；记录实际建成的能力 / 限制，而非任务日志、计划工作或进展；可选描述性 ADR 链接规则。
- `CONTEXT.md`：术语表结构（含 `_Avoid_` 的术语块）。
- `docs/issues/` 树：叶子目录存在（可检查 `.gitkeep`）；额外内容仅供参考。
- `docs/agents/deps/`：叶子文件存在（`grilling.md`、`domain-modeling.md`、`tdd.md`、`doc-opt.md`、`boundaries.md`）；额外内容仅供参考。

### 报告格式

用项目的文档语言撰写报告（默认：中文，与模板一致）。

```
## Init report
- State: v5 aligned/partial｜v4/older docs｜no docs + source｜empty/new
- Created: …
- Aligned: …
- Diff: 每个文件一条：`- <file>: <missing or contradicted rule>`（仅供参考，不自动改；多文件 → 多条）
- Migration/bootstrap decision: none｜migrate now｜plan only｜later (<issue path>)｜skip (migration)｜bootstrap｜templates only｜skip (bootstrap)
- Legacy drift: 检测到的 v4 / 旧版路径及提供的动作——仅供参考；未经用户授权绝不移动或改写。
- Next: 剩余占位符，外加一句「先做这个」。
```

## 参考文档

规则承载细节；按需读取。

- `references/workflow.md`——推荐的单 issue 开发流程：角色与写入权限、读什么、对齐、变更协议、五步、收尾、TOC 维护、发布指针、粒度、范围收敛、边界。
- `references/prd.md`——PRD（宏观）、SPEC（细节）、Current、ADR 模型：目录结构、PRD / SPEC / TOC 契约、权威与冲突、边界、遗留 / 迁移指针。
- `references/current.md`——Current 现状树、基线与验证信心、同步语义、与 PRD 的平级关系、接入规则。
- `references/rendering.md`——可选的可发布多页 PRD 契约（`docs-html-view`）：TOC 驱动范围、PRD 核心 + SPEC / Current / ADR / 术语表附录、链接规则、生成的 manifest、源文档绝不改写、手动 opt-in。
- `references/bootstrap.md`——面向有代码但无产品文档项目的 consent-gated bootstrap：五个阶段、草稿、推断项落入 issue。
- `references/migration.md`——v4 / 旧版 → v5 迁移：检测、提示选项、逐文件 diff、步骤、绝不自动改写。
- `references/terminology.md`——`CONTEXT.md` 主术语表、领域术语表、使用规则。
- `references/coexistence.md`——本方案与 `domain-modeling`、`grilling`、`deepwork`、`tdd`、`retro` 及第一方 `doc-opt` 的共存；其 docs/issues 约定如何取代旧 `.scratch` 式跟踪。
- `references/deps/`——两级解析的内部兜底参考：`grilling` / `domain-modeling` / `tdd` / `doc-opt` / `boundaries`（`deepwork` / `retro` / `improve-codebase-architecture` 共用 `boundaries.md`）。
- `references/issues.md`——issue 跟踪目录契约、条目格式、`suggestion` 路由。
- `references/adr.md`——ADR 生命周期（修改 + Log、删除 → 墓碑桩、引用 sweep、目录索引）、正文形态。

## 模板

- `assets/templates/project/*`——init 物化的文件（中文）。它们带有 provenance 标记（当前代次：`v5`；`agents-block.md` 中位于 `## Agent skills` 标题正下方）——保留它；后续代次会更新标记，以便发现过期副本。
- `assets/templates/project/toc.yml`——`docs/toc.yml` 发布源：必需章节 id、`modules: auto` 与附录集合。
- `references/deps/*`——独立依赖 skill 缺失时使用的内部兜底参考。init 将整个目录原样复制到项目的 `docs/agents/deps/`；它们不是物化模板，不带 provenance 标记。
- `assets/templates/entries/*`——本 skill 在手时日常写作辅助（新建条目时复制骨架）。init **不**物化；规则文档本身自足；物化文档可机会性引用其路径。
