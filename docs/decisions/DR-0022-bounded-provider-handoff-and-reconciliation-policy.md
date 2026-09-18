# DR-0022 — bounded provider handoff and reconciliation policy

Status: **accepted**  
Date: 2026-09-19  
Issue: RCS-025 / #44

## Context

DR-0015 selected a semantic-provider hybrid, while later decisions qualified realistic lathe input, a bounded manual-mill fallback, conservative propagated error budgets, process isolation and truthful STEP interoperability status. Before production foundation freeze, the programme still needed evidence that these individually accepted pieces could compose across repeated provider transitions without corrupting durable identity, body connectivity, replay or error accounting.

RCS-025 exercises those seams using programme-owned durable state, provider-private diagnostic topology identity, repeated pending/reconciliation cycles, split/merge cases, mixed-provider replay and RCS-023 error traces.

## Decision

The semantic-provider hybrid is retained with the following mandatory handoff/reconciliation rules.

### Programme authority is provider-independent

Durable revision IDs, operation IDs, material-body IDs and semantic lineage events belong to programme authority. Backend topology IDs, OCCT/BRepGraph item identities, worker object handles and other provider-private identifiers may exist only as ephemeral diagnostics/cache keys.

A provider transition may regenerate all backend topology. It must not silently replace durable body meaning. If semantic lineage/body correspondence is ambiguous, the engineering state is `accepted_pending` or refused with explicit ambiguity; guessing is prohibited.

### Hard reconciliation boundaries are mandatory

Pending/deferred material must be reconciled before any decision whose correctness requires exact current engineering topology, including body connectivity/selection and STEP export. Provider predicate exits that require a representation transition are also explicit handoff boundaries.

### A finite deferred-state resource guard is also mandatory

Hard semantic boundaries alone do not bound deferred-state growth when many operations occur before the next exact query. The coordinator must therefore enforce a finite, observable resource guard in addition to hard boundaries. The guard may use pending-state size, estimated reconciliation cost, elapsed work/query pressure, or another deterministic bounded metric.

The RCS-025 threshold value `2` is a deliberately small stress-fixture parameter, **not** a frozen production constant. Production may tune the threshold, but may not remove the finite guard or weaken the hard semantic boundaries.

### Reconciliation is not an error-budget reset

RCS-023 error accounting continues across provider conversions. A deferred/fallback representation bound may be discharged only when that representation is replaced from programme authority by an independently justified reconstruction and validation step. The old representation bound is not subtracted or presumed to cancel; the replacement state receives its own reconciliation/validation contribution and continues from the same durable provenance chain.

If the resulting budget is unresolved or exceeds the declared engineering budget, the operation/export remains pending, `error_budget_breach`, or `refused_accuracy_unproven` as applicable. Manufacturing tolerance must not be widened to force success.

### STEP remains a reconciled-B-rep boundary

Bounded directional/implicit/fallback state is never STEP-authoritative. STEP is requested only from conventional reconciled engineering B-rep that passes the applicable RCS-005/RCS-023 gates. Passing those gates does not upgrade RCS-022 Layer D: the current production-candidate profile remains `interoperability_unqualified` until independent interoperability qualification changes that status.

### Replay rebuilds providers from programme authority

Undo/replay may discard provider-private derived state. Rebuilding the accepted dispatch chain must reproduce programme-level statuses, bodies, lineage and geometry invariant within the accepted validation/error-budget policy. Bitwise B-rep identity is not required unless a provider later explicitly promises it.

### Process isolation remains in force

RCS-024 did not remove the RCS-017 global-state defects. Provider handoff/reconciliation therefore does not relax DR-0016: OCCT engineering/STEP work remains process-isolated by default.

## Evidence

RCS-025 frozen deterministic evidence demonstrates:

- lathe→generic provider transition with stable durable body identity and changed backend topology diagnostics;
- mill exact→directional fallback→B-rep with explicit non-cancellation of fallback representation error;
- eight-operation policy comparison: hard-only peak pending `4`, 2 reconciliations / 26 work units; threshold-2 peak pending `2`, 4 reconciliations / 36 work units;
- 64-operation growth control: hard-only peak pending `64`, threshold policy peak `2`;
- connectivity query blocked while pending, then explicit one→two split and two→one merge lineage;
- three topology regenerations with stable durable body identity and an ambiguity control that fails closed;
- equal mixed-provider replay signatures after provider-private state discard;
- propagated budget pass (`0.000016 mm`), breach (`0.000066 mm`) and positive-sub-uncertainty removal controls;
- truthful `interoperability_unqualified` STEP state after geometrically eligible reconciliation.

The detailed record is `docs/33-PROVIDER-HANDOFF-RECONCILIATION-STRESS.md`; machine-readable evidence is `research/rcs-025/reference-results-v1.json`.

## Alternatives considered

### Reconcile only at semantic/query boundaries

Rejected as the sole policy. It minimizes reconciliation frequency in the deterministic fixture but permits pending-state growth proportional to distance from the next boundary.

### Reconcile every operation

Rejected as a founding rule. It trivially bounds pending state but erases much of the specialization/deferred-state advantage and introduces unnecessary conversion cost. Implementations may choose this locally when appropriate, but the architecture does not require it.

### Treat fallback error as cancelled after B-rep conversion

Rejected. Representation conversion alone is not evidence that the previous approximation error disappeared. Safe discharge requires reconstruction from programme authority plus independent validation and a new bounded contribution.

### Persist provider topology/history identifiers for replay

Rejected. This violates DR-0011 and the RCS-024 BRepGraph boundary and makes durable programme meaning depend on backend generations.

## Consequences

The coordinator API must expose pending/reconciled state, body/lineage ambiguity, reconciliation reason, finite resource-policy state and propagated budget status. Provider adapters must accept programme-owned durable context and return mappings/evidence without owning durable identity. Export requests can trigger mandatory reconciliation and can still fail because of unresolved budgets or Layer-D qualification state.

The production implementation retains freedom over the concrete threshold metric, cache layout, provider-local algorithms and scheduling heuristics so long as the mandatory boundaries and fail-closed semantics above hold.

## Reversibility

The exact resource threshold and cost model are intentionally reversible implementation choices. Provider capability predicates can also evolve with later evidence. The durable identity, no-silent-ambiguity, no-budget-reset and reconciled-B-rep-before-STEP rules are founding semantic constraints and require explicit superseding evidence/decision to change.

## Remaining evidence

RCS-026 must qualify Windows/MSVC and Linux behavior, larger operation histories, worker crash/recycle, long-run memory/latency trends and STEP soak. A failure there can refine or block Gate 5 even though the deterministic RCS-025 coordinator semantics are accepted.
