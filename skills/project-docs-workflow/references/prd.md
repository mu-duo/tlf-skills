# PRD product requirements

PRD = Product Requirements Document ("产品需求文档"): the target-state product requirements — the product's currently-effective final target: its modules, outward contracts, and mechanism design. Only confirmed constraints (coarse or fine) are recorded; implemented details are not auto-promoted into the PRD. Default profile; overridable in project copies.

## Structure

- Module directories numbered by reading order (e.g. `01-architecture/`, `02-ui/`). Root `00-README.md` = overview + module index + reading order.
- Each module:
  - `00-README.md` — role / scope-boundary / dependencies / doc map.
  - `01-spec.md` — functional requirements, each with an `FR-<MODULE>-NN` ID and 验收判据 (acceptance criteria). FR IDs are stable and never reused; numbering is continuous per module.
  - `02-interfaces.md` — interface contracts. The providing module owns its outward interfaces; consumers reference them.
  - `03-nfr.md` — non-functional requirements.
  - `design/` — optional mechanism-level design, **not numbered**.
- Cross-module architecture and research material may live in module-external directories.
- The PRD tree holds no current-state or progress material: no `04-current.md`, no 当前进展 section. Current state is a **peer tree** (`current.md`).

## Target & gap→issues

- **The PRD is the target.** `NN/01-spec.md` holds the target state; every recorded requirement — coarse or fine — is a confirmed constraint, not an unknown/unconfirmed classification. There are no separate goal files; the end-state details live in the module specs.
- **Root README is overview/navigation.** It carries the end-state overview, module index, and reading order, and links the peer Current tree; it holds no progress section.
- **Changes route by kind.** A goal change updates the PRD only after alignment; a decision with rationale and trade-offs routes to an ADR (see `adr.md`). Implementation inside an aligned scope proceeds autonomously, respecting ADRs, contracts, and security; high-cost, destructive, or hard-to-reverse decisions are confirmed with the user first. Implemented details do not flow back into the PRD automatically.
- **Gap → issue.** At the Plan step the agent reads the PRD target plus Current state (`current.md`), derives **candidate** tasks (module / FR, suggested type, slice, acceptance criteria), and the user picks. Differences are candidates only — a difference may be drift, a quality gap, unverified behavior, or an outdated target, not necessarily a missing feature. An already-met coarse goal can still be refined; do not invent gaps. Accepted candidates land in `docs/issues/` whose 关联 records the module / FR. No idle auto-creation of issues.
- **Non-goals are scope boundaries.** A PRD may state non-goals / out-of-scope items as positive scope boundaries; they are not rejected alternatives under the ADR negative-decision policy and need no per-item rationale.

## PRD ↔ ADR boundary

- PRD = what the product should be (target state).
- ADR = decisions with rationale and trade-offs. The PRD may point at one with a **descriptive phrase + a stable path link** (e.g. `支持[离线使用](../../adr/0003-offline.md)`); the description is written independently and the ADR's rationale is **not** transcluded or summarized. No requirement must carry an ADR, and the profile never infers ADR links automatically (see `rendering.md`).
- A suggestion's acceptance routes into an ADR or the PRD (see `issues.md`).

## PRD ↔ Current boundary

- Two independent, user-readable trees: `docs/prd/` (target) and `docs/current/` (as-built). Neither embeds the other.
- Modules may align by name, but there is no file/paragraph mirroring; link module / FR references explicitly, many-to-many. **Semantic / navigation / contract links** between the trees are expected — use ordinary relative Markdown links. See `current.md`.
- PRD and Current are both in the default render scope, together with the complete ADR set; see `rendering.md`.

## Legacy `docs/pdr/`

- A pre-rename `docs/pdr/` tree is **legacy drift**, not the current PRD tree. init reports it as informational drift.
- init never moves, rewrites, or deletes it. Migration to `docs/prd/` requires the user's explicit authorization.

## Example (DA_AGENT) — not part of the general rules

DA_AGENT is a concrete instance of this pattern: modules ui / agent / cpp-core / FPGA, plus architect and research as module-external areas; each module uses the spec layer `00-README / 01-spec / 02-interfaces / 03-nfr` with an unnumbered `design/` sub-area; FR prefixes read `FR-AGENT-NN`, `FR-UI-NN`, …; product scenarios sit in a separate `07-scenarios.md`. Source: DA_AGENT ADR-0026.
