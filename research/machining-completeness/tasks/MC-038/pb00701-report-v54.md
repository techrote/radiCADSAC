# PB-007-01 v54 — finite historical-owner inventory and ordered-span adapters

Date: 18 October 2026. Issue: #275. Evidence class: DETERMINISTIC_MODEL.
Issue-reviewed main: `9734776b3cef3d7039be9623e8872df2c2a85174`; branch base main
`7e82d5a21ad5879a497c91ec2b1ca12863e06e9b` (adds only the docs-only PR #276).
Implementation scope: bounded original source event composition, not native geometry.
Acceptance authority: executed repository tests and the exact-head/merged-main
ledger on #275/#100. This report does not itself declare a branch landed.

## Hypothesis and falsification

The reversed V53 principal original B-spline source selects historical
`EXACT_RATIONAL_AMPLITUDE_DOMINANCE` on a root-free piece. Hypothesis: its existing
amplitude certificate establishes a complete strict nonzero sign on the closed span
without any derivative claim, so an owner-specific finite SIGN_SPAN adapter can
close V53's missing-adapter boundary without relabelling the owner V19/V50.

Falsifiers: the actual proof lacking complete-span sign, exact endpoint relation or
source binding; a checker that needs to classify or select a replacement proof; or
an inferred monotonicity/simplicity/order taken from a count or common-looking field.

**Result: confirmed.** The certificate bounds `|F(s)| >= margin > 0` for every `s` in
the closed normalized span (all monomials and trig factors are bounded by one), its
regeneration needs only V7's own `_dominance_certificate`, and the sign/endpoint
relations follow from that bound alone. The same bounded method was then applied to
every implemented owner family (the finite inventory below).

## Recovery context and pre-implementation baseline

Earlier sessions on #275 left no recoverable implementation: the forensic branch
`mc038/pb00701-v54-finite-owner-coverage` holds a truncated staging payload (gzip
`unexpected end of file`), and the 2A-R1 preservation packet contains only main
sources. Both remain untouched. This implementation was rebuilt from authoritative
main on `mc038/pb00701-v54-recovery`, whose temporary recovery workflow is removed.

The local environment could clone directly. Before implementation the unchanged
V53 verifier passed locally (`verify_pb00701_v53.py --contract --self-test`, 5m20s,
including its complete inherited V52→V47 chain). The earlier stale test expectation
`DISCONTINUOUS_PHYSICAL_SOURCE_KNOT` is not reused; V54 tests assert the actual
unchanged V52 reason `PHYSICAL_SOURCE_KNOT_DISCONTINUITY`.

## Finite owner inventory

Static AST enumeration of literal `route_kind` assignments in the implemented
`pb00701_*` modules gives exactly 43 owner identifiers, equal to the canonical table
(`pb00701-finite-owner-inventory-v54.json`). Categories:

1. **Already-supported ordered (5):** V50 product via V51; V19, V47, V48, V49 strict.
2. **Adapted (20):** V7 amplitude dominance as `SIGN_SPAN`; nineteen whole-span strict
   derivative owners V20, V21, V22, V23, V24, V25, V26, V28, V29, V30, V34, V35, V36,
   V37, V38, V39, V40, V42, V43 as `OWNER_STRICT_SPAN`.
3. **Exact owner lacking an ordered premise (16):** V7 stationary polynomial
   (`POLYNOMIAL_ROOT_COUNTS_WITHOUT_ORDERED_ROOT_ISOLATION_OR_PER_ROOT_MULTIPLICITY`);
   V6 delegated constant modulation (tan-half window counts); V8 (factor/chart
   counts, no cross-factor order); V9/V10/V11 (auxiliary-ratio monotonicity per
   pole-safe chart, no physical sign or cross-chart order); V12 (partition cells by
   counts); V13–V17 (nonvanishing multiplier over a category-3 V10/V11/V12 carrier,
   no physical sign transfer); V18 nonvanishing source factor and V18 Laurent factor
   (residual delegated through the full V17 classifier); V27 and V41 (children
   re-classified by the full predecessor classifier and composed by count summaries).
4. **Blocker / non-event (2):** `PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY`; V44's
   always-BLOCKED orientation-cut consumption boundary.

Classification came from the actual route objects of corpus instances, not names.
The nineteen strict owners all return CERTIFIED routes containing an owner-specific
certificate whose `direction` feeds `v19._root_summary`, plus a statement that the
complete derivative is strictly nonzero on the closed span. Category-3 routes contain
only counts, chart-local auxiliary monotonicity or classifier-delegated sub-results.
A category-3 view would need a new ordered-isolation or nested-composition theorem;
it is not a missing check of an existing proof.

An owner identifier's category is separate from an instance's disposition: a
category-2 owner such as V43 can emit a BLOCKED route on a particular span, and then
the complete predecessor BLOCKED result is returned unchanged.

## Construction and finite truth interface

All files are under this directory:

- `pb00701_finite_owner_span_model.py` — owner table, `SIGN_SPAN` and
  `OWNER_STRICT_SPAN` builders, composition wrapper
  `build_finite_owner_source_evidence(original_spec)`.
- `pb00701_finite_owner_span_certificate.py` — `validate_ordered_span_view` and
  `validate_finite_owner_certificate(candidate, original_spec)`.
- `pb00701_finite_owner_witness_check.py` — original-source leaf, selected-anchor,
  strict-residual, endpoint and pinned-route-metadata verification without a
  historical selecting-route invocation.
- `pb00701_finite_owner_inventory.py` — static/observed inventory and corpus runner.

Every new view (`radicadsac-ordered-span-view/54.0`) keeps the actual owner, owner
version, owner-specific adapter name, recipe, original material binding, positive
affine map and complete underlying witness. Construction regenerates the route with the owner's historical recipe. Checking
does not call that selecting route: it validates the supplied harmonic/quadrature
through the historical exact leaf certificate, independently rechecks V20–V30's
two-active-harmonic source admission without selecting a replacement anchor,
any required residual inequality, rational-turn endpoints, root summary and
pinned literal route metadata, then compares the complete typed view.

`SIGN_SPAN`: one positive-width open cell of sign `sign(a0)`, two NONZERO exteriors with
that relation and inward sign, zero roots, `endpoint_roots_possible: false`,
`derivative_certificate_claimed: false`, `monotonicity_claimed: false`. The
endpoint-root case is impossible by the positive closed-span margin.

`OWNER_STRICT_SPAN`: `delta` from the owner's certificate; exterior relations from the
route's own exact `left_event`/`right_event`; zero left endpoint inward `delta`, zero
right endpoint inward `-delta`; opposite signs give one `UNIQUE_ANALYTIC_ROOT`
(multiplicity one, arithmetic nature UNCLAIMED) with cells `(-delta, delta)`. Each
derived summary field must equal the field the owner recorded.

Composition reuses V52's exact lowering, knot continuity (full right-minus-left
physical expression at the exact knot turn), separate one-sided orders,
crossing/tangency from inward signs, root union and maximal nonzero cells. V54 runs
complete V53 first and grows only from `SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE`;
category-3/4 owners give `SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE` (with the named
premise) or `SPAN_OWNER_IS_BLOCKER_OR_NON_EVENT`, retaining the V53 predecessor.

## Executed principal original-source result

`test_pb00701_finite_owner_span_integration.candidate()` is `reverse_source` of the V53
acceptance source: global `u in [0,2]`, phase offset `1/2`, rate `-1/4`. V53 returns
`SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE` at span 0, owner amplitude dominance, margin
`97/200`, sign POSITIVE. V54 certifies:

- span views `SIGN_SPAN` (owner V7, witness byte-identical to the predecessor route)
  and `V51_PRODUCT` (owner V50);
- exact POSITIVE continuous knot at `u=1`, coalesced into the first maximal cell;
- two open roots: one simple crossing and one double tangency (same global summary as
  V53's forward result);
- maximal signs `(+,+,-)`, exactly the reverse of V53's `(-,+,+)`.

## Adversarial and source integration evidence

Direct tests (`test_pb00701_finite_owner_span.py`): positive and negative dominance;
margin zero/negative refused by the historical recipe; forged ZERO exteriors; forged
sign, margin, root counts, `direction`/`monotonicity` fields, boolean/float values and
unknown keys; wrong kinds and relabelled owners; source, phase, harmonic, identity and
interval mutation; every strict owner on frozen instances covering root-free,
endpoint-root and open-root shapes; flipped directions, swapped events, forged counts
and cross-owner witness substitution; checking with every loaded classifier, builder,
carrier/residual delegate and selector disabled; resource refusal versus propagated
unrelated errors; inventory exact-once categories and table corruption.

Integration tests (`test_pb00701_finite_owner_span_integration.py`): the principal
source; preserved V52 all-product and V53 mixed results returned unchanged;
STRICT+legacy (V19 + dominance), all-legacy (dominance + dominance), PRODUCT+legacy and
the four-piece `SIGN(-)|PRODUCT|STRICT|SIGN(+)` source with knot relations
NEGATIVE/POSITIVE/POSITIVE; owner-strict adapters composed on corpus sources; repeated
and different knots/degrees with extra channels; exact continuity versus a `1/10^30`
jump; non-unit affine maps, reversal and negation; certificate-level forgery of order,
duplication, omission, owners, categories, kinds, capability flags and counts (including
`2.0`/`True`); full-source mutation; ignored annotations and typed-input dispositions
equal to V53; stage resource refusals retaining V53; category-3 stationary and
category-4 dispositions; and the frozen corpus rerun.

## Frozen admitted-source corpus rerun

`pb00701-finite-owner-corpus-v54.json` was produced without changing any historical
code: the source argument of V7's `analyze_coupled_bspline_event` was captured while
running every historical `verify_pb00701*.py --self-test` (v6–v53, all PASS), giving 467
unique admitted original B-spline sources. The corpus keeps the fastest source for each
observed (owner, route status) pair (47 HARVESTED cases) plus COMPOSITE_TAIL sources that
append an exactly continuous constant (`tail0`) or steep harmonic-zero (`tail100`) original
piece to one single-span source per owner. Four composites slower than 30 s (V14, V15, V16 and
V18-Laurent constant tails, 88–647 s) were dropped for CI budget; 121
cases remain. Each case freezes its observed per-span owners/status/reason and its complete
V54 disposition; the test reruns all of them through the complete predecessor chain.

Observed owners: 42 of the 43 static identifiers — all 5 category-1, all 20 category-2, all
16 category-3 and V44 from category 4. `PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY` is reachable
only statically: every historical residual-boundary span in the corpus is re-owned by a later
version (typically as a BLOCKED V43 route). Adapter fixtures cover root-free, endpoint-root
and one-open-root shapes for V20, V22–V25 and every other strict owner's observed shapes.

Complete V54 dispositions over the 121 cases:

| Disposition | Cases | Meaning |
|---|---|---|
| `FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED` | 26 | new V54 compositions (SIGN_SPAN and/or OWNER_STRICT_SPAN with V51/V53 views) |
| `MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED` | 5 | V53 result returned unchanged |
| `CERTIFIED` | 40 | single-span sources; predecessor disposition unchanged |
| `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE` | 30 | a category-3 span (mostly a V6 constant tail) — missing premise, not a missing adapter |
| `BLOCKED` | 20 | complete physical chain itself blocked; returned unchanged |

Nineteen category-2 owners compose on an original multi-span source inside the corpus (each
strict owner with a V19 `tail100` neighbour; dominance with dominance, V19, V47, V49, V50 and
V20). V21's composite (`OWNER_STRICT_SPAN` + V19 `STRICT_SPAN`, built the same way from its
harvested span) also certified locally but took 238 s, so it is recorded here and excluded
from the CI corpus; V21's single-span adapter is still exercised by the direct tests.

Uncertified span reasons behind the 20 blocked cases: 11
`V43 CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED`, 5 V27 child failures, one each of V23
anchor not certified, V41 child not composable, V44 consumption authority missing and V6
identity-zero semantics. The observed residual lacks a successful complete derivative/anchor certificate
and a usable common-factor reduction in the implemented routes. Failure to
certify strict monotonicity is NOT a proof of nonmonotonicity. This motivates
investigation of the broader noncommon-factor/nonmonotone analytic family, not
a claim that the observed source is mathematically nonmonotone and not an
ordering-interface gap.

## Recorded negative attempts and corrections

- Static `grep` for owner emitters first found 41 identifiers: V11 and V40 assign
  `route_kind` across multiple lines. The inventory therefore uses an AST walk.
- An exact zero count plus nonzero endpoints would imply constant sign by continuity;
  V54 deliberately does **not** use that for category-3 owners, because the issue
  forbids promoting counts to order and the owners' proofs do not state it.
- V27/V41 children are often category-2 owners. Ordering them would require a nested
  child-composition interface (child views, child maps, internal-cut one-sided orders);
  their own proofs are count summaries, so they stay category 3 rather than being
  adapted by re-classifying children.
- V13–V17 multipliers have a determinable sign (`|lambda|>1` etc.), but their carriers
  are V10/V11/V12 (category 3) in every implemented delegation, so no ordered view exists.

## Verification and remaining boundary

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v54.py --contract --self-test --acceptance
```

The contract pins all reused V53 artifacts and every adapted owner recipe module by
Git blob, checks the inventory and corpus artifacts, forbids classifier/builder calls
in the checker, floats and external numeric libraries, and requires the single focused
workflow. `--acceptance` runs the principal source and the full unchanged V53
verifier exactly once. Required landing evidence (exact-head focused and `mc1-static`,
guarded merge, main/parent/tree verification and merged-main checks) belongs to the
#275/#100 ledger.

The first genuine remaining PB-007-01 mathematical family is general noncommon-factor,
nonmonotone analytic event coverage (`BOUNDED_POLYNOMIAL_TRIGONOMETRIC_EXPONENTIAL_ZERO_PROBLEM`
behind `PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY`). It is routed as a theorem task in
the evidence/current-state handoff; no adapter issue is created automatically.

PB-007-01 remains globally OPEN; PB-007-02 dependent; PB-007-03 OPEN; PB-007-04
OPEN_PROPAGATED; PO-02/04/05/07/08 open. MC-B/MC-1 NOT_ESTABLISHED. All 26 operations
and source/audio/provenance, canonical journal, exact time/path/phase, uncertainty,
positive-volume material, cutter/holder, durable body/lineage, refusal/UNCERTIFIED and
conventional STEP semantics are unchanged. This is not a derivative or monotonicity
theorem for SIGN_SPAN owners, not a general solver, not native topology/material
evidence and not an MC-B retry.
