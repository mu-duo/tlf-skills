# @tanlinfeng/project-docs-workflow

面向 AI agent 的项目文档工作流 skill：帮助项目建立并维护 issue tracker、ADR、PDR、领域术语和开发工作流。主 skill 自带依赖兜底材料，可独立使用。

## 快速开始

**前置条件：** Node.js >= 18，并可使用 `npx`。安装器默认将 skill 安装到 `~/.agents/skills`。

```bash
# 默认动作即安装；@latest 是 dist-tag，不保证等于最高版本
npx @tanlinfeng/project-docs-workflow@latest install

# 也可指定一个实际已发布的确切版本（示例）
npx @tanlinfeng/project-docs-workflow@2.2.0 install
```

不带版本时，`npx` 可能**优先使用当前项目已安装的版本**；要选择安装器版本，请显式写 `@latest` 或 `@<版本>`（缓存 / 网络策略另计）。安装器自身**不获取版本**，而是从所选源包同步内容。

**兼容性限定：** `npx <pkg>@<版本> install` 运行的是**该版本自带的安装器代码**。本页描述的自动同步 / `--force` 等语义**仅适用于包含本安装策略的包版本**；更早的已发布版本保留其当时的行为（例如 `--force` 可能只覆盖主 skill）。因此「指定较旧版本」只在这类兼容版本内才是等价回滚。示例中的 `@2.2.0` 仅用于说明 npm 语法（须为实际已发布的版本），不表示该版本具备上述新语义。

这一步只安装 skill，**不会初始化任何项目文档**。安装完成后，进入要设置文档的**目标项目根目录**，使用当前 agent 自己的 skill 调用方式手动运行 `project-docs-workflow`。例如可以这样请求：

> 请使用 project-docs-workflow skill，为当前项目初始化项目文档工作流。

skill 会检查并创建缺少的内容，包括：

- `AGENTS.md` 中的 `## Agent skills` 区块
- `docs/agents/issues.md`、`docs/agents/domain.md`、`docs/agents/workflow.md`
- `docs/agents/deps/` 依赖兜底文件
- `docs/issues/` issue 目录树
- `docs/adr/README.md`、`docs/pdr/00-README.md`、`docs/current/00-README.md` 和 `CONTEXT.md`

每个项目手动运行一次即可。以后模板更新时可以再次运行，以检查对齐情况并报告差异；运行是幂等的，不会改写已有内容。例外是：若 `AGENTS.md` 已存在但没有 `## Agent skills`，skill 会在文件末尾追加该区块；若区块已存在，则只比较、不重写。

## 命令与选项

| 场景 | 命令 / 选项 | 说明 |
| --- | --- | --- |
| 安装到默认目录 | `npx @tanlinfeng/project-docs-workflow` | 默认动作是安装，目标为 `~/.agents/skills`。 |
| 预览安装 | `npx @tanlinfeng/project-docs-workflow --dry-run` | 仅显示计划：不写文件、不询问、不执行上游；Node 相关判断（如上游可用性）如实反映。 |
| 指定 skills 根目录 | `npx @tanlinfeng/project-docs-workflow --dir <path>` | 覆盖默认目录。 |
| 安装中文镜像 | `npx @tanlinfeng/project-docs-workflow --zh` | 默认从 `skills/` 安装英文版；`--zh` 改为从 `skills_zh/` 安装中文版。两种语言的 skill 同名、互斥，一次只能安装一种；再次运行另一种语言即可切换。仅 install 支持，`check` / `uninstall` 与语言无关。 |
| 覆盖第一方 skill | `npx @tanlinfeng/project-docs-workflow --force` | 当第一方条目无法被有效清单确认为包内安装时，显式替换它；**不**更新外部依赖（外部更新需显式 `--with-matt-skills`）。卸载时表示跳过交互确认。 |
| 显式刷新上游依赖 | `npx @tanlinfeng/project-docs-workflow --with-matt-skills` | 可选增强：通过 `npx` 安装缺失 + 更新已存在的 8 个外部上游完整版；仅在默认 codex 全局目标可执行，其他组合在写入前拒绝。需 Node.js >= 22.20；失败不复制独立轻量版。 |
| 检查依赖 | `npx @tanlinfeng/project-docs-workflow check` | 逐项检查：目标目录存在同名 skill（按名解析，**不**验证是否为完整版）**或**主 skill 内置回退 `references/deps/*` 可用即通过；全新安装（未装任何独立依赖）也会通过。不检查主 skill 是否安装，也不检查项目文档是否初始化。 |
| 预览卸载 | `npx @tanlinfeng/project-docs-workflow uninstall --dry-run` | 只显示删除计划，不询问、不删除。 |
| 交互卸载 | `npx @tanlinfeng/project-docs-workflow uninstall` | 根据安装清单卸载本包记录的内容；TTY 下询问确认（默认否）。 |
| 非交互卸载 | `npx @tanlinfeng/project-docs-workflow uninstall --force` | 跳过确认；非 TTY 下必须显式传入 `--force`。 |

更多安装依赖的选项及行为见下方「高级细节」。

## 安装与更新语义

普通安装（默认动作）对**第一方 skill**（`project-docs-workflow`、`doc-opt`、`docs-html-view`、`lite-task`）执行**全目录同步**：

- 若上一份**有效清单**确认该路径由本包安装（`installed` / `forced`、本地），安装会用源包内容覆盖该目录——**可能覆盖你对本地文件所做的修改**。第一方受管安装目录是可整体替换的分发副本。
- 若某第一方路径无法被有效清单确认为包内安装（手工复制、清单记为 `skipped`、清单缺失、清单损坏 / 不可解析、符号链接），默认**保留**不动；只有显式 `--force` 才替换该第一方条目。替换的是该路径本身，符号链接指向的 referent 不被改动。

**语言选择（默认 en / `--zh`）：** 安装器默认从 `skills/` 安装英文第一方 skill；传入 `--zh` 则从 `skills_zh/` 安装中文镜像。两个镜像的目录名与 frontmatter `name` 完全相同，因此同一目标目录一次只能保留一种语言：用另一种语言重新运行安装，会把清单中由本包接管（`installed` / `forced`）的同名第一方 skill 全量替换为该语言版本；清单中由本包接管（`installed` / `forced`）的第一方条目记录 `lang`（`en` / `zh`），安装器会依据上一份清单提示 `切换语言：en → zh` 或 `zh → en`。`--force` 不是切换语言的必要条件，只有在条目无法被有效清单确认为包内安装（手工复制、`skipped`、清单缺失 / 损坏、符号链接）时才需要用它覆盖接管。

**外部依赖默认不分发、不自动安装**：普通安装与 `--force` 默认都**不**安装或更新独立外部依赖（`--force` 只作用于第一方）；唯一的例外是用户在上文「可选增强」中明确同意安装缺失的上游完整版。缺失的独立名称**不等于能力缺失**——主 skill 内置回退 `references/deps/*` 已可用，全新安装即可独立工作。安装**先检查 / 列出**依赖：已存在的独立依赖一律保留；对**缺失**的受支持名称，仅在交互式安装（stdin 与 stdout 均为 TTY、非 dry-run）且上游目标安全、Node 达标时，**可选**询问一次是否安装上游完整版（回答 yes 只安装缺失项、不更新已有）。No / 回车 / 非 TTY / 非等价的自定义 `--dir` / Node 不足 → 直接使用内部回退，**不**复制任何独立轻量 skill。要**刷新已有外部依赖**，须显式 `--with-matt-skills`（见「可选上游依赖」）或自行手动更新。主 skill 的内部引用（`references/deps/*`）随主 skill 一起更新，不当作独立外部依赖单独管理。

安装只处理 skills 目录，**不会**初始化或改写目标项目内已物化的文档（`AGENTS.md`、`docs/agents/*` 等）；项目文档需要显式运行 skill 对齐 / 迁移。`--dry-run` 不写任何文件、不询问、不执行上游，逐条显示将执行的精确动作。本包不提供独立的 `update` 命令；更新即重新运行安装。

**边界说明（简明）：**

- **清单文件本身是符号链接时始终拒绝**（即使 `--force`），以免覆盖外部文件；这与「第一方 skill 路径是符号链接」不同——后者在 `--force` 下可替换该路径本身。
- 替换按**单个 skill** 进行：某次替换失败时会尝试恢复旧内容；若无法恢复，则保留备份并在报告中给出路径。这只是单个 skill 的失败处理，**不是**所有 skill 的事务性原子操作。

## 卸载安全须知

安装器会在目标 skills 根目录写入 `<target>/.project-docs-workflow.install.json`，卸载时依据清单记录的 skill **名称和操作类型**决定删除哪些路径：`installed` / `forced` 项会删除，`skipped` 项保留。清单记录的是名称和操作，**不记录内容哈希，也不记录你对本地文件的改动指纹**：如果你之后把自己或其他工具的内容放到一个记录为本包安装的同名路径下，卸载仍会删除该路径。第一方受管安装目录是可整体替换的分发副本。运行卸载前请先检查清单和目标目录；不确定时先使用 `--dry-run`。

如果清单不存在，卸载器只会处理主 skill `project-docs-workflow`，不会推测或删除其他依赖。实际卸载中，只有存在可移除条目时才会在完成后删除清单；dry-run、取消操作和没有可移除条目的运行都会保留清单。清单里的上游完整版会尽量通过 `skills` CLI 卸载；无法调用 CLI 时会回退为直接删除，可能留下上游锁文件中的过期条目。

## 手动复制

也可以不使用 npm 安装器，直接将 `skills/`（英文）或 `skills_zh/`（中文）中需要的目录复制到 skills 根目录；两者只能选其一，**不要同时复制**，因为目录名与 skill `name` 相同，会互相覆盖。只复制 `skills/project-docs-workflow` 或 `skills_zh/project-docs-workflow` 也可以独立工作，因为主 skill 内含依赖 ref 兜底。手动复制不创建安装清单，因此这些路径属于「无法被有效清单确认」的第一方路径，安装时默认**保留**，只有显式 `--force` 才替换。之后运行 `uninstall` 时无法识别手动复制的依赖；若没有安装清单，它只会处理主 skill。

## docs-html-view（可选：手动渲染文档）

本包附带一个第一方 skill `docs-html-view`（与主 skill、`doc-opt`、`lite-task` 一样，不属于上游集合）。安装器会随包一起分发它，但**安装时不会运行它**，项目文档初始化时也不会启用它；它只在用户手动调用时工作。

用途：把项目文档（PDR / Current / ADR）用标准的 Read the Docs（RTD）主题与 MyST Markdown 解析渲染成静态 HTML，输出到 `docs/docsHtmlView/build/html`。仅供本地浏览与分享，不替代源文档。

**边界（重要）：**

- **先确认再动手**：初始化与构建前，agent 会先列出所需的 Python 包、环境以及将要创建 / 修改的文件，取得你的明确同意后才执行；不会静默装包或改环境。
- **环境**：优先复用项目明确约定的文档环境；没有合适环境时才创建独立的 `.venv-docs`，不修改系统或应用环境。
- **标准构建**：首次使用 `sphinx-quickstart` 初始化，之后复用配置，通过 `make html`（或 `sphinx-build`）按需增量构建，不自建渲染封装器。
- **全手动**：不注册自动钩子，不自动打开浏览器，不启动常驻服务，不部署。
- **源文档只读**：渲染只读取源文档，不修改 `docs/` 下的 PDR / Current / ADR 源文件。
- **不参与 `check`**：`project-docs-workflow check` 只检查主 skill 的依赖解析状态，**不检查** `docs-html-view`，也不校验其渲染结果。

具体的脚本、命令与参数以该 skill 的 `SKILL.md` 为准（安装后位于 `<skills 根目录>/docs-html-view/SKILL.md`），README 不再重复其接口。

## lite-task（可选：轻型任务开发流程）

本包附带一个第一方 skill `lite-task`（与主 skill、`doc-opt`、`docs-html-view` 一样，不属于上游集合）。它是面向**小、低风险任务**（或用户显式选择时）的轻型开发流程：与 `project-docs-workflow` 相同的五步（功能同步 / 骨架 / 实现 / 异常 / 回顾），但不强制 issue、PDR、Current 或 ADR 记录——默认一般只产出代码。

当任务变大（涉及契约变更、跨模块影响，或需要留存长期决策）时，应升级到 `project-docs-workflow`，不要在本流程里静默写文档。具体行为以该 skill 的 `SKILL.md` 为准（安装后位于 `<skills 根目录>/lite-task/SKILL.md`），README 不再重复其接口。

## 中文镜像（--zh）

`skills_zh/` 是随包分发的中文镜像，用于让中文使用者以相同的 skill 名称工作。它完整覆盖四个第一方 skill：`project-docs-workflow`、`doc-opt`、`docs-html-view`、`lite-task`；目录名与 frontmatter `name` 均与英文源完全一致。

- **同名互斥**：同一目标目录一次只应安装一种语言。默认安装英文源 `skills/`；`--zh` 安装中文镜像 `skills_zh/`，并会把本包接管的同名第一方 skill 替换为中文版本。再运行不带 `--zh` 的安装即切回英文。`--zh` 仅适用于 install；`check` 与 `uninstall` 与语言无关。
- **手工快照，不自动同步**：中文镜像基于英文源提交 `3e408c5`（2026-10-19）翻译，不随英文源后续修改自动同步；英文源更新后需要重新翻译与审校。内容以英文源为准，发现不一致时应修正中文镜像。
- **审校策略**：4 个 `SKILL.md` 与 `skills_zh/README.md` 经人工审校，references / EXAMPLES / technical 抽样复核后合入；不以未审校的机器翻译作为最终版本，涉及命令、路径、边界条件与技术术语的段落需对照英文源复核。
- **一致性检查**：可运行 `node scripts/check-skills-zh.js` 检查中文镜像的结构与名称等一致性。
- **与 `--with-matt-skills` 的关系**：8 个外部依赖来自上游，只有英文；`--zh` 只影响本包第一方 skill 的来源。组合使用时请写成 `--zh --with-matt-skills`；若只运行默认（不带 `--zh`）的安装，会把第一方 skill 切回英文。

## English summary

`@tanlinfeng/project-docs-workflow` is an agent skill for setting up and maintaining project documentation workflows: issues, ADRs, PDRs, domain terminology, and development practices. Install it with `npx @tanlinfeng/project-docs-workflow@latest install`, or pin an exact published version with an npm spec such as `@2.2.0` (Node.js >= 18; default destination `~/.agents/skills`). Without a spec, npx may prefer the version already installed in the current project; write `@latest` or `@<version>` to select the installer version (cache/network policy is separate), and the installer never fetches versions itself. Because `npx <pkg>@<version> install` runs that version's own installer code, the sync / `--force` semantics on this page apply only to package versions that contain this installation strategy; older published versions keep their historical behavior (e.g. `--force` may only overwrite the main skill), so pinning an older version is only an equivalent rollback within such compatible versions. Installation does not initialize a project: from the target project root, manually invoke the skill using your agent's own skill mechanism. It creates missing documentation, reports drift on reruns, and does not overwrite existing content, except that it appends a missing `## Agent skills` block to an existing `AGENTS.md`.

An ordinary install full-directory-syncs the first-party skills (`project-docs-workflow`, `doc-opt`, `docs-html-view`, `lite-task`) when a valid manifest confirms the package installed them, so it may overwrite local edits; a first-party path not confirmed as package-owned is preserved unless `--force` replaces that entry. External dependencies are preserved by default, and `--force` alone does not update them; explicit `--with-matt-skills` refreshes the eight supported upstream names (updating existing ones and installing missing) only on the default codex target, with other target/agent combinations rejected before any write. The package ships no standalone dependency skills: missing external names are covered by the skill's internal fallback references (`references/deps/*`), no independent lite skill is copied, and existing standalone installs (including older lite copies) are preserved and never auto-cleaned or migrated. A manifest file that is itself a symlink is always refused (even with `--force`), unlike a first-party skill path that is a symlink; per-skill replacement failures restore the old content or retain a backup and report the path, so this is not an all-skills transaction. The installer supports custom directories, dry runs, dependency checks, and manifest-based uninstall. Uninstall removes recorded package-owned paths by name, not by content hash, and records no local-edit fingerprints; review the manifest or use a dry run before deleting anything. See the advanced details below for optional upstream dependencies and manifest behavior.

The package also ships `skills_zh/`, a manually reviewed Chinese mirror of the four first-party skills with identical directory and skill names. Installs default to the English tree (`skills/`); pass `--zh` to install the Chinese mirror. The two variants are mutually exclusive: running the other language switches the package-owned same-named first-party skills, and the manifest records the choice in the `lang` field of each package-owned first-party entry. `--zh` is install-only; `check` and `uninstall` are language-agnostic. The mirror is a snapshot of source commit `3e408c5` (2026-10-19) and is not auto-synced; use `node scripts/check-skills-zh.js` to check it. `--with-matt-skills` installs English upstream dependencies, so pass `--zh` too to keep the first-party skills Chinese; an English install without `--zh` switches them back.

The package also ships a first-party `docs-html-view` skill (manual invocation only; distributed but not run at install). It renders PDR/Current/ADR docs to `docs/docsHtmlView/build/html` with Sphinx, MyST, and the stock RTD theme. After approval of packages, environment, and files, it uses `sphinx-quickstart` once and standard `make html` or `sphinx-build` thereafter. It never hooks, opens a browser, serves, deploys, or mutates source docs. `check` does not cover it.

The package also ships a first-party `lite-task` skill: a lightweight development workflow for small, low-risk tasks (or when the user explicitly opts in). It keeps the same five steps as `project-docs-workflow` (功能同步 / 骨架 / 实现 / 异常 / 回顾) but drops its documentation obligations — no forced issue, PDR, Current, or ADR bookkeeping, generally code only. Escalate to `project-docs-workflow` when the task grows (contract change, cross-module impact, or a durable decision).

<details>
<summary>高级细节</summary>

### 可选上游依赖

主 skill **自带内部回退**（`references/deps/{grilling,domain-modeling,tdd,doc-opt,boundaries}.md`）：外部依赖未安装时按对应回退执行，功能可用。本包**不**随包分发独立依赖 skill——默认只分发四个第一方 skill（`project-docs-workflow`、`doc-opt`、`docs-html-view`、`lite-task`）；安装器也不复制任何独立轻量 skill。

**默认（不带 `--with-matt-skills`）：**
- 已存在的独立依赖一律**保留**（含旧版本曾复制的轻量目录），不判定完整版、不自动清理 / 迁移。
- 缺失的受支持名称：仅在交互式安装（stdin 与 stdout 均为 TTY、非 dry-run）且上游目标安全、Node >= 22.20 时**可选**询问一次；这是**可选的完整版增强**，不是必需依赖。回答 yes 只安装缺失项；No / 直接回车 / 非 TTY / 非等价的自定义 `--dir` / Node 不足时，直接使用内部回退（**不**复制独立轻量 skill）。
- `--force` 单独使用**不**安装或更新外部依赖。

**显式 `--with-matt-skills`（可选增强）：** 通过 `npx` 安装缺失 + **更新**已存在的 8 个外部上游完整版；不询问，提示**本地依赖改动可能被覆盖**。第一方自带集合（主 skill、`doc-opt`、`docs-html-view`、`lite-task`）**不提交上游**，但仍照常执行普通第一方全目录同步；命名集合之外的外部目录保留不动。需 Node.js >= 22.20。

仅以下 8 个名称参与上游操作：`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`tdd`、`deepwork`、`retro`、`improve-codebase-architecture`。`/grill-me` 不再由本包提供独立入口；需要独立入口请安装上游，主 skill 的内部回退仍支持相同行为（无斜杠别名）。

**目标目录安全（重要）：** 上游 `skills` CLI 没有 `--dir`，其目标由 `-g -a <agent>` 决定。本安装器只在**默认 codex 全局目标**（或与其 realpath 等价、可验证匹配的目录）下才执行上游操作；只有**非等价的自定义 `--dir`，或未经验证的 `--matt-agent` 组合**无法证明匹配，会在**任何写入之前拒绝** `--with-matt-skills` 并给出手动更新指引。普通（非等价自定义 `--dir`）安装仍照常保留已有依赖、使用内部回退，不给出误导性的上游询问；realpath 与默认目标等价的别名不受此限，仍可能给出可选询问。

**失败处理（非原子）：** 上游 `add -y` 会覆盖，且没有 `--force add`；安装器以窄名称集合 + `--json` 逐个检测成功 / 失败。已有依赖更新**可能部分成功**，本包装器**不负责恢复**，请勿视为原子或可回滚；**不再复制独立轻量版**作为回退。已存在的依赖失败时**不删除、不重建**，保留原归属（可能已被上游部分改动）；仅在**原本缺失、本次尝试新建**的项失败时，清理该新路径（仅此路径）并以非零退出报告。无论成功与否，主 skill 内部回退始终可用，基本安装的主 skill 可正常工作；可选的上游请求未满足时**明确失败**（非零退出），不报告成功。仅在已知安全目标上确认成功的项才在清单中记为 upstream-owned。上游 CLI 的 `--json` 输出契约并未稳定公开；若其格式变化导致无法解析，安装器将**保守地按失败报告**（不声称成功）。

### 安装清单格式

清单合并记录每个 skill 名称的处理结果，不含内容哈希。字段包括包版本、目标目录、更新时间和按名称索引的条目；条目记录类型、操作以及上游 agent（适用时）；由本包安装的第一方条目还记录安装语言 `lang`（`en` / `zh`）。示例：

```json
{
  "version": "<package-version>",
  "target": "/home/me/.agents/skills",
  "updatedAt": "<iso-timestamp>",
  "entries": {
    "project-docs-workflow": { "kind": "main", "lang": "en", "action": "installed", "at": "…" },
    "doc-opt": { "kind": "doc-opt", "lang": "en", "action": "installed", "at": "…" },
    "docs-html-view": { "kind": "docs-html-view", "action": "skipped", "at": "…" },
    "lite-task": { "kind": "lite-task", "lang": "en", "action": "installed", "at": "…" },
    "retro": { "kind": "upstream", "action": "installed", "agent": "codex", "at": "…" }
  }
}
```

`kind` 可为 `main`、`doc-opt`、`docs-html-view`、`lite-task` 或 `upstream`；历史清单里还可能出现 `lite`（早期版本曾复制独立轻量 skill）——安装时一律保留，用户主动运行 `uninstall` 时仍按历史归属处理（升级时不会静默清除用户目录；清理 / 迁移仅在用户显式授权时进行）。`action` 可为 `installed`、`forced` 或 `skipped`。由本包安装（`installed` / `forced`）的第一方条目还记录 `lang`（`en` / `zh`）；`skipped` 条目与上游条目不带 `lang`。卸载按记录的路径/名称操作：`skipped` 以及未知状态的条目保留。上游项会尽量通过 `skills` CLI 批量移除；若 CLI 无法运行或返回失败，安装器会直接删除对应目录作为回退，这可能使 `~/.agents/.skill-lock.json` 留有过期记录。

### 依赖解析与来源

`check` 逐项检查依赖：目标目录中存在同名 skill（按名解析即可，**不**验证是否为完整版）**或**主 skill 内置 `references/deps/*.md` 回退可用，即视为通过——因此全新安装（未装任何独立依赖）也会通过。这不是主 skill 安装检查，也不是项目初始化检查。

内部回退文档中**源自上游的部分**（见 [`NOTICE`](./NOTICE)：`references/deps/{grilling,domain-modeling,tdd,boundaries}.md`）裁剪 / 改编自 [mattpocock/skills](https://github.com/mattpocock/skills)（MIT，Matt Pocock）；`references/deps/doc-opt.md` 为本包第一方回退，**非**上游派生。本包**不**随包分发独立依赖 skill；`doc-opt`、`docs-html-view` 与 `lite-task` 是本包附带的第一方 skill。主 skill 对引用能力先按名解析已安装的独立 skill，不存在时执行内部 ref 回退。详见 [`NOTICE`](./NOTICE)。

</details>

## License

MIT，见 [`LICENSE`](./LICENSE)。
