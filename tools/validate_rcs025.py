#!/usr/bin/env python3
"""Static and runtime contract validator for RCS-025."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "research/rcs-025"
REFERENCE = R / "reference-results-v1.json"

REQUIRED = [
    R / "README.md",
    R / "experiment-plan-v1.json",
    R / "stress_model.py",
    R / "run_campaign.py",
    R / "test_stress_model.py",
    REFERENCE,
    ROOT / "docs/33-PROVIDER-HANDOFF-RECONCILIATION-STRESS.md",
    ROOT / "docs/decisions/DR-0022-bounded-provider-handoff-and-reconciliation-policy.md",
    ROOT / ".github/workflows/rcs025.yml",
]
SCENARIOS = {
    "lathe_to_generic",
    "mill_fallback_brep",
    "repeated_defer_policies",
    "split_merge_pending",
    "topology_regeneration",
    "undo_replay",
    "error_budget_controls",
}
FORBIDDEN_DURABLE = (
    "topods_",
    "occt handle",
    "triangle index",
    "voxel/cell identity",
    "worker_pid",
    "process_id",
    "object_address",
)


def fail(message: str) -> None:
    raise SystemExit(f"RCS-025 validation failed: {message}")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_plan() -> None:
    plan = load(R / "experiment-plan-v1.json")
    if plan.get("schema") != "rcs-025-provider-handoff-stress-plan/1.0" or plan.get("issue") != "RCS-025":
        fail("plan schema/issue mismatch")
    if plan.get("status") != "predeclared_before_frozen_evidence_run":
        fail("plan must state predeclared-before-frozen-evidence-run status")
    predecessors = set(plan.get("accepted_predecessors", []))
    required_predecessors = {
        "research/rcs-018/evidence-schema-v1.json",
        "docs/decisions/DR-0017-realistic-lathe-tool-envelope-capability.md",
        "docs/decisions/DR-0018-manual-freehand-mill-bounded-directional-fallback.md",
        "docs/decisions/DR-0019-step-layer-d-independent-interoperability.md",
        "docs/decisions/DR-0020-conservative-propagated-error-budgets.md",
        "docs/decisions/DR-0021-retain-occt-8-0-1-after-current-differential.md",
    }
    if not required_predecessors.issubset(predecessors):
        fail("plan omits an accepted predecessor")
    hypotheses = plan.get("hypotheses", [])
    if len(hypotheses) < 6 or any(not h.get("falsified_if") for h in hypotheses):
        fail("plan requires at least six hypotheses with falsification criteria")
    policies = {p.get("id") for p in plan.get("reconciliation_policies", [])}
    if policies != {"hard_semantic_boundaries_only", "hard_plus_pending_threshold"}:
        fail("plan must compare both reconciliation policies")
    boundaries = plan.get("boundaries", {})
    for key in (
        "production_scheduler",
        "provider_private_ids_durable",
        "healing_or_tolerance_widening",
        "silent_ambiguous_mapping",
        "fallback_direct_step_authority",
    ):
        if boundaries.get(key) is not False:
            fail(f"unsafe plan boundary {key}")
    if boundaries.get("step_layer_d_state") != "interoperability_unqualified":
        fail("plan must preserve RCS-022 Layer-D state")


def validate_source_contracts() -> None:
    source = (R / "stress_model.py").read_text(encoding="utf-8")
    required_tokens = [
        "research/rcs-018/vertical_slice.py",
        "research/rcs-023/model.py",
        "interoperability_unqualified",
        "refused_unsupported",
        "BODY_CONNECTIVITY_PENDING",
        "LINEAGE_MAPPING_AMBIGUOUS",
        "fallback bound is not subtracted",
        "assert_no_private_identity",
    ]
    for token in required_tokens:
        if token not in source:
            fail(f"stress model missing contract token: {token}")
    if "EXPORT_BUDGET_MM = \"0.00005\"" not in source:
        fail("RCS-023/RCS-005 research export budget drift")
    if "STEP_PROFILE = \"occt-8.0.1-ap242dis\"" not in source:
        fail("STEP profile/reference backend drift")


def validate_durable_values(result: dict[str, Any]) -> None:
    for scenario in result["scenarios"].values():
        if not isinstance(scenario, dict) or "durable_authority" not in scenario:
            continue
        text = stable_json(scenario["durable_authority"]).lower()
        hits = [x for x in FORBIDDEN_DURABLE if x in text]
        if hits:
            fail(f"provider-private identity leaked into durable evidence: {hits}")


def validate_result(result: dict[str, Any]) -> None:
    if result.get("schema") != "rcs-025-handoff-stress-evidence/1.0" or result.get("issue") != "RCS-025":
        fail("result schema/issue mismatch")
    scenarios = result.get("scenarios", {})
    if set(scenarios) != SCENARIOS:
        fail("scenario set drift")
    if not result.get("contract_result") or not all(result["contract_result"].values()):
        fail("one or more campaign contract results are false")

    core = dict(result)
    recorded_hash = core.pop("deterministic_core_sha256", None)
    if recorded_hash != digest(core):
        fail("deterministic core hash mismatch")

    lathe = scenarios["lathe_to_generic"]
    if lathe["durable_authority"]["body_ids"] != ["body-main"]:
        fail("lathe→generic durable body changed")
    if lathe["topology_diagnostics"]["before"] == lathe["topology_diagnostics"]["after"]:
        fail("lathe→generic topology regeneration control did not change")
    if lathe["step"]["engineering_status"] != "interoperability_unqualified":
        fail("lathe STEP status overclaims Layer D")

    mill = scenarios["mill_fallback_brep"]
    if mill["transition"][-1] != "conventional-engineering-brep@rcs-005":
        fail("mill fallback did not reconcile to conventional B-rep")
    if mill["budgets"]["pending_status"] != "bounded_representation_inexact":
        fail("directional fallback incorrectly treated as exact")
    if mill["fallback_scope"]["arbitrary_nonorthogonal_tool_axis"] != "refused_unsupported":
        fail("non-orthogonal fallback capability was fabricated")
    if "volume_budget_only" not in mill["fallback_scope"]["ball_rounded_constant_z"]:
        fail("ball/rounded scope was broadened beyond RCS-021 evidence")
    if mill["step"]["engineering_status"] != "interoperability_unqualified":
        fail("mill STEP status overclaims Layer D")

    policy = scenarios["repeated_defer_policies"]
    hard = policy["hard_semantic_boundaries_only"]
    bounded = policy["hard_plus_pending_threshold"]
    growth = policy["growth_probe"]
    if (hard["peak_pending_units"], hard["reconciliation_count"], hard["reconciliation_work_units"]) != (4, 2, 26):
        fail("hard-only policy reference drift")
    if (bounded["peak_pending_units"], bounded["reconciliation_count"], bounded["reconciliation_work_units"]) != (2, 4, 36):
        fail("bounded policy reference drift")
    if growth != {"operations": 64, "hard_peak_pending_units": 64, "threshold_peak_pending_units": 2}:
        fail("pending growth probe drift")

    split = scenarios["split_merge_pending"]
    query = split["pre_reconciliation_connectivity_query"]
    if query != {
        "engineering_status": "accepted_pending",
        "failure_code": "BODY_CONNECTIVITY_PENDING",
        "body_selection_permitted": False,
    }:
        fail("connectivity query must fail closed while pending")
    if split["body_count_after_split"] != 2 or split["body_count_final"] != 1:
        fail("split/merge body semantics drift")

    topo = scenarios["topology_regeneration"]
    if not topo["topology_ids_changed"] or not topo["durable_body_id_stable"]:
        fail("topology regeneration did not preserve durable identity")
    ambiguity = topo["ambiguous_control"]
    if ambiguity["engineering_status"] != "accepted_pending" or ambiguity["silent_mapping_permitted"] is not False:
        fail("ambiguous lineage did not fail closed")

    replay = scenarios["undo_replay"]
    if replay["provider_private_state_discarded"] is not True or replay["first_replay_signature"] != replay["rebuilt_replay_signature"]:
        fail("mixed-provider replay invariant failed")

    budgets = scenarios["error_budget_controls"]
    if budgets["within_budget"]["engineering_status"] != "interoperability_unqualified":
        fail("within-budget STEP status must retain Layer D truth")
    if budgets["breach"]["engineering_status"] != "error_budget_breach":
        fail("budget breach did not fail closed")
    if budgets["tolerance_widening_permitted"] is not False:
        fail("tolerance widening must remain forbidden")
    positive = budgets["positive_sub_uncertainty_removal"]
    if positive["status"] != "accepted_pending" or positive["commanded_positive_intent_preserved"] is not True:
        fail("positive material-removal intent was erased")

    validate_durable_values(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))
    validate_plan()
    validate_source_contracts()
    reference = load(REFERENCE)
    validate_result(reference)
    if args.results_dir:
        live_path = args.results_dir / "campaign-result-v1.json"
        if not live_path.is_file():
            fail(f"missing live result {live_path}")
        live = load(live_path)
        validate_result(live)
        if stable_json(live) != stable_json(reference):
            fail("live result differs from frozen reference")
    print("RCS-025 contracts and evidence validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
