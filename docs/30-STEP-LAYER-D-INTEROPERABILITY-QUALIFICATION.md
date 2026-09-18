# STEP Layer-D Independent Interoperability Qualification

RCS-022 makes Layer D executable. It does not relax the STEP contract in `docs/13-STEP-CONFORMANCE-CONTRACT.md`; it supplies the independent parser/consumer evidence that contract previously required.

## Export profile

The tested profile is `rcs-022-occt-ap242dis-layer-d/1.0`: OCCT 8.0.1 / commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`, AP242DIS, `STEPControl_ManifoldSolidBrep`, tessellation off, assembly auto, surface curves on, non-manifold export off, `Greatest` precision mode with `0.0001` in the selected file unit, and explicit millimetre or inch output. The exporter refuses invalid/open/non-solid input, non-positive material, or topology tolerance above the established 0.005 mm geometry-accuracy boundary before writing.

Disconnected material is not normalized away. Each solid is transferred into the same STEP model and the expected solid count is checked both after a fresh OCCT readback and by independent consumers.

## Independent evidence roles

`step-io 0.2.4` is the schema-capable Part-21 parser. It is a Rust implementation with no OCCT dependency and exposes the file schema, units, B-rep solids, surfaces, and warnings. It replaces STEPcode only as the concrete RCS-022 parser implementation; it does not change the normative requirement for implementation independence.

`vcad-kernel-step 0.10.0` is the downstream solid consumer. It builds vcad B-rep solids and exposes explicit skipped-face/degradation reporting. It is independently implemented from OCCT. `vcad-kernel-tessellate 0.10.0` is used only to calculate consumer-side bbox/volume diagnostics. Those mesh-derived properties are bounded observations, not a replacement for the strict B-rep round-trip criteria at Layer C.

FreeCAD or another OCCT-backed application would not satisfy this evidence role merely by being a different product, because it would reuse the same underlying STEP/kernel stack. RCS-022 therefore does not count such wrappers as independent.

## Evidence gates

A positive fixture requires: successful exporter status; valid fresh-reader B-rep; exact expected body count; Layer-C bbox within 0.005 mm and volume within either 0.001 mm3 absolute or 1e-6 relative; independent parser acceptance of AP242; correct parser unit scale; exact parser solid count; required analytic surface recognition; independent consumer acceptance without skipped faces; exact consumer solid count; consumer bbox within 0.05 mm; and consumer tessellated volume within 2% relative of exporter material volume.

The wider consumer diagnostic bounds acknowledge tessellation and f32 conversion inside that independent inspection path. They are not export tolerances and cannot make a Layer-C failure pass.

Adversarial controls separately exercise wrong-unit interpretation, omitted-body expectations, open/non-solid export refusal, analytic-class substitution, excessive dimension/volume mismatch, malformed schema, and truncated downstream input. Failure to detect any control is a harness failure. A genuine positive interoperability disagreement is instead retained as an `interoperability_unqualified` research result.

## RCS-020 and RCS-021 relationship

The RCS-020 fixed-axis lathe case is consumed only after reconstruction to conventional manifold B-rep. The fixture represents the qualified material-domain class but does not claim an exact replay of circular-nose/toroidal tool geometry, which RCS-020 explicitly left unqualified.

The RCS-021 mill cut-through case consumes the protected two-body material invariant. Directional/tridexel or mesh fallback states remain deferred material representations and are not written directly as STEP. They must first reconcile to conventional B-rep under DR-0018.

## Provenance and canonical-state boundary

Every generated STEP file is hashed with SHA-256 and evidence binds the digest to the fixture source description, exporter profile id, expected body count, same-kernel readback, independent parser observation, and independent consumer observation. These files are derived interchange artifacts. They neither replace nor mutate the canonical journal, protected source semantics, machine state, body lineage, or provenance records.

## Qualification semantics

`interoperability_qualified` means every declared positive case and every adversarial control passed this exact profile. `interoperability_unqualified` is a valid bounded research outcome when an independent implementation exposes a real blocker; it closes RCS-022 only as a recorded negative result and does not grant production Layer-D qualification. No tolerance widening, body dropping, implicit healing after export, or tessellated substitution is permitted to turn a negative result into a positive one.
