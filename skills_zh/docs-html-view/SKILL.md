---
name: docs-html-view
description: 在只读检查与明确批准后，使用 Sphinx + MyST（原版 RTD 主题）将项目的 PRD / Current / ADR 文档及 L1 视图渲染为本地 HTML。
disable-model-invocation: true
argument-hint: "[项目根目录]"
---

# 文档 HTML 渲染

使用**标准 Sphinx** 配合 MyST（`myst_parser`）和**原版** `sphinx_rtd_theme`，将项目面向人阅读的文档树（`docs/prd`、`docs/current`、`docs/adr`）渲染为本地 HTML 站点。它还支持 PRD 的 **L1 层**（产品 `docs/prd/00-README.md` + 各模块 `00-README.md`）：在完整站点中提供醒目的 L1 入口，以及可打包为 zip 分发的可选 L1 专属视图。这里没有自研渲染器：脚手架使用 `sphinx-quickstart`，导航由一个很小的生成 toctree 的辅助脚本完成，构建则使用 `make html`（或直接调用 `sphinx-build`）。产物是一个本地文件夹，由你自己打开；不提供服务，也不部署。

本 skill 仅手动触发，绝不自动运行，且构建期间绝不抓取任何内容。它可以安装固定版本的渲染依赖，但只在你明确批准之后。先进行只读检查，**只询问一次**批准，之后首次初始化与重复手动渲染都不再询问——直到某项设置发生变化。

## 边界

- **仅由用户触发。** 编辑文档期间，绝不安装、初始化脚手架或构建。
- **写入范围受限。** 已批准的集合为：`docs/docsHtmlView/`（配置、包括 `l1/` 的生成导航、构建产物）、经批准的渲染环境目录（例如 `.venv-docs/`），以及你批准的任何 `.gitignore` 新增项。渲染会读取 `docs/prd`、`docs/current`、`docs/adr`，绝不重写它们，也绝不写入源文档树。
- **仅限已批准的树。** 默认树为 `prd`、`current`、`adr`；可以在配置文件中显式扩展某棵树，但绝不自动扩展。`docs/issues`、`docs/agents`、工具链与构建产物均被排除。缺失或为空的树只报告，不创建。重命名前的 `docs/pdr/` 树会由 `gen_nav.py` 报告，绝不会被移动；除非将 `pdr` 显式加入 `allowed_dirs`，否则不会渲染。已批准的树中没有任何文档 → **停止：不要创建 `docs/docsHtmlView/`，不要初始化脚手架，不要构建。**
- **原版主题。** 不做任何自定义 UI/设计工作。
- **不虚构链接。** 导航由真实文档树生成；不添加跨树关联，也不改写任何文档正文。
- **不启动浏览器/服务器，不部署。** 产出 HTML 即结束。仅限 README/本地产物。

## L1 视图

PRD 的 L1 层是产品 `docs/prd/00-README.md` 加上每个模块的 `docs/prd/<NN-module>/00-README.md`。提供两种视图；两者都是手动的，并复用已批准的工作区。

- **带醒目 L1 入口的完整站点。** 在 `docs/docsHtmlView/docs-html-view.config.json` 中设置 `landing_page`（例如 `prd/00-README.md`）。`gen_nav.py --profile full`（默认）会在 `docsHtmlView/index.md` 的 toctree 之前插入 `## <label>` 和指向 L1 页面的链接。`landing_page_label` 可覆盖标签；否则使用目标的 H1。`00-index.md` 在生成的树中仍是次级的模块导航。
- **L1 专属 profile。** `gen_nav.py --profile l1` 写入 `docsHtmlView/l1/index.md`，其中只含 L1 文件的 toctree：默认先是产品 L1（可用 `navigation_order` 覆盖顺序），然后是模块 L1。L2（`01-spec` 等）、Current、ADR 以及 `00-index.md` 均不包含。构建时使用 `DOCS_HTML_VIEW_PROFILE=l1`，输出到 `docs/docsHtmlView/build-l1/html`。
- **分发。** 将构建出的 L1 **文件夹**压缩为 zip（不是单文件 HTML），并写在已批准的工作区内，例如 `docs/docsHtmlView/build-l1/l1-docs.zip`；接收方打开压缩包内的 `docsHtmlView/l1/index.html`。文档变更后重新构建并重新压缩；不做任何发布。
- **锚点。** 使用标准 Markdown 标题链接（`[text](#heading)`），目标限定为 h1–h3（`myst_heading_anchors = 3`）。`scripts/check_l1.py` 会强制 L1 源链接规则（仅允许内部锚点与指向另一个 `00-README.md` 的链接），并检查构建后 HTML 的锚点。完整站点不受 `check_l1.py` 门禁；L1 专属构建 / 检查才是可强制的路径，断链锚点会使它失败。遇到中文标题 slug 不匹配时，优先调整标题，再回退到显式的 MyST target。

L1 profile 需要产品 L1 `docs/prd/00-README.md`：该文件缺失时 `gen_nav.py --profile l1` 以退出码 1 结束（即使存在模块 L1 文件），缺少该文件时 Sphinx 也会自然失败。L1 构建始终位于已批准的工作区/产物范围内，绝不重写源文档；它不会自动运行，仅在用户要求 L1 交付物时执行。

## 流程

从项目根目录（`cwd`）运行。定义 skill 目录，并在批准后一次性定义准备就绪环境的绝对路径——`DOCS_PY` 是 venv 的 **python**，`DOCS_SPHINXBUILD` 是 venv 的 **sphinx-build**：

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="APPROVED TITLE"                           # the confirmed project/site title
DOCS_PY="$PWD/.venv-docs/bin/python"                 # or the project's existing docs env
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # same env
```

1. **检查（只读）。** 使用常规只读工具（`ls`、`read`、`grep`）了解项目：`docs/prd`、`docs/current`、`docs/adr` 中哪些存在且包含文档，`docs/docsHtmlView/` 是否已存在，存在哪个 Python/venv，以及真实的项目/站点标题。**在批准之前，绝不执行项目的解释器或 `conf.py`。** 如果没有任何已批准的树包含文档，就此停止——没有可渲染的内容。报告计划：固定版本、环境路径、创建的文件、`.gitignore` 新增项、输出路径与标题。

2. **只询问一次。** 在**任何写入、安装或脚手架操作之前**取得明确批准。具体涵盖：包/固定版本（`requirements.txt`）、环境位置、pip 命令、创建的文件、你提议的 `.gitignore` 新增项（例如 `.venv-docs/`、`docs/docsHtmlView/build/`）、构建/输出路径（`docs/docsHtmlView/build/html`），以及确认的站点标题——`docsHtmlView` 是目录名，不是站点名。
   - 在已批准范围内，重复手动渲染**不会**再次询问。
   - 依赖升级、覆盖已有文件，或更改已批准的根目录/范围，**确实**需要重新询问。

3. **准备环境（仅在批准后）。** 优先使用项目已有的文档环境；否则使用项目根目录下的 `.venv-docs`。不做全局/系统安装，不自动安装 `uv`/Python。若不存在合适的 Python，停止并告知用户。该辅助脚本仅使用标准库，因此可用任意可用的 Python 运行；随后将 `DOCS_PY`/`DOCS_SPHINXBUILD` 指向它准备好的环境：

   ```bash
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
   ```

   该辅助脚本只创建/复用可识别的 venv（含 `pyvenv.cfg` 的目录；它会拒绝覆盖非 venv 目录），并且仅在传入 `--install` 时（在你批准后）安装固定版本的依赖。它绝不会在普通文档编辑时运行，分发该 skill 包也不会安装任何东西。

4. **首次初始化（已批准，仅在 `docs/docsHtmlView/` 不存在时）。** 已批准的树已存在，因此只创建工作区目录——在检查确认文档存在且你已批准**之后**：

   ```bash
   mkdir -p docs/docsHtmlView
   ( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
   ```

   然后，**仅针对新生成的配置**：
    - 使用 `assets/conf.py.template` 替换生成的 `conf.py`；该模板中的 `__SITE_TITLE__` / `__AUTHOR__` / `__RELEASE__` 是**不带引号**的，因此对每个 token 使用 `template_text.replace(token, repr(value))`。绝不要将原始用户文本未经转义地插入可执行的配置源码；
    - 将 `assets/guard.py` 复制到 `docs/docsHtmlView/guard.py`；
    - 删除 quickstart 生成的 `index.rst`（落地页是生成的 `index.md`）；
    - 编辑生成的 `Makefile`：设置 `SOURCEDIR = ..` 和 `BUILDDIR = build`（替换生成的 `SOURCEDIR = .` / `BUILDDIR = _build`），并将生成的 `SPHINXOPTS    ?=` 行改为 `SPHINXOPTS = -c . -w build/warnings.log`，或在 `make` 命令行上传入（见下文）。可选地删除已不再使用的生成目录 `_build/`。（`make.bat` 可按同样方式编辑；在 Linux/macOS 上并非必需。）

   如果 `docs/docsHtmlView/` 已存在，**不要覆盖**：给出明确的手动合并计划，由用户自行应用。重新运行初始化绝不会重新生成脚手架。

5. **生成导航（每次构建前）。** 该辅助脚本只写入工作区内带标记的文件，若没有任何已批准的树包含文档则以非零码退出，且绝不运行 Sphinx：

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile full
   ```

   始终传入已批准的标题（或在配置中设置 `site_title`）；否则站点标题会静默回退为 `Documentation`。重复渲染复用同一个商定的 `SITE_TITLE`，不再询问，也不切换标题。`--profile full` 是默认值，保持既有的完整站点产物；L1 专属视图使用 `--profile l1`（第 7 步）。

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

   输出位于 `docs/docsHtmlView/build/html` 下；由于 `root_doc = docsHtmlView/index`，**落地页为 `docs/docsHtmlView/build/html/docsHtmlView/index.html`**（打开该文件）。`build/html/` 的目录布局本身不变——不生成重定向或额外的索引页。警告写入 `docs/docsHtmlView/build/warnings.log`。`build/` 目录仅在批准后创建。源文档的编辑属于合法的重建。更改已批准的设置（根目录、标题、环境）需要重新询问。不要将 `make`/`sphinx-build` 包装进另一个脚本。

   **更改已批准的树属于手动、需批准的编辑。** 若 `allowed_dirs` 发生变化，需手动同步更新以下三处：`docs/docsHtmlView/conf.py` 中的 `include_patterns` 与 `docs_html_view_allowed_roots`，以及 `docs/docsHtmlView/docs-html-view.config.json` 中的 `allowed_dirs`；然后重新运行 `gen_nav`。没有自动同步，且必须在 `make` 之前解决不一致。缺失/为空的树没有问题（报告并跳过）。

7. **L1 专属构建（opt-in，仅在用户要求时）。** 复用同一个已批准环境与标题；它只写入 `docs/docsHtmlView/l1/` 与 `docs/docsHtmlView/build-l1/`：

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile l1
   mkdir -p docs/docsHtmlView/build-l1
   ( cd docs/docsHtmlView && DOCS_HTML_VIEW_PROFILE=l1 "$DOCS_SPHINXBUILD" -b html -c . \
       -d build-l1/doctrees -w build-l1/warnings.log .. build-l1/html )
   "$DOCS_PY" "$SKILL"/scripts/check_l1.py --project-root . --html-dir docs/docsHtmlView/build-l1/html
   python3 -c "import shutil; shutil.make_archive('docs/docsHtmlView/build-l1/l1-docs', 'zip', 'docs/docsHtmlView/build-l1/html')"
   ```

   落地页为 `docs/docsHtmlView/build-l1/html/docsHtmlView/l1/index.html`；警告写入 `docs/docsHtmlView/build-l1/warnings.log`。`--skip-html` 会让 `check_l1.py` 只运行源链接规则。zip 写在已批准工作区内的 `docs/docsHtmlView/build-l1/l1-docs.zip`，包含整个文件夹，因此接收方无需服务器。仅在构建与检查都成功后才重新压缩。

8. **报告。** 概述标准 Sphinx 的结果——见下文的状态。

## 安全模型

边界是一个很小的模板 Sphinx 扩展（`assets/guard.py`），而不是构建编排器。它是针对**可信**项目文档的尽力而为防护，不是通用沙箱；项目自身的 `conf.py` 仍是可执行的 Python。

- **解析阶段阻止文件插入：** `include`、`literalinclude` 和 `raw` 指令会被替换为拒绝执行的指令（不区分大小写，因此 `INCLUDE` 也会被拦截；通过 `eval-rst` 和 MyST 冒号围栏同样可达）。活动/原始 HTML 会被拒绝；只允许纯 HTML 注释（加空白）的 raw 节点，因此 PRD 模板中的无害 `<!-- ... -->` 注释可以正常渲染——但不允许注释+标记的夹带。不依赖仅正则的扫描。
- **本地资源在复制前检查：** 在 `doctree-read` 阶段（优先级 100，早于 Sphinx 的资源收集器复制任何内容），每个已解析的图片与下载目标都会由环境的引用解析器解析，且必须解析到已批准根目录内部（含符号链接），否则构建失败。引用式图片、`:download:` 和大写指令都在覆盖范围内。
- **远程资源绝不抓取：** 远程图片/下载会被替换为内联占位符并发出 Sphinx 警告，因此干净构建不会被报告为完全保真。
- **导航是生成的，不是手写的：** `gen_nav.py` 只写入带标记的文件（`% docs-html-view: generated navigation; do not edit`，一个渲染后无内容的 MyST 注释），对生成的标题做净化（不含 `<`、`>`、反引号、花括号、方括号、竖线或换行），并执行完整预检——检查已批准目录、源文档树以及任何已有的 `nav/`（包括祖先目录）是否存在符号链接，并在首次写入前校验每个输出/冲突，因此拒绝时文档树保持不变。它只删除自己标记的过期导航文件，绝不写入源文档树。L1 产物（`docsHtmlView/l1/`）会接受同样的符号链接、冲突与清理检查。

已批准范围内链接到被排除文档的情况会产生普通的 Sphinx「缺少引用」警告；这些会被报告，绝不自动添加。

## 状态

读取标准 Sphinx 退出码与警告日志（`build/warnings.log`）：

- **干净成功** — 构建退出码为 0 且警告日志为空。
- **带警告的预览** — 构建退出码为 0 但警告日志有内容；报告首批警告与日志路径。
- **失败** — `gen_nav.py` 拒绝执行（或因无文档而退出 1）、`guard.py` 拒绝了构建，或 Sphinx 以非零码退出。失败的 `make` 可能留下 `build/` 下的陈旧或部分产物；应明确说明，不要将其当作新构建展示。没有发布环节：`make` 留下什么就是什么。
- **L1 检查失败** — `check_l1.py` 在 L1 源链接规则违规、构建后锚点断链，或 `build-l1/html` 缺失（先运行 L1 构建，或传入 `--skip-html`）时以 1 退出。概述 `file:line: target` / `file: #id` 行；不要分发检查失败的构建。

## 限制

- 支持的源文档为已批准树下的 `.md` 和 `.rst`；`.mdx` 及其他扩展名不会渲染。
- L1 profile 按文件名识别 `00-README.md`，并假定根目录为 `prd`；其他 L1 根目录需手动编辑 `conf.py`。它需要产品 L1 `docs/prd/00-README.md`：缺失时 `gen_nav.py` 以 1 退出（即使存在模块 L1 文件），应停止。L1 专属产物是文件夹（或其 zip），不是单文件 HTML。
- `include` / `literalinclude` / `raw` 会被拒绝；这不是任意 Markdown 渲染器。
- 远程图片/下载会变为内联占位符并附加 Sphinx 警告；活动 HTML 会被拒绝，因此对于任意标记并不声称「无浏览器网络」。
- 该防护是可信文档的护栏，不是针对不可信输入的沙箱。
- 依赖辅助脚本只安装固定版本的依赖，只在带 `--install` 时，且只在同意之后；它绝不安装 Python 或 uv。

有关确切的命令、模板应用步骤、配置键与导航规则，见 `references/technical.md`。
