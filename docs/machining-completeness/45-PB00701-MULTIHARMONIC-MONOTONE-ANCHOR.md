# PB-007-01 v19 — exact multi-harmonic monotone-anchor derivative dominance

## Contract

This bounded repair follows PB-007-01 v18 and preserves all v8–v18 authority. Historical classification runs first. v19 is considered only for an exact local polynomial span that still carries the PB-007-01 residual coupled-theorem blocker.

The admitted residual form is

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

where `s in [0,1]`, `P=C_0` is a nonconstant exact rational polynomial, every `C_h,S_h` is an exact rational polynomial, `phi(s)=a+r*s` has exact rational `r != 0`, and at least two positive harmonics are active. This is a direct source-event decision route; no source or phase factor is removed.

## Exact Bernstein derivative bound

For a power polynomial `p(s)=sum_j a_j s^j` of degree `n`, v19 derives the exact Bernstein coefficients

`b_k=sum_{j=0}^k a_j * binom(k,j)/binom(n,j)`.

On `[0,1]`, the Bernstein convex-hull property gives

`min_k b_k <= p(s) <= max_k b_k`.

Thus `max_k |b_k|` is a rigorous rational absolute bound. v19 applies this to every modulation polynomial and derivative and to `P'`.

For each positive harmonic,

`d/ds [C_h cos(2*pi*h*phi)+S_h sin(2*pi*h*phi)]`

has magnitude at most

`||C'_h|| + ||S'_h|| + 2*pi*|h*r| (||C_h|| + ||S_h||)`.

Using only the proved rational theorem `pi < 22/7`, v19 replaces the phase term by the exact rational upper bound

`(44/7)|h*r| (||C_h|| + ||S_h||)`.

Let the sum over positive harmonics be `B`. Strict monotonicity is certified only if

`min_Bernstein(P') > B`

or

`max_Bernstein(P') < -B`.

The exact positive difference is recorded as the derivative margin. Equality and all weaker cases remain PB-007-01 blockers. Numerical pi, floating point, epsilon, sampling, approximate minimization, timeout and resource limits are not predicate authority.

## Exact endpoint classification

At `s=0` and `s=1`, every source polynomial is evaluated exactly, leaving a constant-coefficient rational trigonometric polynomial at an exact rational turn. Preserved v6 tangent-half/Sturm authority decides its exact sign or equality.

The tangent-half coordinate has a pole at rational turns `k+1/2`. This is a coordinate pole, not an event singularity. At such an endpoint v19 applies the exact identity

`turn -> turn - 1/2`,

and multiplies every harmonic coefficient by `(-1)^h`. The original trigonometric value is unchanged and the shifted tangent-half coordinate is finite. No epsilon displacement is permitted.

## Root count and multiplicity

Once the source derivative is proved strictly positive or strictly negative on the complete closed span, the event is strictly monotone. Exact endpoint relations therefore determine the complete root structure:

- opposite nonzero endpoint signs imply exactly one open root;
- equal nonzero signs imply no root;
- one exact endpoint equality implies exactly one endpoint root and no additional root.

Two endpoint zeros are incompatible with the strict derivative certificate. Every admitted root is simple because the derivative is bounded away from zero by an exact positive rational margin on the complete closed span.

## Authority and precedence

v8–v18 retain ownership of every source they already certify. v19 consumes only residual blocked spans. Caller derivative, Bernstein, monotonicity, endpoint-sign, root-count, pi-bound or margin metadata is discarded before source analysis and cannot become truth authority.

Resource refusal remains a non-truth status. The route does not narrow the admitted source grammar and does not promote an unresolved residual to success.

## Adversarial boundary

The verifier requires a genuine two-positive-harmonic source that v18 blocks and v19 certifies, positive and negative monotonicity, no-root and one-open-root decisions, both endpoint-root cases, an exact half-turn endpoint, nonconstant positive-harmonic modulation, exact derivative-dominance equality and signed `±1/1000000` neighbours, structural rejection without a qualified anchor/two-harmonic residual, historical precedence, source binding, metadata-forgery resistance, binary-float rejection and resource-refusal non-laundering.

Historical v18 evidence is immutable and checked by Git blob identity. The frozen 26-operation denominator remains unchanged.

## Programme state

**PB-007-01 remains OPEN.** v19 is not a universal decision procedure for the full required coupled analytic grammar. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain binding. No native, paid, production or expensive execution is authorized by this repair.
