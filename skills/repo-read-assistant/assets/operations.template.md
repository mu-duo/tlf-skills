<!-- Template: docs/teach/<user>/03-operations.md -->
<!-- Brief 4 of 4. Cap: 2000 words. A complete document, read in one sitting. -->
<!-- Link runbook.md; do not duplicate it. Every failure path must be specific to this repo. -->

# Operations: <repo>

> **If you read only one paragraph:** <the three failures most likely to hit a newcomer, how each is detected, and the one historical fix that still constrains the design. 4-6 sentences.>

## What this layer deliberately ignores

<Architecture rationale already covered in 02-structure.md, and the full command reference. This layer is about breakage, detection, and history.>

## Failure paths

| Failure | What the user sees | How it is detected | Anchor |
| --- | --- | --- | --- |
| <failure> | <symptom> | <log, metric, alert, exit code> | `<path:line>` |

## Degradation and recovery

| Protection | What it covers | What it costs | Anchor |
| --- | --- | --- | --- |
| <retry / timeout / queue / circuit> | <failure class> | <latency, complexity, hidden failure> | `<path:line>` |

## History

| Change | Commit | What it still constrains |
| --- | --- | --- |
| <fix or rollback> | `<sha>` | <the structure or rule it left behind> |

## Operational trade-offs

| Situation | Fast fix | Correct fix | Why it stays this way |
| --- | --- | --- | --- |
| <scenario> | <action> | <action> | <constraint or cost> |

## Runbook

Commands, env vars, and traps: `runbook.md`. This brief does not repeat them.

## After reading you should be able to answer

1. A request fails at <hop>. What does the user see first, and which log line tells you where it stopped?
2. What breaks if <dependency> is slow rather than down?
3. Name one historical fix that still constrains the design, and what it prevents.
