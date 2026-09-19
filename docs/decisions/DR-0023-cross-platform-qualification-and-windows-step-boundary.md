# DR-0023 — Cross-platform qualification and Windows STEP boundary

Status: accepted from RCS-026 measured evidence  
Issue: RCS-026 / #45

## Context

Genesis-v2 has accepted contracts for durable authority, canonicalization, isolated providers, lathe/mill capability, propagated uncertainty, current-OCCT differential behavior and bounded provider handoff/reconciliation. RCS-026 asks whether those contracts remain deterministic and operationally contained under Windows/Linux, 100k-scale histories, repeated worker faults, cache loss, long-running mixed-provider execution and repeated STEP activity.

## Decision

Use programme-level deterministic equality, not private B-rep identity, as the cross-platform qualification criterion. Require the RCS-019 canonical result, conflicting-configuration isolation outcome, durable body/lineage mapping, replay signatures, failure statuses, cache recovery, reconciliation bounds and long-soak programme signature to agree on the pinned Windows/MSVC and Linux/GCC profiles. Record timing, throughput, native RSS/handle-or-fd trends and Python allocation observations per platform without requiring those physical measurements to be numerically identical.

Use exact Python 3.12.10, Ninja/Release C++17 and compiler-version guards for GCC 13.3 and MSVC 19.51. The accepted hosted Windows campaign explicitly activated Visual Studio 2026's 14.51 toolset and observed compiler 19.51.36256. Retain OCCT 8.0.1 process isolation and all previously accepted source/audio/provenance/body/journal/tolerance/error-budget semantics. A platform failure is evidence to minimize or a Gate-5 blocker; it is not justification to broaden tolerance, discard disconnected bodies, reset propagated error, convert cache/provider identity into programme identity, or downgrade STEP from mandatory engineering output.

Require a warmed 20-epoch/100k-event portable mixed-provider soak to remain within the preregistered coordinator resource guards: no more than four additional handles/fds and no more than 64 MiB current working-set growth. Treat these as research leak detectors rather than product SLAs or measurements of native OCCT-child peak RSS. Require every tracked worker child to be reaped and clean worker execution after timeout, crash and forced kill.

Repeat the actual RCS-022 Linux exporter/parser/consumer path three times and preserve its measured `interoperability_unqualified` status. Stability of a negative Layer-D result is not interoperability qualification. Until an exact-pinned OCCT 8.0.1 Windows/MSVC STEP worker is built and exercised through the corresponding export/read-back soak, Windows STEP support remains conditional and must be reported as a Gate-5 blocker. The portable Windows programme-level campaign cannot stand in for missing kernel/export evidence.

## Accepted evidence

The decision is based on workflow run `35409683331` from PR head `fafe9ef74de7d89e690fdc61ee98c879c062b344`; artifact IDs/digests and measured latency/resource/scale values are frozen in `research/rcs-026/measured-result-v1.json`.

The pinned Linux and Windows campaigns both reached the 100,000-journal-event tier for lathe, mill and mixed-provider histories and produced the identical logical signature `f346cbf442b664c93987ea704b215d7e4efee051b5e62cae585e5b9f936ff98b`; the explicit cross-platform comparison reported zero mismatches. Every scale history preserved programme body/lineage authority and held peak pending state to the preregistered stress value `2`.

On both platforms the recovery campaign contained four timeouts, three crashes and two forced kills, reaped all tracked children, recorded zero orphan processes and completed a clean post-fault workload. The 20-epoch soak completed 100,000 journal events / 75,000 material operations, 20 query boundaries and four successful worker recycles. Linux recorded zero current-RSS growth after warm-up and Windows 36,864 bytes; both recorded zero handle/fd growth, within the preregistered limits.

Three exact-OCCT-8.0.1 Linux STEP campaigns passed all seven adversarial controls while all 11 positive fixtures remained short of Layer-D qualification; the aggregate result therefore remains `interoperability_unqualified`. Repetition produced differing STEP byte hashes, which is acceptable because byte identity was explicitly excluded from programme-level equality. Windows live STEP remains `not_run` and is retained as a Gate-5 blocker.

## Alternatives considered

Require bitwise-identical B-rep or STEP output across platforms. Rejected because private kernel identity is not programme authority and byte identity is stronger than the accepted engineering contract.

Infer Windows STEP support from portable programme-level Windows execution plus Linux STEP soak. Rejected because it would manufacture kernel/export evidence that was not measured.

Treat Python `tracemalloc` alone as memory-leak evidence. Rejected because it does not measure native RSS or OS process resources; RCS-026 therefore samples native coordinator working set plus handles/fds and separately records tracked child reaping.

Relax tolerance, lineage, body, source/audio provenance or error-budget semantics when a platform diverges. Rejected because qualification must test the accepted contract rather than alter it to obtain a pass.

## Consequences

The measured Windows/Linux campaign qualifies programme-level deterministic semantics and bounded coordinator recovery for the tested profiles through the declared 100k research tier. It does not establish a production capacity SLA, native OCCT-worker memory ceiling, or arbitrary-duration leak freedom.

Linux STEP repetition demonstrates stable negative Layer-D behavior but does not upgrade RCS-022 beyond `interoperability_unqualified`. Founding Windows STEP support remains conditional on an exact-pinned OCCT 8.0.1 Windows/MSVC export/read-back campaign. This is an explicit Gate-5 blocker, not an implementation detail that may be inferred away.

The RCS-025 threshold value `2` remains a deliberately small research stress fixture, not a production tuning constant. The durable operation journal, programme body/lineage identities, propagated error, source/audio identity and provenance remain authoritative across provider restart, cache loss and replay.

## Reversibility

This decision can be revised when exact-pinned Windows OCCT STEP-worker evidence, deeper native worker telemetry or a newly qualified kernel/provider exists. Any replacement must rerun the same programme-level and export boundaries and preserve the durable-authority contracts; no migration may silently reinterpret old journal/body/source/audio/provenance state.
