# PB-007-03 follow-up — exact source codec boundary for imported/form/undercut solids

Issue: #166  
Parent integration gate: MC-038 / #100  
Source baseline: `c762ba3a7c5ceff81e7c8ec2f5c37c21e1aa758c`  
Disposition: **bounded exact source codec established; PB-007-03 remains OPEN**  
Native/paid execution: **none**

## Purpose

This follow-up executes the next independently dependency-ready pre-gate branch after the PB-007-01 bounded exact-event investigation. PB-007-02 remains live, but its general coupled membership boundary/equality decisions still consume the unresolved PB-007-01 analytic-event authority; this pass therefore moves to the independent source-representation branch rather than pretending another membership implementation can erase that dependency.

The target is the source-side gap propagated from MC-006 and MC-020 through MC-031: MC-002 admits imported stock and arbitrary form/nonconvex/accessible-undercut cutter instances, while the existing executable exact form/undercut route covers only a bounded rational box-union subtype. The repair establishes a materially richer exact source language without redefining the admitted domain to fit the implementation.

## Preserved authority

The versioned machine record pins MC-002 domain authority, MC-003 numeric authority, MC-006 exact-semialgebraic research, MC-020 bounded form/undercut construction, MC-031 material integration, MC-038 v2 gate routing and the PB-007-01 v3 follow-up by Git blob identity. Those artifacts remain historical inputs. In particular:

- MC-002's missing-constructor-is-gap rule remains authoritative;
- `imported_stock` remains an admitted bounded closed/oriented imported source with explicit representation and source-uncertainty contract; import success alone is not validity;
- arbitrary `lathe_form_tool`, `mill_form` and `mill_accessible_undercut` sources are not retrospectively defined to mean box unions or rational semialgebraic solids;
- MC-003 exact scalar/curve/time encodings do not themselves manufacture an exact universal solid/import codec;
- MC-020's box-union result remains a bounded result, not a universal-source theorem.

The frozen **26-operation denominator** remains exactly 26 operations.

## Exact bounded source language

`pb00703_source_codec.py` implements `radicadsac-exact-semialgebraic-source/1.0`. A source binds:

- a durable `source_id`;
- an explicit `stock`, `cutting` or `holder` role;
- units and common `frame_id`;
- finite exact rational X/Y/Z source bounds;
- an explicit source uncertainty quantity separate from nominal geometry;
- a finite exact solid-expression tree.

The exact solid grammar contains rational-polynomial `<= 0` and `>= 0` atoms over `(x,y,z)`, finite union/intersection, ordered difference and complement inside the explicit finite source bound. Polynomial coefficients are exact rationals only. Like polynomial monomials are combined and sorted; union/intersection children are canonically ordered; noncommutative difference is not reordered. The normalized source is serialized to canonical JSON bytes and SHA-256 bound, including source identity, role, units, frame, bounds, solid and source uncertainty.

This is nominal-source exactness. It deliberately keeps measurement/import uncertainty separate. A source with nonzero `source_uncertainty` may still have an exact nominal expression, but `classify_certifying_point` returns `UNCERTIFIED_SOURCE` rather than promoting that nominal expression to exact material truth. Downstream enclosure/error work must carry that uncertainty.

## Boundary and adversarial controls

The deterministic verifier exercises:

- an exact rational box, including interior, exterior and exact equality;
- an exact unit-sphere quadric at `x=1` and signed `1/1000000` neighbours;
- a nonconvex L-shaped Boolean cutter whose reentrant missing quadrant must remain missing rather than becoming a hull/AABB fill;
- a positive-volume cube of exact width `1/1000000`, including interior, exact face equality and an exterior signed neighbour;
- explicit cutting/holder separation in one common units/frame binding, with access still **not** inferred merely from source validity;
- canonical hashing invariant to commutative Boolean-child order and polynomial-term order, while remaining sensitive to durable source identity;
- nonzero source uncertainty refusing certifying exactness while retaining exact nominal classification.

Adversarial controls reject binary-float coefficients and point coordinates, missing units/frame/source identity, absent finite bounds, holder-role erasure, malformed/unreviewed solid grammar and opaque STEP/B-rep/NURBS/mesh/AABB descriptors as exact source authority. Kernel/import/manifold success is not a source codec certificate. Tessellation, convex hull and AABB substitution do not become equality by convenience or tolerance.

Exact atom equality is reported conservatively as `BOUNDARY_CANDIDATE`. The codec does not infer universal topological boundary/connectivity from a Boolean expression merely because one atom is exactly zero; that would pre-empt the still-open topology proof branch.

## Why PB-007-03 remains open

The new source language is a real exact construction, but it is still a **sublanguage**. MC-002 intentionally admits imported stock and arbitrary form/undercut sources through explicit representation and uncertainty contracts and says a missing constructor is a gap, not automatic exclusion. Nothing in the current authority proves that every valid imported source or every arbitrary form/undercut cutter admits a finite rational-semialgebraic lowering.

Restricting `imported_stock`, `lathe_form_tool`, `mill_form` or `mill_accessible_undercut` to this codec would therefore shrink the frozen domain to match available machinery. Accepting an opaque STEP/NURBS/B-rep import as exact merely because a kernel parses or validates it would commit the opposite error: it would replace a missing source theorem/certificate with backend success.

The residual obligation is explicit: provide a universal finite source representation/lowering and certificate route for every admitted imported-stock and arbitrary form/undercut source instance, **or** make a separately reviewed prospective product-domain decision that changes what is admitted without rewriting prior evidence. This follow-up proves neither an impossibility theorem nor universal coverage.

Therefore `PB-007-03` remains **OPEN**. PO-02 and PO-05 remain **OPEN**. PB-007-01 remains OPEN; PB-007-02 remains OPEN and dependent on the unresolved general analytic event route; PB-007-04 remains propagated. MC-B and MC-1 remain `NOT_ESTABLISHED`.

## Protected semantics

Historical source/audio/provenance and canonical-journal meaning are unchanged. Source uncertainty is not collapsed into nominal exactness. Positive-volume material, including the exact `1/1000000` feature, remains material. Cutting and holder/non-cutting geometry remain distinct and access/clearance remains a separate witness obligation. Durable body/lineage identity remains programme-owned. Conventional STEP remains an engineering-output requirement downstream; this source codec is not a STEP qualification result and must not be used to launder mesh-wrapped or opaque output as success.

No native, paid, production or expensive campaign is authorized or run. `BLOCKED`, `UNCERTIFIED_SOURCE`, resource refusal, opaque import and malformed source remain non-success outcomes.

## Verification

The follow-up is checked independently and is wired into `mc1-static`:

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00703.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00703.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify.py --contract
python3 research/machining-completeness/tasks/MC-038/verify.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

Exact-head `mc1-static` is required before merge and the exact merged `main` SHA must pass the independent push run afterward.

## Routing after this repair

The next pre-gate action is a dependency review of PB-007-04, not an MC-B acceptance retry. PB-007-04 must remain open if universal topology/connectivity certification still depends on unresolved source representation or exact event authority. If no independent constructive branch remains after that review, MC-038 stays blocked rather than manufacturing acceptance from bounded subroutes.
