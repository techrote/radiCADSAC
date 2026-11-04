# MC-038 / PB-007-01 — physical original-source knot continuity without channel continuity

**4 November 2026.** Evidence: `DETERMINISTIC_MODEL`. Scope: bounded exact
physical point/one-sided-jet composition, plus a specific mathematical
counterexample (C). **Not** a universal open-root/event solver or MC-B gate.

## Source authority and preregistration

- Parent: [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100);
  before-write preregistration [#6625710183](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6625710183);
  coordination [#324](https://github.com/techrote/radiCADSAC/issues/324).
- Source baseline: `main=93f80c56e29da00889662e0570476662cef70fd8`.
  Separate RCS-002 PR #367 was merged and the write reservation released.
- Frozen original V54 corpus Git blob:
  `5841c331579489b25caef38cd412bdbf286f9134`.
  Complete post-v54 original-source v2 registry Git blob:
  `e52d3baf3692a011cf86234eeaa992ef407d99fd`.
- Historical **anchor only**, already source-specifically solved by #307/#308:
  `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0`,
  original SHA-256 `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1`.
  This result does not re-solve that frozen source.

## The exact prospective original B-spline source

Grammar: `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`.
Original parameter `source-time-t` on `[0,2]`, exact affine phase in
**turns** `theta(t)=t/4`. Every channel is an original degree-zero
B-spline with knots `[0,1,2]` and right-continuous internal point
selection; the terminal source point is explicitly clamped.

| Channel | First source span | Second source span |
|---|---:|---:|
| H0 cosine | 0 | 1/2 |
| H1 cosine | 1 | 0 |
| H2 cosine | 0 | 1/2 |
| All sine | 0 | 0 |

Canonical JSON original-source SHA-256:
`f6f10c779a6837b61fb1276b664f45930958fe7dec80aa484d502592940ccd97`.
The verifier checks this digest and that it is *not* any of the 121 frozen
source specifications.

Original physical OPEN pieces, derived directly from these B-spline controls:

- `F_L(t)=cos(pi*t/2)` for `0<t<1`.
- `F_R(t)=(1+cos(pi*t))/2=cos^2(pi*t/2)` for `1<t<2`.

Both exact physical one-sided values at the true knot `t=1` equal **zero**,
although **all three Fourier channels have unequal left/right coefficients**.
At `t=1+u`, `F_L=-sin(pi*u/2)` and `F_R=sin^2(pi*u/2)`. Consequently:

- left one-sided first nonzero derivative order **1** (negative derivative,
  positive left-side germ);
- right one-sided order **2** (positive even-order leading coefficient and
  positive right-side germ);
- physical source continuity **holds** at the knot and the actual
  right-continuous selected knot point equals zero;
- both open source pieces are strictly positive and `F(0)=F(2)=1`,
  so the **complete original-source distinct zero set is exactly `{1}`**;
- no single global smooth root multiplicity is assigned.

This establishes a precisely bounded **negative C**: a proposed universal
source-composition rule that treats *Fourier-channel coefficient mismatch as
physical discontinuity*, or that requires coefficientwise continuity as a
**necessary** condition to certify every physically continuous join, fails on
this admissible exact source. Refusing this source is an incompleteness
counterexample; *asserting a physical jump from the mismatch is mathematically
incorrect*. It does **not** falsify a source-bound exact physical-value
comparison or the existence of a general analytic solver.

## Complete finite admitted knot-jet subtheorem

The model also implements a reusable conditional theorem for exact original
degree-zero two-span Fourier splines H0–H4, rational constant cosine/sine
amplitudes, exact phase turns `t/4`, and source knot `t=1`. Sine H0 is
rejected. This is a **knot-point** theorem, not an open-interval root solver.

For a single admitted constant-coefficient analytic source piece,

`F(t)=sum_h [C_h*cos(h*pi*t/2)+S_h*sin(h*pi*t/2)]`.

Its exact derivative normalized by the strictly positive factor
`(pi/2)^n` at `t=1` is the rational number

`J_n=sum_h h^n [C_h*cos((h+n)*pi/2)+S_h*sin((h+n)*pi/2)]`.

The sine and cosine values are exactly `0,+1,-1` by residue modulo four:
no binary float, transcendental numeric approximation, sample, tolerance,
subdivision count or time limit is used as a truth oracle.

If `k` distinct nonzero frequencies occur, with `e=1` when H0 is
nonzero (otherwise 0), the corresponding complex exponential expansion
contains `D=2k+e` distinct frequencies (including zero only for H0).
Its first `D` derivatives form an invertible Vandermonde system after
rescaling by powers of `pi/2`; if all `J_0..J_(D-1)` vanish, **the
analytic piece is identically zero**. Otherwise the first nonzero
`J_n` is the exact first nonzero derivative order `n<D`. Its sign is
the right germ's sign; the left germ's sign multiplies by `(-1)^n`.
An identity-zero piece has no invented isolated finite multiplicity.

Thus the bounded point decision **terminates in at most nine rational
derivative sums** for H0..H4. The returned certificate preserves separate
left/right analytic jet orders, exact physical point value, source/phase
identity, one-sided physical signs, continuity and actual knot policy.
Noncanonical rationals, unsupported harmonics/splines/phase, forged outputs
and resource overflow refuse as nontruth.

## Independent adversarial controls

- Exact point-value continuity despite all three channel jumps; one-sided
  orders 1/2 and positive source signs.
- A different H1 coefficient jump gives a genuine physical crossing at
  the same zero knot (order 1/1, opposite signs).
- A H0 step produces a genuine **physical discontinuity**, showing that
  the theorem does not indiscriminately declare joins continuous.
- An identity-zero left piece plus an isolated right germ retains the
  left continuum semantics and refuses to fabricate a left multiplicity.
- `cos^4(pi*t/2)` requires exact **order 4**, proving the finite
  Vandermonde limit is not hardcoded to simple/tangent order 2.
- A rational `eps=2^-120` added to the cosine produces `F(1)=eps>0`,
  not a knot root. A different **open** root exists in
  `(1,1+2^-118)`: at `u=2^-118`, the elementary strict sine-chord
  bound `sin(pi*u/2)>u>eps`, together with continuity and strict
  monotonicity, proves its existence and uniqueness. This is a
  mathematical inequality, not a numerical sign scan.
- Exact sine phase cases, total identity, wrong source parameter, knot,
  phase, noncanonical rational/float, caller evidence, resource budget,
  forged point/multiplicity/gate flags, and pinned frozen-source drift.

## Frozen-case before/after; exact limits

The same immutable 121-source v54 corpus and 50-case v2 registry are checked
by ID, source SHA-256, provenance, historical disposition and evidence class.
The saved JSON is machine-readable and verifies a **zero change**, not a new
historical admission.

| Category | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original sources | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | 0 |
| Complete supplemental original-source witnesses | 50 | 50 | 0 |
| Newly resolved historical IDs | 0 | 0 | 0 |

The **50/50** registered proofs remain **49 finite, one continuum**. This
prospective source is not one of them. No old raw failures or dispositions
are changed. The bounded theorem does not provide arbitrary open root
isolation, arbitrary phase/cosine sector choice, nonconstant B-spline
amplitudes, irrational-phase point decisions, global knot smoothness,
arbitrary-n source composition, category-3 universal sign transfer, or
complete PB-007-01/02/03/04 coverage.

**PB-007-01/02/03/04 remain OPEN; PO-02/04/05/07/08 remain OPEN;
MC-B/MC-1 NOT_ESTABLISHED.** All 26 operations, original source/provenance,
canonical operation journal, durable bodies/lineage, native material,
usable engineering STEP, topology and production/paid restrictions remain
unchanged. Evidence is `DETERMINISTIC_MODEL`, not a native or independent
STEP qualification.

## Reproduce and integrate

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_physical_knot_cyclotomic.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract --self-test
```

No complete PB theorem or capability gate is promoted by passing these
checks. Integration requires literal-head focused and static qualification,
direct source review, zero unresolved review threads, expected-head-protected
merge and actual merged-main independent CI. If CI or source review fails,
retain draft; preserve original errors.
