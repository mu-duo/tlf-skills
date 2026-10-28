# 课程

四份 brief，从粗到细。每份都是针对某一层的完整文档，写成一次坐下就能读完。上限就是上限：如果一份 brief 放不下，细节属于下一层，或者这一层需要拆分——绝不是进一步压缩。

## 会话与 brief 的对应

| 会话 | brief | 允许的模式 | 配套产物 |
| --- | --- | --- | --- |
| 1 | `00-model.md` | `tour`、`tutor` | `runbook.md`、`glossary.md`、`profile.yml`、会话记录 |
| 2 | `01-map.md` | `tour`、`tutor` | `glossary.md` 更新、会话记录 |
| 3 | `02-structure.md` | 仅 `tutor` | `glossary.md` 更新、会话记录 |
| 4 | `03-operations.md` | 仅 `tutor` | `runbook.md` 刷新、会话记录 |
| 之后任意 | `drill` | `drill` | 会话记录、`profile.yml` |

当用户已经具备该层时，可以跳过某份 brief：用一次模型检查给它评分，并连同证据标记为 `done`。往回走是正常的，不是失败。

每份 brief 都遵循相同的顶层契约：

1. 单段摘要，放在页面最前面。
2. 「这一层刻意忽略什么」——简化契约。
3. 正文：锚定的 `path:line`，每个论断标注 `verified` / `inferred`，标题跟随模型而不是文件树。
4. 三个「读完后你应能回答」、检验模型的问题。

## 00-model.md — 设计者在构建什么？

上限：600 词。这是唯一通常短到可以内联进对话的 brief。

写作前阅读：

- `README`、`CONTEXT.md`、`docs/product/*`、`AGENTS.md` — 明示的目的。
- 最早与最新的提交，加上 `git log --oneline --reverse | head -20` — 在成为现在这样之前，这个项目是什么。
- 清单文件与运行时版本锁定 — 约束的形状。
- CI、Dockerfile、部署配置 — 团队无法改变的东西。

Grep 目标：

```bash
rg -n "^(#|##) " README* CONTEXT* 2>/dev/null
git log --reverse --oneline | head -20
rg -n "engines|python_requires|go [0-9]|rust-version|node" package.json pyproject.toml go.mod Cargo.toml 2>/dev/null
rg -n "TODO|NOTE|HACK|for now|on purpose|by design" -g '!node_modules' -g '!vendor' | head -40
```

章节骨架：

1. 摘要段。
2. 这一层刻意忽略什么（通常是：路径、模块名、失败处理、历史）。
3. 一句话：谁的问题，以何种方式解决。
4. 约束表：约束 / 证据锚点 / 它促成了什么。
5. 核心回路：一个典型任务的 5-7 个编号步骤；每一步都有锚点。
6. 名词：5-8 个实体，各是什么，彼此如何关联。
7. 接缝：系统在哪里被切开，以及有什么穿过。
8. 刻意省略：设计者选择不做什么，以及它解释了哪个奇怪的结构。
9. 三个问题。

自检问题范式（结尾的三个）：

- 「不看材料：一个典型任务要经过哪五六个步骤？」
- 「<noun> 连接了哪两个实体，在它们之间传递什么？」
- 「说出设计刻意不做的一件事，以及为它提供依据的约束。」

完成测试：用户在白板上画出核心回路和名词，关系正确，并能说出每个约束为何在清单里。

刻意省略：锚点证据之外的文件路径、模块清单、类清单、失败模式、提交考古。路径和模块属于 `01-map.md`；失败模式和历史属于 `03-operations.md`。

## 01-map.md — 所有东西在哪里？

上限：1500 词。链路（原称「spine」）属于这一层。

写作前阅读：

- 目录树，两层深，加上清单里的脚本。
- 已有架构文档和 `CONTEXT.md` — 先复用，再对比。
- `references/repo-archetypes.md` 中每种原型的一个入口。
- 用户的 `focus` 答案，已记录在 profile 中。

Grep 目标：

```bash
rg -n "\.(get|post|put|patch|delete)\(|@(app|router)\.(route|get|post)" -g '!node_modules'
rg -n "cobra\.Command|argparse|click\.command|clap::Command|@click" -g '!node_modules'
rg -n "subscribe|consume|handler|listener|worker" -g '!node_modules' -g '!vendor'
rg -n "export (default )?(function|class|const)" src/ lib/ 2>/dev/null
rg -n "^(def main|if __name__|func main|int main)" -g '!vendor' -g '!node_modules'
```

章节骨架：

1. 摘要段。
2. 这一层刻意忽略什么（通常是：这些形状为何存在、失败行为、历史）。
3. 原型，一行说明，以及决定它的信号。
4. 入口表：入口 / 类型 / 锚点 / 状态。
5. 功能到路径表：用户提到的功能、它们的入口、路径上的文件。
6. 链路：从触发到可观察效果的 5-7 跳，每跳都有锚点。
7. 边界：每个边界上穿过什么，以什么形态。
8. focus 与回退：用户说会先改什么，以及那条路径是否处于边缘。
9. 不在范围内：被刻意排除的包或功能。
10. 纠正：错误的第一猜测，作为证据保留。
11. 三个问题。

自检问题范式：

- 「对于 <feature>，说出入口以及其路径上的三个文件。」
- 「链路上数据在哪里改变形态，改变前后各是什么？」
- 「要添加 <extension> 需要跨过哪个边界，必须遵守什么契约？」

完成测试：给定用户说出的任意功能，他们能说出入口和路径，并能把链路画在空白页上。

刻意省略：抽象的理由、取舍、事故历史、完整的符号清单。地图是空间性的，不是解释性的。每个文件的地图是目录，不是模型。

## 02-structure.md — 为什么是这种形状？

上限：2500 词。最密的一份 brief；阅读时间仍不超过 15 分钟。

写作前阅读：

- 链路触及的抽象。不引入新的抽象。
- 先读已有架构文档，让这份 brief 成为增量。
- 这些抽象周围的测试：它们编码了契约。
- 接口与 schema 定义；类型边界。

Grep 目标：

```bash
rg -n "interface |abstract class |protocol |trait |type .* struct|type .* = " <module dirs>
rg -n "TODO|HACK|deprecated|legacy|workaround" -g '!node_modules' -g '!vendor'
git log --oneline -20 -- <path>
rg -n "<symbolName>" --type test
```

章节骨架：

1. 摘要段。
2. 这一层刻意忽略什么（通常是：运行时运维、事故历史、穷举式符号覆盖）。
3. 抽象表：抽象 / 它解决的问题 / 它取代了什么 / 它禁止什么 / 锚点。
4. 数据形态：核心类型，以及数据在链路上如何变换。
5. 契约：每个接缝承诺什么，什么会破坏承诺。
6. 扩展点：设计预期在哪里改变，以及预期的改变方式。
7. 取舍表：选择 / 显然的替代方案 / 为何不选 / 代价 / 锚点。
8. 至多一张图，且仅当它能承载文字无法承载的信息。
9. 三个问题。

自检问题范式：

- 「为什么 <abstraction> 与其调用方分开，如果合并会有什么变糟？」
- 「<seam> 强制执行哪个契约，调用方违反它会导致什么失败？」
- 「陈述一个取舍及其代价，并指出让它成真的代码。」

完成测试：用户解释三个抽象及其契约，说出每个边界上的数据形态，并为其中一个取舍辩护，包括其代价。

刻意省略：逐行走读、穷举的导出符号清单、长代码块。整份 brief 至多三个短代码块。

## 03-operations.md — 什么时候会坏？

上限：2000 词。

写作前阅读：

- 错误路径、重试、超时，以及吞掉异常的地方。
- 日志、指标、健康检查，以及告警定义。
- 用 `git log` 看最近几次修复和回滚；若有 issue 跟踪器也看。
- runbook 中的命令，若环境允许就再跑一遍。

Grep 目标：

```bash
rg -n "catch|except|rescue|recover\(|on error|retry|timeout|circuit" -g '!node_modules' -g '!vendor'
rg -n "logger|log\.|metrics|health|readyz|livez|alert" -g '!node_modules' -g '!vendor'
git log --oneline -30 --grep="fix\|revert\|hotfix\|rollback"
rg -n "TODO|FIXME|HACK|known issue" -g '!node_modules' -g '!vendor'
```

章节骨架：

1. 摘要段。
2. 这一层刻意忽略什么（通常是：已在前文覆盖的架构理由、完整 runbook 的复制）。
3. 失败路径表：失败 / 用户看到的症状 / 如何被发现 / 锚点。
4. 降级与恢复：什么在保护系统，以及这种保护付出什么代价。
5. 历史：两三个解释当前形状的提交或事故；有锚点。
6. 运维取舍：快速修复与正确修复的对比；已知陷阱。
7. 链接到 `runbook.md`，而不是重复它。
8. 三个问题。

自检问题范式：

- 「请求在 <hop> 处失败。用户先看到什么，哪一行日志告诉你它停在哪里？」
- 「如果 <dependency> 变慢（而不是宕机）会坏什么？」
- 「说出一个仍然约束着设计的历史修复，以及它避免了什么。」

完成测试：用户说出针对某个症状会先查的失败、发现点，以及一个他们不会撤销的取舍。

刻意省略：runbook 的第二份副本、穷举的错误码清单、泛泛的建议（「加监控」）。每一行都必须关于这个仓库。

## 当已有文档已经覆盖这一层

一份大型架构说明、一份 `docs/product/02-architecture.md`，或一份好的 `CONTEXT.md` 可能已经拥有某一层。不要重写它。

1. **复用：**从 brief 链接到它，并引用承载该层的那一段。
2. **对比：**列出该文档哪里对、哪里漏、哪里相对当前提交已过时。
3. **只写增量：**写缺失的层或增量，放在明确说明这一点的标题下。以一句明确的话开头：

   > 本 brief 扩展 `docs/product/02-architecture.md`，不取代它。提交 `<sha>` 之后可能过时。

4. **绝不复制。**如果已有文档对那一层正确且完整，这份 brief 可以只是带三个问题的短指引。那是有效的 brief，不是缺失的 brief。

## runbook 优先

`runbook.md` 比任何 brief 都活得久。一个拿到可用 runbook、却没有架构图的新工程师，第一天就能交付；反过来则不行。它必须包含：

- 带版本的前置条件，以及如何检查它们。
- 安装、构建、运行、测试和 lint 命令，逐字照录并已验证。
- 必需的环境变量，以及它们的值从何而来。
- 种子数据或测试夹具。
- 已知陷阱：不稳定测试、端口、代码生成步骤、依赖顺序的初始化、必须运行的服务。

给每一行标注 `verified`（你运行过）或 `inferred`（从配置读到的）。推断出来的命令是带引用的猜测。
