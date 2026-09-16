# OCCT 8.0.1 architecture, robustness, forkability, and license audit

Status: RCS-004 research output  
Date: 2026-09-16  
Audited upstream: `Open-Cascade-SAS/OCCT` tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose and scope

This audit maps Open CASCADE Technology 8.0.1 against the requirements of MSAC and OpenSimachinist. It is an evidence input to later benchmark and architecture work, not a decision to adopt a deep OCCT fork.

The audit asks which OCCT facilities can be reused, which must be isolated behind programme-owned contracts, which are plausible fork/replacement seams, and which remain unproven until the RCS-003 corpus is exercised by RCS-006 and later research.

Claims are labelled using `docs/06-RESEARCH-METHOD.md`: **SOURCE**, **INFERENCE**, **PROPOSAL**, and **OPEN**. No behaviour on the adversarial manufacturing corpus is claimed as measured here.

## Executive finding

**SOURCE:** OCCT 8.0.1 provides a mature exact/parametric B-rep stack, analytic geometry, Boolean infrastructure, General Fuse/cell building, shape validation/healing, sweep machinery, operation-local history, meshing, and STEP translation. Its public APIs expose per-operation fuzzy Boolean tolerance, non-destructive operation mode, parallel execution, explicit validation, history, and per-call STEP parameter objects.

**SOURCE:** The same codebase also contains process-global configuration surfaces. `BOPAlgo_Options` exposes global parallel mode in addition to per-instance mode, and `Interface_Static` explicitly manages named global translation parameters. STEP has a newer `DESTEP_Parameters` value object and writer overload that allow important transfer choices to be passed per operation, but legacy global configuration still exists.

**INFERENCE:** OCCT 8.0.1 is strong enough to remain the programme's primary baseline and a serious candidate implementation/reconciliation backend, but it should remain behind the existing programme-level boundary. The initial architecture should not expose `TopoDS_*`, OCCT handles, `Interface_Static`, or OCCT history objects to MSAC or to the durable journal.

**INFERENCE:** A wholesale fork is not yet justified. The first plausible fork seams are narrower: Boolean intersection/classification/tolerance behaviour and selected healing/reconciliation internals, and only if RCS-006/RCS-007 measurements show those internals are the limiting cause of failures that cannot be corrected by programme-level solver, tolerance, provenance, or deferred-topology strategies.

**SOURCE/INFERENCE:** Upstream was still active after 8.0.1, including August 2026 work explicitly removing global state and modernizing numerical/modeling code. A radical fork would therefore incur immediate merge/rebase cost against improvements directly relevant to robustness.

## Audited version and source pin

The audit target is exactly:

- repository: https://github.com/Open-Cascade-SAS/OCCT
- release: https://github.com/Open-Cascade-SAS/OCCT/releases/tag/V8_0_1
- commit: https://github.com/Open-Cascade-SAS/OCCT/commit/b8f597c677811d1f9f4d8a97f5ae2825c0353a42
- source tree: `76543d44e49c73bfffa2d141089e6c5add106f9a`

The release commit changes the version to 8.0.1 and is signed/verified upstream. RCS-004 intentionally does not substitute later `master` behaviour for this baseline.

Current-upstream observations are used only for fork-maintenance analysis. They are not evidence of 8.0.1 runtime behaviour.

## Classification vocabulary

The machine-readable companion is `research/rcs-004/audit-map.json`. Every area is assigned one initial classification:

- **reuse** — use the facility substantially as supplied, still behind the programme boundary where appropriate;
- **wrap/isolate** — useful facility, but isolate configuration, lifecycle, failure semantics, threading, or ownership from the stable programme API;
- **modify/fork candidate** — a plausible source-level modification seam if measurements justify it; not permission to fork now;
- **replace candidate** — programme requirements should be owned by a separate programme-level facility rather than delegated to this OCCT subsystem;
- **research only / insufficient evidence** — technically relevant, but its role is not justified without experiments.

## Initial subsystem/forkability map

| Area | Initial classification | Evidence and programme interpretation | Reversibility |
|---|---|---|---|
| B-rep topology and `TopoDS` identity | **wrap/isolate** | `TopoDS_Shape` is a lightweight reference to shared `TopoDS_TShape` plus location/orientation. Useful kernel state, unsuitable as durable programme identity or API. | High while backend types stay private. |
| Entity tolerance storage/propagation | **wrap/isolate** | `BRep_TFace`, `BRep_TEdge`, and `BRep_TVertex` store tolerances; edge validity also depends on same-parameter/same-range. Keep as kernel-internal evidence, not the programme's sole tolerance model. | High before RCS-007 architecture choice. |
| Analytic curves/surfaces | **reuse** | OCCT's geometry layer natively represents analytic and spline geometry and is directly compatible with B-rep/STEP workflows. | High; programme API need not expose concrete classes. |
| Boolean orchestration (`BOPAlgo` / `BRepAlgoAPI`) | **wrap/isolate** | Supports error/warning reports, per-instance parallel mode, fuzzy tolerance, non-destructive mode, same-domain maps, images/origins, and history. Configuration and result semantics require an adapter. | High if fixtures target programme contracts. |
| Boolean intersection/classification internals | **modify/fork candidate** | Central to General Fuse and likely robustness leverage, but no RCS-003 measurements yet prove a defect or required modification. Candidate only after RCS-006/RCS-007 evidence. | Medium; source fork raises sync burden. |
| General Fuse / cell building | **research only / insufficient evidence** | `BOPAlgo_CellsBuilder` exposes split parts, cell selection, material labels and internal-boundary removal. Relevant to regularized/deferred-topology research, but not yet proven as manufacturing-state architecture. | High while kept experimental. |
| Same-domain unification | **wrap/isolate** | `ShapeUpgrade_UnifySameDomain` uses explicit linear/angular tolerances, safe-input mode and history. Potentially useful reconciliation step; must not silently alter intended dimensions. | High when invoked only by explicit reconciliation policy. |
| Shape healing | **wrap/isolate** | Broad repair facilities exist and STEP transfer can run shape processing. Healing must be policy-controlled and followed by measurable validation. | High if original state/result metrics are retained. |
| B-rep validation | **reuse** | `BRepCheck_Analyzer` checks topology and edge/surface parameterization and supports exact/parallel modes. It is a baseline validator, not the entire programme conformance oracle. | High. |
| Sweep / pipe / loft machinery | **reuse** | Pipe/sweep APIs expose tolerances, transition policies, approximation controls, error status and generated-shape history. Useful for cutter-envelope experiments; process-specific solvers may bypass them. | High. |
| Operation-local shape history | **wrap/isolate** | `BRepTools_History` records generated/modified/removed relations and supports history composition. Useful diagnostic/provenance evidence but limited to OCCT topology and supported shape types. | High. |
| Durable programme provenance / semantic identity | **replace candidate** | OCCT history/TNaming can help within an OCCT session, but the durable journal and future RCS-008 identity model must survive backend replacement and topology regeneration. | High before production handoff. |
| OCAF `TNaming` | **research only / insufficient evidence** | `TNaming_NamedShape` stores evolution pairs and versions in OCAF. It may supply prior art or internal tooling, but no evidence yet supports making it the programme's manufacturing identity model. | High. |
| Meshing/tessellation | **reuse** | `BRepMesh_IncrementalMesh` provides parameterized/parallel triangulation and status flags. Appropriate for preview/diagnostics, never a substitute for committed STEP B-rep. | High. |
| STEP read/write and shape processing | **wrap/isolate** | `STEPControl_Writer` exposes manifold-solid modes, tolerance, sessions, shape-fix parameters and `DESTEP_Parameters`; successful writer status alone is not programme conformance. | High behind RCS-005 export contract. |
| Data-exchange configuration/global state | **wrap/isolate** | `DESTEP_Parameters` supports per-call settings, but `Interface_Static` remains an explicit global parameter registry. Prefer explicit parameter objects and isolate remaining global/session state. | Medium to high; process isolation remains available. |
| Threading / global parallel controls | **wrap/isolate** | Boolean and mesh APIs have per-instance parallel flags, while Boolean also has a global parallel mode. Do not assume arbitrary concurrent operations are isolated without measurement. | High with worker/process boundary. |
| Memory ownership / handles / shared shapes | **wrap/isolate** | `Standard_Transient` uses atomic reference counts; `TopoDS_Shape` shares underlying `TShape`. Safe ownership inside the backend does not imply safe mutable cross-thread or cross-ABI sharing. | High if C/C++ programme boundary owns opaque IDs rather than handles. |
| CMake/build/platform integration | **reuse** | 8.0.1 requires CMake 3.10+, defaults to C++17, supports shared/static builds and vcpkg. Shared libraries are the upstream default and best fit for LGPL/GDExtension isolation. | High. |
| License boundary | **wrap/isolate** | LGPL-2.1 plus Open CASCADE exception permits open-source use and modification subject to obligations. Keep OCCT-derived code/components distinguishable and preserve notices/source availability. | Medium once distributed artifacts ship. |

## B-rep topology and tolerance model

### Source facts

Pinned sources:

- `TopoDS_Shape`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/TopoDS/TopoDS_Shape.hxx
- `BRep_TFace`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TFace.hxx
- `BRep_TEdge`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TEdge.hxx
- `BRep_TVertex`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TVertex.hxx
- validator: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKTopAlgo/BRepCheck/BRepCheck_Analyzer.hxx

**SOURCE:** `TopoDS_Shape` shares an underlying `TopoDS_TShape` and adds location/orientation. `IsPartner`, `IsSame`, and `IsEqual` are therefore OCCT object/topology relations, not manufacturing semantic identity.

**SOURCE:** Face, edge and vertex implementations each carry tolerance. Edge data additionally carry `SameParameter`, `SameRange`, degenerate state and curve representations. `BRepCheck_Analyzer` tests topology and geometric consistency, including whether edge curve-on-surface representation stays within the edge tolerance.

**INFERENCE:** OCCT's local tolerance storage is necessary for valid OCCT B-reps, but it cannot be allowed to collapse the programme's distinct machine resolution, manufacturing tolerance, numerical uncertainty, topological equivalence, preview tolerance and export tolerance channels. RCS-007 must decide how those channels map into or sit above OCCT tolerances.

## Boolean stack and General Fuse

Pinned sources:

- options: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_Options.hxx
- General Fuse builder: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_Builder.hxx
- cells builder: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_CellsBuilder.hxx

**SOURCE:** `BOPAlgo_Options` supplies structured warning/error reporting, per-instance parallel mode, a global parallel mode, fuzzy tolerance and oriented-bounding-box filtering.

**SOURCE:** `BOPAlgo_Builder` describes itself as the General Fuse base algorithm. It can operate non-destructively, exposes split images/origins and same-domain relations, and prepares history. Its documentation explicitly reports intersection/builder failure classes.

**SOURCE:** `BOPAlgo_CellsBuilder` exposes all General Fuse split parts, user-selected cells, same-material internal-boundary removal, and cell/history mappings. Its own documentation requires valid arguments and warns that some multi-dimensional internal-boundary removal is unsupported.

**INFERENCE:** This is a useful experimental substrate for RCS-009, but not evidence that CellsBuilder itself is the desired internal material representation. Its operations still rely on the underlying intersection/splitting pipeline and conventional B-rep validity assumptions.

**OPEN:** Which RCS-003 families fail in 8.0.1, at what tolerance/operation-count boundaries, and whether failures originate primarily in intersections, classification, split construction, tolerance propagation, or post-processing. RCS-006 must establish this before source modification is justified.

## Healing, same-domain unification, and validation

Pinned sources:

- `ShapeUpgrade_UnifySameDomain`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_UnifySameDomain.hxx
- `BRepCheck_Analyzer`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKTopAlgo/BRepCheck/BRepCheck_Analyzer.hxx

**SOURCE:** same-domain unification defines coincidence using neighboring faces/edges on coincident surfaces/curves. It exposes safe-input mode, explicit linear and angular tolerance, preserved shapes, and modification history.

**SOURCE:** `BRepCheck_Analyzer` is a broad B-rep validity checker and can use exact curve-on-surface checking for applicable edges.

**INFERENCE:** both are valuable reconciliation tools, but healing/unification must never become a silent success path. RCS-005/RCS-006 should measure dimensions, topology, volume and analytic-surface preservation before and after any repair stage.

## Sweep, pipe, and cutter-envelope relevance

Pinned source:

- `BRepOffsetAPI_MakePipeShell`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKOffset/BRepOffsetAPI/BRepOffsetAPI_MakePipeShell.hxx

**SOURCE:** pipe-shell construction supports several sweep frames, auxiliary spines, multiple sections and scaling laws. It exposes 3D/boundary/angular tolerances, approximation controls, transition modes, status reporting, generated-shape history and surface error.

**INFERENCE:** this machinery is worth benchmarking for fixed-orientation and simple cutter-envelope strategies in RCS-011. Its own transition/approximation limitations mean it should not be presumed to solve arbitrary self-crossing freehand milling paths.

## History, naming, and provenance

Pinned sources:

- `BRepTools_History`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRepTools/BRepTools_History.hxx
- `TNaming_NamedShape`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ApplicationFramework/TKCAF/TNaming/TNaming_NamedShape.hxx

**SOURCE:** `BRepTools_History` records generated, modified and removed relations for vertices, edges, faces and solids and can merge sequential histories.

**SOURCE:** `TNaming_NamedShape` stores old/new shape pairs with an evolution type and version inside OCAF.

**INFERENCE:** both are useful sources of topology ancestry evidence, but neither should become the durable manufacturing identity contract. RCS-008 requires semantic identities for stock/body/setup/operation/tool-envelope boundaries that remain meaningful if topology is regenerated by another backend.

## Meshing

Pinned source:

- `BRepMesh_IncrementalMesh`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKMesh/BRepMesh/BRepMesh_IncrementalMesh.hxx

**SOURCE:** OCCT provides incremental triangulation with explicit linear/angular parameters, optional parallelism, custom contexts and status flags.

**INFERENCE:** this is suitable for preview/display and sampled comparison metrics. It does not weaken the programme invariant that committed engineering state and STEP conformance are B-rep/engineering-geometry concerns rather than mesh watertightness alone.

## STEP transfer and configuration

Pinned sources:

- writer: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/STEPControl/STEPControl_Writer.hxx
- per-call parameters: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/DESTEP/DESTEP_Parameters.hxx
- legacy/global parameters: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKXSBase/Interface/Interface_Static.hxx

**SOURCE:** `STEPControl_Writer` can translate to explicit STEP model types including manifold solid B-rep, can set output uncertainty/tolerance, can use an explicit work session, and accepts shape-fix parameters. It has a `Transfer` overload accepting `DESTEP_Parameters`.

**SOURCE:** `DESTEP_Parameters` includes STEP schema, write unit, precision mode/value, assembly mode, tessellation behaviour, model type and other read/write choices. It can also initialize itself from legacy statics.

**SOURCE:** `Interface_Static` describes itself as management for meaningful static variables used as global parameters and provides global setters/getters such as `write.step.schema`.

**INFERENCE:** OpenSimachinist should construct explicit transfer policy objects and per-operation sessions where the API supports them. Code that mutates `Interface_Static` should be isolated, serialized or moved into process-local workers until concurrency behaviour is measured. RCS-005 defines whether the resulting file is acceptable; a writer success code is only one observation.

## Threading and global state

The audit does not claim that OCCT as a whole is or is not thread-safe. That statement would be too broad and is not supported by a complete 8.0.1 component-level concurrency specification.

What the pinned source establishes is narrower:

- **SOURCE:** `BOPAlgo_Options` has both global and per-instance parallel controls.
- **SOURCE:** meshing has per-instance parallel configuration and a separate default-parallel static for plugin/factory use.
- **SOURCE:** `Interface_Static` is a global named-parameter registry.
- **SOURCE:** `Standard_Transient` uses an atomic reference counter.
- **SOURCE:** `TopoDS_Shape` instances may share the same underlying `TShape`.

**INFERENCE:** atomic handle lifetime is not equivalent to thread-safe mutation of the referenced model. Programme code must not infer concurrency safety merely because OCCT handles are atomically reference-counted.

**PROPOSAL:** default OpenSimachinist architecture work should preserve the option to run exact geometry/STEP jobs in controlled worker contexts or processes. This gives crash containment and global-state isolation and is consistent with the RCS-006 harness requirement to contain crashes/hangs. RCS-013 should decide the production boundary after stress evidence exists.

## Memory ownership and ABI boundary

Pinned sources:

- `Standard_Transient`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/FoundationClasses/TKernel/Standard/Standard_Transient.hxx
- `TopoDS_Shape`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/TopoDS/TopoDS_Shape.hxx

**SOURCE:** OCCT transient objects use intrusive atomic reference counting. Topological shapes are small wrappers around shared `TShape` objects plus location/orientation.

**INFERENCE:** this is efficient inside an OCCT implementation but undesirable as a long-lived Godot/GDExtension ABI. The stable MSAC/OpenSimachinist boundary should continue to use programme-owned values/IDs/status records and opaque backend handles with explicit lifetime, not C++ OCCT object layouts.

## Build and Windows/GDExtension footprint

Pinned build source:

- CMake configuration: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/CMakeLists.txt

**SOURCE:** 8.0.1 requires CMake 3.10 or newer, defaults to C++17, supports C++20/23/26 selections, has vcpkg integration, and defaults to shared libraries. The build itself warns about LGPL implications of static linking and recommends shared libraries for production.

**SOURCE:** OCCT is split into modules/toolkits, so an OpenSimachinist build can avoid unrelated visualization/DRAW/application-framework components when the dependency graph permits it rather than shipping an undifferentiated full SDK.

**INFERENCE:** for a Windows-first Godot consumer, prefer a separately built OpenSimachinist native library/worker that owns OCCT. Keep Godot-facing code thin and programme-defined. Do not make Godot modules include OCCT headers or require OCCT runtime types in saved state.

**OPEN:** the minimal exact toolkit set and resulting binary/startup footprint for the first harness/backend should be measured by RCS-006 or the first production build spike rather than guessed here.

## License and derivative-work implications

Pinned license sources:

- LGPL 2.1 text: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/LICENSE_LGPL_21.txt
- Open CASCADE exception: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/OCCT_LGPL_EXCEPTION.txt

**SOURCE:** OCCT is distributed under GNU LGPL 2.1 plus the Open CASCADE exception, with commercial licensing also offered upstream.

**SOURCE:** LGPL §2 requires distributed modifications/derivatives of the library to remain licensed under the LGPL terms and calls for notices on modified files. LGPL §§4–6 govern source availability and distribution of applications linked with the library. §6 explicitly describes a suitable shared-library mechanism as one route that allows the user to substitute a compatible modified library.

**SOURCE:** the Open CASCADE exception permits object code of a work using the library to incorporate material from OCCT headers under terms of the distributor's choice, provided supporting documentation prominently notices use of/basis on OCCT facilities.

**INFERENCE:** an open-source OpenSimachinist project can use and modify OCCT, but a deep OCCT-derived fork would carry ongoing LGPL/source/notice obligations for the derived library. Keeping programme-owned code cleanly separated from the derived OCCT component simplifies provenance, upgrading and compliance.

**PROPOSAL:** prefer shared-library linkage for the initial Windows integration unless a later distribution/legal review provides a reason to choose another compliant route.

**OPEN / NOT LEGAL ADVICE:** final packaging, installer, source-offer, relinking/replacement, third-party-license interaction and attribution details must be reviewed against the actual production distribution. This research records the technical/licensing boundary; it does not substitute for legal advice.

## Upstream velocity and deep-fork maintenance risk

Version-specific release source:

- 8.0.1 release: https://github.com/Open-Cascade-SAS/OCCT/releases/tag/V8_0_1

Current-upstream maintenance evidence observed after the pinned release includes commits such as:

- exact-HLR global-state removal: https://github.com/Open-Cascade-SAS/OCCT/commit/9248874be6f364c106cf3932e193fe670c6120fd
- shape-healing connectivity restoration/tests: https://github.com/Open-Cascade-SAS/OCCT/commit/e62f6b248327911bf2b7f5e649d74bea8e3735ef
- numerical/modeling rework: https://github.com/Open-Cascade-SAS/OCCT/commit/2fa332705f963f7fe5d9039348197b5231f030d2

These post-date 8.0.1 and are cited only to characterize upstream development activity.

**INFERENCE:** a deep fork would have to continuously decide whether to port upstream robustness, numerical, threading, build, STEP and healing improvements. Because several current changes concern exactly the classes of issue OpenSimachinist cares about, divergence cost is not theoretical.

**PROPOSAL:** maintain a pinned upstream baseline plus a narrow patch stack until measurements demonstrate that a deeper fork produces enough value to outweigh upstream-integration cost. If a fork becomes necessary, preserve commits as narrowly reviewable subsystem patches rather than mixing programme semantics into broad OCCT edits.

## Candidate fork seams

These are investigation seams, not accepted architecture:

1. **Boolean intersection/classification and tolerance decisions.** Highest-priority source-level seam if RCS-006 shows recurrent wrong/invalid outcomes concentrated there and RCS-007 shows programme-level equivalence cannot be implemented safely above it.
2. **Selected same-domain/healing/reconciliation internals.** Candidate only where measurement shows deterministic repair is required but current APIs cannot express the programme policy without silent geometry changes.
3. **History extraction adapters.** Prefer wrapping before modifying. Modify only if required ancestry is computed internally but irretrievably discarded before public history can capture it.
4. **STEP transfer isolation.** Prefer wrappers/process isolation/per-call `DESTEP_Parameters`; modifying OCCT solely to avoid global statics is premature unless RCS-005/RCS-006 concurrency tests prove a blocking issue.

Components that should remain behind programme abstraction even if modified include `TopoDS_*`, `BOPAlgo_*`, healing, meshing, OCAF/TNaming, STEP sessions and all OCCT tolerance values. None should become durable journal schema types.

## Areas not justified for replacement

RCS-004 found no source-based reason to replace OCCT's analytic curve/surface model, baseline B-rep validator, mesher, or STEP stack before comparative evidence exists. Alternative-representation research in RCS-012 remains mandatory because these components' existence does not prove the whole B-rep/Boolean architecture is optimal.

Likewise, old forum reports or historical failure folklore are not treated as evidence that 8.0.1 fails a case. Those claims become relevant only when reproduced on the pinned baseline or a later explicitly pinned comparison version.

## Risks and unresolved questions carried forward

- **OPEN:** exact RCS-003 failure envelope for Boolean coincidence, tangency, slivers, retracing and very long histories — RCS-006.
- **OPEN:** whether fuzzy tolerance improves robustness without unacceptable dimensional/topological changes — RCS-006/RCS-007.
- **OPEN:** whether General Fuse/CellsBuilder provides useful intermediate material-cell semantics at manufacturing scale — RCS-009.
- **OPEN:** stability/completeness of OCCT history for MSAC split/merge/replacement workloads — RCS-008.
- **OPEN:** exact STEP body/product and healing policy — RCS-005.
- **OPEN:** concurrent STEP/session/global-parameter behaviour under intended worker topology — follow-up concurrency probe and RCS-013.
- **OPEN:** minimal Windows toolkit/dependency footprint — RCS-006/implementation spike.
- **OPEN:** final production-distribution license review, especially if static linking or non-LGPL third-party libraries are proposed — RCS-013/handoff compliance work.

## Implications for downstream issues

### RCS-005 STEP contract

Treat `STEPControl_Writer`, `DESTEP_Parameters`, work sessions and shape-fix controls as implementation facilities, not definitions of correctness. Include explicit schema/unit/precision/healing settings in reproduction metadata.

### RCS-006 baseline harness

Pin the exact commit audited here. Record Boolean fuzzy/non-destructive/parallel settings, validation mode, healing/unification stages, STEP parameter object values and any global statics touched. Preserve warnings and errors rather than flattening them to pass/fail.

### RCS-007 tolerance/equivalence

Distinguish OCCT's entity tolerance and Boolean fuzzy value from programme-level manufacturing/equivalence/uncertainty policy. Test parameter sweeps rather than treating `SetFuzzyValue` as the proposed solution.

### RCS-008 provenance

Capture `BRepTools_History`, images/origins and same-domain maps as evidence sources while testing a programme-owned semantic ancestry layer independent of `TopoDS_Shape` identity.

### RCS-009 deferred topology

CellsBuilder/General Fuse is a concrete candidate experiment because it exposes split cells and internal-boundary removal. Its conventional B-rep assumptions and unsupported cases remain part of the comparison.

### RCS-010 / RCS-011 process solvers

Reuse OCCT analytic geometry, B-rep construction, sweep machinery, validation and STEP where they fit, while allowing lathe/mill process-specific material solvers to bypass repeated general 3D Booleans.

### RCS-012 alternatives

Compare alternatives against OCCT's actual strengths, including analytic geometry and STEP, not only against Boolean failure anecdotes. Conversion/reconciliation cost remains part of the trade.

### RCS-013 architecture synthesis

The evidence supports preserving an OCCT-isolated option with narrow patch seams. It does not yet select isolated upstream OCCT, a deep fork, or a hybrid as the final architecture.

## Reproduction and source verification

The machine-readable classification map is:

- `research/rcs-004/audit-map.json`

A local source probe is provided at:

- `research/rcs-004/probes/verify_occt_source.py`

Example:

```text
git clone https://github.com/Open-Cascade-SAS/OCCT.git external/OCCT
git -C external/OCCT checkout b8f597c677811d1f9f4d8a97f5ae2825c0353a42
python research/rcs-004/probes/verify_occt_source.py external/OCCT
python tools/validate_rcs004.py
```

The probe checks the exact git revision when available, version metadata, and the source/API markers on which this audit relies. It does not claim runtime robustness; runtime behaviour belongs in RCS-006 and later experiments.
