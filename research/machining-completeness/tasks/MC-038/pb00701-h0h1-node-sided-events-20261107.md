# MC-038 — exact octant-node, endpoint and same-law knot sided-event transfer

**7 November 2026 · restricted constructive theorem / executable deterministic model / research-only.** Issue [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100); ownership ledger [#324](https://github.com/techrote/radiCADSAC/issues/324). This is an **additive, stacked successor to #445**, not a replacement of its exact constant-H0/H1 open-octant theorem. The new Python file imports #445's rational/critical-sign helpers; its PR must have the #445 branch as base until that dependency is integrated. No authoritative main, frozen corpus, proof registry, programme, native geometry, STEP or production files are modified.

## Falsifiable hypothesis and mathematical contract

An exact rational-affine nonstationary phase on a rational interval defines
[
F(t)=h+C\cos(2\pi(u+rt))+S\sin(2\pi(u+rt)),\quad
h,C,S,u,r\in\mathbb Q,\quad r\ne0,\quad C^2+S^2>0.
]
At each exact octant node `u+rt=k/8`, both `F` and the **sign** of `F'` are decidable in `Q(sqrt(2))`. If a node has `F=0` but `F'!=0`, the node is one **simple** physical event. Its one-sided signs with respect to increasing source time are `-sgn(F')` (left) and `sgn(F')` (right), irrespective of increasing or decreasing phase.

If `F=F'=0` at a node, the root is exactly **order two**: since `q=C²+S²>0`, this means `h²=q`, `h!=0`, and `F''=(2*pi*r)²*h!=0`. Both local sided signs equal `sgn(h)`. Thus a tangency splits **two physical open nonzero components of the same sign**, whereas a simple crossing flips the sign.

For each **open** octant cell, replace any zero endpoint value by its exact sign **immediately inside** that cell, then invoke #445's certified one-critical-point interior count. This cannot create an artificial zero: the substituted sign is justified by a nonzero first or second Taylor coefficient, and every nonzero cell endpoint remains unchanged. The cell still has at most one stationary point since its angular length is exactly pi/4, and strict two-root same-cell ambiguity continues to **REFUSE_NONTRUTH**, not report absence.

A physical zero at the boundary between two octant cells is emitted **once**, after the left open cell, before the right open cell. A zero at a source exterior is classified separately as `left_boundary_event` or `right_boundary_event` rather than as an interior event. This prevents inventing an exterior second region. An interior octant node event carries exact rational time; an interior non-node event carries only a strict rational *open bracket*, not a fabricated rational root coordinate. The event-separated open-region sequence always has `len(ordered_interior_events)+1` entries.

## True B-spline knot composition — deliberately restricted

The helper `certify_identical_law_knot(left,right)` accepts **only** two adjacent source spans with **identical rational H0, H1 cosine/sine, phase offset and phase rate**. It separately certifies each span; requires the exact shared boundary event (or its absence) and sided signs to match; and recomputes the whole-source proof as an independent compositional equality. Any coefficient/phase mismatch, nonadjacency or side inconsistency **refuses**. It does not certify a general piecewise-constant discontinuity, nonconstant B-spline amplitude, altered phase or mismatched knot derivative.

This is an actual source-time knot boundary, not a grid line invented in place of the original source. The current positive historical fixture is the **unchanged frozen V6 original** `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0`:

- Original SHA-256 `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1`, row SHA-256 `145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc`.
- Frozen original source time `[0,2]`, **true degree-zero spline knot `t=1`**, cosine H0=0 on both spans, cosine H1=1 on both spans, no sine channel, phase turns `t/4`.
- Therefore the **full original** is `F(t)=cos(pi*t/2)`. Its exact knot `t=1` is one simple zero with `F'(1)=-pi/2`; the ordered signed open regions are POSITIVE then NEGATIVE.
- The earlier strict-node PR #445 correctly **refused this exact original**; the new restricted node-aware proof admits it. **However V6 already has a COMPLETE_SOURCE_SPECIFIC V2 witness. This is a new generic interface/admission, NOT a newly closed historical case or an outstanding PB/PO discharge.**

The prospective C/S and H0 values tested in this successor do not modify or replace the 121 immutable originals.

## Adversarial controls and resource truth policy

The executable has **13 focused tests**: full original pinned V6 knot proof and existing V2 witness; simple left and right exterior zeros; two exterior zeros; interior order-two node tangency; exterior order-two tangencies; negative phase; unchanged V12 strictly negative root-free tail; same-octant hidden two-root refusal; cross-knot law mismatch/nonadjacency refusal; nonzero derivative endpoint without physical zero; preservation of #445's deliberate original V6 refusal; and a genuine `2^-300` near-exterior simple crossing that must **not** be rounded to a node.

All input rational/byte/nesting/canonicalization checks are inherited from the separately validated #445 exact helper. The successor adds no floating-point decisions or scans and inherits its 512-bit input / 2048-bit derived arithmetic and 128-cell admission budget. Resource exhaustion and unsupported source grammar are typed NONTRUTH refusals, never proofs of root absence. The original source is fetched only through #445's Git-blob-verified bounded V54/V2 readers, and both source and full row SHA-256 identities are checked.

## Evidence boundaries and downstream contracts

This is `DETERMINISTIC_MODEL`, and the new full-original V6 event certificate **does not upgrade historical evidence status**: 121 original sources, 20 historical route refusals, 30 historical missing ordered premises, 50 existing complete V2 source witnesses, all delta zero. No new historical case closed; PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN. MC-B/MC-1 remain `NOT_ESTABLISHED`. All 26 mandatory supported operations, native geometry, material topology, independent STEP export and production authorization remain unchanged.

Limitations: nonidentical source laws at a knot, source jumps, arbitrary nonconstant H1/H0, multi-harmonics, general analytic isolation, identity-zero intervals, and parent #445's same-octant two-root unbracketed case are **not admitted**. A general owner-to-consumer sided-order theorem for discontinuous higher derivatives remains future work.

Reproduce on the **literal stacked branch head**:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_h0h1_node_sided_events_20261107.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

Dedicated workflow `mc1-pb00701-h0h1-node-sided-events.yml` checks all three on exact PR head. Keep Draft/unmerged until a **different session independently rederives the sided-event proof**, checks true knot custody, import dependency, raw CI and certificate integrity. Any future merge is controlled exclusively by #397's main-integration lane after explicit release and exact-head requalification. No human authorization to create production repositories is implied.
