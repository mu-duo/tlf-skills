#!/usr/bin/env python3
"""Generate docs-html-view navigation under docs/docsHtmlView.

Writes only marked files inside the workspace: ``docsHtmlView/index.md`` and
``docsHtmlView/nav/**/index.md``. Never writes into source trees. Validates every
symlink and collision in a preflight pass *before* the first write or prune, so a
refusal leaves the tree unchanged. Removes only stale files carrying the marker.
Runs before ``make html``; it never invokes Sphinx itself.

Exit codes: 0 = generated (or nothing needed); 1 = refused, or no documents in
the approved trees (so a later ``make`` cannot silently build a stale site).
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys

MARK = "% docs-html-view: generated navigation; do not edit"
DEFAULT_ROOTS = ["pdr", "current", "adr"]
SUFFIXES = (".md", ".rst")
RESERVED = {"build", "docsHtmlView"}
BIG = float("inf")


def die(msg: str) -> None:
    sys.exit("refusing: " + msg)


def warn(msg: str) -> None:
    print("warning: " + msg, file=sys.stderr)


def sanitize(text: str) -> str:
    text = re.sub(r"[<>`{}\[\]|]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def display_name(name: str) -> str:
    name = re.sub(r"^\d+[-_. ]*", "", name).replace("-", " ").replace("_", " ").strip()
    return sanitize(name) or "section"


def num_key(name: str):
    match = re.match(r"^(\d+)", name)
    return (0, int(match.group(1))) if match else (1, 0)


def has_docs(path: str) -> bool:
    for _dirpath, _dirnames, filenames in os.walk(path, followlinks=False):
        if any(f.lower().endswith(SUFFIXES) for f in filenames):
            return True
    return False


def file_owned(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().lstrip().startswith(MARK)
    except OSError:
        die("cannot read " + path)


def read_config(workspace: str) -> dict:
    path = os.path.join(workspace, "docs-html-view.config.json")
    if not os.path.lexists(path):
        return {}
    if os.path.islink(path):
        die("config is a symlink: " + path)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        die("cannot parse config %s: %s" % (path, exc))
    if not isinstance(data, dict):
        die("config must be a JSON object: " + path)
    return data


def validate_dir_name(name: str) -> None:
    if not name or name in (".", ".."):
        die("invalid allowed_dirs entry: %r" % (name,))
    if "/" in name or "\\" in name:
        die("allowed_dirs entry must be one directory name, no separators: %r" % (name,))
    if name.startswith("."):
        die("allowed_dirs entry must not be hidden: %r" % (name,))
    if name in RESERVED:
        die("allowed_dirs entry may not be %r" % (name,))


def resolve_roots(cfg: dict, docs: str):
    allowed = cfg.get("allowed_dirs")
    if allowed is None:
        candidates = list(DEFAULT_ROOTS)
    else:
        if not isinstance(allowed, list):
            die("allowed_dirs must be a list of simple directory names")
        for name in allowed:
            if not isinstance(name, str):
                die("allowed_dirs entries must be strings")
            validate_dir_name(name)
        candidates = list(dict.fromkeys(allowed))

    present, missing = [], []
    for name in candidates:
        path = os.path.join(docs, name)
        if os.path.islink(path):
            die("approved dir is a symlink: " + path)
        if os.path.isdir(path) and has_docs(path):
            present.append(name)
        else:
            missing.append(name)
    return present, missing


def assert_no_symlinks(base: str, label: str) -> None:
    if not os.path.isdir(base):
        return
    for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
        for name in list(dirnames) + filenames:
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                die("symlink under %s: %s" % (label, path))


def toctree(entries, maxdepth=1) -> str:
    if not entries:
        return "<!-- (no documents) -->\n"
    lines = ["```{toctree}", ":maxdepth: %d" % maxdepth, ""] + list(entries) + ["```"]
    return "\n".join(lines) + "\n"


def build_outputs(docs, workspace, roots, order_map, site_title):
    outputs = {}

    def order_key(base_rel):
        def key(name):
            rel = posixpath.join(base_rel, name) if base_rel else name
            return (order_map.get(rel, BIG), num_key(name), name.casefold())
        return key

    def generate(source_root, rel_parts, src_dir):
        base_rel = posixpath.join(source_root, *rel_parts)
        out_rel = posixpath.join("docsHtmlView", "nav", source_root, *rel_parts)
        children = []
        for name in sorted(os.listdir(src_dir)):
            path = os.path.join(src_dir, name)
            if os.path.islink(path):
                die("symlink in source tree: " + path)
            if os.path.isdir(path):
                if has_docs(path):
                    children.append((name, "dir"))
            elif name.lower().endswith(SUFFIXES):
                children.append((name, "file"))
        children.sort(key=lambda item: order_key(base_rel)(item[0]))

        entries = []
        for name, kind in children:
            if kind == "dir":
                entries.append(posixpath.join(name, "index"))
            else:
                target = posixpath.join(source_root, *rel_parts, name)
                entries.append(posixpath.relpath(target, out_rel))

        title = display_name(rel_parts[-1]) if rel_parts else display_name(source_root)
        out_file = os.path.join(docs, *out_rel.split("/"), "index.md")
        outputs[out_file] = MARK + "\n\n# " + title + "\n\n" + toctree(entries)

        for name, kind in children:
            if kind == "dir":
                generate(source_root, list(rel_parts) + [name], os.path.join(src_dir, name))

    for source_root in roots:
        generate(source_root, [], os.path.join(docs, source_root))

    index_entries = [posixpath.join("nav", r, "index") for r in roots]
    outputs[os.path.join(workspace, "index.md")] = (
        MARK + "\n\n# " + site_title + "\n\n" + toctree(index_entries, maxdepth=2)
    )
    return outputs


def collision_preflight(outputs, nav_root) -> None:
    out_abs = {os.path.abspath(p) for p in outputs}
    for path in sorted(out_abs):
        if os.path.islink(path):
            die("symlinked output: " + path)
        if os.path.lexists(path) and not file_owned(path):
            die("existing unmarked file: " + path)
    if os.path.isdir(nav_root):
        for dirpath, _dirnames, filenames in os.walk(nav_root, followlinks=False):
            for name in filenames:
                path = os.path.abspath(os.path.join(dirpath, name))
                if path in out_abs:
                    continue
                if os.path.islink(path):
                    die("symlinked nav file: " + path)
                if not file_owned(path):
                    die("unmarked file under nav/: " + path)


def verify_inside(outputs, workspace) -> None:
    workspace_real = os.path.realpath(workspace)
    for path in outputs:
        real = os.path.realpath(path)
        if real != workspace_real and not real.startswith(workspace_real + os.sep):
            die("output escapes workspace: " + path)


def write_outputs(outputs) -> None:
    for path in sorted(outputs):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(outputs[path])


def prune(nav_root, outputs) -> None:
    out_abs = {os.path.abspath(p) for p in outputs}
    if not os.path.isdir(nav_root):
        return
    for dirpath, _dirnames, filenames in os.walk(nav_root, followlinks=False):
        for name in filenames:
            path = os.path.abspath(os.path.join(dirpath, name))
            if path not in out_abs and file_owned(path):
                os.remove(path)
    for dirpath, _dirs, _files in os.walk(nav_root, topdown=False):
        if dirpath == nav_root:
            continue
        try:
            os.rmdir(dirpath)  # only succeeds when empty
        except OSError:
            pass


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate docs-html-view navigation (marked files only).")
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument("--title", default=None, help="site title override")
    ap.add_argument("--json", action="store_true", help="print a machine-readable summary on stdout")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    docs = os.path.join(root, "docs")
    if not os.path.isdir(docs):
        die("no docs/ directory at " + root)
    if os.path.islink(docs):
        die("docs/ is a symlink")

    workspace = os.path.join(docs, "docsHtmlView")
    if not os.path.isdir(workspace):
        die("no docs/docsHtmlView workspace; run quickstart/setup first")
    if os.path.islink(workspace):
        die("docsHtmlView/ is a symlink")

    cfg = read_config(workspace)
    site_title_cfg = cfg.get("site_title")
    if site_title_cfg is not None and not isinstance(site_title_cfg, str):
        die("site_title must be a string")
    order = cfg.get("navigation_order")
    if order is None:
        order = []
    elif not isinstance(order, list) or not all(isinstance(x, str) for x in order):
        die("navigation_order must be a list of strings")
    order_map = {rel.strip("/"): i for i, rel in enumerate(order)}

    roots, missing = resolve_roots(cfg, docs)
    if missing:
        warn("missing/empty trees: " + ", ".join(missing))
    if not roots:
        print(
            "no documents in the approved trees; nothing to scaffold (run after adding docs)",
            file=sys.stderr,
        )
        sys.exit(1)

    for name in roots:
        assert_no_symlinks(os.path.join(docs, name), "source tree " + name)
    nav_root = os.path.join(workspace, "nav")
    if os.path.islink(nav_root):
        die("nav/ is a symlink")
    assert_no_symlinks(nav_root, "nav/")

    site_title = sanitize(str(site_title_cfg or args.title or "Documentation"))
    outputs = build_outputs(docs, workspace, roots, order_map, site_title)
    collision_preflight(outputs, nav_root)
    verify_inside(outputs, workspace)

    write_outputs(outputs)
    prune(nav_root, outputs)

    if args.json:
        print(
            json.dumps(
                {"roots": roots, "generated": sorted(os.path.relpath(p, root) for p in outputs)},
                indent=2,
            )
        )
    else:
        print("generated %d nav file(s) for roots: %s" % (len(outputs), ", ".join(roots)))


if __name__ == "__main__":
    main()
