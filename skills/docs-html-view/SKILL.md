---
name: docs-html-view
description: Render a project's PRD / Current / ADR docs to local HTML with Sphinx + MyST (stock RTD theme), plus an optional L1-only view, after a read-only inspection and explicit approval.
disable-model-invocation: true
argument-hint: "[project root]"
---

# Docs HTML View

Render the human-readable documentation trees of a project (`docs/prd`, `docs/current`, `docs/adr`) into a local HTML site using **standard Sphinx** with MyST (`myst_parser`) and the **stock** `sphinx_rtd_theme`. It also supports the PRD **L1 layer** (product `docs/prd/00-README.md` + module `00-README.md`): a prominent L1 entry in the full site, and an optional L1-only view that can be zipped for distribution. There is no custom renderer: scaffolding uses `sphinx-quickstart`, navigation is a small generated-toctree helper, and the build is `make html` (or a plain `sphinx-build`). The output is a local folder you open yourself; nothing is served or deployed.

This skill is manually triggered and never automatic, and it never fetches anything at build time. It may install the pinned render dependencies, but only after your explicit approval. Inspect read-only, ask for approval **once**, then first-time setup and repeat manual renders run without re-asking — until a setting changes.

## Boundaries

- **User-triggered only.** Never install, scaffold, or build while editing docs.
- **Bounded writes.** The approved set is: `docs/docsHtmlView/` (config, generated navigation including `l1/`, build output), the approved render environment directory (e.g. `.venv-docs/`), and any `.gitignore` additions you approved. Rendering reads `docs/prd`, `docs/current`, `docs/adr` and never rewrites them, and it never writes into source trees.
- **Approved trees only.** Default trees are `prd`, `current`, `adr`; a tree may be extended explicitly in the config file, never auto-expanded. `docs/issues`, `docs/agents`, tooling, and build output are excluded. A missing or empty tree is reported, not created. A pre-rename `docs/pdr/` tree is reported by `gen_nav.py`, never moved, and is not rendered unless `pdr` is explicitly added to `allowed_dirs`. No documents in the approved trees → **stop: do not create `docs/docsHtmlView/`, do not scaffold, do not build.**
- **Stock theme.** No custom UI/design work.
- **No invented links.** Navigation is generated from the real tree; no cross-tree associations are added and no document bodies are rewritten.
- **No browser/server/deploy.** Producing HTML is the end. README/local output only.

## L1 view

The PRD L1 layer is the product `docs/prd/00-README.md` plus each module `docs/prd/<NN-module>/00-README.md`. Two views are available; both are manual and reuse the approved workspace.

- **Full site with a prominent L1 entry.** Set `landing_page` (for example `prd/00-README.md`) in `docs/docsHtmlView/docs-html-view.config.json`. `gen_nav.py --profile full` (the default) then prepends `## <label>` and a link to the L1 page above the toctree in `docsHtmlView/index.md`. `landing_page_label` overrides the label; otherwise the target's H1 is used. `00-index.md` remains secondary module navigation in the generated tree.
- **L1-only profile.** `gen_nav.py --profile l1` writes `docsHtmlView/l1/index.md` with a toctree of the L1 files only: product L1 first by default (a `navigation_order` entry can override the order), then module L1. L2 (`01-spec` etc.), Current, ADR, and `00-index.md` are not included. The build uses `DOCS_HTML_VIEW_PROFILE=l1` and outputs to `docs/docsHtmlView/build-l1/html`.
- **Distribution.** Zip the built L1 **folder** (not a single-file HTML) inside the approved workspace, e.g. `docs/docsHtmlView/build-l1/l1-docs.zip`; the recipient opens `docsHtmlView/l1/index.html` inside the archive. Rebuild and re-zip after doc changes; nothing is published.
- **Anchors.** Use standard Markdown heading links (`[text](#heading)`) targeting h1–h3 (`myst_heading_anchors = 3`). `scripts/check_l1.py` enforces the L1 source link rules (internal anchors and links to another `00-README.md` only) and checks the built HTML anchors. The full site is not gated by `check_l1.py`; the L1-only build/check is the enforceable path, and a broken anchor fails it. With Chinese heading slug mismatches, prefer adjusting the heading, then fall back to an explicit MyST target.

`docs/prd/00-README.md` (the product L1) is required for the L1 profile: `gen_nav.py --profile l1` exits 1 if it is missing, even when module L1 files exist, and Sphinx fails naturally without it. The L1 build stays inside the approved workspace/output set and never rewrites sources; it is not automatic and runs only when the user asks for an L1 deliverable.

## Flow

Run from the project root (`cwd`). Define the skill directory and, after approval, the prepared environment's absolute paths once — `DOCS_PY` is the venv **python**, `DOCS_SPHINXBUILD` the venv **sphinx-build**:

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-html-view}"
SITE_TITLE="APPROVED TITLE"                           # the confirmed project/site title
DOCS_PY="$PWD/.venv-docs/bin/python"                 # or the project's existing docs env
DOCS_SPHINXBUILD="$PWD/.venv-docs/bin/sphinx-build"  # same env
```

1. **Inspect (read-only).** Use normal read-only tools (`ls`, `read`, `grep`) to learn the project: which of `docs/prd`, `docs/current`, `docs/adr` exist and contain documents, whether `docs/docsHtmlView/` already exists, which Python/venv exists, and the real project/site title. **Never execute the project's interpreter or `conf.py` before approval.** If no approved tree contains documents, stop here — there is nothing to render. Report the plan: pins, environment path, files created, `.gitignore` additions, output path, and title.

2. **Ask once.** Get explicit approval **before any write, install, or scaffold**. Cover concretely: packages/pins (`requirements.txt`), where the environment lives, the pip command, the files created, the `.gitignore` additions you propose (e.g. `.venv-docs/`, `docs/docsHtmlView/build/`), the build/output paths (`docs/docsHtmlView/build/html`), and the confirmed site title — `docsHtmlView` is a directory name, not the site name.
   - Within the approved scope, repeated manual rendering does **not** re-ask.
   - Dependency upgrades, overwriting existing files, or changing the approved root/range **do** require a fresh ask.

3. **Prepare the environment (approved only).** Prefer an existing project docs environment; otherwise a project-root `.venv-docs`. No global/system installs, no automatic `uv`/Python installation. If no suitable Python exists, stop and tell the user. The helper is stdlib-only, so run it with any working Python; then point `DOCS_PY`/`DOCS_SPHINXBUILD` at the environment it prepared:

   ```bash
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
   ```

   The helper only creates/reuses a recognized venv (a directory with `pyvenv.cfg`; it refuses to clobber a non-venv) and installs the pinned requirements only when `--install` is passed (after your approval). It never runs on ordinary doc edits, and distributing the skill package installs nothing.

4. **First-time setup (approved, only when `docs/docsHtmlView/` does not exist).** The approved trees already exist, so only the workspace dir is created — **after** the inspection confirmed documents exist and you approved:

   ```bash
   mkdir -p docs/docsHtmlView
   ( cd docs/docsHtmlView && "$DOCS_PY" -m sphinx.cmd.quickstart -q -p "$SITE_TITLE" -a "AUTHOR" -v "1.0" --no-sep )
   ```

   Then, **only for the newly generated config**:
    - replace the generated `conf.py` using `assets/conf.py.template`; the template leaves `__SITE_TITLE__` / `__AUTHOR__` / `__RELEASE__` **unquoted**, so use `template_text.replace(token, repr(value))` for each token. Never interpolate raw user text unescaped into executable config source;
   - copy `assets/guard.py` to `docs/docsHtmlView/guard.py`;
   - remove the quickstart's generated `index.rst` (the landing page is generated `index.md`);
   - edit the generated `Makefile`: set `SOURCEDIR = ..` and `BUILDDIR = build` (replace the generated `SOURCEDIR = .` / `BUILDDIR = _build`), and either change the generated `SPHINXOPTS    ?=` line to `SPHINXOPTS = -c . -w build/warnings.log` or pass it on the `make` command line (below). Optionally remove the now-unused generated `_build/`. (`make.bat` may be edited the same way; not required on Linux/macOS.)

   If `docs/docsHtmlView/` already exists, **do not overwrite**: present an explicit manual merge plan and let the user apply it. Re-running setup never re-scaffolds.

5. **Generate navigation (before every build).** The helper writes only marked files under the workspace, exits non-zero if no approved tree has documents, and never runs Sphinx:

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile full
   ```

   Always pass the approved title (or set `site_title` in the config); without it, the site title silently defaults to `Documentation`. Repeat renders reuse the same agreed `SITE_TITLE`, without re-asking or switching titles. `--profile full` is the default and keeps the existing full-site output; the L1-only view uses `--profile l1` (step 7).

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

   Output lands under `docs/docsHtmlView/build/html`; because `root_doc = docsHtmlView/index`, the **landing page is `docs/docsHtmlView/build/html/docsHtmlView/index.html`** (open that file). The `build/html/` directory layout itself is unchanged — no redirect or extra index page is generated. Warnings go to `docs/docsHtmlView/build/warnings.log`. The `build/` dir is created only after approval. Source-doc edits are legitimate rebuilds. A change to an approved setting (roots, title, environment) requires a fresh ask. Do not wrap `make`/`sphinx-build` in another script.

   **Changing the approved trees is a manual, approved edit.** If `allowed_dirs` changes, update all three together by hand: `include_patterns` and `docs_html_view_allowed_roots` in `docs/docsHtmlView/conf.py`, and `allowed_dirs` in `docs/docsHtmlView/docs-html-view.config.json`; then re-run `gen_nav`. There is no automatic sync, and a mismatch must be resolved before `make`. A missing/empty tree is fine (reported, skipped).

7. **L1-only build (opt-in, only when requested).** Reuse the same approved environment and title; this writes only `docs/docsHtmlView/l1/` and `docs/docsHtmlView/build-l1/`:

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_nav.py --project-root . --title "$SITE_TITLE" --profile l1
   mkdir -p docs/docsHtmlView/build-l1
   ( cd docs/docsHtmlView && DOCS_HTML_VIEW_PROFILE=l1 "$DOCS_SPHINXBUILD" -b html -c . \
       -d build-l1/doctrees -w build-l1/warnings.log .. build-l1/html )
   "$DOCS_PY" "$SKILL"/scripts/check_l1.py --project-root . --html-dir docs/docsHtmlView/build-l1/html
   python3 -c "import shutil; shutil.make_archive('docs/docsHtmlView/build-l1/l1-docs', 'zip', 'docs/docsHtmlView/build-l1/html')"
   ```

   The landing page is `docs/docsHtmlView/build-l1/html/docsHtmlView/l1/index.html`; warnings go to `docs/docsHtmlView/build-l1/warnings.log`. `--skip-html` limits `check_l1.py` to the source link rules. The zip is written to `docs/docsHtmlView/build-l1/l1-docs.zip` inside the approved workspace and contains the whole folder, so the recipient needs no server. Rezip only after a successful build and check.

8. **Report.** Summarise the normal Sphinx result — see Statuses below.

## Safety model

The boundary is a small template Sphinx extension (`assets/guard.py`), not a build orchestrator. It is a best-effort guard for **trusted** project docs, not a universal sandbox; the project's own `conf.py` remains executable Python.

- **File insertion blocked at parse time:** `include`, `literalinclude`, and `raw` directives are replaced by a refusing directive (case-insensitive, so `INCLUDE` too; also reached through `eval-rst` and MyST colon fences). Active/raw HTML is refused; only pure HTML-comment (plus whitespace) raw nodes are allowed, so the harmless `<!-- ... -->` comments in the PRD templates render — but no comment+markup smuggling. No regex-only scan is relied on.
- **Local assets checked before copy:** at `doctree-read` (priority 100, before Sphinx's asset collectors copy anything) every parsed image and download target is resolved with the environment's reference resolver and must resolve (symlinks included) inside an approved root, or the build fails. Reference-style images, `:download:`, and uppercase directives are covered.
- **Remote assets are never fetched:** remote images/downloads are replaced with an inline placeholder and a Sphinx warning is emitted, so a clean build is not reported as full fidelity.
- **Navigation is generated, not authored:** `gen_nav.py` writes only marked files (`% docs-html-view: generated navigation; do not edit`, a MyST comment that renders as no content), sanitizes generated titles (no `<`, `>`, backticks, braces, brackets, pipes, or newlines), and runs a full preflight — approved dirs, source trees, and any existing `nav/` (including ancestors) are checked for symlinks, and every output/collision is validated before the first write, so a refusal leaves the tree unchanged. It removes only its own marked stale nav files and never writes into source trees. The L1 output (`docsHtmlView/l1/`) gets the same symlink, collision, and prune checks.

Approved scope that links out to excluded docs produces ordinary Sphinx "missing reference" warnings; those are reported, never auto-added.

## Statuses

Read the normal Sphinx exit code and the warning log (`build/warnings.log`):

- **clean success** — build exited 0 and the warning log is empty.
- **preview with warnings** — build exited 0 but the warning log has entries; report the first warnings and the log path.
- **failure** — `gen_nav.py` refused (or exited 1 with no documents), `guard.py` rejected the build, or Sphinx exited non-zero. A failed `make` may leave stale or partial output under `build/`; state that clearly and do not present it as a fresh build. There is no publisher step: whatever `make` left is what exists.
- **L1 check failure** — `check_l1.py` exits 1 on an L1 source-rule violation, a broken built anchor, or a missing `build-l1/html` (run the L1 build first or pass `--skip-html`). Summarise the `file:line: target` / `file: #id` lines; do not distribute a failing build.

## Limitations

- Supported sources are `.md` and `.rst` under the approved trees; `.mdx` and other extensions are not rendered.
- The L1 profile recognises `00-README.md` by filename and assumes the `prd` root; other L1 roots require manual `conf.py` edits. It requires the product L1 `docs/prd/00-README.md`: missing → `gen_nav.py` exits 1 (even when module L1 files exist), so stop. The L1-only output is a folder (or zip of it), not a single-file HTML.
- `include` / `literalinclude` / `raw` are refused; this is not an arbitrary-Markdown renderer.
- Remote images/downloads become inline placeholders plus a Sphinx warning; active HTML is refused, so "no browser network" is not claimed for arbitrary markup.
- The guard is a trusted-doc guardrail, not a sandbox for untrusted input.
- The dependency helper installs only the pinned requirements, only with `--install`, and only after consent; it never installs Python or uv.

See `references/technical.md` for the exact commands, template apply steps, config keys, and navigation rules.
