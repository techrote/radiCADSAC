# B1-D12 — 512-piece closure cardinality and journal budget qualification
Date: 2026-11-10. Evidence class: **DETERMINISTIC_MODEL / CPython**, research-only. PR [#473](https://github.com/techrote/radiCADSAC/pull/473), branch `research/b1-piecewise-zero-certificates-20261109`. Accepted branch base: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.

## Decisive falsifier (old exact source)
The public `verify_base` caps an initial source at **512** pieces. The shared trusted-closure `_state` checked only nonemptiness and certificate-length parity, so a real authenticated 512-piece C0 constant-positive source could become an **admitted 513-piece `Verified` state** by both `split` and `concatenate`. A serialized `b1-journal-v1` with correct `before`/`after` hashes also replayed a 513-piece split. The old entire published suite passed **94/94**, demonstrating that the earlier tests missed this actual resource-boundary failure.

Control: `Piece(Fraction(i),Fraction(i+1),(Fraction(1),))` for each `i=0..511`; all 512 initial leaves and 511 C0 seams are genuine, not forged. The single-cell split at `1/2` or concatenation with genuine positive interval `[512,513]` preserves exact mathematical semantics but exceeds the advertised resource grammar. Before patch: `split ACCEPTED 513`, `concatenate ACCEPTED 513`, `serialized_replay ACCEPTED 513`. No assertion that the extended 513-piece mathematics is false; the defect is admission **outside the stated bounded model**.

## Repair and proof scope
One change in `certificate_algebra._state` enforces `1 <= len(ps) <= 512` for every internally minted verified snapshot, as well as existing parallel-certificate and epoch checks. This single common postcondition covers `split`, `concatenate`, `replace`, `affine` and serialized journal replay without duplicating import logic. It preserves existing affine/split laws **inside the admitted resource grammar**. Over-limit closure is typed `Refusal` (NONTRUTH), not an invalid mathematical theorem.

A new regression in the **existing** `test_certificate_algebra.py` verifies 512 genuine leaves are admitted, all three formerly accepted 513-piece routes refuse, and 2-piece split/concatenation still succeed. No producer tags, source hashes, result semantics, proof laws, or downstream authority were broadened.

## Source-pinned direct execution
At PR input head `6bbfc5746fe169dedc87e2a1c29a74217187c518`, all **25** original Python source/test/benchmark files were independently fetched from GitHub, their Git blob SHA-1s matched local source files, and the complete original tests executed: **94/94 PASS**. Original core blob `c2f2c5b13bf3f26292a46389ee62e4f4e69056a2`; original test blob `9b7e41b4bfa95490678b9e2aeb6018a7180412a3`.

Corrected core blob: `bdc4858d078ac2039d4b6244017b0c89c971eecc`; corrected test blob: `53772a1e29746242d1d798b926238099ce6bcf86`. These exact bytes were executed locally with:
```sh
cd research/experimental/certificate-algebra/core
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 experiment.py
python3 bench_b1_fair_boundary_20261110.py
python3 -m compileall -q .
```
Outcome: **95/95 corrected tests PASS**; proof-work experiment PASS; fair five-arm benchmark PASS, per-edit exact snapshot-hash parity. Before-and-after direct control: `512` base accepted in both; all three `513` routes accepted before and **refused after**. Existing hostile Python equality, deep primitive arrays, digest swaps, invalid digests, affine/split/mutable source and all E3/E4/E5 consumer tests were executed in the same suite, not substituted by a standalone receipt probe.

## Genuine A1 direct receipt / unresolved custody
Independently reexecuted producer code at actual A1 #470 head `fe0dada7c430053c4c387f17a062909da9aab8bc`; current A1 `algebraic_zero.py` and `receipt_integrity.py` matched Git blobs `5a8e52898725aa10b427de4e5736cb1cf5578d68` and `77f0ba7700002b7a376dfcc2c29b820ea4def485`. The real producer reports verified `EXACT_ZERO` for `-1 + sin(pi*t)` at `t=1/2`, `EXACT_NONZERO` at `0`, and refuses altered result and changed coefficient. B1's actual codec replays the source under supplied research pins, but **stamps older producer head** `281705e947fd7812300d1d2605d3cdf60cdb005e`. Explicit current A1 head is correctly unreviewed. No physical window or authentic B-spline control/knot provenance was established. A2's independent source-identity defect and actual current producer receipt remain a separate HOLD.

## Fair Python recomputation economics (same local host, independent workloads)
32 rational pieces, 64 edits, 2 warmups, 5 symmetric repetitions: one-pass full reproof **82.117 ms**, trusted incremental **31.822 ms** (**2.58×** faster); one-pass full + complete strict readmission **210.332 ms**, incremental + strict readmission **159.369 ms** (**1.32×** faster). All intermediate exact state hashes matched. This benchmark is a **Python deterministic model**; it does not include authentic A1/A2 custody, physical B-spline lineage, native-material reconstruction, journal I/O, topology, STEP realization, or actual consumer invalidation rates. It cannot justify native use on performance grounds.

## Decision, blockers, and invariants
**Scoped GO:** B1's bounded Python research grammar and this shared 512-piece closure/refusal invariant. **HOLD:** independent A3/B5 second-source execution; authenticated current A1/A2 source/receipt admission; A2 source-identity defect; native/STEP recomputation ROI; independent PR admission/merge. No same-session merge or production modification. Only two existing files and this report in B1-owned `research/experimental/certificate-algebra/core/**` changed. Prior results are retained, not overwritten.

MC-038 remains open. The frozen 121 original / 20 historical refusals / 30 missing ordered premises / 50 existing complete witnesses, 26 machining operations, and historical evidence are unchanged. MC-B and MC-1 remain **NOT_ESTABLISHED**; `production_authorized=false`. No native/paid campaign or production bootstrap.

## Independent falsification requests
**A3:** recompute the exact 512→513 before/after case, challenge the closure-invariant placement and find an alternative oversized path or source/identity forgery. **B5:** independently run the 95-test parent + E3/E4/E5 consumer suite at the final literal PR head, verify blob identities, challenge the performance denominator and source-custody boundary. Require real second-source execution, not review-by-description.
