# MC-038 prospective leaf: two-span stationary mixed zero components

**Status:** bounded deterministic mathematical-model research, not a capability decision. This leaf adds no historical source admission and does not change `current-implementation-state-v4.json`, any frozen v54 disposition, the source census, or the programme decision.

## Exact premise and its limit

The input is **one original** rational quadratic B-spline with two independent cosine coefficient channels `0` and `1`, each with five controls and the same knot vector `[L,L,L,K,K,R,R,R]`, `L<K<R`. The original global affine phase is preserved but this leaf **only proves** `offset=0, rate=0`, with no sine channels. Thus the physical function is exactly `F(t)=C0(t)+C1(t)` because both cosine factors are one. The current result **does not** cover moving phase, a stationary nonzero phase, sine channels, a higher-degree curve, arbitrary root providers, or general PB-007-01.

Exact Cox–de Boor extraction yields the first span's original triples `[c0,c1,c2]` and the second's `[c2,c3,c4]`, with independent interior evaluations of the original unsplit basis and exact Bernstein-to-global-polynomial checks. Equality of two quadratic forms at three distinct exact interior points establishes polynomial identity on each physical span. The shared control `c2` enforces the actual source continuity rather than admitting a fabricated caller-supplied piece list. No user-provided root counts or standalone child certificates are trusted.

The resulting degree-at-most-two **physical** polynomials are completely solved on each closed source span when their roots are rational: linear roots, a negative discriminant, rational square-discriminant roots, or the identically-zero polynomial. A nonsquare positive discriminant returns **BLOCKED**, even when an alternate method might prove that its roots fall outside the physical span. That is a deliberately restricted premise, not a claim of irrational-root coverage.

Globally the output derives (1) maximal closed zero intervals, (2) isolated roots outside those intervals, including true exterior endpoints, with distinct left/right knot orders and **no global smooth knot multiplicity**, and (3) maximal nonzero sign cells, merging across proved nonzero knots only. A root on the boundary of a closed zero interval is absorbed; total finite root cardinality is false whenever a zero interval exists. All arithmetic is exact rational with bounded input and intermediate size.

## Reproduction and falsification

```sh
python3 -m py_compile research/machining-completeness/tasks/MC-038/pb00701_two_span_stationary_components.py research/machining-completeness/tasks/MC-038/test_pb00701_two_span_stationary_components.py
python3 research/machining-completeness/tasks/MC-038/test_pb00701_two_span_stationary_components.py
```

Twelve test methods include 120 deterministic continuous linear two-span recompositions. Cases exercise a zero-left/finite-right pair, its mirror, a continuum plus disjoint isolated endpoint, complete stationary cancellation from nonzero channel coefficients, isolated knot sided order (2,1), merge across nonzero knot, negative/nonunit domains, negative and fractional Bernstein controls, forged/stale output/source and noncanonical inputs, and irrational-root refusal. The full-domain moving-phase example and (2,4) sided knot orders in [issue #100 comment 6597886756](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6597886756) remain **unproved by this leaf**, not reclassified as success.

A future expansion would need independently checked moving-phase child zero-component certificates, including continuum zeros, exact endpoints and complete isolated root ordering, composed back to the original B-spline source. Falsify any such expansion on mixed interval/point knots, nonzero-knot cell continuity, distinct one-sided jets, source-binding mutation, negative Bernstein controls, and genuine unsupported roots before discussing a larger coverage claim.

**Authority:** PB-007-01/02/03/04 OPEN; MC-B and MC-1 `NOT_ESTABLISHED`; production unauthorized. No physical/native STEP, independent engineering consumer, or paid campaign evidence is implied.
