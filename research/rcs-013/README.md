# RCS-013 architecture synthesis

Status: accepted Gate-2 research output  
Date: 2026-09-17

RCS-013 synthesizes RCS-005 and RCS-007–RCS-012 into the initial OpenSimachinist architecture. It is an architecture/research result, not production kernel code.

## Durable artifacts

- `../../docs/20-OPENSIMACHINIST-ARCHITECTURE-SYNTHESIS.md` — full evidence-backed trade study and Gate-2 assessment.
- `architecture-v1.json` — machine-readable selected component/API/dispatch/reconciliation/status/versioning contract.
- `unresolved-v1.json` — ranked unresolved research/implementation register with safe current policies.
- `../../docs/decisions/DR-0015-gate-2-semantic-provider-hybrid-architecture.md` — accepted Gate-2 decision.

## Selected architecture

`semantic-provider-hybrid-v1` keeps manufacturing intent, immutable workpiece/material-body revisions, semantic lineage and versioned policies programme-owned. Process-specialized lathe/mill providers, OCCT B-rep state, deferred material ledgers, preview geometry and local fallback representations remain derived/replaceable.

OCCT 8.0.1 is retained as the initial isolated B-rep/validation/reconciliation/STEP baseline, not as durable project ontology. Fixed-axis turning uses the qualified axisymmetric provider. Milling uses the measured strategy hierarchy and explicitly rejects unproven freehand batching/dense sampled-pose B-rep replay as universal fallbacks. Bounded alternative representations may exist locally only under explicit error/scope contracts and must reconcile before STEP success.

## Gate-2 result

The roadmap's required evidence now exists for the pinned baseline, tolerance/provenance, lathe specialization, mill strategy, alternative/hybrid representation and STEP conformance. Gate 2 is therefore accepted without claiming universal computational-geometry completeness.

RCS-017 remains open and may refine OCCT concurrency deployment. Until measured otherwise, process-isolated geometry/STEP workers with timeouts are the accepted safe default.

## Validation

Run:

```text
python3 tools/validate_rcs013.py
```

The validator checks the selected architecture, evidence links, programme/API boundaries, status/tolerance/dispatch/reconciliation contracts, ranked unresolved register, synthesis report and Gate-2 decision record.
