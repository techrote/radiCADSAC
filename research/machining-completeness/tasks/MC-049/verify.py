#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-049"
CONTRACT = TASK / "final-challenge-contract-v1.json"
GENERATOR = TASK / "challenge_generator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def load_json_at_ref(ref: str, path: str):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def import_generator():
    spec = importlib.util.spec_from_file_location("mc049_challenge_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load MC-049 challenge generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    contract = load(CONTRACT)
    generator = import_generator()

    generator.validate_contract(contract)
    generator.adversarial_self_test(contract)

    assert contract["source_baseline"] == "3f8e695838b41913b5a05a0b235e7b3ff118e04f"
    baseline_outcomes = load_json_at_ref(
        contract["source_baseline"],
        "research/machining-completeness/outcomes-v1.json",
    )
    assert baseline_outcomes["tasks"]["MC-026"]["state"] == "NOT_STARTED"
    assert baseline_outcomes["tasks"]["MC-049"]["state"] == "NOT_STARTED"

    dependency_states = {
        "MC-005": "CAPABILITY_ACCEPTED",
        "MC-009": "COMPLETED_RESEARCH",
        "MC-010": "COMPLETED_RESEARCH",
        "MC-011": "COMPLETED_RESEARCH",
        "MC-012": "COMPLETED_RESEARCH",
        "MC-013": "COMPLETED_RESEARCH",
        "MC-014": "COMPLETED_RESEARCH",
        "MC-015": "COMPLETED_RESEARCH",
    }
    assert {
        item["task"]: item["result_kind"]
        for item in contract["dependency_artifacts"]
    } == dependency_states
    for item in contract["dependency_artifacts"]:
        path = ROOT / item["path"]
        assert path.is_file(), item["path"]
        assert git_blob_sha1(path) == item["blob_sha"], f"dependency drift: {item['path']}"

    for pin in contract["source_pins"]:
        path = ROOT / pin["path"]
        assert path.is_file(), pin["path"]
        assert git_blob_sha1(path) == pin["blob_sha"], f"source drift: {pin['path']}"

    auxiliary = contract["reviewed_auxiliary_inputs"]
    assert len(auxiliary) == 1 and auxiliary[0]["task"] == "MC-004"
    aux_path = ROOT / auxiliary[0]["path"]
    assert git_blob_sha1(aux_path) == auxiliary[0]["blob_sha"]
    qualification = load(aux_path)
    assert (
        qualification["workload_generation"]["seed_sha256"]
        == auxiliary[0]["candidate_blind_workload_seed_sha256"]
    )
    assert qualification["retroactive_tuning_forbidden"] is True

    registry = load(ROOT / "research" / "machining-completeness" / "fixture-families-v1.json")
    assert [f["id"] for f in registry["families"]] == [f"F{i:02d}" for i in range(1, 17)]
    assert all(f["mandatory"] is True and f["state"] == "BUILT" for f in registry["families"])

    generated = generator.materialize(contract, CONTRACT.read_bytes())
    assert generated["challenge_count"] == 64
    assert generated["mandatory_family_count"] == 16
    assert generated["candidate_inputs"] == []
    assert generated["held_out"] is False and generated["independent_custodian"] is False
    assert generated["execution_authorized"] is False
    assert all(c["execution_state"] == "FROZEN_NOT_EXECUTED" for c in generated["challenges"])
    assert len({c["challenge_id"] for c in generated["challenges"]}) == 64
    assert {c["family"] for c in generated["challenges"]} == set(contract["required_families"])
    for family in contract["required_families"]:
        classes = {c["class"] for c in generated["challenges"] if c["family"] == family}
        assert classes == set(contract["required_challenge_classes"])

    outcomes = load(ROOT / "research" / "machining-completeness" / "outcomes-v1.json")
    record = outcomes["tasks"]["MC-049"]
    assert record["state"] == "COMPLETED_RESEARCH"
    required_artifacts = {
        "research/machining-completeness/tasks/MC-049/final-challenge-contract-v1.json",
        "research/machining-completeness/tasks/MC-049/challenge_generator.py",
        "research/machining-completeness/tasks/MC-049/report.md",
        "research/machining-completeness/tasks/MC-049/outcome.json",
        "research/machining-completeness/tasks/MC-049/verify.py",
        "docs/machining-completeness/03-ORACLE-AND-CORPUS.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])
    assert record["blockers"] == []

    outcome = load(TASK / "outcome.json")
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
    assert outcome["task"] == "MC-049" and outcome["result_kind"] == "COMPLETED_RESEARCH"
    assert outcome["native_execution"] is False
    assert outcome["blockers"] == []
    assert outcome["custody"]["classification"] == "PUBLIC_PRESELECTION_PREREGISTRATION"
    assert outcome["custody"]["held_out"] is False
    assert outcome["custody"]["independent_custodian"] is False
    assert outcome["custody"]["later_independent_execution_owner"] == "MC-057"

    doc = (ROOT / "docs" / "machining-completeness" / "03-ORACLE-AND-CORPUS.md").read_text(
        encoding="utf-8"
    )
    assert "MC-049 now freezes" in doc
    assert "PUBLIC_PRESELECTION_PREREGISTRATION" in doc
    assert "not an independent held-out set" in doc
    assert "MC-057" in doc

    workflow = (ROOT / ".github" / "workflows" / "mc1-static.yml").read_text(encoding="utf-8")
    assert "tasks/MC-049/challenge_generator.py" in workflow
    assert "tasks/MC-049/verify.py" in workflow
    assert "tools/mc_workflow.py verify MC-049" in workflow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract or --self-test")
    verify_contract()
    print("MC-049 candidate-blind challenge freeze verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
