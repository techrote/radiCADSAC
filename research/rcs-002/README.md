# RCS-002 machine-readable journal examples

Status: accepted RCS-002 research fixtures  
Date: 2026-09-16

## Purpose

These files exercise the logical `msac-journal/1.0` contract defined in `docs/10-CANONICAL-JOURNAL-CONTRACT.md`.

They are deliberately small enough to inspect and validate without choosing the production persistence technology.

## JSON is an illustrative encoding

The JSON files in `fixtures/` are **not** a decision that MSAC/OpenSimachinist projects must store journals as JSON.

The normative content is the logical meaning of:

- fixed physical quantities;
- frame transforms;
- immutable definition references;
- operations;
- workpiece revisions;
- material-body transitions;
- normalization bounds.

A future binary or database encoding must preserve the same meaning and compatibility rules.

## Fixtures

### `lathe-finishing-pass-v1.json`

Demonstrates:

- cylindrical stock;
- explicit workpiece/machine/tool frames;
- one setup activation;
- rotating-workpiece turning semantics;
- neutral/engaged/neutral trajectory sections;
- physical timestamps and integer nanometre coordinates;
- a repeated finishing pass retained as a second canonical operation.

The fixture expects the second pass to remain journal-visible even if a geometry backend concludes that it removes no additional material.

### `mill-cut-through-v1.json`

Demonstrates:

- box stock;
- fixed-orientation end mill;
- an engaged cutter path through the full stock width and thickness;
- a committed split from one durable material body to two;
- explicit retained/detached classification without silently deleting the detached body.

The exact downstream STEP representation of those two bodies remains RCS-005 work.

## Fixture conventions

All fixture dimensional tokens follow `nm-nrad-ns-q15-v1`:

- translation/length: signed integer nanometres;
- angle: signed integer nanoradians;
- time: signed integer nanoseconds;
- angular rate: signed integer nanoradians/second;
- quaternion component: signed integer divided by `10^15`.

Frames are right-handed. `transform_parent_from_child` follows the convention:

`p_parent = R(q) * p_child + t`

The fixtures use identity rotation where possible so the examples emphasize manufacturing semantics rather than rotation arithmetic.

## Validation

From repository root:

```text
python3 tools/validate_repo.py
```

The validator checks the fixture schema, ID uniqueness, frame acyclicity, integer ranges, quaternion structure, revision parentage, reference integrity, trajectory section structure, normalization bounds, and material-body transition consistency.

## Why these are not geometry truth fixtures

RCS-002 defines the durable manufacturing language, not the expected Boolean/B-rep result.

The fixtures therefore assert journal-level intent and history invariants only. RCS-003/RCS-006 will add physical-result expectations and backend measurements without changing the meaning of these canonical operations.
