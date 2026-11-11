# B1-D2 producer source grammar — exact-current-head qualification (10 Nov 2026)

**Disposition:** PASS WITH LIMITED GRAMMAR for corrected Python research implementation; **HOLD** for externally authenticated A1/A2 receipts, MC-038 B-spline ancestry, second-source review, net native benefit and merge.

## Exact source identity and qualification

- Repository `techrote/radiCADSAC`, accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.
- Pre-repair B1 Draft #473 head `3f7c9a0528325bb92e146f4331d01acd2167381d`; all **20 original current source/test Python Git blobs** independently matched local `git hash-object`. Original `producer_codec.py` blob `3f8c988a3ca1708ecac4a13fcd8a5f688032fc99`; original `test_producer_codec.py` `af5951ca57745687d8a578aca27a194eed5c4193`.
- Patched B1 code/test commit `4fe19749c88d8e8ee4183cd0f9ecfeb53185b88a`; published `producer_codec.py` Git blob `563c445c314309a6198395addbecb59b464182a0`; `test_producer_codec.py` blob `cb351096d2d9e12468582a58556d0aeb613c5264`. Other 18 Python blobs unchanged.
- Environment CPython 3.13.5 Linux, disposable source reconstruction checked against exact published Git blobs. Container cannot DNS-resolve `github.com` for cloning; GitHub connector supplies independently verified source bytes.

## Independently executed consumer falsifier and repair

The original `producer_codec.a1_envelope` and `a2_envelope` ran `set(raw)=={literal keys}` and untrusted indexed lookups before primitive admission. A malicious Python `str` subclass with underlying value `alien-a1-key`, hash/equality impersonating `c0`, caused the real A1 adapter to accept a source with *no genuine builtin `c0` key*. Equivalent A2 `alien-a2-key` impersonating `interval` passed. Both original adapters accepted these records when the test supplied **new self-issued matching SHA-256 pins**. They did **not** forge independently trusted A1/A2 source ancestry.

Single scoped repair: reuse `receipt_integrity.validate(raw)` before **all** source comparisons, lookups, hashing or iteration, and translate a failure to the existing typed B1 refusal. No new semantics, source law, authority or native consumer.

| Direct same-source CPython check | Result |
|---|---|
| Original published ten-module B1 source/test suite | **84/84 PASS**, exit 0 |
| Original real producer adapters, hostile key attack | **2/2 wrongly ACCEPTED** |
| Patched A1/A2 adapters, same attacks | **2/2 correctly REFUSED** |
| Complete patched ten-module real-parent test suite | **85/85 PASS**, exit 0 |
| New test: nested cycle, oversized and malformed input | Correct refusal |
| Python syntax compilation, original `experiment.py` | PASS |

Reproduction from the B1 core directory with literal source snapshots:
```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 experiment.py
# Supplemental before/after fixture: b1_hostile_key_falsifier.py in run archive
```

The original and patched source comparisons and raw logs are retained in the run's evidence archive; SHA-256 of full patched suite log `d4ec44d5742ca389abde5f26429a57bca27684dec17ef84b1235771f0082f2d7`, adversarial log `4060767fb3819376172d36b277267118a3bf80c730113075e855857d46046035`.

## Real producers, origin/authentication limits and performance

- **A1 actual producer executed:** `algebraic_zero.py` blob `daeb0b4ff0325c246bbf0f5737daf359400b7c3d` at A1 #470 exact head `22f8751bf9e0fee45b6cac0f5fae16217e54fb80`. Genuine `Source` → `rational_event` → original `verify_rational_event` → B1 `a1_envelope` replay produced `EXACT_ZERO` with source digest `b4ee6d2ee589e440772f32c4250040fd037ef74617bd1e80c7a819df1c29592b`. It used an externally supplied research window, **not** original B-spline ancestry. A separate hostile equality falsifier still shows that the actual original A1 verifier accepts a forged `EXACT_NONZERO` result; A1 owns correction.
- **A2 actual current producer receipt NOT EXECUTED in this run.** Current A2 #471 exact head `d9cb56e74e876efb203e04003aadcf8bd368a369`, current `cyclotomic_moments.py` Git blob `649b6dc6d5f74766ae285115dfd7600f2b6f6036` inspected. B1's internal producer-revision table remains **pinned to older A1/A2 revisions** and is not genuine source ancestry authentication; do not silently repin or infer a reviewed producer from a caller-supplied digest.
- `#462` affine/knot source covariance, geometry/topology and STEP output are external obligations, not established by B1's polynomial source equations or phase equivalence.
- Retained model recomputation counters **2,080 vs 96 full-leaf checks** are logical work counts. **Verification overhead and net native/STEP benefit UNMEASURED**, so no optimization adoption justified.

## Next independent gate and unchanged authority

A3/B5 should independently run the **current** published #473 85-test suite with original parent imports and challenge both source codecs, source-identity swaps, physical window custody and current A2 real producer `point_germ`/`verify_receipt`; an actual A2 receipt is still missing here. B1 remains Draft/HOLD, no merge, native execution, production edits or gate promotion. Historical 121/20/30/50 census and all 26 machining operations preserved; MC-B and MC-1 remain `NOT_ESTABLISHED`, `production_authorized=false`.
