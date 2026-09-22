#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00701-decision-boundary-v3.json"
REPORT = TASK / "pb00701-report-v3.md"
DOC = ROOT / "docs" / "machining-completeness" / "27-PB00701-EXACT-EVENT-BOUNDARY.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "732b8e73e8e4669d51489df5f1975e21b5227a11"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-007/transcendental-route-v1.json": "41ce571bb77a7c8a8b9b69f49f8be119acc66fff",
    "research/machining-completeness/tasks/MC-032/event_engine.py": "789a709c5141479a343035d1b7055dd4e53534e1",
    "research/machining-completeness/tasks/MC-032/outcome.json": "bc42e0f824621af10354534dc83aa03765a893ed",
    "research/machining-completeness/tasks/MC-038/constructive-coverage-review-v1.json": "9042bec1a77d36cfe64de8a13c579a460c926176",
    "research/machining-completeness/tasks/MC-038/gate-scope-retry-v2.json": "76094029a264a5ce226694548b27896f9e0cd430",
}
EXPECTED_OPERATIONS = {
    "lathe_threading_synchronized",
    "lathe_eccentric_turning",
    "mill_thread_helix_fixed_axis",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_event_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def required_operation_count() -> int:
    return len(load(DOMAIN)["coverage_rule"]["required_operation_ids"])


def validate_artifact(artifact, *, check_repo: bool = True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-decision-boundary/3.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 164
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "BOUNDED_EXACT_EXTENSION_ESTABLISHED_FULL_BLOCKER_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, expected_sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == expected_sha
        assert history[path]["preserved"] is True

    grammar = artifact["required_source_grammar"]
    assert grammar["finite_exact_source"] is True
    assert set(grammar["relevant_required_operations"]) == EXPECTED_OPERATIONS
    assert grammar["domain_operation_count"] == 26
    assert grammar["domain_narrowed"] is False
    assert grammar["shared_time_path_phase_parameter_required"] is True
    assert grammar["arbitrary_rational_turn_endpoints_may_occur"] is True
    assert grammar["piecewise_polynomial_path_coefficients_may_occur"] is True

    route = artifact["implemented_bounded_subroute"]
    assert route["id"] == "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW"
    assert route["coefficient_domain"] == "exact rational"
    assert "tan(theta/2)" in route["reduction"]
    assert "MC-032" in route["decision_engine"]
    assert route["established_claims"]
    assert any("arbitrary rational-turn" in claim for claim in route["not_claimed"])
    assert any("polynomial-modulated" in claim for claim in route["not_claimed"])

    boundary = artifact["boundary_controls"]
    for token in (
        "simple crossing", "even-multiplicity tangency", "odd-multiplicity singular crossing",
        "1/1000000", "hidden open-window roots", "non-cardinal", "pole",
        "polynomial-modulated", "parameter projection", "binary-float", "resource refusal",
    ):
        assert any(token in item for item in boundary), f"missing boundary control: {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert "full grammar" in review["reason"]
    forbidden = set(review["conditional_or_unproved_authority_forbidden"])
    assert {"Schanuel's conjecture", "epsilon sign", "finite sampling", "subdivision cap", "timeout", "assume no tangency"} <= forbidden

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    for po in OPEN_POS:
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == "NOT_ESTABLISHED"
    assert effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["next_pre_gate_priority"] == "PB-007-02"

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

    report = REPORT.read_text(encoding="utf-8").lower()
    doc = DOC.read_text(encoding="utf-8").lower()
    for text in (report, doc):
        for token in (
            "pb-007-01", "remains open", "mc-b", "not_established", "26-operation",
            "source/audio/provenance", "tangent", "binary", "pb-007-02",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00701_event_model.py" in workflow
    assert "verify_pb00701.py --contract" in workflow
    assert "verify_pb00701.py --self-test" in workflow


def exact_spec(**overrides):
    spec = {
        "grammar": "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW",
        "cos_coefficients": {},
        "sin_coefficients": {1: "1"},
        "turn_lo": "-1/4",
        "turn_hi": "1/4",
        "source_parameter_id": "source-time-t",
        "witness_half_tan": "0",
    }
    spec.update(overrides)
    return spec


def run_model_controls():
    simple = model.classify_required_analytic_event(exact_spec())
    assert simple["status"] == "CERTIFIED"
    assert simple["distinct_roots_open"] == 1
    assert simple["multiple_roots_open"] == 0
    event = simple["witness_event"]
    assert event["relation"] == "ZERO"
    assert event["multiplicity"] == 1
    assert event["event_kind"] == "SIMPLE_CROSSING"
    assert event["sign_change"] is True

    tangent = model.classify_required_analytic_event(exact_spec(
        cos_coefficients={0: "1", 1: "-1"}, sin_coefficients={}
    ))
    assert tangent["status"] == "CERTIFIED"
    assert tangent["distinct_roots_open"] == 1
    assert tangent["multiple_roots_open"] == 1
    event = tangent["witness_event"]
    assert event["multiplicity"] == 2
    assert event["event_kind"] == "MULTIPLE_TANGENCY"
    assert event["sign_change"] is False

    singular = model.classify_required_analytic_event(exact_spec(
        cos_coefficients={}, sin_coefficients={1: "3/4", 3: "-1/4"}
    ))
    assert singular["status"] == "CERTIFIED"
    event = singular["witness_event"]
    assert event["multiplicity"] == 3
    assert event["event_kind"] == "MULTIPLE_CROSSING"
    assert event["sign_change"] is True

    reduced = model.trig_polynomial_to_tan_half({}, {1: "1"})["numerator"]
    minus = model.EE.peval(reduced, Fraction(-1, 1_000_000))
    plus = model.EE.peval(reduced, Fraction(1, 1_000_000))
    assert minus < 0 < plus

    hidden = model.classify_required_analytic_event(exact_spec(
        cos_coefficients={2: "1"}, sin_coefficients={}, witness_half_tan=None
    ))
    assert hidden["status"] == "CERTIFIED"
    assert hidden["distinct_roots_open"] == 2
    assert hidden["multiple_roots_open"] == 0

    noncardinal = model.classify_required_analytic_event(exact_spec(
        turn_hi="1/6", witness_half_tan=None
    ))
    assert noncardinal["status"] == "BLOCKED"
    assert noncardinal["blocker"] == "PB-007-01"
    assert "NONCARDINAL" in noncardinal["reason"]

    pole = model.classify_required_analytic_event(exact_spec(
        turn_lo="1/4", turn_hi="1/2", witness_half_tan=None
    ))
    assert pole["status"] == "BLOCKED"
    assert pole["blocker"] == "PB-007-01"
    assert "POLE" in pole["reason"]

    modulated = model.classify_required_analytic_event({
        "grammar": "POLYNOMIAL_MODULATED_TRIGONOMETRIC"
    })
    assert modulated == {
        "status": "BLOCKED",
        "reason": "FULL_REQUIRED_ANALYTIC_DECISION_ROUTE_NOT_ESTABLISHED",
        "blocker": "PB-007-01",
    }

    mismatched = model.classify_required_analytic_event(exact_spec(
        parameter_projection="independent-phase"
    ))
    assert mismatched["status"] == "SEMANTIC_BLOCKER"
    assert mismatched["reason"] == "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN"

    float_coeff = model.classify_required_analytic_event(exact_spec(
        sin_coefficients={1: 1.0}
    ))
    assert float_coeff["status"] == "SEMANTIC_BLOCKER"
    assert float_coeff["reason"] == "INVALID_EXACT_TRIGONOMETRIC_POLYNOMIAL"

    float_endpoint = model.classify_required_analytic_event(exact_spec(
        turn_hi=0.25
    ))
    assert float_endpoint["status"] == "SEMANTIC_BLOCKER"
    assert float_endpoint["reason"] == "NONEXACT_TURN_ENDPOINT"

    identity = model.classify_required_analytic_event(exact_spec(
        cos_coefficients={}, sin_coefficients={}
    ))
    assert identity["status"] == "BLOCKED"
    assert identity["blocker"] == "PB-007-01"
    assert "IDENTITY_ZERO" in identity["reason"]

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False


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
    expect_artifact_rejected(lambda a: a["required_source_grammar"].__setitem__("domain_operation_count", 25))
    expect_artifact_rejected(lambda a: a["required_source_grammar"].__setitem__("domain_narrowed", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("positive_volume_material_preserved", False))
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
        print("PB-007-01 follow-up contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-01 exact-event/adversarial controls: PASS")


if __name__ == "__main__":
    main()
