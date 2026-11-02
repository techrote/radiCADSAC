# MC-038 / PB-007-01 — original V23 source: Bernstein positivity and a double boundary root

**Status:** source-specific deterministic-model research candidate, 2 November 2026.  
**Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100).  
**Exact initial base:** `45d4a10343ec8161e92e8bbed634f0edb5f16d24`.  
**Evidence class:** `DETERMINISTIC_MODEL`; no native geometry or capability acceptance.

## Purpose and falsifiable claim

The frozen V54 source
`harvested:verify_pb00701_v52:2250401ce435` has historical owner
`PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR` and refusal
`NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED`.

This work asks whether the **entire original closed source**, rather than a
sample or one subinterval, has exactly the exterior root `t=0`, with order two,
and is positive for every `0<t<=1`. A changed original source, failed exact
factor identity, nonpositive quotient, unsupported phase, extra root, wrong
endpoint derivative, or missing historical custody falsifies this claim.

The source-specific result is affirmative:

\[
F(t)\geq \frac{49}{34992}t^2\qquad(0\leq t\leq1),
\quad F(0)=F'(0)=0,\quad F''(0)=\frac1{36}>0.
\]

Consequently the complete closed-source zero set is `{0}`. There are zero open
roots and one exterior left-endpoint root of analytic order two. The physical
sign is positive on `(0,1]`. No sign outside the admitted source interval is
reported, and this exterior event is not presented as an interior crossing.

## Original source and independent lowering

The immutable source is in the
[frozen V54 corpus](https://github.com/techrote/radiCADSAC/blob/45d4a10343ec8161e92e8bbed634f0edb5f16d24/research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json).
Its canonical source-specification SHA-256 is
`4a3ee3f47b9347429c13830abef382301c7963b0af518f0977390c2d3ffba040`.
The original parameter is `v52-original-source`, on `[0,1]`; its affine phase
in turns is `1/4-t/24`.

Write `theta=pi/2-pi*t/12`. The exact original harmonics give

\[
F(t)=A_0(t)+A_1(t)\cos\theta+B_2(t)\sin(2\theta),
\qquad B_2=A_1/2.
\]

Each source amplitude is one fully clamped polynomial B-spline with no
interior knot. Degree `n` uses exactly `n+1` zero knots followed by `n+1` one
knots and `n+1` rational controls, so its basis is the degree-`n` Bernstein
basis on the **original** `t` coordinate. The checker validates that complete
knot and control structure directly. It does not borrow a route's summary,
translate a source coordinate, or rely on a floating-point spline evaluator.

| Channel | Degree | Original Bernstein controls, in order |
|---|---:|---|
| `A0` / cosine harmonic 0 | 7 | `0, 0, 1/1512, 1/756, 13/7560, 37/20412, 13/7776, 49/34992` |
| `A1` / cosine harmonic 1 | 6 | `0, 0, 1/54000, 1/27000, 23/486000, 7/145800, 49/1166400` |
| `B2` / sine harmonic 2 | 6 | `0, 0, 1/108000, 1/54000, 23/972000, 7/291600, 49/2332800` |

The implementation checks the complete original row identity, harvested
producer, canonical raw-source hash, original owner and refusal, in addition to
proving the mathematical inequalities. It rejects extra harmonics or omitted
residual terms.

## Exact positivity certificate

For `B_i^n(t)=binom(n,i)t^i(1-t)^(n-i)` and `i>=2`,

\[
B_i^n(t)=t^2\frac{n(n-1)}{i(i-1)}B_{i-2}^{n-2}(t).
\]

Because the first two controls of every amplitude are zero, each amplitude is
exactly `t^2` times a lower-degree Bernstein polynomial. The code constructs
these quotient controls and independently verifies the identity by a full
exact rational expansion into the power basis. The original `A0` quotient is

\[
(1/72,\ 1/108,\ 13/2160,\ 37/9720,\ 91/38880,\ 49/34992).
\]

Every coefficient is positive, with minimum `49/34992`. Bernstein basis
functions are nonnegative and sum to one on the closed unit interval, so
`A0(t)>=49*t^2/34992`, including `t=1`. Both remaining quotients have
nonnegative coefficients, giving `A1(t)>=0` and `B2(t)>=0`.

The exact source phase lies in `theta in [5*pi/12,pi/2]`. Therefore
`cos(theta)>=0`, and `2*theta in [5*pi/6,pi]` gives `sin(2*theta)>=0`.
All three terms of `F` are nonnegative; the `A0` term is strictly positive for
every `t>0`. This establishes the complete root-free interval `(0,1]` with a
rational quadratic lower bound. Sampling is not used to prove positivity or
root completeness.

## Exact endpoint order

For degree `n` Bernstein controls `(c0,c1,c2,...)`,
`A''(0)=n(n-1)(c2-2*c1+c0)`. Every amplitude has `A(0)=A'(0)=0`.
At the original left endpoint, `cos(theta(0))=cos(pi/2)=0` and
`sin(2*theta(0))=sin(pi)=0`.

Applying the product rule twice, each contribution from `A1*cos(theta)` or
`B2*sin(2*theta)` vanishes at `t=0`: its amplitude, first amplitude derivative,
or undifferentiated trig factor is zero in every term. Thus

\[
F''(0)=A_0''(0)=7\cdot6\cdot\frac1{1512}=\frac1{36}.
\]

This nonzero derivative proves order exactly two. The original source consists
of one analytic polynomial/trigonometric span, so this endpoint order is not
a fabricated global smooth order across a source knot.

## Reusable bounded checker and conservative refusals

`prove_sector_source` implements the conditional proof above for one clamped
source span `[0,1]` with exactly `C0`, `C1`, `S2`, degrees 2–12, phase turns
`1/4+r*t` for `-1/24<=r<=0`, and a `t^2` factor in each amplitude. Every `C0`
quotient coefficient must be strictly positive; all `C1`/`S2` quotient
coefficients must be nonnegative. Its generic proof does not require
`S2=C1/2`; that equality is separately checked as an original frozen-source
fact. A synthetic `F=t^2` control and intermediate/stationary phase controls
exercise the conditional checker without treating them as historical evidence.

These sufficient conditions are deliberately conservative. A negative
Bernstein coefficient or unsupported phase does **not** prove the physical
source is negative, has an extra root, or lies outside the machining domain.
It yields `SEMANTIC_BLOCKER`. Oversized degrees, rationals, JSON structures or
reports yield `RESOURCE_REFUSAL`; resource exhaustion is not a mathematical
verdict. Unsupported multiple spans, missing clamping, extra harmonics,
identity-zero sources and unproved endpoint orders are not admitted.

The arithmetic proof terminates over fixed finite arrays. Degrees, rational
bit lengths, JSON bytes, nesting and node counts are bounded before the
corresponding expensive operation. Rational tokens must use canonical ASCII
integer/ratio syntax with at most 78 digits per integer; exponent, decimal,
whitespace, Unicode-digit, unreduced and other noncanonical forms are rejected
before the Fraction constructor. Bounded integer parsing and the 256-bit check
also precede Fraction construction. All exact arithmetic uses Python's rational
integers/fractions. No numerical root finder, numerical trigonometry, interval
refinement campaign, native kernel or paid execution is required.

## Custody, falsification and reproduction

Direct immutable dependencies are checked before replay:

| Dependency | Git blob |
|---|---|
| Frozen original corpus | `5841c331579489b25caef38cd412bdbf286f9134` |
| Frozen 43-owner inventory | `8649c20ab77e199f9c3fa351b8b6742218f27abb` |
| Frozen V54 coverage report | `600ba29786f50397f29fd435fc5e2c57076088f9` |
| Post-V54 historical auditor | `12c6efeb667a954ffc5a7e27849ae815d466580a` |
| MC-002 26-operation domain | `23de82f5240a72509f7afe4acd5948b65bc4ff13` |
| Current no-production authority | `fa0233323a0804d8a5d3eb7cd892a274a6173fab` |

The 17 local adversarial test methods exercise source/phase/parameter/knot/
amplitude changes, historical-owner and refusal changes, actual missing
positivity or boundary-order premises, noncanonical/binary rationals, negative
controls, omitted/extra harmonics, altered quotient certificates, forged
root/sign/order reports, Python boolean/integer aliasing, duplicate JSON keys,
source/report resource bounds, and attempted gate/census promotion. A mocked
Fraction constructor proves that short exponent strings and other forbidden
tokens are rejected before allocation-prone parsing; the large exponent payload
is never evaluated by the real constructor. Independent
de Casteljau evaluations challenge the Bernstein transformation; they are
regression controls, not the complete inequality proof.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v23_bernstein_source.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
```

The machine-readable witness stores the original source, historical
observation, dependency pins, exact coefficient certificate, boundary
derivatives and complete physical event/sign description. Validation replays
the proof from the pinned original source; a caller-declared `PASS` is not
accepted. The witness does not pin itself or assert its eventual PR/CI/merge
identity.

## Programme implications and remaining work

This supplies one new source-specific complete mathematical witness for a
historical V23-refused source. It adds a small reusable sufficient-condition
proof, while leaving the V23 historical route and frozen V54 observations
unchanged. The original census remains **121 sources, 20 route refusals, and
30 missing-ordered-premise sources**. This report is not an exhaustive
post-V54 proof census; overlap and distinct-source coverage belong to the
separate source-bound reconciliation work.

For MSAC and OpenSimachinist, the practical implication is evidence that this
particular mathematical obstruction does not require numerical guesswork or
discarding an ordinary source. It establishes no native sweep, nominal
material/body/lineage topology, B-rep realization or usable conventional STEP
output. Those implementation and qualification obligations remain mandatory.

PB-007-01/02/03/04 and the wider proof obligations remain open; MC-B and MC-1
remain `NOT_ESTABLISHED`, and `production_authorized=false`. All 26 operations,
source/provenance/phase, canonical journal, material/body/lineage,
refusal/UNCERTIFIED and conventional-STEP semantics are retained.

Before landing, require final literal-head focused and `mc1-static` CI,
distinct technical source/mathematics review with accurate AI-assisted
attribution, expected-head-protected merge, identical reviewed/synthetic/
landed Git trees and independent merged-main focused/static checks. Local
success alone does not satisfy those integration gates. Subsequent work should
consume this source-specific witness in the reconciled evidence inventory and
select an actually uncovered source or interface obligation.
