#!/usr/bin/env node
"use strict";

// Read-only assertions for the offline tutorial:
//   guide/README.md + guide/index.html in skills/ and skills_zh/.
// Exits non-zero on any failure with concise PASS/FAIL lines.

const fs = require("fs");
const path = require("path");
const { renderGuide } = require("./build-guide");

const ROOT = path.resolve(__dirname, "..");
const GUIDE_REL = path.join("project-docs-workflow", "guide");
const EN_GUIDE = path.join(ROOT, "skills", GUIDE_REL);
const ZH_GUIDE = path.join(ROOT, "skills_zh", GUIDE_REL);
const EN_README = path.join(EN_GUIDE, "README.md");
const ZH_README = path.join(ZH_GUIDE, "README.md");
const EN_HTML = path.join(EN_GUIDE, "index.html");
const ZH_HTML = path.join(ZH_GUIDE, "index.html");
const SHELL = path.join(ROOT, "scripts", "guide-shell.html");

const OUTLINE = [
  "1. 一分钟定位",
  "2. 它治什么病",
  "3. 文档地图",
  "4. 五步流程",
  "5. init 实操",
  "6. 其他 skill 与延伸阅读",
];

const failures = [];
const categories = [];

function fail(message) {
  failures.push(message);
}

function category(label, fn) {
  const start = failures.length;
  fn();
  categories.push({ label, failed: failures.length - start });
}

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

// The shell ships an inert documentation comment that shows literal examples
// such as <a href="#slug">, <link>, and @import. Strip comments before content
// assertions so those examples are not mistaken for live markup. The
// regeneration/drift check must keep using the untouched bytes.
function stripHtmlComments(html) {
  return String(html).replace(/<!--[\s\S]*?-->/g, "");
}

function readVersion() {
  return String(JSON.parse(readText(path.join(ROOT, "package.json"))).version || "");
}

function decodeEntities(text) {
  return String(text)
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&");
}

function stripTags(text) {
  return decodeEntities(String(text).replace(/<[^>]*>/g, "")).trim();
}

function versionToken(version) {
  const parts = String(version).split(".");
  return "v" + parts[0] + "." + parts[1];
}

// --- 1. artifacts exist ----------------------------------------------------

category("guide artifacts exist", () => {
  for (const file of [EN_README, EN_HTML, ZH_README, ZH_HTML]) {
    if (!fs.existsSync(file)) {
      fail("missing " + path.relative(ROOT, file));
    }
  }
});

// --- 2. mirror byte parity -------------------------------------------------

category("skills_zh mirror byte-identical", () => {
  const pairs = [
    [EN_README, ZH_README, "guide/README.md"],
    [EN_HTML, ZH_HTML, "guide/index.html"],
  ];
  for (const [en, zh, label] of pairs) {
    if (!fs.existsSync(en) || !fs.existsSync(zh)) {
      fail("cannot compare " + label + " (missing file)");
      continue;
    }
    if (!fs.readFileSync(en).equals(fs.readFileSync(zh))) {
      fail("skills_zh " + label + " differs from English source");
    }
  }
});

// --- 3. committed HTML matches regeneration --------------------------------

category("committed HTML matches regeneration", () => {
  if (!fs.existsSync(SHELL)) {
    fail("missing scripts/guide-shell.html (cannot regenerate)");
    return;
  }
  if (!fs.existsSync(EN_README)) {
    fail("missing skills/" + GUIDE_REL + "/README.md");
    return;
  }
  let expected;
  try {
    expected = renderGuide({
      md: readText(EN_README),
      shell: readText(SHELL),
      version: readVersion(),
    });
  } catch (error) {
    fail("renderer failed: " + (error && error.message ? error.message : error));
    return;
  }
  const expectedBytes = Buffer.from(expected);
  for (const file of [EN_HTML, ZH_HTML]) {
    if (!fs.existsSync(file)) {
      fail("missing " + path.relative(ROOT, file));
      continue;
    }
    if (!fs.readFileSync(file).equals(expectedBytes)) {
      fail(path.relative(ROOT, file) + " is stale; run npm run build:guide");
    }
  }
});

// --- 4. no external resources ---------------------------------------------

category("no external resources", () => {
  for (const file of [EN_HTML, ZH_HTML]) {
    if (!fs.existsSync(file)) {
      fail("cannot scan " + path.relative(ROOT, file) + " (missing file)");
      continue;
    }
    // Inline SVG namespaces are inert and explicitly allowed.
    const html = stripHtmlComments(readText(file))
      .split('xmlns="http://www.w3.org/2000/svg"')
      .join("");
    const patterns = [
      { re: /\bsrc\s*=\s*["']https?:/i, label: 'src="http' },
      { re: /\bhref\s*=\s*["']https?:/i, label: 'href="http' },
      { re: /url\(\s*["']?https?:/i, label: "url(http" },
      { re: /@import/i, label: "@import" },
      { re: /<link\b/i, label: "<link" },
    ];
    for (const { re, label } of patterns) {
      if (re.test(html)) {
        fail(path.relative(ROOT, file) + " contains external resource marker: " + label);
      }
    }
  }
});

// --- 5. anchor integrity ---------------------------------------------------

function collectIds(html) {
  const ids = new Set();
  const re = /\bid\s*=\s*["']([^"']+)["']/g;
  let match;
  while ((match = re.exec(html)) !== null) {
    ids.add(match[1]);
  }
  return ids;
}

function collectHrefs(html) {
  const hrefs = [];
  const re = /\bhref\s*=\s*["']([^"']*)["']/g;
  let match;
  while ((match = re.exec(html)) !== null) {
    hrefs.push(match[1]);
  }
  return hrefs;
}

category("anchor integrity", () => {
  for (const file of [EN_HTML, ZH_HTML]) {
    if (!fs.existsSync(file)) {
      fail("cannot check anchors in " + path.relative(ROOT, file) + " (missing file)");
      continue;
    }
    const html = stripHtmlComments(readText(file));
    const ids = collectIds(html);
    for (const href of collectHrefs(html)) {
      if (!href.startsWith("#")) continue;
      const id = href.slice(1);
      if (id && !ids.has(id)) {
        fail(path.relative(ROOT, file) + " has href=\"" + href + "\" without matching id");
      }
    }
    const toc = html.match(/<ul class="toc-list">([\s\S]*?)<\/ul>/);
    if (!toc) {
      fail(path.relative(ROOT, file) + " has no toc-list");
    } else {
      for (const href of collectHrefs(toc[1])) {
        if (!href.startsWith("#")) {
          fail(path.relative(ROOT, file) + " TOC entry is not an internal anchor: " + href);
          continue;
        }
        const id = href.slice(1);
        if (id && !ids.has(id)) {
          fail(path.relative(ROOT, file) + " TOC points at missing id: " + id);
        }
      }
    }
  }
});

// --- 6. outline lock -------------------------------------------------------

category("outline lock", () => {
  if (!fs.existsSync(EN_HTML)) {
    fail("cannot check outline (missing " + path.relative(ROOT, EN_HTML) + ")");
    return;
  }
  const html = stripHtmlComments(readText(EN_HTML));
  const titles = [];
  const re = /<h2\b[^>]*>([\s\S]*?)<\/h2>/gi;
  let match;
  while ((match = re.exec(html)) !== null) {
    titles.push(stripTags(match[1]));
  }
  let cursor = -1;
  for (const expected of OUTLINE) {
    const index = titles.indexOf(expected, cursor + 1);
    if (index === -1) {
      fail("missing or out-of-order h2: " + expected);
      continue;
    }
    cursor = index;
  }
});

// --- 7. footer version -----------------------------------------------------

category("footer version", () => {
  const token = versionToken(readVersion());
  for (const file of [EN_HTML, ZH_HTML]) {
    if (!fs.existsSync(file)) {
      fail("cannot check version in " + path.relative(ROOT, file) + " (missing file)");
      continue;
    }
    const html = readText(file);
    const footer = html.match(/<footer\b[\s\S]*?<\/footer>/i);
    const region = footer ? footer[0] : html;
    const found = region.match(/v\d+\.\d+/);
    if (!found) {
      fail(path.relative(ROOT, file) + " has no v<major>.<minor> version token");
    } else if (found[0] !== token) {
      fail(
        path.relative(ROOT, file) +
          " version token " +
          found[0] +
          " does not match package.json " +
          token
      );
    }
  }
});

// --- report ----------------------------------------------------------------

console.log("check-guide: offline tutorial (Markdown -> HTML)");
console.log("Repository root: " + ROOT);
console.log("");

for (const entry of categories) {
  if (entry.failed === 0) {
    console.log("PASS  " + entry.label);
  } else {
    console.log("FAIL  " + entry.label + " (" + entry.failed + " failure(s))");
  }
}

if (failures.length > 0) {
  console.log("");
  console.log("Failures (" + failures.length + "):");
  for (const message of failures) {
    console.log("  - " + message);
  }
  console.log("");
  console.log("Result: FAILED");
  process.exitCode = 1;
} else {
  console.log("");
  console.log("Result: OK");
}
