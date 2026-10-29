# MC-038 / PB-007-01 — exact trigonometric tangency and source-knot control

**Status:** bounded research candidate, 29 October 2026. **Evidence:** DETERMINISTIC_MODEL, not native geometry. Existing owner: [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). No historical source or production gate is changed.

## Hypothesis, admitted grammar and falsifiers

For two *explicitly supplied* continuous rational **constant-coefficient finite trigonometric** source spans on the fixed original source parameter s, [0,1] and [1,2], with phase theta=pi*s, complete physical root ordering, repeated-root multiplicities, one-sided endpoint/knot orders, tangencies and signs are decidable by exact half-angle algebra and rational Sturm arithmetic. Each span has independently specified rational harmonic coefficients of degree at most eight; continuity at the true source knot s=1 must be exact.

This is NOT a generic polynomial-modulated V27/V41 source adapter: the original B-spline sources are outside its admitted grammar. Neither historical child counts, caller-submitted counts nor floating-point samples are proof inputs. Source authority/provenance is not inferred from a caller's source_parameter_id. An original-source binder must validate the generating source separately.

Fail closed for identically zero spans, unsupported phase/parameter/interval/grammar, discontinuous knots, noncanonical/inexact coefficients, incomplete polynomial proofs, zero or ambiguous separators, resource exhaustion, forged witnesses, or unsupported authority. None of these exclusions narrows the overarching 26-operation machining domain.

## Mathematical proof and exact event semantics

On either span, write

    F(s) = sum_h [a_h cos(h*pi*s) + b_h sin(h*pi*s)].

Set t=tan(pi*s/2). By the exact identity

    exp(i*theta) = (1+i*t)^2 / (1+t^2),

the function is a rational function

    F(s) = P(t) / (1+t^2)^H,
    P(t) = sum_h [a_h Re((1+i*t)^(2h)) + b_h Im((1+i*t)^(2h))]
                  * (1+t^2)^(H-h).

The polynomial P has *exact rational* coefficients and degree at most 2H. Its denominator is positive at finite real t. The left physical span maps monotonically to 0<t<+infinity and the right to -infinity<t<0. A real root of P has an exact implicit algebraic identity in t, not an invented rational or algebraic source-coordinate s. The output supplies a strict rational t isolation interval and the inverse half-angle source-coordinate descriptor.

For each nonzero P, remove the t-adic valuation and compute exact polynomial GCD(P,P'), a square-free factor decomposition and a reconstruction identity. Rational Sturm sign variations plus a strict rational Cauchy outer bound establish every distinct real nonzero root. Finite rational partitions yield strictly isolating and disjoint intervals. A unique square-free multiplicity factor identifies the exact integer order of every root; checked polynomial signs before/after a bracket establish crossing or tangency parity. A rational proof cut may never coincide with a root. Unresolved/resource-exhausted cases refuse rather than invent completeness.

The transform singularity t=infinity is the actual source knot s=1. Independently verify its exact physical value

    F(1) = sum_h (-1)^h * a_h.

The one-sided knot vanishing order is 2H-degree(P), independently for the left and right spans, when this value is zero. Exact polynomial leading coefficients derive one-sided signs as t tends to +infinity or -infinity. A zero knot is ONE physical event with separate left/right orders; no smooth global knot multiplicity is claimed. A nonzero knot cannot be an event and must join with identical physical signs. At outer endpoints s=0 and s=2, the t-adic valuation gives exact one-sided vanishing order and the first nonzero polynomial coefficient gives the inward sign. Complete physical sign cells are derived from the proved ordered events, including sign-preserving tangencies.

## Deterministic tests, supplementary falsification, custody

Reproduce:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_half_angle_knot.py --contract --self-test

The included tests cover transverse cos(theta) roots on both spans, multiplicity-two roots of cos(theta)^2=(1+cos(2*theta))/2, unequal one-sided source-knot orders (left 1+cos(theta), right sin(theta)), a touching zero knot (1+cos(theta) on each side), source endpoints of 1-cos(theta) and sin(theta), higher harmonics, exact Sturm square-free factors, discontinuity, canonical-rational/grammar errors, source/result forgeries and nonpromotion.

Local preparation passed 10 tests (one source-custody test was skipped outside the repository checkout). An additional 120 seeded rational pure-trigonometric two-span examples matched independent SymPy rational-polynomial real-root isolation for distinct physical event counts. That supplementary comparison is NOT a proof premise or an assertion of CI performance. CI also checks frozen v54 121-case corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134, MC-002 26-operation domain blob 23de82f5240a72509f7afe4acd5948b65bc4ff13 and current authority blob fa0233323a0804d8a5d3eb7cd892a274a6173fab (all unchanged). The source grammar is limited to two spans, at most eight harmonics, canonical rational coefficient size limits, Sturm recursion and rational resource caps. Typed BLOCKED/RESOURCE_REFUSAL results have is_truth_value=false.

## Admissibility boundary and next justified research

This is a new *conditional mathematical control* for constant-harmonic trigonometric tangency, endpoints and real source-knot joins, complementary to [transverse trigonometric interval PR #296](https://github.com/techrote/radiCADSAC/pull/296). It does not verify the polynomial-modulated V27/V41 original B-splines, arbitrary irrational/cross-owner implicit root comparison, general trigonometric completion, the historical v54 blocked dispositions, PB-007-01 acceptance, or any native/material/B-rep/STEP evidence.

Next: a source-pinned decomposition proving an actual original V27/V41 span belongs to a supported exact subset, or combining independently checked polynomial and trigonometric factors without silently losing coincident events. Continue under existing issue #100; do not invent successor issues or reopen #275. MC-B/MC-1 remain NOT_ESTABLISHED, production_authorized=false. The full 26-operation lathe/mill domain, source/provenance/phase, canonical manufacturing journal, material/body/lineage, refusal/UNCERTIFIED and conventional usable engineering STEP obligations remain intact.
