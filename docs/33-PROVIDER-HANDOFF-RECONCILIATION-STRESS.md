# Provider handoff, deferred-state and reconciliation stress — RCS-025

Status: RCS-025 deterministic research record  
Issue: #44  
Plan: `research/rcs-025/experiment-plan-v1.json`  
Evidence: `research/rcs-025/reference-results-v1.json`

## Purpose

RCS-025 asks whether the accepted semantic-provider hybrid composes safely when engineering state crosses provider boundaries repeatedly. The campaign focuses on programme identity, pending-state resource behavior, reconciliation, replay, body connectivity, STEP eligibility and propagated uncertainty. It deliberately does not reopen broad provider selection or implement a production scheduler.

## Evidence vocabulary

- **SOURCE** — an accepted predecessor contract or measurement reused without re-measuring it here.
- **MEASURED_DETERMINISTIC_MODEL** — a deterministic result produced by the RCS-025 Python handoff/coordinator stress model.
- **INFERENCE** — an architecture conclusion derived from SOURCE and model evidence.
- **OPEN** — intentionally deferred evidence, principally native fallback→B-rep reconstruction qualification and platform/soak resource qualification.

RCS-025 does **not** execute a new native geometry reconstruction for its provider handoffs. Values such as the carried retrace-jitter material volume come from accepted predecessor measurements; reconciliation work units, pending-state growth, replay signatures and synthetic reconciliation bounds are model evidence. Therefore RCS-025 qualifies the coordinator/policy semantics it models, but it does not by itself qualify a production fallback→conventional-B-rep reconstruction path or its claimed geometric accuracy.

## Accepted inputs

**SOURCE:** RCS-018 supplies the durable-authority/evidence vocabulary and the hard prohibition on provider-private identity entering durable state. RCS-020 supplies the realistic axisymmetric lathe capability boundary; non-axisymmetric/live-tool work remains outside that provider. RCS-021 supplies the independently checked `retrace-jitter` material result and a bounded directional fallback that must reconcile to conventional B-rep before STEP. RCS-022 leaves Layer D `interoperability_unqualified`. RCS-023 supplies conservative interval/Minkowski error-budget composition. RCS-024 retains OCCT 8.0.1 and process isolation and rejects backend graph IDs as durable programme identity.

## Handoff hypotheses and falsification

The predeclared plan requires provider regeneration to preserve programme-owned body/operation lineage; requires bounded fallback to remain non-STEP-authoritative; predicts that hard-only reconciliation allows pending-state growth; requires connectivity-dependent decisions to block while pending; requires replay invariance after provider-private state loss; and requires propagated-error breaches to fail closed. Any private-ID dependency, silent lineage mapping, body loss, budget reset/tolerance widening, or replay divergence falsifies the corresponding hypothesis.

## Lathe to generic/exact transition

**MEASURED:** The lathe→generic fixture preserves durable `body-main` while the diagnostic backend topology identity changes during reconciliation. The provider transition is explicit: `lathe-axisymmetric-real-tool@rcs-020` → `generic-exact-brep@rcs-011-control`. A deliberately non-axisymmetric operation therefore leaves the specialized lathe predicate without rewriting prior programme lineage.

**MEASURED:** The composed fixture half-width is `0.000009 mm`. Its RCS-023 geometric decision is eligible, but the programme-facing STEP state is still `interoperability_unqualified` because Layer D is inherited from RCS-022.

**INFERENCE:** Provider capability predicates should dispatch forward from immutable journal/lineage authority; they must not own that authority. A provider transition may replace every backend topology object without changing durable body meaning.

## Mill exact to directional fallback to B-rep

**SOURCE:** RCS-021 measured `retrace-jitter` sequential material volume as `11490.990137750125 mm³` and found the 0.25 mm directional refinement within its declared material-volume budget. It did not qualify arbitrary non-orthogonal/five-axis tool orientation.

**MEASURED:** RCS-025 carries the same durable body through `mill-segment-sweep@rcs-011` → `directional-material-field@rcs-021` → `conventional-engineering-brep@rcs-005`. While directional, the state is `bounded_representation_inexact`; after independent provenance-assisted reconstruction the final B-rep path carries a `0.000026 mm` conservative bound.

**MEASURED:** The campaign has an adversarial guard proving the 0.25 mm fallback representation bound cannot simply be cancelled. Reconciliation succeeds only through an explicit independent reconstruction rule: regenerate conventional B-rep from canonical intent plus material/provenance evidence, validate it, and add the new reconciliation bound to the continuing error trace.

**INFERENCE:** Reconciliation is a replacement-and-validation boundary, not a numerical forgiveness boundary. It can discharge an obsolete representation bound only when the replacement state is independently justified from programme authority and the replacement introduces its own bounded error contribution.

## Repeated defer and reconciliation policy

**MEASURED:** On an identical eight-operation history, hard semantic/query boundaries produce peak pending state `4`, `2` reconciliations and `26` deterministic work units. Adding a pending threshold of `2` produces peak pending state `2`, `4` reconciliations and `36` work units.

**MEASURED:** On a 64-operation growth probe with no intervening hard query, hard-only policy reaches `64` pending units while the threshold policy stays at `2`.

**INFERENCE:** Hard correctness boundaries are necessary but do not bound deferred resource growth. The coordinator contract therefore requires an additional finite resource guard. The exact threshold is implementation-tunable and may be based on size, estimated cost, elapsed work, query pressure, or a combination; it must be explicit, observable and must not weaken semantic boundaries.

## Split/merge while pending

**MEASURED:** A connectivity query made with three pending units returns `accepted_pending` and `BODY_CONNECTIVITY_PENDING`; body selection is prohibited until reconciliation. After reconciliation, one durable body explicitly becomes `body-left` + `body-right`; after another pending/reconcile cycle those two inputs explicitly merge to `body-merged`.

**INFERENCE:** Any operation whose meaning depends on current connectivity/body selection is a hard reconciliation boundary. It is unsafe to guess a body set from stale B-rep topology while deferred material state exists.

## Regenerated topology and lineage ambiguity

**MEASURED:** Three provider regeneration cycles produce four distinct backend topology identifiers while durable `body-main` remains stable and every regeneration is recorded as a lineage event.

**MEASURED:** A deliberately ambiguous mapping produces `accepted_pending` / `LINEAGE_MAPPING_AMBIGUOUS` with silent mapping forbidden.

**INFERENCE:** This strengthens DR-0011 and RCS-024: backend TopoDS/BRepGraph/provider identifiers may optimize or diagnose one worker generation, but programme identity must be journal/body/lineage-owned. Ambiguity is an engineering status, not permission to guess.

## Undo/replay across providers

**MEASURED:** A lathe → generic → pending freehand fallback → reconciled B-rep chain is undone to the generic stage, provider-private state is discarded, and the accepted dispatch sequence is replayed. The programme-level replay signature is identical before and after rebuild.

**INFERENCE:** Durable replay needs operation/status/body/lineage authority and stable provider capability rules. It does not require serialized kernel object graphs or bitwise B-rep identity.

## Propagated error-budget controls

**MEASURED:** A conservative path finishing at `0.000016 mm` is geometrically eligible under the declared `0.00005 mm` RCS-023 budget; overall STEP remains `interoperability_unqualified`. A `0.000066 mm` path fails as `error_budget_breach`. No tolerance widening is permitted.

**MEASURED:** An explicit positive `0.000001 mm` removal under ±`0.00001 mm` uncertainty remains `accepted_pending` with positive intent preserved, rather than becoming no material change.

**INFERENCE:** Provider transitions and reconciliation must extend the same programme-level budget trace. A provider boundary cannot reset accumulated uncertainty, and an exporter cannot silently reinterpret an error-budget breach as manufacturing tolerance.

## Curved/non-orthogonal fallback boundary

**SOURCE:** RCS-021 supports a constant-Z ball/rounded fixture only within its declared material-volume budget and does not qualify arbitrary tool-axis rotation/five-axis fallback.

**MEASURED:** The RCS-025 capability record therefore marks arbitrary non-orthogonal tool-axis fallback `refused_unsupported`; the constant-Z rounded case remains a bounded candidate only. No fabricated curved/five-axis success is introduced to satisfy the RCS-025 scenario list.

## STEP eligibility

**SOURCE:** RCS-022's independent parser/import work did not qualify its downstream Layer-D metric path; the profile is `interoperability_unqualified`.

**MEASURED:** RCS-025 emits STEP status only after conventional B-rep reconciliation and a passing propagated geometric budget. Even then, the programme-facing status remains `interoperability_unqualified`. Pending directional state and budget-breached state cannot become STEP success.

## Resource evidence boundary

**MEASURED:** Pending-state size, reconciliation frequency and deterministic work cost are part of the frozen evidence and directly compare the two policies.

**OPEN:** Wall-clock latency distributions, peak/long-run RSS, process/handle leakage, platform differences and long soak behavior are not RCS-025 acceptance evidence. RCS-026 explicitly owns Windows/Linux scale, soak and fault-recovery qualification.

## Architecture consequences for Gate 5

**INFERENCE:** Retain the semantic-provider hybrid, refined by the following coordinator rules:

1. durable body/revision/operation/lineage identity is provider-independent;
2. provider-private topology/history IDs never enter durable authority;
3. exact topology/connectivity/export queries are mandatory hard reconciliation boundaries;
4. a separate finite deferred-state resource guard is required in addition to hard boundaries;
5. ambiguous lineage/body mapping returns pending/refusal rather than a guessed mapping;
6. fallback-to-B-rep replacement must be provenance-backed and independently validated, never implemented as error cancellation;
7. RCS-023 error budgets continue across every conversion/reconciliation;
8. STEP can originate only from reconciled conventional engineering B-rep and retains RCS-022's Layer-D truth state;
9. OCCT 8.0.1 process isolation remains the reference backend boundary pending later explicit supersession.

These conclusions are recorded as DR-0022. RCS-026 must now determine whether the same rules remain bounded and deterministic on Windows/Linux and at substantially larger/longer workloads.
