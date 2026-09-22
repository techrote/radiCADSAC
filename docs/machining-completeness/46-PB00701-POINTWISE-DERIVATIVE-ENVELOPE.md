# PB-007-01 v20 — exact pointwise polynomial derivative envelope

## Contract

This bounded extension follows PB-007-01 v19 and preserves all v8–v19 authority. Historical classification runs first. v20 is considered only for an exact local residual span for which v19 returns `MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED`.

The admitted residual form remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational polynomial source channels, `P=C_0` nonconstant, exact-rational affine `phi(s)=a+r*s` with `r != 0`, and at least two active positive harmonics. No source factor, harmonic, phase relation, source/audio/provenance identity, or operation is discarded.

## Pointwise polynomial envelope

For each active positive harmonic v20 derives, exclusively from the exact source,

- `C'_h(s)`;
- `S'_h(s)`;
- `(44/7)|h*r| C_h(s)`;
- `(44/7)|h*r| S_h(s)`.

The proved theorem `pi < 22/7` makes those phase terms rigorous upper envelopes for the corresponding `2*pi` derivative terms. Exact-zero envelope polynomials may be omitted; no approximate pruning is permitted.

Let the remaining polynomials be `f_1,...,f_N`. Pointwise,

`|F'(s)-P'(s)| <= sum_i |f_i(s)|`.

Cauchy–Schwarz yields

`sum_i |f_i(s)| <= sqrt(N * sum_i f_i(s)^2)`.

Define the exact rational polynomial

`Q(s)=P'(s)^2-N*sum_i f_i(s)^2`.

v20 certifies monotonicity only when:

1. `P'` has one strict sign on the complete closed interval `[0,1]`; and
2. `Q>0` on the complete closed interval `[0,1]`.

Both claims use existing MC-032 exact rational Sturm authority: exact endpoint events and exact distinct-root counts on the open interval. Endpoint equality, an interior root, or a sign mismatch fails closed. Caller-supplied envelope, Q, Sturm, sign, or root metadata is never authority.

Under these conditions,

`sum_i |f_i(s)| < |P'(s)|`

for every `s`, so the complete event derivative has exactly the sign of `P'` and cannot vanish.

## Termination

The certificate is finite by construction: form a finite family of exact rational polynomials, form one exact sum-of-squares polynomial and `Q`, then make two exact closed-interval polynomial sign decisions. There is no recursive source subdivision and therefore no arbitrary subdivision cap that could become a correctness boundary. Timeout and resource refusal remain non-truth outcomes.

## Endpoint and multiplicity semantics

After monotonicity is certified, v20 reuses v19 endpoint and root semantics unchanged. Exact rational-turn values are decided through the v6 algebraic tangent-half authority. If an endpoint is at a tangent-half coordinate pole, the phase is shifted exactly by half a turn and each harmonic coefficient receives the exact `(-1)^h` parity factor.

Exact endpoint signs plus strict monotonicity yield zero or one open root and exact endpoint-root decisions. Because the complete derivative is strictly nonzero on the closed span, every admitted root has multiplicity one.

## Adversarial boundary

The acceptance construction includes a source whose several oscillatory derivative terms attain their global maxima at different source locations. v19's sum of separate whole-span suprema is therefore too conservative, while v20's exact pointwise sum-of-squares envelope proves strict monotonicity.

Tests cover both derivative directions, zero/open/endpoint roots, exact `Q=0` equality and signed `±1/1000000` rational neighbours, anchor-derivative zeros/sign changes, failing Q certificates, source-parameter mismatch, binary-float authority, forged proof metadata, resource refusal, v19 precedence, historical-v19 drift, denominator shrinkage and false MC-B promotion.

## Programme state

PB-007-01 **remains OPEN** outside the admitted pointwise-envelope family. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator and all protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production or expensive campaign is authorized by this result.
