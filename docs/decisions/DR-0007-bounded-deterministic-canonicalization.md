# DR-0007 — Canonicalization is physical-state based, deterministic, and error bounded

Status: accepted  
Date: 2026-09-16  
Decision scope: canonical journal production

## Context

Raw controller samples are coupled to historical input mappings, deadzones, simulation/render timing and device implementations. The programme nevertheless needs natural analogue machining input, replay, regression minimization and future backend replacement.

Path fitting/simplification is desirable for large traces but could silently alter manufactured geometry if treated as cosmetic smoothing.

## Decision

Canonicalization proceeds from a time-ordered **physical machine-state trace**, after controller mapping/deadzone logic has resolved into physical positions/orientations/process state.

The canonicalization policy is immutable and versioned. It:

- uses physical timestamps rather than frame indices;
- splits at setup/tool/process/body/engagement discontinuities;
- reconstructs motion using a specified interpolation rule;
- permits line/arc/polyline/spline fitting only with explicit certified translation/orientation/event-time bounds;
- falls back to a denser representation when a compact fit cannot meet the bound;
- includes numeric quantization in the claimed normalization error;
- preserves engaged repeated/retraced motion even when a backend predicts zero material change.

Given identical normalized physical input and the same policy version, canonical logical output must be deterministic. Differently sampled traces of the same physical motion need not be byte-identical, but must remain within the declared physical error bounds.

Raw device telemetry may be retained for forensic/research use but is not required for normal journal replay.

## Alternatives considered

### Persist raw controller samples as the authoritative journal

Rejected because future meaning would depend on historical device mapping, deadzones and timing implementation.

### One operation per simulation/render sample

Rejected because it creates unnecessary coupling and pathological operation counts without preserving additional manufacturing intent.

### Unbounded smoothing/compression

Rejected because visually pleasing or compact trajectories can falsify dimensions and contact events.

### Require byte-identical output from arbitrarily resampled traces

Rejected as an unjustified guarantee. The correct invariant is bounded physical equivalence; identical-input determinism remains required.

## Evidence

RCS-001 establishes raw telemetry as optional forensic data and canonical operations as durable manufacturing intent. Natural machining workloads also include jitter, retracing and very large sample counts, requiring controlled normalization rather than prohibition.

## Consequences

- Controller/UI implementation can evolve without changing old committed operations.
- Canonicalizers need deterministic reference tests.
- RCS-003 can parameterize noisy trajectories while separating source trace from canonical intent.
- RCS-010/RCS-011 can consume compact trajectories without learning gamepad semantics.
- Backends may optimize geometry no-ops without deleting manufacturing history.

## Reversibility

Medium. Canonicalization algorithms/policies are versioned and replaceable for new operations or explicit migrations. Historical operations retain the policy version under which they were committed.

## Reconsideration trigger

Reconsider if experiments show that a physical-state trace omits process-critical information, or if a fitting representation cannot provide practical certified bounds for real MSAC workloads. Any replacement must preserve backend independence and explicit error accounting.
