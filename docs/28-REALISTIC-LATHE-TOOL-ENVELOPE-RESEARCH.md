# Realistic lathe tool-envelope derivation research

Status: **RCS-020 accepted measured research pending merge**  
Date: 2026-09-17  
Issue: RCS-020 / #39  
Measured summary: `research/rcs-020/measured-summary-v1.json`

## Purpose

RCS-020 closes the main qualification gap left by RCS-010. RCS-010 showed that a completed 2D axial/radial material profile can be a robust first-class lathe representation, but its experiment began after the removal profile was already known. RCS-020 starts instead from explicit tool geometry, approach/orientation, canonical tool-centre trajectories, and reachability rules, then derives the material profile before invoking the accepted RCS-010 reconstruction/STEP comparator.

## Hypotheses

### H1 — real radiused-tool motion can feed the specialized provider

**Supported for the measured bounded subset.** Circular-nose external and internal tool paths produced material profiles within the declared independent-oracle budget, and all eight one-body qualified cases passed the RCS-010 repeated/batched/axisymmetric geometry checks plus their enabled STEP Layer A-C round trips.

### H2 — approach and holder reachability belong in the capability predicate

**Supported.** The deliberately stepped undercut case detected holder collision after four conservative samples and returned `refused_unsupported`. RCS-020 therefore rejects the idea that rotational symmetry of the desired material alone is sufficient for specialized-provider admission.

### H3 — grooving/parting can preserve explicit connectivity semantics

**Supported for the measured model.** A 2.0 mm cutting-width tool with 0.2 mm corner radii produced a bounded partial-groove profile. Complete parting generated a 1.6 mm zero-material interval and two durable material regions; the independent OCCT connectivity/STEP control returned two solids before export and two solids after fresh STEP read-back.

## Tool-model source basis

The tested definitions are representative abstract tools, not product IDs. Primary manufacturer material recorded in `research/rcs-020/experiment-plan-v1.json` supports the use of geometry-critical insert nose radius, approach/entering angle, grooving/parting cutting width, and corner radii. The campaign exercised a 0.8 mm external nose at 95° and 45° approach configurations, a 0.4 mm internal boring nose, and a 2.0 mm / R0.2 grooving-parting profile.

## Experiment design

### Circular-nose generator

The candidate generator polygonizes the Minkowski capsule of a circular insert nose swept along each canonical tool-centre segment under a `0.0001 mm` circular chord-error policy, then derives an axial/radial material boundary.

### Independent circular-nose oracle

The oracle does not call the polygon generator. It separately solves exact vertical intersections of endpoint circles and segment-offset lines, then integrates the material state at fine spatial resolution with a convergence check. The largest measured candidate/oracle material-volume difference among the eight one-body qualified cases was **0.0164630791 mm³**, below the predeclared `0.05 mm³` campaign budget.

### Facing

Facing is not substituted with a target CAD plane. A radial sweep of the R0.8 nose derives its front plane from the minimum axial support of the tool envelope. The measured candidate and closed-form oracle both produced **z = 1.0 mm**, with zero material-volume disagreement.

### Grooving and parting oracle correction

The first complete ten-case hosted execution exposed a weakness in the *research oracle*, not the candidate profile. Uniform trapezoidal integration across a complete parting discontinuity produced a false `0.3141255 mm³` coarse/fine discrepancy. The candidate profile itself was already close to the physical rounded-groove solution.

RCS-020 therefore replaced that discontinuity-sensitive acceptance oracle with an independent closed-form integral of the exact rounded-groove radius function. No tolerance was widened. For complete parting:

- candidate material volume: **98017.69562984923 mm³**;
- closed-form oracle: **98017.69561097043 mm³**;
- absolute difference: **1.8878796e-05 mm³**.

The discarded numerical quadrature remains recorded as diagnostic negative evidence in the measured summary.

### Reachability

A conservative holder ray begins after a defined insert-to-holder setback. The undercut fixture reached material at approximately `(z=20.0202796 mm, r=8.7202796 mm)` where stock radius was `10 mm`, and the operation was explicitly refused instead of being converted into a feasible target profile.

## Measured campaign

Accepted hosted evidence is workflow run **35275577906**, source head `9a90435a7f9cd07ab36eb9185c227c6e827e5ef9`, artifact **10519883446**, artifact ZIP SHA-256 `e595847e03123b9898dd37d83e49f2a983c4633fdf93ce7b20cec53360db1eec`.

The environment was Ubuntu 24.04.5 / GNU C++ 13.3.0 with the exact OCCT 8.0.1 baseline at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`, build profile `release-shared-cxx17-worker-only-headless-v4`.

### Aggregate results

- **10/10** required cases completed the campaign and validation.
- **8** one-body tool-derived cases passed independent material-oracle checks and downstream RCS-010 geometry validation.
- **24/24** enabled STEP strategy round trips passed.
- Maximum candidate/oracle material-volume delta across the one-body qualified cases: **0.0164630791 mm³**.
- Maximum OCCT strategy-to-axisymmetric volume delta: **7.28e-12 mm³**.
- Maximum OCCT strategy bounding-box delta: **2.13e-14 mm**.
- Maximum STEP read-back volume delta: **3.29e-10 mm³**.
- Maximum STEP read-back bounding-box delta: **2.13e-14 mm**.
- Across the eight one-body cases the repeated comparator used **28 material Booleans**, the batched comparator **8**, and the axisymmetric material provider **0**.

### Tool-derived case results

| Case | Key result |
|---|---|
| OD R0.8 / 95° | candidate/oracle volume delta `0.00976723 mm³`; all geometry/STEP checks pass |
| Facing R0.8 / 95° | derived front plane exactly `z=1.0 mm`; zero oracle material delta; all checks pass |
| Shoulder R0.8 / 95° | delta `0.01646308 mm³`; all checks pass |
| Taper R0.8 / 45° | delta `0.01374463 mm³`; all checks pass |
| Exact retrace ×20 | same derived material profile as first OD pass; 20 repeated Booleans vs 1 batch vs 0 axisymmetric material Booleans; all checks pass |
| Through boring R0.4 | zero oracle material delta; all checks pass |
| Blind boring R0.4 | delta `0.00903819 mm³`; all checks pass |
| Rounded groove R0.2 | closed-form oracle delta `0.00157712 mm³`; all checks pass |
| Complete parting | rounded-profile delta `1.89e-05 mm³`; two bodies; two-solid STEP read-back control passes |
| Undercut holder collision | collision measured; `refused_unsupported` as intended |

## CI repair history and negative evidence

The campaign intentionally preserves three research-harness corrections discovered by hosted measurement:

1. OCCT STEP routines emit human-readable transfer diagnostics before the worker JSON. The supervisor was corrected to parse the final complete JSON record instead of assuming stdout contains only JSON.
2. Existing RCS-010 and RCS-006 research workers label their final schema fields differently (`schema` versus `worker_schema`). The supervisor now accepts both explicit research protocols.
3. Uniform trapezoidal integration was demonstrated to be a poor acceptance oracle at a parting discontinuity and was replaced with the exact rounded-groove integral. The original false discrepancy remains recorded rather than deleted.

None of these repairs widened a geometry, material, or STEP acceptance budget.

## Capability matrix

### Qualified bounded material semantics

RCS-020 supports retaining the axisymmetric provider for the measured fixed-axis subset when admission includes explicit tool geometry, canonical path, and reachability:

- OD turning with the tested circular-nose external tool class;
- facing;
- shoulder formation;
- linear taper motion under the tested alternate approach configuration;
- exact/repeated finishing/retrace;
- through and blind boring with the tested circular-nose internal class;
- bounded rounded-groove material profiles;
- complete parting connectivity semantics.

### Provider handoff or refusal

The tested holder-collision undercut is `refused_unsupported`. Operations whose tool/setup semantics lie outside the qualified envelope or reachability predicate require another qualified provider or an explicit refusal; they may not be reduced to desired target profiles silently.

### Still unqualified

- exact toroidal/circular-insert-nose analytic surface reconstruction in STEP from this polygon research adapter;
- broad holder/fixture interference beyond the deliberately bounded conservative reachability probe;
- general undercut and form tooling;
- live-tool, eccentric, or other non-axisymmetric lathe operations.

## STEP boundary

All 24 enabled repeated/batched/axisymmetric STEP Layer A-C round trips passed with negligible geometric deltas. This qualifies the measured *material/B-rep exchange result*, not exact reconstruction of the insert nose as a toroidal or other preferred analytic class. The polygon research adapter often reconstructs many conical segments, which is precisely why `analytic_nose_surface_exactly_qualified` remains false.

RCS-022 remains responsible for independent Layer-D interoperability qualification of the exact production-candidate export profile.

## Implications for MSAC

MSAC should preserve immutable physical tool definitions, setup/frame semantics, and canonical motion. It does not need to emit finished CAD profiles to make the lathe provider work. Tool orientation and reachability remain manufacturing semantics that may affect whether an operation is accepted.

## Implications for OpenSimachinist

The RCS-010 provider remains a first-class bounded specialization, now with a stronger evidence-backed entry predicate: **qualified rotational material semantics + qualified tool-envelope construction + qualified reachability + explicit body/connectivity handling**.

The `(z,r)` state, polygon research adapter, and OCCT topology remain replaceable derived implementation state.

## Unresolved questions

- provenance-assisted exact analytic reconstruction of nose-generated curved surfaces before STEP;
- production-scale holder/fixture collision and reachability rather than the bounded research probe;
- additional insert/form-tool families and complex undercut tooling;
- live-tool/eccentric/non-axisymmetric lathe dispatch;
- broader parameter sweeps beyond the ten representative qualification fixtures.

These do not invalidate the measured bounded provider capability. They remain explicit capability/reconstruction boundaries for Gate 5 and later work.
