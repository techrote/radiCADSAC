#!/usr/bin/env python3
"""Run the deterministic RCS-023 uncertainty/error-budget campaign."""
from __future__ import annotations

import argparse
from decimal import Decimal as D
import json
from pathlib import Path

from model import (
    BudgetTrace,
    Interval,
    affine_pipeline_bound,
    classify_contact,
    classify_positive_removal,
    compose_conservative,
    correlated_linear_bound,
    decimal_text,
    export_decision,
    representation_status,
    rss_symmetric,
    semantic_no_change,
)

SCHEMA = "rcs-023-campaign-results/1.0"
PLAN_SCHEMA = "rcs-023-uncertainty-plan/1.0"


def add_common_front(trace: BudgetTrace, *, radius_mm: str, angle_nrad: str) -> None:
    trace.add_symmetric(stage="canonicalize", channel="source_quantization", half_width_mm="0.0000005", basis="RCS-019 bounded canonicalization residual", provenance_ref="RCS-019")
    trace.add_symmetric(stage="trajectory-fit", channel="trajectory_fit", half_width_mm="0.0000015", basis="declared deterministic path-fit envelope", provenance_ref="fixture:path-fit")
    trace.add_symmetric(stage="frame-translation", channel="frame_translation", half_width_mm="0.0000010", basis="declared setup transform translation bound", provenance_ref="fixture:setup-transform")
    trace.add_rotation_bound(stage="frame-rotation", radius_mm=radius_mm, angle_nrad=angle_nrad, basis="declared setup transform angular bound", provenance_ref="fixture:setup-transform")
    trace.add_symmetric(stage="tool-envelope", channel="tool_envelope", half_width_mm="0.0000020", basis="bounded envelope construction approximation", provenance_ref="fixture:tool-envelope")


def full_pipeline_cases() -> list[dict[str, object]]:
    lathe = BudgetTrace(
        "lathe-full-pipeline",
        {
            "journal_event_id": "lathe-op-17",
            "revision_id": "rev-lathe-4",
            "body_ids": ["body-workpiece-A"],
            "semantic_operation": "turning.external",
            "source_fixture": "rcs020-realistic-envelope-control",
        },
    )
    add_common_front(lathe, radius_mm="100", angle_nrad="5")
    pre_provider = lathe.interval
    contact = classify_contact("-0.000020", pre_provider)
    lathe.add_symmetric(stage="provider-execution", channel="numerical_algorithm", half_width_mm="0.0000030", basis="provider-declared local numerical residual", provenance_ref="RCS-020")
    lathe.add_symmetric(stage="provider-handoff", channel="fallback_representation", half_width_mm="0.0000040", basis="bounded source-to-reconciliation representation conversion", provenance_ref="RCS-012/RCS-020")
    lathe.add_symmetric(stage="brep-reconciliation", channel="reconciliation", half_width_mm="0.0000020", basis="measured/declared fitting and stitching residual", provenance_ref="RCS-005")
    lathe_export = export_decision(lathe, max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=True)

    mill = BudgetTrace(
        "mill-fallback-full-pipeline",
        {
            "journal_event_id": "mill-op-42",
            "revision_id": "rev-mill-9",
            "body_ids": ["body-workpiece-M"],
            "semantic_operation": "milling.general",
            "source_fixture": "rcs021-bounded-directional-fallback",
        },
    )
    add_common_front(mill, radius_mm="50", angle_nrad="10")
    pre_provider_mill = mill.interval
    mill_contact = classify_contact("-0.000012", pre_provider_mill)
    mill.add_symmetric(stage="exact-provider", channel="numerical_algorithm", half_width_mm="0.0000030", basis="provider-local numerical uncertainty", provenance_ref="RCS-011")
    mill.add_symmetric(stage="bounded-fallback", channel="fallback_representation", half_width_mm="0.0000060", basis="directional fallback representation error budget", provenance_ref="RCS-021")
    pre_reconcile_status = representation_status(representation_bound_mm="0.0000060", representation_budget_mm="0.0000100", reconciled=False)
    mill.add_symmetric(stage="brep-reconciliation", channel="reconciliation", half_width_mm="0.0000030", basis="provenance-assisted B-rep fit/stitch bound", provenance_ref="RCS-012/RCS-021")
    mill_export = export_decision(mill, max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=True)

    return [
        {
            "case_id": "lathe-full-pipeline",
            "trace": lathe.to_json(),
            "contact_before_provider": contact,
            "final": lathe_export,
        },
        {
            "case_id": "mill-fallback-full-pipeline",
            "trace": mill.to_json(),
            "contact_before_provider": mill_contact,
            "fallback_state_before_reconciliation": pre_reconcile_status,
            "final": mill_export,
        },
    ]


def contact_sweep() -> dict[str, object]:
    u = Interval.symmetric("0.000010")
    offsets = ["-0.000020", "-0.000010", "-0.000005", "0", "0.000005", "0.000010", "0.000020"]
    members = []
    for offset in offsets:
        members.append({"nominal_signed_gap_mm": offset, **classify_contact(offset, u)})
    return {"case_id": "contact-boundary-sweep", "uncertainty": u.to_json(), "members": members}


def sub_tolerance_positive() -> dict[str, object]:
    uncertainty = Interval.symmetric("0.000005")
    result = classify_positive_removal("0.000001", uncertainty)
    return {
        "case_id": "positive-removal-1nm-under-5nm-uncertainty",
        "manufacturing_tolerance_mm": "0.01",
        "uncertainty": uncertainty.to_json(),
        "commanded_depth_mm": "0.000001",
        **result,
        "assertion": "manufacturing tolerance does not authorize erasing signed positive removal intent",
    }


def repeated_and_correlated() -> dict[str, object]:
    per = D("0.000001")
    count = 100
    conservative = per * count
    rss = rss_symmetric([per] * count, independence_evidence="diagnostic counterexample only; deliberately assume independence to show under-bound against correlated systematic bias")
    actual_same_sign = conservative
    proven_cancel = correlated_linear_bound(per, [1, -1] * 50, shared_source_proof="paired terms are the same bounded calibration source with exact +1/-1 coefficients")
    return {
        "case_id": "repeated-correlated-chain",
        "per_operation_half_width_mm": decimal_text(per),
        "count": count,
        "conservative_unknown_correlation_half_width_mm": decimal_text(conservative),
        "rss_diagnostic_half_width_mm": decimal_text(rss),
        "same_sign_systematic_witness_mm": decimal_text(actual_same_sign),
        "rss_underbounds_witness": actual_same_sign > rss,
        "proven_same_source_pair_cancellation_half_width_mm": decimal_text(proven_cancel),
        "cancellation_rule": "only a proven shared source with known coefficients may cancel; unknown channels remain conservatively summed",
    }


def provider_handoff() -> dict[str, object]:
    source = Interval.symmetric("0.000008")
    conversion = Interval.symmetric("0.000006")
    destination = Interval.symmetric("0.000004")
    final = compose_conservative([source, conversion, destination])
    naive_max = max(source.max_abs_mm, conversion.max_abs_mm, destination.max_abs_mm)
    return {
        "case_id": "provider-handoff-separate-budgets",
        "source_provider_residual": source.to_json(),
        "conversion_residual": conversion.to_json(),
        "destination_provider_residual": destination.to_json(),
        "conservative_handoff": final.to_json(),
        "unsafe_naive_max_only_mm": decimal_text(naive_max),
        "naive_max_understates_bound": naive_max < final.max_abs_mm,
    }


def order_sensitive_counterexample() -> dict[str, object]:
    # Same two local error sources placed at different sensitivities.  Reordering
    # stages changes which error is amplified, so "sum stage epsilons" detached
    # from the transform graph is not sound.
    a_before = affine_pipeline_bound([
        ("large-source-before-gain", "2", "0.000020"),
        ("small-source-after-gain", "1", "0.000005"),
    ])
    b_before = affine_pipeline_bound([
        ("small-source-before-gain", "2", "0.000005"),
        ("large-source-after-gain", "1", "0.000020"),
    ])
    return {
        "case_id": "order-sensitive-transform-chain",
        "large-before_gain_final_half_width_mm": decimal_text(a_before),
        "small-before_gain_final_half_width_mm": decimal_text(b_before),
        "different": a_before != b_before,
        "rule": "propagate each stage through downstream sensitivity; do not detach errors from stage order",
    }


def reconciliation_cases() -> list[dict[str, object]]:
    passing = BudgetTrace("reconcile-pass", {"journal_event_id": "rec-pass", "revision_id": "r1", "body_ids": ["b1"], "semantic_operation": "milling.general"})
    passing.add_symmetric(stage="fallback", channel="fallback_representation", half_width_mm="0.000010", basis="bounded local fallback")
    passing.add_symmetric(stage="fit", channel="reconciliation", half_width_mm="0.000005", basis="bounded B-rep fit")
    pass_decision = export_decision(passing, max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=True)

    breach = BudgetTrace("reconcile-breach", {"journal_event_id": "rec-breach", "revision_id": "r2", "body_ids": ["b2"], "semantic_operation": "milling.general"})
    breach.add_symmetric(stage="fallback", channel="fallback_representation", half_width_mm="0.000018", basis="bounded local fallback")
    breach.add_symmetric(stage="fit", channel="reconciliation", half_width_mm="0.000008", basis="bounded B-rep fit")
    breach_decision = export_decision(breach, max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=True)

    unknown = BudgetTrace("reconcile-unknown", {"journal_event_id": "rec-unknown", "revision_id": "r3", "body_ids": ["b3"], "semantic_operation": "turning.external"})
    unknown.add_symmetric(stage="known", channel="numerical_algorithm", half_width_mm="0.000003", basis="known provider residual")
    unknown.mark_unresolved("destination reconciliation fit has no demonstrated bound")
    unknown_decision = export_decision(unknown, max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=False)
    return [
        {"case_id": "reconciliation-proves-final-bound", "trace": passing.to_json(), "final": pass_decision},
        {"case_id": "reconciliation-budget-breach", "trace": breach.to_json(), "final": breach_decision},
        {"case_id": "reconciliation-unknown-refusal", "trace": unknown.to_json(), "final": unknown_decision},
    ]


def semantic_retrace() -> dict[str, object]:
    return {
        "case_id": "semantic-exact-retrace",
        **semantic_no_change(proof="durable semantic envelope/provenance equality; journal event retained"),
    }


def run() -> dict[str, object]:
    pipelines = full_pipeline_cases()
    contact = contact_sweep()
    sub = sub_tolerance_positive()
    repeated = repeated_and_correlated()
    handoff = provider_handoff()
    order = order_sensitive_counterexample()
    reconciliations = reconciliation_cases()
    retrace = semantic_retrace()

    statuses: set[str] = set()
    for item in pipelines:
        statuses.add(str(item["final"]["status"]))
        statuses.add(str(item["contact_before_provider"]["status"]))
        if "fallback_state_before_reconciliation" in item:
            statuses.add(str(item["fallback_state_before_reconciliation"]))
    statuses.add(str(sub["status"]))
    statuses.add(str(retrace["status"]))
    for member in contact["members"]:
        statuses.add(str(member["status"]))
    for item in reconciliations:
        statuses.add(str(item["final"]["status"]))

    required = {
        "lathe_and_mill_full_traces": len(pipelines) == 2 and all(p["final"]["status"] == "export_eligible" for p in pipelines),
        "fallback_is_inexact_before_brep": pipelines[1]["fallback_state_before_reconciliation"] == "bounded_representation_inexact",
        "sub_tolerance_positive_intent_preserved": sub["status"] == "accepted_pending" and sub["commanded_positive_intent_preserved"] is True,
        "contact_boundaries_preserve_ambiguity": all(m["status"] == "accepted_pending" for m in contact["members"] if m["nominal_signed_gap_mm"] in {"-0.000010", "0", "0.000010"}),
        "correlated_rss_counterexample": repeated["rss_underbounds_witness"] is True,
        "handoff_budgets_are_additive": handoff["naive_max_understates_bound"] is True,
        "order_sensitive_counterexample": order["different"] is True,
        "reconciliation_fail_closed": {r["case_id"]: r["final"]["status"] for r in reconciliations} == {
            "reconciliation-proves-final-bound": "export_eligible",
            "reconciliation-budget-breach": "error_budget_breach",
            "reconciliation-unknown-refusal": "refused_accuracy_unproven",
        },
        "semantic_retrace_requires_proof": retrace["status"] == "decisively_no_material_change",
    }
    return {
        "schema": SCHEMA,
        "plan_schema": PLAN_SCHEMA,
        "model_version": "rcs-uncertainty-budget/1.0",
        "composition_default": "conservative_interval_minkowski_sum",
        "rss_authority": "diagnostic_only_unless_independence_is_explicitly_proven",
        "pipelines": pipelines,
        "contact_sweep": contact,
        "sub_tolerance_positive": sub,
        "repeated_correlated": repeated,
        "provider_handoff": handoff,
        "order_sensitive": order,
        "reconciliation": reconciliations,
        "semantic_retrace": retrace,
        "observed_statuses": sorted(statuses),
        "required_checks": required,
        "all_required_checks_pass": all(required.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path(".results/rcs023"))
    parser.add_argument("--compare-reference", type=Path)
    args = parser.parse_args()
    result = run()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "campaign-results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.compare_reference:
        reference = json.loads(args.compare_reference.read_text(encoding="utf-8"))
        if result != reference:
            raise SystemExit("RCS-023 deterministic result differs from committed reference")
    print(json.dumps({"all_required_checks_pass": result["all_required_checks_pass"], "output": str(out)}, sort_keys=True))
    return 0 if result["all_required_checks_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
