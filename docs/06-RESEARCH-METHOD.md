# Research method and evidence standard

Status: current programme method  
Date: 2026-09-16

## Purpose

This document makes research issues falsifiable and comparable. It exists to prevent architecture from being selected by anecdote, familiarity or one-off demos.

## Research unit

Each investigation should identify:

- **question** — what is being decided or learned;
- **hypothesis** — the predicted outcome;
- **baseline** — the existing approach used for comparison;
- **fixture set** — deterministic inputs;
- **metrics** — what is measured;
- **falsification criteria** — what would make the hypothesis fail;
- **result** — observed evidence;
- **interpretation** — what follows and what does not;
- **decision impact** — which programme choices the result changes.

## Evidence classes

Label claims where ambiguity matters:

- **MEASURED** — produced by a reproducible experiment in this repository;
- **SOURCE** — directly supported by a cited primary source;
- **INFERENCE** — reasoned conclusion from evidence;
- **PROPOSAL** — architecture/design idea not yet validated;
- **OPEN** — unresolved question.

A proposal must not silently become an accepted constraint because it appears in several documents.

## Reproducibility requirements

Experiments must record:

- operating system/toolchain where relevant;
- compiler and flags;
- external dependency version/commit;
- fixture/version identifiers;
- tolerance/policy configuration;
- seed if randomness exists;
- exact command(s) to reproduce;
- machine-readable output where practical.

## Determinism

Geometry experiments should be repeated enough to detect nondeterminism. If bitwise determinism is not expected, define the weaker invariant being tested, such as equivalent topology and bounded geometric deviation.

## Failure taxonomy

Do not collapse all failures into “Boolean failed”. Record at least:

- rejected input;
- algorithm returned error/status;
- invalid topology;
- valid topology but wrong geometry;
- geometric tolerance breach;
- crash;
- hang/timeout;
- excessive runtime;
- excessive memory;
- nondeterministic result;
- STEP writer failure;
- STEP round-trip failure;
- downstream consumer failure.

## Geometry comparison

Where applicable compare:

- bounding box;
- volume;
- surface area;
- representative dimensions;
- Hausdorff/point-sampled surface deviation or another explicitly justified distance metric;
- topology counts;
- analytic surface classes retained/lost;
- smallest/degenerate feature statistics.

Never use only “looks correct in the viewer”.

## Performance measurement

Performance research should separate:

- canonicalization time;
- exact geometry update time;
- validation time;
- STEP export/re-import time;
- preview update time if tested;
- peak/resident memory where practical.

Warm-up/caching effects must be documented.

## Fixture discipline

Fixtures derived from real MSAC failures should preserve:

1. original operation journal or trace where allowed;
2. minimized reproducer;
3. expected physical intent;
4. baseline results across supported backends/versions;
5. regression status.

Do not minimize away the manufacturing semantics merely to make a generic CAD testcase unless both forms are retained.

## Negative results

A negative result is a deliverable when it is reproducible and explains why a plausible approach is unsuitable.

Examples:

- non-transitive virtual equivalence breaks topology consistency;
- exact arithmetic solves predicate ambiguity but is too expensive for a specific workload;
- mesh fallback survives Booleans but cannot reconstruct required analytic STEP geometry within tolerance;
- a process recognizer misclassifies natural freehand motion often enough to be unsafe.

Record such outcomes under the relevant research directory and link them from the issue/decision record.

## Decision records

Architecture-impacting conclusions should create/update a decision record under `docs/decisions/`.

Accepted decisions must say:

- what evidence supports them;
- what remains unknown;
- what would cause reconsideration;
- whether the choice is reversible before/after production handoff.

## Pull request quality gate

A research PR is ready to merge only when:

- issue acceptance criteria are satisfied;
- claims are sourced or measured appropriately;
- reproduction instructions are present for experiments;
- generated/derived data is identified;
- automated checks pass;
- docs are reconciled rather than contradicted silently;
- unresolved questions are explicitly carried forward.

## Scope control

The goal is not to solve computational geometry universally. Prefer the narrowest experiment that answers an MSAC/OpenSimachinist architecture question.

When a rabbit hole is valuable but not blocking, document it as a follow-up issue rather than expanding the current issue indefinitely.
