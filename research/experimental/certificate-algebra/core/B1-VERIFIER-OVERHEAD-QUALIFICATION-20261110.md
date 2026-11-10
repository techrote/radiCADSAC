# B1-D5 — fair recomputation and strict-receipt boundary qualification (10 Nov 2026)

**Status:** Research Python PASS for tested grammar; **HOLD** for current A1/A2 producer authentication, physical spline ancestry, native/STEP consumer savings, independent admission and merge. This is a **cost-accounting correction**, not a new algebraic law, native optimisation, or MC-038 acceptance.

## Exact source and scope

- Accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.
- B1 input Draft #473 head: `a50aea8d7289a11304d56086bbf22efe208833ca` (all 20 original parent/test Python blobs identical to that head's Git tree, verified by `git hash-object`).
- New research-only apparatus: `bench_b1_fair_boundary_20261110.py`, committed blob `760363d13c8088d7d112ecc2771550d9316c4538`. No original B1 implementation/test or protected source changed.
- CPython 3.13.5, Linux x86_64, 32 positive rational pieces, 64 deterministic local edits, two warmups, five symmetric `ADBCEECBDA` trials. Same host/process; garbage-collect between trials. No hardware cycle/perf counters.
- Direct published suite FIRST: `python3 -m unittest discover -s . -p 'test_*.py' -v` -> **86/86 PASS**, exit 0, original parent imports; `experiment.py`, published `bench_b1_reuse_20261110.py` and Python compilation -> exit 0. Both hostile-key/primitive-budget and split/affine test modules included.

## Decisive cost-accounting distinction

Published `experiment.snapshot()` constructs a receipt using **two** `bernstein(p)` calls for every unchanged piece and subsequently invokes `verify_base()`, which recomputes it **a third time**. The original 2,080 vs 96 `full_leaf_checks` counts only the verification-path invocation; it omits the other two mathematical conversions in the naive arm. Therefore its ~6x wall-clock comparison is a useful *published-code baseline*, but **not a fair one-pass full recomputation comparator**.

A new independent five-arm test compares identical source edits and the **entire 64-step exact B1 snapshot hash trace**, not merely the final hash:

| Arm | Exact operation | Full-leaf checks (meter) | Median complete-workload wall time |
|---|---|---:|---:|
| A | Published snapshot: duplicated certificate construction plus full readmission | 2,080 | 186.704 ms |
| D | Efficient one-pass full reproof, no external readmission | 2,080 | 82.897 ms |
| B | In-process trusted C2 incremental reuse | 96 | 31.021 ms |
| C | Incremental reuse plus full **strict** primitive/leaf/seam readmission at **every edit** | 2,144 | 158.489 ms |
| E | One-pass full reproof plus same strict readmission at every edit | 4,128 | 211.329 ms |

- A/B = **6.02x**, but A/D = **2.25x** shows the original naive reference's redundant construction cost.
- D/B = **2.67x** for fairer trusted, uninterrupted in-process recomputation.
- E/C = **1.33x** for the deliberately *strict every-edit external consumer* comparison; C/D = **1.91x**, i.e. verification dominates over unverified one-pass full recomputation in that different trust regime.
- All 50 measured arm executions agreed on **each intermediate snapshot hash and every modeled zero-set event**; SHA-256 of ordered 64-hash traces: `1b33b99efaaffd86fc2da9a5d55b6fbb3589712ee5d04ee77f03eca50291bf93`.
- Median timing is not a statistical significance bound, and this is CPython model measurement only. No native event isolator, B-spline/STEP assembler, worker, physical hash or end-to-end geometry path was executed.

## Reproduction and guards

From this B1 core directory, on Python >=3.11:

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 experiment.py
python3 bench_b1_reuse_20261110.py
python3 bench_b1_fair_boundary_20261110.py
```

The third command retains historical published evidence; the fourth checks per-edit full-state parity and fairer one-pass/strict-receipt controls. Reports and raw logs are retained outside Git to avoid committing generated local artifacts.

## Consumer and admission decision

The B1 Bernstein/de Casteljau reuse law can reduce mathematical work for **unchanged, trusted piece partitions with complete provenance and local dependencies**. It does not imply a benefit for arbitrary Boolean/topology operations, native B-spline processing, external replay, or CyberSand pressure/solver work. Exact native consumer/invalidation requirements and full-tick/STEP cost remain **UNMEASURED**. The observed Python speed difference depends critically on whether source certificates are kept inside a continuously trusted owner or re-admitted at an external boundary each edit.

B1 `phase_bridge.PRODUCERS` still pins A1 `281705e9...` and A2 `3b6eaf70...`, while current Draft A1 #470 is `406e901a1dd8bd9635129e39c6b634279221f8d4` and A2 #471 is `d9cb56e74e876efb203e04003aadcf8bd368a369` at observation. Current heads correctly fail source admission; no simulated envelope is claimed to originate from a producer. **Actual current A2 point_germ/receipt replay and independently authenticated B-spline source controls/knots are still NOT EXECUTED in this B1 cycle.** A3/B5 need to perform second-source execution and producer-authenticity challenge before any cross-producer GO. Do not update head allowlists to bypass this.

## Frozen gates

The historical 121/20/30/50 census, 26 machining operations and all negative controls remain immutable. MC-B/MC-1 **NOT_ESTABLISHED**, `production_authorized=false`. No production code, native campaigns, paid infrastructure, owner policy, Ready or merge.
