# Source baseline and external research anchors

Status: initial source map; expand during issues  
Date: 2026-09-16

## Purpose

This file records the initial external technical anchors used to prevent the planning programme from relying on stale assumptions or anecdote. Later issues should add primary sources and pin exact versions where experiments depend on them.

## OCCT current baseline

At the founding date, the latest published Open CASCADE Technology release is **8.0.1**, released 2026-07-30.

Primary source:

- OCCT releases: https://github.com/Open-Cascade-SAS/OCCT/releases

Relevant 8.0.1 release-note themes include:

- Boolean/periodic-curve stability fixes;
- shape-healing robustness fixes;
- performance work around face validation and coincident curve-on-surface checks;
- STEP export reliability fixes;
- C++17/API baseline retained from 8.0.0p1.

Implication: the programme must benchmark a pinned 8.0.1 baseline rather than infer current behaviour from older OCCT versions.

## OCCT licensing baseline

OCCT source is distributed under GNU LGPL 2.1 with the Open CASCADE exception.

Primary sources:

- repository: https://github.com/Open-Cascade-SAS/OCCT
- exception text: https://github.com/Open-Cascade-SAS/OCCT/blob/master/OCCT_LGPL_EXCEPTION.txt

The deep-fork research issue must verify obligations and compatibility in detail before combining derived code with other libraries.

## CGAL exact geometry baseline

CGAL provides kernels with exact predicates and exact constructions, which are relevant to robustness research even if they are not selected as the final backend.

Primary sources:

- kernel manual: https://doc.cgal.org/latest/Kernel_23/index.html
- exact-predicates/exact-constructions kernel: https://doc.cgal.org/latest/Kernel_23/classCGAL_1_1Exact__predicates__exact__constructions__kernel.html

Implication: “floating point plus larger epsilon” is not the only robustness strategy worth evaluating.

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

## STEP/OCCT research targets

The STEP conformance issue should inspect current OCCT 8.0.x documentation/source for at least:

- `STEPControl_Writer`;
- transfer modes for manifold solid B-rep / brep-with-voids;
- shape healing applied before/while writing;
- tolerances transferred into STEP;
- XDE/STEPCAF capabilities if metadata becomes relevant;
- thread-safety and determinism constraints;
- read-back validation.

Do not assume that successful `STEPControl_Writer::Write()` is equivalent to programme-level conformance.

## OCCT Boolean/tolerance research targets

The OCCT audit should inspect current source/docs for at least:

- BOPAlgo / BRepAlgoAPI Boolean pipeline;
- fuzzy value/tolerance options;
- non-destructive modes;
- General Fuse / cell-building facilities;
- same-domain unification;
- shape healing;
- Boolean history/provenance facilities;
- validators such as `BRepCheck_Analyzer`;
- sweep/pipe construction relevant to cutter envelopes.

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

Experiments must record exact versions/commits of external dependencies. “Current OCCT” is not a reproducible result.
