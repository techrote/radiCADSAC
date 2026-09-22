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
MODEL = TASK / "pb00701_common_factor_model.py"

EXPECTED_BASE = "c61425cefba46deea9b9012ec833f80621d15163"
EXPECTED_MODEL_SHA = "7fef9b3a4673e4b64b8fb14833e425733b34f954"
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
    "research/machining-completeness/tasks/MC-038/pb00701-coupled-bspline-boundary-v7.json":
        "e75c0a0ab48a9a4eba7249e203a50f7366973ba3",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v7.md":
        "31755f3dbb2ea5a21abd3a979b9875cd259984cd",
    "research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py":
        "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v7.py":
        "7a2f08e578d0f649fd004d30691aea28bd3ffd2d",
    "docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md":
        "6005fc55e2d18e71639e6bc31cfbc1597bf4a915",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import pb00701_common_factor_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def required_operation_count() -> int:
    return len(load(DOMAIN)["coverage_rule"]["required_operation_ids"])


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-common-factor-boundary/8.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 178
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == (
        "EXACT_COMMON_POLYNOMIAL_FACTOR_SUBROUTE_ESTABLISHED_"
        "GENERAL_COUPLED_ZERO_ROUTE_OPEN"
    )
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, expected_sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == expected_sha
        assert history[path]["preserved"] is True

    implementation = artifact["implementation"]
    assert implementation["model_git_blob_sha1"] == EXPECTED_MODEL_SHA
    assert implementation["input_grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
    assert "GCD" in implementation["factor_authority"]
    assert "zero-remainder" in implementation["factor_authority"]
    assert "quarter-turn" in implementation["phase_partition"]
    assert "MC-032" in implementation["polynomial_authority"]
    assert "v6" in implementation["trigonometric_authority"]
    assert "Gelfond-Schneider" in implementation["coincidence_authority"]

    theorem = artifact["theorem_boundary"]
    assert theorem["theorem"] == "Gelfond-Schneider"
    assert theorem["source"].startswith("https://encyclopediaofmath.org/")
    assert "(-1)^(2*turn)" in theorem["recorded_application"]
    assert any("nonzero phase rate" in item for item in theorem["preconditions"])
    assert any("general" in item.lower() for item in theorem["not_claimed"])
    assert any("MC-B" in item for item in theorem["not_claimed"])

    controls = artifact["boundary_controls"]
    for token in (
        "simple common-factor", "repeated common-factor", "rational common-factor",
        "algebraic-irrational", "endpoint", "pole-safe", "constant common factor",
        "non-common", "zero phase rate", "source-parameter", "binary-float",
        "forged", "resource refusal", "26-operation", "historical", "MC-B",
    ):
        assert any(token in control for control in controls), f"missing control {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert review["sampling_refinement_timeout_or_conjecture_is_not_truth"] is True
    assert "nonproportional" in review["reason"]

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

    assert all(value is False for value in artifact["resources"].values())
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    assert git_blob_sha(MODEL) == EXPECTED_MODEL_SHA, "v8 model/artifact binding drift"
    for path, expected_sha in EXPECTED_HISTORY.items():
        assert git_blob_sha(ROOT / path) == expected_sha, f"historical evidence drift: {path}"
    assert required_operation_count() == 26, "frozen 26-operation denominator drift"

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
            "source/audio/provenance", "common", "gelfond", "shared", "binary",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "verify_pb00701.py --contract" in workflow
    assert "verify_pb00701_v6.py --contract" in workflow
    assert "verify_pb00701_v7.py --contract" in workflow
    assert "pb00701_common_factor_model.py" in workflow
    assert "verify_pb00701_v8.py --contract" in workflow
    assert "verify_pb00701_v8.py --self-test" in workflow


def bspline(controls, *, degree=1):
    knots = ["0"] * (degree + 1) + ["1"] * (degree + 1)
    return {
        "degree": degree,
        "knots": knots,
        "controls": [str(value) for value in controls],
    }


def common_spec(**overrides):
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {"1": bspline(["-1/3", "2/3"])},
        "sin_splines": {},
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": "0",
        "phase_turn_rate": "1/4",
        "source_parameter_id": "source-time-t",
    }
    value.update(overrides)
    return value


def certified_routes(result):
    return [
        span["route"]
        for span in result.get("spans", [])
        if span["route"].get("status") == "CERTIFIED"
        and span.get("route_kind") == "EXACT_COMMON_POLYNOMIAL_FACTOR_PRODUCT"
    ]


def run_model_controls():
    simple = model.classify_required_analytic_event(common_spec())
    assert simple["status"] == "CERTIFIED"
    assert simple["relation"] == "FINITE_EXACT_COMMON_FACTOR_PRODUCT_DECISION"
    route = certified_routes(simple)[0]
    assert route["factor_distinct_roots_open"] == 1
    assert route["factor_multiple_roots_open"] == 0
    assert route["distinct_roots_open"] == 1
    assert route["multiple_roots_open"] == 0
    assert route["rational_factor_roots_open"] == ["1/3"]
    assert route["right_event"]["relation"] == "ZERO"
    assert route["right_event"]["multiplicity"] == 1

    repeated = model.classify_required_analytic_event(common_spec(
        cos_splines={"1": bspline(["1/4", "-1/4", "1/4"], degree=2)},
        phase_turn_rate="1/8",
    ))
    assert repeated["status"] == "CERTIFIED"
    route = certified_routes(repeated)[0]
    assert route["factor_distinct_roots_open"] == 1
    assert route["factor_multiple_roots_open"] == 1
    assert route["distinct_roots_open"] == 1
    assert route["multiple_roots_open"] == 1

    coincidence = model.classify_required_analytic_event(common_spec(
        cos_splines={
            "0": bspline(["1/2", "-1/2"]),
            "1": bspline(["-1", "1"]),
        },
        phase_turn_rate="1/3",
    ))
    assert coincidence["status"] == "CERTIFIED"
    coincident_routes = [route for route in certified_routes(coincidence) if route["coincident_roots"]]
    assert len(coincident_routes) == 1
    route = coincident_routes[0]
    assert route["distinct_roots_open"] == 1
    assert route["multiple_roots_open"] == 1
    witness = route["coincident_roots"][0]
    assert witness["source_parameter"] == "1/2"
    assert witness["phase_turn"] == "1/6"
    assert witness["factor_multiplicity"] == 1
    assert witness["trig_multiplicity"] == 1
    assert witness["product_multiplicity"] == 2

    irrational = model.classify_required_analytic_event(common_spec(
        cos_splines={"1": bspline(["-1/2", "-1/2", "1/2"], degree=2)},
        phase_turn_rate="1/8",
    ))
    assert irrational["status"] == "CERTIFIED"
    route = certified_routes(irrational)[0]
    assert route["factor_distinct_roots_open"] == 1
    assert route["rational_factor_roots_open"] == []
    assert route["irrational_algebraic_factor_roots_open"] == 1
    assert route["irrational_disjointness"]["theorem"] == "GELFOND_SCHNEIDER"
    assert route["irrational_disjointness"]["generalized_beyond_recorded_grammar"] is False

    endpoint = model.classify_required_analytic_event(common_spec(
        cos_splines={"1": bspline(["0", "1"])},
        phase_turn_rate="1/8",
    ))
    assert endpoint["status"] == "CERTIFIED"
    route = certified_routes(endpoint)[0]
    assert route["left_event"]["relation"] == "ZERO"
    assert route["left_event"]["multiplicity"] == 1

    pole_partition = model.classify_required_analytic_event(common_spec(phase_turn_rate="1"))
    assert pole_partition["status"] == "CERTIFIED"
    assert pole_partition["partition_boundaries"] == ["0", "1/4", "1/2", "3/4", "1"]
    assert len(certified_routes(pole_partition)) == 4
    for route in certified_routes(pole_partition):
        assert route["trig_certificate"]["status"] == "CERTIFIED"
        assert "chart_shift_turn" in route["trig_certificate"]

    constant = model.classify_required_analytic_event(common_spec(
        cos_splines={"1": bspline(["1", "1"])},
    ))
    assert constant["status"] == "CERTIFIED"
    assert not certified_routes(constant), "constant modulation must remain v7/v6-owned"

    noncommon = model.classify_required_analytic_event(common_spec(
        cos_splines={"1": bspline(["0", "1"])},
        sin_splines={"1": bspline(["1", "2"])},
        phase_turn_rate="1/8",
    ))
    assert noncommon["status"] == "BLOCKED"
    assert noncommon["blocker"] == "PB-007-01"
    assert any(
        span["route"].get("reason") == "NO_NONCONSTANT_COMMON_POLYNOMIAL_FACTOR"
        for span in noncommon["spans"]
    )

    zero_phase = model.classify_required_analytic_event(common_spec(
        phase_turn_offset="1/6",
        phase_turn_rate="0",
    ))
    assert zero_phase["status"] == "BLOCKED"
    assert zero_phase["blocker"] == "PB-007-01"

    mismatch = model.classify_required_analytic_event(common_spec(
        parameter_projection="independent-phase"
    ))
    assert mismatch == {
        "status": "SEMANTIC_BLOCKER",
        "reason": "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN",
    }

    float_control = model.classify_required_analytic_event(common_spec(
        cos_splines={
            "1": {"degree": 1, "knots": ["0", "0", "1", "1"], "controls": [0.0, "1"]}
        }
    ))
    assert float_control["status"] == "SEMANTIC_BLOCKER"

    epsilon = common_spec()
    epsilon["epsilon"] = "1e-9"
    assert model.classify_required_analytic_event(epsilon) == {
        "status": "SEMANTIC_BLOCKER",
        "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD",
    }

    forged = common_spec()
    forged["common_factor"] = ["-1/3", "1"]
    assert model.classify_required_analytic_event(forged) == {
        "status": "SEMANTIC_BLOCKER",
        "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD",
    }

    forged_quotient = common_spec()
    forged_quotient["quotient_constants"] = {"1": "1"}
    assert model.classify_required_analytic_event(forged_quotient) == {
        "status": "SEMANTIC_BLOCKER",
        "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD",
    }

    identity = model._common_factor({1: [Fraction(0)]}, {})
    assert identity["status"] == "BLOCKED"
    assert identity["reason"] == "IDENTITY_ZERO_COUPLED_EVENT"

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
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("paid_campaign_run", True))
    expect_artifact_rejected(
        lambda a: a["protected_semantics"].__setitem__("exact_time_path_phase_correlation_preserved", False)
    )
    expect_artifact_rejected(
        lambda a: a["theorem_boundary"].__setitem__("preconditions", ["any transcendental grammar"])
    )
    expect_artifact_rejected(
        lambda a: a["implementation"].__setitem__("model_git_blob_sha1", "0" * 40)
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
        print("PB-007-01 v8 contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-01 v8 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
