# PB-007-01 v19 — exact residual multi-harmonic monotone-anchor route

Issue: #200  
Parent integration gate: MC-038 / #100  
Source baseline: `4e337136731a423fbdf3aa6fd1952f372de5601a`  
Disposition: **bounded direct multi-harmonic decision route added; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Result

v19 attacks the residual coupled multi-harmonic decision boundary recorded after v18 rather than adding another factor-removal special case. Preserved v18 authority runs first. Only an exact local polynomial span that remains blocked is eligible for v19.

The new route admits a source of the form

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

where `P=C_0` is a nonconstant exact rational polynomial, `phi(s)=a+r*s` has nonzero exact-rational rate, and at least two positive harmonics are active. It proves a fixed source-derivative sign over the complete closed local span and then combines that with exact endpoint relations to count roots and prove multiplicity.

## Exact derivative certificate

Every exact rational power-basis polynomial and its derivative is converted to exact Bernstein coefficients on `[0,1]`. The Bernstein convex-hull property gives exact rational lower/upper bounds and exact rational absolute bounds without sampling.

For each positive harmonic, v19 bounds

`|d(C_h cos(2*pi*h*phi)+S_h sin(2*pi*h*phi))/ds|`

by

`||C'_h|| + ||S'_h|| + (44/7)|h*r| (||C_h|| + ||S_h||)`.

The only transcendental inequality used is the proved rational theorem `pi < 22/7`; no numerical value of pi is correctness authority. Summing those bounds gives `B`. The route accepts only when `min_Bernstein(P') > B` or `max_Bernstein(P') < -B`. Equality is deliberately rejected. The difference is stored as an exact positive rational strict margin, so the complete event function is respectively strictly increasing or strictly decreasing and its source derivative never vanishes.

## Exact endpoint and multiplicity authority

Both endpoint values are classified through preserved v6 rational-turn algebraic tangent-half authority. If an endpoint phase is exactly a tangent-half pole `turn=k+1/2`, v19 performs the exact identity-preserving shift `turn -> turn-1/2` and multiplies every harmonic coefficient by `(-1)^h`; no epsilon displacement is used.

Strict monotonicity plus exact endpoint signs gives zero or one open root. An exact left or right endpoint equality is also decided without approximation. Because the derivative has a strict nonzero lower magnitude bound throughout the closed source span, every accepted open or endpoint root is exactly simple.

## New constructive coverage

The deterministic acceptance fixture contains a nonconstant harmonic-0 polynomial anchor and two genuinely active positive harmonics. v18 remains blocked because no qualified nonvanishing source/Laurent factor reduces it to historical carrier authority. v19 instead certifies the original residual source directly from the derivative bound and endpoint relations.

The suite also exercises decreasing monotonicity, no-root spans, both endpoint-root orientations, a half-turn endpoint, nonconstant positive-harmonic modulation, and the exact derivative-dominance threshold with signed `±1/1000000` neighbours.

## Adversarial boundary

Missing/constant anchors, only one positive harmonic, equality or insufficient derivative dominance, source-parameter mismatch, binary-float source authority, forged derivative/Bernstein/endpoint/root metadata, resource-refusal laundering, historical-v18 mutation, frozen-denominator shrinkage and false MC-B promotion all fail closed. Existing v8–v18 decisions retain precedence.

Neither binary floating point, epsilon, sampling, numerical trigonometry, approximate minimization, timeout nor resource exhaustion is a truth source. Resource refusal remains a non-truth terminal status.

## Programme effect

**PB-007-01 remains OPEN.** v19 does not establish a universal zero/multiplicity procedure for residual coupled exponential-polynomial predicates. Multi-harmonic cases without a certified monotone anchor, or whose derivative bound is insufficient, remain explicit blockers.

PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. No MC-B retry is justified solely by v19.

The frozen 26-operation denominator is unchanged. Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain binding.

## Next repair boundary

The remaining PB-007-01 frontier is the irreducible coupled multi-harmonic branch beyond both exact v18 factor removal and v19 global monotone-anchor derivative dominance. Further work should seek another genuinely broader exact terminating decision construction—rather than another thin coefficient pattern—or record the precise theorem boundary if no unconditional construction is available. Sampling, tolerance, timeout and domain narrowing remain forbidden substitutes.
