<!-- 模板：docs/teach/<user>/runbook.md -->
<!-- 配套产物，与 00-model.md 一同写就，并随 03-operations.md 刷新。 -->
<!-- 替换 <...>。给每条命令标注 verified（你运行过）或 inferred（从配置读到）。 -->
<!-- 这个文件的可复用价值高于任何 brief。保持它可执行，而不是叙述性。 -->

# Runbook：<repo>

最后验证：<YYYY-MM-DD>，基于 <commit sha> / <OS>
事实来源：下文每条命令的 `<path:line>`。

## 前置条件

| 工具 | 版本 | 检查 | verified/inferred |
| --- | --- | --- | --- |
| <运行时> | <版本> | `<command>` | <verified> |
| <包管理器> | <版本> | `<command>` | <inferred> |

## 安装

```bash
<install command>
```

锚点：`<path:line>`

## 运行

```bash
<run command>
```

预期输出：<一行>
锚点：`<path:line>`

## 测试

```bash
<test command>
```

结果：<N passed / N skipped / N failed>，于 <sha>

## Lint / 类型检查

```bash
<command>
```

## 环境

| 变量 | 必需 | 值来自哪里 |
| --- | --- | --- |
| `<VAR>` | <是/否> | <path:line 或密钥存储> |

## 种子数据

<命令，或「无」>

## 已知陷阱

- <不稳定测试、端口冲突、代码生成步骤、顺序要求、必须运行的服务> — `<path:line>`

## 尚未验证

- <仅由推断得出的命令或步骤>
