#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-017"
CONTRACT = TASK / "consumer-probe-v1.json"

EXPECTED_SOURCE_BASELINE = "57689b7128d5c8f9531a1efe398ea6a12daa9804"
EXPECTED_BRLCAD_COMMIT = "0d745fca358e6b4655552186da4221206f4b7483"
EXPECTED_SOURCE_PINS = {
    "import-architecture": ("src/conv/step/STEPImportArchitecture.md", "f998e4c9b1d0ea5e2a4b9f95e4140f429ca48669"),
    "direct-import-target-dependencies": ("src/conv/step/step-g/CMakeLists.txt", "99bd08eeb8dca8c54e89ebb68d33ab882a1824d2"),
    "import-cli-and-policy": ("doc/asciidoc/system/man1/step-g.adoc", "a6f8b7bb2fcd4bbc83a3bc968f4d31a4167d833e"),
    "independent-measurement-cli": ("doc/asciidoc/system/man1/gqa.adoc", "e6bea44d2eab03fb3a4a1ad2735f21705bc84399"),
    "follow-on-boolean-semantics": ("doc/asciidoc/lessons/mged05_learning_boolean_expressions.adoc", "37508ac5902a4475e7332976e4fb63c0a9f9c8e7"),
}
EXPECTED_BLOCKERS = {"XB-017-01"}
EXPECTED_CONTEXT_BLOCKERS = {f"RB-016-{i:02d}" for i in range(1, 6)}
FORBIDDEN_SHARED_STACKS = {"OPEN CASCADE", "OCCT", "MANIFOLD"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    assert contract["schema"] == "radicadsac-mc017-independent-consumer-probe/1.0"
    assert contract["task"] == "MC-017"
    assert contract["issue"] == 79
    assert contract["source_baseline"] == EXPECTED_SOURCE_BASELINE
    assert contract["result"] == "COMPLETED_RESEARCH_WITH_EXECUTION_ACCESS_BLOCKER"
    assert contract["native_execution"] is False

    deps = contract["formal_dependencies"]
    assert len(deps) == 1
    dep = deps[0]
    assert dep == {
        "task": "MC-001",
        "path": "research/machining-completeness/tasks/MC-001/outcome.json",
        "blob_sha": "2efd52cf39102d5722c6bbf281828361e943d6a4",
        "result_kind": "COMPLETED_RESEARCH",
    }
    if check_files:
        dep_path = ROOT / dep["path"]
        assert dep_path.is_file()
        assert git_blob_sha1(dep_path) == dep["blob_sha"], "MC-001 dependency drift"

    context = contract["contextual_inputs"]
    assert len(context) == 1
    mc016 = context[0]
    assert mc016["task"] == "MC-016"
    assert mc016["path"] == "research/machining-completeness/tasks/MC-016/outcome.json"
    assert mc016["blob_sha"] == "606a7d0b8be61131b2272f2eb161d6a4dbba703a"
    assert set(mc016["required_open_blockers"]) == EXPECTED_CONTEXT_BLOCKERS
    assert "non-task-graph contextual input" in mc016["relationship"]
    if check_files:
        mc016_path = ROOT / mc016["path"]
        assert mc016_path.is_file()
        assert git_blob_sha1(mc016_path) == mc016["blob_sha"], "MC-016 contextual source drift"
        mc016_outcome = load(mc016_path)
        blockers = {b["id"]: b for b in mc016_outcome["blockers"]}
        assert EXPECTED_CONTEXT_BLOCKERS <= set(blockers)
        assert all(blockers[x]["status"] == "OPEN" for x in EXPECTED_CONTEXT_BLOCKERS)

    candidate = contract["source_level_candidate"]
    assert candidate["id"] == "BRLCAD-STEP-G-20260918"
    assert candidate["repository"] == "https://github.com/BRL-CAD/brlcad"
    assert candidate["commit"] == EXPECTED_BRLCAD_COMMIT
    assert candidate["status"] == "SOURCE_VIABLE_EXECUTION_UNQUALIFIED"
    assert "not a complete transitive dependency audit" in candidate["independence_scope"].lower()
    pins = {p["role"]: p for p in candidate["source_pins"]}
    assert set(pins) == set(EXPECTED_SOURCE_PINS)
    for role, (path, sha) in EXPECTED_SOURCE_PINS.items():
        assert pins[role]["path"] == path
        assert pins[role]["blob_sha"] == sha

    facts = candidate["observed_source_facts"]
    assert facts["step_importer_selects_schema_plugin_from_part21_header"] is True
    assert facts["documented_ap242_editions"] == [1, 2, 3, 4]
    assert facts["strict_exact_repair_none_mode_available"] is True
    assert facts["machine_readable_import_report_available"] is True
    assert set(facts["report_outcomes"]) == {"complete", "partial", "empty", "failed"}
    assert facts["direct_import_target_names_occt_or_manifold"] is False
    direct = " ".join(facts["direct_import_target_dependencies"]).upper()
    assert "STEPCODE" in direct and "OPENNURBS" in direct and "LIBBREP" in direct
    assert not any(token in direct for token in FORBIDDEN_SHARED_STACKS)
    assert {"volume", "bounding_box", "overlaps", "gaps"} <= set(facts["gqa_measurements"])
    assert set(facts["boolean_operations_documented"]) == {"union", "difference", "intersection"}
    assert set(s.upper() for s in candidate["forbidden_shared_decisive_stacks"]) == FORBIDDEN_SHARED_STACKS

    protocol = contract["probe_protocol"]
    binding = protocol["input_binding"]
    assert binding["consume_exact_step_file_bytes"] is True
    assert binding["required_digest"] == "sha256"
    assert binding["record_file_schema_header"] is True
    assert binding["record_producer_profile_and_accuracy_contract"] is True
    assert binding["producer_in_memory_geometry_may_substitute"] is False

    imp = protocol["import"]
    command = imp["command_template"]
    for token in ("--strict", "--exact", "--repair none", "--reject-invalid-objs", "--report", "--summary"):
        assert token in command
    assert imp["required_exit_code"] == 0
    assert imp["required_report_outcome"] == "complete"
    assert imp["allow_partial"] is False
    assert imp["allow_repair"] is False
    assert imp["allow_inference"] is False
    assert imp["allow_invalid_preserved"] is False
    assert imp["all_expected_product_bound_items_accounted"] is True

    controls = {c["id"]: c for c in protocol["controls_required_before_native_qualification"]}
    assert set(controls) == {"CTRL-017-GOOD", "CTRL-017-BAD", "CTRL-017-MATERIAL-WRONG"}
    assert controls["CTRL-017-GOOD"]["kind"] == "known-good-independent-step"
    assert controls["CTRL-017-BAD"]["kind"] == "known-bad-step"
    assert "valid-but-materially-wrong" in controls["CTRL-017-MATERIAL-WRONG"]["kind"]

    measurement = protocol["measurement"]
    assert measurement["engine"] == "BRL-CAD gqa/librt"
    assert measurement["consume_imported_database"] is True
    assert measurement["approximate_method"] is True
    assert measurement["may_claim_exact_geometry"] is False
    assert measurement["minimum_refinement_runs"] >= 3
    assert measurement["require_explicit_grid_spacing_and_limit"] is True
    assert measurement["require_cross_view_convergence_within_declared_error_budget"] is True
    micro_rule = measurement["micro_feature_rule"].lower()
    assert "no positive micro-feature" in micro_rule
    assert "qualified by gqa unless" in micro_rule

    follow = protocol["follow_on_operation"]
    assert follow["consumer"] == "BRL-CAD"
    assert follow["must_consume_imported_geometry"] is True
    assert follow["may_replay_nominal_machining_history_instead"] is False
    assert "Boolean difference" in follow["operation"]
    assert "independently imported STEP object" in follow["operation"]

    profiles = {p["class"]: p for p in contract["profile_semantics"]}
    assert set(profiles) == {
        "regular-nonempty-manifold",
        "enclosed-disjoint-cavity",
        "multiple-disconnected-positive-volume-components",
        "positive-micro-feature",
        "exact-zero-contact-touching-cavity-singular-pinch",
        "empty-material",
    }
    assert profiles["regular-nonempty-manifold"]["status"] == "SOURCE_PATH_IDENTIFIED_NATIVE_EXECUTION_UNQUALIFIED"
    assert profiles["enclosed-disjoint-cavity"]["status"] == "OPEN"
    assert "RB-016-01" in profiles["enclosed-disjoint-cavity"]["consumer_rule"]
    assert "RB-016-02" in profiles["multiple-disconnected-positive-volume-components"]["consumer_rule"]
    assert "insufficient" in profiles["positive-micro-feature"]["consumer_rule"].lower()
    assert profiles["exact-zero-contact-touching-cavity-singular-pinch"]["status"] == "PROFILE_DECISION_REQUIRED"
    assert "no healing/fusion" in profiles["exact-zero-contact-touching-cavity-singular-pinch"]["consumer_rule"].lower()
    assert profiles["empty-material"]["status"] == "PROFILE_DECISION_REQUIRED"
    assert "no fake epsilon solid" in profiles["empty-material"]["consumer_rule"].lower()

    blockers = {b["id"]: b for b in contract["blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    blocker = blockers["XB-017-01"]
    assert blocker["status"] == "OPEN"
    assert blocker["existing_downstream_owner"] == "MC-043"
    assert {"MC-043", "MC-044", "MC-052"} <= set(blocker["affected_descendants"])
    assert blocker["unaffected_work"]
    assert "native-execution permit" in blocker["summary"]
    assert "does not authorize" in blocker["why_not_solved_here"]

    assert contract["capability_guard"] == {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }


def adversarial_self_test(contract: dict) -> None:
    mutations = []

    bad = copy.deepcopy(contract)
    bad["source_level_candidate"]["observed_source_facts"]["direct_import_target_dependencies"].append("OCCT")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["input_binding"]["producer_in_memory_geometry_may_substitute"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["import"]["allow_repair"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["import"]["required_report_outcome"] = "partial"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["measurement"]["may_claim_exact_geometry"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["measurement"]["minimum_refinement_runs"] = 1
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["measurement"]["micro_feature_rule"] = "gqa alone exactly qualifies every positive micro-feature"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["probe_protocol"]["follow_on_operation"]["must_consume_imported_geometry"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile_semantics"][3]["consumer_rule"] = "gqa alone qualifies the positive micro-feature exactly"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile_semantics"][5]["consumer_rule"] = "represent empty material as a fake epsilon solid"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["blockers"][0]["status"] = "CLOSED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-C"] = "ACCEPTED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["contextual_inputs"][0]["required_open_blockers"].remove("RB-016-04")
    mutations.append(bad)

    rejected = 0
    for bad in mutations:
        try:
            validate_contract(bad, check_files=False)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
    assert rejected == len(mutations), f"accepted {len(mutations) - rejected} adversarial corruption(s)"


def verify_integration() -> None:
    contract = load(CONTRACT)
    validate_contract(contract, check_files=True)
    adversarial_self_test(contract)

    outcome = load(TASK / "outcome.json")
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
    assert outcome["task"] == "MC-017"
    assert outcome["result_kind"] == "COMPLETED_RESEARCH"
    assert outcome["native_execution"] is False
    assert {b["id"] for b in outcome["blockers"]} == EXPECTED_BLOCKERS
    assert outcome["review"]["gate_changed"] is False
    assert outcome["review"]["programme_capability_changed"] is False

    outcomes = load(ROOT / "research/machining-completeness/outcomes-v1.json")
    record = outcomes["tasks"]["MC-017"]
    assert record["state"] == "COMPLETED_RESEARCH"
    assert {b["id"] for b in record["blockers"]} == EXPECTED_BLOCKERS
    required_artifacts = {
        "research/machining-completeness/tasks/MC-017/consumer-probe-v1.json",
        "research/machining-completeness/tasks/MC-017/report.md",
        "research/machining-completeness/tasks/MC-017/outcome.json",
        "research/machining-completeness/tasks/MC-017/verify.py",
        "docs/machining-completeness/04-REPRESENTATION-AND-RECONSTRUCTION.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])

    doc = (ROOT / "docs/machining-completeness/04-REPRESENTATION-AND-RECONSTRUCTION.md").read_text(encoding="utf-8")
    assert "MC-017 independent-consumer probe" in doc
    assert "BRL-CAD" in doc and "STEPcode" in doc and "OpenNURBS" in doc
    assert "XB-017-01" in doc
    assert "source-viable" in doc.lower()
    assert "not measured native interoperability" in doc.lower()
    assert "MC-C remains **NOT_ESTABLISHED**" in doc

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text(encoding="utf-8")
    assert "tasks/MC-017/verify.py" in workflow
    assert "tools/mc_workflow.py verify MC-017" in workflow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract or --self-test")
    verify_integration()
    print("MC-017 independent-consumer probe contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
