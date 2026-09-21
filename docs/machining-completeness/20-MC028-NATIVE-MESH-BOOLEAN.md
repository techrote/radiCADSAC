# MC-028 — Native mesh/Manifold Boolean candidate boundary

Status: **NEGATIVE_RESULT** for total MC-1 material/engineering-output authority. The candidate remains eligible only for a bounded derived/challenger role behind independent certification.

## Stable conclusion

MC-028 evaluates a native Manifold-style triangle-mesh Boolean candidate using the already-qualified **MC-018**, **MC-019** and **MC-020** actual cutter-sweep constructors. Historical **LevelSet** sampling is explicitly not the operand source.

The total-authority role is rejected for three independent reasons:

1. MC-019 contains exact curved ball-end sweep boundaries. A finite set of planar triangles is an approximation of an open spherical patch, not identical exact material authority.
2. The pinned upstream Manifold v3.5.3 mesh contract includes floating-point mesh state and tolerance semantics under which edges shorter than tolerance may collapse and tolerance may grow. MC-1 does not permit tolerance to delete exact positive material or decide exact-zero contact.
3. A manifold triangle mesh is not, by itself, the mandatory conventional primary **STEP** engineering output or independent-consumer qualification required downstream.

This does not assert that Manifold's Boolean implementation is defective. It bounds what a mesh Boolean result can prove for this programme.

## Exact boundary controls

The task verifier imports the producing sweep modules directly.

- MC-018: flat cutter boundary at `x=1` versus outside `1000001/1000000`.
- MC-019: exact sphere witness `(3/5,0,1/5)` with signed Z-neighbours. In XZ, the witness lies on `x^2+(z-1)^2=1` but not on the straight endpoint chord `z=x`.
- MC-020: nonconvex box-union gap plus a positive feature of exact width `1/1000000`.
- Material event: tangent interval overlap `0`, positive penetration `1/1000000`, and separated overlap `0`.

Binary-float or global-epsilon equality is not correctness authority for these controls.

## Retained candidate role

A future native mesh Boolean provider may be useful only when:

- the source-faithful actual sweep remains independently authoritative;
- a separate exact or outward-certified material/error relation owns correctness;
- positive-volume and exact-zero distinctions are validated outside mesh tolerance heuristics;
- `UNCERTIFIED`, resource refusal or tolerance ambiguity remains fail-closed;
- durable body identity/lineage remains journal-owned rather than mesh-component-owned; and
- mesh output is not promoted to primary STEP success.

## Open blockers

MC-028 does not close or duplicate the inherited blockers:

- **PB-007-03** — arbitrary form/undercut source codec remains incomplete;
- **RB-016-02** — durable multi-body engineering-output preservation remains unqualified;
- **RB-016-03** — native STEP preservation of certified positive micro-material remains unqualified;
- **RB-016-04** — exact-zero/touching/singular engineering output remains unqualified.

No native or paid campaign ran. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.

## Protected semantics

Historical research evidence remains intact. **source/audio/provenance** meaning, canonical journal authority, exact positive-volume semantics, durable body/lineage identity, and mandatory STEP primary output are unchanged.
