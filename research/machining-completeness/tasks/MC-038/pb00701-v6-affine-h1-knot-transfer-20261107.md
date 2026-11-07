# MC-038 / PB-007-01 — exact true-knot transfer with genuinely different H1 laws

**7 November 2026. Bounded constructive research, evidence class DETERMINISTIC_MODEL.** Governing programme: [MC-1](../../../..//docs/machining-completeness/00-PROGRAMME.md); owner issue [#100](https://github.com/techrote/radiCADSAC/issues/100), coordination [#324](https://github.com/techrote/radiCADSAC/issues/324). Authority: accepted main \`48222d6c40b15ad42cc36d56e6d25f3b284e7fc9\`; #397 exclusively owns main integration. This is neither a new original-source historical closure nor a completed PB/PO obligation.

## Scope, falsifier and prior work

The [#447](https://github.com/techrote/radiCADSAC/pull/447) V6 rational-H0-ramp theorem has unchanged H1 cosine=1 and sine=0 on both sides of a true knot. The independent next question is whether exact ordered physical events survive when **both H1 laws actually change** across the knot, without introducing a discontinuity in the physical function *or* coefficient values. A single missed hidden right-span root, false knot multiplicity, misidentified source coordinate, or invalid source-spline representation falsifies the claim below.

This is a **prospective** two-span source. The frozen V54 originals \`composite:DELEGATED_V6_CONSTANT_MODULATION:tail0\` and \`:tail100\` provide pinned reference geometry/time/phase and pre-existing V2 evidence only. They **do not** have the following varied H1 laws. The verifier refuses attempts to label this prospective source as an unchanged frozen historical original.

## Exact spline grammar and physical law

Use authentic source time t in [0,2], an actual degree-two B-spline internal **double** knot t=1 and knot vector [0,0,0,1,1,2,2,2]. The phase is \`t/4\` turns, i.e. angle \`pi*t/2\`. The harmonic formula is \`F=H0+C*cos(pi*t/2)+S*sin(pi*t/2)\`.

On the left span 0<=t<=1, choose (H0,C,S)=(0,1,0), so \`F_L(t)=cos(pi*t/2)\`. On the right, x=t-1 in [0,1] and choose the **different, affine** harmonic laws

\`\`\`text
H0_right(x) = m*x
C_right(x)  = 1 - x/2
S_right(x)  = -x/2
F_right(x)  = m*x - (1-x/2)*sin(pi*x/2) - (x/2)*cos(pi*x/2)
\`\`\`

Here m is an exact rational and all three coefficients are continuous at t=1. The following *ordinary quadratic B-spline* controls realize the stated law exactly, not merely as a two-piece informal definition:

| Coefficient | Five controls, common knots [0,0,0,1,1,2,2,2] |
| --- | --- |
| H0 | [0, 0, 0, m/2, m] |
| H1 cosine C | [1, 1, 1, 3/4, 1/2] |
| H1 sine S | [0, 0, 0, -1/4, -1/2] |

The shared third control ensures exact coefficient continuity at the internal double knot. The two quadratic Bezier pieces each reduce to their specified affine polynomial by degree elevation. This is a C0 spline with a possible derivative discontinuity, not a spurious smooth global source.

## Proof: exact complete root and sign classification

Write a=pi/2 and, for x>0,

\`\`\`text
R(x) = sin(a*x)/x
Q(x) = R(x) - sin(a*x)/2 + cos(a*x)/2
F_right(x) = x*(m-Q(x)).
\`\`\`

For 0<x<=1, \`R'(x) = (a*x*cos(a*x)-sin(a*x))/x² < 0\`, because \`g(u)=sin(u)-u*cos(u)\` has \`g(0)=0\` and \`g'(u)=u*sin(u)>0\`. Furthermore

\`\`\`text
Q'(x)=R'(x)-(a/2)*(cos(a*x)+sin(a*x))<0.
Q(0+)=pi/2+1/2,       Q(1)=1/2,       Q(1/2)=sqrt(2).
\`\`\`

Therefore Q is continuous and **strictly decreasing**. In particular no numerical sampling, fixed subdivision resolution, or epsilon is used to infer the root count. For rational m, equality with irrational \`pi/2+1/2\` or \`sqrt(2)\` is impossible. Exact rational Machin alternating enclosures determine comparison with pi/2; a comparison with sqrt(2) is simply the integer-square order of m² and 2 once m>1/2. The finite verifier's arithmetic/time cap produces typed NONTRUTH, not a root assertion.

| Rational slope m | Ordered zero events in [0,2] | Nonzero signs in source order |
| --- | --- | --- |
| m<1/2 | true knot t=1 only | positive / negative |
| m=1/2 | true knot plus simple right exterior zero t=2 | positive / negative |
| 1/2<m<pi/2+1/2 | true knot plus **one and only one** simple right interior crossing | positive / negative / positive |
| m>pi/2+1/2 | true knot only, sided touch | positive / positive |

In the interior case, the additional root has \`F'_right=-x*Q'(x)>0\`, hence it is simple. Its exact rational source-time bracket is **(3/2,2)** for \`m<sqrt(2)\` and **(1,3/2)** for \`m>sqrt(2)\`. Neither is a fictitious exact transcendental coordinate. At t=1 the left derivative is \`-pi/2\`, the right derivative is \`m-(pi/2+1/2)\`; for rational m the two one-sided orders are each one. Do **not** label a sided touch as a globally smooth double root. At m=1/2 the exterior root is simple because \`F'_right(2)=-Q'(1)>0\`.

The extreme proximity controls are analytic: for \`d=2^-100\`, \`Q(0+)-Q(d)>=sin(a*d)/2>3d/8\`; choose rational \`m<pi/2+1/2\` within \`d/4\` of that threshold to force the extra root into (1,1+d). Similarly \`-Q'(x)>3/8\` on [1/2,1], so \`m=1/2+2^-300\` gives a distinct extra root in (2-d,2). Both roots are **strictly distinct** from the boundary zero regardless of how little distance separates them.

## Executable evidence, custody and limitations

Execute \`python3 research/machining-completeness/tasks/MC-038/pb00701_v6_affine_h1_knot_transfer_20261107.py --contract --self-test\`. This checks pinned frozen V54 and V2 blob identities, original source rows and pre-existing complete V2 evidence; it does not replace the historical source. Adversarial controls test crossing/touching, exterior event, true knot provenance, correct degree-two spline controls, both exact midpoint brackets, roots within 2^-100 of boundaries, near irrational thresholds, resource-limit refusal, malformed/canonical rational policy and explicit refusal to masquerade as an original.

**Truth classification:** prospective bounded mathematical theorem only (DETERMINISTIC_MODEL). Before=after historical V54: 121 originals, 20 uncertified routes, 30 missing ordered premises, 50 pre-existing V2 witnesses. Current-frontier registry numbers (15 complete registered, 35 partial/missing) are a different evidence register and are not overwritten. New original IDs [], delta all 0, required PB/PO discharged 0. PB-007-01/02/03/04 and dependent PO-04/05/08 remain open. MC-B and MC-1 are NOT_ESTABLISHED. No native geometry, durable material bodies, engineering STEP, production authority or proof-registry promotion is implied.

**Next unresolved research:** arbitrary source-pinned affine H1/H0 coefficients (rather than this restricted monotone-sign family), nonmonotone Q with multiple right-span events, and composition across multiple authentic knots. This theorem's special monotonicity is a useful positive building block, **not** a generic event-decision procedure.
