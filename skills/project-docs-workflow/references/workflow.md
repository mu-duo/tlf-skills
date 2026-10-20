# Development workflow

Default profile. Projects may override in their materialized `docs/agents/workflow.md`; that copy governs runtime behavior.

The default shape for developing a single issue: align, build a thin slice, fill it in, harden it, then sync docs. The flow is a recommendation — projects may override any step — but while it is in use, its one hard rule is that alignment and planning come before implementation.

## Work unit & granularity

- The work unit is the **issue** (see `issues.md`): one feature-level deliverable. Bug / chore use the same shape, simplified.
- **Granularity is a suggestion**, never forced: size a slice for a single reviewable push (heuristic ≈ 0.5 person-day), elastic per task.
- **Stage slicing is agent-perceived** — which slice of the feature to take next never becomes directories or files; the only materialized tracking is the issue's own `## 步骤` checklist. An optional one-line note inside the issue can make the current stage explicit.

## What to read

- **Human entry**: the product L1 (`docs/prd/00-README.md`) then the module L1 (`docs/prd/<NN-module>/00-README.md`) — orientation only, no implementation detail.
- **Agent fact source**: the L2 spec files (`01-spec` / `02-interfaces` / `03-nfr` / `design/`) plus Current for as-built facts.
- **Navigation**: `docs/prd/00-index.md` and each module's `00-index.md` for module maps, reading order, conventions and traceability.
- **L1 is not a fact source.** On any conflict between L1 and L2, L2 wins.

## Alignment

- **Align before building**: implementation starts only after the alignment is done and the plan / steps are written (align → plan & steps → build).
- Alignment is **conversational and soft**: no freeze, no ceremonial "aligned" record. Re-align proactively when needs change (feature-requirement drift).
- On an ambiguous direction, invoke `grilling`（未安装则按 `references/deps/grilling.md` 执行）; `grill-me` is only an entry alias; `grill-with-docs` = `grilling` + `domain-modeling`（兜底 `references/deps/grilling.md` + `references/deps/domain-modeling.md`）.
- **Gap analysis** happens here, at Plan: read the L2 target plus Current state, derive **candidate** tasks (module / FR, suggested type, slice, acceptance criteria), and let the user pick. Differences are candidates only — a difference may be drift, a quality gap, unverified behavior, or an outdated target, not necessarily a missing feature; do not invent gaps. No idle auto-creation of issues.
- **Autonomy within scope**: once aligned, the agent implements autonomously inside the agreed scope, respecting ADRs, contracts, and security; high-cost, destructive, or hard-to-reverse decisions are confirmed with the user first.

## L1 reading order & maintenance

- **Human**: product L1 → module L1. L1 is the human narrative view of L2; the reader does not need L2 to get oriented.
- **Agent**: `00-index.md` for navigation → the L2 spec files plus Current for facts.
- **L1 never overrides L2.** L1 is derived and lossy; it adds no constraint. Conflict → L2.
- **Hybrid maintenance**: incremental patches when a change affects the narrative; full regeneration at baseline advance, module add/remove, ≥10 accumulated patches, or human request. Always show the diff.
- Keep the invisible marker `<!-- narrative-source: <L2 revision>; generated: <date> -->`.
- The human reviews the L1 diff for readability and factual plausibility; they do not need to read L2.

## Narrative impact trigger

Check these four items at wrap-up (and when planning a target change). There is no per-FR metadata and no extra tracking artifact.

1. An FR cited by L1 changes semantically → review / update L1.
2. A new or changed FR changes user-visible behaviour → add / update L1.
3. Internal-only change → L1 no-op, one log line.
4. Target user / core journey / scope / non-goals change → update L1.

## Change protocol

- **Target change**: Plan → update L2 first → update L1 in the same reviewable unit → human reviews the L1 diff and the target scope before production implementation (soft checkpoint; silence is not approval) → implement → wrap up Current.
- **In-scope implementation**: L2 / L1 no-op → implement → wrap up Current.
- **Internal / bug fix**: L2 / L1 no-op; Current if behavior changes; escalate to a target change when the bug exposes a wrong target.
- Prototypes / spikes are exempt until the direction is confirmed.
- Implemented details do not auto-promote into L2 or L1.

## Scope convergence

- **Default bias: converge the function space.** "Function space" is the user-facing alias for the state / solution space constrained by PRDs; do not introduce a second concept.
- **Trigger = a decision that changes the feature / scope target**, at PRD / ADR level (where the target is defined) or at issue-planning level.
- A feature candidate not covered by an existing PRD is an **expansion**: state a one-sentence rationale before proposing it. A candidate that implements an existing PRD is convergence / implementation and needs no extra rationale.
- Bug fixes and chores that restore or maintain existing behavior are exempt. If a bug / chore actually changes the feature set, reclassify it as a feature.
- This is a bias, not a gate: no new artifact, no blocking. Projects may override it.
- **Recording policy**: rejected alternatives are not recorded by default — see `adr.md` (Negative decisions) and `issues.md` (`-drop` archives). This policy constrains durable records only; alignment / grilling may still explore alternatives.

## The five steps

1. **规划 / Plan** — refine acceptance criteria, set the step checklist status, and write a 1–2 sentence approach. Minimal output; no new sections. Gap analysis happens here, reading the L2 target plus Current; L1 serves as human orientation only.
2. **骨架 / Skeleton** — a minimal runnable vertical slice (ignore output / formatting polish); leave one piece of run evidence and show it to the user — the first review point. Skippable for pure fixes (Log the reason); mandatory for features and structural work.
3. **细节 / Details** — main-path implementation, detail completion, code quality. `tdd`（未安装则按 `references/deps/tdd.md` 执行）is an optional internal loop.
4. **异常 / Exceptions** — failure paths, boundaries, and stability after the main path. Real development blockers are handled immediately and Logged, never queued for this step.
5. **回顾 / Wrap-up review** (收尾回顾) — a lightweight docs-sync checklist at issue completion (prd L1/L2, current, adr, context, issues, agents); if nothing needs updating, one Log line. Doc sync only; session / agent retrospectives belong to `retro`（未安装则按 `references/deps/boundaries.md` 执行）.

## Progress & resume

- The issue entry carries a `## 步骤` checklist (the five steps); update it **in place**. The Log records only key events (scope change, blocker, handoff, abandonment), not every step change.
- **Sessions are soft.** A session is the user's attention window; the user controls pace (they may new / compact between issues). The agent must not absorb work beyond the aligned scope.
- **On resume**, read the issue's 步骤 plus Log first, then confirm the continuation point with the user.

## Docs sync hooks

- **Plan**: gap → issue candidates land in `docs/issues`; the entry's 关联 records the module / FR.
- **Wrap-up review**:
  - **L1 check** (the four narrative-impact items): a cited FR changed semantically, or user-visible behaviour changed, or the target / scope moved → patch or regenerate L1 and show the diff; otherwise log one line stating L1 is a no-op. Also verify mechanically: every FR ID cited in L1 exists in L2 (missing → L1 drift: fix L1, or add to L2 only for a target change), and L1 has no external links and no status markers.
  - **Current check**: confirm the completed change is included in the selected baseline. Yes → update the affected Current docs **in place — facts only, never a self-link to the issue or task history**; no → leave them and record a pending sync item in the issue. Baseline advancement refreshes the relevant Current docs; actual state unchanged → no edit.
  - **prd (L1 / L2)**: L2 target changes land in the same reviewable unit as the L1 update.
  - Touch `adr` / `context` / `issues` / `agents` when the change warrants it.
- **Archival**: archive the issue per `issues.md` when done / dropped.

## Boundaries

- Large or high-risk multi-phase work → `deepwork`（未安装则按 `references/deps/boundaries.md` 执行）; never stack it with this flow.
- `tdd`（未安装则按 `references/deps/tdd.md` 执行）nests inside Details; seam confirmation folds into the Plan alignment (no second gate).
- `retro`（未安装则按 `references/deps/boundaries.md` 执行）owns session / agent retrospectives; the fifth step is docs sync only.
- Docs HTML rendering is optional and manual (`rendering.md`); it never runs as part of this flow — no auto-build on doc edits. See `coexistence.md` for how this profile sits beside these skills.
