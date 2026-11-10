# A2-JOIN-001 — finite exact analytic-join decision at a true B-spline knot

**Date:** 10 November 2026. **Classification:** conditional mathematical lemma + prospective deterministic-model checker. **Status:** Draft/HOLD for exact-module execution and independent A3/B1 source-critical admission. **Ownership:** `research/experimental/analytic-events/jets/**` only. Candidate base: accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; parent A2 Draft #471 at pre-work `96df36de47bc0120d7c70c92ec51fc9e6301cfaa`.

## Problem and predeclared falsifier

A real **structural** B-spline knot with interior multiplicity p in a degree-p spline guarantees only C0, yet particular controls can give a much smoother (even fully analytic) physical function. Conversely, matching value and finitely many low derivatives is insufficient to conclude that a knot is removable unless there is a proved *source-grammar-dependent* bound on the first possible mismatch.

**Falsifier:** one source-authenticated rational C0 two-span H0/H1/H2 example whose left/right analytic continuations have matching derivatives through the proven structural bound R but are not equal, or one nonremovable mismatch of order greater than R; also a wrong order or sign under negative source-time reversal, or acceptance of a substituted complete control vector under the original receipt.

This is not a generic B-spline curve algorithm, all-knot removal procedure, new root-count theorem, or general Continuous Skolem decidability statement.

## Admitted grammar and finite-jet theorem

A2 authenticates full clamped two-span degree-p rational B-spline inputs with knots `[L]*(p+1)+[K]*p+[R]*(p+1)` and exactly `2p+1` rational controls for **each** Fourier channel. The two pieces share the true knot value. Each reconstructed analytic side is

`F_side(t) = P_0(t) + sum_{h=1}^H [P_h(t) cos(2*pi*h*(a+b*t)) + Q_h(t) sin(2*pi*h*(a+b*t))]`,

with rational polynomial coefficients, **common nonzero rational** phase rate b and offset a, distinct integer harmonics, and rational K. Polynomial degree and harmonic count may be arbitrary finite values in the theorem; the existing *executable* A2 grammar bounds p<=3, H<=8, degree<=3, source/phase rational bit budgets, cyclotomic field order<=64 and sign refinement<=96. A refusal due to those budgets proves nothing about event existence or smoothness.

Extend each analytic side across the knot *as an analytic function*, and form `D(t)=F_right(t)-F_left(t)` in the canonical Fourier grammar; this is an algebraic difference, not a physical continuation of either piece outside its proper interval. If every channel polynomial of D is zero, D is identically zero and the true structural knot is **analytically removable** (this does *not* say the physical function vanishes).

Otherwise let d be the maximal polynomial degree among its nonzero Fourier channels, m the number of active positive harmonics and delta=1 if the zero-frequency channel is nonzero, else 0. The already established A2 separated-degree cyclotomic-moment lemma at rational K proves

`0 <= ord_K(D) <= R := d + delta + 2*m - 1.`

Because genuine shared-knot controls impose C0, ord_K(D)>=1. The first nonzero derivative order n therefore lies in `1..R`: the joined physical function is **exactly C^(n-1) but not C^n** at K. Vanishing of derivatives of D for all n=0..R proves D is identically zero, not merely apparently smooth through a heuristic cap. This is a finite conditional decision, independent of root isolation on open cells. If D has no nonzero channels, it is the *difference* which is identity-zero; never reclassify the physical source as a zero continuum.

**Proof:** Difference preserves the rational polynomial/Fourier grammar and the fixed rational affine phase. A2's moment argument separates powers of transcendental pi at rational phase/K, and the constant-amplitude annihilator gives the stated upper bound on the first nonzero local coefficient. Analytic sides share their value at K by exact spline control construction. If D has first nonzero Taylor coefficient of order n, derivatives through n-1 agree and derivative n does not; if D is identically zero, the analytic continuations agree in a neighborhood, indeed throughout their common analytic extension. The result is classical analytic uniqueness plus A2's source-specific finite valuation bound, not a newly discovered general theorem.

For signed reversal `t=A-u` with the physical side definitions swapped, the new difference is `D_rev(u)=-D(A-u)`. Thus the mismatch order stays n and the leading coefficient/sign acquires `(-1)^(n+1)`. A candidate violating that parity is a counterexample. A forward/negative signed coordinate map must always be checked against actual source orientation; knot-side labels cannot be copied unchanged.

## Infinite sharpness family and authenticated controls

For **every** p>=1, m>=0 and distinct rational cL,cR, the piecewise source

`F_side(t)=c_side*(t-1)^p*(1-sin(pi*t/2))^m`

has a genuine structural C0 knot at t=1, represented by rational degree-p clamped two-span Bernstein controls for its polynomial amplitudes. For the polynomial carrier, the exact combined controls are

`[(-1)^p*cL] + [0]*(2p-1) + [cR]`,

and for m>=1 the harmonic expansion of `(1-sin(pi*t/2))^m` has rational coefficients on harmonics 0..m, each multiplied by these same rational spline controls. At `s=t-1`,

`D(1+s)=(cR-cL)*s^p*(1-cos(pi*s/2))^m`
`        =(cR-cL)*(pi^2/8)^m*s^(p+2m)+O(s^(p+2m+2)).`

Thus the first mismatch order is **p+2m**. The structural ceiling is exactly `R=p+2m` for this family, and hence is sharp. The joined source can be smoother than the guaranteed C0 by an *arbitrarily high* finite order while never becoming analytic across the knot. For cL=cR the same complete control source represents a fully analytic join, despite retaining its formal repeated knot. Adding a common constant baseline can give a physically nonzero knot without changing the mismatch order.

The implementation tests only p=1..3 and m=0 or 1. The infinite family is a separately argued algebraic proof and must **not** be reclassified as exhaustively tested code. H1 m=1 gives actual mismatch orders 3, 4 and 5 and saturates the A2 bound within its present runtime grammar.

## Checker, source custody and independent controls

- `analytic_join.py` calls A2's **existing** `clamped_two_span_bezier` to reconstruct the full genuine source, makes an exact rational channel-by-channel difference, then calls the existing cyclotomic `point_germ` to distinguish identity-zero from a finite mismatch; no second spline codec or independent global isolator is introduced.
- The returned receipt binds the full spline hash, actual knot, source-reconstructed difference hash, signed local germ and finite continuity verdict. `verify_join` recomputes from supplied complete controls; it does not trust asserted order/sign/hash. The receipt explicitly sets `complete_zero_set_certified=false`, `original_source_certified=false`, `mc_b_established=false` and `production_authorized=false`.
- `test_analytic_join.py` includes rational Bernstein reconstruction, nonremovable and removable physical examples, signed reversal, intact-difference/different-source substitution, malformed knots, sign and implementation-budget refusals.
- Exact-head command, **not yet executed against the published A2 module**:

```sh
python3 -m unittest discover -s research/experimental/analytic-events/jets -p 'test_*.py' -v
```

**Independently executed algebraic shadow (not an A2 module replay):** using Python `fractions.Fraction`, exact degree-p Bernstein carrier reconstruction passed **1,840/1,840** endpoint/interpolation checks across p=1..20, four rational parameter pairs, p+1 distinct points on each of two sides. The rational formal-series leading-coefficient oracle passed **640/640** combinations with p=1..20 and m=0..15, exact leading coefficient `(cR-cL)/2^m` in `z=pi*s/2`, with all lower coefficients zero. This verifies only the independent algebraic family, not the new wrapper, the exact-hosted branch head, arbitrary B-splines or source-provenance admission. No native, STEP or paid workflows were run.

**Budget/complexity:** the wrapper constructs one difference source on at most eight Fourier channels and degree three and invokes one already bounded A2 local moment/sign decision. Worst-case costs inherit A2's cyclotomic field and interval precision limits; no hot geometry or simulation path, no speedup claimed. Under unrestricted exact arithmetic for fixed admitted rational input, the conditional finite-jet theorem terminates; reaching a finite implementation cap is a typed refusal.

## Prior art and composition boundary

The repeated-knot continuity lower bound C^(p-r), and the possibility of higher smoothness for special controls, are standard spline facts; see the [nurbspy B-spline derivation](https://turbo-sim.github.io/nurbspy/theory/bspline.html) and the [MIT Hyperbook knot treatment](https://web.mit.edu/hyperbook/Patrikalakis-Maekawa-Cho/node18.html). Constant-coefficient ODE uniqueness, exponential-polynomial zero multiplicities and Bernstein/de Boor extraction are prior art. The A2 local order bound is inherited, not newly reproved or promoted. This new research **composition interface** distinguishes finite same-source derivative agreement from analytic identity at a *genuine* C0 knot.

**B1/A1 interface warning:** an artificially introduced common-refinement partition endpoint is not automatically a genuine B-spline knot. A join receipt must carry `TRUE_CLAMPED_C0_BSPLINE_KNOT` provenance and a whole-source hash, while an artificial split carries its own source-preserving transformation witness. Equal finite jets do not independently prove open-cell zero coverage or safe Boolean/topology composition. In particular A2's earlier continuum-alias counterexample still blocks using a knot-local receipt as a complete physical zero-set certificate.

## Requested independent qualification and next action

- **A3:** execute literal-head `test_analytic_join.py` against the published `cyclotomic_moments.py` and independently replay the true p=1..3 B-spline source and signed reversal. Challenge same-difference/different-source receipts, identity-zero difference versus physical zero continuum, the sharp bound and implementation resource boundaries.
- **B1:** review typed `TRUE_CLAMPED_C0_BSPLINE_KNOT` versus B1 artificial refinement provenance and whether this source-bound removable-knot witness can safely compose with common-refinement product certificates without silently asserting global zero-set completion.
- **Stop criterion:** if exact-module replay fails or source authenticity/finite sign verification is inconclusive, retain the counterexample/evidence as Draft and report HOLD, not a gate change.

Historical **121/20/30/50** census and all **26** machining operations unchanged; zero original closures, zero PB/PO discharges; MC-B and MC-1 **NOT_ESTABLISHED**, `production_authorized=false`. No production/native/STEP/proof-registry updates, merges or author-branch cross-edits.
