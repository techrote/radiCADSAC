# B1-D13 — Closed-journal primitive admission before mapping hooks

**Date:** 11 November 2026. **Research-only / DETERMINISTIC_MODEL / DO NOT MERGE.** B1 owner-only source changes inside `research/experimental/certificate-algebra/core/**`. No change to theorem, permitted producer revisions, MC-038 evidence or native implementation.

## Exact source and scope

- Accepted main/PR base: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.
- Previous B1 head: `76f1665a0770d62bb5871e7dfa3806f008de50d0`.
- Actual corrected code/test head before adding this report: `077a1d266c8c686ca0ef1daf946f57e43009143e`.
- `closed_nonzero.py` now has Git blob `6b02119877286a3ed8a2191b458de8efe1af005d`; test `test_closed_nonzero.py` has `1262518fd5c302c39e4e92918f80779d27a6176b`. Original 23 other B1 Python blobs remain identical to the independently recomputed original 25-blob manifest. No sources outside the B1-owned subtree changed.

## Falsifier in the actual E2 consumer

`closed_nonzero.verify_closed_journal(log, base_pin, final_pin)` performed `isinstance(log, dict)`, `log.get("base")` and `log["base"].get("hash")` **before** calling `replay(log)`, which is the component that validates primitive receipt structure. A dict subclass overriding `.get`, or a str-subclass key with matching hash overriding equality, caused executable caller-defined hooks to run **before any shape check**. This is an admission-order correctness/availability failure, not a forged mathematical zero-set witness.

Source-current control: the previously published 95 tests all PASS. A newly added **real `verify_closed_journal` test** fails against the original consumer with three hostile inputs (top-level mapping subclass, colliding top-level key and colliding nested `base.hash` key), including raised `AssertionError` from attacker hooks. The four failures reported by unittest comprise three subtests plus the final guard assertion. No JSON approximation or fake verifier was used.

## Bounded repair

Move `receipt_integrity.validate(log)` before **any** mapping lookup or equality in the public journal verifier; require `type(log) is dict` and `type(log.get("base")) is dict` after admission. Every nested key and value is thereby checked by the existing bounded primitive validator before the remaining built-in dictionary operations. This does **not** claim protection from malicious executable code in the same Python interpreter, or authenticated source/producer custody.

Re-run with repaired source (CPython 3.13, same container):
```sh
cd research/experimental/certificate-algebra/core
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 -m py_compile *.py
python3 experiment.py
python3 bench_b1_fair_boundary_20261110.py
```
**96/96** complete original parent + all downstream consumer tests PASS, no skips; all three hostile variants are `Refusal` with **zero hostile hook executions**; normal positive base/journal case PASS. Python compilation and proof-work experiment PASS. The re-run includes existing deeply nested inputs, Python equality subclasses, stale/swapped source and hashes, rational split/affine and 512-piece closure limits.

## Independent current A1 producer replay and strict cost

At **actual A1 Draft #470 head** `fe0dada7c430053c4c387f17a062909da9aab8bc`, this run matched the two used GitHub producer/verifier blobs `5a8e52898725aa10b427de4e5736cb1cf5578d68` and `77f0ba7700002b7a376dfcc2c29b820ea4def485` to locally executed bytes. The real `source→source_sha→rational_event→verify_rational_event` generated and verified the exact zero for `-1+sin(pi*t)` at `t=1/2`; nonzero at `t=0`, tampered receipt and coefficient substitution controls passed. The **B1 source codec** accepted canonical serialization with independently supplied research source/window pins, but stamps historical producer head `281705e947fd7812300d1d2605d3cdf60cdb005e` and refuses explicit current head as `unreviewed producer revision`. **No current A1 event was admitted as B1 authority.** No physical spline source/control/knot/window ancestry was authenticated. A2 Draft #471 actual producer receipt was **not executed**, its independent source-identity issue remains HOLD.

Fresh five-arm CPython model, 32 rational pieces, 64 edits, 5 symmetric repetitions, 2 warmups, exact *every-edit* snapshot parity:
- one-pass fresh full recomputation `D=102.989 ms`;
- trusted incremental `B=40.119 ms` (**2.57×**);
- one-pass full + complete strict readmission `E=275.463 ms`;
- incremental + complete strict readmission `C=200.430 ms` (**1.37×**).

These timings do **not** include authenticated producer lineage, external pin custody, complete native/STEP consumer construction or physical recomputation. Correcting adversarial journal admission is mandatory despite any marginal overhead. Demonstrated Python reuse advantage is **not** a native or STEP ROI justification.

## Gate and independent acceptance decision

- **GO** only for the tested bounded Python B1 parent and downstream consumers at the exact code/test head; positive tests, denial/refusal adversarial controls and local theorem remain scoped.
- **HOLD** for A1/A2 authenticated producer transfer, actual A2 receipt, independently proved complete physical B-spline ancestry, topology/Boolean reuse, genuine native/STEP consumers, ROI and PR integration.
- **NO-GO** for treating a caller-supplied hash as authenticated ancestry, treating an in-process mint as a cryptographic signature or merging this Draft as MC-038 authority.
- Request A3 and B5 independently fetch the exact literal head, run all 96 tests, test alternate custom dictionary/str hooks at every public consumer, and independently execute A2's `source→point_germ/knot_germ→verify_receipt/verify_knot_receipt` with source-identity substitution controls.

The frozen 121/20/30/50 census, 26 machining operations, MC-B/MC-1 `NOT_ESTABLISHED`, and `production_authorized=false` remain untouched.
