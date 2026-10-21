---
name: docs-html-view
description: 在只读检查与明确批准后，依据 docs/toc.yml 使用 Sphinx + MyST（原版 RTD 主题）将项目 PRD 发布为本地多页 HTML 站点，含核心 PRD 章节以及术语表、SPEC、Current、ADR 附录。
disable-model-invocation: true
argument-hint: "[项目根目录]"
---

# 文档 HTML 渲染

使用**标准 Sphinx** 配合 MyST（`myst_parser`）和**原版** `sphinx_rtd_theme`，依据 `docs/toc.yml` 构建一份可发布的**多页 PRD**。产物包括封面、三个核心 PRD 章节、模块 PRD，以及四组附录（术语表、SPEC、Current、ADR）。这里没有自研渲染器：脚手架使用 `sphinx-quickstart`，`scripts/gen_prd.py` 依据 TOC 生成封面与章节导航页，构建则使用 `make html`（或直接调用 `sphinx-build`）。产物是一个本地文件夹，可压缩后交给读者；不提供服务，不部署，也不自动发布。

本 skill 仅手动触发，绝不自动运行，且构建期间绝不抓取任何内容。它可以安装固定版本的渲染依赖，但只在你明确批准之后。先进行只读检查，**只询问一次**批准，之后首次初始化与重复手动渲染都不再询问——直到某项设置或 TOC 发生变化。

## 发布模型

`docs/toc.yml` 是**唯一事实来源**。它定义标题、版本、日期、摘要，以及要发布的准确文档：

| 部分 | 来源 | 发布为 |
| :--- | :--- | :--- |
| 封面 | `docs/toc.yml` 元数据 | `docsHtmlView/index.md` |
| 核心章节 | `overview`、`requirements`、`architecture` | `docsHtmlView/nav/<id>/index.md` 导航页 |
| 模块 PRD | `architecture` 下的 `modules: auto` | `docs/product/<NN-module>/00-README.md` |
| 附录 | `glossary`、`spec`、`current`、`adr` | `docsHtmlView/nav/appendix/<id>/index.md` |
| 术语表 | 根 `CONTEXT.md` | 生成的 `docsHtmlView/glossary.md` |

`gen_prd.py` 还会写入 `_manifest.json`（准确的包含清单）与 `_meta.json`（标题/版本/日期/摘要/作者）。`conf.py` 读取这两者：只有清单中的文档才会被构建，因此未列入 TOC 的文档绝不会被渲染。模块附属文件（`00-index.md`）与未列出的 `design/` 文件不会发布。

## 边界

- **仅由用户触发。** 编辑文档期间，绝不安装、初始化脚手架、生成或构建。没有自动构建，也没有监听器。
- **写入范围受限。** 已批准的集合为：`docs/docsHtmlView/`（配置、生成的封面/导航/术语表/清单、构建产物）、经批准的渲染环境目录（例如 `.venv-docs/`），以及你批准的任何 `.gitignore` 新增项。发布会读取 `docs/product`、`docs/current`、`docs/adr`、根 `CONTEXT.md` 与 `docs/toc.yml`；绝不重写源文档。
- **发布范围由 TOC 决定。** 只有 `docs/toc.yml` 中列出的文档会被发布。路径必须落在 `docs/product`、`docs/current`、`docs/adr` 之内，或恰好为 `CONTEXT.md`；符号链接会被拒绝。只有一种发布形态：没有其他视图，也没有单独的落地页配置。
- **没有 TOC 或没有文档 → 停止。** 不要创建 `docs/docsHtmlView/`，不要初始化脚手架，也不要构建。改为报告缺失/无效的 TOC。
- **原版主题。** 不做任何自定义 UI/设计工作。
- **不虚构链接或内容。** 导航由 TOC 生成；绝不改写文档正文。`CONTEXT.md` 会原样复制进生成的术语表。
- **不启动浏览器/服务器，不部署。** 产出 HTML 与 zip 即结束。

## 流程

从项目根目录（`cwd`）运行。定义 skill 目录，并在批准后一次性定义准备就绪环境的绝对路径——`DOCS_PY` 是 venv 的 **python**，`DOCS_SPHINXBUILD` 是 venv 的 **sphinx-build**：

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="TOC TITLE"                                # title read from docs/toc.yml
DOCS_PY="$PWD/.venv-docs/bin/python"                 # or the project's existing docs env
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # same env
```

1. **检查（只读）。** 使用常规只读工具（`ls`、`read`、`grep`）了解项目：`docs/toc.yml` 是否存在并列出必需章节，`docs/product`、`docs/current`、`docs/adr` 与 `CONTEXT.md` 中哪些存在，`docs/docsHtmlView/` 是否已存在，存在哪个 Python/venv，以及 TOC 的标题/版本。**在批准之前，绝不执行项目的解释器或 `conf.py`。** 如果没有可用的 TOC，就此停止——没有可发布的内容。报告计划：固定版本、环境路径、创建的文件、`.gitignore` 新增项、输出路径与标题。

2. **只询问一次。** 在**任何写入、安装或脚手架操作之前**取得明确批准。具体涵盖：包/固定版本（`requirements.txt`，包含用于解析 TOC 的 PyYAML）、环境位置、pip 命令、创建的文件、你提议的 `.gitignore` 新增项（例如 `.venv-docs/`、`docs/docsHtmlView/build/`）、构建/输出路径（`docs/docsHtmlView/build/html`），以及将出现在封面上的 TOC 标题/版本。
   - 在已批准范围内，重复手动渲染**不会**再次询问。
   - 依赖升级、覆盖已有文件，或更改 TOC 范围（新根目录、新文档）**确实**需要重新询问。

3. **准备环境（仅在批准后）。** 优先使用项目已有的文档环境；否则使用项目根目录下的 `.venv-docs`。不做全局/系统安装，不自动安装 `uv`/Python。若不存在合适的 Python，停止并告知用户。在安装 PyYAML 之前，该辅助脚本仅使用标准库，因此可用任意可用的 Python 运行；随后将 `DOCS_PY`/`DOCS_SPHINXBUILD` 指向它准备好的环境：

   ```bash
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
   ```

   该辅助脚本只创建/复用可识别的 venv（含 `pyvenv.cfg` 的目录；它会拒绝覆盖非 venv 目录），并且仅在传入 `--install` 时（在你批准后）安装固定版本的依赖。它绝不会在普通文档编辑时运行，分发该 skill 包也不会安装任何东西。

4. **首次初始化（已批准，仅在 `docs/docsHtmlView/` 不存在时）。** TOC 与源文档已存在，因此只创建工作区目录——在检查与你批准**之后**：

   ```bash
   mkdir -p docs/docsHtmlView
   ( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
   ```

   然后，**仅针对新生成的配置**：
   - 使用 `assets/conf.py.template` 替换生成的 `conf.py`。该模板中的 `__SITE_TITLE__` / `__AUTHOR__` / `__RELEASE__` 是**不带引号**的，因此对每个 token 使用 `template_text.replace(token, repr(value))`。绝不要将原始用户文本未经转义地插入可执行的配置源码。这些 token 只是回退值：构建时由生成的 `_meta.json` 提供真实标题、作者与版本；
   - 将 `assets/guard.py` 复制到 `docs/docsHtmlView/guard.py`；
   - 删除 quickstart 生成的 `index.rst`（封面是生成的 `index.md`）；
   - 编辑生成的 `Makefile`：设置 `SOURCEDIR = ..` 和 `BUILDDIR = build`（替换生成的 `SOURCEDIR = .` / `BUILDDIR = _build`），并将生成的 `SPHINXOPTS    ?=` 行改为 `SPHINXOPTS = -c . -w build/warnings.log`，或在 `make` 命令行上传入（见下文）。可选地删除已不再使用的生成目录 `_build/`。（`make.bat` 可按同样方式编辑；在 Linux/macOS 上并非必需。）

   如果 `docs/docsHtmlView/` 已存在，**不要覆盖**：给出明确的手动合并计划，由用户自行应用。重新运行初始化绝不会重新生成脚手架。

5. **生成发布内容（每次构建前）。** 该辅助脚本校验 `docs/toc.yml`、展开 glob 与 `modules: auto`，并只写入工作区内带标记的文件。它在 TOC 无效/不安全或输出冲突时以非零码退出，且绝不运行 Sphinx：

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_prd.py --project-root .
   ```

   它会写入封面、`nav/**` 导航页、`glossary.md`、`_manifest.json` 与 `_meta.json`，并清理自己标记的过期文件。它绝不编辑 `docs/toc.yml` 或源文档；要改变发布内容，请编辑 TOC 并重新运行。`--json` 会打印机器可读的摘要。

6. **构建（可重复执行，无需重新批准）。**

   ```bash
   mkdir -p docs/docsHtmlView/build
   ( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
   ```

   如果 `make` 不可用，则显式使用相同路径：

   ```bash
   mkdir -p docs/docsHtmlView/build
   ( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
   ```

   输出位于 `docs/docsHtmlView/build/html` 下；由于 `root_doc = docsHtmlView/index`，**封面为 `docs/docsHtmlView/build/html/docsHtmlView/index.html`**（打开该文件）。`build/html/` 的目录布局本身不变——不生成重定向或额外的索引页。警告写入 `docs/docsHtmlView/build/warnings.log`。`build/` 目录仅在批准后创建。源文档的编辑与 TOC 的编辑都属于合法的重建（TOC 变更后需先重新运行 `gen_prd.py`）。更改已批准的设置（环境、工作区、输出根目录）需要重新询问。

7. **检查，然后压缩（可选交付物）。**

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/check_prd.py --project-root .
   python3 -c "import shutil; shutil.make_archive('docs/docsHtmlView/build/prd-docs', 'zip', 'docs/docsHtmlView/build/html')"
   ```

   `check_prd.py` 会校验 TOC、清单、PRD 源链接规则、术语表新鲜度、构建后 HTML 锚点，以及没有未列出的 `product/`/`current/`/`adr/` 页面被构建。`--skip-html` 只运行源码侧检查。zip 写在已批准工作区内的 `docs/docsHtmlView/build/prd-docs.zip`，包含整个文件夹，因此接收方打开压缩包内的 `docsHtmlView/index.html` 即可，无需服务器。仅在构建与检查都成功后才重新压缩。

8. **报告。** 概述标准 Sphinx 的结果与检查结果——见下文的状态。

## 安全模型

边界是一个很小的模板 Sphinx 扩展（`assets/guard.py`），而不是构建编排器。它是针对**可信**项目文档的尽力而为防护，不是通用沙箱；项目自身的 `conf.py` 仍是可执行的 Python。

- **解析阶段阻止文件插入：** `include`、`literalinclude` 和 `raw` 指令会被替换为拒绝执行的指令（不区分大小写，因此 `INCLUDE` 也会被拦截；通过 `eval-rst` 和 MyST 冒号围栏同样可达）。活动/原始 HTML 会被拒绝；只允许纯 HTML 注释（加空白）的 raw 节点，因此 PRD 模板中的无害 `<!-- ... -->` 注释可以正常渲染——但不允许注释+标记的夹带。不依赖仅正则的扫描。
- **本地资源在复制前检查：** 在 `doctree-read` 阶段（优先级 100，早于 Sphinx 的资源收集器复制任何内容），每个已解析的图片与下载目标都会由环境的引用解析器解析，且必须解析到已批准根目录内部（含符号链接），否则构建失败。引用式图片、`:download:` 和大写指令都在覆盖范围内。
- **远程资源绝不抓取：** 远程图片/下载会被替换为内联占位符并发出 Sphinx 警告，因此干净构建不会被报告为完全保真。
- **导航是生成的，不是手写的：** `gen_prd.py` 只写入带标记的文件（`% docs-html-view: generated navigation; do not edit`，一个渲染后无内容的 MyST 注释）以及带 `"generated_by": "docs-html-view gen_prd.py"` 的 JSON 文件。它对生成的标题做净化（不含 `<`、`>`、反引号、花括号、方括号、竖线或换行），并执行完整预检——在首次写入前检查输出目录、任何已有的 `nav/` 以及每个输出/冲突的符号链接与未标记文件，因此拒绝时文档树保持不变。它只清理自己标记的过期文件，绝不写入源文档树。
- **准确的包含清单：** `conf.py` 由 `_manifest.json` 加上生成的封面/导航页/术语表构造 `include_patterns`。即使在根目录下存在，未列出的文档也会被排除。

已批准范围内链接到未列出文档的情况会产生普通的 Sphinx「缺少引用」警告；这些会被报告，绝不自动添加。`check_prd.py` 会捕获源文档中的 PRD 层链接违规。

## 状态

读取标准 Sphinx 退出码、警告日志（`build/warnings.log`）与检查结果：

- **干净成功** — `gen_prd.py` 已生成、构建退出码为 0、警告日志为空，且 `check_prd.py` 退出码为 0。
- **带警告的预览** — 构建退出码为 0 但警告日志有内容；报告首批警告与日志路径。警告本身不会让 `check_prd.py` 失败。
- **生成被拒绝** — `gen_prd.py` 以 1 退出（`docs/toc.yml` 缺失/无效、路径超出允许根目录、重复文档、符号链接，或未标记的输出冲突）。报告消息，修复 TOC/冲突，不要构建陈旧产物。
- **检查失败** — `check_prd.py` 在 TOC/清单不一致、PRD 外部/SPEC/Current/ADR 链接、状态标记、术语表陈旧、构建后锚点断链，或未列出的构建页面时以 1 退出。概述 `file:line` / `file: #id` 行；不要分发检查失败的构建。
- **失败** — `guard.py` 拒绝了构建，或 Sphinx 以非零码退出。失败的 `make` 可能留下 `build/` 下的陈旧或部分产物；应明确说明，不要将其当作新构建展示。没有发布环节：`make` 留下什么就是什么。

## 限制

- 支持的源文档为 `docs/product`、`docs/current`、`docs/adr` 下的 `.md` 与 `.rst`，以及根 `CONTEXT.md`。`.mdx` 及其他扩展名不会渲染。
- `docs/toc.yml` 必须存在，并列出必需章节（`overview`、`requirements`、`architecture`、`appendix`）与附录 id（`glossary`、`spec`、`current`、`adr`）。缺失路径、符号链接、重复项以及超出允许根目录的路径会被拒绝，而不是静默跳过。
- 模块附属文件（`00-index.md`）与 `design/` 文件不会发布，除非 TOC 明确列出；默认 TOC glob 不会列出它们。
- 术语表由 `CONTEXT.md` 原样生成；请保持纯文本。`CONTEXT.md` 中的相对图片会解析到 `docsHtmlView/` 内（超出已批准根目录）并导致构建失败。
- `include` / `literalinclude` / `raw` 会被拒绝；这不是任意 Markdown 渲染器。
- 远程图片/下载会变为内联占位符并附加 Sphinx 警告；活动 HTML 会被拒绝，因此对于任意标记并不声称「无浏览器网络」。
- 该防护是可信文档的护栏，不是针对不可信输入的沙箱。
- 依赖辅助脚本只安装固定版本的依赖，只在带 `--install` 时，且只在同意之后；它绝不安装 Python 或 uv。
- 不做自定义主题、浏览器、服务器或部署。

有关确切的命令、TOC schema、生成产物、配置键与校验规则，见 `references/technical.md`。
