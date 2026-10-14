# 文档 HTML 渲染 Skill

> 完成: 2026-10-14 ｜ 责任: agent ｜ 创建: 2026-10-14 ｜ 关联: [模糊PDR与探索式开发模型](../../suggestion/agent/模糊PDR与探索式开发模型.md) ｜ [拆分Current与精简任务日志](../../feature/history/拆分Current与精简任务日志-done.md)

## 背景与目标

用户希望 PDR / Current / ADR 文档除 Markdown 外还能以 HTML 形式阅读。先前的渲染候选（原 `suggestion`）只到「工具不固定」的边界；本轮用户**授权**选定工具与分发方式，本条目因此由原 suggestion 升为 feature。目标：提供第一方、手动触发的 HTML 渲染能力，默认覆盖 `docs/pdr` + `docs/current` + **完整** `docs/adr`（含退役条目与墓碑桩、保留标注），不含 issues / agents。

## 范围

- 仅渲染既有 Markdown **原文**，绝不改写 / 移动 / 归一化源文件。
- 覆盖范围：`docs/pdr`、`docs/current`、完整 `docs/adr`（墓碑桩与退役标注照常呈现）；**不**渲染 `docs/issues`、`docs/agents`。
- 第一方 `/docs-html-view` 手动分发；由用户手动触发。
- 该范围与环境**仅**针对本 docs 渲染能力，**不适用于任何应用运行环境**。
- 明确**不做**：测试用例 / 测试治理改动；本仓库不做 PDR / ADR / project init。

## 方案（已批准 · 简化后的最新版）

- 小依赖脚本：仅在选定环境内安装 / 固定 Sphinx + MyST + RTD 主题依赖；不封装渲染。
- 初始化：标准 `sphinx-quickstart`（交互确认），不自研 init。
- 渲染：标准 Makefile `make html` 或 `sphinx-build`，直接使用原始 Markdown 源（不复制 / 不改写）。
- 可选：仅一个导航脚本（排序 / 生成导航），不含渲染编排。
- 输出 `build/html`。
- 明确**不做**（取代此前的过度设计）：无自研渲染编排器、无 fingerprint / manifest、无鉴权状态机、无 staged publisher。
- 同意方式：由技能交互获得用户同意，不再要求自定义 preflight / 计划批准机制。
- 环境：优先项目既有环境，否则 `.venv-docs`；依赖固定版本；不做系统级安装；手动触发，不自动打开浏览器 / 起服务 / 发布。
- 结果三态：成功 / 预览（有警告）/ 失败——由技能解读标准 Sphinx 的退出码 / 警告得出；`make` 失败可能留下陈旧 / 部分产物，**明确不得声称「新构建成功」**；无任何文档可渲染时判为失败，且**不自动初始化工作流**。
- 范围不变：`docs/pdr` + `docs/current` + 完整 `docs/adr`；ADR 用描述性短语 + 稳定路径链接。
- 仓库 / 用户 / 系统环境**不**安装、**不**做 site init；验证仅在经用户单独明确批准的临时环境进行（见「结果」）。

## 完成判据

- 小依赖脚本 + 标准 `sphinx-quickstart` + 标准 `make html` / `sphinx-build` 链路可由用户手动运行。
- 可选导航脚本仅做导航，不含渲染编排。
- 无自研渲染编排器 / fingerprint / manifest / 鉴权状态机 / staged publisher。
- 三态由标准 Sphinx 退出码 / 警告解读；失败可留陈旧 / 部分产物，且不声称新构建成功。
- 范围正确（pdr / current / 完整 adr；不含 issues / agents），源文件不被改写，输出 `build/html`；手动同意与环境约定满足。
- 仓库 / 用户 / 系统环境保持不安装、不做 site init；仓库常规文档仍无 `pdr` / `current` / `adr`；未做测试或测试治理变更；未做 project init。（验证仅在经用户单独明确批准的临时环境进行，见「结果」。）

## 步骤

- [x] 规划（完成判据与方案已对齐）
- [x] 骨架（最小可运行切片 + 证据；临时环境真实跑通 `make html`）
- [x] 细节（主路径实现与质量）
- [x] 异常（失败路径、边界与稳定性）
- [x] 回顾（收尾回顾：文档同步）

## 结果

交付（简化版）
- 小依赖脚本 + 标准 `sphinx-quickstart` + 标准 `make html` / `sphinx-build` + 可选导航脚本；无自研渲染编排器 / fingerprint / manifest / 状态机 / staged publisher（旧 `docs_html_view.py` 已删除，仅保留依赖 / 导航 helper 与一个小型 guard 插件）。
- 范围：`docs/pdr` + `docs/current` + 完整 `docs/adr`（含退役与墓碑桩）；ADR 用描述性短语 + 稳定路径链接（可带 `#fragment`）；`docs/issues` / `docs/agents` 排除。该范围与环境**仅**针对本 docs 渲染能力，不适用于任何应用运行环境。

临时验证环境（经用户单独明确批准，不涉及系统 / 用户环境）
- 临时根 `/tmp/opencode/docs-html-view-verify.6JyvhY`，Python 3.14.4。
- `python -m venv` 因缺 `ensurepip` 正确失败；改用既有 `uv`（未安装）在临时目录播种已就绪的 `.venv-ready`；`prepare_env.py` 复用识别到的 venv，固定版本依赖仅装入该临时 venv 并冻结到临时目录。**未**改动系统 / 用户环境。

证据（父任务持有，位于临时根）
- 真实 `sphinx-quickstart` + 最终 conf 替换 repr + 生成的导航；标准 `make html` 退出 0、警告为空；重复 `make html` 正常；源文件哈希未变。
- 覆盖 pdr / current / 完整 ADR（退役 + 墓碑）；短语超链接 + `#fragment`；issues / agents 被排除；缺失目标 → preview 退出 0 带警告；严格 `-W` 退出非 0。
- 实际 HTML 入口：`docs/docsHtmlView/build/html/docsHtmlView/index.html`（嵌套 `root_doc`）。
- Guard `results-fixed.json`：17 个真实离线 fixture；direct / ref / symlink 的图片与下载在复制字节前 FAIL；colon / eval-rst / 大写 include 被阻断；raw active 被阻断；普通 HTML 注释放行；远程图片以占位符 + 警告处理、零 socket 尝试。
- 源 / 模板路径静态校验通过；`node --check bin/install.js`、`node bin/install.js check` 通过；实际安装到临时目标逐字节复制 skill（含 scripts / assets），manifest kind `docs-html-view` / action `installed`，包安装未创建任何 Python 环境；uninstall 与重复 install DRYRUN 行为保持；`git diff --check` 干净。

限制
- 仓库 / 用户 / 系统环境仍未安装、未做 site init；仓库常规文档仍无 `pdr` / `current` / `adr`；仓库内不初始化渲染站点、不做 project init。
- 先前的「不安装 / 不渲染」绝对表述由本次经批准的临时验证取代；仅限该临时环境，常规约定不变。

## Log

- 2026-10-14 记录「PDR / Current 手动渲染」候选：确认使用边界（用户触发、两套独立文档均适用、源须可读且渲染友好、工具不固定、绝不自动安装 / 构建 / 渲染、尊重项目覆盖）；实现未获批准，工具 / 格式 / 导航 / 交叉链接 / 产物管理推迟。此为候选，未做任何渲染相关改动（workflow 本轮因 Current 拆分另有变更）。
- 2026-10-14 用户授权，**取代**先前「工具不固定」方向：选定 Sphinx + MyST + RTD 主题，以第一方 `/docs-html-view` 手动分发；渲染范围定为 PDR + Current + 完整 ADR（含退役 / 墓碑桩），不含 issues / agents。本条目由 `suggestion` 升为 feature（`Status: doing`）。
- 2026-10-14 范围变更（简化）：用户推翻最初的过度设计——改为小依赖脚本 + 标准 `sphinx-quickstart` + 标准 `make html` / `sphinx-build` + 可选导航脚本；移除自研渲染编排器 / fingerprint / manifest / 鉴权状态机 / staged publisher；同意改为技能交互；三态由标准 Sphinx 退出码 / 警告解读，`make` 失败可留陈旧 / 部分产物且不声称新构建成功。源不可变 / 范围 / 描述性 ADR 链接 / 手动同意与环境 / 输出 `build/html` 不变。仍待实际验证证据，故保持 `doing`。
- 2026-10-14 完成：简化版可手动运行；经用户单独批准的临时环境（`/tmp/opencode/docs-html-view-verify.6JyvhY`，Python 3.14.4）验证通过——真实 `sphinx-quickstart` + 标准 `make html` CLEAN、源哈希不变、范围 / 链接 / 排除正确、guard 17 fixture 通过、包安装字节一致。仓库 / 用户 / 系统环境仍未安装、未做 site init，仓库仍无 `pdr` / `current` / `adr`。归档为 `-done`。
