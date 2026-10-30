#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");

const PKG_ROOT = path.join(__dirname, "..");
const SKILLS_DIR = path.join(PKG_ROOT, "skills");
const SKILLS_ZH_DIR = path.join(PKG_ROOT, "skills_zh");
const MAIN_SKILL = "project-docs-workflow";
const DEFAULT_TARGET = path.join(os.homedir(), ".agents", "skills");
// 安装清单：记录本包每次安装处理过的 skill 及其归属，供 uninstall 精确卸载。
const MANIFEST_NAME = ".project-docs-workflow.install.json";
const PKG_VERSION = require(path.join(PKG_ROOT, "package.json")).version;

// 安装器只做三件事：
// 1. install（默认）：同步本包自带的第一方 skill（显式名单，见 FIRST_PARTY_NAMES）；
// 2. uninstall：按安装清单卸载本包安装的第一方 skill；
// 3. check：校验主 skill 内嵌的依赖文档（references/deps）是否齐全。
// 依赖能力全部内嵌，安装器不查询、不安装、也不调用任何外部 skill。

const FIRST_PARTY_DEP_KINDS = {
  "doc-opt": "doc-opt",
  "docs-html-view": "docs-html-view",
  "docs-docx-view": "docs-docx-view",
  "lite-task": "lite-task",
  "repo-read-assistant": "repo-read-assistant",
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
  "repo-read-assistant",
]);

function depKind(name) {
  return FIRST_PARTY_DEP_KINDS[name] || "lite";
}

function kindFor(name) {
  return name === MAIN_SKILL ? "main" : depKind(name);
}

// 保守判定清单归属：只有明确记录为本包本地安装（installed/forced 且 kind 为已知本地 kind）
// 才算「已接管」。缺失/损坏/未知/skipped 一律不接管（改为保留）。
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
      "普通安装只同步本包自带的第一方 skill（project-docs-workflow、doc-opt、docs-html-view、docs-docx-view、lite-task、repo-read-assistant）：",
      "缺失则安装；已由本包接管则用当前包内版本全量替换（会移除其中多余/过期文件）；",
      "未接管条目、符号链接（含悬空）默认保留。依赖全部内嵌：能力来自主 skill 的 references/deps/，",
      "不安装、不更新、也不调用任何外部 skill。",
      "默认安装英文源 skills/；--zh 改为安装中文镜像 skills_zh/。两种语言的 skill 同名、互斥，",
      "同一目标一次只保留一种语言；再次运行另一种语言即可切换（仅 install 支持）。",
      "",
      "用法：",
      "  project-docs-workflow [install] [选项]   安装/同步包内第一方 skill（默认动作）",
      "  project-docs-workflow check   [选项]     检查内置依赖文档是否齐全",
      "  project-docs-workflow uninstall [选项]   依据安装清单卸载本包安装的 skill",
      "",
      "选项：",
      "  --dir <path>   指定目标 skills 根目录（默认 ~/.agents/skills）",
      "  --zh           从中文镜像 skills_zh/ 安装第一方 skill（默认英文源 skills/）",
      "                 两种语言 skill 同名、互斥；再次运行另一种语言即可切换；仅 install 支持",
      "  --force        安装：覆盖并接管所有第一方 skill（含替换已存在的符号链接本身，不动其指向）；",
      "                 uninstall：非交互确认（非 TTY 下必须显式传入）",
      "  --dry-run      仅打印将执行的操作（与真实运行相同决策），不写入、不读 stdin",
      "  -h, --help     显示本帮助",
      "",
      "示例：",
      "  project-docs-workflow                          # 安装/同步到默认 ~/.agents/skills（仅第一方）",
      "  project-docs-workflow --zh                     # 安装中文镜像（默认 en；两种语言同名互斥）",
      "  project-docs-workflow --dir <path> --dry-run   # 预演到指定目录（不写入）",
      "  project-docs-workflow --force                  # 接管/替换所有第一方 skill",
      "  project-docs-workflow check                    # 检查内置依赖文档是否齐全",
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

function existsAt(p) {
  return isDir(p) || isFile(p);
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

  // 依据清单归属构建计划：仅本包本地安装（installed/forced 且 kind 为已知本地 kind）才删；
  // skipped、缺失或未知 kind（含旧清单中的历史 kind）一律保留、绝不动作。
  const entries = manifest.entries || {};
  const removeLocal = [];
  const keep = [];
  for (const name of Object.keys(entries).sort()) {
    if (isOwnedLocal(entries[name])) {
      removeLocal.push(name);
    } else {
      keep.push(name);
    }
  }

  console.log("目标目录：" + target + (opts.dryRun ? "（dry-run，不会写入）" : ""));
  console.log("将移除（本包安装）：" + (removeLocal.length ? removeLocal.join("、") : "（无）"));
  for (const name of keep) {
    console.log("保留（安装时已存在、非本包安装或未知归属）：" + name);
  }

  if (removeLocal.length === 0) {
    console.log("没有需要移除的 skill（清单中无本包安装项）。");
    process.exit(0);
  }

  if (opts.dryRun) {
    for (const name of removeLocal) {
      console.log("  [dry-run] 将删除 " + name + " → " + path.join(target, name));
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
  removeManifest(target);
  console.log("卸载完成。");
  process.exit(0);
}

function runCheck(opts) {
  console.log("检查内置依赖（唯一来源：" + DEPS_DIR + "）：");

  let ok = true;
  for (const name of REF_NAMES) {
    const fallbacks = REF_FALLBACKS[name] || [];
    // 组合能力要求「全部」引用文件都在；零引用不算可用。
    const missing = fallbacks.filter((file) => !isFile(path.join(DEPS_DIR, file)));
    if (fallbacks.length > 0 && missing.length === 0) {
      console.log(
        "  " + name + "：内置可用（references/deps/" + fallbacks.join(" + ") + "）"
      );
      continue;
    }
    ok = false;
    if (fallbacks.length === 0) {
      console.log("  " + name + "：不可用（没有内置映射）");
    } else {
      console.log(
        "  " + name + "：不可用（内置副本不完整；缺少：" +
          missing.map((f) => "references/deps/" + f).join("、") +
          "）"
      );
    }
  }

  if (ok) {
    console.log("全部依赖均由内置副本提供，无需外部 skill。");
    process.exit(0);
  } else {
    console.log("内置依赖不完整。");
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
