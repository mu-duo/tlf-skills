# PDR product specs

PDR = target-state product spec ("产品规格书"): what the product should become, its modules, outward contracts, and mechanism design. Default profile; overridable in project copies.

## Structure

- Module directories numbered by reading order (e.g. `01-architecture/`, `02-ui/`). Root `00-README.md` = module index + reading order.
- Each module:
  - `00-README.md` — role / scope-boundary / dependencies / doc map.
  - `01-spec.md` — functional requirements, each with an `FR-<MODULE>-NN` ID and 验收判据 (acceptance criteria). FR IDs are stable and never reused; numbering is continuous per module.
  - `02-interfaces.md` — interface contracts. The providing module owns its outward interfaces; consumers reference them.
  - `03-nfr.md` — non-functional requirements.
  - `04-current.md` — current-state snapshot vs the spec; dated, ≤1 page, conclusions and gaps only. See "Goal / current & gap→issues".
  - `design/` — optional mechanism-level design, **not numbered**.
- Cross-module architecture and research material may live in module-external directories.

## Goal / current & gap→issues

- **The spec is the goal.** `NN/01-spec.md` is the target state; there are no separate goal files — the details of the end state live in the module specs, not in root docs.
- **Root README carries two sections.** `docs/pdr/00-README.md` gains 「最终目标」(one-paragraph end state; details live in the module specs) and 「当前进展」(one line of status per module, each pointing to that module's `04-current.md`).
- **Per-module `04-current.md`** is a current-state snapshot measured against the spec: dated, ≤1 page, conclusions and gaps only (never a log). Updated by the agent at issue completion, as part of the wrap-up review (see `workflow.md`).
- **Scope & adoption.** Applies to numbered modules. Existing projects adopt it lazily — per module, when that module is next touched; init reports the diff and never overwrites.
- **Gap → issue.** At the Plan step the agent reads goal (spec) plus current, derives gap candidates (module / FR, suggested type, slice, acceptance criteria), and the user picks. Accepted candidates land as entries in `docs/issues/` whose 关联 records the module / FR. No idle auto-creation of issues.

## PDR ↔ ADR boundary

- PDR = what the product should be (target state).
- ADR = decisions with rationale and trade-offs.
- A suggestion's acceptance routes into an ADR or the PDR (see `issues.md`).

## Example (DA_AGENT) — not part of the general rules

DA_AGENT is a concrete instance of this pattern: modules ui / agent / cpp-core / FPGA, plus architect and research as module-external areas; each module uses the spec layer `00-README / 01-spec / 02-interfaces / 03-nfr` with an unnumbered `design/` sub-area; FR prefixes read `FR-AGENT-NN`, `FR-UI-NN`, …; product scenarios sit in a separate `07-scenarios.md`. Source: DA_AGENT ADR-0026.
