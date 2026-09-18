# DR-0019 — STEP Layer-D evidence requires independent parser and solid consumer

**Status:** accepted by RCS-022 evidence campaign; final qualification status is measured, not assumed.

## Decision

A STEP export profile may be called Layer-D interoperable only when all lower-layer conformance gates pass and the same emitted file is accepted by both:

1. a schema-capable ISO 10303 Part-21 parser implemented independently from the exporter stack; and
2. a downstream solid consumer whose STEP reader and B-rep kernel do not reuse the exporter kernel.

For RCS-022 the concrete pins are `step-io 0.2.4` for role (1) and `vcad-kernel-step 0.10.0` for role (2). The exporter remains OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`. A fresh OCCT readback remains mandatory Layer-C evidence but is not independent Layer-D evidence.

The founding STEP contract's reference to STEPcode was an implementation candidate, not a requirement to use that particular parser. Independence and schema-capable Part-21 validation are the invariant requirements.

## Protected semantics

This decision does not authorize changing the journal, source geometry, tolerance channels, disconnected-body set, machining semantics, or provenance to accommodate an exporter or consumer. Conventional manifold B-rep remains the STEP boundary. Deferred directional/dexel/mesh material representations from RCS-021 must reconcile to that boundary before export.

Every disconnected material solid must be transferred and independently observed. A consumer that imports one body from a two-body result does not pass merely because its imported body is valid.

## Negative-result rule

If the independent parser or independent solid consumer exposes a real compatibility failure, the profile becomes `interoperability_unqualified`. That bounded negative result may close the research issue if the exact blocker, versions, settings, fixture, and adversarial controls are preserved. It does not authorize production qualification.

No tolerance widening, body dropping, post-export healing, schema substitution, tessellated fallback, or relabelling of a consumer failure may be used to manufacture a positive result.

## Diagnostic bounds

Strict geometry/output accuracy remains governed by the existing Layer-C contract. The independent vcad consumer's tessellated bbox/volume values are additional bounded diagnostics only; they have intentionally wider inspection bounds because they pass through consumer tessellation and f32 positions. A Layer-C failure cannot be rescued by those wider diagnostic bounds.

## Consequences

- Product-brand diversity is insufficient when products share OCCT internally.
- Parser and consumer dependency versions become evidence-bearing pins.
- CI must exercise both positive fixtures and adversarial rejection controls.
- STEP artifact hashes and fixture/source bindings are retained in evidence without making STEP the canonical source of user intent.
