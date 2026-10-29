# MC-038 / PB-007-01 — exact rational-phase point events in polynomial-modulated trigonometric spans

**Status:** bounded research candidate, 29 October 2026. **Evidence class:** deterministic model, not native geometry. **Owner:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Selection, falsifiers and source custody:** [checkpoint #6506353313](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6506353313). Research-only result; no shared authority/registry/frozen v54 edits.

## Purpose and admitted grammar

Complement the general *simple transverse open-root* interval checker of [PR #296](https://github.com/techrote/radiCADSAC/pull/296) and the *pure constant-harmonic tangency* half-angle checker of [PR #297](https://github.com/techrote/radiCADSAC/pull/297). Given a rational source coordinate s0 and one already-lowered **rational polynomial-modulated finite-harmonic** span, prove whether F(s0) is nonzero or, if it is zero, its exact finite vanishing order and inward/outward signs. This includes rational endpoints and source knots of the original pinned V27/V41 B-spline sources.

A span is F(s) = sum_h [P_h(s) cos(2*pi*h*(a+b*s)) + Q_h(s) sin(2*pi*h*(a+b*s))], for rational a,b and rational polynomial coefficients, h<=8 and degree<=3. It uses the exact source parameter, never an arbitrary chart coordinate. The underlying Span constructor enforces bounded rational grammar, domain and harmonic count. This new checker imposes a cyclotomic order <=48 and a derivative-jet order <=10; missing proof before the limit is **RESOURCE_REFUSAL**, not a source-is-root or source-is-not-root conclusion.

This is **point-local only**. It cannot enumerate every open root, prove global zero-set completeness, compare arbitrary irrational cross-owner implicit roots, certify child compositions or authorize a native STEP/B-rep implementation.

## Exact algebraic vanishing theorem

At rational s0, each harmonic phase turn h*(a+b*s0) is rational, with denominator q. Set N=lcm(4, all required q) and zeta=exp(2*pi*i/N). Work in the exact number field Q[x]/Phi_N(x), where Phi_N is recursively derived as (x^N-1) divided by all lower cyclotomic factors. The quotient represents zeta by x, and i=zeta^(N/4).

For phase angle with zeta exponent k, compute exactly in that field:

- cos(theta) = (zeta^k+zeta^(-k))/2;
- sin(theta) = -(i/2)*(zeta^k-zeta^(-k)).

The m-th original-source derivative at s0 is a finite polynomial in pi. For each j=0..m and k=m-j, the Leibniz term has coefficient binomial(m,j)*(2*h*b)^k times the j-th derivative of P_h or Q_h at s0 and the k-th quarter-turn cyclic shift of cosine or sine. Every coefficient of each pi^k is **algebraic**. Since pi is transcendental over the algebraic numbers, a polynomial in pi with algebraic coefficients is zero **if and only if every coefficient is exactly zero**. Exact cyclotomic reduction and rational arithmetic therefore prove all derivative-vanishing tests before the first nonzero derivative, without floating-point equality guesses.

Once the first nonzero derivative order m is established, a separate exact-rational interval evaluation uses the Machin pi bounds and Taylor/Lagrange trigonometric enclosures from the source-independent [#296 interval engine](https://github.com/techrote/radiCADSAC/blob/main/research/machining-completeness/tasks/MC-038/pb00701_transverse_trig_interval.py). A **strict interval sign** is mandatory. If it remains ambiguous, refuse. If proved, the zero has exact one-sided analytic order m: the right sign equals sign(F^(m)(s0)), and the left sign is (-1)^m times the right sign. A nonzero F(s0) is a point nonroot. The proof does not infer global root counts.

For true source knots, verify a common exact rational coordinate and phase, then exact equality of the **actual function values** in the same cyclotomic field. If both vanish, count exactly one physical zero with separate left/right one-sided orders and sign transfer. Unequal orders must **never** be combined into an invented global smooth multiplicity. Equal signs at nonzero knots alone do not suffice for continuity. The original-source bridge separately verifies pinned B-spline channel continuity.

## Reproduction, cases and falsification

Run on a checked-out repository:

~~~sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_rational_phase_point.py --contract --self-test
~~~

Tests exercise cyclotomic Q[x]/Phi_4 and Phi_12 identities, exact polynomial derivatives, first-order cos crossing at s=1/4, order-two sin-squared tangent at s=0, polynomial-modulated order-two and order-three zeros at s=1, an unequal-order 2/1 crossing at a real source knot, same-order touching, nonzero knot, discontinuity and phase mismatches, identity zero, resource caps, forged-result rejection and pinned V27/V41 original-source rational endpoint and knot replay. The latter reuses source/provenance validation and B-spline lowering but **not** historical V27/V41 child root counts or prior proof conclusions.

Read-only custody pins include:
- frozen 121-case v54 original-source corpus Git blob: 5841c331579489b25caef38cd412bdbf286f9134;
- full 26-operation MC-002 domain Git blob: 23de82f5240a72509f7afe4acd5948b65bc4ff13;
- current-authority Git blob: fa0233323a0804d8a5d3eb7cd892a274a6173fab;
- original V27/V41 exact source/proof validators and the V43 refusal evidence under the already-pinned #296 original-source binder.

A caller's source identifier or hash is not authority: exact source provenance must be independently checked. A submitted point-event report is replayed from source; changing a sign, order, claim or SHA is refused.

## Nonpromotion and next gap

This advances an exact **rational-point** primitive, including polynomial-modulated phases, not a full mixed-owner physical-root theorem. Nonrational implicit open roots, distinct-source coincidence comparisons, complete tangent-root isolation on an open interval, and whole-source child consumption remain unproved. The fixed V27/V41 cases can have nonzero rational knots and still require missing open-root premises. Preserve their original historical BLOCKED dispositions and all negative evidence.

MC-B/MC-1 remain NOT_ESTABLISHED, production_authorized=false. Neither PB-007-01 nor native material/topology, conventional B-rep/usable engineering STEP, canonical manufacturing journal, operation phase, material, body, lineage, refusal or UNCERTIFIED requirements change. The 26-operation lathe/mill domain stays intact. No new issue, paid/native permit or production repository is implied.
