# RCS-026 — Windows/Linux scale, soak and fault-recovery qualification

Issue: RCS-026 / #45  
Plan: `experiment-plan-v1.json`  
Status: measured CI campaign pending

## Scope

RCS-026 qualifies the already-accepted Genesis-v2 research contracts under platform, scale, worker-fault, replay/cache and STEP-soak pressure. It does not introduce a production daemon or change manufacturing semantics to make a platform pass. Programme-owned journal, revision/body/lineage identity and provenance remain authoritative; provider-private topology is disposable and OCCT remains process-isolated per RCS-017/RCS-024.

The cross-platform deterministic subset is mandatory on `ubuntu-24.04` and `windows-2025`, Python 3.12, with a compiled C++17 toolchain probe proving the Linux GCC/Clang family and Windows MSVC family actually build and execute. OCCT remains pinned to 8.0.1 / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` by DR-0021.

## Predeclared hypotheses and boundaries

`experiment-plan-v1.json` freezes six hypotheses and their falsification conditions before the measured campaign: RCS-019 canonicalizer equality, isolated worker fault containment, deterministic 10k/100k programme replay, cache-loss recovery, repeated live STEP behavior, and bounded resource/latency observations. The 100k tier means journal events and separately records unique material operations; it is not relabelled as 100k physical cuts.

Cross-platform equality is intentionally programme-level: statuses, canonical results, durable body mapping, lineage, replay signatures, cache recovery and bounded reconciliation state. Wall time, Python allocation samples, compiler strings, STEP bytes and private B-rep identity are observations rather than bitwise-equality gates.

## Adversarial controls

The portable campaign injects provider timeout, injected crash and forced kill, then requires a clean isolated worker to succeed. It deletes and corrupts a derived cache and rebuilds authority solely from the journal. It runs the RCS-025 threshold-2 stress guard at scale and rejects any pending-state escape above the predeclared bound. Unit tests also exercise the 100k replay boundary and preserve RCS-022's measured `interoperability_unqualified` status.

## STEP soak

The Linux CI leg builds the exact pinned OCCT 8.0.1 exporter plus the locked independent RCS-022 Rust parser/consumer once, then performs three complete live export/read-back campaigns. Each repetition must independently pass the RCS-022 validator. RCS-026 compares programme-level export/parser/consumer/body/check outcomes between repetitions; it does not require STEP byte identity or private B-rep identity.

RCS-022's Layer-D outcome remains `interoperability_unqualified`. RCS-026 is forbidden from converting a stable negative result into qualification merely because repetition is stable.

A live exact-pinned OCCT 8.0.1 Windows/MSVC STEP-worker soak is not established by this campaign design. Unless later evidence is added to this issue, that absence is a precise Gate-5 blocker for founding Windows STEP support; Linux STEP evidence must not be generalized to Windows.

## Measurements and claim limits

Each platform result records canonicalizer signature, fault/recovery outcomes, latency distributions, 10k/100k workload signatures, material-operation counts, reconciliation counts, cache-recovery evidence and Python `tracemalloc` observations. `tracemalloc` covers coordinator Python allocations only and is not represented as OCCT-worker RSS. The workflow records actual compiler family through the compiled C++ probe.

Measured values are not frozen in this document until the PR's exact-head CI artifacts have been reviewed. This preserves the repository rule that research documentation distinguishes predeclared method from measured result.

## Reproduction

```bash
python tools/validate_rcs026.py
python -m py_compile research/rcs-026/*.py tools/validate_rcs026.py
python -m unittest discover -v -s research/rcs-026 -p 'test_*.py'
cmake -S research/rcs-026/toolchain -B .build/rcs026-toolchain -DCMAKE_BUILD_TYPE=Release
cmake --build .build/rcs026-toolchain --config Release
ctest --test-dir .build/rcs026-toolchain -C Release --output-on-failure
python research/rcs-026/run_campaign.py --out-dir .results/rcs026/local --toolchain-json .build/rcs026-toolchain/toolchain.json
python tools/validate_rcs026.py --result .results/rcs026/local/result.json
```

The live STEP soak is intentionally CI-oriented because it depends on the exact-pinned OCCT build and the locked independent RCS-022 consumers.
