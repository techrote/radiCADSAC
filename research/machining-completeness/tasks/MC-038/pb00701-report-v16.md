# PB-007-01 v16 — exact Chebyshev/Sturm multiplier nonvanishing

Issue: #194  
Parent integration gate: MC-038 / #100  
Source baseline: `e9f0d464581939b4de0c0dc766553c8672aecdf8`  
Disposition: **bounded exact multi-harmonic family broadened; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Decision

**RAG: AMBER.** v15 already derives an arbitrary finite normalized even-cosine multiplier from the unfactored source harmonic maps, but its nonvanishing proof was the conservative exact condition `|lambda_0|>sum_{k>=1}|lambda_k|`. v16 keeps that source inversion unchanged and extends only the proof of nonvanishing.

For

`M(alpha)=lambda_0+sum_{k=1}^m lambda_k*cos(2*k*alpha)`,

v16 constructs the exact rational Chebyshev polynomial

`P(x)=lambda_0+sum_{k=1}^m lambda_k*T_k(x)`, `x=cos(2*alpha) in [-1,1]`.

It rejects exact roots at `x=-1` or `x=1`, then uses the existing MC-032 rational Sturm machinery to require zero distinct roots in `(-1,1)`. An exact rational midpoint evaluation establishes the constant sign. This proves global nonvanishing without numerical trigonometry, approximate minimization, epsilon, sampling, or a new transcendental oracle.

v15 retains precedence whenever strict L1 dominance already certifies the multiplier. v16 operates only on source-derived v15 factorization candidates that failed that sufficient test. Caller-supplied lambda vectors, factorization metadata, Chebyshev polynomials, Sturm counts, signs, and root-free assertions are non-authoritative and discarded.

## Constructive advance

The adversarial positive witness uses normalized Chebyshev coefficients `[160,-200,50,1]`. Its L1 margin is negative, so v15 cannot certify it, yet the exact Sturm count on `[-1,1]` is zero and the exact sign is positive. The corresponding negative witness `[-160,200,-50,1]` is likewise non-L1 and exactly negative throughout the interval.

The boundary suite rejects an exact endpoint root, a simple interior root, a repeated interior root, and two algebraic-irrational interior roots. The repeated-root case is handled through MC-032 square-free/Sturm authority rather than numerical root multiplicity heuristics. A factored cubic boundary gives exact `+1/1000000` and `-1/1000000` neighbours around an endpoint-root transition.

Once the multiplier is certified globally nonzero, the original multi-harmonic event has exactly the carrier's zero set and every finite event-root multiplicity is preserved. Carrier authority remains delegated to the established v10/v11/v12 routes; a nonconstant carrier gcd remains owned by v8.

## Protected boundaries

This repair does not narrow the frozen 26-operation denominator and does not alter source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, or conventional STEP semantics. Resource exhaustion remains `RESOURCE_REFUSAL`, never evidence of nonvanishing.

`PB-007-01` remains **OPEN** for multi-harmonic coupled predicates outside the exact source-derived finite even-cosine-multiplier times qualified-carrier family, and for carrier cells outside v10/v11/v12. `PB-007-02` remains dependent on PB-007-01; `PB-007-03` remains OPEN; `PB-007-04` remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN; `MC-B` and `MC-1` remain `NOT_ESTABLISHED`.

## Next repair path

The next material PB-007-01 broadening should target a source-derived finite **even trigonometric** multiplier

`lambda_0 + sum_k (c_k*cos(2*k*alpha) + s_k*sin(2*k*alpha))`.

A plausible exact route is tangent-half/projective rationalization: multiply by the known-positive denominator to obtain an exact rational polynomial on the real projective line, prove nonvanishing/sign with exact Sturm authority including the projective point at infinity, and derive all multiplier coefficients from source harmonic maps rather than caller assertions. If source inversion is underdetermined or the projective closure cannot be made exact under current authority, that is a genuine blocker to record rather than weakening PB-007-01 or retrying MC-B.
