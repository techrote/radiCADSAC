# PB-007-03 v6 — exact trimmed convex shell and solid-membership route

Corrective issue: #176. Baseline: `c9c3a41877ec4c4e4c842873a291e746b3239a3e`.

## Result

A bounded exact source-solid route is now executable on top of the preserved PB-007-03 v5 rational parametric boundary codec. The route admits only zero-uncertainty, degree-1 × degree-1, equal-weight affine planar v5 patches with exact-rational strictly convex parameter-space trims. It binds source, role, units, frame, revision, configuration, patch SHA-256 identities, trim data and an exact interior witness.

Trim vertices are evaluated through the v5 exact Cox-de Boor path. Closure is not inferred from a kernel flag: every mapped geometric trim edge must occur exactly twice with the opposite orientation, face incidence must be connected, and the bounded route requires exact genus-0 `V-E+F=2`. Outward orientation is certified by a strict exact-rational interior witness. Convexity is independently checked by requiring every shell vertex to lie on the nonpositive side of every oriented face plane.

For a certified shell, point membership is exact. Exact half-space signs produce `INSIDE`, `BOUNDARY`, or `OUTSIDE`; no epsilon, tessellation, binary float, timeout, importer success, or kernel watertightness enters correctness authority. Signed `±1/1000000` neighbours at a face are deliberately distinguished.

## Adversarial boundary

The deterministic verifier covers valid closed cube certification, exact inside/boundary/outside queries, `1/1000000` signed neighbours, trim-domain escape, nonconvex/bow-tie and degenerate trims, non-affine and unequal-weight patches, nonzero source uncertainty, missing/micro-gapped seams, duplicate or wrong seam incidence, inward orientation, invalid interior witnesses, source/role/units/frame drift, stale patch hashes, binary-float authority, mutated certificates, opaque STEP/kernel/watertight claims, backend topology/body/lineage laundering, denominator shrinkage, and false MC-B promotion.

## Residual blocker

`PB-007-03` **remains OPEN**. This route establishes a useful exact trimmed **convex polyhedral** solid subset, not universal source-solid authority. The frozen 26-operation domain still admits imported stock and arbitrary form/undercut sources whose curved trims, non-convex shells, opaque import representations, or more general rational/NURBS boundaries are not lowered by this certificate route. That missing constructor remains a gap, not an exclusion.

Accordingly PO-02 and PO-05 remain OPEN, PB-007-01 remains OPEN, PB-007-02 remains dependent on PB-007-01, PB-007-04 remains OPEN_PROPAGATED, and MC-B / MC-1 remain `NOT_ESTABLISHED`. This is not an impossibility theorem and does not authorize an MC-B retry.

Historical PB-007-03 v4/v5 evidence is preserved. No native, paid, production or expensive campaign ran. Source/audio/provenance, canonical-journal meaning, source uncertainty, positive-volume material, holder/access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged.
