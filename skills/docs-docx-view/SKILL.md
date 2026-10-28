---
name: docs-docx-view
description: Publish a project's PRD as a single Word document from docs/toc.yml with pandoc (bundled 3.9) — cover, table of contents, core PRD chapters, module PRDs, and glossary/SPEC/Current/ADR appendices — after a read-only inspection and explicit approval.
disable-model-invocation: true
argument-hint: "[project root]"
---

# Docs DOCX View

Build one publishable **PRD Word document** from `docs/toc.yml` using **standard pandoc** with the skill's own `reference.docx` template. The publication is a cover, a table of contents, three core PRD chapters, module PRDs, and four appendix groups (glossary, SPEC, Current, ADR), concatenated in TOC order into a single `.docx`. There is no custom renderer: `scripts/gen_docx.py` validates the TOC, remaps headings, rewrites anchors, blanks remote images, and writes one marked `docs/docsDocxView/combined.md`; the seeded `docs/docsDocxView/build.sh` / `build.bat` helper runs pandoc against it. The output is one local Word file; nothing is served, deployed, or published automatically.

This skill is manually triggered and never automatic, and it never fetches anything at render time. It may install the pinned render dependencies, but only after your explicit approval. Inspect read-only, ask for approval **once**, then first-time setup and repeat manual builds run without re-asking — until a setting or the TOC changes.

## Publication model

`docs/toc.yml` is the **single source of truth**. It defines the title, version, date, abstract, and the exact documents to publish:

| Part | Source | Published as |
| :--- | :--- | :--- |
| Cover | `docs/toc.yml` metadata | pandoc title block (Title/Subtitle/Author styles) at the top of `combined.md` |
| Table of contents | generated | one hand-written Word TOC field, depth 1–3 |
| Core sections | `overview`, `requirements`, `architecture` | Heading 1 section bodies |
| Module PRDs | `modules: auto` under `architecture` | documents appended to the architecture section |
| Appendices | `glossary`, `spec`, `current`, `adr` | Heading 2 sections under the `appendix` Heading 1 |
| Glossary | root `CONTEXT.md` | its leading H1 dropped; body under the glossary section's Heading 2 |

`gen_docx.py` also writes `_manifest.json` (the exact document list, in TOC expansion order) and `_meta.json` (title/version/date/abstract/author/lang/output). The single output is `docs/docsDocxView/build/prd-<version>.docx` (or `build/prd.docx` when the sanitized version is empty), using the `output` path recorded in `_meta.json`. Only manifest-listed documents are included; a document missing from the TOC is never rendered. There is one publication and no alternate view.

## Boundaries

- **User-triggered only.** Never install, generate, or build while editing docs. There is no auto-build, watcher, or CI hook.
- **Bounded writes.** The approved set is: `docs/docsDocxView/` (generated `combined.md`, `_meta.json`, `_manifest.json`, seeded `reference.docx` / `build.sh` / `build.bat`, and `build/` output), the approved render environment directory (e.g. `.venv-docs/`), and any `.gitignore` additions you approved. The publication reads `docs/product`, `docs/current`, `docs/adr`, root `CONTEXT.md`, and `docs/toc.yml`; it never rewrites source documents.
- **User-owned seed files.** `gen_docx.py` seeds `docs/docsDocxView/reference.docx`, `build.sh`, and `build.bat` **only when missing** and never overwrites them; after seeding they are yours to edit. `reference.docx` controls Word styles, header, and footer. The build helpers are build-only: they do not generate or validate content, install or fetch anything, call `gen_docx.py` / `check_docx.py`, look for the skill directory, open a browser/server, or deploy.
- **TOC-controlled range.** Only documents listed in `docs/toc.yml` are published. Paths must resolve under `docs/product`, `docs/current`, `docs/adr`, or be exactly `CONTEXT.md`; symlinks are refused and missing paths fail. There is one publication: no alternate views, covers, or output documents.
- **No TOC or no documents → stop.** Do not create `docs/docsDocxView/`, generate, or build. Report the missing/invalid TOC instead.
- **Generated files are marked.** `combined.md` starts with a generated marker and the JSON files carry `"generated_by"`; generation refuses to overwrite an existing unmarked/unowned output and changes nothing.
- **No invented links or content.** Bodies are never rewritten beyond what the single-document layout requires (heading levels, anchor ids, local-image paths, remote-image placeholders). The TOC supplies the range; `CONTEXT.md` is included at its glossary position with its leading provenance marker stripped.
- **Never fetch remote content.** Remote images become literal `[图片：<alt>]` / `[图片]` placeholders with a warning; pandoc is never allowed to download anything.
- **No browser/server/deploy.** Producing the local `.docx` is the end. Packaging, hosting, and delivery are outside this skill and remain the user's decision.
- **No arbitrary renderer.** `{include}`, `{literalinclude}`, `{raw}`, `{=html}`, `{=openxml}`, and the rST `.. include::` / `.. literalinclude::` / `.. raw::` forms are refused at generation time.

## Flow

Run from the project root (`cwd`). Define the skill directory and, after approval, the prepared environment's **python** path once:

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-docx-view}"
DOCS_PY="$PWD/.venv-docs/bin/python"                 # or the project's existing docs env (needs PyYAML)
```

1. **Inspect (read-only).** Use normal read-only tools (`ls`, `read`, `grep`) to learn the project: whether `docs/toc.yml` exists and lists the required sections, which `docs/product`, `docs/current`, `docs/adr`, and `CONTEXT.md` exist, whether `docs/docsDocxView/` already exists, which Python/venv exists, and the TOC title/version. **Never execute the project's interpreter before approval.** If there is no usable TOC, stop here — there is nothing to publish. Report the plan: pins, environment path, files created (including the three seeded workspace files, only if missing), `.gitignore` additions, output path, and title.

2. **Ask once.** Get explicit approval **before any write or install**. Cover concretely: packages/pins (`requirements.txt`: `pypandoc_binary==1.17`, which bundles pandoc 3.9, and `PyYAML==6.0.2` for TOC parsing; Python >= 3.12), where the environment lives, the pip command, the files created (including `reference.docx`, `build.sh`, `build.bat` when missing), the `.gitignore` additions you propose (e.g. `.venv-docs/`, `docs/docsDocxView/build/`), the output path (`docs/docsDocxView/build/prd-<version>.docx`), and the TOC title/version that will appear on the cover.
   - Within the approved scope, repeated manual builds and regeneration do **not** re-ask.
   - Dependency upgrades, overwriting existing files, or changing the TOC range (new roots, new documents) do require a fresh ask.

3. **Prepare the environment (approved only).** Prefer an existing project docs environment with PyYAML; otherwise a project-root `.venv-docs`. No global/system installs, no automatic `uv`/Python installation. If no suitable Python exists, stop and tell the user. The helper is stdlib-only before PyYAML is installed, so run it with any working Python; then point `DOCS_PY` at the environment it prepared:

   ```bash
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
   python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
   ```

   The helper only creates/reuses a recognized venv (a directory with `pyvenv.cfg`; it refuses to clobber a non-venv), enforces Python >= 3.12, and installs the pinned requirements only when `--install` is passed (after your approval). It never runs on ordinary doc edits, and distributing the skill package installs nothing.

4. **First-time setup (approved, only when `docs/docsDocxView/` does not exist).** There is no separate scaffolding step and no `sphinx-quickstart`: the generator in step 5 creates `docs/docsDocxView/` when missing and seeds `reference.docx`, `build.sh`, and `build.bat` from the skill's `assets/` **only when those files are missing**. If the workspace already exists, nothing is re-seeded or overwritten; to replace a user-owned file, present an explicit manual plan and let the user apply it.

5. **Generate the publication (before every build).** The generator validates `docs/toc.yml`, expands globs and `modules: auto`, and writes the marked publication files under the workspace. It exits non-zero on an invalid/unsafe TOC or output collision, and never runs pandoc:

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/gen_docx.py --project-root .
   ```

   It writes `combined.md` (the single pandoc input), `_manifest.json`, and `_meta.json`, and seeds the three missing workspace files. It prints a one-line summary and any warnings; `--json` prints `{"documents": [...], "output": "...", "generated": [...], "seeded": {...}, "warnings": [...]}` on stdout. It never creates `build/`, never runs pandoc, and never edits `docs/toc.yml` or the source documents; to change the publication, edit the TOC and re-run it. Re-run it after a TOC, `CONTEXT.md`, or module-set change.

6. **Build (repeatable without re-approval).** Use the seeded helper, which runs the same pandoc conversion:

   ```bash
   ( cd docs/docsDocxView && ./build.sh )          # POSIX
   ```
   ```bat
   docs\docsDocxView\build.bat                     :: Windows (from the project root)
   ```

   `build.sh` is POSIX sh and is seeded executable; `build.bat` is Windows batch. Both `cd` to their own directory. They use `DOCS_PY` if set, otherwise `../../.venv-docs/bin/python` (`..\..\.venv-docs\Scripts\python.exe` on Windows). `--clean` deletes `build/` first; it is the only argument (unknown or extra arguments print `usage: ... [--clean]` and exit 2). They require the render environment plus `combined.md`, `_meta.json`, `_manifest.json`, and `reference.docx`; otherwise they print an error telling you to run the docs-docx-view skill first and build nothing. They read the output path from `_meta.json`, resolve the pandoc binary through `pypandoc`, then run exactly:

   ```bash
   "$PANDOC" --from=markdown+raw_attribute --to=docx --reference-doc=reference.docx --resource-path="$(cd ../.. && pwd)" -o "$OUT" combined.md 2> build/pandoc.log
   ```

   They print the pandoc message count (`build/pandoc.log`), the output path, and its size. The document lands at `docs/docsDocxView/build/prd-<version>.docx` (the path recorded in `_meta.json`); `build/` and `build/pandoc.log` are created by `build.sh` only. They do **not** regenerate: if `docs/toc.yml`, `CONTEXT.md`, or the module set changed, run step 5 first. Source-doc edits are legitimate rebuilds. A change to an approved setting (environment, workspace, output path) requires a fresh ask.

7. **Check.**

   ```bash
   "$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
   ```

   `check_docx.py` rebuilds the expected `combined.md` in memory and requires byte equality with the on-disk file, re-checks the manifest/meta consistency and PRD source-link discipline, and then validates the produced `.docx` (zip parts, TOC field, `updateFields`, title, section headings, no provenance text). `--skip-docx` limits it to the source-side checks (useful before the first build); `--docx PATH` points it at a non-default document. Warnings are reported but do not fail it.

8. **Report.** Summarise the generation, pandoc build, and check results — see Statuses below.

## Safety model

The boundary is the generator plus pandoc's fixed input, not a build orchestrator. It is a best-effort guard for **trusted** project docs, not a universal sandbox.

- **Strict TOC validation:** required metadata and section ids, allowed roots (`docs/product`, `docs/current`, `docs/adr`, or exactly `CONTEXT.md`), regular `.md`/`.rst` files, no symlink components, no duplicate documents, missing paths fail. A violation exits 1 and nothing is written.
- **Forbidden constructs fail generation:** `{include}`, `{literalinclude}`, `{raw}`, `{=html}`, `{=openxml}`, `.. include::`, `.. literalinclude::`, and `.. raw::` are scanned in the source text (including code fences and comments) and reported as `file:line`; generation refuses.
- **Remote content is never fetched:** remote images (http/https/protocol-relative/other URL schemes, including reference-style definitions used by images and `<img src=...>`) are replaced with a literal `[图片：<alt>]` placeholder (`[图片]` when there is no alt) and a warning. Absolute and `file:` image targets fail.
- **Local images are checked before use:** each is resolved relative to its source document, must be a regular file whose real path is inside the project root **and** inside `docs/product`, `docs/current`, or `docs/adr`, with no symlink components. The destination is rewritten project-root-relative; a Markdown image also gets `{width=16cm}` when no width/height is given.
- **Provenance markers are stripped in memory:** leading `模板来源` markers (blockquote or HTML-comment form, stacked, before the first heading) are removed from the generated copy; the source files on disk are never modified.
- **Generated files are owned and preflighted:** `combined.md` carries the generated marker, JSON files carry `"generated_by": "docs-docx-view gen_docx.py"`. Existing unmarked/unowned outputs, a symlinked workspace, or an output escaping the workspace make generation refuse before any write.
- **One TOC, no `--toc`:** the cover is pandoc's own title block and the only TOC is the hand-written Word field; pandoc is not asked to build a second one.
- **Build helpers are transparent wrappers:** they contain no parsing, rendering, generation, or validation logic. They only `cd`, require the inputs, run the documented pandoc command, and print the result. They are seeded once, only when missing, and are user-owned.

## Statuses

Read the generator exit code, pandoc exit code and `build/pandoc.log`, and the check result:

- **clean success** — `gen_docx.py` generated, `build.sh` exited 0, `build/pandoc.log` is empty, and `check_docx.py` exits 0.
- **preview with warnings** — the build exited 0 but `build/pandoc.log` has entries (or the generator printed warnings). Report the first messages and the log path. Warnings do not by themselves fail `check_docx.py`.
- **generation refusal** — `gen_docx.py` exits 1 with `refusing: ...` on stderr (missing/invalid `docs/toc.yml`, path outside the allowed roots, duplicate document, symlink, forbidden construct, or an unmarked output collision). Report the message, fix the TOC/source/collision, and do not build stale output.
- **check failure** — `check_docx.py` exits 1 (stale `combined.md`, manifest/meta mismatch, a PRD link violation, a missing/invalid DOCX part, a missing TOC field or section heading, or a provenance leak). Summarise the reported lines; do not present a failing publication as valid.
- **pandoc build failure** — `build.sh` exits non-zero because pandoc failed (or the expected output was not created). The log is `build/pandoc.log`; `build/` may contain stale or partial output. State that clearly and do not present it as a fresh build.
- **precondition failure** — the helper cannot find the render environment, `combined.md`, `_meta.json`, `_manifest.json`, or `reference.docx` (or `pypandoc` is not installed in `DOCS_PY`). It exits non-zero with an instruction to run the docs-docx-view skill first, and nothing is built; fix the precondition (step 3 or 5) before retrying.

## Limitations

- The generated `.docx` is **not opened by Word or LibreOffice** in this skill's verification environment. The TOC field shows its placeholder until Word updates fields (the template sets `w:updateFields`); page layout, fonts, pagination, and table fit need a human check in Word.
- TOC depth is fixed at headings 1–3 (`TOC \o "1-3"`); deeper headings are not listed.
- Headings deeper than H6 are clamped to H6, with a warning; the hierarchy may flatten there.
- Wide tables may overflow the page; pandoc does not shrink columns to fit.
- Mermaid diagrams are not rendered; a Mermaid fence remains a plain code block.
- `.rst` documents are accepted but processed as Markdown (ATX headings only); rST syntax is not converted. `include` / `literalinclude` / `raw` are refused, so this is not an arbitrary-MyST renderer.
- There is no custom theme or per-project design work: one `reference.docx` style set (Calibri/宋体 body, Calibri Light/黑体 headings, A4, header/footer), which you may replace after seeding.
- The glossary is the root `CONTEXT.md` text. Keep it text-only; a relative image would resolve outside the allowed roots and fail, and remote images become placeholders.
- Style fidelity beyond the checked structure (TOC field, headings, title, provenance) is not verified; visual differences are expected and need a Word review.
- The build helpers build only: they do not regenerate, install dependencies, or validate the result. No browser, server, or deployment step exists.

See `references/technical.md` for the exact commands, TOC schema, generated artifacts, heading/anchor mapping, and validation rules.
