# Current-state docs

Current = what the product **is now, as built**: actual capabilities, key behavior, and limits, each stated against a project-specified baseline. A peer tree to the PRD (`prd.md`), not a section of it. Default profile; overridable in project copies. Current is in the default render scope, together with the PRD tree and the complete ADR set (`rendering.md`).

## Structure

- `docs/current/00-README.md` — overview + navigation: it declares the **selected baseline** and, centrally, the verification-confidence convention, then indexes module / topic docs. No per-module status roll-up is required; link out.
- Module docs — one per module as needed; each records actual capabilities, key behavior, and limits. Claims inherit the overview's baseline and confidence; a module doc overrides the baseline only when it genuinely differs.
- Optional topic docs — cross-cutting areas (e.g. operations, data) added only when needed.
- Layering is overview → module → optional topics. Add only what the project actually has; there is no fixed schema.

The Current tree is **not numbered against PRD**: modules may align by name, but there is no file/paragraph mirroring. Link PRD modules / FRs explicitly and many-to-many.

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

## Relationship to PRD

- PRD = target (`prd.md`); Current = as-built. Two independent, user-readable trees; neither embeds the other.
- **Semantic / navigation / contract links** between the trees are expected — write ordinary relative Markdown links; there is no file/paragraph mirroring.
- A Current doc may point at an ADR with a **descriptive phrase + a stable path link** (e.g. `支持[离线使用](../../adr/0003-offline.md)`); the description is written independently and the ADR's rationale is not transcluded. ADR links are optional, and the profile never infers them (see `rendering.md`).
- Gap comparison reads both and yields **candidate** tasks for the user to choose — not every difference is a missing feature. A difference may be drift, a quality gap, unverified behavior, or an outdated target. An already-met coarse goal can still be refined; do not invent gaps.

## Adoption (existing projects)

- Existing docs are never overwritten or moved. If a project previously embedded current/progress material inside the PRD (e.g. per-module `04-current.md`, a 当前进展 section), init reports those paths as informational **legacy drift**. A pre-rename `docs/pdr/` tree is likewise informational legacy drift — never moved, rewritten, or deleted by init.
- Migrating to a separate Current tree, or from a legacy `docs/pdr/` to `docs/prd/`, is an explicit user decision; there is no installation migration script and no automatic move.
