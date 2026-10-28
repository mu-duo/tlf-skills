# Rubric

Levels are assigned from evidence, never from impression. If you cannot quote what the user said or did, the level is `L0`.

## How to grade L0-L4

| Level | Name | Evidence required | Typical failure |
| --- | --- | --- | --- |
| L0 | unknown | No correct statement; or no observation recorded | Confident fluent summary with no anchor |
| L1 | locate | Points at the right file, given a feature or term, without help | Right path, wrong symbol |
| L2 | explain | Describes what the code does and why, unprompted, in the right relations | Correct facts, wrong or reversed relations |
| L3 | predict | States what happens next, or what breaks, before seeing the result; correct | Prediction follows the reveal |
| L4 | apply | Plans a correct change: files, call sites, tests, blast radius | Names files but misses consumers or tests |

Grading rules:

- **One level per concept.** A concept graded L3 on the loop and L1 on retry is L1 today, with the first score kept as evidence.
- **Order and relations beat vocabulary.** Reciting names out of order, or connecting the wrong two, is L1-L2 at most.
- **Coherence caps at L2.** A correct but incoherent model — right facts, wrong relations — cannot be L3, however many facts it recites. Prediction requires a working causal model; if the arrows are wrong, the prediction is luck.
- **Anchors beat prose.** A correct explanation with no locatable anchor caps at L2.
- **Prediction comes after reading.** The user reads the brief, then predicts the impact of a change. L3 is assessed there, not as a guess made before any model exists. A prediction made after seeing the answer is not evidence.
- **Application must include blast radius.** Naming edited files is L3-level recall; L4 requires the consequences.

## Evidence records

Store the observation, not the label. A level without evidence cannot be re-graded, and the next agent inherits a claim it cannot trust.

Good:

```yaml
- id: core-loop
  canonical: core task lifecycle
  anchor: 00-model.md#3-core-loop
  level: L2
  confidence: 0.8
  accuracy: 0.6
  evidence:
    - "On the model check, listed intake -> validate -> persist -> notify correctly, but put notify before persist."
    - "Predicted changing the validator would only affect intake; missed that the notifier reads its output at src/notify.ts:88."
  misconceptions:
    - "Notification runs before persistence."
  next_review: 2026-11-01
```

Bad:

```yaml
- id: core-loop
  level: L2
  notes: "User understands the flow."
```

The bad record has no anchor, no quoted answer, no specific error, and no date. It cannot drive a drill and cannot be corrected.

More bad patterns:

| Pattern | Why it fails |
| --- | --- |
| `level: L3`, evidence: "answered well" | No prediction content; unverifiable |
| Evidence is the agent's explanation | Measures the agent, not the user |
| "Mastered" | A verdict, not an observation |
| Five concepts in one record | Cannot grade or schedule separately |
| Citing "the architecture brief" without a section | The correction cannot be located later |

## Confidence and accuracy

Both are numbers in `[0, 1]`.

- `confidence` — ask directly: "How sure are you, 0 to 1?" Record the number they say.
- `accuracy` — score the answer: correct, ordered, and relational = 1.0; correct with one broken relation = 0.5; wrong = 0.0. Average across observations for that concept.

Calibration:

```
calibration_error = confidence - accuracy
```

| Value | Reading | Action |
| --- | --- | --- |
| `> 0.3` | Overconfident | Drill first. Do not move to the next brief on this concept. |
| `0.1 .. 0.3` | Slight overconfidence | One model check next session. |
| `-0.1 .. 0.1` | Calibrated | Normal spacing. |
| `< -0.1` | Underconfident | Say so; the user knows more than they think. |

Overconfidence is the priority. An underconfident user will ask for help; an overconfident one will refactor the core loop.

Report calibration per concept, never as a single session average. One bad concept hides inside a good average.

## Review scheduling

Set `next_review` from the level after grading:

| Level | Interval | Rationale |
| --- | --- | --- |
| L0 | 1 day | Nothing to space yet; re-establish the anchor |
| L1 | 1 day | Locate decays fast without use |
| L2 | 3 days | Explanation needs one consolidation pass |
| L3 | 7 days | Prediction is more stable but still fragile |
| L4 | 21 days | Application transfers; check occasionally |

Rules:

- A failed review drops the level by one and resets the interval to the new level's value.
- A passed review at L3 or L4 may extend one step beyond the table (L3 to 14 days, L4 to 30) once; do not chain extensions.
- `drill` selects concepts with `next_review <= today`, ordered by `calibration_error` descending, then by oldest review.
- Cap a drill session at 12 concepts. Fatigue produces false negatives, and false negatives corrupt the profile.

## Session-level grading

At session end, record:

- The brief written or corrected, and its section-level changes.
- Concepts touched and their level change.
- The strongest misconception found, verbatim, and the section it was corrected in.
- Whether the brief's done test passed (`references/curriculum.md`).
- One sentence on which brief to start next session.

A session with no level change and no misconception recorded is usually a session where the agent lectured or the user only nodded. Say so in the note.
