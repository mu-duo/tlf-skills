# 产物

状态只存在于文件中，且只存在于文件中。一次没有写入就结束的对话等于没有发生。

## 目录树

```
<root>/
├── index.yml
└── <domain>/
    ├── README.md
    ├── graph.yml
    ├── spine.md
    ├── sources.md
    ├── cheatsheet.md
    ├── metadata.yml
    ├── concepts/
    │   ├── brew-ratio.md
    │   └── extraction-yield.md
    └── sessions/
        └── 2026-11-01.md
```

没有其他文件。根目录里没有缓存目录、没有备份副本、没有 `notes/`、没有 `drafts/`、没有资产目录。概念 id 与领域 slug 为 ASCII kebab-case，永不改变。日期为 ISO `YYYY-MM-DD`，以用户会话所在地为本地时区。

## `index.yml`

每个根目录一个。跨领域索引与续接点。上限：每个领域一行。

```yaml
version: 1
root: /home/tan/learn
owner: tan
updated: 2026-11-01
domains:
  - slug: specialty-coffee
    display_name: Specialty Coffee Brewing
    tier: 2                      # 由 graph.yml:tier_current 渲染
    tier_name: Beginner          # 由 graph.yml:tier_current 渲染
    last_session: 2026-11-01
    due_reviews: 1
    next: extraction-yield
```

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `version` | int | 本文件的格式版本，当前为 `1`。不是技能版本。 |
| `root` | string | 绝对路径。必须等于本文件所在目录。在 `start` 时写一次。 |
| `owner` | string | 用户给出的名字或代号。不写邮箱地址。 |
| `updated` | date | 本文件最后一次写入的日期。 |
| `domains[]` | list | 每个领域目录一项。 |
| `domains[].slug` | string | 不可变，ASCII kebab-case，等于目录名。 |
| `domains[].display_name` | string | 人类可读名称，使用 `graph.yml:language` 指定的语言。 |
| `domains[].tier` | int 1–4 | **由 `graph.yml:tier_current` 渲染。** 在 `start` 时写为 `1`；只在 `exam` 晋级时改变。绝不在此处编辑。 |
| `domains[].tier_name` | string | **由 `graph.yml:tier_current` 渲染**：`Novice`（1）、`Beginner`（2）、`Practitioner`（3）、`Adept`（4）。必须与 `tier` 一致。 |
| `domains[].last_session` | date \| null | `sessions/` 中最新的文件日期，不是此处最后一次编辑的日期。从未学习过则为 `null`。 |
| `domains[].due_reviews` | int | `next_review <= today` 的概念数量。由 `graph.yml` 派生。 |
| `domains[].next` | string \| null | 下一个要教或复习的概念 id；没有待办时为 `null`。模式不存在这里；由 `README.md` 点名。 |

不变量：`slug` 唯一；每个 `slug` 都有对应目录；`tier` 等于 `graph.yml:tier_current` 且 `tier_name` 与 `tier` 匹配；`root` 与现实一致。该行是**缓存**——在收尾时由 `graph.yml` 和 `sessions/` 派生，绝不手工编辑，绝不是记录等级或层级的地方。

## `metadata.yml`

用于幂等续接的版本戳。上限：4 行。

```yaml
skill: domain-tutor
version: 1
updated: 2026-11-01
```

| 字段 | 规则 |
| --- | --- |
| `skill` | 字面量 `domain-tutor`。标识构建者。 |
| `version` | 技能发布戳，当前为 `1`。每次续接时比较。仅在 schema 级刷新时递增。 |
| `updated` | 最后一次 schema 级刷新的日期——新字段、改动的上限。不是每次会话。 |

## `graph.yml`

状态的唯一事实来源：概念状态与用户当前层级。机器可读；一行简介之外不含散文。

```yaml
version: 1
domain: specialty-coffee
display_name: Specialty Coffee Brewing
language: en
updated: 2026-11-01
tier_current: 2

tiers:
  - id: 1
    name: Novice
    display_name: Novice
    milestone: "Names the variables in a brew and what each changes."
    typical_mistakes:
      - "Treats strength and extraction as the same thing."
    self_test: "Which variable do you change first when the cup is sour, and why?"
    gate:
      min_level: L2
      max_calibration_error: 0.3
    concepts:
      - brew-ratio
      - water-alkalinity
  - id: 2
    name: Beginner
    display_name: Beginner
    milestone: "Reproduces a target cup from a written recipe."
    typical_mistakes:
      - "Changes two variables at once."
    self_test: "Given this recipe and this result, what is the next single change?"
    gate:
      min_level: L2
      max_calibration_error: 0.3
    concepts:
      - extraction-yield
  - id: 3
    name: Practitioner
    display_name: Practitioner
    milestone: "Chooses a method for an unfamiliar bean and justifies the choice."
    typical_mistakes:
      - "Applies an espresso model to a filter brew."
    self_test: "Which method would you pick here, and what does it cost?"
    gate:
      min_level: L2
      max_calibration_error: 0.3
    concepts: []
  - id: 4
    name: Adept
    display_name: Adept
    milestone: "Diagnoses an edge case and states where the model stops applying."
    typical_mistakes:
      - "Optimises one variable past the point where the cup is still wanted."
    self_test: "Name the condition under which this method is the wrong tool."
    gate:
      min_level: L2
      max_calibration_error: 0.3
    concepts: []

edges:
  - from: brew-ratio
    to: extraction-yield
    type: prerequisite
  - from: water-alkalinity
    to: extraction-yield
    type: prerequisite

concepts:
  - id: brew-ratio
    canonical: brew ratio
    aliases: ["dose-to-water ratio", "ratio"]
    one_line: "Fixes how much water meets the dose, so it bounds strength before extraction does."
    tier: 1
    level: L2
    confidence: 0.6
    accuracy: 0.5
    evidence:
      - "2026-10-30: \"the cup gets weaker but extraction can still rise\" — case: same dose, twice the water — gap: could not say why strength and extraction move differently"
    misconceptions: []
    next_review: 2026-11-02
    sources: [s1]
    verified: verified
  - id: water-alkalinity
    canonical: water alkalinity
    aliases: ["buffer capacity"]
    one_line: "Sets how much acid the water neutralises, so it changes what the cup tastes like."
    tier: 1
    level: L2
    confidence: 0.5
    accuracy: 0.5
    evidence:
      - "2026-11-01: \"the acidity drops\" — case: same coffee, harder water — gap: named hardness, not alkalinity"
    misconceptions:
      - "hardness and alkalinity are the same thing"
    next_review: 2026-11-04
    sources: [s2]
    verified: verified
  - id: extraction-yield
    canonical: extraction yield
    aliases: ["extraction"]
    one_line: "Sets how much of the dose reaches the cup, so it fixes strength for a given ratio."
    tier: 2
    level: L3
    confidence: 0.8
    accuracy: 0.5
    evidence:
      - "2026-10-25: \"yield fell because water passes through faster\" — case: same recipe, finer grind, cup tastes sour — gap: grind also widens the particle spread"
    misconceptions:
      - "finer grind always raises extraction"
    next_review: 2026-11-01
    sources: [s1, s2]
    verified: verified
```

### 顶层

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `version` | int | 格式版本，当前为 `1`。 |
| `domain` | string | 等于目录 slug。 |
| `display_name` | string | 使用 `language` 指定的语言。与 `index.yml` 行一致。 |
| `updated` | date | 本文件最后一次写入的日期。 |
| `tier_current` | int 1–4 | 用户已被**晋级进入**的层级。在 `start` 时写为 `1`；只由一次晋级的 `exam` 递增。不由概念等级计算——门槛在闯关考时检查，不是持续检查。`index.yml` 的 `tier` / `tier_name` 与 README 的层级行由此字段渲染。 |
| `language` | string | 所有产物行文使用的语言代码（`en`、`zh-CN`）。见语言策略。 |
| `tiers[]` | list | 恰好四项，id 为 `1`–`4`。 |
| `edges[]` | list | 只有在单节点领域时才可为空，而单节点领域不应存在。 |
| `concepts[]` | list | 每个概念一条记录，id 与 `tiers[].concepts` 中的相同。 |

### `tiers[]`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | int 1–4 | 固定。 |
| `name` | string | 英文枚举，固定：`Novice`、`Beginner`、`Practitioner`、`Adept`。永不翻译。 |
| `display_name` | string | 该层级在用户语言中的标签。可以等于 `name`。 |
| `milestone` | string | 一句话，可观察：用户在该层级出口能做什么。不要写「理解」。 |
| `typical_mistakes` | list[str] | 每层 1–3 条。用于构造干扰项与闯关考追问。 |
| `self_test` | string | 用户用来自判该层级的一个问题。 |
| `gate.min_level` | string | `L2`。除非课程改变，否则固定；绝不为了通过而调低。 |
| `gate.max_calibration_error` | float | `0.3`。固定。 |
| `concepts` | list[str] | 该层级中有序的 id。此顺序经人工编排，是选择时的并列裁决依据（`session-loop.md`）。每个 id 在四个层级中恰好出现一次。 |

### `edges[]`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `from` | string | 概念 id。存在于 `concepts[]` 中。 |
| `to` | string | 概念 id，不同于 `from`。 |
| `type` | string | `prerequisite`、`composes`、`contrasts`、`applies` 之一。 |

没有其他边类型，没有属性，没有散文字段。`contrasts` 只存一次；`prerequisite` 子图无环。语义见 `curriculum.md`。

### `concepts[]`

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `id` | string | ASCII kebab-case，不可变，等于 `concepts/<id>.md`。 |
| `canonical` | string | 概念在 `language` 指定语言中的名称。 |
| `aliases` | list[str] | 英文术语与已知同义词。当 `language != en` 时必须包含英文术语。 |
| `one_line` | string | ≤15 词，一个关系，不含「和」。与页面 H1 下的引用块逐字节相同。 |
| `tier` | int 1–4 | 由前置闭包计算，绝不手工分配（`curriculum.md`）。 |
| `level` | string | `L0`–`L4`。只由记录在案的观察设定。 |
| `confidence` | float 0–1 | 用户的自评，在评分**之前**取得。 |
| `accuracy` | float 0–1 \| null | 最近三次观察的平均值。第一次观察前为 `null`。 |
| `evidence` | list[str] | 每条：`"YYYY-MM-DD: \"<verbatim>\" — case: <the case> — gap: <the exact gap>"`。带日期、有引用、具体。`level != L0` 时绝不为空，绝不是判定（「已掌握」）。 |
| `misconceptions` | list[str] | 逐字记录，用用户的话。只有在重测通过后才清除。 |
| `next_review` | date \| null | 来自 `rubric.md`。概念有证据之前为 `null`；有证据却仍为 `null` 时，视为现在到期。 |
| `sources` | list[str] | 来自 `sources.md` 的 `s1`…`s5`；页面依赖五个来源之外的内容时，写一条简短引用。仅当页面完全为 `inferred` 时才可为空。 |
| `verified` | string | `verified` 或 `inferred`。当且仅当页面上每个承重论断都有章节/小节/URL 级别的已检索来源时为 `verified`；任一不满足，或来源冲突时为 `inferred`。 |

校准误差**不存储**。它是 `confidence - accuracy`，按需计算。存储它会招来两个互相矛盾的数字。

## `README.md`

唯一的入口。是缓存，不是事实来源。上限：60 行。

```markdown
# Specialty Coffee Brewing

A field of extraction and water chemistry: it answers how to make a cup repeatable rather than
lucky, for a home brewer or a barista. You are at Beginner, working on tier 2, with 3 concepts
recorded.

## Current tier

Tier 2 — Beginner: reproduces a target cup from a written recipe.
Concepts at L2+: 3/3 · calibration error <= 0.3: yes · due reviews: 1.

## Progress

Strongest:
- `extraction-yield` (L3) — predicted the direction of a grind change on an unseen bean
- `brew-ratio` (L2) — separates strength from extraction in the abstract

Weakest:
- `water-alkalinity` (L2) — confuses hardness with alkalinity
- `extraction-yield` (L3) — did not account for the particle spread

## Next action

`extraction-yield` — review due today; drill before opening the tier 3 concepts.
Due reviews first: 1.

## Pointers

- Spine: [spine.md](spine.md) — the whole field, one page
- Graph: [graph.yml](graph.yml) — source of truth
- Cheat sheet: [cheatsheet.md](cheatsheet.md) — five minutes before use
- Sources: [sources.md](sources.md) — the five that matter
- Concept pages: [concepts/](concepts/)
- Sessions: [sessions/](sessions/)

## What this page deliberately leaves out

Concept bodies, edge detail, evidence quotes, review intervals, and source notes. They live in
`graph.yml` and `concepts/`; this page is a cache for orientation only.
```

规则：

- 一切都由 `graph.yml` 渲染，包括层级行（`tier_current`）和指针。`index.yml` 行是同一张图谱的缓存。
- 每一行都可从状态推导。没有新论断，没有教学，没有建议。
- **冲突规则：** README 与 `graph.yml` 不一致时，图谱胜出，README 重新生成。`tier_current` 与门槛算术不一致时，两者都打印出来，并把层级行标为 `stale`；绝不为协调二者而调高或调低层级。
- 在每个写状态模式的收尾时重新生成（`start`、`learn`、`drill`、`exam`），顺序为图谱 → README → 索引行 → 会话记录。`cheat` 与 `status` 不写它。
- 绝不为了修正一个事实而编辑它。修图谱，然后重新生成。

## `spine.md`

用途：整个领域，粗略版，一页。上限：800 词。骨架、完整示例与省略：`curriculum.md`。

```markdown
# <display_name>

> **If you read only one paragraph:** the field, whose problem it solves, the six parts in
> miniature, and the one assumption that explains most of its shape.

Source basis: [s1] ch. 1–2, [s2] ch. 1 (verified); remainder inferred.

## 1. One sentence
## 2. Boundaries
## 3. Core loop
## 4. Nouns
## 5. Seams
## 6. Deliberate omissions

**What this spine flattens:** <one line naming the simplification and what a reader would wrongly believe without it>.
```

第 2–6 部分各用一张表，如 `assets/spine.template.md` 所示：边界（内部 / 相邻 / 假定）、名词（实体 / 它是什么 / 关联到 / 来源）、接缝（接缝 / 什么穿过 / 两侧各自承诺什么）、省略（忽略什么 / 为何 / 什么显得奇怪）。核心回路为 5–7 个编号步骤，每步标注 `verified` / `inferred`。

在 `start` 时写一次；仅在概念图谱证明它错了时修订。绝不长出定义小节。

## `sources.md`

用途：五个锚点及各自用途。上限：**5 个条目**。条目格式、选择标准、冲突处理：`sources.md`（参考文件）。

## `concepts/<id>.md`

用途：一个概念，完整呈现。上限：整页 **400 词**——包含完整示例。

```markdown
# Extraction yield

> Sets how much of the dose reaches the cup, so it fixes strength for a given ratio.

## What it is
<2–4 sentences: the object or claim itself, terms defined on first use.>

## Why it sits here

- Prerequisites: `brew-ratio` — <what must be in place, and why>
- Dependents: `grind-distribution` — <what cannot be understood until this is>
- Tier: 2 (Beginner) — <the milestone this serves>

## Mechanism / rules

1. <rule> (verified)
2. <rule> (inferred)
3. <rule> (inferred)

**When it holds:** <conditions; the failure past them; what using it costs>. (verified)

## Worked example
<One concrete case, steps and outcome. Not a derivation.>

## Common misconceptions
- <the belief> — <what is wrong, and the one-sentence correction>

## Self-test
> <One question not answerable by recalling the page's wording.>

## Sources
- `s1` ch. 4 — <which claim> (verified)
- <analogy or synthesis> — <which claim> (inferred)

<!-- Deliberately leaves out: <the simplification contract>. -->
```

`assets/concept.template.md` 中的骨架是规范版本；保留它的标题。模板的 **Why it sits here** 区块是强制执行关系的地方：前置与后继必须与 `graph.yml` 的边一致；前置还没有页面时，「尚未写就」是诚实的条目。

## `cheatsheet.md`

用途：使用前五分钟的压缩回忆。上限：一页打印（约 45 行）。骨架：`curriculum.md`。排除 L1 以下的每个概念。

## `sessions/YYYY-MM-DD.md`

用途：发生了什么、哪里做错了、从哪里续接。上限：一页。允许把同一天的第二次坐追加进去；不允许创建 `YYYY-MM-DD-2.md`。

骨架：`session-loop.md` → 会话记录骨架。必需内容：模式、目标、带引用的证据、等级变化、误解、下一个动作、标记。一份没有引用回答的会话记录，是关于 agent 的记录，不是关于用户的。

## 版本戳与幂等续接

- 版本戳在 `start` 时写一次，仅在 schema 级刷新时更新。
- 续接时：读取 `metadata.yml`，把 `version` 与本技能的比较。
  - **相同** —— 正常运作。
  - **学习库更旧** —— 用一行报告，然后按当前模式的需要**逐个文件**刷新。绝不批量迁移，绝不重写 id，绝不删除新 schema 不使用的字段。替换承载用户内容的文件之前，先展示差异。
  - **学习库更新** —— 不要降级 schema。报告不匹配，并针对现有字段运作。
  - **缺失** —— 视为无版本。在第一次成功刷新后写入版本戳，并说明这一点。
- 幂等性，按模式：
  - 对同一 slug 跑两次 `start`：拒绝。行和目录已存在；这是 `learn`。
  - 对一个概念跑两次 `learn`：第二次就地刷新页面。它不创建第二个文件，也不产生重复的概念记录。
  - 一天内跑两次 `drill`：第二次发现没有到期项并说明；它不会把复习强行提前。
  - 跑两次 `cheat`：第二次要么报告「无变化」，要么用相同内容重写同一文件。
  - 跑两次 `exam`：会话记录中有两条独立的闯关考记录；不保留最高分的决定——以最新记录的决定为准，一次晋级不会因之后的失败而撤销。

## README 缓存规则

`README.md` 在收尾时**由**状态渲染。它绝不是事实首次被记录的地方，也从不是「这是真的吗？」的答案。

| 问题 | 答案来源 |
| --- | --- |
| 概念 X 是什么等级？ | `graph.yml` |
| 什么到期了？ | `graph.yml`（`next_review`） |
| 我在哪个层级？ | `graph.yml`（`tier_current`），并对照门槛算术检查 |
| 我接下来该做什么？ | 选择算法，然后是据此渲染出的 README 行 |

冲突 → 图谱胜出；一起重新生成 README 与 `index.yml` 行。如果 README 被手工编辑过，在覆盖之前于会话记录中说明。绝不把纠正只留在 README 中，或只留在索引行中。

## 上下文纪律

| 模式 | 可读 | 不可读 |
| --- | --- | --- |
| `start` | 已有的 `index.yml`（冲突检查）、用户提供的来源 | 其他领域的文件、任何概念页 |
| `learn` | `index.yml`、领域 `README.md`、`graph.yml`、目标页、直接前置的**一行简介** | 其他层级的页面正文、`sessions/`、其他领域 |
| `drill` | `index.yml`、`README.md`、`graph.yml`、到期集合中的页面——一次一个 | 到期集合之外的页面、`sessions/`、其他领域 |
| `exam` | `index.yml`、`README.md`、`graph.yml`、层级元数据、被测层级的页面 | 其他层级的页面正文、其他领域 |
| `cheat` | `graph.yml`、`README.md`、L1+ 的页面 | `sessions/`（误解已在概念上）、其他领域 |
| `status` | `index.yml`、领域 `README.md` | `graph.yml`、概念页、`sessions/`、其他领域 |

绝不 `ls -R`，绝不 glob `concepts/*.md`，绝不为回答一个问题而加载整个层级。如果模式似乎需要更多，是产物太大了：拆分概念。

## 语言策略

- `graph.yml:language` 记录产物行文使用的语言。`spine.md`、概念页、`cheatsheet.md`、`README.md` 与会话记录全部用它书写。
- **文件名、目录名、id 与 slug 为 ASCII kebab-case**，由英文派生。它们不随行文语言变化而改变。
- YAML 键保持英文；schema 不翻译。
- `tiers[].name` 保持固定的英文枚举（`Novice`、`Beginner`、`Practitioner`、`Adept`）；`tiers[].display_name` 承载用户语言的标签。等级保持 `L0`–`L4`。
- 当 `language != en` 时，`concepts[].aliases` 必须包含英文术语，以便之后的 agent 匹配该概念。
- `evidence` 与 `misconceptions` 中的引用按当时所说的语言逐字记录。翻译只能与原文并列，绝不替代原文。
- 来源标题保持原语言；`sources.md` 若使用了译本，注明翻译。
- 学习库中途更换语言是允许的，且不触发重写：新页面用新语言，既有 id 与文件保留，会话记录记下这次切换。
