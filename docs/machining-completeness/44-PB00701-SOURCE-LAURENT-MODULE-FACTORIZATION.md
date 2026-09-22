# PB-007-01 v18 — exact source/Laurent module factorization

## Contract

This bounded repair follows PB-007-01 v17 and preserves all v8–v17 authority. It operates only on exact local polynomial source maps produced by the existing B-spline lowering and only after the historical classifier still reports the PB-007-01 residual coupled-theorem blocker.

v18 may remove a factor only when all of the following are source-derived and exact:

1. the factor divides the original source in the stated module;
2. multiplication of factor and quotient exactly regenerates the original source;
3. the factor is proved globally nonzero on its entire relevant domain; and
4. the exact quotient source is accepted by an already-established v8–v17 event route.

Caller factorization, root-count, sign, nonvanishing, residual, Sturm or projective metadata is non-authoritative.

## Exact common source-polynomial factor

For one local source span, v18 computes the maximal monic rational-polynomial gcd `g(s)` across every nonzero cosine and sine coefficient polynomial. Unlike v8, the quotient channels need not be constant.

The factor can be removed only if it is nowhere zero on the closed source interval `s in [0,1]`:

- `g(0)` and `g(1)` are checked exactly and must be nonzero;
- MC-032 exact rational Sturm authority must report zero distinct roots in `(0,1)`; and
- the exact endpoint signs must agree.

Every channel is then divided exactly, every remainder must be zero, and `g*quotient` must exactly regenerate the original coefficient polynomial. A rooted source gcd is not discarded: it remains a PB-007-01 blocker because removing it would destroy event zeros or multiplicity.

## Exact Laurent/source-module factor

For finite positive odd-harmonic source channels relative to base harmonic `h`, write

`q_r(s)=C_(2r+1)(s)-i*S_(2r+1)(s)`.

For highest odd-harmonic radius `R`, multiply the real Laurent source by the known monomial shift and collect each source-power coefficient as the Gaussian-rational polynomial

`H_l(w)=sum_r conj(q_r,l)*w^(R-r) + q_r,l*w^(R+r+1)`, with `w=z^(2h)`.

A source-independent even-trigonometric phase factor must divide every nonzero `H_l`. v18 therefore computes their exact monic gcd over `Q(i)[w]`. A factor is admissible only if:

- at least two nonzero source-parameter slices exist, avoiding single-slice phase-factor ambiguity;
- the common gcd has nonzero even degree;
- an exact Gaussian-rational scale normalizes it to conjugate-reciprocal form;
- the center coefficient is real, producing a real finite even-trigonometric multiplier; and
- the preserved v17 tangent-projective/Sturm certificate proves that multiplier has no zero on the complete real projective phase line, including infinity.

Every Laurent slice is exactly divided and regenerated. The quotient slices must themselves have the exact conjugate-reciprocal odd-source structure. Their positive-frequency coefficients reconstruct the residual real cosine/sine source maps exactly.

Odd-degree, non-conjugate-reciprocal, projectively rooted, structurally ambiguous, non-dividing or non-regenerating candidate factors fail closed.

## Residual delegation and multiplicity

The residual source is represented exactly as clamped rational B-spline spans and passed through the preserved v17 classifier. This is recursive delegation to existing authority, not a new residual zero algorithm. A residual outside v8–v17 authority remains blocked.

If a removed source or phase factor is proved smooth and globally nonzero, multiplication by that factor cannot create or remove a source-event zero and preserves every finite residual root multiplicity. This is the only multiplicity inheritance used by v18.

## Adversarial boundary

The v18 verifier requires a genuine new source-factor case that v17 blocks and v18 certifies, exact endpoint/interior/algebraic source-root rejection, exact `±1/1000000` source-root boundary neighbours, genuine multi-harmonic Laurent extraction, exact source regeneration, malformed Laurent rejection, projective-root rejection, one-coefficient perturbation rejection, historical precedence, source-parameter binding, caller-metadata forgery resistance, binary-float rejection and resource-refusal non-laundering.

Historical v17 evidence is immutable and verified by Git blob identity. The frozen 26-operation denominator remains unchanged.

## Programme state

**PB-007-01 remains OPEN.** v18 is not a universal decision procedure for the required coupled analytic grammar and is not an impossibility theorem for the residual grammar. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain binding. No native, paid, production or expensive execution is authorized by this repair.
