#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-015"
CONTRACT = TASK / "certificate-attack-contract-v1.json"
CHECKER = TASK / "certificate_checker.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def import_checker():
    spec = importlib.util.spec_from_file_location("mc015_certificate_checker", CHECKER)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load MC-015 certificate checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    contract = load(CONTRACT)
    assert contract["schema"] == "radicadsac-mc015-certificate-attack-contract/1.0"
    assert contract["task"] == "MC-015"
    assert contract["issue"] == 77
    assert contract["source_baseline"] == "045a6a85972ad381cfcc0ccfc014e4dca8c5a970"
    assert contract["protected_semantics"]["native_or_paid_execution"] is False
    assert contract["capability_guard"] == {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }

    expected_dependencies = {"MC-009": "COMPLETED_RESEARCH", "MC-010": "COMPLETED_RESEARCH"}
    assert {d["task"]: d["result_kind"] for d in contract["dependencies"]} == expected_dependencies
    for dep in contract["dependencies"] + contract["reviewed_auxiliary_inputs"]:
        path = ROOT / dep["path"]
        assert path.is_file(), dep["path"]
        assert git_blob_sha1(path) == dep["blob_sha"], f"dependency drift: {dep['path']}"

    for pin in contract["source_pins"]:
        path = ROOT / pin["path"]
        assert path.is_file(), pin["path"]
        assert git_blob_sha1(path) == pin["blob_sha"], f"source drift: {pin['path']}"

    registry = load(ROOT / "research" / "machining-completeness" / "fixture-families-v1.json")
    families = registry["families"]
    assert [f["id"] for f in families] == [f"F{i:02d}" for i in range(1, 17)]
    expected_owners = {**{f"F{i:02d}": "MC-011" for i in range(1, 5)}, **{f"F{i:02d}": "MC-012" for i in range(5, 9)}, **{f"F{i:02d}": "MC-013" for i in range(9, 13)}, **{f"F{i:02d}": "MC-014" for i in range(13, 17)}}
    assert all(f["mandatory"] is True and f["state"] == "BUILT" for f in families)
    assert {f["id"]: f["owner"] for f in families} == expected_owners

    oracle_paths = [
        ROOT / "research/machining-completeness/tasks/MC-010/independent_exact_oracle.py",
        ROOT / "research/machining-completeness/tasks/MC-011/fixture_oracle.py",
        ROOT / "research/machining-completeness/tasks/MC-012/fixture_oracle.py",
        ROOT / "research/machining-completeness/tasks/MC-013/fixture_oracle.py",
        ROOT / "research/machining-completeness/tasks/MC-014/fixture_oracle.py",
    ]
    allowed_oracle_imports = {"__future__", "dataclasses", "fractions", "typing"}
    for path in oracle_paths:
        assert imported_roots(path) <= allowed_oracle_imports, f"unexpected oracle import graph: {path}"
    assert imported_roots(CHECKER) <= {"__future__", "copy", "hashlib", "fractions", "typing"}

    checker = import_checker()
    checker.self_test()

    subprocess.run([sys.executable, str(ROOT / "tools" / "mc_evidence_verifier.py"), "--self-test"], check=True)

    outcomes = load(ROOT / "research" / "machining-completeness" / "outcomes-v1.json")
    record = outcomes["tasks"]["MC-015"]
    assert record["state"] == "COMPLETED_RESEARCH"
    required_artifacts = {
        "research/machining-completeness/tasks/MC-015/certificate-attack-contract-v1.json",
        "research/machining-completeness/tasks/MC-015/certificate_checker.py",
        "research/machining-completeness/tasks/MC-015/report.md",
        "research/machining-completeness/tasks/MC-015/outcome.json",
        "research/machining-completeness/tasks/MC-015/verify.py",
        "docs/machining-completeness/03-ORACLE-AND-CORPUS.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])
    assert record["blockers"] == []

    doc = (ROOT / "docs/machining-completeness/03-ORACLE-AND-CORPUS.md").read_text(encoding="utf-8")
    assert "MC-015 now" in doc
    assert "certificate" in doc.lower() and "does not" in doc.lower() and "establish MC-B" in doc

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text(encoding="utf-8")
    assert "tasks/MC-015/certificate_checker.py" in workflow
    assert "tools/mc_workflow.py verify MC-015" in workflow

    outcome = load(TASK / "outcome.json")
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
    assert outcome["task"] == "MC-015" and outcome["result_kind"] == "COMPLETED_RESEARCH"
    assert outcome["native_execution"] is False
    assert outcome["blockers"] == []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract or --self-test")
    verify_contract()
    print("MC-015 certificate/oracle adversarial contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
