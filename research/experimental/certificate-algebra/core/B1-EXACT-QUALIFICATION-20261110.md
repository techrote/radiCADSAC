# B1 source-current full-suite qualification and E1/E2 receipt repairs — 10 November 2026

**Status: HOLD FOR INDEPENDENT ADMISSION.** This is a research-only security/contract correction, not mathematical novelty, native speed evidence, MC-038 authority, MC-B/MC-1 proof, or permission to merge.

## Exact source and runtime

Repository: `techrote/radiCADSAC`, Draft [#473](https://github.com/techrote/radiCADSAC/pull/473). Accepted main observed `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Original candidate `d6ff1922aad1ec8c17d67b06c3f373578ae3f806`; corrected code+tests `37c4c00dd06c05503772e82f52f10de0670a8c75` (the report-only successor commit does not alter tested Python files). Isolated Linux CPython 3.13.5, no native/STEP or paid runner.

The GitHub connector supplied all **20 relevant original Python sources**: nine imported B1 modules, ten published `test_*.py` modules, and `experiment.py`. Every local `git hash-object` matched the exact Git blob fetched from the published original or corrected PR head. Critical corrected blobs:

| File | Git blob at tested corrected head |
|---|---|
| `certificate_algebra.py` | `8d47787e393c7f26ff9888c02a2ac7708995a2d8` |
| `receipt_integrity.py` | `cb139bd858329bcdf7958474b012bae870eae83b` |
| `product_cone.py` | `be2ed77e835ec90db865aaaf18c16ba11ddb6ad2` |
| `closed_nonzero.py` | `319180e07fc14111bb259a990f887a010332c482` |
| `test_product_cone.py` | `76d18fef0a6af7cf8d50205e4a86d534d7d30adf` |

The remaining fifteen Python Git blob identities are retained with the raw runs in the local qualification manifest supplied with the owner-visible evidence archive, not duplicated in this report.

## Direct execution (published imported parent modules, not shadow mathematics)

From `research/experimental/certificate-algebra/core`:
```sh
python3 -m unittest -v test_base_receipt_integrity test_certificate_algebra test_closed_nonzero test_phase_bridge test_producer_codec test_product_cone test_quotient_sided_germ test_rational_quotient test_receipt_integrity test_refined_product
python3 experiment.py
```

- **Original `d6ff1922...`: 76/76 published methods PASS** in 0.628 s. Positive tests were insufficient to establish hostile E1 source/receipt authentication.
- **Original adversarial E1/E2 receipt:** three added tests **FAIL as intended** (`AssertionError: Refusal not raised`) for forged `schema`, nested `signs[0]`, and downstream `verify_closed_product`. Both original parent hashes and actual signed/positive source remain authentic.
- **Original external-source custody:** hostile `str` subclass with `__eq__=True`, `__ne__=False` was also wrongly accepted as `raw['hash']`, `left_pin`, and E2 `source_pin`/`product_pin`. An ordinary different built-in pin was refused.
- **Repaired `37c4c00...`: 82/82 published methods PASS** in 0.651 s, including six authored E1/E2 security regressions, and **3/3 extra independent falsifier methods PASS**. Combined 85/85. `python3 -m compileall -q` on all 20 published Python sources PASS.
- **Proof-work control:** `experiment.py` repeats 32-cell/64-update deterministic Python proof accounting: full-leaf checks 2080 (naive) vs 96 (incremental), seams 2015 vs 155, proof-leaf ratio `65/3`. These are work counters, **not** wall-clock net benefit.

## Minimal false-premise fixture and boundary repair

```python
class Lie(str):
    def __eq__(self, other): return True
    def __ne__(self, other): return False
    __hash__ = str.__hash__

base = base_record((Piece(Q(0), Q(1), (Q(1),)),))
state, claim, _ = product(base, base, left_pin=base['hash'], right_pin=base['hash'])
claim['signs'][0] = Lie('NEG')
verify_product(base, base, claim, left_pin=base['hash'], right_pin=base['hash'])
# ORIGINAL: incorrectly returns. CORRECTED: Refusal.
```

The actual `product_cone.verify_product` now recomputes the result and calls existing `receipt_integrity.admit(reconstructed, witness)` **before enumerating or accessing submitted witness fields**, so caller-defined equality and key callbacks cannot participate. `product_cone._parent` validates the entire external raw source before accessing keys and requires a builtin 64-lowercase-hex `str` source pin. `closed_nonzero._pin` requires builtin `str`; `verify_closed_base` validates its raw top-level `hash` in addition to base pieces/receipts. Six added original-suite methods cover subclass forgeries, nested/cyclic/oversized inputs, hostile keys, forged raw parent SHA, source/pin substitution and downstream E2 use.

**Scope:** these repairs close the reproduced in-process E1/E2 equality/pin admission holes. They do not authenticate whoever provided the external pins or the original A1/A2 producer, nor prove arbitrary adversarial Python inputs outside validated strict-primitive grammar.

## Actual A1/A2 interface and consumer relevance

Observed open Draft producer heads on 10 November 2026: A1 [#470](https://github.com/techrote/radiCADSAC/pull/470) `22f8751bf9e0fee45b6cac0f5fae16217e54fb80`; A2 [#471](https://github.com/techrote/radiCADSAC/pull/471) `d9cb56e74e876efb203e04003aadcf8bd368a369`. B1's current `phase_bridge.PRODUCERS` pins **older** A1/A2 exact revisions, and `producer_codec`'s tests use self-contained canonical JSON format fixtures. An *actual current authenticated upstream A1/A2 receipt*, independently trusted source origin, physical window, full B-spline knots/control vector provenance and #462 source-to-envelope transformation have **not** been supplied or executed. Neither a fabricated source SHA nor an equivalent locally authored envelope is acceptable as evidence. **Cross-producer admission: HOLD.** Request A3/B5 independent second-source direct test at each actual producer head, using its original verifier, native source pin and true source identity; keep unsafe or unsupported transfers typed `UNVERIFIED`.

The current consumers are **research-only Python**: exact piecewise C0 rational Bernstein cone, product, closed nonvanishing, rational quotient and sided germ contracts. No implementation is presently attached to native machining/STEP or CyberSand World/worker/Rapier. Existing [#462](https://github.com/techrote/radiCADSAC/pull/462) B-spline affine/knot contracts may be reused once independently source-typed, not presumed imported from B1. All B1 consumers replay original parents; the extra strict receipt walk costs O(receipt size), while product output conversion may be avoided. No same-host net runtime measurement or genuine producer-recomputation benchmark demonstrates **savings exceeding verification overhead**. Therefore **NO performance/production GO**.

## Decision and review

**PASS for exact Python published-suite execution and the local E1/E2 repair as scoped; HOLD for independent A3/B5 review, source ancestry, actual A1/A2 receipt, consumer adoption, native timing and merge.** No source ownership outside `research/experimental/certificate-algebra/core/**`; no production files touched, no merge/Ready/authority. Preserve historical 121/20/30/50 census, 26 operations, MC-B and MC-1 `NOT_ESTABLISHED`, and `production_authorized=false`. The highest-value next falsifier is an independently authenticated current-head A1/A2 receipt injected into the actual B1 codec and verifier, with wrong-source, same-local-germ/different-full-knots and false external-pin controls.
