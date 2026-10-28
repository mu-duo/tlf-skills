<!-- 模板：docs/teach/<user>/00-runbook.md -->
<!-- 阶段 1 产物。替换 <...>。每条命令标记 verified（你运行过）或 inferred（从配置读到）。 -->
<!-- 本文件的可复用价值高于任何图表。保持它可执行，而不是叙述。 -->

# Runbook: <repo>

最后验证：<YYYY-MM-DD> 于 <commit sha> / <OS>
事实来源：下面每条命令的 `<path:line>`。

## 前置依赖

| 工具 | 版本 | 检查方式 | verified/inferred |
| --- | --- | --- | --- |
| <runtime> | <version> | `<command>` | <verified> |
| <package manager> | <version> | `<command>` | <inferred> |

## 安装

```bash
<install command>
```

锚点：`<path:line>`

## 运行

```bash
<run command>
```

预期输出：<一行说明>
锚点：`<path:line>`

## 测试

```bash
<test command>
```

结果：<N passed / N skipped / N failed> 于 <sha>

## Lint / 类型检查

```bash
<command>
```

## 环境

| 变量 | 必需 | 取值来源 |
| --- | --- | --- |
| `<VAR>` | <yes/no> | <path:line or secret store> |

## 种子数据

<命令，或 "none">

## 已知陷阱

- <不稳定的测试、端口冲突、代码生成步骤、顺序依赖、必须运行的服务> — `<path:line>`

## 尚未验证

- <仅为 inferred 的命令或步骤>
