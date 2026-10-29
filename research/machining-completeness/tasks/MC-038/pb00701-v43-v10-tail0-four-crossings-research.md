# MC-038 / PB-007-01 — V10 tail0 V43 refusal: four exact simple crossings

**29 October 2026 · DETERMINISTIC_MODEL · source-bound research only · [issue #100](https://github.com/techrote/radiCADSAC/issues/100)**

## Hypothesis, source custody and falsification

Examine **one** historically V43-refused second source span from the frozen 121-case v54 archive. Its original constant harmonic amplitude should have four simple physical crossings despite its historical `CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED` refusal. This is not a general V43 root-order theorem or a revised v54 disposition.

- Original corpus: `research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json`, Git blob `5841c331579489b25caef38cd412bdbf286f9134`.
- Exact case: `composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0`.
- First physical span `[0,1]`: historical V10 owner `CERTIFIED`.
- Second physical span `[1,2]`: historical V43 owner `BLOCKED` with `CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED`.
- Historical whole-case disposition: `BLOCKED`. Total original V43 refusals: **11** (one harvested, ten composite).
- Reviewed source-only clamped B-spline lowerer: `verify_pb00701_v43_refusal_cone.py`, pinned Git blob `2a8079ee2cf012bc2a12794c4c5ff19ebd760007`. Not an independent B-spline codec.
- Base authoritative main: `71b2f95c662ab3d7fcb7f6dbbe0899835be3a102` (after accepted V10 `tail100` research PR #284).

Falsifiers include changes to original harmonic inventory, source identity, degree/knot/control values, physical continuity, half-turn phase offset/rate, historical owner/refusal, ordered root descriptors, crossing signs, or the nonpromotion controls. The verifier pins the complete frozen corpus and source helper, reconstructs original clamped source pieces on **both** spans, and rejects adversarial source/report mutations.

## Exact physical source

Exact affine lowering of the original `source-time-t` control record produces:

| Channel | Original [0,1] | V43-refused [1,2] |
|---|---|---|
| Cosine harmonic 0 | \(0\) | \(0\) |
| Cosine harmonic 1 | \(1\) | \(1\) |
| Sine harmonic 1 | \(1/2-s\) | \(-1/2\) |
| Phase turns | \(-1/2+2s\) | \(-1/2+2s\) |

The channels are continuous at the original source knot \(s=1\). On the refused second span, the function is

\[
F(s)=\cos(\theta(s))-\tfrac12\sin(\theta(s)),
\quad \theta(s)=2\pi(-\tfrac12+2s)=4\pi s-\pi.
\]

**The half-turn phase offset matters**: replacing it with zero changes endpoint signs and invalidates the source identity. This is the same trap diagnosed and preserved as negative evidence for adjacent `tail100` in [PR #284](https://github.com/techrote/radiCADSAC/pull/284), but `tail0` has four roots rather than one.

## Four-root completeness and exact ordered physical brackets

At \(s=1,5/4,3/2,7/4,2\), the phase \(\theta/\pi\) is exactly \(3,4,5,6,7\). Therefore

\[
(F(1),F(5/4),F(3/2),F(7/4),F(2))=(-1,+1,-1,+1,-1).
\]

To prove **complete** root count rather than infer roots only from endpoint signs, solve

\[
\cos\theta-\tfrac12\sin\theta=0
\quad\Longleftrightarrow\quad\tan\theta=2.
\]

Neither \(\sin\theta\) nor \(\cos\theta\) vanishes at a zero, so this equivalence does not divide by zero. Let \(\alpha=\arctan(2)\in(\pi/4,\pi/2)\), using strict tangent monotonicity on its principal quadrant. All and only zeros in the open phase range \((3\pi,7\pi)\) are

\[
\theta_k=3\pi+\alpha+k\pi,\qquad k=0,1,2,3.
\]

Their exact **source-coordinate identities** and rational isolating brackets are

\[
s_k=1+\frac{k}{4}+\frac{\arctan(2)}{4\pi},
\quad
1+\frac{k}{4}+\frac1{16}
<s_k<
1+\frac{k}{4}+\frac18.
\]

| Root | Exact strict rational source bracket | Physical event |
|---|---|---|
| \(s_0\) | \((17/16,9/8)\) | negative to positive |
| \(s_1\) | \((21/16,11/8)\) | positive to negative |
| \(s_2\) | \((25/16,13/8)\) | negative to positive |
| \(s_3\) | \((29/16,15/8)\) | positive to negative |

Because \(\theta(s)\) is strictly increasing, these identities transfer exact root order to the **original source parameter** without assuming a rational or algebraic source root. There are no endpoint roots and no additional roots between them.

All roots are **simple**. At a zero, \(\cos\theta=\frac12\sin\theta\) with \(\sin\theta\ne0\). Thus

\[
F'(s)=4\pi[-\sin\theta-\tfrac12\cos\theta]
=-5\pi\sin\theta\ne0
\]

at the root. Its sign alternates with \(k\), agreeing with the five exact sign cells.

This is a source-specific closed-form trigonometric argument supported by exact rational controls and standard inequalities; it is **not** a generic certified analytic-event solver, general polynomial root isolation or algebraic defining polynomial for the source coordinate. The script checks source identities and rational proof invariants rather than evaluating \(\arctan\) numerically.

## Independent fixed-degree tan-half chart cross-check

The exact second-span coefficients also yield the identity, where \(x=\tan(\theta/2)\),

\[
(1+x^2)F=1-x-x^2.
\]

The polynomial has discriminant \(5>0\) and hence two distinct real \(x\)-roots per full \(2\pi\) phase cycle. Over the original \(4\pi\) phase sweep there are two cycles, consistent with four physical crossings. This exact quadratic identity is checked using the separately lowered rational source coefficients. The phase window **crosses tan-half chart poles**, so the polynomial is only an independent analytic sanity check on the source-specific proof: it does not make the historical V6 pole-free certificate applicable across the entire interval or establish a new general composition route. Explicit report fields prohibit claiming such a cross-pole certificate.

## Reproduction and negative controls

Run from repository root:

`python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v10_tail0_crossings.py --contract --self-test`

The contract checks frozen corpus/lowerer Git blobs, 121 source cases, 11 historical V43 refusals, 26 machining operations, MC-B and MC-1 `NOT_ESTABLISHED`, and false production authorization. The self-test checks original clamped B-splines, both-span continuity, exact phase and quarter-point signs, four disjoint strict brackets, simple alternating crossing events, and rejects source/knot/phase/owner/disposition/root-order/bracket/sign/nonpromotion mutations. Replaying output is source-specific; it is not an independent general theorem proof.

CI is `.github/workflows/mc1-pb00701-v43-v10-tail0-crossings.yml`, with literal PR-head checkout and merged-main path triggers. Require exact-head focused and `mc1-static` success, distinct technical/proof review, expected-head-protected merge, literal/synthetic/landed tree identity and merged-main checks. Preserve negative logs and source identities.

## Boundary of acceptance

The first-span V10 `CERTIFIED` result is **not composed** with the second-span research. Historical v54 `BLOCKED` dispositions and the 43-owner inventory are unchanged. Nothing proves general V43 certification, V27/V41 nested child composition, universal analytic zero isolation, topology, B-rep reconstruction, positive-volume material, lineage, canonical operation journal, source/provenance/phase semantics, typed refusal/`UNCERTIFIED` semantics or conventional engineering STEP. The 26-operation domain remains intact.

PB-007-01/02/03/04 remain `OPEN`, MC-B/MC-1 remain `NOT_ESTABLISHED`, production and expensive/native runs remain unauthorized. No successor issue or new production repository is created. The bounded result may be accepted as **research** only after review, not used to promote capability.
