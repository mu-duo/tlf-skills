#!/usr/bin/env python3
"""Generate the docs-docx-view Word publication under ``docs/docsDocxView``.

The single source of truth is ``docs/toc.yml``. It is validated with the same
semantics as docs-html-view (allowed roots, globs, ``modules: auto``,
``exclude``, no symlinks, no duplicates, missing paths fail), its globs are
expanded, and the listed documents are concatenated into one pandoc input:

- ``docsDocxView/combined.md``      YAML cover metadata + hand-written TOC field
                                    + every document, with heading levels
                                    remapped, anchors rewritten, remote images
                                    replaced by plain text placeholders, and
                                    local images validated and made
                                    project-root-relative (the single pandoc
                                    input; it carries the generated marker)
- ``docsDocxView/_manifest.json``   exact TOC expansion order
- ``docsDocxView/_meta.json``       title/version/date/abstract/author/lang/output

Missing ``reference.docx`` / ``build.sh`` / ``build.bat`` workspace files are
seeded once from the skill's ``assets/`` directory. Any file that already
exists is user-owned and never overwritten. This generator never runs pandoc,
never creates ``build/``, and never edits the sources or the TOC. Build helpers
are thin build-only wrappers; see ``assets/build.sh``.

Exit codes: 0 = generated; 1 = refused (invalid TOC, unsafe document, unowned
output). Nothing is written when generation is refused.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import posixpath
import re
import shutil
import sys
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in a broken env
    sys.exit("error: PyYAML is required (install requirements.txt before running gen_docx.py)")

MARK = "# docs-docx-view: generated document; do not edit"
GENERATED_BY = "docs-docx-view gen_docx.py"
WORKSPACE = "docs/docsDocxView"
CONTEXT = "CONTEXT.md"
MANIFEST_NAME = "_manifest.json"
META_NAME = "_meta.json"
COMBINED_NAME = "combined.md"
BUILD_HELPERS = ("build.sh", "build.bat")
REFERENCE_DOCX = "reference.docx"
HELPER_NEWLINES = {"build.sh": "\n", "build.bat": "\r\n"}
ASSETS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "assets")
)
ALLOWED_ROOTS = ("docs/product", "docs/current", "docs/adr")
REQUIRED_SECTIONS = ("overview", "requirements", "architecture", "appendix")
REQUIRED_APPENDIX = ("glossary", "spec", "current", "adr")
DOC_SUFFIXES = (".md", ".rst")
SECTION_KEYS = {"id", "title", "documents", "sections", "modules", "exclude"}
TOP_KEYS = {"title", "version", "date", "abstract", "author", "sections"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

DOC_MARK_PREFIX = "<!-- docs-docx-view: doc "
DOC_MARK_SUFFIX = " -->"
COVER_MARK = "<!-- docs-docx-view: cover -->"
PAGE_BREAK = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```'
TOC_HEADING = '::: {custom-style="TOC Heading"}\n目录\n:::'
TOC_FIELD = (
    '```{=openxml}\n'
    '<w:p><w:fldSimple w:instr="TOC \\o &quot;1-3&quot; \\h \\z \\u" w:dirty="true">'
    "<w:r><w:t>Update field to build the table of contents</w:t></w:r>"
    "</w:fldSimple></w:p>\n"
    "```"
)

_HEADING = re.compile(r"^(#{1,6})(?:[ \t]+(.*))?$")
_HEADING_TRAILING = re.compile(r"[ \t]+#+[ \t]*$")
_HEADING_ATTR = re.compile(r"[ \t]*\{[^}]*\}[ \t]*$")
_INDENTED_HEADING = re.compile(r"^[ \t]+#{1,6}(?:[ \t]|$)")
_SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
_INLINE_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
_REF_IMAGE = re.compile(r"!\[([^\]]*)\]\[([^\]]*)\]")
_SHORTCUT_IMAGE = re.compile(r"!\[([^\]]+)\](?![\[(])")
_HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_HTML_SRC = re.compile(r"""src\s*=\s*["']([^"']*)["']""", re.IGNORECASE)
_HTML_ALT = re.compile(r"""alt\s*=\s*["']([^"']*)["']""", re.IGNORECASE)
_REF_DEF = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(<[^>]*>|\S+)")
_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_FORBIDDEN = (
    (re.compile(r"\{include\}"), "MyST directive {include}"),
    (re.compile(r"\{literalinclude\}"), "MyST directive {literalinclude}"),
    (re.compile(r"\{raw\}"), "MyST directive {raw}"),
    (re.compile(r"\{=html\}"), "raw HTML block {=html}"),
    (re.compile(r"\{=openxml\}"), "raw OpenXML block {=openxml}"),
    (re.compile(r"^[ \t]*\.\.[ \t]+include::", re.MULTILINE), "rST .. include::"),
    (re.compile(r"^[ \t]*\.\.[ \t]+literalinclude::", re.MULTILINE), "rST .. literalinclude::"),
    (re.compile(r"^[ \t]*\.\.[ \t]+raw::", re.MULTILINE), "rST .. raw::"),
)

_PROVENANCE = re.compile(
    r"\A\ufeff?(?:[ \t]*\r?\n)*"
    r"(?:[ \t]*>[ \t]*模板来源[^\n]*(?:\r?\n[ \t]*>[^\n]*)*"
    r"|[ \t]*<!--[ \t]*模板来源.*?-->)[ \t]*(?:\r?\n)+",
    re.DOTALL,
)

WARNINGS: list = []


class TocError(Exception):
    """A TOC, document, or workspace problem that must stop generation."""


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print("warning: " + msg, file=sys.stderr)


def rel_posix(path: str, base: str) -> str:
    return os.path.relpath(path, base).replace(os.sep, "/")


def strip_provenance(text: str) -> str:
    """Remove leading template-origin markers; never touch body occurrences."""
    while True:
        stripped = _PROVENANCE.sub("", text, count=1)
        if stripped == text:
            return text
        text = stripped


def scalar_text(value, label: str) -> str:
    """Normalize a YAML scalar to a non-empty single-line string."""
    if isinstance(value, bool) or value is None:
        raise TocError("%s must be a non-empty string" % label)
    if isinstance(value, (datetime.date, datetime.datetime)):
        text = value.isoformat()
    elif isinstance(value, (int, float)):
        text = str(value)
    elif isinstance(value, str):
        text = value
    else:
        raise TocError("%s must be a string" % label)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise TocError("%s must be a non-empty string" % label)
    return text


def sanitize(text: str) -> str:
    """Neutralize text that is injected into generated Markdown."""
    text = re.sub(r"[<>`{}\[\]|]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def sanitize_version(version: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", version)
    return value.strip(".-_")


def output_path(version: str) -> str:
    safe = sanitize_version(version)
    return "build/prd.docx" if not safe else "build/prd-%s.docx" % safe


# --------------------------------------------------------------------------- #
# TOC parsing (semantics mirrored from docs-html-view/scripts/gen_prd.py)
# --------------------------------------------------------------------------- #


def load_toc(project_root: str) -> dict:
    path = os.path.join(project_root, "docs", "toc.yml")
    if os.path.islink(path):
        raise TocError("docs/toc.yml must not be a symlink")
    if not os.path.isfile(path):
        raise TocError("missing docs/toc.yml at " + path)
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        raise TocError("cannot parse docs/toc.yml: %s" % exc)
    if not isinstance(data, dict):
        raise TocError("docs/toc.yml must be a YAML mapping")
    unknown = sorted(set(data) - TOP_KEYS)
    if unknown:
        warn("ignoring unknown toc.yml key(s): " + ", ".join(unknown))
    return data


def normalize_pattern(value, label: str) -> str:
    if not isinstance(value, str):
        raise TocError("%s must be a string" % label)
    raw = value.strip()
    if not raw:
        raise TocError("%s must not be empty" % label)
    if "\\" in raw:
        raise TocError("%s must use forward slashes: %r" % (label, value))
    if raw.startswith("/") or _DRIVE.match(raw):
        raise TocError("%s must be relative to the project root: %r" % (label, value))
    norm = posixpath.normpath(raw)
    if norm in (".", "..") or norm.startswith("../"):
        raise TocError("%s must stay inside the project root: %r" % (label, value))
    if norm == CONTEXT:
        return norm
    if not any(norm == root or norm.startswith(root + "/") for root in ALLOWED_ROOTS):
        raise TocError(
            "%s must be under docs/product, docs/current, docs/adr, or be CONTEXT.md: %r"
            % (label, value)
        )
    return norm


def has_magic(pattern: str) -> bool:
    return "*" in pattern or "?" in pattern or "[" in pattern


def check_no_symlink(project_root: str, rel: str, label: str) -> None:
    parts = rel.split("/")
    current = project_root
    for part in parts:
        current = os.path.join(current, part)
        if os.path.islink(current):
            raise TocError("%s must not use a symlink: %s" % (label, rel))
    real_root = os.path.realpath(project_root)
    real = os.path.realpath(os.path.join(project_root, rel))
    try:
        inside = os.path.commonpath([real, real_root]) == real_root
    except ValueError:
        inside = False
    if not inside:
        raise TocError("%s escapes the project root: %s" % (label, rel))


def validate_document(project_root: str, rel: str, label: str) -> str:
    rel = posixpath.normpath(rel)
    if rel == CONTEXT:
        check_no_symlink(project_root, rel, label)
        path = os.path.join(project_root, CONTEXT)
        if not os.path.isfile(path):
            raise TocError("%s: missing %s at the project root" % (label, CONTEXT))
        return rel
    if not any(rel.startswith(root + "/") for root in ALLOWED_ROOTS):
        raise TocError("%s resolves outside the allowed roots: %s" % (label, rel))
    if posixpath.splitext(rel)[1].lower() not in DOC_SUFFIXES:
        raise TocError("%s must be a .md or .rst document: %s" % (label, rel))
    check_no_symlink(project_root, rel, label)
    if not os.path.isfile(os.path.join(project_root, rel)):
        raise TocError("%s is not an existing regular file: %s" % (label, rel))
    return rel


def expand_documents(project_root: str, patterns, label: str) -> list:
    if not isinstance(patterns, list):
        raise TocError("%s.documents must be a list of paths or globs" % label)
    result = []
    for raw in patterns:
        pattern = normalize_pattern(raw, label + ".documents")
        if pattern == CONTEXT:
            result.append((validate_document(project_root, CONTEXT, label), False))
            continue
        if has_magic(pattern):
            full = os.path.join(project_root, *pattern.split("/"))
            matches = sorted(glob.glob(full, recursive=True))
            if not matches:
                warn("%s glob matched nothing: %s" % (label, pattern))
                continue
            for match in matches:
                rel = rel_posix(match, project_root)
                result.append((validate_document(project_root, rel, label), True))
        else:
            result.append((validate_document(project_root, pattern, label), False))
    return result


def module_sort_key(path: str):
    name = posixpath.basename(posixpath.dirname(path))
    match = re.match(r"^(\d+)", name)
    return (0, int(match.group(1)), name.casefold()) if match else (1, 0, name.casefold())


def expand_modules(project_root: str, label: str, exclude) -> list:
    if not isinstance(exclude, list) or not all(isinstance(item, str) for item in exclude):
        raise TocError("%s.exclude must be a list of module names or paths" % label)
    pattern = "docs/product/*/00-README.md"
    matches = sorted(
        glob.glob(os.path.join(project_root, *pattern.split("/"))),
        key=lambda path: module_sort_key(rel_posix(path, project_root)),
    )
    excluded = {item.strip().strip("/") for item in exclude}
    result = []
    for match in matches:
        rel = rel_posix(match, project_root)
        module_dir = posixpath.basename(posixpath.dirname(rel))
        if module_dir in excluded or rel in excluded or posixpath.dirname(rel) in excluded:
            continue
        result.append(validate_document(project_root, rel, label))
    if not result:
        warn("%s has modules: auto but no docs/product/*/00-README.md matched" % label)
    return [(rel, True) for rel in result]


def check_section_id(value, label: str, seen: set) -> str:
    if not isinstance(value, str) or not ID_RE.match(value):
        raise TocError("%s must be a simple id ([A-Za-z0-9._-]): %r" % (label, value))
    if value in seen:
        raise TocError("duplicate section id: %r" % (value,))
    seen.add(value)
    return value


def parse_section(project_root: str, section, label: str, seen_ids: set, seen_docs: dict) -> dict:
    if not isinstance(section, dict):
        raise TocError("%s must be a mapping" % label)
    unknown = sorted(set(section) - SECTION_KEYS)
    if unknown:
        raise TocError("%s has unknown key(s): %s" % (label, ", ".join(unknown)))
    sid = check_section_id(section.get("id"), label + ".id", seen_ids)
    title = section.get("title")
    if not isinstance(title, str) or not title.strip():
        raise TocError("%s.title must be a non-empty string" % label)

    documents = expand_documents(project_root, section.get("documents", []), label)

    modules = section.get("modules")
    if modules is not None:
        if modules != "auto":
            raise TocError('%s.modules must be "auto" when set' % label)
        documents.extend(expand_modules(project_root, label, section.get("exclude", [])))
    elif "exclude" in section:
        raise TocError("%s.exclude is only valid together with modules: auto" % label)

    children = section.get("sections", [])
    if not isinstance(children, list):
        raise TocError("%s.sections must be a list" % label)
    child_sections = [
        parse_section(project_root, child, "%s.sections[%d]" % (label, index), seen_ids, seen_docs)
        for index, child in enumerate(children)
    ]

    if not ("documents" in section or children or modules is not None):
        raise TocError("%s needs documents, sections, or modules: auto" % label)

    unique = []
    for rel, implicit in documents:
        if rel in seen_docs:
            if implicit:
                continue
            raise TocError(
                "duplicate document %s (already listed in %s)" % (rel, seen_docs[rel])
            )
        seen_docs[rel] = label
        unique.append(rel)

    return {"id": sid, "title": title, "documents": unique, "children": child_sections}


def assign_section_ids(sections) -> None:
    """Assign pre-order ordinals and heading levels to every section."""
    counter = [0]

    def walk(section: dict, level: int) -> None:
        counter[0] += 1
        section["ordinal"] = counter[0]
        section["level"] = level
        for child in section["children"]:
            walk(child, level + 1)

    for section in sections:
        walk(section, 1)


def flatten_documents(section: dict) -> list:
    result = list(section["documents"])
    for child in section["children"]:
        result.extend(flatten_documents(child))
    return result


def build_plan(project_root: str) -> dict:
    """Validate docs/toc.yml and return the resolved publication plan."""
    toc = load_toc(project_root)
    meta = {
        "title": scalar_text(toc.get("title"), "toc.yml title"),
        "version": scalar_text(toc.get("version"), "toc.yml version"),
        "date": scalar_text(toc.get("date"), "toc.yml date"),
        "abstract": scalar_text(toc.get("abstract"), "toc.yml abstract"),
    }
    author = toc.get("author")
    meta["author"] = scalar_text(author, "toc.yml author") if author is not None else ""

    sections = toc.get("sections")
    if not isinstance(sections, list) or not sections:
        raise TocError("toc.yml sections must be a non-empty list")

    seen_ids: set = set()
    seen_docs: dict = {}
    parsed = [
        parse_section(project_root, section, "sections[%d]" % index, seen_ids, seen_docs)
        for index, section in enumerate(sections)
    ]

    top_ids = [section["id"] for section in parsed]
    missing = [sid for sid in REQUIRED_SECTIONS if sid not in top_ids]
    if missing:
        raise TocError("toc.yml is missing required section id(s): " + ", ".join(missing))

    appendix = next(section for section in parsed if section["id"] == "appendix")
    appendix_ids = [child["id"] for child in appendix["children"]]
    missing_appendix = [sid for sid in REQUIRED_APPENDIX if sid not in appendix_ids]
    if missing_appendix:
        raise TocError(
            "toc.yml appendix is missing required section id(s): " + ", ".join(missing_appendix)
        )

    documents = [rel for section in parsed for rel in flatten_documents(section)]
    if not documents:
        raise TocError("docs/toc.yml lists no documents")

    assign_section_ids(parsed)
    return {"meta": meta, "sections": parsed, "documents": documents}


# --------------------------------------------------------------------------- #
# Document scanning and heading mapping
# --------------------------------------------------------------------------- #


def fence_mask(lines) -> list:
    mask = [False] * len(lines)
    in_fence = False
    char = ""
    length = 0
    for index, line in enumerate(lines):
        match = _FENCE.match(line)
        if match:
            mask[index] = True
            token = match.group(1)
            if not in_fence:
                in_fence, char, length = True, token[0], len(token)
            elif token[0] == char and len(token) >= length:
                in_fence, char, length = False, "", 0
        elif in_fence:
            mask[index] = True
    return mask


def scan_forbidden(text: str, rel: str) -> None:
    for pattern, label in _FORBIDDEN:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            raise TocError("%s:%d: forbidden construct: %s" % (rel, line, label))


def read_document(project_root: str, rel: str) -> str:
    path = os.path.join(project_root, *rel.split("/"))
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except UnicodeDecodeError as exc:
        raise TocError("%s: cannot decode as UTF-8: %s" % (rel, exc))
    except OSError as exc:
        raise TocError("%s: cannot read: %s" % (rel, exc))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    scan_forbidden(text, rel)
    text = strip_provenance(text)
    if text.startswith("\ufeff"):
        text = text[1:]
    return text


def slugify(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def parse_dest(raw: str):
    """Split a Markdown destination into (dest, trailing title text)."""
    raw = raw.strip()
    if raw.startswith("<"):
        end = raw.find(">")
        if end != -1:
            return raw[1:end], raw[end + 1 :].strip()
        return raw, ""
    parts = raw.split(None, 1)
    if not parts:
        return "", ""
    if len(parts) > 1:
        remainder = parts[1].strip()
        if not remainder.startswith(('"', "'", "(")):
            # Bare destinations may contain spaces in practice (for example
            # ``![alt](img/a b.png)``); treat the whole value as the target.
            return raw, ""
    return parts[0], (parts[1].strip() if len(parts) > 1 else "")


def add_anchor(anchors: dict, text: str, target: str) -> None:
    keys = {text.strip(), unquote(text.strip()), slugify(text), slugify(unquote(text))}
    for key in keys:
        if not key:
            continue
        anchors.setdefault(key, target)
        anchors.setdefault(key.lower(), target)


def image_kind(dest: str) -> str:
    value = dest.strip()
    if not value:
        return "empty"
    low = value.lower()
    if low.startswith(("http://", "https://", "//")):
        return "remote"
    if low.startswith("file:"):
        raise TocError("absolute/file image target is not allowed: %s" % dest)
    if value.startswith(("/", "~")) or _DRIVE.match(value):
        raise TocError("absolute/file image target is not allowed: %s" % dest)
    if _SCHEME.match(value):
        return "remote"
    return "local"


def local_image_dest(project_root: str, rel: str, dest: str) -> str:
    clean = unquote(dest.split("?", 1)[0].split("#", 1)[0])
    if not clean:
        raise TocError("%s: empty local image target" % rel)
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(rel), clean))
    if joined in (".", "..") or joined.startswith("../"):
        raise TocError("%s: image escapes the project root: %s" % (rel, dest))
    parts = joined.split("/")
    current = project_root
    for part in parts:
        current = os.path.join(current, part)
        if os.path.islink(current):
            raise TocError("%s: image path must not use a symlink: %s" % (rel, dest))
    path = os.path.join(project_root, *parts)
    if not os.path.isfile(path):
        raise TocError("%s: image is not an existing regular file: %s" % (rel, dest))
    real = os.path.realpath(path)
    real_root = os.path.realpath(project_root)
    try:
        inside_root = os.path.commonpath([real, real_root]) == real_root
    except ValueError:
        inside_root = False
    if not inside_root:
        raise TocError("%s: image escapes the project root: %s" % (rel, dest))
    inside_allowed = False
    for root in ALLOWED_ROOTS:
        root_real = os.path.realpath(os.path.join(project_root, *root.split("/")))
        try:
            if os.path.commonpath([real, root_real]) == root_real:
                inside_allowed = True
                break
        except ValueError:
            continue
    if not inside_allowed:
        raise TocError(
            "%s: image must be under docs/product, docs/current, or docs/adr: %s" % (rel, dest)
        )
    return joined


def image_reference(dest: str) -> str:
    return "<%s>" % dest if re.search(r"\s", dest) else dest


def placeholder(alt: str) -> str:
    text = re.sub(r"[\[\]\r\n]", "", alt).strip()
    return "[图片：%s]" % text if text else "[图片]"


def apply_image_attrs(attrs: str | None) -> str:
    """Return the attribute block, applying the 16cm width default."""
    if attrs is None:
        return "{width=16cm}"
    body = attrs.strip()
    if "width" in body or "height" in body:
        return "{%s}" % body
    return "{%s}" % (("width=16cm " + body).strip())


def process_images(line: str, info: dict, lineno: int, project_root: str) -> str:
    out = []
    pos = 0
    for match in _INLINE_IMAGE.finditer(line):
        start, end = match.span()
        if start < pos:
            continue
        out.append(line[pos:start])
        alt, raw = match.group(1), match.group(2)
        dest, rest = parse_dest(raw)
        attr_match = re.match(r"\{([^}]*)\}", line[end:])
        attrs = attr_match.group(1) if attr_match else None
        end = end + attr_match.end() if attr_match else end
        pos = end
        kind = image_kind(dest)
        if kind == "remote":
            warn("%s:%d -> remote image replaced: %s" % (info["rel"], lineno, dest))
            out.append(placeholder(alt))
            continue
        new_dest = local_image_dest(project_root, info["rel"], dest)
        suffix = apply_image_attrs(attrs)
        title = " " + rest if rest else ""
        out.append("![%s](%s%s)%s" % (alt, image_reference(new_dest), title, suffix))
    out.append(line[pos:])
    line = "".join(out)

    def html_replacement(match):
        tag = match.group(0)
        src = _HTML_SRC.search(tag)
        if not src:
            return tag
        dest = src.group(1)
        alt_match = _HTML_ALT.search(tag)
        alt = alt_match.group(1) if alt_match else ""
        kind = image_kind(dest)
        if kind == "remote":
            warn("%s:%d -> remote image replaced: %s" % (info["rel"], lineno, dest))
            return placeholder(alt)
        new_dest = local_image_dest(project_root, info["rel"], dest)
        return tag[: src.start(1)] + image_reference(new_dest) + tag[src.end(1) :]

    return _HTML_IMAGE.sub(html_replacement, line)


def resolve_anchor(info: dict, anchor: str):
    if not anchor:
        return None
    for key in (anchor, unquote(anchor)):
        key = key.lstrip("#")
        for candidate in (key, key.lower(), slugify(key)):
            if candidate and candidate in info["anchors"]:
                return info["anchors"][candidate]
    return None


def rewrite_link(info: dict, docs: dict, dest: str, lineno: int):
    target = dest.strip()
    if not target or _SCHEME.match(target):
        return None
    source_rel = info["rel"]

    if target.startswith("#"):
        anchor = target[1:]
        resolved = resolve_anchor(info, anchor)
        if resolved:
            return "#" + resolved
        warn("%s:%d -> %s" % (source_rel, lineno, target))
        return None

    if "#" in target:
        path_part, fragment = target.split("#", 1)
    else:
        path_part, fragment = target, None
    path_clean = unquote(path_part)
    if not path_clean:
        return None
    resolved_rel = posixpath.normpath(
        posixpath.join(posixpath.dirname(source_rel), path_clean)
    )
    target_info = docs.get(resolved_rel)
    if target_info is not None:
        if fragment:
            anchor_id = resolve_anchor(target_info, fragment)
            if anchor_id is None:
                warn("%s:%d -> %s" % (source_rel, lineno, target))
                return None
            return "#" + anchor_id
        return "#" + (target_info["title_id"] or target_info["section_id"])
    if target.endswith(".md") or "#" in target:
        warn("%s:%d -> %s" % (source_rel, lineno, target))
    return None


def process_links(line: str, info: dict, docs: dict, lineno: int) -> str:
    out = []
    pos = 0
    for match in _LINK.finditer(line):
        start, end = match.span()
        if start < pos or match.group(1):
            continue
        text, raw = match.group(2), match.group(3)
        dest, rest = parse_dest(raw)
        new = rewrite_link(info, docs, dest, lineno)
        if new is None:
            continue
        out.append(line[pos:start])
        suffix = " " + rest if rest else ""
        out.append("[%s](%s%s)" % (text, new, suffix))
        pos = end
    out.append(line[pos:])
    return "".join(out)


def collect_remote_image_defs(text: str, lines, mask, rel: str) -> tuple:
    """Find http(s) reference definitions used by reference-style images."""
    used = set()
    for match in _REF_IMAGE.finditer(text):
        label = (match.group(2) or match.group(1)).strip()
        if label:
            used.add(label.lower())
    for match in _SHORTCUT_IMAGE.finditer(text):
        used.add(match.group(1).strip().lower())

    defs = {}
    blank = set()
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        match = _REF_DEF.match(line)
        if not match:
            continue
        dest, _ = parse_dest(match.group(2))
        if not dest.lower().startswith(("http://", "https://", "//")):
            continue
        label = match.group(1).strip()
        if label.lower() not in used:
            continue
        defs[label.lower()] = dest
        blank.add(index)
        warn("%s:%d: reference image definition replaced: %s" % (rel, index + 1, dest))
    return defs, blank


def process_reference_images(line: str, remote_labels: dict) -> str:
    line = _REF_IMAGE.sub(
        lambda m: placeholder(m.group(1) or m.group(2))
        if (m.group(2) or m.group(1)).strip().lower() in remote_labels
        else m.group(0),
        line,
    )

    def shortcut(match):
        key = match.group(1).strip().lower()
        if key in remote_labels:
            return placeholder(match.group(1))
        return match.group(0)

    return _SHORTCUT_IMAGE.sub(shortcut, line)


def process_document(project_root: str, rel: str, section: dict, counter: dict) -> dict:
    text = read_document(project_root, rel)
    lines = text.split("\n")
    mask = fence_mask(lines)
    section_level = section["level"]

    raw_headings = []
    warned_indented = False
    warned_setext = False
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        match = _HEADING.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2) or ""
            heading = _HEADING_TRAILING.sub("", heading)
            heading = _HEADING_ATTR.sub("", heading).strip()
            raw_headings.append((index, level, heading))
            continue
        if _INDENTED_HEADING.match(line):
            if not warned_indented:
                warn("%s:%d: indented heading treated as plain text" % (rel, index + 1))
                warned_indented = True
            continue
        if (
            line.strip()
            and index + 1 < len(lines)
            and not mask[index + 1]
            and _SETEXT_UNDERLINE.match(lines[index + 1])
        ):
            if not warned_setext:
                warn("%s:%d: Setext heading treated as plain text" % (rel, index + 1))
                warned_setext = True

    first = raw_headings[0] if raw_headings else None
    dropped = False
    if first is not None and first[1] == 1:
        if rel == CONTEXT:
            dropped = True
        else:
            section_title = sanitize(section["title"])
            dropped = first[2] == section_title or first[2] == section["title"].strip()

    not_h1 = first is not None and first[1] != 1
    if not_h1:
        warn(
            "%s: first heading is not H1; source heading levels are offset by the section level"
            % rel
        )

    info = {
        "rel": rel,
        "lines": lines,
        "mask": mask,
        "headings": {},
        "anchors": {},
        "section_id": "sec-%d-1" % section["ordinal"],
        "title_id": None,
        "ref_labels": {},
        "blank_lines": set(),
    }

    slug_counts: dict = {}
    for position, (index, level, heading) in enumerate(raw_headings):
        is_first = position == 0
        if is_first and dropped:
            add_anchor(info["anchors"], heading, info["section_id"])
            info["headings"][index] = {
                "line": index,
                "source_level": level,
                "text": heading,
                "new_level": section_level,
                "id": None,
                "emitted": False,
            }
            continue

        if not_h1:
            new_level = section_level + level
        elif dropped:
            new_level = section_level + (level - 1) if level >= 2 else section_level + 1
        else:
            new_level = section_level + level
        if new_level > 6:
            warn("%s:%d: heading deeper than H6 clamped to H6" % (rel, index + 1))
            new_level = 6

        counter["n"] += 1
        heading_id = "sec-%d-%d" % (section["ordinal"], counter["n"])
        info["headings"][index] = {
            "line": index,
            "source_level": level,
            "text": heading,
            "new_level": new_level,
            "id": heading_id,
            "emitted": True,
        }
        if is_first and level == 1 and not dropped:
            info["title_id"] = heading_id

        base = slugify(heading)
        count = slug_counts.get(base, 0)
        slug_counts[base] = count + 1
        slug = base if count == 0 else "%s-%d" % (base, count)
        add_anchor(info["anchors"], heading, heading_id)
        for key in (slug, unquote(slug)):
            if key:
                info["anchors"].setdefault(key, heading_id)
                info["anchors"].setdefault(key.lower(), heading_id)
        info["anchors"].setdefault(heading_id, heading_id)

    info["ref_labels"], info["blank_lines"] = collect_remote_image_defs(text, lines, mask, rel)
    return info


def render_document(info: dict, docs: dict, project_root: str) -> str:
    out = []
    for index, line in enumerate(info["lines"]):
        heading = info["headings"].get(index)
        if heading is not None:
            if heading["emitted"]:
                out.append(
                    "%s %s {#%s}"
                    % ("#" * heading["new_level"], heading["text"], heading["id"])
                )
            else:
                out.append("")
            continue
        if index in info["blank_lines"]:
            out.append("")
            continue
        if info["mask"][index]:
            out.append(line)
            continue
        line = process_images(line, info, index + 1, project_root)
        line = process_reference_images(line, info["ref_labels"])
        line = process_links(line, info, docs, index + 1)
        out.append(line)
    return "\n".join(out).strip("\n")


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def section_has_content(section: dict) -> bool:
    return bool(section["documents"]) or any(
        section_has_content(child) for child in section["children"]
    )


def render_combined(plan: dict, docs: dict, project_root: str) -> str:
    meta = plan["meta"]
    version = meta["version"]
    date = meta["date"]

    lines = [
        "---",
        MARK,
        "title: " + yaml_scalar(meta["title"]),
        "subtitle: " + yaml_scalar("版本 %s · %s" % (version, date)),
    ]
    if meta["author"]:
        lines.append("author: " + yaml_scalar(meta["author"]))
    lines.append("---")

    # The abstract is a styled body paragraph, not pandoc metadata: a `lang`
    # key would make pandoc 3.9 look for missing zh translations (warnings on
    # every build), and without it pandoc prints an English "Abstract" label.
    # The CJK proofing language comes from reference.docx docDefaults instead.
    abstract_block = ""
    if meta["abstract"]:
        abstract_block = '::: {custom-style="Abstract"}\n%s\n:::' % meta["abstract"]

    blocks = [
        "\n".join(lines),
        COVER_MARK,
        abstract_block,
        PAGE_BREAK,
        TOC_HEADING,
        TOC_FIELD,
        PAGE_BREAK,
    ]
    state = {"first_top": True}

    def emit_section(section: dict) -> None:
        if not section_has_content(section):
            warn(
                "section %r resolves to no documents and no child sections; omitting it"
                % section["id"]
            )
            return
        if section["level"] == 1:
            if not state["first_top"]:
                blocks.append(PAGE_BREAK)
            state["first_top"] = False
        heading = "%s %s {#%s}" % (
            "#" * section["level"],
            sanitize(section["title"]),
            "sec-%d-1" % section["ordinal"],
        )
        documents = section["documents"]
        for index, rel in enumerate(documents):
            blocks.append(DOC_MARK_PREFIX + rel + DOC_MARK_SUFFIX)
            if index == 0:
                blocks.append(heading)
            blocks.append(render_document(docs[rel], docs, project_root))
        if not documents:
            blocks.append(heading)
        for child in section["children"]:
            emit_section(child)

    for section in plan["sections"]:
        emit_section(section)
    return "\n\n".join(block for block in blocks if block != "") + "\n"


def build_documents(project_root: str, plan: dict) -> dict:
    docs: dict = {}

    def walk(section: dict) -> None:
        if not section_has_content(section):
            return
        counter = {"n": 1}
        for rel in section["documents"]:
            docs[rel] = process_document(project_root, rel, section, counter)
        for child in section["children"]:
            walk(child)

    for section in plan["sections"]:
        walk(section)
    return docs


# --------------------------------------------------------------------------- #
# Workspace handling
# --------------------------------------------------------------------------- #


def is_marked(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return False
    if not lines:
        return False
    if lines[0].strip() == MARK:
        return True
    return lines[0].strip() == "---" and len(lines) > 1 and lines[1].strip() == MARK


def is_owned_json(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and data.get("generated_by") == GENERATED_BY


def preflight_outputs(workspace: str, outputs) -> None:
    if os.path.islink(workspace):
        raise TocError("docs/docsDocxView/ is a symlink")
    if os.path.lexists(workspace) and not os.path.isdir(workspace):
        raise TocError("docs/docsDocxView exists but is not a directory")
    if not os.path.isdir(workspace):
        return
    workspace_real = os.path.realpath(workspace)
    for rel in sorted(outputs):
        path = os.path.join(workspace, *rel.split("/"))
        if os.path.islink(path):
            raise TocError("output path is a symlink: " + path)
        real = os.path.realpath(path)
        if real != workspace_real and not real.startswith(workspace_real + os.sep):
            raise TocError("output escapes the workspace: " + path)
        if os.path.lexists(path):
            if rel.endswith(".json"):
                if not is_owned_json(path):
                    raise TocError("existing unowned JSON file: " + path)
            elif not is_marked(path):
                raise TocError("existing unmarked file: " + path)


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp-%d" % os.getpid()
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.lexists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def atomic_copy(src: str, dest: str) -> None:
    tmp = dest + ".tmp-%d" % os.getpid()
    try:
        shutil.copyfile(src, tmp)
        os.replace(tmp, dest)
    finally:
        if os.path.lexists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def seed_workspace(workspace: str) -> dict:
    """Seed missing reference.docx / build helpers; never overwrite."""
    statuses = {}
    for name in (REFERENCE_DOCX,) + BUILD_HELPERS:
        dest = os.path.join(workspace, name)
        if os.path.lexists(dest):
            if os.path.islink(dest) or not os.path.isfile(dest):
                warn("%s is a symlink or not a regular file; leaving it untouched" % dest)
                statuses[name] = "skipped"
            else:
                statuses[name] = "exists"
            continue
        asset = os.path.join(ASSETS_DIR, name)
        if not os.path.isfile(asset):
            warn("cannot read workspace asset %s" % asset)
            statuses[name] = "missing-asset"
            continue
        try:
            if name == REFERENCE_DOCX:
                atomic_copy(asset, dest)
            else:
                with open(asset, encoding="utf-8") as fh:
                    text = fh.read()
                newline = HELPER_NEWLINES[name]
                text = text.replace("\r\n", "\n").replace("\n", newline)
                tmp = dest + ".tmp-%d" % os.getpid()
                try:
                    with open(tmp, "w", encoding="utf-8", newline="") as fh:
                        fh.write(text)
                    os.replace(tmp, dest)
                finally:
                    if os.path.lexists(tmp):
                        os.remove(tmp)
        except OSError as exc:
            warn("cannot seed %s: %s" % (dest, exc))
            statuses[name] = "failed"
            continue
        if name == "build.sh" and os.name == "posix":
            os.chmod(dest, 0o755)
        statuses[name] = "created"
    return statuses


def generate(project_root: str) -> dict:
    root = os.path.abspath(project_root)
    docs_dir = os.path.join(root, "docs")
    if not os.path.isdir(docs_dir):
        raise TocError("no docs/ directory at " + root)
    if os.path.islink(docs_dir):
        raise TocError("docs/ is a symlink")

    plan = build_plan(root)
    documents = build_documents(root, plan)
    combined = render_combined(plan, documents, root)
    output = output_path(plan["meta"]["version"])

    outputs = {
        COMBINED_NAME: combined,
        MANIFEST_NAME: json.dumps(
            {"generated_by": GENERATED_BY, "documents": plan["documents"]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        META_NAME: json.dumps(
            {
                "generated_by": GENERATED_BY,
                "title": plan["meta"]["title"],
                "version": plan["meta"]["version"],
                "date": plan["meta"]["date"],
                "abstract": plan["meta"]["abstract"],
                "author": plan["meta"]["author"],
                "lang": "zh-CN",
                "output": output,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    }

    workspace = os.path.join(root, *WORKSPACE.split("/"))
    preflight_outputs(workspace, outputs)
    os.makedirs(workspace, exist_ok=True)
    for rel in sorted(outputs):
        atomic_write(os.path.join(workspace, *rel.split("/")), outputs[rel])
    seeded = seed_workspace(workspace)

    return {
        "plan": plan,
        "output": output,
        "written": sorted(outputs),
        "seeded": seeded,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Generate the Word publication input from docs/toc.yml "
            "(combined.md, _manifest.json, _meta.json, plus missing workspace assets). "
            "Missing reference.docx/build.sh/build.bat are seeded once; they are "
            "user-owned and never overwritten."
        )
    )
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument("--json", action="store_true", help="print a machine-readable summary")
    args = ap.parse_args()

    try:
        result = generate(args.project_root)
    except TocError as exc:
        sys.exit("refusing: %s" % exc)

    plan = result["plan"]
    if args.json:
        print(
            json.dumps(
                {
                    "documents": plan["documents"],
                    "output": result["output"],
                    "generated": [WORKSPACE + "/" + rel for rel in result["written"]],
                    "seeded": {
                        WORKSPACE + "/" + name: status
                        for name, status in sorted(result["seeded"].items())
                    },
                    "warnings": WARNINGS,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    seeded = [
        name for name, status in sorted(result["seeded"].items()) if status == "created"
    ]
    summary = "generated %d document(s) -> %s/%s" % (
        len(plan["documents"]),
        WORKSPACE,
        result["output"],
    )
    if seeded:
        summary += " (seeded: %s)" % ", ".join(seeded)
    print(summary)


if __name__ == "__main__":
    main()
