# 遗留 bootstrap（有代码、无产品文档）

Bootstrap 是**需用户同意**的路径，面向已有源码但没有 PRD / SPEC 的项目。它从代码库起草 v5 文档；用户评审前，草稿绝不当作事实。

## 触发

满足任一条件时使用 bootstrap：

- 没有 `docs/product/`，但存在源码。
- 只有 `CONTEXT.md` 和 / 或 `docs/adr/`，没有 PRD / SPEC。

init 检测到该状态，并在写入任何内容前**询问用户**。这不是常规 init 运行。

## 提示选项

用项目的文档语言询问一次：

1. **Bootstrap**——执行下方五个阶段，产出经评审的草稿。
2. **仅模板**——按模板创建空的 v5 骨架；不建模、不推断。
3. **跳过**——完全不写；仅报告。

没有明确选择，绝不开始 bootstrap 阶段。

## 五个阶段

1. **领域建模**——调用 `domain-modeling`（已安装则按名称；兜底 `references/deps/domain-modeling.md`）**一次**。产出或更新 `CONTEXT.md` 与 ADR。术语与决策由用户确认后才用于后续阶段。
2. **现状**——阅读代码、测试与配置。起草 `docs/current/` 作为实际建成快照：能力、限制、验证信心。向用户询问**选定基线**（revision / release + 日期）；绝不默认 `main` 或最新 release。
3. **PRD 草稿**——起草产品三章：`00-README.md`（一句话、项目说明、目标用户 / 问题、典型应用场景）、`01-requirements.md`（能力地图、关键行为、非目标、约束）、`02-architecture.md`（架构总览、模块划分、模块 PRD 链接）。只为用户确认的模块起草模块 PRD。
4. **SPEC 草稿**——依据代码与测试起草 `01-spec.md`（FR ID + 验收判据）、`02-interfaces.md`、`03-nfr.md`。**只有已确认项进入 SPEC。** 推断、模糊或待定项进入 bootstrap issue 清单——不得污染 SPEC。
5. **用户评审**——展示草稿与逐文件 diff；用户逐项确认、修正或否决。确认后文档成为事实。

## 产出是草稿

- 五个阶段完成前，bootstrap 产出都是草稿。不要发布，也不要在评审前把它当作实现事实标准。
- 绝不覆盖现有文件。展示 diff，由用户决定。
- 创建**一个** `docs/issues/chore/agent/...` bootstrap issue 跟踪阶段与推断 / 待定项。它是 bootstrap 的验收清单。
- 用户选择 Bootstrap 后，本 skill 可调用一次 `domain-modeling`。常规 init 或对齐期间不调用。

## 仅模板

创建空的 v5 骨架：`docs/product/00-README.md`、`01-requirements.md`、`02-architecture.md`、`docs/toc.yml`、`docs/current/00-README.md`、`docs/adr/README.md`、`CONTEXT.md`、`docs/agents/*`、issue 树，以及 `AGENTS.md` 区块。不推断内容。

## 跳过

什么都不写——连非产品产物也不写。仅报告检测到的状态与可用选项。
