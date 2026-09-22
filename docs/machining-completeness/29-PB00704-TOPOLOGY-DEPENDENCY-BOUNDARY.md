# PB-007-04 topology/connectivity dependency boundary

This note records the bounded constructive result from corrective issue #168. It extends the MC-038 blocker evidence without rewriting the historical MC-007, MC-032, MC-033 or MC-038 results.

## Authority boundary

`PB-007-04` is the universal exact topology/connectivity obligation. It remains **OPEN_PROPAGATED**. PO-07 remains **OPEN**, and MC-B remains `NOT_ESTABLISHED`.

A bounded part is now executable: a complete finite material partition that has already been independently certified and is represented as exact-rational positive-volume axis-aligned cells can be checked for connectivity exactly. This is useful certificate infrastructure, but it is not a universal partition generator and does not establish unknown material geometry.

The checker requires source, material, event, configuration, frame and revision binding, plus an external partition-completeness certificate. It deliberately refuses to infer completeness from its own cells.

## Connectivity semantics

For the bounded route, two exact positive-volume cells are connected only by an exact shared face with strictly positive overlap along the other two axes. Edge-only or point-only contact is `TOUCH_ONLY`; it does not connect positive-volume material interiors. Pairwise positive-volume interior overlap invalidates the purported partition.

This matches the protected material semantics used by MC-032/MC-033: touching is not positive-volume material removal or a durable-body merge, and backend topology identifiers are not programme identity.

An exact `1/1000000` bridge and an exact `1/1000000` gap are explicit regression boundaries. No epsilon, tolerance, refinement depth or binary floating point may replace those exact relations.

## Certificate identity

The bounded certificate is canonically bound to:

- common frame;
- source digest;
- material digest;
- event digest;
- configuration digest;
- revision;
- exact canonical cell partition;
- independent completeness-certificate digest.

Certificate-local cells/components are evidence objects only. They do not become `body_id` or `lineage_id`, and component order, volume rank, proximity or provider/kernel identity is forbidden as identity authority.

## Residual universal dependency

Universal PB-007-04 closure is not independently available while its material/event inputs are unresolved. `PB-007-01` still owns general nontransversal analytic-event authority. `PB-007-02` still owns general coupled sweep/material membership and depends on PB-007-01. `PB-007-03` still owns universal exact source representation beyond its bounded rational-semialgebraic sublanguage. PO-02 and PO-04 therefore remain open for the universal source/sweep/classification premises needed to generate a complete topology partition for every admitted material state.

Accordingly, the bounded checker cannot be promoted into a universal topology theorem. This is not an impossibility result: later exact source/event/material constructions may make the universal topology-generation problem dependency-ready.

The canonical global PO DAG is not rewritten by this dependency review. In particular, downstream PO-03/PO-06/PO-09 and RB-016-01..05 remain open where existing evidence says open, but they are not recast as MC-B prerequisites.

## Protected semantics and execution

The frozen 26-operation domain is unchanged. Historical source/audio/provenance, canonical-journal meaning, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP engineering-output semantics remain unchanged. No native, paid, production or expensive execution is authorized by this follow-up.

## Verification

The repository verifier is `research/machining-completeness/tasks/MC-038/verify_pb00704.py`; the model is `pb00704_topology_checker.py`, and the machine-readable decision artifact is `pb00704-topology-dependency-v5.json`. `mc1-static` runs both contract and adversarial self-tests.
