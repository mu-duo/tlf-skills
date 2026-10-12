# @tanlinfeng/project-docs-workflow

> 项目文档工作流 skill 包：提供 issue tracker、ADR、PDR、术语表与协作工作流约定，自带轻量依赖 skill 与 ref 兜底，可独立分发。

## 这是什么

`project-docs-workflow` 是一套面向 AI agent 的「项目文档工作流」skill。它把项目中的几类关键文档沉淀为可复用的模板与约定：

- **issue tracker**：任务 / 缺陷的登记与追踪约定
- **ADR**（Architecture Decision Record）：架构决策记录
- **PDR**（Product/Project Design Record）：设计与需求记录
- **terminology**：领域术语表，统一团队与 agent 的词汇
- **workflow**：上述文档之间的协作与更新流程

skill 本身是自包含的：主 skill 内部带 `references/deps/*.md` 兜底材料，因此即使没有安装任何依赖 skill，也能独立工作。包内同时附带了若干**轻量依赖 skill**（来自 `mattpocock/skills` 的精简版本）以及一个**附赠的 `doc-opt` skill**。

## 安装

通过 npx 直接安装到默认的 skills 根目录（`~/.agents/skills`）：

```bash
npx @tanlinfeng/project-docs-workflow
```

常用选项：

| 命令 | 说明 |
| --- | --- |
| `npx @tanlinfeng/project-docs-workflow` | 默认动作 `install`：安装主 skill 及所有依赖 skill |
| `npx @tanlinfeng/project-docs-workflow --dir <path>` | 指定 skills 根目录（默认 `~/.agents/skills`） |
| `npx @tanlinfeng/project-docs-workflow --force` | 覆盖已存在的 `project-docs-workflow`（**仅主 skill**；依赖 skill 仍不覆盖） |
| `npx @tanlinfeng/project-docs-workflow --dry-run` | 只打印将执行的操作，不写入任何文件 |
| `npx @tanlinfeng/project-docs-workflow --with-matt-skills` | 可选：依赖 skill 改从上游 `mattpocock/skills` 安装**完整版**（需 Node >= 22.20） |
| `npx @tanlinfeng/project-docs-workflow --matt-agent <name>` | 上游安装使用的 agent（默认 `codex`，落盘到其全局目录 `~/.agents/skills`） |
| `npx @tanlinfeng/project-docs-workflow check` | 检查依赖 skill 的解析状态，全部可解析时退出码为 0，否则为 1 |

### 覆盖策略（安全优先）

安装器**永不覆盖用户已存在的同名 skill**。若目标目录中已存在同名目录，会打印 `同名 skill 已存在，保留用户版本：<name>` 并跳过。只有对主 skill `project-docs-workflow` 使用 `--force` 时才会覆盖它；依赖 skill 即使加了 `--force` 也仍会跳过。

### 可选：从上游安装「完整版」依赖 skill

包内自带的依赖 skill 是来自 `mattpocock/skills` 的**轻量版**。如果你更想要**完整上游版本**，可以启用 `--with-matt-skills`：安装器会调用官方 `skills` CLI（npm 包 `skills`）执行

```bash
npx --yes skills@latest add mattpocock/skills -g -y -a <agent> -s <name1> <name2> ...
```

- **交互式询问**：不带 `--with-matt-skills` 时，仅当 stdout 与 stdin **都是 TTY**、动作为 `install`（非 `check`）、且非 `--dry-run` 时，才提示一次 `是否从上游安装依赖 skill 的完整版（mattpocock/skills）？[y/N] `，**默认否**（空输入或其它输入均视为否）。非 TTY / 管道 / CI 场景**完全不询问**，不会挂起。
- **受管集合**：仅这 8 个名字参与上游安装：`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`tdd`、`deepwork`、`retro`、`improve-codebase-architecture`；`doc-opt` 与主 skill 不属于上游集合，维持原有行为。
- **永不覆盖**：调用上游前会先检测这 8 个名字里哪些在目标目录中**已存在**，已存在者**原样保留、绝不提交给上游**；只有缺失的名字才会通过 `-s` 传给上游。
- **顺序与去重**：先跑上游；随后复核上游目标目录，仍然缺失的名字才回退复制本包的轻量版。启用上游时，由上游负责的名字不会再复制轻量版；未启用时（默认）行为与之前完全一致。
- **降级、绝不失败**：Node < 22.20、找不到 `npx`、上游非 0 退出或网络错误时，只打印中文告警并回退到缺失项的轻量版安装，整体仍以退出码 0 结束。
- **agent 与目录注意**：上游固定以 `-a <agent> -g` 安装到该 agent 的**全局目录**（默认 `codex` → `~/.agents/skills`，正好与默认目标一致）。可用 `--matt-agent <name>` 覆盖 agent。若你传入了非默认的 `--dir`，上游部分**无法跟随 `--dir`**（仍落到 agent 全局目录），安装器会明确告警，同时 `--dir` 下的轻量版仍按原逻辑处理。
- **dry-run**：`--dry-run --with-matt-skills` 只打印将执行的上游命令、以及哪些名字因已存在而跳过，不实际执行。

## 直接复制（不使用 npm 安装器）

也可以完全跳过安装器，手动把 `skills/` 下需要的内容复制进你的 skills 根目录：

- 逐个复制 `skills/*` 中的目录；**遇到同名目录就跳过，绝不覆盖用户版本**。
- 也可以**只复制 `skills/project-docs-workflow` 这一个目录**：它会通过内部的 ref 兜底（`references/deps/*.md`）独立工作，无需其他依赖 skill。

## 两级解析协议

skill 在引用依赖能力时，遵循两级解析：

1. **按名解析**：如果 skills 根目录下存在同名 skill（`<target>/<name>/SKILL.md`），直接使用该已安装的 skill。
2. **ref 兜底**：否则，回退到主 skill 内部自带的 `references/deps/<fallback>.md`。

| 引用名 | 兜底文件 |
| --- | --- |
| `grilling` | `grilling.md` |
| `grill-me` | `grilling.md` |
| `grill-with-docs` | `grilling.md`、`domain-modeling.md` |
| `domain-modeling` | `domain-modeling.md` |
| `tdd` | `tdd.md` |
| `deepwork` | `boundaries.md` |
| `retro` | `boundaries.md` |
| `doc-opt` | `doc-opt.md` |
| `improve-codebase-architecture` | `boundaries.md` |

`check` 子命令会对照上表逐个报告「按名可解析（skill 已安装）」或「ref 兜底可用」，只要每个名字能通过任一级解析即视为通过。

## 内置 skill 与来源

| skill | 说明 | 来源 |
| --- | --- | --- |
| `project-docs-workflow` | 主 skill：issue / ADR / PDR / 术语 / 工作流 | 本包 |
| `grilling`、`grill-me`、`grill-with-docs` | 需求拷问相关 | `mattpocock/skills` 精简版（MIT，Matt Pocock） |
| `domain-modeling` | 领域建模 | 同上 |
| `tdd` | 测试驱动开发 | 同上 |
| `deepwork`、`retro`、`improve-codebase-architecture` | 精简/占位版本 | 同上 |
| `doc-opt` | 文档优化（附赠完整版） | 本包附赠 |

部分内置 skill 内容摘自 <https://github.com/mattpocock/skills>（MIT License，Copyright (c) 2026 Matt Pocock），详见 [`NOTICE`](./NOTICE)。

上表中的 8 个上游依赖 skill 都可以改用完整版：安装时加 `--with-matt-skills` 即会从上游安装（见上文「可选：从上游安装『完整版』依赖 skill」）。

## 版本说明

本包版本 `2.x` 与「模板生成 v2」对齐：模板结构与生成约定以 v2 为准。

## License

MIT，见 [`LICENSE`](./LICENSE)。

---

## English summary

`project-docs-workflow` is an npm-packaged agent **skill bundle** for project documentation workflows: issue tracking, ADRs, PDRs, a terminology glossary, and the workflow that ties them together. The main skill is self-contained via internal `references/deps/*.md` fallbacks, and ships with lightweight dependency skills (trimmed from [mattpocock/skills](https://github.com/mattpocock/skills), MIT, Matt Pocock) plus a bundled `doc-opt` bonus skill.

Install with `npx @tanlinfeng/project-docs-workflow` (defaults to `~/.agents/skills`; options: `--dir <path>`, `--force`, `--dry-run`, `--with-matt-skills`, `--matt-agent <name>`, and the `check` subcommand). The installer **never overwrites** an existing skill of the same name — it skips it, preserving your version. `--force` overwrites only the main `project-docs-workflow` skill.

Optionally, `--with-matt-skills` installs the **full upstream** versions of the dependency skills from `mattpocock/skills` via the official `skills` CLI (`npx --yes skills@latest add mattpocock/skills -g -y -a <agent> -s ...`, requires Node >= 22.20). Without the flag, an interactive TTY gets a single prompt (default **No**); non-TTY/piped/CI runs never prompt. The 8 upstream-managed names are `grilling`, `grill-me`, `grill-with-docs`, `domain-modeling`, `tdd`, `deepwork`, `retro`, `improve-codebase-architecture`; `doc-opt` and the main skill are unaffected. Any name already present is left untouched and never sent upstream, and the installer re-checks afterwards, falling back to the bundled lite copy for anything still missing. If upstream can't run (Node too old, no `npx`, non-zero exit, network error), it warns and falls back — the install still exits 0. Upstream installs into the agent's global dir (`codex` → `~/.agents/skills`), so it cannot follow a custom `--dir` (a warning is printed).

You can also copy `skills/*` directly into your skills root (skip any existing directory name, never overwrite); copying just `skills/project-docs-workflow` works standalone thanks to the internal ref fallbacks.

Resolution is two-level: use an installed skill by name if present, otherwise follow `references/deps/*.md` inside the skill. Version `2.x` aligns with template generation v2. Licensed MIT (see `LICENSE` and `NOTICE`).
