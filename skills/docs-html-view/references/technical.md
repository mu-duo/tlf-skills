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
      index.md                    # generated full-site landing page (marked)
      nav/<tree>/**/index.md      # generated full-site toctrees (marked)
      l1/index.md                 # generated L1-only toctree (marked)
      docs-html-view.config.json  # optional, user-authored
      build/html/docsHtmlView/index.html        # full-site landing page
      build-l1/html/docsHtmlView/l1/index.html  # L1-only landing page
```

`docsHtmlView` is the workspace directory name, not the site name.

## Files shipped by this skill

- `scripts/prepare_env.py` — create/reuse a recognized venv; optional pinned install / freeze. Stdlib only.
- `scripts/gen_nav.py` — generate `index.md` + `nav/**` toctrees (full) or `l1/index.md` (L1); marked files only.
- `scripts/check_l1.py` — validate L1 source link rules and built HTML anchors. Stdlib only.
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
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile full
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
```

Repeat render (same approved scope and title, no re-ask):

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile full
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && make html SPHINXBUILD="$DOCS_SPHINXBUILD" SPHINXOPTS='-c . -w build/warnings.log' )
```

No `make`:

```bash
mkdir -p docs/docsHtmlView/build
( cd docs/docsHtmlView && "$DOCS_SPHINXBUILD" -b html -c . -d build/doctrees -w build/warnings.log .. build/html )
```

L1-only profile (opt-in; requires `docs/prd/00-README.md`). The L1 build reads only the L1 layer, but config is still validated (`landing_page` must resolve if set):

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile l1
mkdir -p docs/docsHtmlView/build-l1
( cd docs/docsHtmlView && DOCS_HTML_VIEW_PROFILE=l1 "$DOCS_SPHINXBUILD" -b html -c . \
    -d build-l1/doctrees -w build-l1/warnings.log .. build-l1/html )
"$DOCS_PY" "$SKILL"/scripts/check_l1.py --project-root . --html-dir docs/docsHtmlView/build-l1/html
python3 -c "import shutil; shutil.make_archive('docs/docsHtmlView/build-l1/l1-docs', 'zip', 'docs/docsHtmlView/build-l1/html')"
# or: (cd docs/docsHtmlView/build-l1 && zip -r l1-docs.zip html)
```

The recipient opens `docsHtmlView/l1/index.html` inside `docs/docsHtmlView/build-l1/l1-docs.zip`. Zip the folder, not a single HTML file; re-zip after a successful build and check. `check_l1.py --skip-html` runs only the source link rules.

`gen_nav.py` exits `1` when no approved tree contains documents (full) or no `00-README.md` exists under `l1_roots` (L1); for the L1 profile with the `prd` root active, it also exits `1` when the product L1 `docs/prd/00-README.md` is missing, even if module L1 files exist. A later build therefore cannot silently produce a stale site. Warnings (missing/empty trees) go to stderr; `--json` prints the summary on stdout. Without `--title` the site title defaults to `Documentation`; pass the approved `--title` (or set `site_title`) so repeat renders keep the agreed title.

Optional resolved-version snapshot (approved output):

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsHtmlView/requirements.lock.txt
```

`prepare_env.py` flags: `--project-root` (default cwd), `--venv` (default `.venv-docs`, relative to project root unless absolute), `--base-python` (interpreter used to create the venv), `--requirements`, `--install`, `--freeze PATH`. It refuses to reuse a path that exists without `pyvenv.cfg`, refuses Python < 3.12, and refuses `--install`/`--freeze` unless the interpreter actually belongs to the target venv. It never installs Python/uv and never uses global/system pip.

`gen_nav.py` flags: `--project-root` (default cwd), `--title` (site title override), `--profile {full,l1}` (default `full`), `--json`.

`check_l1.py` flags: `--project-root` (default cwd), `--html-dir` (default `docs/docsHtmlView/build-l1/html`), `--skip-html` (source checks only). Exit 0 = clean, 1 = violations or missing inputs. It prints `L1 files checked`, `links checked`, `broken anchors`, and `violations`.


## Sphinx configuration

`SOURCEDIR=..`, config dir `docs/docsHtmlView` (`-c .`), `BUILDDIR=build` → output `build/html`; `SPHINXOPTS = -c . -w build/warnings.log` (create `build/` first) so warnings are captured for reporting. `root_doc = docsHtmlView/index`, so the landing page is `build/html/docsHtmlView/index.html` (the `build/html/` layout is otherwise unchanged; no redirect or extra page).

`PROFILE = os.environ.get("DOCS_HTML_VIEW_PROFILE", "full")` selects the view. `full` keeps the settings above. `l1` sets:

- `root_doc = "docsHtmlView/l1/index"`;
- `include_patterns = ["docsHtmlView/l1/index.md", "prd/00-README.md", "prd/**/00-README.md"]`;
- `exclude_patterns` covering `docsHtmlView/build/**`, `docsHtmlView/build-l1/**`, `docsHtmlView/nav/**`, `docsHtmlView/.venv*/**`, `.venv-docs/**`, `**/.git/**`;
- `docs_html_view_allowed_roots = ["prd"]`.

`conf.py` uses:

- `include_patterns` — **enumerated**: for `full`, `docsHtmlView/index.md`, `docsHtmlView/nav/**`, and one `<root>/**` per approved tree; for `l1`, the L1 index plus `prd/00-README.md` / `prd/**/00-README.md`. Not a `docsHtmlView/**` wildcard.
- `exclude_patterns` — build outputs (including `build-l1`), `.venv-docs`, workspace venvs, VCS internals; `l1` also excludes `docsHtmlView/nav/**`.
- `myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]`, `myst_heading_anchors = 3`.
- `docs_html_view_allowed_roots` — the same roots for the active profile, read by `guard.py`.

**Changing `allowed_dirs` is a manual, approved edit with no automatic sync.** Update all three by hand — `include_patterns` and `docs_html_view_allowed_roots` in `conf.py`, and `allowed_dirs` in `docs-html-view.config.json` — then re-run `gen_nav.py`; a mismatch between them must be resolved before `make`. Missing/empty trees are fine (reported and skipped).

### Guard (`assets/guard.py`)

- `builder-inited`: registers a refusing directive for `include`, `literalinclude`, `raw` (case-insensitive; also hit via `eval-rst` and colon fences), and validates each allowed root is a simple relative name resolving inside `docs`.
- `doctree-read` (priority 100, before Sphinx's asset collectors at 500): rejects any `raw` node that is not purely HTML comment(s)+whitespace (so PRD-template comments pass, active markup fails); for images and `download_reference` nodes, resolves the original reference via `app.env.relfn2path`, requires it inside an approved root using `realpath`/`commonpath` (symlinks rejected), or raises `SphinxError` before any copy; remote targets are replaced with an inline placeholder and a Sphinx warning, never fetched.
- This is the authoritative boundary and the reason no regex-only scan is used. It guards trusted docs; `conf.py` is trusted executable code and is not sandboxed.

## Optional project config

`docs/docsHtmlView/docs-html-view.config.json` is user-authored and never overwritten. It must be a JSON object; a parse error, a non-object, a non-string `site_title`, a non-string `navigation_order`, an unsafe `allowed_dirs` entry, or a malformed `landing_page` / `l1_roots` is refused (not silently dropped).

| Key | Read by | Effect |
| :--- | :--- | :--- |
| `site_title` | `gen_nav.py` | site title (also settable via `gen_nav.py --title`) |
| `allowed_dirs` | `gen_nav.py` | explicit trees; one directory name each (no separators, not hidden, not `build`/`docsHtmlView`); defaults to `prd`, `current`, `adr` |
| `navigation_order` | `gen_nav.py` | list of path strings relative to `docs/` placed first, in order; then numeric prefix, then case-insensitive name |
| `landing_page` | `gen_nav.py` | path relative to `docs/` (e.g. `prd/00-README.md`) linked prominently at the top of the full-site `index.md`; must exist inside an approved root and not be a symlink (validated whenever set) |
| `landing_page_label` | `gen_nav.py` | optional heading/link label for `landing_page`; defaults to the target's H1, then the filename stem |
| `l1_roots` | `gen_nav.py` | L1 profile roots (approved root names); defaults to `["prd"]` when `prd` is approved, else `[]` |
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

### L1 profile

- Detection is by filename: regular `00-README.md` files under `l1_roots`, recursively. Symlinked L1 files are skipped; symlinks anywhere in the tree are refused.
- If no L1 documents exist, `gen_nav.py --profile l1` prints a clear error and exits 1. With the `prd` root active it also exits 1 when the product L1 `docs/prd/00-README.md` is missing, even when module L1 files exist.
- Ordering: `navigation_order` entries first (by path relative to `docs/`), then numeric prefix components, then casefolded path.
- `docsHtmlView/l1/index.md` is one flat `{toctree}` with `:maxdepth: 1` and path-only entries relative to the generated file, e.g. `../../prd/00-README`, `../../prd/01-mod/00-README`. No per-directory nav files are generated.
- The L1 build includes only the generated L1 index and `prd/00-README.md` + `prd/**/00-README.md`. L2 (`01-spec` etc.), Current, ADR, and `00-index.md` are never rendered.
- `docsHtmlView/l1/` gets the same preflight, collision, verify-inside, and marked-file prune checks as `nav/`.
- Source link rules (`check_l1.py`): same-file anchors and relative links to another `00-README.md` under `docs/prd/` only. External URLs, absolute paths, Current/ADR/L2 links, and anything escaping `docs/prd` are violations, reported as `file:line: target`.
- Built anchors: every same-file `href="#..."` in `build-l1/html/prd/**/00-README.html` must match an `id` in that page; broken anchors are reported as `file: #id`. Missing L1 HTML is an error, not a silent pass; `--skip-html` omits the HTML phase.
- Anchor policy differs by view: the full site is not gated by `check_l1.py`; the L1-only build/check is the enforceable path, and a broken L1 anchor is a failure. Template placeholder links inside HTML comments are ignored by the source check.


## Approval and consent

The Skill asks once, before any write/install/scaffold, covering packages, environment, files, `.gitignore` additions, output path, and title. There is no stored consent state or fingerprint. Repeated renders inside the approved scope do not re-ask; dependency upgrades, overwriting existing files, or changing the approved roots/range require a fresh ask. Missing trees or malformed required config/venv → report and stop, never guess. The template tokens are unquoted, so substitute each with `repr(value)` (valid, escaped Python literal), never raw interpolation into executable config. An L1-only build/zip is inside the approved workspace/output set but remains manual: it runs only when requested, never automatically.

## Limitations

- `.md` / `.rst` only; no `.mdx`.
- `include` / `literalinclude` / `raw` refused.
- Remote assets become inline placeholders plus a warning; active HTML is refused (only HTML comments are allowed), and `conf.py` is trusted code.
- No custom theme, browser, server, or deployment.
- The L1 profile recognises `00-README.md` by filename and assumes the `prd` root for `include_patterns` / `allowed_roots`; a different `l1_roots` needs manual `conf.py` edits. It requires the product L1 `docs/prd/00-README.md`; missing → `gen_nav.py --profile l1` exits 1 even when module L1 files exist. Full site: `prd` + `current` + `adr`.
- L1-only output is a folder (or a zip of it); there is no single-file HTML bundle.
- Failed `make` may leave stale/partial `build/` output; no publisher normalises it.
