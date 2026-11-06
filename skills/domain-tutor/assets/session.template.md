<!-- Template: <root>/<domain>/sessions/YYYY-MM-DD.md -->
<!-- One file per session, named by date. One page, not a transcript. -->
<!-- The next session resumes from graph.yml + README.md + this note; anything not written here is lost. -->
<!-- Replace <...>. Quote the learner verbatim wherever the quote is evidence. -->

# Session <YYYY-MM-DD>

Domain: `<domain-slug>`
Mode: <start | learn | drill | exam | cheat | status>
Concept(s): `<concept-id>`, `<concept-id>`
Duration: <minutes>

## Why this concept

<One sentence: what the previous session left unresolved, or which tier gate this closes, and why this concept comes next.>

## Resume state

- Last session: <YYYY-MM-DD or "first session">
- Tier before: <1-4> — <Novice|Beginner|Practitioner|Adept>
- Concepts due for review: <ids, or "none">
- Carried in: <open questions or misconceptions still live>

## The page handed over

- Path: `<root>/<domain>/concepts/<id>.md`
- Written as: <new page | delta against `<id>`>
- Length: <word count> against cap 400
- Deliberately leaves out: <the simplification contract, verbatim from the page>

## Handover

- Why this concept: <one sentence>
- One question to hold while reading: > <verbatim>

## Instant check after reading

<!-- Ask "how sure are you, 0 to 1?" in the same message as the questions, before grading. -->

### 1. Teach-back (two sentences)

- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

### 2. Locate

- Question: <where the concept sits, what it depends on>
- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

### 3. Predict

- Question: <a new case or variant, and the outcome>
- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

### 4. Explain why, and why not

- Question: <a method or relation, and its limit>
- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

<!-- Two or three questions plus the teach-back. Five minutes, not an exam. No answer revealed before the attempt. -->

## Corrections made to the page

| Section | What the learner's model had | What the page now says |
| --- | --- | --- |
| <heading> | <wrong relation or fact> | <corrected sentence> |

<!-- Edit at the exact point of error. Never append a new essay after the page. -->

## Concept updates

| id | Level before | Level after | Confidence | Accuracy | Evidence (verbatim) | next_review |
| --- | --- | --- | --- | --- | --- | --- |
| `<id>` | <Lx> | <Ly> | <0.0> | <0.0> | "<dated quote>" | <YYYY-MM-DD or null> |

<!-- Never grade above the evidence. A failed review drops one level and resets the interval. -->

## Misconceptions found

- "<verbatim belief>" — corrected at `<page section>` / `sources.md <id>`

## Artifacts touched

- [ ] `<domain>/graph.yml` — levels, evidence, `next_review`
- [ ] `<domain>/README.md` — regenerated from the graph
- [ ] `<domain>/concepts/<id>.md` — <what changed>
- [ ] `<domain>/cheatsheet.md` — <what changed, if mode was `cheat`>

## Next session

- Next mode: <learn | drill | exam | cheat | status>
- Start with: `<concept-id>` — <why>
- Due reviews: <ids or dates>
- Pending: <questions or misconceptions to revisit>
