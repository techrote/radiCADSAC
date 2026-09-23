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
ARTIFACT = TASK / "pb00701-orientation-transition-v42.json"
REPORT = TASK / "pb00701-report-v42.md"
DOC = ROOT / "docs" / "machining-completeness" / "67-PB00701-ORIENTATION-TRANSITION-DERIVATIVE-BRIDGE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v42.yml"
EXPECTED_BASE = "494a29091fcd9afadad006cded4a71b74349c824"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_signed_b_anti_diagonal_model.py": "2f642ac0b6f222dd8ec2cf3a54ffa3c07bb27abe",
    "research/machining-completeness/tasks/MC-038/test_pb00701_signed_b_anti_diagonal_adversarial.py": "a27019656ab364d1de0559e75f9bacb1d2ba0126",
    "research/machining-completeness/tasks/MC-038/pb00701-signed-b-anti-diagonal-v40.json": "f4a2ea57445c9309620f58a6c19e0cd8cade1618",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_orientation_transition_bridge_model as model  # noqa: E402
import test_pb00701_orientation_transition_bridge_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-orientation-transition-bridge/42.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 247
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_ORIENTATION_TRANSITION_DERIVATIVE_BRIDGE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    construction = artifact["construction"]
    assert "complete v40 authority first" in construction["precedence"].lower()
    assert "a=(c+s)/2" in construction["source_authority"].lower()
    assert "b=(c-s)/2" in construction["source_authority"].lower()
    derivative_authority = construction["derivative_orientation_authority"].lower()
    assert "b'>0" in derivative_authority and "-b'>0" in derivative_authority and "sigma_b_prime" in derivative_authority
    assert construction["phase_cell"] == "-3/16+k/2 <= h*phi <= -1/16+k/2"
    assert construction["exact_rational_bounds"] == {
        "L_Y_abs_lower": "2856/2197",
        "U_X_abs_upper": "99/182",
        "W_Y_abs_upper": "99/70",
        "two_pi_upper": "44/7",
    }
    physical = construction["physical_selected_harmonic_identity"].lower()
    assert "d=a'(s)*x+b'(s)*y" in physical and "2*pi*h*r" in physical
    assert "bprime_bar" in construction["favorable_channel"].lower()
    strict = construction["strict_margin"].lower()
    for token in ("2856/2197", "99/182", "44/7", "99/70", "a'", "sigma_a", "sigma_b", "r_i"):
        assert token in strict, token
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["A_or_B_strict_orientation_required"] is False
    assert construction["proof_orientation_zero_is_physical_event"] is False
    assert construction["complete_v40_precedence_first"] is True
    assert construction["caller_orientation_trusted"] is False
    assert construction["caller_derivatives_trusted"] is False
    assert construction["caller_certificate_trusted"] is False
    assert construction["exact_resource_refusal_is_truth"] is False
    assert construction["binary_float_authority"] is False
    for forbidden in ("sampling_used", "epsilon_used", "numerical_trigonometry_used", "arbitrary_subdivision_cap_used"):
        assert construction[forbidden] is False

    acceptance = artifact["acceptance_source"]
    assert acceptance["C_1"] == "-23/60+11*s/10"
    assert acceptance["S_1"] == "17/60-9*s/10"
    assert acceptance["derived_A"] == "-1/20+s/10"
    assert acceptance["derived_B"] == "-1/3+s"
    assert acceptance["derived_A_prime"] == "1/10"
    assert acceptance["derived_B_prime"] == "1"
    assert acceptance["A_interior_zero"] == "1/2"
    assert acceptance["B_interior_zero"] == "1/3"
    assert acceptance["sigma_B_prime"] == 1
    assert acceptance["phase_interval_turns"] == ["-1/8", "-1/16"]
    assert acceptance["phase_rate"] == "1/16"
    assert acceptance["v40_result"].startswith("BLOCKED_")
    assert acceptance["v42_result"] == "CERTIFIED"
    assert "closed" in acceptance["new_authority"].lower()
    assert "without cuts" in acceptance["new_authority"].lower()

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "interior a orientation zero",
        "1/1000000",
        "b' exact sign equality",
        "positive and negative b'",
        "complete-margin equality",
        "phase-cell left/right",
        "positive and negative phase-rate",
        "opposite diagonal",
        "non-anchor",
        "resource refusal",
        "forged caller",
        "binary floats",
        "source-coordinate",
        "v39 and v40",
        "physical events",
        "26-operation",
        "mc-b",
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
            "pb-007-01", "remains open", "orientation-transition", "b'", "2856/2197",
            "99/182", "99/70", "44/7", "closed", "resource refusal", "26 operations",
            "source/audio/provenance", "mc-b", "v40", "physical event",
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
    bad["construction"]["A_or_B_strict_orientation_required"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["proof_orientation_zero_is_physical_event"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["exact_rational_bounds"]["two_pi_upper"] = "22/7"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["v40_result"] = "CERTIFIED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0]["git_blob_sha1"] = "0" * 40
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
