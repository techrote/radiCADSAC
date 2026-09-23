#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00701-orientation-transition-v42.json"
REPORT = TASK / "pb00701-report-v42.md"
DOC = ROOT / "docs" / "machining-completeness" / "67-PB00701-ORIENTATION-TRANSITION-DERIVATIVE-BRIDGE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v42.yml"
EXPECTED_BASE = "494a29091fcd9afadad006cded4a71b74349c824"

sys.path.insert(0, str(TASK))
import test_pb00701_orientation_transition_bridge_adversarial as adversarial  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected adversarial mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-orientation-transition-bridge/42.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 247
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_ORIENTATION_TRANSITION_BRIDGE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    construction = artifact["construction"]
    assert construction["coordinates"].startswith("A=(C+S)/2")
    physical = construction["physical_selected_harmonic_identity"].lower()
    assert "d=a'(s)*x+b'(s)*y" in physical
    assert "strict sign of source-owned b'" in construction["orientation_authority"].lower()
    assert construction["phase_cell"] == "-3/16+k/2 <= h*phi <= -1/16+k/2"
    assert construction["exact_rational_bounds"] == {
        "L_joint_Y_lower": "2856/2197",
        "U_joint_X_upper": "99/182",
        "W_joint_Y_upper": "99/70",
        "two_pi_upper": "44/7",
    }
    margin = construction["strict_margin"].lower()
    for token in ("|b'|*l", "|a'|*u", "44/7", "|a|*w", "|b|*u", "sum_i|r_i|"):
        assert token in margin, token
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["complete_v40_precedence_first"] is True
    assert construction["proof_cut_is_physical_event"] is False
    for key in (
        "caller_orientation_trusted", "caller_rotated_coordinates_trusted",
        "caller_derivatives_trusted", "caller_certificate_trusted",
        "sampling_used", "epsilon_used", "numerical_trigonometry_used",
        "arbitrary_subdivision_cap_used",
    ):
        assert construction[key] is False, key

    acceptance = artifact["acceptance_source"]
    assert acceptance["C_1"] == "-23/6+11*s"
    assert acceptance["S_1"] == "17/6-9*s"
    assert acceptance["derived_A"] == "-1/2+s"
    assert acceptance["derived_B"] == "-10/3+10*s"
    assert acceptance["derived_A_prime"] == "1"
    assert acceptance["derived_B_prime"] == "10"
    assert acceptance["A_zero"] == "1/2" and acceptance["B_zero"] == "1/3"
    assert acceptance["complete_v40_result"] == "BLOCKED"
    assert acceptance["v42_result"] == "CERTIFIED"

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "orientation zero", "b'", "strict equality", "phase-cell", "positive and negative phase rate",
        "opposite diagonal", "non-anchor", "forged", "binary floats", "resource refusal",
        "v39/v40", "26-operation", "mc-b", "mc-1",
    ):
        assert token in controls, token

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDENT_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"] == "OPEN_PROPAGATED"
    for po in ("PO-04", "PO-05", "PO-08"):
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["domain_operation_count"] == 26
    assert effect["domain_narrowed"] is False
    assert "#245" in effect["next_pre_gate_priority"]
    assert artifact["resources"]["production_authorized"] is False
    assert artifact["resources"]["expensive_execution_authorized"] is False
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    assert len(load(DOMAIN)["coverage_rule"]["required_operation_ids"]) == 26
    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False
    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    for po in ("PO-04", "PO-05", "PO-08"):
        assert proofs[po]["state"] == "OPEN"

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-01", "remains open", "orientation-transition", "2856/2197", "99/182",
            "99/70", "44/7", "resource refusal", "26 operations", "source/audio/provenance",
            "mc-b", "#245",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_orientation_transition_bridge_model.py",
        "test_pb00701_orientation_transition_bridge_adversarial.py",
        "verify_pb00701_v42.py --contract",
        "verify_pb00701_v42.py --self-test",
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
    bad["construction"]["proof_cut_is_physical_event"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["complete_v40_result"] = "CERTIFIED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["construction"]["exact_rational_bounds"]["two_pi_upper"] = "7"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v42 exact orientation-transition bridge verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v42 exact orientation-transition bridge contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
