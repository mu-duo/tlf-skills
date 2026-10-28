---
name: docs-docx-view
description: 在只读检查与明确批准后，依据 docs/toc.yml 使用 pandoc（自带 3.9）将项目 PRD 发布为单个 Word 文档，含封面、目录、核心 PRD 章节、模块 PRD 以及术语表、SPEC、Current、ADR 附录。
disable-model-invocation: true
argument-hint: "[项目根目录]"
---

# 文档 Word 渲染

使用**标准 pandoc** 配合本 skill 自带的 `reference.docx` 模板，依据 `docs/toc.yml` 构建一份可发布的 **PRD Word 文档**。产物包括封面、目录、三个核心 PRD 章节、模块 PRD，以及四组附录（术语表、SPEC、Current、ADR），按 TOC 顺序合并为单个 `.docx`。这里没有自研渲染器：`scripts/gen_docx.py` 校验 TOC、重映射标题层级、改写锚点、清空远程图片，并写出带标记的 `docs/docsDocxView/combined.md`；随后由预置的 `docs/docsDocxView/build.sh` / `build.bat` 辅助脚本对它运行 pandoc。产物是一个本地 Word 文件；不提供服务，不部署，也不自动发布。

本 skill 仅手动触发，绝不自动运行，且渲染期间绝不抓取任何内容。它可以安装固定版本的渲染依赖，但只在你明确批准之后。先进行只读检查，**只询问一次**批准，之后首次初始化与重复手动构建都不再询问——直到某项设置或 TOC 发生变化。

## 发布模型

`docs/toc.yml` 是**唯一事实来源**。它定义标题、版本、日期、摘要，以及要发布的准确文档：

| 部分 | 来源 | 发布为 |
| :--- | :--- | :--- |
| 封面 | `docs/toc.yml` 元数据 | `combined.md` 顶部的 pandoc 标题块（Title/Subtitle/Author 样式） |
| 目录 | 生成 | 一个手写的 Word 目录域，深度 1–3 |
| 核心章节 | `overview`、`requirements`、`architecture` | 一级标题（Heading 1）章节正文 |
| 模块 PRD | `architecture` 下的 `modules: auto` | 追加到架构章节的文档 |
| 附录 | `glossary`、`spec`、`current`、`adr` | `appendix` 一级标题下的二级标题（Heading 2）章节 |
| 术语表 | 根 `CONTEXT.md` | 丢弃其开头的一级标题；正文置于术语表章节的二级标题下 |

`gen_docx.py` 还会写入 `_manifest.json`（按 TOC 展开顺序排列的准确文档清单）与 `_meta.json`（标题/版本/日期/摘要/作者/语言/输出）。唯一产物是 `docs/docsDocxView/build/prd-<version>.docx`（净化后版本为空时为 `build/prd.docx`），使用 `_meta.json` 中记录的 `output` 路径。只有清单中的文档才会被包含；未列入 TOC 的文档绝不会被渲染。只有一种发布形态，没有其他视图。

## 边界

- **仅由用户触发。** 编辑文档期间，绝不安装、生成或构建。没有自动构建、监听器或 CI 钩子。
- **写入范围受限。** 已批准的集合为：`docs/docsDocxView/`（生成的 `combined.md`、`_meta.json`、`_manifest.json`、预置的 `reference.docx` / `build.sh` / `build.bat`，以及 `build/` 产物）、经批准的渲染环境目录（例如 `.venv-docs/`），以及你批准的任何 `.gitignore` 新增项。发布会读取 `docs/product`、`docs/current`、`docs/adr`、根 `CONTEXT.md` 与 `docs/toc.yml`；绝不重写源文档。
- **预置文件归用户所有。** `gen_docx.py` **仅在缺失时**预置 `docs/docsDocxView/reference.docx`、`build.sh` 与 `build.bat`，绝不覆盖已有文件；预置之后可由你自由编辑。`reference.docx` 控制 Word 样式、页眉与页脚。构建辅助脚本只负责构建：不生成或校验内容，不安装或抓取任何东西，不调用 `gen_docx.py` / `check_docx.py`，不查找 skill 目录，不启动浏览器/服务器，也不部署。
- **发布范围由 TOC 决定。** 只有 `docs/toc.yml` 中列出的文档会被发布。路径必须落在 `docs/product`、`docs/current`、`docs/adr` 之内，或恰好为 `CONTEXT.md`；符号链接会被拒绝，缺失路径会使生成失败。只有一种发布形态：没有其他视图、封面或输出文档。
- **没有 TOC 或没有文档 → 停止。** 不要创建 `docs/docsDocxView/`，不要生成，也不要构建。改为报告缺失/无效的 TOC。
- **生成文件带标记。** `combined.md` 以生成标记开头，JSON 文件带有 `"generated_by"`；生成器拒绝覆盖已存在的未标记/非归属输出，并保持文件树不变。
- **不虚构链接或内容。** 正文除单文档版式所需之外绝不改写（标题层级、锚点 id、本地图片路径、远程图片占位符）。范围由 TOC 提供；`CONTEXT.md` 在其术语表位置被包含，开头的模板来源标记会被剥离。
- **绝不抓取远程内容。** 远程图片会变为字面量 `[图片：<alt>]` / `[图片]` 占位符并附加警告；绝不允许 pandoc 下载任何内容。
- **不启动浏览器/服务器，不部署。** 产出本地 `.docx` 即结束。打包、托管与交付不在本 skill 范围内，由用户自行决定。
- **不是任意渲染器。** `{include}`、`{literalinclude}`、`{raw}`、`{=html}`、`{=openxml}`，以及 rST 的 `.. include::` / `.. literalinclude::` / `.. raw::` 形式都会在生成阶段被拒绝。

## 流程

从项目根目录（`cwd`）运行。定义 skill 目录，并在批准后一次性定义准备就绪环境的 **python** 路径：

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-docx-view}"
DOCS_PY="$PWD/.venv-docs/bin/python"                 # or the project's existing docs env (needs PyYAML)
```

1. **检查（只读）。** 使用常规只读工具（`ls`、`read`、`grep`）了解项目：`docs/toc.yml` 是否存在并列出必需章节，`docs/product`、`docs/current`、`docs/adr` 与 `CONTEXT.md` 中哪些存在，`docs/docsDocxView/` 是否已存在，存在哪个 Python/venv，以及 TOC 的标题/版本。**在批准之前，绝不执行项目的解释器。** 如果没有可用的 TOC，就此停止——没有可发布的内容。报告计划：固定版本、环境路径、创建的文件（包含三个预置工作区文件，仅在缺失时创建）、`.gitignore` 新增项、输出路径与标题。

2. **只询问一次。** 在**任何写入或安装之前**取得明确批准。具体涵盖：包/固定版本（`requirements.txt`：`pypandoc_binary==1.17`，自带 pandoc 3.9；以及用于解析 TOC 的 `PyYAML==6.0.2`；Python >= 3.12）、环境位置、pip 命令、创建的文件（缺失时包含 `reference.docx`、`build.sh`、`build.bat`）、你提议的 `.gitignore` 新增项（例如 `.venv-docs/`、`docs/docsDocxView/build/`）、输出路径（`docs/docsDocxView/build/prd-<version>.docx`），以及将出现在封面上的 TOC 标题/版本。
   - 在已批准范围内，重复手动构建与重新生成**不会**再次询问。
   - 依赖升级、覆盖已有文件，或更改 TOC 范围（新根目录、新文档）**确实**需要重新询问。

3. **准备环境（仅在批准后）。** 优先使用带 PyYAML 的项目已有文档环境；否则使用项目根目录下的 `.venv-docs`。不做全局/系统安装，不自动安装 `uv`/Python。若不存在合适的 Python，停止并告知用户。在安装 PyYAML 之前，该辅助脚本仅使用标准库，因此可用任意可用的 Python 运行；随后将 `DOCS_PY` 指向它准备好的环境：

   ```bash
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
   ```

   该辅助脚本只创建/复用可识别的 venv（含 `pyvenv.cfg` 的目录；它会拒绝覆盖非 venv 目录），强制 Python >= 3.12，并且仅在传入 `--install` 时（在你批准后）安装固定版本的依赖。它绝不会在普通文档编辑时运行，分发该 skill 包也不会安装任何东西。

4. **首次初始化（已批准，仅在 `docs/docsDocxView/` 不存在时）。** 没有独立的脚手架步骤，也没有 `sphinx-quickstart`：第 5 步的生成器会在缺失时创建 `docs/docsDocxView/`，并**仅在文件缺失时**从 skill 的 `assets/` 预置 `reference.docx`、`build.sh` 与 `build.bat`。如果工作区已存在，则不会重新预置或覆盖任何文件；如需替换归用户所有的文件，请给出明确的手动计划，由用户自行应用。

5. **生成发布内容（每次构建前）。** 该生成器校验 `docs/toc.yml`、展开 glob 与 `modules: auto`，并写入工作区内带标记的发布文件。它在 TOC 无效/不安全或输出冲突时以非零码退出，且绝不运行 pandoc：

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_docx.py --project-root .
   ```

   它会写入 `combined.md`（唯一的 pandoc 输入）、`_manifest.json` 与 `_meta.json`，并预置三个缺失的工作区文件。它打印一行摘要与所有警告；`--json` 会在 stdout 打印 `{"documents": [...], "output": "...", "generated": [...], "seeded": {...}, "warnings": [...]}`。它绝不创建 `build/`、绝不运行 pandoc，也绝不编辑 `docs/toc.yml` 或源文档；要改变发布内容，请编辑 TOC 并重新运行。TOC、`CONTEXT.md` 或模块集合变化后，请重新运行它。

6. **构建（可重复执行，无需重新批准）。** 使用预置的辅助脚本，它运行同一次 pandoc 转换：

   ```bash
   ( cd docs/docsDocxView && ./build.sh )          # POSIX
   ```
   ```bat
   docs\docsDocxView\build.bat                     :: Windows (from the project root)
   ```

   `build.sh` 是 POSIX sh，预置时即带可执行位；`build.bat` 是 Windows 批处理。二者都会 `cd` 到自身所在目录。它们优先使用 `DOCS_PY`，否则使用 `../../.venv-docs/bin/python`（Windows 为 `..\..\.venv-docs\Scripts\python.exe`）。`--clean` 会先删除 `build/`；它是唯一的参数（未知或多余参数会打印 `usage: ... [--clean]` 并以 2 退出）。它们要求渲染环境以及 `combined.md`、`_meta.json`、`_manifest.json`、`reference.docx` 存在；否则打印错误，提示先运行 docs-docx-view skill，并且不构建任何内容。它们从 `_meta.json` 读取输出路径，通过 `pypandoc` 解析 pandoc 二进制，随后精确执行：

   ```bash
   "$PANDOC" --from=markdown+raw_attribute --to=docx --reference-doc=reference.docx --resource-path="$(cd ../.. && pwd)" -o "$OUT" combined.md 2> build/pandoc.log
   ```

   它们会打印 pandoc 消息数（`build/pandoc.log`）、输出路径及其大小。文档落在 `docs/docsDocxView/build/prd-<version>.docx`（即 `_meta.json` 中记录的路径）；`build/` 与 `build/pandoc.log` 仅由 `build.sh` 创建。它们**不会**重新生成：如果 `docs/toc.yml`、`CONTEXT.md` 或模块集合发生变化，请先执行第 5 步。源文档的编辑属于合法的重建。更改已批准的设置（环境、工作区、输出路径）需要重新询问。

7. **检查。**

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
   ```

   `check_docx.py` 会在内存中重建预期的 `combined.md`，并要求与磁盘文件逐字节一致；复核清单/元数据一致性与 PRD 源链接规范；然后校验产出的 `.docx`（zip 部件、目录域、`updateFields`、标题、章节标题、无模板来源文本）。`--skip-docx` 只运行源码侧检查（首次构建前有用）；`--docx PATH` 指向非默认文档。警告会被报告，但不会使其失败。

8. **报告。** 概述生成、pandoc 构建与检查结果——见下文的状态。

## 安全模型

边界是生成器加上固定的 pandoc 输入，而不是构建编排器。它是针对**可信**项目文档的尽力而为防护，不是通用沙箱。

- **严格的 TOC 校验：** 必需元数据与章节 id、允许根目录（`docs/product`、`docs/current`、`docs/adr`，或恰好 `CONTEXT.md`）、常规 `.md`/`.rst` 文件、无符号链接路径、无重复文档，缺失路径失败。违规时以 1 退出，且不写入任何内容。
- **禁止的构造会使生成失败：** 在源文本中（包括代码围栏与注释）扫描 `{include}`、`{literalinclude}`、`{raw}`、`{=html}`、`{=openxml}`、`.. include::`、`.. literalinclude::` 与 `.. raw::`，并以 `file:line` 报告；生成器拒绝执行。
- **远程内容绝不抓取：** 远程图片（http/https/协议相对/其他 URL scheme，包括图片使用的引用式定义与 `<img src=...>`）会被替换为字面量 `[图片：<alt>]` 占位符（无 alt 时为 `[图片]`）并附加警告。绝对路径与 `file:` 图片目标会使生成失败。
- **本地图片在使用前检查：** 每个目标都相对其源文档解析，必须是常规文件，其真实路径位于项目根目录**并且**位于 `docs/product`、`docs/current` 或 `docs/adr` 之内，且路径中无符号链接。目标会被改写为项目根目录相对路径；Markdown 图片未给出宽高时还会追加 `{width=16cm}`。
- **模板来源标记在内存中剥离：** 开头的 `模板来源` 标记（引用块或 HTML 注释形态，可连续多个，位于首个标题之前）会从生成副本中移除；磁盘上的源文件绝不修改。
- **生成文件有归属并经过预检：** `combined.md` 带生成标记，JSON 文件带 `"generated_by": "docs-docx-view gen_docx.py"`。已存在的未标记/非归属输出、符号链接工作区，或逃逸工作区的输出，都会让生成器在任何写入前拒绝。
- **一个 TOC，不传 `--toc`：** 封面是 pandoc 自带的标题块，唯一的目录是手写的 Word 域；不会让 pandoc 再生成一个目录。
- **构建辅助脚本是透明封装：** 其中不含任何解析、渲染、生成或校验逻辑。它们只负责 `cd`、检查输入、运行文档中给出的 pandoc 命令并打印结果。它们仅在缺失时预置一次，归用户所有。

## 状态

读取生成器退出码、pandoc 退出码与 `build/pandoc.log`，以及检查结果：

- **干净成功** — `gen_docx.py` 已生成、`build.sh` 退出码为 0、`build/pandoc.log` 为空，且 `check_docx.py` 退出码为 0。
- **带警告的预览** — 构建退出码为 0 但 `build/pandoc.log` 有内容（或生成器打印了警告）。报告首批消息与日志路径。警告本身不会让 `check_docx.py` 失败。
- **生成被拒绝** — `gen_docx.py` 以 1 退出，stderr 为 `refusing: ...`（`docs/toc.yml` 缺失/无效、路径超出允许根目录、重复文档、符号链接、禁止的构造，或未标记的输出冲突）。报告消息，修复 TOC/源文档/冲突，不要构建陈旧产物。
- **检查失败** — `check_docx.py` 以 1 退出（`combined.md` 陈旧、清单/元数据不一致、PRD 链接违规、DOCX 部件缺失/无效、目录域或章节标题缺失，或模板来源泄漏）。概述报告的行；不要把失败的发布当作有效产物。
- **pandoc 构建失败** — `build.sh` 因 pandoc 失败（或预期输出未创建）而以非零码退出。日志为 `build/pandoc.log`；`build/` 可能包含陈旧或部分产物。应明确说明，不要将其当作新构建展示。
- **前置条件失败** — 辅助脚本找不到渲染环境、`combined.md`、`_meta.json`、`_manifest.json` 或 `reference.docx`（或 `DOCS_PY` 中未安装 `pypandoc`）。它会以非零码退出，并提示先运行 docs-docx-view skill；不会构建任何内容。修复前置条件（第 3 或第 5 步）后再重试。

## 限制

- 生成的 `.docx` **不会在本 skill 的验证环境中由 Word 或 LibreOffice 打开**。目录域会一直显示占位符，直到 Word 更新域（模板已设置 `w:updateFields`）；页面版式、字体、分页与表格适配需要在 Word 中人工检查。
- 目录深度固定为 1–3 级标题（`TOC \o "1-3"`）；更深的标题不会列入。
- 深于 H6 的标题会被钳制为 H6，并附加警告；层级可能在此处被压平。
- 宽表格可能溢出页面；pandoc 不会缩小列宽来适配。
- Mermaid 图不会渲染；Mermaid 围栏仍是普通代码块。
- `.rst` 文档会被接受，但按 Markdown 处理（仅识别 ATX 标题）；rST 语法不会被转换。`include` / `literalinclude` / `raw` 会被拒绝，因此这不是任意 MyST 渲染器。
- 没有自定义主题或按项目的设计工作：只有一套 `reference.docx` 样式（Calibri/宋体正文、Calibri Light/黑体标题、A4、页眉/页脚），预置后可由你替换。
- 术语表是根 `CONTEXT.md` 的文本。请保持纯文本；其中若含相对图片，会解析到允许根目录之外并导致失败，远程图片则变为占位符。
- 除已检查的结构（目录域、标题、文档标题、模板来源）外，样式保真度不做校验；视觉差异属预期，需要人工在 Word 中审阅。
- 构建辅助脚本只负责构建：不重新生成、不安装依赖、不校验结果。不存在浏览器、服务器或部署环节。

有关确切的命令、TOC schema、生成产物、标题/锚点映射与校验规则，见 `references/technical.md`。
