# radiCADSAC

> **Current execution authority (19 September 2026):** MC-1 — Machining Completeness and Engineering Realization is the stronger pre-production research requirement. Start at [`handoffs/current-authority.json`](handoffs/current-authority.json) and [`docs/machining-completeness/00-PROGRAMME.md`](docs/machining-completeness/00-PROGRAMME.md). Genesis-v2.1 remains historical accepted foundation, but production bootstrap is on hold unless MC-1 passes and separate explicit authorization is later given.

Founding research and planning repository for **Machinist Simulation Aided Creation (MSAC)** and the **OpenSimachinist** manufacturing-geometry/STEP backend.

This repository is intentionally a **genesis/R&D record**, not either production implementation repository. It preserves the original programme intent, competing hypotheses, rejected approaches, experiments, and the eventual clean founding handoffs from which separate MSAC and OpenSimachinist repositories will be created.

## North star

MSAC is a new class of CAD interaction: **Simulation Aided Creation**. The user creates engineering geometry by operating simulated manufacturing tools rather than by negotiating a conventional CAD feature/sketch workflow.

The initial target user is an experienced machinist who is also comfortable with console-game controls. Initial machine scope is deliberately narrow: **lathe and mill only**.

The exported engineering object is the product. A successful workpiece must be exportable as a **valid, conventional, usable STEP engineering result**. STL is useful as a derived convenience format, but is not an architectural fallback.

## Repository role

The planning repository may be messy, speculative, contradictory, and research-heavy. The later production repositories should not inherit that archaeology. Instead, this repo will produce frozen founding handoffs containing fresh, reviewed implementation plans.

## Current programme boundary

**MC-1 is the current execution authority.** Genesis-v2.1 remains the accepted historical foundation/evidence package, not present production-start permission. Read `handoffs/current-authority.json`, DR-0026 and the MC-1 documents. Do not create/populate production repositories from the historical handoff while MC-1 is `NOT_ESTABLISHED`.

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
- [Mill cutter-sweep hierarchy research](docs/19-MILL-CUTTER-SWEEP-RESEARCH.md) — accepted RCS-011 fixed-orientation mill strategy hierarchy and measured campaign;
- [Alternative/hybrid geometry representation research](docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md) — accepted RCS-012 bounded hybrid fallback trade study;
- [OpenSimachinist architecture synthesis](docs/20-OPENSIMACHINIST-ARCHITECTURE-SYNTHESIS.md) — accepted RCS-013 Gate-2 semantic-provider hybrid architecture;
- [Genesis-v2 revised roadmap](docs/24-GENESIS-V2-REVISED-ROADMAP.md) — completed RCS-018–RCS-027 qualification tranche;
- [Genesis-v2 Gate-5 synthesis](docs/35-GENESIS-V2-SYNTHESIS-AND-GATE5.md) — accepted final research synthesis;
- [Genesis-v2 bootstrap consistency correction](docs/37-GENESIS-V2-BOOTSTRAP-CONSISTENCY.md) — historical v2.1 routing/durability/connectivity clarification, retained as evidence under MC-1;
- `docs/decisions/` — explicit programme decision records, including DR-0025.

Issue-specific research should additionally consume accepted outputs from its declared dependencies. Machine-readable research assets live under the corresponding `research/rcs-NNN/` directory.

The historical initial plan and critique remain under `docs/` for design archaeology; newer accepted decisions and current foundation documents supersede speculative historical material where they conflict.

## Historical genesis handoffs

The handoff index is [`handoffs/README.md`](handoffs/README.md). `handoffs/genesis-release-v2.json`, consistency revision `2.1`, and [`handoffs/evidence-dependencies-v2.1.json`](handoffs/evidence-dependencies-v2.1.json) remain the exact historical Genesis-v2 foundation/evidence package. They are **not current production-bootstrap authorization**.

Current execution authority is [`handoffs/current-authority.json`](handoffs/current-authority.json) → MC-1. Production repository creation requires a genuine MC-1 pass plus separate explicit authorization. Any eventual production repositories must start with fresh Git histories and may reference this repository for archaeology; they must not import radiCADSAC history as their production history.
