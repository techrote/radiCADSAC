# MC-038 / PB-007-01 — Original two-span moving squared-amplitude event theorem

**Date:** 5 November 2026. **Status:** bounded prospective original-source proof research; subject to exact-head CI and distinct-session review. **Evidence:** DETERMINISTIC_MODEL, neither native geometry nor engineering STEP. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Exclusive source reservation:** [#324/6650035975](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6650035975) with updated main [#324/6650094994](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6650094994). Source-selection main 2ab90bd3ec684f92830b9863ab870bdbe188c1b5. The independent integration owner of #392 and #100 comments is untouched.

## Named obligation and falsifiable contract

PB-007-01 (relevant to OPEN PO-04/05/08) requires full physical events, exact order, sign and termination. The general analytic-event theorem remains unproved. We establish a reusable theorem for ONE original source in a narrowly declared moving-phase grammar:

* Original rational quadratic B-spline in source-time t on [L,R], one true interior knot K, L less than K less than R, with original common knot vector [L,L,L,K,K,R,R,R], five original control values per channel.
* Exactly cosine harmonics C0 and C1, no sine channels, with ONE global affine rational phase in turns beta(t)=b+r*t and nonzero rational r.
* Each exactly extracted Bernstein span admits rational affine P(u),Q(u) satisfying the exact rational polynomial identities C0=(P^2+Q^2)/2 and C1=(P^2-Q^2)/2; local u=(t-a)/(c-a) on that original span.

Original source control extraction and every square identity are recomputed, rather than trusting caller-supplied child sources, event coordinates, or proof flags. Refuse a nonsquare coefficient, unsupported grammar, noncanonical rational, mutated original, ambiguous knot, or exceeded explicit arithmetic budget.

The original physical source function equals

\[
F(t)=C_0(t)+C_1(t)\cos(2\pi\beta(t))
=P(u)^2\cos^2(\pi\beta(t))+Q(u)^2\sin^2(\pi\beta(t)).
\]

**For the admitted class**, the full original zero set is exactly a finite union of maximal closed zero intervals and isolated rational points. Its nonzero physical cells are all strictly positive. Every isolated event has even root order and, at a true original knot, two distinct one-sided orders, never an unproved global smooth multiplicity. A continuum has no finite total cardinality.

## Exact B-spline authority and original knot semantics

For each harmonic, use the ORIGINAL five rational controls, not a substituted polynomial source. The exact Cox–de Boor/Bernstein extraction at the double interior knot yields coefficient triples [c0,c1,c2] and [c2,c3,c4]; an original Bernstein triple [A,B,C] has global-local power coefficients [A, 2(B−A), A−2B+C]. This is a polynomial identity for every physical point on the span. The implementation also compares four exact interior evaluations with an independent unsplit Cox–de Boor evaluator as an adversarial implementation check; sampling is not used to prove root completeness.

Both channel limits at K equal the ORIGINAL shared control c2. Thus the physical source is continuous at K for this admitted grammar and common global phase. The source binding SHA256 covers the original JSON, control arrays, real knot multiplicity, parameter, original phase, exterior and true internal knot. A forged split-source list is not authoritative.

The rational affine-square checker proves each quadratic identity in the coefficient ring Q[u], using an exact rational square-root check. For q0+q1*u+q2*u^2 with q2 positive, p1=sqrt(q2), p0=q1/(2*p1), and the exact identity p0^2=q0 must hold; with q2 zero, q1 must be zero and sqrt(q0) rational. No approximate comparison or numerical discriminant is admitted.

## Exhaustive root theorem and multiplicity

A sum of two nonnegative squares is zero exactly when BOTH factors vanish:

\[
P(u)\cos(\pi\beta(t))=0,\qquad
Q(u)\sin(\pi\beta(t))=0.
\]

This reduces **all** original roots to three exhaustive cases:

1. beta is an integer: sine zero, cosine nonzero, so P must be zero.
2. beta is a half-integer but not integer: cosine zero, sine nonzero, so Q must be zero.
3. Otherwise neither trigonometric factor vanishes, so BOTH affine P and Q must be zero.

Because r is rational and nonzero, the preimages of every integer or half-integer phase level in a bounded closed original interval are exact rational coordinates. Their number is finite and a complete lattice can be enumerated with rational floor comparisons. Each nonidentity affine P,Q contributes at most one additional rational candidate. This is a proof of exhaustive finite enumeration, not a numerical scan, time cap, bounded refinement, or approximate zero test. Identity-zero pieces are recognized coefficientwise and represented as closed intervals.

At an isolated root t0, each finite affine vanishing order is either 0 or 1, and each phase trigonometric zero has exact order 1 because r is nonzero. An identically zero factor is assigned infinite order, not an invented isolated multiplicity. The physical order is

\[
2\min(\mathrm{ord}(P)+\mathrm{ord}(\cos(\pi\beta)),
       \mathrm{ord}(Q)+\mathrm{ord}(\sin(\pi\beta))),
\]

with identically zero summands ignored. Leading real square coefficients are nonnegative and at least one finite leading coefficient is strictly positive, hence cancellation is impossible. Every isolated root has even order and is tangential, and every true zero-free interval has strictly positive F. There is no sign crossing within the admitted squared-amplitude source class.

The original knot point is evaluated once using the common source and phase. An isolated shared-knot root retains its two different left/right orders; equality or multiplication of these orders is not assumed. If a zero interval ends at the knot, any coincident finite child root is absorbed into the continuum, with its nonzero-side boundary germ retained. Two adjacent identity-zero spans merge. Positive cells merge across an exactly nonzero knot. Exteriors retain their inward one-sided orders. All interval endpoint inclusion flags are exact.

## Cost bounds, independent controls and deliberate refusals

Inputs are limited to 16,384 source bytes and canonical rational numerators/denominators at most 120 bits; intermediate rational operands at most 1,024 bits; absolute global endpoint phase at most 32 turns. Those are **algorithm admission and runtime bounds only**, not physical tolerances or mathematical claims about unadmitted sources. Within these bounds, the full process is finite rational arithmetic, exact integer square roots, at most 129 half-integer phase levels plus finite padding, sorting and component composition. Termination and complete exact zeros hold for every admitted source. Exceeding a resource bound returns RESOURCE_REFUSAL with no truth claim, rather than a successful zero exclusion.

Adversarial tests use actual original five-control B-splines: moving global beta=t, left identity-zero and finite right gives the **closed interval [0,1] and isolated right exterior {2}** with a right knot germ of order **4**; its mirror produces **[1,2] and {0}**; two zero spans coalesce to [0,2]; a continuous isolated true knot retains sided orders **(2,4)** and no global order; a nonzero original knot bridges one whole positive cell; an amplitude root at t=2−2^-70 and a phase root at 2 are kept distinct exactly. Tests also cover negative phase rate, negative/nonunit intervals, changed source controls/phase/knot, false source binding, forged continuum/sign/claim, unsupported sine channel, stationary phase, non-square amplitude, malformed rationals and over-budget winding. No synthetic event count contributes to the historical denominator.

## Frozen historical evidence and strict nonpromotion

Historical original anchor: composite:DELEGATED_V6_CONSTANT_MODULATION:tail0, SHA256 9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1, source-time-t on [0,2], global phase turns t/4 and actual knot at 1. It was ALREADY COMPLETE_SOURCE_SPECIFIC in the qualified v2 source registry, and this project does not newly close it.

Pinned original source corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134; v2 fifty-source register Git blob e52d3baf3692a011cf86234eeaa992ef407d99fd. The adversarial test rehashes the actual Git contents and rechecks every original case ID, source SHA256, producer origin, phase/interval, original refusal class and registered evidence level. No frozen source or saved raw failure is edited.

| Identical frozen historical population | Before | After | Delta |
|---|---:|---:|---:|
| Original sources | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Complete source-specific witnesses | 50 | 50 | 0 |

New historical resolved IDs: none. **This new bounded positive theorem is not A, B, or a new C**; synthetic-only/prospective source coverage does not count as closing the frozen historical blockers or discharging a REQUIRED full PO. General noncommon-factor analytic events, arbitrary nonlinear P/Q, stationary phases, discontinuous point semantics, PB-007-02/03/04 and all relevant full proof obligations remain OPEN. MC-B and MC-1 remain NOT_ESTABLISHED. Evidence class DETERMINISTIC_MODEL only. All 26 operations, canonical journal, native bodies/lineage, topology, conventional usable engineering STEP, independent consumer, paid/native campaign and production prohibitions are preserved.

## Reproduce and next critical path

The executable source checker is pb00701_two_span_moving_square_components.py, with --contract and --source arguments. Its independent tests are test_pb00701_two_span_moving_square_components.py. The machine-readable receipt is pb00701-two-span-moving-square-components.json; dedicated literal-head CI is mc1-pb00701-two-span-moving-square-components.yml. Also run the existing full post-v54 v2 producer verifier and MC-1 static validator. Do not treat passing CI alone as proof of general capability.

A future genuinely blocker-closing route must extend beyond the admitted affine-squared two-span grammar, supply exhaustive original-source moving nonconstant amplitude/event witnesses for an unsupported class, or discharge the actual complete PB-007 obligation. Its proof must preserve full original phase/knots, identity-zero, even roots, exact close roots, signed germs and arbitrary supported physical constructions. A separate session must review the final candidate, qualify its literal head and only then consider expected-head-protected merge plus merged-main CI. No same-session merge or #100 comment is authorized while the separately owned #392 integration reservation is active.
