# Research plan review

Status: completed critique of `02-INITIAL-RESEARCH-PLAN.md`  
Date: 2026-09-16

## Executive finding

The initial plan had the right subject matter but was too linear and too implicitly anchored on “radical OCCT fork” as the destination. The revised programme should treat OCCT as a strong baseline and likely source substrate while deliberately testing alternatives and hybrid approaches.

The research must also establish **measurement and conformance definitions earlier**, otherwise later experiments can become opinion-driven.

## Review finding 1 — the sequence was too linear

### Problem

Several tracks are only weakly dependent:

- OCCT source audit;
- STEP conformance research;
- adversarial fixture design;
- operation-journal semantics;
- tolerance model research;
- lathe process reduction;
- alternative representation survey.

Serializing all of them behind one another would make a single research rabbit hole stall the programme.

### Improvement

Use gated parallel tracks after a small shared foundation:

- Foundation: contract + terminology + research method.
- Track A: operation journal / semantics.
- Track B: OCCT / baseline kernel audit.
- Track C: pathological corpus + measurement harness.
- Track D: tolerance/provenance/topology research.
- Track E: process-specific lathe/mill solver research.
- Track F: alternative/hybrid representation research.
- Track G: STEP conformance/export.

Synthesis happens only after evidence exists across the tracks.

## Review finding 2 — architecture was biased toward the presumed fork

### Problem

The founding conversation correctly allowed radical OCCT changes, but “fork OCCT” can become an anchoring bias. The actual requirement is manufacturing-native geometry with valid STEP output.

### Improvement

Research must compare at least these families where applicable:

- OCCT conventional B-rep / Boolean stack;
- heavily modified OCCT-derived stack;
- exact-predicate/exact-construction approaches;
- regularized/cell-complex approaches;
- robust manifold mesh Booleans as intermediate representations;
- implicit/level-set/SDF or voxel representations;
- process-specific analytic/2D reductions;
- hybrids combining more than one.

No alternative automatically satisfies the STEP requirement; conversion/reconciliation quality is part of the evaluation.

## Review finding 3 — “correct STEP” was underspecified

### Problem

Writing a `.step` file is much easier than proving the export is useful engineering geometry.

### Improvement

Define conformance separately from file serialization. Research should specify:

- topology validity;
- manifold/solid expectations;
- geometric tolerance policy;
- analytic surface preservation expectations;
- dimension and mass-property agreement;
- round-trip behaviour;
- independent consumer checks;
- failure reporting;
- how hybrid/internal approximations may be reconciled without lying about accuracy.

The STEP conformance track must start early, not at the end.

## Review finding 4 — no early baseline harness meant no falsifiability

### Problem

Research into tolerances, provenance or topology can produce plausible theory without showing measurable improvement over current OCCT behaviour.

### Improvement

Build the specification for an adversarial corpus and benchmark harness early. Every later geometry idea should be evaluated against the same fixtures and metrics.

Candidate metrics:

- success/failure/crash/hang;
- valid-solid result;
- geometric deviation;
- volume deviation;
- unexpected topology count;
- sliver/minimum feature statistics;
- repeatability/determinism;
- runtime and peak memory;
- topology growth across repeated operations;
- STEP export and re-import success;
- provenance preservation where applicable.

## Review finding 5 — operation normalization is a hidden core problem

### Problem

Raw gamepad/controller samples are not themselves a durable manufacturing language. If the canonical journal stores raw frame samples only, future replay may depend on frame rate, sampling jitter, deadzones or changing input code.

### Improvement

Research a versioned canonical operation representation between raw interaction and geometry. Preserve raw traces optionally for forensic/research use, but define deterministic normalization/canonicalization semantics.

This is also where line/arc/spline fitting, engagement segmentation, redundant-motion elimination and process identification may live.

## Review finding 6 — tolerance concepts were named but not given algebraic rules

### Problem

“Virtual tolerances” can become dangerous if equivalence is non-transitive or context-dependent in ways topology algorithms cannot reason about.

### Improvement

Tolerance research must explicitly study:

- equivalence relation properties;
- locality/context boundaries;
- provenance-conditioned equivalence;
- accumulation of numerical uncertainty;
- precedence/conflict rules between policy channels;
- reproducibility under replay;
- export collapse/reconciliation rules.

A tolerance system that cannot explain its merge decisions is not acceptable merely because it makes more Booleans succeed.

## Review finding 7 — provenance needs a stable identity model

### Problem

B-rep faces and edges are often regenerated by Boolean operations, making naïve object identity fragile.

### Improvement

Research topological/semantic naming and ancestry independently from any one kernel's transient entity IDs. Study how an exported face can be traced back to stock, tool envelope, operation and reconciliation events.

## Review finding 8 — “deferred topology” needs regularization semantics

### Problem

Deferring topology can merely postpone ambiguity unless the programme specifies what physical solid is intended when lower-dimensional contacts occur.

### Improvement

Investigate **regularized solid semantics** explicitly: manufacturing generally cares about volumetric material, not isolated zero-area faces/edges/points. Define when lower-dimensional sets are physically irrelevant, when they signal a real split/contact, and how that maps to export.

## Review finding 9 — lathe research should move earlier

### Problem

The lathe is unusually constrained and likely offers the fastest proof that manufacturing semantics can outperform naïve 3D Boolean modelling.

### Improvement

Start the axisymmetric/2D turning track as soon as the operation schema and corpus conventions are stable. It can progress in parallel with deeper general-kernel work.

## Review finding 10 — the mill track must separate easy analytic cases from freehand generality

### Problem

Treating all milling as “arbitrary swept cutter” discards useful classes such as drilling, facing and simple slots.

### Improvement

Research a hierarchy:

1. analytic process recognizers/explicit semantics;
2. bounded sweep constructions;
3. batched arbitrary trajectory sweeps;
4. hybrid fallback for pathological freehand cases.

## Review finding 11 — licensing/provenance must be researched before a deep fork

### Problem

OpenSimachinist may become a long-lived radical derivative. Source provenance, license obligations and ability to combine alternative libraries matter before architecture hardens.

### Improvement

The OCCT audit must include licensing and dependency compatibility. The programme should keep third-party source boundaries clear and record copied/derived components explicitly.

## Review finding 12 — clean handoff needs objective gates

### Problem

Without handoff gates, “research” can continue indefinitely.

### Improvement

OpenSimachinist handoff should require enough evidence to choose an initial architecture while explicitly leaving research tracks open. MSAC handoff should require a stable backend contract and a credible latency/replay/export model, not complete kernel perfection.

## Resulting plan changes

The revised plan therefore:

- keeps a small serial foundation;
- launches multiple evidence-producing tracks in parallel;
- moves fixtures/measurement and STEP conformance earlier;
- treats OCCT-forking as a hypothesis rather than a foregone conclusion;
- elevates operation normalization and semantic identity to first-class research;
- starts lathe specialization early;
- defines objective synthesis/handoff gates.

See `04-REVISED-RESEARCH-ROADMAP.md` for the resulting programme.
