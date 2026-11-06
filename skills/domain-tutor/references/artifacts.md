# Artifacts

State lives in files, and only in files. A conversation that ends without a write did not happen.

## Tree

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

No other files. No cache directories, no backup copies, no `notes/`, no `drafts/`, no assets inside the root. Concept ids and domain slugs are ASCII kebab-case and never change. Dates are ISO `YYYY-MM-DD`, local to the learner's session.

## `index.yml`

One per root. Cross-domain index and resume point. Cap: one row per domain.

```yaml
version: 1
root: /home/tan/learn
owner: tan
updated: 2026-11-01
domains:
  - slug: specialty-coffee
    display_name: Specialty Coffee Brewing
    tier: 2                      # rendered from graph.yml:tier_current
    tier_name: Beginner          # rendered from graph.yml:tier_current
    last_session: 2026-11-01
    due_reviews: 1
    next: extraction-yield
```

| Field | Type | Rule |
| --- | --- | --- |
| `version` | int | Format version of this file, currently `1`. Not the skill version. |
| `root` | string | Absolute path. Must equal the directory the file is in. Written once at `start`. |
| `owner` | string | The learner's name or handle, as they gave it. No email addresses. |
| `updated` | date | Last write to this file. |
| `domains[]` | list | One entry per domain directory. |
| `domains[].slug` | string | Immutable, ASCII kebab-case, equals the directory name. |
| `domains[].display_name` | string | Human name, in `graph.yml:language`. |
| `domains[].tier` | int 1–4 | **Rendered from `graph.yml:tier_current`.** Written `1` at `start`; changes only when `exam` promotes. Never edited here. |
| `domains[].tier_name` | string | **Rendered from `graph.yml:tier_current`**: `Novice` (1), `Beginner` (2), `Practitioner` (3), `Adept` (4). Must agree with `tier`. |
| `domains[].last_session` | date \| null | The date of the newest file in `sessions/`, not the date of the last edit here. `null` if never studied. |
| `domains[].due_reviews` | int | Count of concepts with `next_review <= today`. Derived from `graph.yml`. |
| `domains[].next` | string \| null | The concept id to teach or review next, or `null` when nothing is pending. The mode is not stored here; `README.md` names it. |

Invariants: `slug` values are unique; every `slug` has a directory; `tier` equals `graph.yml:tier_current` and `tier_name` matches `tier`; `root` matches reality. The row is a **cache** — derived from `graph.yml` and `sessions/` at wrap-up, never edited by hand, never the place a level or a tier is recorded.

## `metadata.yml`

A version stamp for idempotent resumption. Cap: 4 lines.

```yaml
skill: domain-tutor
version: 1
updated: 2026-11-01
```

| Field | Rule |
| --- | --- |
| `skill` | Literal `domain-tutor`. Identifies the builder. |
| `version` | The skill release stamp, currently `1`. Compared on every resume. Bump only on a schema-level refresh. |
| `updated` | Date of the last schema-level refresh — new fields, changed caps. Not every session. |

## `graph.yml`

The single source of truth for state: concept state and the learner's current tier. Machine-readable; no prose beyond the one-liners.

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

### Top level

| Field | Type | Rule |
| --- | --- | --- |
| `version` | int | Format version, currently `1`. |
| `domain` | string | Equals the directory slug. |
| `display_name` | string | In `language`. Matches the `index.yml` row. |
| `updated` | date | Last write to the file. |
| `tier_current` | int 1–4 | The tier the learner has been **promoted into**. Written `1` at `start`; incremented only by a promoted `exam`. Not computed from concept levels — the gate is checked at the exam, not continuously. `index.yml`'s `tier` / `tier_name` and the README's tier line are rendered from this field. |
| `language` | string | Language code for all artifact prose (`en`, `zh-CN`). See language policy. |
| `tiers[]` | list | Exactly four entries, ids `1`–`4`. |
| `edges[]` | list | May be empty only for a one-node field, which should not exist. |
| `concepts[]` | list | One record per concept, same ids as in `tiers[].concepts`. |

### `tiers[]`

| Field | Type | Rule |
| --- | --- | --- |
| `id` | int 1–4 | Fixed. |
| `name` | string | English enum, fixed: `Novice`, `Beginner`, `Practitioner`, `Adept`. Never translated. |
| `display_name` | string | The learner-language label for that tier. May equal `name`. |
| `milestone` | string | One sentence, observable: what the learner can do at the tier's exit. No "understands". |
| `typical_mistakes` | list[str] | 1–3 per tier. Used to build distractors and exam follow-ups. |
| `self_test` | string | One question the learner can ask themselves to judge the tier. |
| `gate.min_level` | string | `L2`. Fixed unless the curriculum changes; never lowered to pass. |
| `gate.max_calibration_error` | float | `0.3`. Fixed. |
| `concepts` | list[str] | Ordered ids in this tier. This order is curated and is the tie-break for selection (`session-loop.md`). Every id appears exactly once across all four tiers. |

### `edges[]`

| Field | Type | Rule |
| --- | --- | --- |
| `from` | string | Concept id. Exists in `concepts[]`. |
| `to` | string | Concept id, different from `from`. |
| `type` | string | One of `prerequisite`, `composes`, `contrasts`, `applies`. |

No other edge type, no attributes, no prose labels. `contrasts` is stored once; `prerequisite` subgraph is acyclic. Semantics in `curriculum.md`.

### `concepts[]`

| Field | Type | Rule |
| --- | --- | --- |
| `id` | string | ASCII kebab-case, immutable, equals `concepts/<id>.md`. |
| `canonical` | string | The concept's name in `language`. |
| `aliases` | list[str] | English term and known synonyms. Include the English term whenever `language != en`. |
| `one_line` | string | ≤15 words, one relation, no "and". Byte-identical to the blockquote under the page's H1. |
| `tier` | int 1–4 | Computed by prerequisite closure, never hand-assigned (`curriculum.md`). |
| `level` | string | `L0`–`L4`. Set only from a recorded observation. |
| `confidence` | float 0–1 | The learner's self-rating, taken **before** grading. |
| `accuracy` | float 0–1 \| null | Mean of the last three observations. `null` until the first observation. |
| `evidence` | list[str] | Each entry: `"YYYY-MM-DD: \"<verbatim>\" — case: <the case> — gap: <the exact gap>"`. Dated, quoted, specific. Never empty when `level != L0`, never a verdict ("mastered"). |
| `misconceptions` | list[str] | Verbatim, in the learner's words. Cleared only when re-tested and passed. |
| `next_review` | date \| null | From `rubric.md`. `null` until the concept has recorded evidence; a `null` **with** evidence is treated as due now. |
| `sources` | list[str] | `s1`…`s5` from `sources.md`, or a short citation when the page rests on something outside the five. May be empty only when the page is entirely `inferred`. |
| `verified` | string | `verified` or `inferred`. `verified` iff every load-bearing claim on the page has a retrieved source at chapter/section/URL level; `inferred` when any is not, or when sources conflict. |

Calibration error is **not stored**. It is `confidence - accuracy`, computed when needed. Storing it invites two numbers that disagree.

## `README.md`

The only entry point. A cache, not a source of truth. Cap: 60 lines.

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

Rules:

- Everything is rendered from `graph.yml`, including the tier line (`tier_current`) and the pointers. The `index.yml` row is a cache of the same graph.
- Every line derivable from state. No new claims, no teaching, no advice.
- **Conflict rule:** if the README and `graph.yml` disagree, the graph wins and the README is regenerated. If `tier_current` and the gate arithmetic disagree, print both and mark the tier line `stale`; never lower or raise a tier to reconcile them.
- Regenerated at the wrap-up of every state-writing mode (`start`, `learn`, `drill`, `exam`), in the order graph → README → index row → session note. `cheat` and `status` do not write it.
- Never edited to fix a fact. Fix the graph, then regenerate.

## `spine.md`

Purpose: the whole field, crudely, one page. Cap: 800 words. Skeleton, worked example, and omissions: `curriculum.md`.

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

Parts 2–6 use the one table each, as in `assets/spine.template.md`: boundaries (inside / adjacent / assumed), nouns (entity / what it is / relates to / source), seams (seam / what crosses / what each side promises), omissions (ignored / why / what looks strange). The core loop is 5–7 numbered steps, each marked `verified` / `inferred`.

Written once at `start`; revised only when the graph proves it wrong. Never grows a definitions section.

## `sources.md`

Purpose: the five anchors and what each is for. Cap: **5 entries**. Entry format, selection criteria, conflict handling: `sources.md` (the reference file).

## `concepts/<id>.md`

Purpose: one concept, in full. Cap: **400 words** for the whole page — worked example included.

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

The skeleton in `assets/concept.template.md` is normative; keep its headings. The template's "Why it sits here" block is where relations are enforced: prerequisites and dependents must match `graph.yml` edges, and "not yet written" is the honest entry when a prerequisite has no page.

## `cheatsheet.md`

Purpose: compressed recall for the five minutes before use. Cap: one printed page (~45 lines). Skeleton: `curriculum.md`. Excludes every concept below L1.

## `sessions/YYYY-MM-DD.md`

Purpose: what happened, what was got wrong, where to resume. Cap: one page. Appending a second sitting the same day is allowed; creating `YYYY-MM-DD-2.md` is not.

Skeleton: `session-loop.md` → session note skeleton. Required content: mode, target, evidence with quotes, level change, misconception, next action, flags. A session note with no quoted answer is a note about the agent, not the learner.

## Metadata stamp and idempotent resumption

- The stamp is written once at `start` and updated only on a schema-level refresh.
- On resume: read `metadata.yml`, compare `version` to this skill's.
  - **Equal** — normal operation.
  - **Library older** — report in one line, then refresh **files individually** as the current mode requires. Never bulk-migrate, never rewrite ids, never delete fields the newer schema does not use. Show the diff before replacing a file that holds user content.
  - **Library newer** — do not downgrade the schema. Report the mismatch and operate against the fields as they exist.
  - **Missing** — treat as unversioned. Write the stamp after the first successful refresh and say so.
- Idempotency, by mode:
  - `start` twice on the same slug: refused. The row and directory exist; this is `learn`.
  - `learn` twice on one concept: the second refreshes the page in place. It creates no second file and no duplicate concept record.
  - `drill` twice in a day: the second finds nothing due and says so; it does not force reviews forward.
  - `cheat` twice: the second either reports "no change" or rewrites the same file with the same content.
  - `exam` twice: two separate exam records in the session note; the highest-score decision is not kept — the latest recorded decision stands, and a promotion is not undone by a later failure.

## The README cache rule

`README.md` is rendered **from** state at wrap-up. It is never the place a fact is first recorded, and never the answer to "is this true?".

| Question | Answer source |
| --- | --- |
| What level is concept X? | `graph.yml` |
| What is due? | `graph.yml` (`next_review`) |
| What tier am I in? | `graph.yml` (`tier_current`), checked against the gate arithmetic |
| What should I do next? | the selection algorithm, then the README line rendered from it |

Conflict → graph wins; regenerate the README and the `index.yml` row together. If the README was hand-edited, say so in the session note before overwriting. Never keep a correction only in the README or only in the index row.

## Context discipline

| Mode | May read | Must not read |
| --- | --- | --- |
| `start` | existing `index.yml` (collision check), user-supplied sources | other domains' files, any concept page |
| `learn` | `index.yml`, domain `README.md`, `graph.yml`, target page, direct prerequisites' **one-liners** | other tiers' page bodies, `sessions/`, other domains |
| `drill` | `index.yml`, `README.md`, `graph.yml`, the due set's pages — one at a time | pages outside the due set, `sessions/`, other domains |
| `exam` | `index.yml`, `README.md`, `graph.yml`, tier metadata, pages of the tier under exam | other tiers' page bodies, other domains |
| `cheat` | `graph.yml`, `README.md`, pages at L1+ | `sessions/` (misconceptions are already on the concepts), other domains |
| `status` | `index.yml`, domain `README.md` | `graph.yml`, concept pages, `sessions/`, other domains |

Never `ls -R`, never glob `concepts/*.md`, never load a whole tier to answer one question. If the mode seems to need more, the artifact is too big: split the concept.

## Language policy

- `graph.yml:language` records the language for artifact prose. All of `spine.md`, concept pages, `cheatsheet.md`, `README.md`, and session notes are written in it.
- **File names, directory names, ids, and slugs are ASCII kebab-case**, derived from English. They never change when the prose language changes.
- YAML keys stay English; the schema is not translated.
- `tiers[].name` stays the fixed English enum (`Novice`, `Beginner`, `Practitioner`, `Adept`); `tiers[].display_name` carries the learner's label. Levels stay `L0`–`L4`.
- `concepts[].aliases` must include the English term when `language != en`, so a later agent can match the concept.
- Quotes in `evidence` and `misconceptions` are verbatim in the language spoken. Translate only alongside the original, never instead of it.
- Source titles stay in their original language; `sources.md` notes a translation if one was used.
- Changing language mid-library is allowed and does not trigger a rewrite: new pages use the new language, existing ids and files stay, and the session note records the switch.
