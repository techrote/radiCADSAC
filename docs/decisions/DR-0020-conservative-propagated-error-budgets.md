# DR-0020 — Conservative propagated error budgets and fail-closed accuracy

Status: **accepted**  
Date: 2026-09-18  
Evidence: RCS-023 / issue #42

## Context

DR-0010 established that manufacturing tolerance, numerical uncertainty, contact classification and export validation are distinct. Subsequent deferred/fallback/provider research introduced additional representation and reconciliation error sources, but the programme still needed an executable rule for carrying those sources across transforms, providers and export boundaries.

Without such a rule, a later implementation could accidentally reset an error budget at a provider handoff, use RSS without independence evidence, hide an unknown numerical error inside manufacturing tolerance, or convert an ambiguous positive cut into a no-op.

## Decision

The programme adopts `rcs-uncertainty-budget/1.0` as the founding propagation semantics for Genesis-v2 synthesis.

1. Bounded numerical/representation errors compose conservatively by interval/Minkowski sum when dependence is unknown.
2. Stage-local errors remain attached to the downstream sensitivity/transform graph; order/gain is part of the bound.
3. RSS is not a correctness bound without explicit independence evidence.
4. Error cancellation is allowed only for a proven shared bounded source with known coefficients.
5. Provider/representation handoff carries source residual + conversion residual + destination residual. A boundary does not reset prior uncertainty.
6. Manufacturing requirements, contact policy and export/validation budgets are non-error channels and may not be added as solver error or used to excuse unknown error.
7. A physical contact/material decision is decisive only when the complete propagated interval lies on one side of the decision boundary. Boundary overlap means `accepted_pending`.
8. Explicit positive-removal intent whose interval overlaps zero remains pending; it never silently becomes `no material change`.
9. A bounded fallback representation may be `bounded_representation_inexact`, but conventional STEP success requires completed B-rep reconciliation.
10. Any required unknown error or incomplete reconciliation causes `refused_accuracy_unproven`. A known bound beyond the requested budget causes `error_budget_breach`.
11. RCS-005 remains the STEP authority. RCS-023's scalar spatial bound maps only to dimension/surface acceptance unless a geometry-specific proof maps it into angular/volume metrics.
12. Budget traces are programme-owned derived evidence tied to durable journal/revision/body/semantic lineage; provider-private topology/process identity is not durable state.

## Evidence

The deterministic RCS-023 campaign demonstrates:

- complete lathe and mill traces with final half-widths 14.5 nm and 17.5 nm respectively;
- a mill fallback that remains representation-inexact until explicit B-rep reconciliation;
- a 10 nm contact sweep whose exact/boundary members remain pending;
- a 1 nm positive-removal command under 5 nm uncertainty that remains pending rather than being erased;
- 100 correlated 1 nm terms yielding a 100 nm same-sign witness versus a 10 nm RSS diagnostic;
- an 8+6+4 nm provider handoff requiring an 18 nm bound rather than max-only 8 nm;
- an order-sensitive 45 nm versus 30 nm transform witness;
- explicit 15 nm pass, 26 nm breach and unknown-fit refusal controls.

Twenty adversarial/boundary unit tests and a deterministic reference-result comparison exercise the executable contract.

## Alternatives considered

### One global programme epsilon

Rejected by RCS-007 and remains rejected. It collapses manufacturing intent, numerical uncertainty and topology/contact policy.

### Sum all tolerances, including manufacturing/export tolerance

Rejected. Requirements are acceptance criteria, not error contributions. Adding them would make a looser requirement appear to increase numerical uncertainty and could mask an unknown solver error.

### Root-sum-square by default

Rejected for correctness. The RCS-023 correlated witness is 100 nm while RSS reports 10 nm. RSS can be retained as a diagnostic only when independence evidence is explicit.

### Reset error at provider/reconciliation boundaries

Rejected. It loses known upstream error. Handoff must account for source, conversion and destination residuals separately.

### Always use worst-case sum even for proven common-mode cancellation

Too conservative when a formal shared-source relation is available. The contract therefore permits exact coefficient-based cancellation, but only with explicit proof that terms refer to the same bounded source.

### Treat any interval that touches zero as decisive

Rejected. A boundary-inclusive interval admits both contact sides. The contract uses strict one-sided classification and keeps boundary members pending.

## Consequences

- RCS-025 must carry a remaining-budget trace through every provider/defer/reconcile transition.
- RCS-027 Gate-5 synthesis must treat these propagation rules as programme contract unless superseded by stronger evidence.
- Providers may maintain richer private uncertainty models, but their programme boundary must return a demonstrable conservative projection plus provenance.
- Production STEP UX must distinguish budget breach, unproven accuracy, representation-pending and independent interoperability qualification.
- A large manufacturing tolerance can never make missing numerical evidence disappear.

## Reversibility

High for concrete data structure and local numerical method; medium for the conservative founding semantics. A later validated affine/interval/exact-arithmetic model may tighten bounds without changing the public safety rules.

The fail-closed rules, separation of requirements from numerical error, positive-intent preservation, and no-reset provider handoff are intended to be durable unless later evidence demonstrates an equally safe replacement.
