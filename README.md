# radiCADSAC

Founding research and planning repository for **Machinist Simulation Aided Creation (MSAC)** and the **OpenSimachinist** manufacturing-geometry/STEP backend.

This repository is intentionally a **genesis/R&D record**, not either production implementation repository. It preserves the original programme intent, competing hypotheses, rejected approaches, experiments, and the eventual clean founding handoffs from which separate MSAC and OpenSimachinist repositories will be created.

## North star

MSAC is a new class of CAD interaction: **Simulation Aided Creation**. The user creates engineering geometry by operating simulated manufacturing tools rather than by negotiating a conventional CAD feature/sketch workflow.

The initial target user is an experienced machinist who is also comfortable with console-game controls. Initial machine scope is deliberately narrow: **lathe and mill only**.

The exported engineering object is the product. A successful workpiece must be exportable as a **valid, conventional, usable STEP solid**. STL is useful as a derived convenience format, but is not an architectural fallback.

## Repository role

The planning repository may be messy, speculative, contradictory, and research-heavy. The later production repositories should not inherit that archaeology. Instead, this repo will produce frozen founding handoffs containing fresh, reviewed implementation plans.

See `docs/` for the RAG research corpus and the GitHub issues for the autonomous research sequence.
