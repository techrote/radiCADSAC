# MC-038 / PB-007-01 — bounded transverse trigonometric interval proof

**Research candidate, 29 October 2026.** Evidence subtype: DETERMINISTIC_MODEL, not native geometry. Owner: [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). MC-1 is NOT_ESTABLISHED. This result is distinct from [PR #294](https://github.com/techrote/radiCADSAC/pull/294) fixed-source replay and [PR #295](https://github.com/techrote/radiCADSAC/pull/295) stationary-polynomial knot joins.

## Hypothesis and falsification

For an exact rational finite source F(s) = sum_h P_h(s) cos(2*pi*h*(a+b*s)) + Q_h(s) sin(2*pi*h*(a+b*s)), the checker can prove **every simple transverse open root** on a given source span WHEN an exhaustive finite rational partition closes. It is not a theorem of universal termination or completeness on arbitrary trigonometric functions. Tangencies, identity-zero spans, zero/undecidable endpoints or true source knots, insufficient interval precision, unsupported grammar and resource exhaustion fail closed; they are not evidence that the underlying source has no root.

The admitted verifier subset is rational affine turns, rational polynomial coefficients through degree three, at most eight harmonics with indices 0..8, rational source coordinates -4..4 and bounded exact resources (depth<=18, nodes<=20000). This is a checker subset only; it does NOT reduce the adopted 26-operation machining domain.

## Exact interval proof argument

Write R=max(1,abs(left),abs(right)), B(P)=sum_i abs(P_i)*R^i, and K_h=44*abs(h*b)/7 (using pi<22/7). Define rational global envelopes:

M1 = sum_h {B(P'_h)+B(Q'_h)+K_h*(B(P_h)+B(Q_h))}.

M2 = sum_h {B(P''_h)+B(Q''_h)+2*K_h*(B(P'_h)+B(Q'_h))+K_h^2*(B(P_h)+B(Q_h))}.

These upper-bound absolute F' and F'' on the entire source span by the triangle inequality, chain rule and abs(sin/cos)<=1. At the midpoint m of any rational cell of half-width r, enclose F everywhere by F(m)+[-M1*r,+M1*r], and F' everywhere by F'(m)+[-M2*r,+M2*r]. All endpoint and midpoint evaluations are outward rational enclosures: pi is bounded by Machin's identity pi=16 atan(1/5)-4 atan(1/239) and alternating-series next-term bounds. Rational turns are reduced exactly modulo 1; at |x|<=pi, rational Taylor polynomials of degrees 26 (cos) and 27 (sin) have Lagrange errors bounded by |x|^27/27! and |x|^28/28!, plus exact pi-argument uncertainty propagated by the global 1-Lipschitz sin/cos bound. No binary floating-point root sampling is used.

A dyadic leaf is accepted only when (A) its entire F enclosure has definite nonzero sign, proving NO_ROOT; or (B) its entire F' enclosure has definite nonzero sign and both endpoint F enclosures have strict signs. With B, equal endpoint signs prove NO_ROOT by strict monotonicity; opposite endpoint signs prove exactly ONE_SIMPLE_ROOT by IVT and nonzero derivative. Strict rational root brackets are refined inside the original monotone leaf and the full leaf retained as the completeness witness. Gaps, overlaps, inconsistent physical signs, and unclassified cells do not receive an accepted result. Refinement that encounters an uncertain rational cut refuses instead of inventing a coordinate.

## Actual original-source bindings

The bridge re-lowers every coefficient channel from frozen v54 121-case original B-spline source corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134. Only source/provenance/owner/phase checks are reused from original V27 source validator blob 006272b173a66bfb53cc4ddf0f5597857a42362b and V41 source validator blob 358dd4071ef968635bcd85f61dfa1965e51abda1. It does NOT reuse their root-count or root-order conclusions. Source lowering is pinned to 2a8079ee2cf012bc2a12794c4c5ff19ebd760007. The original MC-002 full 26-operation domain blob 23de82f5240a72509f7afe4acd5948b65bc4ff13 and current authority blob fa0233323a0804d8a5d3eb7cd892a274a6173fab are read-only pins.

Each original span is certified separately. Exact channel equality across true source knots is checked; strict nonzero one-sided endpoint signs are checked before physical event composition. Every implicit root carries the source-bound SHA-256, owner, source parameter, phase and strictly isolating rational bracket (never a fabricated rational root coordinate).

Expected deterministic cross-checks, NOT proof premises:

| Original frozen source | Complete simple open roots | Physical sign sequence | Frozen v54 disposition |
|---|---:|---|---|
| V27 tail0, two spans | 2 | positive/negative/positive | BLOCKED |
| V27 tail100, two spans | 2 | positive/negative/positive | BLOCKED |
| V41/V13 harvested, one span | 2 | negative/positive/negative | BLOCKED |

The root counts must instead emerge solely from the generic interval partition, not historical count-only child certificates. Reports include every rational leaf and its proof classification, and are rechecked by regeneration to reject forged or omitted roots, owner and phase substitution, altered sign cells, forged multiplicity, and false capability claims.

## Reproduction and negative controls

Run: python3 research/machining-completeness/tasks/MC-038/verify_pb00701_transverse_original_source.py --contract --self-test

Focused GitHub Actions CI runs this exact command alongside the separate mc1-static gate. Tests include a new synthetic source with a crossing at rational one-third, frozen V27/V41 original source re-lowering, independently strict trig controls, complete partition covers, source/phase/owner/status forgery, tangency, identity-zero, endpoint-zero, unsupported grammar and node-limit refusal. The latter cases produce RESOURCE_REFUSAL or BLOCKED with is_truth_value=false; no silently accepted root counts.

## Strict nonpromotion and next work

A successful result is a bounded source-specific mathematical classification for the admitted *transverse* subset, not general trigonometric nested-child completion, arbitrary implicit/algebraic root comparison, shared-knot zero/parity transfer, historical V43/v54 certification, PB-007-01 global acceptance or MC-B/MC-1 acceptance. All 121 frozen dispositions and issue #275 remain unchanged; issue #100 remains OPEN; production_authorized=false. No native material/topology, B-rep, engineering STEP consumer or production authority has been established.

The supported 26 lathe/mill operations, source/provenance/phase, canonical manufacturing journal, material/body/lineage, typed refusal and UNCERTIFIED semantics, and conventional usable engineering STEP obligations remain intact. The next justified research is source-bound tangency/zero-knot multiplicity and exact comparisons between separately proven implicit roots; no speculative successor issue or paid/native campaign is authorized.
