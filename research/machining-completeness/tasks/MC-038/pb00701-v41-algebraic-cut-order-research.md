# MC-038 / PB-007-01 — V41 implicit orientation-root equality/order research

**Status:** 29 October 2026. **Evidence class:** bounded deterministic-model research candidate.  
**Parent:** #100. **Preselection:** https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6511299736  
**Exact base:** `e631b5ad9f36289a92b9a21691caac770b83c322`.

## Targeted live gap

The landed V41 orientation-partition model already computes an exact Sturm count
for each rational-polynomial orientation coordinate, but its current
`exact_rational_orientation_roots` route admits only roots found by the
rational-root theorem. If the Sturm count is larger, it fail-closes with:

`IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE_BY_CURRENT_RATIONAL_CHILD_PARAMETER_MODEL`.

That refusal is correct. This candidate does **not** change that production of
rational child boundaries. It isolates one earlier proof obligation: exact
identity and order of source-owned implicit orientation proof cuts.

## Exact method

The original rational B-spline source is first re-lowered by the pinned
historical coupled lowerer. Caller-provided cuts, roots or polynomials are not
authority. This candidate is limited to one source span at the existing general
coupled V41 research boundary.

For each positive harmonic having both cosine and sine amplitude channels, the
source-owned rotated coordinates are regenerated exactly:

- `A=(C+S)/2`;
- `B=(C-S)/2`.

The landed PR #281 exact polynomial primitive then supplies complete Sturm root
counts, square-free rational defining polynomials, rational isolating intervals,
and exact per-polynomial multiplicity.

A proof coordinate is either an exact rational value or a square-free rational
polynomial plus a rational interval containing exactly one real root. The latter
is an **isolating descriptor**, not a minimal-polynomial claim.

### Cross-polynomial equality

Two implicit roots from different defining polynomials are equal only when the
exact polynomial GCD has exactly one root in the intersection of their two
unique isolating intervals. Merely overlapping intervals are never equality.

For a rational proof cut and an implicit root, equality requires exact
evaluation of the root's defining polynomial to zero at that rational value,
inside the unique isolating interval.

### Strict order

If two roots are proven distinct but their current rational isolating intervals
overlap, exact Sturm bisection refines one or both intervals until they become
disjoint. The disjoint rational bounds then establish strict order. A global
bounded refinement budget is explicit; exhaustion is `RESOURCE_REFUSAL`, not
an order/equality truth value.

Existing rational V27 phase-sector cuts and V41 rotated-certificate-cell cuts
are recomputed from the exact source phase and inserted into the same canonical
proof-cut ordering. Equal cuts are deduplicated; every orientation cause keeps
its own multiplicity. A shared proof coordinate therefore does not require two
different orientation polynomials to have the same multiplicity.

## Source-bound controls

The verifier constructs exact one-span rational B-spline records and sends them
through the pinned historical lowerer before using any orientation polynomial.

1. **Same nonrational coordinate, different polynomials:**  
   `A=2u²-1`, `B=(u+1)(2u²-1)`. Both have the same positive open root;
   equality must be established by exact GCD + Sturm, not interval overlap.
2. **Distinct nonrational coordinates:**  
   `A=2u²-1`, `B=3u²-1`. Their positive roots are strictly ordered because
   `1/3 < 1/2`; the generic checker must independently refine/order them.
3. **Shared coordinate, different per-cause multiplicity:**  
   `A=(2u²-1)²`, `B=2u²-1`. The canonical proof cut is shared, but the two
   causes retain multiplicities 2 and 1.
4. **Rational root / historical phase-cut coincidence:** an orientation root at
   `u=1/2` is exactly merged with the source-derived rational phase-sector cut.

The verifier also calls the current V41 rational-only orientation certificate on
the first fixture and requires the existing algebraic-root blocker, proving that
this research addresses a live boundary rather than a hypothetical one.

## Adversarial controls

The executable rejects/refuses source/phase/parameter/amplitude mutation,
caller-supplied root authority, binary float input, identity orientation
coordinates, interval-overlap-as-equality, wrong common-root/GCD claims,
reversed ordered reports, omitted causes, forged capability fields, and
isolation/refinement resource exhaustion. Source/report replay is hash-bound and
fully recomputed.

Pinned custody:

- historical coupled B-spline lowerer:
  `a086b625e1a6dea8bd202699d161167bb69cc9e7`;
- landed V41 model:
  `2f96622b5c69655279d66fe2b36f8f3e03414660`;
- landed PR #281 algebraic/Sturm verifier:
  `0954c5e1ad63ec1c8dd2acb3202882650b02c516`;
- frozen v54 corpus:
  `5841c331579489b25caef38cd412bdbf286f9134`;
- 26-operation MC-002 domain:
  `23de82f5240a72509f7afe4acd5948b65bc4ff13`;
- no-production authority:
  `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.

## Deliberate nonclaims

This is **proof geometry only**. Existing V41 child construction requires exact
rational child boundaries. This candidate does not convert an algebraic proof
coordinate into a rational child parameter, does not construct algebraic child
reparameterization, and does not assert that existing V43/V27 child summaries
can consume such a boundary.

It therefore does **not** solve the frozen V41 child-composition blocker, admit
any historical v54 disposition, establish arbitrary V27/V41 nested composition,
turn a proof cut into a physical event, or promote PB-007-01, MC-B, MC-1,
native material/topology/lineage, B-rep, usable conventional STEP or production
authorization.

Historical evidence, the 43-owner/v54 inventory, all 26 lathe/mill operations,
source/provenance/phase/canonical-journal/material/body/lineage semantics,
typed refusal/UNCERTIFIED behavior and conventional STEP obligations remain
unchanged.

## Reproduction and landing gate

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v41_algebraic_cut_order.py --contract --self-test
```

Landing requires literal final-head focused success, `mc1-static`, distinct
technical/source review of that exact head, expected-head-protected merge,
reviewed/synthetic/landed tree identity, and merged-main focused/static success.
