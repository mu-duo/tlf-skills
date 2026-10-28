<!-- 模板：docs/teach/<user>/02-map.md -->
<!-- 阶段 2 产物。替换 <...>。把 map 写成假设；走查过之后才把边提升为 verified。 -->
<!-- 范围限定在 spine 上。整棵树的 map 只是目录。 -->

# Map: <repo>

假设状态：<草稿 | 部分验证 | spine 上已验证>
原型：<http-service | cli | library | event-driven | plugin-di | monorepo | data-pipeline | codegen>

## 入口点

| 入口点 | 类型 | 锚点 | 可信度 |
| --- | --- | --- | --- |
| <name> | <http 路由 / cli 命令 / 导出 / 消费者 / job> | `<path:line>` | <verified/inferred> |

## 边界

| 边界 | 跨越什么 | 锚点 | 可信度 |
| --- | --- | --- | --- |
| <api / db / queue / 文件系统> | <数据形状> | `<path:line>` | <verified/inferred> |

## Spine

Focus：<用户对 "which part will you change first?" 的回答>
选定的 spine：<name>
原因：<一句话>
回退：<yes/no — 若是，明确说明>

## 边

```text
<entrypoint> -> <module> -> <module> -> <effect>
```

在阶段 3 走查之前，上面每个箭头都是 `inferred`。

## 不在范围内

- <有意排除的包或功能，以及原因>

## 更正

<!-- 构建 map 时做出的错误猜测。保留它们；它们能预测用户会在哪里迷路。 -->

- <guess> 是错的；实际是 <...>。锚点：`<path:line>`
