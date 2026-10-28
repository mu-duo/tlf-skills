<!-- Template: docs/teach/<user>/01-map.md -->
<!-- Brief 2 of 4. Cap: 1500 words. A complete document, read in one sitting. -->
<!-- The map densifies the model with addresses. It is not a table of contents. -->
<!-- The chain (the "spine") lives here. Every hop needs path:line and a status until walked. -->

# Map: <repo>

> **If you read only one paragraph:** <where work enters the system, the one chain that carries most tasks, and the three boundaries a change usually crosses. 4-6 sentences.>

## What this layer deliberately ignores

<Why the shapes exist, failure behaviour, and history. This layer answers "where", not "why" or "what if".>

## Archetype

<http-service | cli | library | event-driven | plugin-di | monorepo | data-pipeline | codegen> — signal: <the tree evidence that decided it>. See `references/repo-archetypes.md` in the skill.

## Entrypoints

| Entrypoint | Kind | Anchor | Status |
| --- | --- | --- | --- |
| <name> | <http route / cli command / export / consumer / job> | `<path:line>` | <verified/inferred> |

## Where features live

| Feature | Entry point | Files on the path |
| --- | --- | --- |
| <feature the user named> | <entrypoint> | `<path:line>`, `<path:line>` |

## The chain

Focus: <user's answer to "which part will you change first?">
Chosen chain: <name>
Why: <one sentence>
Fallback: <yes/no — if yes, say so explicitly>

| # | Hop | What happens | Anchor | Status |
| --- | --- | --- | --- | --- |
| 1 | <trigger> | <one line> | `<path:line>` | <verified/inferred> |
| 2 | <module> | <one line> | `<path:line>` | <verified/inferred> |
| 3 | <module> | <one line> | `<path:line>` | <verified/inferred> |
| 4 | <module> | <one line> | `<path:line>` | <verified/inferred> |
| 5 | <effect> | <one line> | `<path:line>` | <verified/inferred> |

```text
<trigger> -> <module> -> <module> -> <effect>
```

Every arrow is `inferred` until the hop is walked. Label generated files; nobody edits them.

## Boundaries

| Boundary | What crosses it | Data shape | Anchor | Status |
| --- | --- | --- | --- | --- |
| <api / db / queue / filesystem> | <call or payload> | <before -> after> | `<path:line>` | <verified/inferred> |

## Not in scope

- <packages or features deliberately excluded, and why>

## Corrections

<!-- Wrong first guesses are evidence: they predict where the reader will get lost. Keep them. -->

- <guess> was wrong; actual is <...>. Anchor: `<path:line>`

## After reading you should be able to answer

1. For <feature>, what is the entry point and the three files on its path?
2. Where does the data change shape on the chain, and what is it before and after?
3. Which boundary would you cross to add <extension>, and what contract must you honour?
