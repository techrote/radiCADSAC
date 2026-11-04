# PB-007-01 — actual two-span moving-phase source-knot order falsification

**Status:** scoped negative research candidate, 4 November 2026. **Evidence class:** DETERMINISTIC_MODEL; neither native machining geometry nor independent STEP qualification. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100); preregistration [#6621287841](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6621287841), coordinating owner [#324](https://github.com/techrote/radiCADSAC/issues/324). **Baseline:** main `bded1b5ef5fb43914adee3dda817f6a962023cad`. The earlier [two-span stationary result #359](https://github.com/techrote/radiCADSAC/pull/359) is merged and its scope is *stationary zero phase only*.

## Question, hypothesis and falsification target

The next PB-007-01 premise is **source-bound exact moving-phase zero-component certificates for original two-span B-splines**, including source-knot sided orders, followed by parent physical zero-set recomposition. This is currently unproved in general. We test two specifically stated proposed shortcuts:

1. **Phase-blind transfer:** reuse the stationary polynomial/continuum component set on the same original B-spline controls when the source phase rate changes from zero to a nonzero rational rate, without a fresh moving-phase proof.
2. **Smooth-knot multiplicity coercion:** require a source-knot zero to have one global smooth multiplicity, or infer that the source-knot order in a moving squared-amplitude construction must always be two.

**Expected decisive negative result (C):** exhibit one legal, actual original quadratic B-spline source and prove its full physical zero set under both phase laws. If those sets differ and the one-sided orders differ, both shortcuts fail. This is **not** an impossibility theorem for general event solvers, generalized exact phase comparisons, or full PB-007.

## Exact source (not a sampled polynomial approximation)

Grammar: `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`; source parameter `source-time-t`; original closed source interval [-1,1]; global phase turns \(\beta(t)=t\); cosine harmonics 0 and 1; no sine channels. Both harmonic channels have original degree-2 clamped knot vector

\[
[-1,-1,-1,0,0,1,1,1],
\]

with the **actual interior knot 0 of multiplicity two**. Original five controls:

| Original channel | Controls |
|---|---|
| \(C_0\) | \([1/2,0,0,0,1/2]\) |
| \(C_1\) | \([1/2,0,0,0,-1/2]\) |

The script's canonical original-source SHA-256 is `3c4eea96bf46a769a92902e0c06196258e2107566f956c6f76c818e43f3a3058`. All source fields, exact rational tokens, knot multiplicities, global phase and source parameter are bound and validated. The source is **new prospective research**, not a v54 historical original ID. It must never be counted as reducing any one of the frozen fifty historical cases.

## Exact whole-span identities, roots, orders and positive cells

For a clamped degree-two two-span source with that interior knot, exact Cox–de Boor/Bernstein extraction yields original control triples \([c_0,c_1,c_2]\) on [-1,0] and \([c_2,c_3,c_4]\) on [0,1]. Global-t polynomial expansion establishes, as identities on their entire intervals (not by sampling), that

\[
 C_{0,L}(t)=C_{0,R}(t)=t^2/2,\quad
 C_{1,L}(t)=t^2/2,\quad C_{1,R}(t)=-t^2/2.
\]

Every channel is exactly continuous at the true original source knot: its two endpoint values are zero. An independent rational Cox–de Boor evaluation at six interior checkpoints checks the extraction implementation; the **coefficientwise polynomial identity** is the mathematical proof, not the sample check.

For the same global moving phase \(\beta(t)=t\), \(\cos(2x)=2\cos^2 x-1\) gives the exact physical source:

\[
F_L(t)=t^2\cos^2(\pi t),\qquad t\in[-1,0],
\]
\[
F_R(t)=t^2\sin^2(\pi t),\qquad t\in[0,1].
\]

On [-1,0], cosine vanishes **only** at \(t=-1/2\), with a simple zero. On [0,1], sine vanishes **only** at the two endpoints, with simple zeros. These are exact integer/half-integer phase-zero identities over complete bounded phase intervals, not a finite numerical root scan. The polynomial carrier \(t^2\) contributes order two at 0. Since \(\sin(\pi t)/t\to\pi\ne0\) at 0, the right-hand physical leading term is \(\pi^2t^4\); left-hand leading term is \(t^2\). At the left interior root, \(t^2\) is nonzero and cosine squared contributes order two. At the right exterior, \(t^2\) is nonzero and sine squared contributes inward order two.

Consequently:

| Source coordinate | Event | Exact order and sign |
|---|---|---|
| \(-1/2\) | Strict left-span tangency | order 2, signs \(+,+\) |
| \(0\) | **One true original source-knot root** | **left order 2, right order 4**, signs \(+,+\); **no global smooth multiplicity** |
| \(1\) | Right exterior root | inward order 2, positive on approach |

The exact distinct closed-source zero set is \(\{-1/2,0,1\}\), count **3**. Maximal positive source components are \([-1,-1/2)\), \((-1/2,0)\), and \((0,1)\), count **3**. Equal physical signs **must not** merge cells across a tangency or a root at the original knot.

The source is continuous at the knot; it is not forced to be analytic across that true B-spline break. This is precisely why both sided derivative orders are retained and **not multiplied, summed or relabeled as one global smooth order**.

## Phase-blind control is independently false

Change **only** the original phase rate from 1 to 0, retaining the same controls, source parameter and exact knot. Because \(\cos(0)=1\), the *stationary* source is

\[
F_L^{(0)}(t)=t^2,\qquad F_R^{(0)}(t)\equiv0.
\]

Its zero set is the **entire closed right interval** [0,1], cardinality continuum. The shared knot belongs to that component and must not be reported as an additional isolated point. Its sole maximal positive component is \([-1,0)\). There is no finite total root count. Thus the stationary-source component grammar cannot be transferred to a moving phase without recomputing and independently proving the phase-dependent physical events. The code's moving validator refuses the phase-rate mutation; the stationary calculation is a clearly labeled counterfactual, **not** a reaccepted moving proof.

## Reproduction, exactness and bounds

Files in this leaf:

- [Executable source-bound counterexample](pb00701_moving_phase_knot_falsifier.py).
- [Independent structural, adversarial and historical registry verifier](verify_pb00701_moving_phase_knot_falsifier.py).
- [Machine-readable fixed-source proof view and zero-delta census](pb00701-moving-phase-knot-falsifier.json).
- [Dedicated CI workflow](../../../../.github/workflows/mc1-pb00701-moving-phase-knot-falsifier.yml).

Run from the repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_moving_phase_knot_falsifier.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_moving_phase_knot_falsifier.py --contract --self-test
```

All arithmetic applied to original controls, intervals and knots is exact bounded `fractions.Fraction` polynomial arithmetic. The only nonalgebraic facts invoked are *exact* trigonometric zero positions at integer/half-integer phase and the nonzero derivative of sine/cosine at these positions. The proof has a fixed finite number of source coefficients, two true pieces, and a complete fixed event partition. Timeouts, numerical tolerance, finite sampling and arithmetic resource exhaustion **never** establish a root-free interval or root count. Input and report byte limits cause nontruth; they cannot turn an unresolved source into a proved one. Tests reject changed phase, knot, amplitude, parameter, malformed rationals, forged signs/orders/continuum, counterfeit root/census counts and gate escalation.

The independent census check parses **all 121 frozen v54 source specs** and the accepted v2 fifty-source registry, verifies all fifty original case ID/source SHA-256 identities and unchanged historical dispositions, then confirms the new source is not a member. The v2 proof's prior fifteen complete/35 newly complete source results remain unchanged. Source-specific before/after: **50→50 complete, delta 0**. Historical v54 route-refused cohort **20→20** and missing ordered-premise cohort **30→30** (frozen dispositions unchanged). This result satisfies the stated **bounded falsification C** only when its own fresh exact-head tests and independent technical review qualify; a passing local proof does not imply accepted integration.

## Remaining programme obligations and implications

The required **general moving-phase** two-span zero-component theorem remains open. A future positive route must freshly lower full original controls, invoke source-bound moving-phase child proofs, validate complete roots and positive components on both pieces, compare source-knot point values exactly, deduplicate one physical source coordinate, and retain independent one-sided orders. Mixed interval and isolated-root segmentation also remains necessary, including a zero interval absorbing its shared-knot endpoint. More general noncommon-factor/nonmonotone analytic event families and full coupled phase semantics remain unproved.

This adds no frozen historical case closure and cannot establish PB-007-01, PB-007-02/03/04, any MC-B/MC-1 gate, native material/topology, conventional engineering B-rep/STEP, independent STEP consumer use, or production authorization. All **26 supported operations**, original source/phase/provenance, canonical journals, bodies/lineage, refusal semantics and STEP requirements remain intact. For future OpenSimachinist research, an explicit split between *source-relative one-sided orders* and an unavailable global smooth multiplicity prevents invented topology/sign transfer. For MSAC, the result changes no UI or workflow authority.

**Alternatives rejected:** reusing the stationary report, inferring root order from count/parity, coercing a source-knot to a single analytic germ, accepting sampled trigonometry, or rewriting the v54 source-census denominator. None is a sound shortcut under this witness. A general exact mover-phase composition proof remains worth attempting; this is a scoped counterexample, not a universal impossibility.
