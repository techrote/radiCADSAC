# RCS-018 — integrated semantic contract vertical slice

This directory contains the smallest executable research harness needed to test whether the accepted Genesis-v1 semantic contracts compose. It is deliberately **not** a production scheduler, RPC service, persistence layer, UI, or geometry kernel.

## Reproduce

From repository root:

```bash
python3 research/rcs-018/vertical_slice.py --output /tmp/rcs018-evidence.json
python3 tools/validate_rcs018.py
```

The harness uses only Python's standard library. It consumes the accepted RCS-002 lathe and mill fixtures. Geometry-provider decisions are represented by process-isolated adapters that point to the accepted RCS-010/RCS-011 measured evidence rather than pretending this integration spike re-proves geometry.

## Evidence model

`experiment-plan-v1.json` states the hypotheses, falsification rules, fixtures, metrics and negative controls before interpretation. `evidence-schema-v1.json` fixes the reusable trace envelope for RCS-025/RCS-026.

A run emits two scenarios:

- `lathe`: canonical setup/turning operations, process-isolated provider adapter, immutable commits, replay/discard/rebuild, and STEP handoff;
- `mill_body_split`: canonical `milling.general`, explicit `accepted_pending` → `reconciled` → commit/success, two-body split lineage, replay, and STEP handoff.

Both scenarios inject provider error, crash and timeout before the successful attempt and prove the durable authority digest does not change.

## STEP boundary

RCS-018 does not create new STEP geometry evidence. Layer A semantic preconditions are evaluated by this slice. Layers B/C point to the already accepted automated RCS-006/RCS-010/RCS-011 profile evidence. Layer D remains `interoperability_unqualified` until RCS-022 qualifies the exact exporter profile independently.

## Durable versus derived state

Durable evidence contains only journal schema, project/workpiece IDs, immutable operation context, revisions, material-body transitions and semantic-lineage relations. Provider profile names and worker diagnostics are execution evidence; process IDs, kernel handles, `TopoDS_*`, Godot object identity and provider-private topology identity are forbidden from durable state.

`tools/validate_rcs018.py` runs the slice twice, checks deterministic equality, and adds adversarial guards for private-ID leakage, duplicate body IDs, unresolved STEP reconciliation, invalid body selection and worker fault containment.
