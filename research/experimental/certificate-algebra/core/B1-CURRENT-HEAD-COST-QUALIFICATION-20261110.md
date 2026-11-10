# B1-D4 — exact-current-head qualification and measured Python reuse gate (10 November 2026)

**Decision:** PASS WITH LIMITED GRAMMAR for research-only B1; **HOLD** for current A1/A2 cross-producer receipt admission, authenticated B-spline/STEP ancestry, native net performance and merge. No production authorization.

## Reproduced exact-source suite

B1 #473 input HEAD `7dccd55504fe6f07d93a596de1dffebb85695197`, main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; GitHub compare 57 ahead / zero behind / all 35 paths in this research subtree. The 20 Python file SHA-1 Git blobs from the preceding B1-D3 execution archive matched the latest published tree unchanged. In a disposable CPython 3.13.5 directory with actual original imports:

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v  # 86/86 PASS, exit 0, 0.842 s
python3 experiment.py                                   # exit 0
python3 -m compileall -q .                              # exit 0
python3 bench_b1_reuse_20261110.py                      # A/B/B/A cost comparison
```

Existing tests include hostile custom Python equality, malformed/oversized/cyclic primitives, external source/identity/hash substitutions, split/affine invalidation and E1-E7 consumer refusal. These tests were **actually rerun**, not replaced by a new standalone oracle. Hosted workflow success is not cited as B1 unit-test execution.

## Current producer heads do not qualify through the existing B1 whitelist

As fetched live: A1 #470 = `c2f318215678951961f372866087e425a34e0609`; A2 #471 = `d9cb56e74e876efb203e04003aadcf8bd368a369`.

B1 `phase_bridge.PRODUCERS` continues to name older A1 `281705e947fd7812300d1d2605d3cdf60cdb005e` and A2 `3b6eaf70e1e7422b7ac8e8e9ff6f0fef85281978`. Direct `phase_bridge.canonical()` execution on **synthetic but otherwise grammar-valid** phase envelopes bearing each current producer head refuses with `unreviewed producer revision`. The old-whitelist controls admit the grammar; this does not authenticate either source. No current producer module, receipt, B-spline controls or knots were executed in this cycle, and no ancestry is inferred. A3 has independently documented unresolved *real A2 verifier* source/receipt substitution cases at its exact branch. **Do not whitelist the new heads simply to make a test pass.**

## Python-only same-host A/B/B/A

Published B1 `snapshot/verify_base/replace/events/_state` functions, 32 initially verified rational Bernstein-safe pieces, 64 deterministic local updates, identical final exact snapshot hashes and observed event sets for A (all 32 leaves reissued and reverified every edit) and B (one new leaf plus immediate seams). Two warmups, six A/B/B/A profiles, 12 timings per arm, standard CPython 3.13.5 host. Time includes Python proof/replay/receipt parsing, hashing and `events`; memory collected in a separate `tracemalloc` pass. Research **not native**.

| Metric | Full A | Incremental B |
|---|---:|---:|
| Full-leaf checks incl base | 2080 | 96 |
| Seam checks | 2015 | 155 |
| Median wall, 64 updates | 191.003 ms | 31.414 ms |
| Median per-arm p95 update | 3523.095 µs | 609.514 µs |
| Separate traced peak bytes | 322278 | 68126 |

A/B median ratio: **6.08x for this limited Python workload**. Source identity was preserved by explicitly carrying the mutation generation after each complete full replay; exact snapshot hashes matched. This does not include current producer verification, physical spline origin, native/STEP host integration or machine workload and **does not justify default native adoption**.

## Terminal bounded decision and next independent seam

The existing source-critical B1-D3 repair remains qualified as Python research only; no new algebra or consumer changes in D4. A3/B5 should independently execute a **genuine current A2** `cyclotomic_moments.source -> source_dict -> point_germ -> verify_receipt` with B1's real `a2_envelope/phase_bridge`, an independently held source+window pin and the known A2 hostile source-substitution fixture. Any authenticated current A1 admission similarly needs its reviewed producer code and original physical origin. Only after the upstream verifier is sound should B1 change the producer-head registry. Native/STEP consumer and net whole-operation savings remain unmeasured.

Preserve 121/20/30/50, 26 machining operations, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. No protected code, merge or gate change.
