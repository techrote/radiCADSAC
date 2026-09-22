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
ARTIFACT = TASK / "pb00701-rational-turn-boundary-v6.json"
REPORT = TASK / "pb00701-report-v6.md"
DOC = ROOT / "docs" / "machining-completeness" / "30-PB00701-RATIONAL-TURN-ENDPOINTS.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "fc11c30529c08db1524a99354843c174210a9797"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-decision-boundary-v3.json": "ec2edaef5ef1cf838fc91e68b25147f41525ac2a",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v3.md": "03105103fe9d90553e5add492efb073bd8c9ab1e",
    "research/machining-completeness/tasks/MC-038/pb00701_event_model.py": "104c0e7a459cd7da5025853b246faff244a5948e",
    "research/machining-completeness/tasks/MC-038/verify_pb00701.py": "b555e99f7b5978e6d7640a6389c83b5ce5569038",
    "research/machining-completeness/tasks/MC-038/gate-scope-retry-v2.json": "76094029a264a5ce226694548b27896f9e0cd430",
    "research/machining-completeness/tasks/MC-032/event_engine.py": "789a709c5141479a343035d1b7055dd4e53534e1",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_rational_turn_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def required_operation_count() -> int:
    return len(load(DOMAIN)["coverage_rule"]["required_operation_ids"])


def validate_artifact(artifact, *, check_repo: bool = True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-rational-turn-boundary/6.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 170
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "ARBITRARY_RATIONAL_TURN_ENDPOINTS_ESTABLISHED_FOR_CONSTANT_COEFFICIENT_TRIG_BRANCH_FULL_BLOCKER_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, expected_sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == expected_sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW"
    assert extension["coefficient_domain"] == "exact rational"
    assert "arbitrary finite exact rational turns" in extension["endpoint_domain"]
    assert "Im((1+i*x)^q)" in extension["endpoint_construction"]
    assert "gcd" in extension["endpoint_equality"]
    assert "one-sided Sturm" in extension["root_count"]
    assert any("B-spline" in claim for claim in extension["not_claimed"])
    assert any("closure" in claim for claim in extension["not_claimed"])

    controls = artifact["boundary_controls"]
    for token in (
        "1/6", "even-multiplicity", "hidden interior", "endpoint equality", "negative-turn",
        "pole", "binary-float", "forged", "resource", "26-operation",
    ):
        assert any(token in control for control in controls), f"missing boundary control: {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert "B-spline" in review["reason"]
    residual = set(review["residual_grammar"])
    assert "POLYNOMIAL_MODULATED_TRIGONOMETRIC" in residual
    assert "GENERAL_TANGENTIAL_MULTIPLE_SINGULAR_TRANSCENDENTAL" in residual
    forbidden = set(review["conditional_or_approximate_authority_forbidden"])
    assert {"binary floating point", "epsilon sign", "timeout", "resource refusal", "unproved transcendence conjecture"} <= forbidden

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDENT_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"] == "OPEN_PROPAGATED"
    for po in OPEN_POS:
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == "NOT_ESTABLISHED"
    assert effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["domain_operation_count"] == 26
    assert effect["domain_narrowed"] is False
    assert effect["next_pre_gate_priority"] == "PB-007-01_GENERAL_COUPLED_ANALYTIC_GRAMMAR"

    resources = artifact["resources"]
    assert resources["native_campaign_run"] is False
    assert resources["paid_campaign_run"] is False
    assert resources["production_authorized"] is False
    assert resources["expensive_execution_authorized"] is False
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    assert required_operation_count() == 26, "frozen 26-operation denominator drift"
    for path, expected_sha in EXPECTED_HISTORY.items():
        assert git_blob_sha(ROOT / path) == expected_sha, f"historical evidence drift: {path}"

    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False

    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    for po in OPEN_POS:
        assert proofs[po]["state"] == "OPEN", f"{po} falsely closed"

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-01", "remains open", "mc-b", "not_established", "26",
            "source/audio/provenance", "rational-turn", "b-spline", "binary",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00701_rational_turn_model.py" in workflow
    assert "verify_pb00701_v6.py --contract" in workflow
    assert "verify_pb00701_v6.py --self-test" in workflow
    assert "verify_pb00701.py --contract" in workflow
    assert "verify_pb00701.py --self-test" in workflow


def spec(**overrides):
    value = {
        "grammar": "RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW",
        "cos_coefficients": {0: "-1", 1: "2"},
        "sin_coefficients": {},
        "turn_lo": "0",
        "turn_hi": "1/4",
        "source_parameter_id": "source-time-t",
        "witness_turn": "1/6",
    }
    value.update(overrides)
    return value


def run_model_controls():
    simple = model.classify_required_analytic_event(spec())
    assert simple["status"] == "CERTIFIED"
    assert simple["distinct_roots_open"] == 1
    witness = simple["witness_event"]
    assert witness["relation"] == "ZERO"
    assert witness["multiplicity"] == 1
    assert witness["event_kind"] == "SIMPLE_CROSSING"
    assert witness["sign_change"] is True
    assert simple["witness_endpoint"]["kind"] == "ALGEBRAIC_TAN_RATIONAL_TURN"

    tangent = model.classify_required_analytic_event(spec(
        cos_coefficients={0: "3", 1: "-4", 2: "2"}
    ))
    assert tangent["status"] == "CERTIFIED"
    assert tangent["distinct_roots_open"] == 1
    assert tangent["multiple_roots_open"] == 1
    witness = tangent["witness_event"]
    assert witness["relation"] == "ZERO"
    assert witness["multiplicity"] == 2
    assert witness["event_kind"] == "MULTIPLE_TANGENCY"
    assert witness["sign_change"] is False

    endpoint = model.classify_required_analytic_event(spec(
        turn_lo="1/6", turn_hi="1/4", witness_turn="1/6"
    ))
    assert endpoint["status"] == "CERTIFIED"
    assert endpoint["left_event"]["relation"] == "ZERO"
    assert endpoint["left_event"]["multiplicity"] == 1
    assert endpoint["distinct_roots_open"] == 0

    hidden = model.classify_required_analytic_event(spec(
        cos_coefficients={2: "1"}, sin_coefficients={},
        turn_lo="1/10", turn_hi="1/6", witness_turn=None
    ))
    assert hidden["status"] == "CERTIFIED"
    assert hidden["distinct_roots_open"] == 1
    assert hidden["multiple_roots_open"] == 0

    negative = model.rational_turn_endpoint("-1/6")
    wrapped = model.rational_turn_endpoint("5/6")
    assert negative["principal_turn"] == wrapped["principal_turn"]
    assert negative["defining_polynomial"] == wrapped["defining_polynomial"]
    assert negative["lo"] == wrapped["lo"] and negative["hi"] == wrapped["hi"]
    neg_sign, _ = model._sign_at_endpoint([0, 1], negative)
    wrap_sign, _ = model._sign_at_endpoint([0, 1], wrapped)
    assert neg_sign == wrap_sign == -1

    shifted = model.classify_required_analytic_event(spec(
        turn_lo="1", turn_hi="5/4", witness_turn="7/6"
    ))
    assert shifted["status"] == "CERTIFIED"
    assert shifted["distinct_roots_open"] == simple["distinct_roots_open"]
    assert shifted["witness_event"]["relation"] == "ZERO"

    pole = model.classify_required_analytic_event(spec(
        turn_lo="1/3", turn_hi="2/3", witness_turn=None
    ))
    assert pole["status"] == "BLOCKED"
    assert pole["blocker"] == "PB-007-01"
    assert "POLE" in pole["reason"]

    empty = model.classify_required_analytic_event(spec(turn_lo="1/6", turn_hi="1/6"))
    assert empty["status"] == "SEMANTIC_BLOCKER"
    assert empty["reason"] == "INVERTED_OR_EMPTY_TURN_INTERVAL"

    inverted = model.classify_required_analytic_event(spec(turn_lo="1/4", turn_hi="1/6"))
    assert inverted["status"] == "SEMANTIC_BLOCKER"

    mismatched = model.classify_required_analytic_event(spec(parameter_projection="independent-phase"))
    assert mismatched["status"] == "SEMANTIC_BLOCKER"
    assert mismatched["reason"] == "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN"

    float_turn = model.classify_required_analytic_event(spec(turn_hi=0.25))
    assert float_turn["status"] == "SEMANTIC_BLOCKER"
    assert float_turn["reason"] == "NONEXACT_TURN_ENDPOINT"

    float_coeff = model.classify_required_analytic_event(spec(cos_coefficients={0: -1, 1: 2.0}))
    assert float_coeff["status"] == "SEMANTIC_BLOCKER"
    assert float_coeff["reason"] == "INVALID_EXACT_ANALYTIC_EVENT_SPEC"

    forged = spec()
    forged["tan_half_lo"] = "0.5773502691896257"
    forged_result = model.classify_required_analytic_event(forged)
    assert forged_result == {"status": "SEMANTIC_BLOCKER", "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD"}

    broader = model.classify_required_analytic_event({"grammar": "POLYNOMIAL_MODULATED_TRIGONOMETRIC"})
    assert broader == {
        "status": "BLOCKED",
        "reason": "FULL_REQUIRED_ANALYTIC_DECISION_ROUTE_NOT_ESTABLISHED",
        "blocker": "PB-007-01",
    }

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False

    # v3 compatibility remains live rather than being replaced.
    cardinal = model.classify_required_analytic_event({
        "grammar": "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW",
        "cos_coefficients": {}, "sin_coefficients": {1: "1"},
        "turn_lo": "-1/4", "turn_hi": "1/4",
        "source_parameter_id": "source-time-t", "witness_half_tan": "0",
    })
    assert cardinal["status"] == "CERTIFIED"
    assert cardinal["distinct_roots_open"] == 1


def expect_artifact_rejected(mutator):
    artifact = copy.deepcopy(load(ARTIFACT))
    mutator(artifact)
    try:
        validate_artifact(artifact, check_repo=False)
    except Exception:
        return
    raise AssertionError("adversarial artifact mutation accepted")


def run_adversarial_artifact_controls():
    expect_artifact_rejected(lambda a: a["full_blocker_review"].__setitem__("status", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("PB-007-01", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("MC-B", "ACCEPTED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("domain_operation_count", 25))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("domain_narrowed", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("paid_campaign_run", True))
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("exact_time_path_phase_correlation_preserved", False))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("next_pre_gate_priority", "MC-B"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        args.contract = args.self_test = True
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 rational-turn endpoint contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-01 rational-turn endpoint/adversarial controls: PASS")


if __name__ == "__main__":
    main()
