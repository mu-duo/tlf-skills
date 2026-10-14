# Development workflow

Default profile. Projects may override in their materialized `docs/agents/workflow.md`; that copy governs runtime behavior.

The default shape for developing a single issue: align, build a thin slice, fill it in, harden it, then sync docs. The flow is a recommendation — projects may override any step — but while it is in use, its one hard rule is that alignment and planning come before implementation.

## Work unit & granularity

- The work unit is the **issue** (see `issues.md`): one feature-level deliverable. Bug / chore use the same shape, simplified.
- **Granularity is a suggestion**, never forced: size a slice for a single reviewable push (heuristic ≈ 0.5 person-day), elastic per task.
- **Stage slicing is agent-perceived** — which slice of the feature to take next never becomes directories or files; the only materialized tracking is the issue's own `## 步骤` checklist. An optional one-line note inside the issue can make the current stage explicit.

## Alignment

- **Align before building**: implementation starts only after the alignment is done and the plan / steps are written (align → plan & steps → build).
- Alignment is **conversational and soft**: no freeze, no ceremonial "aligned" record. Re-align proactively when needs change (feature-requirement drift).
- On an ambiguous direction, invoke `grilling`（未安装则按 `references/deps/grilling.md` 执行）; `grill-me` is only an entry alias; `grill-with-docs` = `grilling` + `domain-modeling`（兜底 `references/deps/grilling.md` + `references/deps/domain-modeling.md`）.
- **Gap analysis** happens here, at Plan: read the PDR target plus Current state, derive **candidate** tasks (module / FR, suggested type, slice, acceptance criteria), and let the user pick. Differences are candidates only — a difference may be drift, a quality gap, unverified behavior, or an outdated target, not necessarily a missing feature; do not invent gaps. No idle auto-creation of issues.
- **Autonomy within scope**: once aligned, the agent implements autonomously inside the agreed scope, respecting ADRs, contracts, and security; high-cost, destructive, or hard-to-reverse decisions are confirmed with the user first.

## The five steps

1. **规划 / Plan** — refine acceptance criteria, set the step checklist status, and write a 1–2 sentence approach. Minimal output; no new sections. Gap analysis happens here.
2. **骨架 / Skeleton** — a minimal runnable vertical slice (ignore output / formatting polish); leave one piece of run evidence and show it to the user — the first review point. Skippable for pure fixes (Log the reason); mandatory for features and structural work.
3. **细节 / Details** — main-path implementation, detail completion, code quality. `tdd`（未安装则按 `references/deps/tdd.md` 执行）is an optional internal loop.
4. **异常 / Exceptions** — failure paths, boundaries, and stability after the main path. Real development blockers are handled immediately and Logged, never queued for this step.
5. **回顾 / Wrap-up review** (收尾回顾) — a lightweight docs-sync checklist at issue completion (pdr, current, adr, context, issues, agents); if nothing needs updating, one Log line. Doc sync only; session / agent retrospectives belong to `retro`（未安装则按 `references/deps/boundaries.md` 执行）.

## Progress & resume

- The issue entry carries a `## 步骤` checklist (the five steps); update it **in place**. The Log records only key events (scope change, blocker, handoff, abandonment), not every step change.
- **Sessions are soft.** A session is the user's attention window; the user controls pace (they may new / compact between issues). The agent must not absorb work beyond the aligned scope.
- **On resume**, read the issue's 步骤 plus Log first, then confirm the continuation point with the user.

## Docs sync hooks

- **Plan**: gap → issue candidates land in `docs/issues`; the entry's 关联 records the module / FR.
- **Wrap-up review**: check the change's effect on the Current tree (see `current.md`). If the completed change is part of the described state, update the affected Current docs **in place — facts only, never a self-link to the issue or task history**; otherwise leave them and record a pending sync item in the issue. Baseline advancement refreshes the relevant Current docs; actual state unchanged → no edit. Touch `adr` / `context` / `issues` / `agents` when the change warrants it.
- **Archival**: archive the issue per `issues.md` when done / dropped.

## Boundaries

- Large or high-risk multi-phase work → `deepwork`（未安装则按 `references/deps/boundaries.md` 执行）; never stack it with this flow.
- `tdd`（未安装则按 `references/deps/tdd.md` 执行）nests inside Details; seam confirmation folds into the Plan alignment (no second gate).
- `retro`（未安装则按 `references/deps/boundaries.md` 执行）owns session / agent retrospectives; the fifth step is docs sync only.
- Docs HTML rendering is optional and manual (`rendering.md`); it never runs as part of this flow — no auto-build on doc edits. See `coexistence.md` for how this profile sits beside these skills.
