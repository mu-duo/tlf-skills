---
name: project-docs-workflow
description: Initialize or align a project's documentation workflow — issue tracker, ADRs, a macro PRD with a normative SPEC and a separate Current status tree, the recommended five-step workflow, test authoring rules, roles, and legacy bootstrap/migration. Run manually once per project (idempotent); creates missing files and reports alignment without overwriting.
disable-model-invocation: true
---

# Project Docs Workflow

Scaffold and align a project's documentation system: issue tracker, ADRs, a macro PRD, a normative SPEC, a Current as-built tree, domain terminology, a recommended five-step development workflow with explicit roles, and test authoring rules. The skill is the canonical source; init materializes the rules into the target project so agents read them at runtime.

Run it manually, once per project — on adoption, or again after the skill's templates evolve to check alignment. Re-runs are idempotent: they create what is missing and report drift, never rewrite existing content.

## Ownership model

- **Canonical**: this skill holds the rules (`references/`) and templates (`assets/templates/`).
- **Materialized**: init copies rules into the target project. Those copies are the runtime source agents read; the skill does not auto-load.
- **Overrides are legitimate**: projects edit their copies to fit local reality. Init reports the diff, it does not enforce or revert.
- **Language**: templates default to Chinese; for non-Chinese projects, translate the materialized copies, including `docs/agents/deps/*` — overrides are legitimate. "Copied unchanged" constrains init's copy step, not later project edits.
- **Never overwrite**: existing content is compared, never rewritten (two additive exceptions: the missing `AGENTS.md` block, and the `version` line in `docs/agents/metadata.yml`, which advances only after a verified run).
- **Maintenance**: project docs are agent-maintained by default. Humans steer, review the PRD / SPEC / ADR, and may edit style directly. Factual corrections go through the agent.

## Roles

Three roles: **user** (intent, scope, approval; reviews PRD / SPEC / ADRs), **orchestrator** (maintains the PRD, composes the SPEC with the user, owns `docs/toc.yml`, triggers publication), **coder agent** (reads the SPEC, implements, updates Current at wrap-up, proposes SPEC changes through an issue). A single agent may play both, switching hats explicitly. Write permissions: `references/workflow.md`.

## Bundled dependencies

External capability references resolve to the copies bundled with this skill — **one level, no installed-skill lookup**:

| Capability | Bundled source | Notes |
| :--- | :--- | :--- |
| `grilling` | `references/deps/grilling.md` | `grill-me` is an entry alias, no separate flow |
| `grill-with-docs` | `references/deps/grilling.md` + `references/deps/domain-modeling.md` | interleaved: rounds + immediate term/ADR writes |
| `domain-modeling` | `references/deps/domain-modeling.md` | terms and ADRs |
| `tdd` | `references/deps/tdd.md` | mechanics only; `testing.md` governs |
| `deepwork` / `retro` / `improve-codebase-architecture` | `references/deps/boundaries.md` | boundaries, retrospectives |
| `doc-opt` | `references/deps/doc-opt.md` | prose polish; the full first-party `doc-opt` skill is an optional explicit upgrade |

First-party siblings — `docs-html-view`, `docs-docx-view`, `lite-task` — are separate skills of this package, invoked by name when installed; they are not dependency skills.

Never invoke an external skill by name, even when one happens to be installed: the bundled copy is the contract this profile is aligned with. Aliases are routing only, never separate flows.

Canonical wording: 按 `<deps 路径>/<file>.md` 执行 — skill-internal docs use `references/deps/<file>.md`, materialized project files use `docs/agents/deps/<file>.md`.

## Init procedure

Run from the target project root (`cwd`).

1. **Read `docs/agents/metadata.yml`, then classify the state** (below) before touching anything. The state decides whether init may write, repair, or only report.
2. **Inventory** every artifact in the checklist. Classify each as *missing* or *existing*. Done when every row has a classification.
3. **Create missing** artifacts from their templates, per the state rules, plus the issue directory tree. Do not force module files; never create a product `00-index.md`.
4. **Fill placeholders**: fill only obvious, determinable *fill-in* placeholders (e.g. project name from the repo/directory name); list every remaining fill-in placeholder under `Next:` in the report. **Never guess the Current baseline** — if it is unset, `选定 Current 基线（revision / release + 日期）` is the first `Next:` item. Format notation such as `<标题>` is documentation, not a placeholder — skip it.
5. **Compare existing** files against their template: classify *aligned*, or *diff* with the specific differences listed.
6. **Report** using the format below.

### State detection

Read `docs/agents/metadata.yml` **first** — it records the skill version this tree was built or last verified against.

| State | Condition | Action |
| :--- | :--- | :--- |
| **skip** | `version` equals the current skill version and every checklist artifact exists | write nothing; one-line report |
| **skip + repair** | version matches but artifacts are missing | additive repair only (create the missing files); stamp unchanged |
| **behind** | `version` is lower than the current skill version | run the establishment procedure |
| **ahead** | `version` is higher than the current skill version | write nothing; report "upgrade the skill, or keep as-is" |
| **unknown** | the file is missing or unparsable | run the establishment procedure |

Conformance is **structural**: a version match plus artifact presence. Rule drift is reported, never enforced — project overrides are legitimate.

#### Establishment procedure (behind / unknown)

1. **Inventory** the checklist; classify every artifact as missing or existing.
2. **Read what is readable** — this picks the repair input, not the state:
   - source code only → bootstrap (`references/bootstrap.md`: five phases, drafts reviewed before they become facts);
   - existing docs → align, or migrate when `docs/prd/`, `docs/pdr/`, a v3/v4 provenance line, or the old layered structure is present (`references/migration.md`);
   - neither → scaffold from the templates.
3. **Plan** every write as either **add** (create missing files — automatic) or **rewrite** (an existing file whose required rules are missing or contradicted — always shown as a per-file diff).
4. **Execute**: additions automatically; rewrites only after the user confirms. When the user pre-authorizes ("直接执行" / execute directly), print the plan plus the diff summary and execute without asking again. Nothing is ever moved or deleted without that confirmation.
5. **Stamp last**: write `docs/agents/metadata.yml` only when no rewrite is left pending. Declined rewrites keep the old stamp, so the next run reports `behind` again instead of claiming conformance.

Bootstrap and migration keep their own consent options — the establishment procedure never bypasses them.

### Artifact checklist

| Artifact | Template |
| :--- | :--- |
| `AGENTS.md` → `## Agent skills` block | `assets/templates/project/agents-block.md` |
| `docs/agents/issues.md` | `assets/templates/project/agents-issues.md` |
| `docs/agents/domain.md` | `assets/templates/project/agents-domain.md` |
| `docs/agents/workflow.md` | `assets/templates/project/agents-workflow.md` |
| `docs/agents/testing.md` | `assets/templates/project/agents-testing.md` |
| `docs/agents/metadata.yml` | `assets/templates/project/metadata.yml` |
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
- Bundled dependencies: init copies `references/deps/*` into the project's `docs/agents/deps/` as a whole-directory copy (content unchanged at copy time); they are the runtime source for every dependency capability, so target projects never need an external skill. Projects may translate or edit them afterwards.
- Test rules: `docs/agents/testing.md` (source `references/testing.md`) is **first priority and always present** — it ships with the skill, so no installed-skill / fallback split applies; `tdd` contributes mechanics only. Init creates it when missing; projects may override its defaults. The issue's `## 测试` section (execution / temporary / persistent) is the evidence it produces.
- Metadata: `docs/agents/metadata.yml` carries `skill`, `version`, and `updated`. It is the conformance stamp: equal version + complete artifacts = skip. Never hand-bump it past the version whose rules the tree satisfies.
- Current tree: init creates the `docs/current/00-README.md` overview when missing; it does **not** force module files — add them as modules need describing. The Current tree is peer to the PRD, never embedded in it.
- PRD tree: init creates the three product PRD chapters (`00-README.md`, `01-requirements.md`, `02-architecture.md`) and `docs/toc.yml` when missing. It does **not** force module files, and it never creates a product `00-index.md` — that artifact is retired. Module `00-index.md` is an unpublished agent sidecar created only when a module exists.
- Domain glossaries (e.g. `docs/common/glossary.md`) are **not** scaffolded; the rules cover them and projects create them on demand.
- Publication is **out of scope for init**: init creates no renderer config, artifacts, or hooks. HTML publication is an optional, manual first-party skill (`docs-html-view`); see `references/rendering.md`.

### Alignment comparison (existing files)

Compare **rules, not bytes**. An existing file is **aligned** when every required rule/section below is present in recognizable form — wording, language, ordering, formatting and filled-in project content may all differ. Project additions are always fine, never a diff.

**diff** = a required rule/section is missing, or a default rule is contradicted. Diffs are informational; init never auto-fixes. One bullet per file: `- <file>: <missing or contradicted rule>`.

**Legacy drift** (existing projects): a v4 `docs/prd/` or `docs/pdr/` tree, a product `00-index.md`, a v3/v4 provenance line, or embedded current/progress material in the PRD (e.g. per-module `04-current.md`, a `当前进展` section) is reported as informational legacy drift and offered for migration. init never moves, rewrites, or deletes it.

Ignore in every comparison: the provenance line; filled placeholders; index/table rows; module/term/entry names; language; extra content.

Required elements per artifact: compare against the named source; the project copy is aligned when every rule there is recognizable. Wording, language, ordering, and extra content may differ.

| Artifact | Source of the rules | Required content |
| :--- | :--- | :--- |
| `AGENTS.md` block | `assets/templates/project/agents-block.md` | `## Agent skills` heading; three subsections (Issue tracker / Domain docs / Development workflow); pointer to `docs/agents/testing.md` |
| `docs/agents/issues.md` | `references/issues.md` | directory contract; responsibility; entry format (`Status:`, `## 完成判据`, `## 步骤`, `## 测试`, `## Log`; `## 结果` optional); archive suffixes (`-done`/`-drop`, `-drop` ≠ negative decision); suggestion routing |
| `docs/agents/domain.md` | `assets/templates/project/agents-domain.md` | read CONTEXT.md + `docs/adr/` first; continue silently when missing; glossary vocabulary; ADR-conflict flagging |
| `docs/agents/workflow.md` | `references/workflow.md` | roles & write permissions; what to read; authority & escalation; align-before-build; granularity; `## 步骤` + resume; gap→issue; PRD-impact trigger; change protocol; scope convergence; wrap-up; boundaries; test-rules pointer |
| `docs/agents/testing.md` | `references/testing.md` | three test activities; SPEC / completion-criteria traceability; scratch path + cleanup; regression default; assertions; mocks / fixtures; defense layering; L0–L3; `## 测试` slots |
| `docs/agents/metadata.yml` | `assets/templates/project/metadata.yml` | `skill` + `version` (= the version the tree satisfies) + optional `updated`; stamp advances only after a verified run |
| `docs/adr/README.md` | `references/adr.md` | lifecycle (edit + Log, delete → tombstone stub, no renumber); catalog table; reference sweep over both notations; no `Considered Options` by default |
| `docs/product/{00-README,01-requirements,02-architecture}.md` | `references/prd.md` | PRD banner; three chapters; PRD-layer links only; detail ceiling; no status markers |
| `docs/toc.yml` | `references/prd.md` (TOC contract) | `title` / `version` / `date` / `abstract`; section ids `overview` / `requirements` / `architecture` / `appendix`; appendix ids `glossary` / `spec` / `current` / `adr`; every path exists; `modules: auto` |
| module `00-README.md` | `references/prd.md` | module PRD content; backlink to the product PRD; no doc map / dependencies |
| module `00-index.md` | `references/prd.md` | doc map, dependencies, interface ownership, CAP↔FR traceability; unpublished; links to architecture, TOC, module PRD |
| `docs/current/00-README.md` | `references/current.md` | purpose; PRD-cover backlink (`../product/00-README.md`); selected baseline; module index; reading order; as-built only |
| `CONTEXT.md` | `references/terminology.md` | glossary structure (term blocks with `_Avoid_`) |
| `docs/issues/` tree | — | leaf directories exist (`.gitkeep` may be checked) |

Extras are informational, never a diff.

- `docs/agents/deps/`: leaf files exist (`grilling.md`, `domain-modeling.md`, `tdd.md`, `doc-opt.md`, `boundaries.md`).

### Report format

Write the report in the project's documentation language (default: Chinese, matching the templates).

```
## Init report
- State: skip｜skip+repair｜behind｜ahead｜unknown
- Repair: none｜additive｜scaffold｜bootstrap｜migrate｜align
- Created: …
- Aligned: …
- Diff: one bullet per file: `- <file>: <missing or contradicted rule>`（仅供参考，不自动改；multi-file → multiple bullets）
- Metadata: <old> → <new>（updated）｜<old>（kept — N rewrites pending）
- Legacy drift: detected v4/older paths and the offered action — informational only; never moved or rewritten without user authorization.
- Next: remaining placeholders plus a one-line "do this first"; when the Current baseline is unset, `选定 Current 基线` comes first.
```

## References

Rules carry the detail; read the one you need.

- `references/workflow.md` — recommended single-issue development flow: roles & write permissions, what to read, alignment, change protocol, five steps, wrap-up, TOC maintenance, publication pointer, granularity, scope convergence, boundaries.
- `references/testing.md` — test authoring rules: SPEC tracing, strong assertions, mock / fixture boundaries, defense layering, L0–L3 change control, delivery gate; first priority over `tdd`.
- `references/prd.md` — PRD (macro), SPEC (detail), Current, ADR model: directory structure, PRD / SPEC / TOC contracts, authority & conflict, boundaries, legacy/migration pointer.
- `references/current.md` — Current as-built tree, baseline & verification confidence, sync semantics, peer relationship to the PRD, adoption rules.
- `references/rendering.md` — optional publishable multi-page PRD contract (`docs-html-view`): TOC-driven scope, PRD core + SPEC / Current / ADR / glossary appendices, link rules, generated manifest, sources never rewritten, manual opt-in.
- `references/bootstrap.md` — consent-gated bootstrap for existing code without product docs: five phases, drafts, inferred items in the issue.
- `references/migration.md` — v4/older → v5 migration: detection, prompt options, per-file diffs, steps, never auto-rewrite.
- `references/terminology.md` — `CONTEXT.md` primary glossary, domain glossary, usage rules.
- `references/coexistence.md` — how this profile sits beside `domain-modeling`, `grilling`, `deepwork`, `tdd`, `retro`, and the first-party `doc-opt`; and how its docs/issues conventions supersede older `.scratch`-style trackers.
- `references/deps/` — the bundled dependency docs, and the only source for these capabilities: `grilling` / `domain-modeling` / `tdd` / `doc-opt` / `boundaries` (`deepwork` / `retro` / `improve-codebase-architecture` share `boundaries.md`).
- `references/issues.md` — issue tracker directory contract, entry format, `suggestion` routing.
- `references/adr.md` — ADR lifecycle (edit + Log, delete → tombstone stub, reference sweep, catalog index), body shape.

## Templates

- `assets/templates/project/*` — the files init materializes (Chinese). They carry the provenance marker (current generation: `v5`; in `agents-block.md` it sits just under the `## Agent skills` heading) — keep it; future generations update the marker so stale copies are detectable.
- `assets/templates/project/toc.yml` — the `docs/toc.yml` publication source: required section ids, `modules: auto`, and the appendix set.
- `references/deps/*` — the bundled dependency docs: the single source for every capability (no installed-skill lookup). init copies the whole directory as-is into the project's `docs/agents/deps/`; they are not materialized templates and carry no provenance marker.
- `assets/templates/entries/*` — day-to-day authoring aids used when this skill is at hand (copy the skeleton when creating a new entry). NOT materialized by init; the rule docs are self-sufficient without them; materialized docs may reference their path opportunistically.
