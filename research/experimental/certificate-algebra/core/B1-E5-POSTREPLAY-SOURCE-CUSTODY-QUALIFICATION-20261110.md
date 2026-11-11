# B1-E5 post-replay source custody — 10 November 2026

**Disposition:** GO for bounded research Python tests; **HOLD** for current A1/A2 admission, independent proof, native/STEP ROI and merge. This is a real consumer-custody defect, not a new algebraic theorem or production qualification.

## Pinned baseline

Repository `techrote/radiCADSAC`, B1 Draft #473, main/base `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`, exact tested input head `d2852a7c4c3e981c711af2cdfd4b88c94f40330c`. Before modification, **23/23** published Python source/test/benchmark Git blobs matched fresh GitHub exact-head reads and local `git hash-object`. Only B1's owned `research/experimental/certificate-algebra/core/**` changed.

## Reproduced real E5 source/hash falsifier

E5's `quotient_sided_germ.derive` successfully called the real E4 `rational_quotient.verify` on pinned rational parents, but subsequently reparsed the **caller's original mutable** numerator/denominator dictionaries. A deterministic `sys.settrace` hook at the actual E5 → `certificate_algebra.piece` call changed a right-side numerator coefficient `"1"` to `"-1"` **after** E4 replay. The original real E5 consumer then accepted a sided leading coefficient **-1** while retaining the genuine original `quotient_hash` and `numerator_pin`; stable E4 replay with the altered source correctly refused. No hash collision or producer-signature forgery is claimed.

A new regression in the actual ten-module parent-imported suite fails against unmodified E5 and passes after repair. The repair validates/copies each bounded primitive parent once, revalidates owned copies, and uses **those same copies** for E4 verification and E5 Taylor extraction. This closes the in-process second-read discrepancy, not external source provenance. Blobs: `quotient_sided_germ.py=8671f5981cf679c639eab204fb458f7228f6fe8d`, `test_quotient_sided_germ.py=94e5a934bff597c4fec0d0ac85cc6aafe0e705c8`.

## Executed exact-source checks

- Original parent suite **88/88 PASS**, then new original-parent regression **FAIL** (one expected failure, demonstrating the exposure).
- Repaired `python3 -m unittest discover -s . -p 'test_*.py' -v` **89/89 PASS**, exit 0, CPython 3.13.5; `python3 -m compileall -q .` and `python3 experiment.py` PASS.
- `python3 bench_b1_fair_boundary_20261110.py`: same all-64 intermediate snapshot hashes, 32 pieces / 64 edits. Efficient fresh one-pass **99.798 ms**, trusted incremental **37.182 ms** (2.68x); fresh + strict per-edit receipt readmission **250.374 ms**, incremental + same readmission **189.228 ms** (1.32x). The naive triple-Bernstein arm was 224.119 ms and is not the fair baseline.
- Direct same-host E5 7 blocks × 200 calls after 30 warmups: original median **505.52 μs**, corrected **588.43 μs** (**+16.4%**). Separate research Python workloads, not native throughput or final end-to-end cost.

## Consumer/provenance closure

E5's rational C0 sided quotient orders could inform future geometric zero/tangency handling, but neither a native machining/STEP consumer nor CyberSand solver was exercised. No physical B-spline control/knot/window ancestry was established; Python savings must be compared with **efficient native fresh recomputation plus external custody**, not merely leaf-check counts. Current A1/A2 receipts were not executed this cycle; older executed A1 `098517...` must not be relabeled as the current #470 head. A2 #471 remains a separate source-authentication challenge. Ask A3/B5 to run real current-head receipts and independent second-source E5 mutation controls; do not whitelist new heads without their reviewed provenance.

**Frozen:** 121/20/30/50 census, 26 machining operations, historical evidence unchanged; MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. No paid/native campaign, production edits or merge; Draft / DO NOT MERGE.
