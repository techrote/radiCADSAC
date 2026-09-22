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
ARTIFACT = TASK / "pb00701-phase-dominance-boundary-v11.json"
REPORT = TASK / "pb00701-report-v11.md"
DOC = ROOT / "docs" / "machining-completeness" / "37-PB00701-PHASE-DOMINANCE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "d136ea93d6473b3ce48dae4c70985b0545a9b554"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V10_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-dual-ratio-boundary-v10.json": "e96a6feba54fa859001e9e7f814eaf709a714b2b",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v10.md": "b53ba5d4cab6e93af529f93a3d20ce5e792900eb",
    "research/machining-completeness/tasks/MC-038/pb00701_dual_ratio_model.py": "7644219ae12011d3c5493104e6d752cf87bc6923",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v10.py": "401c7bb4b49537ed27aad7fa972b81cab9fef94d",
    "docs/machining-completeness/36-PB00701-DUAL-PROJECTIVE-RATIO.md": "1215e00ea728640d4680fb64e0e4c7298b82d9c3",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v10 as verify_v10  # noqa: E402
import pb00701_phase_dominance_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def bspline(controls, *, degree=1, knots=None):
    if knots is None:
        knots = ["0", "0", "1", "1"]
    return {
        "degree": degree,
        "knots": knots,
        "controls": [str(v) for v in controls],
    }


def linear(intercept, slope):
    intercept = Fraction(intercept)
    slope = Fraction(slope)
    return bspline([intercept, intercept + slope])


def constant(value):
    return bspline([value, value])


def quadratic_controls(c0, c1, c2):
    return bspline(
        [Fraction(c0), Fraction(c1), Fraction(c2)],
        degree=2,
        knots=["0", "0", "0", "1", "1", "1"],
    )


def turning_quadratic():
    # s^2-s+1/8; D=1-2s against B=1, so D changes sign at s=1/2.
    return quadratic_controls(Fraction(1, 8), Fraction(-3, 8), Fraction(1, 8))


def endpoint_turning_quadratic():
    # s^2-s; same changing D, with exact A(0)=0 endpoint event at phase zero.
    return quadratic_controls(0, Fraction(-1, 2), 0)


def spec(cos=None, sin=None, *, offset="0", rate="1/4", **extra):
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": cos or {},
        "sin_splines": sin or {},
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "source-time-t",
    }
    value.update(extra)
    return value


def assert_raises(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected adversarial mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-phase-dominance-boundary/11.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 184
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == (
        "EXACT_PHASE_DOMINATED_NONMONOTONE_SINGLE_HARMONIC_SUBGRAMMAR_ESTABLISHED_"
        "GENERAL_COUPLED_ROUTE_OPEN"
    )
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v10_evidence"]}
    assert set(history) == set(EXPECTED_V10_HISTORY)
    for path, sha in EXPECTED_V10_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_PHASE_DERIVATIVE_DOMINANCE_SINGLE_HARMONIC_REDUCTION"
    assert "3*abs(u')" in extension["dominance_predicate"]
    assert "pi>3" in extension["transcendental_theorem"]
    assert "v11 upgrades only" in extension["routing"]

    controls = artifact["boundary_controls"]
    for token in (
        "tangent-chart", "cotangent-chart", "decreasing", "1/1000000",
        "threshold equality", "pole", "endpoint", "neither A nor B",
        "multiple active harmonics", "source-parameter", "binary-float", "epsilon",
        "forged", "resource refusal", "historical", "26-operation", "MC-B",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["residual_branch"]
    assert review["not_an_impossibility_theorem"] is True

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
    assert effect["next_pre_gate_priority"].startswith("PB-007-01")

    assert artifact["resources"] == {
        "native_campaign_run": False,
        "paid_campaign_run": False,
        "production_authorized": False,
        "expensive_execution_authorized": False,
    }
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    verify_v10.validate_artifact(verify_v10.load(verify_v10.ARTIFACT))
    for path, sha in EXPECTED_V10_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v10 historical evidence drift: {path}"
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
            "pb-007-01", "remains open", "pi > 3", "phase-dominance",
            "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701_v10.py --contract",
        "pb00701_phase_dominance_model.py",
        "verify_pb00701_v11.py --contract",
        "verify_pb00701_v11.py --self-test",
    ):
        assert token in workflow


def v11_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"]
        for span in result["spans"]
        if span["route_kind"]
        == "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
    ]
    assert routes, result
    route = routes[0]
    assert route["status"] == "CERTIFIED"
    assert route["relation"] == "EXACT_PHASE_DOMINATED_SINGLE_HARMONIC_EVENT_DECISION"
    return route


def run_model_controls():
    tangent_spec = spec(
        cos={"1": turning_quadratic()},
        sin={"1": constant(1)},
        offset="-1/12",
        rate="1/4",
    )
    old_tangent = verify_v10.model.classify_required_analytic_event(tangent_spec)
    assert old_tangent["status"] == "BLOCKED"
    assert old_tangent["spans"][0]["route"]["reason"] == (
        "OPPOSED_RATIO_MONOTONICITY_NOT_CERTIFIED"
    )
    tangent = v11_route(model.classify_required_analytic_event(tangent_spec))
    assert tangent["projective_chart"] == "TANGENT"
    assert tangent["phase_dominance_certificate"]["ratio_derivative_distinct_roots_open"] == 1
    assert tangent["phase_dominance_certificate"]["numeric_pi_used"] is False
    assert tangent["open_roots"]["distinct"] == 1

    cot_spec = spec(
        cos={"1": constant(1)},
        sin={"1": turning_quadratic()},
        offset="1/8",
        rate="1/4",
    )
    old_cot = verify_v10.model.classify_required_analytic_event(cot_spec)
    assert old_cot["status"] == "BLOCKED"
    assert old_cot["spans"][0]["route"]["reason"] == (
        "OPPOSED_DUAL_PROJECTIVE_MONOTONICITY_NOT_CERTIFIED"
    )
    cot = v11_route(model.classify_required_analytic_event(cot_spec))
    assert cot["projective_chart"] == "COTANGENT"
    assert cot["phase_dominance_certificate"]["ratio_derivative_distinct_roots_open"] == 1
    assert cot["open_roots"]["distinct"] == 1

    decreasing = v11_route(model.classify_required_analytic_event(spec(
        cos={"1": turning_quadratic()},
        sin={"1": constant(1)},
        offset="1/6",
        rate="-1/4",
    )))
    assert decreasing["phase_dominance_certificate"]["strict_projective_function_direction"] == "DECREASING"
    assert decreasing["open_roots"]["distinct"] == 1

    eps = Fraction(1, 1000000)
    below = model._phase_dominance_certificate(
        [Fraction(2), -(Fraction(3, 2) - eps)],
        [Fraction(1)], Fraction(1, 2), "TANGENT"
    )
    exact = model._phase_dominance_certificate(
        [Fraction(2), -Fraction(3, 2)],
        [Fraction(1)], Fraction(1, 2), "TANGENT"
    )
    above = model._phase_dominance_certificate(
        [Fraction(2), -(Fraction(3, 2) + eps)],
        [Fraction(1)], Fraction(1, 2), "TANGENT"
    )
    assert below is not None
    assert below["dominance_polynomial_certificate"]["left_value"] == "1/1000000"
    assert exact is None and above is None

    poles = v11_route(model.classify_required_analytic_event(spec(
        cos={"1": turning_quadratic()},
        sin={"1": constant(1)},
        offset="0",
        rate="2",
    )))
    assert len(poles["internal_pole_events"]) == 4
    assert all(not event["original_event_zero"] for event in poles["internal_pole_events"])

    endpoint = v11_route(model.classify_required_analytic_event(spec(
        cos={"1": endpoint_turning_quadratic()},
        sin={"1": constant(1)},
        offset="0",
        rate="1/4",
    )))
    assert endpoint["endpoint_events"]
    assert endpoint["endpoint_events"][0]["side"] == "left"
    assert endpoint["endpoint_events"][0]["multiplicity"] == 1

    neither = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(-1, 3), 1)},
        sin={"1": linear(Fraction(2, 3), -1)},
    ))
    assert neither["status"] == "BLOCKED"
    assert neither["blocker"] == "PB-007-01"

    multiharmonic = model.classify_required_analytic_event(spec(
        cos={"1": turning_quadratic(), "2": constant(1)},
        sin={"1": constant(1)},
    ))
    assert multiharmonic["status"] == "BLOCKED"
    assert multiharmonic["blocker"] == "PB-007-01"

    mismatch = model.classify_required_analytic_event(spec(
        cos={"1": turning_quadratic()},
        sin={"1": constant(1)},
        parameter_projection="other-source",
    ))
    assert mismatch["status"] == "SEMANTIC_BLOCKER"

    float_input = model.classify_required_analytic_event(spec(
        cos={"1": {
            "degree": 1,
            "knots": ["0", "0", "1", "1"],
            "controls": [0.5, "-1/2"],
        }},
        sin={"1": constant(1)},
    ))
    assert float_input["status"] == "SEMANTIC_BLOCKER"

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False


def run_adversarial_controls():
    artifact = load(ARTIFACT)
    mutations = []

    promoted = copy.deepcopy(artifact)
    promoted["gate_state"] = "ESTABLISHED"
    mutations.append(promoted)

    shrunk = copy.deepcopy(artifact)
    shrunk["programme_effect"]["domain_operation_count"] = 25
    mutations.append(shrunk)

    closed = copy.deepcopy(artifact)
    closed["programme_effect"]["PB-007-01"] = "CLOSED"
    mutations.append(closed)

    forged = copy.deepcopy(artifact)
    forged["implemented_extension"]["transcendental_theorem"] = "numeric pi sample"
    mutations.append(forged)

    history = copy.deepcopy(artifact)
    history["historical_v10_evidence"][0]["git_blob_sha1"] = "0" * 40
    mutations.append(history)

    for mutation in mutations:
        assert_raises(lambda m=mutation: validate_artifact(m, check_repo=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("select --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT))
        print("PB-007-01 v11 contract: PASS")
    if args.self_test:
        validate_artifact(load(ARTIFACT))
        run_model_controls()
        run_adversarial_controls()
        print("PB-007-01 v11 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
