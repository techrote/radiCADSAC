# PB-007-01 v45 — exact single-generator child representation

Owner #255. Base `8b215136ea9d30bc018618525d73d9b97c09b4bc`. Evidence class: DETERMINISTIC_MODEL. The theorem, finite-termination argument, interfaces and limitations are in `docs/machining-completeness/69-PB00701-ALGEBRAIC-CHILD-MAP.md`; executable controls and historical pins are in the v45 verifier and artifact.

## Hypothesis and decisive falsification

Source-owned algebraic orientation cuts can be normalized exactly, retaining every polynomial and phase contribution, without consuming a new analytic event. A decisive counterexample to naive reduction is the square-free but reducible modulus `(2x^2-1)(x^2+1)` at alpha=sqrt(2)/2. V45 must derive the selected irreducible factor; otherwise its zero test and field claim are false.

## Implemented result

Finite exact factorization plus MC-032 Sturm root selection supplies a canonical real embedding. Rational coefficient vectors modulo that minimal factor give exact addition, multiplication, equality, zero, inverse and sign. Both affine child maps are constructed in Q(alpha); all source polynomials are restricted in Q(alpha)[u] and reconstructed coefficientwise through inverse maps. The source id, global parent interval, original lowered coefficients and affine phase law remain bound. Each algebraic cut yields an independent two-child representation, not an asserted multi-generator partition.

The v44 residual gains representation evidence through an explicit adapter, while the predecessor's physical event result stays unchanged. No analytic child is dispatched or certified, no physical root is manufactured at an orientation cut, and no non-anchor/amplitude derivative channel is discarded.

## Attempt and validation record

A local development test initially reversed the sign of alpha-470832/665857. Exact integer square comparison showed the fixture expectation was wrong; the test now checks both sides using neighboring rational convergents. The arithmetic algorithm was unchanged. Local core tests execute against an extracted MC-032 arithmetic snapshot because this environment cannot clone the repository; full source integration, historical pins and contract verification are delegated to the actual repository CI and must pass before merge. No local integration PASS is inferred from that snapshot.

Initial PR-head focused run `36914228418` at `c4bc23c75ec2445a27068df07067b436cd0c7d5b` passed all core tests and the genuine source representation, but failed an overly broad forged-metadata equality assertion. The preserved source grammar rejects the unknown `v45_child_representation` field; it must not be stripped or admitted just to reproduce the clean-source result. The suite now separately requires unchanged results for the predecessor's explicitly ignored certificate fields and exact predecessor rejection for unknown fields. The representation adapter also propagates that predecessor rejection/refusal status rather than describing it as NOT_APPLICABLE. No source admission rule or algebraic predicate was relaxed.

The focused gate runs the contract, 10 core test methods and 6 source-integration test methods, with many subcases and mutations. Required coverage includes reducible square-free and repeated moduli, distinct conjugates, nearby algebraic cuts, both phase directions, exact zero and tiny nonzero signs, coefficient reconstruction and chain rule, forged fields/maps/source ids, type rejection and resource refusal. `mc1-static` remains unchanged. PR-head and independent merged-main results must be recorded on #255 and MC-038/#100 before explicit closure.

## Remaining boundary

The representation requirement of v44 is addressed for one algebraic generator at a time. Exact trigonometric endpoint equality/sign/multiplicity and multi-generator composition are not established by this package. PB-007-01 remains OPEN; PB-007-02 dependent; PB-007-03 OPEN; PB-007-04 OPEN_PROPAGATED; PO-04/05/08 OPEN; MC-B and MC-1 NOT_ESTABLISHED. The denominator remains 26 operations. No protected source/audio/provenance or downstream contract changes; no native, paid, production or expensive campaign.
