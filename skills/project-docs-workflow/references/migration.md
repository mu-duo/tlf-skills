# Migration (v4/older → v5)

Migration converts an existing documentation tree to v5. It is **explicit and reviewed** — init never auto-rewrites, moves, or deletes project documents.

## Detection

Init treats any of the following as v4/older docs:

- A `docs/prd/` tree (v4 layout).
- A pre-rename `docs/pdr/` tree.
- A `project-docs-workflow v3` / `v4` provenance line in materialized files.
- The old PFD / layered structure: a product `00-index.md`, `L1` / `L2` / `L3` terminology, or an embedded current/progress section in the PRD.

Legacy vocabulary mapping:

| v4/older | v5 |
| :--- | :--- |
| `docs/prd/` | `docs/product/` |
| L1 (human narrative) | PRD (macro product narrative) |
| L2 (normative spec) | SPEC (implementation fact standard) |
| L3 (Current) | Current (as-built snapshot; unchanged role) |
| PFD / product `00-index.md` | retired — split into PRD chapters + `docs/toc.yml` |
| module `00-index.md` | module sidecar (unchanged, still unpublished) |

## Prompt options

Ask once, in the project's documentation language:

1. **Migrate now** — show a plan and per-file diffs, get user confirmation, then execute.
2. **Show the plan only** — print the plan and diffs; write nothing.
3. **Later** — create **one** `docs/issues/chore/agent/...` migration issue and write nothing else.
4. **Skip** — no writes at all, not even non-product artifacts; report only.

Never auto-rewrite / move / delete. If the user does not confirm, nothing changes.

## Steps (after confirmation)

1. **Move the tree**: `docs/prd/` → `docs/product/`. Use `git mv` where possible so history follows the files. Do not commit.
2. **Split the v4 product `00-README.md`**:
   - one-liner / problem / user journeys → `docs/product/00-README.md`;
   - capability map / non-goals / constraints → `docs/product/01-requirements.md`;
   - module index / reading order → `docs/product/02-architecture.md` and `docs/toc.yml`.
3. **Retire the product `00-index.md`**:
   - module index / reading order → `docs/toc.yml` / `02-architecture.md`;
   - CAP↔FR traceability → the module `00-index.md`, or drop it if no longer needed;
   - delete the now-empty product `00-index.md` only after the content has a new home.
4. **Module files**: `00-README.md` becomes the module PRD (rewrite the banner and remove doc-map / dependency material); `01-spec` / `02-interfaces` / `03-nfr` / `design/` stay as the SPEC, with wording updated where they described the old layers.
5. **Create `docs/toc.yml`** with `overview` / `requirements` / `architecture` / `appendix` sections and the required appendix ids (`glossary`, `spec`, `current`, `adr`).
6. **Update links**: `docs/prd` → `docs/product` everywhere; the Current link (`../product/00-README.md`); ADR path links; `docs/agents/workflow.md` and the `AGENTS.md` block (roles, PRD/SPEC authority, TOC, bootstrap/migration pointers).
7. **Remove or replace old `docs-html-view` config / build output** if present. Publication is a separate flow — do not rebuild it during migration.

Show the per-file diff for each step and stop on any unexpected conflict. Never guess a user's intent for content that does not have an obvious new home; ask.

## Later

Create **one** issue under `docs/issues/chore/agent/` describing the detected legacy layout and the migration plan. No document writes; the issue is the only artifact.

## Skip

No writes. Report the detected state and the options only.

## Existing projects

Never auto-rewrite an existing project. Migration is always an explicit, reviewed decision; the source documents remain authoritative until the user confirms.
