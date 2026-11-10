# B1-D7 — actual current A1 producer receipt versus B1 source bridge (10 November 2026)

**Evidence class:** direct source-identified CPython research execution. **Decision:** GO only for the declared current-A1 rational-event producer/verifier case and B1's existing limited source-serialization checks; **HOLD** current-A1 *cross-producer authority*, actual current-A2 receipt, physical B-spline source/interval/knot/control ancestry, independent review, native/STEP economics and merge. This is not a new theorem or an MC-B/MC-1 acceptance shortcut.

## Exact provenance, source boundaries and executable artifact

- Accepted `main`: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.
- Input B1 Draft #473: `3f161281f0dacd43fe50adb19e7c0c2d73567af7`; A1 Draft #470: `098517a70e63cb8d5b8bab01b34118fa8439c942`; A2 Draft #471: `d9cb56e74e876efb203e04003aadcf8bd368a369`.
- Complete unchanged B1 source/tests from the exact B1 Git tree: **22/22 published Python blobs matched**, including all 10 parent modules, 10 test modules and two benchmarks. Actual `python3 -m unittest discover -s . -p 'test_*.py' -v`: **87/87 PASS**, exit 0, CPython 3.13.5. `python3 experiment.py` and `python3 -m compileall -q .`: exit 0. No stubs.
- Independently reconstructed *current actual A1* `algebraic_zero.py` (Git blob `3c48045a218018c8c3134a1224011c7acc2307b1`) from its older exact source plus the published verified change, and imported current exact A1 `receipt_integrity.py` (blob `77f0ba7700002b7a376dfcc2c29b820ea4def485`). Both byte-for-byte match the **current A1 GitHub tree**. B1 `phase_bridge.py` `dbcb2049d7e3de09f6430e632bee21ce836a1809`, `producer_codec.py` `563c445c314309a6198395addbecb59b464182a0`.
- B1 opt-in cross-branch, blob-refusing executable: [`probe_current_a1_receipt_20261110.py`](probe_current_a1_receipt_20261110.py), published blob `1f5c7a69117b6e8b1321b2cc404af585ee256aae`, directly executed **PASS**, exit 0. Not an extra `test_*.py` method or a native integration step.

Reproduce from two **read-only, exact detached** checkouts: B1 #473 on its exact published head and A1 #470 at the SHA above. From B1 `research/experimental/certificate-algebra/core`, run `python3 -m unittest discover -s . -p 'test_*.py' -v`, then `python3 probe_current_a1_receipt_20261110.py --a1-dir /path/to/A1/research/experimental/analytic-events/isolator`. The probe refuses any changed A1 or B1 critical blob; preserve all raw exit codes and output.

## Actual producer execution and falsifiers

Directly ran the **real current A1 Source -> source_sha -> rational_event -> verify_rational_event** implementation on `F(t)=-1+sin(pi*t)`:

- At `t=1/2`: actual producer `EXACT_ZERO`, genuine event `a1-rational-event/1` verified; source SHA-256 `b4ee6d2ee589e440772f32c4250040fd037ef74617bd1e80c7a819df1c29592b`.
- At `t=0`: `EXACT_NONZERO`; forged result `EXACT_NONZERO` at `1/2` rejected.
- Substituting source `-1+2sin(pi*t)` under the old receipt rejected by actual A1 verifier.
- Actual current A1 `Source` JSON passed B1 `a1_envelope()` with a **research-supplied** externally calculated source SHA and `[0,1]` window pin; a changed sine coefficient with the same pins was refused by the actual B1 adapter.
- The B1 source adapter **assigns the historical allowlisted producer head** `281705e947fd7812300d1d2605d3cdf60cdb005e` itself. This is **not attestation of the origin code revision**. Replacing that field with the genuine *current A1 head* caused B1 `canonical()` to correctly refuse `unreviewed producer revision`. Even the successful historical-tagged self-equivalence receipt is `MODEL_ONLY`, not a verified import of the actual A1 event receipt or authentic physical provenance.

**Interpretation:** This closes the previously unexecuted **current A1 producer rational-receipt** gap for a single bounded example. It **does not** close the producer-head/physical-window provenance gap, and does not establish that current A1 is admitted as a trusted B1 consumer. The unsigned hash proves only equality with the supplied bytes, not who issued them. Current A2's A3-adversarial source-verifier problem is outside B1's ownership; do not change its sources or silently add its revision.

## Recalibrated recomputation economics

Direct exact published `bench_b1_fair_boundary_20261110.py`, same CPython 3.13.5, 32 rational pieces, 64 local edits, 2 warmups, five symmetric A/B/B/A cycles per arm, all intermediate state hashes equal. Medians:

| Path | Milliseconds |
| --- | ---: |
| A naive full (3x Bernstein work per leaf) | 199.303 |
| D efficient one-pass full reproof | 87.025 |
| B trusted incremental | 34.824 |
| C incremental + complete every-edit external revalidation | 175.659 |
| E one-pass full reproof + same external revalidation | 246.913 |

D/B = **2.50x**, E/C = **1.41x** in this *bounded Python model only*; verifier overhead materially narrows the value. No actual machining/native B-rep/STEP consumer, physical source provenance, cost of native hashes/locks or native timing was executed. **HOLD** on production ROI, not a general speedup or MC-038 advance.

## Independent falsification and disposition

**A3:** independently run the exact current A1 Source and its verifier + this B1 probe, then attack any implied physical window/control/knot provenance; separately reproduce/fix the actual A2 `sparse_phase_germ` source substitution at #471 before any A2 admission. **B5:** independently execute published B1 87-test suite, source-matched cross-branch probe and fair 5-arm benchmark; challenge source-head spoofing by B1's self-assigned old provenance, external pin custody and verifier cost. B1 remains **Draft/HOLD**, do not merge or mark Ready.

Preserve the historical original 121 / refusals 20 / missing premises 30 / complete witnesses 50, 26 machining operations, `MC-B=NOT_ESTABLISHED`, `MC-1=NOT_ESTABLISHED` and `production_authorized=false`. No production/native or other lane source modified. No additional algebra was designed this cycle.
