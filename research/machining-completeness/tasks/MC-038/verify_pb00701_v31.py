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
ARTIFACT = TASK / "pb00701-pointwise-separator-blocker-v31.json"
REPORT = TASK / "pb00701-report-v31.md"
DOC = ROOT / "docs" / "machining-completeness" / "57-PB00701-POINTWISE-SEPARATOR-BLOCKER.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v31.yml"
EXPECTED_BASE = "c5b11f6a168bcf4108b05f1432466ac9a30c763d"
EXPECTED_V30_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-source-adaptive-separator-boundary-v30.json": "eb9790c2b6260dfacacc821f3a0f0a4a1404ed31",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v30.md": "d94cd8ec8b8c4157cfa35742cb48c4179a583a66",
    "research/machining-completeness/tasks/MC-038/pb00701_source_adaptive_separator_model.py": "d920a5b670d14ac4a54b0ed879e83532f2114b95",
    "research/machining-completeness/tasks/MC-038/test_pb00701_source_adaptive_separator_adversarial.py": "84aa9e1b7bcabdcb87be5e7aab954e89b9709041",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v30.py": "5796bb100cb54ac7a495ac3de88bfadfbed7b12a",
    "docs/machining-completeness/56-PB00701-SOURCE-ADAPTIVE-SEPARATOR.md": "54af68b2de02d12eb906f15eb3b3384873667e7b",
    ".github/workflows/mc1-pb00701-v30.yml": "0a560b4289064c8ea43c242f7260632fcf8f94c5",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import verify_pb00701_v30 as verify_v30  # noqa: E402
import test_pb00701_pointwise_separator_blocker_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-pointwise-separator-blocker/31.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 225
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_POINTWISE_SEPARATOR_SYNTHESIS_AUTHORITY_BLOCKED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v30_evidence"]}
    assert set(history) == set(EXPECTED_V30_HISTORY)
    for path, sha in EXPECTED_V30_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    inv = artifact["investigation"]
    assert inv["status"] == "THEOREM_ALGORITHM_BLOCKED"
    for token in ("mc-032", "supplied rational", "sturm"):
        assert token in inv["confirmed_existing_authority"].lower(), token
    for token in ("1+2s", "2+3s", "1/5", "5/12"):
        assert token in inv["diagnostic_witness"].lower(), token
    for token in ("critical values", "root isolation", "sqrt(2)-1", "rational"):
        assert token in inv["missing_authority"].lower(), token
    for token in ("resultant", "subresultant", "root isolation", "termination"):
        assert token in inv["required_foundation"].lower(), token
    assert inv["caller_separator_authoritative"] is False
    assert inv["not_an_impossibility_theorem"] is True

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "1/5", "5/12", "1/144", "1/2", "1/1000000", "70/169", "169/408",
        "non-authoritative", "binary float", "resource refusal", "26-operation", "mc-b",
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
    assert "critical-value" in effect["next_pre_gate_priority"].lower()
    assert artifact["resources"] == {
        "native_campaign_run": False,
        "paid_campaign_run": False,
        "production_authorized": False,
        "expensive_execution_authorized": False,
    }
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    verify_v30.validate_artifact(verify_v30.load(verify_v30.ARTIFACT))
    for path, sha in EXPECTED_V30_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v30 historical evidence drift: {path}"
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
            "pb-007-01", "remains open", "mc-032", "critical-value", "root isolation",
            "sqrt(2)-1", "resource refusal", "26 operations", "source/audio/provenance",
        ):
            assert token in text, token
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "test_pb00701_pointwise_separator_blocker_adversarial.py",
        "verify_pb00701_v31.py --contract",
        "verify_pb00701_v31.py --self-test",
    ):
        assert token in workflow, token


def run_self_test():
    verify_v30.run_self_test()
    adversarial.run()
    artifact = load(ARTIFACT)
    validate_artifact(artifact, check_repo=True)
    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["MC-B"] = "ESTABLISHED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_v30_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["investigation"]["caller_separator_authoritative"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    print("PB-007-01 v31 blocker contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v31 blocker contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
