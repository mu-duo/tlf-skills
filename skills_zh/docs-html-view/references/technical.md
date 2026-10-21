# docs-html-view 技术参考

## 固定版本依赖

已在 PyPI 验证（2026-10）；该组合相互兼容。Sphinx 9.1.0 要求 Python >= 3.12。

| 包 | 固定版本 | 说明 |
| :--- | :--- | :--- |
| Sphinx | `Sphinx==9.1.0` | 需要 Python >= 3.12 |
| MyST parser | `myst-parser==5.1.0` | Markdown 支持 |
| RTD 主题 | `sphinx-rtd-theme==3.1.0` | 通过 `html_theme` 使用原版主题 |
| PyYAML | `PyYAML==6.0.2` | `gen_prd.py` / `check_prd.py` 读取 `docs/toc.yml` |

`requirements.txt` 提供该声明。`prepare_env.py` 仅在传入 `--install` 时安装；调用方只在批准后运行它。

## 目录布局

```
<项目根目录>/
  .venv-docs/                     # 默认渲染 venv（或项目已有的文档环境）
  CONTEXT.md                      # 术语表来源（只复制，不修改）
  docs/                           # Sphinx 源根目录
    toc.yml                       # 发布唯一事实来源
    product/                      # 核心 PRD + 模块 PRD/SPEC
      00-README.md                # PRD 封面/总览
      01-requirements.md          # PRD 产品需求
      02-architecture.md          # PRD 架构与模块划分
      <NN-module>/
        00-README.md              # 模块 PRD（由 modules: auto 发布）
        00-index.md               # 代理附属文件（未列入 -> 不发布）
        01-spec.md 02-interfaces.md 03-nfr.md
        design/                   # 默认未列出 -> 不发布
    current/                      # as-built 现状快照
    adr/                          # 决策记录
    docsHtmlView/                 # 工作区
      conf.py                     # 来自 assets/conf.py.template
      guard.py                    # 从 assets/guard.py 复制
      index.md                    # 生成的封面（带标记）
      nav/<id>/index.md           # 按需生成的章节落地页（带标记）
      glossary.md                 # 由 CONTEXT.md 生成（带标记）
      _manifest.json              # 生成的准确包含清单
      _meta.json                  # 生成的标题/版本/日期/摘要/作者
      build/html/docsHtmlView/index.html   # 发布封面
      build/html/index.html       # 生成的根入口（跳转到封面）
```

`docsHtmlView` 是工作区目录名，不是发布标题。标题来自 `docs/toc.yml`。

## 本 skill 提供的文件

- `scripts/prepare_env.py` — 创建/复用可识别的 venv；可选安装固定依赖 / freeze。仅标准库。
- `scripts/gen_prd.py` — 校验 `docs/toc.yml`，展开 glob/`modules: auto`，生成封面、按需的章节落地页、术语表与清单；仅写带标记的文件。
- `scripts/check_prd.py` — 校验 TOC、清单、PRD 源链接、术语表新鲜度、构建后锚点与未列出页面。标准库 + PyYAML。
- `assets/conf.py.template` — 新发布使用的受管 `conf.py`。
- `assets/guard.py` — 解析/渲染防护扩展。
- `requirements.txt` — 固定版本。

## 命令

检查使用常规只读工具完成；没有 inspect 子命令，批准前不会运行项目解释器。批准后，从项目根目录定义准备就绪环境的绝对路径（可用 `--venv` 复用项目文档环境）：

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="TOC TITLE"                                # 从 docs/toc.yml 读取的标题
DOCS_PY="$PWD/.venv-docs/bin/python"                 # venv python
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # venv sphinx-build
```

首次初始化（仅新工作区；若 `docs/docsHtmlView/` 已存在则跳过，改为给出手动合并计划）：

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
mkdir -p docs/docsHtmlView
( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
# 应用 assets/conf.py.template -> docs/docsHtmlView/conf.py
#   token 不带引号；用 repr(value) 替换 __SITE_TITLE__/__AUTHOR__/__RELEASE__
# 复制 assets/guard.py -> docs/docsHtmlView/guard.py
# 删除生成的 docs/docsHtmlView/index.rst
# Makefile: SOURCEDIR = ..   BUILDDIR = build   SPHINXOPTS = -c . -w build/warnings.log
"$DOCS_PY" "$SKILL"/scripts/gen_prd.py --project-root .
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
"$DOCS_PY" "$SKILL"/scripts/check_prd.py --project-root .
```

重复渲染（相同已批准范围；每次 TOC 变更后都要重新运行生成器）：

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_prd.py --project-root .
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
"$DOCS_PY" "$SKILL"/scripts/check_prd.py --project-root .
```

没有 `make` 时：

```bash
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
```

`check_prd.py --skip-html` 只运行源码侧检查。本 skill 到本地 `docs/docsHtmlView/build/html` 文件夹为止；打包、托管与交付不在其范围内，由用户自行决定。

`gen_prd.py` 在 TOC 无效或不安全（缺少元数据/id/路径、显式重复文档、符号链接、路径超出允许根目录）、工作区缺失，或未标记输出冲突时以 `1` 退出。成功写入发布内容后以 `0` 退出，并打印生成文件/清单数量；`--json` 在 stdout 打印解析后的文档、清单、生成文件与清理文件。警告（空 glob、无模块、遗留 `docs/prd/`）写入 stderr。

可选的已解析版本快照（已批准产物）：

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsHtmlView/requirements.lock.txt
```

`prepare_env.py` 参数：`--project-root`（默认 cwd）、`--venv`（默认 `.venv-docs`，相对项目根目录，除非为绝对路径）、`--base-python`（用于创建 venv 的解释器）、`--requirements`、`--install`、`--freeze PATH`。它会拒绝复用存在但没有 `pyvenv.cfg` 的路径，拒绝 Python < 3.12，并拒绝在解释器不属于目标 venv 时执行 `--install`/`--freeze`。它绝不安装 Python/uv，也绝不使用全局/系统 pip。

`gen_prd.py` 参数：`--project-root`（默认 cwd）、`--json`。

`check_prd.py` 参数：`--project-root`（默认 cwd）、`--html-dir`（默认 `docs/docsHtmlView/build/html`）、`--skip-html`（仅源码检查）。退出 0 = 干净，1 = 违规或输入缺失。

## TOC schema（`docs/toc.yml`）

```yaml
title: <发布标题>
version: <版本>
date: <日期>
abstract: <一段话>
# author: <可选；当模板 __AUTHOR__ 回退值为空时使用>

sections:
  - id: overview
    title: 项目说明与典型应用场景
    documents: [docs/product/00-README.md]
  - id: requirements
    title: 产品需求
    documents: [docs/product/01-requirements.md]
  - id: architecture
    title: 架构设计与模块划分
    documents: [docs/product/02-architecture.md]
    modules: auto
    exclude: []
  - id: appendix
    title: 附录
    sections:
      - id: glossary
        title: 术语表
        documents: [CONTEXT.md]
      - id: spec
        title: SPEC（技术规格）
        documents:
          - docs/product/*/01-spec.md
          - docs/product/*/02-interfaces.md
          - docs/product/*/03-nfr.md
      - id: current
        title: 项目现状
        documents: [docs/current/00-README.md, docs/current/**/*.md]
      - id: adr
        title: 架构决策
        documents: [docs/adr/README.md]
```

`gen_prd.py` 强制、`check_prd.py` 复核的规则：

- TOC 是映射，含非空 `title`、`version`、`date`、`abstract`，以及非空 `sections` 列表。`author` 可选。
- 顶层章节 id 必须包含 `overview`、`requirements`、`architecture`、`appendix`。`appendix` 子项必须包含 `glossary`、`spec`、`current`、`adr`。允许额外章节。
- 章节需要非空 `title`，并至少具备 `documents`、`sections` 或 `modules: auto` 之一。id 必须唯一且为安全的目录名（`[A-Za-z0-9._-]`，不含分隔符）。
- `documents` 条目是相对项目根目录的路径或 glob。它们必须解析到 `docs/product`、`docs/current`、`docs/adr` 之内，或恰好为 `CONTEXT.md`。glob 支持 `*` 与 `**`；匹配结果排序，重叠/glob 重复会被去重。显式重复列出同一文档（或跨章节重复）是错误。
- `modules: auto` 展开 `docs/product/*/00-README.md`（模块 PRD），按数字前缀、再不区分大小写名称排序。`exclude` 接受模块目录名（`08-internal`）、项目相对路径（`docs/product/08-internal`）或文档路径。
- `design/` 默认不发布：默认 SPEC glob 不会触及它，未列出的文件也绝不进入清单。
- `CONTEXT.md` 映射到生成的 `docsHtmlView/glossary.md`；仅当术语表章节列出它时才必需。
- 文档路径必须是常规 `.md`/`.rst` 文件，且路径中无符号链接。缺失路径会使 TOC 失败（不会静默跳过）。

要改变发布内容，请编辑 `docs/toc.yml`——绝不要编辑生成文件——然后在构建前重新运行 `gen_prd.py`。

## 生成产物

所有生成的 Markdown 文件以 MyST 注释标记开头（`% docs-html-view: ...`），渲染后无内容；JSON 文件带有 `"generated_by": "docs-html-view gen_prd.py"`。只有带标记/归属的文件会被覆盖或清理。

### 模板来源剥离（仅发布副本）

`guard.py` 在 `source-read` 阶段、渲染之前剥离开头的 `模板来源` 标记。识别两种形态：以 `模板来源` 开头的引用块行（连同紧随其后的连续引用块行），或 `<!-- 模板来源 ... -->` HTML 注释。二者前面都允许有 BOM 与空行，必须位于首个标题之前；连续多个开头标记会逐个剥离。正文中间的出现绝不处理。只修改内存中的源码（`source[0]`），磁盘上的源文件绝不修改。Sphinx 随后会把原始源文件复制到 `build/html/_sources/`，因此 `build-finished` 会对每个复制出的 `*.md.txt` / `*.rst.txt` 应用同样的剥离；“查看页面源代码”链接因此也是干净的。

### `docsHtmlView/index.md`（封面）

`# title`、`版本 <version> · <date>` 行、摘要，以及顶层章节的 `{toctree}`。单文档扁平化的章节直接以该文档的纯路径条目列出（中间没有落地页）；多文档与含子章节的章节通过生成的落地页列出（`nav/overview/index`、`nav/appendix/index` 等）。标题会经过净化，去除 `<`、`>`、反引号、花括号、方括号与竖线。

### `docsHtmlView/nav/<id>/index.md`（按需生成的章节落地页）

仅在需要时生成：TOC 展开后该章节解析出多于一份文档（包括 `modules: auto` 的结果），或它包含子 `sections`。解析结果恰好一份文档且没有子章节的章节会由父级直接链接，不生成 `nav/<id>/` 页面。

每个生成的页面是 `# 章节标题` 加一个相对页面的纯路径 `{toctree}`：文档（`../../../product/00-README`），以及 `appendix` 的子落地页（`glossary/index`）或被扁平化的直接子文档。嵌套附录落地页位于 `nav/appendix/<sub-id>/index.md`。

### `docsHtmlView/glossary.md`

两行标记（`generated glossary`、`% source: CONTEXT.md`）后紧跟根 `CONTEXT.md` 的正文，开头模板来源标记已在生成时剥离。`check_prd.py` 在标记/头部之后比较剥离后的正文；陈旧副本会失败。

### `docsHtmlView/_manifest.json`

```json
{
  "generated_by": "docs-html-view gen_prd.py",
  "documents": ["adr/README.md", "current/00-README.md", "docsHtmlView/glossary.md", "product/00-README.md"]
}
```

路径相对 `docs/`（即相对 Sphinx 源根目录）。它恰好包含 TOC 展开的源文档加上生成的术语表——绝不含 `index.md` 或 `nav/**`，这些由 `conf.py` 自行加入。

### `docsHtmlView/_meta.json`

```json
{
  "generated_by": "docs-html-view gen_prd.py",
  "title": "...", "version": "...", "date": "...", "abstract": "...", "author": ""
}
```

`conf.py` 使用 `title`/`author`/`version`（仅当值为空时才回退到模板 token）。封面还会使用 `date` 与 `abstract`。

## Sphinx 配置

`SOURCEDIR=..`、配置目录 `docs/docsHtmlView`（`-c .`）、`BUILDDIR=build` → 输出 `build/html`；`SPHINXOPTS = -c . -w build/warnings.log`（先创建 `build/`），以便捕获警告用于报告。`root_doc = docsHtmlView/index`，因此封面为 `build/html/docsHtmlView/index.html`。在 `build-finished` 阶段（仅 `html` builder，且构建未抛异常时），`guard.py` 还会写入 `build/html/index.html`：一个跳转到相对路径 `docsHtmlView/index.html` 的根入口页，并提供普通链接兜底。其标题为 `project`（HTML 转义），为空时回退到 `Documentation`。

`assets/conf.py.template` 从自身目录读取 `_meta.json` 与 `_manifest.json`，任一缺失都会**明确失败**（构建前必须先运行 `gen_prd.py`）。随后设置：

- `project` = meta 标题或 `__SITE_TITLE__`，`author` = meta 作者或 `__AUTHOR__`，`release` = meta 版本或 `__RELEASE__`。
- `include_patterns` — `docsHtmlView/index.md`、`docsHtmlView/nav/**`、`docsHtmlView/glossary.md`，加上清单中的每个文档。没有 `docsHtmlView/**` 通配，也没有源树级通配，因此未列出的文档不会被构建。
- `exclude_patterns` — `docsHtmlView/build/**`、`docsHtmlView/.venv*/**`、`.venv-docs/**`、`**/.git/**`。
- `docs_html_view_allowed_roots = ["product", "current", "adr"]` — 由 `guard.py` 读取；`CONTEXT.md` 仅由生成器读取，其内容作为生成的术语表发布。
- `myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]`、`myst_heading_anchors = 3`。

没有环境开关：一个 TOC、一种发布、一个输出目录。

### 防护（`assets/guard.py`）

- `builder-inited`：为 `include`、`literalinclude`、`raw` 注册拒绝执行的指令（不区分大小写；通过 `eval-rst` 与冒号围栏同样可达），并校验每个允许根目录都是解析到 `docs` 内部的简单相对名称。
- `source-read`：仅从内存源码中剥离开头的 `模板来源` 标记（引用块与 HTML 注释两种形态，位于首个标题之前；正文中间的出现与磁盘文件不受影响）。
- `doctree-read`（优先级 100，早于 Sphinx 在 500 的资源收集器）：拒绝任何不是纯 HTML 注释+空白的 `raw` 节点（因此 PRD 模板注释通过，活动标记失败）；对图片与 `download_reference` 节点，通过 `app.env.relfn2path` 解析原始引用，要求其位于已批准根目录内（使用 `realpath`/`commonpath`，拒绝符号链接），否则在复制前抛出 `SphinxError`；远程目标会被替换为内联占位符并发出 Sphinx 警告，绝不抓取。
- `build-finished`：用同样的剥离逻辑清洗 Sphinx 复制出的 `_sources/**/*.md.txt` / `*.rst.txt`；随后（仅 `html` builder 且构建未抛异常时）用根入口页覆盖 `build/html/index.html`（meta refresh 到 `docsHtmlView/index.html`，加 `<a>` 兜底）。构建目录是生成产物，因此覆盖是确定性的。
- 这是权威边界，也是不依赖仅正则扫描的原因。它防护可信文档；`conf.py` 是可信可执行代码，不受沙箱限制。

## 校验（`check_prd.py`）

1. **TOC。** 使用 generator 自身的解析器解析 `docs/toc.yml`：元数据、必需 id、文档路径/glob、`modules: auto`、允许根目录、存在性、常规文件、无符号链接、无重复。
2. **清单。** `_manifest.json` 存在，且其文档集合恰好等于 TOC 展开的文档加上 `docsHtmlView/glossary.md`。缺失/多余条目失败；每个非术语表源文件必须仍然存在。
3. **PRD 源链接。** 扫描 `docs/product/00-README.md`、`01-requirements.md`、`02-architecture.md` 与 `docs/product/*/00-README.md`。HTML 注释、围栏代码与内联代码会被掩码。允许目标：同页锚点，以及指向 `docs/product` 内 PRD 层文档（`00-README.md`、`01-requirements.md`、`02-architecture.md`）的相对链接。标记外部 URL、绝对路径、PRD 层之外的链接（SPEC/Current/ADR/design/缺失）以及状态标记 `✅`/`🚧`/`❌`。
4. **术语表新鲜度。** `docsHtmlView/glossary.md` 正文在生成标记/头部之后等于剥离模板来源标记后的 `CONTEXT.md`；缺失或陈旧则失败。
5. **构建后 HTML 锚点。** 每个清单文档加上生成的封面、按需的章节落地页、术语表与根入口 `build/html/index.html` 都必须在 `--html-dir` 下有构建页面；每个同页 `href="#..."` 都必须匹配该页中的 `id`/`<a name>`。断链/缺失失败。
6. **无未列文档。** 每个 `build/html/product/**/*.html`、`current/**`、`adr/**` 页面都必须映射回清单文档；多余页面失败。没有对应生成页面的 `nav/**` 页面（例如某个章节已变为单文档后遗留的旧落地页）也会被拒绝。
7. **模板来源。** 任何发布页面与复制出的 `_sources/**/*.txt` 都不得包含 `模板来源`；泄漏即失败。

摘要报告 TOC 文档数、清单条目数、PRD 文件/链接检查数、术语表状态、锚点检查数、未列文档数与违规数；仅当违规数为零时退出 0。`--skip-html` 省略第 5–7 阶段（构建前使用）。

## 锚点与链接规则

- 使用标准 Markdown 标题链接（`[text](#heading)`），目标限定为 h1–h3（`myst_heading_anchors = 3`）。遇到中文标题 slug 不匹配时，优先调整标题，再回退到显式的 MyST target。
- PRD 核心与模块 PRD **只**在 PRD 层内链接（产品章节与模块 PRD）。SPEC、Current、ADR、外部 URL 与状态标记会被 `check_prd.py` 拒绝；它们属于附录，不属于 PRD 叙事。
- `docs/current` 与 `docs/adr` 下的页面可自由链接；它们是附录。那里只检查构建后锚点。

## 批准与同意

Skill 在**任何写入/安装/脚手架操作之前**只询问一次，涵盖包、环境、文件、`.gitignore` 新增项、输出路径与 TOC 标题/版本。没有存储的同意状态或指纹。在已批准范围内重复渲染不会再次询问；依赖升级、覆盖已有文件或更改已批准输出根目录需要重新询问。TOC/源文档缺失或工作区畸形 → 报告并停止，绝不猜测。模板 token 不带引号，因此用 `repr(value)`（合法、转义的 Python 字面量）逐个替换，绝不将原始文本插入可执行配置。

## 限制

- 仅 `.md` / `.rst`；无 `.mdx`。
- `include` / `literalinclude` / `raw` 会被拒绝。
- 远程资源变为内联占位符并附加警告；活动 HTML 会被拒绝（仅允许 HTML 注释），`conf.py` 是可信代码。
- 不做自定义主题、浏览器、服务器或部署。
- 只有 `docs/toc.yml` 中列出的文档会被发布。模块附属文件（`00-index.md`）与 `design/` 被默认 TOC 排除；显式加入它们即意味着公开。
- 术语表是原样的 `CONTEXT.md` 正文。其中若含相对图片，会解析到 `docsHtmlView/` 下（超出已批准根目录），导致构建失败；请保持术语表为纯文本。
- 失败的 `make` 可能留下陈旧/部分 `build/` 产物；没有发布器会规范化它。
