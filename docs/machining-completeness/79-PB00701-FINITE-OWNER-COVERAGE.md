# PB-007-01 v54 — finite historical-owner inventory and ordered-span adapters

Date: 18 October 2026. Issue: [#275](https://github.com/techrote/radiCADSAC/issues/275).
Evidence: DETERMINISTIC_MODEL. Programme: MC-B/MC-1 NOT_ESTABLISHED.
This is a bounded exact event-composition result, not native material or STEP qualification.
The verified landing ledger, rather than this document's existence, controls status.

## Purpose and predecessor boundary

V53 ([78-PB00701-MIXED-OWNER-SPANS.md](78-PB00701-MIXED-OWNER-SPANS.md)) composes
original-source B-spline spans across proved-continuous knots when every span
carries either a checked `V51_PRODUCT` view or a checked `STRICT_SPAN` view for the
V19/V47/V48/V49 owners. Any other actual owner stops at
`SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE`. The principal example is the reversed V53
acceptance source: its root-free piece is owned by the oldest V7 route,
`EXACT_RATIONAL_AMPLITUDE_DOMINANCE`, which V53 deliberately refused to relabel.

V54 answers a bounded question: across the finite set of implemented historical
owner families, which owners' **actual proof objects** already justify an ordered
span view, and which do not? It then implements every justified view and records a
precise negative classification for the rest. V54 does not search for new proofs,
does not change any historical module and does not re-own any span.

## Definitions

- **Owner**: the literal `route_kind` identifier a historical classifier assigns to a
  lowered source span. It is the identity of the proof that certified the span.
- **Ordered span view**: a source-bound record of ordered boundary points, physical
  events (roots), one-sided neighborhood signs and open sign cells on one smooth span,
  as consumed by the unchanged V52 knot/root/sign-cell composition.
- **SIGN_SPAN**: a new V54 view kind for a closed span with a proved strict nonzero
  sign everywhere, including both endpoints. It carries no root and **is not a
  derivative certificate** and claims no monotonicity.
- **OWNER_STRICT_SPAN**: a new V54 view kind for an owner whose own route proves a
  strict nonzero complete derivative on the whole closed span. It is distinct from
  V53's `STRICT_SPAN` and keeps the actual owner and an owner-specific adapter name.
- **Owner recipe**: the owner's own fixed route builder (for example
  `_pointwise_envelope_route`) called on the original lowered span. Regenerating it is
  finite checking; calling a classifier would be proof selection and is forbidden.

## Finite owner inventory

`pb00701_finite_owner_inventory.py` enumerates owners two independent ways, and
both must agree with one canonical table in `pb00701_finite_owner_span_model.py`:

1. **Static**: every literal string assigned to a `route_kind` name or
   `['route_kind']` subscript in the implemented `pb00701_*` modules (AST parse). This
   finds exactly 43 identifiers.
2. **Observed**: a frozen admitted-source corpus is rerun through the complete
   unchanged predecessor chain and every observed span owner is looked up.

Every owner has exactly one category (`pb00701-finite-owner-inventory-v54.json`):

| Category | Meaning | Owners |
|---|---|---|
| 1 | Already-supported ordered view | V50 product (via V51), V19, V47, V48, V49 |
| 2 | Actual proof justifies a checked ordered view; V54 adapter implemented | V7 amplitude dominance (`SIGN_SPAN`); V20–V26, V28–V30, V34–V40, V42, V43 (`OWNER_STRICT_SPAN`) |
| 3 | Exact owner lacking an ordered-span premise (named precisely) | V7 stationary polynomial, V6 delegated constant modulation, V8–V17, both V18 kinds, V27, V41 |
| 4 | Blocker / refusal / non-event disposition | V7 general coupled theorem boundary, V44 orientation-cut boundary |

Counts are 5 / 20 / 16 / 2. An unknown identifier would be refused as
`SPAN_OWNER_OUTSIDE_FINITE_V54_INVENTORY`; no owner can be in two categories.

## Category 2a: amplitude dominance as a root-free SIGN_SPAN

V7's certificate on a normalized span `s in [0,1]` uses only exact rational
coefficients. With `a0` the constant coefficient of the harmonic-zero cosine
amplitude, it requires

```text
margin = |a0| - sum(|other harmonic-0 coefficients|) - sum(|all oscillatory coefficients|) > 0
```

Because `|s^k| <= 1` and every cosine/sine factor is bounded by one, the complete
physical field satisfies `sign(F(s)) = sign(a0)` and `|F(s)| >= margin` for **every**
`s` in the closed span. V54 regenerates the certificate from the original span with
V7's own `_dominance_certificate`, requires byte-identical equality, and emits one
open sign cell plus two NONZERO exteriors whose physical relation is the proved sign
and whose inward sign equals it. The endpoint relation authority is recorded as
`CLOSED_SPAN_EXACT_AMPLITUDE_DOMINANCE`.

A justified boundary-root case is **impossible** for this owner: a positive margin on
the closed span excludes a zero endpoint. Forged ZERO exteriors are rejected. This
constant-sign theorem is a root-free sign span, not a derivative certificate; no
direction, monotonicity or V19/V50 identity is attached.

## Category 2b: whole-span strict derivative owners

Nineteen owners (V20–V26, V28–V30, V34–V40, V42, V43) all build their CERTIFIED route
the same way: an owner-specific certificate proves the complete source derivative has
a strict nonzero sign throughout the closed span, the route records exact endpoint
events via V19's rational-turn evaluator, and `v19._root_summary(direction, ...)`
derives the root summary. Their routes say so explicitly (for example "the complete
derivative never vanishes, so every admitted root is simple").

For each, V54 records the owner's module, recipe and the route key holding the
`direction` (`derivative_certificate` for V20/V21; the owner-named anchor
certificate otherwise). Checking regenerates the route with that recipe on the
original span, requires equality, reads `delta` from that certificate, and takes the
exterior relations from the route's own exact `left_event`/`right_event`. The ordered
construction is the V53 strict one: a zero left endpoint has inward sign `delta`, a
zero right endpoint `-delta`; opposite signs give one implicit simple root with cells
`(-delta, delta)`; both endpoints zero is impossible. All three shapes (root-free,
endpoint root, one open root) occur in actual corpus instances.

## Category 3: exact owners lacking an ordered premise

These owners certify exact events but their proof objects do not contain an ordered
physical root sequence or whole-span sign authority. V54 never promotes a count or a
delegated zero set to order:

- **V7 stationary polynomial** — root counts and endpoint events only; no ordered
  isolation or per-root multiplicity.
- **V6 delegated constant modulation** — tan-half turn-window counts only.
- **V8 common factor** — factor and per-chart trigonometric counts with coincidence
  checks; no cross-factor order or sign cells.
- **V9/V10/V11** — monotonicity of an auxiliary tangent/cotangent ratio on each
  pole-safe chart; no physical sign transfer or cross-chart order.
- **V12** — partition cells decided by V9/V10 and composed by counts.
- **V13–V17** — nonvanishing multiplier zero-set equivalence over a V10/V11/V12 carrier
  (itself category 3); no physical sign transfer.
- **V18 (both kinds)** — residual delegated through the full V17 classifier; the
  Laurent kind also records no factor sign.
- **V27/V41** — children re-classified by the full predecessor classifier and composed
  only by count summaries; no ordered child composition.

These are distinct from missing adapters: a category-3 view would need a new ordered
isolation or nested-composition theorem, not a check of an existing proof.

## Category 4: dispositions

`PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY` is the residual blocker for nonconstant
modulation with nonzero phase; V44's route is always a BLOCKED consumption boundary.
Sources containing them never reach V53/V54 composition; the complete predecessor
result is returned unchanged.

## Composition, finite checking and refusal discipline

`build_finite_owner_source_evidence(original_spec)` runs complete V53 first. Any V53
success, all-product V52 success, blocker, refusal or single-span disposition is
returned unchanged. Only `SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE` enters the new scope;
V54 then rebuilds views for every span (V53 kinds through the unchanged V53 builder)
and feeds them to V52's unchanged exact knot continuity, one-sided order, root union
and maximal-cell formulas. A shared zero knot keeps two one-sided orders; no global
analytic multiplicity is invented at a nonsmooth knot.

`pb00701_finite_owner_span_certificate.py` checks V53 kinds through the V53 checker and
new kinds by owner-recipe regeneration plus whole-record equality, then regenerates
lowering, joins and composition. Tests disable every loaded classifier, builder,
carrier/residual delegate, derivative selector and sign search while checking. Memory,
overflow and recursion failures are non-truth refusals retaining the V53 predecessor;
unrelated exceptions propagate.

## Executed examples

The issue #275 principal source is `reverse_source` of the V53 acceptance source
(global `u in [0,2]`). V53 blocks at span 0 with owner amplitude dominance, margin
`97/200`. V54 certifies `SIGN_SPAN` (positive) beside the retained V50/V51 product:
two open roots (one simple crossing, one double tangency), exact POSITIVE knot
coalesced into the first maximal cell, maximal signs `(+,+,-)` — exactly the
reversal of V53's forward `(-,+,+)`.

Further original-source controls: V19 strict + dominance; all-dominance; a four-piece
`SIGN(-) | PRODUCT | STRICT | SIGN(+)` source; owner-strict adapters composed on
corpus sources; repeated/different knots and degrees; exact continuity versus a
`1/10^30` jump; non-unit affine maps, reversal and negation; forged owners, routes,
endpoints, directions and monotonicity fields; missing/duplicate/reordered views;
source/phase/harmonic/identity mutation; boolean/float/unknown inputs; and category-3/4
dispositions.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v54.py --contract --self-test --acceptance
```

## Next mathematical frontier

`pb00701-finite-owner-corpus-v54.json` freezes 121 admitted original sources captured
from every historical verifier run (plus continuous-tail composites). It observes 42 of the
43 owners; the general coupled boundary is static-only because later versions re-own every
such corpus span. Rerunning it after all category-2 adapters gives 26 new V54
certificates, 5 preserved V53 results, 40 single-span certificates, 30 category-3 premise
gaps and 20 unchanged blocked chains — 11 of those on
`V43 CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED` nonmonotone, noncommon-factor spans. The first genuine
remaining PB-007-01 family is **general noncommon-factor/nonmonotone analytic event
coverage** (the `BOUNDED_POLYNOMIAL_TRIGONOMETRIC_EXPONENTIAL_ZERO_PROBLEM` behind the
general coupled boundary). It is routed as a theorem task in the evidence/current-state
handoff; V54 creates no automatic adapter issue. Ordered root isolation for count-only
category-3 owners is a secondary frontier.

## Implications and programme boundaries

OpenSimachinist gains a wider bounded exact original-source event-composition
primitive; no native material realization or topology transition follows. MSAC's
interaction, canonical journal and saved intent do not change.

PB-007-01 remains globally OPEN; PB-007-02 dependent; PB-007-03 OPEN; PB-007-04
OPEN_PROPAGATED; PO-02/04/05/07/08 remain open. MC-B/MC-1 NOT_ESTABLISHED; no MC-B retry
is implied. All 26 operations and source/audio/provenance, canonical journal, exact
time/path/phase, uncertainty, positive-volume material, cutter/holder, durable
body/lineage, refusal/UNCERTIFIED and conventional STEP semantics are retained. No
native, paid, production or expensive campaign, shared-registry or settings change is
authorized by this result.
