# PB-007-01: exact affine-H1 strict-concavity event theorem on frozen V12

**9 November 2026 · MC-038 · source-bound deterministic mathematical model · research only, Draft.**  
Implementation: `pb00701_affine_h1_concavity_v12_20261109.py`; exact committed replay: `pb00701-affine-h1-concavity-v12-20261109.json`.

## New sufficient theorem and proof

Let `theta(t)=pi*t/2`, `t in [0,1]`, and

```text
F(t) = h0+h1*t + (c0+c1*t)*cos(theta(t)) + (s0+s1*t)*sin(theta(t)).
```

All six parameters are **exact rationals** with canonical text and bounded bit length. Define `m=min(c1,-s1)` and `M=max(0,-min_[0,1] C,-min_[0,1] S)`.

If **`m>M`**, then `F''(t)<0` throughout the interval. Put `omega=pi/2`; `H0''=0` and

```text
F'' = -2*omega*(c1*sin(theta)-s1*cos(theta))
      - omega^2*(C*cos(theta)+S*sin(theta)).
```

Since `sin(theta),cos(theta)>=0` and their sum is strictly positive,

```text
F'' <= omega*(-2*m + omega*M)*(sin(theta)+cos(theta)) < 0
```

because `0<omega<2` (from `3<pi<4`) and `m>M>=0`. No numerical subdivision, spectral approximation, finite-resolution root scan, or stationary-root assumption is used.

If further `F(0)<0`, `F(1)<0` and `F(1/2)>0`, then IVT supplies two roots in **disjoint rational source-time brackets `(0,1/2)`** and **`(1/2,1)`**. Strict concavity implies strictly decreasing derivative and thus at most two distinct roots by Rolle; the sign reversals ensure both roots are simple. The three maximal open sign regions are **NEGATIVE, POSITIVE, NEGATIVE**.

All signs are exact: `F(0)=h0+c0`, `F(1)=h0+h1+s0+s1` and

```text
F(1/2) = (h0+h1/2) + ((c0+c1/2+s0+s1/2)/2)*sqrt(2).
```

The implementation compares signs in `Q(sqrt(2))` by exact rational-square inequalities. No floating-point pi or trigonometric samples enter acceptance.

This **does not** solve arbitrary variable-amplitude, H2, moving multi-knot, tangency, discontinuity, phase, source codec or geometric topology cases. If any premise fails, return `RefusedNontruth`, not a fictitious zero set. The theorem proves a new *sufficient subfamily*, not a decision for all admitted sources.

## Real immutable V12 original, not a constructed substitute

The verified frozen source is `composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0`, source SHA-256 `ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5`, row SHA-256 `d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3`.

The complete source has degree-1 B-spline H1 controls `C: (-1/3,2/3,2/3,2/3)`, `S: (2/3,-1/3,-1/3,-1/3)`, degree-0 zero H0, knot vector `(0,0,1,1,2,2)` for H1, and unchanged phase `beta=t/4` turns on `[0,2]`.

- On the *actual first span* `[0,1]`, exact lowering yields `H0=0`, `C=t-1/3`, `S=2/3-t`. Thus `m=1`, `M=1/3`, `F(0)=F(1)=-1/3`, `F(1/2)=sqrt(2)/6>0`. **Two simple roots** follow.
- The *actual second span* `[1,2]` has `C=2/3>0`, `S=-1/3<0`, `H0=0`; there `theta` lies in `[pi/2,pi]`, so `C*cos(theta)+S*sin(theta)<0` everywhere, including endpoints. The source knot at `t=1` has identical one-sided coefficient values and physical `F(1)=-1/3`; no extra knot event or sign region is invented.
- The entire frozen V12 source consequently has exactly two simple roots in the stated first-span brackets and maximal open signs `(-,+,-)`, zero at knot **false**. The independent complete-source V2 receipt *already* establishes this original; our result is an alternate proof method, **zero additional historical closures**.

The script validates exact frozen v54 and post-v54 V2 Git blobs (`5841c331...`, `e52d3baf...`), historical **121/20/30/50** denominator and original V12 row/source SHA before accepting `--contract`. Stand-alone self-tests check hardcoded source identity; only repository-backed contract checks on-disk frozen corpus and V2 evidence.

## Orthogonal positive example and falsifiers

The prospective test `H0=3/10`, `C=t-3/5`, `S=2/5-t` gives `W=C*S'-S*C'=+1/5`, `m=1`, `M=3/5`, negative rational endpoints and a strictly positive midpoint. It therefore has two simple roots by the new theorem, but lies **outside** the `H0=0, rW<=0` sufficiency family of [PR #444](https://github.com/techrote/radiCADSAC/pull/444), and outside the constant H1 family of [PR #445](https://github.com/techrote/radiCADSAC/pull/445). This is prospective source-grammar coverage, not a new frozen historical source. An exact affine-H0 positive control proves curvature does not depend on H0 being constant.

Falsifiers: source/row/spline/phase hash drift; broken `m>M`; wrong coefficient bound; nonnegative endpoint, nonpositive/zero algebraic midpoint, invented tangency/order, invalid tail/knot transfer, noncanonical rational, oversize input, corrupt/duplicated JSON or forged receipt/gate metadata. Replay recomputes complete source-bound claims from pinned source.

## Reproduce and evidence boundaries

On an accepted research tree with these three additive files:

```bash
python3 research/machining-completeness/tasks/MC-038/pb00701_affine_h1_concavity_v12_20261109.py --self-test
python3 research/machining-completeness/tasks/MC-038/pb00701_affine_h1_concavity_v12_20261109.py --contract
python3 research/machining-completeness/tasks/MC-038/pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py --self-test
```

Development-local deterministic tests: **9/9 passed**. Independent, **nonauthoritative** 90-digit numerical root checks: original V12 `0.187815982081791821378382094`, `0.812184017918208178621617906`; prospective positive-W source `0.216803550228680031305063045`, `0.783196449771319968694936955`; no sampled positive second derivative in 201-grid controls. The exact proof is the inequality above, not these samples.

**Pending:** repository exact-head hosted CI, independent mathematical/source-critical review and controlled integration by PR #397's owner. Do not merge this Draft as a replacement of an existing original witness. No frozen corpus mutation, authority change, new PB/PO discharge, native material/topology, conventional STEP, independent consumer, paid campaign or production authorization. All 26 operations and historical 121/20/30/50 remain unchanged. MC-B and MC-1 remain `NOT_ESTABLISHED`.
