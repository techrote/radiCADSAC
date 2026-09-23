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
ARTIFACT = TASK / "pb00701-direct-rotated-coordinate-v38.json"
REPORT = TASK / "pb00701-report-v38.md"
DOC = ROOT / "docs" / "machining-completeness" / "64-PB00701-DIRECT-ROTATED-COORDINATE-TWO-QUADRATURE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v38.yml"
EXPECTED_BASE = "e8b9d37f6f2f23de7f1a176704c2c428ae71aac3"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_phase_correlated_two_polynomial_shared_factor_model.py": "485ad89d9b5ff9847095f48880cc9a9cb3be96ce",
    "research/machining-completeness/tasks/MC-038/test_pb00701_phase_correlated_two_polynomial_shared_factor_adversarial.py": "230fd40d7ae3d0035dae6c17075c0dcb9b533db3",
    "research/machining-completeness/tasks/MC-038/pb00701-phase-correlated-two-polynomial-shared-factor-v37.json": "0e81e744685f3d34872f9cad536ed514e8a3b628",
    "research/machining-completeness/tasks/MC-038/pb00701_pointwise_separator_integration_model.py": "7d6c94e48c018fd6570336fea78930a7169cd650",
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-separator-integration-v33.json": "0002c2283b4ef822f23b19ee821dcdd4bfe72a82",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_direct_rotated_coordinate_model as model  # noqa: E402
import test_pb00701_direct_rotated_coordinate_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-direct-rotated-coordinate/38.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 239
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_DIRECT_ROTATED_COORDINATE_ROUTE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    construction = artifact["construction"]
    family = construction["family"].lower()
    assert "c_h(s)" in family and "s_h(s)" in family and "no common-factor requirement" in family
    assert "a=(c+s)/2" in construction["source_authority"].lower()
    assert "b=(c-s)/2" in construction["source_authority"].lower()
    assert construction["phase_cell"] == "-3/16+k/2 <= h*phi <= -1/16+k/2"
    assert construction["exact_rational_bounds"]["L_joint_Y_lower"] == "2856/2197"
    assert construction["exact_rational_bounds"]["U_joint_X_upper"] == "99/182"
    assert construction["exact_rational_bounds"]["W_joint_Y_upper"] == "99/70"
    assert construction["exact_rational_bounds"]["two_pi_lower"] == "6"
    assert "a'(s)*x+b'(s)*y" in construction["selected_harmonic_identity"].lower()
    assert "c'(s)*cos(theta)+s'(s)*sin(theta)" in construction["equivalent_source_derivative_identity"].lower()
    assert "sigma_b" in construction["phase_gap"].lower()
    assert "a'" in construction["strict_margin"].lower() and "b'" in construction["strict_margin"].lower()
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_A_prime_term_material"] is True
    assert construction["selected_B_prime_term_supported_and_material_when_nonzero"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["caller_rotated_coordinates_trusted"] is False
    assert construction["caller_derivatives_trusted"] is False
    assert construction["caller_certificate_trusted"] is False
    for forbidden in ("sampling_used", "epsilon_used", "numerical_trigonometry_used", "arbitrary_subdivision_cap_used"):
        assert construction[forbidden] is False

    acceptance = artifact["acceptance_source"]
    assert acceptance["C_1"] == "1+6s/5"
    assert acceptance["S_1"] == "11/10+6s/5"
    assert acceptance["canonical_gcd"] == "1"
    assert acceptance["derived_A"] == "21/20+6s/5"
    assert acceptance["derived_B"] == "-1/20"
    assert acceptance["derived_A_prime"] == "6/5"
    assert acceptance["derived_B_prime"] == "0"
    assert acceptance["phase_interval_turns"] == ["-3/16", "-1/16"]
    assert acceptance["v37_result"] == "BLOCKED_BECAUSE_CANONICAL_GCD_IS_CONSTANT"
    assert acceptance["v38_result"] == "CERTIFIED"
    assert acceptance["C_prime_materially_nonzero"] is True
    assert acceptance["S_prime_materially_nonzero"] is True
    assert "nonzero A' and B'" in acceptance["unequal_derivative_secondary_fixture"]

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "positive and negative", "opposite", "1/1000000", "a(s)>0", "phase-gap equality",
        "complete-margin equality", "zero/open/left-endpoint/right-endpoint", "coprime", "canonical gcd is constant",
        "both a' and b'", "source-coordinate", "forged rotated-coordinate", "binary floats", "resource refusal",
        "historical v30, v34, v35, v36 and v37", "v33", "26-operation", "mc-b",
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

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-01", "remains open", "direct rotated-coordinate", "a'", "b'", "2856/2197",
            "99/182", "99/70", "resource refusal", "26 operations", "source/audio/provenance", "mc-b", "v33", "v37",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_direct_rotated_coordinate_model.py",
        "test_pb00701_direct_rotated_coordinate_adversarial.py",
        "verify_pb00701_v38.py --contract",
        "verify_pb00701_v38.py --self-test",
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
    bad["construction"]["selected_A_prime_term_material"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["selected_B_prime_term_supported_and_material_when_nonzero"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["caller_rotated_coordinates_trusted"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["v37_result"] = "CERTIFIED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    print("PB-007-01 v38 exact direct rotated-coordinate verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v38 exact direct rotated-coordinate contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
