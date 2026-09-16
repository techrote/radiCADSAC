# Research issue graph

Status: current issue graph; RCS-001–RCS-017 assigned (GitHub #1–#16 and #20)  
Date: 2026-09-16

## Dependency philosophy

The graph deliberately contains parallel tracks. `Depends on` means the issue should consume accepted output from that predecessor; it does not mean unrelated research must wait.

RCS-001 corrects the original Gate-1 wording so the graph is no longer circular: RCS-002/RCS-003 outputs are **not** prerequisites for starting RCS-002/RCS-003.

## Issues

| GitHub | Key | Research issue | Depends on | Primary output |
|---:|---|---|---|---|
| #1 | RCS-001 | Foundation audit: terminology, invariants and Gate-1 definitions | — | reconciled foundation + decision records |
| #2 | RCS-002 | Canonical manufacturing journal and deterministic normalization | RCS-001 | versioned operation/journal proposal |
| #3 | RCS-003 | Adversarial manufacturing geometry corpus specification | RCS-001 | fixture taxonomy + expected-result policy |
| #4 | RCS-004 | OCCT 8.0.1 architecture, robustness, forkability and license audit | RCS-001 | subsystem/fork map |
| #5 | RCS-005 | STEP conformance and downstream usability contract | RCS-001 | measurable STEP acceptance specification |
| #6 | RCS-006 | Baseline benchmark/validation harness design and spike | RCS-003, RCS-004, RCS-005 | reproducible baseline runner/results |
| #7 | RCS-007 | Virtual tolerance, uncertainty and equivalence research | RCS-003, RCS-006 | candidate tolerance models + evidence |
| #8 | RCS-008 | Provenance, semantic identity and topological naming research | RCS-002, RCS-006 | ancestry/identity model candidates |
| #9 | RCS-009 | Regularized solids and deferred-topology research | RCS-003, RCS-006 | semantics + prototype/experiment results |
| #10 | RCS-010 | Lathe-specialized material-domain solver research | RCS-002, RCS-003, RCS-006 | comparative turning solver evidence |
| #11 | RCS-011 | Mill cutter-sweep and process-hierarchy research | RCS-002, RCS-003, RCS-006 | comparative milling solver evidence |
| #12 | RCS-012 | Alternative/hybrid representation campaign | RCS-003, RCS-006 | B-rep alternatives/hybrid trade study |
| #13 | RCS-013 | OpenSimachinist architecture synthesis / Gate-2 decision | RCS-007–RCS-012, RCS-005 | evidence-backed initial architecture |
| #14 | RCS-014 | Generate clean OpenSimachinist founding handoff | RCS-013 | production-ready founding spec/roadmap |
| #15 | RCS-015 | Generate clean MSAC founding handoff | RCS-002, RCS-005, RCS-013 | production-ready MSAC spec/roadmap |
| #16 | RCS-016 | Freeze genesis handoff release and production-repo launch checklist | RCS-014, RCS-015 | tagged/frozen genesis handoff plan |
| #20 | RCS-017 | OCCT concurrency and global-state isolation probe | RCS-004, RCS-005, RCS-006 | measured thread/process isolation boundary |

GitHub issue and pull-request numbers share one repository-wide sequence, so RCS-017 is GitHub issue #20; #17–#19 are not missing research issues.

## Gate 1 and first fan-out

RCS-001 / GitHub #1 completes **Gate 1 — research-foundation ready** as defined in `04-REVISED-RESEARCH-ROADMAP.md` and `09-FOUNDATION-AUDIT.md`.

Once RCS-001 is accepted and merged, RCS-002 through RCS-005 can proceed in parallel:

- #2 / Track A — canonical journal;
- #3 / Track C — adversarial corpus;
- #4 / Track B — OCCT audit;
- #5 / Track G — STEP conformance.

The final journal schema and fixture format are outputs of #2/#3 and therefore are not Gate-1 prerequisites.

## Parallelism after the baseline harness

RCS-006 combines the corpus, OCCT audit and STEP contract into the shared baseline harness.

After RCS-006 exists, RCS-007 through RCS-012 are intentionally parallel research campaigns subject to their individual declared dependencies. Individual issues may file narrower follow-ups when a rabbit hole is valuable but not blocking.

RCS-017 is one such narrow follow-up: RCS-004 identified concurrency/global-state isolation as important but not appropriate to guess from source inspection alone. It waits for RCS-005/RCS-006 so it can stress the accepted STEP policy and common harness rather than inventing separate correctness criteria.

## Cross-cutting foundation requirements carried downstream

RCS-001 identified two requirements that must be explicit in early research rather than hidden assumptions:

1. **units / coordinate frames / transform semantics** — carried by RCS-002, RCS-003 and RCS-005;
2. **disconnected material bodies / parting / cut-through semantics** — carried by RCS-002, RCS-003 and RCS-005 initially, then RCS-008/RCS-009 for identity/connectivity research.

These requirements are added to the existing issue prompts rather than creating unnecessary serial blocker issues.

## Synthesis discipline

RCS-013 must not simply average earlier recommendations. It must:

- compare evidence against the same programme invariants;
- identify which conclusions are measured versus speculative;
- select an initial architecture with explicit escape routes;
- carry unresolved research into the OpenSimachinist roadmap rather than pretending it is solved;
- avoid requiring universal computational-geometry perfection before productive implementation can begin.

RCS-017 should be consumed by RCS-013 if it has completed by synthesis time. If not, RCS-013 must retain process isolation as an explicit reversible safety boundary rather than silently assuming thread-local OCCT state.

## Handoff discipline

RCS-014 and RCS-015 create **fresh documents** under `handoffs/`. They may cite genesis research, but must be readable without traversing the entire planning history.

RCS-016 should preserve this repository as the historical source and define the exact frozen handoff revision used to seed each production repository.
