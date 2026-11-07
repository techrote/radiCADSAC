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

The generic helper `certify_identical_law_knot(left,right)` accepts **only** two adjacent time intervals with **identical rational H0, H1 cosine/sine, phase offset and phase rate**. It separately certifies each interval, checks matching one-sided physical values/signs, and recomputes the whole-source event proof. Any coefficient/phase mismatch, nonadjacency or sign inconsistency **refuses**. **Matching laws and adjacency do not prove that the join is an actual original-source spline knot.** Generic output is therefore `COMPLETE_RESTRICTED_SAME_LAW_TWO_SPAN_JOIN` with `unverified_same_law_join`, without any `true_source_knot` field. The original V6 wrapper alone upgrades to `COMPLETE_RESTRICTED_SAME_LAW_TWO_SPAN_KNOT` and emits `true_source_knot=1`, but only **after** its exact immutable spline controls, knot vector, source and row hashes are checked. This neither certifies general discontinuous sources, nonconstant B-spline amplitudes, altered phases nor mismatched-knot derivative germs.

The V6 positive witness has an **actual source-time knot**, rather than an artificial phase-grid line. The current positive historical fixture is the **unchanged frozen V6 original** `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0`:

- Original SHA-256 `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1`, row SHA-256 `145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc`.
- Frozen original source time `[0,2]`, **true degree-zero spline knot `t=1`**, cosine H0=0 on both spans, cosine H1=1 on both spans, no sine channel, phase turns `t/4`.
- Therefore the **full original** is `F(t)=cos(pi*t/2)`. Its exact knot `t=1` is one simple zero with `F'(1)=-pi/2`; the ordered signed open regions are POSITIVE then NEGATIVE.
- The earlier strict-node PR #445 correctly **refused this exact original**; the new restricted node-aware proof admits it. **However V6 already has a COMPLETE_SOURCE_SPECIFIC V2 witness. This is a new generic interface/admission, NOT a newly closed historical case or an outstanding PB/PO discharge.**

The prospective C/S and H0 values tested in this successor do not modify or replace the 121 immutable originals.

## Independent 7 November source-provenance falsifier and corrected contract

**Falsifiable route (bounded C):** “Equality of constant H0/H1/phase laws on adjacent rational octant-aligned input intervals proves the join is an authentic *original-source B-spline knot*.” This statement is false. It is not a counterexample to the event-count or sign-transfer theorem.

Use the **same true frozen V6 source law** `F(t)=cos(pi*t/2)` on `[0,2]`, but submit two generic lawful intervals `[0,1/2]` and `[1/2,2]` (or `[0,3/2]` and `[3/2,2]`). Each fake join is exactly an octant phase-grid node and both laws are identical. The previous implementation accepted and emitted `true_source_knot="1/2"` (respectively `"3/2"`) even though the frozen V6 original degree-zero cosine H0/H1 spline knot vectors are **[0,1,2]**, so neither `1/2` nor `3/2` is an original internal knot. This is a precise source-provenance falsifier, not a new physical zero: both fake partitionings correctly retain the single root t=1, of multiplicity one, and POSITIVE/NEGATIVE open signed regions, already proved in V2.

**Repair:** a generic exact same-law **join** still admits physical ordering but must not assert source-knot custody; it emits `unverified_same_law_join` and no `true_source_knot`. Only `original_v6_contract()`, after exact frozen full-spec and canonical-row SHA-256 checks, upgrades the authentic join t=1 into `true_source_knot`, attaches `verified_original_source_sha256` and `verified_original_row_sha256`, and retains the original physical event theorem. Two false-knot adversaries, one authenticated true-knot positive and all previous root/tangency/endpoint/nontruth controls are included. The correction does not validate arbitrary caller-provided spline provenance. No historical case, generic owner or required PB/PO is discharged.

Machine before/after record: [pb00701-h0h1-false-knot-provenance-20261107.json](pb00701-h0h1-false-knot-provenance-20261107.json). Independent [source-critical HOLD](https://github.com/techrote/radiCADSAC/pull/446#pullrequestreview-5809324633) applies to the **pre-repair head** and remains preserved. Corrected literal-head CI and a distinct-session independent re-review are required before admission.

## Adversarial controls and resource truth policy

The executable has **14 focused tests**: full original pinned V6 knot proof and existing V2 witness; simple left and right exterior zeros; two exterior zeros; interior order-two node tangency; exterior order-two tangencies; negative phase; unchanged V12 strictly negative root-free tail; same-octant hidden two-root refusal; cross-knot law mismatch/nonadjacency refusal; nonzero derivative endpoint without physical zero; preservation of #445's deliberate original V6 refusal; and a genuine `2^-300` near-exterior simple crossing that must **not** be rounded to a node.

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
