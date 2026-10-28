<!-- Template: docs/teach/<user>/02-structure.md -->
<!-- Brief 3 of 4. Cap: 2500 words. The densest layer; still under 15 minutes of reading. -->
<!-- Every abstraction must have been touched by the chain in 01-map.md. No new abstractions. -->
<!-- At most three short code blocks for the whole brief. No symbol dumps. -->

# Structure: <repo>

> **If you read only one paragraph:** <the two or three abstractions that carry the design, the contract each enforces, and the trade-off that hurt most. 4-6 sentences.>

## What this layer deliberately ignores

<Runtime operations, incident history, and exhaustive symbol coverage. This layer explains shape and cost, not what happens at 3am.>

## Abstractions

| Abstraction | Problem it solves | What it replaced | What it forbids | Anchor |
| --- | --- | --- | --- | --- |
| <name> | <problem> | <earlier shape> | <the constraint it imposes> | `<path:line>` |

## Data shape

<The central types and how data transforms across the chain. One short block or a small table.>

```text
<type> --<transform>--> <type> --<transform>--> <type>
```

Anchor: `<path:line>`

## Contracts

| Seam | Promise | What breaks the promise | Anchor |
| --- | --- | --- | --- |
| <boundary> | <what callers rely on> | <violation> | `<path:line>` |

## Extension points

| Point | Intended way to extend | What not to do | Anchor |
| --- | --- | --- | --- |
| <hook / interface / registry> | <steps> | <the shortcut that breaks it> | `<path:line>` |

## Trade-offs

| Choice | Obvious alternative | Why not | What it costs | Anchor |
| --- | --- | --- | --- | --- |
| <choice> | <alternative> | <constraint> | <cost> | `<path:line>` |

## Diagram

<!-- At most one, and only if it carries an edge prose cannot. Delete this section otherwise. -->

```text
<boxes and arrows>
```

## After reading you should be able to answer

1. Why is <abstraction> separate from its caller, and what would get worse if it were merged?
2. Which contract does <seam> enforce, and what fails if a caller violates it?
3. State one trade-off and its cost, with the code that makes it real.
