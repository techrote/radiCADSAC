# A2-KNOT-PRODUCT-001 — Endpoint-positive cones do not preserve knot zero orders

**Status:** bounded deterministic research experiment, **Draft / HOLD**, 10 November 2026. This is a source-critical A2/B1/A1 *interface* challenge, not a new transcendence theorem, a general event isolator, MC-038 evidence acceptance, native geometry or a performance result.

## Source, authority and preregistration

- Exact accepted `main`: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.
- Reused sole A2 Draft [PR #471](https://github.com/techrote/radiCADSAC/pull/471) from its pre-experiment head `56c0b0609a90a7dc074dc423484f2b75a2fd0c65`; no author or shared implementation outside `research/experimental/analytic-events/jets/**` was edited.
- [A2 temporary lease and falsifier](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6756080793), [A3 previous review](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5834336109), [B5 exact positivity-seam finding](https://github.com/techrote/radiCADSAC/blob/8200c6c086d27e0d51381f1b1779383696b1e50e/research/experimental/ab-campaign/integration/2026-11-10-positive-cone-seam-review.md).
- Frozen **121/20/30/50** historical counts, **26** operations, original evidence, MC-B/MC-1 **NOT_ESTABLISHED**, `production_authorized=false`; no changed historical sources or live authority.
- **Falsifier:** A2 yields any order other than 4 left / 3 right on the constructed source-authenticated knot; time reversal does not exchange to 3/4; any source edit passes the old receipt; or B1 `POS` incorrectly certifies closed-interval strict positivity where an endpoint Bernstein coefficient vanishes.

## Lemma: finite local product-germ transfer (infinite parameter family)

For any two *nonidentically-zero* real-analytic germs `f`, `p` at rational physical point `t0`, with finite orders `r`, `q` and nonzero leading real coefficients `a`, `c`, the product has order **r+q**, leading coefficient **ac**, right sign `sgn(ac)`, and left sign `(-1)^(r+q) sgn(ac)`. Proof: write `f(t0+s)=a s^r+O(s^(r+1))` and `p(t0+s)=c s^q+O(s^(q+1))`; multiplication gives a nonzero `ac s^(r+q)` term. At a genuine C0 knot this law applies **separately** to each analytic side, even when left/right orders differ. No global smooth multiplicity is implied; an identically zero side is a continuum, not a finite order.

Specific prospective family, for any integers `q>=0`, `m>=1` and nonzero rational `c`:

```text
F_{q,m,c}(t) = c (t-1)^q (1 - sin(pi*t/2))^m.
```

With `s=t-1`, `1-sin(pi*t/2)=1-cos(pi*s/2)=(pi^2/8)s^2+O(s^4)`. Hence order exactly **q+2m**, right sign `sgn(c)`, left sign `(-1)^q sgn(c)`; this is valid for the **infinite** family. The A2 executable subgrammar limits `m` to 1 or 2, `q` to 0..3 and harmonic degree to <=3. The statement is standard analytic valuation arithmetic, not novel mathematics.

### B1 Bernstein endpoint precondition

On `[0,1]`, `P_L(t)=(1-t)^2` has quadratic Bernstein coefficients `(1,0,0)`. On `[1,2]`, `P_R(t)=t-1` has *degree-elevated* quadratic coefficients `(0,1/2,1)`. Both are nonnegative coefficient vectors with at least one strictly positive entry, so B1's `POS` cone proves strict **interior** positivity; nevertheless their shared physical endpoint at `t=1` is exactly zero. Thus `POS` cannot be silently promoted to `CLOSED_STRICT_POS`.

A sufficient *closed* strict-positivity proof for a Bernstein leaf with all coefficients nonnegative is: at least one coefficient positive **and both endpoint coefficients positive** (`b0>0`, `bn>0`). Bernstein basis functions are positive in the open unit interval, and endpoint evaluations equal `b0,bn`. If either endpoint coefficient is zero, classify `INTERIOR_POS_ENDPOINT_ZERO` and use an exact local-sided germ; if mixed coefficients, classify `UNKNOWN`. This is a proposed typed A2/B1 interface, not an accepted shared schema.

### Genuine knot instance and time reversal

The complete clamped quadratic spline source is:

```text
degree = 2
knots = [0,0,0, 1,1, 2,2,2]
h=0 cosine controls = [1, 0, 0, 1/2, 1]
h=0 sine   controls = [0, 0, 0, 0, 0]
h=1 cosine controls = [0, 0, 0, 0, 0]
h=1 sine   controls = [-1, 0, 0, -1/2, -1]
phase turns = t/4
```

Each of the two actual Bernstein pieces is the polynomial factor `P_L` or `P_R` times `1-sin(pi*t/2)`. At `t=1`, the **left-sided order is 4**, the **right-sided order is 3**, and the exterior signs are **positive on both sides**. The physical zero is counted **once**, despite distinct sided orders. Under `t=2-u`, the same source must produce **3 left / 4 right**. All source controls, phase and knots must be authenticated for the receipt; matching event numbers without matching source identity is insufficient.

The independent nonzero knot control uses h0 cosine controls `[3,3,3,4,6]`, h1 cosine controls `[0,1,2,3,2]`, h1 sine controls `[1,0,0,2,3]`, phase turns `1/8+t/4`: its shared knot value is `3-sqrt(2)>0` and its side derivatives are generally unequal. Reversal must remain `NONZERO_KNOT`, not create a false zero. This covers genuinely asymmetric, nonzero C0 knot behaviour beyond the previous equal-zero fixture.

## Executable evidence, cost and status

New standalone checker: [`factor_knot_challenge.py`](factor_knot_challenge.py). Its published Git blob should be verified against **`12e09a77ba3d533622b605d850145017ba768e58`** before qualifying a later run.

```sh
python3 research/experimental/analytic-events/jets/factor_knot_challenge.py --oracle-only
python3 research/experimental/analytic-events/jets/factor_knot_challenge.py
```

**Actually executed locally before publication:** standalone standard-library rational formal-power-series controls: **72/72 PASS**, `m=1..8`, `q=0..8`, with exact zero coefficients before `q+2m` and leading rational coefficient `2^-m` in variable `z=pi*(t-1)/2`; separate Bernstein endpoint-zero control PASS. No numerical sampling was used as an exhaustive zero certificate. Local independent SymPy 1.14.0 limits also gave `pi^(2m)/8^m` for m=1,2 and q=0..3, but are ancillary, not the theorem proof.

**Not executed:** the second command, which imports the complete published A2 `cyclotomic_moments.py` at the PR head, was authored and published but not run in this environment. It contains 16 prospective H1/H2 point-germ + forgery checks, the full 4/3 → 3/4 knot-source/reversal/source-drift test, and the independently nonzero asymmetric-knot control. These are **pending** until exact-head remote checkout execution. Do not conflate the 72 independently executed rational controls with source-matched A2 test passes.

Cost: the optional A2 replay uses 16 source-bounded point checks plus two physical knot cases; no native, STEP, paid model, broad benchmark, runtime acceleration, or production use. The rational oracle truncates to degree `q+2m` and has fixed finite loops (72 cases). No evidence of general B-spline product grammar admission, arbitrary nonrational phases, global root enumeration, or B1 producer authentication.

## Independent review requests and next falsifier

- **A3:** execute the published exact-head module and checker, independently verify true Bernstein extraction/source phase of the asymmetrical 4/3 knot, negative time reversal and the modified-but-same-local-value source replay refusal. Challenge signed interval proof and exact resource limits if any case fails.
- **B1/B5:** do not equate `POS` with positive on the closed piece. Request a source-bound interface that exposes endpoint vanishing plus per-side multiplicity and distinguishes `CLOSED_STRICT_POS`, `INTERIOR_POS_ENDPOINT_ZERO`, `UNKNOWN`; do not claim Boolean/topology composition.
- **Next highest-value falsifier:** a genuinely C0 knot with one **identity-zero** side and another **finite positive-order** product side under source-time reversal. Its physical event semantics are not obtained by merely adding two finite orders.

**Disposition: GO** for the exact analytic local product law and bounded independent rational controls; **HOLD** for implementation replay and B1 source-authenticated composition; **NO GO** for any automatic root-preservation claim from B1 `POS` alone. No original V12/V6 closure, MC gate promotion, or production integration is authorized.

## Prior art

The local order-addition law is elementary analytic function theory. Bernstein coefficient nonnegativity and de Casteljau positivity are established (Bertot, Guilhot & Mahboubi, *A formal study of Bernstein coefficients and polynomials*, 2011, DOI: [10.1017/S0960129511000090](https://doi.org/10.1017/S0960129511000090)). Sloth (2017) demonstrates broader limits on Bernstein nonnegativity certificates when zeros are present ([arXiv:1710.05735](https://arxiv.org/abs/1710.05735)). This experiment contributes an explicitly authenticated-sided contract *candidate*, not mathematical novelty or a solution to the Continuous Skolem problem.
