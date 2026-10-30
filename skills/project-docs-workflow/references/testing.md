# Test authoring rules

Test policy for this profile — **first priority and always present**: it ships with the skill and is materialized as `docs/agents/testing.md`. The `tdd` skill (installed, or the internal fallback `deps/tdd.md`) supplies only the red → green mechanics and the seam baseline; for expectation sources, assertion strength, mock / fixture boundaries, defense layering, and change control, these rules win.

Whether a change gets tests is the agent's call, sized to risk (the user may ask for them). Once tests are written or changed, this document applies in full — it is not gated on a project declaration.

## 0. Terms

- **Must / must not** — hard; a violation makes the test deliverable unacceptable.
- **Should / should not** — default; departing requires a reason in the self-check report.
- **May** — optional.
- **SPEC ID** — stable identifier for an acceptance-relevant behavior, contract, boundary, or defense layer in the SPEC.
- **Defense layer** — the line the SPEC assigns to input validation, authorization, rate limiting, transactions, idempotency, timeouts / retries, and similar.
- **Change level** — L1 SPEC change | L2 test defect | L3 structural refactor (assertion semantics unchanged) | L0 implementation-only.

## 1. Principles

- **The SPEC is the only source of truth.** Every case traces to at least one SPEC ID. Deriving expectations from the implementation is forbidden.
- Tests come **first, or with the change**; never write them afterwards to make things green.
- **Assert observable behavior** — business values, side effects, error contracts. Private methods and internal call counts / order are off limits unless the SPEC defines them as contract.
- **Isolate context.** A test author receives only the PRD summary, the SPEC, public signatures, and defense-layer definitions. If the implementation was visible, say so and let a human check for contamination.
- **Layer the defenses.** Defensive logic is tested at its own layer. No owner for a defense case → ask, mark `defense-ownership-missing`, never invent scenarios.
- **Control change.** Changing an expectation requires a SPEC change or a test defect; L0 never justifies it.

## 2. Inputs

Required: PRD summary (naming and scenario vocabulary, never acceptance detail), SPEC entries, defense-layer definitions, public signatures, existing test conventions (layout, naming, framework, data setup).

Forbidden: "this is how the implementation does it" as a source; rules the SPEC does not define; fixtures or mocks that perform a business step on behalf of the code under test.

Ambiguity, conflict, or a gap in the SPEC → emit an open-questions list; never assume silently.

## 3. Deliverables, in order

1. **Test plan** — per SPEC entry: level, positive / negative / boundary cases, mock rationale, defense ownership, uncovered items, assumptions.
2. **Case table** — Case ID | SPEC ID | level (unit / contract / integration / E2E) | behavior in business language | Given / When / Then | data and boundary type | mocks and why | defense layer | change level.
3. **Test code** — names state behavior (`should_reject_order_when_stock_insufficient`); failure messages carry the expected and actual business value; names and messages must be readable by a non-implementer.
4. **Traceability matrix** — SPEC → Case, plus uncovered entries and their reasons.
5. **Self-check report** — commands run with their output, uncovered items, implementation-visibility declaration, suspected out-of-scope defenses.

Scale: feature and structural changes deliver all five. Bug fixes and chores may reduce to a one-line trace, strong assertions, and the self-check evidence — traceability, assertion strength, and mock rationale are never dropped.

## 4. Case design

- One behavior per case; parameterize multiple data sets of the same behavior.
- Cover, as the SPEC requires: the main path; SPEC business errors and error contracts; input boundaries (empty, whitespace, oversized, extremes, Unicode / special characters, invalid formats); state transitions, idempotency, concurrency; defense-layer interception.
- No coverage padding: no assertion-free cases, no duplicated branches, no "runs through but checks nothing".
- Parameterize dirty input the SPEC defines; if it does not define it, ask — do not invent rules.

## 5. Assertions, mocks, fixtures

- **Strong assertions**: business value, state, side effects, error code / type / contract message. Assert precision and ordering for money, time, and collections per contract.
- Forbidden: `assert result is not None`, type-only checks, truthiness-only checks. Error paths assert the concrete contract, not merely that something threw.
- **Mocks** isolate external dependencies, non-deterministic sources, or collaborations the SPEC says to isolate. Their contract comes from the SPEC or a public interface, and each carries a written reason. Do not mock private collaborators; do not assert call counts or order unless the SPEC requires it (e.g. "the idempotency key triggers exactly one refund").
- **Fixtures** prepare preconditions only and must not insert business side effects. A fixture that turns a flow that should fail green is high risk and needs human review.

## 6. Defense-specific

Each defensive case names its layer and SPEC ID. Business cases do not re-test the layers. An implementation branch the SPEC does not map → mark `suspected out-of-scope defense`; do not legitimize it with a test. Tests never demand new defensive code.

## 7. Change management

- **L1** — SPEC change; semantics and expectations may change; cite the SPEC change ID.
- **L2** — test defect; fix it and explain.
- **L3** — restructure fixtures, mock organization, parameterization; assertion semantics unchanged.
- **L0** — implementation-only; never a reason to change expectations.

A test failure after a refactor is judged on behavior: unchanged → fix the structure; changed → go back to the SPEC.

## 8. Delivery gate

- [ ] Every SPEC behavior has at least one case; uncovered items listed
- [ ] No implementation-detail assertions (private methods, call counts)
- [ ] Key assertions are strong; failure messages readable
- [ ] Every mock has a reason; no fixture completes business logic
- [ ] Defensive cases name their layer; no suspected defense masked by a new test
- [ ] Tests run independently and repeatably (no real network, wall clock, or execution order)
- [ ] Commands and output attached — "tests pass" alone is not evidence
- Mutation testing is recommended for critical modules; surviving mutants get human review.

**Human review looks at four things**: cases came from the SPEC rather than the code; assertions are strong; mocks and fixtures are not doing the implementation's job; defenses stay in their layer. Coverage is a diagnostic, never a quality verdict.
