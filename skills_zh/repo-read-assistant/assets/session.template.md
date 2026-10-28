<!-- 模板：docs/teach/<user>/sessions/YYYY-MM-DD.md -->
<!-- 每次会话一个文件。替换 <...>。内容是发生了什么，不是 brief 的摘要。 -->
<!-- 下一个 agent 从本文件加 profile.yml 恢复；没写在这里的东西都会丢失。 -->

# 会话 <YYYY-MM-DD>

用户：<slug>
仓库提交：<sha>
Brief：<00-model | 01-map | 02-structure | 03-operations | drill>
模式：<tour | tutor | drill>
时长：<分钟>

## 为什么是这份 brief

<一句话：上次会话留下了什么未解决，以及为什么接下来是这一层。>

## 恢复状态

- 上次会话：<YYYY-MM-DD 或 "first session">
- 到期复习的概念：<ids>
- 带入的 pending_explanations：<count>

## 这份 brief

- 路径：`docs/teach/<user>/<file>.md`
- 写作方式：<新文档 | 针对 <doc> 的增量>
- 长度：<字数>，对照上限 <cap>
- 刻意忽略：<简化契约，逐字引自 brief>

## 交付

- 为什么是这一层：<一句话>
- 阅读时带着的一个问题：<逐字>

## 读后的模型检查

### 1. 定位

- 问题：<功能或术语>
- 用户的回答：> <逐字>
- 判定：<correct / partial / wrong>

### 2. 预测影响

- 问题：<改动及其后果>
- 用户的回答：> <逐字>
- 判定：<correct / partial / wrong>

### 3. 解释为何，以及为何不

- 问题：<设计选择、替代方案与代价>
- 用户的回答：> <逐字>
- 判定：<correct / partial / wrong>

## 对 brief 的纠正

| 章节 | 用户的模型原本是什么 | brief 现在说什么 | 锚点 |
| --- | --- | --- | --- |
| <标题> | <错误的关系或事实> | <纠正后的句子> | `<path:line>` |

<!-- 在错误的确切位置修改。不要附上一篇新文章。 -->

## 概念更新

| id | 之前层级 | 之后层级 | 置信度 | 准确度 | 证据（逐字） | next_review |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | <Lx> | <Ly> | <0.0> | <0.0> | <引用> | <YYYY-MM-DD> |

## 发现的误解

- <逐字信念> — 在 `<brief section>` / `<path:line>` 处纠正

## 降级与过载

- <观察到的信号> -> <应对>。余下部分模式：<...>

## 白板测试

- 凭记忆画出：<六个部分，或回路与名词>
- 缺失或错误：<缺少了什么>
- 结果：<passed / failed>

## 触及的产物

- [ ] `profile.yml`
- [ ] `<brief>` — <改了什么>
- [ ] `runbook.md` / `glossary.md` — <改了什么>

## 下次会话

- 下一份 brief：<哪一份，以及为什么>
- 从什么开始：<概念 id 及原因>
- 待处理：<排队待排期的解释>
