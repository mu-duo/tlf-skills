<!-- Template: docs/teach/<user>/03-spine.md -->
<!-- Stage 3 artifact. Replace <...>. One chain only. Every hop needs path:line and a status. -->
<!-- A hop without an anchor is a guess; label it inferred. -->

# Spine: <chain name>

Focus: <user's stated focus>
Trigger: <request / command / event>
Effect: <what the user observes at the end>
Repo commit: <sha>

## The chain

| # | Hop | What happens | Anchor | Status |
| --- | --- | --- | --- | --- |
| 1 | <entrypoint> | <one line> | `<path:line>` | <verified/inferred> |
| 2 | <module> | <one line> | `<path:line>` | <verified/inferred> |
| 3 | <module> | <one line> | `<path:line>` | <verified/inferred> |
| 4 | <module> | <one line> | `<path:line>` | <verified/inferred> |
| 5 | <effect> | <one line> | `<path:line>` | <verified/inferred> |

## Branch points

<!-- Places where the chain could go another way. These are the highest-value questions. -->

- At `<path:line>`: <condition> leads to <other path>. Not walked yet.

## User's first prediction

> <verbatim quote of what the user expected before the trace>

Delta: <what they got wrong, in one sentence>

## Recitation check

- Date: <YYYY-MM-DD>
- Order correct: <yes/no>
- All hops located: <yes/no>
- Time: <seconds>

## Open gaps

- <hop that remains inferred>
