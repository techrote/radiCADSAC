# MC-038 / PB-007-01 — bounded cross-polynomial real-algebraic root comparison

**Date:** 30 October 2026. **Status:** proposed deterministic-model research; not MC-B, MC-1 or production admission. **Owner:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Pre-registration:** [#100 comment 6522837542](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6522837542). **Base:** `9f16d059b9c35e17afaab9ef90fe9d2119c2c4c8` (PR #320). No source files, frozen corpus, authority or MC gate registers changed.

## Hypothesis and decisive falsification

Two separately isolated exact real roots can be ordered or proved equal without constructing a multiquadratic or general compositum field. Represent each root as a primitive positive-leading squarefree integer polynomial and a strictly isolating open rational interval. Compute a rational-polynomial GCD and Sturm root counts. Equality is proved only when the common factor has a root in the *intersection* of both certified isolators. Otherwise use exact rational separation; bounded exhaustion is a resource refusal, **not equality**. A counterexample is any accepted malformed isolator, false common-root equality, wrong ordering, unbounded refinement, or accepted forged replay.

## Exact theorem and algorithm

For squarefree polynomials `f,g` over Q, each with exactly one root in its respective open rational isolator `I,J`, any common zero in `I∩J` is necessarily the selected zero of both. The Euclidean GCD has exactly those common zeros. A Sturm variation difference for the squarefree GCD on the overlap therefore certifies equality if and only if its open root count is 1. If the intervals are already disjoint, their ordering is strict, even if `f=g` globally.

When overlapping intervals contain **no** shared root, a midpoint rational `q` in the overlap splits the selected roots. Direct polynomial evaluation detects a rational root exactly; otherwise Sturm root counts from each isolator's left endpoint to `q` decide the root's side. Different sides give strict order; equal sides shrink both intervals. The roots are distinct, so mathematical rational interval refinement eventually separates them, although this implementation can stop at its explicit 64-round budget and return `RESOURCE_REFUSAL`. No floating point, midpoint sign heuristic, root approximation, or infinite-loop fallback is used. Submitted certificates are structurally and dimension-bounded **before** JSON serialization, then *recomputed* from original canonical records; agreement of a client-supplied sign is never trusted.

The grammar deliberately admits reducible **squarefree** polynomials: this permits the same root to be certified under different parent polynomials, e.g. `2x²−1` and `(2x²−1)(x²−3)`, without pretending to construct a field over the reducible polynomial. Polynomials with repeated factors refuse; primitive integer coefficients, endpoint rational syntax, exact root counts and explicit degree/bit caps are checked before calculation.

## Bounded grammar and negative cases

Degree 1–6; canonical primitive integer coefficient list in ascending degree with positive leading coefficient and at most 96 input bits; exact rational strict open isolator with at most 256 endpoint bits; maximum intermediate rational bits 8192; 64 separation refinements; serialized certificate cap 65536 bytes. No arbitrary algebraic compositum, arbitrary input degree, transcendental phase-zero or equality decision, nonmonotone original-source root theorem, native machining material/topology or STEP result is inferred.

A constructed pair of distinct degree-one rational roots separated by approximately `2^-90` and given broad overlapping isolators must end in typed `RESOURCE_REFUSAL` after the bounded steps; it must **never** be identified as equal. Repeated polynomials, nonprimitive sign flips, ambiguous/multiroot intervals, endpoint zeros, forged relations, oversized data and swapped selected embeddings are negative controls.

## Source binding, verification and custody

The contract tests historical `α=+√2/2` from the actual V45 cut, an independent `β=+√3/3`, the negative α conjugate, rational 1, and the real root of `x³−2`. Their original source is the frozen V44 report SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`. To avoid a copied-constant masquerading as provenance, the hosted contract invokes `verify_pb00701_multiquadratic_embedding.source_contract()`, which in turn verifies the pinned PR #319 independent-checker Git blob and replays the source-bound V44/V45 authority evidence. Those predecessor checks are part of this contract's runtime, not a claim that the new comparison theorem itself has become a historical owner.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_algebraic_cut_comparator.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
```

The new tests cover 25 ordered root pairs, 49 independently cross-checked rational-root pairs and six forward/reverse examples; a shared root of a quartic and a quadratic, same polynomial/different conjugate, rational midpoint-zero, cubic versus quadratic, invalid isolators, exact-zero at a supposedly open boundary, forged certificates and bounded close-root exhaustion. The locally exercised algorithm is source-independent; **hosted exact-head runs are necessary** to qualify the transitive frozen-source check. Failed attempts remain evidence and are not erased. The final PR head, raw workflow run identities, review and landed-main identity must be appended to #100 before any merge qualification is claimed.

## Implications and open obligations

Cross-polynomial equality/order is a useful *algebraic coordinate comparator* and removes one narrow dependency on a fixed Q(√2,√3,√5) basis for comparing cut coordinates. It does not construct affine child maps over arbitrary algebraic extensions, decide non-polynomial physical signs at those coordinates, or resolve whether an analytic timed phase is exactly zero at an irrational coordinate. The historical v54 `EXACT_STATIONARY_PHASE_POLYNOMIAL` gap and general nonmonotone event isolation remain open. PB-007-01 and MC-038 remain open, MC-B and MC-1 remain `NOT_ESTABLISHED`, historical v54 remains `BLOCKED`, and production remains unauthorized. No native or paid permit is used.
