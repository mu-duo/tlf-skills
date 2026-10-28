# docs-docx-view technical reference

## Pinned dependencies

Verified on PyPI (2026-10). The set is mutually compatible; the skill's own Python floor is 3.12.

| Package | Pin | Note |
| :--- | :--- | :--- |
| pandoc (bundled) | `pypandoc_binary==1.17` | bundles pandoc 3.9; provides the `pypandoc` module used by `build.sh` / `build.bat` |
| PyYAML | `PyYAML==6.0.2` | `gen_docx.py` / `check_docx.py` read `docs/toc.yml` |

`requirements.txt` ships this declaration. `prepare_env.py` installs nothing unless `--install` is passed; the caller runs it only after approval. Python >= 3.12 is enforced by `prepare_env.py`.

## Layout

```
<project root>/
  .venv-docs/                     # default render venv (or the project's docs env)
  CONTEXT.md                      # glossary source (read, never modified)
  docs/                           # publication source root
    toc.yml                       # publication source of truth
    product/                      # core PRD + module PRD/SPEC
      00-README.md                # PRD cover/overview
      01-requirements.md          # PRD requirements
      02-architecture.md          # PRD architecture + module map
      <NN-module>/
        00-README.md              # module PRD (included by modules: auto)
        00-index.md               # agent sidecar (not listed -> not published)
        01-spec.md 02-interfaces.md 03-nfr.md
        design/                   # not listed by default -> not published
    current/                      # as-built snapshot
    adr/                          # decisions
    docsDocxView/                 # workspace
      combined.md                 # generated single pandoc input (marked)
      _manifest.json              # generated exact document list
      _meta.json                  # generated title/version/date/abstract/author/lang/output
      reference.docx              # seeded Word template (only if missing; user-owned)
      build.sh                    # seeded build helper (POSIX sh; only if missing; user-owned)
      build.bat                   # seeded build helper (Windows batch; only if missing; user-owned)
      build/prd-<version>.docx    # publication (created by build.sh)
      build/pandoc.log            # pandoc stderr (created by build.sh)
```

`docsDocxView` is the workspace directory name, not the publication title. The title comes from `docs/toc.yml`.

## Files shipped by this skill

- `scripts/prepare_env.py` — create/reuse a recognized venv; optional pinned install / freeze. Stdlib only.
- `scripts/gen_docx.py` — validate `docs/toc.yml`, expand globs/`modules: auto`, render heading levels and anchors, rewrite links and local images, blank remote images, write `combined.md` / `_manifest.json` / `_meta.json`, and seed the three workspace files when missing.
- `scripts/check_docx.py` — validate freshness, manifest/meta consistency, PRD source links, and the produced DOCX. Stdlib + PyYAML.
- `scripts/make_reference.py` — maintenance-only generator for `assets/reference.docx` (not part of the publication flow). Stdlib only.
- `assets/reference.docx` — the committed Word style/header/footer template, produced by `make_reference.py`.
- `assets/build.sh` — POSIX sh build helper, seeded into the workspace only when missing.
- `assets/build.bat` — Windows batch build helper, seeded into the workspace only when missing.
- `requirements.txt` — the pins.

## Commands

Inspection is done with normal read-only tools; there is no inspect subcommand and nothing runs the project interpreter before approval. After approval, define the prepared environment's paths from the project root (override `--venv` to reuse a project docs env):

```bash
SKILL="${SKILL:-$HOME/.agents/skills/docs-docx-view}"
DOCS_PY="$PWD/.venv-docs/bin/python"                 # venv python; needs PyYAML
```

First-time setup (there is no separate scaffolding step; the generator creates the workspace and seeds missing files):

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs --install
"$DOCS_PY" "$SKILL"/scripts/gen_docx.py --project-root .
( cd docs/docsDocxView && ./build.sh )
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
```

`gen_docx.py` creates `docs/docsDocxView/` (mkdir -p) and seeds `reference.docx`, `build.sh`, and `build.bat` from `assets/` only when each is missing. There is no `sphinx-quickstart`, `conf.py`, or other scaffold.

One-click rebuild (helpers seeded once, only when missing; never overwritten):

```bash
( cd docs/docsDocxView && ./build.sh )            # POSIX sh; seeded executable
( cd docs/docsDocxView && ./build.sh --clean )    # delete build/ first
( cd docs/docsDocxView && DOCS_PY=/path/to/.venv-docs/bin/python ./build.sh )
```
```bat
docs\docsDocxView\build.bat                       :: Windows (from the project root)
docs\docsDocxView\build.bat --clean
```

Both helpers `cd` to `docs/docsDocxView` and use `DOCS_PY` if set, otherwise `../../.venv-docs/bin/python` (`..\..\.venv-docs\Scripts\python.exe` on Windows). Before building they require an executable render environment plus `combined.md`, `_meta.json`, `_manifest.json`, and `reference.docx`; otherwise they print an error to run the docs-docx-view skill first and exit non-zero without building. `--clean` is the only option; unknown or extra arguments print `usage: ... [--clean]` and exit 2. They read the output path from `_meta.json`, resolve pandoc through `pypandoc`, create `build/`, and run exactly:

```bash
"$PANDOC" --from=markdown+raw_attribute --to=docx --reference-doc=reference.docx --resource-path="$(cd ../.. && pwd)" -o "$OUT" combined.md 2> build/pandoc.log
```

They print the pandoc message count, the output path, and the output size, and exit with pandoc's status. The helpers build only: they never generate content, run `gen_docx.py` / `check_docx.py`, install packages, look for the skill directory, or open a browser/server. Re-run `gen_docx.py` first after changing `docs/toc.yml`, `CONTEXT.md`, or the module set.

Repeat build (same approved scope; re-run the generator after every TOC change):

```bash
"$DOCS_PY" "$SKILL"/scripts/gen_docx.py --project-root .
( cd docs/docsDocxView && ./build.sh )
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
```

Check, including source-only mode:

```bash
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root .
"$DOCS_PY" "$SKILL"/scripts/check_docx.py --project-root . --skip-docx
```

The skill stops at the local `docs/docsDocxView/build/` folder; packaging, hosting, and delivery are outside its scope and remain the user's decision.

Optional resolved-version snapshot (approved output):

```bash
python3 "$SKILL"/scripts/prepare_env.py --project-root . --venv .venv-docs \
    --freeze docs/docsDocxView/requirements.lock.txt
```

Maintenance-only template regeneration (not run during publication):

```bash
python3 "$SKILL"/scripts/make_reference.py
python3 "$SKILL"/scripts/make_reference.py --pandoc /path/to/pandoc --output /tmp/reference.docx
```

`prepare_env.py` flags: `--project-root` (default cwd), `--venv` (default `.venv-docs`, relative to project root unless absolute), `--base-python` (interpreter used to create the venv), `--requirements`, `--install`, `--freeze PATH`. It refuses to reuse a path that exists without `pyvenv.cfg`, refuses Python < 3.12, and refuses `--install`/`--freeze` unless the interpreter actually belongs to the target venv. It never installs Python/uv and never uses global/system pip.

`gen_docx.py` flags: `--project-root` (default cwd), `--json`. Exit 0 = generated; exit 1 = refused, with `refusing: <reason>` on stderr, and nothing written.

`check_docx.py` flags: `--project-root` (default cwd), `--docx PATH` (default the workspace-relative `output` from `_meta.json`; an explicit relative path is resolved against the project root), `--skip-docx` (source checks only). Exit 0 = no failures, 1 = violations or missing inputs; warnings do not fail.

`make_reference.py` flags: `--pandoc PATH` (default `pypandoc.get_pandoc_path()`, then `pandoc` on `PATH`), `--output PATH` (default `<skill>/assets/reference.docx`). Exit 1 when no usable pandoc is found, with an instruction to install `pypandoc_binary==1.17` and pass `--pandoc`.

`gen_docx.py --json` prints `{"documents": [...], "output": "...", "generated": [...], "seeded": {...}, "warnings": [...]}` on stdout. `documents` are project-root-relative; `generated` are workspace-relative with the `docs/docsDocxView/` prefix; `seeded` maps each seeded file to `created` / `exists` / `skipped` / `missing-asset` / `failed`.

## TOC schema (`docs/toc.yml`)

```yaml
title: <publication title>
version: <version>
date: <date>
abstract: <one paragraph>
# author: <optional; omitted from the cover when empty>

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

Rules enforced by `gen_docx.py` and repeated by `check_docx.py`:

- The TOC is a mapping with non-empty `title`, `version`, `date`, `abstract`, and a non-empty `sections` list. `author` is optional and omitted from the cover metadata when empty.
- Top-level section ids must include `overview`, `requirements`, `architecture`, `appendix`. The `appendix` children must include `glossary`, `spec`, `current`, `adr`. Extra sections are allowed.
- A section needs a non-empty `title` and at least one of `documents`, `sections`, or `modules: auto`. Ids must be unique and safe directory names (`[A-Za-z0-9._-]`, no separators).
- `documents` entries are paths or globs relative to the project root. They must resolve under `docs/product`, `docs/current`, or `docs/adr`, or be exactly `CONTEXT.md`. Globs support `*` and `**`; matches are sorted, and implicit/glob duplicates are de-duplicated. Explicitly listing the same document twice (or in two sections) is an error.
- `modules: auto` expands `docs/product/*/00-README.md` (module PRDs), sorted by numeric prefix then case-insensitive name. `exclude` accepts a module directory name (`08-internal`), a project-relative path (`docs/product/08-internal`), or a document path.
- `exclude` is valid only together with `modules: auto`. Unknown keys are rejected at section level; unknown top-level keys produce a warning.
- `design/` is not published by default: the default SPEC globs do not reach it, and unlisted files never enter the manifest.
- `CONTEXT.md` is included at the glossary position; it is required only when the TOC lists it. There is no generated glossary file.
- Document paths must be regular `.md`/`.rst` files with no symlink components. Missing paths fail the TOC (not silently skipped).
- Section titles become headings in the document; the TOC order is the document order.
- The document language is fixed to `zh-CN` in the cover metadata.

To change the publication, edit `docs/toc.yml` — never the generated files — then re-run `gen_docx.py` before building.

## Generated artifacts

`combined.md` is marked and overwritten; `_manifest.json` / `_meta.json` carry `"generated_by": "docs-docx-view gen_docx.py"` and are overwritten. The seeded `reference.docx`, `build.sh`, and `build.bat` are unmarked, user-owned, and never overwritten.

### `docsDocxView/combined.md` (the single pandoc input)

````markdown
---
# docs-docx-view: generated document; do not edit
title: "<toc title>"
subtitle: "版本 <version> · <date>"
author: "<toc author>"
---
<!-- docs-docx-view: cover -->
::: {custom-style="Abstract"}
<toc abstract>
:::
```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```
::: {custom-style="TOC Heading"}
目录
:::
```{=openxml}
<w:p><w:fldSimple w:instr="TOC \o &quot;1-3&quot; \h \z \u" w:dirty="true"><w:r><w:t>Update field to build the table of contents</w:t></w:r></w:fldSimple></w:p>
```
```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```
<!-- docs-docx-view: doc docs/product/00-README.md -->
# <section title> {#sec-1-1}
...document body...
````

- The first line is `---` and the second is the marker, so `is_marked` recognizes the file. Generation refuses to overwrite an existing `combined.md` without it.
- YAML scalars are emitted with `json.dumps(value, ensure_ascii=False)`, so the title and version line are always valid quoted scalars. The `author` line is omitted entirely when the TOC author is empty.
- The cover title is pandoc's own title block using the `Title` / `Subtitle` / `Author` styles from `reference.docx`; the abstract follows it as a body paragraph in the `Abstract` custom style. Do not pass `--toc`: the hand-written field is the only TOC, and title/date/abstract are not passed on the command line.
- `combined.md` deliberately has no `lang:` metadata key. With `lang: zh-CN`, pandoc 3.9 looks for `translations/zh.yaml` (not shipped) and logs four warnings on every build; without the key it prints an English `Abstract` label. CJK proofing comes from `reference.docx` docDefaults (`w:lang w:val="en-US" w:eastAsia="zh-CN"`), and `_meta.json` records `"lang": "zh-CN"` for the record.
- The `目录` paragraph uses the `TOC Heading` custom style; the TOC field is depth 1–3, hyperlinked, and marked dirty. Word fills it when fields update; `w:updateFields` in `reference.docx` asks Word to update on open.
- The two `{=openxml}` blocks insert page breaks after the cover and after the TOC field.
- Before the first document of each section, the section title is injected as a heading (`#` at section level, or `##` for appendix children) with an explicit `{#sec-<section ordinal>-1}` id; its text is sanitized (no `<`, `>`, backticks, braces, brackets, pipes, or newlines).
- Before every document there is a marker comment `<!-- docs-docx-view: doc <project-root-relative path> -->`. The section heading is emitted once, before that section's first document.
- A page break precedes every top-level Heading 1 except the first, because the TOC block already ends with a page break.
- Document bodies follow the heading/anchor/image/link rules below; source files are not modified.

### `docsDocxView/_meta.json`

```json
{
  "generated_by": "docs-docx-view gen_docx.py",
  "title": "...",
  "version": "...",
  "date": "...",
  "abstract": "...",
  "author": "",
  "lang": "zh-CN",
  "output": "build/prd-v1.0.docx"
}
```

`output` is workspace-relative and is the only path `build.sh` / `check_docx.py` use by default. The file name is `build/prd-<version>.docx`, where the version has runs of characters outside `[A-Za-z0-9._-]` replaced by `-` and leading/trailing `.-_` stripped; an empty result yields `build/prd.docx`.

### `docsDocxView/_manifest.json`

```json
{
  "generated_by": "docs-docx-view gen_docx.py",
  "documents": ["docs/product/00-README.md", "docs/product/01-requirements.md", "..."]
}
```

Paths are project-root-relative POSIX paths in exact TOC expansion order, including `CONTEXT.md` at the glossary position. There is no generated glossary file or extra synthetic document.

### Seeded workspace files

`gen_docx.py` seeds `reference.docx`, `build.sh`, and `build.bat` from `assets/` **only when missing** and never overwrites an existing file. `build.sh` is seeded executable (`0o755`) on POSIX; `build.bat` gets CRLF line endings. A symlink or non-regular existing file is left untouched with a warning. `--json` reports each as `created` / `exists` / `skipped` / `missing-asset` / `failed`.

### `docsDocxView/build/`

Created by `build.sh` only (never by `gen_docx.py`). It contains the output `.docx` and `pandoc.log`. `--clean` removes the directory first. `build/` may contain stale or partial output after a failed pandoc run.

### Provenance stripping (generated copy only)

Leading `模板来源` (template-origin) markers are removed before rendering: a blockquote line starting with `模板来源` (plus its immediately following contiguous blockquote lines) or an `<!-- 模板来源 ... -->` HTML comment. A leading BOM and blank lines are allowed; the marker must sit before the first heading; stacked leading markers are stripped one after another. Occurrences later in the body are never touched, and the source files on disk are never modified.

## Heading and anchor mapping

Headings are remapped per document, relative to the enclosing TOC section level (top-level sections are level 1, appendix children level 2):

| Situation | Result |
| :--- | :--- |
| Top-level section heading | Heading 1, `{#sec-<section ordinal>-1}` |
| Appendix child section heading | Heading 2, `{#sec-<section ordinal>-1}` |
| First ATX H1 differs from the section title | kept; Heading = section level + 1; internal source Hn (n >= 2) -> section level + n |
| First ATX H1 equals the section title | dropped; internal source Hn (n >= 2) -> section level + (n - 1) |
| `CONTEXT.md` leading H1 | always dropped; internal source H2 -> section level + 1 |
| First heading is not H1 | nothing injected; source Hn (n >= 1) -> section level + n; warning names the document |
| Heading deeper than H6 | emitted as H6; warning |
| Setext or indented heading | treated as plain text; warning |
| Section resolving to no documents and no child sections | omitted; warning |

- The section title comparison uses the sanitized title (and the raw trimmed title); the document title is dropped only when it matches.
- The title of a kept first H1 is a normal heading; a dropped title is replaced by the section heading, so no level gap remains.
- Every emitted section heading and document heading gets an explicit `{#id}`. Ids are `sec-<section ordinal>-<heading ordinal>`, with ASCII document-order counters: the section heading is 1, and emitted headings continue 2, 3, ... across **all documents in that section**.
- A page break precedes every top-level section heading except the first.
- ATX headings are rewritten in place; any existing trailing `{#...}` / `{.class}` attribute block is stripped before the generated id is appended.

Link and anchor lookup, per document:

| Source | Resolution |
| :--- | :--- |
| Exact heading text | that heading's id |
| GFM-style slug (lowercase, spaces to `-`, punctuation dropped, CJK kept) | that heading's id; duplicate slugs get `-1`, `-2` suffixes per document |
| Percent-decoded variants | the same id |
| `[text](#anchor)` | rewritten to `#<id>` when resolved |
| `[text](relative/path.md#anchor)` resolving to a manifest document | rewritten to the target heading's `#<id>` |
| `[text](relative/path.md)` with no fragment | `#<title id>` when the document title was kept, otherwise `#<section id>` |
| `http:`, `https:`, `mailto:`, or any target outside the manifest | left untouched |
| Unresolved target ending in `.md` or containing a fragment | warning `file:line -> target`; generation continues |

Relative paths resolve against the source document's directory. Link text is preserved. The fragment is not rewritten when the target is external or outside the publication. A dropped document title still has an anchor entry, but it points at the section heading's id.

## Images, links, and safety

- **Remote images are never fetched.** `http://`, `https://`, protocol-relative (`//`), and other URL-scheme targets — inline images, `<img src=...>` tags, and reference definitions used by reference-style images — are replaced with the literal text `[图片：<alt>]` (`[图片]` when there is no alt) and a warning. The reference definition line is blanked.
- **Local images are validated and re-rooted.** A destination is resolved relative to the source document; it must be an existing regular file whose real path is inside the project root **and** inside `docs/product`, `docs/current`, or `docs/adr`, with no symlink component. It is rewritten to a project-root-relative POSIX path and, for Markdown images, wrapped in angle brackets when it contains spaces and given `{width=16cm}` when no `width`/`height` attribute is present. An existing Markdown attribute block is preserved.
- **Absolute and `file:` image targets fail** generation, as do local images escaping the roots or using symlinks.
- **Forbidden constructs fail generation** with `file:line`: MyST/Sphinx `{include}`, `{literalinclude}`, `{raw}`; raw blocks `{=html}`, `{=openxml}`; rST `.. include::`, `.. literalinclude::`, `.. raw::`. The scan runs on the source text before code/comment masking, so a construct inside a fence or comment also refuses.
- **Links are rewritten only inside the publication.** External schemes and targets outside the manifest stay as written; unresolved internal-looking targets warn but do not fail.
- **Preflight is transactional.** The plan, rendered documents, and expected outputs are computed before the workspace is touched. Existing outputs must be marked Markdown or owned JSON (`generated_by`); a symlinked workspace, an output escaping it, or an unmarked collision refuses with exit 1 and changes nothing. Writes use temp files and atomic replace.
- **Nothing is fetched by the build.** `build.sh` runs pandoc with `--resource-path` set to the project root so already-rewritten local images resolve; remote images were replaced before pandoc ran.

## `reference.docx` and `make_reference.py`

`assets/reference.docx` is derived from pandoc 3.9's default reference document and committed as a binary. It provides:

- `word/styles.xml`: docDefaults with Calibri / eastAsia 宋体; Heading 1–4 in Calibri Light / 黑体 with dark colours and outline levels; `Title` / `Subtitle` / `Author` / `Abstract` styles for the cover; `TOC Heading` at body outline level 9 (so it does not appear in the TOC); `Body Text` / `First Paragraph` spacing; a `Table` style with header shading and banding; `Source Code` / `Verbatim Char` monospace; `Hyperlink`, `Header`, and `Footer` styles.
- `word/settings.xml`: `<w:updateFields w:val="true"/>`, so Word refreshes the TOC and page fields.
- `word/header1.xml`: right-aligned `DOCPROPERTY "title"` field marked dirty, with a bottom border.
- `word/footer1.xml`: centered `第 PAGE 页 / 共 NUMPAGES 页` field runs.
- A single A4 section (`w:pgSz w:w="11906" w:h="16838"`) with 2.54 cm margins, referencing the header/footer relationships; matching `[Content_Types].xml` overrides.

`make_reference.py` is maintenance only and is not run during publication. It reads `pandoc --print-default-data-file reference.docx`, applies these edits while keeping every other part, repacks deterministically (fixed entry order, fixed 1980-01-01 timestamps), then verifies the result: every `.xml`/`.rels` part parses, all required style ids exist, header/footer/settings parts and relationships are present, and a fixture (H1–H4, table, code, CJK, local image) converts through the new template and re-reads as Markdown. On failure the temporary output is removed and the command exits non-zero. It does not touch the workspace or any publication.

## Validation (`check_docx.py`)

1. **Source and freshness.** Rebuild the plan and the expected `combined.md` in memory and require byte equality with the on-disk file. Missing/different means stale: fail with the instruction to re-run `gen_docx.py`. Also require `_manifest.json` documents to equal the plan order, and `_meta.json` to carry the expected `generated_by`, `output`, `title`, `version`, and `lang`. This subsumes glossary freshness, provenance stripping, remote-image blanking, heading/anchor rewriting, and document-marker order.
2. **PRD source discipline.** The same rules as docs-html-view: mask fenced code, inline code, and HTML comments; for `docs/product/00-README.md`, `01-requirements.md`, `02-architecture.md`, and `docs/product/*/00-README.md`, allow only same-page anchors and relative links to PRD-layer documents; flag external URLs, absolute paths, links outside the PRD layer, and status markers `✅` / `🚧` / `❌`. Missing `docs/product` or a core chapter is also a violation.
3. **DOCX (skipped with `--skip-docx`).** The path defaults to the workspace-relative `output` in `_meta.json`; `--docx PATH` overrides it (a relative override resolves against the project root). Require the file to exist and be a valid zip; `word/document.xml`, `word/settings.xml`, and `docProps/core.xml` to parse; `word/document.xml` to contain a `TOC` field instruction (`TOC \o "1-3"`); settings to contain an enabled `w:updateFields`; core properties `dc:title` to equal the TOC title; the expected section headings (top-level H1 + appendix child H2, sanitized titles) to appear in order, with every expected top-level H1 exactly once; and no `模板来源` in the XML parts.
4. **Report.** Counts for TOC documents, manifest entries, PRD links checked, expected headings, DOCX checks, and violations, with `file:line` for source violations. Exit 0 only when there are no failures; warnings do not fail. `check_docx.py` does not validate the user-owned build helpers or visual style fidelity.

## Approval and consent

The skill asks once, before any write/install/generate, covering packages, environment, files, `.gitignore` additions, output path, and the TOC title/version. There is no stored consent state or fingerprint. Repeated builds/regenerations inside the approved scope do not re-ask; dependency upgrades, overwriting existing files, or changing the TOC range require a fresh ask. The seeded `reference.docx`, `build.sh`, and `build.bat` are part of the created-files list and are seeded only when missing; existing files are never overwritten. Missing TOC/source docs → report and stop, never guess. The build is local-only: no network fetch, no installer at build time, no deployment.

## Limitations

- No Word or LibreOffice runs in the verification environment. The TOC field is filled when Word updates fields (`w:updateFields` is set); layout, fonts, pagination, and table fit require a human Word review.
- TOC depth is fixed at headings 1–3.
- Headings deeper than H6 are clamped to H6; the hierarchy may flatten there.
- Wide tables may overflow the page.
- Mermaid diagrams are not rendered; they remain plain code blocks.
- `.rst` is accepted but processed as Markdown (ATX headings only); rST syntax is not converted.
- `include` / `literalinclude` / `raw` are refused; this is not an arbitrary-MyST renderer.
- No custom theme; one `reference.docx` style set applies to every project. Replacing it is user-owned work, and style fidelity is not checked.
- The glossary is `CONTEXT.md` text. A relative image there resolves outside the allowed roots and fails; remote images become placeholders, so keep it text-only.
- The build helpers build only; they do not regenerate, install dependencies, validate, or normalize a failed `build/`. There is no browser, server, or deployment step.
