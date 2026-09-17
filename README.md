# radiCADSAC

Founding research and planning repository for **Machinist Simulation Aided Creation (MSAC)** and the **OpenSimachinist** manufacturing-geometry/STEP backend.

This repository is intentionally a **genesis/R&D record**, not either production implementation repository. It preserves the original programme intent, competing hypotheses, rejected approaches, experiments, and the eventual clean founding handoffs from which separate MSAC and OpenSimachinist repositories will be created.

## North star

MSAC is a new class of CAD interaction: **Simulation Aided Creation**. The user creates engineering geometry by operating simulated manufacturing tools rather than by negotiating a conventional CAD feature/sketch workflow.

The initial target user is an experienced machinist who is also comfortable with console-game controls. Initial machine scope is deliberately narrow: **lathe and mill only**.

The exported engineering object is the product. A successful workpiece must be exportable as a **valid, conventional, usable STEP engineering result**. STL is useful as a derived convenience format, but is not an architectural fallback.

## Repository role

The planning repository may be messy, speculative, contradictory, and research-heavy. The later production repositories should not inherit that archaeology. Instead, this repo will produce frozen founding handoffs containing fresh, reviewed implementation plans.

## Current research foundation and accepted contracts

Start with:

- [Founding brief](docs/00-FOUNDING-BRIEF.md) — preserved product intent;
- [MSAC ↔ geometry contract](docs/01-MSAC-GEOMETRY-CONTRACT.md) — Gate-1 programme boundary;
- [Revised research roadmap](docs/04-REVISED-RESEARCH-ROADMAP.md) — current gated-parallel plan;
- [Research method](docs/06-RESEARCH-METHOD.md) — evidence and reproducibility rules;
- [Research issue graph](docs/07-RESEARCH-ISSUE-GRAPH.md) — issue dependencies;
- [Programme terminology](docs/08-TERMINOLOGY.md) — accepted research vocabulary;
- [Foundation audit](docs/09-FOUNDATION-AUDIT.md) — invariant/hypothesis split and Gate-1 reconciliation;
- [Canonical manufacturing journal contract](docs/10-CANONICAL-JOURNAL-CONTRACT.md) — accepted RCS-002 durable operation/history and normalization contract;
- [Adversarial manufacturing corpus](docs/11-ADVERSARIAL-MANUFACTURING-CORPUS.md) — accepted RCS-003 fixture semantics and regression lifecycle;
- [OCCT 8.0.1 audit](docs/12-OCCT-8.0.1-AUDIT.md) — accepted RCS-004 subsystem/forkability and licensing evidence;
- [STEP conformance contract](docs/13-STEP-CONFORMANCE-CONTRACT.md) — accepted RCS-005 measurable export success/refusal and interoperability contract;
- [Baseline benchmark harness](docs/14-BASELINE-BENCHMARK-HARNESS.md) — accepted RCS-006 measurement substrate;
- [Tolerance, uncertainty and equivalence research](docs/15-VIRTUAL-TOLERANCE-RESEARCH.md) — accepted RCS-007 separated policy channels;
- [Provenance and semantic identity research](docs/16-PROVENANCE-SEMANTIC-IDENTITY-RESEARCH.md) — accepted RCS-008 lineage/topological-naming architecture;
- [Regularized/deferred topology research](docs/17-REGULARIZED-DEFERRED-TOPOLOGY.md) — accepted RCS-009 regularized material and bounded deferred topology;
- [Lathe material-domain research](docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md) — accepted RCS-010 axisymmetric fixed-axis lathe provider evidence;
- [Mill cutter-sweep hierarchy research](docs/19-MILL-CUTTER-SWEEP-RESEARCH.md) — RCS-011 fixed-orientation mill strategy hierarchy and measured campaign;
- `docs/decisions/` — explicit programme decision records.

Issue-specific research should additionally consume accepted outputs from its declared dependencies. Machine-readable research assets live under the corresponding `research/rcs-NNN/` directory.

The historical initial plan and critique remain under `docs/` for design archaeology; newer accepted decisions and current foundation documents supersede speculative historical material where they conflict.
