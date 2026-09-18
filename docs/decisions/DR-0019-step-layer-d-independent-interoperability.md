# DR-0019 — STEP Layer-D evidence requires independent parser and solid consumer

Status: proposed pending final RCS-022 measured campaign  
Date: 2026-09-18  
Decision scope: STEP Layer-D interoperability evidence

## Context

The accepted STEP contract requires independent interoperability evidence beyond OCCT writer → OCCT reader agreement. RCS-022 must qualify a concrete exporter profile, or preserve a bounded `interoperability_unqualified` result, without changing source geometry, material-body meaning, journal authority, tolerance channels or provenance merely to satisfy a downstream tool.

Product-brand diversity alone is not implementation independence. An application that imports STEP through OCCT cannot provide the independent geometry-consumer evidence required for an OCCT exporter simply because it has a different UI or product name.

## Decision

A STEP export profile may be called Layer-D interoperable only when all lower-layer conformance gates pass and the same emitted file is accepted by both:

1. a schema-capable ISO 10303 Part-21 parser implemented independently from the exporter stack; and
2. a downstream solid consumer whose STEP reader and B-rep kernel do not reuse the exporter kernel.

For RCS-022 the concrete pins are `step-io 0.2.4` for role (1) and `vcad-kernel-step 0.10.0` for role (2). The exporter remains OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`. A fresh OCCT readback remains mandatory Layer-C evidence but is not independent Layer-D evidence.

The founding STEP contract's reference to STEPcode was an implementation candidate, not a requirement to use that particular parser. Independence and schema-capable Part-21 validation are the invariant requirements.

Conventional manifold B-rep remains the STEP boundary. Deferred directional/dexel/mesh material states from RCS-021 must reconcile to conventional B-rep before export. Every disconnected material solid must be transferred and independently observed; a consumer that imports only one body from a two-body result fails.

If the independent parser or solid consumer exposes a real compatibility failure, the exact profile becomes `interoperability_unqualified`. That bounded negative result may close the research issue when versions, settings, affected fixtures, artifact hashes and adversarial controls are preserved. It does not grant production Layer-D qualification.

Strict geometry/output accuracy remains governed by the existing Layer-C contract. The independent vcad consumer's tessellated bbox/volume values are bounded diagnostics only; their wider inspection bounds cannot rescue a Layer-C failure.

## Alternatives considered

### Count another OCCT-based CAD application as independent

Rejected. Shared STEP/kernel implementation would leave the writer/self-reader failure class substantially correlated.

### Treat successful Part-21 parsing as sufficient Layer D

Rejected. Syntax/schema inspection cannot prove that an independent solid kernel can reconstruct the requested bodies and material connectivity.

### Widen tolerances or drop difficult bodies until the consumer accepts the file

Rejected. That would change the engineering contract to fit a tool and would violate protected material/body semantics.

### Fall back to tessellated geometry when B-rep import fails

Rejected. Tessellation may provide diagnostics or preview artifacts but cannot satisfy the mandatory conventional B-rep STEP contract.

## Evidence

RCS-022 pins the exporter, parser and consumer versions in `research/rcs-022/profile-v1.json`, defines the positive/adversarial matrix in `research/rcs-022/fixture-plan-v1.json`, and runs the measured campaign through `.github/workflows/rcs022.yml`.

The campaign includes metric/inch scale, analytic cylinder/cone, through/blind holes, disconnected two-body states, RCS-020/RCS-021-derived semantics, explicit same-domain reconciliation and a trimmed curved result. Adversarial controls cover wrong-unit interpretation, body omission, open/non-solid input, analytic loss, excessive dimension/volume mismatch, malformed schema and downstream import failure.

`step-io 0.2.4` is implemented independently from OCCT and provides the Part-21/schema-aware parse role. `vcad-kernel-step 0.10.0` is implemented independently from OCCT and provides the downstream B-rep reconstruction role. Consumer-side tessellation is used only for bounded diagnostic metrics.

The final acceptance state of this record is intentionally deferred until the RCS-022 measured campaign succeeds as a harness and records either `interoperability_qualified` or a precise `interoperability_unqualified` result.

## Consequences

- Parser and consumer dependency versions are evidence-bearing pins and changes trigger requalification.
- CI must exercise both positive fixtures and adversarial rejection controls.
- STEP artifact hashes and fixture/source bindings are retained in evidence without making STEP the canonical source of user intent.
- A positive Layer-D claim applies only to the exact tested exporter profile and configuration.
- A bounded negative result remains useful evidence and must not be cosmetically relabelled as success.

## Reversibility

Moderate. The concrete parser and consumer implementations can be replaced by other genuinely independent implementations after rerunning the same evidence contract. The requirement for implementation independence, exact body preservation, conventional B-rep output and fail-closed qualification is deliberately low-reversibility.

## Reconsideration trigger

Reconsider the concrete pins when the exporter version/schema/healing/body-product policy changes, when `step-io` or vcad materially changes its STEP/B-rep implementation, when a stronger independent CAD/CAM consumer becomes automatable, or when the programme adopts a different STEP profile. Any replacement must preserve the existing source, body, tolerance and provenance invariants.
