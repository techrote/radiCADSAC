# A1-QUAL-009 — square-lift source/digest custody (10 Nov 2026)

**Scope:** one implementation-level certificate-custody correction in the experimental A1 finite H2 square-lift family. Research only; no new theorem, no native code, no production authority. A1 owns only `research/experimental/analytic-events/isolator/**`; lease [#324/6779249137](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6779249137). Existing Draft [#470](https://github.com/techrote/radiCADSAC/pull/470) remains HOLD, not for merge.

## Preregistered original-parent falsifier

At exact pre-edit head `85d49d45ee955d5cbb965cbe360c3f69355156a9`, `square_lift.issue(s)` first copied `k=s.k` but subsequently obtained `source_sha256` from caller-owned mutable-in-practice `Spec`. Python's `@dataclass(frozen=True)` does not prevent `object.__setattr__`. A deterministic trace at the **actual** `source_hash` call replaced `k=4` by `k=5` after the interval was derived. The genuine published producer issued `interval=['4','5']` with the canonical k=5 source SHA-256. The genuine published `verify(s,receipt)` returned **True under the same interleaving**; either static k4 or static k5 verification refused. Original negative script `F5_original_probe.py` exit **1**, `AssertionError: F5 ORIGINAL SOURCE/DIGEST FALSE RECEIPT ACCEPTED`. No artificial replacement oracle was used.

## Corrective invariant and admitted grammar

`issue()` now constructs one private, validated `Spec` before any classification, interval, knot or digest generation. Exact built-in tuple lengths (at most four rationals), exact built-in `Fraction` coefficients, integer k range [3,10000], 128-bit rational budget, C0 seam and existing sufficient Bernstein positivity checks are preserved. Rational fields are reconstructed into fresh Fraction objects, and `Spec` is validated afresh. Classification, entire receipt and hash all consume this captured representation. Nonadmitted values refuse; no forced conversion of generators or user-defined containers. This is one bounded ownership snapshot, not an atomic synchronization promise against arbitrary changes *during* field capture or attacks inside interpreter internals.

## Qualification requirements / outcome

- Full source-inclusive suite at pre-edit head: **108/108 PASS**; independent pre-fix adversarial check **FAIL** as expected.
- Full suite on corrected candidate before publication: **109/109 PASS** (real imported originals, CPython 3.13.5), one additional source-custody regression.
- Direct F6 negative phase / projective pole / order-1 physical roots / strict signs: PASS, actual original parent.
- F1 forged rational/quadratic receipts and F7 hostile int/bool receipts: REFUSED; F4/F6/F7 deterministic mutation replays: PASS; simple-promise grid-pivot collision: typed refusal.
- SymPy 1.14 optional symbolic controls: PASS.
- **Independent A3 on this new exact commit: PENDING**; authenticated original B-spline source ancestry: **UNVERIFIED**; global H0/H1/H2 arbitrary-knot/transcendental partition: **NOT_ESTABLISHED**.

Post-publication receipt must additionally include complete 22-Python-file exact Git-blob readback, the complete 109-test rerun from those exact bytes, fresh adversarial controls and A3 independent review request. If absent, report NOT EXECUTED rather than PASS.

## Limits and provenance

The pre-existing square-lift mathematical identity, transcendental double-touch root family and strict positivity remain conditional on the finite admitted source grammar; neither this correction nor the tests authenticate a physical B-spline knot/control chain. No new general decidability claim, MC-038/MC-B/MC-1 promotion, manufacturing operation coverage change, source-census revision or production release. Preserved: original 121/20/30/50 historical census, 26 machining operations, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`.

Run from the isolated published source directory:

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 challenge_sympy.py
PYTHONPATH=. python3 /path/to/F5_original_probe.py   # EXPECT EXIT 1 on pre-fix only
```

## Completion addendum — bounded denominator/numerator ingress

After initial exact source-snapshot success (109/109), post-publication hardening adds a bit-length preflight on the captured rational numerator and denominator **before** reconstructing the independent Fraction. This prevents performing an unbounded denominator GCD on a forged, oversized Fraction object. New original-parent regression mutates a frozen Spec to carry an oversized (200,000-bit numerator) Fraction and requires typed budget refusal and no certificate acceptance. Corrected complete source-inclusive suite **110/110 PASS** (CPython 3.13.5), with full A3-style direct controls and SymPy rerun; final exact Git readback and independent review remain separate gates.
