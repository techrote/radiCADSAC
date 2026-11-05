# MC-038 / PB-007-01 — exact frozen V9/V43 Cayley semialgebraic-admission boundary

**5 November 2026 · Bounded negative C · DETERMINISTIC_MODEL/source-verified analytical argument · DRAFT, not gate admission.**

**Proposed route under falsification:** `DIRECT_CAYLEY_SEMIALGEBRAIC_ELIMINATION_OF_VARIABLE_AMPLITUDE`: substitute a trigonometric half-angle variable and assume that a nonconstant rational B-spline amplitude becomes an algebraic function of that variable. The proposal would permit a finite polynomial/CAD/Sturm workflow *without* retaining the inverse-phase function or another analytic-event certificate.

**Result:** **false** for an actual frozen original v54 source with a historical V43 route refusal. Both original source spans become rational functions plus a **nonzero rational-polynomial multiple of `atan(u)`**. The classical logarithmic-monodromy theorem shows `atan(u)` is transcendental over `C(u)`; thus neither span function is algebraic over `C(u)`. This is stronger than merely having coefficients outside `Q`, but it refutes only this *defined direct algebraic Cayley elimination*. It does **not** refute algebraic *implicit-root representation after an independently proved transcendental isolation*, or decidability of the original analytic events.

## Source custody and preregistration

- Parent: [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100); live owner coordination: [#324 claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6661520825).
- Assigned main before isolated branch: `10dfeb8e1b1f00f8db34060fc9051302dab483a9` (post-#409).
- Original case: `composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100`.
- Canonical original specification SHA-256: `cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a`.
- Canonical complete v54 case-row SHA-256: `6e122da708ff0c68a339e0bfa5daba1e5321cb79e15af9e27b63712fb1348b63`.
- Immutable v54 121-source JSON Git blob: `5841c331579489b25caef38cd412bdbf286f9134`.
- Existing 50-source v2 complete-evidence JSON Git blob: `e52d3baf3692a011cf86234eeaa992ef407d99fd`.

The historical case was produced by `verify_pb00701_v10`. It has a certified first-span V9 monotone-ratio owner and a **historically refused** second-span `PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF` owner with reason `CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED`. The historical v54 disposition is `BLOCKED`, **not mathematical proof of impossibility**. The v2 register already records a separate, complete original-source witness for this case. This result creates **zero new historical closures**.

The exact original source parameter is **`source-time-t`**, domain `[0,2]`, true interior B-spline knot `t=1`, and unreset affine phase in turns `p(t)=t/8`. The source uses one zero-harmonic cosine, one H1 cosine and one H1 sine:

| Channel | Degree / actual knot sequence | Original rational controls |
|---|---|---|
| cosine H0 | degree 1, `[0,0,1,1,2,2]` | `[0,0,0,100]` |
| cosine H1 | degree 1, `[0,0,1,1,2,2]` | `[-1/2,1/2,1/2,1/2]` |
| sine H1 | degree 0, `[0,1,2]` | `[1,1]` |

Every piece is clamped in its original coordinate. Degree-one first and second span controls are respectively `[c0,c1]` and `[c2,c3]`. No synthetic harmonic or phase reset is introduced.

## Exact physical source across the true knot

Write `theta(t)=pi*t/4`. The exact B-spline extraction gives:

```text
F(t) = (t-1/2) cos(theta) + sin(theta),                  0 <= t <= 1
F(t) = 100(t-1) + (1/2) cos(theta) + sin(theta),         1 <= t <= 2
```

The two expressions agree at the actual knot: `F(1)=3 sqrt(2)/4>0`. At the source left endpoint `F(0)=-1/2<0`; at the right endpoint `F(2)=101>0`.

The first span has **exactly one simple, negative-to-positive physical crossing** in `(0,1)`. Its derivative is

```text
F'(t) = (1+pi/4) cos(theta) - (pi/4)(t-1/2) sin(theta).
```

For `0<=t<=1`, `cos(theta)>=sqrt(2)/2>7/10`, `sin(theta)>=0`, and `(t-1/2) sin(theta)<=1/2`. With `pi<22/7`,

```text
F'(t) >= cos(theta) - pi/8 > 7/10 - 11/28 = 43/140 > 0.
```

The derivative is strictly positive, so the intermediate-value crossing is unique and has analytic order one (odd parity). There are no tangencies or identity-zero subintervals in this original first span.

On the second span, `theta ∈ [pi/4,pi/2]`, so `cos(theta)>=0` and `sin(theta)>0`. Hence `F(t)>0` throughout `[1,2]`, including the knot, and there are zero second-span roots. The **complete original physical zero set has one simple root in `(0,1)`**. No numerical scan, arbitrary subdivision termination claim or resource-limit-as-truth is used.

This exact sign/crossing argument supports the source-specific physical interpretation but does **not** discharge the general PB-007-01 event theorem.

## Cayley substitution and its unavoidable inverse function

Set

```text
u = tan(theta/2) = tan(pi*t/8).
D = 1+u^2.
cos(theta) = (1-u^2)/D;  sin(theta) = 2u/D.
t = (8/pi) atan(u).
```

This is a smooth, strictly monotone, invertible coordinate change on the full original `[0,2]`. Its true knot maps to `u=tan(pi/8)=sqrt(2)-1`; its endpoints map to `u=0` and `u=1`. It is **not** a permission to erase the original `source-time-t` identity or put the knot at a fabricated rational coordinate.

Exact substitution yields, on the first open source piece `0<u<sqrt(2)-1`:

```text
D F_0(u) = (8/pi)*(1-u^2)*atan(u) - (1-u^2)/2 + 2u.
```

On the second open source piece `sqrt(2)-1<u<1`:

```text
D F_1(u) = (800/pi)*(1+u^2)*atan(u)
           -100*(1+u^2) + (1-u^2)/2 + 2u.
```

The executable verifies these **exact rational polynomial coefficient identities** independently of decimal evaluations:

| Original piece | coefficient of `atan(u)/pi`, degrees 0–2 | rational residual, degrees 0–2 |
|---|---|---|
| first | `[8,0,-8]` | `[-1/2,2,1/2]` |
| second | `[800,0,800]` | `[-199/2,2,-201/2]` |

The first coefficient never vanishes on its physical piece because `u<sqrt(2)-1<1`. The second coefficient is strictly positive for every real `u`. This is not a numerical Taylor-enclosure premise.

## Classical analytic theorem: algebraic functions have finite monodromy

Here is the mathematical step which the repository checker records as a **separate external classical argument**, not as a machine-formalized theorem.

For a germ near a real `u_0` in the physical interval, choose local analytic logarithm branches:

```text
atan(u) = [log(1+i*u) - log(1-i*u)] / (2*i).
```

Continue around a small loop enclosing `u=i` but not `u=-i` (with a path from the original basepoint avoiding the singularities). The first logarithm picks up `2*pi*i`, the other does not. Thus `atan(u_0)` changes by `pi` after one loop, and by `n*pi` after `n` loops.

An algebraic germ satisfying `P(u,f(u))=0` for a nonzero `P∈C[u,z]` has at most `deg_z P` values after continuation back to a nonsingular fixed basepoint (provided it is not an identically degenerate polynomial equation). **Infinite distinct branches contradict algebraicity.** Therefore `atan(u)` is transcendental over `C(u)`.

If the first original `F_0(u)` were algebraic over `C(u)`, solving its displayed identity for `atan(u)` (the multiplier `1-u²` is nonzero on the physical interval) would make `atan(u)` algebraic over `C(u)`, contradiction. Likewise `F_1(u)` would make `atan(u)` algebraic because `1+u²` is nonzero on the physical interval. Alternatively, analytic continuation changes each first-span and second-span value respectively by `8(1-u_0²)/D(u_0)` and `800`, nonzero on their physical domains. Each has infinite monodromy.

This proves the **two original open-piece function germs are not algebraic over `C(u)`**. In particular, they cannot be rational, algebraic-polynomial, or semialgebraic Nash-function representations of the physical event function under this substitution. This does not preclude a semialgebraically representable *zero set after independent transcendental analysis*, especially since this particular source already has one isolated root. The rejected shortcut was a pure **function-algebraization and event-equivalence claim**, not the existence of a semialgebraic singleton containing that root over arbitrary real parameters.

## Falsification scope, refusals and cost

**Proposed acceptance condition:** exact source-time/phase/knot/control provenance and a direct algebraic function of Cayley u on each source span, without an inverse phase, log, arctan or separate analytic zero theorem. **Observed:** original provenance passes, but the algebraicity premise fails on both spans. The appropriate verdict is **C (negative for this precisely defined proof route)**, *not* refusal of the original source itself or impossibility of computing its roots.

The verifier works with Python `fractions.Fraction` and canonical JSON/Git/SHA-256; no floating point drives the proof. Costs are bounded by two exact degree-one original spline pieces, four degree-two polynomial coefficient vectors, 121 frozen original rows and 50 registered source witnesses. The original-source model is exact only for this hard-pinned case and refuses any altered source identity, phase, spline knot, harmonic, source parameter or retained receipt.

Adversarial controls include source/whole-row mismatch, v2 provenance substitution, altered nonconstant controls, an added harmonic, an identity-zero mutation, an endpoint/knot/rate mutation, a forged even/tangential crossing, a fabricated extremely-close root bracket, changed denominator/case count, evidence promotion to native geometry, and a forged PB acceptance. Unadmitted prospective tangential, identity-zero or extremely-close source grammars **do not receive a truth verdict**.

The built-in `--self-test` and separate `unittest` test the source/census/algebra contract. The logarithmic-monodromy theorem is documented for independent mathematical inspection; the machine receipt flags that it is **not formally proved by Python**.

## Frozen census and programme impact

| Pinned metric | Before | After | Delta |
|---|---:|---:|---:|
| Original v54 cases | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Missing ordered-premise cases | 30 | 30 | 0 |
| Already complete v2 source-specific witnesses | 50 | 50 | 0 |

`new_historical_case_ids_closed=[]`. This single original already has a complete source witness; no count or classification is edited and no generic v54 owner route is repaired. The C finding restricts a **proposed** Cayley-to-semi-algebraic shortcut, not the accepted V9 or any existing V43 source-specific evidence. Unlike the separate [draft #392](https://github.com/techrote/radiCADSAC/pull/392), which challenges **direct rational-coefficient mixed trigonometric-polynomial theorem admission after radian-phase scaling**, this work challenges a different method: **removing nonconstant amplitudes by algebraic tangent half-angle substitution**. Both bounds coexist without claiming general event theorem undecidability.

PO-02/04/05/07/08 and PB-007-01/02/03/04 remain **OPEN**. MC-B and MC-1 remain `NOT_ESTABLISHED`. This is `DETERMINISTIC_MODEL` and classical source-bound mathematics, not independent-oracle, native geometry, actual usable STEP, durable-body or topology evidence. The original **26 supported machining operations**, native engineering STEP, canonical journal, body/lineage and production prohibitions remain intact.

**Dependency unlock:** an exact source event solver for the full signed nonconstant-amplitude grammar must retain original time-amplitude dependence, or independently justify its analytic-to-algebraic conversion and complete root/order/sign certificates. A mere Cayley rationalization of sin/cos is insufficient.

## Reproduce

From a full checkout of the exact PR head:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v9_cayley_monodromy_boundary_20261105.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/test_pb00701_v9_cayley_monodromy_boundary_20261105.py
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

**Integration hold:** independent source-critical and classical-monodromy mathematical review; literal-head hosted CI and original-source replay; no issue #100 comment, shared 77 ledger or proof registry mutation without separate owner coordination. Do not merge during this authoring session.
