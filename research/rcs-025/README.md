# RCS-025 — provider handoff, deferred-state and reconciliation stress

Issue: RCS-025 / #44  
Evidence schema: `rcs-025-handoff-stress-evidence/1.0`  
Plan: `experiment-plan-v1.json`  
Frozen deterministic result: `reference-results-v1.json`

## Purpose and scope

RCS-025 tests the seams of the accepted semantic-provider hybrid rather than re-running provider qualification. It composes the durable-authority vocabulary and identity guard from RCS-018 with the conservative propagated-error model from RCS-023, while consuming the accepted capability boundaries of RCS-020, RCS-021, RCS-022 and RCS-024.

This is a deterministic research adapter, not a production scheduler and not a new geometry-kernel benchmark. Geometry values used in the stress fixtures are inherited from accepted predecessor evidence or explicitly labelled synthetic contract fixtures. Backend topology identifiers exist only in diagnostic fields and are never admitted to durable programme state.

## Predeclared hypotheses

The versioned plan records six falsifiable hypotheses before the frozen evidence run: durable lineage must survive provider regeneration; bounded fallback must remain non-STEP-authoritative until independent B-rep reconstruction; finite pending thresholds must bound pending-state growth; connectivity decisions must block while pending; mixed-provider replay must survive provider-private state loss; and RCS-023 error budgets must cross handoffs without reset or tolerance widening.

## Deterministic stress result

The frozen campaign records seven executable scenarios plus the explicit non-orthogonal fallback refusal control. All declared contract checks pass in the reference result.

### Lathe → generic/exact handoff

A qualified RCS-020-style axisymmetric lathe state transitions to the generic exact B-rep control when a deliberately non-axisymmetric operation leaves the lathe predicate. Durable `body-main` and the operation lineage remain programme-owned while the diagnostic backend topology identity changes. The composed geometric half-width is `0.000009 mm`, within the research export budget, but the STEP state remains `interoperability_unqualified` because RCS-022 Layer D is not qualified.

### Mill exact → bounded fallback → B-rep

The campaign uses the RCS-021 `retrace-jitter` material result (`11490.990137750125 mm³`) to exercise exact mill → directional material field → conventional B-rep. The directional state is `bounded_representation_inexact` and cannot be supplied directly to STEP. Its `0.25 mm` representation bound is not numerically cancelled during reconciliation: the conventional B-rep is modelled as an independent reconstruction from canonical intent plus material/provenance evidence and receives a fresh `0.00002 mm` reconciliation-validation contribution. The resulting conservative path bound is `0.000026 mm`.

The scope remains narrow. Arbitrary non-orthogonal/rotated tool-axis fallback is `refused_unsupported`. The RCS-021 constant-Z ball/rounded case is recorded only as a volume-budget-supported candidate, not promoted to general curved/five-axis capability.

### Repeated defer/reconcile policies

On the same eight-operation deterministic history:

- hard semantic/query boundaries only: peak pending state `4` units, `2` reconciliations, `26` work units;
- hard boundaries plus pending threshold `2`: peak pending state `2` units, `4` reconciliations, `36` work units.

A 64-operation growth probe makes the resource tradeoff explicit: hard-only pending state reaches `64` units, while the threshold policy remains bounded at `2`. This is evidence for a finite resource guard in addition to mandatory semantic/query boundaries. The value `2` is a stress-fixture control, not a frozen production tuning value.

### Split/merge while pending

A connectivity/body-selection query against three units of pending fallback state returns `accepted_pending` / `BODY_CONNECTIVITY_PENDING`; body selection is not permitted. After reconciliation the durable body explicitly splits into `body-left` and `body-right`, later reconciles again, and explicitly merges to `body-merged`. No body is silently discarded and both lineage events are retained.

### Regenerated topology and ambiguity

Three reconstruction cycles replace diagnostic backend topology identities while the durable body ID remains `body-main`. A deliberately ambiguous mapping control returns `accepted_pending` / `LINEAGE_MAPPING_AMBIGUOUS` with `silent_mapping_permitted=false`. This directly preserves DR-0011 and the RCS-024 BRepGraph boundary: backend graph/topology identity may help inside a worker, never define programme identity.

### Undo/replay across provider changes

A mixed provider chain—lathe, generic exact, pending freehand fallback, reconciled B-rep—is replayed after undo to the generic operation and simulated loss of provider-private state. The before/after programme-level replay signatures are identical. The comparison covers statuses, providers, body IDs, lineage and the declared material invariant rather than requiring bitwise B-rep identity.

### Error-budget controls

The within-budget handoff finishes at `0.000016 mm` and is geometrically export-eligible under RCS-023, while the overall STEP state remains `interoperability_unqualified`. A `0.000066 mm` path exceeds the `0.00005 mm` geometric budget and fails closed as `error_budget_breach`. A positive `0.000001 mm` removal under ±`0.00001 mm` uncertainty remains `accepted_pending` with positive intent preserved; it is never converted to no material change.

## Reconciliation/resource policy result

Hard semantic boundaries are mandatory before operations whose correctness depends on exact topology/connectivity/export state. They are insufficient as the only resource policy because deferred state can grow with the distance to such a boundary. The architecture therefore needs an additional finite resource threshold (size/time/cost or equivalent), with the threshold value implementation-tunable but observable and deterministic for a given configuration.

Reconciliation cannot be used as an error-budget reset. If an approximate/deferred representation is replaced by independently reconstructed and validated engineering state, the old representation bound is discharged by provenance-backed replacement, not subtraction or presumed cancellation; the new reconciliation/validation contribution enters the continuing RCS-023 trace.

## STEP and interoperability truth

Every path reaches STEP only from reconciled conventional B-rep state. Passing the RCS-023 geometric budget does not upgrade RCS-022 Layer D. The profile remains `occt-8.0.1-ap242dis` and the programme-facing status remains `interoperability_unqualified` until an independent downstream metric path is qualified.

## Resource measurement boundary

RCS-025 makes policy growth and reconciliation cost reproducible using pending-state and deterministic work-unit proxies. Wall-clock latency distributions, long-run RSS/memory growth, Windows/MSVC behavior and worker lifecycle leakage are intentionally deferred to RCS-026, whose purpose is platform/scale/soak qualification. Those omitted metrics are not silently treated as passing evidence here.

## Reproduction

```bash
python3 tools/validate_rcs025.py
python3 -m py_compile research/rcs-025/*.py
python3 -m unittest discover -v -s research/rcs-025 -p 'test_*.py'
python3 research/rcs-025/run_campaign.py \
  --out-dir .results/rcs025 \
  --compare-reference research/rcs-025/reference-results-v1.json
python3 tools/validate_rcs025.py --results-dir .results/rcs025
```

## Gate-5 impact

The stress evidence supports retaining the semantic-provider hybrid with a refined coordinator contract: programme-owned lineage/body authority, mandatory hard reconciliation boundaries, a finite deferred-state resource guard, fail-closed ambiguity/connectivity behavior, conservative propagated budgets, and STEP only from reconciled B-rep. RCS-026 remains responsible for proving that these rules remain deterministic and operationally contained across Windows/Linux and larger/long-running workloads.
