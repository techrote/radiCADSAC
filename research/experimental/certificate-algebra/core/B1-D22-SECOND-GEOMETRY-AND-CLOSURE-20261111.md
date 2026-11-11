# B1-D22 — Independent second geometry, exact-source consumer falsification, scoped closure

**Date:** 11 November 2026. **Programme:** speculative B1 certificate-algebra research, Draft PR #473 **DO NOT MERGE**. **No new algebraic subfamily or theorem.** This report supplements D21 and replaces neither its proof scope nor any independent admission requirement.

## Source identity and hypotheses

- Parent read from published B1 head `adc9cba42d1c3bfd8a67b0ffc9a3dfdc1d4fb902`, branch `research/b1-piecewise-zero-certificates-20261109`. GitHub `contents/.../core?ref=adc9cba...` returned **29** current Python filenames and blob identities, exactly matching the 29 D21 independently archived, locally recomputed Git-blob SHA-1 values. The test published in this cycle has separate Git blob `e1c9b2c660e65c55c7b9c84a1253602513aa99e3` (read back from commit `aa5a0d699653abe373a42b1ab409f2be5dba617c`), matching the 4,041-byte locally executed file. Hence **30/30 Python Git blobs match** the executed parent + new test. This is a directory/tree identity check plus local byte hashing, not a network Git clone.
- Actual imported B1 `certificate_algebra`, `closed_nonzero`, `product_cone`, `refined_product`, `rational_quotient`, `quotient_sided_germ`, `phase_bridge` and receipt consumers were executed by `python3 -m unittest discover -p 'test_*.py' -q`.
- Falsification target: (i) a geometrically distinct source changes CROSS semantics under split/negative affine, (ii) source/receipt swaps or invalidated middle leaf survive verified-state replacement, or (iii) bounded whole-consumer tests fail. All remain refutable by the committed test. No guarantee is extended to external physical ancestry.

## Genuine second geometry — planar line intersecting a circle

Use independent exact-implicit geometry, not A2's cubic C0 B-spline: traverse straight line `(x,y)=(t,0)` through circle `(x-1/2)^2+y^2=(1/6)^2`, `0<=t<=1`. The scalar residual is

`F(t)=(t-1/2)^2-(1/6)^2=t^2-t+2/9`.

Its two exact crossing parameters are `t=1/3,2/3`, with signs POS/NEG/POS on the three corresponding bounded rational cells. On each cell `[a,b]`, independent substitution `t=a+(b-a)u` yields power coefficients `(F(a), 2(a-1/2)(b-a), (b-a)^2)`. These are fed as **genuine B1 source pieces**, generating base records and checked receipts at the real consumer, not hand-stamped certificates.

Committed regression `test_circle_line_source_contract.py` checks:
1. Exact two CROSS events and all three leaf signs; full B1 replay through `base_record/verify_base`.
2. Split of negative middle piece at `1/2`, followed by signed reversal `t=2-x` using genuine `split/affine`. Compare source, split and reversed pieces to the independent circle implicit polynomial at **121 rational positions**. Confirm reversed CROSS sided signs at `4/3,5/3`.
3. Replace only the middle polynomial with its negative, preserving zero-valued seams; inspect real `replace` meter (1 leaf reproof, 2 seam checks), two unchanged leaf certificates, changed snapshot hash, and both changed crossings to TOUCH events. This is a **new static authored source**, not a physical change to the original circle.
4. Refuse swapped source with stale receipts and forged middle leaf digest at `verify_base`. Valid freshly issued polynomials are not proof of the circle's external control/parameter ancestry.

**Outcome:** both new tests PASS. No newly exposed algebra/verifier defect; no expansion of proof claims.

## Full exact-source verification

On Python 3.13.5:
- Baseline exact parent: **110/110 PASS** under `unittest discover`.
- After new source test: **112/112 PASS**, whole parent and E1–E7 consumers imported and run; `compileall` and `experiment.py` PASS.
- Existing cases include custom Python equality, nested/nonprimitive input, source/hash substitution, forged receipts, invalidated split/affine, 512-piece admission ceiling, derived 1024-bit rational refusals and 3,500 actual-consumer mutation attempts (at least 2,450 changed primitive inputs).
- Published source scope: 30/30 Python blobs exact; no algorithm repair required in this cycle.
- Limitation: 112 tests and 121 geometry probes are bounded checks, not a universal proof of hostile Python safety or correct native geometry.

## Current A1/A2 producer and custody

A1 #470 head `fe0dada7c430053c4c387f17a062909da9aab8bc` is unchanged. Read back the current published `algebraic_zero.py` blob `5a8e52898725aa10b427de4e5736cb1cf5578d68` and `receipt_integrity.py` blob `77f0ba7700002b7a376dfcc2c29b820ea4def485`, both matching local executable sources. A temporary **local-only** run corrected stale literals in the archived older `probe_current_a1_receipt_20261110.py` fixture (which expected an obsolete A1 head and `phase_bridge.py` blob). This stale fixture is not a B1 admission failure. The corrected direct current-source test PASS: genuine A1 exact-zero/nonzero, forged-result and coefficient-swap refusals, and B1 source codec consistency under **research-supplied** window pins. B1 still stamps a historical approved A1 head, so **current revision admission correctly REFUSES**; producer-custody and physical spline origin remain HOLD.

A2 #471 current head `d9cb56e74e876efb203e04003aadcf8bd368a369` has existing A3 published producer-local tests but **no fresh genuine current-head A2 execution by this B1 lane**. Neither A2 producer tests nor the independent second circle geometry authenticate original B-spline controls, knots, source window, source-to-receipt chain or a native STEP consumer. **HOLD**, not inherited GO.

## Verification economics and application decision

Fresh symmetrical-order 5-repeat Python deterministic-model benchmark, 32 static pieces, 64 single-cell edits, exact intermediate-state-hash parity:

| Workload | median ms | comparison |
| --- | ---: | --- |
| A: published triple-pass full proof | 188.417 | inefficient baseline, do not claim speedup against this |
| D: efficient single-pass full recomputation | 83.387 | fair trusted baseline |
| B: incremental trusted reuse | 30.952 | 2.69x faster vs D |
| E: efficient full recomputation + strict readmission | 209.243 | fair verified baseline |
| C: incremental reuse + same full readmission | 159.531 | **1.31x faster** vs E |

Full strict readmission leaves **49.712 ms savings / 64 edits = 0.777 ms/edit**, before independent producer custody, live dependency-closure discovery, native B-rep, geometric reconstruction or STEP export. Verification adds ~128.6 ms to the incremental workload; the unverified 65/3 proof-work ratio is not a wall-clock application speedup. Any extra incremental-only cost exceeding 0.777 ms/edit would erase this exact Python-model advantage, and actual native benefits or costs have **not been measured**. Dynamic geometrical dependencies, nonlocal effects and topology cannot be inferred from static local source hashes. No CyberSand acceleration claim is supported.

## Scoped final disposition

- **GO:** bounded, exact, static rational-polynomial Python proof/certificate algebra, under the source grammar and checked importer/closure model; the committed tested scope remains research-only.
- **HOLD:** independent A3/B5 current-head acceptance, genuine current A2 producer execution and physical source/window ancestry, current A1/A2 cross-producer B1 admission, hosted exact-head qualification, review and merge. Do not relabel producer revisions.
- **NO-GO:** native STEP/B-rep adoption and CyberSand solver-performance claims on current evidence. The measured Python savings do not justify speculative native integration or paid campaigns.
- **CLOSE B1 IMPLEMENTATION EXPANSION:** no additional theorem family or serial local hardening campaign. Independent A3/B5 challenges and consumer-lineage evidence may reopen a precisely falsified case. Stop the B1-owned recurring work; leave Draft #473 unmerged until an independent acceptance decision.

Source ownership remains exclusive to `research/experimental/certificate-algebra/core/**`; no production/bootstrap or external-lane changes. Frozen 121/20/30/50 census, 26 machining operations, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false` and historical evidence remain unchanged.
