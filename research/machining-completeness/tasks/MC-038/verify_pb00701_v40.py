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
ARTIFACT = TASK / "pb00701-signed-b-anti-diagonal-v40.json"
REPORT = TASK / "pb00701-report-v40.md"
DOC = ROOT / "docs" / "machining-completeness" / "66-PB00701-SIGNED-B-ANTI-DIAGONAL-DIRECT-ROTATED-COORDINATE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v40.yml"
EXPECTED_BASE = "a92115689da4713d30ba74d65c033897e877a4f7"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_signed_a_direct_rotated_coordinate_model.py": "d8cf3c4f3abaf1299bae2e4fd7120b17724a2df1",
    "research/machining-completeness/tasks/MC-038/test_pb00701_signed_a_direct_rotated_coordinate_adversarial.py": "e777c69f7a54a6f61f92de1beaeda661e718b9a5",
    "research/machining-completeness/tasks/MC-038/pb00701-signed-a-direct-rotated-coordinate-v39.json": "2b53d00acb12a6ac6d7f7e0fe417ebe09325758c",
    "research/machining-completeness/tasks/MC-038/pb00701_pointwise_separator_integration_model.py": "7d6c94e48c018fd6570336fea78930a7169cd650",
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-separator-integration-v33.json": "0002c2283b4ef822f23b19ee821dcdd4bfe72a82",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_signed_b_anti_diagonal_model as model  # noqa: E402
import test_pb00701_signed_b_anti_diagonal_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-signed-b-anti-diagonal/40.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 243
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_SIGNED_B_ANTI_DIAGONAL_ROUTE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    construction = artifact["construction"]
    family = construction["family"].lower()
    assert "c_h(s)" in family and "s_h(s)" in family and "strict sign of b" in family
    assert "a=(c+s)/2" in construction["source_authority"].lower()
    assert "b=(c-s)/2" in construction["source_authority"].lower()
    assert "either b>0 or -b>0" in construction["orientation_authority"].lower()
    assert "sigma_b" in construction["orientation_authority"].lower()
    assert "bbar=sigma_b*b" in construction["oriented_variables"].lower()
    assert "atilde=-sigma_b*a" in construction["oriented_variables"].lower()
    assert construction["phase_cell"] == "1/16+k/2 <= h*phi <= 3/16+k/2"
    symmetry = construction["quarter_turn_symmetry"].lower()
    assert "quarter" in symmetry and "x'(theta')=-y(theta)" in symmetry and "y'(theta')=x(theta)" in symmetry
    assert construction["exact_rational_bounds"] == {
        "L_joint_X_lower": "2856/2197",
        "U_joint_Y_upper": "99/182",
        "W_joint_X_upper": "99/70",
        "two_pi_lower": "6",
    }
    oriented = construction["oriented_selected_harmonic_identity"].lower()
    assert "(-sigma_b)*d=" in oriented and "-bbar'(s)*y" in oriented
    assert "+bbar'(s)*y" not in oriented
    physical = construction["physical_selected_harmonic_identity"].lower()
    assert "d=a'(s)*x+b'(s)*y" in physical
    reconciliation = construction["issue_243_contract_reconciliation"].lower()
    assert "sign typo" in reconciliation and "exact algebra requires -bbar'*y" in reconciliation
    assert "sigma_a" in construction["phase_gap"].lower()
    assert "atilde'" in construction["strict_margin"].lower()
    assert "bbar'" in construction["strict_margin"].lower()
    assert construction["physical_sign_recovery"] == "sign(D)=-sigma_B*sign(h*r)*anti_diagonal_projection_sign"
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["complete_v39_precedence_first"] is True
    assert construction["caller_orientation_trusted"] is False
    assert construction["caller_rotated_coordinates_trusted"] is False
    assert construction["caller_derivatives_trusted"] is False
    assert construction["caller_certificate_trusted"] is False
    for forbidden in (
        "sampling_used",
        "epsilon_used",
        "numerical_trigonometry_used",
        "arbitrary_subdivision_cap_used",
    ):
        assert construction[forbidden] is False

    acceptance = artifact["acceptance_source"]
    assert acceptance["C_1"] == "19/20+s/10"
    assert acceptance["S_1"] == "-21/20+s/10"
    assert acceptance["canonical_gcd"] == "1"
    assert acceptance["derived_A"] == "-1/20+s/10"
    assert acceptance["derived_B"] == "1"
    assert acceptance["derived_A_prime"] == "1/10"
    assert acceptance["derived_B_prime"] == "0"
    assert acceptance["sigma_B"] == 1
    assert acceptance["derived_Bbar"] == "1"
    assert acceptance["derived_Atilde"] == "1/20-s/10"
    assert acceptance["phase_interval_turns"] == ["1/16", "3/16"]
    assert acceptance["v39_result"] == "BLOCKED_BECAUSE_A_CROSSES_ZERO"
    assert acceptance["v40_result"] == "CERTIFIED"
    assert "signed-b" in acceptance["new_authority"].lower()
    assert "quarter-turn" in acceptance["new_authority"].lower()

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "both sigma_b signs",
        "b=0",
        "1/1000000",
        "sign-changing b",
        "positive and negative phase-rate",
        "opposite",
        "anti-diagonal phase-cell boundary",
        "phase-gap equality",
        "complete-margin equality",
        "zero/open/left-endpoint/right-endpoint",
        "forged sigma_b",
        "source-coordinate",
        "binary floats",
        "resource refusal",
        "historical v30, v34, v35, v36, v37, v38 and v39",
        "v33",
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
    assert "do not retry mc-b" in effect["next_pre_gate_priority"].lower()
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

    for text in (
        REPORT.read_text(encoding="utf-8").lower(),
        DOC.read_text(encoding="utf-8").lower(),
    ):
        for token in (
            "pb-007-01",
            "remains open",
            "signed-b",
            "sigma_b",
            "anti-diagonal",
            "quarter-turn",
            "2856/2197",
            "99/182",
            "99/70",
            "-bbar'",
            "resource refusal",
            "26 operations",
            "source/audio/provenance",
            "mc-b",
            "v39",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_signed_b_anti_diagonal_model.py",
        "test_pb00701_signed_b_anti_diagonal_adversarial.py",
        "verify_pb00701_v40.py --contract",
        "verify_pb00701_v40.py --self-test",
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
    bad["construction"]["caller_orientation_trusted"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["construction"]["physical_sign_recovery"] = "sign(D)=sign(h*r)"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["construction"]["oriented_selected_harmonic_identity"] = (
        "(-sigma_B)*D=Atilde'(s)*X+Bbar'(s)*Y+2*pi*h*r*(Bbar(s)*X+Atilde(s)*Y)"
    )
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["sigma_B"] = -1
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["v39_result"] = "CERTIFIED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v40 exact signed-B anti-diagonal verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v40 exact signed-B anti-diagonal contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
