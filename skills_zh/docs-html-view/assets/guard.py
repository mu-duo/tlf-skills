"""docs-html-view guard: a best-effort parse/render guard for trusted project docs.

This is a trusted-document renderer, not a universal sandbox. It blocks
file-insertion directives, refuses active/raw HTML (allowing only HTML comments),
and checks local image/download references against the approved roots at
``doctree-read`` (before Sphinx's asset collectors copy anything). Remote
images/downloads are never fetched. Leading ``模板来源`` (template-origin)
provenance markers are stripped from published copies at ``source-read`` and
from Sphinx's copied ``_sources`` files at ``build-finished``; the source files
on disk are never modified. At ``build-finished`` a deterministic root entry
page (``build/html/index.html``) is also written for HTML builds only,
redirecting to the publication cover. The project's own ``conf.py`` remains
executable Python.
"""
from __future__ import annotations

import html
import os
import re
from urllib.parse import urlparse

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.errors import SphinxError
from sphinx.util import logging

logger = logging.getLogger(__name__)

BLOCKED = ("include", "literalinclude", "raw")
# A raw node is allowed only when it is entirely HTML comment(s) and whitespace.
# This permits the harmless `<!-- ... -->` comments used in the PRD templates while
# still refusing any active markup (no comment+script smuggling).
_COMMENT_ONLY = re.compile(r"\s*(?:<!--.*?-->\s*)*", re.DOTALL)

_PROVENANCE = re.compile(
    r"\A\ufeff?(?:[ \t]*\r?\n)*"
    r"(?:[ \t]*>[ \t]*模板来源[^\n]*(?:\r?\n[ \t]*>[^\n]*)*"
    r"|[ \t]*<!--[ \t]*模板来源.*?-->)[ \t]*(?:\r?\n)+",
    re.DOTALL,
)


def strip_provenance(text: str) -> str:
    """Remove leading template-origin markers; never touch body occurrences."""
    while True:
        stripped = _PROVENANCE.sub("", text, count=1)
        if stripped == text:
            return text
        text = stripped


class _Blocked(Directive):
    has_content = True
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        raise SphinxError("docs-html-view: '%s' directive is not allowed" % self.name)


def _block_directives(app):
    # Registered after extensions load; docutils lowercases names, so this also
    # catches INCLUDE and directives reached through eval-rst or colon fences.
    for name in BLOCKED:
        directives.register_directive(name, _Blocked)


def _validate_roots(app):
    """Every allowed root must be a simple relative name that resolves inside docs."""
    srcdir_real = os.path.realpath(app.srcdir)
    for name in app.config.docs_html_view_allowed_roots:
        if not isinstance(name, str) or not name or os.path.isabs(name) or "\\" in name:
            raise SphinxError("docs-html-view: invalid allowed root %r" % (name,))
        parts = name.split("/")
        if any(part in ("", ".", "..") for part in parts):
            raise SphinxError("docs-html-view: allowed root must be a simple relative name: %r" % (name,))
        root_real = os.path.realpath(os.path.join(app.srcdir, name))
        try:
            inside = os.path.commonpath([root_real, srcdir_real]) == srcdir_real
        except ValueError:
            inside = False
        if not inside:
            raise SphinxError("docs-html-view: allowed root escapes docs: %r" % (name,))


def _remote(uri: str) -> bool:
    return bool(urlparse(uri).scheme) or uri.startswith("//")


def _within(path: str, roots) -> bool:
    real = os.path.realpath(path)
    for root in roots:
        root_real = os.path.realpath(root)
        try:
            if os.path.commonpath([real, root_real]) == root_real:
                return True
        except ValueError:
            continue
    return False


def _guard_assets(app, doctree):
    docname = app.env.docname
    roots = [os.path.join(app.srcdir, r) for r in app.config.docs_html_view_allowed_roots]

    for node in doctree.findall(nodes.raw):
        if not _COMMENT_ONLY.fullmatch(node.astext() or ""):
            raise SphinxError("docs-html-view: active/raw HTML is not allowed in %s" % docname)

    def check(uri, kind):
        """True if usable locally, False if remote; raises when local-but-outside."""
        if not uri:
            return True
        if _remote(uri):
            return False
        clean = uri.split("#", 1)[0]
        try:
            _rel, abspath = app.env.relfn2path(clean, docname)
        except Exception:
            abspath = None
        if abspath is None or not _within(abspath, roots):
            raise SphinxError(
                "docs-html-view: %s outside approved roots in %s: %s" % (kind, docname, uri)
            )
        return True

    for node in doctree.findall(nodes.image):
        uri = node.get("uri", "")
        if check(uri, "image"):
            continue
        logger.warning("docs-html-view: remote image not fetched: %s", uri, location=docname)
        node.replace_self(nodes.emphasis("", "[remote image not fetched] " + uri))

    for node in doctree.findall(addnodes.download_reference):
        uri = node.get("reftarget") or node.get("refuri") or ""
        if check(uri, "download"):
            continue
        logger.warning("docs-html-view: remote download not fetched: %s", uri, location=docname)
        node.replace_self(nodes.emphasis("", "[remote download not fetched] " + uri))


def _strip_source_provenance(app, docname, source):
    """Drop template-origin markers from the in-memory source only (never the file)."""
    source[0] = strip_provenance(source[0])


def _clean_copied_sources(app, exception):
    """Strip provenance from Sphinx's ``_sources`` copies as well."""
    if exception is not None or app.builder.name != "html":
        return
    sources_dir = os.path.join(app.outdir, "_sources")
    if not os.path.isdir(sources_dir):
        return
    for dirpath, _dirnames, filenames in os.walk(sources_dir, followlinks=False):
        for name in filenames:
            if not (name.endswith(".md.txt") or name.endswith(".rst.txt")):
                continue
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            cleaned = strip_provenance(text)
            if cleaned == text:
                continue
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(cleaned)


def _write_root_entry(app, exception):
    """Write a deterministic ``index.html`` entry pointing at the cover."""
    if exception is not None or app.builder.name != "html":
        return
    target = "docsHtmlView/index.html"
    title = html.escape(app.config.project or "Documentation")
    page = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta http-equiv="refresh" content="0; url=%s">\n'
        "<title>%s</title>\n"
        "</head>\n"
        "<body>\n"
        '<p><a href="%s">%s</a></p>\n'
        "</body>\n"
        "</html>\n"
    ) % (target, title, target, title)
    outpath = os.path.join(app.outdir, "index.html")
    with open(outpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)


def setup(app):
    app.add_config_value("docs_html_view_allowed_roots", [], "env")
    app.connect("builder-inited", _block_directives)
    app.connect("builder-inited", _validate_roots)
    app.connect("source-read", _strip_source_provenance)
    # doctree-read (priority 100) so we run before Sphinx's asset collectors (500),
    # which copy downloads during read and register images for copy.
    app.connect("doctree-read", _guard_assets, priority=100)
    app.connect("build-finished", _clean_copied_sources)
    app.connect("build-finished", _write_root_entry)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
