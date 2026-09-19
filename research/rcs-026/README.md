# RCS-026 — Windows/Linux scale, soak and fault-recovery qualification

Issue: RCS-026 / #45  
Plan: `experiment-plan-v1.json`  
Status: exact-head measured CI campaign pending final freeze

## Scope

RCS-026 qualifies the already-accepted Genesis-v2 research contracts under platform, scale, worker-fault, replay/cache and STEP-soak pressure. It does not introduce a production daemon or change manufacturing semantics to make a platform pass. Programme-owned journal, revision/body/lineage identity and provenance remain authoritative; provider-private topology is disposable and OCCT remains process-isolated per RCS-017/RCS-024.

The mandatory cross-platform subset runs on `ubuntu-24.04` and `windows-2025` with Python **3.12.10**, Ninja and a C++17 probe. Static qualification guards bind the hosted profiles to GCC 13.3 (`130300`) and MSVC 19.51 (`1951`); `/Zc:__cplusplus` makes the MSVC probe report its actual C++17 language mode rather than the legacy macro. OCCT remains pinned to 8.0.1 / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` by DR-0021.

## Predeclared hypotheses and boundaries

`experiment-plan-v1.json` freezes six hypotheses and falsification conditions before the final measured campaign: RCS-019 canonicalizer equality, isolated fault/configuration containment, deterministic 10k/100k programme replay, cache-loss recovery, repeated live STEP behavior, and a 20-epoch/100k-event mixed-provider soak with native resource guards. The 100k tiers mean journal events and separately record material-operation count; they are not relabelled as 100k physical cuts.

Cross-platform equality is deliberately programme-level: statuses, canonical results, conflicting-configuration isolation result, durable body mapping, lineage, replay signatures, cache recovery, bounded reconciliation and long-soak programme signature. Wall time, throughput, Python allocation samples, native RSS/handle/fd observations, OS metadata, STEP bytes and private B-rep identity are measurements rather than bitwise-equality gates.

## Adversarial controls

The portable campaign injects provider timeout, injected crash and forced kill, requires each tracked child to be reaped, then requires a clean isolated worker to succeed. A separate low/high/low configuration sequence uses fresh worker processes and rejects cross-process configuration contamination. This coordinator control supplements rather than replaces the real OCCT global-state evidence from RCS-017/RCS-024.

Cache recovery deletes and corrupts derived state and reconstructs authority solely from the journal. Scale and long-soak campaigns retain RCS-025's threshold-2 research stress guard and reject pending-state escape above that predeclared bound. Boundary tests additionally exercise the 100k replay tier, native resource probes, worker reaping and RCS-022's measured `interoperability_unqualified` status.

## Scale, long soak and resources

The scale campaign runs lathe, mill and mixed-provider histories at 10,000 and 100,000 journal events and repeats each history to detect nondeterminism. It records material-operation counts, programme body/lineage state, reconciliation work, latency distribution, throughput and Python `tracemalloc` observations.

A separate portable long soak performs 20 mixed-provider epochs of 5,000 events each, with a reconciliation/query boundary every epoch and a clean worker recycle every fifth epoch. Native coordinator RSS and process-resource counts are sampled through `/proc` on Linux and `GetProcessMemoryInfo` / `GetProcessHandleCount` on Windows. The preregistered leak controls are at most four extra coordinator handles/fds and at most 64 MiB current working-set growth over the warmed long-soak window. These are research fault guards, not product performance SLAs or measurements of OCCT child-process peak RSS.

## STEP soak

The Linux CI leg builds the exact pinned OCCT 8.0.1 exporter plus the locked RCS-022 `step-io=0.2.4` and `vcad-kernel-*=0.10.0` independent probes, then performs three complete live export/read-back campaigns. Each repetition must independently pass the RCS-022 validator. RCS-026 compares programme-level export/parser/consumer/body/check outcomes; it deliberately does not require STEP byte identity or private B-rep identity.

RCS-022's Layer-D outcome remains `interoperability_unqualified`. RCS-026 is forbidden from converting a stable negative result into qualification merely because repetition is stable.

A live exact-pinned OCCT 8.0.1 Windows/MSVC STEP-worker soak is not established by this campaign design. Unless exact Windows kernel/export evidence is added, that absence is a named Gate-5 blocker for founding Windows STEP support; portable Windows programme semantics and Linux STEP evidence must not be generalized into Windows STEP qualification.

## Measurements and claim limits

Each platform artifact records the compiler/runtime/build-tool versions actually observed, canonicalizer and programme-level signatures, conflicting configuration control, fault/recovery counts, per-stage latency distributions, throughput, 10k/100k scale evidence, 100k long-soak evidence, native coordinator RSS/handle-or-fd trend, Python allocation trend and cache-recovery evidence. Worker lifecycle evidence distinguishes success, timeout, crash and forced kill and records whether every tracked child was reaped.

Measured values are frozen only after reviewing exact-head CI artifacts. The preregistered plan remains immutable historical evidence of what was promised before the final measurement; the measured result is stored separately.

## Reproduction

```bash
python tools/validate_rcs026.py
python -m py_compile research/rcs-026/*.py tools/validate_rcs026.py
python -m unittest discover -v -s research/rcs-026 -p 'test_*.py'
cmake -S research/rcs-026/toolchain -B .build/rcs026-toolchain -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build .build/rcs026-toolchain --parallel 2
ctest --test-dir .build/rcs026-toolchain --output-on-failure
python research/rcs-026/run_campaign.py --out-dir .results/rcs026/local --toolchain-json .build/rcs026-toolchain/toolchain.json
python tools/validate_rcs026.py --result .results/rcs026/local/result.json
```

The live STEP soak is intentionally CI-oriented because it depends on the exact-pinned OCCT build and the locked independent RCS-022 consumers.
