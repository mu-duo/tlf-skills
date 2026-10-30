# Coexistence with other skills

## Scope

Single-context layouts. Multi-context (`CONTEXT-MAP.md`) is not covered by this profile.

## Bundled capabilities

Every dependency capability resolves to its copy under `references/deps/` (materialized as `docs/agents/deps/`). No external skill is invoked by name, even when one is installed — the bundled copy is the contract this profile is aligned with. External skills may still be installed for other projects; this profile ignores them.

## `domain-modeling`

Active model-sharpening conversations. The base CONTEXT and ADR formats are compatible. Where both apply, **this profile's materialized rules govern project docs** — a superset of the base formats (ADR lifecycle v2: in-place edit + Log, delete → tombstone stub, reference sweep, catalog-style README; issue routing). Do not fork the base formats beyond this house variant.

Bundled: `references/deps/domain-modeling.md`.

## `grill-with-docs`

A wrapper: `grilling` + `domain-modeling`, **interleaved** — as each grilling round surfaces terms or decisions, they are written down immediately: a settled term goes into `CONTEXT.md`; a decision meeting the three ADR criteria (hard to reverse / surprising without context / real trade-off) is recorded as an ADR. `grill-me` is only an entry alias of `grilling` and has no separate flow.

Bundled: `references/deps/grilling.md` + `references/deps/domain-modeling.md`.

## `deepwork`

Large or high-risk multi-phase efforts run under `deepwork`. This profile's `workflow.md` is for routine single-issue development; the two are never stacked — pick one per effort.

Bundled: `references/deps/boundaries.md`.

## `tdd`

Nests inside the Details step of `workflow.md` (red → green loop). Seam confirmation is folded into the Plan alignment — no second gate.

Mechanics only: the test rules (`docs/agents/testing.md`, source `references/testing.md`) always apply and take priority.

Bundled: `references/deps/tdd.md`.

## `retro`

The workflow's fifth step 收尾回顾 is documentation sync only. Session / agent retrospectives belong to `retro`, not here.

Bundled: `references/deps/boundaries.md`.

## `doc-opt`

Post-hoc prose polishing of named files. Bundled: `references/deps/doc-opt.md`. The full first-party `doc-opt` skill is an optional explicit upgrade — it is never resolved automatically.

## Older `.scratch`-style trackers

Not used for issue tracking in these projects (DA_AGENT precedent: ADR-0012, refined by ADR-0026). This skill's `docs/issues` conventions supersede older `.scratch`-style tracking conventions.

A generic scaffolder writing the same surfaces (`docs/agents/domain.md`, an `## Agent skills` block, `CLAUDE.md` preference) is not used for scaffolding in projects on this profile; if one ran before, review its leftovers against this profile's rules (init reports diffs; never overwrites).

## Invocation

This skill is manual-invocation only. Runtime compliance for agents comes from the project's materialized files (`AGENTS.md` + `docs/agents/*`), not from auto-loading this skill.
