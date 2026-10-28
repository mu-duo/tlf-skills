<!-- 模板：docs/teach/<user>/sessions/YYYY-MM-DD.md -->
<!-- 每次会话一个文件。替换 <...>。内容是这 40 分钟的实录，不是总结。 -->
<!-- 下一个 agent 从本文件加 profile.yml 续接；没写在这里的东西都丢了。 -->

# 会话 <YYYY-MM-DD>

用户：<slug>
仓库提交：<sha>
阶段：<orientation | skeleton | spine | structure | apply | drill>
模式：<tour | tutor | drill>
密度：<low | normal | high>
时长：<分钟数>

## 目标

<一句话。只覆盖一个阶段。>

## 续接状态

- 上次会话：<YYYY-MM-DD 或 "first session">
- 待复习概念：<ids>
- 带入的 pending_explanations：<count>

## 热身回忆

| 概念 | 问题 | 回答 | 正确 |
| --- | --- | --- | --- |
| <id> | <question> | <verbatim> | <yes/partial/no> |

## 预测与揭示

### 预测 1

- 问题：<揭示前你问了什么>
- 用户回答：> <verbatim>
- 揭示：<事实>
- 锚点：`<path:line>`
- 差异：<具体错在哪>

### 预测 2

- 问题：
- 用户回答：> <verbatim>
- 揭示：
- 锚点：`<path:line>`
- 差异：

## 概念更新

| id | 之前等级 | 之后等级 | 自信度 | 准确度 | 证据（逐字） | next_review |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | <Lx> | <Ly> | <0.0> | <0.0> | <quote> | <YYYY-MM-DD> |

## 发现的误解

- <逐字记录的信念> — 已在 `<path:line>` 纠正

## 降级与过载

- <观察到的信号> -> <回应>。此后模式：<...>

## 阶段通过测试

- 测试：<references/curriculum.md 中的完成标准>
- 结果：<passed/failed>
- 证据：<用户做了什么>

## 触及的产物

- [ ] `profile.yml`
- [ ] `<artifact>` — <改了什么>

## 下次会话

- 从什么开始：<概念 id 及原因>
- 阶段：<下一阶段，或重复当前阶段>
- 待办：<排队待安排的讲解>
