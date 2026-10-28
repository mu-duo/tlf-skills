# Repo Archetypes

The spine is not always `main` -> handler -> service. Identify the archetype before tracing; a wrong archetype produces a chain that looks plausible and teaches the wrong mental model.

## Quick identification

| Signal in the tree | Archetype |
| --- | --- |
| `Dockerfile` + `routes/` / `handlers/` + a server bootstrap | HTTP service |
| `cmd/<name>/main.go`, `argparse`, `click`, `cobra`, `bin/` | CLI |
| `src/index.ts` exporting functions, no `main`, published `package.json` / `pyproject.toml` | Library / SDK |
| `consumers/`, `subscribers/`, `handlers/` keyed by event name, broker config | Event-driven / queue |
| Registry, `plugins/`, `providers/`, DI container wiring, `@Inject` | Plugin / DI container |
| Multiple `packages/` or `apps/` each with its own manifest | Monorepo |
| `dags/`, `jobs/`, `stages/`, `transform/`, schema files | Data pipeline |
| `.proto`, `.graphql`, schema-first dirs, `generated/`, `*_pb2.py` | Codegen-heavy |

## HTTP service

**Entrypoints:** server bootstrap (`main.go`, `app.py`, `server.ts`), route registration, middleware chain, health checks.

**One chain:** request in -> router match -> middleware -> handler -> service/use-case -> repository/DB -> response shape.

**What invalidates top-down reading:**

- Middleware registered globally and far from the route. The chain includes it even if the handler never mentions it.
- Decorators or framework magic (`@app.route`, auto-wiring) that hide the dispatch hop.
- Multiple servers in one repo (public API, admin, worker) with separate bootstraps.
- A gateway or proxy in front that rewrites paths.

Trace the middleware list before the handler. Most "why is this field missing" bugs live there.

## CLI

**Entrypoints:** `main` plus the command tree. The real entrypoint is the subcommand the user runs, not the binary.

**One chain:** argv parse -> command dispatch -> option validation -> core call -> output/exit code.

**What invalidates top-down reading:**

- A framework's command tree assembled from many files. Reading `main` shows registration, not behavior.
- Global flags or config files merged before command execution.
- Shared `RunE` / `run()` helpers that hide the real work.

Pick the subcommand closest to `focus`. A CLI "spine" that starts at argument parsing is often boring; say so and skip to the command body.

## Library / SDK

**Entrypoints:** the public surface — `index` exports, `__init__.py`, `lib.rs` re-exports, `exports` in `package.json`.

**One chain:** public call -> orchestration layer -> internal core -> side effect or returned value.

**What invalidates top-down reading:**

- The public API is a thin wrapper; the real complexity is three layers down.
- Versioned directories (`v1/`, `v2/`) where only one is live.
- Feature flags selecting alternate implementations.
- The README documents an older API than the code exports.

Start from an exported symbol the user will call, not from the directory tree.

## Event-driven / queue

**Entrypoints:** producer sites (publish/emit), consumer registrations, the broker's topic or queue names, schema definitions.

**One chain:** trigger -> publish -> broker hop -> consumer -> handler -> side effect. It is a chain with a gap in the middle; the broker is not code.

**What invalidates top-down reading:**

- There is no single call stack. Tracing with "find references" stops at the publish call.
- Topic names are strings, often built dynamically or from config. Grep the literal and the config key.
- Retries, dead-letter queues, and idempotency wrappers change the effective order.
- Multiple consumers per topic; the user cares about one.

Never guess a spine here. Ask which event and which consumer, and state that the broker hop is `inferred` unless you can see its config.

## Plugin / DI container

**Entrypoints:** the container bootstrap and the registration list. Behavior is assembled at runtime.

**One chain:** bootstrap -> registration -> resolution/injection -> plugin hook -> effect.

**What invalidates top-down reading:**

- Calling `new Foo()` finds nothing; the instance is constructed by the container.
- Interface implementation chosen by config, profile, or environment.
- Hooks invoked by name or by registry lookup, not by direct call.
- Decorators or macros that generate the wiring.

Trace registration first, then the resolved implementation. If the binding is config-dependent, record both possible implementations and mark the active one `inferred`.

## Monorepo

**Entrypoints:** the workspace manifest (`pnpm-workspace.yaml`, `turbo.json`, `go.work`, `Cargo.toml` workspace), then one package's entrypoint.

**One chain:** boundary of one package -> internal call -> dependency package -> effect. The chain crosses package lines, which is the point.

**What invalidates top-down reading:**

- Multiple apps with overlapping names; the top-level README describes only one.
- Shared packages used by everything (`common/`, `shared/`, `core/`), so "find references" returns noise.
- Build tooling that rewrites imports or aliases paths.
- Duplicate implementations in two packages, one deprecated.

Scope the map to the packages on the spine. A monorepo map of everything is a table of contents, not a mental model.

## Data pipeline

**Entrypoints:** DAG definitions, scheduler registration, job entry scripts, stage lists.

**One chain:** source read -> transform stage 1..n -> validation -> sink write.

**What invalidates top-down reading:**

- The pipeline is declared, not called; order comes from a DAG or stage list.
- Schemas are the real contract, and they live outside the code.
- Backfills and reprocessing paths differ from the normal run.
- Idempotency and partitioning logic changes what "one record" means.

Trace one record through the stages. Record the schema at each boundary; that is where drift happens.

## Codegen-heavy

**Entrypoints:** the schema (`.proto`, `.graphql`, IDL) or the generator config. Generated files are outputs, not sources.

**One chain:** schema definition -> generator -> generated type -> hand-written consumer.

**What invalidates top-down reading:**

- Generated code is checked in and looks hand-written; reading it teaches nothing durable.
- The generator adds behavior (validation, serialization) that never appears in the schema.
- Regeneration happens in a build step, so the committed output may be stale.
- Field numbers, wire formats, or reserved names carry meaning invisible in the code.

Anchor to the schema, not the generated output. Mark generated paths explicitly in the map so nobody edits them.
