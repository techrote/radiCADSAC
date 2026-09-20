# MC-003 — Numeric, curve, transform and encoding sufficiency audit

Status: **COMPLETED_RESEARCH** as a reviewed artifact dependency, subject to exact-head CI and merge. This task does **not** establish native geometry correctness, practical scale, STEP qualification or MC-A.

## Purpose and falsification criterion

MC-003 asks whether the MC-002 machining language can be given finite, exact source semantics without changing any saved `msac-journal/1.0` meaning, and whether a versioned precision/semantic extension is required for the stronger MC-1 domain.

The decisive counterexample was any required MC-002 trajectory/phase/setup constructor that could only be represented by silently reinterpreting old integer/q15 tokens, by inventing a feature-size floor from the one-nanometre storage quantum, by using an untyped epsilon as geometric truth, by losing phase/time correlation, or by accepting overflow/nonfinite/downcast behaviour in an authority path.

The reviewed result is `numeric-encoding-contract-v1.json`, schema `radicadsac-mc-numeric-encoding-contract/1.0`, bound to main `71516b60aa2f9cf536fe7937ef2fc544da3e4dd8` and the reviewed MC-002 outcome blob `930db704e9dd29955e7af99ba793c74e0cfda325`.

## Legacy journal conclusion

`msac-journal/1.0` remains frozen exactly as saved. Its signed 64-bit nanometre, nanoradian, nanosecond, rate and q15 tokens are exact mathematical values at their declared scales. Overflow is rejection, never wraparound. Source canonicalization retains round-to-nearest/ties-to-even and includes quantization in its declared normalization error.

The q15 quaternion tokens are exact rationals before mathematical normalization. Their durable rotation is the normalized mathematical quaternion, not a particular floating-point evaluation. The right-handed, column-vector transform rule remains `p_parent = R(q) * p_child + t`, and composition remains child-to-parent in the already documented order.

No old file gains a new extension marker. The two accepted RCS-002 fixtures remain pinned by blob identity and must continue to parse with `required_extensions: []`. Information that was not present because an old source was quantized cannot later be reconstructed by declaring more arithmetic precision.

## Why an additive MC-1 exact-source profile is needed

The base v1 token set is sufficient to preserve the meaning of existing v1 journals. It is not, by itself, a satisfactory exact source language for all semantic constructors added by MC-002. In particular, exact helical sweep, phase-sensitive spindle/tool correlation, exact spline coefficients/knots outside the fixed storage quantum, and certificate endpoints need a finite representation that does not decimalize symbolic turns or pretend binary floating JSON numbers are exact.

MC-003 therefore defines research profile/required extension `mc-exact-source/1.0`. It is additive: it does not redefine a single v1 token. A journal revision using it must declare the extension in the existing `required_extensions` mechanism. A reader that lacks the extension rejects that revision as unsupported; it must not downcast it to base v1. Adoption into a future production persistence format remains an implementation choice rather than a decision to store JSON.

The profile uses canonical arbitrary-precision rationals represented by decimal integer strings, exact rational fractions of a full revolution (`turn_fraction`) and directed interval endpoints. Numerators/denominators are reduced, denominator-positive and dimensioned. This supplies exact finite source coefficients without picking a practical coefficient-size limit; resource caps belong to MC-004 and later scale work.

## Curve, time and phase semantics

Every MC-002 trajectory constructor now has a finite exact interpretation:

- `stationary`: constant exact pose over a finite interval, with engagement retained;
- `line`: exact affine interpolation between exact endpoints;
- `circular_arc`: exact center/start radial vector/axis plus an exact rational fraction of one revolution, retaining the `2π` factor symbolically;
- `helical_arc`: the same exact rotational law plus exact axial progression on the fixed axis;
- `polyline`: finite ordered exact line composition;
- `spline`: finite non-rational B-spline with integer degree and exact rational knots/control points, evaluated from Cox–de Boor semantics without a knot epsilon;
- `piecewise_motion`: finite ordered composition preserving semantic boundaries;
- `timed_phase_motion`: exact finite time knots tied to exact path progress and spindle phase.

For threading and eccentric turning, time/path/spindle phase are one correlated law. Independent full-angle coverage is not an equivalent replacement. Phase may be geometrically equivalent modulo whole turns while unwrapped chronology remains semantically relevant to history and synchronization.

## Transform and numerical safety contract

Nominal source geometry and measurement/tool/machine uncertainty remain separate channels. Higher arithmetic precision may tighten the nominal computation; it does not make a measurement exact or erase a known nominal cut.

Authority paths reject dimension mismatch, nonfinite values, integer overflow/saturation, tolerance-as-predicate-sign, unqualified flush-to-zero and a dimensionally untyped global epsilon. Exact predicates do not imply exact constructions. Certified floating filters may accelerate decisions only when their fallback preserves the exact source semantics.

Derived geometry is not clamped to the input storage quantum. A valid sub-nanometre derived feature can arise from exact operations on coarser source values; the one-nanometre legacy input unit is not a topology or feature-size floor.

## Serialization and compatibility

Certifying quantities use exact integer/rational/symbolic tokens or directed interval endpoints with explicit dimensions. Ordinary JSON floating numbers cannot carry a claimed exact guarantee. Research JSON is only an inspectable carrier; canonical hashing requires a separately specified byte normalization rather than assuming pretty-printed JSON bytes are canonical.

Existing `msac-journal/1.0` documents are not migrated in place. Any richer source revision is new, declares `mc-exact-source/1.0`, records source identity and leaves the old revision intact. Unsupported readers fail closed. No migration may manufacture precision already lost in an old quantized source.

## Adversarial and boundary verification

`verify.py --contract` checks the contract against the live MC-002 constructor IDs and against both historical RCS-002 fixtures. It also runs negative controls that must reject:

- reinterpretation of saved v1 meaning;
- integer wrapping;
- fake recovery of lost sub-quantum information;
- binary-floating certifying quantities;
- a global untyped epsilon;
- omission of exact helical motion;
- epsilon-defined spline knots;
- phase decimalization or loss of phase correlation;
- treating the legacy quantum as a derived-feature floor;
- in-place migration;
- silently dropping inherited DD-002-04/DD-002-05;
- promoting this design contract to native geometry evidence.

The verifier also fail-closes if MC-002 changes its trajectory, lathe-kinematic or setup constructor sets without MC-003 being reconciled.

## Open questions and negative findings

`OQ-003-01` leaves the future production codec for arbitrary-precision rational/symbolic-turn values open. This does not block the semantic research contract.

`OQ-003-02` leaves coefficient bit-length, knot-count and event-count resource caps to MC-004 and scale qualification. Semantic finiteness does not imply practical bounded cost.

`DD-002-04` (compound live/driven tooling) and `DD-002-05` (simultaneous multi-spindle/transfer-machine semantics) remain open exactly as inherited from MC-002. Numeric work does not decide product scope.

No native arithmetic library, geometry kernel or paid runner was exercised. Consequently this task does not claim that a candidate implements the contract correctly or efficiently.

## Downstream implications

MC-004 may now preregister workload, accuracy and resource requests using this numeric contract and the MC-002 domain grammar. MC-005 must review MC-002–004 together before MC-A can change from `NOT_ESTABLISHED`.

MC-006/007 can consume exact rational/symbolic source semantics when constructing algebraic and phase-sensitive termination arguments. Later implementation/certificate tasks still owe actual arithmetic-library choices, exact/directed checker implementations and native evidence.

## Verification

Cheap deterministic verification:

```text
python3 research/machining-completeness/tasks/MC-003/verify.py --contract
python3 tools/mc_workflow.py verify MC-003
python3 tools/validate_machining_completeness.py
```

The repository `mc1-static` workflow is updated to invoke MC-003 after integration. No native or paid campaign is required by this task.
