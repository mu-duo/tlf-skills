<!-- Template: docs/teach/<user>/sessions/YYYY-MM-DD.md -->
<!-- One file per session. Replace <...>. Content is the 40-minute transcript, not a summary. -->
<!-- The next agent resumes from this file plus profile.yml; anything not written here is lost. -->

# Session <YYYY-MM-DD>

User: <slug>
Repo commit: <sha>
Stage: <orientation | skeleton | spine | structure | apply | drill>
Mode: <tour | tutor | drill>
Density: <low | normal | high>
Duration: <minutes>

## Objective

<One sentence. One stage only.>

## Resume state

- Last session: <YYYY-MM-DD or "first session">
- Concepts due for review: <ids>
- pending_explanations carried in: <count>

## Warm-up retrieval

| Concept | Question | Answer | Correct |
| --- | --- | --- | --- |
| <id> | <question> | <verbatim> | <yes/partial/no> |

## Predictions and reveals

### Prediction 1

- Question: <what you asked before revealing>
- User's answer: > <verbatim>
- Reveal: <the fact>
- Anchor: `<path:line>`
- Delta: <what was wrong, precisely>

### Prediction 2

- Question:
- User's answer: > <verbatim>
- Reveal:
- Anchor: `<path:line>`
- Delta:

## Concept updates

| id | Level before | Level after | Confidence | Accuracy | Evidence (verbatim) | next_review |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | <Lx> | <Ly> | <0.0> | <0.0> | <quote> | <YYYY-MM-DD> |

## Misconceptions found

- <verbatim belief> — corrected at `<path:line>`

## Downgrades and overload

- <signal observed> -> <response>. Mode for remainder: <...>

## Stage exit test

- Test: <the done criterion from references/curriculum.md>
- Result: <passed/failed>
- Evidence: <what the user did>

## Artifacts touched

- [ ] `profile.yml`
- [ ] `<artifact>` — <what changed>

## Next session

- Start with: <concept id and why>
- Stage: <next stage, or repeat>
- Pending: <queued explanations to schedule>
