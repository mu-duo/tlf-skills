# Domain terminology

Two layers. Default profile; overridable in project copies.

## 1. Primary glossary — `CONTEXT.md`

- Per term: `**Term**：definition` followed by `_Avoid_: synonyms`.
- Group terms under sections when clusters emerge; a flat list is fine for a single cohesive area.
- Project-specific concepts only — zero implementation detail.

## 2. Domain glossary — e.g. `docs/common/glossary.md`

- Numbered index table (one line per term) + per-term sections + cross-links.

## Usage rules

- Read `CONTEXT.md` plus the relevant ADRs before exploring.
- Use glossary vocabulary in every artifact (issue titles, refactor proposals, hypotheses, test names). Never drift to `_Avoid_` synonyms.
- A novel concept is a signal: rethink whether you are inventing language the project does not use, or record the gap (hand it to `domain-modeling`, 未安装则按 `references/deps/domain-modeling.md` 执行).
- If these files are missing, continue silently; creation happens when terms or decisions finalize, typically via `domain-modeling`（兜底 `references/deps/domain-modeling.md`）.
- Flag ADR conflicts explicitly (`> _与 ADR-XXXX … 冲突，但…_`); never silently override.
