---
name: lite-task
description: "Lightweight development workflow for small, low-risk tasks, or when the user explicitly opts in — the same five steps as project-docs-workflow (功能同步 / 骨架 / 实现 / 异常 / 回顾) without its documentation system: no forced issue, PDR, Current, or ADR bookkeeping; generally code only."
---

# Lite Task

A lightweight development workflow for **small, low-risk tasks**. It keeps the step discipline of `project-docs-workflow` but drops its documentation obligations: no forced issue entry, no PDR / Current / ADR bookkeeping. It generally produces code only.

## When to use

- Small, low-risk tasks that do **not** change cross-module contracts; or
- The user explicitly opts into this lite workflow.

Otherwise use `project-docs-workflow` (or the project's own materialized workflow). If a lite task turns out to need durable documentation state — a decision, a contract change, a status record — stop and escalate to `project-docs-workflow`; do not silently write docs here. Large or high-risk multi-phase work is out of scope; use `project-docs-workflow` (or `deepwork`).

## The five steps

Same step set and intent as `project-docs-workflow`, lighter in output:

1. **功能同步 / Sync** — align the feature scope and acceptance criteria with the user (equivalent to `project-docs-workflow`'s 规划). Implementation starts only after this alignment.
2. **骨架 / Skeleton** — a minimal runnable vertical slice; leave one piece of run evidence and show it to the user (the first review point). Skippable for pure fixes.
3. **实现 / Implement** — main-path implementation, detail completion, code quality.
4. **异常 / Exceptions** — failure paths, boundaries, and stability after the main path. Real blockers are handled immediately.
5. **回顾 / Wrap-up** — a brief self-check. Docs sync happens only when the change actually warrants it (see below).

Steps are agent-perceived: they are not required to materialize as files, directories, or an issue checklist.

## Docs boundary

- **No issue entry is required**, and there is no forced `## 步骤` tracking.
- **No PDR / Current / ADR updates are required.**
- Generally the only artifacts are code and git commit messages.
- If a durable decision or contract change appears, escalate to `project-docs-workflow` instead of writing docs inline.

## Relationship to `project-docs-workflow`

- Pick **one** flow per task; never stack the two.
- Same step names and intent; the difference is the documentation obligation (this flow: none by default).
- Escalate to `project-docs-workflow` when the task grows (contract change, cross-module impact, durable decision) or when the user asks for the documented flow.
