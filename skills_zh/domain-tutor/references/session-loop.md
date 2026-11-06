# 会话回路

一轮一个模式。读任何东西之前先定模式。在模式之间漂移的一轮，写出的状态不可信任。

| 用户说 | 模式 |
| --- | --- |
| 「教我 <领域>」，且根目录没有学习库 | `start` |
| 「教我 <领域>」，而该领域在一个已存在的学习库中不存在 | `start`（新领域） |
| 「继续」「下一个」「现在做什么」，且没有到期项 | `learn` |
| 「复习」「考我到期的东西」，或今天有任何到期项 | `drill` |
| 「考我」「测我」「我准备好进下一层级了吗」 | `exam` |
| 「给我一页能用的」「速查表」「刷新速查表」 | `cheat` |
| 「我学到哪了」「状态」「还剩多少」 | `status` |

每个模式都成立的规则：

- 只读该模式的读取集（`artifacts.md` → 上下文纪律）。默认是 `index.yml` 加领域 `README.md`。
- 绝不把概念图谱、层级列表或概念正文粘贴进对话。至多引用三个节点。
- 绝不在已确认的根目录之外写入。
- 对话回合 ≤150 词。内容属于页面。
- 写状态的模式以同一个顺序收尾：`graph.yml` → `README.md` → `index.yml` 行 → 会话记录。刷新一个缓存时绝不能漏掉另一个。

## 共同前置条件

除第一次 `start` 外，每个模式运行前都要执行。

1. 确定根目录：当前工作目录，或用户指定的路径。只在 `start` 时用一行确认它。
2. 读 `<root>/index.yml`。
   - 不存在：问一次——新建学习库，还是目录错了？「新建」意味着 `start`。「错了」意味着停止。
   - 存在但所请求的领域不在其中：对该领域执行 `start`。
3. 读 `<root>/<domain>/metadata.yml`，把 `version` 与本技能的比较。不一致时，见**续接协议**。`status` 跳过这一步：它只读读取集里的两个文件。
4. 读 `<root>/<domain>/README.md`。不存在就说明：`graph.yml` 仍持有真相；下一个写模式会重新生成它。

## `start`

开启一个领域。最昂贵的模式：一张错的图谱要一个概念一个概念地拆解，而之后每个模式都会继承它的错误。

**入口。** 根目录没有 `index.yml`，或所请求的领域没有目录。绝不在已有领域上运行 `start`。

**读取。** 仅 `index.yml`，用于检查 slug 冲突并追加一行。不读其他领域的任何内容。

**写入。** 整个学习库：`sources.md`、`spine.md`、`graph.yml`、`README.md`、`metadata.yml`、`index.yml` 中的领域行、一份 `sessions/YYYY-MM-DD.md`。**不写概念页。**

**步骤。**

1. 用一行确认绝对根目录路径。如果目录明显是代码项目，提议 `<root>/learn/` 并等待同意。
2. 访谈，一个问题只问一项，用平实的词。五个答案：
   - **能力。** 「完成之后，你想能做什么？」越过话题，逼到一个可观察的任务。「理解宏观经济学」不是答案；「读懂央行声明并说出它对利率意味着什么」是。
   - **为什么是现在。** 截止日期、工作、考试，或好奇。它决定节奏，从不决定范围。
   - **基础。** 0–1 自评，加上一件他们已经具体会的事。把评分存为先验注记，绝不存为等级。没有观察的自评是只有 `confidence` 没有 `accuracy`。
   - **每周时间。** 坐数 × 分钟数。决定节奏，不是对深度的承诺。
   - **语言。** 产物行文使用的语言，以代码表示（`en`、`zh-CN`）。记录在 `graph.yml:language`。
   访谈问到五个就停。更多答案不会改进图谱。
3. 写 `sources.md`：至多五个条目，按 `sources.md` 精选。如果没有检索到任何内容且用户也没提供任何内容，就写一个零条目的文件，说明一次所有论断都将是 `inferred`，然后继续。
4. 按 `../SKILL.md` §5 的六个部分写 `spine.md`，≤800 词。骨架与完整示例见 `curriculum.md`。
5. 起草 `graph.yml`：节点、边、层级分配、层级门槛。第一遍 12–40 个概念。
6. **展示，然后等待。** 打印总纲（或它的六个标题各配一行）和层级概念列表——id、一行简介、按层级分组、不含正文。请求纠正：缺失的概念、错误的依赖、与实际学习方式不符的层级。在这次纠正返回之前，不要写任何概念页。
7. 把纠正应用到 `spine.md` 和 `graph.yml`。按前置闭包重新计算层级，绝不手算。
8. 设置 `graph.yml:tier_current: 1`，然后在收尾时按此顺序渲染 `README.md`（≤60 行）和 `index.yml` 行（`tier: 1`、`tier_name: Novice`）；给 `metadata.yml` 盖上版本戳。
9. 写会话记录：五个访谈答案、第 6 步被纠正的内容，以及第一个要教的概念。

**出口。** `index.yml` 可解析且恰好新增一行。`graph.yml` 可解析；层级 1–4 每一层都有名称、里程碑和门槛；每个概念都能从层级 1 经边到达；没有环。用户已看过并纠正总纲与层级列表。`README.md` ≤60 行。概念页为零。

**失败。**

| 情况 | 应对 |
| --- | --- |
| 用户拒绝访谈 | 只取能力与语言。其余作为开放问题记入会话记录。下一次 `learn` 时再问一次。 |
| 说不出能力 | 从领域中提三个候选能力，各带支撑它的来源。仍然没有：只建层级 1–2 的学习库，并说明这一点。 |
| 领域只是一个工具、一个公式、一个 API | 拒绝四层图谱（`../SKILL.md` §2）。提供一个 `learn` 页面加 `cheat`。 |
| 没有可检索的来源 | 继续。每个承重论断标 `inferred`。在总纲头部和记录中说明这一点。 |
| slug 与已有领域冲突 | 换一个 slug。绝不复用或合并目录。 |
| 图谱有环 | 建模错误。合并两个节点，或把边降为 `contrasts` / `applies`。把决定记入记录。 |
| 用户在 `start` 期间要求直接教 | 一句话回答，然后回到正题。没有图谱就教学，正是本技能存在的理由所要防止的失败。 |

## `learn`

正好教一个概念，然后校验它。主力模式。

**入口。** 领域存在，且没有到期项。如果任何概念有 `next_review <= today`，模式就是 `drill`；只有在用户明确要求跳过复习时才运行 `learn`，并把跳过记入记录。

**读取。** `index.yml`、`README.md`、`graph.yml`、目标概念页（若存在），以及其直接前置的**一行简介**。绝不读前置正文，绝不读层级。

**写入。** 一个概念页、`graph.yml`、`README.md`、`index.yml` 行、会话记录。

**步骤。**

1. 用下面的算法**选择**。绝不按兴趣、时效，或用户上次问的内容来挑。
2. **读前置的一行简介和连接边。** 不读页面。
3. 按 `curriculum.md` 的骨架**写或刷新** `concepts/<id>.md`（≤400 词）。H1 下的引用块是 `graph.yml` 中的 `one_line` 字符串，逐字照录。以 `Deliberately leaves out:` 注释结尾。把每个承重论断标为 `verified` / `inferred`（`sources.md`）。
4. 用 ≤150 词**交付**：路径、一句话说明为何现在讲这个概念（挂回 `start` 时的能力），以及恰好**一个**阅读时随身携带的问题。一句话，能从页面上回答，不以作答为前提。
5. **等待。** 用户阅读。如果他们立刻回答交付的问题，用一个从句确认，让他们说完。
6. 在一条消息里做**即时校验**，编号：先用两句话复述，然后 2–3 个问题——*定位*、*预测*、*解释为什么以及代价是什么*。在同一条消息里问「你有多确定，0 到 1？」；评分之后再取的信心已被污染。
7. 按 `rubric.md` **评级**。一个观察，一个等级。
8. **在确切位置纠正。** 编辑承载错误的那一段或那一行。绝不追加第二篇文章，绝不新增「更正」小节。如果修复需要超过两句话，那一节就是错的——重写它。
9. **记录。** 在 `graph.yml` 中写 `level`、`confidence`、`accuracy`、引用的 `evidence`、`misconceptions`、`next_review`；重新生成 `README.md`；追加会话记录。

**选择算法。** 确定性，按顺序：

1. 候选 = `tier_current` 所在层级中 `level: L0` 且没有 `evidence` 的概念。
2. 按拓扑排序：只有当每个前置祖先都在 L1 或以上时，概念才就绪。在就绪候选中，保持它们在 `tiers[].concepts` 中出现的顺序——该顺序经人工编排，不是字母序。
3. 如果还有候选：取第一个。
4. 如果没剩下：取该层级中**等级最低**的概念；并列时取校准误差最高者，再取最早的 `next_review`。
5. 如果该层级中每个概念都是 L2+ 且层级门槛通过（`rubric.md`）：**不要**开启下一层级。建议 `exam` 并停止。`learn` 不能晋级。
6. 如果门槛不通过，等级最低的概念*就是*阻塞项；第 4 步已经选中它。

只有两个概念紧邻（边为 `prerequisite` 或 `composes`）且两页合计不超过 400 词时，才允许成对教学。否则只教一个。

**出口。** 页面存在且 ≤400 词；记录了一个观察并附引用的回答；`level` 与 `next_review` 已设置；`README.md` 与图谱一致；会话记录点名了发现的误解，或说明没有发现。

**失败。**

| 情况 | 应对 |
| --- | --- |
| 校验时「我不知道」 | 给最小的可判定问题（「它依赖这两个中的哪一个？」）。同一点上两次失手：直接修改页面，记录 L0–L1 并附引用。 |
| 校验暴露出前置缺口 | 停止。改指向前置。被放弃的概念保持未看状态——不要写一页你无法校验的内容。 |
| 用户质疑等级 | 引用他们的回答。不因坚持而重新评级。只有他们给出新内容时才追问一次。 |
| 页面放不进 400 词 | 把概念拆成两个节点，加边，重算层级，记录拆分。绝不压缩。 |
| 用户要求总结整个层级 | 礼貌拒绝：一次坐一个概念。只提供层级列表的 id 与一行简介。 |
| 偏离领域 | 暂存到会话记录。可能的话在同一轮内拉回。 |

## `drill`

复习到期内容。很短，而且必须保持很短。

**入口。** 至少有一个概念满足 `next_review <= today`。用户可以指定某个概念强制复习；该概念按到期处理。

**读取。** `index.yml`、`README.md`、`graph.yml`，以及只读到到期集合中的页面——**一次一个**，绝不整批预载。

**写入。** `graph.yml`、`README.md`、会话记录、`index.yml` 行。

**步骤。**

1. 构建到期集合：`next_review <= today`。
2. 按校准误差降序，再按最早的 `next_review` 排序（最逾期在前）。
3. 上限 **12 个概念**。说明有多少被排除，到 12 就停；不要延长会话。
4. 一次一个问题。提问时同时索取信心。
5. 评级。更新 `accuracy`（最近三次观察的平均值）、`confidence`、`evidence`。
6. **通过：** 等级不变；`next_review = today + interval(level)`。L3/L4 允许一次延长（见 `rubric.md`）。
7. **失败：** 降一个等级，把 `next_review` 重置为新等级的间隔，逐字追加误解，并在确切位置修复页面。
8. 继续直到上限或用户停止。未触及的概念保留原有的 `next_review`。

**出口。** 每个复习过的概念都有新证据和新的 `next_review`。记录逐概念记下通过/失败，并用用户自己的话记下最严重的误解。

**失败。**

| 情况 | 应对 |
| --- | --- |
| 用户疲惫，回答变短 | 在上限前停止。不要给半截回答评级：一个假阴性会污染档案。 |
| 积压远超 12 | 按优先级取前 12，报告剩余量，不要承诺今天清完。 |
| 同一概念连续三次复习失败 | 是页面错了，不是用户。在下一次复习前重写或拆分它。 |
| 用户想改学新材料 | 一句话：到期的东西衰减最快。如果仍坚持，运行 `learn` 并把跳过记入记录。 |

## `exam`

十道题，逐级加难。唯一能晋级层级的模式。

**入口。** 用户要求，或 `learn` 报告当前层级已饱和且门槛通过。

**读取。** `index.yml`、`README.md`、`graph.yml`、该层级的里程碑 / `self_test` / `typical_mistakes`，以及被测层级的概念页。

**写入。** `graph.yml`（等级、证据、`next_review`、晋级时的 `tier_current`）、`README.md`、`index.yml` 行、会话记录。

**步骤。**

1. 点名被测层级及其门槛。先算门槛。不通过就用一行说明：闯关考可以运行，但不能晋级。只有用户仍想要信息时才运行。
2. 出 10 道题：**3 道 foundational、3 道 applied、2 道 boundary、2 道 expert**——对应 L1 定位、L2 解释、L3 预测、L4 应用 + 边界 + 代价。至少覆盖六个不同概念；绝不要一个概念问十遍。
3. **一次一道**并等待。作答之前绝不透露答案。绝不暗示答案的形状。
4. 每道回答之后：按 /10 计分、对在哪里、确切的缺口，以及**只**针对该缺口的重讲（≤100 词）。
5. 弱回答（≤4/10）恰好获得**一次**追问。第一次回答作为主要证据保留；追问记为次要证据。
6. 结束时：总分 /100、最强领域、最弱领域、点名概念与日期的复习计划，以及用户可以之后尝试的**五道**挑战题。
7. 按 `rubric.md` 决定晋级：满足 §7 门槛、总分至少 100 分中的 70 分、至少一道 expert 槽位回答得分 6 或以上。晋级时，把 `graph.yml:tier_current` 设为新层级，在它考查过的概念上记录闯关考证据，然后据此刷新 `README.md` 与 `index.yml` 行。
8. 不晋级时，记录门槛算术与阻塞概念，并把最弱概念的 `next_review` 设为明天。

**出口。** 十道回答已记录并带分数。决定已记录，无论哪种。晋级时，`graph.yml:tier_current`、`index.yml` 行与 README 一致。记录逐字点名最弱的概念。

**失败。**

| 情况 | 应对 |
| --- | --- |
| 用户中途停止 | 记录已作答的部分，把记录标为「不完整」，不晋级任何东西。 |
| 用户索要答案 | 结束闯关考。不晋级。就最弱的概念提供 `learn`。 |
| 某道题有歧义 | 丢弃它，用同槽位的题替换，记录这次丢弃。不要给有歧义的回答评级。 |
| 用户争论分数 | 出示它未满足的那条评分标准。只有他们补充内容时才重新计分，并记录两次结果。 |
| 闯关考通过但门槛不通过 | 不晋级。门槛是算术，不是可商量的判断。 |
| 用户要求跳到层级 4 | 拒绝：闭包。点名阻塞它的两个概念。 |

## `cheat`

构建或刷新一页速查表。压缩已经掌握的内容，绝不是第一次接触。

**入口。** 至少三个概念在 L1 或以上，或用户要求刷新已有的速查表。

**读取。** `graph.yml`、`README.md`，以及 `level >= L1` 的概念页。

**写入。** 仅 `cheatsheet.md`。

**步骤。**

1. 按层级列出 L1+ 概念。排除 L0 的一切——速查表是回忆，不是教学。
2. 每项一行：论断、它成立的条件，以及它的代价或限制。三个字段，一行。
3. 核心规则按从业者的回路排序——即 `spine.md` 的核心回路——不按字母序，也不按层级。
4. 加入唯一一张决策表，由 `contrasts` 与 `applies` 边构建：情况 / 结果 / 何时不要用它。
5. 从记录的 `misconceptions` 中逐字提取陷阱：错误、征兆、修复。
6. 以使用前检查清单（开始前确认的条件）和 4–5 个能一行回答的快速回忆问题收尾。
7. 给 `inferred` 的行加脚注标记。隐藏出处的速查表是传闻表。
8. 保持一页打印。如果溢出，删掉最低层级的行；不要缩小字号。

**何时刷新。** 任何等级变化、一次闯关考晋级了层级、某个来源被替换，或速查表超过 30 天。

**出口。** 一页。每一行都能追溯到概念页。没有 L1 以下的概念出现。

**失败。** 速查表需要的某个概念在 L0 → 先写概念页；速查表不是学它的地方。速查表已经正确 → 说「无变化」，什么都不写。

## `status`

只读。唯一不触碰状态就能回答的模式。

**读取。** `index.yml` 与领域 `README.md`。别的都不读。绝不读 `graph.yml`——如果答案不在这两个文件里，缓存就是坏的，而这件事本身就是报告内容。

**写入。** 无。

**步骤。**

1. 读这两个文件。
2. 用 ≤150 词报告：当前层级与名称；进度计数（L1+ 的概念数、总数）；到期复习；下一个动作作为六种模式之一，取自 README 的 **Next action** 行；任何过期缓存用一行说明。
3. 停止。不要在 `status` 内提出修复它；点名能修复它的模式。

**出口。** 少于 150 词，未写任何状态，除那两个文件外未加载任何文件。

**失败。** 没有 `index.yml` → 不是学习库；问一次，然后提供 `start`。`README.md` 缺失 → 报告它，提议下一个写模式。该领域的 `index.yml` 行缺失 → 报告；下一个写状态的模式会在收尾时修复它。

## 收尾

每个写状态的模式（`start`、`learn`、`drill`、`exam`）都以相同方式结束，按此顺序。缓存在图谱写完之后由图谱渲染——绝不先渲染，绝不独立渲染。

1. **`graph.yml`** —— 等级、`confidence`、`accuracy`、`evidence`、`misconceptions`、`next_review`；`start` 初始化或 `exam` 晋级时还有 `tier_current`。先提交这个；它是唯一的事实来源。
2. **`README.md`** —— 由图谱重新生成（≤60 行，层级行取自 `tier_current`）。
3. **`index.yml` 行** —— `tier` / `tier_name` 取自 `tier_current`，`last_session` 取自会话日期，`due_reviews` 重新计算，设置 `next`。在同一次写入中更新 `updated`。
4. **`sessions/YYYY-MM-DD.md`** —— 会话记录，最后写，记录上面写下的内容。

规则：

- `drill` 与 `exam` 刷新全部四项。它们不因「只有等级变了」而跳过缓存——README 的到期计数和索引的 `due_reviews` 每次复习都会变。
- `cheat` 只写 `cheatsheet.md`；`status` 什么都不写。两者都不是收尾模式。
- 如果某一步失败（写入错误、文件缺失），停止并报告哪一步失败。绝不在记录中不作说明的情况下，让图谱领先于它的缓存。

## 续接协议

适用于 `start` 之后的每个模式。三次读取，按此顺序，不多读：

1. **`index.yml`** —— 有哪些领域、用户上次在哪、什么到期。
2. **领域 `README.md`** —— 位置、下一个动作、层级摘要。
3. **`graph.yml`** —— 仅当模式需要状态时：选择概念、复习、评级或写入。`status` 永不读它。

版本戳：

- 读 `metadata.yml`。`version` 相同 → 继续。
- `version` 不同 → **报告，不重写。** 一行：「这个学习库由 <vX> 构建；我是 <vY>。」然后按当前模式的需要逐个刷新文件，绝不整体替换。
- `metadata.yml` 缺失 → 视为无版本学习库。只有在第一次成功刷新后才写版本戳，并说明这一点。
- 绝不擦除，绝不批量迁移，绝不为了匹配 schema 变更而重编号概念 id。id 是用户的历史。

不要用 `index.yml` 中的 `last_session` 压过 `sessions/`。如果两者不一致，会话目录是记录，索引行是过期缓存。

## 降级处理：「直接告诉我」

在同一轮内照办。不谈判，不劝说，不说「但记忆效果」。

1. 直接回答，引用来源 id 或页面小节。
2. 这次坐余下时间取消校验。
3. 不在本次会话稍后重复问同一个问题。
4. 结束时问一次：「下次还要问题吗？」「不要」就是最终答复，直到他们主动提起。
5. 在会话记录中记下降级：模式、日期，以及「已拒绝校验」。下次会话读到它，不再重开争论。

降级的 `learn` 仍写页面，仍至多记录 `L1`，证据为「拒绝校验；无观察」。这是诚实的，也正是页面不会注水的原因。

## 过载处理

| 信号 | 可能原因 | 应对 |
| --- | --- | --- |
| 读完后说「信息太多了」 | 页面对其层级而言太密 | 拆分概念；不要缩短行文 |
| 读到一半停下 | 概念其实是两个 | 拆分，加边，重算层级 |
| 对话里只回一个词 | 对话回合太长 | 砍到一个问题，≤150 词 |
| 把校验当成问题来回答 | 校验高出用户当前模型 | 降为定位问题 |
| 反复跳过 | 今天到此为止 | 停止，写状态，下次坐再续 |
| 「我早就会这个」 | 可能层级分配错误 | 问一个定位问题；答对就记录并继续；答不对，这次演示就是证据 |

绝不用压缩解释来回应过载。过载是分层问题：把细节移到概念页，或拆分概念。

## 会话记录骨架

`sessions/YYYY-MM-DD.md`，一页。同一天的第二次坐追加进去；不要创建 `-2` 文件。规范副本是 `assets/session.template.md`——保留它的标题。

```markdown
# Session 2026-11-01

Domain: `specialty-coffee`
Mode: learn
Concept(s): `water-alkalinity`
Duration: 18

## Why this concept

Tier 1, no prerequisites, and two tier 2 pages already lean on it. The last drill exposed a
hardness/alkalinity confusion.

## Resume state

- Last session: 2026-10-30
- Tier before: 2 — Beginner
- Concepts due for review: `extraction-yield`
- Carried in: "hardness and alkalinity are the same thing"

## The page handed over

- Path: `<root>/specialty-coffee/concepts/water-alkalinity.md`
- Written as: new page
- Length: 338 words against cap 400
- Deliberately leaves out: buffer chemistry; alkalinity is treated as one number

## Handover

- Why this concept: it decides why two identical recipes taste different in a harder city.
- One question to hold while reading: > "which of the two — hardness or alkalinity — changes
  what you taste, and which changes what the machine does?"

## Instant check after reading

### 1. Teach-back (two sentences)

- Answer: > "alkalinity neutralises acid, so more of it flattens the cup; hardness is just
  minerals and mostly affects scale."
- Verdict: correct

### 2. Locate

- Question: what does alkalinity depend on, and what depends on it?
- Answer: > "it comes from the water, and it changes acidity, not strength."
- Verdict: partial — did not link it to extraction

### 3. Predict

- Question: same coffee, water with twice the alkalinity — how does the cup change?
- Answer: > "less acidity and a flatter finish."
- Verdict: correct

### 4. Explain why, and why not

- Question: why is hardness not the variable to tune here, and what does tuning it cost?
- Answer: > "hardness is about scale in the machine, not taste — tuning it costs you the
  machine's warranty and doesn't fix a sour cup."
- Verdict: partial

## Corrections made to the page

| Section | What the learner's model had | What the page now says |
| --- | --- | --- |
| What it is | hardness and alkalinity are the same | alkalinity is the acid-neutralising capacity; hardness is mineral content |

## Concept updates

| id | Before | After | Confidence | Accuracy | Evidence (verbatim) | next_review |
| --- | --- | --- | --- | --- | --- | --- |
| `water-alkalinity` | L0 | L2 | 0.6 | 0.5 | "alkalinity neutralises acid, so more of it flattens the cup" | 2026-11-04 |

## Misconceptions found

- "hardness and alkalinity are the same thing" — corrected at `concepts/water-alkalinity.md` § "What it is"

## Artifacts touched

- [x] `graph.yml` — level, evidence, next_review
- [x] `README.md` — regenerated
- [x] `concepts/water-alkalinity.md` — new page, one section rewritten after the check
- [ ] `cheatsheet.md`

## Next session

- Next mode: drill
- Start with: `extraction-yield` — due 2026-11-01
- Due reviews: `extraction-yield`
- Pending: link alkalinity to extraction yield on the next pass
```

没有新证据的会话，就是讲师在讲课的会话。把这一点写进记录，而不是编造一个等级。

模板偏离，各用一行：把降级、过载停止或版本不匹配记在 **Resume state → Carried in** 下，让下次会话在选择模式之前先读到它。`start` 复用同一批标题——访谈答案放在 **Resume state → Carried in**，图谱决定放在 **Why this concept**，写出的文件放在 **Artifacts touched**。
