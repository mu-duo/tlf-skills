---
name: doc-opt
description: "精炼地提升文档的专业性：删除填充语，使用 mermaid/SVG 图表，让引用可跳转。"
disable-model-invocation: true
argument-hint: "要优化的文件或路径"
---

# 文档优化

就地优化指定的 markdown 文档。默认目标：`.md` / `.mdx`。其他格式仅在明确指定时处理。

## 约定

- 只改动指定文件；绝不扫描整个仓库。
- 压缩只删冗余，不删事实。
- 代码围栏、frontmatter、命令与引用输出保持逐字节一致。
- 结构性调整（删除小节、重排、合并图表）先出方案，再执行修改。
- 结束时给出变更报告：涉及文件、变更类别、`待补充来源`、自检证据。

## 文风（默认 L2）

L1 只删填充语；L3 采用电报式。仅在用户明确指定级别时才上调或下调。

- 删除不承载信息的词：填充语、含糊措辞、无意义的开场白。
- 使用简短陈述句、主动语态；用动词代替名词化表达。
- 内容可枚举时使用列表和表格。
- 技术术语保持准确；标题保留，除非标题本身有问题。

见到即删的填充语：

| ZH | EN |
| --- | --- |
| 其实、值得注意的是、让我们来看看、不得不说、说白了、众所周知 | basically, actually, of course, it's worth noting, let's dive in |

`just` 和 `其实` 逐句判断：仅在字面义（“only”）或标记真实对比时保留。

## 图表

默认使用 mermaid。按关系选择类型：flowchart、sequence、state、class、ER、gantt、pie。

SVG 用于 mermaid 无法表达或需要控制布局的场景——带注释的架构图、自定义定位。小图使用内联 SVG；大图或复用的图使用同目录 `.svg` 文件并附链接。

ASCII art 和图片图表仅在用户明确要求时出现。现有 ASCII 图在映射无损时转换为 mermaid/SVG；语义有歧义时先提问。截图保留：补充图注和可跳转的引用。

## 引用

裸数字（`[1]`）不是引用。每条引用都必须可跳转或自包含：

| 目标 | 形式 |
| --- | --- |
| 本文档的小节 | `[label](#anchor)` |
| 仓库其他位置的文件 | `[label](relative/path.md#anchor)` |
| 外部来源 | `[label](https://full-url)` |

没有稳定目标时，将来源写进句子（“按 MCP 规范，……”）。无法识别的来源放入文档末尾的 `待补充来源` 列表，并写入变更报告。

## 工作流

1. 完整阅读目标文件。标记不得改动的 frontmatter 和代码。
2. 规划结构性变更；等待确认。
3. 重写：先文风，再图表，最后引用。
4. 运行自检。
5. 报告文件、变更类别、`待补充来源`、自检证据。

## 自检

报告前运行；将证据写入报告。用目标路径替换 `<files>`；忽略代码围栏内的命中。

```bash
# filler survivors — expect no hits
rg -n "其实|值得注意的是|让我们来看看|说白了|basically|actually|of course|worth noting" <files>

# bare numeric citations — expect no hits
rg -n '\[\d+\]' <files>

# ASCII diagrams — expect no hits unless the user asked for them
rg -n '[┌┐└┘├┤│─]|\+--' <files>

# mermaid fences — count them; each needs a declaration line and a closing fence
rg -n '^```mermaid' <files>
```

`EXAMPLES.md` 收录前后对照：文风（中/英）、ASCII→mermaid、引用形式、mermaid 与 SVG 的选择。
