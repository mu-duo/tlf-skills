<!-- Template: docs/teach/<user>/sessions/YYYY-MM-DD.md -->
<!-- One file per session. Replace <...>. Content is what happened, not a summary of the brief. -->
<!-- The next agent resumes from this file plus profile.yml; anything not written here is lost. -->

# Session <YYYY-MM-DD>

User: <slug>
Repo commit: <sha>
Brief: <00-model | 01-map | 02-structure | 03-operations | drill>
Mode: <tour | tutor | drill>
Duration: <minutes>

## Why this brief

<One sentence: what the previous session left unresolved and why this layer comes next.>

## Resume state

- Last session: <YYYY-MM-DD or "first session">
- Concepts due for review: <ids>
- pending_explanations carried in: <count>

## The brief

- Path: `docs/teach/<user>/<file>.md`
- Written as: <new document | delta against <doc>>
- Length: <word count> against cap <cap>
- Deliberately ignores: <the simplification contract, verbatim from the brief>

## Handover

- Why this layer: <one sentence>
- One question to hold while reading: <verbatim>

## Model check after reading

### 1. Locate

- Question: <feature or term>
- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

### 2. Predict impact

- Question: <change and its consequences>
- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

### 3. Explain why, and why not

- Question: <design choice, alternative, and cost>
- User's answer: > <verbatim>
- Verdict: <correct / partial / wrong>

## Corrections made to the brief

| Section | What the user's model had | What the brief now says | Anchor |
| --- | --- | --- | --- |
| <heading> | <wrong relation or fact> | <corrected sentence> | `<path:line>` |

<!-- Edit at the exact point of error. Do not append a new essay. -->

## Concept updates

| id | Level before | Level after | Confidence | Accuracy | Evidence (verbatim) | next_review |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | <Lx> | <Ly> | <0.0> | <0.0> | <quote> | <YYYY-MM-DD> |

## Misconceptions found

- <verbatim belief> — corrected at `<brief section>` / `<path:line>`

## Downgrades and overload

- <signal observed> -> <response>. Mode for remainder: <...>

## Whiteboard test

- Drawn from memory: <the six parts or the loop and nouns>
- Missing or wrong: <what was absent>
- Result: <passed / failed>

## Artifacts touched

- [ ] `profile.yml`
- [ ] `<brief>` — <what changed>
- [ ] `runbook.md` / `glossary.md` — <what changed>

## Next session

- Next brief: <which, and why>
- Start with: <concept id and why>
- Pending: <queued explanations to schedule>
