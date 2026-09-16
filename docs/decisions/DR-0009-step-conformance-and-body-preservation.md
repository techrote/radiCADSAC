# DR-0009 — STEP success requires measured conformance and explicit body preservation

Status: accepted  
Date: 2026-09-16  
Decision scope: programme STEP export contract

## Context

STEP is the programme's mandatory primary engineering output. Earlier foundation work established that successful serialization is not sufficient and that parting/cut-through can legitimately create multiple disconnected material bodies.

RCS-005 must therefore define an export result that is measurable, preserves physical/material semantics and remains independent from a single writer implementation.

ISO 10303-242:2025 Edition 4 is the current published AP242 application protocol at the time of this decision. OCCT 8.0.1 exposes an `AP242DIS` writer mode, but that implementation label is not itself proof of Edition-4 conformance.

## Decision

The programme adopts `msac-step-conformance/1.0` with these fixed rules:

- The initial protocol target is **AP242-family managed model-based 3D engineering**.
- Conventional manifold B-rep solids are mandatory primary geometry. Mesh/tessellated/surface-only output is not an acceptable success fallback.
- Export success requires four layers of evidence: valid committed pre-export state, valid serialized STEP structure, geometry-aware read-back, and a currently interoperability-qualified exporter profile.
- The exact emitted schema identifier and exporter implementation/version are recorded. An implementation mode such as OCCT `AP242DIS` is not relabelled as ISO certification.
- The default body selection is **all material bodies in the selected committed revision**.
- There is no implicit largest/primary/first-body rule.
- Explicit subset export is allowed only when the selection and omitted body IDs are recorded.
- Disconnected bodies may be represented by a qualified single-product multi-solid representation or an explicit body product structure. If no qualified representation preserves the requested body set, export is refused.
- Healing/same-domain cleanup is explicit and must remain within declared geometric budgets without changing material-body connectivity unless the committed state requires it.
- Required analytic primitives are preserved where the source is exact and the operation does not mathematically destroy that class.
- Millimetre and inch export must be physically equivalent after unit normalization.
- A writer return status alone can never produce programme `success`.

## Alternatives considered

### Treat `STEPControl_Writer::Write()` success as sufficient

Rejected. It cannot prove body completeness, physical scale, topology validity, geometric fidelity, analytic retention, or downstream usability.

### Export only the largest or presumed retained body after parting

Rejected because geometry alone cannot reliably infer product-versus-scrap intent and silent body loss would violate the committed material state.

### Always encode disconnected bodies as an assembly

Rejected as a universal rule because disconnected pieces of one machined workpiece are not necessarily an assembly in product semantics. Both single-product multi-solid and explicit product-structure strategies remain available subject to qualification.

### Require one proprietary CAD system as the truth oracle

Rejected. Interoperability is a qualification matrix. Independent Part 21/schema parsing plus one or more recorded downstream CAD/CAM consumers provides evidence without making one vendor normative.

### Allow STL/faceted geometry when exact STEP B-rep fails

Rejected as a success path. Such output may be offered separately as a convenience artifact but cannot satisfy the mandatory engineering STEP contract.

## Evidence

- ISO 10303-242:2025 Edition 4 scope includes mechanical parts/assemblies and multiple geometry/product-data forms appropriate to the programme.
- OCCT 8.0.1 `STEPControl_StepModelType` exposes manifold solid B-rep / B-rep-with-voids translation modes.
- OCCT 8.0.1 `DESTEP_Parameters` exposes explicit schema, assembly, precision and length-unit settings including `AP242DIS`, millimetres and inches.
- OCCT 8.0.1 `STEPCAFControl_Writer` supports assemblies, product names/properties/metadata and explicit `DESTEP_Parameters` without requiring `Interface_Static` initialization.
- RCS-002/RCS-003 preserve material-body identity and make disconnected parting/cut-through states normal workloads.
- RCS-004 established that STEP should remain wrapped behind programme-level conformance rather than treated as self-validating OCCT output.

## Consequences

- RCS-006 must integrate STEP generation/read-back into the shared benchmark harness using the RCS-005 fixture matrix and metrics.
- RCS-013 can select a backend architecture without changing what counts as a successful engineering export.
- MSAC UI must distinguish `success`, `refused`, `failed`, and `unqualified` rather than displaying every generated `.step` file as success.
- Future body-retention/scrap semantics can add explicit selection policy without changing the rule against silent body loss.
- Exporter upgrades that materially change STEP output require profile requalification.

## Reversibility

Moderate. The exact AP242 implementation profile, multi-body encoding strategy and interoperability consumers are deliberately replaceable. The requirements for measured geometry correctness, explicit body selection and no silent mesh/body-loss fallback are low-reversibility programme invariants because weakening them would invalidate STEP as the primary engineering deliverable.

## Reconsideration trigger

Reconsider the contract when a later STEP edition/profile materially changes the preferred representation, when measured downstream interoperability strongly favours one multi-body strategy, or when another standards-based engineering exchange requirement is added. Any revision must preserve explicit units, measurable fidelity and material-body selection semantics.
