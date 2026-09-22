# MC-033 durable material-body and lineage state

Status: bounded MC-033 implementation completed as research evidence. This document defines the executable nominal body-state boundary; it does **not** accept MC-B or close universal topology/output obligations.

## Product authority

Durable body identity is programme-owned and comes from the canonical journal. A kernel handle, B-rep solid ID, mesh/voxel component, component enumeration order, largest-volume component or nearest/proximity match is never body/lineage authority. Candidate geometric components may help supply independently certified connectivity evidence, but they do not name manufactured bodies.

The authority-path state is revisioned and immutable. Historical durable records remain queryable after split supersession or complete disappearance. IDs are never recycled.

## Pure-removal transitions

MC-033 implements four transitions over regularized material:

| Transition | Required effect |
|---|---|
| `CONTINUE` | Explicitly retain the same durable body and lineage through further removal. |
| `SPLIT` | Account for every certified positive-volume remainder component; retain at most one explicitly selected parent continuation and create fresh descendant IDs/lineage edges for all others. |
| `DISAPPEAR` | Require exact empty material/zero residual; retain an exhausted durable record with no active material. |
| `TOUCH_ONLY` | Record exact-zero contact without removal, fusion or identity change. |

There is no pure-removal `MERGE`: subtraction cannot fuse two previously distinct manufactured bodies or add material. A zero-volume remnant is not a body; a positive-volume remnant, however small, cannot be deleted by tolerance. An exhausted body cannot be revived by another removal operation.

## Certificate admission

Transition commitment requires the same source, canonical material, body, revision, configuration and challenge identities throughout the certificate chain. MC-031 material evidence and MC-032-compatible event evidence are checked as bound inputs. The connectivity/partition evidence must be independently `PROVED`; missing proof stops as a blocker rather than triggering backend topology inference.

For a split, independent evidence must give the exact component count, a complete remainder partition, pairwise disjoint component interiors and the component certificate IDs consumed by the explicit output plan. Each output has an exact positive-volume witness. For disappearance, independent evidence must certify zero components and exact empty material. Touch-only requires zero new removal.

Binary floating point, epsilon/tolerance, refinement depth, timeout and resource exhaustion are not transition truth authority. A stale revision or mutated nested certificate does not mutate state.

## Finite histories

Transitions execute in journal/revision order. Remachining explicitly targets a current durable body ID; detached descendants are not chosen by size or proximity. The first blocked/uncertified/refused/invalid step terminates the attempted continuation and preserves the last committed state exactly.

This supplies the MC-026 `MC033-A/B` bounded implementation needed for later integration and reconstruction work.

## Remaining proof/output boundary

`PB-007-04` remains `OPEN_PROPAGATED`: MC-033 commits independently certified connectivity facts but does not prove a universal exact connectivity classifier for every admitted history. PO-07 therefore remains globally open.

`RB-016-02`, `RB-016-04` and `RB-016-05` also remain open. Nominal multi-body, touching and empty-state semantics are now explicit, but native conventional engineering output and independent-consumer preservation still require their recorded downstream evidence. MC-B through MC-F and MC-1 remain `NOT_ESTABLISHED`.

No production/native/paid campaign is authorized by this result. Historical source/audio/provenance, canonical-journal, positive-volume, durable-lineage and STEP semantics are unchanged.
