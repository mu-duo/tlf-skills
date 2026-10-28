#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const PKG_ROOT = path.join(__dirname, "..");
const SKILLS_DIR = path.join(PKG_ROOT, "skills");
const SKILLS_ZH_DIR = path.join(PKG_ROOT, "skills_zh");
const MAIN_SKILL = "project-docs-workflow";
const DEFAULT_TARGET = path.join(os.homedir(), ".agents", "skills");
// 安装清单：记录本包每次安装处理过的 skill 及其归属，供 uninstall 精确卸载。
const MANIFEST_NAME = ".project-docs-workflow.install.json";
const PKG_VERSION = require(path.join(PKG_ROOT, "package.json")).version;

// 可选上游：mattpocock/skills 的完整版依赖 skill。
// 官方安装器是 vercel-labs/skills 提供的 `skills` CLI（npm 包 skills），以 `-a <agent> -g`
// 安装到该 agent 的全局目录（codex 为 ~/.agents/skills）；它不支持 --dir，因此只有能证明目标
// 就是 codex 默认全局目录时才允许调用上游。
const UPSTREAM_REPO = "mattpocock/skills";
const UPSTREAM_DEFAULT_AGENT = "codex";
// 上游安装器要求 Node >= 22.20（本项目不引入 semver 依赖，手工比较 major/minor）。
const UPSTREAM_MIN_NODE = { major: 22, minor: 20 };
// 仅这 8 个依赖 skill 受上游支持；doc-opt、docs-html-view、docs-docx-view、lite-task 与主 skill 不属于。
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

// 第一方 skill：本包自带、随包版本分发的 skill（共五项）。这是一份**显式名单**——未列出的
// 目录一律不是第一方，也不随包分发（未知包内目录仅提示忽略）。外部依赖（8 个上游名）不随包
// 分发：默认保留已存在的独立安装，缺失时使用主 skill 内部回退文档（references/deps）；只有
// --with-matt-skills 才通过 npx 安装/更新独立完整版。kind 与名单同源。
const FIRST_PARTY_DEP_KINDS = {
  "doc-opt": "doc-opt",
  "docs-html-view": "docs-html-view",
  "docs-docx-view": "docs-docx-view",
  "lite-task": "lite-task",
};
const FIRST_PARTY_NAMES = [MAIN_SKILL].concat(Object.keys(FIRST_PARTY_DEP_KINDS));
const FIRST_PARTY_SET = new Set(FIRST_PARTY_NAMES);
// 清单里认可的「本包本地安装」kind（含历史 kind：分类前 doc-opt 可能被记作 lite）。
const KNOWN_LOCAL_KINDS = new Set([
  "main",
  "lite",
  "doc-opt",
  "docs-html-view",
  "docs-docx-view",
  "lite-task",
]);

function depKind(name) {
  return FIRST_PARTY_DEP_KINDS[name] || "lite";
}

function kindFor(name) {
  return name === MAIN_SKILL ? "main" : depKind(name);
}

// 保守判定清单归属：只有明确记录为本包本地安装（installed/forced 且 kind 为已知本地 kind，
// 非 upstream）才算「已接管」。缺失/损坏/未知/skipped 一律不接管（改为保留）。
function isOwnedLocal(entry) {
  if (!entry || typeof entry !== "object") {
    return false;
  }
  if (entry.action !== "installed" && entry.action !== "forced") {
    return false;
  }
  return KNOWN_LOCAL_KINDS.has(entry.kind);
}

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
      "用法说明：运行 `npx @tanlinfeng/project-docs-workflow@<version> install` 选择安装器/源码版本",
      "（`npm i` 只是把包装进 node_modules，不会运行本工具）。所选旧版本自带它当时的安装器，",
      "行为可能与当前不同，这里只保证兼容、不承诺升级。",
      "普通安装只同步本包自带的第一方 skill（project-docs-workflow、doc-opt、docs-html-view、docs-docx-view、lite-task）：",
      "缺失则安装；已由本包接管则用当前包内版本全量替换（会移除其中多余/过期文件）；",
      "未接管条目、符号链接（含悬空）默认保留。外部依赖不再随包分发：默认保留已存在的独立安装，",
      "缺失时使用主 skill 内部回退文档（references/deps），功能可用、无需独立目录。",
      "默认安装英文源 skills/；--zh 改为安装中文镜像 skills_zh/。两种语言的 skill 同名、互斥，",
      "同一目标一次只保留一种语言；再次运行另一种语言即可切换（仅 install 支持）。",
      "可选：--with-matt-skills 通过 npx 安装/更新独立完整版（默认不安装、不复制）。源项目文档不受影响。",
      "",
      "用法：",
      "  project-docs-workflow [install] [选项]   安装/同步包内第一方 skill（默认动作）",
      "  project-docs-workflow check   [选项]     检查依赖 skill 的解析状态",
      "  project-docs-workflow uninstall [选项]   依据安装清单卸载本包安装的 skill",
      "",
      "选项：",
      "  --dir <path>   指定目标 skills 根目录（默认 ~/.agents/skills）",
      "  --zh           从中文镜像 skills_zh/ 安装第一方 skill（默认英文源 skills/）",
      "                 两种语言 skill 同名、互斥；再次运行另一种语言即可切换；仅 install 支持",
      "  --force        安装：覆盖并接管所有第一方 skill（含替换已存在的符号链接本身，不动其指向）；",
      "                 不影响外部依赖；uninstall：非交互确认（非 TTY 下必须显式传入）",
      "  --dry-run      仅打印将执行的操作（与真实运行相同决策），不写入、不读 stdin、不调用上游",
      "  --with-matt-skills",
      "                 可选增强（显式授权）：通过 npx 安装缺失 + 更新已存在的外部依赖完整版。",
      "                 仅当可证明目标是 codex 默认全局目录 ~/.agents/skills 时可用（不支持 --dir 别名），",
      "                 需 Node >= 22.20；此 flag 下不询问。每项独立完成，非整套事务。",
      "                 成功项记入清单（kind=upstream），之后 uninstall 会一并移除；本地改动可能被覆盖。",
      "                 不加此 flag 时：不安装、不复制任何独立依赖；内部回退已可用。",
      "  --matt-agent <name>",
      "                 上游使用的 agent（仅支持默认 codex；其它值无法证明目标，会拒绝）",
      "  -h, --help     显示本帮助",
      "",
      "示例：",
      "  project-docs-workflow                          # 安装/同步到默认 ~/.agents/skills（仅第一方）",
      "  project-docs-workflow --zh                     # 安装中文镜像（默认 en；两种语言同名互斥）",
      "  project-docs-workflow --dir <path> --dry-run   # 预演到指定目录（不写入）",
      "  project-docs-workflow --force                  # 接管/替换所有第一方 skill",
      "  project-docs-workflow --with-matt-skills       # 可选：安装缺失 + 更新已存在的完整版依赖",
      "  project-docs-workflow check                    # 检查依赖解析状态（外部或内部回退）",
      "  project-docs-workflow uninstall --dry-run      # 卸载预演",
      "  project-docs-workflow uninstall --force        # 非交互卸载（只删本包装的）",
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
    lang: "en",
  };
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "install" || arg === "check" || arg === "uninstall") {
      opts.command = arg;
    } else if (arg === "--zh") {
      opts.lang = "zh";
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

// 存在性用 lstat（不跟随符号链接），因此悬空链接也算「存在」，不会被误判为缺失而覆盖。
function lexists(p) {
  try {
    fs.lstatSync(p);
    return true;
  } catch (e) {
    return false;
  }
}

function isSymlink(p) {
  try {
    return fs.lstatSync(p).isSymbolicLink();
  } catch (e) {
    return false;
  }
}

function readlinkSafe(p) {
  try {
    return fs.readlinkSync(p);
  } catch (e) {
    return "?";
  }
}

// 解析真实路径；路径尚不存在时，解析“最近存在的祖先”再拼接剩余部分（保持符号链接语义）。
// 无法可靠解析（悬空/循环符号链接、权限等）时 fail closed，绝不退化为词法路径。
function resolveRealOrFail(p) {
  const abs = path.resolve(p);
  try {
    return fs.realpathSync(abs);
  } catch (e) {
    if (!e || e.code !== "ENOENT" || isSymlink(abs)) {
      fail("拒绝：无法可靠解析路径（" + abs + "）：" + (e && (e.code || e.message)));
    }
    const parent = path.dirname(abs);
    if (parent === abs) {
      fail("拒绝：无法可靠解析路径（" + abs + "）。");
    }
    return path.join(resolveRealOrFail(parent), path.basename(abs));
  }
}

// child 与 parent 相同或在 parent 之内（词法判定）。
function isSameOrInside(child, parent) {
  const rel = path.relative(parent, child);
  return rel === "" || (rel !== ".." && !rel.startsWith(".." + path.sep) && !path.isAbsolute(rel));
}

// 源 / 目标重叠：目标不得与包内任一语言源目录相同、在其内、或包含它（含经符号链接解析后）。
function assertNoSourceTargetOverlap(target) {
  const targetReal = resolveRealOrFail(target);
  for (const root of [SKILLS_DIR, SKILLS_ZH_DIR]) {
    if (!lexists(root)) {
      continue;
    }
    const rootReal = resolveRealOrFail(root);
    if (isSameOrInside(targetReal, rootReal) || isSameOrInside(rootReal, targetReal)) {
      fail(
        "拒绝：目标目录与包内 skill 源目录重叠（" +
          target +
          " vs " +
          root +
          "）。请选择包外目录（例如 ~/.agents/skills），避免复制/替换包自身源码。"
      );
    }
  }
}

// 仅在目标目录内使用的唯一工具路径（前缀可辨识，便于只清理本工具产生的临时项）。
function uniqueToolPath(parent, name, tag) {
  for (;;) {
    const p = path.join(
      parent,
      ".pdw-" + name + "-" + tag + "-" + Math.random().toString(36).slice(2, 10)
    );
    if (!lexists(p)) {
      return p;
    }
  }
}

function cleanupToolPath(p) {
  try {
    fs.rmSync(p, { recursive: true, force: true });
  } catch (e) {
    /* 尽力清理；不因清理失败中断 */
  }
}

// 递归复制（用可捕获的 JS 调用，避免 Node 原生 cp 在源不可读时硬中止进程而漏清理）。
function copyTree(src, dest) {
  const st = fs.lstatSync(src);
  if (st.isSymbolicLink()) {
    fs.symlinkSync(fs.readlinkSync(src), dest);
    return;
  }
  if (st.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const name of fs.readdirSync(src)) {
      copyTree(path.join(src, name), path.join(dest, name));
    }
    return;
  }
  fs.copyFileSync(src, dest);
}

// 全目录替换（单项，非整套事务）：先把源完整复制到同目录下的唯一临时路径，成功后才把旧
// 条目移开并换上准备好的副本；失败时恢复旧条目，无法恢复则保留备份并报告其路径。
// 绝不在复制成功之前删除现有条目。旧条目为符号链接时，rename/rm 只作用于链接本身。
function replaceFirstPartyDir(name, dest, sourceRoot) {
  const src = path.join(sourceRoot, name);
  const parent = path.dirname(dest);
  const staged = uniqueToolPath(parent, name, "new");
  try {
    copyTree(src, staged);
  } catch (e) {
    cleanupToolPath(staged);
    fail("准备 " + name + " 的新版本失败（原条目未改动）：" + e.message);
  }
  let backup = null;
  try {
    if (lexists(dest)) {
      backup = uniqueToolPath(parent, name, "old");
      fs.renameSync(dest, backup);
    }
    fs.renameSync(staged, dest);
  } catch (e) {
    let restored = false;
    if (!lexists(dest) && backup && lexists(backup)) {
      try {
        fs.renameSync(backup, dest);
        restored = true;
      } catch (e2) {
        /* 保留备份以便人工恢复 */
      }
    }
    cleanupToolPath(staged);
    // 错误路径只保留备份：绝不因为 dest 恰好存在就删除备份（那样会丢失原条目）。
    // 只有成功把备份重命名回 dest 时，备份才被“消耗”掉。
    let note = "";
    if (backup && lexists(backup)) {
      note = "；原条目已保留在 " + backup + "（如需恢复请手动移回）";
    }
    fail("替换 " + name + " 失败" + (restored ? "（已恢复原条目）" : note) + "：" + e.message);
  }
  if (backup && lexists(backup)) {
    cleanupToolPath(backup);
  }
}

// 单个第一方 skill 的安装/同步决策。dry-run 走完全相同的分支，但不复制、不建临时项。
function installFirstParty(name, target, opts, prevEntries, record, sourceRoot) {
  const dest = path.join(target, name);
  const exists = lexists(dest);
  const symlink = exists && isSymlink(dest);
  const prev = prevEntries[name];
  const owned = isOwnedLocal(prev);

  if (!exists) {
    if (opts.dryRun) {
      console.log("  [dry-run] 将安装 " + name + " → " + dest);
    } else {
      replaceFirstPartyDir(name, dest, sourceRoot);
      console.log("  ✓ 已安装 " + name + " → " + dest);
    }
    record(name, { kind: kindFor(name), lang: opts.lang, action: "installed" });
    return;
  }

  // 第一方符号链接：默认永远保留（即使清单记为本包安装）。--force 才替换链接本身。
  if (symlink && !opts.force) {
    console.log(
      "  ⚠ 保留第一方符号链接（未改动，指向 " +
        readlinkSafe(dest) +
        "）：" +
        name +
        "（如需替换链接本身、不动其指向，请加 --force）"
    );
    record(name, { kind: kindFor(name), action: "skipped" });
    return;
  }

  // 现有条目但未被本包接管（清单缺失/损坏/未知/skipped）：默认保留并提示 --force。
  if (!owned && !opts.force) {
    console.log(
      "  ⚠ 保留现有条目（非本包安装，或清单缺失/损坏/未知）：" +
        name +
        "（如需覆盖并接管，请加 --force）"
    );
    record(name, { kind: kindFor(name), action: "skipped" });
    return;
  }

  const action = opts.force ? "forced" : prev && prev.action === "forced" ? "forced" : "installed";
  if (owned && !opts.force) {
    console.log(
      "  ⚠ 更新第一方 skill " +
        name +
        "：managed 安装副本内的本地改动将丢失；项目文档不受影响。"
    );
  } else {
    console.log(
      "  ⚠ --force 接管并替换现有条目：" + name + (symlink ? "（仅替换符号链接本身）" : "")
    );
  }
  if (opts.dryRun) {
    console.log("  [dry-run] 将替换 " + name + " → " + dest + (symlink ? "（仅链接本身）" : ""));
    record(name, { kind: kindFor(name), lang: opts.lang, action });
    return;
  }
  replaceFirstPartyDir(name, dest, sourceRoot);
  console.log("  ✓ 已" + (owned && !opts.force ? "更新" : "接管") + " " + name + " → " + dest);
  record(name, { kind: kindFor(name), lang: opts.lang, action });
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

// Windows 上 Node 禁止不经 shell 直接 spawn .bat/.cmd（CVE-2024-27980，Node >= 18.20.2 起
// 直接返回 EINVAL）。仅在 win32 下启用 shell；shell 会重新解释参数，因此动态参数必须先经
// isSafeCliToken 校验，固定参数由代码常量保证安全。
function spawnNpxSync(args, options) {
  const opts = Object.assign({}, options);
  if (process.platform === "win32") {
    opts.shell = true;
  }
  return spawnSync(npxCommand(), args, opts);
}

// 允许作为 shell 参数传递的动态 token（agent/skill 名）：仅字母数字与 . _ -。
function isSafeCliToken(value) {
  return typeof value === "string" && /^[A-Za-z0-9._-]+$/.test(value);
}

// 组装上游命令参数（不含可执行文件名），以便打印或执行。--json 必需：非 JSON 输出可能在
// 部分失败时仍以 0 退出。窄命令，不使用 -a '*'/-s '*'/--all；单目标始终 copy，无需 --copy。
function buildUpstreamArgs(opts, names) {
  return ["--yes", "skills@latest", "add", UPSTREAM_REPO, "-g", "-y", "-a", opts.mattAgent, "-s"]
    .concat(names)
    .concat(["--json"]);
}

function quoteArg(arg) {
  return /[\s"]/.test(arg) ? '"' + arg.replace(/"/g, '\\"') + '"' : arg;
}

function upstreamCommandString(opts, names) {
  return [npxCommand()].concat(buildUpstreamArgs(opts, names)).map(quoteArg).join(" ");
}

// 上游目标可行性：只有可证明目标就是 codex 默认全局目录（~/.agents/skills）时才允许调用上游。
// 其它 agent、或解析后不等于默认目录的 --dir，都无法证明上游落点，返回 ok:false。
function upstreamTargetCheck(opts) {
  if (opts.mattAgent !== UPSTREAM_DEFAULT_AGENT) {
    return {
      ok: false,
      reason:
        "所选 agent '" +
        opts.mattAgent +
        "' 的全局 skills 目录未知（仅已知 codex → ~/.agents/skills）",
    };
  }
  const targetReal = resolveRealOrFail(opts.target);
  const defaultReal = resolveRealOrFail(DEFAULT_TARGET);
  if (targetReal !== defaultReal) {
    return {
      ok: false,
      reason:
        "目标目录 " +
        opts.target +
        " 解析后不等于 codex 全局目录 " +
        DEFAULT_TARGET +
        "（上游安装不支持 --dir）",
    };
  }
  return { ok: true, reason: "" };
}

// 供用户手动执行的窄命令（不含 --json；不经本安装器）。
function manualUpstreamCommand(names) {
  const list = names && names.length ? names.join(" ") : "<names>";
  return (
    "npx --yes skills@latest add " +
    UPSTREAM_REPO +
    " -g -y -a " +
    UPSTREAM_DEFAULT_AGENT +
    " -s " +
    list
  );
}

function parseUpstreamJson(stdout) {
  if (typeof stdout !== "string") {
    return null;
  }
  // 严格：官方 --json 输出应是完整的 JSON 数组；不从噪声里截取，避免歧义结果被当成成功。
  try {
    const v = JSON.parse(stdout.trim());
    return Array.isArray(v) ? v : null;
  } catch (e) {
    return null;
  }
}

function realpathSoft(p) {
  try {
    return fs.realpathSync(p);
  } catch (e) {
    return null;
  }
}

// 校验 --json 结果：契约必须明确——数组、条目均为对象、name 非空且都在 requested 内、不重复；
// requested 中每个名字必须是 installed、source/scope/agents 正确、mode=copy、path 为非空字符串
// 且解析后等于目标目录、且 SKILL.md 实际存在。path 必填（缺 path 不因 SKILL.md 存在就放行）。
// 契约异常写入 reasons 的 "__contract__"。返回 {ok:Set, reasons:Map}。
function validateUpstreamResults(parsed, requested, target) {
  const ok = new Set();
  const reasons = new Map();
  if (!Array.isArray(parsed)) {
    for (const n of requested) {
      reasons.set(n, "结果不可解析（非数组）");
    }
    return { ok, reasons };
  }
  const reqSet = new Set(requested);
  const byName = new Map();
  for (const el of parsed) {
    if (!el || typeof el !== "object") {
      reasons.set("__contract__", "结果含非对象条目");
      return { ok, reasons };
    }
    if (typeof el.name !== "string" || !el.name) {
      reasons.set("__contract__", "结果含无 name 条目（status=" + String(el.status) + "）");
      return { ok, reasons };
    }
    if (!reqSet.has(el.name)) {
      reasons.set("__contract__", "结果含未请求的条目：" + el.name);
      return { ok, reasons };
    }
    if (byName.has(el.name)) {
      reasons.set("__contract__", "结果含重复条目：" + el.name);
      return { ok, reasons };
    }
    byName.set(el.name, el);
  }
  for (const name of requested) {
    const el = byName.get(name);
    if (!el) {
      reasons.set(name, "结果缺少该条目");
      continue;
    }
    if (el.status !== "installed") {
      reasons.set(name, "status=" + String(el.status) + (el.reason ? "（" + el.reason + "）" : ""));
      continue;
    }
    if (el.source !== UPSTREAM_REPO) {
      reasons.set(name, "source=" + String(el.source));
      continue;
    }
    if (el.scope !== "global") {
      reasons.set(name, "scope=" + String(el.scope));
      continue;
    }
    const agents = Array.isArray(el.agents) ? el.agents.map((a) => String(a).toLowerCase()) : [];
    if (agents.indexOf("codex") === -1) {
      reasons.set(name, "agents=" + JSON.stringify(el.agents));
      continue;
    }
    if (String(el.mode).toLowerCase() !== "copy") {
      reasons.set(name, "mode=" + String(el.mode));
      continue;
    }
    if (typeof el.path !== "string" || !el.path) {
      reasons.set(name, "缺少 path");
      continue;
    }
    const expected = path.join(target, name);
    if (!isFile(path.join(expected, "SKILL.md"))) {
      reasons.set(name, "目标缺少 SKILL.md（不声称成功）");
      continue;
    }
    const p = realpathSoft(path.resolve(el.path));
    const e = realpathSoft(expected);
    if (!p || !e || p !== e) {
      reasons.set(name, "path 与目标不符：" + el.path);
      continue;
    }
    ok.add(name);
  }
  return { ok, reasons };
}

function printBounded(label, text) {
  const lines = String(text || "").split(/\r?\n/).filter((l) => l.trim());
  if (lines.length === 0) {
    return;
  }
  const head = lines.slice(0, 8);
  console.log("  " + label);
  for (const l of head) {
    console.log("    " + l.slice(0, 300));
  }
  if (lines.length > head.length) {
    console.log("    …（其余 " + (lines.length - head.length) + " 行略）");
  }
}

// 执行上游完整版安装并严格校验 --json，按名字分别处理（不再有任何独立轻量版回退/重建）：
// - installed 且校验通过 → 记 upstream（成功项不清理）；
// - 原本缺失的失败项 → 只清理「本次尝试才新建」的路径（阶段开始时不存在），报错；
// - 原本已存在的失败项 → 不删除、不重建，保留原归属，报错（可能已有上游部分写入）。
function runUpstreamPhase(opts, target, existingNames, missingNames, record) {
  const requested = MATT_DEP_NAMES.filter(
    (n) => existingNames.indexOf(n) !== -1 || missingNames.indexOf(n) !== -1
  );
  const externalHandled = new Set();
  // 阶段开始时的存在性快照：仅用于判定「本次尝试新建」的路径，避免清理既有目录。
  const preExisting = new Set(requested.filter((n) => lexists(path.join(target, n))));
  if (opts.dryRun) {
    console.log("  [dry-run] 将执行：" + upstreamCommandString(opts, requested));
    console.log(
      "  [dry-run] 校验 --json 成功项记为 upstream；缺失失败项仅清理本次新建路径；已存在失败项报错；无独立轻量版回退。"
    );
    for (const n of requested) {
      externalHandled.add(n);
    }
    return { externalHandled, hardFail: false };
  }
  console.log("  将执行：" + upstreamCommandString(opts, requested));
  let parsed = null;
  let execFail = null;
  let status = 0;
  const res = spawnNpxSync(buildUpstreamArgs(opts, requested), {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    maxBuffer: 32 * 1024 * 1024,
    env: Object.assign({}, process.env, { DISABLE_TELEMETRY: "1", DO_NOT_TRACK: "1" }),
  });
  if (res.error) {
    execFail = "上游命令无法执行（" + (res.error.code || res.error.message) + "）";
  } else {
    status = typeof res.status === "number" ? res.status : 1;
    if (res.stderr) {
      printBounded("上游 stderr：", res.stderr);
    }
    parsed = parseUpstreamJson(res.stdout);
    if (parsed === null) {
      execFail = "上游 --json 输出无法严格解析为数组";
    }
  }
  const validation = validateUpstreamResults(parsed, requested, target);
  const contractErr = validation.reasons.get("__contract__") || null;
  let hardFail = false;
  for (const name of requested) {
    if (validation.ok.has(name)) {
      record(name, { kind: "upstream", action: "installed", agent: opts.mattAgent });
      console.log("  ✓ 上游完成：" + name);
      continue;
    }
    hardFail = true;
    // 子进程未能执行或输出无法解析时，validate 的逐项「结果不可解析」是次生噪声：
    // 优先报真实执行错误，避免把 EINVAL 等根因掩盖成解析失败。
    const execReason = parsed === null && execFail ? execFail : "";
    const why =
      execReason || validation.reasons.get(name) || contractErr || execFail || "未知原因";
    if (missingNames.indexOf(name) !== -1) {
      // 原本缺失：只清理本次尝试新建的路径（阶段开始时不存在），绝不触碰既有目录。
      if (!preExisting.has(name) && lexists(path.join(target, name))) {
        cleanupToolPath(path.join(target, name));
        console.log(
          "  ✗ 可选上游安装未完成（" +
            name +
            "：" +
            why +
            "）；已清理本次新建的部分安装路径；未安装独立依赖，内部回退文档仍可用。"
        );
      } else {
        console.log(
          "  ✗ 可选上游安装未完成（" +
            name +
            "：" +
            why +
            "）；未新建路径，未安装独立依赖，内部回退文档仍可用。"
        );
      }
    } else {
      console.log(
        "  ✗ 更新已存在依赖失败（" +
          name +
          "：" +
          why +
          "）；不删除、不重建，保留原清单归属，不声称已更新。"
      );
    }
  }
  // 阶段处理过的名字一律标记为已处理：外层不得再对任何名字做复制/回退。
  for (const name of requested) {
    externalHandled.add(name);
  }
  // 整体失败：非零退出或契约异常时，即便有逐项成功也 hardFail；已确认成功项仍保留归属。
  if (status !== 0) {
    hardFail = true;
    console.log(
      "  ⚠ 上游退出码 " + status + "：整体按未成功处理（已确认成功的项仍记录归属，不声称全部完成）。"
    );
  }
  if (contractErr) {
    hardFail = true;
    console.log("  ⚠ 上游结果契约异常：" + contractErr + "（拒绝按歧义结果判定成功）。");
  }
  if (execFail) {
    console.log("  ⚠ " + execFail);
  }
  return { externalHandled, hardFail };
}

function promptUpstreamMissing(missingNames) {
  process.stdout.write(
    "是否可选安装上游完整版依赖 skill（mattpocock/skills）：" +
      missingNames.join("、") +
      "？[y/N]（不加装时内部回退已可用） "
  );
  let answer = "";
  try {
    answer = readLineSync().trim().toLowerCase();
  } catch (e) {
    answer = "";
  }
  return answer === "y" || answer === "yes";
}

// 列出指定语言源目录下的所有子目录名；缺失时返回 null（由调用方给出提示）。
function listSkillDirs(root) {
  if (!isDir(root)) {
    return null;
  }
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

// —— 安装清单（manifest）——

function manifestPath(target) {
  return path.join(target, MANIFEST_NAME);
}

function loadManifest(target) {
  const p = manifestPath(target);
  if (!isFile(p)) {
    return null;
  }
  try {
    const data = JSON.parse(fs.readFileSync(p, "utf8"));
    if (data && typeof data === "object" && data.entries && typeof data.entries === "object") {
      return data;
    }
  } catch (e) {
    /* 忽略：清单损坏时按缺失处理 */
  }
  return null;
}

// 读取清单状态：ok / symlink / missing / invalid。symbolic 一律拒绝（不跟随）；invalid（解析
// 失败或结构不对，entries 非普通对象）按未接管处理，不猜测。
function readManifest(target) {
  const p = manifestPath(target);
  if (!lexists(p)) {
    return { status: "missing", entries: {} };
  }
  if (isSymlink(p)) {
    return { status: "symlink", entries: {} };
  }
  try {
    const data = JSON.parse(fs.readFileSync(p, "utf8"));
    if (
      data &&
      typeof data === "object" &&
      !Array.isArray(data) &&
      data.entries &&
      typeof data.entries === "object" &&
      !Array.isArray(data.entries)
    ) {
      return { status: "ok", entries: data.entries };
    }
  } catch (e) {
    /* 视为 invalid */
  }
  return { status: "invalid", entries: {} };
}

// 合并新旧条目：归属一旦记在本包名下（installed/forced），后续因「已存在」而 skip 时不被降级；
// 而初次即为 skipped（安装时已存在、非本包安装）的名字始终保持 skipped。
function mergeEntries(prev, fresh) {
  const out = Object.assign({}, prev);
  for (const name of Object.keys(fresh)) {
    const f = fresh[name];
    const p = out[name];
    if (f.action === "skipped" && p && p.action !== "skipped") {
      continue;
    }
    out[name] = f;
  }
  return out;
}

// 从清单中读取上一次第一方安装语言：任一第一方条目带 lang 即采用（兼容无 lang 的旧清单）。
function readPreviousLang(entries) {
  for (const name of Object.keys(entries || {})) {
    if (!FIRST_PARTY_SET.has(name)) {
      continue;
    }
    const lang = entries[name] && entries[name].lang;
    if (typeof lang === "string" && lang) {
      return lang;
    }
  }
  return null;
}

function writeManifest(target, entries) {
  const p = manifestPath(target);
  // 写入前再核对一次：若中途出现符号链接，拒绝写入，绝不跟随覆盖其指向的文件。
  if (isSymlink(p)) {
    fail("拒绝：安装清单是符号链接（" + p + "），不写入（请先手动处理）。");
  }
  const data = {
    version: PKG_VERSION,
    target: path.resolve(target),
    updatedAt: new Date().toISOString(),
    entries,
  };
  fs.writeFileSync(p, JSON.stringify(data, null, 2) + "\n");
  console.log("已写入安装清单：" + p);
}

function removeManifest(target) {
  const p = manifestPath(target);
  if (!isFile(p)) {
    return;
  }
  try {
    fs.rmSync(p, { force: true });
    console.log("已删除安装清单：" + p);
  } catch (e) {
    console.log("⚠ 无法删除安装清单：" + p + "（" + e.message + "）");
  }
}

// —— 上游卸载命令组装 ——

function buildUpstreamRemoveArgs(names, agent) {
  return ["--yes", "skills@latest", "remove"].concat(names).concat(["-g", "-y", "-a", agent]);
}

function upstreamRemoveString(names, agent) {
  return [npxCommand()].concat(buildUpstreamRemoveArgs(names, agent)).map(quoteArg).join(" ");
}

function groupByAgent(list) {
  const map = new Map();
  for (const item of list) {
    if (!map.has(item.agent)) {
      map.set(item.agent, []);
    }
    map.get(item.agent).push(item.name);
  }
  return map;
}

// 优先委托上游 skills CLI 卸载；不可用时（Node 过旧 / npx 缺失 / 非 0 退出）回退直接删除目录。
function removeUpstreamWithFallback(names, agent, target) {
  const directFallback = (reason) => {
    console.log("  ⚠ " + reason);
    for (const name of names) {
      const dest = path.join(target, name);
      if (existsAt(dest)) {
        fs.rmSync(dest, { recursive: true, force: true });
        console.log("  ✓ 已直接删除 " + name);
      } else {
        console.log("  - 未找到 " + name + "（跳过）");
      }
    }
    console.log(
      "  注意：上游锁文件 ~/.agents/.skill-lock.json 可能残留过期条目；可用 `npx skills@latest list` 核对。"
    );
  };

  if (!nodeMeetsUpstream()) {
    directFallback("当前 Node " + process.versions.node + " < 22.20，无法运行上游卸载器。");
    return;
  }
  // Windows 下经 shell 启动，动态参数必须是安全 token；不合法时退回直接删除，避免命令注入。
  if (!isSafeCliToken(agent) || names.some((n) => !isSafeCliToken(n))) {
    directFallback("清单中的上游条目名称或 agent 含非法字符，无法安全调用上游卸载器。");
    return;
  }
  console.log("  将执行：" + upstreamRemoveString(names, agent));
  const res = spawnNpxSync(buildUpstreamRemoveArgs(names, agent), {
    stdio: "inherit",
    env: Object.assign({}, process.env, { DISABLE_TELEMETRY: "1", DO_NOT_TRACK: "1" }),
  });
  if (res.error) {
    directFallback("上游卸载无法执行（" + (res.error.code || res.error.message) + "）。");
  } else if (res.status !== 0) {
    directFallback("上游卸载失败（退出码 " + res.status + "）。");
  } else {
    console.log("  ✓ 已通过 skills CLI 卸载：" + names.join("、"));
  }
}

function runInstall(opts) {
  const sourceRoot = opts.lang === "zh" ? SKILLS_ZH_DIR : SKILLS_DIR;
  const dirs = listSkillDirs(sourceRoot);
  if (dirs === null || dirs.length === 0) {
    fail(
      "找不到安装源目录（" +
        sourceRoot +
        "）。请确认已在完整的 npm 包内运行（不要单独复制 bin/）。"
    );
  }
  if (dirs.indexOf(MAIN_SKILL) === -1) {
    fail("缺少主 skill 目录：" + path.relative(PKG_ROOT, path.join(sourceRoot, MAIN_SKILL)));
  }

  const target = path.resolve(opts.target);

  // 源 / 目标重叠必须在任何写入、复制或建目录之前拒绝。
  assertNoSourceTargetOverlap(target);

  // 先读上一份清单：归属判定必须先于规划/更新。清单为符号链接时，任何情况下都拒绝（含
  // --force / --dry-run），且不跟随、不删除该链接——避免覆盖其指向的无关文件。
  const man = readManifest(target);
  if (man.status === "symlink") {
    fail(
      "拒绝：安装清单是符号链接（" +
        manifestPath(target) +
        "）；为避免覆盖其指向的文件，安装器不跟随也不删除该链接，已停止。请先手动处理该链接。"
    );
  }
  if (man.status === "invalid") {
    console.log(
      "  ⚠ 安装清单无效：" +
        manifestPath(target) +
        "（按未接管处理；现有条目保留，如需接管请 --force）"
    );
  }
  const prevEntries = man.entries;

  console.log("安装语言：" + (opts.lang === "zh" ? "zh（中文镜像）" : "en（默认）"));
  const prevLang = readPreviousLang(prevEntries);
  if (prevLang && prevLang !== opts.lang) {
    console.log(
      "切换语言：" + prevLang + " → " + opts.lang + "（同名第一方 skill 将替换为对应语言版本）"
    );
  }

  // 受支持外部依赖（8 个）现状：lstat（含符号链接/悬空）。
  const existingDeps = MATT_DEP_NAMES.filter((name) => lexists(path.join(target, name)));
  const missingDeps = MATT_DEP_NAMES.filter((name) => !lexists(path.join(target, name)));
  const targetCheck = upstreamTargetCheck(opts);

  // 显式 --with-matt-skills：目标/agent 不可证明或 Node 过低时，在任何写入之前拒绝（含自身更新）。
  if (opts.withMattSkills) {
    if (!targetCheck.ok) {
      fail(
        "拒绝 --with-matt-skills：" +
          targetCheck.reason +
          "。请在 codex 默认全局目录手动运行：" +
          manualUpstreamCommand(existingDeps.concat(missingDeps))
      );
    }
    if (!nodeMeetsUpstream()) {
      fail(
        "拒绝 --with-matt-skills：需要 Node >= 22.20（当前 " +
          process.versions.node +
          "），无法更新/安装上游依赖；已在任何改动之前停止。"
      );
    }
  }

  const nowIso = new Date().toISOString();
  const freshEntries = {};
  const record = (name, entry) => {
    freshEntries[name] = Object.assign({ at: nowIso }, entry);
  };

  console.log("目标目录：" + target + (opts.dryRun ? "（dry-run，不会写入）" : ""));
  if (!opts.dryRun) {
    fs.mkdirSync(target, { recursive: true });
  }

  // 第一方 skill：只同步本包显式提供的第一方集合（绝不推断未知目录）；缺失则安装、已接管则
  // 全量替换为当前源；未接管或符号链接默认保留（--force 才接管/替换链接本身）。
  console.log("第一方 skill（同步包内版本）：");
  const firstParty = FIRST_PARTY_NAMES.filter((name) => dirs.indexOf(name) !== -1);
  if (firstParty.length === 0) {
    console.log("  （本包未提供第一方 skill）");
  }
  for (const name of firstParty) {
    installFirstParty(name, target, opts, prevEntries, record, sourceRoot);
  }

  // 受支持外部依赖：先列出已存在/缺失集合，再决定是否/如何询问或调用上游。
  if (existingDeps.length > 0 || missingDeps.length > 0) {
    console.log("外部依赖 skill（可选上游受支持集合；默认不随包分发）：");
    if (existingDeps.length > 0) {
      console.log("  已存在：" + existingDeps.join("、"));
    }
    if (missingDeps.length > 0) {
      console.log("  缺失：" + missingDeps.join("、"));
    }
  }

  let hardFail = false;
  if (opts.withMattSkills) {
    console.log("可选上游完整版（mattpocock/skills；--with-matt-skills 已显式授权）：");
    if (existingDeps.length > 0) {
      console.log(
        "  ⚠ 将更新已存在项，其目录内的本地改动可能被上游覆盖；每一项独立完成，非整套事务。"
      );
    }
    // 调用前按实时状态复核（第一方同步期间可能已有新目录出现）：新出现者归入「已存在」，
    // 失败时按已存在项处理（不删除、不重建），绝不删除询问/同步期间才出现的第三方目录。
    const liveExisting = MATT_DEP_NAMES.filter((n) => lexists(path.join(target, n)));
    const liveMissing = MATT_DEP_NAMES.filter((n) => !lexists(path.join(target, n)));
    if (
      liveExisting.join(",") !== existingDeps.join(",") ||
      liveMissing.join(",") !== missingDeps.join(",")
    ) {
      console.log(
        "  （调用前复核：已存在 " +
          (liveExisting.join("、") || "（无）") +
          "；缺失 " +
          (liveMissing.join("、") || "（无）") +
          "）"
      );
    }
    const phase = runUpstreamPhase(opts, target, liveExisting, liveMissing, record);
    hardFail = phase.hardFail;
  } else {
    if (existingDeps.length > 0) {
      console.log(
        "  已存在独立依赖（保留，不判定完整版）：" +
          existingDeps.join("、") +
          "；如需可选升级可用 --with-matt-skills 显式更新，或用户自行更新。"
      );
    }
    if (missingDeps.length > 0) {
      const fallbackNote = "未安装可选上游完整版/独立入口，内部回退（references/deps）已可用。";
      if (!targetCheck.ok) {
        console.log("  " + targetCheck.reason + "；" + fallbackNote);
      } else if (!nodeMeetsUpstream()) {
        console.log("  Node " + process.versions.node + " < 22.20，无法调用上游；" + fallbackNote);
      } else if (opts.dryRun) {
        console.log(
          "  [dry-run] 交互终端下会询问是否可选安装上游完整版（不读 stdin、不调用上游）；" + fallbackNote
        );
      } else if (!process.stdin.isTTY || !process.stdout.isTTY) {
        console.log(
          "  非交互终端：跳过可选上游安装；" + fallbackNote + "（如需上游请 --with-matt-skills）"
        );
      } else if (promptUpstreamMissing(missingDeps)) {
        // 询问等待期间目录可能已出现：运行前按实时状态复核，只把「仍然缺失」的名字交给上游；
        // 新出现者保留不改动；全部出现则不再调用上游。
        const stillMissing = missingDeps.filter((n) => !lexists(path.join(target, n)));
        const appeared = missingDeps.filter((n) => lexists(path.join(target, n)));
        if (appeared.length > 0) {
          console.log("  询问期间出现的新条目，保留不改动：" + appeared.join("、"));
        }
        if (stillMissing.length === 0) {
          console.log("  询问期间缺失项均已出现，跳过可选上游安装。");
        } else {
          console.log("可选上游完整版（仅安装仍缺失的项，已按询问后状态复核）：");
          const phase = runUpstreamPhase(opts, target, [], stillMissing, record);
          hardFail = phase.hardFail;
        }
      } else {
        console.log("  已选择不安装可选上游完整版；" + fallbackNote);
      }
    }
  }

  // 包内非第一方目录：不再随包分发，也不做 firstparty 推断；仅提示忽略（不复制、不安装）。
  const unknownDirs = dirs.filter((name) => !FIRST_PARTY_SET.has(name));
  if (unknownDirs.length > 0) {
    console.log("忽略的包内目录（不再分发、不推断为第一方）：" + unknownDirs.join("、"));
  }

  if (opts.dryRun) {
    console.log("dry-run 完成，未写入任何文件。");
  } else {
    const merged = mergeEntries(prevEntries, freshEntries);
    writeManifest(target, merged);
  }
  // 部分写入是真实的：先把确认成功项与保留的原归属落盘，再以非零退出报告可选上游未完成。
  if (hardFail) {
    fail(
      "可选上游完整版操作未全部成功；已记录确认成功项并保留原有归属；未安装独立轻量版，内部回退文档仍可用（详见上面输出）。"
    );
  }
  if (!opts.dryRun) {
    console.log("安装完成。");
  }
}

function confirmUninstall(opts) {
  // 返回 "yes"|"no"|"refuse"。--force 直接视为 yes。
  if (opts.force) {
    return "yes";
  }
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    return "refuse";
  }
  process.stdout.write("确认卸载本包安装的 skill？[y/N] ");
  let answer = "";
  try {
    answer = readLineSync().trim().toLowerCase();
  } catch (e) {
    answer = "";
  }
  return answer === "y" || answer === "yes" ? "yes" : "no";
}

function runUninstall(opts) {
  const target = opts.target;
  const manifest = loadManifest(target);

  // 无清单：尽力而为，仅处理主 skill。
  if (!manifest) {
    console.log("⚠ 未找到安装清单：" + manifestPath(target) + "（无清单，尽力而为）");
    const mainDest = path.join(target, MAIN_SKILL);
    if (!existsAt(mainDest)) {
      console.log("目标目录中不存在 " + MAIN_SKILL + "，无需卸载。");
      process.exit(0);
    }
    console.log("仅处理主 skill：" + MAIN_SKILL + "（其余 skill 保持不动）");
    if (opts.dryRun) {
      console.log("  [dry-run] 将删除 " + MAIN_SKILL + " → " + mainDest);
      console.log("dry-run 完成，未写入任何文件。");
      process.exit(0);
    }
    const decision = confirmUninstall(opts);
    if (decision === "refuse") {
      console.log("非交互式终端：为避免误删，已拒绝卸载。如确认请显式传入 --force。");
      process.exit(1);
    }
    if (decision === "no") {
      console.log("已取消卸载。");
      process.exit(0);
    }
    fs.rmSync(mainDest, { recursive: true, force: true });
    console.log("  ✓ 已删除 " + MAIN_SKILL);
    console.log("清单缺失：其余 skill 一律保持不动。");
    process.exit(0);
  }

  // 依据清单归属构建计划：record 说「本包安装」才删，skipped 永不删。
  const entries = manifest.entries || {};
  const removeLocal = [];
  const removeUpstream = [];
  const keep = [];
  for (const name of Object.keys(entries).sort()) {
    const e = entries[name] || {};
    if (e.action === "installed" || e.action === "forced") {
      if (e.kind === "upstream") {
        removeUpstream.push({ name, agent: e.agent || UPSTREAM_DEFAULT_AGENT });
      } else {
        removeLocal.push(name);
      }
    } else {
      // skipped 或未知状态：一律保留。
      keep.push(name);
    }
  }

  console.log("目标目录：" + target + (opts.dryRun ? "（dry-run，不会写入）" : ""));
  const allRemove = removeLocal.concat(removeUpstream.map((u) => u.name));
  console.log("将移除（本包安装）：" + (allRemove.length ? allRemove.join("、") : "（无）"));
  for (const name of keep) {
    console.log("保留（安装时已存在，非本包安装）：" + name);
  }

  if (allRemove.length === 0) {
    console.log("没有需要移除的 skill（清单中无本包安装项）。");
    process.exit(0);
  }

  if (opts.dryRun) {
    for (const name of removeLocal) {
      console.log("  [dry-run] 将删除 " + name + " → " + path.join(target, name));
    }
    for (const [agent, names] of groupByAgent(removeUpstream)) {
      console.log("  [dry-run] 上游完整版（" + agent + "）：" + upstreamRemoveString(names, agent));
    }
    console.log("  [dry-run] 将删除安装清单：" + manifestPath(target));
    console.log("dry-run 完成，未写入任何文件。");
    process.exit(0);
  }

  const decision = confirmUninstall(opts);
  if (decision === "refuse") {
    console.log("非交互式终端：为避免误删，已拒绝卸载。如确认请显式传入 --force。");
    process.exit(1);
  }
  if (decision === "no") {
    console.log("已取消卸载。");
    process.exit(0);
  }

  for (const name of removeLocal) {
    fs.rmSync(path.join(target, name), { recursive: true, force: true });
    console.log("  ✓ 已删除 " + name);
  }
  for (const [agent, names] of groupByAgent(removeUpstream)) {
    console.log("上游完整版（" + agent + "）：");
    removeUpstreamWithFallback(names, agent, target);
  }
  removeManifest(target);
  console.log("卸载完成。");
  process.exit(0);
}

function runCheck(opts) {
  const target = opts.target;
  console.log("检查依赖 skill 解析状态（目标目录：" + target + "）：");

  let ok = true;
  for (const name of REF_NAMES) {
    if (isFile(path.join(target, name, "SKILL.md"))) {
      console.log("  " + name + "：独立 skill 已安装（存在 SKILL.md；不判定来源/是否完整版）");
      continue;
    }
    const fallbacks = REF_FALLBACKS[name] || [];
    // 组合能力要求「全部」引用文件都在；零引用不算可用。
    const missing = fallbacks.filter((file) => !isFile(path.join(DEPS_DIR, file)));
    if (fallbacks.length > 0 && missing.length === 0) {
      console.log(
        "  " + name + "：内部回退可用（references/deps/" + fallbacks.join(" + ") + "）"
      );
      continue;
    }
    ok = false;
    if (fallbacks.length === 0) {
      console.log("  " + name + "：不可用（无外部 SKILL.md，且没有内部回退映射）");
    } else {
      console.log(
        "  " + name + "：不可用（无外部 SKILL.md，且内部回退不完整；缺少：" +
          missing.map((f) => "references/deps/" + f).join("、") +
          "）"
      );
    }
  }

  if (ok) {
    console.log("全部依赖均可解析（外部安装或内部回退）。");
    process.exit(0);
  } else {
    console.log("存在无法解析的依赖。");
    process.exit(1);
  }
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.lang === "zh" && opts.command !== "install") {
    fail("--zh 仅用于 install（check 与 uninstall 与语言无关）：请去掉 --zh 后重试。");
  }
  if (opts.command === "check") {
    runCheck(opts);
  } else if (opts.command === "uninstall") {
    runUninstall(opts);
  } else {
    runInstall(opts);
  }
}

main();
