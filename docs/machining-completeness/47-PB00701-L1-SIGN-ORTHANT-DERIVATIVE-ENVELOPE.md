# PB-007-01 v21 — exact finite sign-orthant L1 derivative envelope

## Contract

This bounded extension follows PB-007-01 v20 and preserves all v8–v20 authority. Historical classification runs first. v21 is considered only for an exact local residual span for which v20 returns `POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED` while the harmonic-0 anchor derivative has one exact strict sign.

The admitted residual form remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational polynomial source channels, `P=C_0` nonconstant, exact-rational affine `phi(s)=a+r*s` with `r != 0`, and at least two active positive harmonics. No source factor, harmonic, phase relation, source/audio/provenance identity, or operation is discarded.

## L1 envelope

v21 reuses the exact v20 source-derived envelope terms `C'_h(s)`, `S'_h(s)`, `(44/7)|h*r|C_h(s)`, and `(44/7)|h*r|S_h(s)`. The theorem `pi < 22/7` supplies the rigorous phase-term bound. Only exact-zero envelope polynomials may be omitted.

For nonzero terms `f_1,...,f_N`,

`|F'(s)-P'(s)| <= sum_i |f_i(s)|`.

Instead of v20's conservative Cauchy–Schwarz upper bound, v21 uses the exact finite identity

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

After proving the strict sign of `P'`, v21 constructs every directed rational-polynomial margin. For a positive anchor derivative,

`M_sigma(s)=P'(s)-sum_i sigma_i f_i(s)`;

for a negative anchor derivative the directed anchor is `-P'`. Every one of the `2^N` margins must be strictly positive on closed `[0,1]`.

## Exact authority and sign-cell interpretation

Each margin is decided using existing MC-032 exact rational polynomial authority: exact endpoint relations plus exact Sturm distinct-root counting on the open interval. Endpoint equality, an interior zero, or an incorrect endpoint sign fails closed.

This finite sign-orthant construction exactly covers every possible sign cell of the envelope polynomials. It therefore proves the same strict L1 condition that an explicit algebraic-root sign-cell partition would prove, while eliminating any need to isolate, approximate, or order algebraic sign-change roots. Rational, algebraic-irrational, repeated, or coincident sign changes do not change the authority: all possible sign orthants are already covered.

Caller-supplied L1, sign-cell, orthant, margin, Sturm, sign, or root certificates are never authority.

## Termination

For finite `N`, v21 forms exactly `2^N` finite rational-polynomial margins and performs one exact closed-interval strict-positivity decision for each, plus the fixed-sign anchor decision. There is no recursive subdivision and no approximation convergence criterion. Timeout and resource exhaustion are non-truth refusal outcomes, not correctness boundaries.

## Endpoint and multiplicity semantics

After monotonicity is certified, v21 reuses v19/v20 endpoint and root semantics unchanged. Exact rational-turn values are decided through the established v6 algebraic tangent-half authority. A tangent-half coordinate pole is handled by exact half-turn shifting and `(-1)^h` parity.

Exact endpoint signs plus strict monotonicity yield zero or one open root and exact endpoint-root decisions. Because strict L1 dominance proves the complete derivative nonzero on the closed source span, every admitted root has multiplicity one.

## Adversarial boundary

The acceptance construction is blocked by v19 and v20 but passes v21. Tests cover both derivative directions, zero/open/endpoint roots, exact L1 equality and signed `±1/1000000` rational neighbours, rational/algebraic-irrational/repeated envelope sign changes, anchor-derivative zeros/sign changes, source-parameter mismatch, binary-float authority, forged proof metadata, resource refusal, v20 precedence, historical-v20 drift, denominator shrinkage, and false MC-B promotion.

## Programme state

PB-007-01 **remains OPEN** outside the admitted L1-envelope family. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator and all protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive campaign is authorized by this result.
