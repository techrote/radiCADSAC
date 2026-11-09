# MC-038 — compose exact first-harmonic octant cells with rational two-root pivots

**9 November 2026 · research-only / DETERMINISTIC_MODEL · Draft until independent source-critical review · DO NOT MERGE INTO MAIN.**

## Task and source custody

This is an additive, *stacked* research contribution on the accepted/reviewed but unmerged constant-H0/H1 octant certificate [#445](https://github.com/techrote/radiCADSAC/pull/445), head `ce9f4fd7bc5dec83fb5301977499e0ae001e54d8`. The independent exact two-root rational-pivot theorem [#464](https://github.com/techrote/radiCADSAC/pull/464), head `7389210bd746d1ce824842b9df54b17b71a176eb`, is imported byte-for-byte: its Python theorem, JSON witness, RAG report and workflow retain their original Git blob SHA-1s. Both foundations remain unchanged. Existing knot-node successor #446 is independent and not edited. #397 alone controls accepted-main integration.

The new adapter is `pb00701_octant_pivot_composition_20261109.py`. The original #445 verifier is `pb00701_constant_h0_h1_octant_20261106.py`, and the imported #464 witness is `pb00701_octant_two_root_witness_20261109.py`. Both are imported **as executable proof dependencies**, not copied/rewritten into a new unreviewed algorithm. The adapter is a proof-composition and consumer contract, not a new physical root finder.

## Precise mathematical claim

For rational constant `h,C,S` with `C²+S²>0`, a nonzero rational affine phase `2π(u+r t)`, an admitted source-time interval partitioned into exact octant cells, and optional caller-provided **canonical rational** pivots, construct a complete span-level ordered event and event-separated open-region certificate *if and only if each octant can be admitted by one of two independently verified sufficient paths*:

1. **Parent #445:** invoke its original `certify` on the exact one-octant subspan. It provides no roots, one simple crossing or one exact interior order-two tangency. Its `PHYSICAL_OCTANT_NODE_ZERO`, non-octant, resource-budget and other typed refusals remain refusals.
2. **Witness #464, only on the precise parent `TWO_ROOTS_SAME_OCTANT_UNBRACKETED` refusal:** require an extra rational interior pivot whose physical sign is strictly opposite to both endpoint signs. The imported exact Machin/Taylor rational enclosures and its verified source-bound receipt establish precisely two **simple** roots, one strictly inside each disjoint open rational interval `(left,pivot)` and `(pivot,right)`. This uses the intermediate value theorem twice and the fact that successive first-harmonic stationary points are separated by π, whereas an octant spans π/4; Rolle excludes any third or multiple root.

The generated child receipts and exact source-time cell boundaries are preserved in the composite receipt. Every child end sign must equal the next child start sign; no octant-node boundary is a root (both existing child engines refuse a zero there). Append open-region signs only at physical events, never at empty octant boundaries. A crossing reverses sign; a tangency separates two open components of the **same** sign. Strict brackets must remain source ordered without positive-length overlap; adjacent brackets may meet at a certified nonzero rational pivot. The resulting invariant is `len(ordered_signed_regions) = root_count + 1`.

### Motivating witness and executable result

Prospective `h=199/200, C=-3/5, S=-4/5, u=r=1/8, t∈[0,2]`:

- On the first octant `[0,1]`, #445 refuses two hidden same-octant roots. The additional rational pivot `t=1/4` has strictly negative physical value while `t=0,1` have strict positive values. #464 certifies one simple root in `(0,1/4)` and one in `(1/4,1)`.
- The second octant `[1,2]` has no physical root and a positive sign. #445 certifies this without an additional pivot.
- The composite emits exactly **two** ordered simple events, physical open-region signs **POSITIVE / NEGATIVE / POSITIVE**, and retains both child certificates. There are **three** maximal physical sign components, *not four* from the artificial phase grid.

Negative phase orientation, sign-mirrored maximum, exact order-two tangency, a root-free historical V12 tail, malicious receipt substitution and the V6 physical knot-node refusal are regression cases.

### Refusal and falsification discipline

- No pivot means no fallback from #445's two-root refusal.
- A supplied pivot is not an invitation to reinterpret an already admitted cell: **unneeded** pivots refuse; out-of-cell, incorrectly signed and numerically undecidable pivots refuse.
- Input source, phase rate, interval/domain, exact octant alignment, rational canonicality, cell budget and parent node-zero exclusions remain no broader than #445.
- All nested source/certificate fields are replayed. The outer receipt is reconstructed from immutable canonical source/pivot fields and compared *type-sensitively* as serialized JSON. Forged event counts, signs, branch/cell proof, hashes and capability claims fail closed.
- Extremely close two-root configurations can still refuse when #464's strict dyadic outward bound or Taylor precision does not establish the pivot sign. Refusal is **NONTRUTH**, never an assertion of zero roots.
- The test intentionally retains the frozen V6 `cos(πt/2)` simple zero at a *true* knot/octant node as REFUSED. #446 is the separately owned knot-node research path.

The parent's entire-span certificate could refuse because one subspan is unproved; the composite does not use an unproved prefix or a saved overall assertion as a substitute. It independently invokes the parent theorem on every individual cell, then allows the new witness only on the exact eligible refusal.

## Reproducibility / qualification

From repository root, on the literal PR head:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_octant_pivot_composition_20261109.py --self-test --contract
python3 research/machining-completeness/tasks/MC-038/pb00701_constant_h0_h1_octant_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/pb00701_octant_two_root_witness_20261109.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

Dedicated `mc1-pb00701-octant-pivot-composition.yml` checks both Ubuntu and Windows theorem/adversarial tests and invokes the unchanged inherited parent suites, full producing original V54/V2 reconciliation and repository MC-1 static validation. Record actual exact-head CI results before advancing from Draft. A separate subsequent-session mathematical/source review is required to admit the composition; passing CI is insufficient alone.

## Historical baseline and decision

The immutable historical census remains **121 originals, 20 blocked routes, 30 missing ordered premises, 50 previously complete V2 original-source witnesses**, with every delta **zero** and no newly closed original source. No required PB-007-01/02/03/04 or PO-02/04/05/07/08 obligation is discharged. MC-B and MC-1 remain `NOT_ESTABLISHED`. No general varying-amplitude/weighted NURBS/event oracle, source-knot coverage, arbitrary pivot discovery, body/topology/journal semantics, independent native geometry, STEP output, manufacturing acceptance or production authorization is claimed. All 26 required operations remain unchanged.

This is a strictly bounded positive **compositional mathematical research result**, not accepted programme capability or original-source A/B/C closure. Follow-on use requires #397's dependency-ordered integration decision and new merged-head qualification.
