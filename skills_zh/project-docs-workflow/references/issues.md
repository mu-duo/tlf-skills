# Issue 跟踪

默认方案。项目可在物化的 `docs/agents/issues.md` 中覆盖；该副本决定运行时行为。

## 目录契约

```
docs/issues/
├── bug/{human,agent}/        # defect fixes
├── feature/{human,agent}/    # new features
├── chore/{human,agent}/      # maintenance / refactor / misc
├── suggestion/{human,agent}/ # improvement ideas (no history, no status; terminus ADR / PRD)
└── <bug|feature|chore>/history/   # archived: filename suffixed -done / -drop
```

- `human/` 与 `agent/` = 当前责任方。用 `git mv` 将责任移交到对方目录。
- 只保留近期工作（约一周窗口）。完成或放弃条目者负责归档；人类定期巡检。
- `history/` 存放归档条目：文件名加后缀 `-done.md`（完成）或 `-drop.md`（放弃）。
- `-drop.md` 是工作状态归档，不是否定决策。默认的「不记录被拒备选方案」规则（见 `adr.md`）不会删除或改写已放弃条目；issue 的 Log 仍可记录放弃原因。
- `suggestion` 特殊：无 `history/`、无状态。

## 条目格式

- issue 是工作流的工作单元：一个 feature 级交付物（bug / chore 同构，形态简化）。见 `workflow.md`。
- 文件名：项目语言短标题，无编号（例如 `修复-波形首屏卡顿.md`）。归档时添加状态后缀。
- 元数据行：`> Status: open|doing|blocked | 责任: human|agent | 创建: YYYY-MM-DD | 关联: ...`（关联存放 `ADR-XXXX` 或其他条目的链接）。
- 正文：背景与目标，以散文形式。
- `## 完成判据`——完成标准。
- `## 结果（完成后填写，可选）`——结果，完成时填写（可选）。
- `## 步骤`——来自 `workflow.md` 的五步清单；就地更新。步骤变化本身不需要 Log 记录。物化（中文）副本显示为：

  ```
  ## 步骤
  - [ ] 规划（完成判据与方案已对齐）
  - [ ] 骨架（最小可运行切片 + 证据；纯修复可跳过并注明理由）
  - [ ] 细节（主路径实现与质量）
  - [ ] 异常（失败路径、边界与稳定性）
  - [ ] 回顾（收尾回顾：文档同步）
  ```

- `## 测试`——`testing.md` 的三个固定槽位（执行 / 临时 / 落盘），收尾时填写。缺失即视为没交代；它是测试证据，绝不是任务历史或进度日志。
- `## Log`——就地追加带日期的行；已有行是历史，绝不改写。只简要记录关键事件：范围变化、阻塞、交接、放弃。不需要逐步机械记录。纯修复跳过骨架的理由属于正当的关键记录。
- `Status` 就地更新。
- 改动 ADR 或 PRD 的工作必须同步这些文档。
- issue 可以引用 FR / 文档。收尾更新 Current 树时只改**事实**——绝不插入指向 issue 的自链接或任务历史（见 `current.md`）。
- 若已安装该 skill，骨架位于 `~/.agents/skills/project-docs-workflow/assets/templates/entries/issue-entry.md`；否则按上述格式创建。

## `suggestion` 路由

当 suggestion 得到处理时：

- 采纳 → 将结论落到 ADR（或更新 PRD），然后删除该条目（`采纳 → 结论落 adr（或更新 prd），随后删除本条目；`）。
- 不采纳 → 删除它。仅在人类显式要求时才记录否决 ADR。
- 实际上是 bug / feature / chore → 移到对应目录。
