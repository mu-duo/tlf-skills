---
name: retro
description: 对编码会话或 agent 表现做回顾，输出针对 agent 环境的改进建议。
disable-model-invocation: true
---

# Retro（会话回顾）

> 轻量精简版，裁剪自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 retro（MIT License, Copyright (c) 2026 Matt Pocock）。若环境已安装同名完整 skill，请优先使用完整版。

会话/agent 回顾的所有权属于本 skill；`project-docs-workflow` 第五步「回顾」只是文档同步，不做会话回顾。

最小回顾至少覆盖三问：

1. **发生了什么**：读指定会话的原始记录（未指定则默认当前会话），尽量取原始来源。
2. **保留什么**：哪些做法或环境配置有效，值得延续。
3. **改变什么**：给出针对 agent **环境**的改进候选（导航指针、自动化检查、编码规范、全局指令瘦身、工具经济性、多余指令、信息可达性），按严重程度排序呈现给用户。

若环境未安装完整 skill，按 `project-docs-workflow/references/deps/boundaries.md` 的最小三问回顾执行。
