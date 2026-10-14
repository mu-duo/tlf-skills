# Issue tracker

Default profile. Projects may override in their materialized `docs/agents/issues.md`; that copy governs runtime behavior.

## Directory contract

```
docs/issues/
├── bug/{human,agent}/        # defect fixes
├── feature/{human,agent}/    # new features
├── chore/{human,agent}/      # maintenance / refactor / misc
├── suggestion/{human,agent}/ # improvement ideas (no history, no status; terminus ADR / PDR)
└── <bug|feature|chore>/history/   # archived: filename suffixed -done / -drop
```

- `human/` and `agent/` = current responsible party. Transfer responsibility with `git mv` to the other directory.
- Keep near-term work only (~1-week window). Whoever finishes or abandons an entry archives it; humans sweep periodically.
- `history/` holds archived entries: suffix the filename `-done.md` (completed) or `-drop.md` (abandoned).
- `suggestion` is special: no `history/`, no status.

## Entry format

- An issue is the workflow's work unit: one feature-level deliverable (bug / chore share the shape, simplified). See `workflow.md`.
- Filename: short title in the project language, no number (e.g. `修复-波形首屏卡顿.md`). Archive by adding the status suffix.
- Metadata line: `> Status: open|doing|blocked | 责任: human|agent | 创建: YYYY-MM-DD | 关联: ...` (关联 holds links such as `ADR-XXXX` or other entries).
- Body: background and goal, as prose.
- `## 完成判据` — completion criteria.
- `## 结果（完成后填写，可选）` — outcome, filled in on completion (optional).
- `## 步骤` — the five-step checklist from `workflow.md`; update it in place. Step changes need no Log entry by themselves. Materialized (Chinese) copies show:

  ```
  ## 步骤
  - [ ] 规划（完成判据与方案已对齐）
  - [ ] 骨架（最小可运行切片 + 证据；纯修复可跳过并注明理由）
  - [ ] 细节（主路径实现与质量）
  - [ ] 异常（失败路径、边界与稳定性）
  - [ ] 回顾（收尾回顾：文档同步）
  ```

- `## Log` — dated lines appended in place; existing lines are history and never rewritten. Record only key events, briefly: scope change, blocker, handoff, abandonment. Mechanical per-step entries are not required. A skipped-skeleton rationale on a pure fix is a legitimate key entry.
- `Status` is updated in place.
- Work that changes an ADR or PDR must sync those documents.
- If the skill is installed, the skeleton lives at `~/.agents/skills/project-docs-workflow/assets/templates/entries/issue-entry.md`; otherwise create from the format above.

## `suggestion` routing

When a suggestion is resolved:

- Accepted → land the conclusion in an ADR (or update the PDR), then remove the entry (`采纳 → 结论落 adr（或更新 pdr），随后删除本条目；`).
- Rejected → delete it. Record a rejection ADR only if a human explicitly asks.
- Actually a bug / feature / chore → move it to that directory.
