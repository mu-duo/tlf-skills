# PRD product requirements

PRD = Product Requirements Document ("产品需求文档"): the target-state product requirements — the product's currently-effective final target: its modules, outward contracts, and mechanism design. Only confirmed constraints (coarse or fine) are recorded; implemented details are not auto-promoted into the PRD. Default profile; overridable in project copies.

## Layers

- **L2 = normative target spec (single source of truth).** A module's `01-spec.md` (functional requirements with `FR-<MODULE>-NN` IDs and acceptance criteria), `02-interfaces.md`, `03-nfr.md`, plus optional `design/`.
- **L1 = human narrative view of L2.** The product `00-README.md` and each module's `00-README.md`. Derived from L2, lossy, written for humans; it must not add constraints. **On any conflict, L2 wins.**
- **L3 = Current as-built snapshot.** `docs/current/`, a peer tree (`current.md`). L1 is target narrative; Current is the only status source.

## Structure

- Module directories numbered by reading order (e.g. `01-architecture/`, `02-ui/`).
- Product root:
  - `00-README.md` — product L1 (narrative).
  - `00-index.md` — navigation / traceability sidecar (agent-facing).
- Each module:
  - `00-README.md` — module L1 (narrative).
  - `00-index.md` — module navigation: doc map, dependencies, interface ownership, traceability.
  - `01-spec.md` — functional requirements, each with an `FR-<MODULE>-NN` ID and 验收判据 (acceptance criteria). FR IDs are stable and never reused; numbering is continuous per module.
  - `02-interfaces.md` — interface contracts. The providing module owns its outward interfaces; consumers reference them.
  - `03-nfr.md` — non-functional requirements.
  - `design/` — optional mechanism-level design, **not numbered**.
- The L1 layer is the product root plus the module roots — not a separate directory tree.
- Cross-module architecture and research material may live in module-external directories.
- The PRD tree holds no current-state or progress material: no `04-current.md`, no 当前进展 section. Current state is a **peer tree** (`current.md`).

## L1 contract

- **Default sections** (product L1): 一句话 (one-liner); 问题与目标 (problem & goal); 核心场景 (core journeys); 能力地图 (capability map); 非目标 (non-goals); 关键产品约束 (shape-changing constraints; drop the section when empty).
- **Module L1 sections**: what the module enables for users / upstream modules; key behaviours; boundaries (responsible / not responsible); optional non-goals.
- **Banner**: every L1 file opens with `本文描述目标态，不代表当前已实现；现状由 agent 查阅 Current。`
- **FR IDs are plain text**, not links. A capability may cite a few supporting FR IDs (`FR-AGENT-12`); never copy acceptance criteria.
- **Links**: only same-file anchors, product L1 ↔ module L1, and module L1 ↔ module L1. No links to L2, Current, ADR, or `http(s)` targets. All external links live in `00-index.md`.
- **Mechanical checks**: every FR ID cited in L1 must exist in L2. A missing ID is L1 drift — fix the L1 reference, or add the FR to L2 only when it is a target change. L1 must also contain no external links and no status markers.
- **Detail ceiling** — allowed: user-visible behaviour, capability names, user outcomes, plain-language constraints. Forbidden: acceptance-criteria text, interface signatures, fields / schemas, error codes, state-machine details, implementation-internal names, implementation steps, performance numbers.
- **No status markers** (✅ / 🚧 / ❌), no roadmap, no progress, no task history.
- **Length**: product L1 ≤ ~2 pages; module L1 ~0.5–1 page. If product L1 exceeds ~3 pages, split by independently released / owned product area: the root L1 keeps the whole-product view plus the L1-layer links, and each area gets `docs/prd/<area>/00-README.md`.
- **Maintenance**: agent-maintained by default; humans steer, review, and may edit style directly (factual corrections go through the agent). Incremental patches on narrative-impacting change; full regeneration at baseline advance, module add/remove, ≥10 accumulated patches, or human request. Always show the diff. Keep the invisible marker `<!-- narrative-source: <L2 revision>; generated: <date> -->`. Humans review the L1 diff for readability and factual plausibility; they do not need to read L2.

## `00-index.md` contract

`00-index.md` is the agent-facing sidecar and the only place for external links.

- **Product `00-index.md`**: purpose; link to the product L1 (`00-README.md`); module index table (`区/模块 | 定位 | L1 入口 | L2 规格入口`); reading order; organization conventions (L1 / L2 / L3, link rules); CAP↔FR / module traceability; links to `../current/00-README.md` and `../adr/README.md`. No progress.
- **Module `00-index.md`**: link to the module L1; doc map; dependencies; interface provider ownership; CAP↔FR traceability; links to the L2 files and the product `00-index.md`.

## L2 contract

- FR IDs are stable and never reused; numbering is continuous per module.
- Every FR carries acceptance criteria (验收判据).
- Interfaces are owned by the providing module; consumers reference them.
- NFRs live in `03-nfr.md`; mechanism-level design is optional in `design/`.
- Implemented details do not auto-promote into L2.

## Target & gap→issues

- **L2 is the target.** `NN/01-spec.md` holds the target state; every recorded requirement — coarse or fine — is a confirmed constraint, not an unknown/unconfirmed classification. There are no separate goal files.
- **Plan reads L2 + Current.** L1 is human orientation only — useful for framing, never a fact source. If L1 and L2 disagree, L2 wins.
- **Gap → issue.** At the Plan step the agent reads the L2 target plus Current state (`current.md`), derives **candidate** tasks (module / FR, suggested type, slice, acceptance criteria), and the user picks. Differences are candidates only — a difference may be drift, a quality gap, unverified behavior, or an outdated target, not necessarily a missing feature. Do not invent gaps. Accepted candidates land in `docs/issues/` whose 关联 records the module / FR. No idle auto-creation of issues.
- **Non-goals are scope boundaries.** A PRD may state non-goals / out-of-scope items as positive scope boundaries; they are not rejected alternatives under the ADR negative-decision policy and need no per-item rationale.

## Change routing

- **Target change** (target user, core journey, scope, non-goals, or FR semantics): Plan → update L2 first → update L1 in the same reviewable unit → human reviews the L1 diff and the target scope before production implementation (soft checkpoint; silence is not approval) → implement → wrap up Current.
- **In-scope implementation**: L2 / L1 no-op → implement → wrap up Current.
- **Internal / bug fix**: L2 / L1 no-op; Current if behavior changes; escalate to a target change when the bug exposes a wrong target.
- Prototypes / spikes are exempt until the direction is confirmed.
- A decision that needs rationale and trade-offs routes to an ADR (see `adr.md`). Implemented details do not auto-promote into L2 or L1.

## PRD ↔ ADR boundary

- PRD = what the product should be (target state).
- ADR = decisions with rationale and trade-offs. In L1, describe capabilities in plain language and do not link ADRs; ADR links live in `00-index.md` or L2, written as a **descriptive phrase + a stable path link** (e.g. `支持[离线使用](../../adr/0003-offline.md)`). The description is written independently and the ADR's rationale is **not** transcluded or summarized. No requirement must carry an ADR, and the profile never infers ADR links automatically (see `rendering.md`).
- A suggestion's acceptance routes into an ADR or the PRD (see `issues.md`).

## PRD ↔ Current boundary

- Two independent, user-readable trees: `docs/prd/` (target) and `docs/current/` (as-built). Neither embeds the other.
- Modules may align by name, but there is no file/paragraph mirroring; link module / FR references explicitly, many-to-many. **Semantic / navigation / contract links** between the trees are expected — use ordinary relative Markdown links. See `current.md`.
- L1 is target narrative; Current is as-built. Current may link to L1 / L2; L1 must not link out. PRD and Current are both in the default render scope, together with the complete ADR set; see `rendering.md`.

## Legacy & migration

- A pre-rename `docs/pdr/` tree is **legacy drift**, not the current PRD tree. init reports it as informational drift.
- An existing `00-README.md` that is a module index / conventions doc is **L1 not aligned** — a diff, not legacy. init reports it; it never rewrites.
- init never moves, rewrites, or deletes either form. Migration requires the user's explicit authorization: create `00-index.md` from the old README's navigation / conventions; generate L1 drafts from L2; move module doc maps / dependencies into the module `00-index.md`; the human reviews the diff.

## Example (DA_AGENT) — not part of the general rules

DA_AGENT is a concrete instance of this pattern: modules ui / agent / cpp-core / FPGA, plus architect and research as module-external areas. The product `docs/prd/00-README.md` is the product L1 and each module's `00-README.md` is its module L1; L2 is the per-module `01-spec / 02-interfaces / 03-nfr` layer with an unnumbered `design/` sub-area; `00-index.md` holds navigation and traceability; FR prefixes read `FR-AGENT-NN`, `FR-UI-NN`, …; product scenarios sit in a separate `07-scenarios.md`. Source: DA_AGENT ADR-0026.
