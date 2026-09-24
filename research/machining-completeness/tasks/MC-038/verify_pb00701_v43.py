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
ARTIFACT = TASK / "pb00701-correlated-closed-handoff-v43.json"
REPORT = TASK / "pb00701-report-v43.md"
DOC = ROOT / "docs" / "machining-completeness" / "68-PB00701-CORRELATED-CLOSED-HANDOFF.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v43.yml"
EXPECTED_BASE = "ab9bc9e52a7db184f10bb6d4b7101cf0682a48d2"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_orientation_transition_bridge_model.py": "a0930d7bfddd619bf930a51bbfa14570e2450fe5",
    "research/machining-completeness/tasks/MC-038/test_pb00701_orientation_transition_bridge_adversarial.py": "21e12227262229c095276d0fa6d6656ca49418a3",
    "research/machining-completeness/tasks/MC-038/pb00701-orientation-transition-v42.json": "e622d5b2f13bfe59d5e80310632d90d35b9d351a",
    "research/machining-completeness/tasks/MC-038/pb00701_phase_sector_partition_model.py": "6211e658621af7100c2509dcafdaeaf348e48d46",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import test_pb00701_correlated_closed_handoff_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-correlated-closed-handoff/43.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 250
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_CORRELATED_CLOSED_HANDOFF_DERIVATIVE_CERTIFICATE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    construction = artifact["construction"]
    assert "complete v42 authority first" in construction["precedence"]
    assert "D=A'*X+B'*Y" in construction["physical_identity"]
    assert "eta*h*r*A" in construction["orientation"]
    assert "2*pi*eta*h*r*A" in construction["favorable_phase_A_bound"]
    assert construction["exact_rational_bounds"] == {
        "L_Y_abs_lower": "2856/2197",
        "U_X_abs_upper": "99/182",
        "W_Y_abs_upper": "99/70",
        "two_pi_lower": "6",
        "two_pi_upper": "44/7",
    }
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["endpoint_orientation_zero_allowed"] is True
    assert construction["interior_orientation_root_allowed"] is False
    assert construction["caller_orientation_trusted"] is False
    assert construction["caller_derivatives_trusted"] is False
    assert construction["caller_margin_trusted"] is False
    assert construction["exact_resource_refusal_is_truth"] is False
    assert construction["binary_float_authority"] is False
    for key in ("sampling_used", "epsilon_used", "numerical_trigonometry_used", "arbitrary_subdivision_cap_used"):
        assert construction[key] is False

    acceptance = artifact["acceptance_source"]
    assert acceptance["C_1"] == "-3/10+17*s/20"
    assert acceptance["S_1"] == "1/20+3*s/20"
    assert acceptance["derived_A_1"] == "-1/8+s/2"
    assert acceptance["derived_B_1"] == "-7/40+7*s/20"
    assert acceptance["A_handoff_root"] == "1/4"
    assert acceptance["parent_v42_result"] == "BLOCKED"
    assert acceptance["right_child_v42_result"] == "BLOCKED"
    assert acceptance["right_child_v43_result"] == "CERTIFIED"
    assert acceptance["composed_parent_result"] == "CERTIFIED"
    assert acceptance["handoff_cut_is_physical_root"] is False

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "equality", "phase-cell", "positive and negative", "endpoint zero",
        "interior a sign change", "resource refusal", "forged caller",
        "binary-float", "v42", "event-neutral", "counted exactly once",
        "v42-v39", "non-anchor", "26-operation", "mc-b",
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
    assert "#245" in effect["next_pre_gate_priority"] and "do not retry mc-b" in effect["next_pre_gate_priority"].lower()
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
            "pb-007-01", "remains open", "correlated", "handoff",
            "2856/2197", "99/182", "99/70", "44/7", "endpoint",
            "resource refusal", "26 operations", "mc-b", "v42", "#245",
        ):
            assert token in text, (text[:80], token)

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_correlated_closed_handoff_model.py",
        "test_pb00701_correlated_closed_handoff_adversarial.py",
        "verify_pb00701_v43.py --contract",
        "verify_pb00701_v43.py --self-test",
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
    bad["construction"]["endpoint_orientation_zero_allowed"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["exact_rational_bounds"]["two_pi_lower"] = "0"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["parent_v42_result"] = "CERTIFIED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    print("PB-007-01 v43 correlated closed-handoff verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v43 correlated closed-handoff contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
