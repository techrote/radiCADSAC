# MC-038 / PB-007-01 — frozen V44 global monotonicity → actual V45 algebraic split bridge

**Status:** bounded candidate, 30 October 2026. **Parent:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100), [preregistered #6516555539](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6516555539). **Initial base:** main 05dd7e1cb62ccc261f6a4e6ec63c6d9a6cebf8dd, after [PR #314](https://github.com/techrote/radiCADSAC/pull/314). This candidate is not yet merged-main qualified and does not change the historical MC-B/MC-1 verdict.

## Gap and falsifiable hypothesis

V45 already produces exact source-polynomial restrictions over a real algebraic field Q(alpha) for a single irrational orientation cut, but its physical irrational-phase endpoint evaluation is deliberately deferred. [PR #314](https://github.com/techrote/radiCADSAC/pull/314) proves F'(t)>0 over the complete *original rational source* for the one frozen V44 case, and [PR #311](https://github.com/techrote/radiCADSAC/pull/311) supplies the exact source-replayed original physical-root atlas with event-neutral proof cuts. No existing consumer connects these specific two authorities to V45's **actual** field representation.

**Hypothesis:** the real V45 Q(alpha) bisection of this precise source is exactly the same irrational original-source proof cut as V41/V46, and both V45 children are positive-width, source/phase/coefficients-preserving affine restrictions. The source-wide strictly positive derivative then proves F_child'(u)>0 by the exact chain rule; the nonzero cut sign plus the complete physical-root atlas allocates the already-proved unique simple source root to exactly one V45 side. The bridge must not evaluate sin/cos at alpha, create a new analytic child root solver, upgrade historical V45/V47 or change v54's BLOCKED outcome.

Any wrong field embedding, source polynomial, phase law, cut identity, affine width, physical endpoint sign, root conservation, whole-source derivative, report replay or source pin must produce BLOCKED/RESOURCE_REFUSAL nontruth.

## Original frozen source and exact producing identities

- Case: harvested:verify_pb00701_v44:ffaea08e30c9.
- Canonical source SHA-256: d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2.
- Source: rational degree-2 B-spline lowered to t in [0,1], phase turns -1/8 + t/16.
- Harmonics: C1 = -3/2 + t + 2t², S1 = -1/2 - t + 2t², C2 = 1/100000000, S2 = 0.
- Frozen v54 case and actual V44 classifier are still BLOCKED with exact reason ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING.
- The existing V45 file is pinned at Git blob c055e7f392a921b386a1a99cc70b5004121ae7f6, and the PR #314 derivative model at 2c1282de6b0a03088b1cbd86c62d43b192301d20. #314 pins the #313/#311/#310/frozen corpus/trig/domain/authority ancestry. No predecessor edits are allowed.
- The physical source derivative lower bound is a strict exact rational 3402574703095661/10276044800000000 on all t in [0,1]; its 16-cell proof and strict endpoint signs are **replayed**, not rederived from the V45 report.

## Mathematical transport, without irrational-phase endpoint arithmetic

For source F(t)=Σ_h(C_h(t)cos θ_h(t)+S_h(t)sin θ_h(t)), θ_h(t)=2πh(o+rt), let alpha be the unique V45 exact isolated real root. The old V45 representation is a pair of maps

- left t = alpha*u, u∈[0,1];
- right t = alpha + (1-alpha)*u, u∈[0,1].

Both widths alpha and (1-alpha) are proved positive in the exact real field (by V45 field sign isolation, not an IEEE approximation). Each child polynomial coefficient is the reviewed V45 exact composition C_h(a+wu), S_h(a+wu), with independently checked full harmonic support and exact phase law offset o+r*a, rate r*w. Exact source-coordinate end maps cover [0,1] without gap, overlap, orientation reversal or dropped source terms. These are *representations*, not certification that a rational-only trig classifier can consume irrational-phase coefficients.

The source-wide theorem certifies F'(t)>m>0 for all t in the original closed source. Therefore for either V45 child, d/du F(a+wu) = w*F'(a+wu)>m*w>0 for all u∈[0,1]. **m is rational, w is a strictly positive real algebraic element**; this is a strict symbolic lower bound, not a fabricated rational bound or trig evaluation at alpha. It does not require computing sin(2πh(o+r alpha)) or introducing an unproved algebraic-value trig evaluator.

V45's defining minimal polynomial and real embedding must be proved **exactly identical** to the already source-owned V41/V46 cut via the existing polynomial GCD + Sturm unique common root equality proof, not by overlapping rational isolation intervals. The cut's physical value is already certified *nonzero*; the atlas's exact left/right signs, conservation of one simple root and source positivity determine which V45 child contains it. The cut is not a physical zero merely because it is a proof geometry split.

This is a **bounded source-coordinate certificate on one frozen source**, not a general Q(alpha) child analytic theorem, not a new complete-root oracle, and not a sufficient derivative theorem for arbitrary admissible V41/V47 inputs.

## Review and falsification controls

The new model rereads the frozen source, full original root partition/atlas and exact PR #314 derivative proof; reconstructs V45 representation from the source polynomials/phase; pins both exact predecessor Git blobs; requires V45's original representation-only and unconsumed-cut flags; checks source-material identity and SHA-256. It verifies each restricted polynomial against regenerated field composition, exact V45 two-child phase and source maps, positive field widths, field record canonicality, exact GCD/Sturm alpha identity, physical nonzero endpoint relation, and total child root-count conservation. The returned report carries exact field data, ordered root counts, strict source bound, algebraic maps, deferred historical endpoint authority and every explicit nonpromotion flag.

Submitted reports are bounded in depth/node count before JSON serialization, sized, then fully compared against a source-regenerated canonical report. Malformed deep/cyclic/oversized input and model budget/exhaustion are typed resource nontruth. The test suite includes forged root side, field embedding, source map, source SHA, cut-equality method, V45 representation/source drift, derivative failure, atlas sign tampering, source pin drift, nonpositive child width, report forgery and attempted gate promotion.

Run on the **exact checkout**:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_v45_monotone_child_bridge.py --contract --self-test

The focused literal-head workflow and mc1-static must pass on the final source. A documented exact-head technical review, tree comparison, expected-head-protected merge and actual merged-main workflows are required for qualified landing. Preserve each failed attempted head/CI and its repair instead of claiming pass by re-running a different revision.

## Remaining obligations and invalidation

The historical V45 V41/V47 route's *general* irrational-phase endpoint/event and arbitrary-source derivative-certificate interface remains unproven. The original V45 report's endpoint_event_authority remains ALGEBRAIC_IRRATIONAL_PHASE_ENDPOINT_AUTHORITY_NOT_ESTABLISHED and analytic_cut_consumed remains false. This one frozen root partition/derivative restriction does not reclassify or admit the immutable v54 case, does not establish PB-007-01/MC-B/MC-1 and is not an independent physical oracle. No native material, topology, B-rep/STEP, user-facing service, expensive campaign or production repository is authorized.

The supported lathe/mill domain keeps all 26 operation IDs, valid finite histories, phase/path/source semantics, disjoint material bodies, exact proof/event and refusal classifications, and conventional usable STEP obligation. If V45's field builder, V41/V46 exact cut equality, original source/trig proof or authority changes, invalidate this bridge and rerun source-matched qualification.

**Next bounded technical question:** whether a *general* V41 proof-cut list can carry a compositional source-bound derivative/event certificate at every cut, with explicit multi-cut field-embedding identities and exhaustion semantics, without silently replacing the historic rational-only child classifier or inferring transcendental endpoint truth from algebraic source coefficients.
