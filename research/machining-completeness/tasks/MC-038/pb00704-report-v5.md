# PB-007-04 follow-up — topology/connectivity dependency boundary

## Result

This follow-up establishes a bounded exact connectivity checker but **does not close `PB-007-04`**. The universal topology/connectivity obligation remains `OPEN_PROPAGATED`, and PO-07 remains OPEN.

The dependency review confirms that MC-032 and MC-033 had already drawn the correct authority boundary. MC-032 may consume independently certified connectivity evidence but does not manufacture it from tolerance, kernel topology, or touching. MC-033 may apply durable `CONTINUE`, `SPLIT`, `DISAPPEAR`, and `TOUCH_ONLY` transitions once a complete independently proved material partition/connectivity certificate exists, but it does not generate the universal partition itself.

The independently constructive portion is therefore narrower: when a producer supplies an independently certified complete finite partition of one material state into exact-rational positive-volume axis-aligned cells, connectivity of that finite partition is exactly decidable. This checker is a certificate consumer/checker, not a universal topology generator.

## Exact bounded route

`pb00704_topology_checker.py` accepts only a finite partition bound to one common `frame_id`, exact source/material/event/configuration digests and an explicit revision. Every cell has exact-rational finite bounds and strictly positive extent in x/y/z. Partition completeness must be supplied by an external certificate whose authority is explicitly `INDEPENDENT_CERTIFIED_PARTITION`; a bare `complete=true` assertion or self-certification is rejected.

Two cells are connected only when they share exactly one boundary plane and overlap with strictly positive extent in each of the other two axes. This gives exact positive-area face adjacency. Edge-only and point-only contacts are `TOUCH_ONLY` for connectivity purposes and do not connect positive-volume material interiors. A positive-volume interior overlap means the alleged cells are not a partition and fails closed.

The checker builds a deterministic component graph, canonicalizes cell order, supports an independently certified exact-empty partition, and returns a source/material/event/partition-bound SHA-256 certificate. Its component identifiers are certificate-local only. They cannot become durable `body_id` or `lineage_id` authority; MC-033 remains the owner of durable transitions.

## Boundary and adversarial evidence

The deterministic verifier covers:

- exact face adjacency;
- edge-only and point-only contact;
- an exact `1/1000000` positive bridge that changes the result to one component;
- an exact `1/1000000` positive gap that preserves separate components;
- multiple disconnected components and input-order invariance;
- independently certified exact empty material;
- positive-volume interior overlap rejection;
- zero-thickness cell rejection;
- binary-float and scientific/approximate coordinate rejection;
- rejection of backend/kernel/component/body/lineage/enumeration/largest-volume/proximity identity fields;
- rejection of stale source, material, event, configuration, frame or revision bindings;
- rejection of a forged completeness assertion and self-certified completeness.

No epsilon, global tolerance, binary floating point, kernel component ordering or proximity heuristic participates in correctness authority.

## Why PB-007-04 remains open

The bounded checker starts **after** a complete exact material partition has been certified. The full MC-1 domain still lacks unconditional authority for producing that input in every admitted case:

- `PB-007-01` remains OPEN for general tangential/multiple/singular analytic events outside the bounded exact trigonometric-polynomial subroute;
- `PB-007-02` remains OPEN for general coupled sweep/material membership and depends on the unresolved PB-007-01 equality authority;
- `PB-007-03` remains OPEN because the exact-rational semialgebraic source codec does not cover every admitted imported-stock/arbitrary form/undercut source;
- PO-02 and PO-04 therefore remain OPEN for universal sweep/material and classification authority.

Those unresolved inputs can change which material cells exist and where topology-critical boundaries occur. A finite exact component checker cannot turn unknown material/event geometry into a universal topology certificate. This is a dependency result, not an impossibility theorem: future source/event/material constructions may discharge the prerequisites, after which the universal PB-007-04 claim can be revisited.

This result does not change the canonical global PO DAG or reclassify downstream representation/qualification work. PO-03/PO-06/PO-09 and RB-016-01..05 remain real downstream MC-1 obligations, but they are not reintroduced as prerequisites that must close before MC-B.

## Programme effect

`PB-007-01`, `PB-007-02`, `PB-007-03`, and `PB-007-04` remain open in their recorded forms. PO-02, PO-04, PO-05, PO-07 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. There is therefore no MC-B retry from this follow-up.

The frozen 26-operation denominator is unchanged. No source/audio/provenance asset, canonical-journal meaning, source uncertainty, positive-volume material rule, cutter/holder access semantics, durable body/lineage rule, refusal/`UNCERTIFIED` semantics, or conventional STEP engineering-output requirement is weakened. No native, paid, production or expensive campaign is run.

## Verification

- `python3 research/machining-completeness/tasks/MC-038/verify_pb00704.py --contract`
- `python3 research/machining-completeness/tasks/MC-038/verify_pb00704.py --self-test`
- `python3 tools/validate_machining_completeness.py --self-test`
- `python3 tools/mc_workflow.py verify MC-038`
- `python3 tools/mc_workflow.py sync --check`

The exact PR head must pass `mc1-static`. After merge, `mc1-static` must pass independently on the exact merged `main` SHA before corrective issue #168 is closed.
