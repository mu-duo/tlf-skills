# PRD publication (docs-html-view)

Default profile; projects may override in their materialized copies.

Publication is an **optional, user-triggered** capability provided outside this profile by the first-party `docs-html-view` skill. This profile only fixes the **document contract** publication relies on: what is published, how links are written, and that sources are never rewritten. It never installs, builds, renders, or activates anything, and init creates no publication artifact.

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
- **SPEC / Current → ADR**: a **descriptive phrase + a stable path link** to the ADR file, e.g. `支持 [离线使用](../../adr/0003-offline.md)`. The description is written independently and stands on its own; the ADR's rationale is **not** transcluded or summarized. No requirement must carry an ADR, and the profile never infers ADR links automatically.
- The native `ADR-XXXX` citation notation is unchanged; ADR deletion / semantic edit sweeps **both** notations (`adr.md`).
- Because the PRD core must not link out, its section pages have no external targets to resolve; only internal anchors matter. Cross-layer navigation is provided by the TOC and the appendices.

## Sources are never rewritten

- The Markdown sources stay the single source of truth and remain human-readable on their own; the renderer is **read-only** toward them — no normalization, no move, no rewrite.
- Out-of-scope or dangling references are **reported**, never fixed in the source.
- "Nothing to publish" is a **failure**, not a silent success; the renderer never bootstraps the docs workflow on its own.

## Output

- The build writes under `docs/docsHtmlView/`; HTML output lands in `docs/docsHtmlView/build/html`. The recipient opens `docsHtmlView/index.html`; the folder can be zipped for distribution.
- Generated files: `index.md`, `nav/**`, `glossary.md`, `_manifest.json`, `_meta.json`. Only marked generated files are written or pruned; source documents are never touched.

## Manual, opt-in

- Publication is **user-triggered and manual**: no hook, no auto-build on doc edits, no change to the main init artifacts.
- Install / init / first build only after explicit user consent obtained through the skill interaction; there is no custom orchestrator, manifest approval state machine, or background build.
- To integrate, point the project at the `docs-html-view` skill explicitly; do not wire it into initialization.
