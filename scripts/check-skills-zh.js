#!/usr/bin/env node
"use strict";

// Read-only consistency checker for the Chinese skill mirror (skills_zh/).
// Source of truth: skills/. Run from any cwd; paths resolve from this file.

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const EN_ROOT = path.join(ROOT, "skills");
const ZH_ROOT = path.join(ROOT, "skills_zh");

// Files copied verbatim from the English tree (Markdown templates included).
const COPIED_PREFIXES = [
  "project-docs-workflow/references/deps/",
  "project-docs-workflow/assets/",
  "docs-html-view/scripts/",
  "docs-html-view/assets/",
  "docs-docx-view/scripts/",
  "docs-docx-view/assets/",
];
const COPIED_EXACT = new Set(["docs-html-view/requirements.txt"]);

// Relative-link examples aimed at target projects, not files in this repository.
const LINK_SKIP_PREFIXES = [
  "../adr/",
  "../../adr/",
  "../prd/",
  "../../prd/",
  "../current/",
  "../../current/",
];

const failures = [];
const categories = [];

for (const dir of [EN_ROOT, ZH_ROOT]) {
  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    console.error(`check-skills-zh: missing directory: ${dir}`);
    process.exit(1);
  }
}

function fail(message) {
  failures.push(message);
}

function category(label, fn) {
  const start = failures.length;
  const checked = fn() || 0;
  categories.push({
    label,
    checked,
    failed: failures.length - start,
  });
}

function walk(dir, base = dir) {
  const result = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      result.push(...walk(full, base));
    } else if (entry.isFile()) {
      result.push(path.relative(base, full));
    }
  }
  return result;
}

function toPosix(rel) {
  return rel.split(path.sep).join("/");
}

function isCopied(rel) {
  if (COPIED_EXACT.has(rel)) return true;
  if (COPIED_PREFIXES.some((prefix) => rel.startsWith(prefix))) return true;
  const ext = path.extname(rel).toLowerCase();
  return ext !== ".md" && ext !== ".markdown" && ext !== ".yaml" && ext !== ".yml";
}

function readText(rel) {
  return fs.readFileSync(path.join(ZH_ROOT, rel), "utf8");
}

function normalizeEol(text) {
  return text.replace(/\r\n/g, "\n");
}

function unquote(value) {
  let v = value.trim();
  if (v.length >= 2) {
    const first = v[0];
    const last = v[v.length - 1];
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      v = v.slice(1, -1);
    }
  }
  return v;
}

// --- structure -------------------------------------------------------------

const enFiles = new Set(walk(EN_ROOT).map(toPosix));
const zhFiles = new Set(walk(ZH_ROOT).map(toPosix));

category("file-set parity", () => {
  let checked = 0;
  for (const rel of enFiles) {
    checked += 1;
    if (!zhFiles.has(rel)) {
      fail(`missing in skills_zh/: ${rel}`);
    }
  }
  for (const rel of zhFiles) {
    if (!enFiles.has(rel) && rel !== "README.md") {
      fail(`extra file in skills_zh/ (only root README.md is allowed): ${rel}`);
    }
  }
  return checked;
});

// --- byte-identical copied files ------------------------------------------

category("copied files byte-identical", () => {
  let checked = 0;
  for (const rel of enFiles) {
    if (!zhFiles.has(rel) || !isCopied(rel)) continue;
    checked += 1;
    const en = fs.readFileSync(path.join(EN_ROOT, rel));
    const zh = fs.readFileSync(path.join(ZH_ROOT, rel));
    if (!en.equals(zh)) {
      fail(`copied file differs from English source: ${rel}`);
    }
  }
  return checked;
});

// --- agents/openai.yaml ----------------------------------------------------

function interfaceValues(text) {
  const values = new Map();
  let inInterface = false;
  for (const line of normalizeEol(text).split("\n")) {
    if (/^interface\s*:\s*$/.test(line)) {
      inInterface = true;
      continue;
    }
    if (!inInterface) continue;
    if (/^\S/.test(line)) {
      inInterface = false;
      continue;
    }
    const match = line.match(/^\s+([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
    if (match) {
      values.set(match[1], unquote(match[2]));
    }
  }
  return values;
}

function policyBlock(text) {
  const index = text.search(/^policy\s*:/m);
  return index === -1 ? null : text.slice(index);
}

category("agents/openai.yaml interface + policy", () => {
  let checked = 0;
  for (const rel of enFiles) {
    if (!rel.endsWith("agents/openai.yaml") || !zhFiles.has(rel)) continue;
    checked += 1;
    const enText = fs.readFileSync(path.join(EN_ROOT, rel), "utf8");
    const zhText = readText(rel);
    const zhInterface = interfaceValues(zhText);

    for (const key of ["display_name", "short_description"]) {
      if (!zhInterface.has(key) || zhInterface.get(key).trim() === "") {
        fail(`missing or empty interface.${key}: ${rel}`);
      }
    }

    const enPolicy = policyBlock(enText);
    const zhPolicy = policyBlock(zhText);
    if (enPolicy !== zhPolicy) {
      fail(`policy block differs from English source: ${rel}`);
    }
  }
  return checked;
});

// --- SKILL.md frontmatter --------------------------------------------------

function firstFrontmatter(text) {
  const normalized = normalizeEol(text).replace(/^\uFEFF/, "");
  const match = normalized.match(/^---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|$)/);
  return match ? match[1] : null;
}

function frontmatterMap(frontmatter) {
  const map = new Map();
  for (const line of frontmatter.split("\n")) {
    const match = line.match(/^([A-Za-z0-9_-]+)\s*:\s*(.*)$/);
    if (match) {
      map.set(match[1], match[2]);
    }
  }
  return map;
}

function hasNonEmptyDescription(value, frontmatter) {
  const raw = value === undefined ? "" : value.trim();
  if (/^[|>][+-]?$/.test(raw)) {
    return frontmatter.split("\n").some((line) => /^\s+\S/.test(line));
  }
  return unquote(raw) !== "";
}

category("SKILL.md frontmatter", () => {
  let checked = 0;
  for (const rel of enFiles) {
    if (!rel.endsWith("SKILL.md") || !zhFiles.has(rel)) continue;
    checked += 1;
    const enFm = firstFrontmatter(
      fs.readFileSync(path.join(EN_ROOT, rel), "utf8")
    );
    const zhFm = firstFrontmatter(readText(rel));
    if (enFm === null) {
      fail(`English source has no frontmatter: ${rel}`);
      continue;
    }
    if (zhFm === null) {
      fail(`missing frontmatter: ${rel}`);
      continue;
    }

    const enMap = frontmatterMap(enFm);
    const zhMap = frontmatterMap(zhFm);

    const enName = enMap.get("name");
    if (enName === undefined) {
      fail(`English source has no frontmatter name: ${rel}`);
    } else if (zhMap.get("name") === undefined) {
      fail(`missing frontmatter name: ${rel}`);
    } else if (unquote(zhMap.get("name")) !== unquote(enName)) {
      fail(
        `frontmatter name mismatch: ${rel} (expected ${unquote(
          enName
        )}, got ${unquote(zhMap.get("name"))})`
      );
    }

    if (!hasNonEmptyDescription(zhMap.get("description"), zhFm)) {
      fail(`missing or empty frontmatter description: ${rel}`);
    }

    for (const key of ["disable-model-invocation", "argument-hint"]) {
      if (enMap.has(key) !== zhMap.has(key)) {
        fail(
          `frontmatter ${key} presence differs from English source: ${rel}`
        );
      }
    }
  }
  return checked;
});

// --- translated Markdown links --------------------------------------------

// Replace fenced code blocks and inline code spans with spaces while keeping
// byte offsets stable, so links shown as code examples are not checked.
function maskCode(text) {
  const fencePattern = /^\s*(```|~~~)/;
  let inFence = false;
  let masked = "";

  for (const line of text.split(/(?<=\n)/)) {
    if (fencePattern.test(line)) {
      inFence = !inFence;
      masked += line.replace(/[^\n]/g, " ");
      continue;
    }
    if (inFence) {
      masked += line.replace(/[^\n]/g, " ");
      continue;
    }
    masked += line;
  }

  return masked.replace(/`{1,3}[^`\n]*`{1,3}/g, (span) =>
    span.replace(/[^\n]/g, " ")
  );
}

function isSkippedTarget(target) {
  const lower = target.toLowerCase();
  if (
    lower.startsWith("http:") ||
    lower.startsWith("https:") ||
    lower.startsWith("mailto:") ||
    target.startsWith("#")
  ) {
    return true;
  }
  if (target.includes("<") || target.includes(">")) return true;
  if (LINK_SKIP_PREFIXES.some((prefix) => target.startsWith(prefix))) {
    return true;
  }
  // Any other URL scheme or root-absolute path is not a repository-relative link.
  if (/^[A-Za-z][A-Za-z0-9+.-]*:/.test(target)) return true;
  if (target.startsWith("/") || target.startsWith("~")) return true;
  return false;
}

category("translated Markdown relative links", () => {
  let checked = 0;
  for (const rel of zhFiles) {
    const ext = path.extname(rel).toLowerCase();
    if (ext !== ".md" && ext !== ".markdown") continue;
    // Copied Markdown is verbatim from skills/ and may contain template examples.
    if (rel !== "README.md" && isCopied(rel)) continue;

    const absolute = path.join(ZH_ROOT, rel);
    const text = fs.readFileSync(absolute, "utf8");
    const masked = maskCode(text);
    const linkPattern = /\[([^\]]*)\]\(([^)]*)\)/g;
    let match;

    while ((match = linkPattern.exec(masked)) !== null) {
      const rawTarget = match[2].trim().split(/\s+/)[0];
      if (!rawTarget || isSkippedTarget(rawTarget)) continue;

      const withoutSuffix = rawTarget.split("#")[0].split("?")[0];
      if (!withoutSuffix) continue;

      checked += 1;
      const resolved = path.resolve(path.dirname(absolute), withoutSuffix);
      if (!fs.existsSync(resolved)) {
        const line = masked.slice(0, match.index).split("\n").length;
        fail(`broken relative link: ${rel}:${line} -> ${rawTarget}`);
      }
    }
  }
  return checked;
});

// --- package.json ----------------------------------------------------------

category("package.json files includes skills_zh", () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));
  if (!Array.isArray(pkg.files) || !pkg.files.includes("skills_zh")) {
    fail('package.json "files" does not include "skills_zh"');
  }
  return 1;
});

// --- report ----------------------------------------------------------------

const failedCount = failures.length;
console.log("check-skills-zh: skills/ (English) -> skills_zh/ (Chinese mirror)");
console.log(`Repository root: ${ROOT}`);
console.log("");

for (const entry of categories) {
  if (entry.failed === 0) {
    const count = entry.checked > 0 ? ` (${entry.checked} checked)` : "";
    console.log(`PASS  ${entry.label}${count}`);
  } else {
    console.log(`FAIL  ${entry.label} (${entry.failed} failure(s))`);
  }
}

if (failedCount > 0) {
  console.log("");
  console.log(`Failures (${failedCount}):`);
  for (const message of failures) {
    console.log(`  - ${message}`);
  }
  console.log("");
  console.log("Result: FAILED");
  process.exitCode = 1;
} else {
  console.log("");
  console.log("Result: OK");
}
