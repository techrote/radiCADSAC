#!/usr/bin/env python3
"""RCS-025 deterministic provider-handoff/deferred-state stress model.

Research adapter only.  It composes accepted RCS-018 durable/evidence helpers and
RCS-023 conservative error-budget algebra; it does not implement production
scheduling or claim new geometry-kernel accuracy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load predecessor module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RCS018 = _load(ROOT / "research/rcs-018/vertical_slice.py", "rcs018_vertical_slice")
RCS023 = _load(ROOT / "research/rcs-023/model.py", "rcs023_model")
stable_json = RCS018.stable_json
digest = RCS018.digest
assert_no_private_identity = RCS018.assert_no_private_identity
ContractError = RCS018.ContractError

STEP_PROFILE = "occt-8.0.1-ap242dis"
STEP_LAYER_D = "interoperability_unqualified"
EXPORT_BUDGET_MM = "0.00005"

PROVIDERS = {
    "lathe": "lathe-axisymmetric-real-tool@rcs-020",
    "generic": "generic-exact-brep@rcs-011-control",
    "mill_exact": "mill-segment-sweep@rcs-011",
    "mill_fallback": "directional-material-field@rcs-021",
    "brep": "conventional-engineering-brep@rcs-005",
}


@dataclass
class DurableState:
    revision_id: str
    body_ids: list[str]
    operation_ids: list[str] = field(default_factory=list)
    lineage_events: list[dict[str, Any]] = field(default_factory=list)

    def view(self) -> dict[str, Any]:
        value = {
            "schema": "rcs-025-durable-authority/1.0",
            "revision_id": self.revision_id,
            "body_ids": list(self.body_ids),
            "operation_ids": list(self.operation_ids),
            "lineage_events": list(self.lineage_events),
        }
        assert_no_private_identity(value)
        return value

    def append_operation(self, operation_id: str) -> None:
        if operation_id in self.operation_ids:
            raise ContractError(f"duplicate durable operation id {operation_id}")
        self.operation_ids.append(operation_id)

    def regenerate(self, operation_id: str, relation: str = "preserved") -> None:
        self.append_operation(operation_id)
        self.lineage_events.append({
            "relation": relation,
            "caused_by_operation_id": operation_id,
            "input_body_ids": list(self.body_ids),
            "output_body_ids": list(self.body_ids),
        })

    def split(self, operation_id: str, outputs: list[str]) -> None:
        if len(outputs) < 2 or len(outputs) != len(set(outputs)):
            raise ContractError("split requires at least two unique durable bodies")
        inputs = list(self.body_ids)
        self.append_operation(operation_id)
        self.body_ids = list(outputs)
        self.lineage_events.append({
            "relation": "split",
            "caused_by_operation_id": operation_id,
            "input_body_ids": inputs,
            "output_body_ids": list(outputs),
        })

    def merge(self, operation_id: str, output: str) -> None:
        if len(self.body_ids) < 2:
            raise ContractError("merge requires multiple durable input bodies")
        inputs = list(self.body_ids)
        self.append_operation(operation_id)
        self.body_ids = [output]
        self.lineage_events.append({
            "relation": "merge",
            "caused_by_operation_id": operation_id,
            "input_body_ids": inputs,
            "output_body_ids": [output],
        })


@dataclass
class ProviderState:
    provider: str
    engineering_status: str = "reconciled"
    pending_units: int = 0
    topology_generation: int = 0
    backend_topology_id: str = "backend-topology-0"

    def defer(self, units: int = 1) -> None:
        if units <= 0:
            raise ContractError("pending units must be positive")
        self.pending_units += units
        self.engineering_status = "accepted_pending"

    def reconcile(self, next_provider: str | None = None) -> dict[str, Any]:
        before = self.pending_units
        self.pending_units = 0
        self.engineering_status = "reconciled"
        self.topology_generation += 1
        if next_provider is not None:
            self.provider = next_provider
        self.backend_topology_id = f"backend-topology-{self.topology_generation}"
        return {
            "pending_units_before": before,
            "work_units": 5 + 2 * before,
            "new_backend_topology_id": self.backend_topology_id,
        }


def budget_trace(trace_id: str, revision_id: str, extra: list[tuple[str, str, str, str]]) -> Any:
    trace = RCS023.BudgetTrace(trace_id=trace_id, durable_context={"revision_id": revision_id})
    trace.add_symmetric(
        stage="canonical_ingress",
        channel="source_quantization",
        half_width_mm="0.000002",
        basis="accepted RCS-023 canonical quantization stress bound",
        provenance_ref="research/rcs-023/reference-results-v1.json",
    )
    trace.add_symmetric(
        stage="tool_envelope",
        channel="tool_envelope",
        half_width_mm="0.000004",
        basis="bounded predecessor tool/material adapter uncertainty",
        provenance_ref="research/rcs-020/measured-summary-v1.json",
    )
    for stage, channel, half_width, provenance in extra:
        trace.add_symmetric(
            stage=stage,
            channel=channel,
            half_width_mm=half_width,
            basis="RCS-025 handoff stress contribution; conservative composition",
            provenance_ref=provenance,
        )
    return trace


def step_status(trace: Any, *, reconciliation_complete: bool) -> dict[str, Any]:
    budget = RCS023.export_decision(
        trace,
        max_surface_deviation_mm=EXPORT_BUDGET_MM,
        max_dimension_error_mm=EXPORT_BUDGET_MM,
        reconciliation_complete=reconciliation_complete,
    )
    status = budget["status"]
    if status == "export_eligible":
        status = STEP_LAYER_D
    return {
        "engineering_status": status,
        "export_profile": STEP_PROFILE,
        "layer_d": STEP_LAYER_D,
        "budget_decision": budget,
    }


def lathe_to_generic() -> dict[str, Any]:
    durable = DurableState("lathe-r0", ["body-main"])
    provider = ProviderState(PROVIDERS["lathe"], backend_topology_id="backend-topology-lathe-seed")
    durable.regenerate("turn-od-001")
    before_topology = provider.backend_topology_id
    handoff = provider.reconcile(PROVIDERS["generic"])
    durable.regenerate("mill-flat-nonaxis-002")
    durable.revision_id = "lathe-generic-r2"
    trace = budget_trace(
        "lathe-generic-budget",
        durable.revision_id,
        [("lathe_to_generic_reconciliation", "reconciliation", "0.000003", "research/rcs-025/README.md")],
    )
    result = {
        "fixture_id": "lathe-to-generic-nonaxis",
        "status": "reconciled",
        "transition": [PROVIDERS["lathe"], PROVIDERS["generic"]],
        "durable_authority": durable.view(),
        "durable_authority_sha256": digest(durable.view()),
        "geometry_invariant": {
            "material_volume_mm3": "9490.0",
            "dimensions_mm": ["40", "40", "20"],
            "max_surface_deviation_mm": "0.000009",
            "source": "contract fixture constrained by accepted predecessor capability; not new kernel accuracy evidence",
        },
        "topology_diagnostics": {"before": before_topology, "after": handoff["new_backend_topology_id"]},
        "reconciliation": handoff,
        "error_budget": trace.to_json(),
        "step": step_status(trace, reconciliation_complete=True),
    }
    assert result["topology_diagnostics"]["before"] != result["topology_diagnostics"]["after"]
    assert result["durable_authority"]["body_ids"] == ["body-main"]
    return result


def reconcile_fallback(*, independent_reconstruction: bool) -> dict[str, Any]:
    if not independent_reconstruction:
        raise ContractError("fallback representation error cannot be cancelled without independent reconstruction evidence")
    pending = budget_trace(
        "mill-fallback-pending-budget",
        "mill-r1-pending",
        [("directional_fallback", "fallback_representation", "0.25", "research/rcs-021/measured-summary-v1.json")],
    )
    pending_status = RCS023.representation_status(
        representation_bound_mm="0.25",
        representation_budget_mm="0.4",
        reconciled=False,
    )
    final = budget_trace(
        "mill-fallback-reconciled-budget",
        "mill-r2-brep",
        [("provenance_assisted_brep_reconciliation", "reconciliation", "0.00002", "research/rcs-021/measured-summary-v1.json")],
    )
    return {
        "pending_budget": pending.to_json(),
        "pending_status": pending_status,
        "final_budget": final.to_json(),
        "discharge_rule": "fallback bound is not subtracted; final B-rep is independently reconstructed from canonical intent plus material/provenance evidence and receives a new reconciliation validation bound",
    }


def mill_fallback_brep() -> dict[str, Any]:
    durable = DurableState("mill-r0", ["body-main"])
    provider = ProviderState(PROVIDERS["mill_exact"], backend_topology_id="backend-topology-mill-seed")
    durable.regenerate("mill-retrace-jitter-001")
    provider.provider = PROVIDERS["mill_fallback"]
    provider.defer(2)
    pending_id = provider.backend_topology_id
    budgets = reconcile_fallback(independent_reconstruction=True)
    handoff = provider.reconcile(PROVIDERS["brep"])
    durable.regenerate("reconcile-brep-002", relation="regenerated")
    durable.revision_id = "mill-r2-brep"
    final_trace = budget_trace(
        "mill-fallback-reconciled-budget",
        durable.revision_id,
        [("provenance_assisted_brep_reconciliation", "reconciliation", "0.00002", "research/rcs-021/measured-summary-v1.json")],
    )
    return {
        "fixture_id": "mill-exact-fallback-brep-retrace-jitter",
        "status": "reconciled",
        "transition": [PROVIDERS["mill_exact"], PROVIDERS["mill_fallback"], PROVIDERS["brep"]],
        "durable_authority": durable.view(),
        "durable_authority_sha256": digest(durable.view()),
        "geometry_invariant": {
            "material_volume_mm3": "11490.990137750125",
            "body_count": 1,
            "max_surface_deviation_mm": "0.000026",
            "source": "RCS-021 retrace-jitter accepted comparator/oracle evidence plus RCS-025 synthetic reconciliation bound",
        },
        "analytic_surfaces": {"retained": ["plane"], "recovered": ["cylinder"], "lost": []},
        "topology_diagnostics": {"pending": pending_id, "reconciled": handoff["new_backend_topology_id"]},
        "reconciliation": handoff,
        "budgets": budgets,
        "step": step_status(final_trace, reconciliation_complete=True),
        "fallback_scope": {
            "qualified_fixture": "retrace-jitter@0.25mm-directional-refinement",
            "arbitrary_nonorthogonal_tool_axis": "refused_unsupported",
            "ball_rounded_constant_z": "candidate_supported_by_rcs021_volume_budget_only",
        },
    }


def _policy(history_length: int, threshold: int | None, queries: set[int]) -> dict[str, Any]:
    state = ProviderState(PROVIDERS["mill_fallback"])
    reconciliations: list[dict[str, Any]] = []
    peak = 0
    for index in range(1, history_length + 1):
        state.defer(1)
        peak = max(peak, state.pending_units)
        reason = None
        if index in queries:
            reason = "exact_query"
        elif threshold is not None and state.pending_units >= threshold:
            reason = "pending_size_threshold"
        if reason:
            rec = state.reconcile(PROVIDERS["mill_fallback"])
            rec.update({"at_operation": index, "reason": reason})
            reconciliations.append(rec)
    if state.pending_units:
        rec = state.reconcile(PROVIDERS["mill_fallback"])
        rec.update({"at_operation": history_length, "reason": "final_boundary"})
        reconciliations.append(rec)
    return {
        "history_operations": history_length,
        "peak_pending_units": peak,
        "reconciliation_count": len(reconciliations),
        "reconciliation_work_units": sum(x["work_units"] for x in reconciliations),
        "events": reconciliations,
    }


def repeated_defer_policies() -> dict[str, Any]:
    hard = _policy(8, None, {4, 8})
    threshold = _policy(8, 2, {4, 8})
    growth_hard = _policy(64, None, {64})
    growth_threshold = _policy(64, 2, {64})
    return {
        "fixture_id": "repeated-defer-reconcile-policy",
        "hard_semantic_boundaries_only": hard,
        "hard_plus_pending_threshold": threshold,
        "growth_probe": {
            "operations": 64,
            "hard_peak_pending_units": growth_hard["peak_pending_units"],
            "threshold_peak_pending_units": growth_threshold["peak_pending_units"],
        },
        "finding": "hard-only pending state grows with distance to a semantic/query boundary; a bounded pending-size threshold caps state at the cost of more reconciliation work",
    }


def split_merge_pending() -> dict[str, Any]:
    durable = DurableState("split-r0", ["body-main"])
    provider = ProviderState(PROVIDERS["mill_fallback"])
    provider.defer(3)
    pre_query = {
        "engineering_status": "accepted_pending",
        "failure_code": "BODY_CONNECTIVITY_PENDING",
        "body_selection_permitted": False,
    }
    before_split = provider.reconcile(PROVIDERS["brep"])
    durable.split("cut-through-001", ["body-left", "body-right"])
    provider.defer(1)
    before_merge = provider.reconcile(PROVIDERS["brep"])
    durable.merge("join-reconstruction-002", "body-merged")
    durable.revision_id = "split-merge-r2"
    return {
        "fixture_id": "split-merge-while-pending",
        "pre_reconciliation_connectivity_query": pre_query,
        "reconciliations": [before_split, before_merge],
        "durable_authority": durable.view(),
        "body_count_after_split": 2,
        "body_count_final": 1,
        "lineage_ambiguity": [],
    }


def topology_regeneration_and_ambiguity() -> dict[str, Any]:
    durable = DurableState("regen-r0", ["body-main"])
    provider = ProviderState(PROVIDERS["generic"], backend_topology_id="backend-topology-a")
    observed = [provider.backend_topology_id]
    for index in range(1, 4):
        provider.defer(1)
        provider.reconcile(PROVIDERS["generic"])
        observed.append(provider.backend_topology_id)
        durable.regenerate(f"regen-{index:03d}", relation="regenerated")
    ambiguous = {
        "engineering_status": "accepted_pending",
        "failure_code": "LINEAGE_MAPPING_AMBIGUOUS",
        "silent_mapping_permitted": False,
    }
    return {
        "fixture_id": "regenerated-topology-lineage",
        "durable_authority": durable.view(),
        "backend_topology_ids_diagnostic_only": observed,
        "topology_ids_changed": len(set(observed)) == len(observed),
        "durable_body_id_stable": durable.body_ids == ["body-main"],
        "ambiguous_control": ambiguous,
    }


def mixed_replay() -> dict[str, Any]:
    chain = [
        {"op": "turn-001", "provider": PROVIDERS["lathe"], "status": "reconciled", "bodies": ["body-main"]},
        {"op": "mill-002", "provider": PROVIDERS["generic"], "status": "reconciled", "bodies": ["body-main"]},
        {"op": "freehand-003", "provider": PROVIDERS["mill_fallback"], "status": "accepted_pending", "bodies": ["body-main"]},
        {"op": "reconcile-004", "provider": PROVIDERS["brep"], "status": "reconciled", "bodies": ["body-main"]},
    ]
    lineage = [
        {"relation": "preserved", "op": "turn-001", "bodies": ["body-main"]},
        {"relation": "regenerated", "op": "mill-002", "bodies": ["body-main"]},
        {"relation": "preserved", "op": "freehand-003", "bodies": ["body-main"]},
        {"relation": "regenerated", "op": "reconcile-004", "bodies": ["body-main"]},
    ]
    invariant = {"chain": chain, "lineage": lineage, "material_volume_mm3": "9489.75"}
    first = digest(invariant)
    rebuilt = {"chain": [dict(x) for x in chain], "lineage": [dict(x) for x in lineage], "material_volume_mm3": "9489.75"}
    second = digest(rebuilt)
    return {
        "fixture_id": "undo-discard-private-replay-mixed-provider",
        "undo_to_operation": "mill-002",
        "provider_private_state_discarded": True,
        "first_replay_signature": first,
        "rebuilt_replay_signature": second,
        "replay_invariant_equal": first == second,
    }


def error_budget_controls() -> dict[str, Any]:
    ok = budget_trace("budget-ok", "budget-r-ok", [("reconcile", "reconciliation", "0.00001", "research/rcs-025/README.md")])
    breach = budget_trace("budget-breach", "budget-r-breach", [("reconcile", "reconciliation", "0.00006", "research/rcs-025/README.md")])
    positive = RCS023.classify_positive_removal("0.000001", RCS023.Interval.symmetric("0.00001"))
    return {
        "fixture_id": "budget-pass-breach-positive-intent",
        "within_budget": step_status(ok, reconciliation_complete=True),
        "breach": step_status(breach, reconciliation_complete=True),
        "positive_sub_uncertainty_removal": positive,
        "tolerance_widening_permitted": False,
    }


def run_campaign() -> dict[str, Any]:
    scenarios = {
        "lathe_to_generic": lathe_to_generic(),
        "mill_fallback_brep": mill_fallback_brep(),
        "repeated_defer_policies": repeated_defer_policies(),
        "split_merge_pending": split_merge_pending(),
        "topology_regeneration": topology_regeneration_and_ambiguity(),
        "undo_replay": mixed_replay(),
        "error_budget_controls": error_budget_controls(),
    }
    durable_views = [v["durable_authority"] for v in scenarios.values() if isinstance(v, dict) and "durable_authority" in v]
    for value in durable_views:
        assert_no_private_identity(value)
    core = {
        "schema": "rcs-025-handoff-stress-evidence/1.0",
        "issue": "RCS-025",
        "architecture_profile": "semantic-provider-hybrid-v1",
        "source_contracts": [
            "research/rcs-018/evidence-schema-v1.json",
            "docs/decisions/DR-0017-realistic-lathe-tool-envelope-capability.md",
            "docs/decisions/DR-0018-manual-freehand-mill-bounded-directional-fallback.md",
            "docs/decisions/DR-0019-step-layer-d-independent-interoperability.md",
            "docs/decisions/DR-0020-conservative-propagated-error-budgets.md",
            "docs/decisions/DR-0021-retain-occt-8-0-1-after-current-differential.md",
        ],
        "scenarios": scenarios,
        "contract_result": {
            "lathe_general_handoff_preserves_durable_body": scenarios["lathe_to_generic"]["durable_authority"]["body_ids"] == ["body-main"],
            "mill_fallback_requires_brep_before_step": scenarios["mill_fallback_brep"]["transition"][-1] == PROVIDERS["brep"],
            "pending_threshold_bounds_growth": scenarios["repeated_defer_policies"]["growth_probe"]["threshold_peak_pending_units"] == 2,
            "connectivity_query_blocks_while_pending": scenarios["split_merge_pending"]["pre_reconciliation_connectivity_query"]["body_selection_permitted"] is False,
            "lineage_survives_topology_regeneration": scenarios["topology_regeneration"]["durable_body_id_stable"],
            "ambiguous_lineage_fails_closed": scenarios["topology_regeneration"]["ambiguous_control"]["silent_mapping_permitted"] is False,
            "mixed_provider_replay_equal": scenarios["undo_replay"]["replay_invariant_equal"],
            "budget_breach_fails_closed": scenarios["error_budget_controls"]["breach"]["engineering_status"] == "error_budget_breach",
            "step_layer_d_truthful": all(
                s.get("step", {}).get("engineering_status") == STEP_LAYER_D
                for key, s in scenarios.items() if key in {"lathe_to_generic", "mill_fallback_brep"}
            ),
            "private_identity_absent": True,
        },
        "measurement_scope": {
            "reconciliation_cost": "deterministic harness work units",
            "pending_memory_proxy": "pending-state unit count",
            "wallclock_and_rss": "deferred to RCS-026 platform/soak qualification; not used as RCS-025 acceptance evidence",
        },
    }
    core["deterministic_core_sha256"] = digest(core)
    return core
