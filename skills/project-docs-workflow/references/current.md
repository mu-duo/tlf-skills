# Current-state docs

Current = what the product **is now, as built**: capabilities, key behavior, and limits, stated against a project-specified baseline. A peer tree beside the PRD and SPEC (`prd.md`), not a section of either. Default profile; overridable in project copies. Published with the PRD and SPEC appendices (`rendering.md`).

**The PRD is status-free; Current is the only status source.** The PRD narrates the target and carries no progress, status markers, or as-built claims. What works now is read here.

## Structure

- `docs/current/00-README.md` — overview + navigation: it declares the **selected baseline** and, centrally, the verification-confidence convention, then indexes module / topic docs. No per-module status roll-up is required; link out. It links to the PRD cover at `../product/00-README.md`.
- Module docs — one per module as needed; each records actual capabilities, key behavior, and limits. Claims inherit the overview's baseline and confidence; a module doc overrides the baseline only when it genuinely differs.
- Optional topic docs — cross-cutting areas (e.g. operations, data) added only when needed.
- Layering is overview → module → optional topics. Add only what the project has; there is no fixed schema.

The Current tree is **not numbered against the PRD**: modules may align by name, but there is no file/paragraph mirroring. Link PRD modules / FRs explicitly and many-to-many.

## Who writes it

- The **coder agent** updates Current facts at issue wrap-up, against the selected baseline.
- The **orchestrator** reviews the Current diff.
- Nobody writes task history, todos, or planned work here.

## What a Current doc records

- **Baseline** — the **selected** baseline: a concrete revision / release plus the snapshot date. The project selects it explicitly; if none is chosen, ask the user — never silently default to `main` or the latest release. A mutable branch name alone is not a snapshot id; pin a revision or release.
- **Actual capabilities** — what works now, in behavior terms.
- **Limits and known constraints** — what does not work, downside, boundaries, caveats.
- **Verification confidence** — how claims were established (tested / observed / inferred). Declare the norm centrally in the overview; state confidence per claim only where it matters (an exception), not repetitively for every claim.

Do not record: task logs, todos, planned / future capabilities, per-issue progress. Those live in `docs/issues/` and the PRD. An issue wrap-up updates the affected Current **facts in place**; it never inserts a self-link to the issue or task history.

## Sync

- Current follows the **selected baseline**: record only changes included in that baseline. Refresh the affected Current docs when the baseline advances; a change not included in the selected baseline is not Current yet. Actual state unchanged → no edit.
- Issue wrap-up **checks** whether the completed change is included in the selected baseline: yes → update the affected Current docs; no → leave them and record a pending sync item in the issue.
- There is no automation or hook that writes Current. Sync is a review step, not a generated artifact.

## Relationship to PRD / SPEC

- PRD = target narrative, SPEC = implementation facts, Current = as-built. The PRD and Current are independent trees: neither embeds the other, and the PRD is not a fact source. Relative Markdown links between them are expected — there is no file/paragraph mirroring.
- Current may link to the PRD, SPEC, or ADR; the PRD must not link back to Current, SPEC, or ADR.
- ADR links use a descriptive phrase + stable path (e.g. `支持[离线使用](../../adr/0003-offline.md)`); form and non-transclusion rules live in `adr.md`.
- Gap comparison reads SPEC + Current and yields **candidate** tasks: a difference may be drift, quality, unverified behavior, or an outdated target. Never invent gaps.

## Adoption (existing projects)

- Existing docs are never overwritten or moved. A v4 `docs/prd/` tree, an embedded current/progress section in the PRD (e.g. per-module `04-current.md`, a 当前进展 section), or a pre-rename `docs/pdr/` tree is informational legacy drift — detected by init, never moved, rewritten, or deleted (`migration.md`).
- Migrating to a separate Current tree, or from v4 to v5, is an explicit user decision; there is no automatic move.
