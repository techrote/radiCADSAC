# MC-045 — Unambiguous permit/plan JSON ingress (2026-11-05)

**Status:** bounded source-level admission correction proposed for independent exact-head review. **Evidence class:** deterministic contract/negative test only; **not** native geometry or manufacturing qualification.

## Authority and ownership

- Parent issue: [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107); proof lane separately owns [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100).
- Starting authoritative main: `cbd6de3139fba117a6475da16fef0873e4e70889`.
- Branch: `fix/mc045-unambiguous-json-ingress-20261105`.
- Scoped writes: this Markdown and `research/machining-completeness/tasks/MC-045/campaign_harness.py`; **no** authority, proof registry, programme register, frozen corpus, journal, native source, production or expensive-work changes.
- Gate status from `handoffs/current-authority.json`: MC-1 NOT_ESTABLISHED; production not authorized. PB-007 / MC-B remain open. The complete 26-operation denominator remains unchanged.

## Source-level defect

The accepted `load_json(path)` previously invoked the default Python `json.loads(path.read_text(...))`, which silently resolves repeated keys by keeping their final value. An on-disk permit could contain both `"permit_id":"A"` and `"permit_id":"B"`, or duplicated nested `tariff_basis.paid` flags. Later `validate_plan` validates only the collapsed dictionary, not the uniquely interpretable source record. Even **equal-valued** duplicate keys are not a unique authority encoding. This is a genuine admission ambiguity, not merely a formatting difference.

## Bounded implementation

`load_json` now supplies an `object_pairs_hook` that rejects duplicate keys at every object depth, a `parse_constant` hook that explicitly rejects `NaN`/`Infinity`, a top-level object check, and existing `canonical_bytes` validation at ingress for floats/unpaired Unicode surrogates. Malformed JSON and invalid Unicode are converted into `ContractError`. The loader does **not** authorize native dispatch or change permits, accounting limits, resource policy, or ledger semantics.

The MC-045 `self-test` now exercises the real `load_json` against temporary files:

| Control | Expected result |
| --- | --- |
| Canonical valid synthetic MODEL_ONLY permit | Accept unchanged |
| Canonical valid synthetic plan | Accept unchanged |
| Same-valued top-level duplicate permit ID | `ContractError` |
| Conflicting top-level duplicate permit ID | `ContractError` |
| Nested duplicate tariff paid flag | `ContractError` |
| Same-valued plan max-jobs duplicate | `ContractError` |
| Nonfinite `NaN` / `-Infinity` extensions | `ContractError` |
| Unpaired Unicode surrogate | `ContractError` |
| Top-level array / invalid syntax | `ContractError` |

Every injected duplicate must be visibly present in the raw JSON before refusal. Existing positive resource accounting and ledger/capture adversarial checks remain intact.

## Reproduction and evidence

From the repository root:

```sh
python3 -m py_compile research/machining-completeness/tasks/MC-045/campaign_harness.py
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/validate_machining_completeness.py
```

The existing Linux/Windows MC-045 single-writer and interrupted-ledger CI, the MC-047 replay suite, and static MC-1 validation provide source-matched regression checks; no workflow or infrastructure configuration is changed. Retain any failed initial runs and requalify the exact final head. The test is deterministic and does not require a native/paid permit.

## Explicit nonclaims and next prerequisites

- Rejecting ambiguous authority JSON does not attest a hostile filesystem, establish durable atomic append, verify a signed permit, or authorize campaign execution.
- No PB-007 mathematical proof, MC-B, MC-D, MC-E, MC-F, MC-1, native STEP or manufacturing claim is advanced.
- Distinct-session direct source/CI review of the final literal head, followed by guarded integration if accepted, then separately recorded merged-main CI. Owner-account `COMMENTED` review is not human `APPROVED`.
