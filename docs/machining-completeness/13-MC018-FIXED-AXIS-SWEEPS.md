# MC-018 fixed-axis flat/corner-radius sweep construction

Status: **MC-018 completed research; programme-wide sweep and completeness obligations remain open.** This note reconciles the executable MC-018 construction with the accepted MC-A domain and MC-058 curve/sweep-enclosure contract. The task-local machine contract remains authoritative at `research/machining-completeness/tasks/MC-018/fixed-axis-sweep-contract-v1.json`.

## Scope

MC-018 covers finite fixed-axis flat-end and corner-radius milling cutters. It does not cover ball/round cutters (MC-019), form/nonconvex/undercut cutters (MC-020), lathe process reductions or synchronized turning (MC-021/022), or setup/body composition (MC-023). Cutter orientation is fixed within one admitted milling operation; later reorientation is an explicit setup transition.

For flat cutters the local cutting solid is the finite cylinder `x^2+y^2 <= R^2`, `0 <= z <= L`. For corner-radius cutters the upper region is the finite radius-`R` cylinder and the lower profile uses core radius `a=R-c` with exact rounded relation `(rho-a)^2 + (z-c)^2 <= c^2`. Positive finite cutter length is mandatory; centreline-only and infinite-extrusion substitutes are not admissible.

## Exact source slice

Stationary, line and polyline translations use exact rational source coordinates and exact closed engaged intervals. Simultaneous XYZ motion is therefore first-class rather than reduced to constant-Z machining. Flat-cutter line membership is an exact axial-interval intersection plus quadratic radial minimum. Corner-radius line membership splits cylindrical/core branches from the lower fillet; the fillet existential is decided using exact rational polynomial arithmetic and Sturm isolation.

Retraces and reversals remain in immutable source history even though swept-set union is idempotent. Engaged teleportation is rejected. Exact-line evaluation accepts only the source classes `stationary`, `line` and `polyline`; a nonlinear source leaf is never promoted to an exact line merely because a supplied enclosure happens to be zero.

## MC-058-derived nonlinear slice

Circular-arc, helical, spline, piecewise and timed/phase paths are consumed through finite source-bound MC-058 line leaves carrying a certified Euclidean translation enclosure `e`. The leaf must remain bound to its exact source interval, engagement state and semantic boundaries; time/path/phase correlation cannot be replaced by independent coverage.

For a cutter outer radius `R` and finite axial length `L`, the true sweep is enclosed by the union of approximate-segment cylinders with radius `R+e` and axial interval `[-e,L+e]`. A definitely-inside witness may use the central cutter cylinder shrunk by `e`: radius `core_radius-e` and axial interval `[e,L-e]` when nonempty. This yields only `INSIDE`, `OUTSIDE` or `UNCERTIFIED`; the unresolved shell is not converted into an equality sign, topology verdict or pass.

## Boundary and adversarial evidence

The deterministic verifier includes exact varying-Z flat tangency with signed neighbours, an exact rational corner-fillet boundary with signed neighbours, the same corner witness transported through simultaneous XYZ motion, retrace idempotence without source deletion, engaged-teleport rejection, unknown/unbound source-leaf rejection, and definite-inside/outside/uncertified MC-058 envelope controls. It also catches substitution of a corner-radius cutter by its enclosing flat cylinder and the unsafe promotion of a zero-error nonlinear leaf into the exact-line path.

Certifying authority rejects binary floating-point values and an untyped global epsilon. The contract mutation suite rejects loss of varying-Z support, deletion of retraces, removal of `UNCERTIFIED`, topology promotion, dependency drift and premature MC-B acceptance.

## Proof and capability boundary

MC-018 is deterministic construction/model evidence; no native or paid geometry campaign is implied. **PO-02 remains OPEN** because MC-018 supplies only one fixed-axis milling slice and later sweep/process tasks plus integration remain required. **PO-04, PO-05 and PO-06 remain OPEN** for general classification, finite progress and full error certification. MC-018 does not close inherited transcendental event blockers and does not establish topology, conventional engineering realization or STEP preservation.

Accordingly **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`**. Protected historical `research/rcs-*` source/audio/provenance evidence, canonical journal semantics, positive-volume material rules and durable body/lineage semantics are unchanged.
