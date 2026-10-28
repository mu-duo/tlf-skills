<!-- 模板：docs/teach/<user>/03-spine.md -->
<!-- 阶段 3 产物。替换 <...>。只写一条链。每一跳都需要 path:line 和状态。 -->
<!-- 没有锚点的跳只是猜测；标为 inferred。 -->

# Spine: <chain name>

Focus：<用户陈述的 focus>
触发：<请求 / 命令 / 事件>
效果：<用户在末端观察到的效果>
仓库提交：<sha>

## 调用链

| # | 跳 | 发生了什么 | 锚点 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | <entrypoint> | <一行说明> | `<path:line>` | <verified/inferred> |
| 2 | <module> | <一行说明> | `<path:line>` | <verified/inferred> |
| 3 | <module> | <一行说明> | `<path:line>` | <verified/inferred> |
| 4 | <module> | <一行说明> | `<path:line>` | <verified/inferred> |
| 5 | <effect> | <一行说明> | `<path:line>` | <verified/inferred> |

## 分支点

<!-- 调用链可能走另一条路的地方。这些是价值最高的问题。 -->

- 在 `<path:line>`：<condition> 会走向 <other path>。尚未走查。

## 用户最初的预测

> <用户在追踪前所预期的内容，逐字引用>

差异：<他们错在哪，一句话>

## 复述检查

- 日期：<YYYY-MM-DD>
- 顺序正确：<yes/no>
- 所有跳都定位到：<yes/no>
- 用时：<秒数>

## 未闭合的缺口

- <仍为 inferred 的跳>
