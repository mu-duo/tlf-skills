# 拆分 Current 与精简任务日志

> 完成: 2026-10-14 ｜ 责任: agent ｜ 创建: 2026-10-14 ｜ 关联: [模糊PDR与探索式开发模型](../../suggestion/agent/模糊PDR与探索式开发模型.md) ｜ [文档HTML渲染Skill](文档HTML渲染Skill-done.md)

## 背景与目标

按已批准行为，把 PDR 的现状文档（Current）从 PDR 规格中拆分出来，成为与 PDR 并列、用户可读的独立文档树；并精简任务日志，使其只记录**重要事件**而非逐阶段流水。批准的行为与形态决定见 [模糊PDR与探索式开发模型](../../suggestion/agent/模糊PDR与探索式开发模型.md)。

## 范围（已批准行为）

- 变更**规则 + 中文模板 + README**。
- **同步 / 迁移不覆盖**：init 只报告差异，绝不覆盖既有文档。
- 明确**不做**：不实现测试，不实现渲染 skill，不做 project init。

## 方案（简述）

在 `skills/project-docs-workflow` 内按批准行为更新规则 / 中文模板 / README：Current 拆为与 PDR 并列、用户可读的独立文档树（含 baseline + 版本 / 置信度），模块改为链接而非镜像，日志只进 issues / git；init 同步 / 迁移只报告差异、不覆盖。

## 完成判据

- 规则、中文模板、README 已按批准行为更新。
- 同步 / 迁移保持不覆盖边界。
- 未触及测试与渲染 skill；未做 project init。

## 步骤

- [x] 规划（完成判据与方案已对齐）
- [x] 骨架（纯文档变更，无最小可运行切片；不适用，理由见 Log）
- [x] 细节（主路径实现与质量）
- [x] 异常（失败路径、边界与稳定性）
- [x] 回顾（收尾回顾：文档同步）

## 结果

- 规则 / 中文模板 / README 已按批准行为更新；同步 / 迁移保持不覆盖边界；未触及测试与渲染 skill，未做 project init。
- 证据：`node bin/install.js check` PASS；`node bin/install.js install --dry-run --dir /tmp/opencode/current-split-check` PASS（无写入）；`git diff --check` PASS；临时 Python 校验 PASS（16 个 SKILL 引用 / 模板指针；已退役的 `pdr-current` 不存在；PDR 无 progress / 内嵌 current 且含 peer link；Current 选中基线 / 待同步 / 无自动化且含 peer link；全部 issue 相对链接）。
- 限制：未运行 project init / 既有项目迁移（属手动 skill 指令，非自动化 init 代码）；未安装渲染器 / 测试框架；未做 git commit / stage。仓库无实际 `docs/current`，因按范围不做项目初始化。
- 说明：初版校验器误纳入占位符 `<file>` 路径；修正后校验器排除占位符，非产品缺陷。

## Log

- 2026-10-14 按已批准行为创建本条目（feature，doing），记录范围 / 完成判据 / 步骤；关联模型条目与渲染候选。
- 2026-10-14 骨架跳过理由：本变更纯属文档（规则 / 模板 / README），无最小可运行切片，故骨架不适用；无运行证据。
- 2026-10-14 完成：规则 / 模板 / README 与 issue 链接校验通过；归档为 `-done`。
