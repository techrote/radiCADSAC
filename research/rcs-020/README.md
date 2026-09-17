# RCS-020 — realistic lathe tool-envelope qualification

Status: research candidate pending hosted measured campaign  
Issue: RCS-020 / GitHub #39  
Plan schema: `rcs-020-lathe-tool-envelope-plan/1.0`

## Purpose

RCS-010 demonstrated that a 2D axial/radial material domain can reconstruct a useful fixed-axis lathe subset efficiently and with good STEP Layer A-C behavior, but that campaign began from an oracle-derived completed material profile. RCS-020 tests the missing upstream seam: deriving that material profile from immutable tool geometry, tool orientation/approach, canonical tool-centre trajectories and explicit reachability rules.

This directory is research infrastructure, not the production tool library.

## What is being tested

The campaign includes:

- an abstract external turning insert with a 0.8 mm circular nose and representative 95°/45° approach configurations;
- radiused OD, facing, shoulder, taper and exact-retrace paths;
- a 0.4 mm nose internal boring tool with through/blind cases;
- a 2.0 mm grooving/parting tool with 0.2 mm left/right corner radii;
- complete parting with explicit two-body semantics;
- a holder-clearance undercut case that must fail closed rather than be approximated into the axisymmetric provider.

The numerical tool dimensions are seeded from current primary manufacturer training/catalogue material recorded in `experiment-plan-v1.json`. They are abstract research definitions, not a dependency on one commercial insert catalogue.

## Independent material evidence

`tool_envelope.py` intentionally separates two calculation paths:

1. the candidate generator polygonizes the Minkowski capsule of the circular nose swept along canonical line segments and derives a bounded radial material profile;
2. the oracle independently computes closed-form vertical intersections of exact segment-plus-disc capsules and integrates material at a much finer spatial step.

Grooving uses the same independence discipline: the candidate constructs quarter-circle corner geometry while the oracle evaluates a separately coded analytic radius function.

The RCS-010 OCCT worker is downstream comparison evidence, not the physical oracle.

## STEP scope

Qualified one-body cases are passed to the accepted RCS-010 worker for repeated-3D, batched-3D and axisymmetric reconstruction plus automated STEP Layer A-C read-back. Complete parting additionally uses the RCS-006 multi-solid parting worker as an all-bodies connectivity/STEP control.

The candidate adapter supplies polygonized radial profiles to RCS-010. Therefore this issue does **not** infer exact toroidal/circular-insert-nose analytic-surface preservation from successful STEP output. Geometry/material fidelity can pass while exact nose-surface reconstruction remains a separate capability boundary.

## Reproduction

Static contract check:

```text
python3 tools/validate_rcs020.py
```

Research-only material derivation without OCCT:

```text
python3 research/rcs-020/run_campaign.py --out-dir .results/rcs020-material-only
```

The hosted measured workflow additionally builds the pinned OCCT 8.0.1 RCS-010 and RCS-006 workers, runs:

```text
python3 research/rcs-020/run_campaign.py \
  --lathe-worker .build/rcs010/rcs010_lathe_worker \
  --baseline-worker .build/rcs006/rcs006_occt_worker \
  --out-dir .results/rcs020
python3 tools/validate_rcs020.py --results-dir .results/rcs020
```

## Expected research outcome

A positive result refines DR-0013 from “axisymmetric material solver qualified after an oracle envelope” to a bounded capability whose envelopes can be derived from explicit realistic tool semantics. A negative result is equally useful when it narrows the provider predicate or demonstrates an operation that must hand off/refuse.

No result may silently widen tolerance, discard a separated body, ignore a holder collision, or claim analytic STEP fidelity not actually measured.
