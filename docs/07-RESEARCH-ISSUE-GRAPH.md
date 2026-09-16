# Research issue graph

Status: planned issue graph; GitHub issue numbers are assigned at creation  
Date: 2026-09-16

## Dependency philosophy

The graph deliberately contains parallel tracks. “Depends on” means the issue should consume accepted output from that predecessor; it does not mean unrelated research must wait.

## Issues

| Key | Research issue | Depends on | Primary output |
|---|---|---|---|
| RCS-001 | Foundation audit: terminology, invariants and Gate-1 definitions | — | reconciled foundation + decision records |
| RCS-002 | Canonical manufacturing journal and deterministic normalization | RCS-001 | versioned operation/journal proposal |
| RCS-003 | Adversarial manufacturing geometry corpus specification | RCS-001 | fixture taxonomy + expected-result policy |
| RCS-004 | OCCT 8.0.1 architecture, robustness, forkability and license audit | RCS-001 | subsystem/fork map |
| RCS-005 | STEP conformance and downstream usability contract | RCS-001 | measurable STEP acceptance specification |
| RCS-006 | Baseline benchmark/validation harness design and spike | RCS-003, RCS-004, RCS-005 | reproducible baseline runner/results |
| RCS-007 | Virtual tolerance, uncertainty and equivalence research | RCS-003, RCS-006 | candidate tolerance models + evidence |
| RCS-008 | Provenance, semantic identity and topological naming research | RCS-002, RCS-006 | ancestry/identity model candidates |
| RCS-009 | Regularized solids and deferred-topology research | RCS-003, RCS-006 | semantics + prototype/experiment results |
| RCS-010 | Lathe-specialized material-domain solver research | RCS-002, RCS-003, RCS-006 | comparative turning solver evidence |
| RCS-011 | Mill cutter-sweep and process-hierarchy research | RCS-002, RCS-003, RCS-006 | comparative milling solver evidence |
| RCS-012 | Alternative/hybrid representation campaign | RCS-003, RCS-006 | B-rep alternatives/hybrid trade study |
| RCS-013 | OpenSimachinist architecture synthesis / Gate-2 decision | RCS-007–RCS-012, RCS-005 | evidence-backed initial architecture |
| RCS-014 | Generate clean OpenSimachinist founding handoff | RCS-013 | production-ready founding spec/roadmap |
| RCS-015 | Generate clean MSAC founding handoff | RCS-002, RCS-005, RCS-013 | production-ready MSAC spec/roadmap |
| RCS-016 | Freeze genesis handoff release and production-repo launch checklist | RCS-014, RCS-015 | tagged/frozen genesis handoff plan |

## Parallelism after RCS-001

Once RCS-001 is accepted, RCS-002 through RCS-005 can proceed in parallel.

After the baseline harness exists, RCS-007 through RCS-012 are intentionally parallel research campaigns. Individual issues may file narrower follow-ups when a rabbit hole is valuable but not blocking.

## Synthesis discipline

RCS-013 must not simply average earlier recommendations. It must:

- compare evidence against the same programme invariants;
- identify which conclusions are measured versus speculative;
- select an initial architecture with explicit escape routes;
- carry unresolved research into the OpenSimachinist roadmap rather than pretending it is solved;
- avoid requiring universal computational-geometry perfection before productive implementation can begin.

## Handoff discipline

RCS-014 and RCS-015 create **fresh documents** under `handoffs/`. They may cite genesis research, but must be readable without traversing the entire planning history.

RCS-016 should preserve this repository as the historical source and define the exact frozen handoff revision used to seed each production repository.
