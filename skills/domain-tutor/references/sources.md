# Sources

A field has no `path:line`. Claims are anchored in sources instead, and the anchor is only as good as the retrieval behind it.

**Hard rule: never fabricate a citation.** Not a chapter number, not a page, not an author, not a URL, not a date. If a source was not retrieved in this session and was not handed over by the user, the claim is `inferred` — however certain it feels, however famous the book.

## `verified` and `inferred`

Two markers, applied to every load-bearing claim on `spine.md`, `concepts/<id>.md`, and `cheatsheet.md`. `README.md` and `graph.yml` carry no prose claims; they inherit from the pages.

- **`verified`** — traceable to a source at chapter / section / URL level, **and that source was actually retrieved or supplied in this session**. The reader can open it and find the claim.
- **`inferred`** — model knowledge, analogy, synthesis, or a remembered source not re-opened. It may be right. It is not anchored.

Boundary cases, decided:

| Case | Marker | Reason |
| --- | --- | --- |
| Text quoted from a page retrieved this session | `verified` | Directly traceable |
| A textbook you know well but did not open | `inferred` | Memory of a source is not the source |
| A book's table of contents seen, chapter unread | `verified` for "the chapter exists"; `inferred` for anything you say it contains | The anchor proves structure, not content |
| A ubiquitous formula (`F = ma`, compound interest) | `inferred`, noted "(standard; not re-checked here)" | Common ≠ retrieved; do not dress memory as provenance |
| An analogy you constructed ("extraction is like a sponge") | `inferred` | It is yours, and it is a model, not a fact |
| A synthesis across two verified sources | `inferred` | The joining is yours, even when both premises are anchored |
| A source the user pasted or named and supplied | `verified`, with "user-supplied" | Supply counts as retrieval (`../SKILL.md` §12) |
| A number, date, name, or statistic you half-remember | Omit, or say unknown | Never assert an unverified number as fact |
| A claim you saw quoted inside another source | `inferred`, citing the quoting source | You retrieved the quote, not the original |
| Your own worked calculation | `inferred`, and show the arithmetic | Reproducible beats attributed |

When in doubt: `inferred`. Over-marking costs one line; a fabricated citation costs the library's credibility permanently.

## `sources.md` — at most five

Curation happens **before** the first concept page. A library with fifteen sources and no pages is deferral wearing a bibliography.

Entry format: one table row per source, as in `assets/sources.template.md`.

```markdown
| id | Source | Type | Part of the field | Why worth the time | Difficulty | How to use it | What not to waste time on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s1 | <title, author, edition, URL> | book / course / paper / reference / manual | <subfield or chapters> | <one sentence: what only this source gives> | intro / working / expert | <read, do, or exercise; which parts> | <sections or digressions to skip> |
```

Rules:

- **Five rows maximum. No exceptions, no "supporting" list.** A sixth candidate replaces one of the five or is dropped. Delete unused rows; do not leave blanks.
- Ids are `s1`…`s5`, stable. A replaced source keeps its id retired, never reused: `s2 (retired 2026-11-14)`.
- The `Source` cell carries the access trail: edition/year for books, retrieval date for URLs, "user-supplied" for material the user handed over. No access trail means the entry cannot make anything `verified`.
- **Part of the field** names the concepts or tiers, not just chapters. The reader must be able to tell which page each source sits under.
- **What not to waste time on** is a column, not an afterthought: it is the only thing that stops a learner reading a 600-page book cover to cover.
- Each row must earn its place against the other four. A source no concept page cites after two weeks is dead weight — replace or drop it, and say so in the session note.

Selection criteria, in order:

1. **Leverage over completeness.** One source that covers 60% of the field at the right level beats five that each cover 15%. Coverage is measured in concepts served, not pages read.
2. **Level fit.** The primary source must match the tier the learner is in. A research monograph for a Novice is a source the learner will not read; a pop summary for a Practitioner is a source that will teach wrong models.
3. **Canonical vs current.** Prefer the source the field treats as standard for the base model, and one current source for anything the field has moved on. Two schools, two entries — not five.
4. **Retrievable.** If it cannot be opened this session, it does not anchor anything. It may still be listed, marked `inferred`.
5. **Breadth of the spine.** Across the five, parts 1–6 of `spine.md` must each be supported by at least one entry. A gap in part 6 (assumptions) is the most expensive gap.

What not to waste time on:

- A second source for a concept already anchored, unless the two disagree.
- Textbooks you will not open within the week.
- Video courses and lectures as primary anchors — they are hard to cite at section level and easy to misremember.
- Bibliographies, "further reading" lists, and canonical-paper chains.
- Popular summaries of primary work you already have.
- Anything paywalled with no access path. A source you cannot retrieve is a note-to-self, not a citation.
- Sources chosen to look thorough. The cap exists because thoroughness here is measured in pages written, not sources listed.

## The 7-day path

A first pass over the field using only the five sources. It is a route, not a schedule; a sitting is still 10–20 minutes.

| Day | Focus (mode) | Source | Output |
| --- | --- | --- | --- |
| 1 | Orientation — the field in one sentence, boundaries, core loop (`start`) | s1 overview | `spine.md`, `graph.yml` with 12–40 nodes and four tiers, shown for correction |
| 2–3 | Tier 1 — the 4–6 concepts with no prerequisites (`learn`) | s1 for the base model, s3 for a second angle | 2–3 concept pages, one check each |
| 4–5 | Tier 2 — mechanism, in dependency order (`learn`) | s1, s4 for applied detail | 1–2 concept pages at L2–L3; stop at the first failed prerequisite check |
| 6 | Seams, contrasts, limits; then review and compress (`learn`, `drill`, `cheat`) | s2 for contrasts, s5 for the current view | contrast edges, `cheatsheet.md`, due reviews cleared |
| 7 | Ten-question exam for tiers 1–2, then report (`exam`, `status`) | none new — an exam tests the pages | exam record, next week's plan |

Constraints on the path:

- No new source is fetched mid-week. A gap is recorded, not patched. Adding a source mid-week is how the five-source cap dies.
- If the field is large, the week covers tier 1–2 only. Say so on day 1; do not compress four tiers into seven days and call it coverage.
- If day 1's correction session changes the graph materially, the week's route follows the graph, not this table.

## Known gaps

A short list at the end of `sources.md`, three bullets at most, each one line:

- `<part of the field none of the five covers well>` — which concept pages it affects.
- `<claim currently inferred>` — what would settle it, and where to look.
- `<conflict between s1 and s2>` — which one the field currently follows, or "unresolved".

Delete a bullet when the gap closes; do not leave a resolved list as history. A gap marked here is cheaper than a fabricated citation later, and it is the first thing to read when a page feels thin.

## Conflict handling

Two sources disagree on a load-bearing claim. Do not silently pick one, and do not average them.

1. **Record it in the concept page**, under a heading such as `## Disagreement` or inside "When it holds" if it is narrow: `[s1]` says X, `[s2]` says Y, at chapter/section level.
2. **Say which one the field currently follows**, and on what basis: recency, adoption, or a newer method superseding an older one. If that is not knowable from the sources, say "unresolved in the sources I have".
3. **Keep the base model singular.** The page teaches one version; the other is one line plus the reason. Two parallel explanations in one 400-word page produce a learner who can state both and use neither.
4. **Mark the concept `verified: inferred`** in `graph.yml` while the conflict is unresolved — it has no single anchored claim set.
5. **Never exam the disagreement** until the base model is at L2. At L3, the learner should be able to say what the other position claims and why the field leans the way it does.
6. If the disagreement is genuinely two schools, it becomes a node (`curriculum.md` → competing schools), not a footnote.

## When no source answers a load-bearing question

The honest sequence, in one turn:

1. **Say unknown.** "None of the five sources answers that at section level." One line, no hedging paragraph.
2. **Mark the claim `inferred`, or remove it.** If the page cannot stand without it, the page shrinks.
3. **Record the gap twice**: one line on the concept page — `Open: <question> — not covered by s1–s5.` — and one bullet under **Known gaps** in `sources.md`. It stays until answered; a gap that disappears without a source was filled by invention.
4. **Propose one specific source**: title, and the section or chapter to check. Specific enough that the user can decide in ten seconds.
5. **Do not fill the gap with plausible content.** A confident paragraph over a gap is the failure mode this file exists to prevent.
6. If the gap blocks the concept entirely, say so, and choose a different next concept for this sitting.

## Citation hygiene

- **Chapter / section / URL level.** `[s1] ch. 4`, `[s2] §2.1`, `[s3] https://… (retrieved 2026-11-01)`. That is enough to find the claim again.
- **No page numbers unless you actually saw them.** Pagination differs by edition and format; a page number you reconstructed is a fabricated citation with extra confidence.
- **Edition and year for books.** A claim can be true of the 2nd edition and false of the 4th.
- **Access date for anything online.** Content moves; the date is what makes the anchor honest.
- **Never cite a search snippet as retrieved.** Open the page, or mark `inferred`.
- **Never cite "the literature", "standard practice", or "most textbooks".** Name a source or mark it inferred.
- **No invented DOIs, ISBNs, or URLs.** If unsure of a URL, cite the title and section only.
- **One anchor per claim.** A claim with three citations usually means the author is unsure which one says it.
- The cheat sheet may compress citations to footnote markers, but every line still traces to a page that carries the full anchor.
