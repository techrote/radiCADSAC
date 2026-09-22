# PB-007-01 v8 — exact common-factor product subroute

Status: **bounded constructive route established; PB-007-01 remains OPEN**.  
Corrective issue: #178.  
Source baseline: `c61425cefba46deea9b9012ec833f80621d15163`.

## Purpose

PB-007-01 v7 reduced exact rational B-spline modulation to finite rational power-basis spans but left genuinely nonconstant polynomial modulation coupled to nonzero affine trigonometric phase unresolved. This v8 repair advances that exact residual boundary without changing the admitted 26-operation denominator or weakening any refusal semantics.

The new route recognizes the real sublanguage

`F(s) = g(s) * T(a + b*u(s))`

where every nonzero local harmonic modulation polynomial has the same nonconstant exact-rational polynomial GCD `g`, every exact quotient is constant, `T` is therefore a finite nonzero rational-coefficient trigonometric polynomial, and the phase law has rational offset and nonzero rational rate on the same source parameter.

## Exact construction

The factor is not supplied by the caller. The implementation computes the polynomial GCD using MC-032 exact rational arithmetic, divides every nonzero modulation channel by that GCD, requires exact zero remainder, and accepts v8 only if all quotients are degree zero. A constant GCD or any surviving nonconstant quotient falls back to the existing PB-007-01 blocker.

B-spline knot boundaries remain exact semantic boundaries. The source interval is additionally split wherever the affine phase reaches an exact quarter turn. Each resulting phase interval is at most a quarter turn wide. A cardinal quarter-turn chart shift is selected exactly so PB-007-01 v6 can use its tangent-half/Sturm route without treating a tangent-half pole as a physical singularity. No epsilon, sampling, floating-point sign, refinement cap, timeout or resource refusal becomes truth authority.

The polynomial factor uses MC-032 Sturm root counts and multiplicity. The constant trigonometric factor uses PB-007-01 v6 rational-turn endpoint isolation and Sturm root counts. Product endpoint multiplicities are added exactly.

## Exact coincidence rule

A product root can belong to both factors. Rational roots of `g` are enumerated exactly with the rational-root theorem and checked at their exact rational phase turns. Their factor and trigonometric multiplicities are added.

For the remaining roots, `g` has rational coefficients, so every non-rational root is algebraic irrational. Rational source-span maps preserve algebraicity, and a nonzero rational affine phase rate maps such a root to an algebraic-irrational turn. If a nonzero rational trigonometric polynomial vanished at that turn, `z = exp(2*pi*i*turn)` would satisfy a nonzero rational Laurent polynomial and hence be algebraic. The Gel'fond–Schneider theorem makes that same value transcendental as the principal value of `(-1)^(2*turn)`, a contradiction. The programme therefore excludes such coincidences only under these recorded preconditions.

Source for the theorem statement: Encyclopedia of Mathematics, *Gel'fond–Schneider method*, https://encyclopediaofmath.org/wiki/Gel%27fond%E2%80%93Schneider_method . The source states the classical result for algebraic base and irrational algebraic exponent; this repair uses only the narrow `-1` specialization described above.

This is not a general continuous-Skolem, Pfaffian, exponential-polynomial or arbitrary transcendental decision theorem.

## Boundary and adversarial controls

The deterministic verifier covers a simple common-factor root, a repeated common-factor root, rational factor/trigonometric coincidence with additive multiplicity, an algebraic-irrational factor root certified disjoint from the trigonometric factor, source-span endpoint roots, exact quarter-turn/pole-safe partitioning, constant-factor fallback, non-common polynomial modulation, zero phase rate, source-parameter mismatch, binary-float and epsilon authority, forged/caller-supplied factor fields, resource-refusal laundering, denominator shrinkage, historical v3/v6/v7 mutation and false MC-B promotion.

Historical v3, v6 and v7 artifacts/models/verifiers are byte-preserved and remain separate CI gates.

## Residual blocker

PB-007-01 **remains OPEN**. The v7 grammar still contains nonproportional nonconstant polynomial modulation such as independently varying harmonic channels. v8 does not establish an unconditional exact zero/multiplicity procedure for that family. PO-04, PO-05 and PO-08 therefore remain OPEN; PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; MC-B and MC-1 remain `NOT_ESTABLISHED`.

This result is a constructive subset, not an impossibility theorem for the residual family.

## Programme and semantic effect

No native, paid, production or expensive campaign is authorized or run. The frozen 26-operation denominator is unchanged. Historical source/audio/provenance, canonical-journal meaning, exact time/path/phase correlation, source uncertainty, positive-volume material semantics, holder/access semantics, durable body/lineage identity, refusal/`UNCERTIFIED` semantics and conventional STEP engineering-output requirements are preserved.
