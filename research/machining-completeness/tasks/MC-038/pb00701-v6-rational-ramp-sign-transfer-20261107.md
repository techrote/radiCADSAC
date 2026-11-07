# MC-038 / PB-007-01 — exact rational-ramp source-knot sign-transfer theorem

**7 November 2026 · Independent bounded constructive research · DETERMINISTIC_MODEL.** This is not an A historical case reduction, B full required PB/PO discharge, or C newly falsified route. It is a source-bound positive, parameterized theorem to support a future category-3 physical sign-transfer consumer. MC-B and MC-1 remain NOT_ESTABLISHED.

**Authority and ownership.** Issue [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100), [coordination #324](https://github.com/techrote/radiCADSAC/issues/324), base main 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9. Independent additive Draft PR; no changes to open #445, #446, or #397, which owns exclusive main integration. Named work concerns PB-007-01 and dependent PO-04/05/08. All remain OPEN.

## Original-source identity, knot and phase

Two **genuine historical frozen originals** are selected:

- composite:DELEGATED_V6_CONSTANT_MODULATION:tail0, source SHA-256 9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1, row SHA-256 145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc;
- composite:DELEGATED_V6_CONSTANT_MODULATION:tail100, source SHA-256 f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5, row SHA-256 0801317d3452c77733a129148d58eaac2f06aa9cd26396a44892e82c524e1db2.

Both are original source-time-t on [0,2] with **true internal B-spline knot t=1**, phase turns beta(t)=t/4, H1 cosine degree-zero knots [0,1,2], controls [1,1], no sine channel. Tail0 has H0 cosine degree zero, controls [0,0]. Tail100 has H0 degree one, knots [0,0,1,1,2,2], controls [0,0,0,100]. The executable verifies the full original spec and row SHA and the frozen V54 Git blob 5841c331579489b25caef38cd412bdbf286f9134, together with prior COMPLETE_SOURCE_SPECIFIC V2 witness Git blob e52d3baf3692a011cf86234eeaa992ef407d99fd.

**Parameterized admission grammar:** same true source time, knot, H1 and phase, H0=0 on [0,1] and H0=m(t−1) on [1,2], m rational. m=0 matches the *physical function* of actual tail0 (its original H0 degree differs); m=100 matches actual tail100 source controls exactly. All other m are prospective source laws, **not additional frozen original cases**. Arbitrary nonconstant H1, multiple harmonics, phase changes or discontinuous true-knot point policies are outside this theorem.

## Falsifiable hypothesis and exact proof

For source-time t on the original first span, F(t)=cos(pi*t/2)>0 for 0<=t<1. Put x=t−1 on the second span. Then F(1+x)=m*x−sin(pi*x/2)=x(m−R(x)), with R(x)=sin(pi*x/2)/x for 0<x<=1. Exactly F(1)=0 at the true knot.

**Strict root uniqueness proof.** With a=pi/2, the derivative R'(x)=[a*x*cos(a*x)−sin(a*x)]/x² is strictly negative: g(u)=sin(u)−u*cos(u), g(0)=0, g'(u)=u*sin(u)>0 for u in (0,pi/2]. Hence R decreases continuously from R(0+)=pi/2 to R(1)=1. No numerical root scan, derivative-sign guess or timeout is used. The exhaustive exact rational slope classification is:

| Rational m | Physical zero events in [0,2] | Ordered nonzero physical regions | True knot semantics |
|---|---|---|---|
| m less than 1 | only knot t=1 | positive, negative | sided crossing |
| m exactly 1 | knot t=1 and exterior t=2 | positive, negative | sided crossing; right endpoint simple |
| 1 less than m less than pi/2 | knot t=1 and exactly one *simple* interior root in (1,2) | positive, negative, positive | sided crossing, then simple crossing |
| m greater than pi/2 | only knot t=1 | positive, positive | sided touching (not a globally smooth double root) |

At the second interior zero, the source derivative is −x*R'(x)>0; the root is simple. For rational m=3/2, the exact root is t=4/3 because sin(pi/6)=1/2. For generic m in (1,pi/2), the root is recorded only by the proven unique open original-source rational bracket (1,2), not a fabricated coordinate. For m=1, F'(2)=1 establishes the exterior order. At the knot, the left derivative is −pi/2 and the right is m−pi/2, each nonzero for rational m, but a **global smooth knot multiplicity is not assigned** because the piecewise function can have different first derivatives.

**Terminating pi comparison.** Rational m never equals pi/2 (pi is irrational). Machin's exact identity pi/2=8 arctan(1/5)−2 arctan(1/239), with strict rational lower/upper alternating Taylor arctan partial sums, yields converging rational intervals. They eventually separate every rational m from pi/2; that is a mathematical termination argument, independently of implementation caps. The executable uses at most 128 pairs, and if this resource budget is exhausted it returns NONTRUTH rather than making a sign/root claim. m<=1 and m>=2 need no pi comparison.

## Cost, independent adversaries, evidence boundary

The executable uses exact Fraction arithmetic only, canonical input numerators/denominators at most 512 bits, rational tokens at most 320 bytes, Git-blob-verified V54/V2 read cap 400000 bytes, duplicate-key refusal and bounded arctan iteration. No floating-point scan or false rational locator is an oracle. It tests the two pinned historical cases, negative and zero slopes, endpoint equality m=1, implicit/simple and exact m=3/2 roots, m=2 and m=100 touching, rational slopes 333/212 and 355/226 bracketing pi/2, 1±2^-300 near-endpoint controls, zero-H1/changed phase refusal, identity-zero attempts, budget/canonical rationals and event-region cardinality.

Prior art is explicit: [V6 tail100 knot source proof](pb00701-v6-tail100-knot-source-research.md) already establishes the m>2 original case; [knot unsigned-sign information-loss result](pb00701-knot-unsigned-sign-erasure-20261105.md) already proves why same roots and unsigned sided orders cannot distinguish touching from crossing. The contribution here is the exact **rational-slope classification with an additional interior physical event for 1<m<pi/2**, with original knot and endpoint semantic preservation. This is not a second claim to have discovered either original V6 root.

## Reproduction, before/after and dispositions

Execute on the literal PR head:

    python3 research/machining-completeness/tasks/MC-038/pb00701_v6_rational_ramp_sign_transfer_20261107.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
    python3 tools/validate_machining_completeness.py

The first command outputs source-hash matched machine evidence, including the same 50 unchanged original IDs; the dedicated workflow reruns the full historical producer and static checks. No frozen V54 or V2 material is edited.

| Matched frozen measure | Before | After | Delta |
|---|---:|---:|---:|
| Original source IDs | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Complete preexisting V2 source witnesses | 50 | 50 | 0 |
| Required PB/PO discharge | 0 | 0 | 0 |

New historical cases resolved: none. No V54 owner/consumer implementation or general source theorem is declared complete; the original 50-case historical cohort remains unchanged. Evidence classification is DETERMINISTIC_MODEL, **not** native geometry, independent oracle, manufacturing topology or engineering STEP.

**Stop gates:** keep Draft pending direct mathematical review, literal corrected-head focused and full V54/V2 CI, distinct independent admission, then #397-coordinated integration; never alter main, 77/current-state, shared proof/programme or frozen registries in this task. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED. All 26 supported machining operations, physical source semantics, durable journal/bodies/topology, native STEP, permits and production restrictions remain intact. Next critical path: lift the signed-knot theorem beyond a single rational H0 ramp to genuinely varying H1, identity-zero, multiharmonic and general source-to-consumer event partitions.
