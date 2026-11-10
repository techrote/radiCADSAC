# A1-QUAL-001 — Exact-current-head qualification and source-bound receipt repair

**10 November 2026 · Research-only Draft/HOLD.** Exclusive A1 source lease registered in [#324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6768133281). Parent PR #470 head `22f8751bf9e0fee45b6cac0f5fae16217e54fb80`; accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. All changes are isolated to `research/experimental/analytic-events/isolator/**`.

## Original falsifiers — RETAINED

The **entire original nine-module source suite** at the parent head was independently reconstructed from 19 Git-blob-matched source/checker/test files and executed with the actual imports on CPython 3.13.5: **91/92 PASS; one FAIL**. `test_algebraic_zero.test_other_cyclotomic_and_phase` expected `EXACT_ZERO` for `F(t)=-1+2 cos(pi/3)=0` when phase rate is zero. This is an **identity-zero continuum**, and the source producer correctly returned `IDENTICAL_ZERO_PIECE`. The repair changes only the stale assertion, not the producer.

The actual original F1 rational/quadratic, F6 projective H2, and F7 zero-capacity verifier calls accepted **13 of 13 tested false receipt substitutions** (seven F1 hostile/typed, four F6 hostile `str` subclass, two F7 bool/int aliases). These are implementation-level in-process Python receipt-authentication failures; they are not counterexamples to the bounded mathematical theorems. A3 separately demonstrated that F7's `certify` analyzed one mutable source state but hashed a later state: a deliberately traced mutation switched H0 right-span from nonzero to all-zero before `canonical_digest`, allowing an inconsistent zero-continuum receipt to be accepted by original `verify`. See [A3's exact-source finding](https://github.com/techrote/radiCADSAC/pull/470#issuecomment-6767199648).

## Correction and narrow invariant

`receipt_integrity.strict_equal(expected,offered)` checks exact built-in Python types recursively before invoking equality, with bounded tree depth (32), node count (8192), string length (65536), integer bit length (4096) and container size (4096). It rejects hostile equality subclasses, `True == 1`, `False == 0`, cyclic/deep trees, nested forged fields and extra/missing receipt fields. The A1 verifier call sites now compare their own recomputed receipts with this guard, including the full simple-promise certificate envelope. This is **local structural integrity**, not cryptographic attestation or authenticated physical provenance.

F7 `certify(source)` captures a **single, bounded built-in JSON primitive-tree snapshot** and uses only that owned snapshot for spline analysis, knot and SHA-256. This prevents the demonstrated intra-call analysis/hash TOCTOU split. The captured data is still supplied-only; external original-source custody, true atomic acquisition under concurrent writers, and rollback/lifetime attestation are **not** proven by copying. The exact attack requires a mutable Python source, not a static signed JSON document.

## Direct candidate execution and run commands

All nine original `test_*.py` modules, their real parent implementations, the newly added `test_receipt_integrity.py` and the actual source were locally executed on CPython 3.13.5, from tested bytes matching the candidate Git blobs: **97/97 PASS, no skips, exit 0**. Original F6 negative signed phase `b=-2` and projective-pole fixture emitted physically ascending `[-1/2,-1/4,0,1/4]` with four order-one CROSS events and alternating sided signs; exact source-adapted direct F6 challenges refused 4/4 hostile receipts; F1 refused 7/7 and F7 refused 2/2. New trace-based F7 regression executes actual `certify` and `verify` and refuses the source/hash topology substitution. Plain-source honest controls remain accepted.

```sh
# On the literal corrected head; run from repository root:
cd research/experimental/analytic-events/isolator
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 challenge_sympy.py  # Optional, SymPy 1.14; separate model oracle
```

The test suite above is the **real A1 candidate**, not an isolated rewritten mathematics example. The two direct challenge scripts used in the review are in the owner evidence archive; the committed regression exercises these original producer/verifier functions without shadowing them. Parent-source SHA assertions in historical adversary scripts must be repinned to the new literal head rather than ignored.

## Qualification and unresolved obligations

| Gate | Decision |
|---|---|
| Bounded F1–F7 research mathematics | Existing **conditional** results retained; no new theorem or broad decidability |
| Original pre-repair complete suite | **91/92**, one stale-assertion failure retained |
| Corrected complete current suite | **97/97 local PASS**, exact candidate bytes; require second-source A3 |
| Original direct receipt/TOCTOU challenges | Falsified original implementations; candidate regressions **PASS** |
| Independent A3 on new exact head | **PENDING**, request all 13 forgeries + TOCTOU and physical ordering |
| Original physical B-spline ancestry | **UNVERIFIED**, supplied constructed C0 spline only |
| General arbitrary B-spline knots and transcendental event isolation | **NOT_ESTABLISHED** |
| MC-B / MC-1 | **NOT_ESTABLISHED**, `production_authorized=false` |

The proof is not promoted to MC-038 acceptance. The frozen original census remains **121/20/30/50**, 26 operations untouched, no native/paid work, no production, source registry or authority changes. **Draft/HOLD** pending independent review and source custody.
