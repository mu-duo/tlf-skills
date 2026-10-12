# Coexistence with other skills

## Scope

Single-context layouts. Multi-context (`CONTEXT-MAP.md`) is not covered by this profile.

## `domain-modeling`

Active model-sharpening conversations. The base CONTEXT and ADR formats are compatible. Where both apply, **this profile's materialized rules govern project docs** — it is a superset of the base formats (ADR lifecycle v2 (in-place edit + Log, delete→tombstone stub, reference sweep, catalog-style README); issue routing). Do not fork or redefine the base formats beyond this house variant.

Bundled lite version ships with the package; fallback doc `references/deps/domain-modeling.md`.

## `grill-with-docs`

A wrapper: `grilling` + `domain-modeling`. Unaffected. `grill-me` is only an entry alias of `grilling`.

Bundled lite `grilling` ships with the package; fallback doc `references/deps/grilling.md` (and `references/deps/domain-modeling.md`).

## `deepwork`

Large or high-risk multi-phase efforts run under `deepwork`. This profile's `workflow.md` is for routine single-issue development; the two are never stacked — pick one per effort.

Bundled lite version ships with the package; fallback doc `references/deps/boundaries.md`.

## `tdd`

Nests inside the Details step of `workflow.md` (red → green loop). Seam confirmation is folded into the Plan alignment — no second gate.

Bundled lite version ships with the package; fallback doc `references/deps/tdd.md`.

## `retro`

The workflow's fifth step 收尾回顾 is documentation sync only. Session / agent retrospectives belong to `retro`, not here.

Bundled lite version ships with the package; fallback doc `references/deps/boundaries.md`.

## `doc-opt`

Post-hoc prose polishing of named files. Ships with the package as a full bonus skill (`skills/doc-opt`), plus the fallback doc `references/deps/doc-opt.md`. Chain it after authoring if desired; explicit invocation only.

## Older `.scratch`-style trackers

Not used for issue tracking in these projects (DA_AGENT precedent: ADR-0012, refined by ADR-0026). This skill's `docs/issues` conventions supersede older `.scratch`-style tracking conventions.

A generic scaffolder writing the same surfaces (`docs/agents/domain.md`, an `## Agent skills` block, `CLAUDE.md` preference) is not used for scaffolding in projects on this profile; if one ran before, review its leftovers against this profile's rules (init reports diffs; never overwrites).

## Invocation

This skill is manual-invocation only. Runtime compliance for agents comes from the project's materialized files (`AGENTS.md` + `docs/agents/*`), not from auto-loading this skill.
