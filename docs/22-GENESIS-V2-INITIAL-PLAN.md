# Genesis v2 initial research plan

Status: initial planning proposal; deliberately superseded by the reviewed plan in `24-GENESIS-V2-REVISED-ROADMAP.md`  
Date: 2026-09-17  
Baseline: `main` at `6638a09d3ec6605b7bab0ccaa1cb4b380ad1f910` after RCS-017

## Purpose

Genesis v1 established a defensible semantic-provider hybrid architecture and clean handoff packages, but several architecture-driving conclusions were supported by smoke-scale experiments rather than integrated qualification. Genesis v2 exists to deepen evidence **before** the two production repositories harden those choices into costly implementation structure.

This tranche does not reopen high-confidence programme invariants merely because more research is possible. It targets decisions whose implementation shape could still change materially when exposed to real tool envelopes, manual/freehand machining, provider transitions, cross-platform execution, current OCCT behavior, and independent STEP consumers.

## Evidence basis

Genesis v2 starts from the accepted outputs of RCS-001 through RCS-017, especially:

- `docs/10-CANONICAL-JOURNAL-CONTRACT.md`;
- `docs/13-STEP-CONFORMANCE-CONTRACT.md`;
- `research/rcs-007/measured-summary-v1.json` through `research/rcs-012/measured-summary-v1.json`;
- `docs/20-OPENSIMACHINIST-ARCHITECTURE-SYNTHESIS.md`;
- `research/rcs-013/unresolved-v1.json`;
- `handoffs/genesis-release-v1.json`;
- `docs/21-OCCT-CONCURRENCY-ISOLATION.md` and RCS-017 measured evidence.

Genesis v1 handoffs remain historical evidence. Genesis v2 must not rewrite their original meaning.

## High-confidence decisions not reopened by default

The following remain the baseline unless new evidence directly falsifies them:

- STEP is the mandatory primary engineering output.
- The canonical manufacturing journal owns durable manufacturing intent.
- Backend-private OCCT/Godot topology/object identity is not durable programme identity.
- Machine/process semantics cross the MSAC/OpenSimachinist boundary explicitly.
- Material-body split/merge state is explicit and disconnected bodies are not silently discarded.
- A single enlarged global fuzzy epsilon is not programme truth.
- Semantic lineage, not transient topology identity, owns durable ancestry.
- Preview geometry is derived and non-authoritative.
- Process-isolated OCCT workers are the founding scheduler-level safety boundary.

## Architecture risks requiring deeper evidence

### A. Integration risk

The selected journal, lineage, uncertainty, provider, deferred-state, reconciliation, worker and STEP abstractions were primarily tested in separate campaigns. Genesis v2 needs an executable research-only vertical slice that exercises their contracts together.

### B. Canonicalization risk

RCS-002 is mostly a logical contract. Integer nanometres/nanoradians, q15 rotations, transform rules, bounded fitting and deterministic segmentation need executable cross-implementation conformance vectors and platform qualification.

### C. Lathe-provider risk

RCS-010 begins with an oracle-derived completed axisymmetric removal envelope. Real insert nose radius/orientation, boring-tool geometry, grooving/parting and undercuts remain unqualified upstream of the successful 2D material-domain solver.

### D. Manual mill risk

RCS-011 proved that unrestricted freehand batching can return valid-but-wrong material and that dense sampled-pose B-rep fallback is intractable. Arbitrary manual motion therefore remains the largest capability hole in a product built around direct simulated machining.

### E. STEP interoperability risk

RCS-005 Layer D requires independent parser/downstream-consumer evidence. OCCT writer/read-back evidence does not qualify a production exporter profile by itself.

### F. Uncertainty-model risk

RCS-007 strongly falsifies global fuzzy tolerance but the operation-local interval model is still a decision policy rather than a complete propagated uncertainty algebra spanning canonicalization, transforms, tool envelopes, provider conversion and reconciliation.

### G. Hybrid/reconciliation risk

RCS-012 proved that local alternative representations can be useful, but executable prototypes were deliberately narrow. Real fallback-to-B-rep stitching and repeated provider handoff remain unqualified.

### H. Platform/scale risk

Most decisive runtime evidence was generated on Ubuntu CI. Windows/MSVC behavior, long-running worker pools, 10k–100k operation histories, replay/export soak, memory growth and fault recovery remain lightly tested.

### I. Upstream-differential risk

The founding OCCT baseline is pinned to 8.0.1. Current upstream behavior may have changed around STEP concurrency, history/topology graph facilities and Boolean robustness. Genesis v2 should determine whether any backend-private implementation choices should use a newer pinned baseline without changing programme semantics.

## Initial candidate work packages

The first draft intentionally errs toward separation of concerns:

1. integrated semantic vertical-slice/reference harness;
2. canonicalizer determinism and conformance;
3. realistic lathe tool-envelope derivation;
4. freehand mill independent material oracle;
5. machining-native dexels/tri-dexels fallback experiment;
6. external mesh/volumetric fallback qualification (Manifold/OpenVDB/targeted exact arithmetic);
7. STEP Layer-D independent interoperability qualification;
8. propagated uncertainty/error-budget model;
9. current OCCT differential, concurrency minimization and BRepGraph investigation;
10. provider-handoff/deferred-state/reconciliation torture campaign;
11. Windows/cross-platform scale/soak/fault-recovery qualification;
12. Genesis v2 architecture synthesis;
13. separate OpenSimachinist/MSAC v2 handoff regeneration and final freeze.

## Initial dependency idea

Work packages 2–9 can fan out after the planning baseline. The integrated vertical slice should begin early and produce reusable instrumentation but must not become production code. Provider-handoff stress consumes the decisive provider/fallback/uncertainty results. Cross-platform soak consumes the integrated slice and matured research harnesses. Architecture synthesis and re-freeze occur only after all foundation-affecting evidence has landed.

## Initial stopping rule

Genesis v2 ends when the remaining unknowns can reasonably be owned by implementation without threatening the stable journal/API/STEP/provider boundaries. It does **not** require a universal geometry kernel, general five-axis machining, live-tool turning, final game UX, or release packaging.

## Review requirement

Before issues are emitted, this draft must be reviewed for:

- unnecessary issue fragmentation;
- duplicated experiments;
- circular dependencies;
- missing independent oracles;
- experiments that accidentally implement production code;
- acceptance criteria that can pass despite physically wrong results;
- any v2 work that can safely remain a production issue rather than genesis research.
