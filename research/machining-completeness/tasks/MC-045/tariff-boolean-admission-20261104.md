# MC-045 — exact Boolean tariff-admission contract (4 November 2026)

> Evidence class: **DETERMINISTIC_MODEL / source-contract only**. No native or paid dispatch was performed. This research increment is not an accepted MC-045 campaign, MC-F gate or MC-1 capability.

## Authority, scope and independence

- Source base: `main=c6518151c27ebd183972599bc29852876d53bab6`, after the independent MC-047 #379 integration. Source entrypoint: `campaign_harness.py` (initial base blob `680ef4fb0f968fe0f4c472d8c3e0769e7d6dfbb8`).
- Owner: MC-045, issue #107; isolated branch `fix/mc045-tariff-boolean-20261104`.
- Precise changed behavior: `validate_permit` requires **both** `tariff_basis.paid` and `tariff_basis.verified_current` to exist with exact Python `bool` type (canonical JSON booleans). Reject any malformed/omitted flags with `ContractError`, even for model-only plans. Paid permits require explicitly `verified_current: true`; paid tariff is rejected for `MODEL_ONLY`.
- Unchanged: permit/plan bindings, budget/accounting, terminal evidence, ledger replay/capture digest, explicit `allow_native` opt-in, stop policy and all supported operation scope. No shared programme, proof, frozen audit, current-authority or MC-038 #100 modifications.

## Source-level defect and falsification

The pre-repair code distinguished `paid` only using `is True` and `is False`, so omitted `paid`, `paid: 0`, and `paid: 1` matched neither branch. Both tariff requirements could be evaded. Meanwhile `verified_current not in {True, False}` relied on Python equality: `0 == False` and `1 == True`. Integer or malformed tariff flags were therefore able to reach an admitted plan despite the purported explicit tariff authority.

**Adversarial contract controls:** in the existing self-test, separately mutate *each* flag to `null`, `0`, `1`, `-1`, `"false"`, `"true"`, `[]`, `{}` and `[false]`; test missing flags, non-object tariff basis, and `paid: true, verified_current: true` paired with `MODEL_ONLY`. All must raise `ContractError`. Also exercise free/model positive controls with `verified_current: false` and `verified_current: true`.

The tested values deliberately distinguish Python's `bool` subclassing of `int`, JSON numeric coercion and false-similar text. The tests stay in the existing MC-045 `self-test` command, so a separate second implementation or mock validator cannot accidentally pass instead of the production admission function.

## Reproduction and CI acceptance

```sh
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 tools/validate_machining_completeness.py --self-test
python3 -m py_compile research/machining-completeness/tasks/MC-045/campaign_harness.py
```

The already-landed `mc1-mc047-replay-preflight.yml` workflow explicitly watches MC-045's `campaign_harness.py`, verifies the checkout's **literal PR head**, executes the MC-045 original self-test, the MC-047 fault matrix and the MC-1 registry self-test. It is intentionally reused rather than adding a duplicate workflow. MC-1 static CI is separately required. Record exact run SHA and results in the PR; this document does not claim CI results before execution.

## Negative evidence, limits and next prerequisites

- Before-fix source defect: absent/numeric `paid` bypass; numeric `verified_current` may be admitted due to Python Boolean equality.
- Source contract is only a static admission invariant: it does **not** attest to the reality of a provider tariff, guarantee payer permission or native cost accounting, or authorize an execution. A syntactically valid reviewed-looking string is not actual permission.
- MC-041 native capability, MC-046 actual genuine-geometry scale and MC-047 Windows/Linux native recovery remain unestablished; PB-007-01–04, MC-B and MC-1 remain open/not established. All 26 supported operations remain in scope and production creation remains separately unauthorized.
- Integration requires a subsequent distinct-session review of the exact final head, terminal applicable CI, a guarded merge and independent merged-main CI. Preserve any red CI or review findings rather than discounting them.
