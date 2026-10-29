# MC-038 / PB-007-01 — V6 constant-modulation source-ordered root research

**Status:** 28 October 2026. **Evidence class:** deterministic exact-arithmetic research candidate. **Parent:** [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100). **Base main:** `8198ab3c97c3df2809c14366e164ec5ed52e1b10`.

This is a bounded candidate for one existing v54 category-3 premise. It does not alter historical V6–V54 routes or frozen evidence and does not establish PB-007-01, MC-B/MC-1, native geometry, B-rep or STEP capability.

## Targeted missing premise

The v54 inventory records `DELEGATED_V6_CONSTANT_MODULATION` as:

`TAN_HALF_TURN_WINDOW_ROOT_COUNTS_WITHOUT_SOURCE_ORDERED_ROOTS_OR_SIGN_CELLS`.

The pinned v54 corpus contains **22** cases mentioning this owner. **18 cases / 18 V6 owner spans** are frozen specifically as `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE`.

Historical V6 already supplies, for a certified pole-free rational turn window:

- an exact rational tan-half numerator `P(x)`;
- a strictly positive real denominator `(1+x^2)^n`;
- exact rational/algebraic tan-half endpoint descriptors;
- exact endpoint event/multiplicity queries;
- exact Sturm distinct-root counts between algebraic endpoints.

The missing interface is physical ordering in the original source parameter.

## Source-order construction

For `x = tan(pi*t)`, a V6-certified window contains no tangent pole. Therefore `x(t)` is a strict analytic diffeomorphism on that window, with nonzero derivative. Consequently:

- zero order in tan-half coordinate is exactly zero order in turn coordinate;
- multiplicity is unchanged by the coordinate substitution;
- sign is unchanged because the removed denominator is strictly positive;
- crossing/tangency parity is unchanged.

For a V7 constant-modulation span, phase is the exact affine map

`t(u) = offset + rate*u`, with rational `offset`, nonzero rational `rate`, and rational source span endpoints.

The first prototype attempted to bisect directly in source coordinate. That is exact but unsuitable: each finer rational source turn can increase the degree of the exact tangent-endpoint polynomial, so endpoint construction cost grows with the bisection denominator. The preserved first CI attempt is therefore treated as a negative implementation result, not as a route to optimize around.

The corrected candidate isolates roots in V6's **tan-half coordinate using rational x-bisection**, where the numerator polynomial degree is fixed. The tan-half chart remains internal. Because the certified phase window is pole-free and the affine phase slope is nonzero, each exact tan-half root has one and only one source preimage, and tan-half order transfers to source order (reversed when phase rate is negative).

A non-rational source root is represented by a unique exact tan-half **bracket** whose endpoints may include the certified algebraic V6 window endpoint plus an internal rational cut, together with the original source span and affine phase map. The bracket need not be shrunk away from the window endpoint: completeness comes from exact root rank and the full ordered root set. No algebraic polynomial, rational isolating interval, or transcendental closed form for the source coordinate itself is claimed. Source sign cells are bounded symbolically by the exact source-ordered root sequence and receive their signs from exact one-sided root/endpoint signs; no arbitrary witness gap is promoted to a physical cell boundary.

## Source and provenance binding

The verifier pins the landed affine-identity/source helper from PR #280 at Git blob
`9fd150e97bce84fdb3c4bad075c9938f4df9136c`. That helper fail-closes on the unchanged V7/V6/event-engine source/parser chain and supplies exact raw-source hashing.

The frozen v54 corpus is independently pinned at Git blob
`5841c331579489b25caef38cd412bdbf286f9134`.

The candidate independently re-lowers the original B-spline source to identify the constant-modulation spans, reconstructs the exact V6 call from constant channel coefficients and the phase endpoints, and requires exact equality with the historical V7 V6 route before building an ordered view.

This reconstruction shares the historical V7 B-spline lowering/dominance primitives and V6 algebraic endpoint/Sturm predicates. It is therefore a source-bound refinement/falsifier, **not an independent ownership theorem or independent source-codec implementation**.

## Exact ordered view

For each certified V6 span, the candidate records:

- exact original source interval and affine phase map;
- historical tan-half numerator;
- source endpoint relation, multiplicity and inward sign;
- exact tan-half root descriptors (rational value or unique exact bracket) with a source identity defined as the unique preimage under the pole-free monotone chart;
- source-order indices obtained from tan-half order, explicitly reversed for negative phase rate;
- per-root multiplicity from the repeated GCD/derivative chain;
- crossing/tangency parity and adjacent source-order signs;
- complete open source sign cells bounded symbolically by source endpoints/root descriptors, with signs established from the complete root order and exact one-sided signs;
- typed resource refusal when the fixed-degree tan-half isolation budget is exhausted.

The validator independently replays root counts, endpoint events, multiplicities, phase/source mappings, root order, exact one-sided sign evidence for the **symbolic** sign-cell boundaries, summary counts, and exact completeness of the submitted V6 span set. Interior chart samples are not physical cell boundaries.

## Falsification controls

The executable controls include:

- the same two non-rational roots of `cos(theta)=1/3` under positive and negative phase rate, requiring the source-order sequence to reverse while the exact tan-half roots remain the same;
- exact left source-endpoint and negative-rate right source-endpoint roots with **zero open roots**, checking endpoint multiplicity, flags and inward-sign handling;
- the double-root identity
  `(cos(theta)-1/3)^2 = 11/18 - 2/3 cos(theta) + 1/2 cos(2theta)`,
  requiring two multiplicity-2 tangencies;
- explicit isolation-budget exhaustion returning `RESOURCE_REFUSAL`, never mathematical truth;
- identity-zero and tangent-pole windows remaining outside certified isolated-root scope;
- a nonvacuous two-span omission with adjusted declared count; forged source identity, multiplicity, parity, complete-cell flag, affine phase map and summary attacks; and algebraic endpoint turn/principal-turn/rank/denominator/polynomial/interval provenance mutations;
- replay of every frozen v54 V6 owner case.

## Frozen v54 target

The checker requires exactly:

- 22 frozen cases mentioning `DELEGATED_V6_CONSTANT_MODULATION`;
- 21 cases with at least one historically `CERTIFIED` V6 owner span;
- 18 frozen ordered-premise cases / 18 V6 spans receiving checked source-ordered views.

The identity-zero/refused historical V6 case must remain outside the candidate. Historical v54 dispositions are never rewritten.

## Explicit nonclaims

This candidate does not solve:

- nonconstant-amplitude nonzero-phase polynomial/trigonometric/exponential roots;
- tan-half windows that cross a pole;
- identity-zero continuum semantics;
- V8–V18 cross-owner carrier/chart order transfer;
- V27/V41 nested child composition;
- V43 failed correlation certificates;
- source-knot composition between distinct owners;
- native material/topology/B-rep/STEP construction.

It does not modify the v54 43-owner inventory, frozen 121-case evidence, MC-038 gate/outcome, current authority, task graph, or 26-operation machining domain.

## Reproduction

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6_source_order.py --contract --self-test
```

Landing requires exact-head focused CI, `mc1-static`, and distinct technical review of the final source. Even if accepted, PB-007-01 remains globally open and MC-B/MC-1 remain `NOT_ESTABLISHED`.
