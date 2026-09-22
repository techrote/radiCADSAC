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
ARTIFACT = TASK / "pb00701-common-factor-boundary-v8.json"
REPORT = TASK / "pb00701-report-v8.md"
DOC = ROOT / "docs" / "machining-completeness" / "34-PB00701-COMMON-FACTOR-REDUCTION.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "c61425cefba46deea9b9012ec833f80621d15163"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-decision-boundary-v3.json": "ec2edaef5ef1cf838fc91e68b25147f41525ac2a",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v3.md": "03105103fe9d90553e5add492efb073bd8c9ab1e",
    "research/machining-completeness/tasks/MC-038/pb00701_event_model.py": "104c0e7a459cd7da5025853b246faff244a5948e",
    "research/machining-completeness/tasks/MC-038/verify_pb00701.py": "b555e99f7b5978e6d7640a6389c83b5ce5569038",
    "research/machining-completeness/tasks/MC-038/pb00701-rational-turn-boundary-v6.json": "fcff758b5f227452fb65cf273b6e6d8b9f6ab2f8",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v6.md": "b782bd980d5b491d0b1bd0a8b95b74704c44767f",
    "research/machining-completeness/tasks/MC-038/pb00701_rational_turn_model.py": "a1316ff0f71b2d7aa80807843a74fd8280779cb2",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py": "7fb1966247bbe2d46b243d3f01db85efdb2c8c84",
    "research/machining-completeness/tasks/MC-038/pb00701-coupled-bspline-boundary-v7.json": "e75c0a0ab48a9a4eba7249e203a50f7366973ba3",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v7.md": "31755f3dbb2ea5a21abd3a979b9875cd259984cd",
    "research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py": "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v7.py": "7a2f08e578d0f649fd004d30691aea28bd3ffd2d",
    "docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md": "6005fc55e2d18e71639e6bc31cfbc1597bf4a915",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_common_factor_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def bspline(controls, *, degree=1, knots=None):
    if knots is None:
        knots = ["0", "0", "1", "1"]
    return {"degree": degree, "knots": knots, "controls": [str(v) for v in controls]}


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


def linear_factor(scale=1):
    scale = Fraction(scale)
    return bspline([-scale / 2, scale / 2])


def repeated_factor():
    return bspline([Fraction(1, 4), Fraction(-1, 4), Fraction(1, 4)], degree=2,
                   knots=["0", "0", "0", "1", "1", "1"])


def irrational_factor():
    return bspline([Fraction(-1, 2), Fraction(-1, 2), Fraction(1, 2)], degree=2,
                   knots=["0", "0", "0", "1", "1", "1"])


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-common-factor-boundary/8.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 178
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_COMMON_FACTOR_SUBGRAMMAR_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_COMMON_FACTOR_COUPLED_ANALYTIC_REDUCTION"
    assert "GCD" in extension["factorization"]
    assert "degree-zero" in extension["factorization"]
    assert "v6" in extension["trig_route"]
    assert "Gelfond-Schneider" in extension["coincidence_route"]
    assert extension["theorem_scope_generalized"] is False

    controls = artifact["boundary_controls"]
    for token in (
        "simple common-factor", "repeated common-factor", "rational factor/trig coincidence",
        "algebraic-irrational", "endpoint", "phase-pole", "constant common factor",
        "non-common modulation", "zero trig", "zero phase rate", "source-parameter",
        "binary-float", "epsilon", "forged quotient", "resource refusal", "26-operation", "MC-B",
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

    resources = artifact["resources"]
    assert resources == {
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
        for token in ("pb-007-01", "remains open", "common factor", "gelfond-schneider", "mc-b", "not_established", "26", "source/audio/provenance"):
            assert token in text, f"documentation missing {token}"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701.py --contract", "verify_pb00701_v6.py --contract", "verify_pb00701_v7.py --contract",
        "pb00701_common_factor_model.py", "verify_pb00701_v8.py --contract", "verify_pb00701_v8.py --self-test",
    ):
        assert token in workflow


def common_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [span["route"] for span in result["spans"] if span["route_kind"] == "PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION"]
    assert routes, result
    return routes[0]


def run_model_controls():
    simple = common_route(model.classify_required_analytic_event(spec(
        cos={"1": linear_factor(1)}, sin={"1": linear_factor(2)}
    )))
    assert simple["common_factor_degree"] == 1
    assert simple["factorization_proof"]["all_remainders_zero"] is True
    assert simple["factorization_proof"]["all_quotients_degree_zero"] is True
    assert simple["factor_open_roots"]["distinct"] == 1

    repeated = common_route(model.classify_required_analytic_event(spec(
        cos={"1": repeated_factor()}, rate="1/8"
    )))
    assert repeated["factor_open_roots"]["distinct"] == 1
    assert repeated["factor_open_roots"]["multiplicity_sum"] == 2
    assert repeated["factor_open_roots"]["multiple_distinct"] == 1

    coincidence = common_route(model.classify_required_analytic_event(spec(
        sin={"1": linear_factor(1)}, offset="-1/4", rate="1/2"
    )))
    assert coincidence["coincidences"] == [{
        "source": "1/2", "factor_multiplicity": 1, "trig_multiplicity": 1,
        "product_multiplicity": 2, "checked_exactly": True,
    }]
    assert coincidence["product_open_roots"]["distinct"] == 1
    assert coincidence["product_open_roots"]["multiplicity_sum"] == 2
    assert coincidence["product_open_roots"]["multiple_distinct"] == 1

    irrational = common_route(model.classify_required_analytic_event(spec(
        cos={"1": irrational_factor()}, rate="1/8"
    )))
    assert irrational["factor_open_roots"]["algebraic_irrational_distinct"] == 1
    assert irrational["coincidences"] == []
    assert irrational["coincidence_authority"]["algebraic_irrational_source_roots_disjoint_by"] == "GELFOND_SCHNEIDER"
    assert irrational["coincidence_authority"]["generalization_outside_grammar_forbidden"] is True

    endpoint = common_route(model.classify_required_analytic_event(spec(
        sin={"1": bspline([0, 1])}, offset="0", rate="1/4"
    )))
    assert endpoint["left_event"]["relation"] == "ZERO"
    assert endpoint["left_event"]["factor_multiplicity"] == 1
    assert endpoint["left_event"]["trig_multiplicity"] == 1
    assert endpoint["left_event"]["product_multiplicity"] == 2

    pole = common_route(model.classify_required_analytic_event(spec(
        sin={"1": linear_factor(1)}, offset="0", rate="2"
    )))
    assert pole["phase_chart_boundaries"] == ["0", "1/4", "1/2", "3/4", "1"]
    assert len(pole["pole_safe_charts"]) == 4
    assert all(chart["status"] == "CERTIFIED" for chart in pole["pole_safe_charts"])

    constant = model.classify_required_analytic_event(spec(cos={"1": bspline([1, 1])}))
    assert constant["status"] == "CERTIFIED"
    assert constant["spans"][0]["route_kind"] == "DELEGATED_V6_CONSTANT_MODULATION"

    noncommon = model.classify_required_analytic_event(spec(
        cos={"1": linear_factor(1)}, sin={"1": bspline([0, 1])}
    ))
    assert noncommon["status"] == "BLOCKED"
    assert noncommon["blocker"] == "PB-007-01"
    assert noncommon["spans"][0]["route_kind"] == "PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY"

    zero_trig = model.classify_required_analytic_event(spec(cos={"1": bspline([0, 0])}))
    assert zero_trig["status"] == "BLOCKED"
    assert zero_trig["blocker"] == "PB-007-01"

    stationary = model.classify_required_analytic_event(spec(cos={"1": linear_factor(1)}, rate="0"))
    assert stationary["status"] == "CERTIFIED"
    assert stationary["spans"][0]["route_kind"] == "EXACT_STATIONARY_PHASE_POLYNOMIAL"

    mismatch = model.classify_required_analytic_event(spec(
        cos={"1": linear_factor(1)}, parameter_projection="other"
    ))
    assert mismatch["status"] == "SEMANTIC_BLOCKER"

    float_input = model.classify_required_analytic_event(spec(
        cos={"1": {"degree": 1, "knots": ["0", "0", "1", "1"], "controls": [0.0, "1"]}}
    ))
    assert float_input["status"] == "SEMANTIC_BLOCKER"

    epsilon = spec(cos={"1": linear_factor(1)})
    epsilon["epsilon"] = "1e-9"
    assert model.classify_required_analytic_event(epsilon)["reason"] == "UNREVIEWED_EVENT_AUTHORITY_FIELD"

    forged = spec(cos={"1": linear_factor(1)})
    forged["common_factor"] = ["-1/2", "1"]
    forged["quotients"] = {"cos:1": "1"}
    assert model.classify_required_analytic_event(forged)["reason"] == "UNREVIEWED_EVENT_AUTHORITY_FIELD"

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL" and refusal["is_truth_value"] is False


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
    expect_artifact_rejected(lambda a: a["implemented_extension"].__setitem__("theorem_scope_generalized", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["historical_evidence"][0].__setitem__("git_blob_sha1", "forged"))
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
        print("PB-007-01 v8 contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-01 v8 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
