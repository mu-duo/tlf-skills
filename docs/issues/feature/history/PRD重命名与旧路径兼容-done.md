# PRD 重命名与旧路径兼容

> 完成: 2026-10-19 ｜ 责任: agent ｜ 创建: 2026-10-19 ｜ 关联: 无独立关联条目；本条记录术语纠正（PDR → PRD）

## 背景与目标

PDR 是非标准缩写。本项目文档描述的是产品需求，应统一为标准术语 PRD（Product Requirements Document，产品需求文档）。目标是把活跃包内的术语、路径、模板与渲染默认值全部改为 PRD 体系，避免继续生产新的 PDR 产物。

已初始化项目中的 `docs/pdr/` 目录树属于历史漂移：只做检测与报告，不移动、不重命名、不重写其中内容；如用户需要迁移，必须获得显式授权后单独执行。历史 issue 记录同样保持原样，不追改。

## 范围

- `skills/project-docs-workflow/**` 与 `skills_zh/project-docs-workflow/**`：完成 12 个文件重命名，并同步内容中的术语、路径与模板引用。
- `skills/docs-html-view/**` 与 `skills_zh/docs-html-view/**`：调整渲染根目录与默认值，并对旧 `docs/pdr/` 输入给出兼容性警告。
- `scripts/check-skills-zh.js`：同步中英文镜像检查中的新路径。
- `package.json`、根 `README.md`：同步包内路径与使用说明。
- lite-task SKILL 文件：同步相关术语与路径。
- 排除 `docs/issues/**` 历史记录，不重写历史；不提交、不发布。
- 旧路径兼容仅限“发现并提示”，不在初始化或渲染时自动迁移 `docs/pdr/`。

## 完成判据

- 活跃代码与文档中不再出现 `PDR` 术语或 `pdr` 路径，仅保留有意为之的 `docs/pdr` 旧路径兼容说明与警告。
- 12 个文件已按要求重命名，英文与中文镜像的静态资源逐字节一致。
- 初始化遇到旧 `docs/pdr/` 时只报告，渲染遇到旧路径时只警告，均不移动或改写用户文件。
- 历史 `docs/issues/**` 内容未发生变化。
- `node scripts/check-skills-zh.js`、`node bin/install.js check`、安装 dry-run、`git diff --check` 及 Python/JS 语法检查均通过。

## 步骤

- [x] 规划（确认 12 个重命名清单与兼容边界）
- [x] 骨架（先完成路径与模板重命名，保证可运行）
- [x] 细节（同步文档、渲染默认值与中英文镜像）
- [x] 异常（旧 `docs/pdr/` 只报告、不写入；校验失败路径）
- [x] 回顾（复核差异、清理残留术语并记录验证结果）

## 结果

- 活跃包已统一为 PRD：12 个文件重命名（`references/prd.md`、`prd-00-readme.md`、`prd-{module-readme,nfr,spec,interfaces}.md`，英文与中文镜像各一套）；模板、引用、渲染默认值、README 与 package description 同步。
- 兼容行为：`project-docs-workflow` init 在存在有内容的遗留 `docs/pdr/` 且 `docs/prd/` 缺失时只报告、不创建；`docs-html-view` 默认渲染 `prd/current/adr`，对旧 `docs/pdr/` 给出警告，不移动、不重写；显式允许 `pdr` 时仍可按原样渲染。
- 历史 `docs/issues/**` 记录未改写；`模糊PDR与探索式开发模型.md` 保持原名，避免破坏历史链接。
- 证据：`node scripts/check-skills-zh.js` PASS（file-set parity 43、copied byte-identical 26、links PASS）；`node bin/install.js check` PASS；`install --dry-run --dir /tmp/opencode/prd-rename-check` PASS（无写入）；`git diff --check` PASS；`node --check` / `python3 -m py_compile` PASS；`npm pack --dry-run` 无 pdr 命名文件（96 files）；`gen_nav.py` 临时 fixture 验证旧路径警告、`prd/current/adr` 正常渲染、显式允许 `pdr` 时警告不触发。
- 未提交、未发布；`skills_zh/README.md` 的源基线提交未推进（无新提交）。

## Log

- 2026-10-19 用户选择完整迁移（选项 1），创建本条目：统一 PDR → PRD，旧 `docs/pdr/` 仅报告不迁移，待实施与验证。
- 2026-10-19 完成：活跃包全量改为 PRD；init 与 docs-html-view 增加旧 `docs/pdr/` 只报告兼容；历史 issue 保持原样；镜像校验、安装 dry-run、语法检查与 `gen_nav.py` fixture 均通过。归档为 `-done`。
