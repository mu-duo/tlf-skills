# Curriculum

Four briefs, coarse to fine. Each is a complete document for one layer, written to be read in one sitting. Caps are caps: if a brief will not fit, the detail belongs one layer lower, or the layer needs splitting — never more compression.

## Session to brief mapping

| Session | Brief | Mode allowed | Supporting artifacts |
| --- | --- | --- | --- |
| 1 | `00-model.md` | `tour`, `tutor` | `runbook.md`, `glossary.md`, `profile.yml`, session note |
| 2 | `01-map.md` | `tour`, `tutor` | `glossary.md` update, session note |
| 3 | `02-structure.md` | `tutor` only | `glossary.md` update, session note |
| 4 | `03-operations.md` | `tutor` only | `runbook.md` refresh, session note |
| any later | `drill` | `drill` | session note, `profile.yml` |

A brief may be skipped when the user already holds that layer: grade it with one model check and mark it `done` with the evidence. Going backward is normal and not a failure.

Every brief follows the same top-level contract:

1. One-paragraph summary, first thing on the page.
2. "What this layer deliberately ignores" — the simplification contract.
3. The body: anchored `path:line`, each claim `verified` / `inferred`, headings that follow the model rather than the file tree.
4. Three "after reading you should be able to answer" questions that test the model.

## 00-model.md — what was the designer building?

Cap: 600 words. This is the only brief normally short enough to inline in chat.

Read before writing:

- `README`, `CONTEXT.md`, `docs/product/*`, `AGENTS.md` — stated purpose.
- The oldest and newest commits, plus `git log --oneline --reverse | head -20` — what the project was before it was this.
- Manifests and runtime version pins — the shape of the constraints.
- CI, Dockerfile, deploy config — what the team could not change.

Grep targets:

```bash
rg -n "^(#|##) " README* CONTEXT* 2>/dev/null
git log --reverse --oneline | head -20
rg -n "engines|python_requires|go [0-9]|rust-version|node" package.json pyproject.toml go.mod Cargo.toml 2>/dev/null
rg -n "TODO|NOTE|HACK|for now|on purpose|by design" -g '!node_modules' -g '!vendor' | head -40
```

Section skeleton:

1. Summary paragraph.
2. What this layer deliberately ignores (usually: paths, module names, failure handling, history).
3. One sentence: whose problem, solved how.
4. Constraints table: constraint / evidence anchor / what it forced.
5. Core loop: 5-7 numbered steps for one typical task; every step anchored.
6. Nouns: 5-8 entities, what each is, how it relates to the others.
7. Seams: where the system is cut and what crosses.
8. Deliberate omissions: what the designer chose not to do, and which strange structure it explains.
9. Three questions.

Self-check question pattern (the three at the end):

- "Without looking: what are the five or six steps a typical task goes through?"
- "Which two entities does <noun> connect, and what does it pass between them?"
- "Name one thing the design deliberately does not do, and the constraint that justified it."

Done test: the user draws the core loop and the nouns on a whiteboard, in the right relations, and can say why each constraint is in the list.

Deliberately omit: file paths beyond the anchor evidence, module inventories, class lists, failure modes, commit archaeology. Paths and modules belong to `01-map.md`; failure modes and history belong to `03-operations.md`.

## 01-map.md — where does everything live?

Cap: 1500 words. The chain (formerly the "spine") belongs here.

Read before writing:

- The tree, two levels deep, plus the manifest scripts.
- Existing architecture docs and `CONTEXT.md` — reuse, then diff.
- One entrypoint per archetype in `references/repo-archetypes.md`.
- The user's `focus` answer, recorded in the profile.

Grep targets:

```bash
rg -n "\.(get|post|put|patch|delete)\(|@(app|router)\.(route|get|post)" -g '!node_modules'
rg -n "cobra\.Command|argparse|click\.command|clap::Command|@click" -g '!node_modules'
rg -n "subscribe|consume|handler|listener|worker" -g '!node_modules' -g '!vendor'
rg -n "export (default )?(function|class|const)" src/ lib/ 2>/dev/null
rg -n "^(def main|if __name__|func main|int main)" -g '!vendor' -g '!node_modules'
```

Section skeleton:

1. Summary paragraph.
2. What this layer deliberately ignores (usually: why the shapes exist, failure behaviour, history).
3. Archetype, in one line, with the signal that decided it.
4. Entrypoints table: entrypoint / kind / anchor / status.
5. Feature-to-path table: the user's named features, their entrypoint, the files on the path.
6. The chain: 5-7 hops from trigger to observable effect, each anchored.
7. Boundaries: what crosses each one, and in what shape.
8. Focus and fallback: what the user said they will change first, and whether that path is peripheral.
9. Not in scope: packages or features deliberately excluded.
10. Corrections: wrong first guesses, kept as evidence.
11. Three questions.

Self-check question pattern:

- "For <feature>, name the entry point and the three files on its path."
- "Where does the data change shape on the chain, and what is it before and after?"
- "Which boundary would you cross to add <extension>, and what contract must you honour?"

Done test: given any feature the user names, they name the entry point and the path, and can place the chain on a blank page.

Deliberately omit: abstraction rationale, trade-offs, incident history, full symbol inventories. The map is spatial, not explanatory. A map of every file is a table of contents, not a model.

## 02-structure.md — why is it shaped this way?

Cap: 2500 words. The densest brief; still under 15 minutes of reading.

Read before writing:

- The abstractions the chain touched. No new abstractions.
- Existing architecture docs first, so the brief is a delta.
- Tests around those abstractions: they encode the contract.
- Interface and schema definitions; type boundaries.

Grep targets:

```bash
rg -n "interface |abstract class |protocol |trait |type .* struct|type .* = " <module dirs>
rg -n "TODO|HACK|deprecated|legacy|workaround" -g '!node_modules' -g '!vendor'
git log --oneline -20 -- <path>
rg -n "<symbolName>" --type test
```

Section skeleton:

1. Summary paragraph.
2. What this layer deliberately ignores (usually: runtime operations, incident history, exhaustive symbol coverage).
3. Abstractions table: abstraction / problem it solves / what it replaced / what it forbids / anchor.
4. Data shape: the central types and how data transforms across the chain.
5. Contracts: what each seam promises and what breaks the promise.
6. Extension points: where the design expects change, and the intended way to change it.
7. Trade-offs table: choice / obvious alternative / why not / what it costs / anchor.
8. At most one diagram, only if it carries an edge prose cannot.
9. Three questions.

Self-check question pattern:

- "Why is <abstraction> separate from its caller, and what would get worse if it were merged?"
- "Which contract does <seam> enforce, and what is the failure if a caller violates it?"
- "State one trade-off and its cost, with the code that makes it real."

Done test: the user explains three abstractions and their contracts, names the data shape at each boundary, and defends one trade-off including its cost.

Deliberately omit: line-by-line walkthroughs, exhaustive exported-symbol lists, long code blocks. Three short blocks maximum for the whole brief.

## 03-operations.md — when does it break?

Cap: 2000 words.

Read before writing:

- Error paths, retries, timeouts, and the places that swallow exceptions.
- Logging, metrics, health checks, and alert definitions.
- `git log` for the last few fixes and rollbacks; issue tracker if present.
- The runbook commands, run again if the environment allows.

Grep targets:

```bash
rg -n "catch|except|rescue|recover\(|on error|retry|timeout|circuit" -g '!node_modules' -g '!vendor'
rg -n "logger|log\.|metrics|health|readyz|livez|alert" -g '!node_modules' -g '!vendor'
git log --oneline -30 --grep="fix\|revert\|hotfix\|rollback"
rg -n "TODO|FIXME|HACK|known issue" -g '!node_modules' -g '!vendor'
```

Section skeleton:

1. Summary paragraph.
2. What this layer deliberately ignores (usually: architecture rationale already covered, full runbook duplication).
3. Failure paths table: failure / symptom the user sees / how it is detected / anchor.
4. Degradation and recovery: what protects the system, and what that protection costs.
5. History: two or three commits or incidents that explain current shape; anchored.
6. Operational trade-offs: what is fast to fix versus correct to fix; known traps.
7. Link to `runbook.md` rather than repeating it.
8. Three questions.

Self-check question pattern:

- "A request fails at <hop>. What does the user see first, and which log line tells you where it stopped?"
- "What breaks if <dependency> is slow rather than down?"
- "Name one historical fix that still constrains the design, and what it prevents."

Done test: the user names the first failure they would investigate for a given symptom, the detection point, and one trade-off they would not undo.

Deliberately omit: a second copy of the runbook, exhaustive error-code lists, generic advice ("add monitoring"). Every line must be about this repo.

## When an existing doc already covers this layer

A large architecture note, a `docs/product/02-architecture.md`, or a good `CONTEXT.md` may already own a layer. Do not rewrite it.

1. **Reuse:** link it from the brief and quote the one paragraph that carries the layer.
2. **Diff:** list what the doc gets right, what it misses, and what is stale against the current commit.
3. **Delta only:** write the missing layer, or the delta, under a heading that says so. Start with an explicit line:

   > This brief extends `docs/product/02-architecture.md`; it does not replace it. Stale after commit `<sha>`.

4. **Never duplicate.** If the existing doc is correct and complete for that layer, the brief may be a short pointer with the three questions. That is a valid brief, not a missing one.

## The runbook has priority

`runbook.md` outlives every brief. A new engineer with a working runbook and no architecture diagram ships on day one; the reverse is not true. It must contain:

- Prerequisites with versions, and how to check them.
- Install, build, run, test, and lint commands, verbatim and verified.
- Required env vars and where their values come from.
- Seed data or fixtures.
- Known traps: flaky tests, ports, codegen steps, order-dependent setup, services that must run.

Mark each line `verified` (you ran it) or `inferred` (read from config). An inferred command is a guess with a citation.
