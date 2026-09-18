#!/usr/bin/env python3
"""Validate RCS-023 propagated uncertainty/error-budget research.

This validator deliberately checks semantic failure modes, not merely JSON shape:
- policy/requirement channels cannot become numerical error;
- ambiguity at contact boundaries remains pending;
- explicit positive removal cannot become a no-op;
- correlated errors cannot use RSS as authority without evidence;
- provider handoff must retain source + conversion + destination budgets;
- fallback state must reconcile before STEP/export success;
- unknown or over-budget reconciliation fails closed;
- durable evidence must remain representation/provider neutral.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/rcs-023"
PLAN = BASE / "experiment-plan-v1.json"
MODEL = BASE / "model.py"
RUN = BASE / "run_campaign.py"
TESTS = BASE / "test_model.py"
REFERENCE = BASE / "reference-results-v1.json"
README = BASE / "README.md"
REPORT = ROOT / "docs/31-PROPAGATED-UNCERTAINTY-ERROR-BUDGET-ALGEBRA.md"
DECISION = ROOT / "docs/decisions/DR-0020-conservative-propagated-error-budgets.md"
WORKFLOW = ROOT / ".github/workflows/rcs023.yml"

EXPECTED_COMPOSABLE = {
    "source_quantization",
    "trajectory_fit",
    "frame_translation",
    "frame_rotation",
    "tool_envelope",
    "numerical_algorithm",
    "fallback_representation",
    "reconciliation",
}
EXPECTED_POLICIES = {
    "manufacturing_requirement",
    "contact_policy",
    "export_validation",
}
EXPECTED_STATUSES = {
    "decisively_no_material_change",
    "decisively_positive_material_change",
    "bounded_representation_inexact",
    "accepted_pending",
    "error_budget_breach",
    "refused_accuracy_unproven",
    "export_eligible",
}
EXPECTED_CASES = {
    "lathe-full-pipeline",
    "mill-fallback-full-pipeline",
    "contact-boundary-sweep",
    "positive-removal-1nm-under-5nm-uncertainty",
    "repeated-correlated-chain",
    "provider-handoff-separate-budgets",
    "order-sensitive-transform-chain",
    "reconciliation-proves-final-bound",
    "reconciliation-budget-breach",
    "reconciliation-unknown-refusal",
    "semantic-exact-retrace",
}
EXPECTED_CHECKS = {
    "contact_boundaries_preserve_ambiguity",
    "correlated_rss_counterexample",
    "fallback_is_inexact_before_brep",
    "handoff_budgets_are_additive",
    "lathe_and_mill_full_traces",
    "order_sensitive_counterexample",
    "reconciliation_fail_closed",
    "semantic_retrace_requires_proof",
    "sub_tolerance_positive_intent_preserved",
}

errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}")
        return None


def decimal_text(value: Any, expected: str, label: str) -> None:
    require(str(value) == expected, f"{label}: expected {expected!r}, got {value!r}")


def validate_plan(plan: Any) -> None:
    require(isinstance(plan, dict), "experiment plan must be a JSON object")
    if not isinstance(plan, dict):
        return
    require(plan.get("schema") == "rcs-023-uncertainty-plan/1.0", "unexpected plan schema")
    require(plan.get("issue") == "RCS-023" and plan.get("issue_number") == 42, "plan must bind RCS-023/#42")
    require(plan.get("model_version") == "rcs-uncertainty-budget/1.0", "model version drift")

    deps = set(plan.get("dependencies", []))
    for dep in {"RCS-002", "RCS-005", "RCS-007", "RCS-008", "RCS-009", "RCS-012"}:
        require(dep in deps, f"missing declared dependency {dep}")

    channels = plan.get("channel_model", {})
    require(set(channels.get("composable_error_channels", [])) == EXPECTED_COMPOSABLE,
            "composable error-channel set drifted")
    require(set(channels.get("non_error_policy_channels", [])) == EXPECTED_POLICIES,
            "non-error policy/requirement-channel set drifted")
    rule = str(channels.get("rule", "")).lower()
    require("forbidden" in rule and "numerically" in rule,
            "plan must forbid treating policy/requirement channels as numerical error")

    composition = plan.get("composition", {})
    require("conservative" in str(composition.get("default", "")).lower(),
            "default composition must remain conservative")
    require("independence" in str(composition.get("rss_rule", "")).lower(),
            "RSS rule must require independence evidence")
    require("shared" in str(composition.get("cancellation_rule", "")).lower(),
            "cancellation rule must require shared-source proof")
    require("refusal" in str(composition.get("unknown_rule", "")).lower(),
            "unknown required error must fail closed")

    status_contract = plan.get("status_contract", {})
    require(set(status_contract) == EXPECTED_STATUSES, "status contract set drifted")

    hyps = plan.get("hypotheses", [])
    require(isinstance(hyps, list) and len(hyps) >= 6, "at least six falsifiable hypotheses required")
    if isinstance(hyps, list):
        for hyp in hyps:
            require(isinstance(hyp, dict) and hyp.get("id") and hyp.get("statement") and hyp.get("falsified_by"),
                    "each hypothesis must include id, statement and falsification criterion")

    require(set(plan.get("cases", [])) == EXPECTED_CASES, "required case set drifted")
    stages = plan.get("required_pipeline_stages", [])
    require(len(stages) >= 8, "complete canonical-to-STEP propagation path is required")
    rcs005 = plan.get("rcs005_mapping", {})
    for field in (
        "max_dimension_error_nm",
        "max_surface_deviation_nm",
        "max_angular_error_nrad",
        "max_volume_error_abs_mm3",
        "max_volume_error_rel",
    ):
        require(field in rcs005.get("geometric_fields", []), f"RCS-005 mapping missing {field}")
    require("provider-private" in str(plan.get("provenance_rule", "")).lower(),
            "plan must explicitly reject provider-private durable identity")


def validate_reference(result: Any, *, label: str) -> None:
    require(isinstance(result, dict), f"{label}: result must be an object")
    if not isinstance(result, dict):
        return
    require(result.get("schema") == "rcs-023-campaign-results/1.0", f"{label}: campaign schema drift")
    require(result.get("plan_schema") == "rcs-023-uncertainty-plan/1.0", f"{label}: plan binding drift")
    require(result.get("model_version") == "rcs-uncertainty-budget/1.0", f"{label}: model binding drift")
    require(result.get("composition_default") == "conservative_interval_minkowski_sum",
            f"{label}: conservative composition drift")
    require(result.get("all_required_checks_pass") is True, f"{label}: required checks must all pass")

    checks = result.get("required_checks", {})
    require(set(checks) == EXPECTED_CHECKS, f"{label}: required-check set drift")
    for key in EXPECTED_CHECKS:
        require(checks.get(key) is True, f"{label}: required check failed: {key}")
    require(set(result.get("observed_statuses", [])) == EXPECTED_STATUSES,
            f"{label}: campaign must exercise every contract status")

    pipelines = {p.get("case_id"): p for p in result.get("pipelines", []) if isinstance(p, dict)}
    require(set(pipelines) == {"lathe-full-pipeline", "mill-fallback-full-pipeline"},
            f"{label}: representative lathe/mill pipelines missing")
    lathe = pipelines.get("lathe-full-pipeline", {})
    mill = pipelines.get("mill-fallback-full-pipeline", {})
    decimal_text(lathe.get("final", {}).get("final_max_abs_mm"), "0.0000145", f"{label}: lathe final bound")
    require(lathe.get("final", {}).get("status") == "export_eligible", f"{label}: lathe should fit 20 nm budget")
    decimal_text(mill.get("final", {}).get("final_max_abs_mm"), "0.0000175", f"{label}: mill final bound")
    require(mill.get("fallback_state_before_reconciliation") == "bounded_representation_inexact",
            f"{label}: mill fallback must remain representation-inexact before B-rep reconciliation")
    require(mill.get("final", {}).get("status") == "export_eligible", f"{label}: reconciled mill should fit 20 nm budget")

    for pipeline_name, pipeline in pipelines.items():
        trace = pipeline.get("trace", {})
        require(trace.get("unresolved") == [], f"{label}: {pipeline_name} full trace cannot carry unresolved errors")
        context = json.dumps(trace.get("durable_context", {}), sort_keys=True).lower()
        for forbidden in ("topods", "kernel_handle", "provider_private", "process_id", "pointer"):
            require(forbidden not in context, f"{label}: provider-private identity leaked into {pipeline_name} durable context")
        channels = [s.get("channel") for s in trace.get("stages", []) if isinstance(s, dict)]
        require(set(channels).issubset(EXPECTED_COMPOSABLE), f"{label}: unknown/policy channel was numerically composed")
        require("reconciliation" in channels, f"{label}: full trace must include B-rep reconciliation")

    contact = result.get("contact_sweep", {})
    members = {m.get("nominal_signed_gap_mm"): m for m in contact.get("members", []) if isinstance(m, dict)}
    require(members.get("-0.000020", {}).get("status") == "decisively_positive_material_change",
            f"{label}: strictly overlapping contact member must be decisive positive")
    require(members.get("0.000020", {}).get("status") == "decisively_no_material_change",
            f"{label}: strictly clear contact member must be decisive no-change")
    for boundary in ("-0.000010", "0", "0.000010"):
        require(members.get(boundary, {}).get("status") == "accepted_pending",
                f"{label}: contact interval touching zero must remain pending at {boundary}")

    positive = result.get("sub_tolerance_positive", {})
    require(positive.get("status") == "accepted_pending", f"{label}: 1 nm positive removal must remain pending under 5 nm uncertainty")
    require(positive.get("commanded_positive_intent_preserved") is True,
            f"{label}: positive removal intent was erased")
    decimal_text(positive.get("commanded_depth_mm"), "0.000001", f"{label}: positive-removal depth")
    decimal_text(positive.get("uncertainty", {}).get("max_abs_mm"), "0.000005", f"{label}: positive-removal uncertainty")

    corr = result.get("repeated_correlated", {})
    decimal_text(corr.get("conservative_unknown_correlation_half_width_mm"), "0.0001", f"{label}: correlated conservative bound")
    decimal_text(corr.get("rss_diagnostic_half_width_mm"), "0.00001", f"{label}: RSS diagnostic")
    require(corr.get("rss_underbounds_witness") is True, f"{label}: RSS counterexample must underbound systematic witness")
    decimal_text(corr.get("proven_same_source_pair_cancellation_half_width_mm"), "0", f"{label}: proven same-source cancellation")

    handoff = result.get("provider_handoff", {})
    decimal_text(handoff.get("conservative_handoff", {}).get("max_abs_mm"), "0.000018", f"{label}: provider handoff bound")
    decimal_text(handoff.get("unsafe_naive_max_only_mm"), "0.000008", f"{label}: unsafe max-only handoff")
    require(handoff.get("naive_max_understates_bound") is True, f"{label}: provider-handoff undercount control failed")

    order = result.get("order_sensitive", {})
    require(order.get("different") is True, f"{label}: order-sensitive counterexample disappeared")
    decimal_text(order.get("large-before_gain_final_half_width_mm"), "0.000045", f"{label}: large-before-gain bound")
    decimal_text(order.get("small-before_gain_final_half_width_mm"), "0.00003", f"{label}: small-before-gain bound")

    reconciliation = {r.get("case_id"): r for r in result.get("reconciliation", []) if isinstance(r, dict)}
    require(reconciliation.get("reconciliation-proves-final-bound", {}).get("final", {}).get("status") == "export_eligible",
            f"{label}: bounded reconciliation pass should be export eligible")
    require(reconciliation.get("reconciliation-budget-breach", {}).get("final", {}).get("status") == "error_budget_breach",
            f"{label}: over-budget reconciliation must breach")
    unknown = reconciliation.get("reconciliation-unknown-refusal", {}).get("final", {})
    require(unknown.get("status") == "refused_accuracy_unproven" and unknown.get("reconciliation_complete") is False,
            f"{label}: unmeasured reconciliation must fail closed")
    require(bool(unknown.get("unresolved")), f"{label}: unknown reconciliation must retain explicit unresolved reason")

    retrace = result.get("semantic_retrace", {})
    require(retrace.get("status") == "decisively_no_material_change" and "provenance" in str(retrace.get("proof", "")),
            f"{label}: semantic retrace requires durable proof")


def validate_static() -> tuple[Any, Any]:
    paths = [PLAN, MODEL, RUN, TESTS, REFERENCE, README, REPORT, DECISION, WORKFLOW]
    for path in paths:
        require(path.exists(), f"missing RCS-023 file: {path.relative_to(ROOT)}")

    plan = load_json(PLAN)
    result = load_json(REFERENCE)
    validate_plan(plan)
    validate_reference(result, label="reference")

    for path in (MODEL, RUN, TESTS):
        if path.exists():
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as exc:
                errors.append(f"{path.relative_to(ROOT)}: syntax error: {exc}")

    marker_sets = {
        MODEL: (
            "COMPOSABLE_ERROR_CHANNELS",
            "NON_ERROR_POLICY_CHANNELS",
            "classify_contact",
            "classify_positive_removal",
            "rss_symmetric",
            "correlated_linear_bound",
            "export_decision",
            "provider_private",
        ),
        RUN: (
            "lathe-full-pipeline",
            "mill-fallback-full-pipeline",
            "positive-removal-1nm-under-5nm-uncertainty",
            "repeated-correlated-chain",
            "provider-handoff-separate-budgets",
            "order-sensitive-transform-chain",
            "reconciliation-unknown-refusal",
        ),
        README: (
            "conservative",
            "accepted_pending",
            "bounded_representation_inexact",
            "RCS-005",
            "RCS-018",
            "RCS-025",
            "Reproduction",
        ),
        REPORT: (
            "Hypotheses",
            "Channel contract",
            "Correlation",
            "Provider handoff",
            "sub-tolerance",
            "RCS-005",
            "RCS-018",
            "RCS-025",
            "provider-private",
        ),
        DECISION: (
            "Status: **accepted**",
            "## Context",
            "## Decision",
            "## Evidence",
            "## Alternatives",
            "## Consequences",
            "## Reversibility",
            "RSS",
            "positive-removal",
        ),
        WORKFLOW: (
            "tools/validate_rcs023.py",
            "test_*.py",
            "research/rcs-023/run_campaign.py",
            "--compare-reference",
        ),
    }
    for path, markers in marker_sets.items():
        if path.exists():
            text = path.read_text(encoding="utf-8")
            for marker in markers:
                require(marker in text, f"{path.relative_to(ROOT)} missing contract marker {marker!r}")
    return plan, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()

    _, reference = validate_static()
    if args.results_dir is not None:
        live_path = args.results_dir / "campaign-results.json"
        require(live_path.exists(), f"runtime campaign result missing: {live_path}")
        live = load_json(live_path) if live_path.exists() else None
        validate_reference(live, label="runtime")
        if isinstance(reference, dict) and isinstance(live, dict):
            require(live == reference, "runtime campaign differs from frozen deterministic reference")

    if errors:
        for err in errors:
            print(f"RCS-023 validation failed: {err}")
        return 1
    print("RCS-023 validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
