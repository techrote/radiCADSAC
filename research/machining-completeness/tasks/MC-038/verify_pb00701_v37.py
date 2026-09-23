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
ARTIFACT = TASK / "pb00701-phase-correlated-two-polynomial-shared-factor-v37.json"
REPORT = TASK / "pb00701-report-v37.md"
DOC = ROOT / "docs" / "machining-completeness" / "63-PB00701-PHASE-CORRELATED-TWO-POLYNOMIAL-SHARED-FACTOR.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v37.yml"
EXPECTED_BASE = "14bf34b37b7397a0186afe6a8d4628734e71bba6"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_phase_correlated_varying_ratio_shared_factor_model.py": "e4b9ecefed12a92c3d72da4edf0a12f45ce05e3d",
    "research/machining-completeness/tasks/MC-038/test_pb00701_phase_correlated_varying_ratio_shared_factor_adversarial.py": "788c94ef8122e59e077e019263ead24dc0c5a11e",
    "research/machining-completeness/tasks/MC-038/pb00701-phase-correlated-varying-ratio-shared-factor-v36.json": "994c68cf913a8d39f831b5b9d9df5edca458f142",
    "research/machining-completeness/tasks/MC-038/pb00701_pointwise_separator_integration_model.py": "7d6c94e48c018fd6570336fea78930a7169cd650",
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-separator-integration-v33.json": "0002c2283b4ef822f23b19ee821dcdd4bfe72a82",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_phase_correlated_two_polynomial_shared_factor_model as model  # noqa: E402
import test_pb00701_phase_correlated_two_polynomial_shared_factor_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-phase-correlated-two-polynomial-shared-factor/37.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 237
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR_ROUTE_ESTABLISHED_PB00701_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    construction = artifact["construction"]
    family = construction["family"].lower()
    for token in ("c_h(s)=n(s)*g(s)", "s_h(s)=d(s)*g(s)", "gcd", "nonconstant"):
        assert token in family, token
    assert "monic euclidean gcd" in construction["gcd_authority"].lower()
    assert "zero remainders" in construction["gcd_authority"].lower()
    assert construction["canonical_normalization"] == "MONIC_OVER_Q"
    assert construction["phase_cell"] == "-3/16+k/2 <= h*phi <= -1/16+k/2"
    assert construction["exact_rational_bounds"]["L_joint_Y_lower"] == "2856/2197"
    assert construction["exact_rational_bounds"]["U_joint_X_upper"] == "99/182"
    assert construction["exact_rational_bounds"]["W_joint_Y_upper"] == "99/70"
    assert construction["exact_rational_bounds"]["two_pi_lower"] == "6"
    assert "g'*(a*x+b*y)" in construction["selected_harmonic_identity"].lower()
    assert "g*(a'*x+b'*y)" in construction["selected_harmonic_identity"].lower()
    assert "n'*g*cos(theta)+d'*g*sin(theta)" in construction["equivalent_quotient_derivative_identity"].lower()
    assert "sigma_b" in construction["phase_gap"].lower()
    assert "a'*g" in construction["strict_margin"].lower()
    assert "b'*g" in construction["strict_margin"].lower()
    assert construction["selected_C_prime_and_S_prime_consumed_only_jointly"] is True
    assert construction["selected_A_prime_G_term_mandatory"] is True
    assert construction["selected_B_prime_G_term_mandatory"] is True
    assert construction["selected_phase_C_and_phase_S_consumed_only_jointly"] is True
    assert construction["all_nonanchor_residuals_retained"] is True
    assert construction["caller_gcd_trusted"] is False
    assert construction["caller_quotients_trusted"] is False
    assert construction["caller_common_factor_trusted"] is False
    assert construction["caller_certificate_trusted"] is False
    for forbidden in ("sampling_used", "epsilon_used", "numerical_trigonometry_used", "arbitrary_subdivision_cap_used"):
        assert construction[forbidden] is False

    acceptance = artifact["acceptance_source"]
    assert acceptance["source_common_factor"] == "(1+3s/4)^2"
    assert acceptance["N_source_scaling"] == "9/10+s/100"
    assert acceptance["D_source_scaling"] == "1+s/200"
    assert acceptance["canonical_monic_G"] == "16/9+8s/3+s^2"
    assert acceptance["derived_N"] == "81/160+9s/1600"
    assert acceptance["derived_D"] == "9/16+9s/3200"
    assert acceptance["derived_N_prime"] == "9/1600"
    assert acceptance["derived_D_prime"] == "9/3200"
    assert acceptance["phase_interval_turns"] == ["-3/16", "-1/16"]
    assert acceptance["v36_result"] == "BLOCKED_BECAUSE_C_OVER_S_IS_NOT_AN_EXACT_POLYNOMIAL"
    assert acceptance["v37_result"] == "CERTIFIED"
    assert acceptance["both_quotient_derivatives_materially_nonzero"] is True
    assert acceptance["both_selected_amplitude_derivatives_active"] is True

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "positive and negative", "opposite", "1/1000000", "a(s)>0", "phase-gap equality",
        "complete-margin equality", "zero/open/left-endpoint/right-endpoint", "coprime", "constant canonical gcd",
        "division remainder", "source-coordinate", "forged gcd", "binary floats", "resource refusal",
        "historical v30, v34, v35 and v36", "v33", "26-operation", "mc-b",
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
    assert "direct exact rotated-coordinate" in effect["next_pre_gate_priority"].lower()

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
            "pb-007-01", "remains open", "two-polynomial", "a'*x+b'*y", "2856/2197", "99/182", "99/70",
            "resource refusal", "26 operations", "source/audio/provenance", "mc-b", "v33", "v36",
        ):
            assert token in text, token

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_phase_correlated_two_polynomial_shared_factor_model.py",
        "test_pb00701_phase_correlated_two_polynomial_shared_factor_adversarial.py",
        "verify_pb00701_v37.py --contract",
        "verify_pb00701_v37.py --self-test",
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
    bad["construction"]["selected_A_prime_G_term_mandatory"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["selected_B_prime_G_term_mandatory"] = False
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["construction"]["caller_gcd_trusted"] = True
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["acceptance_source"]["derived_D_prime"] = "0"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    print("PB-007-01 v37 exact phase-correlated two-polynomial shared-factor verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v37 exact phase-correlated two-polynomial shared-factor contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
