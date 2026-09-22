# PB-007-03 exact parametric-patch boundary

This document records the versioned PB-007-03 v5 follow-up from corrective issue #174. It extends, but does not rewrite, the v4 exact semialgebraic source-codec evidence.

## Qualified bounded route

`EXACT_RATIONAL_TENSOR_PRODUCT_PARAMETRIC_BOUNDARY_V1` represents a single nominal tensor-product B-spline/NURBS-style boundary patch using exact rational knots, three-dimensional control points and strictly positive rational weights. Exact source identity, patch identity, stock/cutting/holder role, units, frame, distinct `u`/`v` parameter identities, active parameter domains and source uncertainty are mandatory authority bindings.

Cox-de Boor evaluation is performed entirely with exact rational arithmetic. Repeated knots are legal when the overall knot vector and control cardinality are valid; zero-width spans contribute exact zero rather than being widened by epsilon. The declared parameter domain must equal the exact active knot domain. Canonical serialization normalizes rationals before SHA-256 binding.

The construction includes exact planar/bilinear examples, a genuinely rational weighted example, and signed `1/1000000` parameter neighbours. Binary floating point and global tolerance are excluded from exact source authority.

## What the route does not establish

An exact parametric boundary patch is not an exact solid by declaration. This route does not certify trim curves, trim-region topology, seam consistency, watertight shell closure, shell orientation, positive-volume interior, or exact inside/outside material membership. A caller cannot promote kernel validity, opaque STEP/NURBS/B-rep import success, a mesh/tessellation, or a self-asserted `watertight` flag into those missing authorities.

For that reason solid-membership requests fail closed with `PB-007-03`. Nonzero source uncertainty remains `UNCERTIFIED_SOURCE` even when nominal patch evaluation itself is exact. Holder/access authority remains separate from cutter geometry.

## Gate status

PB-007-03 **remains open** because the frozen admitted source domain is broader than this bounded exact boundary language and no universal source-solid trim/shell/membership construction has been established. PO-02 and PO-05 remain OPEN. PB-007-01 remains OPEN, PB-007-02 remains dependent on it, and PB-007-04 remains OPEN_PROPAGATED. MC-B and MC-1 remain `NOT_ESTABLISHED`.

The 26-operation denominator is unchanged. Source/audio/provenance, canonical-journal intent, source uncertainty, positive-volume material, holder/access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are preserved. No native, paid, production or expensive execution is authorized by this work.
