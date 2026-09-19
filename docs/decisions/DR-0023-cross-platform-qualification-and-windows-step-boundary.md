# DR-0023 — Cross-platform qualification and Windows STEP boundary

Status: proposed pending exact-head RCS-026 measured evidence  
Issue: RCS-026 / #45

## Context

Genesis-v2 has accepted contracts for durable authority, canonicalization, isolated providers, lathe/mill capability, propagated uncertainty, current-OCCT differential behavior and bounded provider handoff/reconciliation. RCS-026 asks whether those contracts remain deterministic and operationally contained under Windows/Linux, 100k-scale histories, repeated worker faults, cache loss, long-running mixed-provider execution and repeated STEP activity.

## Decision

Provisionally use programme-level deterministic equality, not private B-rep identity, as the cross-platform qualification criterion. Require the RCS-019 canonical result, conflicting-configuration isolation outcome, durable body/lineage mapping, replay signatures, failure statuses, cache recovery, reconciliation bounds and long-soak programme signature to agree on the pinned Windows/MSVC and Linux/GCC profiles. Record timing, throughput, native RSS/handle-or-fd trends and Python allocation observations per platform without requiring those physical measurements to be numerically identical.

Use exact Python 3.12.10, Ninja/Release C++17 and compiler-version guards for GCC 13.3 and MSVC 19.51. Retain OCCT 8.0.1 process isolation and all previously accepted source/audio/provenance/body/journal/tolerance/error-budget semantics. A platform failure is evidence to minimize or a Gate-5 blocker; it is not justification to broaden tolerance, discard disconnected bodies, reset propagated error, convert cache/provider identity into programme identity, or downgrade STEP from mandatory engineering output.

Require a warmed 20-epoch/100k-event portable mixed-provider soak to remain within the preregistered coordinator resource guards: no more than four additional handles/fds and no more than 64 MiB current working-set growth. Treat these as research leak detectors rather than product SLAs or measurements of native OCCT-child peak RSS. Require every tracked worker child to be reaped and clean worker execution after timeout, crash and forced kill.

Repeat the actual RCS-022 Linux exporter/parser/consumer path three times and preserve its measured `interoperability_unqualified` status. Stability of a negative Layer-D result is not interoperability qualification. Until an exact-pinned OCCT 8.0.1 Windows/MSVC STEP worker is built and exercised through the corresponding export/read-back soak, Windows STEP support remains conditional and must be reported as a Gate-5 blocker. The portable Windows programme-level campaign cannot stand in for missing kernel/export evidence.

## Alternatives considered

Require bitwise-identical B-rep or STEP output across platforms. Rejected because private kernel identity is not programme authority and byte identity is stronger than the accepted engineering contract.

Infer Windows STEP support from portable programme-level Windows execution plus Linux STEP soak. Rejected because it would manufacture kernel/export evidence that was not measured.

Treat Python `tracemalloc` alone as memory-leak evidence. Rejected because it does not measure native RSS or OS process resources; RCS-026 therefore samples native coordinator working set plus handles/fds and separately records tracked child reaping.

Relax tolerance, lineage, body, source/audio provenance or error-budget semantics when a platform diverges. Rejected because qualification must test the accepted contract rather than alter it to obtain a pass.

## Consequences

A passing portable Windows/Linux campaign can qualify programme-level deterministic semantics and bounded coordinator recovery while leaving Windows STEP support explicitly conditional. Linux STEP repetition can demonstrate soak stability but cannot upgrade RCS-022 Layer D beyond its measured `interoperability_unqualified` result. Platform-specific failures remain evidence to minimize or record as named Gate-5 blockers.

The resource guards are deliberately bounded research controls. They do not establish a production capacity target, a native OCCT worker RSS ceiling, or long-duration leak freedom beyond the measured campaign. Later deployment work must profile actual production worker pools separately.

## Reversibility

This decision can be revised when exact-pinned Windows OCCT STEP-worker evidence, deeper native worker telemetry or a newly qualified kernel/provider exists. Any replacement must rerun the same programme-level and export boundaries and preserve the durable-authority contracts; no migration may silently reinterpret old journal/body/source/audio/provenance state.

## Evidence required before acceptance

DR-0023 remains proposed until one exact PR head has: passing pinned Windows and Linux platform artifacts, a passing cross-platform comparison, passing conflicting-configuration/fault/reaping controls, deterministic 10k/100k scale evidence, a passing 20-epoch/100k long soak with native resource trends, cache loss/corruption recovery, three validated live Linux STEP repetitions, explicit Windows STEP blocker retention, and all repository CI checks green. The exact toolchain/runtime observations, signatures, resource/latency measurements, artifact identifiers/digests and completed workload tiers must then be frozen into RCS-026 documentation before this record is accepted.
