---
name: docs-html-view
description: Publish a project's PRD as a local multi-page HTML site from docs/toc.yml with Sphinx + MyST (stock RTD theme) — core PRD chapters plus glossary, SPEC, Current, and ADR appendices — after a read-only inspection and explicit approval.
disable-model-invocation: true
argument-hint: "[project root]"
---

# Docs HTML View

Build one publishable, multi-page **PRD** from `docs/toc.yml` using **standard Sphinx** with MyST (`myst_parser`) and the **stock** `sphinx_rtd_theme`. The publication is a cover page, three core PRD chapters, module PRDs, and four appendix groups (glossary, SPEC, Current, ADR). There is no custom renderer: scaffolding uses `sphinx-quickstart`, `scripts/gen_prd.py` generates the cover and conditional section landing pages from the TOC, and the build is `make html` (or a plain `sphinx-build`). Sections with exactly one document are linked directly from their parent (no extra wrapper level); multi-document and branch sections get a generated landing page. The output is a local HTML folder; nothing is served, deployed, or published automatically.

This skill is manually triggered and never automatic, and it never fetches anything at build time. It may install the pinned render dependencies, but only after your explicit approval. Inspect read-only, ask for approval **once**, then first-time setup and repeat manual renders run without re-asking — until a setting or the TOC changes.

## Publication model

`docs/toc.yml` is the **single source of truth**. It defines the title, version, date, abstract, and the exact documents to publish:

| Part | Source | Published as |
| :--- | :--- | :--- |
| Cover | `docs/toc.yml` metadata | `docsHtmlView/index.md` |
| Core sections | `overview`, `requirements`, `architecture` | `docsHtmlView/nav/<id>/index.md` (only for multi-document/branch sections; single-document sections are linked directly) |
| Module PRDs | `modules: auto` under `architecture` | `docs/product/<NN-module>/00-README.md` |
| Appendices | `glossary`, `spec`, `current`, `adr` | `docsHtmlView/nav/appendix/<id>/index.md` (only where a landing page is needed) |
| Glossary | root `CONTEXT.md` | generated `docsHtmlView/glossary.md` |

`gen_prd.py` also writes `_manifest.json` (the exact include list) and `_meta.json` (title/version/date/abstract/author). `conf.py` reads both: only manifest-listed documents are built, so a document missing from the TOC is never rendered. Module sidecars (`00-index.md`) and unlisted `design/` files stay unpublished.

## Boundaries

- **User-triggered only.** Never install, scaffold, generate, or build while editing docs. There is no auto-build and no watcher.
- **Bounded writes.** The approved set is: `docs/docsHtmlView/` (config, generated cover, conditional nav landing pages, glossary, manifests, build output), the approved render environment directory (e.g. `.venv-docs/`), and any `.gitignore` additions you approved. The publication reads `docs/product`, `docs/current`, `docs/adr`, root `CONTEXT.md`, and `docs/toc.yml`; it never rewrites source documents.
- **TOC-controlled range.** Only documents listed in `docs/toc.yml` are published. Paths must resolve under `docs/product`, `docs/current`, `docs/adr`, or be exactly `CONTEXT.md`; symlinks are refused. There is one publication: no alternate views, no separate landing-page configuration.
- **No TOC or no documents → stop.** Do not create `docs/docsHtmlView/`, scaffold, or build. Report the missing/invalid TOC instead.
- **Stock theme.** No custom UI/design work.
- **No invented links or content.** Navigation is generated from the TOC; document bodies are never rewritten. `CONTEXT.md` is copied into the generated glossary with its leading provenance marker stripped.
- **No browser/server/deploy.** Producing the local HTML folder is the end. Packaging, hosting, and delivery are outside this skill and remain the user's decision.

## Flow

Run from the project root (`cwd`). Define the skill directory and, after approval, the prepared environment's absolute paths once — `DOCS_PY` is the venv **python**, `DOCS_SPHINXBUILD` the venv **sphinx-build**:

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="TOC TITLE"                                # title read from docs/toc.yml
DOCS_PY="$PWD/.venv-docs/bin/python"                 # or the project's existing docs env
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # same env
```

1. **Inspect (read-only).** Use normal read-only tools (`ls`, `read`, `grep`) to learn the project: whether `docs/toc.yml` exists and lists the required sections, which `docs/product`, `docs/current`, `docs/adr`, and `CONTEXT.md` exist, whether `docs/docsHtmlView/` already exists, which Python/venv exists, and the TOC title/version. **Never execute the project's interpreter or `conf.py` before approval.** If there is no usable TOC, stop here — there is nothing to publish. Report the plan: pins, environment path, files created, `.gitignore` additions, output path, and title.

2. **Ask once.** Get explicit approval **before any write, install, or scaffold**. Cover concretely: packages/pins (`requirements.txt`, including PyYAML for TOC parsing), where the environment lives, the pip command, the files created, the `.gitignore` additions you propose (e.g. `.venv-docs/`, `docs/docsHtmlView/build/`), the build/output path (`docs/docsHtmlView/build/html`), and the TOC title/version that will appear on the cover.
   - Within the approved scope, repeated manual rendering does **not** re-ask.
   - Dependency upgrades, overwriting existing files, or changing the TOC range (new roots, new documents) do require a fresh ask.

3. **Prepare the environment (approved only).** Prefer an existing project docs environment; otherwise a project-root `.venv-docs`. No global/system installs, no automatic `uv`/Python installation. If no suitable Python exists, stop and tell the user. The helper is stdlib-only before PyYAML is installed, so run it with any working Python; then point `DOCS_PY`/`DOCS_SPHINXBUILD` at the environment it prepared:

   ```bash
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
   ```

   The helper only creates/reuses a recognized venv (a directory with `pyvenv.cfg`; it refuses to clobber a non-venv) and installs the pinned requirements only when `--install` is passed (after your approval). It never runs on ordinary doc edits, and distributing the skill package installs nothing.

4. **First-time setup (approved, only when `docs/docsHtmlView/` does not exist).** The TOC and source docs already exist, so only the workspace dir is created — **after** the inspection and your approval:

   ```bash
   mkdir -p docs/docsHtmlView
   ( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
   ```

   Then, **only for the newly generated config**:
   - replace the generated `conf.py` using `assets/conf.py.template`. The template leaves `__SITE_TITLE__` / `__AUTHOR__` / `__RELEASE__` **unquoted**, so use `template_text.replace(token, repr(value))` for each token. Never interpolate raw user text unescaped into executable config source. These tokens are only fallbacks: the generated `_meta.json` supplies the real title, author, and version at build time;
   - copy `assets/guard.py` to `docs/docsHtmlView/guard.py`;
   - remove the quickstart's generated `index.rst` (the cover is generated `index.md`);
   - edit the generated `Makefile`: set `SOURCEDIR = ..` and `BUILDDIR = build` (replace the generated `SOURCEDIR = .` / `BUILDDIR = _build`), and either change the generated `SPHINXOPTS    ?=` line to `SPHINXOPTS = -c . -w build/warnings.log` or pass it on the `make` command line (below). Optionally remove the now-unused generated `_build/`. (`make.bat` may be edited the same way; not required on Linux/macOS.)

   If `docs/docsHtmlView/` already exists, **do not overwrite**: present an explicit manual merge plan and let the user apply it. Re-running setup never re-scaffolds.

5. **Generate the publication (before every build).** The helper validates `docs/toc.yml`, expands globs and `modules: auto`, and writes only marked files under the workspace. It exits non-zero on an invalid/unsafe TOC or output collision, and never runs Sphinx:

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_prd.py --project-root .
   ```

   It writes the cover, conditional `nav/**` section landing pages, `glossary.md`, `_manifest.json`, and `_meta.json`, and prunes its own stale marked files. It never edits `docs/toc.yml` or the source documents; to change the publication, edit the TOC and re-run it. `--json` prints a machine-readable summary.

6. **Build (repeatable without re-approval).**

   ```bash
   mkdir -p docs/docsHtmlView/build
   ( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
   ```

   If `make` is unavailable, use the same paths explicitly:

   ```bash
   mkdir -p docs/docsHtmlView/build
   ( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
   ```

   Output lands under `docs/docsHtmlView/build/html`; because `root_doc = docsHtmlView/index`, the **cover is `docs/docsHtmlView/build/html/docsHtmlView/index.html`**. The build also writes a root entry page, **`docs/docsHtmlView/build/html/index.html`**, which meta-refreshes to that cover (with a plain link as fallback); open the root entry for convenience. Warnings go to `docs/docsHtmlView/build/warnings.log`. The `build/` dir is created only after approval. Source-doc edits and TOC edits are legitimate rebuilds (re-run `gen_prd.py` first after a TOC change). A change to an approved setting (environment, workspace, output root) requires a fresh ask.

7. **Check.**

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/check_prd.py --project-root .
   ```

   `check_prd.py` validates the TOC, the manifest, PRD source link rules, glossary freshness, built HTML anchors, the generated root entry, the absence of template-provenance text, and that no unlisted `product/`/`current/`/`adr/` page was built. `--skip-html` limits it to the source-side checks.

8. **Report.** Summarise the normal Sphinx result and the check result — see Statuses below.

## Safety model

The boundary is a small template Sphinx extension (`assets/guard.py`), not a build orchestrator. It is a best-effort guard for **trusted** project docs, not a universal sandbox; the project's own `conf.py` remains executable Python.

- **File insertion blocked at parse time:** `include`, `literalinclude`, and `raw` directives are replaced by a refusing directive (case-insensitive, so `INCLUDE` too; also reached through `eval-rst` and MyST colon fences). Active/raw HTML is refused; only pure HTML-comment (plus whitespace) raw nodes are allowed, so the harmless `<!-- ... -->` comments in PRD templates render — but no comment+markup smuggling. No regex-only scan is relied on.
- **Local assets checked before copy:** at `doctree-read` (priority 100, before Sphinx's asset collectors copy anything) every parsed image and download target is resolved with the environment's reference resolver and must resolve (symlinks included) inside an approved root, or the build fails. Reference-style images, `:download:`, and uppercase directives are covered.
- **Remote assets are never fetched:** remote images/downloads are replaced with an inline placeholder and a Sphinx warning is emitted, so a clean build is not reported as full fidelity.
- **Provenance markers stripped at render time:** leading `模板来源` (template-origin) markers — either a blockquote or an `<!-- ... -->` comment, before the first heading — are removed from the in-memory source at `source-read`, so the published copy omits them. Sphinx's copied `_sources/**/*.txt` files are sanitized at `build-finished` too. Only leading markers are affected; body occurrences are left alone and the source files on disk are never modified.
- **Navigation is generated, not authored:** `gen_prd.py` writes only marked files (`% docs-html-view: generated navigation; do not edit`, a MyST comment that renders as no content) and JSON files carrying `"generated_by": "docs-html-view gen_prd.py"`. It sanitizes generated titles (no `<`, `>`, backticks, braces, brackets, pipes, or newlines) and runs a full preflight — output directories, any existing `nav/`, and every output/collision are checked for symlinks and unmarked files before the first write, so a refusal leaves the tree unchanged. It prunes only its own marked stale files and never writes into source trees.
- **Exact include manifest:** `conf.py` builds `include_patterns` from `_manifest.json` plus the generated cover, any section landing pages, and the glossary. Unlisted documents are excluded even if they exist under the roots.

Approved scope that links out to unlisted docs produces ordinary Sphinx "missing reference" warnings; those are reported, never auto-added. `check_prd.py` catches PRD-layer link violations in the sources.

## Statuses

Read the normal Sphinx exit code, the warning log (`build/warnings.log`), and the check result:

- **clean success** — `gen_prd.py` generated, build exited 0, the warning log is empty, and `check_prd.py` exits 0.
- **preview with warnings** — build exited 0 but the warning log has entries; report the first warnings and the log path. Warnings do not by themselves fail `check_prd.py`.
- **generation refusal** — `gen_prd.py` exits 1 (missing/invalid `docs/toc.yml`, path outside the allowed roots, duplicate document, symlink, or an unmarked output collision). Report the message, fix the TOC/collision, and do not build stale output.
- **check failure** — `check_prd.py` exits 1 on a TOC/manifest mismatch, a PRD external/SPEC/Current/ADR link, a status marker, a stale glossary, a broken built anchor, a provenance leak, or an unlisted built page. Summarise the `file:line` / `file: #id` lines; do not present a failing build as valid.
- **failure** — `guard.py` rejected the build or Sphinx exited non-zero. A failed `make` may leave stale or partial output under `build/`; state that clearly and do not present it as a fresh build. There is no publisher step: whatever `make` left is what exists.

## Limitations

- Supported sources are `.md` and `.rst` under `docs/product`, `docs/current`, and `docs/adr`, plus the root `CONTEXT.md`. `.mdx` and other extensions are not rendered.
- `docs/toc.yml` must exist and list the required sections (`overview`, `requirements`, `architecture`, `appendix`) and appendix ids (`glossary`, `spec`, `current`, `adr`). Missing paths, symlinks, duplicates, and paths outside the allowed roots are refused rather than skipped.
- Module sidecars (`00-index.md`) and `design/` files are not published unless the TOC explicitly lists them; the default TOC globs do not.
- The glossary is generated from `CONTEXT.md` as-is; keep it text-only. A relative image in `CONTEXT.md` would resolve inside `docsHtmlView/` (outside the approved roots) and fail the build.
- `include` / `literalinclude` / `raw` are refused; this is not an arbitrary-Markdown renderer.
- Remote images/downloads become inline placeholders plus a Sphinx warning; active HTML is refused, so "no browser network" is not claimed for arbitrary markup.
- The guard is a trusted-doc guardrail, not a sandbox for untrusted input.
- The dependency helper installs only the pinned requirements, only with `--install`, and only after consent; it never installs Python or uv.
- No custom theme, browser, server, or deployment.

See `references/technical.md` for the exact commands, TOC schema, generated artifacts, config keys, and validation rules.
