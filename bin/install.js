#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const PKG_ROOT = path.join(__dirname, "..");
const SKILLS_DIR = path.join(PKG_ROOT, "skills");
const MAIN_SKILL = "project-docs-workflow";
const DEFAULT_TARGET = path.join(os.homedir(), ".agents", "skills");

// 可选上游：mattpocock/skills 的完整版依赖 skill。
// 官方安装器是 vercel-labs/skills 提供的 `skills` CLI（npm 包 skills），
// 固定以 `-a <agent> -g` 安装到该 agent 的全局目录（codex 为 ~/.agents/skills）。
const UPSTREAM_REPO = "mattpocock/skills";
const UPSTREAM_DEFAULT_AGENT = "codex";
// 上游安装器要求 Node >= 22.20（本项目不引入 semver 依赖，手工比较 major/minor）。
const UPSTREAM_MIN_NODE = { major: 22, minor: 20 };
// 仅这 8 个依赖 skill 属于上游集合；doc-opt 与主 skill 不属于。
const MATT_DEP_NAMES = [
  "grilling",
  "grill-me",
  "grill-with-docs",
  "domain-modeling",
  "tdd",
  "deepwork",
  "retro",
  "improve-codebase-architecture",
];
const MATT_DEP_SET = new Set(MATT_DEP_NAMES);

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
      "  --with-matt-skills",
      "                 可选：改从上游 mattpocock/skills 安装依赖 skill 的完整版",
      "                 （需 Node >= 22.20；无此 flag 时在交互式终端会询问一次，默认否）",
      "  --matt-agent <name>",
      "                 上游安装使用的 agent（默认 codex，落盘到其全局目录 ~/.agents/skills）",
      "  -h, --help     显示本帮助",
    ].join("\n")
  );
}

function parseArgs(argv) {
  const opts = {
    command: "install",
    target: DEFAULT_TARGET,
    force: false,
    dryRun: false,
    withMattSkills: false,
    mattAgent: UPSTREAM_DEFAULT_AGENT,
  };
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "install" || arg === "check") {
      opts.command = arg;
    } else if (arg === "--force") {
      opts.force = true;
    } else if (arg === "--dry-run") {
      opts.dryRun = true;
    } else if (arg === "--with-matt-skills") {
      opts.withMattSkills = true;
    } else if (arg === "--matt-agent") {
      const value = argv[++i];
      if (!value) {
        fail("--matt-agent 需要一个参数");
      }
      opts.mattAgent = value;
    } else if (arg.startsWith("--matt-agent=")) {
      const value = arg.slice("--matt-agent=".length);
      if (!value) {
        fail("--matt-agent 需要一个参数");
      }
      opts.mattAgent = value;
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

// —— 上游（mattpocock/skills）相关辅助 ——

function existsAt(p) {
  return isDir(p) || isFile(p);
}

// 手工解析 process.versions.node 并与 22.20 比较（不引入 semver 依赖）。
function nodeMeetsUpstream() {
  const parts = String(process.versions.node).split(".");
  const major = parseInt(parts[0], 10) || 0;
  const minor = parseInt(parts[1], 10) || 0;
  if (major !== UPSTREAM_MIN_NODE.major) {
    return major > UPSTREAM_MIN_NODE.major;
  }
  return minor >= UPSTREAM_MIN_NODE.minor;
}

// 同步等待若干毫秒（用于 stdin 非阻塞时的短暂重试，避免忙等）。
function sleepSync(ms) {
  try {
    const sab = new SharedArrayBuffer(4);
    Atomics.wait(new Int32Array(sab), 0, 0, ms);
  } catch (e) {
    /* 忽略：无法等待时直接继续 */
  }
}

// 同步读取 stdin 的一行。仅在已确认 stdin 为 TTY 时调用。
function readLineSync() {
  const buf = Buffer.alloc(1);
  let line = "";
  for (;;) {
    let bytesRead = 0;
    try {
      bytesRead = fs.readSync(0, buf, 0, 1, null);
    } catch (err) {
      if (err && err.code === "EAGAIN") {
        sleepSync(10);
        continue;
      }
      if (err && (err.code === "EOF" || err.code === "ENXIO")) {
        return line;
      }
      throw err;
    }
    if (bytesRead === 0) {
      return line;
    }
    const ch = buf.toString("utf8", 0, 1);
    if (ch === "\n") {
      return line;
    }
    if (ch !== "\r") {
      line += ch;
    }
  }
}

function npxCommand() {
  return process.platform === "win32" ? "npx.cmd" : "npx";
}

// 组装上游命令参数（不含可执行文件名），以便打印或执行。
function buildUpstreamArgs(opts, names) {
  return ["--yes", "skills@latest", "add", UPSTREAM_REPO, "-g", "-y", "-a", opts.mattAgent, "-s"].concat(
    names
  );
}

function quoteArg(arg) {
  return /[\s"]/.test(arg) ? '"' + arg.replace(/"/g, '\\"') + '"' : arg;
}

function upstreamCommandString(opts, names) {
  return [npxCommand()].concat(buildUpstreamArgs(opts, names)).map(quoteArg).join(" ");
}

// 决定是否启用上游安装。仅在 install 且非 dry-run、且 stdin/stdout 均为 TTY 时提示。
function decideUpstream(opts) {
  if (opts.withMattSkills) {
    return true;
  }
  if (opts.command !== "install" || opts.dryRun) {
    return false;
  }
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    return false;
  }
  process.stdout.write("是否从上游安装依赖 skill 的完整版（mattpocock/skills）？[y/N] ");
  let answer = "";
  try {
    answer = readLineSync().trim().toLowerCase();
  } catch (e) {
    answer = "";
  }
  return answer === "y" || answer === "yes";
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

  // 是否启用上游完整版安装（可能触发一次交互式询问，仅限 TTY + install + 非 dry-run）。
  const upstreamEnabled = decideUpstream(opts);

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

  // 可选：先从上游安装 8 个依赖 skill 的完整版。
  // upstreamHandled 记录「本次由上游负责」的名字，这些名字不再复制本包轻量版。
  let upstreamHandled = new Set();
  if (upstreamEnabled) {
    console.log("上游依赖 skill（mattpocock/skills 完整版）：");
    if (opts.target !== DEFAULT_TARGET) {
      console.log(
        "  ⚠ 检测到自定义 --dir：上游安装固定使用 agent 全局目录（" +
          opts.mattAgent +
          " → ~/.agents/skills），无法跟随 --dir；--dir 下的轻量版仍按原逻辑处理。"
      );
    }
    const preexisting = MATT_DEP_NAMES.filter((name) => existsAt(path.join(target, name)));
    const missing = MATT_DEP_NAMES.filter((name) => preexisting.indexOf(name) === -1);
    if (preexisting.length > 0) {
      console.log("  已存在，保留且不提交上游：" + preexisting.join("、"));
    }
    if (missing.length === 0) {
      console.log("  8 个依赖 skill 均已在目标目录，无需上游安装。");
    } else if (opts.dryRun) {
      console.log("  [dry-run] 将执行：" + upstreamCommandString(opts, missing));
      upstreamHandled = new Set(missing);
    } else if (!nodeMeetsUpstream()) {
      console.log(
        "  ⚠ 当前 Node " +
          process.versions.node +
          " < 22.20，无法运行上游安装器；将对缺失项回退轻量版。"
      );
    } else {
      console.log("  将执行：" + upstreamCommandString(opts, missing));
      const res = spawnSync(npxCommand(), buildUpstreamArgs(opts, missing), {
        stdio: "inherit",
        env: Object.assign({}, process.env, { DISABLE_TELEMETRY: "1", DO_NOT_TRACK: "1" }),
      });
      if (res.error) {
        console.log(
          "  ⚠ 上游安装无法执行（" +
            (res.error.code || res.error.message) +
            "）；将对缺失项回退轻量版。"
        );
      } else if (res.status !== 0) {
        console.log("  ⚠ 上游安装失败（退出码 " + res.status + "）；将对缺失项回退轻量版。");
      }
      // 复核：仅把「本次新增」的名字标记为已由上游处理；已存在者走下面的保留逻辑。
      const nowPresent = MATT_DEP_NAMES.filter((name) => existsAt(path.join(target, name)));
      upstreamHandled = new Set(nowPresent.filter((name) => missing.indexOf(name) !== -1));
    }
  }

  // 其他依赖 skill：永不覆盖。
  console.log("依赖 skill：");
  const others = dirs.filter((name) => name !== MAIN_SKILL);
  if (others.length === 0) {
    console.log("  （未发现其他目录）");
  }
  for (const name of others) {
    if (upstreamEnabled && MATT_DEP_SET.has(name) && upstreamHandled.has(name)) {
      console.log(
        (opts.dryRun
          ? "  [dry-run] 将由上游安装完整版，跳过轻量版："
          : "  已由上游安装完整版，跳过轻量版：") + name
      );
      continue;
    }
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
