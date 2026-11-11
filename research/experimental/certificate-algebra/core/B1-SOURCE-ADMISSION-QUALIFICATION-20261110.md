# B1 source-admission equality falsifier — current-head qualification, 10 November 2026

**Disposition:** scoped B1 Python research **PASS with limited grammar** after the source boundary repair; cross-producer authenticity, A2 receipt, actual B-spline ancestry, native use, and merger remain **HOLD**. A1's independently reported original false receipt verifier issue remains **CHANGES REQUIRED** in its own lane. No production or MC authority claim.

## Source identity and actual execution

- Repository: `techrote/radiCADSAC`; accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.
- Original research B1 branch head before this correction: `a76afe6a5b9f46456ecfadaa3acbbaf4cd76a50a`.
- Actual unmodified published `phase_bridge.py` Git blob: `47fe8783c5e7a173cbb2a9c1288148339617d290`.
- Repaired `phase_bridge.py` Git blob: `155c21003234836a85d0e2ab69cc04474cbcf086`.
- Repaired full published `test_phase_bridge.py` Git blob: `3dfa773ba9d3db58957ac3db140aa6e9660bdc78`.
- The earlier **20/20 complete B1 Python modules** are preserved from the previous source-pinned 83-test qualification; the two changed modules were checked against these exact new Git blobs. CPython 3.13.5 local disposable execution of all ten *original* `test_*.py` modules with original imports: **84/84 PASS**, 0.831 seconds, exit 0. `python3 -m compileall -q .` exit 0. `python3 experiment.py` exit 0.
- Direct pre/post challenge against actual `phase_bridge.canonical`, `prove_equivalent`, and `verify`: **four forged source-schema/head/offset/rate inputs ACCEPTED by the original verifier**, with matching caller-supplied SHA-256 envelope pins. Exact same four **REFUSED by the corrected verifier**; honest phase-normalized controls still verified. The source objects themselves were hostile Python `str` subclasses (`__eq__` always True, `__ne__` always False), not serialized plain JSON. No original A1/A2 producer signed these malformed records.
- Regression additionally rejects hostile identity subclass, nested rational and dictionary-key subclass, with ordinary source positive controls.

## Minimal falsifier and precise repair

Original `canonical` checked the claimed `schema` and `producer_head` using Python equality on untrusted subclass values. `exact` used `isinstance(x,str)` and later `str(Fraction(x)) != x`; a hostile `__ne__` also admitted noncanonical `1/1`. Consequently `verify` could return `True` for an unreviewed producer head when the submitted envelope hash pin matched the malformed raw JSON value. That is **source grammar/authentication of the claimed producer version**, not evidence that the normalized mathematical function was wrong; a trusted authentic previously recorded pin would not be forged by this example.

Repair only at B1 source admission: `canonical` invokes the existing bounded `receipt_integrity.validate` *before any reads, equality, membership or JSON hashing*; nonprimitive/deep/oversized input is converted to a typed B1 `Refusal`. `exact` now requires the builtin `str` type. The existing builtin-only certificate-receipt validator remains authoritative; no new standalone authentication policy or handwritten equality engine.

Reproduce from detached B1 branch within `research/experimental/certificate-algebra/core`:

```sh
git hash-object phase_bridge.py test_phase_bridge.py
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 experiment.py
python3 -m compileall -q .
```

The accompanying disposable evidence script `source_boundary_direct_negative.py` loads the original literal Git blob and repaired literal Git blob separately and calls the **actual original/current B1 verifiers**, not an imitation predicate. Expected result: original admits all four false-source fields, revised refuses all four, canonical legitimate source passes in both.

## External producer and consumer relevance

Earlier same-day execution directly instantiated genuine A1 `Source`, `rational_event`, `verify_rational_event` at A1 #470 `22f8751bf9e0fee45b6cac0f5fae16217e54fb80` (`algebraic_zero.py` Git blob `daeb0b4ff0325c246bbf0f5737daf359400b7c3d`). The B1 `producer_codec.a1_envelope` accepted its *authentic complete source serialization* with a caller-controlled physical window; a changed complete source under the old trusted pin refused. That demonstrates one real A1 producer/codec boundary, but **NOT** authenticated B-spline controls/knots, provenance for the physical window, or current A1 verifier trust: its hostile `EXACT_NONZERO` equality attack is separately recorded on A1 #470.

The B1 `PRODUCERS` table still references historical A1/A2 implementation identities. Actual **current-head A2 receipt** has not been executed through a B1 consumer; merely importing an A2 shape or inventing a matching hash is not qualification. Producer/phase normalization is not currently a demonstrated native STEP or CyberSand consumer path. A1/A2 source identity and knot/time conversion must be grounded independently, especially negative affine orientation, sided knot germs and changes to controls/knots.

The deterministic `experiment.py` retains 2,080 naïve vs 96 incremental leaf proof rechecks and 2,015 vs 155 seam checks, with the same reconstructed source/events. These are *counts*, not runtime savings. Recursively validating the source and recomputing producer-derived proof obligations incurs work not counted by that ratio. There is **no measured net native/STEP saving**, and no reason to enable a hot-path proof checker.

**B5/A3 independent request:** execute all ten published B1 test modules at the exact updated PR head with the real B1 parent; separately replay the original-vs-corrected source-head subclass falsifier. Challenge an actual A1/A2 producer receipt with independently established source ancestry, phase rate and knot ownership, and report cost of trusted pins/checks versus actual recomputation. A3 must not take B1's Python proof as authorization of the currently defective A1 verifier.

Original 121/20/30/50 census, 26 machining operations and negative records unchanged. MC-B/MC-1 `NOT_ESTABLISHED`; `production_authorized=false`. No Ready/merge/production/native changes.