# project-docs-workflow 使用教程

一份 10 分钟的预览：它解决什么问题、由哪些文档组成、日常怎么走，以及第一次初始化会发生什么。规则细节以 `references/` 为准，本文不重复命令表。

## 1. 一分钟定位

**它是什么**：一套把「产品意图、实现目标、当前事实、决策记录」分层存档，并以 issue 为单位、按五步推进的文档工作流。skill 只提供规则与模板；初始化后，规则被复制进你的项目，由项目自己的文档接管运行时。

**适合**：中大型功能、长期维护、多人或多 agent 协作、害怕文档与代码脱节的项目。

**不适合**：一次性脚本、纯原型、只有几个文件且不打算长期演进的小工具。

**30 秒上手**

1. `npx @tanlinfeng/project-docs-workflow@latest install`（中文镜像加 `--zh`）。
2. 在项目根对 agent 说：`用 project-docs-workflow 初始化文档系统`。该 skill 禁止模型自动调用，必须点名。
3. 打开 `AGENTS.md` 与 `docs/agents/`，按报告里的 `Next:` 逐项补齐。

## 2. 它治什么病

文档腐烂通常不是"没人写"，而是**写错了层**：

- 代码变了文档没变——因为只记了事实，没有记目标。
- PRD 变成变更日志——因为把历史和设计混在一起。
- 同一个问题反复讨论——因为决策没有落地成可查的记录。

解法是分层，并且让每层有明确的维护者：

| 层 | 回答的问题 | 位置 | 谁维护 |
| :--- | :--- | :--- | :--- |
| 意图 | 为谁、解决什么 | `docs/product/` | orchestrator |
| 目标 | 具体怎么做、接口与约束 | SPEC | orchestrator + user |
| 事实 | 现在实际跑成什么样 | `docs/current/` | coder（收尾时更新） |
| 决策 | 为什么这样选 | `docs/adr/` | 任何角色，需评审 |
| 工作单元 | 这一次做什么 | `docs/issues/` | coder |

关键不是"写得多"，而是**每层只写它该写的**：PRD 不写实现，Current 不写历史，ADR 不写步骤。

## 3. 文档地图

<figure class="fig">
<svg viewBox="0 0 760 300" role="img" aria-label="文档分层与流向示意">
  <defs>
    <marker id="guide-arrow-1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" class="arrowhead"/>
    </marker>
  </defs>
  <rect class="box" x="20" y="30" width="200" height="72" rx="10"/>
  <text class="label" x="120" y="62" text-anchor="middle">PRD · 意图与范围</text>
  <text class="muted" x="120" y="84" text-anchor="middle">docs/product/</text>
  <rect class="box" x="280" y="30" width="200" height="72" rx="10"/>
  <text class="label" x="380" y="62" text-anchor="middle">SPEC · 目标与接口</text>
  <text class="muted" x="380" y="84" text-anchor="middle">01-spec / 02-interfaces</text>
  <rect class="box" x="540" y="30" width="200" height="72" rx="10"/>
  <text class="label" x="640" y="62" text-anchor="middle">Current · 当前事实</text>
  <text class="muted" x="640" y="84" text-anchor="middle">docs/current/</text>
  <line class="edge" x1="220" y1="66" x2="280" y2="66" marker-end="url(#guide-arrow-1)"/>
  <line class="edge" x1="480" y1="66" x2="540" y2="66" marker-end="url(#guide-arrow-1)"/>
  <rect class="box" x="280" y="180" width="200" height="64" rx="10"/>
  <text class="label" x="380" y="208" text-anchor="middle">ADR · 决策与理由</text>
  <text class="muted" x="380" y="228" text-anchor="middle">docs/adr/</text>
  <line class="edge dashed" x1="380" y1="180" x2="380" y2="102" marker-end="url(#guide-arrow-1)"/>
  <text class="muted" x="392" y="148">约束</text>
  <rect class="box" x="20" y="180" width="200" height="64" rx="10"/>
  <text class="label" x="120" y="208" text-anchor="middle">issue · 工作单元</text>
  <text class="muted" x="120" y="228" text-anchor="middle">docs/issues/</text>
  <line class="edge" x1="120" y1="180" x2="120" y2="102" marker-end="url(#guide-arrow-1)"/>
  <text class="muted" x="132" y="148">驱动</text>
  <rect class="box" x="540" y="180" width="200" height="64" rx="10"/>
  <text class="label" x="640" y="208" text-anchor="middle">toc.yml · 发布清单</text>
  <text class="muted" x="640" y="228" text-anchor="middle">docs/toc.yml</text>
  <line class="edge dashed" x1="640" y1="180" x2="640" y2="102" marker-end="url(#guide-arrow-1)"/>
  <text class="muted" x="652" y="148">发布范围</text>
</svg>
<figcaption>文档按“意图 → 目标 → 事实”分层：ADR 约束设计，issue 驱动一次工作，toc 决定对外发布什么。</figcaption>
</figure>

日常阅读顺序：先看 PRD 定范围，再读 SPEC 找实现口径，用 Current 确认现状，最后查 ADR 看有没有已定约束。四者冲突时：实现细节以 SPEC 为准，范围与意图以 PRD 为准。

## 4. 五步流程

<figure class="fig">
<svg viewBox="0 0 760 150" role="img" aria-label="五步开发流程">
  <defs>
    <marker id="guide-arrow-2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" class="arrowhead"/>
    </marker>
  </defs>
  <text class="muted" x="380" y="26" text-anchor="middle">硬规则：对齐先于实现；未确认范围不进入实现</text>
  <rect class="box" x="20" y="50" width="128" height="64" rx="10"/>
  <text class="label" x="84" y="78" text-anchor="middle">1 · 规划</text>
  <text class="muted figure-note" x="84" y="98" text-anchor="middle">对齐 → 方案</text>
  <rect class="box" x="168" y="50" width="128" height="64" rx="10"/>
  <text class="label" x="232" y="78" text-anchor="middle">2 · 骨架</text>
  <text class="muted figure-note" x="232" y="98" text-anchor="middle">可运行纵切</text>
  <rect class="box" x="316" y="50" width="128" height="64" rx="10"/>
  <text class="label" x="380" y="78" text-anchor="middle">3 · 细节</text>
  <text class="muted figure-note" x="380" y="98" text-anchor="middle">主路径完成</text>
  <rect class="box" x="464" y="50" width="128" height="64" rx="10"/>
  <text class="label" x="528" y="78" text-anchor="middle">4 · 异常</text>
  <text class="muted figure-note" x="528" y="98" text-anchor="middle">失败与边界</text>
  <rect class="box" x="612" y="50" width="128" height="64" rx="10"/>
  <text class="label" x="676" y="78" text-anchor="middle">5 · 回顾</text>
  <text class="muted figure-note" x="676" y="98" text-anchor="middle">文档同步</text>
  <line class="edge" x1="148" y1="82" x2="168" y2="82" marker-end="url(#guide-arrow-2)"/>
  <line class="edge" x1="296" y1="82" x2="316" y2="82" marker-end="url(#guide-arrow-2)"/>
  <line class="edge" x1="444" y1="82" x2="464" y2="82" marker-end="url(#guide-arrow-2)"/>
  <line class="edge" x1="592" y1="82" x2="612" y2="82" marker-end="url(#guide-arrow-2)"/>
</svg>
<figcaption>一轮 issue 的推荐节奏：骨架是第一个评审点，回顾只做文档同步。</figcaption>
</figure>

| 步骤 | 谁做 | 产出 | 门禁 |
| :--- | :--- | :--- | :--- |
| 规划 | orchestrator + user 对齐 SPEC；coder 写验收与 1–2 句方案 | issue 的 `## 步骤` + 方案 | 未对齐不开工 |
| 骨架 | coder | 最小可运行纵切 + 一次运行证据 | 给用户看第一眼 |
| 细节 | coder | 主路径实现与代码质量 | 测试遵循 `testing.md` |
| 异常 | coder | 失败路径、边界与稳定性 | 同上，不写弱断言 |
| 回顾 | coder 更新 Current 并提议 SPEC；orchestrator 复核 | 文档同步 + `## 测试` 证据 | 文档未同步不算完成 |

三个角色：**user** 负责意图、范围与批准；**orchestrator** 维护 PRD、与 user 共同编写 SPEC、拥有 `toc.yml`；**coder** 读 SPEC 实现、收尾更新 Current，SPEC 变更只能经 issue 提议。单 agent 时允许一人分饰，但换角色要显式说明，边界不合并。

骨架对纯修复可跳过，但要在 Log 写明理由；功能与结构性工作不可跳过。

## 5. init 实操

init 由你点名触发。它会先读 `docs/agents/metadata.yml` 判定状态：版本相同且产物齐全则**零写入**；版本相同但缺文件只做加法；版本落后走建立流程；版本超前只提示。

初始化会补齐这些东西：

| 分组 | 产物 |
| :--- | :--- |
| 规则层 | `docs/agents/{workflow,issues,testing,domain}.md`、`metadata.yml`、`deps/` |
| 产品层 | `docs/product/{00-README,01-requirements,02-architecture}.md` |
| 事实层 | `docs/current/00-README.md` |
| 决策层 | `docs/adr/README.md` |
| 索引与入口 | `docs/toc.yml`、`CONTEXT.md`、`AGENTS.md` 的 `## Agent skills` 块 |
| 工作单元 | `docs/issues/` 目录树 |

覆盖口径只有一条：**缺失自动创建；已存在的文件只报告差异，改写或移动必须先给出逐文件 diff 并获得确认**。项目对模板的本地修改是合法的，init 不会强制回滚。

报告字段固定，值是示意：

```text
## Init report
- State: unknown
- Repair: scaffold
- Created: AGENTS.md, docs/agents/*, docs/product/*, docs/current/00-README.md
- Aligned: （无）
- Diff: （无）
- Metadata: — → 5.12.0（updated）
- Legacy drift: （无）
- Next: 选定 Current 基线 → 填写 01-requirements
```

第一次使用建议只做三件事：选定 Current 基线（revision 或 release + 日期）、把 `01-requirements.md` 的占位换成真实场景、按模块是否成形再拆模块 PRD 与 `00-index.md`。不要急着补全所有文档——规则要求"未确定的设计保持缺席"，缺席表示未定，而不是禁止。

## 6. 其他 skill 与延伸阅读

同一包里还有五个可选 skill，按需使用，不装也不影响主流程：

| skill | 何时用 | 别用它做 |
| :--- | :--- | :--- |
| `doc-opt` | 就地收紧 Markdown 文风与去冗余（默认 L2），必要时补 Mermaid/SVG 图 | 替代规则源；扫全仓库 |
| `docs-html-view` | 把 PRD/SPEC/Current/ADR 发布成多页 Sphinx 站点 | 渲染任意 Markdown；它不产出单文件 HTML |
| `docs-docx-view` | 评审或交付时导出 Word | 当作日常编辑源 |
| `lite-task` | 小范围、低风险的轻量流程 | 跨系统或高风险改动 |
| `repo-read-assistant` | 接手陌生仓库，产出 `docs/teach/` | 替代项目自身文档 |

想读细节时按需取用：

- `../references/workflow.md` — 五步、角色、变更协议、完成判据。
- `../references/prd.md` — PRD / SPEC / TOC 契约与边界。
- `../references/current.md` — Current 的同步语义与基线。
- `../references/issues.md` — issue 目录契约与条目格式。
- `../references/adr.md` — ADR 生命周期与索引。
- `../references/testing.md` — 测试规则（优先级高于 `tdd`）。
- `../references/bootstrap.md` 与 `../references/migration.md` — 无文档项目与旧版迁移。
- `../references/rendering.md` — 可选的 PRD 发布。

安装位置：`~/.agents/skills/project-docs-workflow/`；本文与 HTML 版都在其 `guide/` 下。
