# B1 phase-receipt equality correction and real A1 producer boundary — 10 November 2026

**Disposition: PASS for the exact imported B1 Python research-suite at the pinned source, CHANGES REQUIRED for an independently demonstrated A1 upstream verifier, HOLD for cross-producer/native admission.** Research only. Not an MC-038 acceptance claim. No physical B-spline source ancestry, native/STEP verification, or production authorization is asserted.

## Source and execution identity

Repository: `techrote/radiCADSAC`. Draft [B1 #473](https://github.com/techrote/radiCADSAC/pull/473). Current accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Input B1 head `788cf6d606c4a33854d2f214fb0112531001cb4c`; corrected source commit `8de4376b695660cd7d5021b4d4f12437f0fe0ec5`, regression commit / exact tested head `2a5688a760af7244b6aa24d24143a4643145dc37`. Source changes ONLY `research/experimental/certificate-algebra/core/phase_bridge.py` and `test_phase_bridge.py`. All 20 B1 Python source/test files were independently reconstructed into a disposable directory from exact GitHub-connected content; **20/20** `git hash-object` values matched published Git blobs. This is an exact-blob reconstruction, **not a full Git checkout**; `git ls-remote` remains DNS-blocked in the execution sandbox. CPython 3.13.5 on Linux, local/free.

Changed exact Git blobs:
- `phase_bridge.py` input `4ff925423fe74ef76dcf3fd27cc71c5b3761a09a` → corrected `47fe8783c5e7a173cbb2a9c1288148339617d290`.
- `test_phase_bridge.py` input `ea3b2d9552e74e1bd6ba18dc9890dc8002113751` → corrected `078c6dddc800680c630b5dbf98d115ceaf823837`.
- Unchanged `receipt_integrity.py` `cb139bd858329bcdf7958474b012bae870eae83b` and `certificate_algebra.py` `8d47787e393c7f26ff9888c02a2ac7708995a2d8` were directly imported. A full manifest of every original Python blob and stdout/stderr is retained in the accompanying evidence archive.

## Direct false-receipt falsifier, before correction

**Actual published consumer** `phase_bridge.verify(source,target,claim,pinned_source_hash=...,pinned_target_hash=...)` recomputed an authentic phase-equivalence receipt and checked `claim != expected` with unrestricted Python dictionary equality. A hostile `str` subclass whose `__eq__` always returns `True` and `__ne__` always returns `False` substituted a false `schema`, `source_hash`, `target_hash`, or `semantic_hash`. The genuine pinned source/target envelopes were unchanged; each forged receipt was accepted. Ordinary false built-in strings were correctly refused. Direct observed control: `authentic: ACCEPT`, `plain false schema: REFUSED`, `hostile schema: ACCEPT`, then `AssertionError: false receipt accepted schema`. This is a real B1 in-process receipt authentication failure, **not** a counterexample to rational phase-substitution algebra.

**Repair:** require exact-builtin, recursively bounded receipt admission via the existing `receipt_integrity.admit(expected, claim)`, translating its typed `certificate_algebra.Refusal` back to the phase-bridge `Refusal`. Verify source/target pin arguments are exact builtin `str`, not subclasses. New published test covers four hostile receipt fields, hostile dict key, nested cyclic input, invalid/bool fields and externally pinned hash subclass, plus valid receipt.

## Complete same-head B1 tests

Executed original parent modules, ten published `test_*.py` modules and the new real-verifier regression:
```sh
cd research/experimental/certificate-algebra/core
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 experiment.py
python3 -m compileall -q .
git hash-object phase_bridge.py test_phase_bridge.py receipt_integrity.py
```

**83/83 PASS** (CPython 3.13.5, 0.854 s on the final replay, exit 0); `experiment.py` exit 0; `compileall` exit 0. The previously 82-test corrected B1 suite therefore now includes the seventh phase-bridge method. Existing E1/E2/E3/E4/E5/E6/E7 source-bound tests reexecuted without stubs, including hostile equality, nested primitive/depth/budget refusals, source/identity/hash substitution, split, signed affine and source replacement controls. Green general hosted quality is separate: source-current workflow runs succeeded but are not substitutes for this Python test command.

Deterministic `experiment.py`: 2,080 naïve versus 96 incremental full-leaf proof checks; 2,015 versus 155 seam checks. These are accounting operations, not measured native/STEP wall-clock or memory savings. Receipt strict-type walking adds O(receipt size) validation. Net benefit after verifier overhead remains **UNMEASURED** and cannot justify production consumption.

## Actual A1 producer execution and authentication limit

A1 [Draft #470](https://github.com/techrote/radiCADSAC/pull/470), exact current head `22f8751bf9e0fee45b6cac0f5fae16217e54fb80`, actual `algebraic_zero.py` Git blob `daeb0b4ff0325c246bbf0f5737daf359400b7c3d` reconstructed and **directly executed**. Its real `source((-1,),cos=((),),sin=((1,),),phase_rate=1)`, `rational_event(source,Fraction(1,2))`, and `verify_rational_event` produce and accept a genuine `EXACT_ZERO` mathematical receipt for `-1+sin(pi*t)` at `t=1/2`. Original A1 `source_sha256` is `b4ee6d2ee589e440772f32c4250040fd037ef74617bd1e80c7a819df1c29592b`. Actual A1 object fields serialized using the published producer codec match `algebraic_zero.source_sha` exactly; B1's actual `producer_codec.a1_envelope` accepts this original A1 serialization under its exact source pin and a separately supplied research window pin, and rejects a substituted full A1 source using the old pin.

**This does not supply authenticated physical ancestry.** The interval `[0,2]` was independently *supplied as a model-domain control*, not authenticated to physical B-spline controls, knots, geometry, or #462's source-time transformation. In addition, B1's `phase_bridge.PRODUCERS` still enumerates historical A1/A2 heads `281705e...`/`3b6eaf70...`; it does not currently identify latest actual A1/A2 heads. Thus there is NO current-head A1/A2-to-B1 authenticated phase-equivalence/geometry certificate or externally trusted window. A2 actual producer and #462 transformed physical source were **NOT EXECUTED** here.

**New direct A1 upstream negative:** The real unchanged `algebraic_zero.verify_rational_event` recomputes the authentic receipt but applies ordinary Python dict equality. Replacing its true `result='EXACT_ZERO'` by a `str` subclass evaluating equal to all strings with actual value `EXACT_NONZERO` is **incorrectly accepted** by the actual A1 verifier. This is distinct from B1's now repaired phase verifier. The A1 author/A3 should apply recursive exact-type bounded receipt comparison at the **real A1 verifier** with negative controls; do not edit A1 from this B1 lane. No claim against the mathematical zero theorem. This direct falsifier is being handed to A1/A3 on #470.

## Admission/ownership decision

B1 **PASS WITH LIMITED RESEARCH GRAMMAR** for the exact patched Python modules, **HOLD** on A3/B5 independent second-source replay, genuine current-producer source/window/knots authentication, #462 consumption, native/STEP performance and merge. The A1 `algebraic_zero` verifier has **CHANGES REQUIRED**. Request B5/A3 run this literal corrected B1 head with original modules (not shadow maths), reproduce A1 false receipt, and independently supply producer-controlled source/window ancestry before even considering cross-producer admission. Preserve B1 Draft, no Ready/merge, no production/native changes, no self-acceptance. Historical **121/20/30/50** census, **26 operations**, MC-B/MC-1 **NOT_ESTABLISHED**, `production_authorized=false` remain unchanged.
