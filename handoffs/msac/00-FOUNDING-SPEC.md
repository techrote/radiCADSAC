# MSAC founding specification

Status: implementation-ready founding specification  
Handoff: `msac-handoff/1.0`  
Frontend architecture: `sac-machine-module-client-v1`  
Backend architecture consumed: `semantic-provider-hybrid-v1`  
Genesis source state: radiCADSAC main `2e77ea087b01ac1415c4c76ff1dc0661aab286fb`

## Product brief and SAC philosophy

**MSAC — Machinist Simulation Aided Creator** is a user-facing engineering creation environment in which simulated manufacturing is the modelling interface. A user should create an engineering object by operating simulated machine tools and ultimately obtain trustworthy conventional engineering output, principally STEP.

The defining SAC proposition is not “CAD with game controls.” The user's manufacturing action is the source intent. If a machinist wants a turned shoulder, they turn it; if they want a milled slot or pocket, they mill it. MSAC captures that physical/process meaning into the canonical manufacturing journal and delegates authoritative geometry realization, reconciliation and export to OpenSimachinist.

The initial implementation scope is deliberately **lathe and mill only**. It should become useful for productive engineering creation before workshop breadth, progression systems, content libraries, publication polish or game mechanics dominate effort.

## Target user and product test

The first serious target user is:

- an experienced machinist;
- comfortable with machining terminology, setups and machine behavior;
- familiar with console-game motor control;
- not assumed to prefer conventional parametric CAD workflows.

The product hypothesis is that this user's machining knowledge can transfer directly into digital solid creation without first requiring a separate feature-tree CAD mental model.

A useful early usability test is therefore not “does a CAD expert recognize our UI?” It is “can the target machinist make, inspect, undo/revise and export an intended part while thinking primarily in machining terms?”

## Anti-chore and asymmetric-realism doctrine

Physical simulation is valuable when it improves intuition, feedback, control or engineering meaning. It must not make creation needlessly punitive.

Geometry-critical behavior must be trustworthy enough for engineering use:

- stock dimensions;
- setup/workholding transforms;
- geometry-relevant tool definitions;
- tool position/orientation and machine kinematics;
- material addition/removal semantics within supported processes;
- workpiece/body dimensions and topology state;
- units, tolerance/status and STEP export behavior.

Experiential phenomena may be approximate or cosmetic unless later evidence gives them engineering significance:

- chatter and sound;
- sparks/chips/coolant appearance;
- camera shake;
- dirt and cosmetic wear;
- dramatic crash effects.

MSAC must not require floor sweeping, consumable-filling chores, arbitrary warm-up waits or similar maintenance busywork merely to continue modelling. A dramatic crash may provide feedback or spectacle, but creative work must be recoverable through first-class undo/revision semantics.

## Product architecture

The founding MSAC architecture has five programme-owned layers:

1. **Interaction/presentation** — input devices, camera, UI, visual machine simulation and non-authoritative effects.
2. **Machine modules** — kinematics, tooling/setup interaction, physical machine state, process semantics and process-aware normalization hints.
3. **Canonical project model** — definitions, `msac-journal/1.0`, immutable revision graph, material-body IDs, current UI head, persistence and undo/redo navigation.
4. **OpenSimachinist client boundary** — versioned semantic requests/responses, capability discovery, status/diagnostics, replay/reconciliation/export requests.
5. **Derived presentation caches** — preview meshes and other disposable visualization artifacts keyed to semantic revision/backend identity.

Godot scenes/nodes, controller mappings and rendering objects are never the authoritative manufacturing/project representation.

## Machine-module architecture and contract surface

A **machine module** is the MSAC-side implementation of one simulated machine/process family. It owns interactive behavior without becoming an exact-geometry kernel.

A machine module may provide:

- kinematic axes/limits and physical state;
- tool/setup/workholding interaction;
- process type and engagement semantics;
- raw machine-state sampling after device mapping;
- machine-native coordinate conventions and explicit conversion into canonical frames;
- process-aware trajectory segmentation/canonicalization hints;
- preview hints;
- capability queries and UI affordances.

It must not:

- expose or persist OCCT/private backend topology;
- make render meshes authoritative;
- silently mutate committed historical definitions;
- redefine the canonical unit/frame contract;
- declare engineering success because a visual interaction looked plausible.

The matching OpenSimachinist **geometry process provider** is backend-side. A machine module and provider may share versioned semantic process definitions, but they remain replaceable implementations on opposite sides of the stable contract.

## Tool, setup and definition model

Geometry-relevant definitions referenced by committed operations are immutable revisions.

A tool definition/revision must be sufficient to identify the geometry-critical tool shape/orientation semantics sent into the journal/backend contract. Changing cutter diameter, insert nose geometry, stickout/orientation convention or another geometry-critical property produces a new revision rather than rewriting history.

A setup revision records workpiece↔machine/workholding frame meaning. Re-chucking/re-clamping creates a new setup/frame revision rather than mutating an old transform.

User-friendly libraries may point to these immutable definitions, but convenience names are not durable identity.

## Gamepad and manual-control principles

Gamepad/manual control is a product advantage to test, not a permanently frozen control map.

The durable pipeline is:

`device event` → `logical control action` → `machine-module physical state/rate/pose` → `canonicalizer` → `journal operation`.

Rules:

- controller model, HID code, stick deadzone and response curve stay upstream of the journal;
- logical actions are remappable;
- machine modules map logical actions into physical motion appropriate to their kinematics;
- continuous axes/rates should preserve fine control and allow simultaneous movement where useful;
- control mappings/configuration are versioned as user/product configuration for reproducible UX testing but do not define committed engineering meaning;
- changing a deadzone or sensitivity may alter future motion but never reinterprets existing journal history;
- no single “perfect” mapping is declared by this handoff before target-user testing.

Keyboard/mouse and other devices may coexist. Device support must not require changes to `msac-journal/1.0` semantics.

## Camera and spatial-navigation concept

MSAC should support at least two camera concepts once the engineering shell can consume them:

- **first-person machinist view** — spatial perspective tied to the operator experience;
- **workpiece-follow/free-flight view** — camera follows the workpiece/reference while allowing inspection-oriented free movement, preserving the founding “second-person” idea without binding it to a misleading formal term.

Cameras are presentation/navigation state only. Camera transforms must never become setup/tool/workpiece engineering transforms implicitly. An inspection view may query engineering geometry, but moving the camera cannot alter the canonical part.

The final feel, FOV, collision comfort and exact controls remain usability work rather than founding contract constants.

## Canonical operation-journal producer contract

MSAC is responsible for producing the accepted logical `msac-journal/1.0` manufacturing language.

The journal stores physical/process meaning, not raw controller input or render-frame events. The founding canonical numeric convention is `nm-nrad-ns-q15-v1`:

- length/translation: signed integer nanometres;
- angle: signed integer nanoradians;
- time/duration: signed integer nanoseconds;
- linear/angular rates in corresponding physical integer units;
- quaternion components as fixed rational `q15` tokens.

Canonical frames are explicit right-handed frames with explicit parentage and transform composition.

### Producer pipeline

A conforming production implementation should separate:

1. device mapping/deadzone processing;
2. machine-module physical state;
3. normalized physical machine-state trace;
4. semantic boundary detection (setup/tool/process/body/engagement changes);
5. bounded deterministic trajectory fitting/simplification;
6. canonical quantization with included error budget;
7. journal/revision validation and atomic commit.

If optional curve fitting cannot certify its declared bound, it must fall back to a less compressed representation such as a polyline rather than falsify the motion.

Repeated/retraced operations remain journal-visible even when the backend later proves them to be material no-ops.

## Immutable project history, undo and redo

A committed workpiece revision is immutable. Undo/redo changes the selected project head among revision nodes; it does not destructively rewrite old operations.

Founding requirements:

- one parent per revision under `msac-journal/1.0` with branch creation supported;
- explicit material-body set/transition records at committed revisions;
- immutable referenced setup/tool/policy/frame definitions;
- current UI head stored as mutable navigation metadata;
- redo branches preserved until an explicit user/project policy removes them;
- derived backend/preview caches disposable and rebuildable.

Undo must remain available after a backend/kernel failure because the durable semantic revision store is not the worker's private geometry memory.

## MSAC↔OpenSimachinist boundary

MSAC consumes a **semantic and versioned** programme contract. Transport is deliberately replaceable; the handoff does not prematurely freeze in-process ABI, local IPC, RPC, JSON, Protobuf or Godot GDExtension.

The founding request families are:

- `capabilities`;
- `apply_canonical_operations`;
- `commit_revision`;
- `replay_revision`;
- `query_material_state`;
- `request_preview`;
- `request_reconciliation`;
- `inspect_reconciled_geometry`;
- `export_step`.

Requests carry enough identity for deterministic interpretation, including contract/journal versions, semantic revision, operation IDs, setup/tool revisions, coordinate-frame reference, relevant material-body selection and policy versions.

Responses carry programme status, resulting revision/body IDs, lineage events, provider/dispatch/reconciliation identity and diagnostics.

Forbidden stable-boundary concepts include OCCT `TopoDS_*`, OCCT handles, backend object addresses/hashes, Godot node identity, triangle-index identity and voxel/cell IDs.

## Client execution model

The OpenSimachinist client must assume engineering work may be asynchronous relative to frame rendering. No product requirement says exact reconciliation/STEP export completes inside one render frame.

MSAC should maintain explicit request identity and lifecycle so it can:

- show immediate local machine/preview feedback;
- submit canonical intent;
- receive `accepted_pending` or reconciled results;
- discard stale responses that target an old UI/project head without discarding their durable revision evidence;
- retry/replay after worker crash/timeout according to explicit policy;
- request reconciliation when inspection/export requires it;
- keep UI responsive while authoritative geometry work proceeds.

The initial backend may use process-isolated workers. MSAC must tolerate that deployment topology without depending on shared backend memory.

## Programme-facing status and failure presentation

The user-facing model must distinguish at least:

- `accepted_pending` — intent is durably accepted but bounded material/topology work remains deferred;
- `reconciled` — conventional validated engineering geometry exists;
- `success` — the requested qualified action/query/export completed;
- `refused_unsupported`;
- `refused_unresolved_ambiguity`;
- `invalid_topology`;
- `wrong_geometry`;
- `tolerance_breach`;
- `kernel_error`;
- `crash`;
- `timeout`;
- `nondeterministic_result`;
- `step_writer_failure`;
- `step_roundtrip_failure`;
- `interoperability_unqualified`.

MSAC must not collapse all of these into “failed” or, worse, hide them behind a successfully rendered mesh/file. Diagnostics should preserve backend/provider/build/profile context while the primary UI explains what the user can do next: wait/reconcile, retry, undo, choose another body, change an unsupported operation, or export only once the requested qualification permits it.

## Preview versus authoritative engineering geometry

The render workpiece is not engineering truth.

MSAC may show a responsive preview based on tessellated B-rep, incremental mesh or another backend/local representation. Preview state is tagged with the semantic revision/provider state from which it derives.

The UI must make meaningful distinction between:

- local/immediate simulated motion;
- preview derived for a revision;
- `accepted_pending` engineering state;
- `reconciled` committed engineering state;
- qualified/unqualified export result.

A preview may temporarily lead the authoritative backend for responsiveness. It may not be saved as the only durable representation or silently used to manufacture a fake STEP success result.

## Initial lathe capability and limitations

The first productive lathe slice should target the backend's qualified fixed-axis subset:

- cylindrical OD turning;
- facing;
- shoulders;
- linear taper/chamfer-class boundaries;
- simple cylindrical through/blind boring;
- repeated finishing/retrace cases whose material meaning is proven.

MSAC should expose backend capability discovery rather than assuming all visible lathe motions have identical qualified engineering support.

Not initially proven as general authoritative support:

- arbitrary insert nose-radius/orientation envelopes;
- grooving/parting connectivity beyond qualified cases;
- difficult undercuts;
- eccentric/live-tool/non-axisymmetric turning.

Unsupported semantics can still be simulated visually only if the product labels them clearly as non-authoritative and does not commit/export false engineering state. Otherwise the correct response is pending/handoff/refusal.

## Initial mill capability and limitations

The first productive mill slice should target:

- fixed tool orientation;
- supplied/recognized simple process operations;
- strict proven collinear/simple-path canonical batching;
- exact per-segment cutter-envelope baseline;
- overlaps and qualified cut-through/body separation.

Arbitrary self-crossing/retraced/freehand batching is **not** assumed safe merely because a Boolean returns a valid B-rep. Pathological cases may return pending/fallback/refusal until a qualified route is available.

The frontend should not invent geometry strategies; it supplies manufacturing semantics and displays backend capability/status honestly.

## Material-body presentation and selection

Parting/cut-through can create multiple disconnected volumetric material bodies. MSAC must preserve and present them explicitly.

Requirements:

- durable material-body IDs come from programme semantic state, not mesh/topology enumeration;
- body split/merge/replacement lineage can be inspected diagnostically;
- setup/workholding may classify retained/detached bodies but must not silently delete detached material;
- export defaults to all material bodies unless the user explicitly chooses a subset;
- subset selection records requested and omitted body IDs;
- there is no implicit largest/first/primary-body rule.

## Dimensional inspection and DRO requirements

MSAC must become useful as an engineering creation tool, not merely an expressive sculpting interface.

The initial product therefore needs:

- machine-axis/readout display in user-selected display units without altering canonical storage;
- workpiece/setup coordinate references;
- tool position/rate/spindle state relevant to operation control;
- measurement queries for dimensions that can be supported reliably by current engineering state;
- body count/selection and reconciliation state;
- clear distinction between measurements derived from preview and authoritative reconciled geometry;
- tolerance/status context when reporting a backend measurement.

Exact topology-dependent inspection can request reconciliation. The UI should say why a query is pending rather than fabricate precision from the preview mesh.

## STEP export UX and conformance/status presentation

STEP is the primary engineering output.

The initial UX should provide:

- selected committed revision and body selection;
- explicit export unit/profile information;
- all-body default with deliberate subset override;
- reconciliation progress/status if required;
- clear refusal if the state cannot satisfy the conformance contract;
- output record including backend/export profile and file identity/digest where available;
- Layer A/B/C local validation summary;
- independent-interoperability qualification state.

`msac-step-conformance/1.0` distinguishes successful file generation from full product interoperability qualification. Until independent consumer evidence exists, `interoperability_unqualified` must be presented precisely rather than marketed as “fully validated.”

Mesh/STL output may exist as a convenience derived artifact, but it is never the success fallback when STEP reconciliation fails.

## Save, project and versioning model

A saved MSAC project must retain enough programme-owned information to rebuild derived geometry after a backend upgrade.

Durable project content includes:

- journal schema/numeric convention and project/workpiece identity;
- immutable definition registry;
- canonical operations;
- immutable revision graph and material-body transitions;
- selected UI branch/head;
- required extension/schema versions;
- tolerance/normalization policy identities;
- user/product configuration such as display units and control profiles where useful, kept distinct from engineering meaning.

Optional/non-authoritative content includes:

- raw controller telemetry;
- preview meshes;
- backend B-rep snapshots/caches;
- thumbnails/UI state;
- diagnostic logs.

### Atomic save and recovery

Journal/revision commits must be transactionally durable at the project layer before the UI treats them as recoverable committed work. Autosave/checkpointing should occur at safe committed boundaries.

If MSAC or an isolated backend worker crashes, restart should recover the last durable semantic revision, discard suspect derived caches and replay/re-request backend state. Unsaved local interaction may be recoverable opportunistically, but must never corrupt the last committed project.

Schema migrations are explicit and versioned. Opening an unsupported future/old schema fails clearly or uses a tested migration; it never silently reinterprets physical meaning.

## Initial productive vertical slice

The first useful proof should be intentionally thin:

1. create/load simple stock and immutable setup/tool definitions;
2. manually operate a minimal lathe or mill interaction through machine-module physical state;
3. canonicalize/commit one `msac-journal/1.0` operation;
4. submit it through the semantic backend boundary;
5. show responsive preview plus authoritative status;
6. reconcile/inspect a resulting body/dimension;
7. undo/redo or branch the operation;
8. export the committed revision to STEP under the accepted profile;
9. reload/delete derived caches/replay and verify equivalent engineering state.

A second thin machine slice then proves the same project/backend machinery works for the other initial machine family.

This core loop should work before workshop decoration, progression/content systems, multiplayer, cinematic crashes or broad tooling libraries become roadmap blockers.

## Explicit first-implementation non-goals

The first MSAC production implementation does **not** need:

- a complete simulated workshop;
- additive/welding processes;
- conventional sketch/extrude/feature-tree CAD as a fallback interaction model;
- final publication/storefront polish;
- progression/economy systems;
- irreversible crash damage;
- physically exact chips, coolant, chatter, thermal effects or wear;
- every lathe tool/envelope and every arbitrary mill trajectory qualified for authoritative output;
- direct OCCT linkage in the frontend;
- synchronous exact geometry every render frame;
- one fixed permanent gamepad map before usability evidence;
- production repository coupling to the radiCADSAC Git history.

These exclusions keep the implementation focused on proving SAC as an engineering creation workflow.

## Genesis evidence map

The founding implementation should treat the following genesis artifacts as evidence when a requirement needs to be understood or challenged:

- `docs/00-FOUNDING-BRIEF.md` — SAC product intent, target user, anti-chore/realism, camera/gamepad concepts;
- `docs/01-MSAC-GEOMETRY-CONTRACT.md` — stable responsibility boundary;
- `docs/10-CANONICAL-JOURNAL-CONTRACT.md` — journal/canonicalization/numeric/history contract;
- `docs/13-STEP-CONFORMANCE-CONTRACT.md` — engineering export success/refusal model;
- `docs/20-OPENSIMACHINIST-ARCHITECTURE-SYNTHESIS.md` and DR-0015 — accepted backend boundary/status/provider architecture;
- `handoffs/opensimachinist/` — clean sibling backend founding package;
- RCS-007–RCS-012 decisions/evidence — reasons global fuzzy tolerance, topology identity, unbounded deferred state, arbitrary freehand batching and coarse fallback loss must not be hidden by the frontend.

This handoff translates those results into MSAC requirements without importing research chronology as product architecture.
