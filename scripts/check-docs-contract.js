#!/usr/bin/env node
"use strict";

// Read-only consistency checker for the project-docs-workflow contract:
// SKILL.md artifact checklist <-> templates <-> references, plus a simulated
// scaffold materialized into a throwaway temp directory.
// Run from any cwd; paths resolve from this file.

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const SKILL_DIR = path.join(ROOT, "skills", "project-docs-workflow");
const SKILL_MD = path.join(SKILL_DIR, "SKILL.md");
const TEMPLATE_DIR = path.join(SKILL_DIR, "assets", "templates", "project");
const ENTRY_DIR = path.join(SKILL_DIR, "assets", "templates", "entries");
const REFS_DIR = path.join(SKILL_DIR, "references");
const DEPS_DIR = path.join(REFS_DIR, "deps");
const GEN_PRD = path.join(ROOT, "skills", "docs-html-view", "scripts", "gen_prd.py");

const failures = [];
const categories = [];
const skips = [];

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

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

function normalizeEol(text) {
  return text.replace(/\r\n/g, "\n");
}

function walk(dir, base = dir) {
  const result = [];
  if (!fs.existsSync(dir)) return result;
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

function sorted(list) {
  return list.slice().sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}

// --- SKILL.md artifact checklist -------------------------------------------

function checklistRows(text) {
  const lines = normalizeEol(text).split("\n");
  const start = lines.findIndex((line) => /^###\s+Artifact checklist\s*$/.test(line));
  if (start === -1) return null;

  const rows = [];
  for (let i = start + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^#{1,6}\s/.test(line)) break;
    if (!/^\s*\|/.test(line)) continue;
    if (/^\s*\|\s*:?-{2,}/.test(line)) continue;
    const cells = line.split("|").slice(1, -1).map((cell) => cell.trim());
    if (cells.length < 2) continue;
    if (/^Artifact$/i.test(cells[0])) continue;
    rows.push({ artifact: cells[0], template: cells[1] });
  }
  return rows;
}

function templateRows(text) {
  const rows = checklistRows(text);
  if (rows === null) return null;
  const mapped = [];
  for (const row of rows) {
    const raw = row.template.replace(/`/g, "").trim();
    if (!/^assets\/templates\/project\/[^/*\s]+$/.test(raw)) continue;
    const artifactMatch = row.artifact.match(/`([^`]+)`/);
    if (!artifactMatch) {
      fail(`checklist row has no backticked artifact path: ${row.artifact}`);
      continue;
    }
    mapped.push({
      artifact: artifactMatch[1].trim(),
      template: raw,
      templateFile: path.join(SKILL_DIR, raw),
    });
  }
  return mapped;
}

const skillText = fs.existsSync(SKILL_MD) ? normalizeEol(readText(SKILL_MD)) : "";

category("artifact checklist", () => {
  if (!fs.existsSync(SKILL_MD)) {
    fail("missing skills/project-docs-workflow/SKILL.md");
    return 0;
  }
  const rows = templateRows(skillText);
  if (rows === null) {
    fail("SKILL.md has no Artifact checklist table");
    return 0;
  }
  if (rows.length === 0) {
    fail("Artifact checklist has no template rows");
    return 0;
  }

  const seen = new Map();
  let checked = 0;
  for (const row of rows) {
    checked += 1;
    if (!fs.existsSync(row.templateFile)) {
      fail(`mapped template does not exist: ${row.template} (for ${row.artifact})`);
    }
    seen.set(row.template, (seen.get(row.template) || 0) + 1);
  }

  const templateFiles = sorted(walk(TEMPLATE_DIR).map(toPosix));
  for (const rel of templateFiles) {
    checked += 1;
    const key = `assets/templates/project/${rel}`;
    const count = seen.get(key) || 0;
    if (count === 0) {
      fail(`template is not mapped by any checklist row: ${key}`);
    } else if (count > 1) {
      fail(`template is mapped by ${count} checklist rows: ${key}`);
    }
  }
  return checked;
});

// --- references coverage ---------------------------------------------------

function section(text, heading) {
  const lines = normalizeEol(text).split("\n");
  const start = lines.findIndex((line) =>
    new RegExp(`^##\\s+${heading}\\s*$`).test(line)
  );
  if (start === -1) return null;
  const body = [];
  for (let i = start + 1; i < lines.length; i += 1) {
    if (/^##\s+/.test(lines[i])) break;
    body.push(lines[i]);
  }
  return body.join("\n");
}

function bulletsMentioning(text, needle) {
  const lines = normalizeEol(text).split("\n");
  const result = [];
  for (let i = 0; i < lines.length; i += 1) {
    if (!/^\s*[-*]\s+/.test(lines[i])) continue;
    if (!lines[i].includes(needle)) continue;
    const parts = [lines[i]];
    for (let j = i + 1; j < lines.length; j += 1) {
      if (/^\s*[-*]\s+/.test(lines[j]) || /^#{1,6}\s/.test(lines[j])) break;
      if (lines[j].trim() === "") break;
      parts.push(lines[j]);
    }
    result.push(parts.join("\n"));
  }
  return result;
}

function referenceTexts() {
  const files = [SKILL_MD];
  for (const rel of walk(SKILL_DIR)) {
    files.push(path.join(SKILL_DIR, rel));
  }
  files.push(path.join(ROOT, "README.md"));
  return files.filter((file) => fs.existsSync(file));
}

category("references coverage", () => {
  let checked = 0;

  const refSection = section(skillText, "References");
  const topRefs = sorted(
    fs.existsSync(REFS_DIR)
      ? fs
          .readdirSync(REFS_DIR, { withFileTypes: true })
          .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
          .map((entry) => entry.name)
      : []
  );

  if (refSection === null) {
    fail("SKILL.md has no ## References section");
  }
  for (const name of topRefs) {
    checked += 1;
    if (refSection !== null && !refSection.includes(`references/${name}`)) {
      fail(`reference not listed in SKILL.md ## References: references/${name}`);
    }
  }

  const depBullets = bulletsMentioning(skillText, "docs/agents/deps/").join("\n");
  const depFiles = sorted(
    fs.existsSync(DEPS_DIR)
      ? fs
          .readdirSync(DEPS_DIR, { withFileTypes: true })
          .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
          .map((entry) => entry.name)
      : []
  );
  for (const name of depFiles) {
    checked += 1;
    if (!depBullets.includes(name)) {
      fail(`dep reference not listed next to docs/agents/deps/: ${name}`);
    }
  }

  const entryFiles = sorted(walk(ENTRY_DIR).map(toPosix));
  const texts = referenceTexts().map((file) => readText(file));
  const wildcard = skillText.includes("assets/templates/entries/*");
  for (const rel of entryFiles) {
    checked += 1;
    const needle = `assets/templates/entries/${rel}`;
    if (!texts.some((text) => text.includes(needle))) {
      // The skill documents the entries directory as a wildcard authoring aid;
      // individual skeletons may be covered by that declaration.
      if (!wildcard) {
        fail(`entry template is not referenced by path: ${needle}`);
      }
    }
  }

  return checked;
});

// --- simulated scaffold ----------------------------------------------------

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

  masked = masked.replace(/`{1,3}[^`\n]*`{1,3}/g, (span) =>
    span.replace(/[^\n]/g, " ")
  );
  return masked.replace(/<!--[\s\S]*?-->/g, (comment) =>
    comment.replace(/[^\n]/g, " ")
  );
}

function isSkippedLink(target) {
  if (!target) return true;
  if (target.startsWith("#")) return true;
  const lower = target.toLowerCase();
  if (lower.startsWith("http:") || lower.startsWith("https:")) return true;
  if (lower.startsWith("mailto:")) return true;
  if (target.startsWith("/") || target.startsWith("~")) return true;
  if (target.includes("<") || target.includes(">")) return true;
  if (/^[A-Za-z][A-Za-z0-9+.-]*:/.test(target)) return true;
  return false;
}

function collectTocDocuments(text) {
  const result = [];
  const lines = normalizeEol(text).split("\n");
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const inline = line.match(/^\s*documents\s*:\s*\[([^\]]*)\]\s*$/);
    if (inline) {
      for (const entry of inline[1].split(",")) {
        const value = entry.trim().replace(/^["']|["']$/g, "");
        if (value) result.push(value);
      }
      continue;
    }
    if (!/^\s*documents\s*:\s*$/.test(line)) continue;
    const baseIndent = line.match(/^\s*/)[0].length;
    for (let j = i + 1; j < lines.length; j += 1) {
      const next = lines[j];
      if (/^\s*#/.test(next) || next.trim() === "") continue;
      const item = next.match(/^(\s*)-\s+(.+?)\s*$/);
      if (!item || item[1].length <= baseIndent) break;
      if (/^[A-Za-z_][A-Za-z0-9_-]*:/.test(item[2])) break;
      const value = item[2].trim().replace(/^["']|["']$/g, "");
      if (value) result.push(value);
    }
  }
  return result;
}

function copyTemplate(scaffold, row) {
  const dest = path.join(scaffold, row.artifact);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(row.templateFile, dest);
}

function scaffoldProject(scaffold, rows) {
  for (const row of rows) {
    copyTemplate(scaffold, row);
  }

  const issueLeaves = [];
  for (const kind of ["bug", "feature", "chore"]) {
    for (const owner of ["human", "agent", "history"]) {
      issueLeaves.push(path.join("docs", "issues", kind, owner));
    }
  }
  for (const owner of ["human", "agent"]) {
    issueLeaves.push(path.join("docs", "issues", "suggestion", owner));
  }
  for (const leaf of issueLeaves) {
    const dir = path.join(scaffold, leaf);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, ".gitkeep"), "");
  }

  const depsDest = path.join(scaffold, "docs", "agents", "deps");
  fs.mkdirSync(depsDest, { recursive: true });
  if (fs.existsSync(DEPS_DIR)) {
    for (const entry of fs.readdirSync(DEPS_DIR, { withFileTypes: true })) {
      if (!entry.isFile()) continue;
      fs.copyFileSync(path.join(DEPS_DIR, entry.name), path.join(depsDest, entry.name));
    }
  }
}

category("simulated scaffold", () => {
  const rows = templateRows(skillText);
  if (rows === null || rows.length === 0) {
    fail("simulated scaffold cannot run without checklist template rows");
    return 0;
  }

  let checked = 0;
  const scaffold = fs.mkdtempSync(path.join(os.tmpdir(), "docs-contract-"));
  try {
    scaffoldProject(scaffold, rows);

    const markdownFiles = sorted(
      walk(scaffold)
        .map(toPosix)
        .filter((rel) => rel.endsWith(".md"))
    );

    // Check A: relative Markdown links resolve inside the scaffold.
    for (const rel of markdownFiles) {
      checked += 1;
      const absolute = path.join(scaffold, rel);
      const masked = maskCode(readText(absolute));
      const linkPattern = /\[([^\]]*)\]\(([^)]*)\)/g;
      let match;
      while ((match = linkPattern.exec(masked)) !== null) {
        const rawTarget = match[2].trim().split(/\s+/)[0];
        if (isSkippedLink(rawTarget)) continue;
        const withoutSuffix = rawTarget.split("#")[0].split("?")[0];
        if (!withoutSuffix) continue;
        // A fresh scaffold has no ADR entries yet; links to example ADR files
        // illustrate the convention and are not materialized targets.
        if (/(^|\/)adr\/\d{4}-[A-Za-z0-9._-]+\.md$/.test(withoutSuffix)) continue;
        const resolved = path.resolve(path.dirname(absolute), withoutSuffix);
        if (!fs.existsSync(resolved)) {
          const line = masked.slice(0, match.index).split("\n").length;
          fail(`broken relative link in scaffold: ${rel}:${line} -> ${rawTarget}`);
        }
      }
    }

    // Check B: explicit documents: paths in docs/toc.yml exist.
    const tocPath = path.join(scaffold, "docs", "toc.yml");
    if (!fs.existsSync(tocPath)) {
      checked += 1;
      fail("scaffold is missing docs/toc.yml");
    } else {
      const documents = collectTocDocuments(readText(tocPath));
      for (const doc of documents) {
        checked += 1;
        if (doc.includes("*")) continue;
        if (!fs.existsSync(path.join(scaffold, doc))) {
          fail(`docs/toc.yml lists a missing document: ${doc}`);
        }
      }
    }

    // Check C: every materialized template carries the provenance marker.
    for (const row of rows) {
      checked += 1;
      const dest = path.join(scaffold, row.artifact);
      if (!fs.existsSync(dest)) continue;
      const head = readText(dest).split("\n").slice(0, 5).join("\n");
      if (!head.includes("模板来源")) {
        fail(`materialized template lacks 模板来源 in first 5 lines: ${row.artifact}`);
      }
    }

    // Check D: the scaffolded AGENTS.md exposes the required pointers.
    checked += 1;
    const agentsPath = path.join(scaffold, "AGENTS.md");
    if (!fs.existsSync(agentsPath)) {
      fail("scaffold is missing AGENTS.md");
    } else {
      const agents = readText(agentsPath);
      const required = [
        "## Agent skills",
        "### Issue tracker",
        "### Domain docs",
        "### Development workflow",
        "docs/agents/testing.md",
      ];
      for (const needle of required) {
        if (!agents.includes(needle)) {
          fail(`scaffolded AGENTS.md is missing: ${needle}`);
        }
      }
    }

    // Check E: the 测试 contract is present on both sides.
    const testSlots = ["## 测试", "- 执行：", "- 临时：", "- 落盘："];
    const testTargets = [
      path.join(scaffold, "docs", "agents", "issues.md"),
      path.join(scaffold, "docs", "agents", "testing.md"),
      path.join(ENTRY_DIR, "issue-entry.md"),
    ];
    for (const file of testTargets) {
      checked += 1;
      const label = file.startsWith(scaffold + path.sep)
        ? path.relative(scaffold, file)
        : path.relative(ROOT, file);
      if (!fs.existsSync(file)) {
        fail(`missing file for 测试 slots: ${label}`);
        continue;
      }
      const text = readText(file);
      for (const slot of testSlots) {
        if (!text.includes(slot)) {
          fail(`${label} is missing 测试 element: ${slot}`);
        }
      }
    }
    for (const name of ["testing.md", "issues.md"]) {
      checked += 1;
      const file = path.join(REFS_DIR, name);
      if (!fs.existsSync(file)) {
        fail(`missing reference for 测试 contract: references/${name}`);
      } else if (!readText(file).includes("## 测试")) {
        fail(`references/${name} is missing the ## 测试 heading`);
      }
    }

    // Check E2: the workflow doc points at the test rules and at the 测试 slot.
    checked += 1;
    const workflowPath = path.join(scaffold, "docs", "agents", "workflow.md");
    if (!fs.existsSync(workflowPath)) {
      fail("scaffold is missing docs/agents/workflow.md");
    } else {
      const workflow = readText(workflowPath);
      for (const needle of ["testing.md", "## 测试"]) {
        if (!workflow.includes(needle)) {
          fail(`docs/agents/workflow.md is missing a test-rules pointer: ${needle}`);
        }
      }
    }

    // Check E3: the metadata stamp is materialized and matches the package version.
    checked += 1;
    const metaPath = path.join(scaffold, "docs", "agents", "metadata.yml");
    if (!fs.existsSync(metaPath)) {
      fail("scaffold is missing docs/agents/metadata.yml");
    } else {
      const meta = readText(metaPath).match(/^version:\s*(\S+)\s*$/m);
      const pkgVersion = JSON.parse(readText(path.join(ROOT, "package.json"))).version;
      if (!meta) {
        fail("scaffold docs/agents/metadata.yml has no version: line");
      } else if (meta[1] !== pkgVersion) {
        fail(
          `scaffold metadata.yml version ${meta[1]} does not match package.json ${pkgVersion}`
        );
      }
    }

    // Check F: published TOC dry run (optional; degrades to SKIP).
    const python = spawnSync("python3", ["-c", "import yaml"], {
      encoding: "utf8",
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
    });
    if (python.error || python.status !== 0 || !fs.existsSync(GEN_PRD)) {
      const reason = !fs.existsSync(GEN_PRD)
        ? "missing skills/docs-html-view/scripts/gen_prd.py"
        : python.error
        ? "python3 unavailable"
        : "PyYAML unavailable";
      skips.push(`SKIP  publish dry-run (${reason})`);
    } else {
      checked += 1;
      // The publication workspace normally exists after project setup; the
      // simulated scaffold only needs the directory itself.
      fs.mkdirSync(path.join(scaffold, "docs", "docsHtmlView"), { recursive: true });
      const run = spawnSync(
        "python3",
        [GEN_PRD, "--project-root", scaffold, "--json"],
        { encoding: "utf8", timeout: 120000, env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" } }
      );
      if (run.error || run.status !== 0) {
        const detail = `${run.stderr || ""}${run.stdout || ""}`
          .trim()
          .split("\n")
          .slice(-5)
          .join(" | ");
        fail(
          `publish dry-run failed (exit ${run.status})${
            detail ? `: ${detail}` : ""
          }`
        );
      }
    }
  } catch (error) {
    fail(`simulated scaffold crashed: ${error && error.message ? error.message : error}`);
  } finally {
    fs.rmSync(scaffold, { recursive: true, force: true });
  }

  return checked;
});

// --- version + mirror baseline ---------------------------------------------

category("version + mirror baseline", () => {
  let checked = 0;
  const pkgPath = path.join(ROOT, "package.json");
  if (!fs.existsSync(pkgPath)) {
    fail("missing package.json");
    return 0;
  }
  const pkg = JSON.parse(readText(pkgPath));
  const version = String(pkg.version || "");
  const parts = version.split(".");
  if (parts.length < 2) {
    fail(`package.json version is not major.minor: ${version}`);
    return 0;
  }
  const token = `v${parts[0]}.${parts[1]}`;

  checked += 1;
  const zhReadmePath = path.join(ROOT, "skills_zh", "README.md");
  if (!fs.existsSync(zhReadmePath)) {
    fail(`missing skills_zh/README.md (expected baseline ${token})`);
  } else {
    const zh = readText(zhReadmePath);
    const baseline = zh
      .split("\n")
      .find((line) => /基线提交/.test(line));
    if (baseline === undefined || !baseline.includes(token)) {
      fail(`skills_zh/README.md baseline row does not contain ${token}`);
    }
  }

  checked += 1;
  const readmePath = path.join(ROOT, "README.md");
  if (!fs.existsSync(readmePath)) {
    fail(`missing README.md (expected mirror snapshot ${token})`);
  } else {
    const readme = readText(readmePath);
    const occurrences = readme.split(token).length - 1;
    if (occurrences < 2) {
      fail(
        `README.md must contain ${token} in both the Chinese and English mirror snapshot lines (found ${occurrences})`
      );
    }
  }

  return checked;
});

// --- metadata contract -----------------------------------------------------

category("metadata contract", () => {
  let checked = 0;
  const templatePath = path.join(TEMPLATE_DIR, "metadata.yml");
  if (!fs.existsSync(templatePath)) {
    fail("missing assets/templates/project/metadata.yml");
    return 0;
  }
  const pkgVersion = String(
    JSON.parse(readText(path.join(ROOT, "package.json"))).version || ""
  );
  const template = readText(templatePath);

  checked += 1;
  const skill = template.match(/^skill:\s*(\S+)\s*$/m);
  if (!skill || skill[1] !== "project-docs-workflow") {
    fail("metadata.yml must declare skill: project-docs-workflow");
  }

  checked += 1;
  const version = template.match(/^version:\s*(\S+)\s*$/m);
  if (!version) {
    fail("metadata.yml has no version: line");
  } else if (version[1] !== pkgVersion) {
    fail(
      `metadata.yml version ${version[1]} does not match package.json ${pkgVersion}`
    );
  }

  checked += 1;
  if (!skillText.includes("docs/agents/metadata.yml")) {
    fail("SKILL.md does not reference docs/agents/metadata.yml");
  }

  const provenance = `project-docs-workflow v${pkgVersion.split(".")[0]}`;
  for (const rel of sorted(walk(TEMPLATE_DIR).map(toPosix))) {
    checked += 1;
    const head = readText(path.join(TEMPLATE_DIR, rel)).split("\n").slice(0, 5).join("\n");
    if (!head.includes(provenance)) {
      fail(
        `template provenance generation is not "${provenance}": assets/templates/project/${rel}`
      );
    }
  }

  return checked;
});

// --- report ----------------------------------------------------------------

const failedCount = failures.length;
console.log("check-docs-contract: project-docs-workflow checklist -> templates -> scaffold");
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

for (const line of skips) {
  console.log(line);
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
