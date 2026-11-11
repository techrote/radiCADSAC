# B1-D10 — direct-state falsifier and source-current A1 qualification

Date: 10 Nov 2026. **DRAFT / RESEARCH ONLY / DO NOT MERGE.** Accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; B1 input `86fac5865833ea69a2d530d6fce92dc4a3db1d9b`. All changes remain within `research/experimental/certificate-algebra/core/**`.

## Actual full B1 consumer execution

All **23/23 original B1 Python blobs matched** GitHub's exact input head. Original `python3 -m unittest discover -s . -p 'test_*.py' -v`: **89/89 PASS**, exit 0. The full test import path, not a standalone receipt probe, includes hostile custom Python equality, malformed/deep/cyclic inputs, wrong and invalid SHA pins, source swaps, rational split/negative affine, E3/E4/E5 receipts, source-custody snapshot regressions and resource refusals.

**New falsifier at the real public `split`/`affine` consumer input:** An ordinary caller could instantiate the exported `Verified` dataclass with a false certificate for `P(u)=1-2u`, source hash matching `P` but a forged `POS` Bernstein vector `(1,1)`. The unmodified public transforms then emitted positive certificates and an empty zero set despite `P(1/2)=0` and actual Bernstein vector `(1,-1)`. Real `check_leaf` refused the same lie, but the forged dataclass bypassed that entry point. `dataclasses.replace` on an originally genuine state was another way to construct this nominally verified forgery. Prepatch new regression **FAIL** (constructor incorrectly permitted); existing 89 tests alone had not covered this route.

**Correction:** `Verified` construction now requires an internal `InitVar` mint passed only by B1's trusted `_state` closure. Direct construction and `dataclasses.replace` refuse without mint. The real `verify_base`/`replay` entry points and their full leaf-proof checking remain unchanged. Corrected complete suite **90/90 PASS**, exit 0; `compileall`, `experiment.py` and five-arm fair benchmark also PASS, with exact intermediate hash parity. Published changed Git blobs: `certificate_algebra.py` `66b2e4e6acb3d330af1de676f370e7a9bd93473b`; `test_certificate_algebra.py` `9b7e41b4bfa95490678b9e2aeb6018a7180412a3`.

**Limits:** The module-private marker is API hygiene, **not cryptographic or hostile-in-process security**: arbitrary executing Python can introspect private symbols or mutate objects with `object.__setattr__`. It does not authenticate externally issued source, producer or geometry. Consumers admitting untrusted inputs must use full `verify_base`/`replay` or their downstream independent replayers. Direct `Verified` transfer across an untrusted in-process boundary remains HOLD.

## Actual exact-current A1 producer execution

At A1 #470 head `976ec8c093a17bbe117b7ddd14dc4f391c7ea25c`, source blob `algebraic_zero.py=5a8e52898725aa10b427de4e5736cb1cf5578d68` was reconstructed from an earlier matched source and the exact published Git compare patch, then re-hashed against the live GitHub blob. The unchanged `receipt_integrity.py=77f0ba7700002b7a376dfcc2c29b820ea4def485` also matched.

The real A1 `source([-1],cos=[[]],sin=[[1]])` → `source_sha` → `rational_event(t=1/2)` → `verify_rational_event` returned **EXACT_ZERO / verified**, SHA-256 `b4ee6d2ee589e440772f32c4250040fd037ef74617bd1e80c7a819df1c29592b`. At `t=0` the same producer gives EXACT_NONZERO; forged event result and changed amplitude are refused. New `probe_a1_head_976ec8_20261110.py` (blob `c52993db7f33310595b5a3d6e7ae3292fe3151a0`) reuses the original actual-source B1 probe to run `a1_envelope`, `phase_bridge.prove_equivalent` and `phase_bridge.verify`. B1 codec blob `d9858061f47df687722eb1069965cd8e03c219b6` and phase blob `dbcb2049d7e3de09f6430e632bee21ce836a1809` matched.

**Provenance HOLD:** B1's existing adapter itself stamps historical admitted A1 head `281705e947fd7812300d1d2605d3cdf60cdb005e`. It does **not** authenticate that the currently executed A1 head produced the event. Explicit actual head `976ec8...` is correctly **REFUSED** as unreviewed by phase admission. The `[0,1]` window is research supplied, not physical B-spline control/knot/window custody. The A1 receipt has **not** become an authoritative B1 operational receipt. Current A2 actual producer receipt remains unexecuted, and the earlier A2 source-identity forgery remains open.

## Fair Python cost and native relevance

Five symmetric repeats, CPython model, 32 rational pieces and 64 edits; all intermediate snapshot hashes match (`1b33b99efaaffd86fc2da9a5d55b6fbb3589712ee5d04ee77f03eca50291bf93`). Efficient one-pass full reproof median **82.633 ms** versus trusted incremental **30.585 ms** (2.70x). Full reproof plus strict every-edit readmission **207.822 ms** versus incremental plus the same readmission **153.682 ms** (1.35x). The earlier naive threefold redundant Bernstein baseline is not used for the GO decision. These are **not native/STEP measurements** and omit authenticated upstream producer custody, spline provenance and real downstream consumer verification. Verified Python savings therefore **do not justify native integration** at this time.

## GO / HOLD / NO-GO

**GO:** bounded B1 Python research grammar and tested current A1 exact model event. **HOLD:** cross-producer A1/A2 admission, source/windows/knots/control identity, genuine current A2 execution, independent A3/B5 second-source challenge, native ROI, Ready/merge. **NO-GO:** forged direct `Verified` as proof, self-issued producer ancestry/pins, using a guessed spline window, promotion of Python timing into native savings.

No cross-lane/production edits, no merge or gate change. Immutable 121/20/30/50 census, 26 machining operations, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false` preserved. Request independent exact-head 90-test run and new direct-state falsifier challenge from A3 and B5.
