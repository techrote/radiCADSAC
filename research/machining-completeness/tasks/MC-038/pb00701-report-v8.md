# PB-007-01 v8 — exact common-factor reduction

## RAG status

**AMBER — bounded constructive extension established; PB-007-01 remains OPEN.** Corrective issue #178 extends the existing v7 exact B-spline lowering without rewriting any v3/v6/v7 evidence. The frozen 26-operation denominator and all protected source/audio/provenance semantics remain unchanged. MC-B and MC-1 remain `NOT_ESTABLISHED`.

## Exact route established

On each exact v7 knot span, the v8 model examines the already-lowered rational power-basis modulation polynomials. It computes their common divisor by exact rational polynomial GCD, normalises it, and divides every nonzero harmonic channel exactly. The v8 route is admitted only when the common factor `g(s)` is genuinely nonconstant, every remainder is exactly zero, and every quotient has exact degree zero. No caller-supplied factor or quotient is accepted as authority.

The admitted predicate therefore has the proved form

`F(s) = g(s) * T(theta(s))`,

where `T` is a nonzero constant-coefficient rational trigonometric polynomial and `theta(s)` is the same shared exact-rational affine phase law inherited from v7. Factor roots and multiplicities use the existing MC-032 exact rational-polynomial Sturm/event machinery.

## Exact pole-safe trigonometric charts

The implementation partitions the local source interval at exact rational source points where the affine phase reaches half-turn chart boundaries. This includes every tangent-half pole. Each resulting chart is shifted by an exact quarter turn so its transformed phase interval is finite in the v6 tangent-half coordinate. The transformed rational sine/cosine coefficients are obtained by exact cardinal identities and the chart is delegated to PB-007-01 v6. Internal chart-boundary events are evaluated exactly and counted once; epsilon, finite sampling and floating-point sign tests are not used.

## Coincidence theorem boundary

Every rational root of `g(s)` is enumerated and checked directly against the trigonometric factor with exact rational-turn endpoint authority. If both factors vanish, product multiplicity is the exact sum of their multiplicities.

For an algebraic-irrational root `s` of a rational polynomial, with rational phase offset, nonzero rational phase rate and a nonzero rational trigonometric polynomial, a trigonometric coincidence is excluded by the Gelfond-Schneider theorem: a trigonometric zero would make `exp(2*pi*i*(a+b*s))` algebraic, while `b*s` is algebraic irrational and the corresponding exponential is transcendental. This argument is recorded only for this commensurate rational-coefficient grammar. It is not generalized to irrational phase coefficients, unrelated transcendental grammars, or an impossibility result.

## Adversarial and boundary coverage

The deterministic verifier exercises simple and repeated common-factor roots; exact rational factor/trigonometric coincidence with multiplicities adding; an algebraic-irrational factor root under the theorem preconditions; source-span endpoint coincidence; exact phase-pole partitioning; constant-factor fallback to prior authority; non-common modulation remaining blocked; zero trigonometric identity; zero phase rate; source-parameter mismatch; binary-float and epsilon rejection; forged factor/quotient fields; resource-refusal non-truth; historical-evidence immutability; frozen-denominator preservation; and false MC-B promotion.

## Residual blocker

PB-007-01 remains OPEN. The admitted v7 grammar still contains genuinely non-common nonconstant rational polynomial harmonic modulation coupled to nonzero rational affine phase. Such a predicate does not in general factor into one polynomial times one constant-coefficient trigonometric polynomial, and this repair does not establish a terminating exact zero/multiplicity procedure for every such remaining case. This is not an impossibility theorem.

Accordingly PO-04, PO-05 and PO-08 remain OPEN; PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; MC-B and MC-1 remain `NOT_ESTABLISHED`. No native, paid, production or expensive campaign was run or authorized.

## Protected semantics

The source/audio/provenance record, canonical-journal meaning, exact time/path/phase correlation, source-uncertainty accounting, positive-volume material semantics, cutter/holder access, durable body/lineage identity, refusal/`UNCERTIFIED` semantics and conventional STEP semantics are preserved. Binary floating point, epsilon, finite sampling, timeout and resource refusal remain forbidden as correctness authority.

## Verification

The repository gate must compile the v8 model/verifier and run both `verify_pb00701_v8.py --contract` and `verify_pb00701_v8.py --self-test`, while retaining all historical PB-007-01 v3/v6/v7 checks. Exact-head `mc1-static` must pass before merge and an independent post-merge `mc1-static` must pass on the exact merged `main` SHA before issue #178 may close.
