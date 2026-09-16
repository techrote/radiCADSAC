# Source baseline and external research anchors

Status: current research source baseline  
Date: 2026-09-16

## Purpose

This file records the external technical anchors used to prevent the programme from relying on stale assumptions or anecdote. Research issues add primary sources and pin exact versions where experiments depend on them.

## OCCT current baseline

At the founding date, the latest published Open CASCADE Technology release is **8.0.1**, released 2026-07-30.

Pinned Gate-1 / RCS-004 baseline:

- upstream repository: `Open-Cascade-SAS/OCCT`;
- release tag: `V8_0_1`;
- commit: `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`;
- source tree: `76543d44e49c73bfffa2d141089e6c5add106f9a`.

Primary sources:

- releases: https://github.com/Open-Cascade-SAS/OCCT/releases
- pinned release: https://github.com/Open-Cascade-SAS/OCCT/releases/tag/V8_0_1
- pinned commit: https://github.com/Open-Cascade-SAS/OCCT/commit/b8f597c677811d1f9f4d8a97f5ae2825c0353a42

The exact release commit was verified during RCS-001 and audited in RCS-004. Later experiments may intentionally introduce comparison versions/commits, but every result must record them explicitly.

Relevant 8.0.1 release-note themes include:

- Boolean/periodic-curve stability fixes;
- shape-healing robustness fixes;
- performance work around face validation and coincident curve-on-surface checks;
- STEP export reliability fixes;
- C++17/API baseline retained from 8.0.0p1.

Implication: the programme must benchmark the pinned 8.0.1 baseline rather than infer current behaviour from older OCCT versions or later `master`.

## OCCT licensing baseline

OCCT source is distributed under GNU LGPL 2.1 with the Open CASCADE exception.

Primary sources at the audited revision:

- LGPL 2.1: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/LICENSE_LGPL_21.txt
- Open CASCADE exception: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/OCCT_LGPL_EXCEPTION.txt

RCS-004 records the programme's source-based licensing/forkability analysis. Distribution-specific legal questions remain subject to review rather than being guessed in architecture documents.

## STEP current standards and implementation baseline

As of 2026-09-16, the current published AP242 application protocol is **ISO 10303-242:2025, Edition 4**, published 2025-08.

Primary source:

- ISO: https://www.iso.org/standard/84300.html

RCS-005 adopts AP242-family managed model-based 3D engineering as the programme target for founding STEP export, but does not claim ISO certification.

Pinned OCCT 8.0.1 source facts relevant to that contract:

- `DESTEP_Parameters::WriteMode_StepSchema` includes `WriteMode_StepSchema_AP242DIS`, not a symbol claiming ISO 10303-242:2025 Edition-4 certification: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/DESTEP/DESTEP_Parameters.hxx
- `STEPControl_ManifoldSolidBrep` targets STEP `manifold_solid_brep` or `brep_with_voids`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/STEPControl/STEPControl_StepModelType.hxx
- `STEPCAFControl_Writer` supports document/assembly transfer and explicit `DESTEP_Parameters` so important transfer settings need not be sourced only from global `Interface_Static`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/STEPCAFControl/STEPCAFControl_Writer.hxx
- OCCT length-unit choices include inches and millimetres: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/FoundationClasses/TKernel/UnitsMethods/UnitsMethods_LengthUnit.hxx

Independent structural/schema research anchor:

- STEPcode `p21read`: https://stepcode.github.io/docs/p21read/

Programme implication: the concrete OCCT baseline profile is named `occt-8.0.1-ap242dis`. It must pass `msac-step-conformance/1.0`; it is not automatically treated as equivalent to the current ISO edition because the writer mode happens to contain `AP242` in its name.

## CGAL exact geometry baseline

CGAL provides kernels with exact predicates and exact constructions, which are relevant to robustness research even if they are not selected as the final backend.

Primary sources:

- kernel manual: https://doc.cgal.org/latest/Kernel_23/index.html
- exact-predicates/exact-constructions kernel: https://doc.cgal.org/latest/Kernel_23/classCGAL_1_1Exact__predicates__exact__constructions__kernel.html

Implication: `floating point plus larger epsilon` is not the only robustness strategy worth evaluating.

## CGAL Nef baseline

CGAL Nef polyhedra are explicitly closed under Boolean set operations and can represent mixed-dimensional/non-manifold intermediate sets.

Primary sources:

- Nef 3 package: https://doc.cgal.org/latest/Nef_3/group__PkgNef3Ref.html
- class reference: https://doc.cgal.org/latest/Nef_3/classCGAL_1_1Nef__polyhedron__3.html

Important caution:

- current Nef 3 package licensing and dependency implications must be investigated before any source-level integration proposal;
- Nef polyhedra operate in a polyhedral domain and do not by themselves solve analytic STEP B-rep reconstruction.

## Manifold mesh-Boolean baseline

The Manifold project explicitly targets topologically robust manifold triangle-mesh operations and describes a precision/error model based on epsilon-valid geometry.

Primary sources:

- project: https://github.com/elalish/manifold
- algorithm/library notes: https://github.com/elalish/manifold/wiki/Manifold-Library

Implication: Manifold is useful both as a candidate intermediate representation and as prior art for separating accrued numerical error/precision from naïve exact coordinate equality. It does not automatically satisfy the programme's analytic STEP requirement.

## OCCT Boolean/tolerance research targets

The OCCT audit and later experiments inspect current source/docs for at least:

- BOPAlgo / BRepAlgoAPI Boolean pipeline;
- fuzzy value/tolerance options;
- non-destructive modes;
- General Fuse / cell-building facilities;
- same-domain unification;
- shape healing;
- Boolean history/provenance facilities;
- validators such as `BRepCheck_Analyzer`;
- sweep/pipe construction relevant to cutter envelopes.

RCS-004 provides the initial source-based classification. RCS-006 and later research must measure behaviour on the common fixture corpus before source-level modification is justified.

## Research-source hierarchy

Prefer, in order:

1. standards or normative specifications when legally/technically accessible;
2. upstream source code and versioned official documentation;
3. peer-reviewed or primary research papers;
4. upstream issue/PR discussions demonstrating concrete edge cases;
5. reproducible local experiments;
6. secondary technical summaries.

Any conclusion that drives architecture should state which category supports it.

## Source pinning rule

Experiments must record exact versions/commits of external dependencies. `Current OCCT` is not a reproducible result.
