# 领域术语

两层。默认方案；可在项目副本中覆盖。

## 1. 主术语表——`CONTEXT.md`

- 每个术语：`**术语**：定义`，后接 `_Avoid_: 同义词`。
- 出现聚类时按章节分组；单一内聚领域用扁平列表即可。
- 只收项目特定概念——零实现细节。

## 2. 领域术语表——例如 `docs/common/glossary.md`

- 编号索引表（每个术语一行）+ 逐术语章节 + 交叉链接。

## 使用规则

- 探索前先读 `CONTEXT.md` 及相关 ADR。
- 在每个产物中使用术语表词汇（issue 标题、重构提案、假设、测试名）。绝不漂移到 `_Avoid_` 同义词。
- 新概念是一个信号：重新思考你是在发明项目不使用的语言，还是记录这个缺口（交给 `domain-modeling`，未安装则按 `references/deps/domain-modeling.md` 执行）。
- 若这些文件缺失，静默继续；术语或决策定案时再创建，通常通过 `domain-modeling`（兜底 `references/deps/domain-modeling.md`）。
- 显式标注 ADR 冲突（`> _与 ADR-XXXX … 冲突，但…_`）；绝不静默覆盖。
