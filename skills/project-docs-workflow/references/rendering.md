# PRD publication (docs-html-view)

Default profile; projects may override in their materialized copies.

Publication is an **optional, user-triggered** capability provided by the first-party `docs-html-view` skill. This profile fixes only the **document contract** it relies on: what is published, how links are written, and that sources are never rewritten. It never installs, builds, or activates anything; init creates no publication artifact.

## Publishable multi-page PRD

The renderer builds a **publishable multi-page PRD** from `docs/toc.yml`:

- **Core**: the three PRD chapters (`docs/product/00-README.md`, `01-requirements.md`, `02-architecture.md`) plus every module PRD (`docs/product/*/00-README.md`, expanded by `modules: auto`).
- **Appendices**: glossary (`CONTEXT.md`), SPEC (`01-spec` / `02-interfaces` / `03-nfr`, plus optional `design/`), Current (`docs/current/`), and ADR (`docs/adr/README.md` and selected ADRs).
- **Out of scope**: `docs/issues/`, `docs/agents/`, module `00-index.md` sidecars, and anything not listed in the TOC.

There is no full-site mode and no profile switch: every build is a PRD publication driven by the TOC. The TOC is the single publication source; only TOC-listed documents are built.

## TOC-driven

- `docs/toc.yml` declares `title`, `version`, `date`, `abstract`, and the section tree.
- Required section ids: `overview`, `requirements`, `architecture`, `appendix`.
- Appendix ids: `glossary`, `spec`, `current`, `adr`.
- The `architecture` section uses `modules: auto`; `exclude` removes specific modules. `design/` is excluded by default.
- Every path / glob must resolve inside `docs/product`, `docs/current`, `docs/adr`, or to `CONTEXT.md`. Only TOC-listed documents are published; an exact include manifest is generated so unlisted docs are never built.

## Glossary

- Root `CONTEXT.md` is copied to `docs/docsHtmlView/glossary.md` at build time and marked as generated.
- The glossary page appears under the appendix; it is not edited by hand in the publication workspace.

## Link authoring

- **PRD core links**: PRD-layer only — same-file anchors, product chapter ↔ module PRD, and module PRD ↔ module PRD. No external links (`http` / `https` / `mailto`), no links to SPEC, Current, or ADR, and no status markers.
- **SPEC / Current → ADR**: a descriptive phrase + a stable path link to the ADR file, e.g. `支持 [离线使用](../../adr/0003-offline.md)`. The form and never-transclude rules live in `adr.md`.
- The native `ADR-XXXX` citation notation is unchanged; ADR deletion / semantic edit sweeps **both** notations (`adr.md`).
- Because the PRD core must not link out, its section pages have no external targets to resolve; only internal anchors matter. Cross-layer navigation is provided by the TOC and the appendices.

## Sources are never rewritten

- Sources stay the single source of truth and stay readable on their own; the renderer is **read-only** — no normalization, no move, no rewrite.
- Out-of-scope or dangling references are **reported**, never fixed in the source.
- "Nothing to publish" is a **failure**; the renderer never bootstraps the workflow.

## Output

- The build writes under `docs/docsHtmlView/`; HTML output lands in `docs/docsHtmlView/build/html`. The recipient opens `docsHtmlView/index.html`; the folder can be zipped for distribution.
- Generated files: `index.md`, `nav/**`, `glossary.md`, `_manifest.json`, `_meta.json`. Only marked generated files are written or pruned; source documents are never touched.

## Manual, opt-in

- **User-triggered and manual**: no hook, no auto-build on doc edits, no change to the init artifacts.
- Install / init / first build only after explicit consent from the skill interaction; there is no orchestrator, approval state machine, or background build.
- Integrate by pointing the project at `docs-html-view` explicitly; never wire it into initialization.
