# MC-038 / PB-007-01 — alternate exact stationary source-knot and signed-cell derivation

**Date:** 6 November 2026 UTC; **corrected 8 November 2026** following [#421 exact-head HOLD](https://github.com/techrote/radiCADSAC/pull/421#pullrequestreview-5815240000) and [#428 prior-art challenge](https://github.com/techrote/radiCADSAC/pull/428). **Status:** independently reviewable alternate derivation, *not* novel historical ordered-premise closure, a V54 edit, final PB-007 acceptance, or MC-B/MC-1 success. **Evidence class:** `DETERMINISTIC_MODEL`. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Coordination:** [#324 claim 6672895157](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6672895157). **Base:** `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.

## Precise hypothesis and falsifiers

The frozen V54 owner `EXACT_STATIONARY_PHASE_POLYNOMIAL` has a separately completed, independently checkable ordered Sturm span verifier. Its original V54 category-3 refusal concerned whole-original knot continuity, ordered root/endpoint semantics, sided multiplicity, physical sign transfer and maximal nonzero cell recomposition. **That capability is not new here:** accepted main already has the generic source-bound `pb00701_stationary_knot_composition.py`, Git blob `d0fbe7e189066fd9398958f1b1814b8147a6a64e`, which composes these same two frozen originals. PR #428 explicitly falsified the novelty/30→28 argument. The present implementation gives an alternate constrained verifier and certificate representation, not new historical evidence.

**Hypothesis:** for an original two-piece rational B-spline source whose actual phase is stationary and cardinal, both source-polynomials are nonidentically zero, every original span is admitted by the *same* stationary owner, both span order certificates validate, and their actual rational physical knot values agree, the ordered union of the two root sets (plus a zero knot, if present) yields every distinct original-source zero. At a nonzero knot, adjacent same-sign cells glue; at a zero knot they cannot glue and both one-sided orders must remain distinct.

**Falsifiers:** any source/hash mismatch; a missing, overlapping or forged ordered child; an unaccepted owner; a discontinuous physical knot; a missed or doubled root; a flipped physical sign; a wrong even-root parity; a true knot zero recorded as a single unsourced multiplicity; any identity-zero interval encoded as finite; or a resource budget converted into truth. The output is an **alternate preexisting-result derivation**; neither its existence nor its independently replayed source proof changes any accepted v54 disposition or previously complete V2 result.

## Exact original frozen witnesses

The selected originals are actual immutable V54 source records, not newly manufactured arithmetic examples. Both use `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`, shared source parameter `source-time-t`, interval `[0,2]`, true knot `1`, and exact phase offset/rate `0/0`.

| Case ID suffix | Canonical source SHA-256 | Original physical function on [0,1] | Original physical function on [1,2] |
|---|---|---|---|
| `EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0` | `f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff` | `t-1/2` | `1/2` |
| `EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100` | `a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd` | `t-1/2` | `1/2+100(t-1)` |

The first H1 cosine B-spline has degree one with clamped controls `[-1/2, 1/2]` on the left and `[1/2,1/2]` on the right. The second case has the same H1 controls and additionally H0 cosine controls `[0,0]` on the first span and `[0,100]` on the second. These controls, not caller-supplied simplified polynomials, determine the physical functions; the verifier reconstructs them independently with the existing pinned V7 lowerer. The knot value is exactly `1/2` from both sides.

In **each** original, the entire zero set is exactly `{1/2}`, multiplicity one on the first original span, crossing NEGATIVE to POSITIVE. There is no exterior or knot zero. The maximal physical nonzero cells are `(0,1/2)` NEGATIVE and `(1/2,2)` POSITIVE, the latter constructed by gluing the two actually continuous positive source pieces.

Both V54 records originally say `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE`. They already appear as complete source-specific witnesses in the **previous** V2 50-source register; this study does not count those witnesses as new.

## Constructive proof and termination boundary

On each normalized span, the pinned `verify_pb00701_stationary_polynomial_order.py` validator re-lowers actual original polynomial coefficients, checks historical `EXACT_STATIONARY_PHASE_POLYNOMIAL` owner attribution and pre-existing route summary, and independently checks every ordered root descriptor against square-free Sturm counts. Rational roots must evaluate to exactly zero. Nonrational roots must have an exact rational isolating interval with exactly one root. The GCD/derivative chain certifies multiplicity; exact rational witnesses and parity certify the open-cell signs. Exact endpoint germs and the affine original-source map remain bound. The validator checks **all** stationary spans, not merely views selected by a caller.

This alternate compositor, distinct from the accepted generic compositor, checks that there are exactly two consecutive source spans, both certified under that owner, and their exact physical knot values coincide. For a nonzero knot, equality plus continuity forces both adjacent source signs to equal the knot sign; it glues exactly those two cells. For a zero knot, it retains two explicit sided orders and distinct one-sided signs; equal signs mean a touch, unequal signs a crossing, with **no invented global analytic multiplicity**. It concatenates exact child event orders by their disjoint source intervals, includes every zero knot once, retains exterior inward germs, and checks the resulting maximal nonzero cell partition has `events+1` cells. Nothing is decided by numerical sampling: completeness is inherited from the exhaustive Sturm-root child proofs plus the exact rational knot equality and disjoint piece partition.

**Termination:** exact polynomial Sturm isolation terminates in the mathematical unbounded algorithm because a nonzero rational polynomial has finitely many separated real algebraic roots; repeated GCDs strictly decrease degree, and rational bisection isolates distinct roots after finite steps. The public implementation enforces a 512-bisection work budget, with exhaustion returning **nontruth refusal**. The two frozen linear originals terminate without any difficulty. This does **not** establish the project's general nonstationary analytic event theorem, arbitrary identity-zero source-interval composition, or an unlimited-complexity total program.

## Adversarial contract

Executable checks exercise the two original cases; mutated source hash, fake gate acceptance, omitted or changed root multiplicity, changed signs, incorrect maximal-cell counts, corrupted knot relation, corrupted child proof; a rational open crossing arbitrarily close to the knot using `2^-120`-scale controls; exact zero knot crossings and two-sided touches; two quadratic interior double tangencies; identity-zero span refusal; discontinuity refusal; nonstationary phase refusal; and a zero-bisection typed nontruth refusal. Mutant controls must fail even if totals are unchanged. The original historical source and raw failure records are never rewritten.

Run from the repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_stationary_knot_successor_20261106.py --self-test --report
python3 research/machining-completeness/tasks/MC-038/pb00701_stationary_knot_successor_20261106.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

The machine-readable companion freezes **unchanged** historical before/after and both original source identities. Its producer replays both exact source proofs **and** the already accepted generic compositor from pinned Git blob `d0fbe7e189066fd9398958f1b1814b8147a6a64e`, comparing source SHA-256, exact root coordinate/order/multiplicity/signs, nonzero physical knot and maximal cells. A mismatch is NONTRUTH. It then checks the complete receipt against its Git blob `7b613448510b5465aeec44a1bf8bc3d289b84a16` on `--contract`, not a self-signed unverified novelty assertion. Adversarial regressions reject invented 30→28, new-ID and gate acceptance credit.

## Exact matched census and status of claim

The unchanged v54 corpus Git blob is `5841c331579489b25caef38cd412bdbf286f9134`; the unchanged v2 source-specific evidence register is `e52d3baf3692a011cf86234eeaa992ef407d99fd`. The child polynomial research code blob is `0954c5e1ad63ec1c8dd2acb3202882650b02c516`; that code pins its underlying original-source lowerer.

| Population/status | Historical before | This proposed successor overlay | Candidate delta |
|---|---:|---:|---:|
| Frozen original sources | 121 | 121 | 0 |
| Historical blocked source routes | 20 | 20 | 0 |
| Missing ordered source premises | 30 | **30** (preexisting proof replay only) | **0** |
| Previously complete source-specific V2 witnesses | 50 | 50 | 0 |
| Required PB-007 proof obligations discharged | 0 | 0 | 0 |

The two selected source IDs remain historically blocked in immutable V54 but have **preexisting complete V2 source-specific witnesses and preexisting generic stationary two-span composition**. Their event/sign semantics are independently replayed here without advancing the 30 historic missing ordered premises, the 20 route refusals or the 50 complete V2 witnesses. There is no claimed new generic stationary owner consumer interface; no `30→28` credit is permitted. This corrected statement supersedes the original novelty claim in the PR description.

## Limits and downstream dependency

An accepted result would preserve an **alternate, independently rechecked certificate representation for two already-composed stationary-cardinal original sources**. It does not newly discharge an ordered physical sign-transfer premise or originate a general compositor, since both were present in accepted main. It would **not** repair V6 delegated carrier order, V9–V18 sine-bearing/nonconstant phase, V27/V41 nested child consumption, V43 uncertified routes, the general analytic event theorem, identity-zero continua, or any global PB-007-01..04/PO-02/04/05/07/08 obligation.

MC-B and MC-1 remain `NOT_ESTABLISHED`. This research is deterministic model mathematics, not native material, independent oracle, actual engineering STEP, or a change to the 26-operation domain, topology, durable bodies, journal, source semantics, evidence authority or production restrictions. There is no authorization to merge into main while a separate integration owner holds that write scope.
