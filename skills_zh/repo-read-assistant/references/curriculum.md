# 课程

五个阶段，每次会话一个。每个阶段都有一份可执行的检查清单、一份 grep 目标列表、一个记录目标和一个完成测试。无法评分的阶段等于没发生过。

## 会话与阶段映射

| 会话 | 阶段 | 允许的模式 | 写入的产物 |
| --- | --- | --- | --- |
| 1 | Orientation | `tour`、`tutor` | `00-runbook.md`、`01-glossary.md`、`profile.yml`、会话笔记 |
| 2 | Skeleton | `tour`、`tutor` | `02-map.md`、会话笔记 |
| 3 | Spine | 仅 `tutor` | `03-spine.md`、会话笔记 |
| 4 | Structure | 仅 `tutor` | `04-architecture.md`、会话笔记 |
| 5 | Apply | 仅 `tutor` | 会话笔记加补丁计划 |
| 之后任意次 | `drill` | `drill` | 会话笔记、profile 更新 |

当用户已经掌握某个阶段时允许向前跳；用一个问题考一下，并连同证据标记为 `done`。向后回退是正常的，不是失败。

## 阶段 1 — Orientation

目标：最小词汇量。用户能说出项目做什么，能让它跑起来，并知道团队使用的十个词。

检查清单：

1. 读 `README`、`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml`，以及顶层目录列表。不要再深入。
2. 列出入口点：`main`、`index`、`cmd/*/main.go`、`bin/*`、`__main__.py`、server bootstrap。
3. 三类术语对齐。请用户把十个术语分到：产品名词、代码名词、基础设施名词。只纠正放错的。这比倒一份术语表更快发现假朋友。
4. 跑通构建与测试。自己在仓库里只读地运行它们。
5. 写 `00-runbook.md` 和 `01-glossary.md`。

grep 目标：

```bash
rg -n "^(#|##) " README* CONTRIBUTING* 2>/dev/null
rg -n '"scripts"' -A 20 package.json
rg -n "^(def main|if __name__|func main|int main)" -g '!vendor' -g '!node_modules'
rg -n "docker-compose|docker run|make " README* docs/ 2>/dev/null
```

记录：十个术语及其 `path:line` 锚点和 `verified`/`inferred`；确切的构建/测试命令以及是否通过。

完成测试：用户不看书就能用一句话解释项目，且构建/测试命令是从 runbook 复现的，而不是凭记忆。

## 阶段 2 — Skeleton

目标：空间感。用户知道东西放在哪里，并能说出任意功能的入口点。

检查清单：

1. 建立入口清单：HTTP 路由、CLI 子命令、导出的符号、队列消费者、定时任务。
2. 把 `02-map.md` 写成假设，而非事实。在走过一条边之前，每条边都标 `inferred`。
3. 选定 spine（见 `repo-archetypes.md`）并记录 `focus`。
4. 在展示正确位置之前，先请用户把三个指定功能放到 map 上。

grep 目标：

```bash
rg -n "\.(get|post|put|patch|delete)\(|@(app|router)\.(route|get|post)" -g '!node_modules'
rg -n "cobra\.Command|argparse|click\.command|clap::Command|@click"
rg -n "subscribe|consume|handler|listener|worker" -g '!node_modules' -g '!vendor'
rg -n "export (default )?(function|class|const)" src/ lib/ 2>/dev/null
```

记录：入口清单表（入口、类型、`path:line`、可信度）、spine 选择及其理由、`focus`。

完成测试：给定用户命名的任意功能，用户能说出入口点。错误答案记录为 `misconceptions`，而不是悄悄纠正。

## 阶段 3 — Spine

目标：时间感。一条端到端调用链，从入口一直到用户关心的效果。

检查清单：

1. 先让用户用自己的话描述这条链；那个预测就是基线证据。
2. 逐跳追踪。每跳之后，在揭示前问 "what happens next?"。
3. 每一跳写成 `path:line` 加一行说明它做什么。没有锚点的跳只是猜测。
4. 记下让用户意外的分支；那是最有价值的误解。
5. 写 `03-spine.md`。

grep 目标取决于原型；使用 `repo-archetypes.md` 中的表格。通用情形下：

```bash
rg -n "functionName|handlerName|methodName" -g '!node_modules' -g '!vendor'
rg -n "await |\.then\(|yield |return " <the file at the current hop>
```

记录：有序的跳列表，每跳带锚点和 `verified`/`inferred`；用户最初的预测（逐字）；复述所用时间。

完成测试：用户凭记忆按顺序复述调用链，并能打开每一跳对应的文件。只有位置没有顺序是 L1；只有顺序没有位置是 L2。

## 阶段 4 — Structure

目标：结构感。代码为什么是这个形状，这个形状付出了什么代价。

检查清单：

1. 挑出 spine 触及的三个抽象。不要引入新抽象。
2. 对每个抽象：它解决什么问题、取代了什么、禁止了什么。
3. 每个取舍及其代价各用一句话说明。
4. 先读现有架构文档，再把 `04-architecture.md` 写成仅含差异（DELTA）。
5. 最多一张图，且仅当它承载了文字无法表达的边时才画。

grep 目标：

```bash
rg -n "interface |abstract class |protocol |trait |type .* struct" <module dirs>
rg -n "TODO|HACK|deprecated|legacy|workaround" -g '!node_modules' -g '!vendor'
git log --oneline -20 -- <path>
```

记录：三个取舍，每个都带能看到该约束的锚点，以及文档差异。

完成测试：用户解释三个取舍及其代价，并能指出强制执行每个取舍的代码位置。

## 阶段 5 — Apply

目标：可操作性。用户能推理变更影响。

检查清单：

1. 取一处用户真正需要的 S 级变更（或用户提出的一处）。
2. 在任何分析之前，先请用户说出会改哪些文件、影响范围有多大。
3. 走查影响面：调用点、测试、迁移、配置、契约、消费者。
4. 起草补丁计划：有序步骤、每步的验证、回滚。
5. 不要写补丁。本 skill 止步于计划，除非用户在别处要求实现。

grep 目标：

```bash
rg -n "symbolName" -g '!node_modules' -g '!vendor'
rg -n "symbolName" --type test
rg -n "tableName|env\.|config\." -g '!node_modules'
```

记录：含影响范围的补丁计划，以及用户分析前的猜测与实测集合的对比。

完成测试：对一处 S 级变更，文件与影响范围都命名正确，且至少找到一个不显眼的调用点。

## runbook 优先

`00-runbook.md` 比任何图表都活得久。一个有可用 runbook 但没有架构图的新工程师，第一天就能交付；反过来则不成立。它必须包含：

- 带版本的前置依赖，以及如何检查它们。
- 安装、构建、运行、测试、lint 命令，逐字且已验证。
- 必需的环境变量及其取值来源。
- 种子数据或 fixtures。
- 已知陷阱：不稳定的测试、端口、代码生成步骤、有顺序依赖的初始化、必须运行的服务。

每行标注 `verified`（你亲自运行过）或 `inferred`（从配置读到）。inferred 的命令是带引用的猜测。
