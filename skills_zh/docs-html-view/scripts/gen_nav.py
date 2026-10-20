#!/usr/bin/env python3
"""Generate docs-html-view navigation under docs/docsHtmlView.

Writes only marked files inside the workspace. The ``full`` profile writes
``docsHtmlView/index.md`` and ``docsHtmlView/nav/**/index.md``; the ``l1`` profile
writes ``docsHtmlView/l1/index.md`` for the L1 layer (product + module
``00-README.md`` only). Never writes into source trees. Validates every symlink
and collision in a preflight pass *before* the first write or prune, so a refusal
leaves the tree unchanged. Removes only stale files carrying the marker. Runs
before ``make html``; it never invokes Sphinx itself.

Exit codes: 0 = generated (or nothing needed); 1 = refused, or no documents in
the approved trees / L1 roots (so a later ``make`` cannot silently build a stale
site).
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys

MARK = "% docs-html-view: generated navigation; do not edit"
DEFAULT_ROOTS = ["prd", "current", "adr"]
DEFAULT_L1_ROOTS = ["prd"]
LEGACY_ROOTS = {"pdr": "prd"}
SUFFIXES = (".md", ".rst")
L1_FILE = "00-README.md"
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
    return present, missing, candidates


def validate_rel_path(value, label: str) -> str:
    if not isinstance(value, str):
        die(label + " must be a string")
    raw = value.strip()
    if not raw:
        die(label + " must not be empty")
    if "\\" in raw:
        die(label + " must use forward slashes: %r" % (value,))
    if raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        die(label + " must be relative to docs/: %r" % (value,))
    norm = posixpath.normpath(raw)
    if norm in (".", "..") or norm.startswith("../"):
        die(label + " must stay inside docs/: %r" % (value,))
    parts = norm.split("/")
    if any(part in ("", ".", "..") for part in parts):
        die(label + " must stay inside docs/: %r" % (value,))
    return norm


def resolve_landing_page(cfg: dict, docs: str, roots):
    raw = cfg.get("landing_page")
    if raw is None:
        return None
    rel = validate_rel_path(raw, "landing_page")
    target = os.path.join(docs, *rel.split("/"))
    if os.path.islink(target):
        die("landing_page must not be a symlink: " + target)
    if not os.path.isfile(target):
        die("landing_page is not an existing regular file: " + target)
    real = os.path.realpath(target)
    for name in roots:
        root_real = os.path.realpath(os.path.join(docs, name))
        try:
            if os.path.commonpath([real, root_real]) == root_real:
                return rel, target
        except ValueError:
            continue
    die("landing_page is outside the approved roots: " + target)


def heading_title(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        die("cannot read landing_page %s: %s" % (path, exc))
    lines = text.splitlines()
    for line in lines:
        match = re.match(r"^\s{0,3}#\s+(.*?)\s*#*\s*$", line)
        if match:
            return sanitize(match.group(1))
    for index, line in enumerate(lines[:-1]):
        underline = lines[index + 1].strip()
        if line.strip() and underline and len(set(underline)) == 1 and underline[0] in "=-":
            return sanitize(line.strip())
    return ""


def landing_label(cfg: dict, landing) -> str:
    rel, path = landing
    configured = cfg.get("landing_page_label")
    if configured is not None:
        if not isinstance(configured, str):
            die("landing_page_label must be a string")
        label = sanitize(configured)
        if label:
            return label
    label = heading_title(path)
    if label:
        return label
    return sanitize(posixpath.splitext(posixpath.basename(rel))[0]) or "L1"


def resolve_l1_roots(cfg: dict, candidates) -> list:
    raw = cfg.get("l1_roots")
    if raw is None:
        return [name for name in DEFAULT_L1_ROOTS if name in candidates]
    if not isinstance(raw, list):
        die("l1_roots must be a list of approved root names")
    l1_roots = []
    for name in raw:
        if not isinstance(name, str):
            die("l1_roots entries must be strings")
        validate_dir_name(name)
        if name not in candidates:
            die("l1_roots entry is not an approved root: %r" % (name,))
        if name not in l1_roots:
            l1_roots.append(name)
    return l1_roots


def l1_documents(docs: str, roots) -> list:
    found = []
    for name in roots:
        base = os.path.join(docs, name)
        for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
            dirnames.sort()
            for filename in sorted(filenames):
                if filename != L1_FILE:
                    continue
                path = os.path.join(dirpath, filename)
                if os.path.islink(path):
                    warn("skipping symlinked L1 file: " + path)
                    continue
                if not os.path.isfile(path):
                    continue
                found.append(os.path.relpath(path, docs).replace(os.sep, "/"))
    return found


def l1_sort_key(rel: str, order_map: dict):
    return (
        order_map.get(rel, BIG),
        tuple(num_key(part) for part in rel.split("/")),
        rel.casefold(),
    )


def warn_legacy_roots(cfg: dict, docs: str, roots) -> None:
    allowed = cfg.get("allowed_dirs")
    explicitly_allowed = allowed if isinstance(allowed, list) else []
    for legacy, replacement in LEGACY_ROOTS.items():
        path = os.path.join(docs, legacy)
        if not os.path.isdir(path) or not has_docs(path):
            continue
        if legacy in roots or legacy in explicitly_allowed:
            continue
        warn(
            "legacy docs/%s/ detected; not rendered. Migrate to docs/%s/ or add \"%s\" to allowed_dirs explicitly."
            % (legacy, replacement, legacy)
        )


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


def build_outputs(docs, workspace, roots, order_map, site_title, landing_block=""):
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
    landing = landing_block + "\n" if landing_block else ""
    outputs[os.path.join(workspace, "index.md")] = (
        MARK + "\n\n# " + site_title + "\n\n" + landing + toctree(index_entries, maxdepth=2)
    )
    return outputs


def build_l1_output(docs, l1_files, site_title):
    out_rel = posixpath.join("docsHtmlView", "l1", "index.md")
    out_file = os.path.join(docs, *out_rel.split("/"))
    entries = []
    for rel in l1_files:
        target = rel[:-3] if rel.endswith(".md") else rel
        entries.append(posixpath.relpath(target, "docsHtmlView/l1"))
    body = MARK + "\n\n# " + site_title + " · L1\n\n" + toctree(entries, maxdepth=1)
    return {out_file: body}


def collision_preflight(outputs, owned_root, label="nav/") -> None:
    out_abs = {os.path.abspath(p) for p in outputs}
    for path in sorted(out_abs):
        if os.path.islink(path):
            die("symlinked output: " + path)
        if os.path.lexists(path) and not file_owned(path):
            die("existing unmarked file: " + path)
    if os.path.isdir(owned_root):
        for dirpath, _dirnames, filenames in os.walk(owned_root, followlinks=False):
            for name in filenames:
                path = os.path.abspath(os.path.join(dirpath, name))
                if path in out_abs:
                    continue
                if os.path.islink(path):
                    die("symlinked " + label + " file: " + path)
                if not file_owned(path):
                    die("unmarked file under " + label + ": " + path)


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
    ap.add_argument(
        "--profile",
        choices=("full", "l1"),
        default="full",
        help="full = prd/current/adr site navigation (default); l1 = L1 00-README.md view",
    )
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

    for key in ("landing_page", "landing_page_label"):
        value = cfg.get(key)
        if value is not None and not isinstance(value, str):
            die(key + " must be a string")

    roots, missing, candidates = resolve_roots(cfg, docs)
    l1_roots = resolve_l1_roots(cfg, candidates)
    if missing:
        warn("missing/empty trees: " + ", ".join(missing))
    warn_legacy_roots(cfg, docs, roots)
    if not roots:
        print(
            "no documents in the approved trees; nothing to scaffold (run after adding docs)",
            file=sys.stderr,
        )
        sys.exit(1)

    for name in roots:
        assert_no_symlinks(os.path.join(docs, name), "source tree " + name)

    if args.profile == "l1" and "prd" in l1_roots and "prd" in roots:
        product_l1 = os.path.join(docs, "prd", L1_FILE)
        if os.path.islink(product_l1) or not os.path.isfile(product_l1):
            print(
                "l1 profile requires the product L1 docs/prd/%s; module L1 files "
                "alone are not enough" % L1_FILE,
                file=sys.stderr,
            )
            sys.exit(1)

    site_title = sanitize(str(site_title_cfg or args.title or "Documentation"))
    landing = resolve_landing_page(cfg, docs, roots)

    if args.profile == "l1":
        if not l1_roots:
            die("l1 profile requires a non-empty l1_roots; allow \"prd\" or set l1_roots in the config")
        active = [name for name in l1_roots if name in roots]
        if not active:
            print(
                "no L1 documents (%s) in l1_roots: %s; nothing to generate"
                % (L1_FILE, ", ".join(l1_roots)),
                file=sys.stderr,
            )
            sys.exit(1)
        l1_files = l1_documents(docs, active)
        if not l1_files:
            print(
                "no L1 documents (%s) under: %s; nothing to generate"
                % (L1_FILE, ", ".join(active)),
                file=sys.stderr,
            )
            sys.exit(1)
        l1_files.sort(key=lambda rel: l1_sort_key(rel, order_map))

        l1_root = os.path.join(workspace, "l1")
        if os.path.islink(l1_root):
            die("l1/ is a symlink")
        assert_no_symlinks(l1_root, "l1/")

        outputs = build_l1_output(docs, l1_files, site_title)
        collision_preflight(outputs, l1_root, "l1/")
        verify_inside(outputs, workspace)

        write_outputs(outputs)
        prune(l1_root, outputs)

        if args.json:
            print(
                json.dumps(
                    {
                        "profile": "l1",
                        "roots": active,
                        "generated": sorted(os.path.relpath(p, root) for p in outputs),
                    },
                    indent=2,
                )
            )
        else:
            print("generated %d L1 nav file(s) for roots: %s" % (len(outputs), ", ".join(active)))
        return

    landing_block = ""
    if landing is not None:
        label = landing_label(cfg, landing)
        landing_block = "## %s\n\n[%s](../%s)\n" % (label, label, landing[0])

    nav_root = os.path.join(workspace, "nav")
    if os.path.islink(nav_root):
        die("nav/ is a symlink")
    assert_no_symlinks(nav_root, "nav/")

    outputs = build_outputs(docs, workspace, roots, order_map, site_title, landing_block)
    collision_preflight(outputs, nav_root)
    verify_inside(outputs, workspace)

    write_outputs(outputs)
    prune(nav_root, outputs)

    if args.json:
        print(
            json.dumps(
                {
                    "profile": "full",
                    "roots": roots,
                    "generated": sorted(os.path.relpath(p, root) for p in outputs),
                },
                indent=2,
            )
        )
    else:
        print("generated %d nav file(s) for roots: %s" % (len(outputs), ", ".join(roots)))


if __name__ == "__main__":
    main()
