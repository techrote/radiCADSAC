# PB-007-01 v16 — exact Chebyshev/Sturm multiplier route

## Contract

This is a bounded constructive extension of `PB-007-01` after v15. It does not replace v15 source inversion. The admitted source family remains the exact rational finite odd-harmonic factorization

`F=M(alpha)*(A*cos(alpha)+B*sin(alpha))`

with source-derived normalized

`M(alpha)=lambda_0+sum_{k=1}^m lambda_k*cos(2*k*alpha)`, `m>=3`.

`PB-007-01` remains **OPEN** outside the admitted family.

## Route precedence

v15 exact strict dominance `|lambda_0|>sum_{k>=1}|lambda_k|` retains precedence. v16 is consulted only when v15 has already reconstructed and exactly rechecked the finite source factorization but strict dominance does not certify nonvanishing. Genuine common polynomial factors remain owned by v8. Carrier decision authority remains v10/v11/v12.

## Exact Chebyshev reduction

Using the identity `T_k(cos(beta))=cos(k*beta)` with `x=cos(2*alpha)`, v16 derives

`P(x)=lambda_0+sum_{k=1}^m lambda_k*T_k(x)`

entirely in exact rational polynomial arithmetic. Since real `alpha` maps `x` onto the complete closed interval `[-1,1]`, `M` is globally nonzero exactly when `P` is nonzero on that closed interval.

The certificate is valid only when all of the following hold:

- exact endpoint evaluation proves `P(-1)!=0` and `P(1)!=0`;
- MC-032 exact rational Sturm authority reports zero distinct roots in `(-1,1)`;
- exact rational evaluation establishes one constant sign;
- the lambda vector comes only from the v15 source-derived inversion.

An endpoint root, any open-interval root, malformed exact arithmetic, or bounded resource refusal fails closed. Resource refusal is not a truth value.

## Authority exclusions

Caller-supplied `lambda_vector`, `factorization`, Chebyshev coefficients/polynomials, Sturm certificates/counts, root-free flags, multiplier signs, and nonvanishing certificates are non-authoritative. Binary floating point, epsilon/tolerance, sampling, numeric trigonometry, approximate minimization, timeout, and resource exhaustion cannot establish correctness.

## Multiplicity and downstream semantics

A certified `P` is a smooth globally nonzero multiplier after composition with `cos(2*alpha)`. Therefore multiplication preserves the carrier zero set and every finite event-root multiplicity exactly. No new transcendental event oracle is introduced.

The frozen 26-operation denominator and source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. `PB-007-02` remains dependent on PB-007-01; `PB-007-03` remains OPEN; `PB-007-04` remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN; `MC-B` and `MC-1` remain `NOT_ESTABLISHED`.

## Residual repair path

The next dependency-ready PB-007-01 target is a source-derived finite even trigonometric multiplier with both cosine and sine even harmonics, using exact projective/tangent-half rationalization plus Sturm nonvanishing authority if source inversion and projective closure can be established without new numerical or transcendental authority.
