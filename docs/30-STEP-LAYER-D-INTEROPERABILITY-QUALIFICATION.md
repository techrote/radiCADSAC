# STEP Layer-D Independent Interoperability Qualification

RCS-022 makes Layer D executable. It does not relax the STEP contract in `docs/13-STEP-CONFORMANCE-CONTRACT.md`; it supplies the independent parser/consumer evidence that contract requires and records the exact tested profile as **`interoperability_unqualified`**.

## Export profile

The tested profile is `rcs-022-occt-ap242dis-layer-d/1.0`: OCCT 8.0.1 / commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`, AP242DIS, `STEPControl_ManifoldSolidBrep`, tessellation off, assembly auto, surface curves on, non-manifold export off, `Greatest` precision mode with `0.0001` in the selected file unit, and explicit millimetre or inch output. The measured serialized schema identifier is `AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF {1 0 10303 442 1 1 4 }`; this remains an OCCT AP242-family implementation output, not an ISO 10303-242:2025 Edition-4 certification claim.

The exporter refuses invalid/open/non-solid input, non-positive material, or topology tolerance above the established 0.005 mm geometry-accuracy boundary before writing. Disconnected material is not normalized away. Each solid is transferred into the same STEP model and the expected solid count is checked after fresh OCCT readback and independently.

## Independent evidence roles

`step-io 0.2.4` is the schema-capable Part-21 parser. It is a Rust implementation with no OCCT dependency and exposes the file schema, units, B-rep solids, surfaces, and warnings. It replaces STEPcode only as the concrete RCS-022 parser implementation; implementation independence and schema-capable Part-21 validation remain the contract invariants.

`vcad-kernel-step 0.10.0` is the downstream solid consumer. It builds vcad B-rep solids and exposes skipped-face/degradation reporting. It is independently implemented from OCCT. Its B-rep import observation runs separately from `vcad-kernel-tessellate 0.10.0`, which supplies bounded bbox/volume diagnostics after a successful import. A diagnostic crash, timeout, or resource-bound hit cannot erase a successful B-rep import observation, but it does prevent the profile from being qualified when the declared metric gate is not satisfied.

The independent parser/consumer children are bounded to 8 seconds wall time, 6 seconds CPU time and 1 GiB address space. A bound hit is retained as evidence that the exact tested implementation/profile did not satisfy the declared qualification envelope; it is not converted into success by widening resource or geometry tolerances after the fact.

FreeCAD or another OCCT-backed application would not satisfy this evidence role merely by being a different product, because it would reuse the exporter kernel family.

## Evidence gates

A positive fixture requires: successful exporter status; valid fresh-reader B-rep; exact expected body count; Layer-C bbox within 0.005 mm and volume within either 0.001 mm3 absolute or 1e-6 relative; independent parser acceptance of AP242; correct parser unit scale; exact parser solid count; required analytic surface recognition; independent consumer acceptance without skipped faces; exact consumer solid count; successful bounded consumer metric diagnostic; consumer bbox within 0.05 mm; and consumer tessellated volume within 2% relative of exporter material volume.

The wider consumer metric bounds acknowledge tessellation and f32 conversion inside the independent diagnostic path. They are not export tolerances and cannot rescue a Layer-C failure.

Adversarial controls separately exercise wrong-unit interpretation, omitted-body expectations, open/non-solid export refusal, analytic-class substitution, excessive dimension/volume mismatch, malformed schema, and truncated downstream input. Failure to detect any control is a harness failure. A positive-case interoperability disagreement instead produces `interoperability_unqualified` while retaining the exact blocker.

## Measured result — 2026-09-18

The final measured campaign ran at source head `be3812856d600e3fa09bc8462ff0e2c2b851fcd9` in workflow run `35349677095`, job `105614535156`. The evidence artifact `rcs022-step-layer-d-evidence` has artifact id `10549412055`, size 69,626 bytes and SHA-256 `d30bce4672da74d3714cb16d655f5b102ba1ce46e46f4d754684eade377b30d0`. The durable condensed record, including every STEP SHA-256, is `research/rcs-022/frozen-result-v1.json`.

All 11 declared positive fixtures passed the strict Layer-C checks. `step-io` accepted all 11, reported zero warnings, retained the expected mm/inch scale and analytic cylinder/cone classes, and observed exact solid counts. `vcad-kernel-step` independently reconstructed all 11 fixtures cleanly with zero skipped faces and exact solid counts, including both disconnected solids in `two-body-parting` and `mill-cut-through`.

The profile nevertheless remains **`interoperability_unqualified`**. For nine fixtures, the separate vcad tessellation/metric child attempted a 1,610,612,736-byte allocation and was terminated under the declared 1 GiB address-space bound; therefore consumer bbox/volume evidence was unavailable inside the qualification envelope. The analytic-cylinder and analytic-cone metric paths completed, but their 64-triangle mesh volumes differed from the exporter material volume by about 33.76% and 14.84% respectively, exceeding the declared 2% diagnostic bound. Those are consumer diagnostic limitations/disagreements, not permission to weaken the strict Layer-C result.

The `healed-same-domain` fixture explicitly measured `ShapeUpgrade_UnifySameDomain`: body count remained 1, maximum bbox delta was 0, volume changed by about `9.09e-13 mm3`, and coplanar faces reduced from 10 to 6. All seven adversarial controls detected their intended failure class.

## RCS-020 and RCS-021 relationship

The RCS-020 fixed-axis lathe case is consumed only after reconstruction to conventional manifold B-rep. The fixture represents the qualified material-domain class but does not claim an exact replay of circular-nose/toroidal tool geometry, which RCS-020 left unqualified.

The RCS-021 mill cut-through case consumes the protected two-body material invariant. Directional/tridexel or mesh fallback states remain deferred material representations and are not written directly as STEP. They must first reconcile to conventional B-rep under DR-0018.

## Provenance and canonical-state boundary

Every generated STEP file is SHA-256 digested and the evidence binds the digest to the fixture source description, exporter profile, expected body count, same-kernel readback, independent parser observation, and independent consumer observation. Both Rust dependency graphs are now committed as `Cargo.lock` files and CI builds them with `--locked`; Cargo metadata and compiler identity remain attached to the workflow artifact.

Generated STEP files and metric evidence are derived interchange artifacts. They neither replace nor mutate the canonical journal, protected source semantics, machine state, material-body lineage, or provenance records.

## Qualification and rerun semantics

`interoperability_qualified` remains reserved for a future run in which every declared positive case and every adversarial control passes the exact profile. The current bounded negative result closes the RCS-022 research question but does **not** grant production Layer-D qualification.

Requalification is mandatory when the OCCT exporter version/commit, schema or solid mode, precision/healing/body-product policy, process/global-state configuration, independent probe bounds, `step-io` version, vcad STEP/B-rep implementation, or consumer metric implementation changes. No tolerance widening, body dropping, implicit healing after export, or tessellated substitution may turn a negative result into a positive one.
