---
name: project-docs-workflow
description: Initialize or align a project's documentation workflow — issue tracker, ADRs, PDR target specs with a separate Current status tree, recommended five-step development workflow, and domain terminology. Run manually once per project (idempotent); creates missing files and reports alignment without overwriting.
disable-model-invocation: true
---

# Project Docs Workflow

Scaffold and align a project's documentation system: issue tracker, ADRs, PDR product specs, domain terminology, and a recommended five-step development workflow. The skill is the canonical source; init materializes the rules into the target project so agents read them at runtime.

Run it manually, once per project — on adoption, or again after the skill's templates evolve to check alignment. Re-runs are idempotent: they create what is missing and report drift, never rewrite existing content.

## Ownership model

- **Canonical**: this skill holds the rules (`references/`) and templates (`assets/templates/`).
- **Materialized**: init copies rules into the target project. Those copies are the runtime source agents read; the skill does not auto-load.
- **Overrides are legitimate**: projects edit their copies to fit local reality. Init reports the diff, it does not enforce or revert.
- **Language**: templates default to Chinese; for non-Chinese projects, translate the materialized copies — overrides are legitimate.
- **Never overwrite**: existing content is compared, never rewritten (one additive exception: the missing `AGENTS.md` block — see checklist).

## 依赖解析（两级）

External skill references resolve in two levels:

1. **Invoke the skill by name** — the user has the full version installed, or the bundled lite version ships with the package (canonical names: `grilling`, `domain-modeling`, `tdd`, `deepwork`, `retro`, `doc-opt`, `improve-codebase-architecture`; the full version wins when present).
2. **Fallback** — if that skill is absent, follow `references/deps/<name>.md`; `deepwork` / `retro` / `improve-codebase-architecture` share `references/deps/boundaries.md`.

Canonical wording (templates use the same line with the deps path parameterized): 调用 `<skill>`（未安装则按 `<deps 路径>/<file>.md` 执行）— skill-internal docs use `references/deps/<file>.md`, materialized project files use `docs/agents/deps/<file>.md`.

## Init procedure

Run from the target project root (`cwd`).

1. **Inventory** every artifact in the checklist below. Classify each as *missing* or *existing*. Done when every row has a classification.
2. **Create missing** files from their template, and create the issue directory tree. Create the `docs/current/00-README.md` overview when missing — do not force module files.
2b. **Fill placeholders**: fill only obvious, determinable *fill-in* placeholders (e.g. project name from the repo/directory name); list every remaining fill-in placeholder under `Next:` in the report. Format notation such as `<标题>` is documentation, not a placeholder — skip it.
3. **Compare existing** files against their template: classify *aligned*, or *diff* with the specific differences listed.
4. **Report** using the format below.

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
| `docs/pdr/00-README.md` | `assets/templates/project/pdr-00-readme.md` |
| `docs/current/00-README.md` | `assets/templates/project/current-00-readme.md` |
| `CONTEXT.md` | `assets/templates/project/context.md` |

- Create `AGENTS.md` only if missing — its whole content is this block; a file containing only this section is intentional (projects add their own guidance around it). If `AGENTS.md` exists: heading `## Agent skills` present → compare the block in place (never edit); absent → append the block at end of file, separated by one blank line. Only `AGENTS.md` is touched, never `CLAUDE.md`.
- The provenance line sits immediately under the `## Agent skills` heading and is intentional — keep it (it identifies materialized files and their generation).
- Issue tree: `bug/{human,agent,history}`, `feature/{human,agent,history}`, `chore/{human,agent,history}`, `suggestion/{human,agent}`; add a `.gitkeep` to each leaf directory (one containing no files). Do not run `git init`.
- Dep fallbacks: init copies `references/deps/*` into the project's `docs/agents/deps/` as a whole-directory copy (content unchanged), so target projects are self-sufficient even without this skill installed.
- Current tree: init creates the `docs/current/00-README.md` overview when missing; it does **not** force module files — add them as modules need describing. The Current tree is peer to PDR, never embedded in it.
- Domain glossaries (e.g. `docs/common/glossary.md`) are **not** scaffolded; the rules cover them and projects create them on demand.

### Alignment comparison (existing files)

Compare **rules, not bytes**. An existing file is **aligned** when every required rule/section below is present in recognizable form — wording, language, ordering, formatting and filled-in project content may all differ. Project additions are always fine, never a diff.

**diff** = a required rule/section is missing, or a default rule is contradicted. Diffs are informational; init never auto-fixes. One bullet per file: `- <file>: <missing or contradicted rule>`.

**Legacy drift** (existing projects): embedded current/progress material found in an existing project — e.g. per-module `04-current.md`, a `当前进展` section in the PDR README — is reported as informational legacy drift. init never moves, rewrites, or deletes it, and there is no installation migration script; migrating to a separate Current tree requires the user's explicit authorization.

Ignore in every comparison: the provenance line; filled placeholders; index/table rows; module/term/entry names; language; extra content.

Required elements per artifact:

- `AGENTS.md` block: `## Agent skills` heading + three subsections (`### Issue tracker`, `### Domain docs`, `### Development workflow`).
- `docs/agents/issues.md`: directory contract; human/agent responsibility; entry format (`Status:` line, `## 完成判据`, `## 步骤`, `## Log`; the `## 结果` section itself is optional); archiving suffixes (`-done`/`-drop`); suggestion routing.
- `docs/agents/domain.md`: read CONTEXT.md + docs/adr before exploring; silently continue if missing; glossary vocabulary rule; ADR-conflict flagging.
- `docs/agents/workflow.md`: recommended five-step flow (规划 / 骨架 / 细节 / 异常 / 回顾 with 回顾 = docs-sync wrap-up); align-before-build ordering; conversational alignment (no freeze); elastic granularity suggestion (≈0.5 人天 heuristic); issue `## 步骤` tracking + resume anchor; PDR-target / Current gap→issue candidate derivation; boundaries (deepwork / tdd / retro / grilling 调用 + 兜底指针).
- `docs/adr/README.md`: lifecycle rules (edit+Log, delete→tombstone stub, no renumber); catalog table present.
- `docs/pdr/00-README.md`: purpose; end-state overview; module index; reading order; link to the peer Current tree (no progress section, no embedded current).
- `docs/current/00-README.md`: purpose; the baseline (revision/date) the tree describes; module/topic index; reading order; link to the peer PDR tree; records as-built capabilities/limits, not task logs or planned work.
- `CONTEXT.md`: glossary structure (term blocks with `_Avoid_`).
- `docs/issues/` tree: leaf directories exist (`.gitkeep` may be checked); extras informational only.
- `docs/agents/deps/`: leaf files exist (`grilling.md`, `domain-modeling.md`, `tdd.md`, `doc-opt.md`, `boundaries.md`); extras informational only.

### Report format

Write the report in the project's documentation language (default: Chinese, matching the templates).

```
## Init report
- Created: …
- Aligned: …
- Diff: one bullet per file: `- <file>: <missing or contradicted rule>`（仅供参考，不自动改；multi-file → multiple bullets）
- Legacy drift: embedded current/progress paths found (e.g. `04-current.md`, `当前进展` section) — informational only, never moved or rewritten; migration needs explicit user authorization.
- Next: remaining placeholders plus a one-line "do this first".
```

## References

Rules carry the detail; read the one you need.

- `references/issues.md` — issue tracker directory contract, entry format, `suggestion` routing.
- `references/adr.md` — ADR lifecycle (edit + Log, delete → tombstone stub, reference sweep, catalog index), body shape.
- `references/pdr.md` — PDR target-spec structure (`00-README` / `01-spec` / `02-interfaces` / `03-nfr` + `design/`), the target & gap→candidate-issue layer, PDR↔ADR and PDR↔Current boundaries.
- `references/current.md` — Current as-built tree (`00-README` + module/topic docs), baseline & verification confidence, sync semantics, peer relationship to PDR, legacy-drift adoption.
- `references/terminology.md` — `CONTEXT.md` primary glossary, domain glossary, usage rules.
- `references/workflow.md` — recommended single-issue development flow (five steps, alignment, granularity, tracking, docs-sync hooks, skill boundaries).
- `references/coexistence.md` — how this profile sits beside `domain-modeling`, `grilling`, `deepwork`, `tdd`, `retro`, and the bundled `doc-opt`; and how its docs/issues conventions supersede older `.scratch`-style trackers.
- `references/deps/` — fallback procedures for the two-level resolution: `grilling` / `domain-modeling` / `tdd` / `doc-opt` / `boundaries` (`deepwork` / `retro` / `improve-codebase-architecture` share `boundaries.md`).

## Templates

- `assets/templates/project/*` — the files init materializes (Chinese). They carry the provenance marker (current generation: `v2`; in `agents-block.md` it sits just under the `## Agent skills` heading) — keep it; future generations update the marker so stale copies are detectable.
- `references/deps/*` — fallback procedures when an external skill is absent. init copies the whole directory as-is into the project's `docs/agents/deps/`; they are not materialized templates and carry no provenance marker.
- `assets/templates/entries/*` — day-to-day authoring aids used when this skill is at hand (copy the skeleton when creating a new entry). NOT materialized by init; the rule docs are self-sufficient without them; materialized docs may reference their path opportunistically.
