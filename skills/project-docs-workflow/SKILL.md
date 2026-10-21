---
name: project-docs-workflow
description: Initialize or align a project's documentation workflow — issue tracker, ADRs, a macro PRD with a normative SPEC and a separate Current status tree, the recommended five-step workflow, roles, and legacy bootstrap/migration. Run manually once per project (idempotent); creates missing files and reports alignment without overwriting.
disable-model-invocation: true
---

# Project Docs Workflow

Scaffold and align a project's documentation system: issue tracker, ADRs, a macro PRD, a normative SPEC, a Current as-built tree, domain terminology, and a recommended five-step development workflow with explicit roles. The skill is the canonical source; init materializes the rules into the target project so agents read them at runtime.

Run it manually, once per project — on adoption, or again after the skill's templates evolve to check alignment. Re-runs are idempotent: they create what is missing and report drift, never rewrite existing content.

## Ownership model

- **Canonical**: this skill holds the rules (`references/`) and templates (`assets/templates/`).
- **Materialized**: init copies rules into the target project. Those copies are the runtime source agents read; the skill does not auto-load.
- **Overrides are legitimate**: projects edit their copies to fit local reality. Init reports the diff, it does not enforce or revert.
- **Language**: templates default to Chinese; for non-Chinese projects, translate the materialized copies — overrides are legitimate.
- **Never overwrite**: existing content is compared, never rewritten (one additive exception: the missing `AGENTS.md` block — see checklist).
- **Maintenance**: project docs are agent-maintained by default. Humans steer, review the PRD / SPEC / ADR, and may edit style directly. Factual corrections go through the agent.

## Roles

- **User** — intent, scope, approval; reviews the PRD, SPEC, and ADRs.
- **Orchestrator** — maintains the PRD; composes the SPEC with the user; reviews PRD / SPEC diffs; owns `docs/toc.yml`; triggers publication; delegates coding.
- **Coder agent** — reads the SPEC, implements; updates Current facts at wrap-up; may propose SPEC changes through an issue; does not directly edit the PRD, SPEC, or TOC.
- **Single-agent setups** — one agent may play orchestrator + coder; role boundaries still apply.

## 依赖解析（两级）

External capability references resolve in two levels:

1. **Invoke the installed skill by name** — when the user has the standalone skill installed (canonical names: `grilling`, `grill-me`, `grill-with-docs`, `domain-modeling`, `tdd`, `deepwork`, `retro`, `improve-codebase-architecture`, plus the first-party `doc-opt`); the installed version wins.
2. **Internal fallback** — otherwise **execute** the bundled reference(s) as instructions; do **not** invoke them as skills (there are none). Most names map to `references/deps/<name>.md`; the aliases map explicitly:
   - `grill-me` → `references/deps/grilling.md` (entry alias of `grilling`, no separate flow)
   - `grill-with-docs` → `references/deps/grilling.md` **+** `references/deps/domain-modeling.md`, interleaved (grilling rounds + immediate term/ADR writes)
   - `deepwork` / `retro` / `improve-codebase-architecture` → `references/deps/boundaries.md`
   The package ships **no** standalone dependency skills; these internal references are the always-available fallback.

> **Trigger policy.** Follow each installed skill's invocation metadata; wrappers such as `grill-me` / `grill-with-docs` may be user-invoked only. An optional name does **not** imply availability: if it is not installed, use the internal fallback — never invoke a missing skill or autonomously invoke a user-only wrapper. Per-name routing lives in `references/workflow.md`.

Canonical wording (templates use the same line with the deps path parameterized): 调用 `<skill>`（未安装则按 `<deps 路径>/<file>.md` 执行）— skill-internal docs use `references/deps/<file>.md`, materialized project files use `docs/agents/deps/<file>.md`.

## Init procedure

Run from the target project root (`cwd`).

1. **Detect the state** (below) before touching anything. The state decides whether init may write, prompt for migration, or prompt for bootstrap.
2. **Inventory** every artifact in the checklist. Classify each as *missing* or *existing*. Done when every row has a classification.
3. **Create missing** files from their template, per the state rules, and create the issue directory tree. Create the `docs/current/00-README.md` overview when missing — do not force module files. Create `docs/product/00-README.md`, `docs/product/01-requirements.md`, `docs/product/02-architecture.md`, and `docs/toc.yml` when missing — do **not** force module files, and never create a product `00-index.md`.
4. **Fill placeholders**: fill only obvious, determinable *fill-in* placeholders (e.g. project name from the repo/directory name); list every remaining fill-in placeholder under `Next:` in the report. Format notation such as `<标题>` is documentation, not a placeholder — skip it.
5. **Compare existing** files against their template: classify *aligned*, or *diff* with the specific differences listed.
6. **Report** using the format below.

### State detection

Classify the project before init writes anything:

1. **v5 (aligned or partial)** — `docs/product/` exists (for example `docs/product/00-README.md`). Treat it as v5: no migration or bootstrap prompt; run the normal inventory / alignment report and create only missing checklist files (including the three PRD chapters and `docs/toc.yml` when missing). Never rewrite. A partial v5 tree is **not** a bootstrap case.
2. **v4/older docs** — `docs/prd/`, `docs/pdr/`, a v3/v4 provenance line, or the old PFD / layered structure (product `00-index.md`, L1/L2/L3 terms). **Prompt**:
   - **migrate now** → show the plan plus per-file diffs, ask for confirmation, then execute (`references/migration.md`);
   - **show the plan only** → print the plan and diffs, write nothing;
   - **later** → create one `docs/issues/chore/agent/...` migration issue, write nothing else;
   - **skip** → no writes at all (not even non-product artifacts); report only.
   Never auto-rewrite, move, or delete. Without an explicit choice, write nothing.
3. **no docs + source code** — no `docs/product/`, but the repo has source code (or only `CONTEXT.md` / ADRs). **Prompt** the legacy bootstrap (`references/bootstrap.md`):
   - **Bootstrap** → five phases: domain modeling, as-built, PRD draft, SPEC draft, user review;
   - **templates only** → create the v5 empty skeleton; no modeling;
   - **skip** → no writes.
4. **empty/new repo** — scaffold v5: create the checklist artifacts from their templates.

### Artifact checklist

| Artifact | Template |
| :--- | :--- |
| `AGENTS.md` → `## Agent skills` block | `assets/templates/project/agents-block.md` |
| `docs/agents/issues.md` | `assets/templates/project/agents-issues.md` |
| `docs/agents/domain.md` | `assets/templates/project/agents-domain.md` |
| `docs/agents/workflow.md` | `assets/templates/project/agents-workflow.md` |
| `docs/agents/deps/` | `references/deps/*`（整目录复制，不改内容） |
| `docs/issues/` directory tree | none — create dirs (below) |
| `docs/adr/README.md` | `assets/templates/project/adr-readme.md` |
| `docs/toc.yml` | `assets/templates/project/toc.yml` |
| `docs/product/00-README.md`（PRD 封面） | `assets/templates/project/prd-00-readme.md` |
| `docs/product/01-requirements.md` | `assets/templates/project/prd-01-requirements.md` |
| `docs/product/02-architecture.md` | `assets/templates/project/prd-02-architecture.md` |
| `docs/current/00-README.md` | `assets/templates/project/current-00-readme.md` |
| `CONTEXT.md` | `assets/templates/project/context.md` |

- Create `AGENTS.md` only if missing — its whole content is this block; a file containing only this section is intentional (projects add their own guidance around it). If `AGENTS.md` exists: heading `## Agent skills` present → compare the block in place (never edit); absent → append the block at end of file, separated by one blank line. Only `AGENTS.md` is touched, never `CLAUDE.md`.
- The provenance line sits immediately under the `## Agent skills` heading and is intentional — keep it (it identifies materialized files and their generation; current generation `v5`).
- Issue tree: `bug/{human,agent,history}`, `feature/{human,agent,history}`, `chore/{human,agent,history}`, `suggestion/{human,agent}`; add a `.gitkeep` to each leaf directory (one containing no files). Do not run `git init`.
- Dep fallbacks: init copies `references/deps/*` into the project's `docs/agents/deps/` as a whole-directory copy (content unchanged), so target projects are self-sufficient even without this skill installed.
- Current tree: init creates the `docs/current/00-README.md` overview when missing; it does **not** force module files — add them as modules need describing. The Current tree is peer to the PRD, never embedded in it.
- PRD tree: init creates the three product PRD chapters (`00-README.md`, `01-requirements.md`, `02-architecture.md`) and `docs/toc.yml` when missing. It does **not** force module files, and it never creates a product `00-index.md` — that artifact is retired. Module `00-index.md` is an unpublished agent sidecar created only when a module exists.
- Domain glossaries (e.g. `docs/common/glossary.md`) are **not** scaffolded; the rules cover them and projects create them on demand.
- Publication is **out of scope for init**: init creates no renderer config, artifacts, or hooks. HTML publication is an optional, manual first-party skill (`docs-html-view`); see `references/rendering.md`.

### Alignment comparison (existing files)

Compare **rules, not bytes**. An existing file is **aligned** when every required rule/section below is present in recognizable form — wording, language, ordering, formatting and filled-in project content may all differ. Project additions are always fine, never a diff.

**diff** = a required rule/section is missing, or a default rule is contradicted. Diffs are informational; init never auto-fixes. One bullet per file: `- <file>: <missing or contradicted rule>`.

**Legacy drift** (existing projects): a v4 `docs/prd/` or `docs/pdr/` tree, a product `00-index.md`, a v3/v4 provenance line, or embedded current/progress material in the PRD (e.g. per-module `04-current.md`, a `当前进展` section) is reported as informational legacy drift and offered for migration. init never moves, rewrites, or deletes it.

Ignore in every comparison: the provenance line; filled placeholders; index/table rows; module/term/entry names; language; extra content.

Required elements per artifact:

- `AGENTS.md` block: `## Agent skills` heading + three subsections (`### Issue tracker`, `### Domain docs`, `### Development workflow`).
- `docs/agents/issues.md`: directory contract; human/agent responsibility; entry format (`Status:` line, `## 完成判据`, `## 步骤`, `## Log`; the `## 结果` section itself is optional); archiving suffixes (`-done`/`-drop`); `-drop` is a work-status archive, not a negative decision (dropped entries are not removed or rewritten); suggestion routing.
- `docs/agents/domain.md`: read CONTEXT.md + docs/adr before exploring; silently continue if missing; glossary vocabulary rule; ADR-conflict flagging.
- `docs/agents/workflow.md`: roles and write permissions (user / orchestrator / coder, single-agent note); what to read (PRD for intent & scenarios, SPEC for implementation facts, Current for as-built, TOC for publication); PRD / SPEC authority and conflict escalation; align-before-build ordering; conversational alignment (no freeze); elastic granularity suggestion (≈0.5 人天 heuristic); issue `## 步骤` tracking + resume anchor; gap→issue candidate derivation; the four-item PRD-impact trigger with one-line no-op logging; PRD / SPEC / Current / ADR change protocol; scope-convergence default; wrap-up (coder updates Current facts and proposes SPEC changes; orchestrator reviews and updates the TOC if modules/appendices changed); boundaries (deepwork / tdd / retro / grilling 调用 + 兜底指针); bootstrap / migration pointers.
- `docs/adr/README.md`: lifecycle rules (edit+Log, delete→tombstone stub, no renumber); catalog table present; reference sweep covers both `ADR-XXXX` and `adr/<NNNN>-<slug>.md` path links (any relative prefix); body defaults to no `Considered Options`; rejected alternatives are not recorded by default (durable records only; discussions may explore alternatives).
- `docs/product/00-README.md`: PRD banner (`本文档描述产品目标与方案，不代表当前实现状态；实现细节见 SPEC，现状见 Current。`); project description sections (one-liner, project description, target users / problems, typical scenarios); no external links, no status markers, no acceptance criteria.
- `docs/product/01-requirements.md`: capability map, key behaviors, non-goals, shape constraints; FR IDs plain text; no acceptance criteria or interface detail.
- `docs/product/02-architecture.md`: architecture overview + module map; links to module PRDs; no SPEC detail.
- `docs/toc.yml`: `title` / `version` / `date` / `abstract`; required section ids `overview`, `requirements`, `architecture`, `appendix`; appendix ids `glossary`, `spec`, `current`, `adr`; all paths exist; `modules: auto`.
- module `00-README.md`: module PRD (what it enables, key behaviors, boundaries, non-goals); backlink to the product PRD; no doc map / dependencies.
- module `00-index.md`: doc map, dependencies, interface ownership, CAP↔FR traceability; not published; links to the architecture chapter, the TOC, and the module PRD.
- `docs/current/00-README.md`: purpose; link to the PRD cover (`../product/00-README.md`); the baseline (revision/date) the tree describes; module/topic index; reading order; records as-built capabilities/limits, not task logs, planned work, or progress; optional descriptive ADR link rule.
- `CONTEXT.md`: glossary structure (term blocks with `_Avoid_`).
- `docs/issues/` tree: leaf directories exist (`.gitkeep` may be checked); extras informational only.
- `docs/agents/deps/`: leaf files exist (`grilling.md`, `domain-modeling.md`, `tdd.md`, `doc-opt.md`, `boundaries.md`); extras informational only.

### Report format

Write the report in the project's documentation language (default: Chinese, matching the templates).

```
## Init report
- State: v5 aligned/partial｜v4/older docs｜no docs + source｜empty/new
- Created: …
- Aligned: …
- Diff: one bullet per file: `- <file>: <missing or contradicted rule>`（仅供参考，不自动改；multi-file → multiple bullets）
- Migration/bootstrap decision: none｜migrate now｜plan only｜later (<issue path>)｜skip (migration)｜bootstrap｜templates only｜skip (bootstrap)
- Legacy drift: detected v4/older paths and the offered action — informational only; never moved or rewritten without user authorization.
- Next: remaining placeholders plus a one-line "do this first".
```

## References

Rules carry the detail; read the one you need.

- `references/workflow.md` — recommended single-issue development flow: roles & write permissions, what to read, alignment, change protocol, five steps, wrap-up, TOC maintenance, publication pointer, granularity, scope convergence, boundaries.
- `references/prd.md` — PRD (macro), SPEC (detail), Current, ADR model: directory structure, PRD / SPEC / TOC contracts, authority & conflict, boundaries, legacy/migration pointer.
- `references/current.md` — Current as-built tree, baseline & verification confidence, sync semantics, peer relationship to the PRD, adoption rules.
- `references/rendering.md` — optional publishable multi-page PRD contract (`docs-html-view`): TOC-driven scope, PRD core + SPEC / Current / ADR / glossary appendices, link rules, generated manifest, sources never rewritten, manual opt-in.
- `references/bootstrap.md` — consent-gated bootstrap for existing code without product docs: five phases, drafts, inferred items in the issue.
- `references/migration.md` — v4/older → v5 migration: detection, prompt options, per-file diffs, steps, never auto-rewrite.
- `references/terminology.md` — `CONTEXT.md` primary glossary, domain glossary, usage rules.
- `references/coexistence.md` — how this profile sits beside `domain-modeling`, `grilling`, `deepwork`, `tdd`, `retro`, and the first-party `doc-opt`; and how its docs/issues conventions supersede older `.scratch`-style trackers.
- `references/deps/` — internal fallback references for the two-level resolution: `grilling` / `domain-modeling` / `tdd` / `doc-opt` / `boundaries` (`deepwork` / `retro` / `improve-codebase-architecture` share `boundaries.md`).
- `references/issues.md` — issue tracker directory contract, entry format, `suggestion` routing.
- `references/adr.md` — ADR lifecycle (edit + Log, delete → tombstone stub, reference sweep, catalog index), body shape.

## Templates

- `assets/templates/project/*` — the files init materializes (Chinese). They carry the provenance marker (current generation: `v5`; in `agents-block.md` it sits just under the `## Agent skills` heading) — keep it; future generations update the marker so stale copies are detectable.
- `assets/templates/project/toc.yml` — the `docs/toc.yml` publication source: required section ids, `modules: auto`, and the appendix set.
- `references/deps/*` — internal fallback references used when a standalone dependency skill is absent. init copies the whole directory as-is into the project's `docs/agents/deps/`; they are not materialized templates and carry no provenance marker.
- `assets/templates/entries/*` — day-to-day authoring aids used when this skill is at hand (copy the skeleton when creating a new entry). NOT materialized by init; the rule docs are self-sufficient without them; materialized docs may reference their path opportunistically.
