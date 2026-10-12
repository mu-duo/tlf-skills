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
| `npx @tanlinfeng/project-docs-workflow check` | 检查依赖 skill 的解析状态，全部可解析时退出码为 0，否则为 1 |

### 覆盖策略（安全优先）

安装器**永不覆盖用户已存在的同名 skill**。若目标目录中已存在同名目录，会打印 `同名 skill 已存在，保留用户版本：<name>` 并跳过。只有对主 skill `project-docs-workflow` 使用 `--force` 时才会覆盖它；依赖 skill 即使加了 `--force` 也仍会跳过。

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

## 版本说明

本包版本 `2.x` 与「模板生成 v2」对齐：模板结构与生成约定以 v2 为准。

## License

MIT，见 [`LICENSE`](./LICENSE)。

---

## English summary

`project-docs-workflow` is an npm-packaged agent **skill bundle** for project documentation workflows: issue tracking, ADRs, PDRs, a terminology glossary, and the workflow that ties them together. The main skill is self-contained via internal `references/deps/*.md` fallbacks, and ships with lightweight dependency skills (trimmed from [mattpocock/skills](https://github.com/mattpocock/skills), MIT, Matt Pocock) plus a bundled `doc-opt` bonus skill.

Install with `npx @tanlinfeng/project-docs-workflow` (defaults to `~/.agents/skills`; options: `--dir <path>`, `--force`, `--dry-run`, and the `check` subcommand). The installer **never overwrites** an existing skill of the same name — it skips it, preserving your version. `--force` overwrites only the main `project-docs-workflow` skill.

You can also copy `skills/*` directly into your skills root (skip any existing directory name, never overwrite); copying just `skills/project-docs-workflow` works standalone thanks to the internal ref fallbacks.

Resolution is two-level: use an installed skill by name if present, otherwise follow `references/deps/*.md` inside the skill. Version `2.x` aligns with template generation v2. Licensed MIT (see `LICENSE` and `NOTICE`).
