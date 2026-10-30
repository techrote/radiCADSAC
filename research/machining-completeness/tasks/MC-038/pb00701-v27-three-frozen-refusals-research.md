# MC-038 / PB-007-01 — three frozen original-source V27 refusals: exact physical events

**Date:** 30 October 2026. **Status:** bounded, source-bound mathematical research pending exact-head review/CI. **Evidence class:** DETERMINISTIC_MODEL. **Owner:** [MC-038/#100](https://github.com/techrote/radiCADSAC/issues/100). **Scheduswarm claim:** [#324](https://github.com/techrote/radiCADSAC/issues/324). **Starting authoritative main:** 0b0e5231335e1e88e0b5a29f23c11343779090a3, after reviewed/landed PR #323.

## Question and strict scope

The immutable v54 121-source corpus records four source cases with the exact reason V27_CHILD_NOT_CERTIFIED. PR #323 independently proves one of them, the V6 tail100 touching-knot source, but correctly does not repair V27 globally. This research examines three **other** original source records, including one genuinely harvested source, with disjoint original-source identities. It does not consume V27's failed child summaries as exact physical evidence.

| Frozen source-case ID | Original canonical JSON SHA-256 | Historical V27 status |
|---|---|---|
| harvested:verify_pb00701_v9:1a5fd052a155 | 710259612833cfe40e73ae528e0d0e944a87123c9bb4b3f4f76cef33c45bcf4d | BLOCKED: V27_CHILD_NOT_CERTIFIED, one span |
| composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0 | 9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af | first V8 CERTIFIED; second V27 BLOCKED |
| composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100 | 8e3af5a5e74c3fc3f364607f5c3c4b03cd1adc2e2dd6e16bfc03ddf870de0d2b | first V8 CERTIFIED; second V27 BLOCKED |

Their historical source archive remains Git blob 5841c331579489b25caef38cd412bdbf286f9134. The independent verifier checks every complete original B-spline degree, knot vector, rational control, harmonic channel, source parameter, interval, phase offset/rate, original case ID and producing verifier, plus the unchanged exact v54 refusal/owner. It derives exact degree-0/1 global-source-coordinate polynomials rather than using a manually supplied physical root report as authority. The source-coordinate proof below is a checkable closed-form mathematical argument; it is not a general analytic root algorithm.

### A. Harvested V9 original source: only left source-endpoint root

Original source parameter: t in [0,1]. The only active source channels are the exact degree-1 B-spline C0(t)=t and S1(t)=1, with phase turns t/8. Consequently the **original** physical function is

    F(t) = t + sin(pi*t/4).

For 0<t<=1, 0<pi*t/4<=pi/4, so sin(pi*t/4)>0 and t>0. Thus F(t)>0 everywhere on (0,1]. At the exact left source endpoint, F(0)=0. Its right derivative is F'(0+)=1+pi/4>0, proving a **simple one-sided boundary root**. The right exterior value is F(1)=1+sqrt(2)/2>0.

**Exact result:** one closed-source root, at t=0 only; zero strict span-open roots; open sign (+). Do not misreport this source endpoint as a strict interior physical event or claim a negative-side sign outside the admitted interval.

### B. Frozen V8 tail0: one interior order-2 tangency and one simple crossing

Original source parameter: t in [0,2], true B-spline knot at t=1. Phase turns -1/4+t/2, hence harmonic-1 angle pi*(t-1/2). From the complete original controls:

- On 0<=t<=1: C0=0, S1=t-1/2.
- On 1<=t<=2: C0=0, S1=1/2.
- No other harmonic/sine/cosine channel contributes.

Set x=t-1/2 on the first span, where -1/2<=x<=1/2. The actual physical predicate is

    F_first(t) = x*sin(pi*x).

For x nonzero inside this interval, x and sin(pi*x) have the same strict sign, so their product is positive. At x=0 (t=1/2), the zero is **order two**, because

    lim_{x->0} x*sin(pi*x)/x^2 = pi > 0
    F_first''(1/2) = 2*pi > 0.

It is therefore one *TOUCHING* open-span event with positive signs on both sides, not a crossing. Exact first-span exterior values F(0)=F(1)=1/2.

On the second original span, set u=t-1 in [0,1]; the exact source becomes

    F_tail0(t) = (1/2)*cos(pi*u).

cos(pi*u) decreases strictly from +1 to -1 on [0,1] and has exactly one zero at u=1/2, or t=3/2. Its derivative there is -pi/2<0, so this is a simple positive-to-negative *CROSSING*. At the true source knot t=1, the two original source pieces meet at F(1)=1/2, not at zero.

**Exact result:** physical roots in order t=1/2 (order 2, touching) and t=3/2 (order 1, crossing); strict span-open root counts [1,1]; maximal open signs (+,+,-), closed-source endpoint values (+1/2,-1/2).

### C. Frozen V8 tail100: same order-2 tangency but no tail root

This is a **different full original source history** from tail0, although its first B-spline span and the corresponding physical function coincide exactly. The second source span additionally contains the harmonic-zero cosine ramp C0=100*(t-1). With u=t-1 in [0,1],

    F_tail100(t) = 100*u + (1/2)*cos(pi*u).

Its exact derivative is

    F_tail100'(t) = 100 - (pi/2)*sin(pi*u)
                   >= 100 - pi/2 > 98 > 0

using only 0<pi<4 and |sin|<=1. Since F_tail100(1)=1/2>0, its entire second span is strictly positive; there is **no** additional tail root. At t=2 it is exactly 199/2. The source knot t=1 remains nonzero and continuous.

**Exact result:** the same unique mathematical first-span order-2 touching coordinate t=1/2, with no second-span root; strict span-open root counts [1,0]; maximal open signs (+,+). Equality of the first-span functions does **not** assert a shared physical machining event, manufacturing clock, journal, body or history between these distinct source records.

The sufficient derivative bound is deliberately not generalized to all positive ramps. In a synthetic control with A=1/4, the second endpoint would be A-1/2=-1/4; an indiscriminate rule claiming all A>0 tails remain positive is **false**. For slopes A<=2 the sufficient margin gate refuses, rather than concluding mathematical nonmonotonicity or root existence.

## Falsification and test boundary

The standard-library verifier binds the frozen v54 121-source archive, the pinned post-v54 auditor, original MC-002 26-operation domain, and no-production/NOT_ESTABLISHED authority. It independently checks exact source values at original rational *cardinal-phase* points (including the knot on both sides), not transcendental binary-float evaluations at arbitrary points. The analytical proof explicitly establishes the remaining interval sign/multiplicity/termination statements.

Adversarial controls reject:
- altered spline degrees, knots, controls, harmonics or noncanonical rational coefficients;
- source parameter, phase, interval, origin, case identifier or canonical SHA mismatch;
- false promotion of historical V27 refusals, forged root counts/signs/orders and incorrect knot event;
- source-identity collapse, identity-zero substitution and an overgeneralized weak ramp;
- mismatched historical census, changed domain/gate status, forged capability/production acceptance;
- untrusted cyclic/deep/oversized report structures and floating-point report scalars.

A source-model theorem may be independently checkable without being a native geometry theorem or a general event/zero decision procedure. No historical route statuses are changed in the frozen corpus. The current V27 algorithm continues to refuse these source records.

## Measured baseline, proposed supplemental overlay, and gate boundaries

| Claim | Historical frozen v54 | Additional three-case source-specific research overlay |
|---|---:|---:|
| Total original frozen cases | 121 | 121 |
| Historical uncertified route refusals | 20 | 17 lacking **these three new mathematical source proofs** |
| Missing ordered-span premise cases | 30 | 30 |
| v54 original recorded dispositions changed | no | **no** |

**Important:** the 20→17 subtraction is *only* a clearly labelled three-claim overlay. It is **not** an exhaustive combined post-v54 accepted-route census. The separate PR #323 V6 tail100 witness establishes another disjoint individual source proof, but must be reviewed as its own evidence and must not be silently added or double-counted. All four original V27_CHILD_NOT_CERTIFIED cases can have separate mathematical event proofs while the **generic V27 child-certification failure remains wholly unresolved**.

This proof does not address V27 child-consumption interfaces generally, other V27 failure classes, noncommon-factor/nonmonotone universal analytic zero theorems, irrational-phase algebraic endpoint zero tests, unrelated V41 source/root ordering, topology/connectivity, native B-rep/STEP or the full 26-operation machining programme. In particular the result does not accept PB-007-01 or any other PB-007 blocker, PO-02/04/05/07/08, MC-B, MC-1, production creation, native/paid execution or a permission to narrow source/operation scope.

## Reproduction and qualification

On a checked-out full source tree:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v27_three_frozen_refusals.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
```

Require literal final PR-head focused Actions proof and mc1-static checks, current-head source/mathematics review, preservation of all negative evidence and verified source-tree identity for any later merge. Do not infer final review/merge from a green earlier head. No shared current-state/77 ledger, frozen audits or proof/programme registries have been modified.

**Next substantive theorem/interface priority:** integrate full original-source event proofs into a fail-closed general V27 checked child/endpoint consumer without relying on count-only summaries, then challenge additional frozen V27 endpoint/pole and missing ordered-premise cases. A finite special-source proof is not a general terminating analytic decision procedure.
