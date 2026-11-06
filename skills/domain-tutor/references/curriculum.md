# Curriculum

Build artifacts in one order: `spine.md` → `graph.yml` → concept pages → `cheatsheet.md`. Writing a concept page before the graph is a page with no prerequisites and no place in the path; it will be rewritten or orphaned.

Caps are caps. If an artifact will not fit, the content is mis-scoped: split the concept, split the artifact, or demote detail to a lower layer. Never compress prose to fit.

## `spine.md` — the whole field, crudely

Cap: 800 words. Written once at `start`, revised only when the graph proves it wrong.

The six parts in `../SKILL.md` §5, in that order, as headings. A reader must be able to hold all six in one sitting; that is the whole test.

| # | Heading | Content | Length |
| --- | --- | --- | --- |
| 1 | One sentence | What question the field answers, for whom, by what means | 1–3 sentences |
| 2 | Boundaries | Inside / adjacent / assumed and never questioned | ≤180 words |
| 3 | Core loop | One typical practitioner task, 5–7 numbered steps, end to end | ≤200 words |
| 4 | Nouns | 5–8 entities, one line each, and the relation between them | ≤180 words |
| 5 | Seams | Where the field is cut into subfields, schools, or methods; what crosses each cut | ≤150 words |
| 6 | Deliberate omissions | What standard treatments ignore on purpose, and what looks strange because of it | ≤150 words |

Part 6 is not optional and not a disclaimer. It is the reason the field's results hold and its failures are predictable. A learner without it will apply a model outside its domain and be confidently wrong — which is worse than not knowing it.

The shipped template (`assets/spine.template.md`) renders parts 2–6 as one table each — boundaries: inside / adjacent / assumed; nouns: entity / what it is / relates to / source; seams: seam / what crosses / what each side promises; omissions: ignored / why / what looks strange — plus a closing line "What this spine flattens". The example below is prose for density; the fields are the same. Every core-loop step carries a `verified` / `inferred` marker.

### Worked example — specialty coffee brewing

Not a table of contents. No history, no equipment reviews.

**1. One sentence.** The field answers: given a fixed mass of ground coffee and water, how do you change the variables you control so that a cup is reproducible rather than lucky — for a person brewing at home or a barista dialling in a café.

**2. Boundaries.**
Inside: extraction, water chemistry, grind distribution, brew ratio, temperature, time, and the sensory judgement that closes the loop.
Adjacent: green-coffee agriculture and roasting (they set the input; this field takes the bean as given), equipment engineering, café operations.
Assumed and never questioned: that a target flavour can be described and repeated; that a refractometer or a trained palate is a valid instrument; that "better" means more even extraction, not stronger.

**3. Core loop.** (1) Fix a recipe: dose, water mass, temperature, grind setting. (2) Brew, timing the contact. (3) Measure: yield, time, and either TDS or taste. (4) Compare against the target. (5) Change **one** variable — usually grind. (6) Re-brew. (7) Record the setting that hit the target, because the next bag of beans will need it again.

**4. Nouns.** *Extraction yield* (what dissolved, as a fraction of the dose); *TDS* (concentration in the cup); *brew ratio* (dose to water); *grind distribution* (the spread of particle sizes, not the average); *water hardness/alkalinity* (what the water brings); *evenness* (the relation between the six). Relations: ratio and extraction jointly set TDS; grind shifts both rate and evenness; water chemistry changes what is extracted at all.

**5. Seams.** Immersion vs percolation (what carries the soluble material: steeped volume or flow); espresso vs filter (pressure changes the mechanism, not just the strength); sensory vs instrumental assessment (palate vs refractometer, and they disagree at the edges). What crosses each cut: the same extraction model, with different time constants.

**6. Deliberate omissions.** Caffeine pharmacology, milk and syrup, café economics, bean provenance. The strange consequence: the field talks about "balance" as if it were measurable, and it is — roughly, by two instruments that disagree by a few tenths. A learner who never sees this omission will treat a refractometer reading as ground truth.

### What to omit from the spine

- Definitions of individual concepts — those are pages.
- History, names, dates, and who invented what.
- Worked examples with numbers.
- Tool and vendor comparisons.
- Source citations beyond `[s1]`-style ids; the spine is a model, not a bibliography.
- Controversies beyond one clause in part 5; a real disagreement gets a concept node.

The spine states its own simplification. End part 6 with one line naming what the spine flattens.

## `graph.yml` — the skeleton

Machine-readable state, no prose (`artifacts.md` for the schema). Built from the spine, not from a textbook's table of contents.

### Finding nodes

Sources, in order:

1. The **nouns** (5–8) and the **core loop** steps — these are almost always nodes.
2. The **seams** — each crossing is usually a node or an edge type.
3. The user's named **capability** — decompose it into the concepts a practitioner would need, working backwards.
4. A source's chapter list as a **checklist**, not a copy. If a chapter has no node, ask whether the field ignores it or the graph is missing it.

Aim for **12–40** concepts on the first pass.

| Count | Reading |
| --- | --- |
| < 10 | Too coarse to teach; likely a single skill, not a field (`../SKILL.md` §2) |
| 12–40 | Right for a first pass |
| > 40 | A table of contents, not a model — merge siblings |

Later passes add nodes where a page split. Growth is normal; a 40-node first pass that ends at 55 after two months is healthy.

### Edge types

Four, no others. Every edge reads `from → to`.

| Type | Reads as | Affects tier | Example |
| --- | --- | --- | --- |
| `prerequisite` | "to hold `to`, you must first hold `from`" | **Yes** — the only type that does | `brew-ratio → extraction-yield` |
| `composes` | "`from` comprises `to`" (whole → part) | No | `espresso-brewing → puck-preparation` |
| `contrasts` | "`from` and `to` are alternatives or commonly confused" | No | `immersion → percolation` |
| `applies` | "`from` is applied within `to`" | No | `refractometry → dialling-in` |

Rules:

- Store a `contrasts` edge **once**. Direction: lower tier → higher tier; equal tiers → alphabetical by `from`.
- `composes` is not transitive for tier math. A part is not automatically a prerequisite; if it truly is, add the `prerequisite` edge as well and say why in the session note.
- `applies` is how methods and instruments enter the graph. It keeps them out of the prerequisite chain, where they would wrongly gate theory.
- A cycle is a modeling error, never a quirk to preserve. Merge the nodes, or demote one edge to `contrasts` / `applies`.

### Stable ids

- ASCII, kebab-case, derived from the canonical English name: `extraction-yield`, `water-alkalinity`.
- **Never rename after the first write.** A rename breaks the session notes, the evidence trail, and any link the user made by hand. Synonyms go in `aliases`.
- A genuine split creates a new id; the old id keeps its evidence and gains a `composes` or `prerequisite` edge to the new node.
- Collisions get a disambiguating suffix, not a number: `elasticity-price`, `elasticity-substitution`.

### The one-line rule

`one_line` is the concept in one sentence, ≤15 words, describing what it **does**, not what it is called.

- One relation maximum, no "and". If the line needs "and", the concept is two nodes.
- No restatement of the name: "Extraction yield — the fraction of coffee mass dissolved into the cup" is a definition; "Sets how much of the dose reaches the cup, so it fixes strength for a given ratio" is a one-liner.
- It is also the page's first line, verbatim, and the only thing a tier scan loads. Write it for scanning.

### Tier assignment

Assign by prerequisite closure, mechanically:

```
tier(c) = 1                                  if c has no prerequisite
tier(c) = min(4, max(tier(p) for p in prereqs(c)) + 1)
```

Compute this in dependency order; a concept with a tier-3 prerequisite is at least tier 4, clamped. Then check the result against the tier definitions in `../SKILL.md` §7:

| Tier | English | Check the assignment against this |
| --- | --- | --- |
| 1 | Novice | Can be taught with vocabulary and one relation |
| 2 | Beginner | Can be reproduced from a worked example |
| 3 | Practitioner | Requires choosing between methods for a new case |
| 4 | Adept | Requires boundary and cost, and is teachable to someone else |

If the arithmetic puts a concept in tier 4 but nothing about it has a boundary or a cost, it is a topic, not a concept. Split it or drop it. If a concept lands in tier 1 but cannot be explained with vocabulary alone, a prerequisite edge is missing — find it before writing the page.

Never hand-assign tiers to make the graph look balanced. The arithmetic is the contract; a four-tier graph with an empty tier 4 is honest, and a padded one is not.

`tier_current` is a different number and lives at the top of `graph.yml`: the tier the learner has been **promoted into**. It is written `1` at `start`, incremented only by a promoted `exam`, and never recomputed from concept levels. Concept `tier` values and the learner's `tier_current` legitimately drift apart — a learner can be at `tier_current: 2` while some tier 3 concepts already sit at L1 from stray reading. Never "fix" the drift by editing either field.

### Deduplication and merge

Merge when any of these is true:

- One question would answer for both.
- One is a special case of the other **and** has the same failure mode.
- They differ only by vocabulary (school terminology, translation).

Do not merge when the special case has a **different failure mode or different cost** — that difference is the reason the node exists.

Merge procedure: keep the id with more edges; move the other's id and name into `aliases`; keep the stronger `one_line`; take `max(level)` with **all** evidence retained; union `sources`; re-point edges; record the merge and its reason in the session note. Never delete evidence to tidy a graph.

## Selection algorithm

Defined once, in `session-loop.md` → `learn`. Do not improvise a different order in `learn`, `drill`, or `cheat`: the schedule is the only thing making the library a path.

Short form, in case the graph is being built and the next concept must be chosen before any page exists:

1. The tier at `graph.yml:tier_current` only. Candidates are concepts at `L0` with no evidence.
2. A candidate is ready only when every prerequisite ancestor is `L1` or above.
3. Among ready candidates, take the first in `tiers[].concepts` order — that order is curated, not alphabetical.
4. No candidates left: take the lowest-level concept in the tier (ties: highest calibration error, then earliest `next_review`).
5. Everything at `L2+` and the gate passes: recommend `exam`; do not open the next tier.

The long form, with failure handling, is normative.

## Concept page

Cap: **400 words**. One page, one concept.

```markdown
# Extraction yield

> <one_line from graph.yml, verbatim>

## What it is
2–4 sentences: the claim itself, terms defined on first use.

## Why it sits here

- Prerequisites: `brew-ratio` — what must already be in place, and why
- Dependents: `grind-distribution` — what cannot be understood until this is
- Tier: 2 (Beginner) — the milestone this concept serves

## Mechanism / rules

1. <rule> (verified)
2. <rule> (inferred)
3. <rule> (inferred)

**When it holds:** conditions; the failure when pushed past them; what using it costs. (verified)

## Worked example
One concrete case: steps and outcome, not a derivation.

## Common misconceptions
- <the belief a learner actually holds> — <what is wrong, one-sentence correction>

## Self-test
> <one question not answerable by recalling the page's wording>

## Sources
- `s1` ch. 4 — which claim this supports (verified)
- analogy to pressure drop — which claim (inferred)

<!-- Deliberately leaves out: <the simplification contract>. -->
```

`assets/concept.template.md` is the normative copy; the headings above are its headings and their order is not optional.

Hard parts:

- **Blockquote = `one_line`.** Byte-identical apart from the `>` marker. A tier scan of sixty pages depends on it.
- **Relations, not facts.** "Why it sits here" must match the `graph.yml` edges: prerequisites, dependents, tier. If a prerequisite has no page yet, write "not yet written" — do not silently drop the link.
- **"When it holds" is mandatory.** A claim with no condition cannot be used on a new case, so it cannot reach L3.
- **The closing comment is mandatory.** Progressive elaboration, not disclosure (`../SKILL.md` §6).
- **400 words is the whole page**, worked example included. One case, no derivation, max 2 formulas, and only when the relation cannot be stated in words.
- **One misconception per real belief.** Invented misconceptions are exam fodder that teaches wrong things.

### Good page (compressed)

> **Extraction yield.** *Sets how much of the dose reaches the cup, so it fixes strength for a given ratio.*
> What it is: how much of the coffee dissolved — the number that separates "strong" from "bitter".
> Mechanism: water dissolves surface compounds first, then reaches cell walls; a finer grind shortens the path but widens the spread. Yield = dissolved mass / dose. (inferred)
> When it holds: the bed is evenly wetted and the water is within the recipe's temperature band. Past ~22%, bitter compounds dominate and the model still predicts, but the cup is no longer wanted.
> Leaves out: what "bitter" is chemically, and pressure-driven flow.

### Bad page (what not to write)

> **Extraction yield.** Extraction yield is a key concept in coffee. Historically, coffee science developed through the 20th century with contributions from SCA, Lockhart, and others. There are several definitions: the SCA definition, the "brewing control chart" definition, and the refractometer-derived definition. TDS is measured with a refractometer, which uses refractive index. Many factors affect extraction: grind, temperature, time, ratio, water, agitation, pressure, basket shape. Extraction can be measured in several ways. It is important to understand extraction yield for good coffee.

Why it fails: no mechanism, no condition, no cost, no relation that can be used on a new case; history and names instead of a model; an undefined list where an arrow belongs; it teaches that knowing the vocabulary is the goal. It also exceeds the cap while containing less than the good page. Any grader reading it can only award L1.

### Deliberate omissions on a concept page

Omit: the field's history, other concepts' mechanisms, full derivations, tool reviews, exam-style worked examples, and anything already on a prerequisite page. State the omission in one line rather than pretending the page is complete.

## `cheatsheet.md` — one page

Built last, from concept pages at L1+, never from the spine alone (`session-loop.md` → `cheat`).

```markdown
# <Field> — cheat sheet

> **<one line: what this field gives you>**

## Core rules, formulas, and steps
- **<rule>** — <when it applies; one condition>
- **<step sequence>** — <the order, and where it breaks>

## One table or diagram
| <input / case> | <output / result> | <when not to use it> |
| --- | --- | --- |
| <case> | <result> | <boundary> |

## Concrete examples
1. <one-line case> — <the result, and the rule it exercises>

## Pitfalls
- <the mistake that looks correct> — <the tell, and the fix>

## Pre-use checklist
- [ ] <condition confirmed before starting>

## Quick recall
1. <question answered in one line>
```

`assets/cheatsheet.template.md` is the normative copy. Rules: one line per item; order the rules along the core loop from `spine.md`, not alphabetically; the table is built from `contrasts` / `applies` edges and is optional only if a table would carry nothing; pitfalls are recorded misconceptions, verbatim; no prose paragraphs; one printed page (treat ~45 lines as the budget). Anything that needs a paragraph belongs on a concept page.

## Fields with competing schools

The field may contain a genuine disagreement — two methods, two definitions, two traditions. Rules:

1. **One domain, one base model.** Pick the school the user's context uses; if none, pick the one the sources treat as current, and say why in one line.
2. **The disagreement is a node**, not two parallel curricula. Id like `schools-of-<x>` or `<x>-measurement-dispute`, at the tier where the disagreement first changes an answer.
3. **The other school gets an alias and one line** inside that node, plus a `contrasts` edge to the base concept — not its own page, unless it has its own prerequisites. If it does, it is a separate field and gets its own domain directory (`../SKILL.md` §3).
4. **Never exam two schools' vocabularies in one sitting.** The exam tests the base model, plus the ability to say what the other school claims and why the field currently prefers one (`sources.md` → conflict handling).
5. The node's "when it holds" section says what evidence would settle the dispute. That is the honest form of "we don't know yet".

## Deliberate omissions, by artifact

| Artifact | Leaves out on purpose | Because |
| --- | --- | --- |
| `spine.md` | concept definitions, history, numbers, tool comparisons | It is a model, not a summary |
| `graph.yml` | prose, rationale, ordering by importance | It is state; prose goes stale first |
| `concepts/<id>.md` | other concepts' mechanisms, derivations, worked exam answers | 400 words is a loading unit |
| `cheatsheet.md` | anything below L1, anything needing a paragraph | It is compressed recall |
| `sources.md` | everything past the fifth source | Curation beats collection |
| `README.md` | any fact not derivable from `graph.yml` | It is a cache |
