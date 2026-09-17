# MSAC integration escape routes and unresolved assumptions

Status: founding integration register  
Handoff: `msac-handoff/1.0`

## Purpose

MSAC can begin product implementation without pretending every backend, transport, controller or qualification question is solved. This register turns known uncertainty into explicit product behavior and replacement seams.

Each item states the safe founding policy. An escape route is not permission to fabricate engineering success; it is a way to keep the product moving while preserving manufacturing intent.

## Priority 1 — replaceable backend transport

ID: `replaceable-backend-transport`

**Open:** The semantic MSAC↔OpenSimachinist API is defined, but production transport/deployment is not permanently selected.

**Founding policy:** Keep semantic request/response types transport-independent. Hide local IPC/shared-library/RPC/GDExtension details behind one adapter.

**Escape route:** Swap transport without migrating journal/project meaning. Use a deterministic fake backend in frontend CI.

## Priority 2 — capability and contract-version discovery

ID: `capability-version-discovery`

**Open:** Frontend/backend may evolve independently.

**Founding policy:** Negotiate contract/capability versions explicitly and gate UI actions on supported semantics.

**Escape route:** Refuse unsupported combinations or run a tested compatibility adapter; never infer support from frontend version alone.

## Priority 3 — pathological mill pending/fallback/refusal

ID: `pathological-mill-pending-fallback-refusal`

**Open:** Arbitrary self-crossing/retraced/freehand milling is not generally qualified.

**Founding policy:** Commit manufacturing intent only when the backend contract can accept it under an explicit state; display `accepted_pending`, fallback qualification or refusal honestly.

**Escape route:** Preserve the canonical path as a regression fixture and allow later backend providers/fallbacks to replay it. Do not simplify it beyond certified bounds to force success.

## Priority 4 — lathe tool-envelope capability gating

ID: `lathe-tool-envelope-capability-gating`

**Open:** Real insert nose radius/orientation, difficult grooving/parting and non-axisymmetric/live-tool cases remain incompletely qualified.

**Founding policy:** Query provider capability against tool/process semantics before claiming authoritative support.

**Escape route:** Hand off to another provider, keep operation pending, or refuse. A visual-only uncommitted simulation may be offered if clearly labeled.

## Priority 5 — STEP interoperability qualification state

ID: `step-interoperability-qualification-status`

**Open:** Local writer/read-back conformance does not by itself prove independent CAD/CAM interoperability.

**Founding policy:** Preserve the four-layer STEP success model and show `interoperability_unqualified` until Layer D evidence exists.

**Escape route:** Add independent consumer qualification records later without changing project/journal semantics. Never label a local-only result fully qualified.

## Priority 6 — deferred reconciliation state

ID: `deferred-reconciliation-state`

**Open:** Backend may safely defer topology/material work for some operations.

**Founding policy:** Product model explicitly distinguishes pending from reconciled. Exact topology-dependent inspection/export can request reconciliation.

**Escape route:** If reconciliation is expensive, keep UI responsive and show progress/status; if it fails, preserve intent and offer retry/undo/refusal rather than substituting preview geometry.

## Priority 7 — process-isolated worker tolerance

ID: `process-isolated-worker-tolerance`

**Open:** RCS-017 will further measure OCCT concurrency/global state.

**Founding policy:** The frontend assumes geometry workers may be process-isolated and restartable. No shared backend memory is project authority.

**Escape route:** A later backend may safely optimize deployment after measurement without changing MSAC semantic/project contracts.

## Priority 8 — backend crash replay and recovery

ID: `backend-crash-replay-recovery`

**Open:** Exact geometry can crash/hang on pathological workloads.

**Founding policy:** Commit semantic project state transactionally; isolate request lifecycle from project durability; record crash/timeout distinctly.

**Escape route:** Restart worker, discard suspect derived cache and replay the immutable revision. Preserve minimized failing operation as regression evidence.

## Priority 9 — semantic lineage rather than topology persistence

ID: `semantic-lineage-not-topology-persistence`

**Open:** Reconciled face/edge identities can change across backend rebuilds.

**Founding policy:** Persist material-body/operation/setup/tool semantic identity, never topology-object identity.

**Escape route:** Topology picks/selections used for UI inspection are transient/re-resolved against current reconciled geometry or become explicitly stale.

## Priority 10 — backend-private hybrid representations

ID: `backend-private-hybrid-representations`

**Open:** OpenSimachinist may use cells/mesh/voxel/SDF/deferred local representations.

**Founding policy:** MSAC sees capability/reconciliation/error/status metadata, not private representation IDs.

**Escape route:** Backend can replace fallback libraries/representations without project migration so long as stable semantics and STEP/refusal contract remain intact.

## Priority 11 — explicit version migration

ID: `explicit-version-migration`

**Open:** Journal/API/tool/policy/backends will evolve.

**Founding policy:** Store logical schema/definition/policy versions. Cached derived geometry is rebuildable and may be invalidated.

**Escape route:** Tested migrations create a new explicitly interpreted representation; unsupported versions fail clearly. Never silently reinterpret physical units/frames/path meaning.

## Priority 12 — remappable control profiles

ID: `remappable-control-profiles`

**Open:** Final gamepad mappings/deadzones/sensitivity require target-user evidence.

**Founding policy:** Logical controls and physical-state generation are independent from device binding. Candidate profiles are product config.

**Escape route:** Iterate mappings rapidly without changing journal schema or backend API. Preserve test profiles/results for usability comparison.

## Priority 13 — camera presentation only

ID: `camera-presentation-only`

**Open:** Final first-person/workpiece-follow/free-flight camera comfort/control details remain usability work.

**Founding policy:** Cameras are presentation state and never engineering frames.

**Escape route:** Replace camera implementation/FOV/collision/control schemes freely without migrating manufacturing history.

## Priority 14 — unsupported-operation authority label

ID: `unsupported-operation-authority-label`

**Open:** Product simulation may eventually portray interactions that the current backend cannot commit authoritatively.

**Founding policy:** The UI must distinguish visual-only/uncommitted simulation from authoritative manufacturing operations.

**Escape route:** Allow clearly labeled visual experimentation where useful, then require supported canonical commit/pending/refusal before it can affect saved authoritative workpiece/export state.

## Escape-route doctrine

When an integration/backend problem cannot be solved immediately:

1. preserve canonical manufacturing intent and immutable history;
2. preserve explicit units/frames/tool/setup/body identity;
3. report exact programme-facing status and diagnostic evidence;
4. choose only among **defer**, **reconcile**, **handoff**, **bounded fallback**, **retry/replay**, or **refuse** according to qualified capability;
5. allow a visual-only interaction only when it is unmistakably non-authoritative;
6. minimize/preserve the failing case for later qualification.

Never resolve an integration problem by silently widening tolerance, deleting material bodies, replacing a user's path with an uncertified approximation, using preview/mesh as engineering truth, or claiming STEP success beyond the evidence.
