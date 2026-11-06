# Rubric

Levels are assigned from evidence, never from impression. If you cannot quote what the learner said, and name the case it was said about, the level is `L0`.

A field has no `path:line`. The anchor is a **quoted answer plus the case that produced it**, and, for claims rather than answers, a source id at chapter / section / URL level (`sources.md`).

## How to grade L0–L4

| Level | Name | Evidence required | Typical failure |
| --- | --- | --- | --- |
| L0 | unknown | No correct statement; or no observation recorded | A fluent restatement of the page with no relation in it |
| L1 | locate | Places the concept: which subfield, what question it answers, what it depends on | Right vocabulary, wrong or missing dependency |
| L2 | explain | Explains the mechanism in their own words, with the right relations | Correct facts, one reversed or missing arrow |
| L3 | predict | Given a new case or a variant, predicts the outcome, or judges whether the method applies; correct, and with the condition stated | Right outcome, wrong reason; or a prediction that only works knowing the answer |
| L4 | apply | Uses it on a real task, and names its boundary and its cost | Uses it well, cannot say when it stops working, or what it costs |

Grading rules:

- **One level per concept.** A concept explained well on the loop and wrongly on retry is the weaker level today. Keep the first answer as evidence, not as the score.
- **Relations beat vocabulary.** Reciting names in the right order is L1. Connecting two of them correctly is L2. Naming the right relation but reversing its direction is still L2 at most — a reversed arrow predicts wrongly.
- **Coherence caps at L2.** Correct facts with the wrong relations cannot be L3, however fluent. Prediction needs a working causal model; if the arrows are wrong, a correct prediction is luck.
- **A condition is the anchor.** L3 requires the condition under which the prediction holds. A prediction with no stated condition is a guess that happened to land.
- **L4 includes cost.** Using a method is L3-level recall. L4 requires naming what it costs and where it stops applying — the "when it holds" section of the page, in their words.
- **The case must be new.** L3 and L4 are assessed on a case that is not in the concept page. A case the learner has already read the answer to measures memory, not transfer.
- **No observation, no level.** A blank check, a skipped check, or a "just tell me" session records `L0` with the evidence "no observation; check declined". It does not record the old level as confirmed.

## Evidence records

Store the observation, not the label. A level without evidence cannot be re-graded, cannot drive a drill, and hands the next agent a claim it cannot trust.

Good:

```yaml
- id: extraction-yield
  canonical: extraction yield
  tier: 2
  level: L3
  confidence: 0.8
  accuracy: 0.5
  evidence:
    - "2026-10-30: \"yield fell because water passes through faster\" — case: same recipe, finer grind, cup tastes sour — gap: grind also widens the particle spread; the answer is not one-directional"
    - "2026-10-30: \"they measure TDS differently\" — case: why two roasters publish different target yields — gap: could not name the instrument or the correction"
  misconceptions:
    - "finer grind always raises extraction"
  sources: [s1]
  verified: verified
  next_review: 2026-11-04
```

Bad:

```yaml
- id: extraction-yield
  level: L3
  notes: "Learner understands extraction well."
```

The bad record has no case, no quoted answer, no specific gap, and no date. It cannot produce the next question, and it cannot be corrected when it turns out to be wrong.

More bad patterns:

| Pattern | Why it fails |
| --- | --- |
| `level: L3`, evidence: "answered well" | No prediction, no case; unverifiable and unrepeatable |
| The agent's explanation stored as evidence | Measures the agent, not the learner |
| "Mastered" | A verdict, not an observation |
| Five concepts in one record | Cannot be graded, scheduled, or drilled separately |
| "The coffee book, chapter on extraction" with no section and no quote | The correction cannot be located later |
| Evidence is the topic, not the answer ("talked about grind") | Nothing to re-grade against |
| `confidence` recorded after the score was given | Contaminated; calibration is meaningless |
| Two levels in one record ("L2 on the loop, L4 on application") | Pick the level the evidence supports today |

## Confidence and accuracy

Both are numbers in `[0, 1]`.

- `confidence` — ask before grading, in the same message as the question: "How sure are you, 0 to 1?" Record the number they say, not the number their answer deserves.
- `accuracy` — score the attempt:
  - `1.0` — correct, ordered, and relational, with the condition stated.
  - `0.5` — correct with one broken or missing relation, or a correct claim with no condition.
  - `0.0` — wrong, reversed, or a non-answer.
- `accuracy` is the mean of the **last three** observations for that concept, so a fixed misconception moves the number and a lucky answer does not.

Calibration:

```
calibration_error = confidence - accuracy
```

| Value | Reading | Action |
| --- | --- | --- |
| `> 0.3` | Overconfident | Drill first. Do not open new material on this concept's tier until it is under 0.3. |
| `0.1 .. 0.3` | Slight overconfidence | One extra check next session. |
| `-0.1 .. 0.1` | Calibrated | Normal spacing. |
| `< -0.1` | Underconfident | Say so once; they know more than they think. Not a blocker. |

Overconfidence is the priority. An underconfident learner asks for help; an overconfident one applies the model outside its domain and is confidently wrong — the exact failure `spine.md` part 6 exists to prevent.

Report calibration per concept, never as a session average. One badly calibrated concept hides inside a good mean. Negative calibration never blocks a tier gate; the gate only rejects overconfidence.

## Review scheduling

Set `next_review` from the level **after** grading:

| Level | Interval | Rationale |
| --- | --- | --- |
| L0 | 1 day | Nothing to space; re-establish the anchor |
| L1 | 1 day | Placement decays fast without use |
| L2 | 3 days | Explanation needs one consolidation pass |
| L3 | 7 days | Prediction is more stable, still fragile |
| L4 | 21 days | Application transfers; check occasionally |

Rules:

- **A failed review drops one level and resets the interval** to the new level's value. It does not halve, extend, or "try again tomorrow" at the same level.
- **One extension, once.** A passed review at L3 may extend to 14 days, at L4 to 30. Do not chain extensions; the next pass returns to the table.
- `drill` selects `next_review <= today`, ordered by `calibration_error` descending, then by earliest `next_review`.
- **Cap a drill at 12 concepts.** Fatigue produces false negatives, and a false negative corrupts the profile for weeks.
- A concept with no `next_review` is treated as due now; the first observation sets it.
- Skipped concepts keep their date. Never advance a review that did not happen.

## Tier gate

Four tiers, `Novice` / `Beginner` / `Practitioner` / `Adept` (`../SKILL.md` §7). A gate is arithmetic, not a judgement:

```
gate(T) passes iff
  for every concept in tier T, and every prerequisite ancestor of those concepts:
      level >= L2
  and max over that set of (confidence - accuracy) <= 0.3
```

Notes:

- The check is over the tier's **prerequisite closure**, not just the tier's own list (`../SKILL.md` §7). Tier 3 cannot open while a concept it depends on sits at L1.
- `min_level` and `max_calibration_error` are stored per tier in `graph.yml:tiers[].gate` and are not edited to make a gate pass.
- A concept with `accuracy` unset has no observation and fails the gate at `L0`. Self-ratings do not enter the arithmetic.
- Negative calibration passes. Underconfidence is not a defect in knowledge.
- The gate is evaluated **at the exam**, for the tier being left. A pass increments `graph.yml:tier_current` by one; nothing else advances it.

**When the gate fails:**

1. Name the blocking concepts — id, level, calibration error. At most five, sorted by how badly they block.
2. Do not run a promotion exam. An exam may still be run for information; say up front that it cannot promote.
3. Set the blockers' `next_review` to today or tomorrow and run `drill`, or run `learn` on the lowest one.
4. Record the gate arithmetic in the session note, so the next session sees the same numbers rather than re-deriving them.
5. Never lower the threshold, never round a `0.31` down, never count an unobserved concept as "probably fine".

## Exam protocol and scoring

Ten questions, one at a time, before any promotion. Composition is fixed:

| Slot | Count | Target level | Question shape |
| --- | --- | --- | --- |
| foundational | 3 | L1 locate | "which part of the field, what does it answer, what does it depend on" |
| applied | 3 | L2 explain | "explain the mechanism in your own words" |
| boundary | 2 | L3 predict | "here is a case you have not seen — what happens, and does the method apply" |
| expert | 2 | L4 apply + boundary | "use it on this task, then name its limit and its cost" |

Cover at least six distinct concepts across the ten questions. Never ask ten questions about one concept; that measures one page, not a tier.

Slot labels are **difficulty**, not tiers. `foundational` / `applied` / `boundary` / `expert` do not map onto `Novice` / `Beginner` / `Practitioner` / `Adept`; a tier exam simply needs harder questions than the tier it tests.

Scoring:

- Each answer is scored **/10**, against the L0–L4 evidence for the level the slot targets.
- Record per answer: score, what was right, the exact gap, and the re-teach of that gap only.
- A weak answer (≤4/10) earns **one** follow-up. Keep the first answer as primary evidence; log the follow-up separately.
- Total is **/100**. Report strongest area, weakest area, a review plan with dates, and **five** challenge questions.
- **Promotion requires all three:** the §7 gate holds for the tier under exam; the total is at least 70 out of 100; at least one expert-slot answer scores 6 or more. Anything else is a hold. A high total built entirely from foundational questions does not promote.
- Only `exam` promotes. On promotion, write `graph.yml:tier_current`, then render the `index.yml` row and `README.md` from it (`session-loop.md` → Wrap-up). `learn` may report that the gate passes; it may not advance the tier.

Anti-inflation rules:

| Claim | Why it does not count |
| --- | --- |
| "I knew that once I saw the answer" | A prediction made after the reveal is not evidence |
| Fluent, well-structured, content-free answer | Fluent vagueness is L1–L2 |
| The right label with the wrong relation | L1; naming is not knowing |
| A correct formula with no condition | Caps at L2; it cannot be applied to a new case |
| Agreement after a hint | The hint supplied the model; not the learner's |
| Restating the page's sentence verbatim | Recall of wording, L2 at most |
| "I've spent 20 hours on this" | Hours are input; levels are output |
| Self-rating "I'm about a 4" | A prior, not a measurement |
| One good answer after three failures | Today's level is the weaker one |
| Correct outcome with a wrong causal story | L2; luck is not a model |

A failed exam is information, not a verdict. Record which slot failed, re-teach only those gaps, set reviews, and say when the next attempt is reasonable (not before the blocking concepts reach L2).

## Session-level grading

At session end, record in `sessions/YYYY-MM-DD.md` and in `graph.yml`:

- The mode, the target concept(s), and the page written or corrected — with the section changed, not "updated".
- Each concept touched and its level change (`L1 → L2`, or "unchanged, passed review").
- The strongest misconception, **verbatim**, and the section where it was corrected.
- Confidence, accuracy, and calibration error for each concept touched.
- Whether the tier gate passes, with the counts, if the tier was relevant.
- Exam result if one ran: total, per-slot weakness, decision, next attempt condition.
- The single next action, as one of the six modes plus a target id.

Then the honesty line:

> A session with no level change and no misconception recorded is usually a session where the tutor lectured. Say so in the note.

Do not invent a misconception to fill the field, and do not record a level for an answer that was never given. An empty evidence record is a true record.
