---
name: deepwork
description: 高成本、多阶段、高风险深度工作会议的边界占位；与五步流程互斥，需要完整工作流时请另行安装。
disable-model-invocation: true
---

# Deepwork（边界占位）

本 skill 只界定边界，不含完整流程；需要完整的 deepwork 工作流时请单独安装。

- **适用**：成本高、风险大、需跨多个阶段推进的整块工作。
- **互斥**：与 `project-docs-workflow` 的五步流程（规划 / 骨架 / 细节 / 异常 / 回顾）互斥——同一个 effort 只能选一个，绝不叠加。
- **无完整 deepwork 时**：退回一个最小的分阶段计划，每个阶段设评审闸门：计划 → 实现 → 评审，逐阶段推进。

术语或 ADR 需求交给 `domain-modeling`。
