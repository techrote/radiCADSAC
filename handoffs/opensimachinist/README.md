# OpenSimachinist founding handoff

Status: RCS-014 clean production-repository founding package  
Version: `opensimachinist-handoff/1.0`  
Date: 2026-09-17  
Selected architecture: `semantic-provider-hybrid-v1`

## Purpose

This directory is the clean founding specification intended to seed a future **OpenSimachinist** production repository. It is written for an implementation agent that has not read the founding conversation and should not need to reconstruct the rejected alternatives or chronological archaeology in `radiCADSAC` before beginning useful work.

The production repository must be created separately. RCS-014 does **not** create or populate it.

## Read this package in order

1. `00-FOUNDING-SPEC.md` — product/kernel purpose, invariants, programme API, architecture, solver boundaries, STEP contract, dependency/build assumptions and evidence map.
2. `01-IMPLEMENTATION-ROADMAP.md` — measurable implementation stages and vertical slices.
3. `02-INITIAL-ISSUE-GRAPH.md` — initial autonomous production issues with dependencies and acceptance criteria.
4. `03-UNRESOLVED-RESEARCH-REGISTER.md` — ranked unknowns, safe current policy, and explicit escape routes.
5. `04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md` — checklist for creating the production repository without importing genesis history.
6. `handoff-v1.json` — machine-readable handoff/Gate-3 manifest used by validation.

## What is authoritative in this package

The package inherits accepted programme decisions through RCS-013 and translates them into implementation requirements. Major inherited choices point back to accepted decision records and measured evidence, but the handoff text is deliberately fresh rather than a copy of the genesis reports.

The production project should treat these as founding constraints unless it records a later explicit decision with new evidence:

- the canonical manufacturing journal and semantic revision/lineage state are durable authority;
- geometry providers, B-reps, preview meshes and caches are replaceable derived state;
- the stable MSAC/OpenSimachinist boundary is semantic and versioned, never an OCCT/Godot object boundary;
- STEP is mandatory primary engineering output and success requires conformance, not merely a file writer return code;
- initial process scope is lathe and mill;
- pathological coincidence/tangency/retrace/sub-tolerance/high-operation-count workloads are normal inputs;
- material-body split/merge states are explicit and may not be silently discarded;
- separate tolerance/uncertainty/contact/export/validation policy channels are retained;
- process-specific solvers and bounded hybrid/deferred representations are allowed behind explicit capability/error contracts;
- OCCT 8.0.1 is the founding pinned B-rep/reconciliation/STEP baseline, isolated behind programme-owned adapters rather than exposed as the product model.

## Archaeology rule

Implementation agents may follow the evidence links in this package when a decision needs to be challenged or a failure needs to be reproduced. They should **not** import the genesis repository wholesale, copy historical issue threads into production, or reinterpret rejected proposals as requirements.

Negative research remains preserved in `radiCADSAC`. In particular, valid-but-wrong fuzzy/global-tolerance behavior, unproven freehand mill batching, dense sampled-pose B-rep fallback timeouts, and coarse voxel loss are constraints on implementation, not material to hide during handoff.

## Gate 3 statement

The handoff satisfies the roadmap's OpenSimachinist Gate-3 content requirements when merged and validated:

- an accepted initial backend architecture exists;
- the stable programme-facing contract is defined;
- unresolved research is explicit;
- the baseline corpus/benchmark strategy is available;
- dependency/license/upstream provenance policy is explicit;
- STEP acceptance is defined;
- the implementation roadmap is staged through measurable vertical slices.

Gate 3 means **implementation-ready with explicit escape routes**. It does not mean every pathological geometry problem or release qualification task is solved.
