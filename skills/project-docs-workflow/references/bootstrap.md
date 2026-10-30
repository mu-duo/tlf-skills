# Legacy bootstrap (existing code, no product docs)

Bootstrap is the **consent-gated** path for a project that already has source code but no PRD/SPEC. It drafts the v5 documents from the codebase; it never treats drafts as facts before the user reviews them.

## Trigger

Use bootstrap when one of these holds:

- No `docs/product/` exists, but source code does.
- Only `CONTEXT.md` and/or `docs/adr/` exist, without a PRD/SPEC.

Init detects this state and **asks the user** before writing anything. This is not a normal init run.

## Prompt options

Ask once, in the project's documentation language:

1. **Bootstrap** — run the five phases below and produce reviewed drafts.
2. **Templates only** — create the empty v5 skeleton from the templates; no modeling, no inference.
3. **Skip** — no writes at all; report only.

Never start the bootstrap phases without an explicit choice.

## Five phases

1. **Domain modeling** — run `references/deps/domain-modeling.md` **once**. Produce or update `CONTEXT.md` and ADRs. The user confirms terms and decisions before they are used downstream.
2. **As-built** — read the code, tests, and configuration. Draft `docs/current/` as an as-built snapshot: capabilities, limits, verification confidence. Ask the user for the **selected baseline** (revision / release + date); never default to `main` or the latest release.
3. **PRD draft** — draft the product three chapters: `00-README.md` (one-liner, project description, target users / problems, typical scenarios), `01-requirements.md` (capability map, key behaviors, non-goals, constraints), `02-architecture.md` (architecture overview, module map, links to module PRDs). Draft module PRDs only for modules the user confirms.
4. **SPEC draft** — draft `01-spec.md` (FR IDs + acceptance criteria), `02-interfaces.md`, `03-nfr.md` from the code and tests. **Only confirmed items enter the SPEC.** Inferred, ambiguous, or pending items go into the bootstrap issue checklist — they must not pollute the SPEC.
5. **User review** — show the drafts and per-file diffs; the user confirms, corrects, or rejects each. After confirmation the documents become facts.

## Outputs are drafts

- Bootstrap outputs are drafts until phase 5 completes. Do not publish them, and do not use them as the implementation fact standard before review.
- Never overwrite existing files. Show diffs and let the user decide.
- Create **one** `docs/issues/chore/agent/...` bootstrap issue to track the phases and the inferred / pending items. It is the acceptance checklist for the bootstrap.
- After the user chooses Bootstrap, run `references/deps/domain-modeling.md` once. It does not run during normal init or alignment.

## Templates only

Create the v5 empty skeleton: `docs/product/00-README.md`, `01-requirements.md`, `02-architecture.md`, `docs/toc.yml`, `docs/current/00-README.md`, `docs/adr/README.md`, `CONTEXT.md`, `docs/agents/*`, the issue tree, and the `AGENTS.md` block. Do not infer content.

## Skip

Write nothing — not even non-product artifacts. Report the detected state and the available options only.
