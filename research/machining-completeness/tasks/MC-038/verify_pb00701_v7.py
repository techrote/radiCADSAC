#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00701-coupled-bspline-boundary-v7.json"
REPORT = TASK / "pb00701-report-v7.md"
DOC = ROOT / "docs" / "machining-completeness" / "31-PB00701-COUPLED-BSPLINE-BOUNDARY.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "08834827a5277d782a7ddcd7437a6e1527353620"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-decision-boundary-v3.json":
        "ec2edaef5ef1cf838fc91e68b25147f41525ac2a",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v3.md":
        "03105103fe9d90553e5add492efb073bd8c9ab1e",
    "research/machining-completeness/tasks/MC-038/pb00701_event_model.py":
        "104c0e7a459cd7da5025853b246faff244a5948e",
    "research/machining-completeness/tasks/MC-038/verify_pb00701.py":
        "b555e99f7b5978e6d7640a6389c83b5ce5569038",
    "research/machining-completeness/tasks/MC-038/pb00701-rational-turn-boundary-v6.json":
        "fcff758b5f227452fb65cf273b6e6d8b9f6ab2f8",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v6.md":
        "b782bd980d5b491d0b1bd0a8b95b74704c44767f",
    "research/machining-completeness/tasks/MC-038/pb00701_rational_turn_model.py":
        "a1316ff0f71b2d7aa80807843a74fd8280779cb2",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py":
        "7fb1966247bbe2d46b243d3f01db85efdb2c8c84",
    "research/machining-completeness/tasks/MC-003/report.md":
        "289183f5fa4e2aaa8fc030fac056e6b1d466f620",
    "research/machining-completeness/tasks/MC-007/report.md":
        "e5e922acd742e0774d7a62750a94a8a7ebefd2d3",
    "research/machining-completeness/tasks/MC-022/report.md":
        "3a635abcce148c1f136ed0b7b8917e0815d221c3",
    "research/machining-completeness/tasks/MC-038/gate-scope-retry-v2.json":
        "76094029a264a5ce226694548b27896f9e0cd430",
    "research/machining-completeness/tasks/MC-032/event_engine.py":
        "789a709c5141479a343035d1b7055dd4e53534e1",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_coupled_bspline_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def required_operation_count() -> int:
    return len(load(DOMAIN)["coverage_rule"]["required_operation_ids"])


def validate_artifact(artifact, *, check_repo: bool = True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-coupled-bspline-boundary/7.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 172
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == (
        "EXACT_BSPLINE_PIECEWISE_LOWERING_ESTABLISHED_"
        "GENERAL_NONCONSTANT_COUPLED_ZERO_ROUTE_OPEN"
    )
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, expected_sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == expected_sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
    assert "Cox-de Boor" in extension["lowering"]
    assert "shared source parameter" in extension["source_domain"]
    assert "nonconstant rational polynomial modulation" in extension["residual_branch"]
    assert any("amplitude-dominance" in route for route in extension["exact_subroutes"])
    assert any("v6" in route for route in extension["exact_subroutes"])
    assert any("MC-B" in claim for claim in extension["not_claimed"])

    controls = artifact["boundary_controls"]
    for token in (
        "degree-1", "degree-2", "repeated exact knot", "one-sided",
        "constant-via-equal-control", "stationary cardinal", "amplitude dominance",
        "nonconstant polynomial", "source-parameter", "binary-float", "epsilon",
        "knot/control cardinality", "resource refusal", "26-operation", "MC-B",
    ):
        assert any(token in control for control in controls), f"missing boundary control: {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert "Pfaffian" in review["theorem_context"]
    assert "not asserted as a reduction" in review["continuous_skolem_note"]
    forbidden = set(review["conditional_or_approximate_authority_forbidden"])
    assert {
        "binary floating point", "epsilon sign", "finite sampling", "subdivision cap",
        "timeout", "resource refusal", "unproved transcendence conjecture",
    } <= forbidden

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
    assert effect["next_pre_gate_priority"].startswith("PB-007-03")

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
            "source/audio/provenance", "b-spline", "shared", "binary",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00701_coupled_bspline_model.py" in workflow
    assert "verify_pb00701_v7.py --contract" in workflow
    assert "verify_pb00701_v7.py --self-test" in workflow
    assert "verify_pb00701_v6.py --contract" in workflow
    assert "verify_pb00701_v6.py --self-test" in workflow
    assert "verify_pb00701.py --contract" in workflow
    assert "verify_pb00701.py --self-test" in workflow


def bspline(controls, *, degree=1, knots=None):
    if knots is None:
        knots = ["0", "0", "1", "1"]
    return {"degree": degree, "knots": knots, "controls": [str(v) for v in controls]}


def coupled_spec(**overrides):
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {"1": bspline([0, 1])},
        "sin_splines": {},
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": "0",
        "phase_turn_rate": "1/4",
        "source_parameter_id": "source-time-t",
    }
    value.update(overrides)
    return value


def run_model_controls():
    linear = model.lower_bspline(bspline([0, 1]))
    assert len(linear) == 1
    assert linear[0]["coefficients"] == [Fraction(0), Fraction(1)]
    assert linear[0]["left_limit"] == 0
    assert linear[0]["right_limit"] == 1

    constant = model.lower_bspline(bspline([3, 3]))
    assert constant[0]["coefficients"] == [Fraction(3)]

    quadratic = model.lower_bspline({
        "degree": 2,
        "knots": ["0", "0", "0", "1", "1", "1"],
        "controls": ["0", "1", "0"],
    })
    assert quadratic[0]["coefficients"] == [Fraction(0), Fraction(2), Fraction(-2)]

    discontinuous = model.lower_bspline({
        "degree": 1,
        "knots": ["0", "0", "1/2", "1/2", "1", "1"],
        "controls": ["0", "1", "2", "3"],
    })
    assert len(discontinuous) == 2
    assert discontinuous[0]["source_interval"] == (Fraction(0), Fraction(1, 2))
    assert discontinuous[1]["source_interval"] == (Fraction(1, 2), Fraction(1))
    assert discontinuous[0]["right_limit"] == 1
    assert discontinuous[1]["left_limit"] == 2

    constant_route = model.classify_required_analytic_event(coupled_spec(
        cos_splines={"1": bspline([1, 1])},
    ))
    assert constant_route["status"] == "CERTIFIED"
    span = constant_route["spans"][0]
    assert span["route_kind"] == "DELEGATED_V6_CONSTANT_MODULATION"
    assert span["route"]["status"] == "CERTIFIED"
    assert span["route"]["right_event"]["relation"] == "ZERO"
    assert span["route"]["right_event"]["multiplicity"] == 1

    stationary = model.classify_required_analytic_event(coupled_spec(
        phase_turn_rate="0",
        cos_splines={"1": bspline([0, 1])},
    ))
    assert stationary["status"] == "CERTIFIED"
    route = stationary["spans"][0]["route"]
    assert route["relation"] == "EXACT_STATIONARY_CARDINAL_POLYNOMIAL_EVENT"
    assert route["left_event"]["relation"] == "ZERO"
    assert route["left_event"]["multiplicity"] == 1
    assert route["distinct_roots_open"] == 0

    dominance = model.classify_required_analytic_event(coupled_spec(
        cos_splines={"0": bspline([3, 3]), "1": bspline([0, 1])},
        phase_turn_rate="1",
    ))
    assert dominance["status"] == "CERTIFIED"
    route = dominance["spans"][0]["route"]
    assert route["relation"] == "SEPARATED_BY_EXACT_RATIONAL_AMPLITUDE_DOMINANCE"
    assert route["margin"] == "2"
    assert route["distinct_roots_open"] == 0

    residual = model.classify_required_analytic_event(coupled_spec())
    assert residual["status"] == "BLOCKED"
    assert residual["blocker"] == "PB-007-01"
    route = residual["spans"][0]["route"]
    assert route["blocker"] == "PB-007-01"
    assert route["sampling_or_timeout_is_truth"] is False
    assert route["satisfying_unproved_conjecture_assumed"] is False

    mismatch = model.classify_required_analytic_event(coupled_spec(
        parameter_projection="independent-phase"
    ))
    assert mismatch == {
        "status": "SEMANTIC_BLOCKER",
        "reason": "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN",
    }

    float_control = model.classify_required_analytic_event(coupled_spec(
        cos_splines={"1": {"degree": 1, "knots": ["0", "0", "1", "1"], "controls": [0.0, "1"]}}
    ))
    assert float_control["status"] == "SEMANTIC_BLOCKER"
    assert float_control["reason"] == "INVALID_EXACT_COUPLED_BSPLINE_EVENT_SPEC"

    float_phase = model.classify_required_analytic_event(coupled_spec(phase_turn_rate=0.25))
    assert float_phase["status"] == "SEMANTIC_BLOCKER"

    malformed = model.classify_required_analytic_event(coupled_spec(
        cos_splines={"1": {"degree": 1, "knots": ["0", "0", "1"], "controls": ["0", "1"]}}
    ))
    assert malformed["status"] == "SEMANTIC_BLOCKER"

    multiplicity = model.classify_required_analytic_event(coupled_spec(
        cos_splines={"1": {
            "degree": 1,
            "knots": ["0", "0", "0", "1", "1"],
            "controls": ["0", "1", "2"],
        }}
    ))
    assert multiplicity["status"] == "SEMANTIC_BLOCKER"

    empty = model.classify_required_analytic_event(coupled_spec(parameter_hi="0"))
    assert empty["status"] == "SEMANTIC_BLOCKER"

    epsilon = coupled_spec()
    epsilon["epsilon"] = "1e-9"
    assert model.classify_required_analytic_event(epsilon) == {
        "status": "SEMANTIC_BLOCKER",
        "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD",
    }

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False

    v6_result = model.classify_required_analytic_event({
        "grammar": "RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW",
        "cos_coefficients": {"1": "1"},
        "sin_coefficients": {},
        "turn_lo": "0",
        "turn_hi": "1/4",
        "source_parameter_id": "source-time-t",
    })
    assert v6_result["status"] == "CERTIFIED"
    assert v6_result["right_event"]["relation"] == "ZERO"

    v3_result = model.classify_required_analytic_event({
        "grammar": "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW",
        "cos_coefficients": {},
        "sin_coefficients": {"1": "1"},
        "turn_lo": "-1/4",
        "turn_hi": "1/4",
        "source_parameter_id": "source-time-t",
        "witness_half_tan": "0",
    })
    assert v3_result["status"] == "CERTIFIED"


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
    expect_artifact_rejected(
        lambda a: a["protected_semantics"].__setitem__("exact_time_path_phase_correlation_preserved", False)
    )
    expect_artifact_rejected(
        lambda a: a["full_blocker_review"].__setitem__("not_an_impossibility_theorem", False)
    )
    expect_artifact_rejected(
        lambda a: a["programme_effect"].__setitem__("next_pre_gate_priority", "MC-B")
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("select --contract and/or --self-test")

    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v7 contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-01 v7 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
