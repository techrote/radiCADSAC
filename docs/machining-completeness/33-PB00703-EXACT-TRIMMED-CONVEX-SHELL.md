# PB-007-03 v6 — Exact trimmed convex shell certificate boundary

This document records the bounded source-solid construction added by corrective issue #176. It extends, but does not replace, PB-007-03 v4 exact semialgebraic source authority and PB-007-03 v5 exact-rational parametric **boundary** authority.

## Scope

The v6 route accepts only a deliberately narrow, independently checkable subset of the v5 patch language: zero-source-uncertainty degree-1 × degree-1 2×2 patches with equal exact-rational positive weights and an exact affine-planar/parallelogram control net. Each face carries an exact-rational strictly convex trim polygon inside the patch's active parameter domain. All faces must share source identity, role, units and frame, while the shell additionally binds explicit shell, revision and configuration identities.

This is a constructive certificate route for exact trimmed **convex polyhedral** solids assembled through the v5 evaluator. It is not a claim that an arbitrary NURBS patch collection, STEP import, kernel-valid B-rep, tessellation or `watertight=true` flag is an exact solid.

## Exact trim and seam contract

Trim vertices are exact rational `(u,v)` pairs. Binary floating point and tolerance predicates are not correctness authority. Every trim vertex must lie inside the exact active parameter domain, and each trim loop must have nonzero exact area with consistent strict convex orientation. The corresponding 3D vertices are obtained only by the v5 exact rational patch evaluator.

Shell closure is established from exact mapped geometry rather than backend topology identifiers. Every undirected geometric trim edge must have exactly two incidences from distinct faces, and those two face loops must traverse the edge in exactly opposite directions. A missing edge, a `1/1000000` micro-gap, a same-direction seam, more than two incidences, or a self-seam fails closed. Face incidence must be connected and the bounded route requires exact genus-0 `V-E+F=2`.

## Orientation, convexity and positive-volume material

Each face defines an exact rational plane. An explicit exact-rational interior witness must lie strictly on the negative side of every outward face plane; reversing a face therefore invalidates the certificate. The route then proves convexity by requiring every shell vertex to lie on the nonpositive side of every oriented face plane.

These conditions provide a finite exact solid authority for the admitted bounded subset. Exact-zero contact remains boundary, not positive-volume material. No backend component identity, face enumeration, largest-volume heuristic or proximity rule acquires durable body/lineage authority.

## Exact solid membership

A successful certificate binds the canonical shell SHA-256 to shell/source/role/units/frame/revision/configuration identity, the strict interior witness, every v5 patch SHA-256 and every exact trim loop. A membership query recomputes and compares that certificate before using it; stale or mutated evidence fails closed.

For a valid certificate, classification is the exact intersection of the certified outward half-spaces:

- any positive face sign means `OUTSIDE`;
- no positive sign and at least one exact zero means `BOUNDARY`;
- all signs strictly negative means `INSIDE`.

The adversarial control set distinguishes an exact face from signed `±1/1000000` neighbours. No epsilon, binary float, tessellation resolution, timeout or resource refusal may substitute for an exact sign.

## Failure-closed authority boundary

The verifier rejects trim-domain escape; zero-area, bow-tie or nonconvex trims; non-affine bilinear patches; unequal rational weights; nonzero source uncertainty; missing/micro-gapped/duplicate seams; inward faces; invalid interior witnesses; source/role/units/frame drift; stale patch hashes; binary-float coordinates; fake STEP/kernel/watertight claims; backend topology/body/lineage identity laundering; denominator shrinkage; and false MC-B promotion.

Opaque importer success, kernel-valid B-rep status and mesh containment remain non-authoritative for PB-007-03 exact source-solid semantics.

## Residual PB-007-03 obligation

`PB-007-03` **remains OPEN**. The frozen 26-operation domain still includes imported stock and arbitrary form/undercut source families broader than this exact convex-polyhedral subset. Curved trims, more general rational/NURBS boundaries, non-convex closed shells and opaque imported representations do not yet have a universal exact finite source-solid lowering/certificate route. Missing constructors remain gaps, not exclusions from the admitted domain.

Therefore PO-02 and PO-05 remain OPEN; PB-007-01 remains OPEN; PB-007-02 remains dependent on PB-007-01; PB-007-04 remains OPEN_PROPAGATED; and MC-B and MC-1 remain `NOT_ESTABLISHED`. This bounded result is not an impossibility theorem and does not justify an MC-B retry by itself.

## Protected semantics

Historical source/audio/provenance evidence remains immutable. Canonical-journal meaning, explicit source uncertainty, positive-volume material semantics, holder/access separation, durable body/lineage identity, refusal/`UNCERTIFIED` as non-success, and conventional STEP output semantics are unchanged. No native, paid, production or expensive campaign is authorized or executed by this repair.
