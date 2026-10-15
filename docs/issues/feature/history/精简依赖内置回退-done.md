# 精简依赖为内置回退

> 完成: 2026-10-15 ｜ 责任: agent ｜ 创建: 2026-10-15 ｜ 关联: [依赖检查与显式上游更新](依赖检查与显式上游更新-done.md)

## 背景与目标

用户批准内部化的依赖回退打包：不再随包分发独立轻量依赖 skill，改为把有用语义并入主 skill 的内置回退 `references/deps/*`。本条目**取代**先前历史中「随包分发独立轻量 skill」与「上游失败回退复制轻量版」的做法；默认保留策略与显式 `--with-matt-skills` 的语义沿用 [依赖检查与显式上游更新](依赖检查与显式上游更新-done.md)，仅移除独立轻量分发。所有历史条目的日志**保留不改**。

## 范围

- 本 feature 全局覆盖：README、NOTICE、package.json（仅 description）、`skills/project-docs-workflow/**` 内容、删除 8 个来源目录下共 11 个轻量文件（`grilling` / `grill-me` / `grill-with-docs` / `domain-modeling` / `tdd` / `deepwork` / `retro` / `improve-codebase-architecture`），以及**安装器 `bin/install.js`**——安装器由 core writer **单独实现**，本条目只记录策略、未在此写代码。
- **不**改 `skills/doc-opt/**`、`skills/docs-html-view/**`；不发布 / 不提交；不触网、不写真实 home、不做 project init；不新增持久测试。
- 不在来源 11 文件之外删除任何路径。

## 方案（简述）

- 默认只分发三个第一方 skill；缺失外部名称用主 skill 内置回退 `references/deps/{grilling,domain-modeling,tdd,doc-opt,boundaries}.md`（**纯 .md**，无嵌套 `SKILL.md`，宿主不注册为独立 skill）。
- 保留语义：`grilling`/`grill-me` 别名（`grill-me` → `grilling.md`）；`grill-with-docs` → `grilling.md` + `domain-modeling.md` 交织（术语即写 `CONTEXT.md`，满足三条判据记 ADR）；最小 domain 主动校验 / 澄清范围 / 示例；`tdd` 重构归评审（`code-review`）；`retro` 环境改进分类清单；architecture 共享词汇边界。
- 解析两级：按名调用已安装的独立 skill；否则**执行**内置 ref（不作为 skill 调用）；触发器策略以各 skill 的调用元数据为准，可选名不代表可用，不自动调用 user-only 包装。init 仍把 `references/deps/*` 整目录复制到 `docs/agents/deps/`；包内路径与物化本地路径各自自洽。
- README：默认只分发三个第一方、默认不自动安装独立依赖（用户同意可选增强除外）；独立外部名称缺失 ≠ 能力缺失（`check` 按名或 ref 即通过，全新安装通过）；No / 回车 / 非 TTY / 非等价自定义目录 / 低 Node 用内置回退（不复制独立 skill）；可选 TTY 询问保留为可选增强；`--with-matt-skills` 显式可选完整版安装 / 更新；失败不再复制轻量版；历史 `lite` 清单保留、不自动清理 / 迁移；`/grill-me` 不再由本包提供独立入口。
- 许可：保留上游 MIT 版权与来源链接；NOTICE 仅把**源自上游**的 ref 列入派生清单（`grilling` / `domain-modeling` / `tdd` / `boundaries`），`doc-opt.md` 为第一方、不误标为上游派生。

## 完成判据

- 可发现的 `SKILL.md` 恰为 3（主 skill、`doc-opt`、`docs-html-view`）；8 个来源目录的 11 个文件已删，且无其它删除。
- 内置回退 refs 为纯 `.md` 且语义保留；主 skill 两级解析（含别名映射 / 触发器策略）与 coexistence / README 无「随包分发轻量 skill」的过时断言。
- README / NOTICE / package.json（description）与安装器行为一致；版本仍 2.3.0。
- `bin/install.js` 由 core writer 单独实现并与策略一致；未改 `skills/doc-opt/**` / `skills/docs-html-view/**`；未新增持久测试；不发布 / 不提交 / 不触网 / 不写真实 home。

## 步骤

- [x] 规划（完成判据与方案已对齐）
- [x] 骨架（最小可运行切片 + 证据；整包 + `npm pack` 列表验证）
- [x] 细节（主路径实现与质量）
- [x] 异常（失败路径、边界与稳定性）
- [x] 回顾（收尾回顾：文档同步）

## 结果

- 交付：内部化依赖回退——删除 8 个来源目录共 11 个轻量文件；语义并入 `references/deps/*`（纯 `.md`）；主 skill 两级解析补齐别名映射（`grill-me` → `grilling.md`；`grill-with-docs` → `grilling.md` + `domain-modeling.md` 交织）与触发器策略；coexistence / NOTICE / package.json（description）/ README 与安装器行为对齐；安装器 `bin/install.js` 由 core writer 单独实现同一策略。
- 证据（父任务持有）：
  - 安装器策略套件 `/tmp/opencode/pdw-pkg-policy/RESULTS-final.json`（73/73，取代早先 69）：默认仅 3 第一方 / 无独立轻量；No / yes 可选；上游 `npx` 仍为显式完整版更新；旧 `lite` 在 default + `--force` 下保留且旧清单归属不变、无自动清理；未知包内目录忽略；可选**新**缺失项部分失败只清理新建路径并非零、refs 仍可用；已有项失败不重拷；严格处理 malformed / duplicate / unknown / nopath / exit1；询问窗口重检；dry-run；源 / 清单符号链接安全；第一方陈旧项移除；组合回退要求**两个**文件，缺一即失败（已装外部包装可按名解析）。
  - 父任务独立**整包 + 打包** `/tmp/opencode/pdw-internal-parent-9zvmgq/RESULTS.json`（25 断言）：默认非 TTY 恰装 3 + 自清单 / 不调用 `npx`；3 个第一方与源逐字节一致；5 个纯 `.md` 回退均安装、全新 `check` 通过且列出组合 refs；既有外部 `grilling` lite 本地改动 + 清单在 `--force` 下保留，未复制其它上游独立项；dry-run 字节快照一致；真实 `npx` **STUB** 部分失败时仅清理新目录、保留旧 legacy、非零而 `check` 仍通过；`npm pack --dry-run --ignore-scripts --json`（隔离 npm-cache）恰列 3 个 `SKILL.md`（`doc-opt` / `docs-html-view` / `project-docs-workflow`），无任何嵌套 `SKILL`，5 个回退 `.md` 均在，移除的 8 路径均不在。
  - `node --check` / `git diff --check` 通过；父任务静态阅读 refs / 模板别名映射与 MIT notice 保留。
- 限制：验证为 stub / 隔离 HOME / 打包列表，**无**网络、无依赖安装、未改真实用户目录、无 commit / 版本发布。纯 CLI 断言**不**证明所有宿主下的真实模型合规，不外推。删除包内来源 11 **不**影响用户已安装的 lite，且**未**使用迁移授权（历史 `lite` 目录保留、仅用户主动 `uninstall` 或显式清理时处理）。

## Log

- 2026-10-15 用户批准内部化依赖回退打包，创建本条目（feature，doing）：删除 11 个轻量文件、语义并入内置 ref、README / NOTICE / package.json 与安装器对齐。取代历史中独立轻量分发与失败回退复制轻量版；历史日志保留不改。安装器由 core writer 负责。
- 2026-10-15 父任务复核修正：主 SKILL 补齐别名映射（`grill-me` → `grilling.md`；`grill-with-docs` → `grilling.md` + `domain-modeling.md` 交织）与触发器策略；物化 `agents-domain.md` 补组合回退、去斜杠式入口承诺；README 精确化（默认不自动安装、用户同意可选增强除外；非等价自定义目录；NOTICE 仅列源自上游的 ref，`doc-opt.md` 不误标）。保持 `doing`，待最终验证。
- 2026-10-15 完成：内置回退打包与安装器策略落地并通过父任务验证（core 73/73 + 独立整包 25 断言；`npm pack` 恰含 3 个 `SKILL.md`、5 个回退 `.md`；`node --check` / `git diff --check` 通过）。删除包内来源 11 不影响用户已装 lite；未使用迁移授权。归档为 `-done`。
