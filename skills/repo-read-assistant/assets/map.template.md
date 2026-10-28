<!-- Template: docs/teach/<user>/02-map.md -->
<!-- Stage 2 artifact. Replace <...>. Write the map as a HYPOTHESIS; promote edges to verified only after walking them. -->
<!-- Scope to the spine. A map of the whole tree is a table of contents. -->

# Map: <repo>

Hypothesis status: <draft | partially verified | verified on spine>
Archetype: <http-service | cli | library | event-driven | plugin-di | monorepo | data-pipeline | codegen>

## Entrypoints

| Entrypoint | Kind | Anchor | Confidence |
| --- | --- | --- | --- |
| <name> | <http route / cli command / export / consumer / job> | `<path:line>` | <verified/inferred> |

## Boundaries

| Boundary | What crosses it | Anchor | Confidence |
| --- | --- | --- | --- |
| <api / db / queue / filesystem> | <data shape> | `<path:line>` | <verified/inferred> |

## Spine

Focus: <user's answer to "which part will you change first?">
Chosen spine: <name>
Why: <one sentence>
Fallback: <yes/no — if yes, say so explicitly>

## Edges

```text
<entrypoint> -> <module> -> <module> -> <effect>
```

Every arrow above is `inferred` until Stage 3 walks it.

## Not in scope

- <packages or features deliberately excluded, and why>

## Corrections

<!-- Wrong guesses made while building the map. Keep them; they predict where the user will get lost. -->

- <guess> was wrong; actual is <...>. Anchor: `<path:line>`
