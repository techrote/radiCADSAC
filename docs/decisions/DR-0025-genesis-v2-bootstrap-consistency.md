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

## Consequences

- Current root routing and handoff manifests point to Genesis-v2 consistency revision 2.1.
- The original Genesis-v1 and RCS-027 freeze identities remain archaeology.
- A saved project can recover accepted pending intent without serializing provider-private state or falsely advancing the revision graph.
- Body splitting/merging cannot depend on lower-dimensional contact or backend enumeration.
- RCS-025 remains useful coordinator-policy evidence without being misread as live fallback→B-rep qualification.
- RCS-026 100k-event evidence remains useful coordinator/platform evidence without being misread as 100k native geometry operations.

## Reversibility

The persistence encoding and transport of pending-intent transactions remain production implementation choices. The semantic distinction between pending intent and committed revision, explicit body-transition identity, evidence-class honesty and immutable evidence pins require an explicit superseding decision to change.
