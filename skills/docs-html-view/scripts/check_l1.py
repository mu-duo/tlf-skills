#!/usr/bin/env python3
"""Validate docs-html-view L1 sources and built HTML anchors. Stdlib only.

Source rules for the L1 layer (``docs/prd/00-README.md`` and each module
``docs/prd/<NN-module>/00-README.md``):

- allowed link targets: same-file anchors (``#...``) and relative paths that
  resolve to another ``00-README.md`` under ``docs/prd/``;
- everything else is a violation: external URLs, absolute paths, links to
  Current / ADR / L2 (``01-spec``, ``02-interfaces``, ``03-nfr``, ``design/``),
  or anything that escapes ``docs/prd``.

Links inside fenced code, inline code, and HTML comments are ignored (template
placeholder comments are not violations). The product ``docs/prd/00-README.md``
is required; module L1 files alone are not enough.

Built-HTML rules: every same-file ``href="#..."`` target in
``<html-dir>/prd/**/00-README.html`` must match an ``id`` in that page. If no L1
HTML files are found the check fails instead of silently passing.

Exit codes: 0 = clean, 1 = violations (or missing inputs).
"""
from __future__ import annotations

import argparse
import os
import posixpath
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

L1_FILE = "00-README.md"
L1_HTML = "00-README.html"

# L2 / Current / ADR markers that must never appear in an L1 link target.
FORBIDDEN_MARKERS = (
    "../current",
    "../adr",
    "01-spec",
    "02-interfaces",
    "03-nfr",
    "design/",
)

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`{1,3}[^`\n]*`{1,3}")
LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]*)\)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HTML_COMMENT = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL)


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
    masked = "".join(masked_lines)
    return INLINE_CODE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), masked)


def mask_comments(text: str) -> str:
    """Blank out HTML comments (including template placeholders), keeping offsets."""
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


def find_sources(prd_root: str):
    sources = []
    for dirpath, dirnames, filenames in os.walk(prd_root, followlinks=False):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename != L1_FILE:
                continue
            path = os.path.join(dirpath, filename)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            sources.append(path)
    return sources


def display(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def check_sources(sources, prd_root: str, project_root: str):
    violations = []
    links = 0
    prd_real = os.path.realpath(prd_root)
    for source in sources:
        rel_source = display(source, project_root)
        try:
            with open(source, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            violations.append("%s: cannot read: %s" % (rel_source, exc))
            continue
        masked = mask_comments(mask_code(text))
        for match in LINK.finditer(masked):
            target = parse_target(match.group(2))
            line = line_number(masked, match.start())
            links += 1
            reason = link_violation(source, prd_real, target)
            if reason:
                violations.append(
                    "%s:%d: %s (%s)"
                    % (rel_source, line, target or "(empty target)", reason)
                )
    return links, violations


def link_violation(source: str, prd_real: str, target: str):
    """Return a reason string when the target is not an allowed L1 link."""
    if not target:
        return "empty target"
    if target.startswith("#"):
        return None
    lower = target.lower()
    if lower.startswith(("http:", "https:", "mailto:")):
        return "external link"
    if SCHEME.match(target):
        return "non-relative link"
    if target.startswith(("/", "~")) or re.match(r"^[A-Za-z]:[\\/]", target):
        return "absolute path"
    for marker in FORBIDDEN_MARKERS:
        if marker in lower:
            return "links outside the L1 layer"
    path_part = target.split("#", 1)[0].split("?", 1)[0]
    if not path_part:
        return None
    if "\\" in path_part:
        return "non-portable path"
    resolved = os.path.normpath(
        os.path.join(os.path.dirname(source), path_part.replace("/", os.sep))
    )
    resolved_real = os.path.realpath(resolved)
    try:
        inside = os.path.commonpath([resolved_real, prd_real]) == prd_real
    except ValueError:
        inside = False
    if not inside:
        return "escapes docs/prd"
    if os.path.basename(resolved) != L1_FILE:
        return "not an L1 00-README.md"
    if os.path.islink(resolved) or not os.path.isfile(resolved):
        return "missing L1 target"
    return None


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


def find_html(html_root: str):
    pages = []
    for dirpath, dirnames, filenames in os.walk(html_root, followlinks=False):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename == L1_HTML:
                pages.append(os.path.join(dirpath, filename))
    return pages


def check_html(pages, project_root: str):
    broken = []
    anchors = 0
    for page in pages:
        parser = AnchorParser()
        try:
            with open(page, encoding="utf-8") as fh:
                parser.feed(fh.read())
            parser.close()
        except (OSError, UnicodeDecodeError) as exc:
            broken.append("%s: cannot parse: %s" % (display(page, project_root), exc))
            continue
        for target in parser.targets:
            anchors += 1
            fragment = unquote(target)
            if target in parser.ids or fragment in parser.ids:
                continue
            broken.append("%s: #%s" % (display(page, project_root), target))
    return anchors, broken


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate L1 links and built HTML anchors.")
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument(
        "--html-dir",
        default="docs/docsHtmlView/build-l1/html",
        help="built L1 HTML root (default: docs/docsHtmlView/build-l1/html)",
    )
    ap.add_argument("--skip-html", action="store_true", help="run source checks only")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    prd_root = os.path.join(root, "docs", "prd")
    if not os.path.isdir(prd_root):
        print("error: no docs/prd/ directory at " + root, file=sys.stderr)
        sys.exit(1)

    product_l1 = os.path.join(prd_root, L1_FILE)
    if os.path.islink(product_l1) or not os.path.isfile(product_l1):
        print(
            "error: missing product L1 docs/prd/%s; module L1 files alone are not "
            "enough (create the product L1 before checking)" % L1_FILE,
            file=sys.stderr,
        )
        sys.exit(1)

    sources = find_sources(prd_root)
    if not sources:
        print(
            "error: no L1 files (%s) under docs/prd/; nothing to check" % L1_FILE,
            file=sys.stderr,
        )
        sys.exit(1)

    links, violations = check_sources(sources, prd_root, root)

    anchors = 0
    broken = []
    html_note = "HTML check: skipped (--skip-html)"
    if not args.skip_html:
        html_dir = args.html_dir
        if not os.path.isabs(html_dir):
            html_dir = os.path.join(root, html_dir)
        if not os.path.isdir(html_dir):
            print("error: no L1 HTML directory at " + html_dir, file=sys.stderr)
            print("run the L1 build first or pass --skip-html", file=sys.stderr)
            sys.exit(1)
        pages = find_html(os.path.join(html_dir, "prd"))
        if not pages:
            print(
                "error: no L1 HTML files (%s) under %s; run the L1 build first or pass --skip-html"
                % (L1_HTML, os.path.join(html_dir, "prd")),
                file=sys.stderr,
            )
            sys.exit(1)
        anchors, broken = check_html(pages, root)
        html_note = "HTML pages checked: %d" % len(pages)

    for item in violations:
        print("source: " + item, file=sys.stderr)
    for item in broken:
        print("anchor: " + item, file=sys.stderr)

    print("L1 files checked: %d" % len(sources))
    print("links checked: %d" % links)
    print("broken anchors: %d" % len(broken))
    print(html_note)
    print("violations: %d" % (len(violations) + len(broken)))

    sys.exit(1 if violations or broken else 0)


if __name__ == "__main__":
    main()
