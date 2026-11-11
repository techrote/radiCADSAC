# B1-D21 — exact-head consumer falsification and closure disposition (11 Nov 2026)

**Research-only; DETERMINISTIC_MODEL / CPython.** Draft [#473](https://github.com/techrote/radiCADSAC/pull/473), **DO NOT MERGE**. No claimed native geometry, STEP export, MC-038 original-source coverage or CyberSand performance. The correct decision is **GO for bounded B1 research**, **HOLD for cross-producer admission and independent PR acceptance**, and **NO-GO for native/STEP/solver adoption on existing evidence**.

## Exact source identity and full parent+consumer execution

- Accepted main/base remains `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; pre-test B1 literal head `5822fe1c1faf99ed1b098cfe5d2ec4654e83daac`, which compares ahead of D19 with **only one extra test and its report**, no changed Python implementation.
- Reconstructed all **27** D19 Python modules, test modules, benchmark/probe modules from the archived exact-source evidence; each local Git-blob SHA-1 matched its D19 manifest. Independently queried GitHub Contents for **all 27** blob IDs at the literal B1 parent head: **27/27 match**. The D20 `test_metamorphic_consumer_properties.py` file was reconstructed as exactly **4,078 bytes**, local Git blob `7d65395dbf735e71cf3b22fba4ecebe21969f2ac` and GitHub current-head blob identical: **28/28 Python blobs source-qualified**.
- Executed `python3 -m unittest discover -p 'test_*.py' -v` against that complete source in the real `certificate_algebra` parent and imported E1–E7 consumers: **108/108 PASS, 0 skips, 0 errors**, 1.748 s locally. `python3 experiment.py` and `python3 -m compileall -q .` also passed. This includes existing hostile custom Python equality/`Fraction` subclasses, nested/cyclic/oversized primitive trees, altered source and producer head, hash forgery, stale journals, signed affine, split, C0 invalidation, cardinality and derived rational budget refusals, E1–E7 real verifiers and D20's 150-source metamorphic tests.
- Added only `test_bspline_shape_contract.py` under B1's owned subtree on B1 candidate head `6bdf868a91e64c5b00d9a17d24773db7b9b5660c`. Its local and published blob are identically `9eeef302a63719fee0b611087cc323614c8046ae`, giving **29/29 Python files matched**. Reran **110/110 complete tests PASS, 0 skips, 0 errors**, 1.703 s. No implementation code changed, no new falsifier was found and no claim was broadened.

## Second genuinely different geometry, not a producer shortcut

The new test imports actual B1 `base_record → verify_base → events/split/affine/replace` consumers. The independent evaluator uses a **degree-3, seven-control, physical C0 B-spline-shaped case** disclosed by A2 [#471](https://github.com/techrote/radiCADSAC/pull/471): knots `[0]*4+[1]*3+[2]*4`, scalar controls `[1,1/3,0,0,0,0,-1]`. The exact two Bezier spans are `(1-t)^2` on [0,1] and `-(t-1)^3` on [1,2]; the seam at 1 is an isolated **CROSS, POS→NEG**, with asymmetric sided orders 2 and 3. Its negative affine reversal yields **NEG→POS** and side swap.

At 33 rational physical points the actual imported B1 pieces equal separately evaluated cubic Bezier controls; reversed and split domains preserve evaluation. Actual B1 source/receipt swapping, forged source digest and a C0-breaking replacement are typed refusals. A legal single-cell edit preserves the untouched leaf and invalidates the snapshot hash. **This is an independent geometric shape/control calculation, not a claim to have run A2's Python importer or authenticated original MC-038 physical ancestry.** The test proves neither native B-spline topology nor general knot/STEP semantics.

## Genuine producer receipt and external qualification

- Executed source-matched real A1 #470 producer `algebraic_zero.py` and `receipt_integrity.py` at `fe0dada7c430053c4c387f17a062909da9aab8bc`. The exact `-1+sin(pi*t)` event at t=1/2 is verified `EXACT_ZERO`, t=0 is `EXACT_NONZERO`; forged result and changed sine coefficient are refused. B1 bridge serialization with separately supplied [0,1] window passes under research pins, but the adapter **still stamps historical A1 head `281705e947fd7812300d1d2605d3cdf60cdb005e`** and correctly refuses explicit current-head admission. The test's window was not supplied by authenticated physical spline controls/knots.
- A3 independently **executed 32 actual A2 tests** at [review #583...](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-583760), using eight exact Git blobs, and rejected 14/14 hostile forged receipts after the prior implementation repair. This is **A3's scoped A2 producer-local execution**, not this B1 run's A2 execution or B1↔A2 admission. Current A2 #471 head `d9cb56e74e876efb203e04003aadcf8bd368a369` differs from A3's tested `494a7889587d7176cd7278d29faf09dff46c21ff` **only** in ancillary `continuum_alias_challenge.py`; the tested `cyclotomic_moments.py` blob remains `649b6dc6d5f74766ae285115dfd7600f2b6f6036`. Whole-current-A2 checker execution, cross-head authenticated source lineage and physical controls/knots/window remain **HOLD**. Independent B5 whole-B1 review is still required; do not mislabel this owner-lane run as external reviewer acceptance.

## Reverification economics: concrete native adoption threshold

Executed the existing fair, identical 32-piece / 64-local-edit, five-repeat, symmetric-arm CPython benchmark (`bench_b1_fair_boundary_20261110.py`), with equal per-edit hash traces (SHA-256 `1b33b99efaaffd86fc2da9a5d55b6fbb3589712ee5d04ee77f03eca50291bf93`):

| Arm | Median ms / 64 edits | Scope |
|---|---:|---|
| D | 87.914 | Efficient one-pass full proof each edit, no extra readmission |
| B | 32.418 | Trusted incremental single-leaf update |
| E | 224.131 | Efficient full proof **plus** strict full readmission |
| C | 169.446 | Incremental **plus equivalent** strict full readmission |

Trusted-model improvement ~**2.71x**, with symmetric complete readmission only **1.32x**. Net gross saving E−C is **54.686 ms per 64 edits**, or **0.854 ms/edit**, *before* incremental-only producer/source custody, nonlocal dependency graph completeness, topology/STEP provenance, serialization, native recomputation and export checks. Any extra differential cost >=54.686 ms for the same workload removes the apparent benefit. This is not a portable wall-time prediction or evidence of a particular native consumer's cost. A real native/STEP integration requires demonstrated complete dependencies and a measured end-to-end net win over an efficient full-recompute control; no such integration is qualified.

## Closure / retained gates / next independent actions

**Scoped GO:** B1's stated, restrictive C0 rational-polynomial Bernstein cone and exact local transformations, under tested primitive size and source-admission contract, remain useful *research* with no new counterexample in this run. This is bounded execution plus existing classical algebra, not a proof of all inputs or novel arbitrary topology decidability.

**HOLD:** B1 Draft #473 merge; independent B5 second-source full-head execution; authenticated exact-current A1/A2 producer import and physical spline controls/knots/window; complete dependency graph and saved journal provenance outside the admitted static source grammar; final hosted exact-head checks.

**NO-GO:** native B-rep/STEP, machining completeness, generalized Boolean/topology truth or CyberSand simulation optimization based only on the Python benchmark.

Keep the frozen **121/20/30/50** census, **26 machining operations**, MC-B and MC-1 both **`NOT_ESTABLISHED`**, and **`production_authorized=false`**. No production edits, merge, native/paid campaigns, proof-registry or cross-lane writes. The next worthwhile step is **independent B5 execution and actual native consumer/custody cost measurement under a separate permit**, not expanding the certificate-algebra theorem catalogue.
