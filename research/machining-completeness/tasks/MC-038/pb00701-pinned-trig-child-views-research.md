# MC-038 / PB-007-01 — pinned original-source trigonometric ordered-child views

**Date:** 29 October 2026. **Owner:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Baseline:** `9d42dbdec90b37ee875208e966e7270aec50dfc3` (#293). **Evidence class:** deterministic-model, limited original-source mathematics; no native geometry qualification.

## Exact scope and contrast with the existing subset checker

The [conditional rational-polynomial core](pb00701-checked-child-composition-core-research.md) in PR #293 derives complete ordered roots only when full rational-linear factorization of each *original global-source polynomial* is verified. Its refusal of trigonometric/affine-phase sources is deliberate. This research does **not** relax that validator, forge rational factors for trigonometric roots, or turn owner/count-only results into certificates.

Instead, the new Python checker reconciles *exactly three frozen original-source cases* with the existing source-specific ordered-root proofs: V27 `tail0`, V27 `tail100` from [PR #291](https://github.com/techrote/radiCADSAC/pull/291), and harvested V41/V13 from [PR #292](https://github.com/techrote/radiCADSAC/pull/292). It replays both exact-source proof drivers and the frozen corpus/authority gates before constructing any view. It then requires a submitted child view to equal the independently regenerated original-source witness; a caller-supplied root count, status, phase, source digest, proof family or event is never accepted on its own.

## Frozen custody, proof dependencies and falsification

- Frozen 121-case v54 corpus Git blob `5841c331579489b25caef38cd412bdbf286f9134`; MC-002 26-operation domain blob `23de82f5240a72509f7afe4acd5948b65bc4ff13`; current authority blob `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.
- Pinned prior proof-driver blobs: V27 `006272b173a66bfb53cc4ddf0f5597857a42362b` and V41/V13 `358dd4071ef968635bcd85f61dfa1965e51abda1`. Both import the pinned degree-0/1 original B-spline lowerer, verify source spline controls, phase, knots, producer and historical owner/disposition, and leave original `BLOCKED` results untouched.
- If *any* blob, original B-spline/phase/provenance, proof result, view field, source owner, ordered strict bracket, root simplicity/parity, one-sided sign or true-knot sign changes, validation fails closed. Unsupported source grammar returns typed `BLOCKED` nontruth; an oversized payload returns typed `RESOURCE_REFUSAL` nontruth. No fallback treats a failed or timed-out proof as success.

## Exact physical semantics of the bounded result

All view positions are in the **original source-time-t parameter**, not a local child interval or an invented trigonometric coordinate. An `IMPLICIT_ROOT_n` denotes the *unique simple zero of the pinned original physical function within the stated strict rational bracket*, not a rational/algebraic closed form and not a sample coordinate. In each source-specific proof, opposite strict signs plus nonzero derivative/strict monotonicity on the isolating interval establish root existence, uniqueness, crossing parity and smooth multiplicity one. The root bracket endpoints are **not** asserted to be roots.

| Frozen source | Physical child spans and original owner | Strict original-source root brackets | Physical sign cells |
|---|---|---|---|
| V27 tail0 | [0,1] V27; [1,2] V27 | (3/4,1), (9/8,3/2) | +, −, + |
| V27 tail100 | [0,1] V27; [1,2] V19 | (3/4,1), (1,9/8) | +, −, + |
| V41 harvested V13 | [0,1] V41 | (3/20,1/5), (4/5,17/20) | −, +, − |

The V27 original source knot at `s=1` is continuously **negative**. No physical zero exists at that knot, and no cross-knot smooth multiplicity is invented. Source/sector cuts (for example `3/4`, `1`, `9/8`) are **proof cuts**, not independent physical events. The two nonoverlapping root uniqueness brackets establish strict ordering even where an endpoint of a bracket coincides with a source knot. Three maximal open sign cells are reported with symbolic root references as boundaries, not with fictitious numerical root coordinates.

V27's prior proof is an explicit exact *analytic sector argument* coupled to source/lowering/inequality assertions; it is **not** a general mechanically certified trigonometric root isolator. V41's prior proof additionally uses rational Machin bounds and Taylor/Lagrange continuous interval enclosures. This interface replays those bounded proofs but does not claim to improve their mathematical scope or validate arbitrary trigonometric child certificates.

## Interface and adversarial verification

The checker is `pb00701_pinned_trig_child_views.py`; test entry point is `verify_pb00701_pinned_trig_child_views.py`. Source submissions are strict JSON-compatible dictionaries with schema `radicadsac-pb00701-pinned-trig-child-views/1.0`, a pinned case/source binding, proof-family identity, complete original-source child spans, owner IDs, unique-zero brackets, one-sided signs, source-knot identities and non-physical proof cuts. Unknown/extra fields, count-only statuses, forged exact coordinates, wrong multiplicities, missing/duplicate roots, reversals, mismatched span ownership, phase/source swaps and false source-knot events fail closed.

Reproduce on the exact repository source revision:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_pinned_trig_child_views.py --contract --self-test
```

CI executes this command at the literal PR head and after merge. The independent earlier V27/V41 source-specific verifiers are not weakened. No arbitrary caller can inject a replacement proof report into the public composition entry point.

## Explicit nonclaims, unresolved obligation and relevance

This is a **fixed-case, original-source-bound consumption/reconciliation example**, not the missing general V27/V41 checked nested-child theorem. In particular it does not accept historical V27/V41 count-only child views as complete evidence, support general implicit/algebraic root comparisons, identity-zero intervals, arbitrary tangencies or knots with zero, resource-unbounded input, or establish end-to-end V43 composition. The frozen V54 outcomes remain unchanged. No PB-007-01, MC-B, MC-1, native material, B-rep, or conventional usable engineering STEP route is certified. Production remains unauthorized.

The next valid proof frontier is a source/provenance-preserving **general completeness/ordering interface** capable of reconstructing and independently verifying each trigonometric child root witness, multiplicity and one-sided sign across arbitrary finite original-source cuts and true knots, with typed nontruth refusal. One set of three pinned examples cannot establish that universal obligation. The entire 26-operation lathe/mill domain, canonical manufacturing journal, positive material, multiple bodies, lineage and `UNCERTIFIED` obligations remain in force.
