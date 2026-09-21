# Domain, material semantics and numerical contract

Status: **MC-A domain lock accepted by MC-005 for the current MC-1 tranche**. Owners: MC-002–005, sweep tasks MC-018–023 and profile decision MC-054. Read [programme](00-PROGRAMME.md) and [proof specification](02-COMPLETENESS-ARGUMENT.md). MC-A acceptance fixes the requirements boundary; it is not a constructive-completeness, native-geometry, STEP or scale claim.

## Process-first domain

Define admissibility from physical/product semantics before testing a solver. Inventory bounded volumetric stock, subsequently machined states, multiple bodies, cavities, thin webs and imported-stock validity; finite effective cutting solids including flat, ball/rounded, corner-radius, drill, form and accessible undercut families; engaged finite continuous piecewise motion including lines, arcs, polylines, splines, stationarity, reversals, self-crossings and arbitrarily dense finite segmentation; conventional lathe spindle/feed relations; rigid setups, re-clamping/re-chucking and lathe → mill → lathe histories. Fixed tool axis during an individual three-axis milling operation does not forbid a later reoriented setup.

Classify threads, synchronized/phase-dependent turning, tapered/formed/internal cuts, finite cutter length, nonconvex cutting regions, eccentric setups and accessible undercuts explicitly. Do not relabel an ordinary operation as five-axis or unsupported because a height field or axisymmetric provider cannot represent it. Disputed boundaries remain open with product/machine justification until their integration owner resolves them. Continuous five-axis reorientation, additive processes, deformation and force simulation are not silently added.

A finite source description is necessary but does not itself prove decidability. State an effective deterministic constructor language, parameter/coefficient domains and source-to-language mapping. Do not admit arbitrary unanalysed executable predicates and assume a terminating solver follows. Equally, do not define the language merely as the current solver's successful subset. An uncovered ordinary machining constructor is a PO-01/02/05 gap.

### MC-002 reviewed constructor/physical-validity artifact

MC-002 records the reviewed candidate-independent constructor and witness map at `research/machining-completeness/tasks/MC-002/domain-contract-v1.json`. It is a requirement/design artifact, not native geometry evidence and did not by itself accept MC-A. The map explicitly covers ordinary lathe, fixed-axis three-axis mill, re-clamp/reorientation, cross-machine, parting/multi-body and complete-removal histories; it also binds boundary/pathology policy and physical witnesses without using provider success as an admissibility oracle.

For MC-1, a mill tool axis is fixed during one admitted cutting operation. Indexed/reoriented work is represented by an explicit non-cutting setup transition and a later operation; continuous cutting-time five-axis reorientation is outside the current MC-1 tranche. A drill cutting solid is machine-neutral and may be used in a witnessed lathe or mill setup. Fixed-axis helical motion is represented explicitly rather than inferred from a planar arc.

MC-002 intentionally left two product boundaries for its integration owner rather than deciding them from provider convenience: `DD-002-04` covers compound lathe live/driven-tool semantics, and `DD-002-05` covers simultaneously controlled multi-spindle/transfer-machine semantics. Their historical MC-002 records remain unchanged. MC-005 resolves both for the current tranche in the integration section below without removing any of the 26 admitted operations.

### MC-003 reviewed numeric/encoding artifact

MC-003 records the reviewed exact-source and compatibility contract at `research/machining-completeness/tasks/MC-003/numeric-encoding-contract-v1.json`. Existing `msac-journal/1.0` documents are not migrated in place: their signed 64-bit nm/nrad/ns/rate tokens and q15 quaternion tokens retain exactly the meaning frozen by RCS-002, including reject-on-overflow, ties-to-even source canonicalization, the right-handed column-vector transform convention and mathematical normalization of exact q15 rationals. The historical RCS-002 fixtures remain extension-free and pinned as compatibility controls.

For stronger MC-1 source semantics, `mc-exact-source/1.0` is an additive required extension/profile rather than a redefinition of v1. It uses canonical arbitrary-precision rationals, exact rational fractions of a full revolution and directed interval endpoints with explicit dimensions. It gives exact finite semantics to line/arc/helix/polyline/B-spline/piecewise/timed-phase motion, including spindle/path phase correlation, without decimalizing π or using an untyped epsilon as geometry truth. Unsupported readers reject an extension-bearing revision rather than downcasting it, and any migration creates a new revision with source identity; information absent from an old quantized journal is never reconstructed by fiat.

The legacy one-nanometre source quantum is not a derived feature-size floor. Exact predicates do not imply exact constructions; nominal arithmetic and source/tool/machine/metrology uncertainty remain separate channels. Production persistence for the exact-source tokens remains an open implementation choice rather than a semantic-domain gap. Practical coefficient/event limits are bounded by the frozen qualification/resource contract and later scale work. The historical MC-003 artifact propagates `DD-002-04` and `DD-002-05` exactly as inherited from MC-002; MC-005 subsequently resolves their current-tranche status without rewriting MC-003.

Historical verifier compatibility note: MC-002 and MC-003 completed before the integration review with the explicit statement **MC-A remains `NOT_ESTABLISHED`**. That sentence is retained here only as a faithful pre-MC-005 marker; the current gate state is the MC-005 decision below.

### MC-005 integrated domain lock

The canonical integration record is `research/machining-completeness/tasks/MC-005/domain-lock-review-v1.json`. MC-005 cross-checks MC-002, MC-003, MC-004 and MC-056 and accepts PO-01 plus MC-A for the current MC-1 tranche.

The machine/process boundary is **conventional lathe plus fixed-axis three-axis mill**, composed through finite explicit setup histories. The frozen denominator remains exactly the same 26 admitted operation/composition classes in MC-002 and MC-004. Provider refusal, implementation weakness or later candidate performance cannot remove a case from that denominator.

The two previously open product decisions are resolved prospectively from programme scope:

- `DD-002-04` — simultaneously controlled compound turn-mill/live-tool kinematics are **outside the current MC-1 tranche**. A workpiece achievable through the admitted lathe, mill, re-clamp and machine-transition history remains in scope; this decision does not permit rejection of any admitted operation merely because a commercial machine could combine the actions in one setup.
- `DD-002-05` — simultaneously coordinated multi-spindle/transfer-machine process semantics are **outside the current MC-1 tranche**. Conventional lathe/mill work with explicit re-chuck/re-clamp, body retention and cross-machine transitions remains in scope.

Neither decision is based on a solver/provider limitation, and neither shrinks the current operation denominator. Future addition of compound turn-mill/live tooling, coordinated multi-spindle transfer, continuous five-axis cutting, additive processes or another process class requires a new reviewed domain/profile version before candidate testing. Such a revision cannot retroactively pass a candidate failure or rewrite this MC-A evidence.

MC-A acceptance states what the programme must solve and the exact request against which it will be judged. It does **not** establish a terminating constructive route, native material/topology correctness, engineering B-rep/STEP realization, independent consumer usability, practical scale or MC-1 acceptance. Those remain owned by later gates and proof obligations.

## Physical witness

Each mandatory fixture records stock/tool definitions, cutting versus non-cutting regions, engagement intervals, machine travel/kinematics, access, holder/fixture clearance where relevant, support assumptions, setup transforms and post-separation handling. A body machined after parting must remain held or be explicitly re-clamped; a free detached remnant cannot remain magically fixed. This does not require chip dynamics.

Physical-validity checking must not call candidate success as its oracle. A collision or out-of-process decision needs its own witness. Keep invalid witnesses and replace their capability role only by a reviewed manifest amendment. Never move failed valid cases out of the denominator. Imported stock must have explicit boundedness, orientation/closure, body identity, units and representation/uncertainty contracts; successful import alone is not material validity.

## Nominal material

Use a common workpiece frame. For body b, effective cutting solid T, engaged intervals E and cutter-to-workpiece placement K(t):

```text
S = closure(union over t in E of K(t)(T))
M_next,b = closure(interior(M_b \\ S))
```

Specify endpoints, engagement boundaries, finite cutter shoulders and tool/setup revisions. Engaged teleportation is invalid motion, not an optimization. Regularization removes lower-dimensional artifacts, not positive-volume slivers.

Candidate geometric components are closures of connected components of one material set's interior. Durable manufactured bodies remain separate identities even if boundaries coincide. Point/edge contact does not establish volumetric connection. Face-contact cases require local-interior analysis plus the separate identity rule; a blanket all-contact-splits rule is wrong. Body transitions must be explicit and validated, never inferred from kernel handles, tessellation IDs or nearest/largest faces.

Differentiate tangent no-removal, exact retrace, positive new removal however small, connectivity-changing cuts, whole-body removal and physically uncertain outcomes. Positive commanded penetration into already removed material is not positive new removal. No-op claims need set reasoning or certificates; positive removal may use an independently checked positive-volume witness instead of subtracting nearly equal large volumes. A final empty material state is valid and produces an explicit disappearance transition, not an invented residual solid.

Pure-removal algebraic simplifications are permitted only under proved hypotheses in unchanged coordinates and compatible target/setup semantics. Chronology can affect access, targets, definitions, setup and provenance. Preserve the immutable journal even when derived duplicate sweeps are eliminated. Unevaluated expressions, replayability or cached fields alone are not completed material evaluation.

## Precision and uncertainty

Audit the existing `msac-journal/1.0` signed 64-bit nanometres, nanoradians, curve definitions and exact-rational quaternion tokens against the domain. Existing journals retain exactly their saved meaning. Integer input coordinates do not imply a lower bound on derived feature size. A required richer definition needs a versioned profile/extension, migration/new-revision rules and compatibility tests. Do not pretend to recover information already lost in an old quantized input.

Compute nominal geometry while separately preserving tool/machine/metrology/source uncertainty. Increased arithmetic precision can improve the nominal answer, not make measurements exact. Measurement uncertainty cannot erase a known nominal cut. Requests must separate source-to-nominal uncertainty from nominal-to-output numerical error.

Use certified floating filters, outward-rounded intervals, higher precision and exact rational/algebraic or other reviewed decisions. Exact predicates are not exact constructions. Prohibit a dimensionally untyped global epsilon, tolerance-as-sign, silent overflow/nonfinite propagation and unqualified flush-to-zero in authority paths. Record compiler flags, rounding, arithmetic libraries and versions.

Encode certificate quantities as exact integers/rationals/decimal strings with specified meaning or directed interval endpoints; ordinary JSON floating-point serialization must not destroy a claimed guarantee. Include physical units and dimensional types, including squared distance. Check transforms and serialization in the independent checker.

## Accuracy vector and error chain

Freeze dimensional/surface-distance limits; smooth-patch angular limits with corner/nonsmooth rules; separate missing and extra material bounds with absolute and relative volume rules; exact components/voids/channels and protected local features; analytic-entity retention; and source uncertainty separately from numerical error. Empty-state comparisons avoid undefined relative volume. Global volume cancellation cannot establish local geometry or topology.

Track source, canonicalization, transform, cutter, sweep, representation, reconstruction, sewing and serialization channels. Unknown dependence composes conservatively; do not assume RSS independence, charge the same source uncertainty repeatedly or reset error at handoffs. Recomputing from exact nominal authority can remove prior derived error only when the actual recomputation proves that removal.

The initial research ladder is 10, 1 and 0.1 micrometres plus local requests below w/8 for certified positive feature width/gap w. Exact-zero neighbours use event/topology decisions. These are experiments, not a feature-size floor or theorem that distance preserves topology. Preserve the historical RCS-021 150 mm³ interval criterion for reproduction only.

### MC-058 certified curve/transform and sweep-bound contract

MC-058 records the source-faithful curve, transform and finite-cutter enclosure contract at `research/machining-completeness/tasks/MC-058/curve-sweep-contract-v1.json`. It does not replace MC-003 source semantics: line/arc/helix/polyline/B-spline/piecewise/timed-phase definitions, exact endpoints, engagement boundaries, transform order and immutable saved operations remain authoritative. Approximation is a derived representation only.

Circular arcs retain exact rational `turn_fraction`; subdivision uses a conservative rational upper bound on π only to enclose chord sag, never as an equality value or predicate authority. Non-rational B-splines retain exact Cox-de Boor and knot-multiplicity semantics and may be enclosed through exact knot insertion/control hulls or exact rational derivative bounds. Piecewise and timed/phase motion cannot be fitted across semantic boundaries or factored into independent path/angle coverage.

For an effective cutter with certified support radius `rho` covering the complete cutting region, including finite radius/length/shoulders, and an approximate pose over the same closed engaged source parameter set, the conservative actual-sweep transfer is:

```text
e_total = e_inherited + e_translation + rho*e_rotation + e_tool
```

where rotation error is a certified angular upper bound in radians. A centreline-only error is therefore insufficient whenever finite cutter extent or orientation error contributes. The formula is a geometric enclosure, not a topology, material-membership or exact-zero event certificate. Exact rigid transforms preserve distance bounds; reclamps and machine transitions inherit rather than reset upstream error.

`PB-007-01` and `PB-007-02` remain open. MC-058 does not decide all tangential/multiple/singular transcendental equalities and does not establish the unconditional general coupled helical/spindle-feed/eccentric sweep-membership route. PO-02, PO-05 and PO-06 remain open under their existing owners. No native or paid campaign ran, and **MC-B remains NOT_ESTABLISHED**.

## Domain-lock outputs

MC-002 supplies the constructor/process/physical-witness map; MC-003 supplies exact numeric/curve/transform semantics and compatibility decisions; MC-004 supplies candidate-independent intended-session workloads, accuracy, reference hardware and usable time/memory envelopes; MC-005 integrates those artifacts, resolves the remaining current-tranche product boundaries, accepts PO-01 and records **MC-A = ACCEPTED**. Later scope additions must be prospective reviewed versions and must not weaken the frozen current-tranche target.
