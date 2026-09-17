# RCS-020 — realistic lathe tool-envelope qualification

Status: **accepted measured research pending merge**  
Issue: RCS-020 / GitHub #39  
Plan schema: `rcs-020-lathe-tool-envelope-plan/1.0`  
Measured summary: `measured-summary-v1.json`

## Purpose

RCS-010 demonstrated that a 2D axial/radial material domain can reconstruct a useful fixed-axis lathe subset, but that campaign began from an already completed material profile. RCS-020 measures the missing upstream seam: deriving that material profile from immutable tool geometry, tool orientation/approach, canonical tool-centre trajectories, and explicit reachability rules.

This directory remains research infrastructure, not the production tool library.

## Accepted measured result

Hosted workflow run `35275577906` completed all ten required cases with the pinned OCCT 8.0.1 baseline. The campaign qualified eight one-body tool-derived material cases, a two-body complete-parting connectivity case, and an explicit holder-collision refusal.

Key results are frozen in `measured-summary-v1.json`:

- maximum one-body tool-profile/oracle volume difference: `0.016463079120512703 mm³` under the predeclared `0.05 mm³` budget;
- 24/24 enabled STEP repeated/batched/axisymmetric Layer A-C round trips passed;
- maximum STEP read-back volume difference: `3.292370820418e-10 mm³`;
- complete rounded parting preserved two material bodies; the independent two-solid STEP control read back two solids;
- exact retrace retained 20 journal events while comparing 20 repeated material Booleans, one batched Boolean, and zero axisymmetric material Booleans;
- the undercut fixture was correctly `refused_unsupported` after measured holder collision.

The accepted result supports a bounded real-tool entry predicate for the RCS-010 axisymmetric provider. It does not qualify general undercut/form tools, live-tool/non-axisymmetric work, or exact circular-nose/toroidal STEP analytic reconstruction from the polygon research adapter.

## Independent material evidence

`tool_envelope.py` separates candidate and oracle paths:

1. the candidate generator polygonizes the Minkowski capsule of the circular nose swept along canonical line segments and derives a bounded radial material profile;
2. the circular-nose oracle independently solves exact vertical capsule intersections and integrates material at finer resolution;
3. rounded groove/parting acceptance uses a separately derived closed-form material integral in `refine_oracles.py`.

The first complete parting run showed why that distinction matters: uniform numerical quadrature across the material discontinuity produced a false `0.3141255 mm³` discrepancy. The closed-form rounded-groove integral showed the candidate was only about `1.89e-05 mm³` away. The old numerical value remains recorded as negative diagnostic evidence; no acceptance budget was widened.

The RCS-010 OCCT worker remains downstream comparison evidence, not the physical oracle.

## Tool/process coverage

The campaign includes:

- abstract external R0.8 circular-nose turning tools at representative 95° and 45° approach configurations;
- OD, facing, shoulder, taper, and 20-event exact retrace;
- an R0.4 internal boring tool with through and blind cases;
- a 2.0 mm grooving/parting tool with R0.2 left/right corners;
- complete parting with explicit two-body semantics;
- a holder-clearance undercut case that fails closed rather than being approximated into the axisymmetric provider.

The numerical tool dimensions are seeded from primary manufacturer training/catalogue material recorded in `experiment-plan-v1.json`; commercial product identity is not programme meaning.

## STEP scope

Qualified one-body cases use the accepted RCS-010 repeated-3D, batched-3D and axisymmetric reconstruction plus automated STEP Layer A-C fresh read-back. Complete parting uses the RCS-006 multi-solid parting worker as an all-bodies connectivity/STEP control.

The research adapter supplies polygonized radial profiles. Therefore successful STEP geometry/read-back does **not** qualify exact toroidal/circular-insert-nose analytic-surface preservation. `analytic_nose_surface_exactly_qualified` remains false by design.

## Reproduction

Static contract check:

```text
python3 tools/validate_rcs020.py
```

Research-only material derivation:

```text
python3 research/rcs-020/run_campaign.py --out-dir .results/rcs020-material-only
python3 research/rcs-020/refine_oracles.py --results-dir .results/rcs020-material-only
```

Hosted measured workflow:

```text
python3 research/rcs-020/run_campaign.py \
  --lathe-worker .build/rcs010/rcs010_lathe_worker \
  --baseline-worker .build/rcs006/rcs006_occt_worker \
  --out-dir .results/rcs020
python3 research/rcs-020/refine_oracles.py --results-dir .results/rcs020
python3 tools/validate_rcs020.py --results-dir .results/rcs020
```

No result may silently widen tolerance, discard a separated body, ignore a holder collision, or claim analytic STEP fidelity not actually measured.
