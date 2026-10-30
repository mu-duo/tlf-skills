# 中文 Skill 镜像（skills_zh）

本目录是 `skills/` 的完整中文镜像，用于安装中文版 skill。目录名、文件名与 frontmatter 的 `name` 值均与英文版保持一致。

- **唯一源**：`skills/` 是唯一事实来源（source of truth）；本目录只是它的中文快照。
- **手动快照**：本目录不自动同步，也不参与构建时生成。
- **更新时机**：仅在用户明确要求时，才按 `skills/` 更新本目录。
- **内容范围**：翻译 Markdown 正文与 YAML 接口值；不改代码、命令、路径、标识符、frontmatter 键和 `policy`。

## 安装

默认安装英文版；传入 `--zh` 安装本中文镜像。

- **默认（英文）**：运行安装器时不加语言参数，安装 `skills/`。
- **中文（`--zh`）**：运行 `npx @tanlinfeng/project-docs-workflow install --zh`，安装 `skills_zh/`。
- **互斥**：两个目录中的 skill 目录名与 `name` 完全相同，安装后占用同一组 skill 名，因此不能同时安装。
- **切换语言**：用目标语言参数重新运行安装器；安装器会替换本包接管的同名 skill。切回英文时去掉 `--zh` 即可。
- **`check` / `uninstall`**：与语言无关，按已安装的 skill 名与安装清单工作，不需要指定语言。
- **npm 包**：`skills_zh` 已列入 `package.json` 的 `files`，因此会随包分发；但只有使用 `--zh` 时才会安装。
- **`--with-matt-skills`**：该选项只控制是否通过 npx 安装/更新上游外部依赖（共 8 个），与英文/中文选择无关。中文镜像不提供单独的中文版外部依赖，也不改变该选项的行为。当前是中文安装时，若同时运行该选项，请记得也传 `--zh`；否则默认安装会把第一方 skill 切回英文。

## 源基线

| 项目 | 值 |
| --- | --- |
| 源目录 | `skills/` |
| 基线提交 | `v5.6` |
| 基线日期 | 2026-10-30 |

`skills/` 在本目录创建后若有新提交，本目录不会自动跟随；需要按用户请求重新快照并更新上表。

## 翻译约定

- **正文**：Markdown 叙述性内容译为中文。
- **领域术语**：保留英文，如 issue、ADR、PRD、Current、skill、frontmatter、policy。
- **通用技术词**：使用中文表达。
- **代码与命令**：代码块、行内代码、命令、路径、文件名、标识符保持原样。
- **frontmatter**：键名不变；`name` 不变；`description` 等接口值翻译为中文。
- **YAML 接口**：`agents/openai.yaml` 的 `interface` 值翻译为中文；`policy` 保持不变。
- **逐字节复制**：以下文件必须与英文源逐字节一致，不翻译：
  - `project-docs-workflow/references/deps/**`
  - `project-docs-workflow/assets/**`
  - `docs-html-view/scripts/**`
  - `docs-html-view/assets/**`
  - `docs-html-view/requirements.txt`
  - `docs-docx-view/scripts/**`
  - `docs-docx-view/assets/**`
  - `docs-docx-view/requirements.txt`

## 范围与映射

本镜像包含六个第一方 skill，目录名和 `name` 均与英文版相同：

| Skill | 目录 | frontmatter `name` |
| --- | --- | --- |
| project-docs-workflow | `project-docs-workflow/` | `project-docs-workflow` |
| doc-opt | `doc-opt/` | `doc-opt` |
| docs-html-view | `docs-html-view/` | `docs-html-view` |
| docs-docx-view | `docs-docx-view/` | `docs-docx-view` |
| lite-task | `lite-task/` | `lite-task` |
| repo-read-assistant | `repo-read-assistant/` | `repo-read-assistant` |

## 更新清单

1. 从 `skills/` 复制完整目录树到 `skills_zh/`。
2. 翻译有变化的英文 Markdown 正文与 YAML 接口值；`name`、frontmatter 键、`policy` 保持不变。
3. 保持逐字节复制清单中的文件与英文源完全一致。
4. 运行 `npm run check`（或分别运行 `node scripts/check-skills-zh.js`、`node scripts/check-docs-contract.js`），修复报告中的问题；两项校验都只读，不会自动修改文件。
5. 更新本文档中的源基线提交和日期。

## 复核策略

- 六个 skill 的 `SKILL.md` 与本文档 `README.md` 做完整复核。
- `references/**` 等其余 Markdown（包括 `EXAMPLES.md`）做抽样复核。
- 逐字节复制的文件与产物契约由 `scripts/check-skills-zh.js`、`scripts/check-docs-contract.js` 做机械校验，避免人工遗漏。

## 许可证与归属

本仓库及其中文镜像采用 MIT 许可证，许可证文本见根目录 `LICENSE`。中文镜像源自 `skills/`，不改变原有许可证与归属；上游依赖的署名与归属信息保留在根目录 `NOTICE` 及相关依赖文档中。
