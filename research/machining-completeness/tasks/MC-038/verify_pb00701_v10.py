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
ARTIFACT = TASK / "pb00701-dual-ratio-boundary-v10.json"
REPORT = TASK / "pb00701-report-v10.md"
DOC = ROOT / "docs" / "machining-completeness" / "36-PB00701-DUAL-PROJECTIVE-RATIO.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "a5f5d20623f6437fbed0e77c26c73d0a30641c54"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import verify_pb00701_v9 as verify_v9  # noqa: E402
import pb00701_dual_ratio_model as model  # noqa: E402

EXPECTED_HISTORY = dict(verify_v9.EXPECTED_HISTORY)
EXPECTED_HISTORY.update({
    "research/machining-completeness/tasks/MC-038/pb00701-monotone-ratio-boundary-v9.json": "8982105e5e94e29b5af45b7b18a6ca6831d78e20",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v9.md": "e10bb13f3ea65e9c63e708420da5facaf2644fd8",
    "research/machining-completeness/tasks/MC-038/pb00701_monotone_ratio_model.py": "322035132bb05a9dbdf58f2d1f022394ce94e92f",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v9.py": "6b5bb32218c4d8f4a54861957559cc07533246a5",
    "docs/machining-completeness/35-PB00701-MONOTONE-RATIO-REDUCTION.md": "1f2bb887d3fb70a978748ec808300368548a4282",
})


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def bspline(controls, *, degree=1, knots=None):
    if knots is None:
        knots = ["0", "0", "1", "1"]
    return {"degree": degree, "knots": knots, "controls": [str(v) for v in controls]}


def linear(intercept, slope):
    intercept = Fraction(intercept)
    slope = Fraction(slope)
    return bspline([intercept, intercept + slope])


def constant(value):
    return bspline([value, value])


def quadratic_turning():
    return bspline(
        [Fraction(1, 4), Fraction(-1, 4), Fraction(1, 4)],
        degree=2,
        knots=["0", "0", "0", "1", "1", "1"],
    )


def spec(cos=None, sin=None, *, offset="0", rate="1/8", **extra):
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


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-dual-ratio-boundary/10.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 182
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_AND_ENDPOINT_SIMPLE_SUBGRAMMAR_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_REDUCTION"
    assert "tan" in extension["tangent_chart"]
    assert "cot" in extension["cotangent_chart"]
    assert "D=A*B'-A'*B" in extension["common_derivative_authority"]
    assert "u=n" in extension["phase_partition"]
    assert "pi=D/(u'*(A^2+B^2))" in extension["endpoint_route"]

    controls = artifact["boundary_controls"]
    for token in (
        "B-denominator-zero", "B=0", "v9", "left external endpoint", "right external endpoint",
        "1/1000000", "cotangent-pole", "neither A nor B", "derivative sign", "multiple active harmonics",
        "v8", "source-parameter", "binary-float", "epsilon", "forged", "resource refusal",
        "historical", "26-operation", "MC-B",
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
    assert len(load(DOMAIN)["coverage_rule"]["required_operation_ids"]) == 26
    for path, sha in EXPECTED_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"historical evidence drift: {path}"
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
            "pb-007-01", "remains open", "cotangent", "endpoint", "mc-b",
            "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701_v9.py --contract", "pb00701_dual_ratio_model.py",
        "verify_pb00701_v10.py --contract", "verify_pb00701_v10.py --self-test",
    ):
        assert token in workflow


def v10_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span["route_kind"] == "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    ]
    assert routes, result
    route = routes[0]
    assert route["status"] == "CERTIFIED"
    assert route["relation"] == "EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_EVENT_DECISION"
    return route


def blocked_v10_route(result, reason):
    assert result["status"] == "BLOCKED", result
    routes = [
        span["route"] for span in result["spans"]
        if span["route_kind"] == "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    ]
    assert routes, result
    assert routes[0]["reason"] == reason, routes[0]
    return routes[0]


def run_model_controls():
    cot = v10_route(model.classify_required_analytic_event(spec(
        cos={"1": constant(1)},
        sin={"1": linear(Fraction(1, 2), -1)},
        offset="1/4", rate="1/8",
    )))
    assert cot["projective_chart"] == "COTANGENT"
    assert cot["ratio_denominator_certificate"]["distinct_roots_open"] == 0
    assert cot["ratio_monotonicity_certificate"]["strict_projective_function_direction"] == "DECREASING"
    assert cot["open_roots"]["distinct"] == 1
    exact_b_zero = model._finite_cot_comparison(
        [Fraction(1)], [Fraction(1, 2), Fraction(-1)],
        Fraction(1, 2), Fraction(1, 4), Fraction(1, 2),
    )
    assert exact_b_zero["status"] == "DECIDED"
    assert exact_b_zero["relation"] != "ZERO"

    tangent = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(-1, 2), 1)}, sin={"1": constant(1)},
    ))
    assert tangent["status"] == "CERTIFIED"
    assert tangent["spans"][0]["route_kind"] == "PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO"

    left_endpoint = v10_route(model.classify_required_analytic_event(spec(
        cos={"1": linear(0, 1)}, sin={"1": constant(1)},
    )))
    assert left_endpoint["projective_chart"] == "TANGENT"
    assert len(left_endpoint["endpoint_events"]) == 1
    assert left_endpoint["endpoint_events"][0]["side"] == "left"
    assert left_endpoint["endpoint_events"][0]["multiplicity"] == 1
    assert left_endpoint["endpoint_events"][0]["numeric_pi_used"] is False
    assert left_endpoint["all_certified_events"]["multiplicity_sum"] == 1

    right_endpoint = v10_route(model.classify_required_analytic_event(spec(
        cos={"1": linear(-1, 1)}, sin={"1": constant(1)},
        offset="-1/8", rate="1/8",
    )))
    assert len(right_endpoint["endpoint_events"]) == 1
    assert right_endpoint["endpoint_events"][0]["side"] == "right"
    assert right_endpoint["endpoint_events"][0]["multiplicity"] == 1

    above = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(1, 1000000), 1)}, sin={"1": constant(1)},
    ))
    below = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(-1, 1000000), 1)}, sin={"1": constant(1)},
    ))
    assert above["status"] == "CERTIFIED" and below["status"] == "CERTIFIED"
    assert above["spans"][0]["route"]["open_roots"]["distinct"] == 0
    assert below["spans"][0]["route"]["open_roots"]["distinct"] == 1

    poles = v10_route(model.classify_required_analytic_event(spec(
        cos={"1": constant(1)}, sin={"1": linear(Fraction(1, 2), -1)},
        offset="-1/2", rate="2",
    )))
    assert poles["projective_chart"] == "COTANGENT"
    assert poles["projective_pole_boundaries"] == ["0", "1/4", "1/2", "3/4", "1"]
    assert len(poles["internal_pole_events"]) == 3
    assert all(not event["original_event_zero"] for event in poles["internal_pole_events"])

    neither = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(-1, 3), 1)},
        sin={"1": linear(Fraction(2, 3), -1)},
    ))
    blocked_v10_route(neither, "NO_ZERO_FREE_PROJECTIVE_COMPONENT_FOR_DUAL_RATIO_ROUTE")

    nonmonotone = model.classify_required_analytic_event(spec(
        cos={"1": constant(1)}, sin={"1": quadratic_turning()},
    ))
    blocked_v10_route(nonmonotone, "OPPOSED_DUAL_PROJECTIVE_MONOTONICITY_NOT_CERTIFIED")

    multiharmonic = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(-1, 2), 1), "2": constant(1)},
        sin={"1": constant(1)},
    ))
    assert multiharmonic["status"] == "BLOCKED"
    assert multiharmonic["blocker"] == "PB-007-01"
    assert multiharmonic["spans"][0]["route_kind"] == "PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY"

    factor = linear(Fraction(-1, 2), 1)
    common = model.classify_required_analytic_event(spec(
        cos={"1": factor}, sin={"1": linear(-1, 2)},
    ))
    assert common["status"] == "CERTIFIED"
    assert common["spans"][0]["route_kind"] == "PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION"

    mismatch = model.classify_required_analytic_event(spec(
        cos={"1": constant(1)}, sin={"1": linear(Fraction(1, 2), -1)},
        parameter_projection="other-source",
    ))
    assert mismatch["status"] == "SEMANTIC_BLOCKER"

    float_input = model.classify_required_analytic_event(spec(
        cos={"1": constant(1)},
        sin={"1": {"degree": 1, "knots": ["0", "0", "1", "1"], "controls": [0.5, "-1/2"]}},
    ))
    assert float_input["status"] == "SEMANTIC_BLOCKER"

    epsilon = spec(
        cos={"1": constant(1)}, sin={"1": linear(Fraction(1, 2), -1)}, epsilon="1e-9",
    )
    assert model.classify_required_analytic_event(epsilon)["reason"] == "UNREVIEWED_EVENT_AUTHORITY_FIELD"

    forged = spec(
        cos={"1": constant(1)}, sin={"1": linear(Fraction(1, 2), -1)},
        projective_chart_certificate={"trusted": True}, endpoint_multiplicity=1,
    )
    assert model.classify_required_analytic_event(forged)["reason"] == "UNREVIEWED_EVENT_AUTHORITY_FIELD"

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
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("domain_operation_count", 25))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("domain_narrowed", True))
    expect_artifact_rejected(lambda a: a["implemented_extension"].__setitem__("endpoint_route", "caller says simple"))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["historical_evidence"][-1].__setitem__("git_blob_sha1", "forged"))
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("exact_time_path_phase_correlation_preserved", False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("select --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v10 contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-01 v10 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
