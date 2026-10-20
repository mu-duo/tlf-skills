# Docs HTML rendering (docs-html-view)

Default profile; projects may override in their materialized copies.

Rendering is an **optional, user-triggered** capability provided outside this profile by the first-party `docs-html-view` skill. This profile only fixes the **doc contract** rendering relies on: what is rendered, how links are written, and that sources are never rewritten. It never installs, builds, renders, or activates anything, and init creates no renderer artifact.

## Default render scope (full site)

- **In scope**: `docs/prd/`, `docs/current/`, and the **complete** `docs/adr/` — retired entries and tombstone stubs included, with their retirement markers (`> 已废弃…` / `> 已删除…`) kept visible, so retired decisions stay navigable.
- **Out of scope**: `docs/issues/`, `docs/agents/` — working material, not published docs.
- **Product L1 is a prominent entry** in the full site: the product `docs/prd/00-README.md` is the designated "product overview" entry (configured via the renderer's `landing_page`), linked prominently above the toctree so readers start from the narrative.
- **`00-index.md` is secondary** — it renders as module navigation and traceability, not as the first read.
- A project may override the scope.

## L1-only render profile

- **In scope**: the product L1 (`docs/prd/00-README.md`) plus each module L1 (`docs/prd/<NN-module>/00-README.md`) — nothing else.
- **Out of scope**: L2 (`01-spec` / `02-interfaces` / `03-nfr` / `design/`), Current, ADR, and `00-index.md`.
- The output is a self-contained folder that can be zipped and distributed to readers who only need the product narrative.
- Because L1 must not link out, the L1-only build has no external targets to resolve; only internal anchors matter.

## Link authoring

- **L1 links**: internal only — same-file anchors, product L1 ↔ module L1, and module L1 ↔ module L1. Anchor targets are standard Markdown headings, h1–h3. No external links (`http` / `https` / `mailto`), no links to L2, Current, or ADR; those live in `00-index.md`.
- **PRD ↔ Current**: semantic / navigation / contract links between the two trees are expected (`prd.md`, `current.md`). Write ordinary relative Markdown links so both the source and the render navigate.
- **PRD / Current → ADR**: a **descriptive phrase + a stable path link** to the ADR file, e.g. `支持 [离线使用](../../adr/0003-offline.md)`. The description is written independently and stands on its own; the ADR's rationale is **not** transcluded or summarized. No requirement must carry an ADR, and the profile never infers ADR links automatically. This rule applies to L2 and Current, **not** to L1.
- The native `ADR-XXXX` citation notation is unchanged; ADR deletion / semantic edit sweeps **both** notations (`adr.md`).

## Sources are never rewritten

- The Markdown sources stay the single source of truth and remain human-readable on their own; the renderer is **read-only** toward them — no normalization, no move, no rewrite.
- Out-of-scope or dangling references are **reported**, never fixed in the source.
- "Nothing to render" is a **failure**, not a silent success; the renderer never bootstraps the docs workflow on its own.

## Manual, opt-in

- Rendering is **user-triggered and manual**: no hook, no auto-build on doc edits, no change to the main init artifacts to create a renderer.
- Install / init / first build only after explicit user consent obtained through the skill interaction; there is no custom orchestrator, manifest, or approval state machine.
- To integrate, point the project at the `docs-html-view` skill explicitly; do not wire it into initialization.
