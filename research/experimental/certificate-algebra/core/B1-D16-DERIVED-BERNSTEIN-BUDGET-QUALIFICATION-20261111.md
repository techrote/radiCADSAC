# B1-D16 — Derived Bernstein output-budget qualification

**Date:** 11 November 2026. **Classification:** deterministic Python research, not native geometry or STEP. **Disposition:** GO for repaired bounded B1 certificate algebra; HOLD for authenticated A1/A2/physical admission, native economics, second-source acceptance and merge.

## Source and ownership

- Accepted main/base: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Existing Draft [#473](https://github.com/techrote/radiCADSAC/pull/473); no merge.
- Prepatch B1 exact head: `0b99adbda5c8b2cb7104944302ab31a98b038571`. All **25/25 Python source/test/benchmark Git blob IDs** were independently fetched and matched to the locally executed prior evidence archive. Prepatch B1 suite: **100/100 PASS**, with the new regression not yet installed.
- Source patch Git blob: `1f257d29dc4d1faa85beb7af867594a391014d42`; test patch Git blob: `1c00541bd0f4f3b80def25581f29bac445c78dff`. Both independently read back and matched their locally tested files at exact Draft head `aad9c42681625547cc48b77f908ab0a50f107bf2` before adding this report.
- Changed code/testing is only `research/experimental/certificate-algebra/core/certificate_algebra.py` and `test_certificate_algebra.py`; report is in the same B1-owned subtree. No other worker branch or frozen authority edited.

## Real parent-consumer falsifier

B1's input contract bounds each rational coefficient to **1024 numerator/denominator bits**, but `bernstein(p)` formerly accepted derived Bernstein fractions without the same *output* limit. On Python 3.13, `Certificate.record()` could consequently raise an uncaught `ValueError` when decimal-string rendering exceeded Python's 4300-digit safeguard, despite every source coefficient being individually valid.

Deterministic adversary: degree 24 on `[0,1]`; take the first 25 distinct primes `p_i=2,3,5,...,97`, and define `a_i=1/p_i^{floor(1023 / bit_length(p_i))}`. Every coefficient is exact, positive, and its denominator is at most 1011 bits in this concrete instance. The final degree-24 Bernstein coefficient is `b_24=sum(a_i)`. The denominators are pairwise coprime, so no denominator factor cancels, and `b_24` has a **22614-bit denominator**. This is a positive polynomial, not a disputed zero certificate; it exposes a resource-boundary error in the *proof representation*.

Before patch:
- `prove(Piece(...), EvidenceMeter())` returned `POS` with a 22614-bit proof scalar.
- `base_record((source,))` raised **uncaught ValueError** at the actual Certificate-record serialization boundary.
- The original complete **100/100 tests passed**; the added regression failed on original code (expected typed `Refusal` was not raised).

## Repair and executable qualification

- `bernstein()` now checks each *derived* numerator/denominator before returning an output certificate. Exceeding the 1024-bit output policy is a typed **Refusal**, never a sign or zero/nonzero verdict.
- `Certificate.__post_init__()` enforces nonempty bounded built-in `Fraction` tuples on all certificate construction routes, including split/affine and imported public dataclass values. This protects output serialization even when certificates are constructed outside `prove()`. Mathematical laws are unchanged on admitted states.
- The new **actual parent module regression** checks `prove()`, `base_record()`, direct oversized `Certificate`, and a valid small exact positive control.
- Full corrected `python3 -m unittest discover -v -p 'test*.py'` **101/101 PASS** (CPython 3.13.5), all parent/E1–E7/hostile equality/deep source/hash/split/affine/512-piece refusal tests included. `python3 -m compileall -q .` PASS and `python3 experiment.py` PASS. Prepatch targeted regression FAIL and previous **100/100** PASS retained as separate logs.

## External A1/A2 and physical-source identity

Reexecuted original A1 #470 at exact head `fe0dada7c430053c4c387f17a062909da9aab8bc`, byte-identical to published producer blobs `algebraic_zero.py=5a8e52898725aa10b427de4e5736cb1cf5578d68` and `receipt_integrity.py=77f0ba7700002b7a376dfcc2c29b820ea4def485`. Real `source→source_sha→rational_event→verify_rational_event` confirmed `-1+sin(pi*t)` zero at `1/2`, nonzero at `0`, and refused modified source/receipt. Actual B1 producer codec passed under explicitly **research-supplied** source/window pins, self-stamped *historical* A1 `281705e9...`, and correctly refused explicitly declared current A1 head. This **does not** import the A1 event as an operational B1 certificate.

A2 #471 current head `d9cb56e74e876efb203e04003aadcf8bd368a369` was read but its actual producer functions were **NOT executed** in this cycle. Independent A2 source-identity/receipt validation is still missing. B-spline original control vectors, knot/window source provenance, upstream Git identity/pin custody, native STEP consumer binding and source lifetime/ABA tracking remain **UNVERIFIED**. Do not reinterpret supplied hashes as independent custody.

## Fair Python recomputation economics

Reexecuted existing five-arm 32-piece/64-edit, five-symmetric-repeat Python benchmark. Intermediate snapshot hashes all matched. Median milliseconds: trusted incremental `32.026` vs one-pass fresh full reproof `83.350` (**2.60×**). Incremental plus strict per-edit readmission `158.701` vs equally readmitted one-pass full `212.204` (**1.34×**). Includes neither end-to-end E5 nor source-provider authentication, original physical lineage checks, STEP, nor native kernel/solver recomputation. The modest strict Python advantage **does not justify production/native integration** absent an independently qualified real-consumer A/B measurement.

## Decision, independent challenge, retained holds

**GO:** only source-pinned corrected 101-test Python proof implementation and its restricted infinite-family rational/Bernstein closure laws within declared output budgets.

**HOLD:** A2 actual producer receipt and forged-source challenge, independently held current-head A1/A2 provenance, physical B-spline lineage, second-source A3/B5 test execution, native/STEP relevance/cost-benefit, review and merge. **NO-GO:** treating Python benchmark or old-head adapter stamp as native authorization or source ancestry.

The 121/20/30/50 historical census, 26 supported machining operations, MC-B and MC-1 `NOT_ESTABLISHED`, and `production_authorized=false` are untouched. No paid/native campaigns, production bootstrap, protected documents or cross-lane edits.
