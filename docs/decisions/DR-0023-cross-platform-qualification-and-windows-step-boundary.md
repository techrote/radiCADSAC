# DR-0023 — Cross-platform qualification and Windows STEP boundary

Status: proposed pending exact-head RCS-026 measured evidence  
Issue: RCS-026 / #45

## Context

Genesis-v2 now has accepted contracts for durable authority, canonicalization, isolated providers, lathe/mill capability, propagated uncertainty, current-OCCT differential behavior and bounded provider handoff/reconciliation. RCS-026 asks whether those contracts remain operationally deterministic under Windows/Linux, larger histories, worker faults, cache loss and repeated STEP activity.

## Proposed decision

Use programme-level deterministic equality, not private B-rep identity, as the cross-platform qualification criterion. Require the RCS-019 canonical result, durable body/lineage mapping, replay signatures, failure statuses, cache recovery and reconciliation bounds to agree on Windows/MSVC and Linux. Record timing and allocation observations per platform without requiring equality.

Retain OCCT 8.0.1 process isolation and all previously accepted source/provenance/body/journal/tolerance semantics. A platform failure is evidence to minimize or a Gate-5 blocker; it is not justification to broaden tolerance, discard disconnected bodies, reset propagated error, convert cache/provider identity into programme identity, or downgrade STEP from mandatory engineering output.

Repeat the actual RCS-022 Linux exporter/parser/consumer path three times and preserve its measured `interoperability_unqualified` status. Stability of a negative Layer-D result is not interoperability qualification.

Until an exact-pinned OCCT 8.0.1 Windows/MSVC STEP worker is built and exercised through the corresponding export/read-back soak, Windows STEP support remains conditional and must be reported as a Gate-5 blocker. The portable Windows programme-level campaign cannot stand in for missing kernel/export evidence.

## Evidence required before acceptance

DR-0023 remains proposed until the exact PR head has: passing Windows and Linux platform artifacts, a passing cross-platform comparison, passing worker/cache/100k stress evidence, three validated live Linux STEP repetitions, explicit Windows STEP blocker retention, and all repository CI checks green. The measured toolchain versions, signatures, latency/allocation observations and exact completed workload tiers must then be frozen into RCS-026 documentation before this record is accepted.
