#!/usr/bin/env python3
"""Validate the docs-docx-view Word publication. Stdlib + PyYAML only.

Checks, in order:

1. **Source / freshness.** Rebuilds the publication plan and the expected
   ``docs/docsDocxView/combined.md`` in memory with ``gen_docx.build_plan`` +
   ``build_documents`` + ``render_combined`` and requires byte equality with the
   on-disk file. ``_manifest.json`` must list exactly the plan documents in
   plan order, and ``_meta.json`` must belong to this generator with a
   consistent output path and title.
2. **PRD source discipline.** Same rules as docs-html-view ``check_prd.py``:
   for ``docs/product/00-README.md``, ``01-requirements.md``,
   ``02-architecture.md`` and ``docs/product/*/00-README.md`` only same-page
   anchors and relative links to other PRD-layer documents are allowed.
   External URLs, absolute paths, out-of-layer links, and status markers
   (``✅/🚧/❌``) are violations. HTML comments, fenced code, and inline code are
   masked.
3. **DOCX.** The built document must exist, be a valid zip, contain parseable
   ``word/document.xml`` and ``word/settings.xml``, carry the hand-written TOC
   field (``TOC \\o "1-3"``), enable ``w:updateFields``, have a ``dc:title``
   equal to the TOC title, contain the expected section headings in document
   order with every top-level heading exactly once, and contain no
   ``模板来源`` provenance text in any ``w:t``.

Exit codes: 0 = clean (warnings allowed), 1 = violations or unusable inputs.
No files are written; pass ``--skip-docx`` to validate only sources.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True  # never leave __pycache__ in the installed skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_docx  # noqa: E402  (ships next to this script)

PRD_ALLOWED_BASENAMES = {"00-README.md", "01-requirements.md", "02-architecture.md"}
STATUS_MARKERS = ("✅", "🚧", "❌")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`{1,3}[^`\n]*`{1,3}")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HTML_COMMENT = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)
BARE_URL = re.compile(r"(?:https?|ftp)://[^\s)>\]]+")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % W_NS
DC = "{http://purl.org/dc/elements/1.1/}"
TOC_INSTR = re.compile(r'TOC\s+\\o\s+["\']?1-3["\']?')
HEADING_STYLE = re.compile(r"^heading\s*([1-9])$", re.IGNORECASE)
PROVENANCE = "模板来源"


def mask_code(text: str) -> str:
    """Blank out fenced code blocks and inline code spans, keeping offsets."""
    masked_lines = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE.match(line):
            in_fence = not in_fence
            masked_lines.append(re.sub(r"[^\n]", " ", line))
        elif in_fence:
            masked_lines.append(re.sub(r"[^\n]", " ", line))
        else:
            masked_lines.append(line)
    return INLINE_CODE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), "".join(masked_lines))


def mask_comments(text: str) -> str:
    return HTML_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def parse_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            return target[1:end]
    return target.split()[0] if target else ""


def display(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def workspace_dir(root: str) -> str:
    return os.path.join(root, *gen_docx.WORKSPACE.split("/"))


# --------------------------------------------------------------------------- #
# Phase 1: source / freshness
# --------------------------------------------------------------------------- #


def rebuild_expected(root: str, failures: list, warnings: list):
    """Rebuild plan + combined.md in memory, capturing generator warnings."""
    saved_warn = gen_docx.warn
    saved_warnings = gen_docx.WARNINGS
    gen_docx.WARNINGS = []

    def collect(message: str) -> None:
        gen_docx.WARNINGS.append(message)
        warnings.append(message)

    gen_docx.warn = collect
    try:
        plan = gen_docx.build_plan(root)
        documents = gen_docx.build_documents(root, plan)
        combined = gen_docx.render_combined(plan, documents, root)
        return plan, combined
    except gen_docx.TocError as exc:
        failures.append("toc: %s" % exc)
        return None, None
    finally:
        gen_docx.warn = saved_warn
        gen_docx.WARNINGS = saved_warnings


def first_difference_line(expected: str, actual: str) -> int:
    expected_lines = expected.splitlines(keepends=True)
    actual_lines = actual.splitlines(keepends=True)
    for index, (left, right) in enumerate(zip(expected_lines, actual_lines), 1):
        if left != right:
            return index
    return min(len(expected_lines), len(actual_lines)) + 1


def check_combined(root: str, expected_combined: str, failures: list) -> str:
    rel = gen_docx.WORKSPACE + "/" + gen_docx.COMBINED_NAME
    path = os.path.join(workspace_dir(root), gen_docx.COMBINED_NAME)
    if os.path.islink(path) or not os.path.isfile(path):
        failures.append("source: missing %s (run gen_docx.py)" % rel)
        return "missing"
    try:
        with open(path, "rb") as fh:
            actual_bytes = fh.read()
    except OSError as exc:
        failures.append("source: cannot read %s: %s" % (rel, exc))
        return "unreadable"

    expected_bytes = expected_combined.encode("utf-8")
    if actual_bytes == expected_bytes:
        return "fresh"

    detail = ""
    try:
        expected_text = expected_combined
        actual_text = actual_bytes.decode("utf-8")
        detail = "; first difference at line %d" % first_difference_line(
            expected_text, actual_text
        )
    except UnicodeDecodeError:
        detail = "; file is not valid UTF-8"
    failures.append(
        "source: %s is stale%s; re-run gen_docx.py" % (rel, detail)
    )
    return "STALE"


def check_manifest(root: str, plan: dict, failures: list) -> int:
    rel = gen_docx.WORKSPACE + "/" + gen_docx.MANIFEST_NAME
    path = os.path.join(workspace_dir(root), gen_docx.MANIFEST_NAME)
    if os.path.islink(path) or not os.path.isfile(path):
        failures.append("manifest: missing %s (run gen_docx.py)" % rel)
        return 0
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        failures.append("manifest: cannot parse %s: %s" % (rel, exc))
        return 0

    documents = data.get("documents") if isinstance(data, dict) else None
    if not isinstance(documents, list) or not all(
        isinstance(item, str) for item in documents
    ):
        failures.append("manifest: documents must be a list of strings")
        return 0

    expected = plan["documents"]
    if documents != expected:
        missing = [item for item in expected if item not in documents]
        extra = [item for item in documents if item not in expected]
        for item in missing:
            failures.append("manifest: missing document: %s" % item)
        for item in extra:
            failures.append("manifest: unexpected document (not in toc.yml): %s" % item)
        if len(documents) != len(set(documents)):
            failures.append("manifest: duplicate entries")
        if not missing and not extra:
            mismatch = next(
                index
                for index, (left, right) in enumerate(zip(documents, expected))
                if left != right
            )
            failures.append(
                "manifest: document order does not match docs/toc.yml "
                "(first mismatch at entry %d)" % (mismatch + 1)
            )
    return len(documents)


def check_meta(root: str, plan: dict, failures: list):
    rel = gen_docx.WORKSPACE + "/" + gen_docx.META_NAME
    path = os.path.join(workspace_dir(root), gen_docx.META_NAME)
    if os.path.islink(path) or not os.path.isfile(path):
        failures.append("meta: missing %s (run gen_docx.py)" % rel)
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        failures.append("meta: cannot parse %s: %s" % (rel, exc))
        return None
    if not isinstance(data, dict):
        failures.append("meta: %s must contain a JSON object" % rel)
        return None

    expected_output = gen_docx.output_path(plan["meta"]["version"])
    if data.get("generated_by") != gen_docx.GENERATED_BY:
        failures.append(
            "meta: generated_by is %r; expected %r"
            % (data.get("generated_by"), gen_docx.GENERATED_BY)
        )
    if data.get("output") != expected_output:
        failures.append(
            "meta: output is %r; expected %r from docs/toc.yml version"
            % (data.get("output"), expected_output)
        )
    for key, expected in (
        ("title", plan["meta"]["title"]),
        ("version", plan["meta"]["version"]),
        ("lang", "zh-CN"),
    ):
        if data.get(key) != expected:
            failures.append(
                "meta: %s is %r; expected %r (re-run gen_docx.py)"
                % (key, data.get(key), expected)
            )
    return data


# --------------------------------------------------------------------------- #
# Phase 2: PRD source links
# --------------------------------------------------------------------------- #


def prd_sources(root: str, failures: list) -> list:
    product = os.path.join(root, "docs", "product")
    if not os.path.isdir(product) or os.path.islink(product):
        failures.append("prd: no docs/product/ directory at " + root)
        return []
    sources = []
    for name in ("00-README.md", "01-requirements.md", "02-architecture.md"):
        path = os.path.join(product, name)
        if os.path.islink(path) or not os.path.isfile(path):
            failures.append("prd: missing core document docs/product/%s" % name)
        else:
            sources.append(path)
    for path in sorted(glob.glob(os.path.join(product, "*", "00-README.md"))):
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        sources.append(path)
    return sources


def link_violation(root: str, source: str, target: str):
    """Return a reason string when a PRD link is not allowed."""
    if not target:
        return "empty target"
    if target.startswith("#"):
        return None
    parsed = urlparse(target)
    if parsed.scheme or target.startswith("//"):
        return "external link"
    if target.startswith(("/", "~")) or re.match(r"^[A-Za-z]:[\\/]", target):
        return "absolute path"
    path_part = target.split("#", 1)[0].split("?", 1)[0]
    if not path_part:
        return None
    if "\\" in path_part:
        return "non-portable path"
    resolved = os.path.normpath(
        os.path.join(os.path.dirname(source), path_part.replace("/", os.sep))
    )
    product_real = os.path.realpath(os.path.join(root, "docs", "product"))
    resolved_real = os.path.realpath(resolved)
    try:
        inside = os.path.commonpath([resolved_real, product_real]) == product_real
    except ValueError:
        inside = False
    if not inside:
        return "outside the PRD layer"
    name = os.path.basename(resolved)
    if name not in PRD_ALLOWED_BASENAMES:
        return "not a PRD-layer document (%s)" % (name or "?")
    if os.path.islink(resolved) or not os.path.isfile(resolved):
        return "missing PRD target"
    return None


def check_prd_links(root: str, failures: list) -> tuple:
    sources = prd_sources(root, failures)
    links = 0
    status = 0
    seen = set()
    for source in sources:
        rel_source = display(source, root)
        try:
            with open(source, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            failures.append("prd: %s: cannot read: %s" % (rel_source, exc))
            continue
        masked = mask_comments(mask_code(text))

        for match in LINK.finditer(masked):
            target = parse_target(match.group(3))
            line = line_number(masked, match.start())
            links += 1
            reason = link_violation(root, source, target)
            if reason:
                key = (rel_source, line, target, reason)
                if key not in seen:
                    seen.add(key)
                    failures.append(
                        "prd: %s:%d: %s (%s)"
                        % (rel_source, line, target or "(empty target)", reason)
                    )

        for index, line_text in enumerate(masked.splitlines()):
            match = REF_DEF.match(line_text)
            if not match:
                continue
            target = parse_target(match.group(1))
            if not target or target.startswith("#"):
                continue
            links += 1
            reason = link_violation(root, source, target)
            if reason:
                failures.append("prd: %s:%d: %s (%s)" % (rel_source, index + 1, target, reason))

        for match in BARE_URL.finditer(masked):
            key = (rel_source, line_number(masked, match.start()), match.group(0), "external link")
            if key not in seen:
                seen.add(key)
                failures.append(
                    "prd: %s:%d: %s (external link)" % (rel_source, key[1], match.group(0))
                )

        for index, line_text in enumerate(masked.splitlines()):
            for marker in STATUS_MARKERS:
                if marker in line_text:
                    status += 1
                    failures.append(
                        "prd: %s:%d: status marker %s" % (rel_source, index + 1, marker)
                    )
    return links, len(sources), status


# --------------------------------------------------------------------------- #
# Phase 3: DOCX
# --------------------------------------------------------------------------- #


def expected_headings(plan: dict) -> list:
    """Section headings in document order: top-level H1 + appendix child H2."""
    headings: list = []

    def walk(section: dict) -> None:
        if not gen_docx.section_has_content(section):
            return
        if section["level"] <= 2:
            headings.append((section["level"], gen_docx.sanitize(section["title"])))
        for child in section["children"]:
            walk(child)

    for section in plan["sections"]:
        walk(section)
    return headings


def extract_headings(document_root) -> list:
    headings = []
    for paragraph in document_root.iter(W + "p"):
        ppr = paragraph.find(W + "pPr")
        if ppr is None:
            continue
        level = None
        style = ppr.find(W + "pStyle")
        if style is not None:
            match = HEADING_STYLE.match(style.get(W + "val", ""))
            if match:
                level = int(match.group(1))
        if level is None:
            outline = ppr.find(W + "outlineLvl")
            if outline is not None:
                try:
                    level = int(outline.get(W + "val", "")) + 1
                except ValueError:
                    level = None
        if level is None:
            continue
        text = normalize_text(
            "".join(node.text or "" for node in paragraph.iter(W + "t"))
        )
        if text:
            headings.append((level, text))
    return headings


def parse_part(archive: zipfile.ZipFile, name: str, failures: list):
    try:
        data = archive.read(name)
    except KeyError:
        failures.append("docx: missing %s" % name)
        return None
    except (OSError, zipfile.BadZipFile) as exc:
        failures.append("docx: cannot read %s: %s" % (name, exc))
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        failures.append("docx: %s: XML parse error: %s" % (name, exc))
        return None


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def check_docx(root: str, docx_path: str, plan: dict, failures: list) -> int:
    rel = display(docx_path, root)
    checks = 0

    if os.path.islink(docx_path) or not os.path.isfile(docx_path):
        failures.append("docx: missing %s (run assets/build.sh)" % rel)
        return checks
    checks += 1

    if not zipfile.is_zipfile(docx_path):
        failures.append("docx: %s is not a valid zip archive" % rel)
        return checks
    checks += 1

    try:
        archive = zipfile.ZipFile(docx_path)
    except (OSError, zipfile.BadZipFile) as exc:
        failures.append("docx: cannot open %s as a zip archive: %s" % (rel, exc))
        return checks

    with archive:
        document_root = parse_part(archive, "word/document.xml", failures)
        settings_root = parse_part(archive, "word/settings.xml", failures)
        core_root = parse_part(archive, "docProps/core.xml", failures)
        if document_root is not None:
            checks += 1
        if settings_root is not None:
            checks += 1
        if core_root is not None:
            checks += 1

        if document_root is not None:
            instructions = []
            for element in document_root.iter():
                # ``w:fldSimple`` carries the instruction in a ``w:instr``
                # attribute; complex fields use ``w:instrText`` elements.
                for attr_name, value in element.attrib.items():
                    if local_name(attr_name) == "instr" and value:
                        instructions.append(value)
                name = local_name(element.tag)
                if name == "instrText" and element.text:
                    instructions.append(element.text)
            if any(TOC_INSTR.search(normalize_text(value)) for value in instructions if value):
                checks += 1
            else:
                failures.append(
                    'docx: word/document.xml has no TOC field instruction (TOC \\o "1-3")'
                )

            expected = expected_headings(plan)
            actual = extract_headings(document_root)
            position = 0
            for level, text in expected:
                match_index = None
                for index in range(position, len(actual)):
                    if actual[index] == (level, text):
                        match_index = index
                        break
                if match_index is None:
                    earlier = [
                        found_level
                        for found_level, found_text in actual[:position]
                        if found_text == text and found_level == level
                    ]
                    levels = [
                        found_level for found_level, found_text in actual if found_text == text
                    ]
                    if earlier:
                        failures.append(
                            "docx: heading out of order: H%d %r appears before an "
                            "expected preceding heading" % (level, text)
                        )
                    elif levels:
                        failures.append(
                            "docx: heading level mismatch for %r: expected H%d, found H%d"
                            % (text, level, levels[0])
                        )
                    else:
                        failures.append("docx: missing heading: H%d %r" % (level, text))
                else:
                    position = match_index + 1
                checks += 1

            for level, text in expected:
                if level != 1:
                    continue
                count = sum(1 for found_level, found_text in actual if found_level == 1 and found_text == text)
                if count > 1:
                    failures.append(
                        "docx: top-level heading %r appears %d times (expected exactly once)"
                        % (text, count)
                    )
                checks += 1

            leaked = False
            for name in sorted(archive.namelist()):
                if not name.endswith((".xml", ".rels")):
                    continue
                try:
                    part_root = ET.fromstring(archive.read(name))
                except (ET.ParseError, KeyError, OSError):
                    continue
                text = "".join(
                    node.text or ""
                    for node in part_root.iter()
                    if local_name(node.tag) == "t"
                )
                if PROVENANCE in text:
                    failures.append(
                        "docx: template-origin text leaked into %s" % name
                    )
                    leaked = True
            if not leaked:
                checks += 1

        if settings_root is not None:
            update_fields = None
            for element in settings_root.iter():
                if local_name(element.tag) == "updateFields":
                    update_fields = element
                    break
            if update_fields is None:
                failures.append("docx: word/settings.xml lacks w:updateFields")
            else:
                value = (update_fields.get(W + "val") or "").lower()
                if value in ("false", "0", "off"):
                    failures.append("docx: word/settings.xml disables w:updateFields")
                else:
                    checks += 1

        if core_root is not None:
            title_element = core_root.find(DC + "title")
            actual_title = (
                normalize_text(title_element.text or "")
                if title_element is not None
                else None
            )
            expected_title = normalize_text(plan["meta"]["title"])
            if actual_title is None:
                failures.append("docx: docProps/core.xml has no dc:title")
            elif actual_title != expected_title:
                failures.append(
                    "docx: dc:title is %r; expected %r from docs/toc.yml"
                    % (actual_title, expected_title)
                )
            else:
                checks += 1

    return checks


def resolve_docx_path(root: str, explicit: str | None, meta):
    if explicit:
        return explicit if os.path.isabs(explicit) else os.path.join(root, explicit)
    if not isinstance(meta, dict) or not isinstance(meta.get("output"), str):
        return None
    return os.path.join(workspace_dir(root), *meta["output"].split("/"))


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate the docs-docx-view Word publication.")
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument(
        "--docx",
        default=None,
        help=(
            "built .docx to check (default: _meta.json output, relative to "
            "docs/docsDocxView; relative paths are resolved against --project-root)"
        ),
    )
    ap.add_argument("--skip-docx", action="store_true", help="skip the built DOCX checks")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        sys.exit("error: project root not found: " + root)

    failures: list = []
    warnings: list = []

    plan, expected_combined = rebuild_expected(root, failures, warnings)

    combined_status = "unchecked"
    manifest_count = 0
    meta = None
    if plan is not None:
        combined_status = check_combined(root, expected_combined, failures)
        manifest_count = check_manifest(root, plan, failures)
        meta = check_meta(root, plan, failures)

    links, sources, status = check_prd_links(root, failures)

    expected_count = len(expected_headings(plan)) if plan is not None else 0
    docx_checks = 0
    if args.skip_docx:
        docx_note = "docx: skipped (--skip-docx)"
    elif plan is None:
        docx_note = "docx: skipped (toc.yml is not usable)"
    else:
        docx_path = resolve_docx_path(root, args.docx, meta)
        if docx_path is None:
            docx_note = "docx: skipped (no output path in _meta.json; pass --docx PATH)"
        else:
            docx_checks = check_docx(root, docx_path, plan, failures)
            docx_note = "docx: checked %s" % display(docx_path, root)

    for message in warnings:
        print("warning: " + message, file=sys.stderr)
    for item in failures:
        print(item, file=sys.stderr)

    print("toc documents: %d" % (len(plan["documents"]) if plan is not None else 0))
    print("combined: %s" % combined_status)
    print("manifest entries: %d" % manifest_count)
    print("prd files checked: %d" % sources)
    print("prd links checked: %d" % links)
    if status:
        print("status markers: %d" % status)
    print("expected headings: %d" % expected_count)
    print(docx_note)
    print("docx checks: %d" % docx_checks)
    print("warnings: %d" % len(warnings))
    print("violations: %d" % len(failures))
    print("result: %s" % ("OK" if not failures else "FAILED"))
    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
