#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-045"
CONTRACT = TASK / "campaign-harness-contract-v1.json"
OUTCOME = TASK / "outcome.json"
REGISTRY = ROOT / "research" / "machining-completeness" / "outcomes-v1.json"
DOC = ROOT / "docs" / "machining-completeness" / "05-QUALIFICATION.md"
HARNESS_PATH = TASK / "campaign_harness.py"
EXPECTED_BASELINE = "25ca84ad82022e832b9198ec313178f8d1500130"
EXPECTED_DEPS = {
    "MC-056": ("research/machining-completeness/tasks/MC-056/outcome.json", "e9b971c593ca1a90baf17f9ae9a5a568dd313ac3", "COMPLETED_RESEARCH"),
    "MC-009": ("research/machining-completeness/tasks/MC-009/outcome.json", "3a2c52997ace526add72b0f2051e6b5120c0a44d", "COMPLETED_RESEARCH"),
}
EXPECTED_AUX = ("research/machining-completeness/tasks/MC-004/qualification-contract-v1.json", "22d5f976718edac9a8ccce3cb46f799b76e85ab4")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def reject_binary_float(value) -> None:
    if isinstance(value, float):
        raise AssertionError("binary float forbidden in decisive MC-045 authority data")
    if isinstance(value, dict):
        for item in value.values():
            reject_binary_float(item)
    elif isinstance(value, list):
        for item in value:
            reject_binary_float(item)


def load_harness():
    spec = importlib.util.spec_from_file_location("mc045_campaign_harness", HARNESS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    reject_binary_float(contract)
    assert contract["schema"] == "radicadsac-mc045-campaign-harness-contract/1.0"
    assert contract["task"] == "MC-045"
    assert contract["issue"] == 107
    assert contract["source_baseline"] == EXPECTED_BASELINE
    assert contract["result"] == "QUALIFIED_STATIC_CAMPAIGN_HARNESS"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob, result_kind) in EXPECTED_DEPS.items():
        assert deps[task] == {"task": task, "path": path, "blob_sha": blob, "result_kind": result_kind}
        if check_files:
            dep = ROOT / path
            assert dep.is_file()
            assert git_blob_sha1(dep) == blob, f"{task} dependency drift"
            assert load(dep)["result_kind"] == result_kind

    aux = contract["reviewed_auxiliary_inputs"]
    assert len(aux) == 1 and aux[0]["task"] == "MC-004"
    assert aux[0]["path"] == EXPECTED_AUX[0]
    assert aux[0]["blob_sha"] == EXPECTED_AUX[1]
    if check_files:
        assert git_blob_sha1(ROOT / EXPECTED_AUX[0]) == EXPECTED_AUX[1], "MC-004 qualification contract drift"

    permit = contract["permit_contract"]
    assert permit["schema"] == "radicadsac-mc-native-permit/1.0"
    required = set(permit["required_fields"])
    assert {
        "approval_evidence", "source_sha", "candidate_config_digest", "fixture_profile_digest",
        "platform_id", "allocated_vcpus", "max_processes", "threads_per_process", "max_jobs",
        "sequential_repeats", "timeout_seconds", "peak_rss_bytes_max", "storage_bytes_max",
        "egress_bytes_max", "tariff_basis", "retention_path", "stop_rules", "expensive_campaign_lock",
    } <= required
    assert set(permit["dispatch_classes"]) == {"MODEL_ONLY", "NATIVE_BOUNDED"}
    assert permit["approval_authority"] == "MC-1-programme"
    assert permit["native_dispatch_requires_external_approved_permit"] is True
    assert permit["issue_existence_is_approval"] is False
    assert permit["missing_or_placeholder_approval_is_rejected"] is True
    assert permit["paid_tariff_may_be_guessed"] is False
    assert permit["permit_reuse_across_source_candidate_profile_or_platform"] is False
    assert permit["one_active_expensive_campaign"] is True
    assert permit["expensive_campaign_lock_value"] == "HELD_BY_THIS_PERMIT"

    plan = contract["plan_contract"]
    assert plan["schema"] == "radicadsac-mc-campaign-plan/1.0"
    assert set(plan["bindings"]) == {"permit_id", "source_sha", "candidate_config_digest", "fixture_profile_digest", "platform_id"}
    assert plan["command_is_argv_array"] is True
    assert plan["shell_command_forbidden"] is True
    assert plan["repeats_are_sequential"] is True
    assert plan["parallel_repeat_copies_forbidden"] is True
    assert "allocated_vcpus" in plan["nested_parallelism_rule"]
    assert plan["timeout_must_not_exceed_permit"] is True
    assert plan["memory_storage_egress_caps_must_not_exceed_permit"] is True

    accounting = contract["accounting_contract"]
    assert accounting["reserved_vcpu_seconds_formula"] == "allocated_vcpus * timeout_seconds * max_jobs * sequential_repeats"
    assert "exact rational" in accounting["reserved_vcpu_minutes_representation"]
    assert accounting["runner_wall_time_distinct_from_cpu_time"] is True
    assert accounting["all_attempts_retained"] is True
    assert "JSONL" in accounting["ledger_format"] and "fsync" in accounting["ledger_format"]
    assert accounting["timeout_resource_crash_incomplete_are_nonpass"] is True
    assert accounting["resource_cap_violation_terminal"] == "RESOURCE_EXHAUSTED"
    assert accounting["budget_exhaustion_terminal"] == "INCOMPLETE"

    controls = set(contract["self_test_controls"])
    for required_control in {
        "missing permit", "placeholder approval evidence", "source/config/profile/platform binding mismatch",
        "parallel repeats", "nested worker oversubscription", "timeout/memory/storage/egress over-plan",
        "paid tariff marked unverified", "lock mismatch", "timeout terminal retention",
        "resource-exhausted terminal retention", "crash terminal retention",
        "three sequential successful repeats retained in order", "exact reserved vCPU-minute calculation",
    }:
        assert required_control in controls

    assert contract["capability_guard"] == {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }
    assert "does not authorize" in contract["scope_limit"]

    harness = load_harness()
    harness.self_test()

    if check_files:
        outcome = load(OUTCOME)
        assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
        assert outcome["task"] == "MC-045"
        assert outcome["result_kind"] == "COMPLETED_RESEARCH"
        assert outcome["source_baseline"] == EXPECTED_BASELINE
        assert outcome["native_execution"] is False
        assert outcome["resources"]["native_or_paid_campaign_run"] is False
        assert outcome["resources"]["self_test_reserved_vcpu_seconds"] == 120
        assert outcome["resources"]["self_test_reserved_vcpu_minutes"] == {"numerator": 2, "denominator": 1}
        assert outcome["blockers"] == []

        registry = load(REGISTRY)["tasks"]["MC-045"]
        assert registry["state"] == "COMPLETED_RESEARCH"
        assert registry["issue"] == 107
        assert registry["blockers"] == []
        for path in (
            "research/machining-completeness/tasks/MC-045/campaign-harness-contract-v1.json",
            "research/machining-completeness/tasks/MC-045/campaign_harness.py",
            "research/machining-completeness/tasks/MC-045/report.md",
            "research/machining-completeness/tasks/MC-045/outcome.json",
            "research/machining-completeness/tasks/MC-045/verify.py",
        ):
            assert path in registry["accepted_artifacts"]

        doc = DOC.read_text(encoding="utf-8")
        assert "### MC-045 permit-bound campaign harness" in doc
        assert "MODEL_ONLY" in doc
        assert "NATIVE_BOUNDED" in doc
        assert "fsync" in doc
        assert "does not authorize native or paid execution" in doc


def adversarial_self_test(contract: dict) -> None:
    def must_fail(mutator) -> None:
        bad = copy.deepcopy(contract)
        mutator(bad)
        try:
            validate_contract(bad, check_files=False)
        except (AssertionError, KeyError):
            return
        raise AssertionError("adversarial contract mutation was accepted")

    must_fail(lambda x: x.__setitem__("native_execution", True))
    must_fail(lambda x: x["permit_contract"].__setitem__("issue_existence_is_approval", True))
    must_fail(lambda x: x["permit_contract"].__setitem__("paid_tariff_may_be_guessed", True))
    must_fail(lambda x: x["permit_contract"].__setitem__("one_active_expensive_campaign", False))
    must_fail(lambda x: x["permit_contract"].__setitem__("expensive_campaign_lock_value", "FREE"))
    must_fail(lambda x: x["plan_contract"].__setitem__("repeats_are_sequential", False))
    must_fail(lambda x: x["plan_contract"].__setitem__("parallel_repeat_copies_forbidden", False))
    must_fail(lambda x: x["accounting_contract"].__setitem__("all_attempts_retained", False))
    must_fail(lambda x: x["accounting_contract"].__setitem__("timeout_resource_crash_incomplete_are_nonpass", False))
    must_fail(lambda x: x["capability_guard"].__setitem__("MC-F", "ACCEPTED"))
    must_fail(lambda x: x["formal_dependencies"][0].__setitem__("blob_sha", "0" * 40))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    contract = load(CONTRACT)
    validate_contract(contract, check_files=True)
    if args.self_test:
        adversarial_self_test(contract)
    print("MC-045 contract verification passed" + (" with adversarial self-test" if args.self_test else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
