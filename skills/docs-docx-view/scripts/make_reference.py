#!/usr/bin/env python3
"""Build the docs-docx-view Word reference template (maintenance only).

This script is **not** part of the publication flow.  It derives a
``reference.docx`` from pandoc's own default reference document
(``pandoc --print-default-data-file reference.docx``, pandoc 3.9) and applies
the house style used by the docs-docx-view skill:

* Calibri / 宋体 body fonts, Calibri Light / 黑体 headings (1-4),
  title block, abstract, TOC heading, body text, table and code styles;
* ``w:updateFields`` so TOC/PAGE fields refresh on open;
* a right-aligned ``DOCPROPERTY "title"`` header and a
  ``第 PAGE 页 / 共 NUMPAGES 页`` footer;
* a single A4 section with 2.54 cm margins referencing those parts.

The output zip is written deterministically (fixed entry order, fixed
1980-01-01 timestamps) and every part that is not deliberately edited is
copied through unchanged.  Only the Python standard library is used.

Usage::

    python3 scripts/make_reference.py [--pandoc PATH] [--output PATH]

``--pandoc`` defaults to ``pypandoc.get_pandoc_path()`` and then to a
``pandoc`` executable on ``PATH``.  ``--output`` defaults to
``<skill>/assets/reference.docx``.
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W = "{%s}" % W_NS

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = SKILL_ROOT / "assets" / "reference.docx"

STYLE_IDS = [
    "Normal",
    "BodyText",
    "FirstParagraph",
    "Compact",
    "Title",
    "TitleChar",
    "Subtitle",
    "SubtitleChar",
    "Author",
    "Date",
    "AbstractTitle",
    "Abstract",
    "Bibliography",
    "Heading1",
    "Heading2",
    "Heading3",
    "Heading4",
    "Heading5",
    "Heading6",
    "Heading7",
    "Heading8",
    "Heading9",
    "Heading1Char",
    "Heading2Char",
    "Heading3Char",
    "Heading4Char",
    "Heading5Char",
    "Heading6Char",
    "Heading7Char",
    "Heading8Char",
    "Heading9Char",
    "BlockText",
    "FootnoteText",
    "FootnoteBlockText",
    "DefaultParagraphFont",
    "Table",
    "DefinitionTerm",
    "Definition",
    "Caption",
    "TableCaption",
    "ImageCaption",
    "Figure",
    "CaptionedFigure",
    "BodyTextChar",
    "VerbatimChar",
    "SourceCode",
    "SectionNumber",
    "FootnoteReference",
    "Hyperlink",
    "TOCHeading",
    "Header",
    "Footer",
]

# ---------------------------------------------------------------------------
# Style definitions (string templates; the source parts are edited textually so
# untouched parts of styles.xml survive byte-for-byte).
# ---------------------------------------------------------------------------


def _para(
    sid: str,
    name: str,
    *,
    based: str,
    next_: str | None = None,
    link: str | None = None,
    custom: bool = False,
    ui_priority: int | None = None,
    qformat: bool = True,
    ppr: str = "",
    rpr: str = "",
) -> str:
    attrs = ' w:type="paragraph"'
    if custom:
        attrs += ' w:customStyle="1"'
    attrs += ' w:styleId="%s"' % sid
    out = ['  <w:style%s>' % attrs]
    out.append('    <w:name w:val="%s" />' % name)
    out.append('    <w:basedOn w:val="%s" />' % based)
    if next_:
        out.append('    <w:next w:val="%s" />' % next_)
    if link:
        out.append('    <w:link w:val="%s" />' % link)
    if ui_priority is not None:
        out.append('    <w:uiPriority w:val="%d" />' % ui_priority)
    if qformat:
        out.append("    <w:qFormat />")
    if ppr:
        out.append("    <w:pPr>")
        out.extend("      " + line for line in ppr.splitlines())
        out.append("    </w:pPr>")
    if rpr:
        out.append("    <w:rPr>")
        out.extend("      " + line for line in rpr.splitlines())
        out.append("    </w:rPr>")
    out.append("  </w:style>")
    return "\n".join(out)


def _char(
    sid: str,
    name: str,
    *,
    based: str,
    link: str | None = None,
    ui_priority: int | None = None,
    rpr: str = "",
) -> str:
    out = [
        '  <w:style w:type="character" w:customStyle="1" w:styleId="%s">' % sid,
        '    <w:name w:val="%s" />' % name,
        '    <w:basedOn w:val="%s" />' % based,
    ]
    if link:
        out.append('    <w:link w:val="%s" />' % link)
    if ui_priority is not None:
        out.append('    <w:uiPriority w:val="%d" />' % ui_priority)
    if rpr:
        out.append("    <w:rPr>")
        out.extend("      " + line for line in rpr.splitlines())
        out.append("    </w:rPr>")
    out.append("  </w:style>")
    return "\n".join(out)


def _fonts(ascii_: str, eastasia: str, cs: str | None = None) -> str:
    cs = cs or ascii_
    return (
        '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:eastAsia="%s" w:cs="%s" />'
        % (ascii_, ascii_, eastasia, cs)
    )


DOC_DEFAULTS = """  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="宋体" w:cs="Calibri" />
        <w:sz w:val="24" />
        <w:szCs w:val="24" />
        <w:lang w:val="en-US" w:eastAsia="zh-CN" w:bidi="ar-SA" />
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="160" w:line="360" w:lineRule="auto" />
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>"""


def build_style_blocks() -> dict[str, str]:
    heading_rpr = {
        1: _fonts("Calibri Light", "黑体")
        + "\n<w:color w:val=\"1F3864\" />\n<w:sz w:val=\"36\" />\n<w:szCs w:val=\"36\" />",
        2: _fonts("Calibri Light", "黑体")
        + "\n<w:color w:val=\"2E5496\" />\n<w:sz w:val=\"30\" />\n<w:szCs w:val=\"30\" />",
        3: _fonts("Calibri Light", "黑体")
        + "\n<w:color w:val=\"1F4E79\" />\n<w:sz w:val=\"26\" />\n<w:szCs w:val=\"26\" />",
        4: _fonts("Calibri Light", "黑体")
        + "\n<w:color w:val=\"404040\" />\n<w:sz w:val=\"24\" />\n<w:szCs w:val=\"24\" />",
    }
    heading_ppr = {
        1: "<w:keepNext />\n<w:keepLines />\n<w:spacing w:before=\"360\" w:after=\"160\" w:line=\"240\" w:lineRule=\"auto\" />\n<w:outlineLvl w:val=\"0\" />",
        2: "<w:keepNext />\n<w:keepLines />\n<w:spacing w:before=\"300\" w:after=\"120\" w:line=\"240\" w:lineRule=\"auto\" />\n<w:outlineLvl w:val=\"1\" />",
        3: "<w:keepNext />\n<w:keepLines />\n<w:spacing w:before=\"240\" w:after=\"100\" w:line=\"240\" w:lineRule=\"auto\" />\n<w:outlineLvl w:val=\"2\" />",
        4: "<w:keepNext />\n<w:keepLines />\n<w:spacing w:before=\"200\" w:after=\"80\" w:line=\"240\" w:lineRule=\"auto\" />\n<w:outlineLvl w:val=\"3\" />",
    }

    blocks: dict[str, str] = {}

    blocks["BodyText"] = _para(
        "BodyText",
        "Body Text",
        based="Normal",
        link="BodyTextChar",
        ppr='<w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto" />',
    )
    blocks["FirstParagraph"] = _para(
        "FirstParagraph",
        "First Paragraph",
        based="BodyText",
        next_="BodyText",
        custom=True,
        ppr='<w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto" />',
    )
    blocks["Title"] = _para(
        "Title",
        "Title",
        based="Normal",
        next_="BodyText",
        link="TitleChar",
        ui_priority=10,
        ppr=(
            '<w:keepNext />\n<w:keepLines />\n'
            '<w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto" />\n'
            '<w:jc w:val="center" />'
        ),
        rpr=_fonts("Calibri Light", "黑体")
        + '\n<w:color w:val="1F3864" />\n<w:sz w:val="52" />\n<w:szCs w:val="52" />',
    )
    blocks["TitleChar"] = _char(
        "TitleChar",
        "Title Char",
        based="DefaultParagraphFont",
        link="Title",
        ui_priority=10,
        rpr=_fonts("Calibri Light", "黑体")
        + '\n<w:color w:val="1F3864" />\n<w:sz w:val="52" />\n<w:szCs w:val="52" />',
    )
    blocks["Subtitle"] = _para(
        "Subtitle",
        "Subtitle",
        based="Normal",
        next_="BodyText",
        link="SubtitleChar",
        ui_priority=11,
        ppr=(
            '<w:keepNext />\n<w:keepLines />\n'
            '<w:spacing w:before="0" w:after="240" w:line="240" w:lineRule="auto" />\n'
            '<w:jc w:val="center" />'
        ),
        rpr=_fonts("Calibri Light", "黑体")
        + '\n<w:color w:val="595959" />\n<w:sz w:val="28" />\n<w:szCs w:val="28" />',
    )
    blocks["SubtitleChar"] = _char(
        "SubtitleChar",
        "Subtitle Char",
        based="DefaultParagraphFont",
        link="Subtitle",
        ui_priority=11,
        rpr=_fonts("Calibri Light", "黑体")
        + '\n<w:color w:val="595959" />\n<w:sz w:val="28" />\n<w:szCs w:val="28" />',
    )
    blocks["Author"] = _para(
        "Author",
        "Author",
        based="Normal",
        next_="BodyText",
        custom=True,
        ppr=(
            '<w:keepNext />\n<w:keepLines />\n'
            '<w:spacing w:before="0" w:after="60" />\n'
            '<w:jc w:val="center" />'
        ),
        rpr=_fonts("Calibri", "宋体")
        + '\n<w:color w:val="404040" />\n<w:sz w:val="24" />\n<w:szCs w:val="24" />',
    )
    blocks["AbstractTitle"] = _para(
        "AbstractTitle",
        "Abstract Title",
        based="Normal",
        next_="Abstract",
        custom=True,
        ppr=(
            '<w:keepNext />\n<w:keepLines />\n'
            '<w:spacing w:before="240" w:after="100" />\n'
            '<w:jc w:val="center" />'
        ),
        rpr=_fonts("Calibri Light", "黑体")
        + '\n<w:b />\n<w:color w:val="1F3864" />\n<w:sz w:val="22" />\n<w:szCs w:val="22" />',
    )
    blocks["Abstract"] = _para(
        "Abstract",
        "Abstract",
        based="Normal",
        next_="BodyText",
        custom=True,
        ppr=(
            '<w:keepNext />\n<w:keepLines />\n'
            '<w:spacing w:before="120" w:after="240" w:line="320" w:lineRule="auto" />\n'
            '<w:ind w:left="420" w:right="420" />'
        ),
        rpr=_fonts("Calibri", "宋体")
        + '\n<w:color w:val="404040" />\n<w:sz w:val="21" />\n<w:szCs w:val="21" />',
    )

    for level in range(1, 5):
        blocks["Heading%d" % level] = _para(
            "Heading%d" % level,
            "heading %d" % level,
            based="Normal",
            next_="BodyText",
            link="Heading%dChar" % level,
            ui_priority=9,
            ppr=heading_ppr[level],
            rpr=heading_rpr[level],
        )
        blocks["Heading%dChar" % level] = _char(
            "Heading%dChar" % level,
            "Heading %d Char" % level,
            based="DefaultParagraphFont",
            link="Heading%d" % level,
            ui_priority=9,
            rpr=heading_rpr[level],
        )

    blocks["Table"] = """  <w:style w:type="table" w:default="1" w:styleId="Table">
    <w:name w:val="Table" />
    <w:basedOn w:val="TableNormal" />
    <w:uiPriority w:val="59" />
    <w:qFormat />
    <w:tblPr>
      <w:tblBorders>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="BFBFBF" />
        <w:left w:val="single" w:sz="4" w:space="0" w:color="BFBFBF" />
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="BFBFBF" />
        <w:right w:val="single" w:sz="4" w:space="0" w:color="BFBFBF" />
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D9D9D9" />
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="D9D9D9" />
      </w:tblBorders>
      <w:tblCellMar>
        <w:top w:w="60" w:type="dxa" />
        <w:left w:w="108" w:type="dxa" />
        <w:bottom w:w="60" w:type="dxa" />
        <w:right w:w="108" w:type="dxa" />
      </w:tblCellMar>
    </w:tblPr>
    <w:tblStylePr w:type="firstRow">
      <w:pPr>
        <w:spacing w:before="0" w:after="0" />
      </w:pPr>
      <w:rPr>
        <w:b />
        <w:color w:val="1F3864" />
      </w:rPr>
      <w:tcPr>
        <w:shd w:val="clear" w:color="auto" w:fill="EAF1FB" />
        <w:tcBorders>
          <w:bottom w:val="single" w:sz="8" w:space="0" w:color="2E5496" />
        </w:tcBorders>
        <w:vAlign w:val="center" />
      </w:tcPr>
    </w:tblStylePr>
    <w:tblStylePr w:type="band1Horz">
      <w:tcPr>
        <w:shd w:val="clear" w:color="auto" w:fill="F7F9FC" />
      </w:tcPr>
    </w:tblStylePr>
  </w:style>"""
    blocks["SourceCode"] = _para(
        "SourceCode",
        "Source Code",
        based="Normal",
        link="VerbatimChar",
        custom=True,
        ppr=(
            '<w:wordWrap w:val="off" />\n'
            '<w:spacing w:before="80" w:after="80" w:line="240" w:lineRule="auto" />\n'
            '<w:shd w:val="clear" w:color="auto" w:fill="F5F5F5" />\n'
            '<w:ind w:left="120" w:right="120" />'
        ),
    )
    blocks["VerbatimChar"] = _char(
        "VerbatimChar",
        "Verbatim Char",
        based="BodyTextChar",
        rpr=_fonts("Consolas", "宋体")
        + '\n<w:color w:val="24292E" />\n<w:sz w:val="20" />\n<w:szCs w:val="20" />',
    )
    blocks["TOCHeading"] = _para(
        "TOCHeading",
        "TOC Heading",
        based="Normal",
        next_="BodyText",
        ui_priority=39,
        ppr=(
            '<w:keepNext />\n<w:keepLines />\n'
            '<w:spacing w:before="240" w:after="240" />\n'
            '<w:outlineLvl w:val="9" />'
        ),
        rpr=_fonts("Calibri Light", "黑体")
        + '\n<w:b w:val="0" />\n<w:bCs w:val="0" />\n'
        '<w:color w:val="1F3864" />\n<w:sz w:val="32" />\n<w:szCs w:val="32" />',
    )
    blocks["Hyperlink"] = _char(
        "Hyperlink",
        "Hyperlink",
        based="BodyTextChar",
        rpr='<w:color w:val="2E5496" />\n<w:u w:val="single" />',
    )
    blocks["Header"] = _para(
        "Header",
        "header",
        based="Normal",
        ppr='<w:spacing w:before="0" w:after="0" />',
        rpr=_fonts("Calibri", "宋体")
        + '\n<w:color w:val="595959" />\n<w:sz w:val="18" />\n<w:szCs w:val="18" />',
    )
    blocks["Footer"] = _para(
        "Footer",
        "footer",
        based="Normal",
        ppr='<w:spacing w:before="0" w:after="0" />',
        rpr=_fonts("Calibri", "宋体")
        + '\n<w:color w:val="595959" />\n<w:sz w:val="18" />\n<w:szCs w:val="18" />',
    )
    return blocks


def edit_styles(xml: str) -> str:
    xml, n = re.subn(
        r"[ \t]*<w:docDefaults>.*?</w:docDefaults>",
        DOC_DEFAULTS,
        xml,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError("styles.xml: could not locate <w:docDefaults>")

    blocks = build_style_blocks()
    for sid, block in blocks.items():
        pattern = (
            r"[ \t]*<w:style\b[^>]*\bw:styleId=\"%s\"[^>]*>.*?</w:style>"
            % re.escape(sid)
        )
        if re.search(pattern, xml, flags=re.S):
            xml = re.sub(pattern, lambda _m, b=block: b, xml, count=1, flags=re.S)
        else:
            xml = xml.replace("</w:styles>", block + "\n</w:styles>", 1)
    return xml


SETTINGS_UPDATE = '  <w:updateFields w:val="true" />'


def edit_settings(xml: str) -> str:
    if re.search(r"<w:updateFields\b", xml):
        return re.sub(
            r"<w:updateFields\b[^>]*/>",
            '<w:updateFields w:val="true" />',
            xml,
            count=1,
        )
    if "<w:proofState" in xml:
        return xml.replace(
            '  <w:proofState', SETTINGS_UPDATE + "\n  <w:proofState", 1
        )
    return xml.replace("</w:settings>", SETTINGS_UPDATE + "\n</w:settings>", 1)


HEADER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:p>
    <w:pPr>
      <w:pStyle w:val="Header" />
      <w:pBdr>
        <w:bottom w:val="single" w:sz="4" w:space="1" w:color="BFBFBF" />
      </w:pBdr>
      <w:jc w:val="right" />
    </w:pPr>
    <w:r>
      <w:fldChar w:fldCharType="begin" w:dirty="true" />
    </w:r>
    <w:r>
      <w:instrText xml:space="preserve"> DOCPROPERTY "title" </w:instrText>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="separate" />
    </w:r>
    <w:r>
      <w:t>文档标题</w:t>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="end" />
    </w:r>
  </w:p>
</w:hdr>
"""

FOOTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:p>
    <w:pPr>
      <w:pStyle w:val="Footer" />
      <w:jc w:val="center" />
    </w:pPr>
    <w:r>
      <w:t xml:space="preserve">第 </w:t>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="begin" w:dirty="true" />
    </w:r>
    <w:r>
      <w:instrText xml:space="preserve"> PAGE </w:instrText>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="separate" />
    </w:r>
    <w:r>
      <w:t>1</w:t>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="end" />
    </w:r>
    <w:r>
      <w:t xml:space="preserve"> 页 / 共 </w:t>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="begin" w:dirty="true" />
    </w:r>
    <w:r>
      <w:instrText xml:space="preserve"> NUMPAGES </w:instrText>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="separate" />
    </w:r>
    <w:r>
      <w:t>1</w:t>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="end" />
    </w:r>
    <w:r>
      <w:t xml:space="preserve"> 页</w:t>
    </w:r>
  </w:p>
</w:ftr>
"""

SECTPR_XML = """<w:sectPr>
      <w:headerReference w:type="default" r:id="rId9" />
      <w:footerReference w:type="default" r:id="rId10" />
      <w:footnotePr>
        <w:numRestart w:val="eachSect" />
      </w:footnotePr>
      <w:pgSz w:w="11906" w:h="16838" />
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="851" w:footer="992" w:gutter="0" />
      <w:cols w:space="425" />
      <w:docGrid w:type="lines" w:linePitch="312" />
    </w:sectPr>"""


def edit_document(xml: str) -> str:
    matches = re.findall(r"<w:sectPr\b.*?</w:sectPr>", xml, flags=re.S)
    if len(matches) != 1:
        raise RuntimeError(
            "document.xml: expected exactly one <w:sectPr>, found %d" % len(matches)
        )
    return re.sub(
        r"<w:sectPr\b.*?</w:sectPr>", lambda _m: SECTPR_XML, xml, count=1, flags=re.S
    )


REL_HEADER = (
    '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/header" Id="rId9" Target="header1.xml" />'
)
REL_FOOTER = (
    '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/footer" Id="rId10" Target="footer1.xml" />'
)


def edit_document_rels(xml: str) -> str:
    if 'Id="rId9"' in xml or 'Target="header1.xml"' in xml:
        raise RuntimeError("document.xml.rels already references header1.xml")
    if 'Id="rId10"' in xml or 'Target="footer1.xml"' in xml:
        raise RuntimeError("document.xml.rels already references footer1.xml")
    if "></Relationships>" in xml:
        return xml.replace("></Relationships>", ">" + REL_HEADER + REL_FOOTER + "</Relationships>", 1)
    return xml.replace(
        "</Relationships>", REL_HEADER + REL_FOOTER + "</Relationships>", 1
    )


CT_HEADER = (
    '<Override PartName="/word/header1.xml" ContentType="application/'
    'vnd.openxmlformats-officedocument.wordprocessingml.header+xml" />'
)
CT_FOOTER = (
    '<Override PartName="/word/footer1.xml" ContentType="application/'
    'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml" />'
)


def edit_content_types(xml: str) -> str:
    if "/word/header1.xml" in xml:
        raise RuntimeError("[Content_Types].xml already contains header1.xml")
    return xml.replace("</Types>", CT_HEADER + CT_FOOTER + "</Types>", 1)


# ---------------------------------------------------------------------------
# Deterministic packaging.
# ---------------------------------------------------------------------------


def repack(parts: dict[str, bytes], order: list[str]) -> bytes:
    """Write a zip with a fixed entry order and fixed timestamps."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in order:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.external_attr = 0o644 << 16
            zf.writestr(info, parts[name])
    return buf.getvalue()


def build_parts(default_docx: bytes) -> tuple[dict[str, bytes], list[str]]:
    with zipfile.ZipFile(io.BytesIO(default_docx)) as zf:
        names = zf.namelist()
        parts = {name: zf.read(name) for name in names}

    required = {
        "word/styles.xml",
        "word/settings.xml",
        "word/document.xml",
        "word/_rels/document.xml.rels",
        "[Content_Types].xml",
    }
    missing = required - parts.keys()
    if missing:
        raise RuntimeError(
            "pandoc default reference.docx is missing parts: %s"
            % ", ".join(sorted(missing))
        )

    def edit(name: str, fn) -> None:
        text = parts[name].decode("utf-8")
        parts[name] = fn(text).encode("utf-8")

    edit("word/styles.xml", edit_styles)
    edit("word/settings.xml", edit_settings)
    edit("word/document.xml", edit_document)
    edit("word/_rels/document.xml.rels", edit_document_rels)
    edit("[Content_Types].xml", edit_content_types)

    parts["word/header1.xml"] = HEADER_XML.encode("utf-8")
    parts["word/footer1.xml"] = FOOTER_XML.encode("utf-8")

    # Fixed order: package scaffolding first, then the main document and its
    # header/footer, then everything else in the order pandoc shipped it.
    order = ["[Content_Types].xml", "_rels/.rels"]
    order += [n for n in names if n.startswith("docProps/")]
    order += ["word/document.xml", "word/header1.xml", "word/footer1.xml"]
    order += [
        n
        for n in names
        if n not in order and not n.startswith("docProps/")
    ]
    order = list(dict.fromkeys(order))
    assert set(order) == set(parts), "zip entry order does not cover all parts"
    return parts, order


# ---------------------------------------------------------------------------
# Pandoc discovery / invocation.
# ---------------------------------------------------------------------------


def find_pandoc(explicit: str | None) -> str:
    if explicit:
        path = shutil.which(explicit) or (explicit if os.path.isfile(explicit) else None)
        if not path or not os.access(path, os.X_OK):
            raise SystemExit(
                "error: pandoc not found or not executable at %r. "
                "Pass --pandoc with a valid path." % explicit
            )
        return path
    try:
        import pypandoc  # type: ignore

        path = pypandoc.get_pandoc_path()
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    except Exception:
        pass
    path = shutil.which("pandoc")
    if not path:
        raise SystemExit(
            "error: pandoc not found. Install pypandoc_binary==1.17 in a venv "
            "(its bundled pandoc is 3.9), or install pandoc on PATH, then pass "
            "--pandoc /path/to/pandoc."
        )
    return path


def pandoc_version(pandoc: str) -> str:
    proc = subprocess.run(
        [pandoc, "--version"], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise SystemExit("error: `%s --version` failed:\n%s" % (pandoc, proc.stderr))
    return proc.stdout.splitlines()[0].strip()


def default_reference_bytes(pandoc: str) -> bytes:
    proc = subprocess.run(
        [pandoc, "--print-default-data-file", "reference.docx"],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            "error: `pandoc --print-default-data-file reference.docx` failed:\n%s"
            % proc.stderr.decode("utf-8", "replace")
        )
    if not proc.stdout.startswith(b"PK"):
        raise SystemExit("error: pandoc returned a non-zip reference document")
    return proc.stdout


# ---------------------------------------------------------------------------
# Verification.
# ---------------------------------------------------------------------------

# 1x1 PNG.
PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

FIXTURE_MD = """---
title: "验证标题"
subtitle: "版本 1.0 · 2026-10-28"
abstract: "这是摘要。Abstract text for verification."
author: "测试作者"
lang: zh-CN
---

# 一级标题 {#sec-1}

正文中文 text with `inline code` and **bold**.

## 二级标题

| 列一 | 列二 |
|------|------|
| 甲   | 乙   |

```python
print("hello")
```

### 三级标题

#### 四级标题

![示例图片](img.png){width=4cm}
"""


def parse_xml_part(name: str, data: bytes) -> ET.Element:
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:  # pragma: no cover - defensive
        raise SystemExit("error: %s is not well-formed XML: %s" % (name, exc))


def verify_reference_docx(path: Path, pandoc: str) -> list[str]:
    notes: list[str] = []
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise SystemExit("error: corrupt zip entry %s" % bad)
        names = zf.namelist()
        parts = {name: zf.read(name) for name in names}

    for name in names:
        if name.endswith(".xml") or name.endswith(".rels"):
            parse_xml_part(name, parts[name])
    notes.append("all %d XML/rels parts parse" % len([n for n in names if n.endswith((".xml", ".rels"))]))

    for required in (
        "word/header1.xml",
        "word/footer1.xml",
        "word/settings.xml",
        "word/styles.xml",
        "word/document.xml",
        "word/_rels/document.xml.rels",
        "[Content_Types].xml",
    ):
        if required not in parts:
            raise SystemExit("error: reference.docx missing %s" % required)

    styles_root = parse_xml_part("word/styles.xml", parts["word/styles.xml"])
    ids = {el.get(W + "styleId") for el in styles_root.iter(W + "style")}
    missing = [sid for sid in STYLE_IDS if sid not in ids]
    if missing:
        raise SystemExit(
            "error: styles.xml is missing style ids: %s" % ", ".join(missing)
        )
    notes.append("style ids present: %d (incl. SourceCode, TOCHeading, Table)" % len(ids))

    settings = parts["word/settings.xml"].decode("utf-8")
    if not re.search(r'<w:updateFields\b[^>]*w:val="true"', settings):
        raise SystemExit("error: settings.xml lacks <w:updateFields w:val=\"true\"/>")
    notes.append("settings.xml has updateFields")

    doc = parts["word/document.xml"].decode("utf-8")
    if len(re.findall(r"<w:sectPr\b", doc)) != 1:
        raise SystemExit("error: document.xml does not have exactly one w:sectPr")
    if 'r:id="rId9"' not in doc or 'r:id="rId10"' not in doc:
        raise SystemExit("error: sectPr does not reference header/footer relationships")
    if 'w:pgSz w:w="11906" w:h="16838"' not in doc:
        raise SystemExit("error: sectPr is not A4")
    notes.append("document.xml: one A4 sectPr with header/footer references")

    rels = parts["word/_rels/document.xml.rels"].decode("utf-8")
    for needle in ("header1.xml", "footer1.xml"):
        if needle not in rels:
            raise SystemExit("error: document.xml.rels missing %s" % needle)
    ct = parts["[Content_Types].xml"].decode("utf-8")
    for needle in ("/word/header1.xml", "/word/footer1.xml"):
        if needle not in ct:
            raise SystemExit("error: [Content_Types].xml missing %s" % needle)
    notes.append("relationships and content-type overrides present")

    header = parts["word/header1.xml"].decode("utf-8")
    if 'DOCPROPERTY &quot;title&quot;' not in header and 'DOCPROPERTY "title"' not in header:
        raise SystemExit("error: header1.xml lacks DOCPROPERTY \"title\" field")
    if 'w:dirty="true"' not in header:
        raise SystemExit("error: header1.xml field is not marked dirty")
    footer = parts["word/footer1.xml"].decode("utf-8")
    for token in ("PAGE", "NUMPAGES", "第 ", " 页"):
        if token not in footer:
            raise SystemExit("error: footer1.xml lacks %r" % token)
    notes.append("header DOCPROPERTY/title dirty field and footer PAGE/NUMPAGES fields present")

    # Real conversion check: fixture -> docx via --reference-doc.
    tmp = Path(tempfile.mkdtemp(prefix="docs-docx-ref-verify-"))
    try:
        (tmp / "img.png").write_bytes(PNG_1PX)
        (tmp / "fixture.md").write_text(FIXTURE_MD, encoding="utf-8")
        out = tmp / "out.docx"
        proc = subprocess.run(
            [
                pandoc,
                "--from=markdown+raw_attribute",
                "--to=docx",
                "--reference-doc=%s" % path,
                "--resource-path=%s" % tmp,
                "-o",
                str(out),
                str(tmp / "fixture.md"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(
                "error: pandoc conversion with the new reference docx failed:\n%s"
                % proc.stderr
            )
        with zipfile.ZipFile(out) as zf:
            out_names = zf.namelist()
            out_doc = zf.read("word/document.xml").decode("utf-8")
            out_settings = zf.read("word/settings.xml").decode("utf-8")
        if "<w:headerReference" not in out_doc or "<w:footerReference" not in out_doc:
            raise SystemExit("error: converted fixture has no header/footer references")
        if not re.search(r"<w:updateFields\b", out_settings):
            raise SystemExit("error: converted fixture settings lack updateFields")
        for sid in ("Heading1", "Heading2", "Heading3", "Heading4",
                    "SourceCode", "Title", "Subtitle", "Author", "Abstract"):
            if 'w:pStyle w:val="%s"' % sid not in out_doc:
                raise SystemExit("error: converted fixture does not use style %s" % sid)
        if '<w:tblStyle w:val="Table"' not in out_doc:
            raise SystemExit("error: converted fixture does not use the Table style")
        media = [n for n in out_names if n.startswith("word/media/")]
        if not media:
            raise SystemExit("error: converted fixture did not embed the local image")
        notes.append(
            "fixture -> docx uses H1-H4/Table/SourceCode/title block styles, "
            "embeds %d image part(s)" % len(media)
        )

        # docx -> markdown round trip must not fail.
        back = subprocess.run(
            [pandoc, "--from=docx", "--to=markdown", "-o", str(tmp / "back.md"), str(out)],
            capture_output=True,
            text=True,
            check=False,
        )
        if back.returncode != 0:
            raise SystemExit(
                "error: pandoc could not re-read the generated docx:\n%s" % back.stderr
            )
        back_text = (tmp / "back.md").read_text(encoding="utf-8")
        if "一级标题" not in back_text:
            raise SystemExit("error: docx -> markdown round trip lost the CJK heading")
        notes.append("docx -> markdown re-read succeeds and keeps CJK content")

        # The template itself must also be readable by pandoc's docx reader.
        self_read = subprocess.run(
            [pandoc, "--from=docx", "--to=markdown", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if self_read.returncode != 0:
            raise SystemExit(
                "error: pandoc could not re-read reference.docx:\n%s"
                % self_read.stderr
            )
        if "Heading 1" not in self_read.stdout:
            raise SystemExit(
                "error: reference.docx -> markdown round trip lost the placeholder headings"
            )
        notes.append("reference.docx itself re-reads via pandoc docx reader")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return notes


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the docs-docx-view reference.docx (maintenance only)."
    )
    parser.add_argument("--pandoc", default=None, metavar="PATH",
                        help="pandoc executable (default: pypandoc or PATH)")
    parser.add_argument("--output", default=None, metavar="PATH",
                        help="output path (default: skills/docs-docx-view/assets/reference.docx)")
    args = parser.parse_args(argv)

    output = Path(args.output).expanduser() if args.output else DEFAULT_OUTPUT
    output = output if output.is_absolute() else (Path.cwd() / output)
    pandoc = find_pandoc(args.pandoc)
    version = pandoc_version(pandoc)
    source = default_reference_bytes(pandoc)
    print("pandoc: %s (%s)" % (pandoc, version))
    print("source: pandoc --print-default-data-file reference.docx (%d bytes)" % len(source))

    parts, order = build_parts(source)
    data = repack(parts, order)

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp_out = output.with_name(output.name + ".tmp")
    tmp_out.write_bytes(data)
    try:
        notes = verify_reference_docx(tmp_out, pandoc)
        os.replace(tmp_out, output)
    except BaseException:
        tmp_out.unlink(missing_ok=True)
        raise

    print("wrote: %s (%d bytes, %d parts)" % (output, output.stat().st_size, len(order)))
    for note in notes:
        print("ok: " + note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
