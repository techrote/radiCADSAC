# PB-007-03 — exact curved swept-form source lowering from original F08

Status: **DRAFT RESEARCH / bounded exact nominal construction; PB-007-03 OPEN**  
Date: 9 November 2026  
Repository authority: accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`  
Scope: independent of the concurrently owned nonconvex planar-patch shell research.  
Evidence class: **DETERMINISTIC_MODEL + exact rational argument + original independent MC-012 oracle**; no native/STEP test or consumer admission.

## Exact unmet proposition and witnessed old counterexample

MC-020's executable form/accessible-undercut cutter construction is confined to **finite unions of axis-aligned rational boxes**. It cannot reproduce the exact *curved circular* boundary of the original independently authored physical **MC-012 F08-TSLOT** undercut tool and its XY translation. An axis-aligned box union cannot have an open circular boundary arc: every such box-union boundary lies in a finite set of planes parallel to coordinate axes. A box/AABB/hull stand-in would change machining truth, including the original undercut roof-survivor and exact radial contacts.

The accepted PB-007-03 v4 semialgebraic codec can evaluate rational polynomial atoms but did not provide a source-derived constructor for this actual physical F08 operation. This increment lowers the **unchanged original F08-ACCESS and F08-TSLOT operation fields**, not reauthored synthetic geometry, to v4-compatible finite rational polynomial Boolean ASTs. It preserves two distinct journal operation/source identities; the cutting head/neck union belongs to **F08-TSLOT alone**, and access drilling belongs to **F08-ACCESS alone**.

Pinned original authority:
- `research/machining-completeness/tasks/MC-012/physical-corpus-f05-f08-v1.json` Git blob `8bb04fd5c643d02c42d2b58e49192ddb346b5b3f`.
- Independent exact original physical oracle `MC-012/fixture_oracle.py` Git blob `2f0c7f5ff91ce9f82b591267d3ba1b3070c34e54`.
- Accepted semialgebraic-source v4 `MC-038/pb00703_source_codec.py` Git blob `87429f3aa42692222287e62762d08c01b989a61c`.
- MC-020 `form-undercut-sweep-contract-v1.json` blob `6fca79b5d70329346e2c4ceab292c1be3fc3e528`.

The original F08 physical witness is a 3 mm radius circular undercut head at z=[4,6], 1 mm neck at z=[6,14], continuous XY path (5,10)→(25,10), and 7/2 mm entry bore. It includes removed undercut-shadow (15,25/2,5), surviving roof (15,25/2,8), removed neck slot (15,10,10), and exact **1/2 mm radial starter-pocket margin**. The margin is a necessary access control only; full body/holder/collision access is **not** claimed.

## Exact finite construction and theorem

For rational planar path endpoints A,B, fixed positive rational radius r, and point P, put v=B−A, L=v·v and u=(P−A)·v. For **L>0**, the swept closed disk along the segment is the union of exactly three semialgebraic regions:

1. `u<=0` and `|P−A|²−r²<=0`;
2. `u>=L` and `|P−B|²−r²<=0`;
3. `0<=u<=L` and `L(|P−A|²−r²)−u²<=0`.

These follow from minimizing the strictly convex squared distance to A+tv on t∈[0,1], with unique clamped orthogonal projection. Multiplication by positive rational L introduces no inequality reversal. All constraints are polynomial of degree at most two with exact rational coefficients; their finite Boolean union is **exactly** the planar capsule, not an approximation, tessellation or mesh. For L=0 the valid stationary segment is a single exact closed disk. Intersecting with a rational Z slab yields a finite exact closed swept cutting solid. A finite XY polyline is the union of its individual capsules; reversal, retraces and consecutive stationary points remain semantically retained in the original path and need not alter nominal set membership.

This produces a **source-derived curved envelope** under the existing v4 rational-semialgebraic grammar. It covers arbitrary *finite rational XY polylines* within the explicit verification resource limit, positive rational head/neck radii and rational nonzero Z intervals under fixed tool orientation. The original F08 is an actual covered physical witness, not a claim of universal domain/source representability. Neither source semantics nor the original journal are replaced with anonymous AABB sweep truth.

## Executable independent verification

```sh
python3 research/machining-completeness/tasks/MC-038/pb00703_f08_capsule_source_20261109.py --contract
python3 research/machining-completeness/tasks/MC-038/test_pb00703_f08_capsule_source_20261109.py --self-test
python3 tools/validate_machining_completeness.py --self-test
```

The test suite pins the original fixture, original independent oracle and accepted v4 codec by Git-blob identity. It compares **each** original F08 operation separately with the independently authored MC-012 oracle on 1,400 deterministic exact-rational three-dimensional points, plus prescribed original source witnesses, signed exact 1/1000000 boundary neighbours, circular endcap counterexamples, and 450 exact-rational prospective polyline/retrace controls. Original-source mutation and role/frame/uncertainty changes fail closed. The codec returns `BOUNDARY_CANDIDATE` for algebraic equality; this is not promoted into a universal topological boundary theorem. Source uncertainty >0 retains `UNCERTIFIED_SOURCE`.

Limits and invalid/OPEN distinction: at most **64** finite line segments, **1024-bit** rational numerator/denominator per authority-bearing intermediate coefficient and **131072 bytes** per original fixture. Exceeding budgets yields typed `OpenSource` retaining PB-007-03 rather than declaring a valid physically realizable source invalid. Malformed rationals, negative radius, wrong original operation order, float authority and incorrect original fixture byte identity are `InvalidSource`. Zero radius, zero-thickness cutting support, unsupported cutter sequence/orientation and unknown form-tool variants remain **OPEN**, not excluded from the domain.

## Scope and consumer contract

The source role is **cutting** in explicit millimetres and `F08:S-F08:common` frame; the two journal operation IDs and complete original fixture Git-blob identity are retained in separate v4 canonical source SHA-256 receipts. Actual holder geometry, source uncertainty beyond exact nominal F08, cutting/holder clearance, full 3D/reoriented tool orientation, nonrational/opaque imported stock, general NURBS surfaces, nonplanar trajectories, arbitrary variable-radius cutters, global topology/body lineage and resource-independent finite progress are **not** established.

MC-020/MC-026/MC-038 may consume this restricted original-source lowering as a candidate deterministic-model source constructor. They must not silently replace it with boxes, merge the two operations in the journal, claim independent access from the radius margin, or promote it to native material output, STEP engineering validity or universal form-tool source support.

**Programme preservation:** 26 frozen operations; 121 originals, 20 refusals, 30 missing premises, 50 complete V2 witnesses; required PB/PO discharges **zero**. PB-007-03, PO-02, PO-05 and other propagated PB cases remain OPEN; MC-B/MC-1 are `NOT_ESTABLISHED`; `production_authorized=false`. No accepted-main integration under this work; #397 alone owns that action.

## Remaining prerequisite

An independent source-critical review and exact-head qualification must establish that the new constructor correctly binds the **whole** original F08 source and yields expected responses under adversarial parser mutations. Next, general exact source geometry outside rational planar disk paths (including true imported stock, curved/trimmed NURBS and arbitrary accessible undercut tool geometries) still needs an exact lowering theorem or explicit finite refusal with named consumer proof dependency. No negative datum or unsolved source family may be removed from MC-B's required obligations.


## 9 November 2026 — source-custody correction after independent HOLD

The direct adapter previously defaulted untrusted parsed fixtures to the frozen MC-012 original Git-blob ID. This was unsound: changing only F08-TSLOT head_radius from 3 to 13/4 preserved the original ID while changing exact membership at P=(15,105/8,5). Its segment-distance squared is 625/64; original r²=9 is OUTSIDE, altered r²=169/16 is INSIDE. The original capsule algebra was correct, but the source identity was forged.

The repaired adapter independently checks original fixture bytes against the pinned MC-012 Git blob before assigning the original ID and compares canonical **complete JSON semantics** (mapping key order normalized; original array order, scalar types, all field values bound) with its untrusted supplied fixture. Only an exact semantic match inherits the frozen original source ID. Every altered but supported prospective input receives a distinct PB-007-03:derived-canonical-sha256:<digest>:<operation> identity bound to all source fields, never the original MC-012 label. Passing an asserted provenance argument is rejected. A derived geometric result does not confer independent physical source validity.

The direct-adapter adversarial test checks the reviewed 3→13/4 mutation, independent MC-012 oracle membership, exact rational inequalities, canonical original and derived identities, whole-fixture mutation, JSON key-order invariance, source descriptor digest changes, and explicit forged-provenance rejection. The original byte-authenticated loader remains a positive control. This correction does not change original fixtures, capsule algebra, holder/access certificates or broader PB-007-03 coverage; required PO and MC-B/MC-1 obligations stay OPEN/NOT_ESTABLISHED.
