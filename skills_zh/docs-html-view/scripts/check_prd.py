#!/usr/bin/env python3
"""Validate the docs-html-view PRD publication. Stdlib + PyYAML only.

Checks, in order:

1. ``docs/toc.yml``: required metadata and section ids, paths/globs,
   ``modules: auto``, allowed roots, no symlinks, no duplicates.
2. ``_manifest.json``: exact set equality with the TOC-expanded documents plus
   the generated glossary; every source file exists.
3. PRD source links: product chapters and module PRDs may link only to other
   PRD-layer documents (``00-README.md``, ``01-requirements.md``,
   ``02-architecture.md``) or same-page anchors. External URLs, SPEC / Current /
   ADR links, and status markers (``✅/🚧/❌``) are violations. HTML comments,
   fenced code, and inline code are masked.
4. Glossary freshness: ``docsHtmlView/glossary.md`` body equals ``CONTEXT.md``
   (the generated marker/header is ignored).
5. Built HTML anchors: every same-page ``href="#..."`` on a published page has a
   matching ``id``.
6. No unlisted docs: every built ``product/`` ``current/`` ``adr/`` page maps to
   a source document in the manifest.

Exit codes: 0 = clean, 1 = violations (or missing inputs).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import posixpath
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_prd  # noqa: E402  (ships next to this script)

PRD_ALLOWED_BASENAMES = {"00-README.md", "01-requirements.md", "02-architecture.md"}
STATUS_MARKERS = ("✅", "🚧", "❌")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`{1,3}[^`\n]*`{1,3}")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HTML_COMMENT = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)
BARE_URL = re.compile(r"(?:https?|ftp)://[^\s)>\]]+")


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
    return os.path.relpath(path, root).replace(os.sep, "/")


# --- 1. TOC -----------------------------------------------------------------


def check_toc(project_root: str):
    try:
        plan = gen_prd.build_plan(project_root)
    except gen_prd.TocError as exc:
        return None, ["toc: %s" % exc], 0
    return plan, [], len(plan["documents"])


# --- 2. manifest ------------------------------------------------------------


def check_manifest(project_root: str, plan: dict, failures: list) -> int:
    path = os.path.join(project_root, "docs", "docsHtmlView", gen_prd.MANIFEST_NAME)
    if os.path.islink(path) or not os.path.isfile(path):
        failures.append("manifest: missing docs/docsHtmlView/%s (run gen_prd.py)" % gen_prd.MANIFEST_NAME)
        return 0
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        failures.append("manifest: cannot parse %s: %s" % (path, exc))
        return 0
    documents = data.get("documents") if isinstance(data, dict) else data
    if not isinstance(documents, list) or not all(isinstance(item, str) for item in documents):
        failures.append("manifest: documents must be a list of strings")
        return 0

    expected = set(plan["manifest"])
    actual = set(documents)
    for item in sorted(expected - actual):
        failures.append("manifest: missing document: %s" % item)
    for item in sorted(actual - expected):
        failures.append("manifest: unexpected document (not in toc.yml): %s" % item)
    if len(documents) != len(actual):
        failures.append("manifest: duplicate entries")

    for item in sorted(actual):
        if item == "docsHtmlView/glossary.md":
            continue
        source = os.path.join(project_root, "docs", *item.split("/"))
        if os.path.islink(source) or not os.path.isfile(source):
            failures.append("manifest: source does not exist: docs/%s" % item)
    return len(actual)


# --- 3. PRD source links ----------------------------------------------------


def prd_sources(project_root: str, failures: list) -> list:
    product = os.path.join(project_root, "docs", "product")
    if not os.path.isdir(product) or os.path.islink(product):
        failures.append("prd: no docs/product/ directory at " + project_root)
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


def link_violation(project_root: str, source: str, target: str):
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
    product_real = os.path.realpath(os.path.join(project_root, "docs", "product"))
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


def check_prd_links(project_root: str, failures: list) -> tuple:
    sources = prd_sources(project_root, failures)
    links = 0
    status = 0
    seen = set()
    for source in sources:
        rel_source = display(source, project_root)
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
            reason = link_violation(project_root, source, target)
            if reason:
                key = (rel_source, line, target, reason)
                if key not in seen:
                    seen.add(key)
                    failures.append("prd: %s:%d: %s (%s)" % (rel_source, line, target or "(empty target)", reason))

        for index, line_text in enumerate(masked.splitlines()):
            match = REF_DEF.match(line_text)
            if not match:
                continue
            target = parse_target(match.group(1))
            if not target or target.startswith("#"):
                continue
            links += 1
            reason = link_violation(project_root, source, target)
            if reason:
                failures.append("prd: %s:%d: %s (%s)" % (rel_source, index + 1, target, reason))

        for match in BARE_URL.finditer(masked):
            reason = "external link"
            key = (rel_source, line_number(masked, match.start()), match.group(0), reason)
            if key not in seen:
                seen.add(key)
                failures.append("prd: %s:%d: %s (external link)" % (rel_source, key[1], match.group(0)))

        for index, line_text in enumerate(masked.splitlines()):
            for marker in STATUS_MARKERS:
                if marker in line_text:
                    status += 1
                    failures.append(
                        "prd: %s:%d: status marker %s" % (rel_source, index + 1, marker)
                    )
    return links, len(sources), status


# --- 4. glossary ------------------------------------------------------------


def glossary_body(text: str) -> str:
    lines = text.splitlines()
    index = 0
    while index < len(lines) and (not lines[index].strip() or lines[index].startswith("%")):
        index += 1
    return "\n".join(lines[index:]).strip()


def check_glossary(project_root: str, plan: dict, failures: list) -> bool:
    if not plan["glossary"]:
        return False
    generated = os.path.join(project_root, "docs", "docsHtmlView", "glossary.md")
    source = os.path.join(project_root, gen_prd.CONTEXT)
    if os.path.islink(generated) or not os.path.isfile(generated):
        failures.append("glossary: missing docs/docsHtmlView/glossary.md (run gen_prd.py)")
        return False
    try:
        with open(generated, encoding="utf-8") as fh:
            generated_text = fh.read()
        with open(source, encoding="utf-8") as fh:
            source_text = fh.read()
    except OSError as exc:
        failures.append("glossary: cannot read: %s" % exc)
        return False
    if glossary_body(generated_text) != source_text.replace("\r\n", "\n").strip():
        failures.append("glossary: docs/docsHtmlView/glossary.md is stale; re-run gen_prd.py")
        return False
    return True


# --- 5. built HTML anchors --------------------------------------------------


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            if name == "id":
                self.ids.add(value)
            elif name == "name" and tag == "a":
                self.ids.add(value)
            elif name == "href" and value.startswith("#") and len(value) > 1:
                self.targets.append(value[1:])

    handle_startendtag = handle_starttag


def expected_pages(plan: dict) -> list:
    pages = set()
    for entry in plan["manifest"]:
        pages.add(posixpath.splitext(entry)[0] + ".html")
    pages.add("docsHtmlView/index.html")
    for wrapper in plan["wrappers"]:
        pages.add(wrapper["docname"] + ".html")
    return sorted(pages)


def check_html(project_root: str, html_dir: str, plan: dict, failures: list) -> tuple:
    if not os.path.isdir(html_dir):
        failures.append("html: no build directory at %s (run the build first or pass --skip-html)" % html_dir)
        return 0, 0

    pages = expected_pages(plan)
    anchors = 0
    seen = set()
    for rel in pages:
        path = os.path.join(html_dir, *rel.split("/"))
        if os.path.islink(path) or not os.path.isfile(path):
            failures.append("html: missing built page: %s (run the build first)" % rel)
            continue
        parser = AnchorParser()
        try:
            with open(path, encoding="utf-8") as fh:
                parser.feed(fh.read())
            parser.close()
        except (OSError, UnicodeDecodeError) as exc:
            failures.append("html: %s: cannot parse: %s" % (rel, exc))
            continue
        for target in parser.targets:
            anchors += 1
            if target in parser.ids or unquote(target) in parser.ids:
                continue
            key = (rel, target)
            if key not in seen:
                seen.add(key)
                failures.append("anchor: %s: #%s" % (rel, target))

    allowed = {posixpath.splitext(entry)[0] for entry in plan["manifest"]}
    unlisted = 0
    for root_name in ("product", "current", "adr"):
        root = os.path.join(html_dir, root_name)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames.sort()
            for name in sorted(filenames):
                if not name.endswith(".html"):
                    continue
                page = os.path.join(dirpath, name)
                docname = posixpath.splitext(display(page, html_dir))[0]
                if docname in allowed:
                    continue
                unlisted += 1
                failures.append("unlisted: built page is not in the manifest: %s" % display(page, html_dir))
    return anchors, unlisted


# --- main -------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate the docs-html-view PRD publication.")
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument(
        "--html-dir",
        default="docs/docsHtmlView/build/html",
        help="built HTML root (default: docs/docsHtmlView/build/html)",
    )
    ap.add_argument("--skip-html", action="store_true", help="skip the built HTML checks")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    failures: list = []

    plan, toc_failures, doc_count = check_toc(root)
    failures.extend(toc_failures)
    if plan is None:
        for item in failures:
            print(item, file=sys.stderr)
        print("result: FAILED (toc.yml is not usable)")
        sys.exit(1)

    manifest_count = check_manifest(root, plan, failures)
    links, sources, status = check_prd_links(root, failures)
    glossary_ok = check_glossary(root, plan, failures)

    anchors = 0
    unlisted = 0
    html_note = "html: skipped (--skip-html)"
    if not args.skip_html:
        html_dir = args.html_dir
        if not os.path.isabs(html_dir):
            html_dir = os.path.join(root, html_dir)
        anchors, unlisted = check_html(root, html_dir, plan, failures)
        html_note = "html: checked %d page(s)" % len(expected_pages(plan))

    for item in failures:
        print(item, file=sys.stderr)

    print("toc documents: %d" % doc_count)
    print("manifest entries: %d" % manifest_count)
    print("prd files checked: %d" % sources)
    print("prd links checked: %d" % links)
    if status:
        print("status markers: %d" % status)
    print("glossary: %s" % ("fresh" if glossary_ok else ("absent" if not plan["glossary"] else "FAILED")))
    print("anchors checked: %d" % anchors)
    print(html_note)
    print("unlisted docs: %d" % unlisted)
    print("violations: %d" % len(failures))
    print("result: %s" % ("OK" if not failures else "FAILED"))
    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
