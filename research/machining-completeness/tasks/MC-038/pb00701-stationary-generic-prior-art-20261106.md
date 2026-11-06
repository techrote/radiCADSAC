# MC-038 / PB-007-01 — prior generic stationary-compositor boundary

**6 November 2026 · source-critical C candidate · `DETERMINISTIC_MODEL` · NO PB/MC gate promotion.** Parent [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100); [coordination #324](https://github.com/techrote/radiCADSAC/issues/324). This is an independent **generic-interface** audit, distinct from [PR #427](https://github.com/techrote/radiCADSAC/pull/427)'s separate *source-specific novelty counting* falsifier.

## Falsifiable hypothesis / narrow decision

**Proposed route:** `NEW_GENERIC_STATIONARY_TWO_SPAN_KNOT_COMPOSITION_REQUIRED` — [PR #421](https://github.com/techrote/radiCADSAC/pull/421) offers the first conditional general original-source knot/sign-cell compositor for two stationary rational B-spline polynomial spans, so the 30 historically missing owner premises can be reduced by the two named originals solely on that basis.

**Falsifier:** a previously accepted implementation already handles **all** exact signed-root/cell composition primitives in that two-span *stationary-polynomial, complete-child-certificate, nonidentity-zero* subgrammar, including zero/nonzero true knot, one-sided multiplicities/parity, original-source ordered roots, endpoints and maximal physical sign cells, without requiring either of the two newly proposed fixed-source certificates. The old generic implementation also accepts a third source span, making the admitted two-span composition no new mathematical coverage. A distinct certificate format, defensive validation or alternative derivation may still be useful; that is not a previously absent mathematical event/sign-transfer ability. We do **not** claim all code, checks or implementation choices in #421 are identical.

## Primary source custody / exact proof contracts

- Authoritative source at claim: [main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`](https://github.com/techrote/radiCADSAC/commit/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9).
- Previously landed [`pb00701_stationary_knot_composition.py`](https://github.com/techrote/radiCADSAC/blob/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9/research/machining-completeness/tasks/MC-038/pb00701_stationary_knot_composition.py), Git blob `d0fbe7e189066fd9398958f1b1814b8147a6a64e`. Its **preexisting** `compose_polynomial_spans` explicitly accepts 1..32 complete ordered polynomial source spans (256-event budget), independently revalidates each Sturm view, rejects identity-zero child intervals as discrete finite events, requires exactly consecutive intervals and rational physical knot equality, and preserves endpoints, source-knot sided orders, crossing/touch, sign transfer, physical root order and maximal nonzero cells.
- Its preexisting `replay_frozen_stationary_cases` binds the true original source, fixed historical v54 owner, frozen corpus, source-domain authority and the 26 accepted operations before invoking that generic compositor. The generic mathematical function alone never authorizes an arbitrary caller's source.
- Candidate [#421](https://github.com/techrote/radiCADSAC/pull/421) exact head `359784454c4eaeda173458b9f4919b07edbdacd8`; candidate source blob `01605f2f00abc327ffdba2ab600d4ff9588da619`, machine receipt blob `d7ee51ed09bc317f29177286dbd9b1e827c8bd10`. Its `compose_checked_child` offers a second source-bound two-span validation/representation; independent difference in contract structure or validation engineering is not denied.
- Frozen 121-case original corpus blob `5841c331579489b25caef38cd412bdbf286f9134`; preexisting complete 50-source V2 register blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`. Neither modified.

| Named actual frozen original | Original canonical SHA-256 | Closed source/phase/knot | Exact already-produced signed result |
|---|---|---|---|
| `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0` | `f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff` | t∈[0,2], stationary 0 turns, knot 1 | F=t−1/2 then 1/2; unique simple t=1/2 NEG→POS, positive knot |
| `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100` | `a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd` | t∈[0,2], stationary 0 turns, knot 1 | F=t−1/2 then 1/2+100(t−1); same source-time root order, knot, signs |

Both already `COMPLETE_SOURCE_SPECIFIC` in frozen V2 and remain v54 `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE` as historical **generic-owner** states. The original V54 failure must not be silently edited or counted as closed by another equivalent source witness.

## Mathematical coverage and terminating proof boundary

For a finite ordered source partition `a=t0<t1<...<tn=b`, suppose every open piece has an independently certified **nonidentically zero rational polynomial** with complete exact distinct roots, multiplicities and strict cell signs; the actual global source parameter/phase and piece maps are preserved; and exact left/right limits at each common true knot agree. Then the full zero set equals the disjoint union of every open-piece root, all zero true knots (once each), and zero exterior endpoints. No new interior zero can appear because each child certificate is exhaustive. Exactly matching nonzero knot values imply equal adjacent nonzero signs, so those cells join; a zero knot interrupts them, retaining separate left/right one-sided multiplicities and signs. This construction determines all maximal physical nonzero cells and crossing/touch parity without assuming global smoothness at knots.

The old `compose_polynomial_spans` has exactly these necessary transfer checks and already produced both frozen originals. Finite-polynomial Sturm/GCD sign/root certificates terminate mathematically for each admitted nonzero rational polynomial, with finite roots and exact rational separating intervals. Implementation span/event limits and optional Sturm bisection budgets produce **nontruth refusal** when exhausted; they do not prove nonexistence, monotonicity or general analytic-event decidability. No identity-zero continuum or arbitrary sine-bearing/nonstationary source is covered by this narrow compositor.

## Reproduction / independent positive and adversarial controls

The companion Python verifier pins the **Git blobs**, reconstructs original-source SHA-256, recomputes the 121/20/30/50 v54/V2 census and reexecutes the *existing* baseline producer for all historical stationary rows. It independently exercises prior generic composition over:

- original nonzero positive knot join; zero true knot with a 1/1 crossing; zero true knot with a 2/2 tangential touch;
- interior degree-two double tangency; an exact rational crossing at distance `2^-120` from a true knot; an exterior endpoint zero;
- a **three-span** nonzero signed source, strictly outside #421's two-span-only composition interface;
- conservative refusal of an identity-zero source piece, a physical knot discontinuity, source or evidence hash drift, nonfinite/duplicate JSON, type-alias receipt promotion, and over-budget raw data.

The separate hosted workflow checks out **literal #421 SHA as a second working tree** and runs its existing full mathematical/adversarial verifier; it additionally compares that candidate's two exact original-source root/order/sign/knot results against the prior producer. This does not claim proof beyond these exact source and grammar gates.

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_stationary_generic_prior_art_20261106.py --contract --self-test --candidate-root candidate421
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

`candidate421` must be an independently checked-out Git worktree exactly at `359784454c4eaeda173458b9f4919b07edbdacd8`; the Python verifier fails closed if the candidate's commit or blob differs. A local source-only audit may omit `--candidate-root`, but **must not** then claim a newly executed candidate differential comparison.

## Source-matched evidence census and consequences

| Classification | Before | After | Accepted delta |
|---|---:|---:|---:|
| Frozen original sources | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Missing generic owner ordered premises | 30 | 30 | **0** |
| Already complete V2 source witnesses | 50 | 50 | 0 |
| Required PB/PO discharges | 0 | 0 | 0 |

**Candidate bounded C:** the claim that #421's **generic stationary two-span composition semantics** were wholly unavailable before #421 is contradicted by a prior, broader, already-executable compositor with the same mathematical transfer obligations, including bound original-source replay. This is a finding about prior capabilities and novelty, **not** a proof that #421's source code is incorrect or that every extra validation/representation feature was redundant. It does not falsify an independently demonstrated new generic *nonstationary*, sine-bearing, >32-span, identity-zero or universal source-consumer theorem.

**Critical path:** stop assigning historical blocker reduction for duplicate source-specific/knot-composition certificates. Require a precise source-bound previously missing **owner/consumer condition** or tackle the unreconciled nonstationary sine-bearing event/root-order theorem and physical category-3 transfer. Preserve PB-007-01/02/03/04 and PO-02/04/05/07/08 as OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`. All 26 operations, bodies, topology, journal, native engineering STEP/independent consumer/evidence custody and separate production/native authorization remain unchanged.
