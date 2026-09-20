# Domain, material semantics and numerical contract

Status: adopted requirements and an explicit research specification, not a completed domain lock. Owners: MC-002–005, sweep tasks MC-018–023 and profile decision MC-054. Read [programme](00-PROGRAMME.md) and [proof specification](02-COMPLETENESS-ARGUMENT.md).

## Process-first domain

Define admissibility from physical/product semantics before testing a solver. Inventory bounded volumetric stock, subsequently machined states, multiple bodies, cavities, thin webs and imported-stock validity; finite effective cutting solids including flat, ball/rounded, corner-radius, drill, form and accessible undercut families; engaged finite continuous piecewise motion including lines, arcs, polylines, splines, stationarity, reversals, self-crossings and arbitrarily dense finite segmentation; conventional lathe spindle/feed relations; rigid setups, re-clamping/re-chucking and lathe → mill → lathe histories. Fixed tool axis during an individual three-axis milling operation does not forbid a later reoriented setup.

Classify threads, synchronized/phase-dependent turning, tapered/formed/internal cuts, finite cutter length, nonconvex cutting regions, eccentric setups and accessible undercuts explicitly. Do not relabel an ordinary operation as five-axis or unsupported because a height field or axisymmetric provider cannot represent it. Disputed boundaries remain open with product/machine justification. Continuous five-axis reorientation, additive processes, deformation and force simulation are not silently added.

A finite source description is necessary but does not itself prove decidability. State an effective deterministic constructor language, parameter/coefficient domains and source-to-language mapping. Do not admit arbitrary unanalysed executable predicates and assume a terminating solver follows. Equally, do not define the language merely as the current solver's successful subset. An uncovered ordinary machining constructor is a PO-01/02/05 gap.

### MC-002 reviewed constructor/physical-validity artifact

MC-002 records the reviewed candidate-independent constructor and witness map at `research/machining-completeness/tasks/MC-002/domain-contract-v1.json`. It is a requirement/design artifact, not native geometry evidence and not an MC-A acceptance. The map explicitly covers ordinary lathe, fixed-axis three-axis mill, re-clamp/reorientation, cross-machine, parting/multi-body and complete-removal histories; it also binds boundary/pathology policy and physical witnesses without using provider success as an admissibility oracle.

For MC-1, a mill tool axis is fixed during one admitted cutting operation. Indexed/reoriented work is represented by an explicit non-cutting setup transition and a later operation; continuous cutting-time five-axis reorientation is outside the current MC-1 tranche. A drill cutting solid is machine-neutral and may be used in a witnessed lathe or mill setup. Fixed-axis helical motion is represented explicitly rather than inferred from a planar arc.

The unresolved product boundaries remain named rather than silently narrowed: `DD-002-04` covers compound lathe live/driven-tool semantics, and `DD-002-05` covers simultaneously controlled multi-spindle/transfer-machine semantics. Provider limitations cannot resolve either decision. MC-003 still owns exact numeric/curve/phase/transform encoding, MC-004 owns workload/accuracy/resource requests, and MC-A remains `NOT_ESTABLISHED` until MC-005 reviews the combined domain lock.

## Physical witness

Each mandatory fixture records stock/tool definitions, cutting versus non-cutting regions, engagement intervals, machine travel/kinematics, access, holder/fixture clearance where relevant, support assumptions, setup transforms and post-separation handling. A body machined after parting must remain held or be explicitly re-clamped; a free detached remnant cannot remain magically fixed. This does not require chip dynamics.

Physical-validity checking must not call candidate success as its oracle. A collision or out-of-process decision needs its own witness. Keep invalid witnesses and replace their capability role only by a reviewed manifest amendment. Never move failed valid cases out of the denominator. Imported stock must have explicit boundedness, orientation/closure, body identity, units and representation/uncertainty contracts; successful import alone is not material validity.

## Nominal material

Use a common workpiece frame. For body b, effective cutting solid T, engaged intervals E and cutter-to-workpiece placement K(t):

```text
S = closure(union over t in E of K(t)(T))
M_next,b = closure(interior(M_b \ S))
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

## Domain-lock outputs

MC-002 supplies the constructor/process/physical-witness map; MC-003 supplies exact numeric/curve/transform semantics and compatibility decisions; MC-004 supplies candidate-independent intended-session workloads, accuracy, reference hardware and usable time/memory envelopes; MC-005 reviews the combined domain and records MC-A. Missing actual product values remain named unresolved decisions. They must not be filled with a candidate's conveniently achieved performance.
