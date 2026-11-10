# B1-D3 — E3/E4/E5 parent-ingress qualification, 10 November 2026

**Status:** PASS WITH LIMITED GRAMMAR for the corrected B1 Python research checker; **HOLD** on A1/A2 cross-producer admission, physical source ancestry, native/STEP benefit, independent B5/A3 acceptance, Ready and merge. This is not MC-038 or production authority.

## Source identities and test provenance

- Repository: [radiCADSAC](https://github.com/techrote/radiCADSAC); existing B1 [Draft PR #473](https://github.com/techrote/radiCADSAC/pull/473).
- Accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Exact pre-change B1 Draft head: `f2ab6f5d8647b6ce8ed7a4bb04b4e5aecc2e77ea`.
- Repair commit: `f9ed6c3b8b01d492515328794b00412e030649ce`. Regression commit: `621a04c788060623ed69c1471a66440b755a8d1d`.
- Exact corrected blobs: `refined_product.py=e508b3fa4a18b3620364528cb6b535d8d20dcfc9`, `test_refined_product.py=6f772015776ce7cbf0a05628099f2855398bc26c`; old blobs `5641e50b742eab14789c60d075eb020acfa45e2b` and `31275a644561d63262f6b7276efb5990f87b2e6a`, respectively.
- Complete **20/20** published B1 Python modules were fetched at the final code head and compared with `git hash-object` in a disposable local copy. The other 18 blobs are unchanged from the prior [B1 producer-codec qualification](B1-PRODUCER-CODEC-QUALIFICATION-20261110.md). No parent modules were substituted or mocked.
- CPython 3.13.5, Linux; Python standard library. The native/STEP runtime and independent host are **NOT EXECUTED**.

## Reproducible falsifier and scoped repair

The old [E3 `refined_product._parent`](refined_product.py) checked `set(raw)` and indexed `raw['hash']`, `raw['pieces']`, or `raw['receipts']` before primitive admission. An attacker can replace one genuine builtin source-map key with a Python `str` subclass whose actual text is `noncanonical-source-key` but whose `__hash__` and `__eq__` impersonate the removed key. Thus the Python map has no genuine builtin field, yet the original real E3 consumer accepted it. E4 rational quotient and E5 quotient-sided germ both transitively use this same parent path, and accepted all three key substitutions.

**Before repair:** original complete published `python3 -m unittest discover -s . -p 'test_*.py' -v` => **85/85 PASS**, exit 0. The new source-current published regression against the original module fails in three subtests (`AssertionError: Refusal not raised`), exit 1. A separate executable source-faithful real-consumer negative probe confirms **9/9 incorrect admissions** (E3/E4/E5 × three impersonated keys), exit 0 under an explicitly vulnerable-case expectation. Valid original E3/E4/E5 positive controls pass.

**Repair:** import and invoke the already accepted `receipt_integrity.validate(raw)` at the **start** of the shared E3 `_parent`, before any dictionary membership, equality, indexing, hashing or proof reconstruction. This requires exact builtin primitive keys/values and enforces bounded depth, node count and string/integer size. Do not duplicate consumer-specific validators.

**After repair:** exact corrected 20-file suite **86/86 PASS**, exit 0; the same nine actual E3/E4/E5 attacks **9/9 REFUSED**, valid three-consumer positive controls retained; malformed cyclic and oversized source structures refused; Python compilation and deterministic `experiment.py` exit 0. Only two B1-owned Python files changed, plus this additive report. No production, native, A1/A2/A3/B4/B5, frozen registry, or MC-1 authority edits.

For source-reproducible verification from the B1 core directory:

```sh
git checkout --detach 621a04c788060623ed69c1471a66440b755a8d1d
git hash-object refined_product.py test_refined_product.py
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 experiment.py
python3 -m compileall -q .
```

## What this does and does not establish

The new **canonical source-grammar** counterexample retains correctly pinned original B1 snapshot content and thus attacks the in-process verification boundary, not SHA-256 collision resistance. It does **not** forge independently held source hashes, authenticate producer identities or demonstrate wrong polynomial zero sets. The research closure and source-local conservation proofs remain conditional on verified parents.

The deterministic 32-piece/64-update experiment continues to count **2,080 naive vs 96 incremental full-leaf checks** (21.67× fewer leaf proof checks). It does *not* include the new validator, all hashing, allocations, wall-clock runtime or any native/STEP consumer: **net performance savings UNMEASURED and not justified for adoption**.

Current producer heads checked in this cycle: A1 #470 `c2f318215678951961f372866087e425a34e0609`; A2 #471 `d9cb56e74e876efb203e04003aadcf8bd368a369`. B1's accepted A1/A2 revision declarations are historical; its older actual A1 source-to-event replay does not authenticate either **current** producer, physical B-spline controls/knots or source-to-window custody. **Current A1/A2 independent live receipt re-execution is NOT DONE.** Require a real producer-imported receipt, its exact canonical source, a second-source exact-head verifier execution, and externally witnessed source/window pins; do not silently repin old adapters.

**Requested independent closure:** A3/B5 run all current 86 B1 tests with original imports at the code head, inject hostile source-map keys into the real E3/E4/E5 consumers and confirm fail-closed behavior; independently qualify current A1/A2 receipt provenance and confirm physical source-knot custody before any additive research merge. MC-B/MC-1 remain `NOT_ESTABLISHED`, `production_authorized=false`; historical 121/20/30/50 census and 26 machining operations remain untouched.
