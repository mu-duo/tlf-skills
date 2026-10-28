<!-- Template: docs/teach/<user>/00-model.md -->
<!-- Brief 1 of 4. Cap: 600 words. A complete document, read in one sitting. -->
<!-- Headings follow the designer's model, not the file tree. Anchors are evidence, not a tour. -->

# Model: <repo>

> **If you read only one paragraph:** <the project, whose problem, the six-part design in miniature, and the one constraint that explains most of the shape. 4-6 sentences.>

## What this layer deliberately ignores

<!-- The simplification contract. Without it a crude model becomes a wrong model. -->

<The map, module names, failure handling, and history. This page is the design in the author's head before any file was opened.>

## 1. One sentence

<Whose problem, solved how. No adjectives, no feature list.>

## 2. Constraints

| Constraint | Evidence | What it forced |
| --- | --- | --- |
| <language / deployment / compliance / performance / team> | `<path:line>` or commit `<sha>` | <the structure it explains> |

## 3. Core loop

The lifecycle of one typical task:

1. <step> — `<path:line>` <verified/inferred>
2. <step> — `<path:line>` <verified/inferred>
3. <step> — `<path:line>` <verified/inferred>
4. <step> — `<path:line>` <verified/inferred>
5. <step> — `<path:line>` <verified/inferred>
6. <step> — `<path:line>` <verified/inferred>
7. <step> — `<path:line>` <verified/inferred>

<!-- 5 to 7 steps. More means you are describing two loops. -->

## 4. Nouns

| Entity | What it is | Relates to | Anchor |
| --- | --- | --- | --- |
| <noun> | <one sentence> | <other noun, and how> | `<path:line>` |

<!-- 5 to 8 nouns. This is where the glossary converges; do not list synonyms as separate nouns. -->

## 5. Seams

| Seam | What crosses it | Contract | Anchor |
| --- | --- | --- | --- |
| <boundary> | <data or call> | <what each side promises> | `<path:line>` |

## 6. Deliberate omissions

| Not built | Why the designer skipped it | Structure it explains |
| --- | --- | --- |
| <thing> | <constraint or bet> | <the strange-looking part> |

## After reading you should be able to answer

1. Without looking: what are the five to seven steps of a typical task?
2. Which two nouns does <entity> connect, and what passes between them?
3. Name one thing the design deliberately does not do, and the constraint that justified it.
