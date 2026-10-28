# MC-038 / PB-007-01 — stationary-cardinal polynomial ordered-root research

**Status:** 28 October 2026. **Evidence class:** deterministic exact-arithmetic research candidate. **Parent:** [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100). **Base main:** `219b60fbb97c1492b9e55a1554825bdaf0bff410`.

This is a bounded attempt to repair one explicit v54 category-3 premise. It does not create a successor issue, alter historical V6–V54 evidence, or establish MC-B/MC-1/native/STEP capability.

## Targeted missing premise

The v54 owner table classifies `EXACT_STATIONARY_PHASE_POLYNOMIAL` as:

`POLYNOMIAL_ROOT_COUNTS_WITHOUT_ORDERED_ROOT_ISOLATION_OR_PER_ROOT_MULTIPLICITY`.

Historical V7 already lowers a stationary cardinal-phase B-spline span to one exact nonzero polynomial over Q and records endpoint events plus distinct/multiple root counts. The missing interface is an ordered physical root sequence with exact multiplicity/parity and root-free sign cells.

The research hypothesis is that this premise is completely recoverable for the existing nonidentity stationary-cardinal owner by finite exact polynomial methods:

1. remove any rational endpoint factors exactly;
2. apply Sturm root counts to the square-free interior polynomial;
3. recursively bisect over Q until every open root is either an exact rational root or a rational interval containing exactly one real algebraic root;
4. recover that root's multiplicity with the repeated GCD/derivative chain;
5. use exact endpoint/interval signs and parity to classify crossings versus tangencies;
6. represent each physical sign cell by the exact ordered root/endpoint descriptors, with a rational witness subinterval used only to establish its sign; completeness follows from the complete ordered root list, not from truncating the physical cell to the isolating interval endpoints.

An algebraic root is represented by a square-free defining polynomial plus a unique rational isolating interval. No minimal-polynomial claim is made.

## Source and owner binding

The verifier pins the landed affine-identity/source helper from PR #280 at Git blob
`9fd150e97bce84fdb3c4bad075c9938f4df9136c`. That helper in turn fail-closes on the unchanged V7/V6/event-engine source/parser chain and supplies the exact raw-source digest rules.

The frozen v54 source corpus is separately pinned at Git blob
`5841c331579489b25caef38cd412bdbf286f9134`.

For checking, the source is re-lowered without invoking the historical selecting route. A stationary span is accepted only when:

- the source has zero affine phase rate;
- the prior amplitude-dominance owner does **not** apply;
- every active harmonic is cardinal at the stationary rational phase;
- the resulting physical polynomial is nonzero.

The builder may call the historical V7 route to retain the exact owner witness. The checker compares that supplied witness against an independently re-lowered stationary polynomial summary, requires the source parameter, source interval and affine map to match the original source piece, validates every rational/algebraic root's source-coordinate mapping, validates complete sign cells against the exact root/endpoint sequence, and proves that the submitted view set contains **exactly every** reconstructed stationary-polynomial span rather than merely validating whichever spans the candidate supplied.

Identity-zero stationary spans remain a different continuum-zero semantic case. Stationary noncardinal sources and preceding dominance-owned spans remain outside this candidate.

## Frozen v54 relevance

The pinned 121-case corpus contains exactly three cases involving the stationary-polynomial owner:

- one harvested single-span case, already returned as a one-span `CERTIFIED` result by v54;
- `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0`;
- `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100`.

The two composite cases are among the frozen 30
`BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE` results. The new verifier attempts to construct and independently check an ordered view for every stationary span in those exact source records.

**This does not change their historical v54 dispositions.** It establishes only that a candidate ordered premise now exists for this one owner family and can be considered for later reviewed integration.

## Falsification controls

The executable checks:

- endpoint multiplicities 2 and 3 plus one interior rational multiplicity-4 tangency;
- a simple rational crossing ordered before an irrational double tangency;
- two very close rational roots and typed resource refusal under an intentionally exhausted bisection budget;
- a nonzero constant polynomial;
- identity-zero refusal;
- wrong multiplicity, endpoint relation, summary parity/counts, wrong sign cell, omitted/reversed roots, omitted stationary spans, forged source parameter/interval/affine-map identities and corrupted exact cell-boundary references;
- preceding amplitude-dominance ownership, stationary identity-zero and stationary noncardinal boundaries;
- all three pinned frozen stationary-owner cases.

The isolation implementation has an explicit bounded bisection budget. Exhaustion is `RESOURCE_REFUSAL`, not a zero/nonzero or ordering truth value.

## Explicit nonclaims

This candidate does **not** solve:

- nonstationary polynomial-trigonometric/exponential root isolation;
- stationary noncardinal algebraic coefficients;
- identity-zero continuum semantics;
- V6/V8–V18 carrier/chart order transfer;
- V27/V41 nested child composition;
- V43 failed correlation certificates;
- original-source knot continuity/composition;
- native material, topology, B-rep or STEP construction.

It does not modify the 43-owner v54 inventory, frozen 121-case evidence, MC-038 gate/outcome, task graph, current authority, or the 26-operation domain.

## Reproduction

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_stationary_polynomial_order.py --contract --self-test
```

Landing requires exact-head focused CI, `mc1-static`, and a distinct technical review of the final source. Even if this bounded result is accepted, PB-007-01 remains globally OPEN and MC-B/MC-1 remain `NOT_ESTABLISHED`.
