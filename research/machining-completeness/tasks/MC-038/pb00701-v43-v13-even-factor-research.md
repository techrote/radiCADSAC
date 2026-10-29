# MC-038 / PB-007-01 — frozen V13 nonvanishing even-multiplier V43 refusal

**Date:** 29 October 2026. **Scope:** deterministic exact original-source mathematics for **one** historical V43-refused physical span, not a new V43 certificate, owner integration or capability verdict. **Parent:** [issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** `bbbc8f8c9b565cd7d1cd063fc65654f57e2f8bf1` (merged #287).

## Source custody and frozen nonclaims

Read-only frozen `pb00701-finite-owner-corpus-v54.json` Git blob `5841c331579489b25caef38cd412bdbf286f9134`, 121 original cases including 11 historical V43 refused spans. The selected source is `composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0`, provenance `verify_pb00701_v13`. It retains first-span `PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC` **CERTIFIED** and second-span `PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF` **BLOCKED:CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED**; whole v54 case **BLOCKED**.

Original source grammar `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`; source parameter `source-time-t` on [0,2]; affine phase turns `s/4`. Harmonic-zero cosine is zero; first and third cosine/sine harmonics use fully clamped degree-1 Bernstein pieces at the physical knot s=1, with exact first-piece and second-piece polynomials:

| Harmonic coefficient | Original [0,1] polynomial | Original [1,2] polynomial |
|---|---|---|
| C0 | 0 | 0 |
| C1 | −5/6+(5/2)s | 5/3 |
| C3 | −1/6+(1/2)s | 1/3 |
| S1 | 1−(3/2)s | −1/2 |
| S3 | 1/3−(1/2)s | −1/6 |

Every original channel is continuous at s=1; the accepted exact degree-0/1 source-lowering helper Git blob `2a8079ee2cf012bc2a12794c4c5ff19ebd760007` checks each polynomial and knot. This research shares its source-lowering assumptions; it is **not** an independent full B-spline codec or general historical owner theorem.

## Exact trig factorization and strict sign

On original second physical span s∈[1,2], set θ=πs/2∈[π/2,π], c=cosθ≤0 and v=sinθ≥0. The exact source function is

\[
F(s)=\frac53\cos\theta+\frac13\cos(3\theta)
-\frac12\sin\theta-\frac16\sin(3\theta).
\]

Using cos3θ=4c³−3c, sin3θ=3v−4v³, and v²=1−c², exact rational coefficient reduction gives

\[
F(s)=\frac23c+\frac43c^3-\frac13v-\frac23c^2v
=\underbrace{(1+2c^2)}_{\text{strictly positive}}\,
 \underbrace{\frac{2c-v}{3}}_{\text{strictly negative}}.
\]

For u=−c≥0 and v≥0 with u²+v²=1, the identity
\((2u+v)^2-(u^2+v^2)=3u^2+4uv\ge0\)
establishes 2u+v≥1 **on the entire closed quadrant**. The even multiplier lies in [1,3]. Thus

\[
\boxed{F(s)\le-\frac13<0\quad\text{for every }s\in[1,2].}
\]

There are **zero** open or endpoint physical roots on that second span, with one complete negative sign cell. The sign conclusion requires the **actual V13 first and third harmonics and positive multiplier**; it is not a replacement first-harmonic owner result.

## Genuine nonmonotonicity

Exact physical endpoints are F(1)=−1/3 and F(2)=−2. Differentiate the original harmonic expression with respect to θ:

\[
F_\theta=-\tfrac53\sin\theta-\sin(3\theta)
-\tfrac12\cos\theta-\tfrac12\cos(3\theta).
\]

At θ=π/2 and π, respectively, Fθ=−2/3 and +1. With dθ/ds=π/2, this yields

\[
F'(1)=-\pi/3<0,\qquad F'(2)=\pi/2>0.
\]

The source is not monotone on [1,2] and has an interior turning point. The historical V43 refusal is **not** a physical root existence theorem or a mathematical proof that F is monotone/nonmonotone. Our result classifies only the immutable original source, retaining the refusal unchanged.

## Reproduction, falsifiers and evidence class

Run on repository checkout:

~~~sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v13_even_factor.py --contract --self-test
~~~

Verifier requires: exact frozen corpus Git blob and 121 distinct identities; 11 unchanged historical V43 refusals; exact V13 original first/third harmonic B-spline channels, knots, phase, continuity and owner/disposition; rational triple-angle factor equality; strict quadrant sign inequality and endpoint derivative signs; 26-operation denominator; unchanged `NOT_ESTABLISHED` MC-B/MC-1 and disabled production authority. Its in-memory adversarial controls reject source/phase/knots/provenance/historical disposition changes, forged roots/signs/factor/margin/derivative and capability promotion.

**Evidence subtype:** deterministic case-specific exact-source research, not native geometry, an independent oracle, a generic zero-isolation solver, or a reusable V43 ordered-span proof object. Historical records are read-only. The verifier's exact replay comparator is intentionally case-specific; a successful mutation suite is not general algorithmic verification.

## Integration boundary

The research candidate owns only this memo, the verifier and focused GitHub Actions workflow. Exact-head focused and static CI, distinct final-head technical review, literal/merge tree identity, expected-head-protected merge and actual merged-main CI are required before acceptance. No historical v54 disposition is revised; no V13/V43 owner table, proof registry, gate/outcome, domain, task graph, source/canonical journal/material/body/lineage/refusal/`UNCERTIFIED`/conventional usable STEP policy changes.

PB-007-01/02/03/04 remain open. MC-B and MC-1 remain `NOT_ESTABLISHED`, production unauthorized. #275 stays closed. No native/paid campaigns, no successor issue. Additional V17/V16 correlated tails and V27/V41 child-composition premises require separate independently source-bound research.
