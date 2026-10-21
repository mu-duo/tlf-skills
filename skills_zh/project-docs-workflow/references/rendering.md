# PRD 发布（docs-html-view）

默认方案；项目可在物化副本中覆盖。

发布是**可选、由用户触发**的能力，由第一方 `docs-html-view` skill 在本方案之外提供。本方案只固定发布所依赖的**文档契约**：发布什么、链接怎么写，以及源文档绝不改写。它绝不安装、构建、渲染或激活任何东西，init 也不创建任何发布产物。

## 可发布的多页 PRD

渲染器从 `docs/toc.yml` 构建**可发布的多页 PRD**：

- **核心**：三个 PRD 章节（`docs/product/00-README.md`、`01-requirements.md`、`02-architecture.md`）加上每个模块 PRD（`docs/product/*/00-README.md`，由 `modules: auto` 展开）。
- **附录**：术语表（`CONTEXT.md`）、SPEC（`01-spec` / `02-interfaces` / `03-nfr`，以及可选 `design/`）、Current（`docs/current/`）与 ADR（`docs/adr/README.md` 及选定 ADR）。
- **范围外**：`docs/issues/`、`docs/agents/`、模块 `00-index.md` 侧车，以及任何未列入 TOC 的文档。

没有全站模式，也没有 profile 开关：每次构建都是由 TOC 驱动的 PRD 发布。TOC 是唯一的发布来源；只构建 TOC 列出的文档。

## TOC 驱动

- `docs/toc.yml` 声明 `title`、`version`、`date`、`abstract` 与章节树。
- 必需章节 id：`overview`、`requirements`、`architecture`、`appendix`。
- 附录 id：`glossary`、`spec`、`current`、`adr`。
- `architecture` 章节使用 `modules: auto`；`exclude` 移除特定模块。`design/` 默认排除。
- 每个路径 / glob 必须落在 `docs/product`、`docs/current`、`docs/adr` 内，或指向 `CONTEXT.md`。只发布 TOC 列出的文档；生成精确包含清单，未列出的文档绝不构建。

## 术语表

- 构建时把根 `CONTEXT.md` 复制为 `docs/docsHtmlView/glossary.md`，并标记为生成物。
- 术语表页出现在附录下；不在发布工作区中手工编辑。

## 链接编写

- **PRD 核心链接**：仅 PRD 层——同文件锚点、产品章节 ↔ 模块 PRD、模块 PRD ↔ 模块 PRD。无外链（`http` / `https` / `mailto`），无指向 SPEC、Current 或 ADR 的链接，无状态标记。
- **SPEC / Current → ADR**：**描述性短语 + 稳定路径链接**指向 ADR 文件，例如 `支持 [离线使用](../../adr/0003-offline.md)`。描述独立撰写、自足；**不**转述或摘要 ADR 理由。不要求每条需求都挂 ADR，方案绝不自动推断 ADR 链接。
- 原生 `ADR-XXXX` 引用记号不变；ADR 删除 / 语义修改会 sweep **两种**写法（`adr.md`）。
- 因为 PRD 核心不得外链，其章节页没有外部目标需要解析；只有内部锚点重要。跨层导航由 TOC 与附录提供。

## 源文档绝不改写

- Markdown 源文档仍是唯一事实源，本身保持人类可读；渲染器对它们**只读**——不规范化、不移动、不改写。
- 范围外或悬空引用会被**报告**，绝不在源中修复。
- 「没有可发布内容」是**失败**，不是静默成功；渲染器绝不自行 bootstrap 文档工作流。

## 输出

- 构建写入 `docs/docsHtmlView/` 下；HTML 输出落在 `docs/docsHtmlView/build/html`。接收者打开 `docsHtmlView/index.html`；文件夹可打包分发。
- 生成文件：`index.md`、`nav/**`、`glossary.md`、`_manifest.json`、`_meta.json`。只写入或清理带标记的生成文件；源文档绝不被触碰。

## 手动、opt-in

- 发布是**由用户触发、手动**的：无钩子、文档编辑不自动构建、不改动 init 主产物。
- 安装 / init / 首次构建只在通过 skill 交互获得用户明确同意后进行；没有自定义编排器、manifest 审批状态机或后台构建。
- 集成时，显式把项目指向 `docs-html-view` skill；不要接进初始化。
