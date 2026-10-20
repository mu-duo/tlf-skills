# docs-html-view 技术参考

## 固定依赖

已于 2026-10-14 在 PyPI 上验证；该组合互相兼容。Sphinx 9.1.0 要求 Python >= 3.12。

| 包 | 固定版本 | 说明 |
| :--- | :--- | :--- |
| Sphinx | `Sphinx==9.1.0` | 需要 Python >= 3.12 |
| MyST parser | `myst-parser==5.1.0` | 支持 Markdown |
| RTD theme | `sphinx-rtd-theme==3.1.0` | 通过 `html_theme` 使用的原版主题 |

`requirements.txt` 随附这份声明。除非传入 `--install`，否则 `prepare_env.py` 不安装任何东西；调用方仅在批准后运行它。

## 布局

```
<project root>/
  .venv-docs/                     # default render venv (or the project's docs env)
  docs/                           # Sphinx source root
    prd|current|adr/              # approved trees, never modified
    issues/ agents/ ...           # excluded
    docsHtmlView/                 # workspace
      conf.py                     # from assets/conf.py.template
      guard.py                    # copied from assets/guard.py
      index.md                    # generated full-site landing page (marked)
      nav/<tree>/**/index.md      # generated full-site toctrees (marked)
      l1/index.md                 # generated L1-only toctree (marked)
      docs-html-view.config.json  # optional, user-authored
      build/html/docsHtmlView/index.html        # full-site landing page
      build-l1/html/docsHtmlView/l1/index.html  # L1-only landing page
```

`docsHtmlView` 是工作区目录名，不是站点名。

## 本 skill 分发的文件

- `scripts/prepare_env.py` — 创建/复用可识别的 venv；可选的固定版本安装 / 冻结。仅使用标准库。
- `scripts/gen_nav.py` — 生成 `index.md` + `nav/**` toctree（完整站点）或 `l1/index.md`（L1）；仅限带标记的文件。
- `scripts/check_l1.py` — 校验 L1 源链接规则与构建后 HTML 锚点。仅使用标准库。
- `assets/conf.py.template` — 用于新站点的受管 `conf.py`。
- `assets/guard.py` — 解析/渲染防护扩展。
- `requirements.txt` — 固定版本。

## 命令

检查使用常规只读工具完成；没有 inspect 子命令，且在批准前不会运行项目解释器。批准后，从项目根目录定义准备就绪环境的绝对路径（可通过覆盖 `--venv` 来复用项目文档环境）：

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="APPROVED TITLE"                           # the confirmed project/site title
DOCS_PY="$PWD/.venv-docs/bin/python"                 # venv python
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # venv sphinx-build
```

首次初始化（仅新站点；如果 `docs/docsHtmlView/` 已存在则跳过，改为展示手动合并计划）：

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
mkdir -p docs/docsHtmlView
( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
# apply assets/conf.py.template -> docs/docsHtmlView/conf.py
#   tokens are UNQUOTED; replace __SITE_TITLE__/__AUTHOR__/__RELEASE__ with repr(value)
# copy assets/guard.py -> docs/docsHtmlView/guard.py
# remove the generated docs/docsHtmlView/index.rst
# Makefile: SOURCEDIR = ..   BUILDDIR = build   SPHINXOPTS = -c . -w build/warnings.log
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile full
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
```

重复渲染（相同已批准范围与标题，无需重新询问）：

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile full
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
```

不使用 `make`：

```bash
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
```

L1 专属 profile（opt-in；需要 `docs/prd/00-README.md`）。L1 构建只读取 L1 层，但配置仍会被校验（若设置了 `landing_page`，它必须能正确解析）：

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile l1
mkdir -p docs/docsHtmlView/build-l1
( cd docs/docsHtmlView && DOCS_HTML_VIEW_PROFILE=l1 "$DOCS_SPHINXBUILD" -b html -c . \
    -d build-l1/doctrees -w build-l1/warnings.log .. build-l1/html )
"$DOCS_PY" "$SKILL"/scripts/check_l1.py --project-root . --html-dir docs/docsHtmlView/build-l1/html
python3 -c "import shutil; shutil.make_archive('docs/docsHtmlView/build-l1/l1-docs', 'zip', 'docs/docsHtmlView/build-l1/html')"
# 或: (cd docs/docsHtmlView/build-l1 && zip -r l1-docs.zip html)
```

接收方打开 `docs/docsHtmlView/build-l1/l1-docs.zip` 内的 `docsHtmlView/l1/index.html`。请压缩整个文件夹，而不是单个 HTML 文件；在构建与检查都成功后重新压缩。`check_l1.py --skip-html` 只运行源链接规则。

当没有任何已批准的树包含文档（完整站点），或 `l1_roots` 下不存在 `00-README.md`（L1）时，`gen_nav.py` 退出码为 `1`；L1 profile 在 `prd` 根处于活动状态时，若产品 L1 `docs/prd/00-README.md` 缺失，即使存在模块 L1 文件，也会以 `1` 退出。因此后续构建无法静默产出陈旧站点。警告（缺失/为空的树）输出到 stderr；`--json` 会将摘要打印到 stdout。若不传 `--title`，站点标题默认是 `Documentation`；请传入已批准的 `--title`（或设置 `site_title`），以便重复渲染保持商定的标题。

可选的已解析版本快照（已批准产物）：

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsHtmlView/requirements.lock.txt
```

`prepare_env.py` 选项：`--project-root`（默认当前工作目录）、`--venv`（默认 `.venv-docs`，除非为绝对路径，否则相对于项目根目录）、`--base-python`（用于创建 venv 的解释器）、`--requirements`、`--install`、`--freeze PATH`。它会拒绝复用存在但不含 `pyvenv.cfg` 的路径，拒绝 Python < 3.12，并且除非解释器确实属于目标 venv，否则拒绝 `--install`/`--freeze`。它绝不安装 Python/uv，也绝不使用全局/系统 pip。

`gen_nav.py` 选项：`--project-root`（默认当前工作目录）、`--title`（站点标题覆盖）、`--profile {full,l1}`（默认 `full`）、`--json`。

`check_l1.py` 选项：`--project-root`（默认当前工作目录）、`--html-dir`（默认 `docs/docsHtmlView/build-l1/html`）、`--skip-html`（仅源检查）。退出码 0 = 通过，1 = 违规或缺少输入。它会打印 `L1 files checked`、`links checked`、`broken anchors` 与 `violations`。


## Sphinx 配置

`SOURCEDIR=..`，配置目录 `docs/docsHtmlView`（`-c .`），`BUILDDIR=build` → 输出 `build/html`；`SPHINXOPTS = -c . -w build/warnings.log`（需先创建 `build/`），以便捕获警告用于报告。`root_doc = docsHtmlView/index`，因此落地页为 `build/html/docsHtmlView/index.html`（除此之外 `build/html/` 的布局不变；无重定向或额外页面）。

`PROFILE = os.environ.get("DOCS_HTML_VIEW_PROFILE", "full")` 选择视图。`full` 保持上述设置。`l1` 设置：

- `root_doc = "docsHtmlView/l1/index"`；
- `include_patterns = ["docsHtmlView/l1/index.md", "prd/00-README.md", "prd/**/00-README.md"]`；
- `exclude_patterns` 覆盖 `docsHtmlView/build/**`、`docsHtmlView/build-l1/**`、`docsHtmlView/nav/**`、`docsHtmlView/.venv*/**`、`.venv-docs/**`、`**/.git/**`；
- `docs_html_view_allowed_roots = ["prd"]`。

`conf.py` 使用：

- `include_patterns` — **逐项枚举**：`full` 下为 `docsHtmlView/index.md`、`docsHtmlView/nav/**`，以及每棵已批准树一个 `<root>/**`；`l1` 下为 L1 索引加 `prd/00-README.md` / `prd/**/00-README.md`。不是 `docsHtmlView/**` 通配符。
- `exclude_patterns` — 构建产物（包括 `build-l1`）、`.venv-docs`、工作区 venv、VCS 内部目录；`l1` 还会排除 `docsHtmlView/nav/**`。
- `myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]`，`myst_heading_anchors = 3`。
- `docs_html_view_allowed_roots` — 当前 profile 对应的相同根，由 `guard.py` 读取。

**更改 `allowed_dirs` 属于手动、需批准的编辑，没有自动同步。** 手动更新全部三处——`conf.py` 中的 `include_patterns` 与 `docs_html_view_allowed_roots`，以及 `docs-html-view.config.json` 中的 `allowed_dirs`——然后重新运行 `gen_nav.py`；它们之间的不一致必须在 `make` 之前解决。缺失/为空的树没有问题（报告并跳过）。

### 防护（`assets/guard.py`）

- `builder-inited`：为 `include`、`literalinclude`、`raw` 注册拒绝执行的指令（不区分大小写；通过 `eval-rst` 与冒号围栏同样会命中），并校验每个已批准根目录都是简单的相对名称且解析到 `docs` 内部。
- `doctree-read`（优先级 100，早于 Sphinx 在 500 的资源收集器）：拒绝任何不是纯 HTML 注释+空白的 `raw` 节点（因此 PRD 模板注释可通过，活动标记失败）；对于图片与 `download_reference` 节点，通过 `app.env.relfn2path` 解析原始引用，要求它位于已批准根目录内（使用 `realpath`/`commonpath`，拒绝符号链接），否则在任何复制之前抛出 `SphinxError`；远程目标会被替换为内联占位符并发出 Sphinx 警告，绝不抓取。
- 这是权威边界，也是不使用仅正则扫描的原因。它防护可信文档；`conf.py` 是可信的可执行代码，不受沙箱限制。

## 可选项目配置

`docs/docsHtmlView/docs-html-view.config.json` 由用户编写，绝不覆盖。它必须是 JSON 对象；解析错误、非对象、非字符串的 `site_title`、非字符串的 `navigation_order`、不安全的 `allowed_dirs` 条目，或格式错误的 `landing_page` / `l1_roots` 都会被拒绝（不会静默丢弃）。

| 键 | 读取方 | 作用 |
| :--- | :--- | :--- |
| `site_title` | `gen_nav.py` | 站点标题（也可通过 `gen_nav.py --title` 设置） |
| `allowed_dirs` | `gen_nav.py` | 显式指定的树；每项一个目录名（不含分隔符、非隐藏、不是 `build`/`docsHtmlView`）；默认为 `prd`、`current`、`adr` |
| `navigation_order` | `gen_nav.py` | 相对于 `docs/` 的路径字符串列表，按顺序排在最前；其后按数字前缀，再按不区分大小写的名称 |
| `landing_page` | `gen_nav.py` | 相对于 `docs/` 的路径（例如 `prd/00-README.md`），在完整站点 `index.md` 顶部醒目的位置生成链接；必须存在于已批准根目录内且不是符号链接（只要设置就会校验） |
| `landing_page_label` | `gen_nav.py` | `landing_page` 的可选标题/链接标签；默认使用目标的 H1，再回退到文件名主干 |
| `l1_roots` | `gen_nav.py` | L1 profile 的根（已批准根名）；当 `prd` 已批准时默认 `["prd"]`，否则为 `[]` |
| `author`、`release` | 仅人工 / agent | 应用 `conf.py.template` 时的模板 token 值；脚本不读取 |
| `python` | 仅人工 / agent | 选择 venv 路径时优先使用的解释器；脚本不读取 |

## 导航规则

- 仅限带标记的生成文件（`% docs-html-view: generated navigation; do not edit`，一个 MyST 注释）；未标记的冲突与符号链接会被拒绝。
- **任何写入前预检：** 检查已批准目录、源文档树以及任何已有的 `nav/`（包括祖先目录）是否存在符号链接；在首次写入或清理前校验每个输出路径与已有冲突，因此拒绝时文档树保持不变。
- 当没有任何已批准的树包含文档时，`gen_nav.py` 退出码为 `1`，并将警告（缺失/为空的树）打印到 stderr。
- 若存在已填充内容的旧版 `docs/pdr/` 树且它不在解析出的根目录中，则会报告：`warning: legacy docs/pdr/ detected; not rendered. Migrate to docs/prd/ or add "pdr" to allowed_dirs explicitly.` 该树绝不会被移动或重命名，默认也不会渲染。若要按原样渲染，请将 `pdr` 显式加入 `allowed_dirs`（并按照上文的手动同步规则，同时加入 `include_patterns` 与 `docs_html_view_allowed_roots`）；当 `pdr` 被显式允许或渲染时，该警告不会触发。
- 层级镜像目录树；每个目录都会获得其文档的 `{toctree}` 与子索引链接；条目标题来自源文档的 H1（toctree 条目仅使用路径），因此任何源文本都无法注入 MyST。
- 目录/站点标题会被净化（不含 `<`、`>`、反引号、花括号、方括号、竖线、换行）。
- 完整 ADR 树都会渲染，包括已退役/已删除的墓碑桩。
- 重新运行只清理带标记的过期导航文件；用户文件绝不触碰。

### L1 profile

- 按文件名识别：`l1_roots` 下递归寻找常规 `00-README.md` 文件。符号链接的 L1 文件会被跳过；树中任何位置的符号链接都会被拒绝。
- 若不存在 L1 文档，`gen_nav.py --profile l1` 会打印明确错误并以 1 退出。当 `prd` 根处于活动状态时，若产品 L1 `docs/prd/00-README.md` 缺失，即使存在模块 L1 文件，也会以 1 退出。
- 排序：`navigation_order` 条目优先（按相对于 `docs/` 的路径），然后是各路径组件的数字前缀，最后是不区分大小写的路径。
- `docsHtmlView/l1/index.md` 是一个扁平的 `{toctree}`，`:maxdepth: 1`，条目为相对于生成文件的纯路径，例如 `../../prd/00-README`、`../../prd/01-mod/00-README`。不生成按目录划分的导航文件。
- L1 构建只包含生成的 L1 索引以及 `prd/00-README.md` + `prd/**/00-README.md`。L2（`01-spec` 等）、Current、ADR 与 `00-index.md` 绝不渲染。
- `docsHtmlView/l1/` 会接受与 `nav/` 相同的预检、冲突、越界校验与带标记文件清理检查。
- 源链接规则（`check_l1.py`）：仅允许同文件锚点，以及指向 `docs/prd/` 下另一个 `00-README.md` 的相对链接。外部 URL、绝对路径、Current/ADR/L2 链接，以及任何逃出 `docs/prd` 的目标都是违规，报告为 `file:line: target`。
- 构建后锚点：`build-l1/html/prd/**/00-README.html` 中每个同文件 `href="#..."` 都必须在同一页面中存在对应 `id`；断链锚点报告为 `file: #id`。缺失 L1 HTML 属于错误，不会静默通过；`--skip-html` 会省略 HTML 阶段。
- 锚点策略因视图而异：完整站点不受 `check_l1.py` 门禁；L1 专属构建 / 检查才是可强制的路径，断链的 L1 锚点属于失败。HTML 注释中的模板占位链接会被源检查忽略。


## 批准与同意

该 Skill 在任何写入/安装/脚手架操作之前询问一次，涵盖包、环境、文件、`.gitignore` 新增项、输出路径与标题。没有存储的同意状态或指纹。已批准范围内的重复渲染不会再次询问；依赖升级、覆盖已有文件，或更改已批准的根目录/范围需要重新询问。缺失的树或格式错误但必需的配置/venv → 报告并停止，绝不猜测。模板 token 不带引号，因此请用 `repr(value)`（合法、转义的 Python 字面量）替换每个 token，绝不要将原始内容插值进可执行配置。L1 专属构建/压缩位于已批准的工作区/产物范围内，但仍属手动：仅在用户要求时运行，绝不自动执行。

## 限制

- 仅支持 `.md` / `.rst`；不支持 `.mdx`。
- `include` / `literalinclude` / `raw` 会被拒绝。
- 远程资源会变为内联占位符并附加警告；活动 HTML 会被拒绝（仅允许 HTML 注释），且 `conf.py` 是可信代码。
- 无自定义主题、浏览器、服务器或部署。
- L1 profile 按文件名识别 `00-README.md`，并为 `include_patterns` / `allowed_roots` 假定根目录为 `prd`；不同的 `l1_roots` 需要手动编辑 `conf.py`。它需要产品 L1 `docs/prd/00-README.md`；缺失时即使存在模块 L1 文件，`gen_nav.py --profile l1` 也会以 1 退出。完整站点：`prd` + `current` + `adr`。
- L1 专属产物是文件夹（或其 zip）；没有单文件 HTML 包。
- 失败的 `make` 可能留下陈旧/部分的 `build/` 产物；没有发布环节将其规范化。
