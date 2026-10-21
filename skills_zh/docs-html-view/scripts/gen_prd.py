#!/usr/bin/env python3
"""Generate the docs-html-view PRD publication under ``docs/docsHtmlView``.

The single source of truth is ``docs/toc.yml``. It is validated, its globs and
``modules: auto`` entries are expanded, and only the listed documents are
published:

- ``docsHtmlView/index.md``         cover + top-level section toctrees
- ``docsHtmlView/nav/<id>/index.md`` section wrappers (nested for appendices)
- ``docsHtmlView/glossary.md``      generated from the root ``CONTEXT.md``
- ``docsHtmlView/_manifest.json``   exact include list (paths relative to docs/)
- ``docsHtmlView/_meta.json``       title/version/date/abstract/author

Generated Markdown files carry the ``% docs-html-view: ...`` marker (a MyST
comment that renders as nothing). Stale marked files are pruned; unmarked files
are never overwritten or deleted. Source documents are never written. The helper
runs before ``sphinx-build`` and never invokes Sphinx itself.

Exit codes: 0 = generated; 1 = refused (invalid TOC, unsafe output, no docs).
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import posixpath
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in a broken env
    sys.exit("error: PyYAML is required (install requirements.txt before running gen_prd.py)")

MARK = "% docs-html-view: generated navigation; do not edit"
GLOSSARY_MARK = "% docs-html-view: generated glossary; do not edit"
MANIFEST_NAME = "_manifest.json"
META_NAME = "_meta.json"
WORKSPACE = "docs/docsHtmlView"
CONTEXT = "CONTEXT.md"
GLOSSARY_DOCNAME = "docsHtmlView/glossary"
ALLOWED_ROOTS = ("docs/product", "docs/current", "docs/adr")
REQUIRED_SECTIONS = ("overview", "requirements", "architecture", "appendix")
REQUIRED_APPENDIX = ("glossary", "spec", "current", "adr")
DOC_SUFFIXES = (".md", ".rst")
SECTION_KEYS = {"id", "title", "documents", "sections", "modules", "exclude"}
TOP_KEYS = {"title", "version", "date", "abstract", "author", "sections"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class TocError(Exception):
    """A TOC or workspace problem that must stop the build."""


def warn(msg: str) -> None:
    print("warning: " + msg, file=sys.stderr)


def rel_posix(path: str, base: str) -> str:
    return os.path.relpath(path, base).replace(os.sep, "/")


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
    if raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
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

    if not documents and not child_sections and modules is None:
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


def manifest_entry(rel: str) -> str:
    if rel == CONTEXT:
        return "docsHtmlView/glossary.md"
    return rel[len("docs/"):] if rel.startswith("docs/") else rel


def docname(rel: str) -> str:
    if rel == CONTEXT:
        return GLOSSARY_DOCNAME
    if rel.startswith("docs/"):
        rel = rel[len("docs/") :]
    return posixpath.splitext(rel)[0]


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
    if author is not None:
        meta["author"] = scalar_text(author, "toc.yml author")
    else:
        meta["author"] = ""

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

    manifest = sorted({manifest_entry(rel) for rel in documents})
    wrappers = []
    for section in parsed:
        add_wrappers(wrappers, section, "docsHtmlView/nav")

    return {
        "meta": meta,
        "sections": parsed,
        "documents": documents,
        "manifest": manifest,
        "glossary": CONTEXT in documents,
        "wrappers": wrappers,
    }


def flatten_documents(section: dict) -> list:
    result = list(section["documents"])
    for child in section["children"]:
        result.extend(flatten_documents(child))
    return result


def add_wrappers(out: list, section: dict, parent_dir: str) -> None:
    out_dir = posixpath.join(parent_dir, section["id"])
    out.append(
        {
            "docname": posixpath.join(out_dir, "index"),
            "dir": out_dir,
            "title": section["title"],
            "documents": section["documents"],
            "children": section["children"],
        }
    )
    for child in section["children"]:
        add_wrappers(out, child, out_dir)


def toctree_entry(from_dir: str, target: str) -> str:
    return posixpath.relpath(target, from_dir)


def render_plan(plan: dict) -> dict:
    """Return {workspace-relative path: text} for every generated file."""
    meta = plan["meta"]
    title = sanitize(meta["title"])
    abstract = sanitize(meta["abstract"])
    version = sanitize(meta["version"])
    date = sanitize(meta["date"])

    index_dir = "docsHtmlView"
    outputs = {}

    index_entries = [toctree_entry(index_dir, wrapper["docname"]) for wrapper in top_wrappers(plan)]
    index_body = "%s\n\n# %s\n\n版本 %s · %s\n\n%s\n\n%s" % (
        MARK,
        title,
        version,
        date,
        abstract,
        toctree(index_entries),
    )
    outputs["index.md"] = index_body

    for wrapper in plan["wrappers"]:
        entries = [
            toctree_entry(wrapper["dir"], docname(rel)) for rel in wrapper["documents"]
        ]
        entries.extend(
            toctree_entry(wrapper["dir"], posixpath.join(wrapper["dir"], child["id"], "index"))
            for child in wrapper["children"]
        )
        out_rel = wrapper["docname"][len("docsHtmlView/") :] + ".md"
        outputs[out_rel] = "%s\n\n# %s\n\n%s" % (
            MARK,
            sanitize(wrapper["title"]),
            toctree(entries),
        )

    if plan["glossary"]:
        context_path = os.path.join(plan["project_root"], CONTEXT)
        try:
            with open(context_path, encoding="utf-8") as fh:
                body = fh.read()
        except OSError as exc:
            raise TocError("cannot read %s: %s" % (CONTEXT, exc))
        body = body.rstrip("\n") + "\n"
        outputs["glossary.md"] = "%s\n%% source: %s\n\n%s" % (
            GLOSSARY_MARK,
            CONTEXT,
            body,
        )

    outputs[MANIFEST_NAME] = json.dumps(
        {"generated_by": "docs-html-view gen_prd.py", "documents": plan["manifest"]},
        indent=2,
        ensure_ascii=False,
    ) + "\n"
    outputs[META_NAME] = json.dumps(
        {
            "generated_by": "docs-html-view gen_prd.py",
            "title": meta["title"],
            "version": meta["version"],
            "date": meta["date"],
            "abstract": meta["abstract"],
            "author": meta["author"],
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"
    return outputs


def top_wrappers(plan: dict) -> list:
    result = []
    for section in plan["sections"]:
        docname = posixpath.join("docsHtmlView/nav", section["id"], "index")
        result.append({"docname": docname, "id": section["id"]})
    return result


def toctree(entries) -> str:
    if not entries:
        return "```{toctree}\n:maxdepth: 1\n```\n"
    lines = ["```{toctree}", ":maxdepth: 1", ""] + list(entries) + ["```"]
    return "\n".join(lines) + "\n"


def is_marked(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().lstrip().startswith("% docs-html-view:")
    except (OSError, UnicodeDecodeError):
        return False


def is_owned_json(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and data.get("generated_by") == "docs-html-view gen_prd.py"


def preflight_outputs(outputs, workspace: str, nav_root: str) -> None:
    if os.path.islink(workspace):
        raise TocError("docsHtmlView/ is a symlink")
    if os.path.islink(nav_root):
        raise TocError("docsHtmlView/nav/ is a symlink")
    workspace_real = os.path.realpath(workspace)
    for rel in sorted(outputs):
        path = os.path.join(workspace, *rel.split("/"))
        parent = os.path.dirname(path)
        current = workspace
        for part in os.path.relpath(parent, workspace).split(os.sep):
            if part in ("", "."):
                continue
            current = os.path.join(current, part)
            if os.path.islink(current):
                raise TocError("output directory is a symlink: " + current)
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
    if os.path.isdir(nav_root):
        planned = {os.path.abspath(os.path.join(workspace, *rel.split("/"))) for rel in outputs}
        for dirpath, _dirnames, filenames in os.walk(nav_root, followlinks=False):
            for name in filenames:
                path = os.path.abspath(os.path.join(dirpath, name))
                if path in planned:
                    continue
                if os.path.islink(path):
                    raise TocError("symlinked nav file: " + path)
                if not is_marked(path):
                    raise TocError("unmarked file under nav/: " + path)


def write_outputs(workspace: str, outputs) -> list:
    written = []
    for rel in sorted(outputs):
        path = os.path.join(workspace, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(outputs[rel])
        written.append(rel)
    return written


def prune(workspace: str, nav_root: str, outputs) -> list:
    """Delete stale marked files; leave unmarked user files alone."""
    planned = {os.path.abspath(os.path.join(workspace, *rel.split("/"))) for rel in outputs}
    removed = []
    for dirpath, dirnames, filenames in os.walk(workspace, followlinks=False):
        dirnames[:] = [
            name
            for name in dirnames
            if not name.startswith(".venv")
            and name not in ("build", "__pycache__")
            and not os.path.islink(os.path.join(dirpath, name))
        ]
        for name in filenames:
            path = os.path.abspath(os.path.join(dirpath, name))
            if path in planned:
                continue
            if is_marked(path):
                os.remove(path)
                removed.append(rel_posix(path, workspace))
    workspace_abs = os.path.abspath(workspace)
    for dirpath, _dirnames, _filenames in os.walk(workspace, topdown=False):
        if os.path.abspath(dirpath) == workspace_abs:
            continue
        if os.path.basename(dirpath).startswith((".venv", "build")):
            continue
        try:
            os.rmdir(dirpath)
        except OSError:
            pass
    return removed


def check_legacy(project_root: str) -> None:
    legacy = os.path.join(project_root, "docs", "prd")
    if os.path.isdir(legacy) and not os.path.islink(legacy):
        warn(
            "legacy docs/prd/ detected; v5 publishes from docs/toc.yml. "
            "Migrate to docs/product/ (see project-docs-workflow migration)."
        )


def generate(project_root: str) -> dict:
    root = os.path.abspath(project_root)
    docs = os.path.join(root, "docs")
    if not os.path.isdir(docs):
        raise TocError("no docs/ directory at " + root)
    if os.path.islink(docs):
        raise TocError("docs/ is a symlink")
    workspace = os.path.join(root, *WORKSPACE.split("/"))
    if not os.path.isdir(workspace):
        raise TocError("no docs/docsHtmlView workspace; run setup first")
    check_legacy(root)
    plan = build_plan(root)
    plan["project_root"] = root
    outputs = render_plan(plan)
    nav_root = os.path.join(workspace, "nav")
    preflight_outputs(outputs, workspace, nav_root)
    written = write_outputs(workspace, outputs)
    removed = prune(workspace, nav_root, outputs)
    return {"plan": plan, "written": written, "removed": removed}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate the PRD publication from docs/toc.yml (marked files only)."
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
                    "title": plan["meta"]["title"],
                    "version": plan["meta"]["version"],
                    "documents": plan["documents"],
                    "manifest": plan["manifest"],
                    "glossary": plan["glossary"],
                    "generated": [WORKSPACE + "/" + rel for rel in result["written"]],
                    "pruned": [WORKSPACE + "/" + rel for rel in result["removed"]],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    print("generated %d file(s) for %d document(s)" % (len(result["written"]), len(plan["documents"])))
    print("cover: docs/docsHtmlView/index.md")
    print("manifest: %d entries" % len(plan["manifest"]))
    if result["removed"]:
        print("pruned %d stale marked file(s)" % len(result["removed"]))


if __name__ == "__main__":
    main()
