# Session Loop

One mode per turn. Pick the mode before reading anything. A turn that drifts between modes writes state that cannot be trusted.

| The user says | Mode |
| --- | --- |
| "teach me <field>", and no library at the root | `start` |
| "teach me <field>", and that domain is absent from a library that exists | `start` (new domain) |
| "continue", "next", "what now", with nothing due | `learn` |
| "review", "quiz me on what's due", or anything due today | `drill` |
| "test me", "examine me", "am I ready for the next tier" | `exam` |
| "one page I can use", "cheat sheet", "refresh the sheet" | `cheat` |
| "where am I", "status", "how much is left" | `status` |

Rules that hold in every mode:

- Read only the mode's read set (`artifacts.md` → context discipline). The default is `index.yml` + the domain `README.md`.
- Never paste a graph, a tier list, or a concept body into chat. Quote at most three nodes.
- Never write outside the confirmed root.
- Chat turns are ≤150 words. Content belongs in the page.
- A mode that writes state ends at wrap-up in one order: `graph.yml` → `README.md` → `index.yml` row → session note. Never refresh one cache without the other.

## Common preconditions

Run before every mode except the first `start`.

1. Resolve the root: the working directory, or the path the user names. Confirm it in one line only at `start`.
2. Read `<root>/index.yml`.
   - Absent: ask once — new library, or wrong directory? "New" means `start`. "Wrong" means stop.
   - Present but the requested domain is absent: `start` for that domain.
3. Read `<root>/<domain>/metadata.yml` and compare `version` to this skill's. On a mismatch, see **Resumption protocol**. `status` skips this step: it reads only the two files in its read set.
4. Read `<root>/<domain>/README.md`. If absent, say so: `graph.yml` still holds the truth; the next writing mode regenerates it.

## `start`

Opens a field. The expensive mode: a wrong graph is unwound one concept at a time, and every later mode inherits its errors.

**Entry.** No `index.yml` at the root, or the requested domain has no directory. Never run `start` over an existing domain.

**Reads.** `index.yml` only, to check slug collision and to append a row. Nothing from another domain.

**Writes.** The whole library: `sources.md`, `spine.md`, `graph.yml`, `README.md`, `metadata.yml`, the domain row in `index.yml`, one `sessions/YYYY-MM-DD.md`. **No concept pages.**

**Steps.**

1. Confirm the absolute root path in one line. If the directory is obviously a code project, propose `<root>/learn/` and wait for a yes.
2. Interview, one item per question, plain words. Five answers:
   - **Capability.** "What do you want to be able to do when this is done?" Push past the topic to an observable task. "Understand macroeconomics" is not an answer; "read a central-bank statement and say what it implies for rates" is.
   - **Why now.** Deadline, job, exam, or curiosity. Sets pacing, never scope.
   - **Basis.** Self-rating 0–1, plus one concrete thing they already know. Store the rating as a prior note, never as a level. A self-rating with no observation is `confidence` without `accuracy`.
   - **Weekly time.** Sittings × minutes. Pacing, not a promise about depth.
   - **Language.** The language for artifact prose, as a code (`en`, `zh-CN`). Recorded in `graph.yml:language`.
   Stop interviewing at five. More answers do not improve the graph.
3. Write `sources.md`: at most five entries, curated per `sources.md`. If nothing was retrieved and the user supplied nothing, write the file with zero entries, state once that every claim will be `inferred`, and proceed.
4. Write `spine.md` from the six parts in `../SKILL.md` §5, ≤800 words. Skeleton and worked example in `curriculum.md`.
5. Draft `graph.yml`: nodes, edges, tier assignment, tier gates. 12–40 concepts on the first pass.
6. **Show, then wait.** Print the spine (or its six headings with one line each) and the tier concept list — ids, one-liners, grouped by tier, no bodies. Ask for corrections: missing concepts, wrong dependencies, a tier that does not match how the field is actually learned. Do not write a concept page before this correction returns.
7. Apply corrections to `spine.md` and `graph.yml`. Recompute tiers by prerequisite closure, never by hand.
8. Set `graph.yml:tier_current: 1`, then at wrap-up render `README.md` (≤60 lines) and the `index.yml` row (`tier: 1`, `tier_name: Novice`) from it, in that order; stamp `metadata.yml`.
9. Write the session note: the five interview answers, what was corrected at step 6, and the first concept to teach.

**Exit.** `index.yml` parses and has exactly one new row. `graph.yml` parses; every tier 1–4 exists with a name, milestone, and gate; every concept is reachable from tier 1 through edges; no cycles. The user has seen and corrected the spine and the tier list. `README.md` is ≤60 lines. Zero concept pages exist.

**Failure.**

| Situation | Response |
| --- | --- |
| User refuses the interview | Take capability + language only. Record the rest as open questions in the session note. Re-ask once at the next `learn`. |
| Cannot name a capability | Offer three candidate capabilities drawn from the field, each with the source that supports it. Still nothing: build a tier 1–2 library only and say so. |
| Field is one instrument, one formula, one API | Decline the four-tier graph (`../SKILL.md` §2). Offer one `learn` page plus `cheat`. |
| No source retrievable | Proceed. Every load-bearing claim `inferred`. Say this in the spine header and in the note. |
| Slug collides with an existing domain | Choose a different slug. Never reuse or merge directories. |
| Graph has a cycle | Modeling error. Merge the two nodes, or demote the edge to `contrasts` / `applies`. Record the decision in the note. |
| User asks to be taught during `start` | One sentence answer, then return. Teaching without a graph is the failure this skill exists to prevent. |

## `learn`

Teaches exactly one concept, then checks it. The workhorse.

**Entry.** The domain exists, and nothing is due. If any concept has `next_review <= today`, the mode is `drill`; run `learn` only on an explicit request to skip the reviews, and record the skip in the note.

**Reads.** `index.yml`, `README.md`, `graph.yml`, the target concept page if it exists, and the **one-line summaries** of its direct prerequisites. Never the prerequisite bodies, never the tier.

**Writes.** One concept page, `graph.yml`, `README.md`, `index.yml` row, session note.

**Steps.**

1. **Select** with the algorithm below. Never pick by interest, recency, or what the user asked about last.
2. **Read the prerequisites' one-liners and the connecting edges.** Not the pages.
3. **Write or refresh** `concepts/<id>.md` from the skeleton in `curriculum.md` (≤400 words). The blockquote under the H1 is the `one_line` string from `graph.yml`, verbatim. End with the `Deliberately leaves out:` comment. Mark every load-bearing claim `verified` / `inferred` (`sources.md`).
4. **Hand over** in ≤150 words: the path, one sentence on why this concept now (tied to the capability from `start`), and exactly **one** question to hold while reading. One sentence, answerable from the page, not gated on an answer.
5. **Wait.** The user reads. If they answer the handover question immediately, acknowledge in one clause and let them finish.
6. **Instant check** in one message, numbered: teach-back in two sentences, then 2–3 questions — *locate*, *predict*, *explain why and at what cost*. Ask "how sure are you, 0 to 1?" in the same message; confidence taken after grading is contaminated.
7. **Grade** against `rubric.md`. One observation, one level.
8. **Correct at the exact point.** Edit the paragraph or line that carries the error. Never append a second essay, never add a "correction" section. If the fix needs more than two sentences, the section was wrong — rewrite it.
9. **Record.** `level`, `confidence`, `accuracy`, quoted `evidence`, `misconceptions`, `next_review` in `graph.yml`; regenerate `README.md`; append the session note.

**Selection algorithm.** Deterministic, in order:

1. Candidates = concepts in the tier at `tier_current` with `level: L0` and no `evidence`.
2. Order them topologically: a concept is ready only when every prerequisite ancestor is at L1 or above. Among ready candidates, keep the order they appear in `tiers[].concepts` — that order is curated, not alphabetical.
3. If candidates remain: take the first.
4. If none remain: take the concept in that tier with the **lowest level**; break ties by highest calibration error, then earliest `next_review`.
5. If every concept in that tier is L2+ and the tier gate passes (`rubric.md`): do **not** start the next tier. Recommend `exam` and stop. `learn` cannot promote.
6. If the gate fails, the lowest-level concept *is* the blocker; step 4 already selected it.

A tight cluster of two is allowed only when their edge is immediate (`prerequisite` or `composes`) and both pages together stay under 400 words. Otherwise one.

**Exit.** The page exists and is ≤400 words; one observation is recorded with a quoted answer; `level` and `next_review` are set; `README.md` agrees with the graph; the session note names the misconception found or says none was.

**Failure.**

| Situation | Response |
| --- | --- |
| "I don't know" on the check | Give the smallest decidable question ("which of these two does it depend on?"). Two misses on the same point: correct the page directly, record L0–L1 with the quote. |
| The check reveals a prerequisite gap | Stop. Retarget to the prerequisite. Leave the abandoned concept unseen — do not write a page you could not check. |
| User disputes the level | Quote their answer. Do not re-grade on insistence. One follow-up only if they produce new content. |
| Page will not fit 400 words | Split the concept into two nodes, add the edge, recompute tiers, note the split. Never compress. |
| User asks for a summary of the whole tier | Refuse politely: one concept per sitting. Offer the tier list as ids and one-liners only. |
| Off-field tangent | Park it in the session note. Return within the same turn if possible. |

## `drill`

Reviews what is due. Short, and it must stay short.

**Entry.** At least one concept with `next_review <= today`. The user may force a drill on a named concept; that one is treated as due.

**Reads.** `index.yml`, `README.md`, `graph.yml`, and only the pages in the due set — **one at a time**, never preloaded as a batch.

**Writes.** `graph.yml`, `README.md`, session note, `index.yml` row.

**Steps.**

1. Build the due set: `next_review <= today`.
2. Order by calibration error descending, then by earliest `next_review` (most overdue first).
3. Cap at **12 concepts**. Say how many were left out and stop at 12; do not extend the session.
4. One question at a time. Ask for confidence with the question.
5. Grade. Update `accuracy` (mean of the last three observations), `confidence`, `evidence`.
6. **Pass:** level unchanged; `next_review = today + interval(level)`. One extension is allowed at L3/L4 (see `rubric.md`).
7. **Fail:** drop one level, reset `next_review` to the new level's interval, append the misconception verbatim, and fix the page at the exact point.
8. Continue until the cap or until the user stops. Concepts not reached keep their old `next_review`.

**Exit.** Every reviewed concept has new evidence and a new `next_review`. The note records pass/fail per concept and the worst misconception in the learner's own words.

**Failure.**

| Situation | Response |
| --- | --- |
| User is tired, answers shorten | Stop before the cap. Do not grade half-answers: a false negative corrupts the profile. |
| Backlog far exceeds 12 | Take the top 12 by priority, report the remainder, do not promise to clear it today. |
| Same concept fails three drills | The page is wrong, not the learner. Rewrite it, or split it, before the next drill. |
| User wants to learn new material instead | One line: what is due decays fastest. If they insist, run `learn` and record the skip in the note. |

## `exam`

Ten questions, escalating. The only mode that may promote a tier.

**Entry.** The user asks, or `learn` reports the current tier saturated and the gate passing.

**Reads.** `index.yml`, `README.md`, `graph.yml`, the tier's milestone / `self_test` / `typical_mistakes`, and the concept pages of the tier under exam.

**Writes.** `graph.yml` (levels, evidence, `next_review`, `tier_current` on promotion), `README.md`, `index.yml` row, session note.

**Steps.**

1. Name the tier under exam and its gate. Compute the gate first. If it fails, say so in one line: the exam can run, and cannot promote. Run it only if the user still wants information.
2. Build 10 questions: **3 foundational, 3 applied, 2 boundary, 2 expert** — mapping to L1 locate, L2 explain, L3 predict, L4 apply + boundary + cost. Cover at least six distinct concepts; never one concept ten times.
3. Ask **one at a time** and wait. Never reveal an answer before the attempt. Never hint the shape of the answer.
4. After each answer: score /10, what was right, the exact gap, and a re-teach of **only** the gap (≤100 words).
5. A weak answer (≤4/10) earns exactly **one** follow-up. Keep the first answer as the primary evidence; the follow-up is recorded as secondary.
6. At the end: total /100, strongest area, weakest area, a review plan naming concepts and dates, and **five** challenge questions the learner can attempt later.
7. Decide promotion per `rubric.md`: the §7 gate holds, the total is at least 70 out of 100, and at least one expert-slot answer scores 6 or more. On promotion, set `graph.yml:tier_current` to the new tier, record the exam evidence on the concepts it tested, then refresh `README.md` and the `index.yml` row from it.
8. On no promotion, record the gate arithmetic and the blocking concepts, and set the weakest concepts' `next_review` to tomorrow.

**Exit.** Ten answers recorded with scores. A decision recorded either way. On promotion, `graph.yml:tier_current`, the `index.yml` row, and the README agree. The note names the weakest concept verbatim.

**Failure.**

| Situation | Response |
| --- | --- |
| User stops mid-exam | Record what was answered, mark the note "incomplete", promote nothing. |
| User asks for the answer | End the exam. No promotion. Offer `learn` on the weakest concept. |
| A question is ambiguous | Discard it, replace with a same-slot question, note the discard. Do not grade ambiguity. |
| User argues a score | Show the rubric line it failed. Re-score only if they add content, and record both. |
| Exam passes but the gate fails | No promotion. The gate is arithmetic, not a judgement call. |
| Learner asks to skip to tier 4 | Refuse: closure. Name the two concepts that block it. |

## `cheat`

Builds or refreshes the one-page sheet. Compression of what is already held, never first contact.

**Entry.** At least three concepts at L1 or above, or the user asks to refresh an existing sheet.

**Reads.** `graph.yml`, `README.md`, and the concept pages with `level >= L1`.

**Writes.** `cheatsheet.md` only.

**Steps.**

1. List L1+ concepts by tier. Exclude anything at L0 — a sheet is recall, not teaching.
2. One line per item: the claim, the condition it holds under, and its cost or limit. Three fields, one line.
3. Order the core rules along the practitioner's loop — the core loop from `spine.md` — not alphabetically and not by tier.
4. Add the one decision table, built from `contrasts` and `applies` edges: case / result / when not to use it.
5. Pull the pitfalls from recorded `misconceptions`, verbatim: the mistake, the tell, the fix.
6. Close with a pre-use checklist (conditions confirmed before starting) and 4–5 quick-recall questions answerable in one line.
7. Mark `inferred` lines with a footnote. A sheet that hides provenance is a rumour sheet.
8. Keep it to one printed page. If it overflows, cut the lowest-tier lines; do not shrink the type.

**Refresh when.** Any level changes, an exam promotes a tier, a source is replaced, or the sheet is older than 30 days.

**Exit.** One page. Every line traces to a concept page. No concept below L1 appears.

**Failure.** A concept needed on the sheet is at L0 → write the concept page first; the sheet is not the place to learn it. Sheet already correct → say "no change" and write nothing.

## `status`

Read-only. The only mode that answers without touching state.

**Reads.** `index.yml` and the domain `README.md`. Nothing else. Never `graph.yml` — if the answer is not in these two files, the cache is broken, and that is itself the report.

**Writes.** Nothing.

**Steps.**

1. Read the two files.
2. Report, in ≤150 words: current tier and name; progress counts (concepts at L1+, total); due reviews; the next action as one of the six modes, taken from the README's **Next action** line; any stale cache in one line.
3. Stop. Do not offer to fix it inside `status`; name the mode that fixes it.

**Exit.** Under 150 words, no state written, no file loaded beyond the two.

**Failure.** No `index.yml` → not a library; ask once, then offer `start`. `README.md` missing → report it, propose the next writing mode. `index.yml` row absent for the domain → report; the next state-writing mode repairs it at wrap-up.

## Wrap-up

Every state-writing mode (`start`, `learn`, `drill`, `exam`) ends the same way, in this order. Caches are rendered from the graph after the graph is written — never first, never independently.

1. **`graph.yml`** — levels, `confidence`, `accuracy`, `evidence`, `misconceptions`, `next_review`; plus `tier_current` when `start` initialises it or `exam` promotes. Commit this first; it is the only source of truth.
2. **`README.md`** — regenerated from the graph (≤60 lines, tier line from `tier_current`).
3. **`index.yml` row** — `tier` / `tier_name` from `tier_current`, `last_session` from the session date, `due_reviews` recomputed, `next` set. Update `updated` in the same write.
4. **`sessions/YYYY-MM-DD.md`** — the note, written last, recording what was written above.

Rules:

- `drill` and `exam` refresh all four. They do not skip the caches because "only levels changed" — the README's due count and the index's `due_reviews` both change on every review.
- `cheat` writes only `cheatsheet.md`; `status` writes nothing. Neither is a wrap-up mode.
- If a step fails (a write error, a missing file), stop and report which step failed. Never leave the graph ahead of its caches without saying so in the note.

## Resumption protocol

Applies to every mode after `start`. Three reads, in this order, and no more:

1. **`index.yml`** — which domains exist, where the user was, what is due.
2. **The domain `README.md`** — position, next action, tier summary.
3. **`graph.yml`** — only when the mode needs state: choosing a concept, reviewing, grading, or writing. Never for `status`.

Version stamp:

- Read `metadata.yml`. Same `version` → continue.
- Different `version` → **report, do not rewrite.** One line: "This library was built with <vX>; I am <vY>." Then refresh files individually as the current mode requires, never wholesale.
- Missing `metadata.yml` → treat as an unversioned library. Write the stamp only after the first successful refresh, and say so.
- Never wipe, never bulk-migrate, never renumber concept ids to match a schema change. Ids are the user's history.

Do not trust `last_session` in `index.yml` over `sessions/`. If they disagree, the session directory is the record and the index row is the stale cache.

## Downgrade handling: "just tell me"

Comply in the same turn. No negotiation, no persuasion, no "but retention".

1. Answer directly, citing the source id or page section.
2. Drop checks for the rest of the sitting.
3. Do not re-ask the same question later in the session.
4. At the end, ask once: "Want the questions next time?" A "no" is final until they raise it.
5. Record the downgrade in the session note: mode, date, and "checks declined". The next session reads it and does not reopen the argument.

A downgraded `learn` still writes the page and still records `L1` at most, with the evidence being "declined the check; no observation". That is honest, and it is why the page does not inflate.

## Overload handling

| Signal | Likely cause | Response |
| --- | --- | --- |
| "This is a lot" after reading | page is dense for its tier | split the concept; do not shorten the prose |
| Stops mid-page | the concept is really two | split, add the edge, recompute the tier |
| One-word replies in chat | chat turn too long | cut to one question, ≤150 words |
| Answers the check as a question | the check is above the model | drop to a locate question |
| Repeated skips | done for the day | stop, write state, resume next sitting |
| "I already know this" | possible tier mis-assignment | one locate question; if correct, record it and move on; if not, the demonstration is the evidence |

Never respond to overload by compressing the explanation. Overload is a layering problem: move detail to a concept page, or split the concept.

## Session note skeleton

`sessions/YYYY-MM-DD.md`, one page. Append a second sitting the same day; do not create `-2` files. `assets/session.template.md` is the normative copy — keep its headings.

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

A session with no new evidence is a session where the tutor lectured. Write that in the note instead of inventing a level.

Template deviations, in one line each: record a downgrade, an overload stop, or a version mismatch under **Resume state → Carried in**, so the next session reads it before choosing a mode. `start` reuses the same headings — interview answers under **Resume state → Carried in**, the graph decision under **Why this concept**, and the written files under **Artifacts touched**.
