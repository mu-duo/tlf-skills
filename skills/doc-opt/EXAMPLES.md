# Doc Opt — Examples

Behavioral anchors for the rules in `SKILL.md`. Each pair shows one rule applied.

## Style — 中文

**Before**

> 其实呢，这个模块的性能问题，说白了主要就是每次请求都重新创建连接。值得注意的是，换成连接池之后，其实功能不会有太大影响，但是速度会快很多。

**After**

> 性能瓶颈来自每次请求重建连接。改用连接池，功能不变，延迟显著下降。

Removed: 其实呢 / 说白了 / 主要就是 / 值得注意的是 / 其实 / "不会有太大影响"（模糊）→ 功能不变 / "会快很多"（模糊）→ 延迟显著下降。

## Style — English

**Before**

> Basically, it's worth noting that the retry logic just retries forever, which is, of course, a problem. Simply add a cap and you're good to go.

**After**

> The retry logic loops forever. Cap the retry count.

Removed: Basically / it's worth noting / just / of course / Simply / you're good to go.

## Diagram — ASCII to mermaid

**Before**

```text
+--------+     +---------+     +---------+
| Client | --> | Gateway | --> | Service |
+--------+     +---------+     +---------+
```

**After**

```mermaid
flowchart LR
    client[Client] --> gateway[Gateway] --> service[Service]
```

The mapping is lossless: same nodes, same order, same direction. When an annotation has no mermaid equivalent, ask before converting.

## Citations — rejected and accepted forms

**Rejected (bare numbers)**

> Batched requests cut per-call overhead in half [2]. The gateway supports HTTP/2 [1].

**Accepted (jumpable)**

> Batched requests cut per-call overhead in half ([MCP spec — Batching](https://modelcontextprotocol.io/specification/2025-06-18#batching)). The gateway supports HTTP/2 ([RFC 9113](https://www.rfc-editor.org/rfc/rfc9113)).

**Accepted (self-contained, no stable target)**

> Per the MCP specification, batching cuts per-call overhead.

**Unknown source — move to the end**

```markdown
## 待补充来源

- 吞吐提升数据（原文 [3]）：来源不明，待补。
```

## mermaid vs SVG

| Situation | Use |
| --- | --- |
| Flow, sequence, state, class, ER, gantt, pie | mermaid |
| Annotated architecture, custom positioning, layout mermaid misrepresents | svg |
| Diagram too large or reused across documents | sibling `.svg` file, linked |
| ASCII art or image explicitly requested by the user | keep as asked |
