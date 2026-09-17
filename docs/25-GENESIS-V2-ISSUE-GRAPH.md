# Genesis v2 research issue graph

Status: current Genesis-v2 issue/dependency graph  
Date: 2026-09-17  
Planning basis: `22-GENESIS-V2-INITIAL-PLAN.md`, `23-GENESIS-V2-PLAN-REVIEW.md`, `24-GENESIS-V2-REVISED-ROADMAP.md`

## Purpose

This graph extends the completed Genesis-v1 RCS-001–RCS-017 programme. It does not renumber or rewrite Genesis-v1 issues. GitHub issue and pull-request numbers share one repository-wide sequence, so Genesis-v2 RCS keys map to GitHub issues #37–#46.

## Issues

| GitHub | Key | Research issue | Depends on | Primary output |
|---:|---|---|---|---|
| #37 | RCS-018 | Integrated semantic contract vertical slice | RCS-013, RCS-017, Genesis-v1 handoffs | executable end-to-end contract trace/instrumentation |
| #38 | RCS-019 | Canonicalizer conformance and deterministic normalization qualification | RCS-002, RCS-003, RCS-007 | cross-implementation canonicalizer conformance suite |
| #39 | RCS-020 | Realistic lathe tool-envelope derivation and provider qualification | RCS-002, RCS-007, RCS-008, RCS-009, RCS-010 | real-tool envelope evidence + refined lathe capability predicate |
| #40 | RCS-021 | Manual/freehand mill independent material oracle and bounded fallback campaign | RCS-002, RCS-003, RCS-007, RCS-009, RCS-011, RCS-012 | independent oracle + dexels/external fallback evidence |
| #41 | RCS-022 | STEP Layer-D independent interoperability qualification | RCS-005, RCS-006, RCS-010, RCS-011, RCS-017 | pinned exporter profile + independent consumer qualification state |
| #42 | RCS-023 | Propagated uncertainty and error-budget algebra | RCS-002, RCS-005, RCS-007, RCS-008, RCS-009, RCS-012 | executable cross-stage uncertainty/error-budget model |
| #43 | RCS-024 | Current OCCT differential, concurrency minimization and BRepGraph/history probe | RCS-004, RCS-006, RCS-007, RCS-008, RCS-011, RCS-017 | 8.0.1/current differential + backend baseline recommendation |
| #44 | RCS-025 | Provider handoff, deferred-state and reconciliation stress campaign | RCS-018, RCS-020, RCS-021, RCS-023, RCS-024 | mixed-provider/reconciliation stress evidence + resource policy |
| #45 | RCS-026 | Windows/Linux scale, soak and fault-recovery qualification | RCS-018, RCS-019, RCS-020, RCS-021, RCS-024, RCS-025 | cross-platform scale/soak/recovery qualification |
| #46 | RCS-027 | Genesis v2 synthesis, Gate-5 decision, v2 handoff regeneration and freeze | RCS-018–RCS-026 | final v2 architecture decisions + new v2 handoffs/freeze |

## Fan-out after planning merge

The planning merge is not itself a research dependency beyond making the authoritative Genesis-v2 docs available on `main`.

The first wave can proceed largely in parallel:

- RCS-018 / #37 — contract integration substrate;
- RCS-019 / #38 — canonicalizer conformance;
- RCS-020 / #39 — real lathe tool envelopes;
- RCS-021 / #40 — manual/freehand mill oracle/fallback;
- RCS-022 / #41 — STEP Layer-D qualification;
- RCS-023 / #42 — uncertainty/error propagation;
- RCS-024 / #43 — current OCCT differential.

RCS-018 is intentionally **not** a blanket blocker for the other first-wave campaigns. Each uses accepted Genesis-v1 outputs and can contribute independently.

## Integration wave

RCS-025 / #44 waits for the provider/fallback/uncertainty/upstream evidence it must integrate:

- RCS-018;
- RCS-020;
- RCS-021;
- RCS-023;
- RCS-024.

RCS-022 should be consumed where its exact STEP profile is relevant, but a blocked Layer-D consumer should not prevent RCS-025 from measuring internal handoff correctness; it must report export status honestly as unqualified where necessary.

## Platform/soak wave

RCS-026 / #45 consumes the mature research substrate:

- RCS-018 integration trace/harness;
- RCS-019 canonicalizer vectors;
- RCS-020 lathe capability;
- RCS-021 mill/fallback capability;
- RCS-024 accepted OCCT baseline recommendation;
- RCS-025 provider/reconciliation stress path.

It additionally consumes RCS-022 and RCS-023 where their evidence applies.

## Final Gate-5 synthesis

RCS-027 / #46 is strictly serial after RCS-018 through RCS-026. It may not infer completion from issue closure alone: it must read the accepted reports, negative results, machine-readable evidence and decision records.

Its output is a **new Genesis-v2 handoff/freeze**, not a mutation of Genesis-v1 identity.

## Critical-path interpretation

There are three practical critical paths:

1. **direct machining capability:** RCS-020 + RCS-021 → RCS-025 → RCS-026 → RCS-027;
2. **durable semantic correctness:** RCS-019 + RCS-023 → RCS-025/RCS-026 → RCS-027;
3. **engineering output/upstream substrate:** RCS-022 + RCS-024 → RCS-025/RCS-026 where applicable → RCS-027.

A negative result can still satisfy a research issue when it conclusively narrows capability and supplies a safe defer/handoff/refusal rule. A negative result cannot be converted into a pass by widening tolerances, hiding a body, substituting mesh output, or treating valid topology as correct material.

## Global autonomous-execution contract

Every issue #37–#46 contains its own execution prompt. In addition, all Genesis-v2 issues inherit the repository protocol:

1. read `AGENTS.md`, the founding docs, `06-RESEARCH-METHOD.md`, `24-GENESIS-V2-REVISED-ROADMAP.md`, this graph, declared predecessor outputs and applicable accepted decisions;
2. inspect current `main` before work;
3. state hypotheses/baseline/fixtures/metrics/falsification criteria;
4. prefer primary sources and pin external versions/commits;
5. preserve negative results and evidence classes;
6. add deterministic machine-readable evidence and RAG Markdown;
7. add/extend automated checks without breaking accepted regressions;
8. work on a branch, open a PR, repair CI, merge only after required automated checks pass, verify the merge landed on `main`, then close only when acceptance criteria genuinely hold;
9. if blocked, record exact evidence and stop rather than weakening acceptance criteria;
10. do not create production repositories unless explicitly authorized by a later user instruction.

## Genesis-v1 relationship

The completed Genesis-v1 issue graph remains historical evidence in `07-RESEARCH-ISSUE-GRAPH.md`. Existing Genesis-v1 handoff trees/manifests remain frozen in meaning. RCS-027 will create versioned Genesis-v2 package trees and a v2 freeze manifest after Gate 5 is genuinely satisfied.
