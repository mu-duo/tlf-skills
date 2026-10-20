# 轻型任务专用 Skill

> Status: done ｜ 责任: agent ｜ 创建: 2026-10-15 ｜ 关联: [测试治理与可选Skill](../../suggestion/agent/测试治理与可选Skill.md) ｜ [模糊PDR与探索式开发模型](../../suggestion/agent/模糊PDR与探索式开发模型.md)

## 背景

用户提出为轻型任务新增专用 skill。本条目原为 `suggestion`（`docs/issues/suggestion/agent/轻型任务专用Skill.md`）；2026-10-16 与用户对齐全部待讨论问题后，确定本质是 **feature**，转入本目录并完成实现。

相关背景：

- 现有 `project-docs-workflow` 五步流程（规划 / 骨架 / 细节 / 异常 / 回顾）依赖 PDR / Current / issues / ADR 文档体系；本条目要的是**不依赖该文档体系**的轻型变体。

## 原始提议（保留，作为出发点）

- 新增轻型任务专用 skill：即「功能同步、骨架、实现」等步骤工作流；不必增加 docs 记录项目状态。

## 已对齐决定（2026-10-16）

- **形态**：独立 skill（独立于 `project-docs-workflow`）。
- **「功能同步」含义**：与用户对齐功能范围 / 验收标准（≈ 主流程的「规划」）。
- **步骤集合**：保留全部五步——功能同步 → 骨架 → 实现 → 异常 → 回顾；「轻型」体现在**不强制文档状态**，而非削减步骤。
- **docs 边界**：不强制创建 issue；一般仅产出代码。
- **适用边界**：小型、低风险、不涉及跨模块契约变更的任务；或用户显式启用。

## 完成判据

- [x] 新增独立 skill（`skills/lite-task/SKILL.md`）。
- [x] 接入本包分发：`bin/install.js` 第一方清单、`README.md`、`package.json`（`NOTICE` 不涉及）。
- [x] 按 `suggestion` 约定处理原条目（已转入 feature 并归档）。

## 步骤

- [x] 规划（完成判据与方案已对齐）
- [x] 骨架（skill 文件 + 接入安装器的最小可运行切片）
- [x] 细节（SKILL.md 与分发接入完整实现）
- [x] 异常（适用边界、与主流程的关系、升级路径已写明）
- [x] 回顾（分发接入一致性检查）

## 结果

- 新增第一方 skill `lite-task`（`skills/lite-task/SKILL.md`）：面向小型 / 低风险任务（或用户显式启用）的轻型开发流程；五步与 `project-docs-workflow` 一致（功能同步 / 骨架 / 实现 / 异常 / 回顾），但不强制 issue / PDR / Current / ADR，默认一般仅产出代码；任务变大时升级回 `project-docs-workflow`。
- 接入分发：`bin/install.js` 第一方清单（kind `lite-task`）、`README.md`（含新增 `lite-task` 章节）、`package.json` 描述；`NOTICE` 不涉及。
- 验证：`node bin/install.js --help` 与 `--dry-run` 均列出 `lite-task`，dry-run 未写入任何文件；`check` 退出 0。

遗留 / 待定（未擅自决定）：

- frontmatter 未加 `disable-model-invocation`，即允许模型按适用边界自动选用；若希望仅手动触发，改/删该行即可。
- 是否 bump `package.json` 版本由上架维护者决定（本次未改版本号）。
- 未在主 skill 的 references（如 `workflow.md` / `coexistence.md`）中交叉引用 `lite-task`。

## Log

- 2026-10-15 记录用户关于轻型任务专用 skill 的原始提议（功能同步 / 骨架 / 实现等步骤，不依赖 docs 记录项目状态）；供后续讨论，不是实现授权；未创建 skill，未改动 workflow。
- 2026-10-16 与用户对齐全部待讨论问题（形态 / 功能同步含义 / 步骤集合 / docs 边界 / 适用边界）；条目由 `suggestion` 转入 `feature`。
- 2026-10-16 实现 `lite-task` skill 并接入分发，验证通过；归档本条目。
