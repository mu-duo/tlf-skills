# 开发流程

默认方案。项目可在物化的 `docs/agents/workflow.md` 中覆盖；该副本决定运行时行为。

开发单条 issue 的默认形态：对齐、搭最小切片、填充细节、加固、同步文档。流程是推荐——项目可覆盖任一步骤——但只要在使用，唯一的硬规则是：实现之前先对齐与规划。

## 角色与写入权限

- **用户**——拥有意图、范围与批准；评审 PRD、SPEC 与 ADR。
- **编排者（orchestrator）**——维护 PRD；与用户共同编写 SPEC；评审 PRD / SPEC diff；拥有 `docs/toc.yml`；触发发布；把编码工作交给 coder。
- **编码 agent（coder）**——读 SPEC 实现；收尾时更新 Current 事实；可通过 issue 提议 SPEC 变更；**不**直接编辑 PRD、SPEC 或 TOC。
- **单 agent 模式**——一个 agent 可同时担任编排者 + coder；角色边界仍然适用，同一 agent 要显式换帽子。

## 工作单元与粒度

- 工作单元是 **issue**（见 `issues.md`）：一个 feature 级可交付物。Bug / chore 同构，简化处理。
- **粒度是建议**，从不强制：切到可单次 review 的推进单元（启发式 ≈ 0.5 人天），按任务弹性调整。
- **阶段切分由 agent 自行感知**——下一片做哪部分，绝不落成目录或文件；唯一物化的跟踪是 issue 自己的 `## 步骤` 清单。可在 issue 内加一句说明当前阶段。

## 读什么

- **意图与场景**：PRD——产品 `docs/product/00-README.md`、`01-requirements.md`、`02-architecture.md`，再读模块 PRD（`docs/product/<NN-module>/00-README.md`）。用于理解范围与目标，绝不是实现事实源。
- **实现事实**：SPEC 文件（`01-spec` / `02-interfaces` / `03-nfr` / `design/`）。
- **现状**：Current（`docs/current/`），看当前实际能做什么。
- **发布**：`docs/toc.yml` 决定发布文档集合。
- **冲突**：实现细节 → SPEC 为准；范围 / 意图 → PRD 为准；仍不清楚则升级给编排者 / 用户。

## 对齐

- **先对齐再实现**：只有对齐完成、计划 / 步骤写好后，才开始实现（对齐 → 计划与步骤 → 实现）。
- 编排者 + 用户编写或对齐 SPEC；coder 按 SPEC 实现。范围或意图变化时，先更新 PRD。
- 对齐是**对话式、软的**：不冻结，不设仪式化的「已对齐」记录。需求变化时主动重新对齐（功能需求漂移）。
- 方向有歧义时，调用 `grilling`（未安装则按 `references/deps/grilling.md` 执行）；`grill-me` 仅入口别名；`grill-with-docs` = `grilling` + `domain-modeling`（兜底 `references/deps/grilling.md` + `references/deps/domain-modeling.md`）。
- **差距分析**在此处（规划）完成：读 SPEC 目标与 Current 现状，推导**候选**任务（模块 / FR、建议类型、切片、验收判据），由用户挑选。差异只是候选——可能是漂移、质量缺口、未验证行为或目标过时，不一定是缺失功能；不要凭空造差距。不空闲自动创建 issue。
- **范围内自主**：对齐后，agent 在约定范围内自主实现，遵守 ADR、契约与安全；高成本、破坏性或难以回退的决策先与用户确认。

## 变更协议

- **PRD 变更**（范围 / 意图 / 目标用户 / 典型场景 / 非目标）：与用户对齐，对齐后更新 PRD；需求变化时更新 SPEC；人类评审 PRD diff。绝不让 coder 直接改写 PRD。
- **SPEC 变更**（实现细节、FR 语义、接口、NFR）：用户 + 编排者共同编写；coder 可通过 issue 提议；人类 / 编排者在实现前评审。
- **Current 变更**：coder 在收尾时按选定基线更新事实；编排者评审。
- **ADR**：记录带理由与取舍的决策；ADR 是平级文档，不是本协议中的一步。
- **冲突**：实现细节以 SPEC 为准，范围以 PRD 为准；二者无法调和时升级。
- 原型 / spike 在方向确认前豁免。
- 已实现的细节不会自动提升进 PRD 或 SPEC。

## PRD 影响触发

收尾时（以及规划范围变更时）逐项检查这四项。不设逐 FR 元数据，也不新增跟踪产物。

1. PRD 引用到的需求发生语义变化 → review / 更新 PRD。
2. 新增或变更的 FR 改变用户可见行为 → 新增 / 更新 PRD。
3. 纯内部改动 → PRD no-op，记一行 Log。
4. 目标用户 / 典型场景 / 范围 / 非目标变化 → 更新 PRD。

## 范围收敛

- **默认偏好：收敛功能空间。** 「功能空间」是用户面向的别名，指 PRD 约束下的状态 / 解空间；不要引入第二个概念。
- **触发条件 = 改变功能 / 范围目标的决策**，发生在 PRD / ADR 层（定义目标的地方）或 issue 规划层。
- 未被现有 PRD 覆盖的功能候选属于**扩张**：提出前先用一句话说明理由。实现现有 PRD 的候选属于收敛 / 实现，无需额外论证。
- 恢复或维持既有行为的 bug 修复与 chore 豁免。若 bug / chore 实际改变了功能集合，重新归类为 feature。
- 这是偏好，不是门禁：不新增产物、不阻断。项目可覆盖。
- **记录策略**：默认不记录被拒备选——见 `adr.md`（否定决策）与 `issues.md`（`-drop` 归档）。该策略只约束持久记录；对齐 / grilling 仍可探索备选。

## 五步流程

1. **规划 / Plan**——编排者 + 用户确认范围并对齐 SPEC；coder 细化验收判据、更新步骤清单状态，并写 1–2 句方案。产出最小；不新开章节。差距分析在此完成，读 SPEC 目标与 Current；PRD 只作人类理解参考。
2. **骨架 / Skeleton**——最小可运行的垂直切片（忽略输出 / 格式打磨）；留一条运行证据并展示给用户——首个 review 点。纯修复可跳过（Log 原因）；feature 与结构性工作必做。
3. **细节 / Details**——主路径实现、细节补全、代码质量。`tdd`（未安装则按 `references/deps/tdd.md` 执行）是可选的内部循环。
4. **异常 / Exceptions**——主路径之后的失败路径、边界与稳定性。真实开发阻塞立即处理并记 Log，绝不排队到这一步。
5. **回顾 / Wrap-up review**（收尾回顾）——issue 完成时的轻量文档同步清单：coder 更新 Current 事实并提议 SPEC 变更；编排者评审 PRD / SPEC / Current，模块或附录变化时更新 TOC；`adr` / `context` / `issues` / `agents` 按需更新。无需更新则一行 Log。仅做文档同步；会话 / agent 复盘属于 `retro`（未安装则按 `references/deps/boundaries.md` 执行）。

## 进度与续接

- issue 条目带 `## 步骤` 清单（五步）；**就地**更新。Log 只记关键事件（范围变化、阻塞、交接、放弃），不记每次步骤变化。
- **session 是软的。** session 是用户的注意力窗口；用户掌握节奏（可在 issue 之间 new / compact）。agent 不得吞并超出对齐范围的工作。
- **恢复时**，先读 issue 的步骤与 Log，再与用户确认续接点。

## 文档同步钩子

- **规划**：差距 → issue 候选落到 `docs/issues`；条目的关联记录模块 / FR。
- **收尾回顾**：
  - **PRD 检查**（四项影响触发）：被引用的需求语义变化，或用户可见行为变化，或目标 / 范围移动 → 打补丁更新 PRD 并展示 diff；否则记一行说明 PRD 无变化。编排者评审 PRD diff。
  - **SPEC 检查**：coder 通过 issue 提议必要的 SPEC 变更；用户 + 编排者编写并确认。coder 绝不直接编辑 SPEC。
  - **Current 检查**：确认完成的变更已包含在选定基线内。是 → **就地**更新受影响的 Current 文档——**只改事实，绝不插入指向 issue 的自链接或任务历史**；否 → 保持原样，在 issue 记一条待同步项。基线前移会刷新相关 Current 文档；实际状态未变 → 不改。
  - 变更需要时触碰 `adr` / `context` / `issues` / `agents`。
- **归档**：完成 / 放弃后按 `issues.md` 归档 issue。

## TOC 维护与发布

- `docs/toc.yml` 是发布来源。模块或附录变化时，编排者 / agent 更新；用户可直接编辑。所有路径必须存在，并落在允许的根内（`docs/product`、`docs/current`、`docs/adr` 或根 `CONTEXT.md`；见 `prd.md`）。
- 发布是**手动、流程之外**的：PRD / SPEC / Current 变更后，用户可触发 `docs-html-view` 构建多页 PRD。文档编辑不自动构建，init 也不创建任何渲染器产物（`rendering.md`）。

## 边界

- 大规模或高风险多阶段工作 → `deepwork`（未安装则按 `references/deps/boundaries.md` 执行）；绝不与本流程叠加。
- `tdd`（未安装则按 `references/deps/tdd.md` 执行）嵌在细节内；seam 确认并入规划对齐（不设第二道门）。
- `retro`（未安装则按 `references/deps/boundaries.md` 执行）拥有会话 / agent 复盘；第五步只做文档同步。
- 没有产品文档的现有项目 → 需用户同意的 bootstrap（`bootstrap.md`）。v4 / 旧版文档 → 迁移（`migration.md`）。二者都不会在本流程中自动运行。
- 文档 HTML 发布是可选手动能力（`rendering.md`）；绝不在本流程中运行——文档编辑不自动构建。本方案与这些 skill 的共存见 `coexistence.md`。
