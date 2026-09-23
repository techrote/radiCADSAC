#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00701-algebraic-separator-foundation-v32.json"
REPORT = TASK / "pb00701-report-v32.md"
DOC = ROOT / "docs" / "machining-completeness" / "58-PB00701-ALGEBRAIC-SEPARATOR-FOUNDATION.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v32.yml"
EXPECTED_BASE = "bee133512e8e95096c38356ca086b9a0ae53fe10"
EXPECTED_MC032 = {
    "research/machining-completeness/tasks/MC-032/event_engine.py": "789a709c5141479a343035d1b7055dd4e53534e1",
}
EXPECTED_V31_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-separator-blocker-v31.json": "10299cc9831989e27278eee5f67ca43156cfb1e5",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v31.md": "3f9feddfc22b60f4d714029cae17e5f0f0f8ef41",
    "research/machining-completeness/tasks/MC-038/test_pb00701_pointwise_separator_blocker_adversarial.py": "c64cd94c1b8e8266e0ccf40e9e99540df24eef6f",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v31.py": "1a26810f60f96cae9312718a0dca41f595fe9e00",
    "docs/machining-completeness/57-PB00701-POINTWISE-SEPARATOR-BLOCKER.md": "cf51db5d58db28cf5fcb3ef16e5399edbc7e92f2",
    ".github/workflows/mc1-pb00701-v31.yml": "496fc4827fa79c68d02c6613525b0d9baf2af757",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_algebraic_separator_foundation_model as model  # noqa: E402
import test_pb00701_algebraic_separator_foundation_adversarial as adversarial  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def assert_rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected adversarial mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-algebraic-separator-foundation/32.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 227
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_ALGEBRAIC_CRITICAL_VALUE_SEPARATOR_FOUNDATION_CERTIFIED_PB00701_REMAINS_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    dep = artifact["qualified_dependency"]
    assert dep["path"] in EXPECTED_MC032
    assert dep["git_blob_sha1"] == EXPECTED_MC032[dep["path"]]
    assert "sturm" in dep["authority"].lower()

    history = {entry["path"]: entry for entry in artifact["historical_v31_evidence"]}
    assert set(history) == set(EXPECTED_V31_HISTORY)
    for path, sha in EXPECTED_V31_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    foundation = artifact["foundation"]
    assert foundation["status"] == "CERTIFIED"
    for token in ("rational", "closed [0,1]", "dominant sign"):
        assert token in foundation["scope"].lower(), token
    for token in ("d'(s)t(s)-d(s)t'(s)", "transverse", "multiplicit"):
        assert token in foundation["stationary_construction"].lower(), token
    for token in ("sturm", "mignotte", "finite"):
        assert token in foundation["root_isolation"].lower() + " " + foundation["finite_termination"].lower(), token
    for token in ("sylvester", "bareiss", "resultant"):
        assert token in foundation["critical_value_elimination"].lower(), token
    for token in ("sqrt(2)-1", "minimal polynomial", "sign-at-algebraic-root"):
        assert token in foundation["algebraic_boundary_ordering"].lower(), token
    for token in ("beta", "closed form", "sqrt(2)-1"):
        assert token in foundation["separator_synthesis"].lower(), token
    assert "mc-032" in foundation["independent_final_check"].lower()
    assert foundation["event_classifier_promoted"] is False
    assert foundation["caller_separator_or_root_metadata_authoritative"] is False

    controls = " ".join(artifact["acceptance_controls"]).lower()
    for token in (
        "1+2s", "2+3s", "1/5", "5/12", "irrational", "endpoint", "transverse",
        "repeated", "sqrt(2)-1", "1/1000000", "70/169", "169/408", "forged",
        "binary float", "resource refusal", "26-operation", "mc-b",
    ):
        assert token in controls, token

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDENT_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"] == "OPEN_PROPAGATED"
    for po in OPEN_POS:
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["domain_operation_count"] == 26
    assert effect["domain_narrowed"] is False
    assert "v33" in effect["next_pre_gate_priority"].lower()
    assert "residual" in effect["next_pre_gate_priority"].lower()

    assert artifact["resources"] == {
        "native_campaign_run": False,
        "paid_campaign_run": False,
        "production_authorized": False,
        "expensive_execution_authorized": False,
    }
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    for path, sha in {**EXPECTED_MC032, **EXPECTED_V31_HISTORY}.items():
        assert git_blob_sha(ROOT / path) == sha, f"historical/qualified evidence drift: {path}"
    assert len(load(DOMAIN)["coverage_rule"]["required_operation_ids"]) == 26
    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False
    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    for po in OPEN_POS:
        assert proofs[po]["state"] == "OPEN"

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-01", "remains open", "mc-032", "sturm", "mignotte", "resultant",
            "sqrt(2)-1", "resource refusal", "26 operations", "source/audio/provenance", "v33",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_algebraic_separator_exact.py",
        "pb00701_algebraic_separator_foundation_model.py",
        "test_pb00701_algebraic_separator_foundation_adversarial.py",
        "verify_pb00701_v32.py --contract",
        "verify_pb00701_v32.py --self-test",
    ):
        assert token in workflow, token


def run_self_test():
    adversarial.run()
    artifact = load(ARTIFACT)
    validate_artifact(artifact, check_repo=True)

    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["MC-B"] = "ESTABLISHED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_v31_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["foundation"]["event_classifier_promoted"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["foundation"]["caller_separator_or_root_metadata_authoritative"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    diag = model.synthesize_separator([1, 2], [2, 3])
    assert diag["status"] == "CERTIFIED" and model.verify_binding(diag)
    print("PB-007-01 v32 exact algebraic separator foundation verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v32 exact algebraic separator foundation contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
