# docs-html-view technical reference

## Pinned dependencies

Verified on PyPI (2026-10); the set is mutually compatible. Sphinx 9.1.0 requires Python >= 3.12.

| Package | Pin | Note |
| :--- | :--- | :--- |
| Sphinx | `Sphinx==9.1.0` | needs Python >= 3.12 |
| MyST parser | `myst-parser==5.1.0` | Markdown support |
| RTD theme | `sphinx-rtd-theme==3.1.0` | stock theme via `html_theme` |
| PyYAML | `PyYAML==6.0.2` | `gen_prd.py` / `check_prd.py` read `docs/toc.yml` |

`requirements.txt` ships this declaration. `prepare_env.py` installs nothing unless `--install` is passed; the caller runs it only after approval.

## Layout

```
<project root>/
  .venv-docs/                     # default render venv (or the project's docs env)
  CONTEXT.md                      # glossary source (copied, never modified)
  docs/                           # Sphinx source root
    toc.yml                       # publication source of truth
    product/                      # core PRD + module PRD/SPEC
      00-README.md                # PRD cover/overview
      01-requirements.md          # PRD requirements
      02-architecture.md          # PRD architecture + module map
      <NN-module>/
        00-README.md              # module PRD (published by modules: auto)
        00-index.md               # agent sidecar (not listed -> not published)
        01-spec.md 02-interfaces.md 03-nfr.md
        design/                   # not listed by default -> not published
    current/                      # as-built snapshot
    adr/                          # decisions
    docsHtmlView/                 # workspace
      conf.py                     # from assets/conf.py.template
      guard.py                    # copied from assets/guard.py
      index.md                    # generated cover (marked)
      nav/<id>/index.md           # generated section landing pages, only where needed (marked)
      glossary.md                 # generated from CONTEXT.md (marked)
      _manifest.json              # generated exact include list
      _meta.json                  # generated title/version/date/abstract/author
      build.sh                    # seeded build helper (POSIX sh; seeded only if missing)
      build.bat                   # seeded build helper (Windows batch; seeded only if missing)
      build/html/docsHtmlView/index.html   # publication cover
      build/html/index.html       # generated root entry (meta-refresh to the cover)
```

`docsHtmlView` is the workspace directory name, not the publication title. The title comes from `docs/toc.yml`.

## Files shipped by this skill

- `scripts/prepare_env.py` — create/reuse a recognized venv; optional pinned install / freeze. Stdlib only.
- `scripts/gen_prd.py` — validate `docs/toc.yml`, expand globs/`modules: auto`, generate the cover, conditional section landing pages, glossary, and manifests; seed the two build helpers when missing. Publication content is marked files only; the helpers are unmarked and user-owned.
- `scripts/check_prd.py` — validate TOC, manifest, PRD source links, glossary freshness, built anchors, and unlisted pages. Stdlib + PyYAML.
- `assets/conf.py.template` — the managed `conf.py` for a new publication.
- `assets/guard.py` — the parse/render guard extension.
- `assets/build.sh` — POSIX sh build helper, seeded into the workspace only when missing.
- `assets/build.bat` — Windows batch build helper, seeded into the workspace only when missing.
- `requirements.txt` — the pins.

## Commands

Inspect is done with normal read-only tools; there is no inspect subcommand and nothing runs the project interpreter before approval. After approval, define the prepared environment's absolute paths from the project root (override `--venv` to reuse a project docs env):

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="TOC TITLE"                                # title read from docs/toc.yml
DOCS_PY="$PWD/.venv-docs/bin/python"                 # venv python
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # venv sphinx-build
```

First-time setup (new workspace only; skip if `docs/docsHtmlView/` already exists and instead show a manual merge plan):

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
mkdir -p docs/docsHtmlView
( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
# apply assets/conf.py.template -> docs/docsHtmlView/conf.py
#   tokens are UNQUOTED; replace __SITE_TITLE__/__AUTHOR__/__RELEASE__ with repr(value)
# copy assets/guard.py -> docs/docsHtmlView/guard.py
# remove the generated docs/docsHtmlView/index.rst
# Makefile: SOURCEDIR = ..   BUILDDIR = build   SPHINXOPTS = -c . -w build/warnings.log
"$DOCS_PY" "$SKILL"/scripts/gen_prd.py --project-root .
# gen_prd.py also seeds docs/docsHtmlView/build.sh and build.bat when missing
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
"$DOCS_PY" "$SKILL"/scripts/check_prd.py --project-root .
```

One-click rebuild (helpers seeded by `gen_prd.py` only when missing; never overwritten):

```bash
( cd docs/docsHtmlView && ./build.sh )            # POSIX sh; seeded executable
( cd docs/docsHtmlView && ./build.sh --clean )    # delete build/ first
( cd docs/docsHtmlView && DOCS_PY=/path/to/.venv-docs/bin/python ./build.sh )
```
```bat
docs\docsHtmlView\build.bat                       :: Windows (from the project root)
docs\docsHtmlView\build.bat --clean
```

Both helpers `cd` to `docs/docsHtmlView` and use `DOCS_PY` if set, otherwise `../../.venv-docs/bin/python` (`..\..\.venv-docs\Scripts\python.exe` on Windows). Before building they require the render environment plus `conf.py`, `guard.py`, `_manifest.json`, `_meta.json`, and `index.md`; otherwise they print an error to run the docs-html-view skill first and exit non-zero without building. `--clean` is the only option; unknown or extra arguments print `usage: ... [--clean]` and exit 2. They then run exactly:

```bash
"$PY" -m sphinx -b html -c . -d build/doctrees -w build/warnings.log .. build/html
```

and print the warnings count plus the root entry and cover paths. The helpers build only: they never generate content, run `check_prd.py`, install packages, look for the skill directory, or open a browser/server. Re-run `gen_prd.py` first after changing `docs/toc.yml`, `CONTEXT.md`, or the module set.

Repeat render (same approved scope; re-run the generator after every TOC change):

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_prd.py --project-root .
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
"$DOCS_PY" "$SKILL"/scripts/check_prd.py --project-root .
```

No `make`:

```bash
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
```

`check_prd.py --skip-html` runs only the source-side checks. The skill stops at the local `docs/docsHtmlView/build/html` folder; packaging, hosting, and delivery are outside its scope and remain the user's decision.

`gen_prd.py` exits `1` on an invalid or unsafe TOC (missing metadata/ids/paths, duplicate explicit document, symlink, path outside the allowed roots), a missing workspace, or an unmarked output collision. It exits `0` after writing the publication and prints generated/manifest counts; `--json` prints the resolved documents, manifest, generated files, and pruned files on stdout. Warnings (empty glob, no modules, legacy `docs/prd/`) go to stderr.

Optional resolved-version snapshot (approved output):

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsHtmlView/requirements.lock.txt
```

`prepare_env.py` flags: `--project-root` (default cwd), `--venv` (default `.venv-docs`, relative to project root unless absolute), `--base-python` (interpreter used to create the venv), `--requirements`, `--install`, `--freeze PATH`. It refuses to reuse a path that exists without `pyvenv.cfg`, refuses Python < 3.12, and refuses `--install`/`--freeze` unless the interpreter actually belongs to the target venv. It never installs Python/uv and never uses global/system pip.

`gen_prd.py` flags: `--project-root` (default cwd), `--json`.

`check_prd.py` flags: `--project-root` (default cwd), `--html-dir` (default `docs/docsHtmlView/build/html`), `--skip-html` (source checks only). Exit 0 = clean, 1 = violations or missing inputs.

## TOC schema (`docs/toc.yml`)

```yaml
title: <publication title>
version: <version>
date: <date>
abstract: <one paragraph>
# author: <optional; used when the template __AUTHOR__ fallback is empty>

sections:
  - id: overview
    title: 项目说明与典型应用场景
    documents: [docs/product/00-README.md]
  - id: requirements
    title: 产品需求
    documents: [docs/product/01-requirements.md]
  - id: architecture
    title: 架构设计与模块划分
    documents: [docs/product/02-architecture.md]
    modules: auto
    exclude: []
  - id: appendix
    title: 附录
    sections:
      - id: glossary
        title: 术语表
        documents: [CONTEXT.md]
      - id: spec
        title: SPEC（技术规格）
        documents:
          - docs/product/*/01-spec.md
          - docs/product/*/02-interfaces.md
          - docs/product/*/03-nfr.md
      - id: current
        title: 项目现状
        documents: [docs/current/00-README.md, docs/current/**/*.md]
      - id: adr
        title: 架构决策
        documents: [docs/adr/README.md]
```

Rules enforced by `gen_prd.py` and repeated by `check_prd.py`:

- The TOC is a mapping with non-empty `title`, `version`, `date`, `abstract`, and a non-empty `sections` list. `author` is optional.
- Top-level section ids must include `overview`, `requirements`, `architecture`, `appendix`. The `appendix` children must include `glossary`, `spec`, `current`, `adr`. Extra sections are allowed.
- A section needs a non-empty `title` and at least one of `documents`, `sections`, or `modules: auto`. Ids must be unique, safe directory names (`[A-Za-z0-9._-]`, no separators).
- `documents` entries are paths or globs relative to the project root. They must resolve under `docs/product`, `docs/current`, or `docs/adr`, or be exactly `CONTEXT.md`. Globs support `*` and `**`; matches are sorted, and overlapping/glob duplicates are de-duplicated. Explicitly listing the same document twice (or in two sections) is an error.
- `modules: auto` expands `docs/product/*/00-README.md` (module PRDs), sorted by numeric prefix then case-insensitive name. `exclude` accepts a module directory name (`08-internal`), a project-relative path (`docs/product/08-internal`), or a document path.
- `design/` is not published by default: the default SPEC globs do not reach it, and unlisted files never enter the manifest.
- `CONTEXT.md` maps to the generated `docsHtmlView/glossary.md`; it is required only when the glossary section lists it.
- Document paths must be regular `.md`/`.rst` files with no symlink components. Missing paths fail the TOC (not silently skipped).

To change the publication, edit `docs/toc.yml` — never the generated files — then re-run `gen_prd.py` before building.

## Generated artifacts

All generated Markdown files start with a MyST comment marker (`% docs-html-view: ...`) that renders as nothing; JSON files carry `"generated_by": "docs-html-view gen_prd.py"`. Only marked/owned files are overwritten or pruned.

### `docsHtmlView/build.sh` / `build.bat` (seeded helpers)

`gen_prd.py` seeds these two helpers **only when the files are missing** and never overwrites an existing one. They are user-owned after seeding (edit freely), carry no `%` marker, are not pruned, and are not listed in `_manifest.json` or `_meta.json`. Both `cd` to `docs/docsHtmlView` and run `"$PY" -m sphinx -b html -c . -d build/doctrees -w build/warnings.log .. build/html`, where `PY` comes from `DOCS_PY` or defaults to `../../.venv-docs/bin/python` (`..\..\.venv-docs\Scripts\python.exe` on Windows). `--clean` removes `build/` first and is the only option. The helpers build only: they do not generate, validate, install, or look for the skill directory. `--json` reports their status in a `build_helpers` map; human output prints each helper's status.

### Provenance stripping (published copies only)

`guard.py` strips leading `模板来源` (template-origin) markers at `source-read`, before rendering. Two forms are recognized: a blockquote line beginning with `模板来源` (plus its immediately following contiguous blockquote lines), or an `<!-- 模板来源 ... -->` HTML comment. Each may be preceded by a BOM and blank lines, must sit before the first heading, and stacked leading markers are stripped one after another. Occurrences later in the body are never touched. Only the in-memory source (`source[0]`) changes; the source files on disk are never modified. Sphinx then copies the original source files into `build/html/_sources/`, so `build-finished` applies the same strip to every copied `*.md.txt` / `*.rst.txt`; the "View page source" link therefore shows clean content too.

### `docsHtmlView/index.md` (cover)

`# title`, a `版本 <version> · <date>` line, the abstract, and a `{toctree}` of the top-level sections. A section flattened to a single document is listed directly by that document's path-only entry (no landing page in between); multi-document and branch sections are listed through their generated landing page (`nav/overview/index`, `nav/appendix/index`, ...). Titles pass through a sanitizer that strips `<`, `>`, backticks, braces, brackets, and pipes.

### `docsHtmlView/nav/<id>/index.md` (conditional section landing pages)

Generated only when needed: after TOC expansion the section resolves to more than one document (including `modules: auto` results), or it has child `sections`. A section that resolves to exactly one document and has no child sections is linked directly from its parent and gets no `nav/<id>/` page.

Each generated page is `# section title` plus a `{toctree}` of path-only entries relative to the page: documents (`../../../product/00-README`) and, for `appendix`, child landing pages (`glossary/index`) or a direct child document when that child was flattened. Nested appendix landing pages live at `nav/appendix/<sub-id>/index.md`.

### `docsHtmlView/glossary.md`

Two marker lines (`generated glossary`, `% source: CONTEXT.md`) followed by the **verbatim** body of the root `CONTEXT.md`. `check_prd.py` compares the body after the header/marker; a stale copy fails.

### `docsHtmlView/_manifest.json`

```json
{
  "generated_by": "docs-html-view gen_prd.py",
  "documents": ["adr/README.md", "current/00-README.md", "docsHtmlView/glossary.md", "product/00-README.md"]
}
```

Paths are relative to `docs/` (i.e. Sphinx source-root-relative). It contains exactly the TOC-expanded source documents plus the generated glossary — never `index.md` or `nav/**`, which `conf.py` adds itself.

### `docsHtmlView/_meta.json`

```json
{
  "generated_by": "docs-html-view gen_prd.py",
  "title": "...", "version": "...", "date": "...", "abstract": "...", "author": ""
}
```

`conf.py` uses `title`/`author`/`version` (falling back to the template tokens only when the value is empty). The cover uses `date` and `abstract` too.

## Sphinx configuration

`SOURCEDIR=..`, config dir `docs/docsHtmlView` (`-c .`), `BUILDDIR=build` → output `build/html`; `SPHINXOPTS = -c . -w build/warnings.log` (create `build/` first) so warnings are captured for reporting. `root_doc = docsHtmlView/index`, so the cover is `build/html/docsHtmlView/index.html`. At `build-finished` (the `html` builder only, and only when the build did not raise) `guard.py` also writes `build/html/index.html`, a root entry page that meta-refreshes to the relative `docsHtmlView/index.html` with a plain-link fallback. Its title is `project`, HTML-escaped, falling back to `Documentation` when empty.

`assets/conf.py.template` reads `_meta.json` and `_manifest.json` from its own directory and **fails clearly** when either is missing (the build must run `gen_prd.py` first). It then sets:

- `project` = meta title or `__SITE_TITLE__`, `author` = meta author or `__AUTHOR__`, `release` = meta version or `__RELEASE__`.
- `include_patterns` — `docsHtmlView/index.md`, `docsHtmlView/nav/**`, `docsHtmlView/glossary.md`, plus every manifest document. There is no `docsHtmlView/**` wildcard and no source-tree-wide wildcard, so unlisted docs are not built.
- `exclude_patterns` — `docsHtmlView/build/**`, `docsHtmlView/.venv*/**`, `.venv-docs/**`, `**/.git/**`.
- `docs_html_view_allowed_roots = ["product", "current", "adr"]` — read by `guard.py`; `CONTEXT.md` is only read by the generator, and its content is published as the generated glossary.
- `myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]`, `myst_heading_anchors = 3`.

There is no environment switch: one TOC, one publication, one output directory.

### Guard (`assets/guard.py`)

- `builder-inited`: registers a refusing directive for `include`, `literalinclude`, `raw` (case-insensitive; also hit via `eval-rst` and colon fences), and validates each allowed root is a simple relative name resolving inside `docs`.
- `source-read`: strips leading `模板来源` provenance markers from the in-memory source only (both blockquote and HTML-comment forms, before the first heading; body occurrences and on-disk files untouched).
- `doctree-read` (priority 100, before Sphinx's asset collectors at 500): rejects any `raw` node that is not purely HTML comment(s)+whitespace (so PRD-template comments pass, active markup fails); for images and `download_reference` nodes, resolves the original reference via `app.env.relfn2path`, requires it inside an approved root using `realpath`/`commonpath` (symlinks rejected), or raises `SphinxError` before any copy; remote targets are replaced with an inline placeholder and a Sphinx warning, never fetched.
- `build-finished`: sanitizes Sphinx's copied `_sources/**/*.md.txt` / `*.rst.txt` with the same provenance strip, then (for `html`-builder builds that completed without an exception) overwrites `build/html/index.html` with the root entry (meta refresh to `docsHtmlView/index.html` plus an `<a>` fallback). The build directory is generated output, so the overwrite is deterministic.
- This is the authoritative boundary and the reason no regex-only scan is used. It guards trusted docs; `conf.py` is trusted executable code and is not sandboxed.

## Validation (`check_prd.py`)

1. **TOC.** Parses `docs/toc.yml` with the generator's own resolver: metadata, required ids, document paths/globs, `modules: auto`, allowed roots, existence, regular files, no symlinks, no duplicates.
2. **Manifest.** `_manifest.json` exists and its document set is exactly the TOC-expanded documents plus `docsHtmlView/glossary.md`. Missing/extra entries fail; every non-glossary source must still exist.
3. **PRD source links.** Scans `docs/product/00-README.md`, `01-requirements.md`, `02-architecture.md`, and `docs/product/*/00-README.md`. HTML comments, fenced code, and inline code are masked. Allowed targets: same-page anchors and relative links to PRD-layer documents (`00-README.md`, `01-requirements.md`, `02-architecture.md`) inside `docs/product`. Flags external URLs, absolute paths, links outside the PRD layer (SPEC/Current/ADR/design/missing), and status markers `✅`/`🚧`/`❌`.
4. **Glossary freshness.** `docsHtmlView/glossary.md` body equals `CONTEXT.md` after the generated marker/header; missing or stale fails.
5. **Built HTML anchors.** Every manifest document plus the generated cover, required section landing pages, glossary, and the root entry `build/html/index.html` must have a built page under `--html-dir`; every same-page `href="#..."` must match an `id`/`<a name>` in that page. Broken/missing fails.
6. **No unlisted docs.** Every `build/html/product/**/*.html`, `current/**`, `adr/**` page must map back to a manifest document; extras fail. A `nav/**` page with no generated counterpart (for example a stale landing page for a section that is now single-document) is also rejected.
7. **Provenance.** No published page and no copied `_sources/**/*.txt` may contain `模板来源`; a leak fails the check.

The summary reports toc documents, manifest entries, PRD files/links checked, glossary state, anchors checked, unlisted docs, and violation count; exit 0 only when the violation count is zero. `--skip-html` omits phases 5–7 (use it before a build). `check_prd.py` does not validate the user-owned build helpers.

## Anchor and link rules

- Use standard Markdown heading links (`[text](#heading)`) targeting h1–h3 (`myst_heading_anchors = 3`). With Chinese heading slug mismatches, prefer adjusting the heading, then fall back to an explicit MyST target.
- PRD core and module PRDs link **only** within the PRD layer (product chapters and module PRDs). SPEC, Current, ADR, external URLs, and status markers are rejected by `check_prd.py`; they belong in the appendices, not the PRD narrative.
- Pages under `docs/current` and `docs/adr` may link freely; they are appendices. Only the built anchors are checked there.

## Approval and consent

The Skill asks once, before any write/install/scaffold, covering packages, environment, files, `.gitignore` additions, output path, and the TOC title/version. There is no stored consent state or fingerprint. Repeated renders inside the approved scope do not re-ask; dependency upgrades, overwriting existing files, or changing the approved output root require a fresh ask. The build helpers are part of the created-files list and are seeded only when missing; existing helper files are never overwritten. Missing TOC/source docs or a malformed workspace → report and stop, never guess. The template tokens are unquoted, so substitute each with `repr(value)` (a valid, escaped Python literal), never raw interpolation into executable config.

## Limitations

- `.md` / `.rst` only; no `.mdx`.
- `include` / `literalinclude` / `raw` refused.
- Remote assets become inline placeholders plus a warning; active HTML is refused (only HTML comments are allowed), and `conf.py` is trusted code.
- No custom theme, browser, server, or deployment.
- Only documents listed in `docs/toc.yml` are published. Module sidecars (`00-index.md`) and `design/` are excluded by the default TOC; adding them explicitly makes them public.
- The glossary is the verbatim `CONTEXT.md` body. A relative image inside it resolves under `docsHtmlView/`, outside the approved roots, so the build fails; keep the glossary text-only.
- The build helpers build only; they do not regenerate. TOC, `CONTEXT.md`, or module-set changes require re-running the skill so `gen_prd.py` refreshes the generated files first.
- The helpers require the render environment and the generated workspace files (`conf.py`, `guard.py`, `_manifest.json`, `_meta.json`, `index.md`), and they neither install dependencies nor validate the result.
- Failed `make` or a failed helper may leave stale/partial `build/` output; no publisher normalises it.
