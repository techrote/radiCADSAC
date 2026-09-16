# DR-0008 — Journal history uses immutable revisions with explicit material-body transitions

Status: accepted  
Date: 2026-09-16  
Decision scope: canonical journal history and body identity hooks

## Context

MSAC requires undo/redo, branching, backend replay and future body-provenance research. Machining can also split one connected material body into several or, in future processes, merge bodies. A singular latest-solid model would either destroy history or silently lose separated material.

The detailed face/edge ancestry problem belongs to RCS-008, so RCS-002 needs durable hooks without pretending transient topology IDs are stable.

## Decision

`msac-journal/1.0` uses an immutable single-parent workpiece revision graph.

- Committing an operation creates a new child revision.
- Undo/redo moves a mutable UI/history reference rather than deleting/reversing journal records.
- New work from an older revision creates a branch.
- Automatic merging of divergent manufacturing-history branches is not part of version 1.

Every connected material body at a committed revision has a durable journal-level `body_id` independent of backend object identity.

When connectivity changes, the commit records an explicit `material_body_transition` containing the causal operation, input body IDs, output body IDs, transition kind and optional retention/classification state.

Output body IDs become durable journal identities at commit time. Future backend replay must map realized bodies to those expected identities or report an explicit ambiguity/divergence; it may not silently discard or rename material.

## Alternatives considered

### Mutable linear history

Rejected because undo/branching would rewrite or discard manufacturing evidence.

### Persist backend solid/topology IDs as durable body identity

Rejected because those identifiers are backend/version specific and may change during regeneration.

### Infer body identity afresh on every replay without journal records

Rejected because cross-version replay could silently attach later operations to a different disconnected component.

### Solve full topological naming in RCS-002

Rejected as unnecessary scope expansion. RCS-008 owns detailed ancestry and topology naming research.

## Evidence

RCS-001 explicitly requires undo/redo, backend-independent history, and non-silent handling of disconnected material bodies. A durable body transition record is the minimum journal-level mechanism that lets later provenance research and export policy refer to those states without private kernel IDs.

## Consequences

- RCS-003 fixtures can state expected body connectivity and identity transitions.
- RCS-005 can define export selection/product structure against durable bodies rather than transient solids.
- RCS-008 receives stable journal-level hooks but remains free to research backend ancestry/mapping algorithms.
- Snapshots/caches are safely keyed to immutable revision IDs.
- Detached material remains explicit until a later user/policy operation classifies or removes it.

## Reversibility

Low for the requirement to preserve immutable history and explicit body transitions; medium for the exact revision/body record structure. A future major journal version may generalize parentage or identity fields through explicit migration.

## Reconsideration trigger

Reconsider the exact body-transition structure if RCS-008 demonstrates that committed bodies cannot be mapped robustly enough for replay, or if additive/multi-workpiece processes require a richer many-to-many material identity model. Any replacement must still prevent silent body loss and private-kernel identity leakage.
