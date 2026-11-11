# B1-D14 — E5 derived-rational overflow and bounded refusal qualification (11 November 2026)

Status: **bounded Python research GO after correction; cross-producer/native/merge HOLD**. Draft PR #473; audited parent head `a81a7285c54e68645ad48ff2a3e62f8f907e7e7c`, accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. This report is a deterministic Python model finding, not independent MC-B/MC-1 authorization.

## Hypothesis and falsifier

Hypothesis: B1's primitive/parent 1024-bit rational admissions imply every E5 sided-germ result or signed-affine projection stays inside B1's rational output budget. **Falsified.** Exact derivatives rescale by source-cell width to powers of 24; independently admitted affine rates can also amplify order-24 leading coefficients. Both are unbounded by admission alone.

1. **Real E4→E5 derivative consumer:** One source cell `[0,1/2^1023]`, numerator `N(u)=u^24` and denominator `D=1`. Both B1 parent receipts and E4 quotient replay are valid. `quotient_sided_germ.derive(...,time="0")` attempts to serialize physical order-24 leading coefficient `2^(1023*24)` and raises raw CPython `ValueError: Exceeds the limit (4300 digits) for integer string conversion`, rather than B1 `Refusal`.
2. **Real E5 signed-affine prediction consumer:** On `[0,1]`, numerator `N(u)=u^24/2^1023`, denominator `D=1`. E4 and E5 produce a genuine valid bounded germ. The separately valid input `rate=2^1023`, `offset=0` makes the projected leading coefficient `2^(1023*23)`, again raising raw CPython `ValueError` before any result/certificate admission.

These are controlled **over-budget refusals**, not claims the exact underlying mathematics is incorrect; no sign or event truth may be inferred from failure.

## Actual consumer-boundary repair

At `quotient_sided_germ.py`, apply `_enc_bounded` to every *newly derived* rational exposed in E5 or its unbound signed-affine projection: local leading coefficient, transformed leading coefficient and transformed event time. Check numerator/denominator bit lengths **before** `str(Fraction)`; values exceeding `MAX_BITS=1024` produce typed `Refusal`. No admission grammar, source hash, parent verifier, A1/A2 allowlist or external trust policy changes.

## Execution and exact evidence

- Audited literal predecessor PR #473 head `a81a7285c54e68645ad48ff2a3e62f8f907e7e7c`; verified 25/25 bundled Python files against the source/run manifest, and checked the complete repository B1 directory's published Git blob SHA listing. Independent GitHub directory reads identify original E5 blob `8671f5981cf679c639eab204fb458f7228f6fe8d`, original E5 test blob `94e5a934bff597c4fec0d0ac85cc6aafe0e705c8`.
- **Before change:** complete suite 96/96 PASS, but the two newly added real consumer tests **ERROR (raw ValueError)** against original E5 implementation. Full original suite is therefore insufficient to claim bounded refusal.
- **After correction:** `python3 -m unittest discover -v -p 'test*.py'` **98/98 PASS**, including hostile custom equality, deep nested input, source/hash/identity substitutions, split/affine invalidation, 512→513 piece budget, E4 and E5 tests. `python3 -m compileall -q .` PASS; `python3 experiment.py` PASS.
- Fair five-arm CPython 3.13 model benchmark: 32 pieces, 64 edits, five symmetric repetitions, two warmups. Incremental 30.34 ms; efficient one-pass full 79.27 ms (**2.61×**). Incremental plus complete every-edit readmission 151.07 ms; one-pass full plus equivalent readmission 203.43 ms (**1.35×**). Every intermediate hash matches. The benchmark does **not** exercise E5 derivative/affine over-budget cases, producer authentication, physical spline source lineage, native geometric reconstruction or STEP consumers. It cannot establish native ROI.

## Source-critical HOLD and next qualified dependency

The earlier genuine A1 #470 event verified at source head `fe0dada7c430053c4c387f17a062909da9aab8bc` is a *producer-local* check, not cross-head B1 admission. B1 still hard-pins older A1/A2 heads; current A1/A2 receipt admission is **HOLD**. Physical original B-spline controls, knot window and producer-code provenance remain unverified. Direct latest A2 producer receipt was **not executed** here; A2's independent source-identity finding still blocks admission. A3/B5 should re-execute the genuine A2 receipt, challenge this E5 output bound and independently validate consumer source lineage. The verified Python cost advantage is not a native savings claim; consumer proof reuse and completeness of invalidation dependencies must first be demonstrated on a real native/STEP workload.

Keep 121/20/30/50 frozen historical census; 26 machining operations; MC-B/MC-1 `NOT_ESTABLISHED`; `production_authorized=false`. No cross-lane writes, production bootstrap, native campaign, merge or gate promotions.
