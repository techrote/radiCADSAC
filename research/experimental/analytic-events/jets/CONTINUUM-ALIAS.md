# A2-CONTINUUM-001 — A finite sided knot germ is not a complete physical zero-set

**10 November 2026 · deterministic mathematical research · Draft / HOLD.** Owns only `research/experimental/analytic-events/jets/**`, extends existing A2 [Draft PR #471](https://github.com/techrote/radiCADSAC/pull/471). Source lease: [#324 comment 6757060323](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6757060323). Before this increment: accepted `main=48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; A2 head `bce8bde5184c32af80fc1ff9389725bb3a627bc7`, source Git blob `cyclotomic_moments.py=77b79335ffffb8382eb348afd44e7d9416f34583`. Recheck live heads before applying any conclusion.

## The falsifier and precise result

Local knot evidence is necessary but insufficient for **global zero-set completeness**, even after the correct identity-zero/finite-order sided classification. For `u=t-1`, integers `q>=1`, `m>=1`, rational `lambda` and physical domain `0<=t<=2`, define the prospective piecewise physical source

```text
F(t) = 0,                                             0 <= t <= 1
F(t) = u^q * (1-lambda*u) * (1-sin(pi*t/2))^m,      1 <= t <= 2 .
```

Every such source is continuous at the genuine knot `t=1`. The left analytic piece is identically zero (a **continuum**, not a root of some enormous finite multiplicity). On the right, since `1-sin(pi*t/2)=1-cos(pi*u/2)=(pi^2/8)u^2+O(u^4)`, the *finite* right-sided knot order is **q+2m**, with positive right leading sign. Importantly, this germ does not depend on `lambda` at all at leading order.

On `1<t<=2`, `1-sin(pi*t/2)>0`; therefore the **complete physical zero-set** is `[0,1]` for `lambda=0`, whereas `lambda>1` gives `[0,1] U {1+1/lambda}`. In particular, `lambda=2` adds the exact isolated root `t=3/2` while retaining exactly the same identity-zero left span, right order and right leading sign at the knot. The extra root is a **simple crossing**: `1-lambda*u` is a simple factor and the other factors are nonzero there.

This is an infinite parameter family, proven by factorization and the elementary analytic expansion; it is **not a novel analytic identity theorem, general root isolator or proof of arbitrary-phase decidability**. For `lambda=1` the added root is the exterior endpoint `t=2`, and for `0<lambda<1` there is no extra root on this domain. The code tests a bounded subfamily, not the infinite theorem by enumeration.

### Authentic C0 spline realization, not a fabricated piecewise value

For `m=1`, the form is an H0/H1 rational-polynomial-amplitude source with global phase **in turns** `offset=0, rate=1/4`, h0 cosine amplitude `P(t)`, h1 sine amplitude `-P(t)`, and all other channels zero. For polynomial degree `p >= q+1`, represent the zero left piece and right polynomial `P=u^q(1-lambda*u)` as exact Bernstein controls. Use a clamped degree-p two-span knot vector

```text
[0]*(p+1) + [1]*p + [2]*(p+1)
```

and join the left and right controls at the **single shared zero control** at `t=1`, thereby proving C0 source continuity. Example `p=2,q=1`:

```text
lambda=0: h0 cosine controls [0,0,0, 1/2, 1]
lambda=2: h0 cosine controls [0,0,0, 1/2,-1]
h1 sine controls are the negatives of h0 cosine controls
h0 sine and h1 cosine controls are all zero
```

Both have identical left identity, right knot order **3**, and positive right germ, but the right Bernstein polynomials are respectively `u` and `u-2u^2`. Changing only the last right control creates the additional interior root. The complete spline source hash changes. A caller must never transfer a local certificate from one to the other or infer a complete event partition from a knot receipt.

Under signed source-time reversal `t=2-v`, the left zero continuum moves to **[1,2]**, the finite germ becomes the **left** germ at `v=1`, and the extra root moves from `3/2` to `1/2`. Counting the shared knot as an additional isolated zero would double-count the boundary of a continuum. The correct local category is `CONTINUUM_ADJACENT_ZERO_KNOT` with isolated-knot count **0**, not `SINGLE_PHYSICAL_ZERO_KNOT` with count 1.

## Exact reproducibility and falsification criteria

Run, from the repository root:

```sh
python3 research/experimental/analytic-events/jets/continuum_alias_challenge.py
python3 research/experimental/analytic-events/jets/continuum_alias_challenge.py --a2-module research/experimental/analytic-events/jets/cyclotomic_moments.py
```

The first command is standalone standard-library **Fraction/Bernstein** independent oracle work. The second deliberately checks the complete A2 module's exact Git blob `77b79335ffffb8382eb348afd44e7d9416f34583` before import; it refuses changed or unreviewed source. Re-pin and review the script if A2 module legitimately changes. No numerical sampling decides root absence: on the right it follows from exact rational polynomial factorization and a strict analytic factor sign.

**Actually executed before publication:** 12 prospective p/q/lambda exact Bernstein reconstructions (p,q) = (2,1),(3,1),(3,2), lambda = 0,2,3,-1; **6** admitted extra-root controls; **3** matched-local-germ but unequal-global-zero-set/source-identity pairs; eight independent exact rational Taylor-series controls for `(1-cos z)^m`, m=1..8, with first nonzero coefficient `2^-m` at degree 2m. The standalone script exited successfully and was syntax-compiled; no full upstream module execution was available in the author-local environment. The complete source-pinned replay is **authored but not executed**; it must not be reported as PASS without actual checkout execution.

Explicit falsifiers for the source-pinned replay: A2 returns a finite-multiplicity left zero instead of `IDENTITY_ZERO_ON_ANALYTIC_SPAN`; returns an isolated knot event; returns right order other than q+2; misclassifies signed reversal; allows the `lambda=0` full knot receipt to verify against `lambda=2` source; or gives source hashes identical for these distinct complete controls. A separate **global consumer** falsifier is claiming full zero-set equality merely because all *local* knot features agree. The A2 code is not presently known to make that global claim.

## Certificate consumer interface and open obligations

For each genuine knot: authenticate **complete** source controls/knots/phase, then preserve `LEFT_IDENTITY_CONTINUUM` or finite left order and `RIGHT_IDENTITY_CONTINUUM` or finite right order independently; carry a single knot ownership, continuum endpoint inclusion and source hash. A local germ receipt proves **only local analytic behavior**. A complete interval event receipt must additionally certify all open-root cells and exterior boundaries for the same entire source (A1/#453 or another independently reviewed global mechanism, not a freely inferred union). A B1 `CLOSED_STRICT_POS` factor might prove an appropriate open cell, but its certificate must authenticate the **same physical source** and preserve endpoint conditions. Do not collapse `IDENTITY_ZERO` to `order=infinity` and feed it into finite-order addition.

This source is a deliberate grammar slice, not arbitrary spline knots, NURBS, nonlinear time, global H0/H1/H2 event isolation, or MC-038 input admissibility. Spline degree is limited by current A2 prototype to 1..3, and its active harmonic count/degree have implementation budgets. The mathematical `m>=1` expansion is an infinite-family proof, while the executable source-pinned replay uses `m=1` and `p<=3`. Neither fixed implementation refusal nor a bounded sign-series cap falsifies mathematical termination.

## Source-critical literature and interpretation

- DLMF [§1.10(i), zeros](https://dlmf.nist.gov/1.10) defines finite analytic zero multiplicity by first nonzero Taylor coefficient; an identity-zero analytic piece has no finite multiplicity.
- Carl de Boor, *A Practical Guide to Splines* (2001), standard multiple-knot C0 spline/Bezier representation. [Reference scan](https://djvu.online/file/W5YE3VGOgt1Ml); C0 source authentication must use complete knot/control vectors.
- [Mathlib analytic isolated zeros / identity theorem](https://imperialcollegelondon.github.io/FLT/docs/Mathlib/Analysis/Analytic/IsolatedZeros.html) formalizes the distinct cases of a locally identically zero analytic function and an isolated finite zero.
- Existing radiCADSAC [#453](https://github.com/techrote/radiCADSAC/pull/453) supplies bounded global event work, [#462](https://github.com/techrote/radiCADSAC/pull/462) source-time/knot composition, [#471](https://github.com/techrote/radiCADSAC/pull/471) A2 local germ receipts, and B1 [#473](https://github.com/techrote/radiCADSAC/pull/473) closed-positivity contracts. No result here silently supersedes them.

**Disposition:** GO for elementary theorem and bounded executed exact oracle; HOLD for full A2 exact-module replay and independent A3/B1 interface review; NO-GO for deriving a complete physical zero-set from local knot certificates alone. Historical frozen original **121/20/30/50**, all **26** operations, MC-B/MC-1 **NOT_ESTABLISHED**, `production_authorized=false` unchanged. No original-source closure, production, native, STEP, paid campaign or merge.