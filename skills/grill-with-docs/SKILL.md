---
name: grill-with-docs
description: 追问式访谈的同时产出文档（ADR 与术语表）。
disable-model-invocation: true
---

# Grill with Docs

> 轻量精简版，裁剪自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 grill-with-docs（MIT License, Copyright (c) 2026 Matt Pocock）。若环境已安装同名完整 skill，请优先使用完整版。

`grill-with-docs` 是一个包装器：把 `grilling` 与 `domain-modeling` 一起跑。

- 用 `grilling` 推进设计树、逐轮追问，直到达成共同理解。
- 同时用 `domain-modeling`：术语确定时当场写入 `CONTEXT.md`；决策满足「难以逆转 / 无背景会意外 / 真实取舍」三条时记录 ADR。

两个流程交织进行：每轮追问中浮现的术语与决策，立刻落成文档。

若环境未安装，按 `project-docs-workflow/references/deps/grilling.md` 与 `project-docs-workflow/references/deps/domain-modeling.md` 执行。
