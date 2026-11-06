# MC-038 / PB-007-01 — constant-phase-frame obstruction on two frozen originals

**Date:** 6 November 2026. **Classification:** bounded source-matched **negative C** against one precisely specified shortcut; research verification and independent admission required. **Evidence:** `DETERMINISTIC_MODEL`. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Coordination/preregistration:** [#324/6683345021](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6683345021). **Initial exact main:** `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.

## Proposed route and falsifiable scope

**Proposed shortcut:** `ONE_GLOBAL_CONSTANT_PHASE_SHIFT_ELIMINATES_H1_SINE`. To make the sine-bearing original first-harmonic inputs directly admissible to the sine-free grammar of the separate [#397 two-span moving-square proof](https://github.com/techrote/radiCADSAC/pull/397), choose **one constant real phase-origin shift**, optionally combined with a constant phase reversal, across an entire original source. Preserve source time, actual B-spline amplitudes, true source knots, and physical phase correlation, and re-express the original (C_1(t)\cos\theta(t)+S_1(t)\sin\theta(t)) as an H1 cosine term without an H1 sine channel.

The falsifier is a pair of actual original-source times at which the exact H1 coefficient vectors ((C_1(t),S_1(t))) have **nonzero determinant**. Any single global constant orthogonal phase-frame transform maps both vectors invertibly, preserving nonzero linear independence; the two transformed vectors cannot both lie on the one-dimensional cosine axis. A changed original source, phase/knot/source identity, non-orthogonal substitution, incorrect determinant, or unsupported source grammar invalidates the proposed C certificate and must be refused.

This is a challenge of a **hypothetical shortcut**, not a claim that PR #397 actually implements it. It does **not** exclude nonconstant coefficient-dependent rephasing, a more expressive polynomial/trigonometric theorem, a legitimate source-preserving factorization, or the general analytic event theorem. A nonzero determinant says nothing by itself about physical root count, multiplicity, parity, sign cells or physical zero identities.

## Original source custody and exact derivation

Frozen V54 source corpus Git blob `5841c331579489b25caef38cd412bdbf286f9134`; complete fifty-original V2 evidence register Git blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`. Their 121 and 50 unique IDs, v54 classifications and every V2 source/whole-row SHA-256 binding are rechecked by the executable against these pinned inputs. The old historical refused and ordered-premise records remain immutable.

**Original 1 — an actual missing ordered-premise source:**

- `composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0`
- Canonical source SHA-256 `4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2`; full-row SHA-256 `406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279`.
- Original source time ([0,2]), physical knot at (t=1), global affine phase **turns** (t/8). No sine-harmonic suppression is authorized.
- On its *original first piece* ([0,1]), exact degree-one Cox–de Boor extraction of the original H1 controls gives (C_1(t)=t-1/2,;S_1(t)=1). H0 is exactly zero. At original times (t=1/4,3/4), the vectors are ((-1/4,1)) and ((1/4,1)). Their exact determinant is (-1/2\ne0).
- Frozen v54 disposition: `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE`. This **historical owner gap is not closed** by the present negative method result.

**Original 2 — an actual uncertified historical route:**

- `harvested:verify_pb00701_v9:4e7b85fa122a`
- Canonical source SHA-256 `a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10`; full-row SHA-256 `62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad`.
- Original source time ([0,1]), one fully clamped degree-one B-spline piece and **no true interior knot**, phase turns (t/8).
- H1 controls give (C_1(t)=1,;S_1(t)=t-1/2). At (t=1/4,3/4), exact vectors are ((1,-1/4)) and ((1,1/4)). Their exact determinant is (+1/2\ne0).
- Frozen v54 disposition: `BLOCKED`, original V43 correlated handoff not certified. V2 already contains a complete source-specific witness; this is **not** a newly solved case.

These two source records are distinct in provenance, source interval, true knot semantics and historical failure class. Both have nonconstant H1 **orientation** even though each individual coefficient is rational-polynomial in original time.

## Mathematical proof of bounded C

Let (	heta(t)=2\pi\beta(t)), (v(t)=(C_1(t),S_1(t))^\top), and (R) be the real (2\times2) orthogonal matrix of a single constant phase shift, or a constant phase reflection followed by a shift. Rewriting (cos\theta,sin\theta) in the new constant frame transforms coefficients to (v'(t)=Rv(t)) (or its inverse; both have (det R=\pm1)). If the transformed H1 sine coefficient vanished for every original time, the second component of **both** (v'(t_0)) and (v'(t_1)) would be zero. Thus

\[
  0=\det[v'(t_0),v'(t_1)]
   =\det(R)\det[v(t_0),v(t_1)].
\]

Since (det(R)\ne0), this requires the original coefficient-pair determinant to be zero. But the exact determinants computed from two genuine source values are (-1/2) and (+1/2), respectively. Contradiction for **every** real constant phase shift/reflection, not only rational angle choices. The exact witness is finite and deterministic, with no sampling-based inference of root completeness or numerical trigonometric evaluation. Two exact evaluations suffice to falsify a universal algebraic identity.

**Why this is not more:** A zero two-sample determinant would be inconclusive: hidden rotation of coefficients between samples is possible. This checker never certifies an affirmative sine-free conversion from a zero determinant. Nothing here proves a source physical zero, evaluates a tangency, or treats the 121-case corpus as representative of all machinable shapes. The existing complete V2 signed witnesses stay registered and do not become new closures.

## Executable original-source contract and adversarial controls

Run on a checked-out repository at this branch head:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_constant_phase_frame_obstruction_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

The checker reads at most 300,001 and 220,001 bytes of V54/V2 source JSON, first checks Git blob pinning and duplicate/nonfinite-key refusals, rehashes the complete V2 selected-original bindings with SHA-256, and uses rational Cox–de Boor evaluation with degree/control-count/bit budgets. The machine receipt (64 KiB ingress cap) must match the entire freshly recomputed result using type-preserving canonical JSON.

Positive/negative/adversarial cases exercise both pinned originals, exact (2^{-120})-separated source-time witness positions, source/phase/parameter mutations, rank-zero constant/identity-zero controls (inconclusive, **not positive admission**), duplicate JSON keys, nonfinite JSON, oversized receipt, false 30→28 historical tally and false production authorization type aliases. No root-count, tangency, repeated-root, continuum, endpoint-multiplicity or sign/parity claim is derived from a coefficient-frame rank witness; these remain under the independently recorded V2 source-specific proof and the OPEN generic theorem. Budget exhaustion is a **nontruth refusal**, never a decision about roots. Runtime is linear in 121+50 JSON provenance checks plus two small rational spline evaluations per original; no native geometry or paid campaign.

The original complete-source V2 producers and older V54 raw failures are replayed separately, not replaced by a saved JSON receipt. Exact-head hosted CI and independent source/machine admission are required before any integration. Same-session COMMENT review is not external-human APPROVED. The separately held #397 main integration lock prohibits merge in this run.

## Recomputed matched historical census

| Exact pinned population / status | Before | After | Delta |
|---|---:|---:|---:|
| Frozen V54 originals | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | **0** |
| Preexisting V2 complete source witnesses | 50 | 50 | 0 |
| Required PB/PO obligation discharges | 0 | 0 | 0 |

New historical closure IDs: **none**. The two source IDs are **negative route challenge anchors**, not newly solved physical geometry. Evidence class `DETERMINISTIC_MODEL`, not native geometry, independent oracle or engineering STEP. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN, MC-B and MC-1 remain `NOT_ESTABLISHED`. All 26 supported operations, durable body identity, topology, source/phase, journal, source provenance, genuine STEP and consumer gates remain mandatory. No production repository, budget or domain contraction is authorized.

**Next critical-path research:** a genuinely orientation-preserving, nonstationary, sine-bearing original-source event-order/sign-transfer theorem or a narrowly proved transformation with explicit source/knot/multiplicity/termination semantics, independently qualified against historical cases. The constant-phase-only workaround is ruled out for these two originals. 
