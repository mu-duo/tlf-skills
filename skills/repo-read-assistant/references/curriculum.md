# Curriculum

Five stages, one per session. Each stage has a runnable checklist, a grep target list, a record target, and a done test. A stage that cannot be graded is a stage that did not happen.

## Session to stage mapping

| Session | Stage | Mode allowed | Artifact written |
| --- | --- | --- | --- |
| 1 | Orientation | `tour`, `tutor` | `00-runbook.md`, `01-glossary.md`, `profile.yml`, session note |
| 2 | Skeleton | `tour`, `tutor` | `02-map.md`, session note |
| 3 | Spine | `tutor` only | `03-spine.md`, session note |
| 4 | Structure | `tutor` only | `04-architecture.md`, session note |
| 5 | Apply | `tutor` only | session note plus patch plan |
| any later | `drill` | `drill` | session note, profile update |

Skipping forward is allowed when the user already knows a stage; grade it in one question and mark it `done` with the evidence. Skipping backward is normal and not a failure.

## Stage 1 — Orientation

Goal: minimum vocabulary. The user can say what the project does, gets it running, and knows ten words the team uses.

Checklist:

1. Read `README`, `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml`, and the top-level directory listing. Nothing deeper.
2. List entrypoints: `main`, `index`, `cmd/*/main.go`, `bin/*`, `__main__.py`, server bootstrap.
3. Three-class terminology sync. Ask the user to sort ten terms into: product nouns, code nouns, infra nouns. Correct only the misplacements. This finds false friends faster than a glossary dump.
4. Get build and tests running. Run them yourself, in the repo, read-only.
5. Write `00-runbook.md` and `01-glossary.md`.

Grep targets:

```bash
rg -n "^(#|##) " README* CONTRIBUTING* 2>/dev/null
rg -n '"scripts"' -A 20 package.json
rg -n "^(def main|if __name__|func main|int main)" -g '!vendor' -g '!node_modules'
rg -n "docker-compose|docker run|make " README* docs/ 2>/dev/null
```

Record: the ten terms with `path:line` anchors and `verified`/`inferred`; the exact build/test commands and whether they passed.

Done test: the user explains the project in one sentence without reading, and the build/test commands are reproduced from the runbook, not from memory.

## Stage 2 — Skeleton

Goal: spatial sense. The user knows where things live and can name the entry point for any feature.

Checklist:

1. Build the entrypoint inventory: HTTP routes, CLI subcommands, exported symbols, queue consumers, scheduled jobs.
2. Write `02-map.md` as a HYPOTHESIS, not a fact. Mark every edge `inferred` until a hop is walked.
3. Pick the spine (see `repo-archetypes.md`) and record `focus`.
4. Ask the user to place three named features on the map before showing the correct placement.

Grep targets:

```bash
rg -n "\.(get|post|put|patch|delete)\(|@(app|router)\.(route|get|post)" -g '!node_modules'
rg -n "cobra\.Command|argparse|click\.command|clap::Command|@click"
rg -n "subscribe|consume|handler|listener|worker" -g '!node_modules' -g '!vendor'
rg -n "export (default )?(function|class|const)" src/ lib/ 2>/dev/null
```

Record: inventory table (entrypoint, kind, `path:line`, confidence), the spine choice and its justification, `focus`.

Done test: given any feature named by the user, they name the entry point. Wrong answers are recorded as `misconceptions`, not corrected silently.

## Stage 3 — Spine

Goal: temporal sense. One end-to-end chain, from ingress to the effect the user cares about.

Checklist:

1. Ask for the chain in the user's words first; that prediction is the baseline evidence.
2. Trace hop by hop. After each hop, ask "what happens next?" before revealing.
3. Write every hop as `path:line` plus one line of what it does. A hop without an anchor is a guess.
4. Note the branch that surprised the user; it is the highest-value misconception.
5. Write `03-spine.md`.

Grep targets depend on the archetype; use the table in `repo-archetypes.md`. For the generic case:

```bash
rg -n "functionName|handlerName|methodName" -g '!node_modules' -g '!vendor'
rg -n "await |\.then\(|yield |return " <the file at the current hop>
```

Record: ordered hop list, each with anchor and `verified`/`inferred`; the user's first prediction, verbatim; elapsed time to recite.

Done test: the user recites the chain from memory, in order, and can open the file for each hop. Recitation without location is L2; location without order is L1.

## Stage 4 — Structure

Goal: structural sense. Why the code is shaped this way, and what that shape costs.

Checklist:

1. Pick three abstractions the spine touched. No new abstractions.
2. For each: what problem it solves, what it replaced, what it forbids.
3. Name the trade-off and its cost in one sentence each.
4. Read the existing architecture docs first, then write `04-architecture.md` as DELTAS only.
5. One diagram maximum, and only if it carries an edge the prose cannot.

Grep targets:

```bash
rg -n "interface |abstract class |protocol |trait |type .* struct" <module dirs>
rg -n "TODO|HACK|deprecated|legacy|workaround" -g '!node_modules' -g '!vendor'
git log --oneline -20 -- <path>
```

Record: three trade-offs, each with the anchor where the constraint is visible, and the doc-delta.

Done test: the user explains three trade-offs and their costs, and can point at the code that enforces each one.

## Stage 5 — Apply

Goal: operability. The user can reason about change impact.

Checklist:

1. Take one S-sized change the user actually needs (or one they propose).
2. Ask them to name the files they would touch and the blast radius before any analysis.
3. Walk the impact: call sites, tests, migrations, config, contracts, consumers.
4. Draft a patch plan: ordered steps, verification per step, rollback.
5. Do not write the patch. This skill stops at the plan unless the user asks for implementation elsewhere.

Grep targets:

```bash
rg -n "symbolName" -g '!node_modules' -g '!vendor'
rg -n "symbolName" --type test
rg -n "tableName|env\.|config\." -g '!node_modules'
```

Record: patch plan with blast radius, and the user's pre-analysis guess versus the measured set.

Done test: files and blast radius named correctly for an S-sized change, with at least one non-obvious call site found.

## The runbook has priority

`00-runbook.md` outlives every diagram. A new engineer with a working runbook and no architecture diagram ships on day one; the reverse is not true. It must contain:

- Prerequisites with versions, and how to check them.
- Install, build, run, test, and lint commands, verbatim and verified.
- Required env vars and where their values come from.
- Seed data or fixtures.
- Known traps: flaky tests, ports, codegen steps, order-dependent setup, services that must run.

Mark each line `verified` (you ran it) or `inferred` (read from config). An inferred command is a guess with a citation.
