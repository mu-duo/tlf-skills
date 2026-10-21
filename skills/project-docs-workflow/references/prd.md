# PRD, SPEC, Current, and ADR

PRD = Product Requirements Document: the **macro product narrative** — what the product is for, who it serves, the typical scenarios, the high-level product requirements, and the architecture / module overview. It is the authority on **scope and intent**.

SPEC = technical specification: the **normative implementation detail and fact standard** — functional requirements with acceptance criteria, interfaces, non-functional requirements, and optional mechanism design. It is the authority on **implementation details**.

Current = the **as-built snapshot** at a selected baseline. It is the only status source. ADR = a decision record with its rationale; a **peer** of these documents, not a layer. Issue = the work unit.

## Document model

| Document | Audience | Role | Wins on |
| :--- | :--- | :--- | :--- |
| **PRD** | user / orchestrator / reviewer | macro product narrative | scope, intent, user journey |
| **SPEC** | coder agent / orchestrator | implementation fact standard | implementation details |
| **Current** | everyone | as-built snapshot at a selected baseline | actual status |
| **ADR** | everyone | decision + rationale (peer) | why a decision was made |
| **Issue** | orchestrator / coder | work unit | — |

The PRD is the macro narrative of the SPEC; the SPEC serves the PRD's goals. Current is the only status source; an ADR is the only "why" source.

## Directory structure

```
docs/
  toc.yml
  product/
    00-README.md              # PRD: cover + project description + typical scenarios
    01-requirements.md        # PRD: high-level product requirements
    02-architecture.md        # PRD: architecture overview + module map
    <NN-module>/
      00-README.md            # module PRD
      00-index.md             # agent sidecar (not published)
      01-spec.md              # SPEC
      02-interfaces.md        # SPEC
      03-nfr.md               # SPEC
      design/                 # SPEC (optional; excluded from publication by default)
  current/
  adr/
  docsHtmlView/               # publication workspace (docs-html-view)
    conf.py
    guard.py
    index.md                  # generated cover + TOC
    nav/**                    # generated section pages
    glossary.md               # generated from root CONTEXT.md
    _manifest.json            # generated exact include list
    _meta.json                # generated title/version/date/abstract
    build/html                # output
CONTEXT.md                    # project root glossary source
```

- There is a **single `docs/product/` tree**. The product `00-index.md` is retired; only a module `00-index.md` remains, as an unpublished agent sidecar.
- `docs/prd/` is the v4/legacy layout. It is detected and offered for migration (`migration.md`); it is never rewritten during init.

## PRD contract

The PRD is a macro narrative. It explains what the product is and should become, not how it is built.

### Product PRD (three chapters)

- `00-README.md` — cover and project description: one-liner, project description, target users and the problem, and 3–5 typical scenarios.
- `01-requirements.md` — high-level product requirements: capability map, key behaviors, non-goals, and shape constraints. FR IDs may be cited as **plain text**; never copy acceptance criteria.
- `02-architecture.md` — architecture overview and module map; key constraints; links to the module PRDs.

### Module PRD

Each `docs/product/<NN-module>/00-README.md` states what the module enables, its key behaviors, its boundaries and its non-goals. It is 0.5–1 page. It carries no doc map, dependencies, interface ownership, or traceability — those live in the module `00-index.md`.

### PRD-layer links only

- Allowed: same-file anchors, product chapter ↔ product chapter, product chapter ↔ module PRD, and module PRD ↔ module PRD.
- Forbidden: links to SPEC files, Current, ADR, `http(s)` / `mailto`, or any external target.
- Navigation and traceability (including links to SPEC / Current / ADR) live in the module `00-index.md` or the SPEC layer, never in the PRD.

### Detail ceiling

Forbidden in the PRD: acceptance-criteria text, interface signatures, fields / schemas, error codes, state-machine details, implementation-internal names or steps, and performance numbers. Allowed: user-visible behavior, capability names, user outcomes, plain-language constraints.

### Status

No status markers (✅ / 🚧 / ❌), no roadmap, no progress, no task history.

### Banner

Every PRD file (product chapters and module PRDs) opens with:

`本文档描述产品目标与方案，不代表当前实现状态；实现细节见 SPEC，现状见 Current。`

### Length

Each product chapter ≤ ~2 pages; a module PRD 0.5–1 page. If the product narrative outgrows this, split by independently owned product area: the product chapters keep the whole-product view and link to area module PRDs.

### Maintenance

The orchestrator maintains the PRD with the user; humans review the PRD diff for readability and intent. Always show the diff. On conflict with the SPEC over implementation details, the SPEC wins.

## SPEC contract

- FR IDs are stable, never reused, and continuous per module; in the PRD they are plain text.
- Every FR carries acceptance criteria (验收判据).
- Interfaces are owned by the providing module; consumers reference them.
- NFRs live in `03-nfr.md`; mechanism-level design is optional in `design/`.
- The SPEC is authored by the user + orchestrator. The coder agent reads it and may **propose** changes through an issue; it does not edit the SPEC directly.
- Implemented details do not auto-promote into the SPEC.
- On implementation-detail conflicts the SPEC wins; on scope / intent conflicts the PRD wins.

## TOC contract

- `docs/toc.yml` is the **publication source**, consumed by the first-party `docs-html-view` skill. Only TOC-listed documents are published.
- Metadata: `title`, `version`, `date`, `abstract`.
- Required section ids: `overview`, `requirements`, `architecture`, `appendix`.
- Appendix ids: `glossary`, `spec`, `current`, `adr`.
- The architecture section uses `modules: auto` to expand `docs/product/*/00-README.md` in numeric order, with an optional `exclude` list.
- Every listed path / glob must resolve inside `docs/product`, `docs/current`, `docs/adr`, or to `CONTEXT.md`.
- The orchestrator owns the TOC and updates it when modules or appendices change.

## Authority & conflict

- Implementation details: **SPEC wins**.
- Scope / intent: **PRD wins**.
- Conflict: escalate to the orchestrator / user; update the wrong document; never silently choose.
- A decision that needs rationale and trade-offs routes to an ADR (`adr.md`).
- Current is the only status source; no other document claims what is implemented now.

## Current & ADR boundaries

- Current (`current.md`) records the as-built facts at a selected baseline. It may link to the PRD, SPEC, or ADR.
- The PRD core must not link to Current. Current and the PRD are independent, user-readable trees; neither embeds the other.
- ADR = decisions with rationale and trade-offs, a peer and an appendix. In the PRD, describe capabilities in plain language and do not link ADRs.
- Outside the PRD core, an ADR link is a **descriptive phrase + a stable path link** (e.g. `支持[离线使用](../../adr/0003-offline.md)`). The description stands on its own; the ADR rationale is not transcluded or summarized. No requirement must carry an ADR, and links are never inferred automatically.

## Legacy & migration

- The v4 layout (`docs/prd/`), a pre-rename `docs/pdr/` tree, v3/v4 provenance lines, and the old PFD / layered structure are **legacy**. Init detects them and offers migration (`migration.md`).
- Legacy material is never auto-rewritten, moved, or deleted. The user chooses: migrate now, show the plan only, defer into one chore issue, or skip.
- Existing projects without any product docs may use the consent-gated legacy bootstrap (`bootstrap.md`); it produces drafts, never instant facts.

## Example (DA_AGENT) — not part of the general rules

DA_AGENT is a concrete instance: modules ui / agent / cpp-core / FPGA, plus architect and research as module-external areas. Its `docs/product/00-README.md` is the PRD cover and project description (typical scenarios live here); `01-requirements.md` holds the capability map, key behaviors, non-goals and constraints; `02-architecture.md` holds the architecture overview and module map; each module's `00-README.md` is its module PRD and `00-index.md` its agent sidecar; the per-module `01-spec / 02-interfaces / 03-nfr` plus unnumbered `design/` form the SPEC. `docs/toc.yml` is the publication source, FR prefixes read `FR-AGENT-NN`, `FR-UI-NN`, …, Current lives in `docs/current/`, and decisions in `docs/adr/`. Source: DA_AGENT ADR-0026.
