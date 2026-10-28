# 文档 DOCX 渲染 Skill

> 完成: 2026-10-28 ｜ 责任: agent ｜ 创建: 2026-10-28 ｜ 关联: [文档HTML渲染Skill](./文档HTML渲染Skill-done.md)

## 背景与目标

现有 `docs-html-view` 已能把 `docs/toc.yml` 发布为多页 HTML，但部分读者与对外分发场景需要**单个 Word 文档**。目标：新增第一方 skill `docs-docx-view`，从同一份 `docs/toc.yml` 手动导出单个 `.docx`（封面 + 三个核心 PRD 章节 + 各模块 PRD + 术语表 / SPEC / Current / ADR 附录），并随包分发中英文镜像。

## 范围

- 输入与 `docs-html-view` 相同的 `docs/toc.yml` 及允许的源文档根：`docs/product`、`docs/current`、`docs/adr`、根目录 `CONTEXT.md`。
- 输出单个 Word 文档：工作区 `<项目根>/docs/docsDocxView/`，产物默认 `build/prd-<版本>.docx`。
- 第一方手动调用：安装时只分发，不运行；不参与项目初始化，也不参与 `check`。
- 不在本条目内：发布 / 推送 / 上架。

## 方案（已批准）

- **单一 docx**：只产出一个 Word 文档，没有 profile、全站构建或多页站点；`docs/toc.yml` 仍是唯一发布源。
- **渲染依赖**：`requirements.txt` 固定 `pypandoc_binary==1.17`（内置 pandoc 3.9）与 `PyYAML==6.0.2`；Python >= 3.12，由 `prepare_env.py` 校验；不做系统级安装。
- **模板**：提交固定的 `assets/reference.docx`，并由维护脚本 `scripts/make_reference.py` 从 pandoc 3.9 默认参考文档确定性生成（字体、Heading 1–4、Title/Subtitle/Author/Abstract、TOC Heading、页眉 / 页脚、`updateFields`、单一 `sectPr` 等）。
- **生成器**：`scripts/gen_docx.py` 校验 TOC、展开模块 PRD、剥离模板来源标记、拦截不安全构造、改写标题 / 锚点 / 图片路径，生成 `combined.md`、`_meta.json`、`_manifest.json`，并仅在缺失时预置 `reference.docx`、`build.sh`、`build.bat`；自身不运行 pandoc、不建 `build/`。
- **标题映射**：顶层 TOC 章节 → Heading 1，附录子章节 → Heading 2；文档首个 H1 与章节标题相同则丢弃（`CONTEXT.md` 的 H1 始终丢弃），否则作为更低一级标题保留；源码 Hn 按规则降级，H6 封顶并告警；每个标题写入显式 `{#sec-<n>}` 锚点；除首个顶层章节外，每个 Heading 1 前分页。
- **安全边界（失败退出 1）**：拒绝符号链接 / 越界路径、MyST/Sphinx include/raw 与 rST include/raw 指令、远程图片（替换为 `[图片：<alt>]` 占位并告警、绝不联网）、绝对路径 / `file:` 图片；本地图片必须位于允许根内且无符号链接；输出预检拒绝无标记 / 无 `generated_by` 的既有工作区文件。
- **构建辅助**：`build.sh` / `build.bat` 只做构建（`--clean` 清理、读取 `_meta.json` 输出路径、调用 pandoc、记录 `build/pandoc.log`），预置后归用户所有且绝不覆盖；不生成、不校验、不安装、不部署。
- **检查**：`scripts/check_docx.py` 分阶段校验源时效（重建 `combined.md` 与磁盘逐字节一致）、PRD 源链接纪律、`.docx` 结构（TOC 域、`updateFields`、标题顺序 / 唯一性、无模板来源残留）；`--skip-docx` 可跳过 DOCX 阶段；警告不失败。
- **分发接入**：`bin/install.js` 第一方清单（kind `docs-docx-view`）、`package.json` 版本 **5.3.0**、`README.md` 中英文说明、`skills_zh/README.md` 镜像清单；`check-skills-zh.js` 将 `docs-docx-view/scripts/`、`docs-docx-view/assets/` 纳入逐字节复制范围。
- **镜像**：英文源为事实来源，`skills_zh/docs-docx-view/` 为人工审校的中文镜像，目录名与 `name` 一致。
- **不做**：不发布、不推送、不创建 git tag、不执行 `npm publish`。

实现期与批准的方案有一处机制偏差（目标不变）：`combined.md` 的 YAML **不写 `lang: zh-CN`**，摘要改为 `::: {custom-style="Abstract"}` 正文段落。原因是 pandoc 3.9 缺少 `translations/zh.yaml`，写 `lang` 会让每次构建产生 4 行无害但嘈杂的警告；不写 `lang` 时 pandoc 又会插入英文 “Abstract” 标签。CJK 校对语言由 `reference.docx` 的 docDefaults（`w:lang w:val="en-US" w:eastAsia="zh-CN"`）提供，`_meta.json` 仍记录 `"lang": "zh-CN"`，构建日志因此保持为空、clean 状态可用。

## 完成判据

- [x] `skills/docs-docx-view/` 含 `SKILL.md`、`scripts/gen_docx.py`、`scripts/prepare_env.py`、`scripts/check_docx.py`、`scripts/make_reference.py`、`requirements.txt`、`assets/reference.docx`、`assets/build.sh`、`assets/build.bat`。
- [x] 生成器、检查器、构建辅助与环境准备脚本按契约行为实现，`python3 -m py_compile` 全部通过，`sh -n assets/build.sh` 通过。
- [x] `skills_zh/docs-docx-view/` 提供对应中文镜像（含逐字节复制的 scripts / assets / requirements），`node scripts/check-skills-zh.js` 通过。
- [x] 分发元数据与文档一致：五个第一方 skill、版本 5.3.0、安装器 dry-run 计划 kind `docs-docx-view`。
- [x] `npm pack --dry-run --ignore-scripts --json` 列出 `skills/` 与 `skills_zh/` 各 5 个 `SKILL.md`，并列出两份 `reference.docx`。
- [x] 未发布、未推送、未提交。

## 步骤

- [x] 规划（完成判据与方案已对齐，契约于 2026-10-28 批准）
- [x] 骨架（gen 核心脚本、requirements、构建辅助与 `reference.docx`）
- [x] 细节（`check_docx.py`、`SKILL.md`、references / agents、中文镜像文档）
- [x] 分发接入（`bin/install.js`、`scripts/check-skills-zh.js`、`package.json`、`README.md`、`skills_zh/README.md`）
- [x] 验证（见「结果」）
- [x] 回顾（文档同步与一致性检查）

## 结果

交付（英文 `skills/`，中文镜像 `skills_zh/`）：

| 文件 | 说明 |
| :--- | :--- |
| `SKILL.md` | 发布模型、边界、8 步流程、安全模型、六种状态、限制 |
| `references/technical.md` | 固定依赖、目录布局、命令、TOC schema、`combined.md` / `_meta.json` / `_manifest.json`、标题与锚点映射、图片 / 链接 / 安全规则、`reference.docx` 与 `make_reference.py`、检查阶段 |
| `agents/openai.yaml` | `allow_implicit_invocation: false` |
| `scripts/gen_docx.py` | TOC 校验与展开、标题 / 锚点 / 图片改写、`combined.md` 生成、工作区预检与预置 |
| `scripts/check_docx.py` | 源时效 + PRD 内链纪律 + docx 结构校验 |
| `scripts/prepare_env.py` | 与 `docs-html-view` 同实现，仅 docstring 改名 |
| `scripts/make_reference.py` | 从 pandoc 默认参考文档确定性生成 `assets/reference.docx`（维护期手动运行） |
| `assets/reference.docx` | 12,336 字节，18 个部件；样式 / 页眉 / 页脚 / `updateFields` / A4 单节 |
| `assets/build.sh` / `build.bat` | 只构建的薄封装，预置后归用户所有 |
| `requirements.txt` | `pypandoc_binary==1.17`、`PyYAML==6.0.2` |

验证证据（fixture 位于 `/tmp/opencode/docs-docx-final-verify`，临时 venv 内 pandoc 3.9，仓库 / 用户 / 系统环境零残留）：

- 生成：8 篇文档（核心三章 + 模块 PRD + 四组附录），两次运行 `combined.md` / `_meta.json` / `_manifest.json` 逐字节一致且幂等；构建辅助仅在缺失时预置（`build.sh` 0755），修改后重跑不被覆盖。
- 构建：`build.sh` 退出 0，`build/pandoc.log` 为 **0 行**；产物 13,903 字节。
- 检查：`check_docx.py` 退出 0（8 篇文档、manifest 8、PRD 文件 4、链接 4、预期标题 8、docx 检查 21、violations 0）。
- DOCX 断言：`TOC \o "1-3"` 域存在；`updateFields` 存在；`header1.xml` 含 `DOCPROPERTY "title"`、`footer1.xml` 含 `PAGE` / `NUMPAGES`；`dc:title` 为 TOC 标题；封面为 `Title` / `Subtitle` / `Author` / `Abstract` 且顺序正确；标题层级与 TOC 顺序一致；5 处分页；本地图片嵌入 `word/media/`；远程图片变为 `[图片：远程示意图]`；无 `模板来源`、无远程 URL；CJK 字体 eastAsia 宋体 / 黑体生效。
- 失败路径：陈旧 `combined.md` → 退出 1 并给出行号；`{include}` → 退出 1 并给出 `file:line`；缺失 `docs/` → 退出 1；PRD 外链 / 状态标记 → 退出 1。
- 仓库检查：`python3 -m py_compile` 全部通过；`sh -n` 通过；`node --check bin/install.js` 通过；`node scripts/check-skills-zh.js` 全项 PASS；`npm pack --dry-run` 列出 5 + 5 个 `SKILL.md` 与两份 `reference.docx`；安装器 dry-run 计划五个第一方 skill（含 `docs-docx-view`）；`git status` 无 `__pycache__` 等杂散产物。

残余风险（已写入 SKILL.md 的 Limitations）：验证环境没有 Word / LibreOffice，目录域的实际填充、分页与字体观感需在真实 Word 中人工确认；超宽表格可能溢出；Mermaid 不渲染；`.rst` 按 Markdown 处理。`--skip-docx` 的源侧检查不含 docx 结构。PRD 层文档中的图片链接会像 `docs-html-view` 的 `check_prd.py` 一样被内链规则拒绝（图片应放在 SPEC / Current / ADR）。

## Log

- 2026-10-28 契约批准：新增第一方 skill `docs-docx-view`，单一 docx 导出；pandoc 3.9（`pypandoc_binary==1.17`）+ 固定 `reference.docx`；中英文镜像；版本 5.3.0；不发布、不推送。
- 2026-10-28 完成分发接入（安装器第一方清单、中文镜像校验范围、包版本 / 描述、中英文 README、`skills_zh/README.md`）。
- 2026-10-28 完成实现与验证；摘要改为 `Abstract` 自定义样式段落、`combined.md` 不写 `lang` 键，以保持 pandoc 日志为空与中文封面无英文标签。
