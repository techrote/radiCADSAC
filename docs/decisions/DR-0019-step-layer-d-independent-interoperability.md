# DR-0019 — STEP Layer-D evidence requires independent parser and solid consumer

Status: accepted by RCS-022 measured campaign  
Date: 2026-09-18  
Decision scope: STEP Layer-D interoperability evidence

## Context

The accepted STEP contract requires independent interoperability evidence beyond OCCT writer → OCCT reader agreement. RCS-022 must qualify a concrete exporter profile, or preserve a bounded `interoperability_unqualified` result, without changing source geometry, material-body meaning, journal authority, tolerance channels or provenance merely to satisfy a downstream tool.

Product-brand diversity alone is not implementation independence. An application that imports STEP through OCCT cannot provide the independent geometry-consumer evidence required for an OCCT exporter simply because it has a different UI or product name.

## Decision

A STEP export profile may be called Layer-D interoperable only when all lower-layer conformance gates pass and the same emitted file is accepted by both:

1. a schema-capable ISO 10303 Part-21 parser implemented independently from the exporter stack; and
2. a downstream solid consumer whose STEP reader and B-rep kernel do not reuse the exporter kernel and whose declared qualification measurements satisfy their bounded acceptance envelope.

For RCS-022 the concrete pins are `step-io 0.2.4` for role (1) and `vcad-kernel-step 0.10.0` plus `vcad-kernel-tessellate 0.10.0` for role (2). The exporter remains OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`. A fresh OCCT readback remains mandatory Layer-C evidence but is not independent Layer-D evidence.

The founding STEP contract's reference to STEPcode is treated as a concrete implementation candidate, not as the invariant requirement. The invariant is independently implemented, schema-capable Part-21 validation. The exact parser and consumer dependency graphs are committed and CI uses `cargo build --locked`.

Conventional manifold B-rep remains the STEP boundary. Deferred directional/dexel/mesh material states from RCS-021 must reconcile to conventional B-rep before export. Every disconnected material solid must be transferred and independently observed; a consumer that imports only one body from a two-body result fails.

If the independent parser or solid consumer exposes a compatibility, resource-bound or metric disagreement, the exact profile becomes `interoperability_unqualified`. A bounded negative result may close the research issue when versions, settings, affected fixtures, artifact hashes and adversarial controls are preserved. It does not grant production Layer-D qualification.

Strict geometry/output accuracy remains governed by the existing Layer-C contract. The independent vcad consumer's tessellated bbox/volume values are bounded diagnostics only; their wider inspection bounds cannot rescue a Layer-C failure.

## Alternatives considered

### Count another OCCT-based CAD application as independent

Rejected. Shared STEP/kernel implementation would leave the writer/self-reader failure class substantially correlated.

### Treat successful Part-21 parsing as sufficient Layer D

Rejected. Syntax/schema inspection cannot prove that an independent solid kernel can reconstruct the requested bodies and material connectivity.

### Treat B-rep import alone as full qualification when consumer metric evidence fails

Rejected for this profile. RCS-022 declared downstream bbox/volume evidence as part of the positive qualification gate. Clean independent B-rep reconstruction is valuable evidence, but it does not retroactively remove a declared measurement gate.

### Widen tolerances or resource limits after observing the result

Rejected. That would fit the qualification envelope to the observed consumer rather than testing the declared profile. Any future envelope change is a new profile/requalification event.

### Fall back to tessellated geometry when B-rep import fails

Rejected. Tessellation may provide diagnostics or preview artifacts but cannot satisfy the mandatory conventional B-rep STEP contract.

## Evidence

RCS-022 pins the exporter, parser and consumer versions in `research/rcs-022/profile-v1.json`, defines the positive/adversarial matrix in `research/rcs-022/fixture-plan-v1.json`, and runs the measured campaign through `.github/workflows/rcs022.yml`.

The final measured campaign at source head `be3812856d600e3fa09bc8462ff0e2c2b851fcd9` ran as workflow `35349677095`, job `105614535156`. Artifact `10549412055` (`rcs022-step-layer-d-evidence`) has SHA-256 `d30bce4672da74d3714cb16d655f5b102ba1ce46e46f4d754684eade377b30d0`. The durable condensed record is `research/rcs-022/frozen-result-v1.json`.

The emitted schema identifier observed by the independent parser is `AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF {1 0 10303 442 1 1 4 }`.

All 11 positive fixtures passed strict Layer C. `step-io` accepted all 11 with zero warnings and the expected units/body counts/required analytic classes. `vcad-kernel-step` independently reconstructed all 11 cleanly with zero skipped faces and exact solid counts, including both two-body fixtures.

The profile is nevertheless **`interoperability_unqualified`**. Nine fixtures reached a vcad metric-path allocation request of 1,610,612,736 bytes and were terminated by the declared 1 GiB child-process limit. The analytic-cylinder and analytic-cone diagnostics completed but their 64-triangle mesh volumes differed from the exporter material volume by approximately 33.76% and 14.84%, exceeding the declared 2% consumer diagnostic bound. These disagreements are preserved rather than repaired by tolerance widening, resource-envelope expansion, body dropping or substitution.

The explicit same-domain reconciliation fixture preserved one body, had zero maximum bbox change and about `9.09e-13 mm3` absolute volume change while reducing ten coplanar planar faces to six. All seven adversarial controls detected their intended fault classes: wrong scale, omitted body, open/non-solid source, analytic loss, excessive geometry deviation, malformed schema, and downstream import failure.

## Consequences

- The exact RCS-022 profile is **not** production Layer-D qualified.
- Independent parser and B-rep import evidence is positive and reusable, but the consumer metric path remains the qualification blocker.
- Parser and consumer dependency versions and complete lockfiles are evidence-bearing pins; changes trigger requalification.
- STEP artifact hashes and fixture/source bindings are retained without making STEP the canonical source of user intent.
- A future positive Layer-D claim applies only to its exact tested exporter/profile/consumer configuration.
- The negative result must remain visible to later synthesis and must not be cosmetically relabelled as success.

## Reversibility

Moderate. The concrete parser and consumer implementations can be replaced by other genuinely independent implementations after rerunning the same evidence contract. The requirement for implementation independence, exact body preservation, conventional B-rep output and fail-closed qualification is deliberately low-reversibility.

## Reconsideration trigger

Reconsider the concrete pins or qualification envelope when the exporter version/schema/healing/body-product policy changes, when `step-io` or vcad materially changes its STEP/B-rep implementation, when the vcad metric-path allocation/tessellation defects are repaired, when a stronger independent CAD/CAM consumer becomes automatable, or when the programme adopts a different STEP profile. Any replacement must preserve the existing source, body, tolerance and provenance invariants.
