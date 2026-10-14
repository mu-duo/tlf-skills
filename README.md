# @tanlinfeng/project-docs-workflow

面向 AI agent 的项目文档工作流 skill：帮助项目建立并维护 issue tracker、ADR、PDR、领域术语和开发工作流。主 skill 自带依赖兜底材料，可独立使用。

## 快速开始

**前置条件：** Node.js >= 18，并可使用 `npx`。安装器默认将 skill 安装到 `~/.agents/skills`。

```bash
npx @tanlinfeng/project-docs-workflow
```

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
| 预览安装 | `npx @tanlinfeng/project-docs-workflow --dry-run` | 仅显示计划，不写入文件。 |
| 指定 skills 根目录 | `npx @tanlinfeng/project-docs-workflow --dir <path>` | 覆盖默认目录。 |
| 覆盖主 skill | `npx @tanlinfeng/project-docs-workflow --force` | 安装时只覆盖 `project-docs-workflow`；依赖 skill 不覆盖。卸载时则表示跳过交互确认。 |
| 安装上游完整版 | `npx @tanlinfeng/project-docs-workflow --with-matt-skills` | 可选；需 Node.js >= 22.20。自定义 agent 可加 `--matt-agent <name>`。 |
| 检查依赖 | `npx @tanlinfeng/project-docs-workflow check` | 只检查依赖 skill 的解析状态；不检查主 skill 是否安装，也不检查项目文档是否初始化。 |
| 预览卸载 | `npx @tanlinfeng/project-docs-workflow uninstall --dry-run` | 只显示删除计划，不询问、不删除。 |
| 交互卸载 | `npx @tanlinfeng/project-docs-workflow uninstall` | 根据安装清单卸载本包记录的内容；TTY 下询问确认（默认否）。 |
| 非交互卸载 | `npx @tanlinfeng/project-docs-workflow uninstall --force` | 跳过确认；非 TTY 下必须显式传入 `--force`。 |

更多安装依赖的选项及行为见下方「高级细节」。

## 卸载安全须知

安装器会在目标 skills 根目录写入 `<target>/.project-docs-workflow.install.json`，卸载时依据清单记录的 skill **名称和操作类型**决定删除哪些路径：`installed` / `forced` 项会删除，`skipped` 项保留。清单记录的是名称和操作，**不记录内容哈希**：如果你之后把自己或其他工具的内容放到一个记录为本包安装的同名路径下，卸载仍会删除该路径。运行卸载前请先检查清单和目标目录；不确定时先使用 `--dry-run`。

如果清单不存在，卸载器只会处理主 skill `project-docs-workflow`，不会推测或删除其他依赖。实际卸载中，只有存在可移除条目时才会在完成后删除清单；dry-run、取消操作和没有可移除条目的运行都会保留清单。清单里的上游完整版会尽量通过 `skills` CLI 卸载；无法调用 CLI 时会回退为直接删除，可能留下上游锁文件中的过期条目。

## 手动复制

也可以不使用 npm 安装器，直接将 `skills/` 中需要的目录复制到 skills 根目录；只复制 `skills/project-docs-workflow` 也可以独立工作，因为主 skill 内含依赖 ref 兜底。手动复制不创建安装清单，也**不由安装器强制执行不覆盖规则**。之后运行 `uninstall` 时无法识别手动复制的依赖；若没有安装清单，它只会处理主 skill。

## docs-html-view（可选：手动渲染文档）

本包附带一个第一方 skill `docs-html-view`（与主 skill、`doc-opt` 一样，不属于上游集合）。安装器会随包一起分发它，但**安装时不会运行它**，项目文档初始化时也不会启用它；它只在用户手动调用时工作。

用途：把项目文档（PDR / Current / ADR）用标准的 Read the Docs（RTD）主题与 MyST Markdown 解析渲染成静态 HTML，输出到 `docs/docsHtmlView/build/html`。仅供本地浏览与分享，不替代源文档。

**边界（重要）：**

- **先确认再动手**：初始化与构建前，agent 会先列出所需的 Python 包、环境以及将要创建 / 修改的文件，取得你的明确同意后才执行；不会静默装包或改环境。
- **环境**：优先复用项目明确约定的文档环境；没有合适环境时才创建独立的 `.venv-docs`，不修改系统或应用环境。
- **标准构建**：首次使用 `sphinx-quickstart` 初始化，之后复用配置，通过 `make html`（或 `sphinx-build`）按需增量构建，不自建渲染封装器。
- **全手动**：不注册自动钩子，不自动打开浏览器，不启动常驻服务，不部署。
- **源文档只读**：渲染只读取源文档，不修改 `docs/` 下的 PDR / Current / ADR 源文件。
- **不参与 `check`**：`project-docs-workflow check` 只检查主 skill 的依赖解析状态，**不检查** `docs-html-view`，也不校验其渲染结果。

具体的脚本、命令与参数以该 skill 的 `SKILL.md` 为准（安装后位于 `<skills 根目录>/docs-html-view/SKILL.md`），README 不再重复其接口。

## English summary

`@tanlinfeng/project-docs-workflow` is an agent skill for setting up and maintaining project documentation workflows: issues, ADRs, PDRs, domain terminology, and development practices. Install it with `npx @tanlinfeng/project-docs-workflow` (Node.js >= 18; default destination `~/.agents/skills`). Installation does not initialize a project: from the target project root, manually invoke the skill using your agent's own skill mechanism. It creates missing documentation, reports drift on reruns, and does not overwrite existing content, except that it appends a missing `## Agent skills` block to an existing `AGENTS.md`.

The installer supports custom directories, dry runs, dependency checks, and manifest-based uninstall. Uninstall removes recorded package-owned paths by name, not by content hash; review the manifest or use a dry run before deleting anything. See the advanced details below for optional upstream dependencies and manifest behavior.

The package also ships a first-party `docs-html-view` skill (manual invocation only; distributed but not run at install). It renders PDR/Current/ADR docs to `docs/docsHtmlView/build/html` with Sphinx, MyST, and the stock RTD theme. After approval of packages, environment, and files, it uses `sphinx-quickstart` once and standard `make html` or `sphinx-build` thereafter. It never hooks, opens a browser, serves, deploys, or mutates source docs. `check` does not cover it.

<details>
<summary>高级细节</summary>

### 可选上游依赖

本包默认安装自带的轻量依赖 skill。可以通过 `--with-matt-skills` 改为尝试从 `mattpocock/skills` 安装完整版；上游 `skills` CLI 需要 Node.js >= 22.20。没有传此选项时，只有在 stdin 和 stdout 都是 TTY、执行安装且不是 dry-run 时，才会询问一次是否安装上游版本，默认否；非 TTY 场景不询问。可以用 `--matt-agent <name>` 指定上游 CLI 的 agent，默认是 `codex`。

仅以下 8 个依赖名参与上游安装：`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`tdd`、`deepwork`、`retro`、`improve-codebase-architecture`。主 skill、`doc-opt` 和 `docs-html-view` 不属于上游集合。目标目录中已存在的同名 skill 路径会保留，不会提交给上游。安装器通过 `npx --yes skills@latest` 调用上游；如果 Node 版本不足、找不到 `npx`、上游命令失败或网络错误，会回退复制缺失项的轻量版本，包安装仍以退出码 0 结束。

**上游安装目录注意：** 上游 CLI 使用 `-g -a <agent>`，安装到所选 agent 的全局 skills 目录，而不保证与 `--dir` 相同。安装器的安装后复核针对 `--dir`：两处目录不一致时，可能在 agent 全局目录安装完整版，同时在 `--dir` 下复制轻量版；`--dir` 中的清单只记录该目录里的项目，不记录独立的全局安装。这种错配既可能由自定义 `--dir` 引起，也可能由将 `--matt-agent` 改为其他 agent 引起。启用 `--with-matt-skills` 前，请确认 `--dir` 与所选 agent 的全局 skills 目录一致；否则建议使用默认轻量版。

### 安装清单格式

清单合并记录每个 skill 名称的处理结果，不含内容哈希。字段包括包版本、目标目录、更新时间和按名称索引的条目；条目记录类型、操作以及上游 agent（适用时）。示例：

```json
{
  "version": "<package-version>",
  "target": "/home/me/.agents/skills",
  "updatedAt": "<iso-timestamp>",
  "entries": {
    "project-docs-workflow": { "kind": "main", "action": "installed", "at": "…" },
    "tdd": { "kind": "lite", "action": "installed", "at": "…" },
    "deepwork": { "kind": "lite", "action": "skipped", "at": "…" },
    "retro": { "kind": "upstream", "action": "installed", "agent": "codex", "at": "…" }
  }
}
```

`kind` 可为 `main`、`lite`、`doc-opt`、`docs-html-view` 或 `upstream`；`action` 可为 `installed`、`forced` 或 `skipped`。卸载按记录的路径/名称操作：`skipped` 以及未知状态的条目保留。上游项会尽量通过 `skills` CLI 批量移除；若 CLI 无法运行或返回失败，安装器会直接删除对应目录作为回退，这可能使 `~/.agents/.skill-lock.json` 留有过期记录。

### 依赖解析与来源

`check` 逐项检查依赖是否能通过目标目录中同名 skill 的 `SKILL.md` 解析，或由主 skill 内置的 `references/deps/*.md` 兜底。每项至少有一种解析方式即通过；这不是主 skill 安装检查，也不是项目初始化检查。

内置轻量依赖来自 [mattpocock/skills](https://github.com/mattpocock/skills)（MIT，Matt Pocock）；`doc-opt` 与 `docs-html-view` 是本包附带的第一方 skill。主 skill 对引用能力先按名解析已安装 skill，不存在时使用内部 ref 兜底。详见 [`NOTICE`](./NOTICE)。

</details>

## License

MIT，见 [`LICENSE`](./LICENSE)。
