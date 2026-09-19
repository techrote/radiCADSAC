# Windows/Linux scale, soak and fault-recovery qualification

RCS-026 / issue #45 qualifies the accepted Genesis-v2 research contracts under platform, scale and recovery pressure. It is intentionally downstream of RCS-018 through RCS-025: it does not rediscover provider capability, invent a production daemon, or relax earlier semantic findings.

## Contract under test

The durable operation journal remains manufacturing intent. Revision IDs, programme body IDs, lineage, source/audio identity and provenance remain programme-owned across process restarts, provider changes and cache loss. OCCT 8.0.1 remains isolated in a worker process because RCS-024 found the same global-state and geometry defects in the tested 8.1.0 development candidate. RCS-025's finite deferred-state guard remains an implementation resource policy in addition to mandatory semantic reconciliation boundaries; the fixture value `2` is not a production tuning constant.

## Pinned cross-platform subset

The mandatory matrix runs on `ubuntu-24.04` and `windows-2025` with exact Python 3.12.10, Ninja, Release C++17 and no C++ extensions. Static guards bind the hosted Linux profile to GCC 13.3 (`130300`) and Windows to MSVC 19.51 (`1951`); MSVC additionally uses `/Zc:__cplusplus`. The workflow records CMake and Ninja versions observed at execution. OCCT is retained at exact 8.0.1 / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`; independent STEP probes remain locked to `step-io=0.2.4` and `vcad-kernel-step/tessellate=0.10.0`.

The accepted RCS-019 canonicalizer vectors are reevaluated on both platforms. Programme-level cross-platform equality covers canonical/status results, durable body and lineage mapping, replay signatures, cache recovery, bounded reconciliation, isolated-configuration outcome and long-soak authority signature. Timing, throughput, resource measurements, OS metadata, STEP bytes and private B-rep identity are deliberately not equality gates.

## Worker and configuration recovery stress

The coordinator repeatedly creates isolated workers for success, timeout, deliberate crash and forced kill, waits/reaps each tracked child, and requires a clean post-fault job. A low/high/low conflicting-configuration control uses separate processes and rejects contamination of the repeated low configuration. This portable control verifies coordinator isolation semantics; it does not supersede RCS-017/RCS-024's real OCCT global-state evidence.

Cache recovery separately deletes and corrupts derived cache data, then reconstructs programme authority from journal/body/lineage data alone. Derived cache content is never accepted as durable authority.

## Scale and long-running soak

Lathe, mill and mixed-provider histories run at both 10,000 and 100,000 journal events, and each history is repeated to detect deterministic disagreement. Material-operation count is reported separately from journal-event count. Reconciliation must finish with no pending decision state and must never exceed the preregistered threshold-2 stress guard.

A second long-running portable campaign executes 20 mixed-provider epochs of 5,000 events (100,000 total), with one reconciliation/query boundary per epoch and a fresh worker recycle every fifth epoch. It records per-epoch latency, throughput, programme identity, reconciliation counts and an aggregate authority signature. The portable soak checks the STEP qualification/status boundary; actual STEP export/read-back is exercised separately in the Linux live soak.

## Memory and resource observations

Python `tracemalloc` remains a narrow coordinator-allocation diagnostic. Native coordinator working set/RSS and process-resource counts are measured separately: `/proc/self/status` plus `/proc/self/fd` on Linux, and `GetProcessMemoryInfo` plus `GetProcessHandleCount` on Windows. The preregistered long-soak fault guards permit no more than four additional coordinator handles/fds and no more than 64 MiB current working-set growth after warm-up. These are bounded research leak detectors, not production SLAs and not claims about peak native RSS inside OCCT child workers.

Worker observations also record whether every spawned child was reaped. Therefore a passing campaign supplies both coordinator resource-trend evidence and process lifecycle evidence rather than inferring leak freedom from successful output alone.

## STEP soak and Gate-5 boundary

Linux CI uses the exact OCCT 8.0.1 exporter and locked independent RCS-022 probes for three complete live export/read-back campaigns covering the accepted metric/inch, analytic and multi-body fixture set. Each repetition is independently validated, then compared at the programme-level body/export/parser/consumer/check boundary. STEP byte identity and private B-rep identity are not required.

The measured RCS-022 Layer-D state remains `interoperability_unqualified`; repeated stability cannot convert that negative result into interoperability qualification. A live exact-pinned OCCT 8.0.1 Windows/MSVC STEP-worker soak is also not established by this campaign. Founding Windows STEP support therefore remains a named Gate-5 blocker unless exact Windows kernel/export evidence is added. The portable Windows campaign is meaningful programme-level qualification evidence, not a substitute for missing Windows STEP execution.

## Evidence lifecycle

`research/rcs-026/experiment-plan-v1.json` is the historical preregistration: hypotheses, toolchain/runtime pins, workload tiers, repeat counts, leak guards and falsification rules are fixed before the final measured campaign. Per-platform, cross-platform and STEP-soak results are machine-readable CI artifacts. Once an exact PR head passes, its artifact identifiers/digests and measured values are frozen separately, this document and DR-0023 are reconciled to them, and the complete exact final head is rerun before merge.
