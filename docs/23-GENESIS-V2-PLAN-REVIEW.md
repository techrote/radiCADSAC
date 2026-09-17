# Genesis v2 plan review

Status: completed planning review; feeds `24-GENESIS-V2-REVISED-ROADMAP.md`  
Date: 2026-09-17

## Review objective

This review challenges `22-GENESIS-V2-INITIAL-PLAN.md` using the repository research method rather than assuming that more issues automatically means better research.

The review asks whether each proposed campaign changes a foundational decision, supplies an independent correctness oracle, avoids duplicating another campaign, and can be completed autonomously without turning radiCADSAC into a production implementation repository.

## What the initial plan gets right

The first draft correctly identifies the architecture risks that remain material after RCS-017:

- individually successful abstractions have not been exercised together end-to-end;
- canonicalization semantics are more specified than empirically qualified;
- the axisymmetric lathe solver has not yet been fed realistic tool-derived envelopes;
- arbitrary manual milling still lacks a qualified authoritative fallback;
- STEP Layer-D interoperability remains unqualified;
- operation-local uncertainty is not yet a propagated computational model;
- hybrid fallback reconciliation/provider transitions remain under-tested;
- Windows/scale/soak/fault behavior is weakly covered;
- a current-OCCT differential could materially reduce backend-private work.

These are appropriate Genesis-v2 topics because failure could change architecture or stable contract choices rather than merely implementation tuning.

## Problems in the first draft

### 1. Fallback research is over-fragmented

The first draft separates freehand material oracles, dexels, and external mesh/volumetric engines into three issues. That risks producing three incomparable toy studies and serializing work unnecessarily.

**Improvement:** one manual/freehand mill campaign should define an independent physical/material oracle first, then compare machining-native multi/tri-dexel material models and at least one externally maintained mesh/volumetric candidate on the same decisive fixtures. Candidate implementation is subordinate to the manufacturing question.

### 2. Architecture synthesis and handoff generation are too fragmented

A separate synthesis issue followed by three more handoff/freeze issues repeats the RCS-013–RCS-016 sequence even though Genesis v2 is deliberately narrower.

**Improvement:** keep one final Gate-5 issue. It must first synthesize evidence and update/supersede decisions, then generate **new v2 handoff trees** and a v2 freeze manifest. It may not mutate Genesis-v1 package identity.

### 3. The integrated slice must not become a prototype product

An end-to-end executable spike can easily expand into an unofficial OpenSimachinist implementation.

**Improvement:** constrain it to contract/instrumentation work: deterministic journal fixtures, request/response/status transitions, lineage/revision assertions, provider stubs/adapters around accepted research workers, explicit reconciliation points, process supervision and STEP handoff. Rendering, Godot integration, production persistence/RPC, UI and performance engineering remain out of scope.

### 4. Mill correctness cannot use OCCT segment sweep as the only oracle

RCS-011 often uses per-segment OCCT removal as the reference. That is useful but not independent precisely in the pathological cases where OCCT behavior is under investigation.

**Improvement:** Genesis v2 requires at least one independent material-set oracle for freehand fixtures. Agreement between two OCCT constructions is supporting evidence, not physical truth.

### 5. Real lathe tooling must be tested upstream of the 2D solver

Simply adding more RCS-010 target profiles would deepen the wrong layer. The important missing experiment is deriving the rotational material envelope from representative insert/tool geometry, orientation and machine motion.

**Improvement:** qualify nose radius/orientation, representative external/internal tools, grooving/parting and an undercut/reachability boundary before deciding the first-class provider capability predicate.

### 6. STEP interoperability must fail closed

A planning issue that can close after OCCT write/read-back or an OCCT-based second application would merely rename existing evidence.

**Improvement:** the Layer-D issue must record implementation independence of each parser/consumer. If no genuinely independent downstream solid consumer is available, the issue remains open or records a precise blocker; it may not silently mark the export profile qualified.

### 7. Cross-platform testing should consume matured research harnesses

Running Windows variants of every early smoke test independently would duplicate effort and make findings hard to compare.

**Improvement:** create one late qualification campaign that runs the canonicalizer, worker, provider-transition, replay and export evidence on Windows/MSVC and Linux with scale/soak/fault injection.

### 8. The uncertainty issue needs measurable propagation, not more terminology

RCS-007 already established separate channels and a local defer policy. Another prose model would add little.

**Improvement:** require executable propagation through transforms, canonicalization error, tool-envelope construction, Boolean/reconciliation boundaries and export metrics, with explicit conditions for decisive classification versus `accepted_pending`/ambiguity.

### 9. Current OCCT research should be a differential, not a rolling-upgrade project

Moving the whole programme to an unqualified new OCCT version during research would confound results.

**Improvement:** keep 8.0.1 as the control; pin one current stable/current-upstream candidate separately; reproduce decisive failures and the RCS-017 concurrency leak; investigate BRepGraph/history facilities strictly as backend-private implementation aids; recommend upgrade/no-upgrade with evidence.

## Revised issue count

The review reduces the initial 13 work packages to **10 RCS issues**:

- six parallel or near-parallel foundation campaigns;
- one provider/reconciliation integration stress campaign;
- one cross-platform/scale qualification campaign;
- one integrated contract vertical-slice campaign that begins early and remains research-only;
- one final Gate-5 synthesis + v2 handoff/freeze issue.

This is deliberately small enough to finish, but broad enough that the remaining implementation unknowns should no longer threaten the foundational semantic/API/provider/export boundaries.

## Dependency principles after review

1. RCS-018 creates an executable integration substrate but does not block all domain research.
2. RCS-019 through RCS-024 fan out primarily from Genesis-v1 evidence and may proceed in parallel where their individual dependencies are satisfied.
3. RCS-025 consumes the realistic provider/fallback/uncertainty/upstream evidence and stresses transitions/reconciliation.
4. RCS-026 is late cross-platform/scale/soak qualification over the matured research paths.
5. RCS-027 is the sole Gate-5 synthesis/re-freeze issue and cannot begin until RCS-018 through RCS-026 are accepted.

## Genesis-v1 preservation rule

The existing `handoffs/opensimachinist/`, `handoffs/msac/`, and `handoffs/genesis-release-v1.json` are historical Genesis-v1 artifacts. Genesis v2 must create new versioned package paths/manifests instead of rewriting v1 package identity or pretending the earlier freeze contained later evidence.

## Review conclusion

The improved programme should emphasize **independent physical oracles, integration transitions, real tool/process geometry, independent downstream STEP evidence, and cross-platform qualification**. Generic library exploration is useful only when tied to one of those falsifiable questions.
