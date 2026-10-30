---
name: project-docs-workflow
description: 初始化或对齐项目的文档工作流——issue 跟踪、ADR、宏观 PRD 与规范 SPEC、独立的 Current 现状树、推荐的五步流程、测试用例编写准则、角色，以及遗留项目的 bootstrap / 迁移。每个项目手动运行一次（幂等）；创建缺失文件并报告对齐情况，不覆盖现有内容。
disable-model-invocation: true
---

# 项目文档工作流

搭建并对齐项目的文档体系：issue 跟踪、ADR、宏观 PRD、规范 SPEC、Current 现状树、领域术语、带明确角色的推荐五步开发流程，以及测试用例编写准则。本 skill 是权威源；init 将规则物化到目标项目，使 agent 在运行时读取。

手动运行，每个项目一次——在接入时，或在 skill 模板演进后再次运行以检查对齐。重复运行是幂等的：只创建缺失内容并报告漂移，绝不改写现有内容。

## 归属模型

- **权威源**：本 skill 持有规则（`references/`）与模板（`assets/templates/`）。
- **物化**：init 把规则复制到目标项目。这些副本是 agent 在运行时读取的源；本 skill 不会自动加载。
- **允许覆盖**：项目可按本地实际情况修改副本。init 只报告差异，不强制执行也不回退。
- **语言**：模板默认中文；非中文项目可翻译物化副本（含 `docs/agents/deps/*`）——覆盖是正当的。「内容不变」约束的是 init 的复制动作，不约束项目后续编辑。
- **绝不覆盖**：现有内容只做比较，绝不改写（两处加法例外：缺失的 `AGENTS.md` 区块；以及 `docs/agents/metadata.yml` 的 `version` 行，仅在一次已验证的运行后前移）。
- **维护**：项目文档默认由 agent 维护。人类掌舵、评审 PRD / SPEC / ADR，并可直接修改文风。事实性修正走 agent。

## 角色

三种角色：**用户**（意图、范围与批准；评审 PRD / SPEC / ADR）、**编排者**（维护 PRD，与用户共同编写 SPEC，拥有 `docs/toc.yml`，触发发布）、**编码 agent**（读 SPEC 实现，收尾更新 Current，通过 issue 提议 SPEC 变更）。单 agent 可同时担任两者，但换帽子必须显式。写入权限见 `references/workflow.md`。

## 依赖解析（两级）

外部能力引用按两级解析：

1. **按名称调用已安装的 skill**——当用户安装了独立 skill 时（规范名称：`grilling`、`grill-with-docs`、`domain-modeling`、`tdd`、`deepwork`、`retro`、`improve-codebase-architecture`，以及第一方 `doc-opt`、`lite-task`）；已安装版本优先。`grill-me` 仅是 `grilling` 的入口别名。
2. **内部兜底**——否则将随附的参考文档**作为指令执行**；**不要**把它们当作 skill 调用（并不存在对应 skill）。多数名称映射到 `references/deps/<name>.md`；别名映射如下：
   - `grill-me` → `references/deps/grilling.md`（`grilling` 的入口别名，无独立流程）
   - `grill-with-docs` → `references/deps/grilling.md` **+** `references/deps/domain-modeling.md`，交织进行（grilling 轮次 + 即时写入术语/ADR）
   - `deepwork` / `retro` / `improve-codebase-architecture` → `references/deps/boundaries.md`
   本包**不随附**任何独立依赖 skill；这些内部参考是始终可用的兜底。

> **触发策略。** 遵循每个已安装 skill 的调用元数据；`grill-me` / `grill-with-docs` 等包装器可能仅允许用户调用。可选名称**不**意味着可用：若未安装，使用内部兜底——绝不调用缺失的 skill，也不要自主调用仅限用户调用的包装器。逐名称路由见 `references/workflow.md`。

规范措辞（模板使用同一行，仅将 deps 路径参数化）：调用 `<skill>`（未安装则按 `<deps 路径>/<file>.md` 执行）——skill 内部文档使用 `references/deps/<file>.md`，物化的项目文件使用 `docs/agents/deps/<file>.md`。

## Init 流程

在目标项目根目录（`cwd`）运行。

1. **先读 `docs/agents/metadata.yml`，再判定状态**（见下）。状态决定 init 可以写入、修复，还是只报告。
2. **盘点**下方清单中的每个产物。将每项归类为*缺失*或*已存在*。每一行都有分类即完成。
3. **按状态规则创建缺失**产物（按模板），并创建 issue 目录树。不强制创建模块文件；绝不创建产品 `00-index.md`。
4. **填充占位符**：只填充明显、可确定的*待填*占位符（例如由仓库/目录名得到项目名）；将剩余每个待填占位符列在报告的「下一步」下。**绝不猜 Current 基线**——未选定基线时，`选定 Current 基线（revision / release + 日期）` 是「下一步」的第一项。`<标题>` 这类格式记号是文档说明，不是占位符——跳过。
5. **比较现有**文件与模板：归类为*已对齐*，或*有差异*并列出具体差异。
6. **报告**：使用下方格式。

### 状态检测

**先读 `docs/agents/metadata.yml`**——它记录这棵树是按哪个 skill 版本建立或最后复查的。

| 状态 | 条件 | 动作 |
| :--- | :--- | :--- |
| **skip** | `version` 等于当前 skill 版本，且清单产物齐全 | 零写入；一行报告 |
| **skip + 修复** | 版本相同但产物缺失 | 只做加法补齐（创建缺失文件）；戳不变 |
| **behind** | `version` 低于当前 skill 版本 | 走建立流程 |
| **ahead** | `version` 高于当前 skill 版本 | 零写入；报告「请升级 skill，或保持现状」 |
| **unknown** | 文件缺失或无法解析 | 走建立流程 |

符合性是**结构性**的：版本相同 + 产物齐全。规则差异只报告、不强制执行——项目覆盖是正当的。

#### 建立流程（behind / unknown）

1. **盘点**清单，把每个产物归类为缺失或已存在。
2. **看能读到什么**——这决定修复输入，不决定状态：
   - 只有源码 → bootstrap（`references/bootstrap.md`：五阶段，草稿经评审才成为事实）；
   - 已有文档 → 对齐；存在 `docs/prd/`、`docs/pdr/`、v3/v4 provenance 行或旧分层结构时走迁移（`references/migration.md`）；
   - 两者都没有 → 按模板搭建。
3. **计划**每笔写入：**加法**（创建缺失文件——自动执行）或**改写**（现有文件缺少必需规则或与之矛盾——始终以逐文件 diff 呈现）。
4. **执行**：加法自动；改写必须经用户确认。用户预授权「直接执行」时，先打印计划与 diff 摘要，随后不再逐项询问。未经确认绝不移动或删除任何内容。
5. **最后写戳**：只有在没有待定改写时才写入 `docs/agents/metadata.yml`。被拒绝的改写保留旧戳，下次运行仍报 `behind`，而不是声称已对齐。

bootstrap 与迁移保留各自的同意选项——建立流程不得绕过它们。

### 产物清单

| 产物 | 模板 |
| :--- | :--- |
| `AGENTS.md` → `## Agent skills` 区块 | `assets/templates/project/agents-block.md` |
| `docs/agents/issues.md` | `assets/templates/project/agents-issues.md` |
| `docs/agents/domain.md` | `assets/templates/project/agents-domain.md` |
| `docs/agents/workflow.md` | `assets/templates/project/agents-workflow.md` |
| `docs/agents/testing.md` | `assets/templates/project/agents-testing.md` |
| `docs/agents/metadata.yml` | `assets/templates/project/metadata.yml` |
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
- 依赖兜底：init 将 `references/deps/*` 整目录复制到项目的 `docs/agents/deps/`（复制时内容不变），使目标项目即使未安装本 skill 也自足。项目之后可翻译或修改它们。
- 测试准则：`docs/agents/testing.md`（源 `references/testing.md`）是**第一优先级、始终存在**——随 skill 分发，不适用「已安装 skill / 兜底」二分；`tdd` 只提供机制。缺失时 init 创建；项目可覆盖其默认值。其产出落在 issue 的 `## 测试`（执行 / 临时 / 落盘）。
- 元数据：`docs/agents/metadata.yml` 携带 `skill`、`version`、`updated`，是符合性戳：版本相同 + 产物齐全即跳过。绝不手工把它改成这棵树并不满足的版本。
- Current 树：缺失时 init 创建 `docs/current/00-README.md` 概览；**不**强制创建模块文件——按需补充。Current 树与 PRD 平级，绝不嵌入 PRD。
- PRD 树：缺失时 init 创建三个产品 PRD 章节（`00-README.md`、`01-requirements.md`、`02-architecture.md`）与 `docs/toc.yml`。它**不**强制创建模块文件，也绝不创建产品 `00-index.md`——该产物已退役。模块 `00-index.md` 是不发布的 agent 侧车，仅在模块存在时创建。
- 领域术语表（例如 `docs/common/glossary.md`）**不**搭建；规则覆盖它们，项目按需创建。
- 发布**不属于 init 范围**：init 不创建渲染器配置、产物或钩子。HTML 发布是可选的、手动的第一方 skill（`docs-html-view`）；见 `references/rendering.md`。

### 对齐比较（现有文件）

比较**规则，而非字节**。当下列每项必需规则 / 章节都以可识别形式存在时，现有文件即为**已对齐**——措辞、语言、顺序、格式与已填项目内容均可不同。项目额外内容始终正常，绝不算差异。

**差异（diff）** = 缺少必需规则 / 章节，或与默认规则矛盾。差异仅供参考；init 绝不自动修复。每个文件一条：`- <file>: <missing or contradicted rule>`。

**遗留漂移**（现有项目）：v4 `docs/prd/` 或 `docs/pdr/` 树、产品 `00-index.md`、v3/v4 provenance 行，或 PRD 中嵌入的现状 / 进展材料（例如每模块 `04-current.md`、`当前进展` 章节）都作为信息性遗留漂移报告，并提供迁移选项。init 绝不移动、改写或删除它们。

每次比较都忽略：provenance 行；已填占位符；索引 / 表格行；模块 / 术语 / 条目名称；语言；额外内容。

各产物必需元素：对照「规则来源」——项目副本只要可识别地包含该来源中的每条规则即为已对齐。措辞、语言、顺序与额外内容均可不同。

| 产物 | 规则来源 | 必需内容 |
| :--- | :--- | :--- |
| `AGENTS.md` 区块 | `assets/templates/project/agents-block.md` | `## Agent skills` 标题；三个子章节（Issue tracker / Domain docs / Development workflow）；指向 `docs/agents/testing.md` 的指针 |
| `docs/agents/issues.md` | `references/issues.md` | 目录契约；责任划分；条目格式（`Status:`、`## 完成判据`、`## 步骤`、`## 测试`、`## Log`；`## 结果` 可选）；归档后缀（`-done`/`-drop`，`-drop` ≠ 否定决策）；suggestion 路由 |
| `docs/agents/domain.md` | `assets/templates/project/agents-domain.md` | 先读 CONTEXT.md + `docs/adr/`；缺失静默继续；术语表用词；ADR 冲突标注 |
| `docs/agents/workflow.md` | `references/workflow.md` | 角色与写入权限；读什么；权威与升级；先对齐再实现；粒度；`## 步骤` + 续接；差距→issue；PRD 影响触发；变更协议；范围收敛；收尾；边界；测试准则指针 |
| `docs/agents/testing.md` | `references/testing.md` | 三种测试行为；SPEC / 完成判据追溯；scratch 路径与清理；回归默认；断言；Mock / Fixture；防御分层；L0–L3；`## 测试` 槽位 |
| `docs/agents/metadata.yml` | `assets/templates/project/metadata.yml` | `skill` + `version`（= 这棵树满足的版本）+ 可选 `updated`；戳只在验证过的运行后前移 |
| `docs/adr/README.md` | `references/adr.md` | 生命周期（修改 + Log、删除→墓碑桩、编号不复用）；目录表；两种写法的引用 sweep；默认不设 `Considered Options` |
| `docs/product/{00-README,01-requirements,02-architecture}.md` | `references/prd.md` | PRD 横幅；三章；仅 PRD 层链接；细节上限；无状态标记 |
| `docs/toc.yml` | `references/prd.md`（TOC 契约） | `title` / `version` / `date` / `abstract`；章节 id `overview` / `requirements` / `architecture` / `appendix`；附录 id `glossary` / `spec` / `current` / `adr`；所有路径存在；`modules: auto` |
| 模块 `00-README.md` | `references/prd.md` | 模块 PRD 内容；回链产品 PRD；无文档地图 / 依赖 |
| 模块 `00-index.md` | `references/prd.md` | 文档地图、依赖、接口归属、CAP↔FR 追溯；不发布；链接架构章节、TOC、模块 PRD |
| `docs/current/00-README.md` | `references/current.md` | 目的；PRD 封面回链（`../product/00-README.md`）；选定基线；模块索引；阅读顺序；只记现状 |
| `CONTEXT.md` | `references/terminology.md` | 术语表结构（含 `_Avoid_` 的术语块） |
| `docs/issues/` 树 | — | 叶子目录存在（可检查 `.gitkeep`） |

额外内容仅供参考，绝不算差异。

- `docs/agents/deps/`：叶子文件存在（`grilling.md`、`domain-modeling.md`、`tdd.md`、`doc-opt.md`、`boundaries.md`）。

### 报告格式

用项目的文档语言撰写报告（默认：中文，与模板一致）。

```
## Init report
- State: skip｜skip + 修复｜behind｜ahead｜unknown
- Repair: none｜additive｜scaffold｜bootstrap｜migrate｜align
- Created: …
- Aligned: …
- Diff: 每个文件一条：`- <file>: <missing or contradicted rule>`（仅供参考，不自动改；多文件 → 多条）
- Metadata: <旧> → <新>（updated）｜<旧>（kept — N 项改写待确认）
- Legacy drift: 检测到的 v4 / 旧版路径及提供的动作——仅供参考；未经用户授权绝不移动或改写。
- Next: 剩余占位符，外加一句「先做这个」；Current 基线未选定时，`选定 Current 基线` 排第一。
```

## 参考文档

规则承载细节；按需读取。

- `references/workflow.md`——推荐的单 issue 开发流程：角色与写入权限、读什么、对齐、变更协议、五步、收尾、TOC 维护、发布指针、粒度、范围收敛、边界。
- `references/testing.md`——测试用例编写准则：SPEC 追溯、强断言、Mock / Fixture 边界、防御分层、L0–L3 变更控制、交付门禁；优先级高于 `tdd`。
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
