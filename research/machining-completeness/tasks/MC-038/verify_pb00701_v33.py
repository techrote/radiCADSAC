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
ARTIFACT = TASK / "pb00701-pointwise-separator-integration-v33.json"
REPORT = TASK / "pb00701-report-v33.md"
DOC = ROOT / "docs" / "machining-completeness" / "59-PB00701-POINTWISE-SEPARATOR-INTEGRATION.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v33.yml"
EXPECTED_BASE = "9bf9ddf77371139d69540307ee8053b4ed158b41"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_source_adaptive_separator_model.py": "d920a5b670d14ac4a54b0ed879e83532f2114b95",
    "research/machining-completeness/tasks/MC-038/test_pb00701_source_adaptive_separator_adversarial.py": "84aa9e1b7bcabdcb87be5e7aab954e89b9709041",
    "research/machining-completeness/tasks/MC-038/pb00701_algebraic_separator_exact.py": "bb90aed7b5933520fdcb43205da40a98701fb7bd",
    "research/machining-completeness/tasks/MC-038/pb00701_algebraic_separator_foundation_model.py": "2855b4de81e061801fb43abf94817434e33619d6",
    "research/machining-completeness/tasks/MC-038/test_pb00701_algebraic_separator_foundation_adversarial.py": "bb83917458699eedec8ef2177315a8e302248030",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v32.py": "966365aaf280ed7c6a90db611ac67bfcdc334370",
    "research/machining-completeness/tasks/MC-038/pb00701-algebraic-separator-foundation-v32.json": "1d0232358eb86d92a2d867b2427e7a33473e0837",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v32.md": "dc7688c623e9e9250c30ef0314316c3430fc037d",
    "docs/machining-completeness/58-PB00701-ALGEBRAIC-SEPARATOR-FOUNDATION.md": "2ad24a2028bca4827f44ad691d970bafef9c9147",
    ".github/workflows/mc1-pb00701-v32.yml": "c2a2eecf23620601892367bbd9664b43577b20c3",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_pointwise_separator_integration_model as model  # noqa: E402
import test_pb00701_pointwise_separator_integration_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-pointwise-separator-integration/33.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 229
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "V32_SEPARATOR_INTEGRATED_EXACTLY_BUT_PRESERVED_FULL_RESIDUAL_REMAINS_LIMITING_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    pins = {}
    for entry in artifact["historical_v30_executable_evidence"] + artifact["qualified_v32_foundation"]:
        pins[entry["path"]] = entry["git_blob_sha1"]
    assert pins == EXPECTED_HISTORY

    integration = artifact["integration_result"]
    assert integration["status"] == "THEOREM_BOUNDARY_RECORDED"
    for token in ("v32", "source-owned", "v30", "sign-orthant"):
        assert token in integration["mechanical_integration"].lower(), token
    for token in ("1+2s", "2+3s", "d'=2", "t'=3"):
        assert token in integration["v31_diagnostic"].lower(), token
    for token in ("common", "16/49", "pointwise", "amplitude-derivative"):
        assert token in integration["common_factor_control"].lower(), token
    assert integration["event_classifier_promoted"] is False
    assert integration["residual_contract_weakened"] is False
    assert integration["not_an_impossibility_theorem"] is True
    assert "phase-correlated" in integration["precise_next_theorem"].lower()

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "v31", "source-owned", "16/49", "70/169", "169/408", "sin/cos",
        "positive/negative", "caller", "binary float", "resource refusal", "v30",
        "26-operation", "mc-b",
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
    assert "v34" in effect["next_pre_gate_priority"].lower()
    assert "phase-correlated" in effect["next_pre_gate_priority"].lower()

    assert artifact["resources"] == {
        "native_campaign_run": False,
        "paid_campaign_run": False,
        "production_authorized": False,
        "expensive_execution_authorized": False,
    }
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    for path, sha in EXPECTED_HISTORY.items():
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
            "pb-007-01", "remains open", "v32", "v30", "16/49", "phase-correlated",
            "resource refusal", "26 operations", "source/audio/provenance", "mc-b",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_pointwise_separator_integration_model.py",
        "test_pb00701_pointwise_separator_integration_adversarial.py",
        "verify_pb00701_v33.py --contract",
        "verify_pb00701_v33.py --self-test",
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
    bad["integration_result"]["event_classifier_promoted"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["integration_result"]["residual_contract_weakened"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["qualified_v32_foundation"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v33 exact pointwise separator integration verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v33 exact pointwise separator integration contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
