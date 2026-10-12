#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");

const PKG_ROOT = path.join(__dirname, "..");
const SKILLS_DIR = path.join(PKG_ROOT, "skills");
const MAIN_SKILL = "project-docs-workflow";
const DEFAULT_TARGET = path.join(os.homedir(), ".agents", "skills");

// 依赖 skill 的按名解析与 ref 兜底映射。
// 顺序：先按名解析 <target>/<name>/SKILL.md，其次尝试 ref 兜底文件。
// grill-with-docs 的兜底包含 grilling.md 与 domain-modeling.md 两个文件。
const REF_FALLBACKS = {
  grilling: ["grilling.md"],
  "grill-me": ["grilling.md"],
  "grill-with-docs": ["grilling.md", "domain-modeling.md"],
  "domain-modeling": ["domain-modeling.md"],
  tdd: ["tdd.md"],
  deepwork: ["boundaries.md"],
  retro: ["boundaries.md"],
  "doc-opt": ["doc-opt.md"],
  "improve-codebase-architecture": ["boundaries.md"],
};

const REF_NAMES = Object.keys(REF_FALLBACKS);
const DEPS_DIR = path.join(SKILLS_DIR, MAIN_SKILL, "references", "deps");

function usage() {
  console.log(
    [
      "project-docs-workflow 安装器",
      "",
      "用法：",
      "  project-docs-workflow [install] [选项]   安装 skill 到目标目录（默认动作）",
      "  project-docs-workflow check   [选项]     检查依赖 skill 的解析状态",
      "",
      "选项：",
      "  --dir <path>   指定目标 skills 根目录（默认 ~/.agents/skills）",
      "  --force        覆盖已存在的 project-docs-workflow（仅主 skill；依赖仍不覆盖）",
      "  --dry-run      仅打印将执行的操作，不实际写入",
      "  -h, --help     显示本帮助",
    ].join("\n")
  );
}

function parseArgs(argv) {
  const opts = { command: "install", target: DEFAULT_TARGET, force: false, dryRun: false };
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "install" || arg === "check") {
      opts.command = arg;
    } else if (arg === "--force") {
      opts.force = true;
    } else if (arg === "--dry-run") {
      opts.dryRun = true;
    } else if (arg === "--dir") {
      const value = argv[++i];
      if (!value) {
        fail("--dir 需要一个路径参数");
      }
      opts.target = path.resolve(value);
    } else if (arg.startsWith("--dir=")) {
      opts.target = path.resolve(arg.slice("--dir=".length));
    } else if (arg === "-h" || arg === "--help") {
      usage();
      process.exit(0);
    } else if (arg.startsWith("-")) {
      fail("未知选项：" + arg);
    } else {
      positional.push(arg);
    }
  }
  if (positional.length > 0) {
    fail("未知参数：" + positional.join(" "));
  }
  return opts;
}

function fail(message) {
  console.error("错误：" + message);
  process.exit(1);
}

function isDir(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch (e) {
    return false;
  }
}

function isFile(p) {
  try {
    return fs.statSync(p).isFile();
  } catch (e) {
    return false;
  }
}

// 列出 skills/ 下的所有子目录名；缺失时返回空数组（由调用方给出提示）。
function listSkillDirs() {
  if (!isDir(SKILLS_DIR)) {
    return null;
  }
  return fs
    .readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function copySkill(name, dest, dryRun) {
  const src = path.join(SKILLS_DIR, name);
  if (dryRun) {
    console.log("  [dry-run] 将复制 " + name + " → " + dest);
    return;
  }
  fs.cpSync(src, dest, { recursive: true });
  console.log("  ✓ 已安装 " + name + " → " + dest);
}

function runInstall(opts) {
  const dirs = listSkillDirs();
  if (dirs === null || dirs.length === 0) {
    fail(
      "找不到 skills 目录（" +
        SKILLS_DIR +
        "）。请确认已在完整的 npm 包内运行（不要单独复制 bin/）。"
    );
  }
  if (dirs.indexOf(MAIN_SKILL) === -1) {
    fail("缺少主 skill 目录：skills/" + MAIN_SKILL);
  }

  const target = opts.target;
  console.log("目标目录：" + target + (opts.dryRun ? "（dry-run，不会写入）" : ""));
  if (!opts.dryRun) {
    fs.mkdirSync(target, { recursive: true });
  }

  // 主 skill：仅在 --force 时覆盖已存在的版本，否则同样保护用户版本。
  const mainDest = path.join(target, MAIN_SKILL);
  const mainExists = isDir(mainDest) || isFile(mainDest);
  console.log("主 skill：" + MAIN_SKILL);
  if (mainExists && !opts.force) {
    console.log("  同名 skill 已存在，保留用户版本：" + MAIN_SKILL + "（如需覆盖请加 --force）");
  } else if (mainExists && opts.force) {
    if (opts.dryRun) {
      console.log("  [dry-run] 将覆盖 " + MAIN_SKILL + " → " + mainDest);
    } else {
      fs.rmSync(mainDest, { recursive: true, force: true });
      copySkill(MAIN_SKILL, mainDest, false);
    }
  } else {
    copySkill(MAIN_SKILL, mainDest, opts.dryRun);
  }

  // 其他依赖 skill：永不覆盖。
  console.log("依赖 skill：");
  const others = dirs.filter((name) => name !== MAIN_SKILL);
  if (others.length === 0) {
    console.log("  （未发现其他目录）");
  }
  for (const name of others) {
    const dest = path.join(target, name);
    if (isDir(dest) || isFile(dest)) {
      console.log("  同名 skill 已存在，保留用户版本：" + name);
      continue;
    }
    copySkill(name, dest, opts.dryRun);
  }

  if (opts.dryRun) {
    console.log("dry-run 完成，未写入任何文件。");
  } else {
    console.log("安装完成。");
  }
}

function runCheck(opts) {
  const target = opts.target;
  console.log("检查依赖 skill 解析状态（目标目录：" + target + "）：");

  let ok = true;
  for (const name of REF_NAMES) {
    const installed = isFile(path.join(target, name, "SKILL.md"));
    if (installed) {
      console.log("  " + name + "：按名可解析（skill 已安装）");
      continue;
    }
    const fallbacks = REF_FALLBACKS[name] || [];
    const hit = fallbacks.find((file) => isFile(path.join(DEPS_DIR, file)));
    if (hit) {
      console.log("  " + name + "：ref 兜底可用（references/deps/" + hit + "）");
      continue;
    }
    ok = false;
    console.log(
      "  " + name + "：无法解析（未安装，且缺少 ref 兜底：" +
        fallbacks.map((f) => "references/deps/" + f).join("、") +
        "）"
    );
  }

  if (ok) {
    console.log("全部依赖 skill 均已解析。");
    process.exit(0);
  } else {
    console.log("存在无法解析的依赖 skill。");
    process.exit(1);
  }
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.command === "check") {
    runCheck(opts);
  } else {
    runInstall(opts);
  }
}

main();
