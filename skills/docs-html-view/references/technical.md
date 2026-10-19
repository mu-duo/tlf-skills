# docs-html-view technical reference

## Pinned dependencies

Verified on PyPI 2026-10-14; the set is mutually compatible. Sphinx 9.1.0 requires Python >= 3.12.

| Package | Pin | Note |
| :--- | :--- | :--- |
| Sphinx | `Sphinx==9.1.0` | needs Python >= 3.12 |
| MyST parser | `myst-parser==5.1.0` | Markdown support |
| RTD theme | `sphinx-rtd-theme==3.1.0` | stock theme via `html_theme` |

`requirements.txt` ships this declaration. `prepare_env.py` installs nothing unless `--install` is passed; the caller runs it only after approval.

## Layout

```
<project root>/
  .venv-docs/                     # default render venv (or the project's docs env)
  docs/                           # Sphinx source root
    prd|current|adr/              # approved trees, never modified
    issues/ agents/ ...           # excluded
    docsHtmlView/                 # workspace
      conf.py                     # from assets/conf.py.template
      guard.py                    # copied from assets/guard.py
      index.md                    # generated landing page (marked)
      nav/<tree>/**/index.md      # generated toctrees (marked)
      docs-html-view.config.json  # optional, user-authored
      build/html/docsHtmlView/index.html   # landing page (root_doc = docsHtmlView/index)
```

`docsHtmlView` is the workspace directory name, not the site name.

## Files shipped by this skill

- `scripts/prepare_env.py` — create/reuse a recognized venv; optional pinned install / freeze. Stdlib only.
- `scripts/gen_nav.py` — generate `index.md` + `nav/**` toctrees (marked files only).
- `assets/conf.py.template` — the managed `conf.py` for a new site.
- `assets/guard.py` — the parse/render guard extension.
- `requirements.txt` — the pins.

## Commands

Inspect is done with normal read-only tools; there is no inspect subcommand and nothing runs the project interpreter before approval. After approval, define the prepared environment's absolute paths from the project root (override `--venv` to reuse a project docs env):

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="APPROVED TITLE"                           # the confirmed project/site title
DOCS_PY="$PWD/.venv-docs/bin/python"                 # venv python
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # venv sphinx-build
```

First-time setup (new site only; skip if `docs/docsHtmlView/` already exists and instead show a manual merge plan):

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
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE"
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
```

Repeat render (same approved scope and title, no re-ask):

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE"
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
```

No `make`:

```bash
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
```

`gen_nav.py` exits `1` when no approved tree contains documents, so a later `make` cannot silently build a stale site. Warnings (missing/empty trees) go to stderr; `--json` prints the summary on stdout. Without `--title` the site title defaults to `Documentation`; pass the approved `--title` (or set `site_title`) so repeat renders keep the agreed title.

Optional resolved-version snapshot (approved output):

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsHtmlView/requirements.lock.txt
```

`prepare_env.py` flags: `--project-root` (default cwd), `--venv` (default `.venv-docs`, relative to project root unless absolute), `--base-python` (interpreter used to create the venv), `--requirements`, `--install`, `--freeze PATH`. It refuses to reuse a path that exists without `pyvenv.cfg`, refuses Python < 3.12, and refuses `--install`/`--freeze` unless the interpreter actually belongs to the target venv. It never installs Python/uv and never uses global/system pip.

`gen_nav.py` flags: `--project-root` (default cwd), `--title` (site title override), `--json`.


## Sphinx configuration

`SOURCEDIR=..`, config dir `docs/docsHtmlView` (`-c .`), `BUILDDIR=build` → output `build/html`; `SPHINXOPTS = -c . -w build/warnings.log` (create `build/` first) so warnings are captured for reporting. `root_doc = docsHtmlView/index`, so the landing page is `build/html/docsHtmlView/index.html` (the `build/html/` layout is otherwise unchanged; no redirect or extra page).

`conf.py` uses:

- `include_patterns` — **enumerated**: `docsHtmlView/index.md`, `docsHtmlView/nav/**`, and one `<root>/**` per approved tree. Not a `docsHtmlView/**` wildcard.
- `exclude_patterns` — build, `.venv-docs`, workspace venvs, VCS internals.
- `myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]`, `myst_heading_anchors = 3`.
- `docs_html_view_allowed_roots` — the same roots, read by `guard.py`.

**Changing `allowed_dirs` is a manual, approved edit with no automatic sync.** Update all three by hand — `include_patterns` and `docs_html_view_allowed_roots` in `conf.py`, and `allowed_dirs` in `docs-html-view.config.json` — then re-run `gen_nav.py`; a mismatch between them must be resolved before `make`. Missing/empty trees are fine (reported and skipped).

### Guard (`assets/guard.py`)

- `builder-inited`: registers a refusing directive for `include`, `literalinclude`, `raw` (case-insensitive; also hit via `eval-rst` and colon fences), and validates each allowed root is a simple relative name resolving inside `docs`.
- `doctree-read` (priority 100, before Sphinx's asset collectors at 500): rejects any `raw` node that is not purely HTML comment(s)+whitespace (so PRD-template comments pass, active markup fails); for images and `download_reference` nodes, resolves the original reference via `app.env.relfn2path`, requires it inside an approved root using `realpath`/`commonpath` (symlinks rejected), or raises `SphinxError` before any copy; remote targets are replaced with an inline placeholder and a Sphinx warning, never fetched.
- This is the authoritative boundary and the reason no regex-only scan is used. It guards trusted docs; `conf.py` is trusted executable code and is not sandboxed.

## Optional project config

`docs/docsHtmlView/docs-html-view.config.json` is user-authored and never overwritten. It must be a JSON object; a parse error, a non-object, a non-string `site_title`, a non-string `navigation_order`, or an unsafe `allowed_dirs` entry is refused (not silently dropped).

| Key | Read by | Effect |
| :--- | :--- | :--- |
| `site_title` | `gen_nav.py` | site title (also settable via `gen_nav.py --title`) |
| `allowed_dirs` | `gen_nav.py` | explicit trees; one directory name each (no separators, not hidden, not `build`/`docsHtmlView`); defaults to `prd`, `current`, `adr` |
| `navigation_order` | `gen_nav.py` | list of path strings relative to `docs/` placed first, in order; then numeric prefix, then case-insensitive name |
| `author`, `release` | human / agent only | template token values when applying `conf.py.template`; not read by the scripts |
| `python` | human / agent only | preferred interpreter when choosing the venv path; not read by the scripts |

## Navigation rules

- Marked generated files only (`% docs-html-view: generated navigation; do not edit`, a MyST comment); unmarked collisions and symlinks are refused.
- **Preflight before any write:** approved dirs, source trees, and any existing `nav/` (including ancestors) are checked for symlinks; every output path and existing collision is validated before the first write or prune, so a refusal leaves the tree unchanged.
- `gen_nav.py` exits `1` when no approved tree has documents, and prints warnings (missing/empty trees) to stderr.
- A populated legacy `docs/pdr/` tree that is not among the resolved roots is reported with `warning: legacy docs/pdr/ detected; not rendered. Migrate to docs/prd/ or add "pdr" to allowed_dirs explicitly.` It is never moved or renamed, and it is not rendered by default. To render it as-is, add `pdr` explicitly to `allowed_dirs` (and, per the manual-sync rule above, to `include_patterns` and `docs_html_view_allowed_roots`); the warning does not fire when `pdr` is explicitly allowed or rendered.
- Hierarchy mirrors the tree; each directory gets a `{toctree}` of its documents and child-index links; entry titles come from the source H1 (path-only toctree entries), so no source text can inject MyST.
- Directory/site headings are sanitized (no `<`, `>`, backticks, braces, brackets, pipes, newlines).
- The full ADR tree renders, including retired/deleted tombstones.
- Re-running prunes only marked stale nav files; user files are never touched.


## Approval and consent

The Skill asks once, before any write/install/scaffold, covering packages, environment, files, `.gitignore` additions, output path, and title. There is no stored consent state or fingerprint. Repeated renders inside the approved scope do not re-ask; dependency upgrades, overwriting existing files, or changing the approved roots/range require a fresh ask. Missing trees or malformed required config/venv → report and stop, never guess. The template tokens are unquoted, so substitute each with `repr(value)` (valid, escaped Python literal), never raw interpolation into executable config.

## Limitations

- `.md` / `.rst` only; no `.mdx`.
- `include` / `literalinclude` / `raw` refused.
- Remote assets become inline placeholders plus a warning; active HTML is refused (only HTML comments are allowed), and `conf.py` is trusted code.
- No custom theme, browser, server, or deployment.
- Failed `make` may leave stale/partial `build/` output; no publisher normalises it.
