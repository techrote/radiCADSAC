# MC-038 / PB-007-01 — frozen V44 algebraic proof-cut / physical-root partition

**Status:** bounded deterministic-model candidate  
**Date:** 30 October 2026  
**Parent:** #100  
**Preselection:** https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6512935140  
**Exact base:** `71a40a274b803d6779fadec8c4d16f4646fd50af`

## Purpose

This candidate addresses one exact frozen historical blocker:

`harvested:verify_pb00701_v44:ffaea08e30c9`

The historical source is a single original rational B-spline span on
`source parameter in [0,1]`, with affine phase turns `-1/8+t/16`. Its frozen
v54 disposition remains **BLOCKED** at
`ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING`.

The question here is narrower than constructing an algebraic child solver:
can an independently complete physical root set on the original source span be
partitioned exactly across already-certified proof cuts?

## Evidence combined

The candidate composes four reviewed deterministic-model layers without
rewriting them:

1. **Historical V44 boundary** — the exact frozen source must still reproduce
   the historical fail-closed algebraic-orientation consumption blocker.
2. **#296 original-source root proof** — the generic rational interval checker
   must prove a complete set of simple physical roots over the entire original
   rational source span. This proof is independent of historical child root
   counts.
3. **#306 V41 cut geometry** — every rational/algebraic orientation and
   historical proof cut is regenerated from the same original source and
   strictly ordered by exact rational arithmetic / Sturm refinement.
4. **V46 algebraic endpoint semantics** — the algebraic orientation cut must
   be physically NONZERO with exact sign and multiplicity zero.

V47 is also replayed as a negative ownership control: this frozen V44 source
must not silently become certified merely because V47 has a sufficient
closed-child derivative family for a different source.

## Partition theorem

For this frozen source, success requires exactly one complete simple physical
root from the original-span proof. Each proof cut is then ordered relative to
that root.

- Rational proof cuts use exact rational comparison; if their coordinate lies
  inside the strict root bracket, the exact interval evaluation sign determines
  whether the cut lies before or after the unique simple root.
- An algebraic cut is refined only by #306's exact Sturm descriptor. If its
  rational bounds separate from the root bracket, order follows directly.
  Otherwise, once the descriptor lies wholly inside the monotone one-root proof
  cell, V46's exact physical sign at that algebraic coordinate determines which
  side of the root it occupies.
- A ZERO or unresolved algebraic endpoint is outside this theorem and refuses.

The ordered proof cuts therefore define open proof cells. The one proved
physical root is assigned to exactly one cell and the sum of cell root counts
must equal the complete original-source count.

## Critical semantic boundary

A **proof cut is not a physical event**. This package does not claim:

- an algebraic child analytic reparameterization;
- a closed-child derivative theorem;
- V47 ownership of the frozen V44 source;
- a historical v54 route rewrite/admission;
- general multi-cut or multi-generator child certification;
- PB-007-01, MC-B, MC-1, native topology/material/lineage, B-rep or usable STEP;
- production authorization.

The result is root-set partition evidence only. It can inform later source-bound
child-interface work but cannot substitute for any required analytic child
certificate.

## Decisive falsifiers

The verifier must refuse if:

- the frozen source or historical V44 blocker changes;
- #296 cannot prove the entire physical root set as simple roots;
- #306 cannot reproduce exact source-bound proof cuts;
- V46 says the algebraic cut is ZERO or unresolved;
- a proof cut cannot be separated/ordered against the physical root under the
  bounded exact refinement rule;
- cut order or root-count conservation is forged;
- source, phase, parameter identity or pinned producer blobs drift;
- binary-float/noncanonical authority enters;
- resource limits are exhausted; or
- any unearned capability flag is asserted.

## Source custody

Pinned read-only inputs include:

- frozen v54 corpus:
  `5841c331579489b25caef38cd412bdbf286f9134`;
- #296 original-source binder:
  `992ad17ddbdf34687bcb59acba46f672b2d4a1c4`;
- exact trig interval checker:
  `2320f92efe4316d865a89f6d848737e2c000ca4d`;
- #306 source-bound algebraic cut ordering:
  `e15944ee0fd7819b818c8c556f2c079039d042b7`;
- historical V44 model:
  `a56d6487963d269405ab82f3db4cce58a0165520`;
- V46 algebraic endpoint model:
  `77c18cb5c8c0700072c65969c973e8f3c4c12a99`;
- V47 sufficient single-cut model:
  `07b092f9c7df8b3325c2b15d17ca7abe9781cb10`;
- 26-operation domain:
  `23de82f5240a72509f7afe4acd5948b65bc4ff13`;
- no-production authority:
  `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.

## Verification and landing gate

```bash
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_algebraic_cut_root_partition.py --contract --self-test
```

The final literal PR head must also pass `mc1-static`, receive a distinct
technical/source review, and merge only with expected-head protection. Reviewed,
synthetic-merge and landed source trees must match, followed by actual
merged-main focused/static qualification and a durable #100 checkpoint.

All 26 machining operations and protected source/provenance/phase/canonical
journal/material/body/lineage/refusal/UNCERTIFIED/conventional-STEP semantics
remain mandatory.
