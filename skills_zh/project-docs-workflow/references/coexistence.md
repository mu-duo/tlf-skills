# 与其他 skill 共存

## 范围

单 context 布局。多 context（`CONTEXT-MAP.md`）不在本方案覆盖范围内。

## `domain-modeling`

主动打磨模型的对话。基础 CONTEXT 与 ADR 格式兼容。两者都适用时，**以本方案物化的规则治理项目文档**——它是基础格式的超集（ADR 生命周期 v2（就地修改 + Log、删除→墓碑桩、引用核查、目录式 README）；issue 路由）。不要在本家变体之外分叉或重新定义基础格式。

独立 skill 可选；内部兜底 `references/deps/domain-modeling.md`。

> 本包**不随附**任何独立依赖 skill：每个被引用的能力先按已安装 skill 名称解析，否则使用 `references/deps/` 中的内部兜底参考。下文的独立名称可作为可选的上游名称保留。

## `grill-with-docs`

一个包装器：`grilling` + `domain-modeling`，**交织进行**——每轮 grilling 暴露出术语或决策时立即写下：定案的术语写入 `CONTEXT.md`；满足三条 ADR 判据（难以回退 / 无上下文会令人意外 / 存在真实权衡）的决策记为 ADR。`grill-me` 只是 `grilling` 的入口别名，没有独立流程。

独立 skill 可选；内部兜底 `references/deps/grilling.md` + `references/deps/domain-modeling.md`。

## `deepwork`

大规模或高风险的多阶段工作放在 `deepwork` 下进行。本方案的 `workflow.md` 用于例行的单 issue 开发；两者绝不叠加——每项工作只选其一。

独立 skill 可选；内部兜底 `references/deps/boundaries.md`。

## `tdd`

嵌套在 `workflow.md` 的细节步骤内（红 → 绿循环）。seam 确认并入规划对齐——不设第二道门禁。

独立 skill 可选；内部兜底 `references/deps/tdd.md`。

## `retro`

工作流第五步收尾回顾仅做文档同步。会话 / agent 复盘属于 `retro`，不在这里。

独立 skill 可选；内部兜底 `references/deps/boundaries.md`。

## `doc-opt`

对指定文件做事后行文润色。作为完整附赠 skill 随包提供（`skills/doc-opt`），另有兜底文档 `references/deps/doc-opt.md`。需要时可在撰写之后串接使用；仅限显式调用。

## 旧式 `.scratch` 风格跟踪器

这些项目不用它做 issue 跟踪（DA_AGENT 先例：ADR-0012，由 ADR-0026 细化）。本 skill 的 `docs/issues` 约定取代旧式 `.scratch` 风格跟踪约定。

使用本方案的项目不会用一个通用脚手架工具来搭建这些相同表面（`docs/agents/domain.md`、`## Agent skills` 区块、偏好 `CLAUDE.md`）；如果之前运行过这类工具，请对照本方案规则审查其残留（init 报告差异；绝不覆盖）。

## 调用

本 skill 仅支持手动调用。agent 的运行时遵循来自项目物化的文件（`AGENTS.md` + `docs/agents/*`），而不是自动加载本 skill。
