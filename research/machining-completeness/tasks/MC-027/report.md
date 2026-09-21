# MC-027 — Multi-/tri-directional material candidate falsification

Status: **NEGATIVE_RESULT** as a total material authority; retained as a bounded derived interval index/accelerator after an independently certified full-3D material relation.  
Issue: #89.  
Source baseline: `263b5e35f6a0d9a6c9695a926cbb37e3f65b9606`.  
Evidence class: dependency-bound source/research review + deterministic exact-rational 3D controls.  
Native/paid execution: **none**.

## Question and decision

MC-027 asks whether directional material can be extended beyond a single height field by keeping multiple intervals, using several directions, surviving reorientation, and consulting certified full-3D relations.

The answer is split deliberately.

- **Useful bounded role: retained.** Multiple exact/certified intervals per line remove the single-height-field obstruction for cavities, reentrant sections and separated material along a line. Exact common-frame reorientation can rebuild or query such indexes without changing source semantics. Given an independently authoritative 3D material relation plus certified transverse event boundaries, directional interval structures are valid derived indexes and can be useful accelerators.
- **Total material-authority role: falsified.** Any finite sampled set of rays is non-injective: distinct positive-volume materials can agree on every sampled ray. Replacing finite samples with a continuous directional field does not make the representation self-sufficient; a finite exact implementation must encode where interval count/order/endpoints change over the transverse plane, which requires the same certified full-3D relation/event information that the candidate was supposed to replace. The directional structure therefore cannot by itself be the programme's total authoritative material representation.

This is a candidate result, not a capability gate. MC-026 may consume the result when selecting a primary route and independent challenger/control, but it must not promote the bounded derived-index role into total material authority.

## Dependency binding

`directional-material-falsification-v1.json` pins the reviewed outcomes for:

- MC-010 — independent exact-rational material controls;
- MC-016 — early output representability and its still-open multi-body/singular-output blockers;
- MC-019 — complete finite ball/round cutter semantics over genuine simultaneous XYZ motion; and
- MC-023 — durable common-frame multi-setup/reorientation semantics.

The task does not rewrite those producing records. Historical `research/rcs-*`, source/audio/provenance meaning, canonical journal history, positive-volume material semantics and durable body/lineage authority are unchanged.

## Candidate contract

A directional record is a finite ordered union of exact or outward-certified material intervals on one directed line. A single line may contain any finite number of intervals; reducing the record to one top/bottom height is forbidden.

The retained use is explicitly **derived**. Before a directional index can answer an authoritative query, all of the following must already be justified for the concrete instance:

1. an independent canonical full-3D material relation exists;
2. each stored interval is derived from that relation with exact/certified endpoint semantics;
3. transverse event boundaries at which interval count or ordering changes are certified;
4. positive-volume material is never deleted by tolerance or sampling;
5. MC-023 common-frame transform direction/order/handedness is preserved;
6. MC-019's complete finite cutter and simultaneous-XYZ semantics are preserved rather than projected onto a preferred axis; and
7. an unknown relation remains `UNCERTIFIED` or a typed blocker instead of being guessed from neighbouring rays.

Three directions do not vote on truth. Directional conflicts are resolved by the canonical 3D relation. Missing rays are not material, empty, or success by default.

## Exact multi-interval and tri-directional control

The primary exact control is a `3 × 3 × 3` box with the open central `1 × 1 × 1` cavity represented as a finite union of six rational boxes. At the exact transverse centre `(3/2, 3/2)`, each of the X, Y and Z line families yields exactly two material intervals:

`[0,1] ∪ [2,3]`.

That is the minimum useful property a multi-directional candidate must have beyond a height field. Collapsing either line to `[0,3]`, keeping only the first/last interval, or bridging the gap is rejected.

The verifier also checks an exact positive `1/1000000` interval. There is no grid pitch or sewing tolerance that may erase it.

## Reorientation control

MC-023 already established that setup-local geometry must map into the durable common workpiece frame under explicit right-handed transforms. MC-027 exercises that rule with an exact signed-permutation rotation: a `2 × 1 × 1` box is rotated 90 degrees about Z and translated so its image is exactly `1 × 2 × 1`.

The transformed Y-directed centre line is exactly `[0,2]`. Inverse-transform substitution, composition-order changes or a left-handed reflection are not alternate answers. More general transforms remain subject to the exact/outward-certified transform rules already established upstream.

Reorientation therefore does not defeat directional indexing, but neither does it make the index authoritative. It only demonstrates that a derived index can be rebuilt/query-transformed without changing common-frame semantics.

## Boundary control

A unit material box is queried by X-directed lines at three exact Y coordinates:

- `y = 1`: exact boundary contact, material interval `[0,1]`;
- `y = 1000001/1000000`: strictly outside, no material interval; and
- `y = 999999/1000000`: strictly inside, material interval `[0,1]`.

Binary floating equality and a global epsilon are not correctness authority. This prevents a directional implementation from converting exact boundary distinctions into a fuzzy sampling convention.

## Decisive finite-sampling obstruction

The decisive falsification is not a performance argument. It is an information-loss counterexample.

Take the unit cube and sample X-, Y- and Z-directed rays whose two transverse coordinates are chosen from `{1/4, 3/4}`. Now compare two materials:

1. the complete unit cube; and
2. the same cube with the exact interior cavity `[49/100,51/100]^3` removed.

Every sampled ray misses that cavity because every fixed transverse coordinate is either `1/4` or `3/4`, outside the cavity's transverse range. Consequently every sampled ray returns the same `[0,1]` interval for both materials. Yet the materials differ by exact positive volume

`(2/100)^3 = 1/125000`.

The counterexample generalizes: the union of any finite family of sampled lines in finitely many directions has empty 3D interior. A sufficiently small rational positive-volume box can be placed away from those lines. Therefore finite sampled rays cannot be an injective encoding of arbitrary 3D material, regardless of whether there are one, three, or several preferred directions.

Increasing sampling density only moves the blind spot. A finite pitch is a resource/approximation choice, not a proof of material identity.

## Why a continuous directional field does not rescue totality by itself

One may avoid the finite-ray counterexample by defining the interval set for **every** line in a continuous family. Mathematically, that can characterize material. But a finite implementation must then encode the functions and event sets over the two-dimensional transverse domain.

For exact/certified use, it must know where:

- interval count changes;
- endpoint order changes;
- intervals merge or split;
- a tangent creates or destroys a zero-width contact;
- curved or reoriented sweep boundaries enter/leave a line; and
- an unresolved query must remain uncertain rather than being sampled away.

Those are certified full-3D relation/event obligations. Supplying them independently makes the directional structure a useful derived index. Assuming the directional index itself can discover them merely by denser sampling is circular and is rejected.

This distinction matters directly for MC-019. A simultaneous-XYZ ball/round sweep has genuine curved 3D boundary semantics; projecting it onto independent X/Y/Z occupancy or a centreline/constant-Z surrogate is already forbidden. The directional candidate may index a certified result, but it cannot replace the certification by taking several projections.

## Body, lineage and engineering-output boundary

Directional interval groups are not programme durable body identity or lineage. The same body can produce many disjoint line intervals; one interval can participate in connectivity that is invisible from a single ray. Majority voting or connected interval labels cannot replace the durable journal transition rules.

Accordingly existing MC-016 blockers remain open and are not duplicated:

- **RB-016-02** — multi-solid engineering output is structurally expressible, but durable-body mapping and independent-consumer preservation remain unqualified;
- **RB-016-04** — exact-zero contacts, touching cavities and singular pinches still require the approved profile plus independent-consumer evidence without healing or tolerance fusion.

A directional model can preserve exact material distinctions without qualifying STEP, grouped engineering output or independent downstream behaviour.

## Total-dispatch consequence

For MC-026 candidate selection, directional material has this reviewed role:

- **yes:** bounded derived index over an independently authoritative material relation;
- **yes:** exact/certified multiple intervals rather than a single height field;
- **yes:** acceleration/query structure after common-frame reorientation;
- **no:** finite sampled rays as complete material authority;
- **no:** three-direction majority/intersection/union heuristics as truth;
- **no:** self-sufficient continuous interval field without certified transverse events/full-3D relation;
- **no:** durable body/lineage authority;
- **no:** engineering-output or STEP qualification.

A failed admission may dispatch once to another reviewed owner or terminate truthfully as `UNCERTIFIED`/typed blocker. Provider cycling, timeout-as-success, sampling-density-as-proof and denominator shrinkage are forbidden.

## Capability state and non-claims

No native or paid campaign ran. MC-027 does not establish a native tridexel engine, a general exact solid classifier, topology reconstruction, practical-scale performance, STEP qualification or any output capability gate.

MC-A remains `ACCEPTED`. **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.** The machining-domain denominator is unchanged.

## Verification

```text
python3 research/machining-completeness/tasks/MC-027/verify.py --contract
python3 research/machining-completeness/tasks/MC-027/verify.py --self-test
python3 tools/mc_workflow.py verify MC-027
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge, and merged `main` must pass the same workflow before issue #89 is treated as accepted research evidence.
