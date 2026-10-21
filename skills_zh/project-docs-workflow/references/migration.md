# 迁移（v4 / 旧版 → v5）

迁移把现有文档树转换为 v5。它是**显式且经评审**的——init 绝不自动改写、移动或删除项目文档。

## 检测

init 将以下任一视为 v4 / 旧版文档：

- `docs/prd/` 树（v4 布局）。
- 改名前的 `docs/pdr/` 树。
- 物化文件中的 `project-docs-workflow v3` / `v4` provenance 行。
- 旧 PFD / 分层结构：产品 `00-index.md`、`L1` / `L2` / `L3` 术语，或 PRD 中嵌入的现状 / 进展章节。

旧版词汇映射：

| v4 / 旧版 | v5 |
| :--- | :--- |
| `docs/prd/` | `docs/product/` |
| L1（人类叙事） | PRD（宏观产品叙事） |
| L2（规范规格） | SPEC（实现事实标准） |
| L3（Current） | Current（实际建成快照；角色不变） |
| PFD / 产品 `00-index.md` | 退役——拆入 PRD 章节 + `docs/toc.yml` |
| 模块 `00-index.md` | 模块侧车（不变，仍不发布） |

## 提示选项

用项目的文档语言询问一次：

1. **立即迁移**——展示计划与逐文件 diff，获得用户确认后执行。
2. **只看计划**——打印计划与 diff；不写入。
3. **稍后**——创建**一个** `docs/issues/chore/agent/...` 迁移 issue，其余不写。
4. **跳过**——完全不写，连非产品产物也不写；仅报告。

绝不自动改写 / 移动 / 删除。用户未确认时，什么都不变。

## 步骤（确认后）

1. **移动树**：`docs/prd/` → `docs/product/`。尽量用 `git mv` 让历史跟随文件。不要提交。
2. **拆分 v4 产品 `00-README.md`**：
   - 一句话 / 问题 / 用户旅程 → `docs/product/00-README.md`；
   - 能力地图 / 非目标 / 约束 → `docs/product/01-requirements.md`；
   - 模块索引 / 阅读顺序 → `docs/product/02-architecture.md` 与 `docs/toc.yml`。
3. **退役产品 `00-index.md`**：
   - 模块索引 / 阅读顺序 → `docs/toc.yml` / `02-architecture.md`；
   - CAP↔FR 追溯 → 模块 `00-index.md`，不再需要则丢弃；
   - 内容有了新归属后，才删除空掉的产品 `00-index.md`。
4. **模块文件**：`00-README.md` 成为模块 PRD（改写横幅，移除文档地图 / 依赖材料）；`01-spec` / `02-interfaces` / `03-nfr` / `design/` 保留为 SPEC，凡描述旧分层的措辞一并更新。
5. **创建 `docs/toc.yml`**，包含 `overview` / `requirements` / `architecture` / `appendix` 章节与必需附录 id（`glossary`、`spec`、`current`、`adr`）。
6. **更新链接**：全局 `docs/prd` → `docs/product`；Current 链接（`../product/00-README.md`）；ADR 路径链接；`docs/agents/workflow.md` 与 `AGENTS.md` 区块（角色、PRD/SPEC 权威、TOC、bootstrap / 迁移指针）。
7. **移除或替换旧的 `docs-html-view` 配置 / 构建输出**（若有）。发布是独立流程——迁移期间不要重建它。

逐步展示逐文件 diff，遇到意外冲突即停止。对没有明显新归属的内容，绝不猜测用户意图；要询问。

## 稍后

在 `docs/issues/chore/agent/` 下创建**一个** issue，描述检测到的旧布局与迁移计划。不写文档；issue 是唯一产物。

## 跳过

不写入。仅报告检测到的状态与选项。

## 现有项目

绝不自动改写现有项目。迁移始终是显式、经评审的决策；用户确认前，源文档仍是权威。
