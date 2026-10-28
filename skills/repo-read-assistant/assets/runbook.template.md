<!-- Template: docs/teach/<user>/00-runbook.md -->
<!-- Stage 1 artifact. Replace <...>. Mark every command verified (you ran it) or inferred (read from config). -->
<!-- This file has more reuse value than any diagram. Keep it executable, not narrative. -->

# Runbook: <repo>

Last verified: <YYYY-MM-DD> on <commit sha> / <OS>
Owner of truth: `<path:line>` for each command below.

## Prerequisites

| Tool | Version | Check | verified/inferred |
| --- | --- | --- | --- |
| <runtime> | <version> | `<command>` | <verified> |
| <package manager> | <version> | `<command>` | <inferred> |

## Install

```bash
<install command>
```

Anchor: `<path:line>`

## Run

```bash
<run command>
```

Expected output: <one line>
Anchor: `<path:line>`

## Test

```bash
<test command>
```

Result: <N passed / N skipped / N failed> at <sha>

## Lint / typecheck

```bash
<command>
```

## Environment

| Variable | Required | Where the value comes from |
| --- | --- | --- |
| `<VAR>` | <yes/no> | <path:line or secret store> |

## Seed data

<command or "none">

## Known traps

- <flaky test, port conflict, codegen step, ordering requirement, service that must run> — `<path:line>`

## Not yet verified

- <commands or steps that were inferred only>
