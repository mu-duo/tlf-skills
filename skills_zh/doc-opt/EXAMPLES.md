# 文档优化 — 示例

`SKILL.md` 中规则的行为锚点。每个对照展示一条规则的应用。

## 文风 — 中文

**修改前**

> 其实呢，这个模块的性能问题，说白了主要就是每次请求都重新创建连接。值得注意的是，换成连接池之后，其实功能不会有太大影响，但是速度会快很多。

**修改后**

> 性能瓶颈来自每次请求重建连接。改用连接池，功能不变，延迟显著下降。

删去：其实呢 / 说白了 / 主要就是 / 值得注意的是 / 其实 / “不会有太大影响”（模糊）→ 功能不变 / “会快很多”（模糊）→ 延迟显著下降。

## 文风 — 英文

**修改前**

> Basically, it's worth noting that the retry logic just retries forever, which is, of course, a problem. Simply add a cap and you're good to go.

**修改后**

> The retry logic loops forever. Cap the retry count.

删去：Basically / it's worth noting / just / of course / Simply / you're good to go.

## 图表 — ASCII 转 mermaid

**修改前**

```text
+--------+     +---------+     +---------+
| Client | --> | Gateway | --> | Service |
+--------+     +---------+     +---------+
```

**修改后**

```mermaid
flowchart LR
    client[Client] --> gateway[Gateway] --> service[Service]
```

映射无损：节点相同、顺序相同、方向相同。当注释没有对应的 mermaid 表达时，转换前先询问。

## 引用 — 拒绝与接受的形式

**拒绝（裸数字）**

> Batched requests cut per-call overhead in half [2]. The gateway supports HTTP/2 [1].

**接受（可跳转）**

> Batched requests cut per-call overhead in half ([MCP spec — Batching](https://modelcontextprotocol.io/specification/2025-06-18#batching)). The gateway supports HTTP/2 ([RFC 9113](https://www.rfc-editor.org/rfc/rfc9113)).

**接受（自包含，无稳定目标）**

> Per the MCP specification, batching cuts per-call overhead.

**来源不明 — 移到末尾**

```markdown
## 待补充来源

- 吞吐提升数据（原文 [3]）：来源不明，待补。
```

## mermaid 与 SVG

| 场景 | 用法 |
| --- | --- |
| 流程、时序、状态、类、ER、gantt、pie | mermaid |
| 带注释的架构、自定义定位、mermaid 无法正确表达的布局 | svg |
| 图表过大或在多个文档中复用 | 同目录 `.svg` 文件，并链接 |
| 用户明确要求 ASCII art 或图片 | 按要求保留 |
