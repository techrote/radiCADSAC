# DR-0003 — Initial production/research process scope is lathe and mill

Status: accepted  
Date: 2026-09-16  
Decision scope: founding programme scope

## Context

SAC could eventually support many subtractive/additive manufacturing processes. Broadening immediately would make kernel research, machine semantics, UI, fixtures, and conformance too diffuse before the core approach is proven.

The lathe and mill are complementary founding processes:

- lathe machining provides strong symmetry/process semantics and a high-leverage specialized-solver research path;
- milling provides a substantially more general cutter-trajectory workload and exercises the backend's harder cases.

## Decision

The initial MSAC/OpenSimachinist research and first productive implementation scope contains **lathe and mill only**.

Future processes such as welding, arc spray, grinding, EDM, additive deposition, or other machine tools should remain architecturally possible but are not required for founding gates or initial production handoff.

## Alternatives considered

### Model a complete workshop immediately

Rejected because it would dilute the geometry research and delay proof of the productive engineering core loop.

### Lathe only

Rejected as the entire founding programme because lathe symmetry alone would not sufficiently exercise general 3D machining requirements.

### Generic freeform cutter engine only

Rejected as the sole founding approach because it would discard high-value process semantics and make the easier/more constrained lathe proof unnecessarily difficult.

## Evidence

This scope is explicitly stated in the founding brief, AGENTS.md, roadmap, and issue graph.

## Consequences

- Research fixtures prioritize turning and milling pathologies.
- Backend interfaces must be extensible without requiring future process details now.
- Product polish/content breadth must not outrun the lathe/mill → STEP productive loop.
- Additive operation semantics may be reserved in generic data models but need not be implemented initially.

## Reversibility

High after the initial productive core is proven. New processes can be added modularly. Changing the initial scope before proof would require an explicit roadmap decision because it affects every current research track.

## Reconsideration trigger

A new process may enter founding scope only if it demonstrates a critical architecture requirement that cannot be represented/tested through lathe or mill workloads and the added complexity is justified explicitly.
