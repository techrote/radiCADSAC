# MC-038 / PB-007-01 — exact finite-budget event partition for polynomial H0/H1/H2 affine-phase sources

**8 November 2026. Research-only DETERMINISTIC_MODEL, no gate or main promotion.** Owner: [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100); [coordination #324](https://github.com/techrote/radiCADSAC/issues/324). Accepted main when work began: \`48222d6c40b15ad42cc36d56e6d25f3b284e7fc9\`; [#397](https://github.com/techrote/radiCADSAC/pull/397) exclusively owns main integration. This is a checkable **sufficient** finite-budget event procedure, not a total analytic event decision theorem or completed machining proof.

## Objective, falsifier and novelty

The original-source V44 isolation in [#452](https://github.com/techrote/radiCADSAC/pull/452) uses a separately established source-specific *single-root* theorem. This independent implementation proves an exhaustive root partition for a reusable family of exact H0/H1/H2 laws *without assuming the root count*. It returns either a source-bound set of certified zero-free cells and exactly-one-root cells covering the entire interval, or typed NONTRUTH. In addition to harmonic mixtures, it handles multiple physical roots and contiguous coefficient-continuous piece boundaries with nonzero knot signs.

Falsifiers: any missed event, unsupported or false multiplicity, incorrect root direction, invalid trigonometric/derivative interval, missing coverage cell, incorrectly continuous interface, or certificate falsely promoted to historical/MC-B truth. A resource limit never means zero roots.

## Exact admitted source grammar and boundaries

The source is a canonical Python dict with \`phase_offset_pi=a\`, \`phase_slope_pi=b\` and 1–4 contiguous \`pieces\`. Each piece has rational endpoints \`lo, hi\` and ascending-degree polynomial coefficient arrays \`H0, C1, S1, C2, S2\`. Degree is at most 3 and all rational numerators/denominators are bounded to 128 bits. The source scalar is

\[
F(t)=H_0(t)+\sum_{h=1}^{2}\left[C_h(t)\cos(h\pi(a+bt))+S_h(t)\sin(h\pi(a+bt))\right].
\]

The global interval lies in [-8,8]. On every adjacent piece boundary, all five coefficient functions must **exactly agree in value**; a single global phase applies. This is a strong, sufficient coefficient-continuity test, **not proof of an authentic B-spline source/codec**. Every exterior and interior piece boundary must also have a *strictly certified nonzero* physical sign, so exact knot/endpoint zeros are deliberately unsupported. A historical source requires independent source-identity and genuine spline-control admission before any of these model certificates can be applied to it.

## Constructive enclosure proof

1. **Exact \(\pi\).** Machin's identity \(\pi=16\arctan(1/5)-4\arctan(1/239)\), with alternating arctangent partial sums, supplies exact rational lower and upper enclosures. Never substitute a binary float.
2. **Exact trigonometry bounds.** At a rational cell midpoint, reduce rational phase modulo its exact period 2 in units of \(\pi\). Use Taylor polynomials of degrees \(2n+1\) (sine) and \(2n\) (cosine). Lagrange remainders, because all relevant derivative magnitudes are bounded by 1, are no larger than \(|z|^{2n+2}/(2n+2)!\) and \(|z|^{2n+1}/(2n+1)!\). Include the rational \(\pi\)-uncertainty radius. Extend each point enclosure over the source cell using the rigorous Lipschitz bound \(\pi_{\rm hi}|hb|(hi-lo)/2\). This remains valid across trigonometric extrema.
3. **Polynomial and derivative bounds.** Exact rational interval Horner evaluation encloses each polynomial and derivative. Interval operations enclose both the physical function \(F\) and
   \[
   F'=H'_0+\sum_h\bigl[C'_h\cos(h\theta)+S'_h\sin(h\theta)+h\pi b(S_h\cos(h\theta)-C_h\sin(h\theta))\bigr].
   \]
4. **Root-free leaves.** If the cell's full \(F\)-interval is strictly positive or strictly negative, it contains no zero. If its full \(F'\)-interval has one strict sign and the exact endpoint signs are both equal and nonzero, monotonicity also proves no root.
5. **One-simple-root leaves.** If \(F'\) has one strict sign on a cell, the two exact nonzero endpoint signs are opposite in the derivative direction, and the cell width is within the requested \(2^{-bits}\), the intermediate-value theorem proves existence and strict monotonicity proves exactly one *simple* crossing inside the reported strict rational bracket.
6. **No missing cells.** The verifier independently rechecks the exact SHA-256 of the canonical source, each leaf's rational interval and endpoint/derivative certificates, contiguous tiling, inter-piece signed continuity, event count and nonpromotion flags. It rejects gaps, overlaps, false signs, extra/missing roots and unauthorized promotion.

Subdivision uses certified nonzero rational pivots at the midpoint or two trisection alternatives. A pivot that cannot be proved nonzero is not treated as a root-free cut. The limits are **256** explored nodes, maximum depth **28**, at most **16** requested binary bits, and rational precision levels \`6,10,16,24\`. When no supported certificate emerges within these bounds, the call raises \`Nontruth\`. Tangencies, source-knot zeros, endpoints at zero, very close multiple roots or insufficient arithmetic may refuse. There is no generic termination proof for all admitted inputs.

## Executable evidence and falsification

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/pb00701_generic_interval_events_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
\`\`\`

The contract executes seven synthetic but source-shaped controls: a root-free harmonic, one H1 root, two H2 roots, two polynomial roots, two piecewise roots across a nonzero boundary, one mixed H1/H2 source, and a source-**shaped** V44 model with nonzero H2. The last one is expressly **not** an authenticated historical-source witness and cannot be added to the frozen denominator or V2 registry.

Eight focused tests check interval special values, source partitions, complete independent certificate replay, exact-algebraic pair controls for **30 rational root pairs × two positive scale factors**, exact periodic phase-shift metamorphism, tangent and endpoint refusal, discontinuity/grammar refusal, claim tampering and source-identity drift. Additional 110-digit mpmath checking was performed as a nonproof cross-check for 320 function/derivative inclusions across the seven source families, with zero observed violations. This numerical challenge is subordinate to, not a substitute for, rational interval proof.

The executable uses only Python's exact rational arithmetic for *truth*. It does not invoke a native geometry kernel, independent material oracle, STEP consumer or an expensive campaign. Arithmetic intermediate denominators may grow substantially despite the finite recursion/node/precision controls. Source import, authenticated B-spline equivalence and generic tangency resolution remain open.

## Truth/authority custody and next steps

- **Bounded positive result:** on success, a conservative and independently rechecked signed complete partition for a rational-polynomial H0/H1/H2 affine-phase source including zero, one or multiple simple roots and admissible C0 piece boundaries.
- **Open limitations:** true source-knot root handling, even-order zeros/tangencies, arbitrary harmonics/nonaffine phases, unbounded polynomial or spline coefficient grammar, finite-step termination for all admissible source data, verified original source codec and all general PB-007 obligations. This cannot close PB-007-01, PO-04/05/08, MC-B or MC-1.
- **Historical before=after:** immutable V54 121 original sources, 20 refused routes and 30 missing ordered premises; 50 V2 complete source-specific witnesses remain untouched. Newly closed historical IDs **[]**, required PB/PO discharges **0**. No change to main, current authority, proof registries, native geometry, engineering STEP or production permission.
- **Concrete successor:** independently authenticate real source spline controls, carry exact zero/knot sided orders across span boundaries, and establish a terminating strategy for non-simple zeros or record a principled frontier. Do not convert a bounded success or a resource refusal into general coverage.
