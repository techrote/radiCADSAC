# MC-038 / PB-007-01 — V17 exact positive nonmonotone original-source V43 refusal

**Date:** 29 October 2026. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** `876987d455429b0750d434e6a04e8bf4e1c92a5a` (accepted #288). **Evidence class:** deterministic exact original-source, one frozen case only; not a generic V43 event certificate, independent oracle, geometry kernel or MC-B/MC-1 evidence.

## Frozen source and provenance

Read-only original 121-case v54 corpus Git blob `5841c331579489b25caef38cd412bdbf286f9134` contains 11 historical V43 refusal spans. Selected case `composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0`, provenance `verify_pb00701_v17`. First [0,1] physical span is historically `PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER` **CERTIFIED**; second [1,2] span is `PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF` **BLOCKED:CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED**. The whole v54 disposition is **BLOCKED**. Neither the source nor historical result is edited.

Original grammar is `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`; parameter `source-time-t` lies in [0,2]; phase turns `s/4`. The original clamped degree-1 B-spline channels expand (independently checked via the pinned accepted degree-0/1 lowerer Git blob `2a8079ee2cf012bc2a12794c4c5ff19ebd760007`) to:

| Channel | Original [0,1] polynomial | Original [1,2] polynomial |
|---|---|---|
| C0 | 0 | 0 |
| C1 | 1−5s/2 | −3/2 |
| C3 | −1/3+s/2 | 1/6 |
| S1 | −3/2+5s/2 | 1 |
| S3 | −1/6+s/2 | 1/3 |

Each channel is continuous at the physical source knot s=1. This proof shares historical helper source-lowering assumptions, so it cannot qualify as an independent original-source codec.

## Exact sign proof and root count

On the original second span s∈[1,2], put θ=πs/2∈[π/2,π], c=cosθ, v=sinθ, and u=−c≥0. Then u²+v²=1 and u,v≥0. The original source expression, retaining both harmonic orders, is

\[
F(s)=-\frac32\cos\theta+\frac16\cos(3\theta)+\sin\theta+\frac13\sin(3\theta).
\]

With cos3θ=4c³−3c and sin3θ=3v−4v³, exact coefficient reduction gives

\[
F=-2c+\frac23c^3+\frac23v+\frac43c^2v
 =\frac23\left[u(3-u^2)+v(1+2u^2)\right].
\]

For 0≤u≤1 and v≥0, u(3−u²)≥2u and v(1+2u²)≥v. Since

\[
(2u+v)^2-(u^2+v^2)=3u^2+4uv\ge0,
\]

it follows that 2u+v≥1. Therefore, on the **entire closed physical source span**,

\[
\boxed{F(s)\ge\frac23(2u+v)\ge\frac23>0.}
\]

No open or endpoint roots exist; the complete second-span physical sign cell is POSITIVE. No rational or algebraic source-root coordinate has been invented.

## Genuine source nonmonotonicity

The original exact endpoint values are F(1)=2/3 and F(2)=4/3. Differentiation in θ gives Fθ(π/2)=2 and Fθ(π)=−2. Since θ'(s)=π/2, F'(1)=π>0 and F'(2)=−π<0. The function therefore has an interior turning point and cannot be monotone across [1,2]. The V43 correlated closed-handoff refusal is preserved rather than retrospectively reclassified.

## Reproduction and adversarial controls

Run in a repository checkout:

~~~sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v17_positive_turn.py --contract --self-test
~~~

The verifier requires the exact 121-case corpus blob and 11 original V43 refusals, full V17 first/second-span clamped B-spline controls, knots, continuity, source parameter and affine phase, unchanged historical owner/refusal/disposition, strict rational coefficient and quadrant inequality predicates, endpoint derivative signs, 26 required operations, MC-B/MC-1 `NOT_ESTABLISHED` and no production authority. Mutations reject changed source/provenance/knot/phase, removed/added harmonics, invented zeroes or signs, weakened lower margin, forged derivative/monotonicity and unsupported capability promotion.

**Falsifier:** any source mismatch or failure of the exact coefficient/strict sign/turning proof rejects the claim. Scope remains deterministic single-case classification; the checker replays a pinned source, not a generic V43 termination/child-composition theorem.

## Remaining proof and integration boundaries

Only three new isolated artifacts are owned: this RAG memo, the executable verifier, and its focused workflow. Require exact-head focused and static CI, distinct exact-head technical source/proof review, literal/synthetic tree match, protected merge, merged-main focused/static CI and an issue #100 durable checkpoint. Historical v54 dispositions, 43-owner inventory, source/phase/provenance/operation journal, material/body/lineage, refusal/`UNCERTIFIED`, 26-operation domain, conventional usable STEP, gate/outcome and production authorization are unchanged. PB-007-01/02/03/04 remain OPEN; MC-B/MC-1 remain `NOT_ESTABLISHED`; no native campaign, successor issue or #275 reopening.
