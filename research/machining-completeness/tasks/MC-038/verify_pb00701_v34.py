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
ARTIFACT = TASK / "pb00701-phase-correlated-common-factor-v34.json"
REPORT = TASK / "pb00701-report-v34.md"
DOC = ROOT / "docs" / "machining-completeness" / "60-PB00701-PHASE-CORRELATED-COMMON-FACTOR.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v34.yml"
EXPECTED_BASE = "224e663bee1b45c50680e4739eed9424d06eb530"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_source_adaptive_separator_model.py": "d920a5b670d14ac4a54b0ed879e83532f2114b95",
    "research/machining-completeness/tasks/MC-038/test_pb00701_source_adaptive_separator_adversarial.py": "84aa9e1b7bcabdcb87be5e7aab954e89b9709041",
    "research/machining-completeness/tasks/MC-038/pb00701_pointwise_separator_integration_model.py": "7d6c94e48c018fd6570336fea78930a7169cd650",
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-separator-integration-v33.json": "0002c2283b4ef822f23b19ee821dcdd4bfe72a82",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_phase_correlated_common_factor_model as model  # noqa: E402
import test_pb00701_phase_correlated_common_factor_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-phase-correlated-common-factor/34.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 231
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_PHASE_CORRELATED_COMMON_FACTOR_ROUTE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    construction = artifact["construction"]
    for token in ("c_h(s)=s_h(s)=g(s)", "strict sign"):
        assert token in construction["family"].lower(), token
    assert construction["phase_cell"] == "-3/16+k/2 <= h*phi <= -1/16+k/2"
    assert construction["exact_rational_bounds"]["joint_phase_lower"] == "2856/2197"
    assert construction["exact_rational_bounds"]["joint_amplitude_upper"] == "99/182"
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["caller_certificate_trusted"] is False
    for forbidden in ("sampling_used", "epsilon_used", "numerical_trigonometry_used", "arbitrary_subdivision_cap_used"):
        assert construction[forbidden] is False

    acceptance = artifact["acceptance_source"]
    assert acceptance["G"] == "(1+3s/4)^2"
    assert acceptance["C_1_equals_S_1"] is True
    assert acceptance["phase_interval_turns"] == ["-3/16", "-1/16"]
    assert acceptance["v30_global_projective_ratio"] == "16/49"
    assert "sqrt(2)-1" in acceptance["v30_boundary"]
    assert acceptance["v34_result"] == "CERTIFIED"
    assert acceptance["both_selected_amplitude_derivatives_active"] is True

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "positive and negative", "opposite", "1/1000000", "equality",
        "zero/open/left-endpoint/right-endpoint", "unequal", "sign-changing",
        "source-coordinate", "forged", "binary floats", "resource refusal",
        "historical v30", "v33", "26-operation", "mc-b",
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
    assert "proportional/common-factor" in effect["next_pre_gate_priority"].lower()

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
        assert git_blob_sha(ROOT / path) == sha, f"historical evidence drift: {path}"
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
            "pb-007-01", "remains open", "phase-correlated", "2856/2197",
            "99/182", "resource refusal", "26 operations", "source/audio/provenance",
            "mc-b", "v33",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_phase_correlated_common_factor_model.py",
        "test_pb00701_phase_correlated_common_factor_adversarial.py",
        "verify_pb00701_v34.py --contract",
        "verify_pb00701_v34.py --self-test",
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
    bad["construction"]["selected_C_prime_and_S_prime_consumed_only_jointly"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["all_nonanchor_residuals_retained"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][2]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v34 exact phase-correlated common-factor verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v34 exact phase-correlated common-factor contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
