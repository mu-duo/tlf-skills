#!/usr/bin/env node
"use strict";

// Read-only contract checker for skills/domain-tutor.
// Verifies that the artifact tree, modes, caps and schemas declared in SKILL.md
// are actually backed by references/ and assets/, and that the skill is wired
// into the installer and the package description.
// Run from any cwd; paths resolve from this file.

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SKILL_DIR = path.join(ROOT, "skills", "domain-tutor");
const SKILL_MD = path.join(SKILL_DIR, "SKILL.md");
const ASSET_DIR = path.join(SKILL_DIR, "assets");
const REF_DIR = path.join(SKILL_DIR, "references");

// Artifacts named in SKILL.md §3 and §8, mapped to the template that seeds them.
const ARTIFACT_TEMPLATES = new Map([
  ["index.yml", "index.template.yml"],
  ["metadata.yml", "metadata.template.yml"],
  ["README.md", "readme.template.md"],
  ["graph.yml", "graph.template.yml"],
  ["spine.md", "spine.template.md"],
  ["sources.md", "sources.template.md"],
  ["cheatsheet.md", "cheatsheet.template.md"],
  ["concepts/<id>.md", "concept.template.md"],
  ["sessions/YYYY-MM-DD.md", "session.template.md"],
]);

const REQUIRED_REFS = [
  "session-loop.md",
  "curriculum.md",
  "rubric.md",
  "sources.md",
  "artifacts.md",
];

const MODES = ["start", "learn", "drill", "exam", "cheat", "status"];

// Required top-level keys per YAML template. Checked at column 0, so this is a
// shape check, not a full parser: the repo ships no YAML dependency.
const YAML_SHAPES = new Map([
  ["graph.template.yml", ["version", "domain", "display_name", "language", "updated", "tier_current", "tiers", "edges", "concepts"]],
  ["index.template.yml", ["version", "root", "owner", "updated", "domains"]],
  ["metadata.template.yml", ["skill", "version", "updated"]],
]);

// Numeric caps that must appear in both SKILL.md and the seeding template.
const CAPS = [
  ["400", "concept.template.md"],
  ["800", "spine.template.md"],
  ["60", "readme.template.md"],
];

const failures = [];
const categories = [];

function fail(message) {
  failures.push(message);
}

function category(label, fn) {
  const start = failures.length;
  const checked = fn() || 0;
  categories.push({ label, checked, failed: failures.length - start });
}

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

function exists(rel, base = SKILL_DIR) {
  return fs.existsSync(path.join(base, rel));
}

function topLevelKeys(text) {
  const keys = new Set();
  for (const line of text.replace(/\r\n/g, "\n").split("\n")) {
    const match = line.match(/^([A-Za-z0-9_-]+)\s*:/);
    if (match) keys.add(match[1]);
  }
  return keys;
}

// --- structure -------------------------------------------------------------

category("SKILL.md present", () => {
  if (!fs.existsSync(SKILL_MD)) {
    fail("missing skills/domain-tutor/SKILL.md");
    return 0;
  }
  return 1;
});

if (!fs.existsSync(SKILL_MD)) {
  report();
}

const skillText = readText(SKILL_MD);
const normalizedSkill = skillText.replace(/\r\n/g, "\n");

// --- frontmatter -----------------------------------------------------------

category("SKILL.md frontmatter", () => {
  const match = normalizedSkill.match(/^---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|$)/);
  if (!match) {
    fail("SKILL.md has no frontmatter");
    return 0;
  }
  const name = match[1].match(/^name\s*:\s*(.+)$/m);
  if (!name || name[1].trim().replace(/^["']|["']$/g, "") !== "domain-tutor") {
    fail("frontmatter name is not domain-tutor");
  }
  const description = match[1].match(/^description\s*:\s*(.+)$/m);
  if (!description || description[1].trim().replace(/^["']|["']$/g, "") === "") {
    fail("frontmatter description is empty");
  }
  return 2;
});

// --- artifact templates ----------------------------------------------------

category("artifact templates exist", () => {
  let checked = 0;
  for (const [artifact, template] of ARTIFACT_TEMPLATES) {
    checked += 1;
    const file = path.join(ASSET_DIR, template);
    if (!fs.existsSync(file)) {
      fail(`missing template for ${artifact}: assets/${template}`);
      continue;
    }
    if (fs.statSync(file).size < 100) {
      fail(`template looks empty: assets/${template}`);
    }
  }
  return checked;
});

category("SKILL.md tree matches templates", () => {
  let checked = 0;
  for (const [artifact, template] of ARTIFACT_TEMPLATES) {
    checked += 1;
    const name = path.basename(artifact);
    if (!normalizedSkill.includes(name)) {
      fail(`SKILL.md never names the artifact ${name} (template assets/${template})`);
    }
  }
  return checked;
});

// --- references ------------------------------------------------------------

category("references exist and are linked", () => {
  let checked = 0;
  for (const ref of REQUIRED_REFS) {
    checked += 1;
    if (!exists(path.join("references", ref))) {
      fail(`missing references/${ref}`);
    }
    if (!normalizedSkill.includes(`references/${ref}`)) {
      fail(`SKILL.md does not link references/${ref}`);
    }
  }
  return checked;
});

category("relative links in SKILL.md resolve", () => {
  let checked = 0;
  let inFence = false;
  for (const line of normalizedSkill.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const pattern = /`(references\/[^`]+|assets\/[^`]+)`/g;
    let match;
    while ((match = pattern.exec(line)) !== null) {
      const target = match[1].replace(/\/$/, "");
      if (target.includes("<") || target.includes("*")) continue;
      checked += 1;
      if (!fs.existsSync(path.join(SKILL_DIR, target))) {
        fail(`broken relative reference in SKILL.md: ${target}`);
      }
    }
  }
  return checked;
});

// --- modes -----------------------------------------------------------------

category("six modes declared and described", () => {
  let checked = 0;
  for (const mode of MODES) {
    checked += 1;
    const modeRow = new RegExp(`\\|\\s*\`${mode}\`\\s*\\|`).test(normalizedSkill);
    if (!modeRow) {
      fail(`SKILL.md mode table has no row for \`${mode}\``);
    }
    const loopPath = path.join(REF_DIR, "session-loop.md");
    if (fs.existsSync(loopPath)) {
      const loop = readText(loopPath);
      const hits = loop.split(new RegExp(`\\b${mode}\\b`, "g")).length - 1;
      if (hits < 1) {
        fail(`references/session-loop.md never mentions the \`${mode}\` mode`);
      }
    }
  }
  return checked;
});

// --- caps ------------------------------------------------------------------

category("cap numbers agree between SKILL.md and templates", () => {
  let checked = 0;
  for (const [cap, template] of CAPS) {
    checked += 1;
    if (!normalizedSkill.includes(cap)) {
      fail(`SKILL.md does not state the ${cap} cap (see assets/${template})`);
    }
    const file = path.join(ASSET_DIR, template);
    if (fs.existsSync(file) && !readText(file).includes(cap)) {
      fail(`assets/${template} does not repeat its ${cap} cap`);
    }
  }
  return checked;
});

// --- YAML shape ------------------------------------------------------------

category("YAML templates declare required keys", () => {
  let checked = 0;
  for (const [template, keys] of YAML_SHAPES) {
    checked += 1;
    const file = path.join(ASSET_DIR, template);
    if (!fs.existsSync(file)) {
      fail(`missing assets/${template}`);
      continue;
    }
    const present = topLevelKeys(readText(file));
    for (const key of keys) {
      if (!present.has(key)) {
        fail(`assets/${template} is missing top-level key: ${key}`);
      }
    }
  }
  return checked;
});

// --- distribution wiring ---------------------------------------------------

category("installer and package description mention domain-tutor", () => {
  let checked = 0;

  const installJs = path.join(ROOT, "bin", "install.js");
  checked += 1;
  if (!fs.existsSync(installJs)) {
    fail("missing bin/install.js");
  } else {
    const text = readText(installJs);
    if (!/"domain-tutor"\s*:\s*"domain-tutor"/.test(text)) {
      fail('bin/install.js FIRST_PARTY_DEP_KINDS has no "domain-tutor" entry');
    }
    if (!/KNOWN_LOCAL_KINDS[\s\S]*?"domain-tutor"/.test(text)) {
      fail('bin/install.js KNOWN_LOCAL_KINDS has no "domain-tutor" entry');
    }
  }

  const pkgFile = path.join(ROOT, "package.json");
  checked += 1;
  if (!fs.existsSync(pkgFile)) {
    fail("missing package.json");
  } else {
    const pkg = JSON.parse(readText(pkgFile));
    if (!String(pkg.description || "").includes("domain-tutor")) {
      fail("package.json description does not mention domain-tutor");
    }
    if (!Array.isArray(pkg.files) || !pkg.files.includes("skills")) {
      fail('package.json "files" does not include "skills"');
    }
  }

  checked += 1;
  const readme = path.join(ROOT, "README.md");
  if (!fs.existsSync(readme) || !readText(readme).includes("domain-tutor")) {
    fail("README.md does not mention domain-tutor");
  }

  checked += 1;
  const zhReadme = path.join(ROOT, "skills_zh", "README.md");
  if (!fs.existsSync(zhReadme) || !readText(zhReadme).includes("domain-tutor")) {
    fail("skills_zh/README.md does not mention domain-tutor");
  }

  return checked;
});

// --- report ----------------------------------------------------------------

function report() {
  const failedCount = failures.length;
  console.log("check-domain-tutor: contract for skills/domain-tutor");
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
    return;
  }

  console.log("");
  console.log("Result: OK");
}

report();
