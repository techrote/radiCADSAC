# MC-038 / PB-007-01 — exactly two physical roots after a nonzero genuine source knot

**8 November 2026.** Research only, `DETERMINISTIC_MODEL`. Owner: [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). Coordination: [#324](https://github.com/techrote/radiCADSAC/issues/324). Source authority: accepted `main=48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. **NO MERGE** without the #397 main integrator; **no historical closure, PB/PO discharge, native geometry or STEP claim**.

## New falsifiable capability and prior art

Earlier restricted knot proofs [#447](https://github.com/techrote/radiCADSAC/pull/447) and [#449](https://github.com/techrote/radiCADSAC/pull/449) handle a zero-valued true knot with an H0 ramp and one additional right-span root, using monotonic quotient arguments. The present *different* prospective family has a **nonzero true knot** and **two simple right-span roots**. Any unreported root, invented knot zero, wrong phase/time coordinate, invalid ordinary B-spline controls, false sign or falsely claimed original-source closure falsifies the certificate. It is a sound, deliberately restricted sufficient criterion, not a generic analytic event solver.

## Exact source grammar

Source time `t in [0,2]`, true repeated interior knot `t=1`, phase `t/4` turns (angle `pi*t/2`). Ordinary degree-two clamped B-spline knot vector `[0,0,0,1,1,2,2,2]`, five coefficients for each harmonic amplitude, and exact rational parameters `m,b`:

| Source amplitude | Actual five B-spline controls |
| --- | --- |
| H0 | `[m,m,m,m+b/2,m+b]` |
| H1 cosine | `[1,1,1,1,1]` |
| H1 sine | `[0,0,0,0,0]` |

The controls represent the exact piecewise laws `H0=m` on `[0,1]`, and `H0=m+b*(t-1)` on `[1,2]`. The common control at the degree-two double knot makes coefficients continuous. H1 cosine/sine are unchanged. There is no H2 term. With `x=t-1` on the right,

```text
F_L(t)    = m + cos(pi*t/2),              0 <= t <= 1
F_R(1+x)  = m + b*x - sin(pi*x/2),        0 <= x <= 1
```

This is a prospective variant, **not** the unchanged frozen V6 original. The verifier pins the actual original `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0` (source SHA-256 `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1`) only as source-grammar/phase provenance. Original H0 differs. The frozen V54 and V2 Git blobs remain unchanged.

## Theorem: strict sufficient criterion, exhaustive count and physical signs

For canonical rationals m,b, define `q=m+b/2`. Admit only

```text
m > 0;   m+b > 1;   q > 0;   2*q*q < 1.
```

These are **entirely exact rational comparisons**. The strict `2q²<1` and `q>0` establish `q<sqrt(2)/2` without evaluating a transcendental constant. Consequently,

- `F_L(t)=m+cos(pi*t/2)>0` for all left source times `0<=t<=1`.
- `F_R(1)=m>0` at the real source knot `t=1`.
- `F_R(3/2)=q-sqrt(2)/2<0`.
- `F_R(2)=m+b-1>0`.

For `0<x<1`, the ordinary analytic second derivative in the local right coordinate is

```text
d²F_R/dx² = (pi/2)^2 * sin(pi*x/2) > 0.
```

Thus `F_R` is strictly convex. Each of the two disjoint intervals `(0,1/2)`, `(1/2,1)` contains a crossing by continuity and the proved opposite endpoint signs. A strictly convex differentiable function cannot have three distinct zeros on this interval: the middle zero would have to lie strictly below the chord joining outer zeros. Both zeros are simple, with decreasing/increasing local sign crossing respectively. **Exactly** two physical zeros occur over the entire original source interval; neither lies at the knot or an exterior endpoint, and both are given by strict rational *source-time brackets* `(1,3/2)` and `(3/2,2)`. No invented exact transcendental root coordinate is emitted.

The three maximal signed physical nonzero regions have signs **POSITIVE / NEGATIVE / POSITIVE**. In particular the continuous nonzero true knot at `t=1` belongs to the first positive region and does not introduce a separate event.

One concrete rational witness is `m=1/5, b=9/10`. Then `q=13/20`, `2q²=169/200<1`, and `m+b-1=1/10>0`. Further valid independent controls include `(1/4,4/5)` and `(1/3,7/10)`. Outside these sufficient conditions the verifier returns typed **NONTRUTH refusal**, not a false no-root result. It does not claim to decide tangent cases, a generic affine-H1 source or arbitrary B-spline phases.

## Executable evidence and custody

Run at the literal Git head:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v6_nonzero_knot_two_roots_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

The verifier checks the exact frozen V54/V2 source Git blob identities, 121 source IDs, 20 route refusals, 30 missing ordered source premises, 50 existing V2 witnesses, and the pinned original V6 source/phase/H1 grammar. It constructs the prospective source certificate from rational parameters and independently checks the entire adjacent machine receipt with canonical **type-sensitive** JSON comparison. Receipt input is byte/nesting/integer bounded and duplicate-key rejecting.

Adversarial tests cover exact degree-two spline evaluation; alternative rational witnesses; refusal outside the strict sufficient region; malformed/noncanonical/unbounded rationals; wrong original identity and phase; altered event count, signs, PB/PO and production flags; duplicate keys, excessive JSON depth/bytes, noninteger numbers and malformed documents. The certificate is mathematical and source-based, not produced by finite sampling.

## Independent limitations and programme significance

This supplies a novel **restricted** exact two-event construction over an authentic nonzero B-spline knot and prevents an endpoint-only solver from missing two internal roots while reporting no events. It is a useful building block for future source-time composition, but **does not establish PB-007-01, PO-04/05/08, MC-B, MC-1 or source-wide analytic decidability**. It is not a new complete historical case: the source is prospective and the V6 original is used for grammar provenance only.

Historical before/after remains **121 originals / 20 route refusals / 30 missing ordered premises / 50 preexisting V2 witnesses**, with zero delta and zero required discharges. No native geometry, machine workload, conventional STEP, production or expensive campaign is qualified. Future extensions should admit genuinely different H1 coefficients, source-pinned cases not covered by saved V2 witnesses, and repeated/event-tangent roots using independently checkable exact arithmetic. Maintain a separate owner for final review and do not infer gate passage from a passing research CI workflow.
