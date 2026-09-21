# MC-058 — Certified curve, transform and swept-volume approximation contract

Status: **COMPLETED_RESEARCH** with inherited proof/event obligations left open. Issue: #120. Source baseline: `54a75e34e93f21964e93ba05a0391033d4081f3d`.

## Purpose and result

MC-058 freezes a source-faithful approximation/enclosure interface between the exact MC-003 curve/transform language and the later actual-sweep implementations in MC-018–MC-023. It does **not** claim native cutter-sweep construction, universal exact event decidability, topology correctness, STEP qualification or MC-B acceptance.

The central result is that curve approximation may be derived from, but may not replace, the saved nominal operation. Every admitted motion class now has an explicit evaluator/enclosure rule and either a checked finite bound or a named inherited open obligation. Rigid setup transforms, reclamps and machine transitions receive the same treatment. The contract is machine-readable in `curve-sweep-contract-v1.json`; `verify.py` independently exercises exact and adversarial controls using only Python exact rational arithmetic.

No native or paid geometry campaign was run.

## Authority and preserved semantics

The task consumes the reviewed MC-003 exact-source contract, MC-008 proof/arithmetic integration and MC-010 independent-control foundation. Their exact producing artifacts are pinned in the contract. Historical `research/rcs-*` inputs and source/audio/provenance evidence are untouched.

The following rules are non-negotiable:

- an old saved operation is never rewritten to its approximation;
- exact endpoints and engagement boundaries remain authoritative;
- setup, tool and target boundaries are not fitted across;
- exact retraces stay in the immutable journal even when derived computation can reuse work;
- source uncertainty and nominal numerical error remain separate channels;
- an inherited error channel cannot silently become zero at a provider, piece, reclamp or machine transition;
- certifying quantities use exact rationals/directed endpoints with dimensions, not binary JSON floats or a global epsilon.

These rules preserve the MC-A domain lock rather than narrowing it to what a convenient interpolator can solve.

## Curve classes

### Stationary and line motion

A stationary piece is a constant exact pose over the source interval. A line remains the exact affine map `P(u)=(1-u)P0+uP1` on closed `[0,1]`. Exact rational evaluation therefore has zero source-level curve error. If a downstream numerical evaluator approximates either piece, it must expose a directed positional enclosure rather than changing the source.

Signed-neighbour controls around an interior line parameter prove that the exact boundary value is distinct from its left/right neighbours. Stationary controls verify that subdivision itself does not manufacture motion.

### Circular arcs

The source remains an oriented rigid rotation defined by exact center, start radial vector, axis and rational `turn_fraction`. π is not decimalized and no assumption is made that arbitrary trigonometric values are algebraic.

For a circular arc of radius `R`, exact turn magnitude `|s|`, and `N>0` equal derived subarcs, use

```text
theta_bar = 2 * (22/7) * |s| / N
sag <= R * theta_bar^2 / 8
```

`22/7` is used only as a conservative upper bound on π. The sag inequality follows from `1-cos(x) <= x^2/2`; it is not an equality test and not predicate authority. The source-semantic endpoint is restored exactly at the semantic boundary rather than reconstructed from a sampled chord.

The exact control uses `R=3`, `s=1/4`, `N=4`, giving `theta_bar=11/28` and `sag<=363/6272` with exact rational arithmetic. A quarter-turn endpoint control independently maps `(1,0,0)` to `(0,1,0)`.

This does not discharge `PB-007-01`: a conservative enclosure does not decide every tangential, multiple or singular transcendental equality event.

### Helical arcs

A helix binds the circular rotation and exact axial interpolation to the same exact parameter `u`. Derived subdivision must split both together. The circular transverse enclosure applies; an exact linear axial term adds no source-level error, while any approximate axial evaluator must contribute its own explicit enclosure.

Decoupling angular and axial progress is forbidden. `PB-007-01` and `PB-007-02` remain open where exact singular-event or general coupled helical/spindle-feed/eccentric membership decisions are required.

### Polylines

A polyline remains a finite ordered composition of exact line pieces. Vertices are hard semantic boundaries. A derived representation may subdivide inside a line or exactly at a vertex but may not replace two adjacent segments with a cross-vertex shortcut. Source-semantic zero-length pieces remain present when they carry an engagement or other boundary meaning.

Boundary controls approach a shared vertex from the left and right and verify the two source segments remain distinct even though they share the exact endpoint.

### Non-rational B-splines

The spline source is the exact MC-003 non-rational B-spline: exact degree, rational knots, exact control points and Cox-de Boor semantics. Knot multiplicity is semantic; no knot epsilon is permitted.

Derived evaluation/enclosure may use exact knot insertion and span subdivision. Two conservative enclosure routes are allowed:

1. the exact local B-spline/Bézier control hull, which contains the curve on the leaf; or
2. an exact componentwise derivative upper bound. If `L` is a rational L1 upper bound on curve speed over a leaf of parameter width `h`, then point displacement over the leaf is at most `L*h` in Euclidean norm because the L1 norm upper-bounds it.

The exact quadratic control `[(0,0),(1,2),(2,0)]` gives `(1,1)` at `u=1/2`. Its derivative L1 bound is `6`, so a leaf of width `1/16` has displacement bound `3/8`.

This is an enclosure interface, not a claim that arbitrary requested zero error can be reached by finite subdivision.

### Piecewise and timed/phase motion

Piecewise motion retains ordered piece boundaries and their shared-boundary policy. No fitting may cross an engaged discontinuity or a setup/tool/target/engagement transition. Per-piece error budgets are unioned/composed; they do not restart.

Timed/phase motion keeps time, path progress and spindle phase on the same exact chronology. Subdivision uses the same exact time interval for all channels. Replacing synchronized motion with independent full-angle coverage is forbidden. The deterministic control at `t=1/2` simultaneously produces path progress `1` and spindle phase `1/4` turn; those values are not independently selectable.

## Rigid transforms and setup transitions

The MC-003 convention remains authoritative:

```text
p_parent = R(q) * p_child + t
```

Frames are right-handed, points are column vectors, and composition order is explicit. The exact q15 source components are mathematically normalized; a backend may not apply the raw quaternion as though it were already unit length.

A proper rigid transform preserves distances, so an already certified spatial bound is covariant under an exact setup transform. An approximate transform must separately enclose translation and rotation-angle error. The exact control uses raw quaternion ratio `(1,0,0,1)` plus translation `(10,20,30)` and maps `(1,0,0)` to `(10,21,30)` while preserving squared distances.

A reclamp or machine transition creates a new immutable setup/frame definition. It does not mutate historical coordinates, guess a body target or reset inherited error.

## Actual finite-cutter sweep transfer

A centreline bound is not an actual-sweep certificate.

Let the effective cutting solid have certified finite support radius `rho` from the declared cutter-frame origin. `rho` must cover the **complete cutting region**, including radial extent, finite axial length, shoulders and admitted nonconvex/undercut extent. Let an approximate pose cover the same closed engaged source parameter/time set as the nominal pose. If, for every source parameter,

- translation displacement is at most `e_translation`; and
- orientation angular displacement is at most `e_rotation` radians,

then each cutter point moves by at most

```text
e_translation + rho * e_rotation
```

because rotational chord displacement is at most `rho * angle`. If the cutter representation itself has certified Hausdorff error `e_tool`, and an upstream numerical channel `e_inherited` still applies, the conservative transfer is

```text
e_total = e_inherited + e_translation + rho*e_rotation + e_tool
```

under unknown dependence. This is an upper bound on geometric sweep displacement for common source parameter coverage. It is **not** a topology, material-membership or exact-zero event certificate.

The finite-cutter control uses radial extent `3` and axial extent `4`, requiring support radius `5`. With `e_translation=1/1000` and `e_rotation=1/10000`, the pose/sweep bound is `3/2000`, not the centreline-only `1/1000`. Adding `e_inherited=1/4000` and `e_tool=1/2000` gives total `9/4000`. Corrupt controls that use radius `3`, drop rotation, trim endpoints or reset inherited error are rejected.

## Proof boundary and retained blockers

MC-058 intentionally does not turn an approximation bound into a constructive-completeness theorem.

- **PB-007-01 remains OPEN.** Exact decisions for required tangential, multiple and singular transcendental events are not universally established. An enclosure may remain `UNCERTIFIED` at equality; it must not guess a sign.
- **PB-007-02 remains OPEN.** The unconditional constructive route for general coupled helical/spindle-feed/eccentric sweep membership remains unestablished. Shared time/path/phase correlation must survive any later solution.
- **PO-02 remains OPEN.** MC-018–MC-023 still own actual process-specific cutter-sweep construction and qualification.
- **PO-05 remains OPEN.** Finite subdivision formulas do not discharge the inherited universal event/termination blockers.
- **PO-06 remains OPEN.** This task supplies one error-transfer rule, not the full source-to-reconstruction error certificate.

Accordingly **MC-B remains NOT_ESTABLISHED**. MC-C, MC-D, MC-E, MC-F and MC-1 are also unchanged.

## Adversarial verification

`verify.py` uses `fractions.Fraction` and candidate-independent local mathematics. It checks exact line, quarter-arc, helix, quadratic-spline, transform-covariance, polyline-boundary, timed-phase and finite-cutter controls. It then mutates the contract and requires rejection of, among other defects:

- saved-source mutation;
- missing endpoint or engagement authority;
- π replaced by a convenient decimal/rational equality assumption;
- assumed algebraic trigonometric constants;
- arc epsilon fitting;
- polyline cross-vertex fitting;
- spline knot snapping;
- independent-angle phase substitution;
- unit/handedness/transform-order weakening;
- reclamp error reset;
- centreline-only sweep certification;
- cutter support radius that ignores axial length;
- endpoint trimming;
- inherited/tool error removal;
- inherited blocker closure; and
- premature MC-B acceptance.

## Verification commands

```text
python3 research/machining-completeness/tasks/MC-058/verify.py --contract
python3 research/machining-completeness/tasks/MC-058/verify.py --self-test
python3 tools/mc_workflow.py verify MC-058
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

## Downstream use

MC-018–MC-023 may now consume one explicit curve/transform/sweep-bound interface instead of inventing per-provider fitting rules. Each still has to construct and qualify its actual cutter family and process semantics. MC-038 may consume the same artifact in the later MC-B integration review, but it must retain every unresolved proof/event blocker and cannot promote this planning/model evidence to native geometry evidence.
