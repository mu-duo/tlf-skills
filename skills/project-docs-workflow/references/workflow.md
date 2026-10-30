# Development workflow

Default profile. Projects may override in their materialized `docs/agents/workflow.md`; that copy governs runtime behavior.

The default shape for developing a single issue: align, build a thin slice, fill it in, harden it, then sync docs. The flow is a recommendation — projects may override any step — but while it is in use, its one hard rule is that alignment and planning come before implementation.

## Roles & write permissions

- **User** — owns intent, scope, and approval. Reviews the PRD, SPEC, and ADRs.
- **Orchestrator** — maintains the PRD; composes the SPEC with the user; reviews PRD / SPEC diffs; owns `docs/toc.yml`; triggers publication; delegates coding.
- **Coder agent** — reads the SPEC, implements; updates Current facts at wrap-up; may propose SPEC changes through an issue; does **not** directly edit the PRD, SPEC, or TOC.
- **Single-agent setups** — one agent may play orchestrator + coder; role boundaries still apply, so the same agent switches hats explicitly.

## Work unit & granularity

- The work unit is the **issue** (see `issues.md`): one feature-level deliverable. Bug / chore use the same shape, simplified.
- **Granularity is a suggestion**, never forced: size a slice for a single reviewable push (heuristic ≈ 0.5 person-day), elastic per task.
- **Stage slicing is agent-perceived** — which slice of the feature to take next never becomes directories or files; the only materialized tracking is the issue's own `## 步骤` checklist. An optional one-line note inside the issue can make the current stage explicit.

## What to read

- **Intent & scenarios**: the PRD — product `docs/product/00-README.md`, `01-requirements.md`, `02-architecture.md`, then the module PRD (`docs/product/<NN-module>/00-README.md`). Orientation for scope, never an implementation fact source.
- **Implementation facts**: the SPEC files (`01-spec` / `02-interfaces` / `03-nfr` / `design/`).
- **As-built**: Current (`docs/current/`) for what actually works now.
- **Publication**: `docs/toc.yml` for the published document set.
- **Tests**: `docs/agents/testing.md` — the rules that govern writing or changing tests. First priority; `tdd` supplies mechanics only.
- **Conflict**: implementation detail → SPEC wins; scope / intent → PRD wins; if still unclear, escalate to the orchestrator / user.

## Alignment

- **Align before building**: implementation starts only after the alignment is done and the plan / steps are written (align → plan & steps → build).
- The orchestrator + user compose or align the SPEC; the coder implements it. If the scope or intent changes, update the PRD first.
- Alignment is **conversational and soft**: no freeze, no ceremonial "aligned" record. Re-align proactively when needs change (feature-requirement drift).
- On an ambiguous direction, run `references/deps/grilling.md`; `grill-me` is only an entry alias; `grill-with-docs` = `references/deps/grilling.md` + `references/deps/domain-modeling.md`, interleaved.
- **Gap analysis** happens here, at Plan: read the SPEC target plus Current state, derive **candidate** tasks (module / FR, suggested type, slice, acceptance criteria), and let the user pick. Differences are candidates only — a difference may be drift, a quality gap, unverified behavior, or an outdated target, not necessarily a missing feature; do not invent gaps. No idle auto-creation of issues.
- **Autonomy within scope**: once aligned, the agent implements autonomously inside the agreed scope, respecting ADRs, contracts, and security; high-cost, destructive, or hard-to-reverse decisions are confirmed with the user first.

## Change protocol

- **PRD change** (scope / intent / target user / typical scenarios / non-goals): align with the user, update the PRD after alignment, and update the SPEC if the requirements change; the human reviews the PRD diff. Never let the coder rewrite the PRD directly.
- **SPEC change** (implementation detail, FR semantics, interfaces, NFR): the user + orchestrator compose it; the coder may propose through an issue; the human / orchestrator reviews before implementation.
- **Current change**: the coder updates the facts at wrap-up against the selected baseline; the orchestrator reviews.
- **ADR**: record decisions with rationale and trade-offs; an ADR is a peer document, not a step in this protocol.
- **Conflict**: SPEC wins on implementation details, PRD wins on scope; escalate when the two cannot be reconciled.
- Prototypes / spikes are exempt until the direction is confirmed.
- Implemented details do not auto-promote into the PRD or SPEC.

## PRD impact trigger

Check these four items at wrap-up (and when planning a scope change). There is no per-FR metadata and no extra tracking artifact.

1. A requirement cited by the PRD changes semantically → review / update the PRD.
2. A new or changed FR changes user-visible behavior → add / update the PRD.
3. Internal-only change → PRD no-op, one log line.
4. Target user / typical scenario / scope / non-goals change → update the PRD.

## Scope convergence

- **Default bias: converge the function space.** "Function space" is the user-facing alias for the state / solution space constrained by the PRD; do not introduce a second concept.
- **Trigger = a decision that changes the feature / scope target**, at PRD / ADR level (where the target is defined) or at issue-planning level.
- A feature candidate not covered by an existing PRD is an **expansion**: state a one-sentence rationale before proposing it. A candidate that implements an existing PRD is convergence / implementation and needs no extra rationale.
- Bug fixes and chores that restore or maintain existing behavior are exempt. If a bug / chore actually changes the feature set, reclassify it as a feature.
- This is a bias, not a gate: no new artifact, no blocking. Projects may override it.
- **Recording policy**: rejected alternatives are not recorded by default — see `adr.md` (Negative decisions) and `issues.md` (`-drop` archives). This policy constrains durable records only; alignment / grilling may still explore alternatives.

## The five steps

1. **规划 / Plan** — the orchestrator + user confirm scope and align the SPEC; the coder refines acceptance criteria, sets the step checklist status, and writes a 1–2 sentence approach. Minimal output; no new sections. Gap analysis happens here, reading the SPEC target plus Current; the PRD serves as human orientation only.
2. **骨架 / Skeleton** — a minimal runnable vertical slice (ignore output / formatting polish); leave one piece of run evidence and show it to the user — the first review point. Skippable for pure fixes (Log the reason); mandatory for features and structural work.
3. **细节 / Details** — main-path implementation, detail completion, code quality. Any test work follows `docs/agents/testing.md` (run / temporary / persistent tiers; temporary tests are deleted before wrap-up); `tdd` (`references/deps/tdd.md`) is an optional internal red → green loop, subordinate to those rules.
4. **异常 / Exceptions** — failure paths, boundaries, and stability after the main path; their tests follow the same test rules (defense-layer ownership, no weak assertions). Real development blockers are handled immediately and Logged, never queued for this step.
5. **回顾 / Wrap-up review** (收尾回顾) — a lightweight docs-sync checklist at issue completion: the coder updates Current facts and proposes SPEC changes; the orchestrator reviews PRD / SPEC / Current and updates the TOC if modules or appendices changed; `adr` / `context` / `issues` / `agents` as needed. The issue's `## 测试` section is filled (execution evidence, temporary outcome, persistent trace) and scratch tests are gone. If nothing needs updating, one Log line. Doc sync only; session / agent retrospectives belong to `retro` (`references/deps/boundaries.md`).

## Progress & resume

- The issue entry carries a `## 步骤` checklist (the five steps); update it **in place**. The Log records only key events (scope change, blocker, handoff, abandonment), not every step change.
- **Sessions are soft.** A session is the user's attention window; the user controls pace (they may new / compact between issues). The agent must not absorb work beyond the aligned scope.
- **On resume**, read the issue's 步骤 plus Log first, then confirm the continuation point with the user.

## Docs sync hooks

- **Plan**: gap → issue candidates land in `docs/issues`; the entry's 关联 records the module / FR.
- **Wrap-up review**:
  - **PRD check** (the four impact items): a cited requirement changed semantically, or user-visible behavior changed, or the target / scope moved → patch the PRD and show the diff; otherwise log one line stating the PRD is a no-op. The orchestrator reviews the PRD diff.
  - **SPEC check**: the coder proposes necessary SPEC changes through the issue; the user + orchestrator compose and confirm them. The coder never edits the SPEC directly.
  - **Current check**: confirm the completed change is included in the selected baseline. Yes → update the affected Current docs **in place — facts only, never a self-link to the issue or task history**; no → leave them and record a pending sync item in the issue. Baseline advancement refreshes the relevant Current docs; actual state unchanged → no edit.
  - Touch `adr` / `context` / `issues` / `agents` when the change warrants it.
- **Archival**: archive the issue per `issues.md` when done / dropped.

## TOC maintenance & publication

- `docs/toc.yml` is the publication source. The orchestrator / agent updates it when modules or appendices change; the user may edit it directly. All paths must exist and stay inside the allowed roots (`docs/product`, `docs/current`, `docs/adr`, or root `CONTEXT.md`; see `prd.md`).
- Publication is **manual and outside the five steps**: after the PRD / SPEC / Current change, the user may trigger `docs-html-view` to build the multi-page PRD. No auto-build on doc edits, and no renderer artifact is created by init (`rendering.md`).

## Boundaries

- Large or high-risk multi-phase work → `references/deps/boundaries.md`; never stack it with this flow.
- `tdd` (`references/deps/tdd.md`) nests inside Details; seam confirmation folds into the Plan alignment (no second gate). The test rules (`docs/agents/testing.md`, source `references/testing.md`) always apply and take priority over `tdd`.
- `retro` (`references/deps/boundaries.md`) owns session / agent retrospectives; the fifth step is docs sync only.
- Existing projects without product docs → consent-gated bootstrap (`bootstrap.md`). v4/older docs → migration (`migration.md`). Neither runs automatically inside this flow.
- Docs HTML rendering is optional and manual (`rendering.md`); it never runs as part of this flow — no auto-build on doc edits. See `coexistence.md` for how this profile sits beside these skills.
