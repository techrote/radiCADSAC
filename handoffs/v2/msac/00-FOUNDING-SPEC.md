# MSAC Genesis v2 founding specification

## Product intent

MSAC lets an experienced machinist create engineering geometry by operating a simulated lathe or mill with game-like/direct controls. Machine simulation aids creation, teaches state and provides feedback; it must not impose punitive chores that prevent geometry work. Undo/redo, replay and inspection are first-class.

The initial process scope remains lathe and mill.

## Machine modules and canonical producer

A machine module converts high-rate device/controller motion and machine state into explicit physical samples with tool/setup/frame/engagement/body semantics. A policy-versioned canonicalizer then emits `msac-journal/1.0`. MSAC must not stream frame-loop noise as durable geometry commands.

Units, coordinate frames, transforms, orientation, timestamps and fit bounds are explicit. Semantic boundaries such as engagement/tool/setup/target-body changes survive numeric quantization. Canonicalizer refusal is user-visible; it is not silently smoothed away.

## Backend boundary

MSAC sends canonical operations and programme identity, never OCCT objects. The stable request/status model includes capabilities, apply, commit/replay, material query, preview request, reconciliation, inspection and STEP export.

`accepted_pending` means intent is retained but engineering state still requires bounded provider work/reconciliation; it is not success and cannot authorize STEP. Failure/crash/timeout leaves the last committed revision authoritative.

Durable material-body IDs and semantic lineage are programme-owned. Split/cut-through can create multiple legitimate bodies. Default STEP body selection is **all committed material bodies**.

## Preview versus authority

MSAC may render GPU/mesh/dexel/approximate previews keyed by revision and engineering status. Preview is disposable. It cannot answer exact body selection/connectivity, inspection tolerance or STEP qualification by itself. Show when visual state is pending or stale relative to the committed/reconciled revision.

## Undo, replay and recovery

Undo navigates immutable revisions; redo/replay regenerates replaceable derived provider state from canonical authority. Project saves preserve journal, revision/body/lineage, source/audio identity, provenance and versioned policy references. They do not require serialization of kernel topology.

After backend restart/cache corruption, MSAC can reconnect/replay and obtain the same programme-level invariant. Surface crash/timeout statuses without corrupting history.

## Lathe capability UX

Expose the bounded realistic founding subset: qualified circular-nose external/internal turning, facing, shoulder, linear taper in qualified orientation, rounded groove and complete parting, subject to reachability and body/connectivity checks. Holder-collision undercut and unsupported form/live-tool/eccentric work must route to a capable provider when available or show `refused_unsupported`. Never fake the desired target profile.

## Mill capability UX

Exact fixed-axis paths are preferred. Manual/freehand fixed-axis work may enter bounded directional `accepted_pending` state when exact B-rep work is unsafe. Only cases whose material/spatial/error budgets close may progress through reconciliation. Unqualified five-axis/tool-reorientation and rounded simultaneous-Z operations must show pending/refusal/capability status rather than a plausible-looking but unproven solid.

## Inspection, DRO and workflow

DRO/readout uses explicit frames/units and can show canonical/committed/reconciled revision state. Inspection requests requiring exact geometry trigger reconciliation. Body selection is disabled or explicitly pending when current connectivity is unresolved. Machine spectacle (chatter/crash/dirt/wear) may be visual/feedback unless a separately versioned engineering rule says it changes canonical material intent.

## STEP UX

STEP is mandatory primary engineering output. STL/mesh export is derived convenience only.

The exact founding profile is `rcs-022-occt-ap242dis-layer-d/1.0`. Current independent Layer-D status is **`interoperability_unqualified`**. MSAC must distinguish:
- file generated / Layer A-C engineering validation passed;
- independent parser/import observations;
- full Layer-D qualification.

A successful write is not a green “fully interoperable” claim. Preserve explicit reason/blockers and profile/version. Never hide body loss, tolerance/error breach or pending reconciliation.

## Project/version model

Save the canonical journal schema/profile versions, tool/setup/frame definitions, durable revisions/bodies/lineage, source/audio identity and provenance, and user-selected engineering requirements. Provider caches, topology IDs and preview buffers are rebuildable.

Migration must preserve old physical meaning. Unknown required version/profile semantics fail closed or open read-only with an explicit migration path.

## Platform and failure expectations

Windows is the primary user target, with Linux a supported research/backend development platform. Genesis v2 demonstrates programme semantic equality and recovery under hosted Windows/Linux through 100k-event research histories. Product responsiveness/capacity must be measured separately.

The UI must remain usable during backend work: async statuses, cancellation where safe, visible pending/reconciliation state and recovery. Do not mask kernel hangs by blocking the UI thread.

## Protected provenance

Source/audio identity and provenance are programme-owned immutable metadata. Playback/audio/visual assets may be derived, but a provider rebuild or geometry coincidence cannot replace their identity or history.
