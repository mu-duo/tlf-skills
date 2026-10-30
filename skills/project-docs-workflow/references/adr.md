# ADR conventions

Default profile. Projects may override in their materialized `docs/adr/README.md`; that copy governs runtime behavior.

## Files

- Filename `NNNN-slug.md`: 4-digit zero-padded. **Numbers are never reused** — a new entry takes the current maximum number + 1 (tombstone stubs count). H1 title in the project language.
- The slug (filename) is **immutable**: tombstoning clears the body only, it never renames the file.
- Numbering race: when adding, if the number is already taken (concurrent write), shift +1 and sweep references (see Reference sweep).

## Lifecycle

The ADR set keeps current entries plus retired marker lines; editing and deleting are both allowed. Full history is held by git.

- **Semantic change** (conclusion / constraint / scope): edit in place and append one line to `## Log` — `- YYYY-MM-DD <one-line reason>` (canonical format: the date then the reason, no prefix label).
- **Non-semantic change** (typos, format, links): edit directly, no Log.
- Default is in-place editing. Write a **new** ADR only when the change is direction-defining or worth citing on its own long-term; then annotate the old entry (see Annotations).

## Deletion

- Prefer an annotation first: `> 已废弃（日期）：原因` keeps the content. Delete only when the project's **human owner** (or someone explicitly authorized by them) judges the entry has no reference value / is pure noise — agents must not decide deletion on their own.
- Deletion = **tombstone stub**: clear the file body to two lines — `# <original title>` and `> 已删除（YYYY-MM-DD）：原因` — keeping the number and filename (existing path links stay valid).
- **Tombstones are final**: a tombstone stub is never deleted; the number retires permanently.
- Deletion order: ① tombstone-stub the file (rewrite the body) → ② remove the row from the catalog → ③ run the whole-repo reference sweep. On retry / re-run, check first to avoid duplicate Log lines or annotations.

## Annotations

Status block on the first lines after the H1. Active entries carry none. Retired entries carry **only marker lines from this fixed set** — one line per retirement event, stackable; no free-form notes:

| Marker | Meaning |
| --- | --- |
| `> 已被 ADR-XXXX 取代（日期）：原因` | superseded by a newer ADR (a new entry was written) |
| `> 经 ADR-XXXX 修订（日期）：说明` | amended in place by a newer ADR |
| `> 已废弃（日期）：原因` | deprecated; content retained |
| `> 已删除（日期）：原因` | deleted; tombstone stub |

## Reference sweep

`ADR-XXXX` (4-digit zero-padded) is the native citation notation. PRD / Current may also link an ADR by **stable Markdown path** — e.g. `支持[离线使用](../../adr/0003-offline.md)`, optionally with a `#fragment`; there the descriptive phrase carries the meaning, so no `ADR-XXXX` label is required at the link site. The descriptive phrase stands alone and the rationale is never transcluded or summarized; linking is optional and never inferred. Both notations are valid; this does not change the ADR lifecycle (see `rendering.md`).

Whenever an entry is **deleted or semantically edited**, the executor must sweep references: prefer a subagent; without one, grep directly. Sweep **both notations** — the `ADR-\d{4}` number, and Markdown links to an ADR file by its stable filename pattern `adr/<NNNN>-<slug>.md` (any relative prefix — `docs/adr/…`, `../adr/…`, `../../adr/…`, with or without a `#fragment`). Scope = the whole repository (`docs/` must be updated; code comments judged one by one: keep / update / annotate in place). Handle every hit before finishing. When a reference points at a deleted entry, prefer retargeting it to the replacing ADR number; with no replacement, drop the sentence or annotate it in place `(ADR-XXXX deleted)`.

Path links survive tombstoning (the filename is immutable) and a tombstone stays rendered, so such links keep resolving — but a **semantic** edit changes the content the link is about, so re-read and review each path-linked reference, not only the number.

## Index (README)

`docs/adr/README.md` is a **catalog**, not a status authority: table `| 编号 | 标题 | 一句话 |`. It lists every **not-deleted** entry — including entries carrying a retired marker; deleting removes the row, and a gap in the numbering means deleted (see the matching tombstone stub / git). The one-line column may note a retired entry's status (e.g. "superseded by ADR-XXXX"). Its rules section states this v2 lifecycle. After adding an entry, register a row in the catalog.

## Body shape

H1 title → decision + rationale + trade-off (`代价：…`) → optional `## Log` (appended on every semantic change). No `## Considered Options` section by default; `代价` is the cost borne by the chosen option.

An ADR can be a single paragraph; the value is recording *that* a decision was made and *why*.

## Negative decisions

Default: record accepted decisions, not rejected alternatives. Do not add a `## Considered Options` section. A rejected alternative may be mentioned in one sentence only when it prevents foreseeable re-litigation, or when audit / compliance explicitly requires it; never enumerate alternatives. The agent judges the "prevents re-litigation" exception by default; the user / project may override. `代价：…` describes the cost of the chosen option, not what was rejected. Existing entries are history: do not rewrite them; a user may explicitly authorize a cleanup. This policy constrains durable records only; alignment / grilling may still explore alternatives. PRD non-goals / out-of-scope statements are scope boundaries, not rejected alternatives; keep them without per-item rationale.

## Relationship to domain-modeling

The base ADR format is compatible with the `domain-modeling` skill's ADR-FORMAT (未安装则按 `references/deps/domain-modeling.md` 执行). That skill forbids neither edits nor deletes and carries its own `proposed | accepted | deprecated | superseded` status words; this profile is a superset (reference sweep, tombstone stubs, catalog-style README), and the two coexist. The base format lists `Considered Options` as an optional section; this profile defaults to omitting it (see `## Negative decisions`). See `coexistence.md`.
