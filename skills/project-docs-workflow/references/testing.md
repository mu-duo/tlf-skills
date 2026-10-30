# Test authoring rules

Test policy for this profile — **first priority and always present**: it ships with the skill and is materialized as `docs/agents/testing.md`. The `tdd` skill (installed, or the internal fallback `deps/tdd.md`) supplies only the red → green mechanics and the seam baseline; for expectation sources, assertion strength, mock / fixture boundaries, defense layering, and change control, these rules win.

Whether a change gets tests is the agent's call, sized to risk (the user may ask for them). Once any test activity happens, this document applies in full — it is not gated on a project declaration.

## 0. Terms

- **Must / must not** — hard; a violation makes the test deliverable unacceptable.
- **Should / should not** — default; departing requires a reason in the self-check report.
- **May** — optional.
- **SPEC ID** — stable identifier for an acceptance-relevant behavior, contract, boundary, or defense layer in the SPEC.
- **Defense layer** — the line the SPEC assigns to input validation, authorization, rate limiting, transactions, idempotency, timeouts / retries, and similar.
- **Change level** — L1 SPEC change | L2 test defect | L3 structural refactor (assertion semantics unchanged) | L0 implementation-only.
- **Temporary test** — written by the agent to verify the current change; never committed, deleted at wrap-up.
- **Persistent test** — committed to the repository; long-lived regression protection.

## 1. Three test activities

| Activity | Purpose | Committed | Required output | Traceability |
| :--- | :--- | :--- | :--- | :--- |
| **Run** | show existing behavior was not broken | no | command + result + skipped / gaps | none |
| **Temporary** | verify new behavior during development | no | scenario + strong assertions + result; deleted at wrap-up | none |
| **Persistent** | durable regression protection | yes | plan / case table / matrix / self-check (§4), tiered | a SPEC ID, else the issue's completion criteria marked `pending SPEC write-back` |

- Validity rules (§6, §7) bind all three activities. The tiers differ in **paperwork**, never in standard.
- A temporary test is not acceptance evidence: report it as "development self-check (temporary)". Current may record confidence as `tested (one-off)`; it never counts as regression coverage.
- Temporary tests live in the project's declared scratch path (default `tmp/`, gitignored) and are deleted at wrap-up. Never let one reach a commit, and never leave one sitting in the real test directories.
- **Bug fixes**: by default land at least one regression case for the defect (the reduced tier is enough). If landing it is not worth it, temporary evidence alone is allowed — but `## 测试` must state why. Not applicable when the project declares no test surface.

## 2. Principles

- **The SPEC is the only source of truth** for persistent tests. Every case traces to at least one SPEC ID, or — when none exists — to the issue's completion criteria, marked `pending SPEC write-back`. Deriving expectations from the implementation is forbidden.
- Persistent and temporary tests alike come **first, or with the change**; never write them afterwards to make things green.
- **Assert observable behavior** — business values, side effects, error contracts. Private methods and internal call counts / order are off limits unless the SPEC defines them as contract.
- **Isolate context.** A test author receives only the PRD summary, the SPEC, public signatures, and defense-layer definitions. If the implementation was visible, say so and let a human check for contamination.
- **Layer the defenses.** Defensive logic is tested at its own layer. No owner for a defense case → ask, mark `defense-ownership-missing`, never invent scenarios.
- **Control change.** Changing a persistent expectation requires a SPEC change or a test defect; L0 never justifies it.

## 3. Inputs

Required: PRD summary (naming and scenario vocabulary, never acceptance detail), SPEC entries, defense-layer definitions, public signatures, existing test conventions (layout, naming, framework, data setup), the project's test entry command, and its scratch path.

Forbidden: "this is how the implementation does it" as a source; rules the SPEC does not define; fixtures or mocks that perform a business step on behalf of the code under test.

Ambiguity, conflict, or a gap in the SPEC → emit an open-questions list; never assume silently.

## 4. Deliverables

**Every bug / feature / chore issue carries a `## 测试` section** — absence reads as "no account given". (A `suggestion` is not a work issue; it has no test section.) Three fixed slots:

```markdown
## 测试
- 执行：<command> → pass | skipped N (why)
- 临时：<scenario> → pass, cleaned up | none
- 落盘：<case> ↔ <SPEC ID / completion criterion> (none)
```

Then:

1. **Persistent — plan** (per SPEC entry): level, positive / negative / boundary cases, mock rationale, defense ownership, uncovered items, assumptions.
2. **Persistent — case table**: Case ID | SPEC ID | level (unit / contract / integration / E2E) | behavior in business language | Given / When / Then | data and boundary type | mocks and why | defense layer | change level.
3. **Persistent — test code**: names state behavior (`should_reject_order_when_stock_insufficient`); failure messages carry the expected and actual business value; names and messages must be readable by a non-implementer.
4. **Persistent — traceability matrix**: SPEC → Case, plus uncovered entries and their reasons.
5. **Persistent — self-check report**: commands run with output, uncovered items, implementation-visibility declaration, suspected out-of-scope defenses.

Tiering: feature and structural changes deliver all five. Bug fixes and chores reduce to a one-line trace, strong assertions, and the self-check evidence — traceability, assertion strength, and mock rationale are never dropped. Temporary activity needs only its `## 测试` line; running existing tests needs only the execution line.

## 5. Case design (persistent)

- One behavior per case; parameterize multiple data sets of the same behavior.
- Cover, as the SPEC requires: the main path; SPEC business errors and error contracts; input boundaries (empty, whitespace, oversized, extremes, Unicode / special characters, invalid formats); state transitions, idempotency, concurrency; defense-layer interception.
- No coverage padding: no assertion-free cases, no duplicated branches, no "runs through but checks nothing".
- Parameterize dirty input the SPEC defines; if it does not define it, ask — do not invent rules.

## 6. Assertions, mocks, fixtures (all activities)

- **Strong assertions**: business value, state, side effects, error code / type / contract message. Assert precision and ordering for money, time, and collections per contract.
- Forbidden: `assert result is not None`, type-only checks, truthiness-only checks. Error paths assert the concrete contract, not merely that something threw.
- **Mocks** isolate external dependencies, non-deterministic sources, or collaborations the SPEC says to isolate. Their contract comes from the SPEC or a public interface, and each carries a written reason. Do not mock private collaborators; do not assert call counts or order unless the SPEC requires it (e.g. "the idempotency key triggers exactly one refund").
- **Fixtures** prepare preconditions only and must not insert business side effects. A fixture that turns a flow that should fail green is high risk and needs human review.

## 7. Defense-specific

Each defensive case names its layer and SPEC ID. Business cases do not re-test the layers. An implementation branch the SPEC does not map → mark `suspected out-of-scope defense`; do not legitimize it with a test. Tests never demand new defensive code.

## 8. Change management (persistent)

- **L1** — SPEC change; semantics and expectations may change; cite the SPEC change ID.
- **L2** — test defect; fix it and explain.
- **L3** — restructure fixtures, mock organization, parameterization; assertion semantics unchanged.
- **L0** — implementation-only; never a reason to change expectations.

A test failure after a refactor is judged on behavior: unchanged → fix the structure; changed → go back to the SPEC.

## 9. Delivery gate

- [ ] `## 测试` filled for the issue: execution evidence, temporary outcome, persistent trace (or "none" + why)
- [ ] Every SPEC behavior has at least one persistent case, or the gap is listed
- [ ] No implementation-detail assertions (private methods, call counts) in any activity
- [ ] Key assertions are strong; failure messages readable
- [ ] Every mock has a reason; no fixture completes business logic
- [ ] Defensive cases name their layer; no suspected defense masked by a new test
- [ ] Temporary tests deleted; `git status` clean of scratch files
- [ ] Bug fix: a landed regression case, or the `## 测试` reason for not landing one
- [ ] Tests run independently and repeatably (no real network, wall clock, or execution order)
- [ ] Commands and output attached — "tests pass" alone is not evidence
- Mutation testing is recommended for critical modules; surviving mutants get human review.

**Human review looks at four things**: cases came from the SPEC rather than the code; assertions are strong; mocks and fixtures are not doing the implementation's job; defenses stay in their layer. Coverage is a diagnostic, never a quality verdict.
