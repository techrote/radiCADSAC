# Revised research roadmap

Status: current programme plan  
Date: 2026-09-16

## Programme structure

The research programme is intentionally **gated-parallel** rather than purely serial. A small foundation is completed first; then multiple tracks proceed independently enough that one rabbit hole does not stall the entire programme.

## Phase 0 — foundation

### R0.1 Founding brief and geometry contract

Already seeded by:

- `00-FOUNDING-BRIEF.md`
- `01-MSAC-GEOMETRY-CONTRACT.md`

Research must validate and refine these rather than assuming every sentence is correct forever.

### R0.2 Terminology and success definitions

Define unambiguous meanings for:

- SAC;
- MSAC;
- OpenSimachinist;
- workpiece;
- stock;
- setup;
- machine module;
- process;
- operation;
- canonical trajectory;
- preview geometry;
- authoritative geometry;
- valid solid;
- regularized solid;
- tolerance classes;
- STEP conformance.

### R0.3 Research method and evidence rules

Establish benchmark/fixture conventions, result recording, deterministic reproduction, source hierarchy and decision-record format.

## Track A — canonical manufacturing journal

### Objective

Define a durable manufacturing language between interactive simulation and geometry.

### Research questions

- What belongs in raw input traces versus canonical operations?
- How are controller/machine samples segmented into engaged operations?
- How are lines/arcs/splines or other curves fitted without falsifying user intent?
- How is path simplification bounded by explicit error?
- How are coordinate frames and setup changes versioned?
- How are tool definitions identified and frozen for replay?
- How are machine/process semantics encoded without coupling to Godot?
- How deterministic must replay be across platforms/kernel versions?
- How are undo/redo and branching history represented?

### Deliverables

- journal schema proposal;
- canonicalization policy;
- deterministic fixtures;
- compatibility/versioning strategy;
- provenance hooks required by later tracks.

## Track B — OCCT baseline and forkability audit

### Objective

Establish what current OCCT actually provides, where MSAC workloads fail, and which subsystems are suitable for reuse, isolation, replacement or radical modification.

### Baseline

At programme creation time the latest published OCCT release is **8.0.1** (30 July 2026). Upstream notes explicitly mention continued work on Boolean stability, shape healing and STEP export reliability, which reinforces the need to benchmark current behaviour rather than rely on old folklore.

### Audit areas

- topology/B-rep model;
- geometry primitives and curves/surfaces;
- Boolean pipeline and intersection classifiers;
- fuzzy tolerance behaviour;
- same-domain unification/healing;
- naming/history facilities;
- shape validation;
- sweeping/pipe machinery;
- meshing;
- STEP import/export and healing;
- threading/global state;
- memory/performance characteristics;
- build/platform burden;
- license and derivative-work obligations;
- feasibility of maintaining a deep fork.

### Deliverables

- subsystem map;
- MSAC-relevant failure/risk map;
- candidate fork seams;
- “reuse / wrap / replace / research” table;
- upstream version/provenance strategy.

## Track C — adversarial manufacturing corpus and measurement harness

### Objective

Turn pathological manufacturing geometry into reproducible evidence.

### Corpus families

#### Lathe

- exact repeated finishing pass;
- micron/sub-tolerance skim;
- tangent shoulder touch;
- tool exactly meeting prior face;
- bore meeting existing shoulder;
- repeated facing to same plane;
- path reversal over same surface;
- noisy analogue feed around a nominal cylinder;
- extremely long series of redundant passes.

#### Mill

- cutter following an existing edge;
- exact coplanar face skim;
- tangent corner entry/exit;
- repeated identical slot;
- overlapping slots/pockets;
- tiny cusp left between passes;
- self-crossing freehand path;
- retraced path with jitter;
- sub-tolerance plunge;
- path touching fixture/workpiece boundaries;
- very high sample/segment count.

#### Generic

- coincident/coplanar solids;
- barely overlapping solids;
- lower-dimensional contact;
- near-degenerate slivers;
- tolerance accumulation chains;
- topology explosion sequences.

### Metrics

- operation completion/failure;
- crash/hang;
- result validity;
- deterministic repeatability;
- geometric and volume deviation;
- topology counts/growth;
- smallest face/edge statistics;
- runtime;
- peak memory;
- STEP export success;
- STEP re-import success;
- independent-consumer conformance where available.

### Deliverables

- fixture format;
- expected-result policy;
- baseline benchmark specification;
- minimized-regression procedure;
- result-report schema.

## Track D — tolerance, equivalence, provenance and topology semantics

### D1 Tolerance/equivalence research

Investigate:

- OCCT tolerance propagation and fuzzy Boolean behaviour;
- virtual/process-specific tolerance channels;
- numerical uncertainty tracking;
- manufacturing tolerance versus topological equivalence;
- transitivity and conflict handling;
- symbolic/controlled perturbation;
- reproducibility and tolerance accumulation;
- export-collapse rules.

### D2 Provenance/semantic identity

Investigate stable ancestry independent of transient B-rep entity IDs:

- stock origin;
- tool-envelope origin;
- operation origin;
- split/merge ancestry;
- same-domain equivalence;
- face/edge semantic naming;
- replay and export traceability.

### D3 Regularized/deferred topology

Investigate whether manufacturing should operate on regularized volumetric material sets rather than materializing every zero-dimensional/one-dimensional event immediately.

Questions include:

- when zero-volume contact can be ignored;
- when contact implies meaningful separation;
- representation of unresolved coincidence;
- delayed face/edge creation;
- canonicalization boundaries;
- validation before export.

## Track E — process-specific solvers

### E1 Lathe solver

Highest-priority specialization.

Test whether common turning can be represented as a 2D radius/axial material domain with robust planar operations, followed by exact reconstruction/revolution.

Compare against:

- repeated 3D cutter subtraction;
- batched 3D cutter sweeps;
- 2D envelope/material-domain approach.

Must include OD turning, facing and selected ID/boring cases before claiming general usefulness.

### E2 Mill solver hierarchy

Investigate a hierarchy rather than one universal swept-solid algorithm:

1. explicit/recognized analytic operations (e.g. drilling, facing where appropriate);
2. simple fixed-orientation sweeps;
3. batched cutter-envelope removal;
4. arbitrary canonicalized freehand sweep;
5. hybrid fallback for cases that remain pathological.

Measure robustness and fidelity against Track C fixtures.

## Track F — alternative and hybrid representations

### Objective

Prevent OCCT/B-rep assumptions from defining the solution space.

### Candidate families

- exact-predicate/exact-construction computational geometry;
- CGAL Nef/cell-complex ideas;
- robust manifold mesh Boolean approaches;
- implicit/SDF/level-set fields;
- sparse voxel/cell representations;
- CSG/deferred evaluation;
- analytic process-specific material fields;
- hybrid conversion/reconciliation pipelines.

### Evaluation criteria

- ability to survive coincidence/tangency;
- support for manufacturing-scale operation counts;
- preservation/recovery of analytic geometry;
- error bounds;
- conversion cost;
- provenance support;
- ability to reconcile to STEP B-rep;
- licensing/dependency implications;
- performance and memory.

No candidate should be accepted solely because it produces a watertight mesh.

## Track G — STEP conformance and reconciliation

### Objective

Define and prove what “valid, correct and usable STEP output” means for this programme.

### Research areas

- STEP solid entity/model choices;
- AP profile expectations appropriate to downstream use;
- B-rep validity before serialization;
- geometric tolerances;
- analytic versus spline/approximated surfaces;
- same-domain cleanup;
- healing policy;
- metadata/provenance possibilities;
- writer round-trip;
- independent CAD consumer tests;
- exact criteria for refusing export.

### Principle

Internal permissiveness ends at the export boundary. A visually plausible or manifold mesh is not enough.

## Integration gates

### Gate 1 — research-ready

Requires:

- stable-enough vocabulary;
- versioned founding geometry contract;
- research method;
- initial journal schema direction;
- initial adversarial fixture format;
- current OCCT baseline pinned.

After Gate 1, Tracks B–G can proceed substantially in parallel.

### Gate 2 — architecture-choice ready

Requires evidence covering:

- baseline OCCT behaviour on core fixtures;
- at least one tolerance/provenance model evaluated;
- lathe specialization evaluated;
- mill strategy evaluated on representative cases;
- at least one alternative/hybrid representation evaluated;
- STEP conformance criteria drafted and exercised.

Gate 2 does **not** require solving every pathological case.

### Gate 3 — OpenSimachinist handoff ready

Requires:

- initial backend architecture decision;
- stable programme-facing API/contract;
- explicit unresolved research register;
- baseline test corpus and benchmark design;
- licensing/provenance plan;
- STEP acceptance contract;
- staged implementation roadmap with measurable milestones.

### Gate 4 — MSAC handoff ready

Requires:

- backend boundary stable enough to consume;
- operation-journal/canonicalization contract;
- preview/exact reconciliation model;
- error/status model;
- machine-module extension contract;
- initial lathe/mill capabilities and limitations documented;
- productive-core-loop plan that does not wait for complete kernel research.

## Handoff outputs

When Gates 3/4 are met, generate fresh documents under:

- `handoffs/opensimachinist/`
- `handoffs/msac/`

These handoffs are the only material intended to seed the clean production repositories. The rest of `radiCADSAC` remains historical/research context.

## Programme stopping rule

Research should not attempt to perfect a universal CAD kernel before implementation starts.

The purpose of this repository is to produce enough validated knowledge to found productive projects with explicit escape routes. Open questions that can be tested during implementation should move into the relevant production roadmap rather than keeping the genesis phase open indefinitely.
