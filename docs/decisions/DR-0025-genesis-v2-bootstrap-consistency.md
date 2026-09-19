# DR-0025 — Genesis-v2 bootstrap consistency and pending-intent durability

Status: accepted consistency clarification  
Date: 2026-09-19  
Issue: #60  
Scope: production-bootstrap contract consistency only; no new geometry research result

## Context

RCS-027 accepted Gate 5 and froze Genesis-v2 packages, but a post-campaign review found six bootstrap inconsistencies: package manifests still carried the pre-Windows `candidate_gate5_pending_windows_step` status; root routing still emphasized Genesis v1; production issue prompts referenced evidence by research name rather than immutable file identity; `accepted_pending` wording differed between RCS-018 and the architecture synthesis; material-body connectivity wording was not precise enough around lower-dimensional contact; and synthesis sometimes used one broad "measured" label for native geometry and deterministic policy models.

None of those findings falsifies an accepted native geometry result. They can, however, cause two autonomous production implementations to preserve different project meaning.

## Decision

### Current bootstrap revision

The current bootstrap handoff is Genesis v2 **consistency revision 2.1**. The original RCS-027 merge SHA, release-manifest blob and package tree SHAs remain recorded as historical freeze identities. The correction updates current package content explicitly rather than pretending the original tree hashes meant something different.

### Pending intent

`accepted_pending` means durable programme-owned manufacturing intent whose engineering realization is unresolved.

Before the application acknowledges that state, it persists a **pending-intent transaction** anchored to the last committed workpiece revision. The transaction contains the ordered canonical operation(s), immutable setup/tool/frame/policy references, signed intent, source/audio/provenance references and error/reconciliation context needed to restart.

The pending transaction is not a committed workpiece revision and does not allocate a material-body transition before connectivity is resolved. Provider-private B-rep/dexel/mesh/cache/worker state is disposable. Save/crash/restart reloads the committed parent plus pending transactions and reruns derived work. Cancellation/refusal closes the transaction explicitly without rewriting the parent revision.

### Material-body connectivity and identity

For one regularized material set, candidate geometric components are closures of connected components of the material interior. Point/edge-only contact therefore does not create a volumetric bridge. Face-coincident geometry may form one geometric component only when the regularized union contains an interior neighbourhood across it.

Durable body identity is stronger than backend connectivity. Two distinct programme body IDs never merge merely because reconstructed/kernel geometry touches, overlaps within tolerance or is returned as one solid. A merge requires explicit programme/process semantics, validated material result and a recorded body transition.

### Evidence claim classes

Architecture-impacting synthesis distinguishes `MEASURED_NATIVE_GEOMETRY`, `MEASURED_INDEPENDENT_ORACLE`, `MEASURED_DETERMINISTIC_MODEL`, `MEASURED_PLATFORM_PROCESS`, `SOURCE`, `INFERENCE`, `PROPOSAL`, and `OPEN`.

Model evidence can qualify the policy/model question it executes. It cannot, by label or repetition count, become native geometry qualification.

### Exact evidence dependencies

Production bootstrap consumes the immutable vectors/results listed in `handoffs/evidence-dependencies-v2.1.json`. Each entry records the exact radiCADSAC source commit and Git blob SHA. Production repositories may copy those fixture contents, but must retain provenance and deliberately requalify any changed evidence/profile.

## Alternatives considered

### Leave the RCS-027 package manifests unchanged and rely on prose overlays

Rejected. Autonomous bootstrap must not require an agent to notice that a machine-readable package status contradicts the accepted release status. The original RCS-027 trees remain historical evidence, while consistency revision 2.1 makes the current route explicit.

### Commit `accepted_pending` directly as a workpiece revision before reconciliation

Rejected. That would allocate durable engineering revision/body meaning before connectivity and reconciliation are resolved, contradicting the fail-closed body/reconciliation contracts. Pending intent is durable transaction state anchored to the last committed revision instead.

### Persist provider-private pending geometry as the recovery source

Rejected. This would make save/recovery depend on one provider/kernel generation and violate journal/backend replaceability. Provider-private caches may accelerate recovery but remain disposable.

### Let kernel connectedness or topology identity define durable body identity

Rejected. Lower-dimensional contact and regenerated topology are not sufficient semantic evidence for split/merge identity. Durable body transitions remain explicit programme events.

### Keep a single generic `MEASURED` label in synthesis

Rejected for architecture-impacting claims. Native geometry, independent-oracle, deterministic-model and platform/process evidence answer different questions; flattening them can promote model evidence into an unsupported capability claim.

## Evidence

This decision is a consistency synthesis of already accepted evidence rather than a new geometry experiment.

- **SOURCE:** RCS-018 documents the pre-reconciliation transaction/status model and explicitly states that its executable slice is not a production persistence implementation.
- **SOURCE:** RCS-002 defines committed journal/revision/body-transition semantics and leaves deferred-state durability for later contracts.
- **SOURCE:** DR-0011/DR-0022 keep durable body/lineage identity independent of provider-private topology and require explicit reconciliation/body mapping.
- **SOURCE:** RCS-009 regularized material semantics preserve lower-dimensional contact as evidence without making it material volume.
- **SOURCE:** RCS-025 is implemented as a deterministic Python coordinator/policy model; its reconciliation work units and synthetic bounds are model evidence.
- **SOURCE:** RCS-026 separates its portable coordinator/100k history campaign from the live OCCT STEP soak; the 100k event tier is not native geometry-complexity qualification.
- **SOURCE:** RCS-027 accepted Gate 5 while the two package manifests still retained the pre-closure `candidate_gate5_pending_windows_step` string, creating the machine-readable handoff-status inconsistency corrected here.
- **MEASURED_DETERMINISTIC_MODEL / validation:** the issue-#60 consistency validator checks current package/release status agreement, historical freeze identities, exact predecessor blob pins, pending-intent/connectivity wording and evidence-class boundaries. Its adversarial controls deliberately reject stale Gate-5 package status and altered evidence blob identity.

## Consequences

- Current root routing and handoff manifests point to Genesis-v2 consistency revision 2.1.
- The original Genesis-v1 and RCS-027 freeze identities remain archaeology.
- A saved project can recover accepted pending intent without serializing provider-private state or falsely advancing the revision graph.
- Body splitting/merging cannot depend on lower-dimensional contact or backend enumeration.
- RCS-025 remains useful coordinator-policy evidence without being misread as live fallback→B-rep qualification.
- RCS-026 100k-event evidence remains useful coordinator/platform evidence without being misread as 100k native geometry operations.

## Reversibility

The persistence encoding and transport of pending-intent transactions remain production implementation choices. The semantic distinction between pending intent and committed revision, explicit body-transition identity, evidence-class honesty and immutable evidence pins require an explicit superseding decision to change.
