# docs-docx-view 技术参考

## 固定版本依赖

已在 PyPI 验证（2026-10）；该组合相互兼容。本 skill 自身的 Python 下限为 3.12。

| 包 | 固定版本 | 说明 |
| :--- | :--- | :--- |
| pandoc（自带） | `pypandoc_binary==1.17` | 自带 pandoc 3.9；提供 `build.sh` / `build.bat` 使用的 `pypandoc` 模块 |
| PyYAML | `PyYAML==6.0.2` | `gen_docx.py` / `check_docx.py` 读取 `docs/toc.yml` |

`requirements.txt` 提供该声明。`prepare_env.py` 仅在传入 `--install` 时安装；调用方只在批准后运行它。Python >= 3.12 由 `prepare_env.py` 强制。

## 目录布局

```
<project root>/
  .venv-docs/                     # default render venv (or the project's docs env)
  CONTEXT.md                      # glossary source (read, never modified)
  docs/                           # publication source root
    toc.yml                       # publication source of truth
    product/                      # core PRD + module PRD/SPEC
      00-README.md                # PRD cover/overview
      01-requirements.md          # PRD requirements
      02-architecture.md          # PRD architecture + module map
      <NN-module>/
        00-README.md              # module PRD (included by modules: auto)
        00-index.md               # agent sidecar (not listed -> not published)
        01-spec.md 02-interfaces.md 03-nfr.md
        design/                   # not listed by default -> not published
    current/                      # as-built snapshot
    adr/                          # decisions
    docsDocxView/                 # workspace
      combined.md                 # generated single pandoc input (marked)
      _manifest.json              # generated exact document list
      _meta.json                  # generated title/version/date/abstract/author/lang/output
      reference.docx              # seeded Word template (only if missing; user-owned)
      build.sh                    # seeded build helper (POSIX sh; only if missing; user-owned)
      build.bat                   # seeded build helper (Windows batch; only if missing; user-owned)
      build/prd-<version>.docx    # publication (created by build.sh)
      build/pandoc.log            # pandoc stderr (created by build.sh)
```

`docsDocxView` 是工作区目录名，不是发布标题。标题来自 `docs/toc.yml`。

## 本 skill 提供的文件

- `scripts/prepare_env.py` — 创建/复用可识别的 venv；可选安装固定依赖 / freeze。仅标准库。
- `scripts/gen_docx.py` — 校验 `docs/toc.yml`，展开 glob/`modules: auto`，渲染标题层级与锚点，改写链接与本地图片，清空远程图片，写入 `combined.md` / `_manifest.json` / `_meta.json`，并在缺失时预置三个工作区文件。
- `scripts/check_docx.py` — 校验新鲜度、清单/元数据一致性、PRD 源链接与产出的 DOCX。标准库 + PyYAML。
- `scripts/make_reference.py` — `assets/reference.docx` 的维护专用生成器（不属于发布流程）。仅标准库。
- `assets/reference.docx` — 提交入库的 Word 样式/页眉/页脚模板，由 `make_reference.py` 生成。
- `assets/build.sh` — POSIX sh 构建辅助脚本，仅缺失时预置到工作区。
- `assets/build.bat` — Windows 批处理构建辅助脚本，仅缺失时预置到工作区。
- `requirements.txt` — 固定版本。

## 命令

检查使用常规只读工具完成；没有 inspect 子命令，批准前不会运行项目解释器。批准后，从项目根目录定义准备就绪环境的路径（可用 `--venv` 复用项目文档环境）：

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-docx-view}"
DOCS_PY="$PWD/.venv-docs/bin/python"                 # venv python; needs PyYAML
```

首次初始化（没有独立的脚手架步骤；生成器会创建工作区并预置缺失文件）：

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
"$DOCS_PY" "$SKILL"/scripts/gen_docx.py --project-root .
( cd docs/docsDocxView && ./build.sh )
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
```

`gen_docx.py` 会创建 `docs/docsDocxView/`（mkdir -p），并仅在各自缺失时从 `assets/` 预置 `reference.docx`、`build.sh` 与 `build.bat`。没有 `sphinx-quickstart`、`conf.py` 或其他脚手架。

一键重建（辅助脚本仅缺失时预置一次；绝不覆盖）：

```bash
( cd docs/docsDocxView && ./build.sh )            # POSIX sh; seeded executable
( cd docs/docsDocxView && ./build.sh --clean )    # delete build/ first
( cd docs/docsDocxView && DOCS_PY=/path/to/.venv-docs/bin/python ./build.sh )
```
```bat
docs\docsDocxView\build.bat                       :: Windows (from the project root)
docs\docsDocxView\build.bat --clean
```

两个辅助脚本都会 `cd` 到 `docs/docsDocxView`，优先使用 `DOCS_PY`，否则使用 `../../.venv-docs/bin/python`（Windows 为 `..\..\.venv-docs\Scripts\python.exe`）。构建前，它们要求可执行的渲染环境以及 `combined.md`、`_meta.json`、`_manifest.json`、`reference.docx` 存在；否则打印错误，提示先运行 docs-docx-view skill，并以非零码退出且不构建。`--clean` 是唯一选项；未知或多余参数会打印 `usage: ... [--clean]` 并以 2 退出。它们从 `_meta.json` 读取输出路径，通过 `pypandoc` 解析 pandoc，创建 `build/`，随后精确执行：

```bash
"$PANDOC" --from=markdown+raw_attribute --to=docx --reference-doc=reference.docx --resource-path="$(cd ../.. && pwd)" -o "$OUT" combined.md 2> build/pandoc.log
```

它们会打印 pandoc 消息数、输出路径与输出大小，并以 pandoc 的状态退出。辅助脚本只负责构建：它们绝不生成内容、运行 `gen_docx.py` / `check_docx.py`、安装包、查找 skill 目录，也不启动浏览器/服务器。更改 `docs/toc.yml`、`CONTEXT.md` 或模块集合后，请先重新运行 `gen_docx.py`。

重复构建（相同已批准范围；每次 TOC 变更后都要重新运行生成器）：

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_docx.py --project-root .
( cd docs/docsDocxView && ./build.sh )
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
```

检查，包括仅源码模式：

```bash
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root . --skip-docx
```

本 skill 到本地 `docs/docsDocxView/build/` 文件夹为止；打包、托管与交付不在其范围内，由用户自行决定。

可选的已解析版本快照（已批准产物）：

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsDocxView/requirements.lock.txt
```

维护专用的模板重新生成（发布期间不运行）：

```bash
python3 "$SKILL"/scripts/make_reference.py
python3 "$SKILL"/scripts/make_reference.py --pandoc /path/to/pandoc --output /tmp/reference.docx
```

`prepare_env.py` 参数：`--project-root`（默认 cwd）、`--venv`（默认 `.venv-docs`，相对项目根目录，除非为绝对路径）、`--base-python`（用于创建 venv 的解释器）、`--requirements`、`--install`、`--freeze PATH`。它会拒绝复用存在但没有 `pyvenv.cfg` 的路径，拒绝 Python < 3.12，并拒绝在解释器不属于目标 venv 时执行 `--install`/`--freeze`。它绝不安装 Python/uv，也绝不使用全局/系统 pip。

`gen_docx.py` 参数：`--project-root`（默认 cwd）、`--json`。退出 0 = 已生成；退出 1 = 拒绝，stderr 为 `refusing: <reason>`，且不写入任何内容。

`check_docx.py` 参数：`--project-root`（默认 cwd）、`--docx PATH`（默认是 `_meta.json` 中工作区相对的 `output`；显式相对路径相对项目根目录解析）、`--skip-docx`（仅源码检查）。退出 0 = 无失败，1 = 违规或输入缺失；警告不会使其失败。

`make_reference.py` 参数：`--pandoc PATH`（默认 `pypandoc.get_pandoc_path()`，然后回退到 `PATH` 上的 `pandoc`）、`--output PATH`（默认 `<skill>/assets/reference.docx`）。找不到可用 pandoc 时以 1 退出，并提示安装 `pypandoc_binary==1.17` 后传入 `--pandoc`。

`gen_docx.py --json` 在 stdout 打印 `{"documents": [...], "output": "...", "generated": [...], "seeded": {...}, "warnings": [...]}`。`documents` 为项目根目录相对路径；`generated` 为工作区相对路径并带 `docs/docsDocxView/` 前缀；`seeded` 将每个预置文件映射为 `created` / `exists` / `skipped` / `missing-asset` / `failed`。

## TOC schema（`docs/toc.yml`）

```yaml
title: <publication title>
version: <version>
date: <date>
abstract: <one paragraph>
# author: <optional; omitted from the cover when empty>

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

`gen_docx.py` 强制、`check_docx.py` 复核的规则：

- TOC 是映射，含非空 `title`、`version`、`date`、`abstract`，以及非空 `sections` 列表。`author` 可选，为空时不会写入封面元数据。
- 顶层章节 id 必须包含 `overview`、`requirements`、`architecture`、`appendix`。`appendix` 子项必须包含 `glossary`、`spec`、`current`、`adr`。允许额外章节。
- 章节需要非空 `title`，并至少具备 `documents`、`sections` 或 `modules: auto` 之一。id 必须唯一且为安全的目录名（`[A-Za-z0-9._-]`，不含分隔符）。
- `documents` 条目是相对项目根目录的路径或 glob。它们必须解析到 `docs/product`、`docs/current`、`docs/adr` 之内，或恰好为 `CONTEXT.md`。glob 支持 `*` 与 `**`；匹配结果排序，隐式/glob 重复会被去重。显式重复列出同一文档（或跨章节重复）是错误。
- `modules: auto` 展开 `docs/product/*/00-README.md`（模块 PRD），按数字前缀、再不区分大小写名称排序。`exclude` 接受模块目录名（`08-internal`）、项目相对路径（`docs/product/08-internal`）或文档路径。
- `exclude` 仅在配合 `modules: auto` 时有效。章节层级的未知键会被拒绝；顶层未知键只会产生警告。
- `design/` 默认不发布：默认 SPEC glob 不会触及它，未列出的文件也绝不进入清单。
- `CONTEXT.md` 在术语表位置被包含；仅当 TOC 列出它时才必需。不存在生成的术语表文件。
- 文档路径必须是常规 `.md`/`.rst` 文件，且路径中无符号链接。缺失路径会使 TOC 失败（不会静默跳过）。
- 章节标题会成为文档中的标题；TOC 顺序即文档顺序。
- 文档语言在封面元数据中固定为 `zh-CN`。

要改变发布内容，请编辑 `docs/toc.yml`——绝不要编辑生成文件——然后在构建前重新运行 `gen_docx.py`。

## 生成产物

`combined.md` 带标记并被覆盖；`_manifest.json` / `_meta.json` 带有 `"generated_by": "docs-docx-view gen_docx.py"` 并被覆盖。预置的 `reference.docx`、`build.sh` 与 `build.bat` 不带标记、归用户所有，绝不覆盖。

### `docsDocxView/combined.md`（唯一的 pandoc 输入）

````markdown
---
# docs-docx-view: generated document; do not edit
title: "<toc title>"
subtitle: "版本 <version> · <date>"
author: "<toc author>"
---
<!-- docs-docx-view: cover -->
::: {custom-style="Abstract"}
<toc abstract>
:::
```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```
::: {custom-style="TOC Heading"}
目录
:::
```{=openxml}
<w:p><w:fldSimple w:instr="TOC \o &quot;1-3&quot; \h \z \u" w:dirty="true"><w:r><w:t>Update field to build the table of contents</w:t></w:r></w:fldSimple></w:p>
```
```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```
<!-- docs-docx-view: doc docs/product/00-README.md -->
# <section title> {#sec-1-1}
...document body...
````

- 第一行是 `---`，第二行是标记，因此 `is_marked` 能识别该文件。生成器拒绝覆盖没有该标记的既有 `combined.md`。
- YAML 标量通过 `json.dumps(value, ensure_ascii=False)` 输出，因此标题与版本行始终是合法的引号标量。TOC 作者为空时，`author` 行完全省略。
- 封面标题是 pandoc 自带的标题块，使用 `reference.docx` 中的 `Title` / `Subtitle` / `Author` 样式；摘要紧随其后，以 `Abstract` 自定义样式的正文段落呈现。不要传 `--toc`：手写域是唯一的目录，标题/日期/摘要也不通过命令行传入。
- `combined.md` 刻意不输出 `lang:` 元数据键。若写 `lang: zh-CN`，pandoc 3.9 会查找未随包提供的 `translations/zh.yaml`，并在每次构建时记录四条警告；若不写该键，pandoc 会打印英文 `Abstract` 标签。CJK 校对语言来自 `reference.docx` 的 docDefaults（`w:lang w:val="en-US" w:eastAsia="zh-CN"`），`_meta.json` 仍记录 `"lang": "zh-CN"`。
- `目录` 段落使用 `TOC Heading` 自定义样式；目录域深度为 1–3，带超链接并标记为 dirty。Word 更新域时会填充它；`reference.docx` 中的 `w:updateFields` 会要求 Word 在打开时更新。
- 两个 `{=openxml}` 块分别在封面之后与目录域之后插入分页符。
- 在每个章节的第一份文档之前，章节标题会作为标题注入（章节层级用 `#`，附录子章节用 `##`），并带显式 `{#sec-<section ordinal>-1}` id；其文本会经过净化（不含 `<`、`>`、反引号、花括号、方括号、竖线或换行）。
- 每份文档之前都有标记注释 `<!-- docs-docx-view: doc <project-root-relative path> -->`。章节标题只在其第一份文档前输出一次。
- 除第一个外，每个顶层一级标题前都有分页符，因为目录块本身已以分页符结束。
- 文档正文遵循下文的标题/锚点/图片/链接规则；源文件不会被修改。

### `docsDocxView/_meta.json`

```json
{
  "generated_by": "docs-docx-view gen_docx.py",
  "title": "...",
  "version": "...",
  "date": "...",
  "abstract": "...",
  "author": "",
  "lang": "zh-CN",
  "output": "build/prd-v1.0.docx"
}
```

`output` 是工作区相对路径，也是 `build.sh` / `check_docx.py` 默认使用的唯一路径。文件名为 `build/prd-<version>.docx`，其中版本号里连续的非 `[A-Za-z0-9._-]` 字符会被替换为 `-`，并去掉首尾的 `.-_`；结果为空则使用 `build/prd.docx`。

### `docsDocxView/_manifest.json`

```json
{
  "generated_by": "docs-docx-view gen_docx.py",
  "documents": ["docs/product/00-README.md", "docs/product/01-requirements.md", "..."]
}
```

路径为项目根目录相对的 POSIX 路径，严格按 TOC 展开顺序排列，并在术语表位置包含 `CONTEXT.md`。不存在生成的术语表文件或额外的合成文档。

### 预置的工作区文件

`gen_docx.py` **仅在缺失时**从 `assets/` 预置 `reference.docx`、`build.sh` 与 `build.bat`，绝不覆盖已有文件。POSIX 上 `build.sh` 预置时即带可执行位（`0o755`）；`build.bat` 使用 CRLF 行尾。既有的符号链接或非常规文件会被保持原样并附加警告。`--json` 会将每个文件报告为 `created` / `exists` / `skipped` / `missing-asset` / `failed`。

### `docsDocxView/build/`

仅由 `build.sh` 创建（`gen_docx.py` 绝不创建）。其中包含输出的 `.docx` 与 `pandoc.log`。`--clean` 会先删除该目录。pandoc 运行失败后，`build/` 可能包含陈旧或部分产物。

### 模板来源剥离（仅生成副本）

渲染前会移除开头的 `模板来源` 标记：以 `模板来源` 开头的引用块行（连同紧随其后的连续引用块行），或 `<!-- 模板来源 ... -->` HTML 注释。允许前置 BOM 与空行；标记必须位于首个标题之前；连续多个开头标记会逐个剥离。正文中间的出现绝不处理，磁盘上的源文件绝不修改。

## 标题与锚点映射

标题按文档重映射，相对于其所属 TOC 章节层级（顶层章节为 1 级，附录子章节为 2 级）：

| 情况 | 结果 |
| :--- | :--- |
| 顶层章节标题 | 一级标题，`{#sec-<section ordinal>-1}` |
| 附录子章节标题 | 二级标题，`{#sec-<section ordinal>-1}` |
| 第一个 ATX H1 与章节标题不同 | 保留；标题层级 = 章节层级 + 1；内部源 Hn（n >= 2）-> 章节层级 + n |
| 第一个 ATX H1 与章节标题相同 | 丢弃；内部源 Hn（n >= 2）-> 章节层级 + (n - 1) |
| `CONTEXT.md` 开头 H1 | 始终丢弃；内部源 H2 -> 章节层级 + 1 |
| 第一个标题不是 H1 | 不注入任何额外标题；源 Hn（n >= 1）-> 章节层级 + n；警告会指出该文档 |
| 深于 H6 的标题 | 输出为 H6；附加警告 |
| Setext 或缩进标题 | 按纯文本处理；附加警告 |
| 解析后既无文档也无子章节的章节 | 省略；附加警告 |

- 章节标题比较使用净化后的标题（以及原始去空白标题）；仅当文档标题匹配时才丢弃。
- 保留的第一个 H1 是普通标题；被丢弃的标题由章节标题取代，因此不会留下层级空缺。
- 每个输出的章节标题与文档标题都带显式 `{#id}`。id 为 `sec-<section ordinal>-<heading ordinal>`，使用 ASCII 文档顺序计数器：章节标题为 1，随后输出的标题从 2、3…… 继续，跨该章节内的**所有文档**连续计数。
- 除第一个外，每个顶层章节标题前都有分页符。
- ATX 标题就地改写；追加生成的 id 之前，会先剥离标题行末尾既有的 `{#...}` / `{.class}` 属性块。

链接与锚点查找（按文档）：

| 来源 | 解析结果 |
| :--- | :--- |
| 精确标题文本 | 该标题的 id |
| GFM 风格 slug（小写、空格转 `-`、去标点、保留 CJK） | 该标题的 id；重复 slug 在每个文档内加 `-1`、`-2` 后缀 |
| 百分号解码后的变体 | 同一个 id |
| `[text](#anchor)` | 解析成功时改写为 `#<id>` |
| `[text](relative/path.md#anchor)` 且目标是清单文档 | 改写为目标标题的 `#<id>` |
| 无片段的 `[text](relative/path.md)` | 文档标题被保留时为 `#<title id>`，否则为 `#<section id>` |
| `http:`、`https:`、`mailto:`，或清单之外的任何目标 | 保持原样 |
| 以 `.md` 结尾或含片段的未解析目标 | 警告 `file:line -> target`；生成继续 |

相对路径相对源文档所在目录解析。链接文本保留。目标为外部或发布范围之外时，片段不会被改写。被丢弃的文档标题仍保留锚点条目，但指向章节标题的 id。

## 图片、链接与安全

- **远程图片绝不抓取。** `http://`、`https://`、协议相对（`//`）以及其他 URL scheme 目标——内联图片、`<img src=...>` 标签，以及被引用式图片使用的引用定义——会被替换为字面量 `[图片：<alt>]`（无 alt 时为 `[图片]`）并附加警告。引用定义行会被清空。
- **本地图片经过校验并重新定位。** 目标相对源文档解析；它必须是已存在的常规文件，其真实路径位于项目根目录**并且**位于 `docs/product`、`docs/current` 或 `docs/adr` 之内，且路径中无符号链接。它会被改写为项目根目录相对的 POSIX 路径；对 Markdown 图片，含空格时用尖括号包裹，未给出 `width`/`height` 属性时追加 `{width=16cm}`。既有 Markdown 属性块会保留。
- **绝对路径与 `file:` 图片目标会使生成失败**，逃逸允许根目录或使用符号链接的本地图片同样失败。
- **禁止的构造会使生成失败**，并报告 `file:line`：MyST/Sphinx `{include}`、`{literalinclude}`、`{raw}`；原始块 `{=html}`、`{=openxml}`；rST `.. include::`、`.. literalinclude::`、`.. raw::`。扫描在代码/注释掩码之前对源文本运行，因此围栏或注释中的构造同样会被拒绝。
- **链接只在发布范围内改写。** 外部 scheme 与清单之外的目标保持原样；未解析的内部目标只会警告，不会失败。
- **预检是事务性的。** 计划、渲染后的文档与预期输出都会在工作区被触碰之前计算完成。既有输出必须是带标记的 Markdown 或带归属的 JSON（`generated_by`）；符号链接工作区、逃逸工作区的输出，或未标记的冲突会以 1 拒绝，且不改变任何内容。写入使用临时文件与原子替换。
- **构建不抓取任何内容。** `build.sh` 以项目根目录作为 `--resource-path` 运行 pandoc，使已改写好的本地图片能够解析；远程图片在 pandoc 运行前已被替换。

## `reference.docx` 与 `make_reference.py`

`assets/reference.docx` 派生自 pandoc 3.9 的默认参考文档，并作为二进制提交入库。它提供：

- `word/styles.xml`：docDefaults 使用 Calibri / eastAsia 宋体；Heading 1–4 使用 Calibri Light / 黑体，带深色与大纲级别；封面使用 `Title` / `Subtitle` / `Author` / `Abstract` 样式；`TOC Heading` 为正文大纲级别 9（因此不会出现在目录中）；`Body Text` / `First Paragraph` 间距；带表头底色与斑马纹的 `Table` 样式；等宽的 `Source Code` / `Verbatim Char`；以及 `Hyperlink`、`Header`、`Footer` 样式。
- `word/settings.xml`：`<w:updateFields w:val="true"/>`，使 Word 刷新目录与页码域。
- `word/header1.xml`：右对齐的 `DOCPROPERTY "title"` 域，标记为 dirty，带下边框。
- `word/footer1.xml`：居中的 `第 PAGE 页 / 共 NUMPAGES 页` 域组合。
- 单个 A4 节（`w:pgSz w:w="11906" w:h="16838"`），2.54 cm 页边距，引用页眉/页脚关系；`[Content_Types].xml` 中有匹配的 overrides。

`make_reference.py` 仅用于维护，发布期间不运行。它读取 `pandoc --print-default-data-file reference.docx`，应用这些编辑并保留其他所有部件，以确定性方式重新打包（固定条目顺序、固定 1980-01-01 时间戳），随后验证结果：每个 `.xml`/`.rels` 部件都能解析、所有必需样式 id 存在、页眉/页脚/设置部件与关系存在，且一个夹具（H1–H4、表格、代码、CJK、本地图片）能通过新模板转换并重新读回 Markdown。失败时会删除临时输出并以非零码退出。它不触碰工作区或任何发布产物。

## 校验（`check_docx.py`）

1. **源码与新鲜度。** 在内存中重建计划与预期的 `combined.md`，并要求与磁盘文件逐字节一致。缺失/不同即表示陈旧：失败并提示重新运行 `gen_docx.py`。同时要求 `_manifest.json` 的文档等于计划顺序，且 `_meta.json` 带有预期的 `generated_by`、`output`、`title`、`version` 与 `lang`。这涵盖术语表新鲜度、模板来源剥离、远程图片清空、标题/锚点改写与文档标记顺序。
2. **PRD 源规范。** 与 docs-html-view 相同的规则：掩码围栏代码、内联代码与 HTML 注释；对 `docs/product/00-README.md`、`01-requirements.md`、`02-architecture.md` 与 `docs/product/*/00-README.md`，只允许同页锚点与指向 PRD 层文档的相对链接；标记外部 URL、绝对路径、PRD 层之外的链接，以及状态标记 `✅` / `🚧` / `❌`。缺少 `docs/product` 或某个核心章节同样属于违规。
3. **DOCX（`--skip-docx` 时跳过）。** 路径默认是 `_meta.json` 中工作区相对的 `output`；`--docx PATH` 可覆盖（相对覆盖路径相对项目根目录解析）。要求文件存在且为合法 zip；`word/document.xml`、`word/settings.xml` 与 `docProps/core.xml` 可解析；`word/document.xml` 含 `TOC` 域指令（`TOC \o "1-3"`）；settings 含启用的 `w:updateFields`；核心属性 `dc:title` 等于 TOC 标题；预期章节标题（顶层 H1 + 附录子 H2，净化后的标题）按顺序出现，每个预期顶层 H1 恰好出现一次；且 XML 部件中不含 `模板来源`。
4. **报告。** 统计 TOC 文档数、清单条目数、检查的 PRD 链接数、预期标题数、DOCX 检查数与违规数，源码违规会给出 `file:line`。仅当没有失败时退出 0；警告不会使其失败。`check_docx.py` 不校验归用户所有的构建辅助脚本，也不校验视觉样式保真度。

## 批准与同意

本 skill 在**任何写入/安装/生成之前**只询问一次，涵盖包、环境、文件、`.gitignore` 新增项、输出路径与 TOC 标题/版本。没有存储的同意状态或指纹。在已批准范围内重复构建/重新生成不会再次询问；依赖升级、覆盖已有文件或更改 TOC 范围需要重新询问。预置的 `reference.docx`、`build.sh` 与 `build.bat` 属于「创建的文件」清单，仅在缺失时预置；已有文件绝不覆盖。TOC/源文档缺失 → 报告并停止，绝不猜测。构建仅在本地进行：不抓取网络、构建时不运行安装器、不部署。

## 限制

- 验证环境中没有 Word 或 LibreOffice 运行。目录域会在 Word 更新域时填充（已设置 `w:updateFields`）；版式、字体、分页与表格适配需要人工在 Word 中审阅。
- 目录深度固定为 1–3 级标题。
- 深于 H6 的标题会被钳制为 H6；层级可能在此处被压平。
- 宽表格可能溢出页面。
- Mermaid 图不会渲染；它们仍是普通代码块。
- `.rst` 会被接受，但按 Markdown 处理（仅识别 ATX 标题）；rST 语法不会被转换。
- `include` / `literalinclude` / `raw` 会被拒绝；这不是任意 MyST 渲染器。
- 没有自定义主题；每个项目都使用同一套 `reference.docx` 样式。替换它属于用户自行维护的工作，且样式保真度不做校验。
- 术语表是 `CONTEXT.md` 的文本。其中若含相对图片，会解析到允许根目录之外并导致失败；远程图片会变为占位符，因此请保持纯文本。
- 构建辅助脚本只负责构建；它们不会重新生成、安装依赖、校验或规范化失败的 `build/`。不存在浏览器、服务器或部署环节。
