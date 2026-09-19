# DR-0023 — Cross-platform qualification and Windows STEP boundary

Status: proposed pending exact-head RCS-026 measured evidence  
Issue: RCS-026 / #45

## Context

Genesis-v2 now has accepted contracts for durable authority, canonicalization, isolated providers, lathe/mill capability, propagated uncertainty, current-OCCT differential behavior and bounded provider handoff/reconciliation. RCS-026 asks whether those contracts remain operationally deterministic under Windows/Linux, larger histories, worker faults, cache loss and repeated STEP activity.

## Decision

Provisionally use programme-level deterministic equality, not private B-rep identity, as the cross-platform qualification criterion. Require the RCS-019 canonical result, durable body/lineage mapping, replay signatures, failure statuses, cache recovery and reconciliation bounds to agree on Windows/MSVC and Linux. Record timing and allocation observations per platform without requiring equality.

Retain OCCT 8.0.1 process isolation and all previously accepted source/provenance/body/journal/tolerance semantics. A platform failure is evidence to minimize or a Gate-5 blocker; it is not justification to broaden tolerance, discard disconnected bodies, reset propagated error, convert cache/provider identity into programme identity, or downgrade STEP from mandatory engineering output.

Repeat the actual RCS-022 Linux exporter/parser/consumer path three times and preserve its measured `interoperability_unqualified` status. Stability of a negative Layer-D result is not interoperability qualification.

Until an exact-pinned OCCT 8.0.1 Windows/MSVC STEP worker is built and exercised through the corresponding export/read-back soak, Windows STEP support remains conditional and must be reported as a Gate-5 blocker. The portable Windows programme-level campaign cannot stand in for missing kernel/export evidence.

## Alternatives considered

Require bitwise-identical B-rep or STEP output across platforms. Rejected because private kernel identity is not programme authority and byte identity is stronger than the accepted engineering contract.

Infer Windows STEP support from portable programme-level Windows execution plus Linux STEP soak. Rejected because it would manufacture kernel/export evidence that was not measured.

Relax tolerance, lineage, body, provenance or error-budget semantics when a platform diverges. Rejected because qualification must test the accepted contract rather than alter it to obtain a pass.

## Consequences

A passing portable Windows/Linux campaign can qualify programme-level deterministic semantics while leaving Windows STEP support explicitly conditional. Linux STEP repetition can demonstrate soak stability but cannot upgrade RCS-022 Layer D beyond its measured `interoperability_unqualified` result. Platform-specific failures remain evidence to minimize or record as Gate-5 blockers.

## Reversibility

This decision can be revised when exact-pinned Windows OCCT STEP-worker evidence or a newly qualified kernel/provider exists. Any replacement must rerun the same programme-level and export boundaries and preserve the durable-authority contracts; no migration may silently reinterpret old journal/body/provenance state.

## Evidence required before acceptance

DR-0023 remains proposed until the exact PR head has: passing Windows and Linux platform artifacts, a passing cross-platform comparison, passing worker/cache/100k stress evidence, three validated live Linux STEP repetitions, explicit Windows STEP blocker retention, and all repository CI checks green. The measured toolchain versions, signatures, latency/allocation observations and exact completed workload tiers must then be frozen into RCS-026 documentation before this record is accepted.
