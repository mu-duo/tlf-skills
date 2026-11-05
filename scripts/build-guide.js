#!/usr/bin/env node
"use strict";

// Zero-dependency Markdown-subset renderer for the offline tutorial.
// Builds skills{,_zh}/project-docs-workflow/guide/index.html from the English
// guide README plus scripts/guide-shell.html. The renderer is exported so the
// checker can regenerate the expected bytes without writing anything.

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_SHELL = path.join(ROOT, "scripts", "guide-shell.html");
const GUIDE_REL = path.join("project-docs-workflow", "guide");
const README_EN = path.join(ROOT, "skills", GUIDE_REL, "README.md");
const README_ZH = path.join(ROOT, "skills_zh", GUIDE_REL, "README.md");
const OUT_EN = path.join(ROOT, "skills", GUIDE_REL, "index.html");
const OUT_ZH = path.join(ROOT, "skills_zh", GUIDE_REL, "index.html");

const TOKENS = ["{{TITLE}}", "{{VERSION}}", "<!--{{TOC}}-->", "<!--{{CONTENT}}-->"];

// Block-level HTML tags passed through verbatim. Inline HTML in paragraphs is
// escaped; only a line that starts with one of these tags opens a raw block.
const RAW_BLOCK_TAGS = new Set([
  "figure",
  "div",
  "section",
  "table",
  "details",
  "pre",
  "script",
  "style",
  "svg",
  "aside",
  "header",
  "footer",
  "main",
  "nav",
]);

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderInline(text) {
  const parts = String(text).split(/(`[^`]*`)/g);
  return parts
    .map((part) => {
      if (/^`[^`]*`$/.test(part)) {
        return "<code>" + escapeHtml(part.slice(1, -1)) + "</code>";
      }
      return renderInlinePlain(part);
    })
    .join("");
}

function renderInlinePlain(text) {
  let out = "";
  let last = 0;
  const pattern = /\[([^\]]+)\]\(([^)\s]+)\)|\*\*([^*]+)\*\*/g;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    out += escapeHtml(text.slice(last, match.index));
    if (match[1] !== undefined) {
      out +=
        '<a href="' + escapeHtml(match[2]) + '">' + renderInline(match[1]) + "</a>";
    } else {
      out += "<strong>" + renderInline(match[3]) + "</strong>";
    }
    last = pattern.lastIndex;
  }
  out += escapeHtml(text.slice(last));
  return out;
}

function plainInline(text) {
  return String(text)
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1");
}

function isHorizontalRule(line) {
  return /^ {0,3}([-*_])\s*(\1\s*){2,}$/.test(line);
}

function isFence(line) {
  return /^\s*(```|~~~)/.test(line);
}

function isHeading(line) {
  return /^#{1,6}\s+/.test(line);
}

function isListStart(line) {
  return /^(\s*)([-*+]|\d+\.)\s+/.test(line);
}

function isBlockquote(line) {
  return /^>\s?/.test(line);
}

function rawBlockTag(line) {
  const match = String(line)
    .trim()
    .match(/^<([A-Za-z][A-Za-z0-9-]*)\b/);
  if (!match) return null;
  const tag = match[1].toLowerCase();
  return RAW_BLOCK_TAGS.has(tag) ? tag : null;
}

function isTableSeparator(line) {
  const trimmed = String(line).trim();
  if (!trimmed.includes("-") || !trimmed.includes("|")) return false;
  let body = trimmed;
  if (body.startsWith("|")) body = body.slice(1);
  if (body.endsWith("|")) body = body.slice(0, -1);
  const cells = body.split("|").map((cell) => cell.trim());
  return cells.length > 0 && cells.every((cell) => /^:?-{1,}:?$/.test(cell));
}

function splitTableRow(line) {
  let body = String(line).trim();
  if (body.startsWith("|")) body = body.slice(1);
  if (body.endsWith("|")) body = body.slice(0, -1);
  return body.split("|").map((cell) => cell.trim());
}

function startsBlock(line, lines, index) {
  if (line.trim() === "") return true;
  if (isFence(line) || isHeading(line) || isHorizontalRule(line)) return true;
  if (isListStart(line) || isBlockquote(line) || rawBlockTag(line)) return true;
  if (line.trim().startsWith("|")) return true;
  if (
    line.includes("|") &&
    index + 1 < lines.length &&
    isTableSeparator(lines[index + 1])
  ) {
    return true;
  }
  return false;
}

function renderMarkdown(md) {
  const lines = String(md).replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  const toc = [];
  let title = "";
  let h2Count = 0;
  let h3Count = 0;
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.trim() === "") {
      i += 1;
      continue;
    }

    // Fenced code blocks.
    const fence = line.match(/^\s*(```|~~~)/);
    if (fence) {
      const marker = fence[1];
      const code = [];
      i += 1;
      while (i < lines.length && !new RegExp("^\\s*" + marker).test(lines[i])) {
        code.push(lines[i]);
        i += 1;
      }
      if (i < lines.length) i += 1; // closing fence
      blocks.push("<pre><code>" + escapeHtml(code.join("\n")) + "</code></pre>");
      continue;
    }

    // Raw HTML block (e.g. <figure> with inline SVG). Pass through verbatim.
    const rawTag = rawBlockTag(line);
    if (rawTag) {
      const closeRe = new RegExp("</" + rawTag + "\\s*>", "i");
      let end = i;
      while (end < lines.length && !closeRe.test(lines[end])) {
        end += 1;
      }
      if (end < lines.length) {
        end += 1;
      } else {
        // Unclosed block: fall back to the next blank line.
        end = i;
        while (end < lines.length && lines[end].trim() !== "") {
          end += 1;
        }
      }
      blocks.push(lines.slice(i, end).join("\n"));
      i = end;
      continue;
    }

    // ATX headings.
    const heading = line.match(/^(#{1,6})\s+(.*?)\s*#*\s*$/);
    if (heading) {
      const level = heading[1].length;
      const text = heading[2];
      if (level === 1) {
        // The shell renders the page title from {{TITLE}}; drop the source h1
        // so the injected content does not duplicate it.
        if (!title) title = plainInline(text);
      } else if (level === 2) {
        h2Count += 1;
        h3Count = 0;
        const id = "sec-" + h2Count;
        const html = renderInline(text);
        toc.push('<li><a href="#' + id + '">' + html + "</a></li>");
        blocks.push('<h2 id="' + id + '">' + html + "</h2>");
      } else if (level === 3) {
        h3Count += 1;
        const id = "sub-" + h2Count + "-" + h3Count;
        blocks.push('<h3 id="' + id + '">' + renderInline(text) + "</h3>");
      } else {
        blocks.push("<h" + level + ">" + renderInline(text) + "</h" + level + ">");
      }
      i += 1;
      continue;
    }

    // Horizontal rule.
    if (isHorizontalRule(line)) {
      blocks.push("<hr>");
      i += 1;
      continue;
    }

    // Blockquote.
    if (isBlockquote(line)) {
      const quoted = [];
      while (i < lines.length && isBlockquote(lines[i])) {
        quoted.push(lines[i].replace(/^>\s?/, ""));
        i += 1;
      }
      blocks.push("<blockquote><p>" + renderInline(quoted.join(" ")) + "</p></blockquote>");
      continue;
    }

    // GFM pipe table.
    if (line.includes("|") && i + 1 < lines.length && isTableSeparator(lines[i + 1])) {
      const header = splitTableRow(line);
      i += 2;
      const rows = [];
      while (
        i < lines.length &&
        lines[i].trim() !== "" &&
        lines[i].includes("|") &&
        !isHeading(lines[i])
      ) {
        rows.push(splitTableRow(lines[i]));
        i += 1;
      }
      let html = "<table>\n<thead>\n<tr>";
      for (const cell of header) {
        html += "<th>" + renderInline(cell) + "</th>";
      }
      html += "</tr>\n</thead>\n<tbody>\n";
      for (const row of rows) {
        html += "<tr>";
        for (const cell of row) {
          html += "<td>" + renderInline(cell) + "</td>";
        }
        html += "</tr>\n";
      }
      html += "</tbody>\n</table>";
      blocks.push(html);
      continue;
    }

    // Lists (single level; continuation lines are indented).
    const list = line.match(/^(\s*)([-*+]|\d+\.)\s+(.*)$/);
    if (list) {
      const indent = list[1].length;
      const ordered = /^\d+\.$/.test(list[2]);
      const items = [];
      while (i < lines.length) {
        const item = lines[i].match(/^(\s*)([-*+]|\d+\.)\s+(.*)$/);
        if (
          !item ||
          item[1].length !== indent ||
          /^\d+\.$/.test(item[2]) !== ordered
        ) {
          break;
        }
        let text = item[3];
        i += 1;
        while (
          i < lines.length &&
          lines[i].trim() !== "" &&
          !isListStart(lines[i]) &&
          !isHeading(lines[i]) &&
          !isFence(lines[i]) &&
          /^\s+/.test(lines[i])
        ) {
          text += "\n" + lines[i].trim();
          i += 1;
        }
        items.push(text);
      }
      const tag = ordered ? "ol" : "ul";
      let html = "<" + tag + ">\n";
      for (const text of items) {
        html += "<li>" + renderInline(text) + "</li>\n";
      }
      html += "</" + tag + ">";
      blocks.push(html);
      continue;
    }

    // Paragraph.
    const paragraph = [line];
    i += 1;
    while (i < lines.length && !startsBlock(lines[i], lines, i)) {
      paragraph.push(lines[i]);
      i += 1;
    }
    blocks.push("<p>" + renderInline(paragraph.join("\n")) + "</p>");
  }

  return {
    title,
    content: blocks.join("\n\n"),
    toc: '<ul class="toc-list">' + toc.join("") + "</ul>",
  };
}

function versionToken(version) {
  const raw = String(version || "")
    .trim()
    .replace(/^v/i, "");
  const parts = raw.split(".");
  if (parts.length < 2 || parts[0] === "" || parts[1] === "") {
    throw new Error("package.json version is not major.minor: " + version);
  }
  return "v" + parts[0] + "." + parts[1];
}

function replaceToken(shell, token, value) {
  return shell.split(token).join(value);
}

function renderGuide(input) {
  const md = input && input.md;
  const shell = input && input.shell;
  if (typeof md !== "string" || typeof shell !== "string") {
    throw new Error("renderGuide requires { md, shell, version } strings");
  }
  const missing = TOKENS.filter((token) => shell.indexOf(token) === -1);
  if (missing.length > 0) {
    throw new Error("guide shell is missing token(s): " + missing.join(", "));
  }
  const rendered = renderMarkdown(md);
  let html = shell;
  html = replaceToken(html, "{{TITLE}}", escapeHtml(rendered.title));
  html = replaceToken(html, "{{VERSION}}", versionToken(input.version));
  html = replaceToken(html, "<!--{{TOC}}-->", rendered.toc);
  html = replaceToken(html, "<!--{{CONTENT}}-->", rendered.content);
  return html;
}

function readPackageVersion() {
  const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));
  return String(pkg.version || "");
}

function parseArgs(argv) {
  const opts = { shell: DEFAULT_SHELL, out: null, check: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--check") {
      opts.check = true;
    } else if (arg === "--shell") {
      const value = argv[++i];
      if (!value) throw new Error("--shell requires a path");
      opts.shell = path.resolve(value);
    } else if (arg.startsWith("--shell=")) {
      opts.shell = path.resolve(arg.slice("--shell=".length));
    } else if (arg === "--out") {
      const value = argv[++i];
      if (!value) throw new Error("--out requires a directory");
      opts.out = path.resolve(value);
    } else if (arg.startsWith("--out=")) {
      opts.out = path.resolve(arg.slice("--out=".length));
    } else if (arg === "-h" || arg === "--help") {
      console.log(
        [
          "Usage: node scripts/build-guide.js [--shell <path>] [--out <dir>] [--check]",
          "",
          "  --shell <path>  Override scripts/guide-shell.html",
          "  --out <dir>     Write index.html to <dir> instead of the repo",
          "  --check         Compare the committed HTML with freshly rendered output",
        ].join("\n")
      );
      process.exit(0);
    } else {
      throw new Error("unknown argument: " + arg);
    }
  }
  return opts;
}

function readShell(shellPath) {
  if (!fs.existsSync(shellPath)) {
    console.error(
      "错误：找不到指南外壳 " +
        shellPath +
        "\n需要先提供 scripts/guide-shell.html，`npm run build:guide` 才能运行。"
    );
    process.exit(1);
  }
  return fs.readFileSync(shellPath, "utf8");
}

function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error("错误：" + error.message);
    process.exit(1);
  }

  const shell = readShell(opts.shell);
  if (!fs.existsSync(README_EN)) {
    console.error("错误：找不到教程源文件 " + README_EN);
    process.exit(1);
  }
  const md = fs.readFileSync(README_EN, "utf8");
  const version = readPackageVersion();

  let html;
  try {
    html = renderGuide({ md, shell, version });
  } catch (error) {
    console.error("错误：" + error.message);
    process.exit(1);
  }

  if (opts.check) {
    let drift = false;
    for (const target of [OUT_EN, OUT_ZH]) {
      if (!fs.existsSync(target)) {
        console.error("FAIL 缺少已提交文件：" + path.relative(ROOT, target));
        drift = true;
        continue;
      }
      const current = fs.readFileSync(target);
      if (!current.equals(Buffer.from(html))) {
        console.error("FAIL 已提交文件与重新生成结果不一致：" + path.relative(ROOT, target));
        drift = true;
      }
    }
    if (drift) {
      console.error("请运行 npm run build:guide 重新生成指南。");
      process.exit(1);
    }
    console.log("PASS 指南 HTML 与重新生成结果一致。");
    return;
  }

  if (opts.out) {
    fs.mkdirSync(opts.out, { recursive: true });
    const dest = path.join(opts.out, "index.html");
    fs.writeFileSync(dest, html);
    console.log("已生成 " + dest);
    return;
  }

  for (const target of [OUT_EN, OUT_ZH]) {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, html);
    console.log("已生成 " + path.relative(ROOT, target));
  }
}

if (require.main === module) {
  main();
}

module.exports = { renderGuide, versionToken, README_EN, README_ZH, OUT_EN, OUT_ZH };
