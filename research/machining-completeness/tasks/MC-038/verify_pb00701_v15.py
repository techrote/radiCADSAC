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
ARTIFACT = TASK / "pb00701-finite-multiplier-boundary-v15.json"
REPORT = TASK / "pb00701-report-v15.md"
DOC = ROOT / "docs" / "machining-completeness" / "41-PB00701-FINITE-MULTIPLIER.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "c61fc3338992f40e3382eb75d69d2a3bfbe5003e"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V14_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-multiterm-multiplier-boundary-v14.json": "7483bdc568341b89a24f0e27ba6c8e3d72db551d",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v14.md": "349fc4b6f12ba0d1a53a374f17a471fba7bd6aa8",
    "research/machining-completeness/tasks/MC-038/pb00701_multiterm_multiplier_model.py": "7eb80ea1a660b5a935e67c45355784cba4d7c34f",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v14.py": "a7221fe951d54d1c83f146b4059808303f4d8cee",
    "docs/machining-completeness/40-PB00701-MULTITERM-MULTIPLIER.md": "3875e142dc77eb96a40ef77ba475dafff1c3f88e",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v14 as verify_v14  # noqa: E402
import pb00701_finite_multiplier_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def scale_linear(intercept, slope, scalar):
    return verify_v14.scale_linear(intercept, slope, scalar)


def constant(value):
    return verify_v14.constant(value)


def factor_spec(lambdas, *, harmonic=1, offset="0", rate="1/4", omit=None, **extra):
    lambdas = [Fraction(value) for value in lambdas]
    m = len(lambdas) - 1
    assert m >= 3 and lambdas[-1] == 1
    omit = set(omit or ())
    a0, a1 = Fraction(-1, 3), Fraction(1)
    b0, b1 = Fraction(2, 3), Fraction(-1)
    cos_splines = {}
    sin_splines = {}
    for r in range(m + 1):
        h = (2 * r + 1) * harmonic
        if r == 0:
            c_scalar = lambdas[0] + lambdas[1] / 2
            s_scalar = lambdas[0] - lambdas[1] / 2
        elif r < m:
            c_scalar = (lambdas[r] + lambdas[r + 1]) / 2
            s_scalar = (lambdas[r] - lambdas[r + 1]) / 2
        else:
            c_scalar = s_scalar = Fraction(1, 2)
        if ("c", h) not in omit:
            cos_splines[str(h)] = scale_linear(a0, a1, c_scalar)
        if ("s", h) not in omit:
            sin_splines[str(h)] = scale_linear(b0, b1, s_scalar)
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": cos_splines,
        "sin_splines": sin_splines,
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "source-time-t",
    }
    value.update(extra)
    return value


def factor_polys(a_poly, b_poly, lambdas, harmonic=1):
    lambdas = [Fraction(value) for value in lambdas]
    m = len(lambdas) - 1
    cos_polys = {}
    sin_polys = {}
    for r in range(m + 1):
        h = (2 * r + 1) * harmonic
        if r == 0:
            c_scalar = lambdas[0] + lambdas[1] / 2
            s_scalar = lambdas[0] - lambdas[1] / 2
        elif r < m:
            c_scalar = (lambdas[r] + lambdas[r + 1]) / 2
            s_scalar = (lambdas[r] - lambdas[r + 1]) / 2
        else:
            c_scalar = s_scalar = Fraction(1, 2)
        cos_polys[h] = model._pscale(a_poly, c_scalar)
        sin_polys[h] = model._pscale(b_poly, s_scalar)
    return cos_polys, sin_polys


def assert_raises(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected adversarial mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-finite-multiplier-boundary/15.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 192
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == (
        "EXACT_FINITE_STRICT_DOMINANCE_EVEN_COSINE_MULTIPLIER_FAMILY_ESTABLISHED_"
        "GENERAL_MULTIHARMONIC_ROUTE_OPEN"
    )
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v14_evidence"]}
    assert set(history) == set(EXPECTED_V14_HISTORY)
    for path, sha in EXPECTED_V14_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_FINITE_STRICT_DOMINANCE_EVEN_COSINE_MULTIPLIER_REDUCTION"
    assert "(2m+1)h" in extension["harmonic_family"]
    assert "m>=3" in extension["harmonic_family"]
    assert "lambda_m=1" in extension["normalization"]
    for token in ("A=2*C_top", "B=2*S_top", "lambda_0", "lambda_{r+1}", "overlapping"):
        assert token in extension["source_derived_inversion"]
    assert "|lambda_0|>sum_{k>=1}|lambda_k|" in extension["multiplier_authority"]
    assert all(token in extension["carrier_dispatch"] for token in ("v10", "v11", "v12", "v8", "v14"))

    controls = artifact["boundary_controls"]
    for token in (
        "{h,3h,5h,7h}", "m=4", "equality", "1/1000000", "positive and negative lambda_0",
        "mixed-sign", "missing intermediate", "inconsistent adjacent", "perturbed", "top carrier",
        "even", "v14", "v8", "carrier residual", "source-parameter", "binary-float", "forged",
        "resource refusal", "historical v14", "26-operation", "MC-B",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "multi-harmonic" in review["residual_branch"]
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

    verify_v14.validate_artifact(verify_v14.load(verify_v14.ARTIFACT))
    for path, sha in EXPECTED_V14_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v14 historical evidence drift: {path}"
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
            "pb-007-01", "remains **open**", "|lambda_0|>sum_{k>=1}|lambda_k|",
            "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701_v14.py --contract",
        "pb00701_finite_multiplier_model.py",
        "verify_pb00701_v15.py --contract",
        "verify_pb00701_v15.py --self-test",
    ):
        assert token in workflow


def v15_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span["route_kind"] == "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER"
    ]
    assert routes, result
    route = routes[0]
    assert route["status"] == "CERTIFIED"
    assert route["relation"] == "EXACT_FINITE_STRICT_DOMINANCE_MULTIHARMONIC_EVENT_REDUCTION"
    return route


def run_model_controls():
    base_lambdas = [Fraction(4), Fraction(1, 2), Fraction(-1, 4), Fraction(1)]
    genuine = factor_spec(base_lambdas)
    old = verify_v14.model.classify_required_analytic_event(genuine)
    assert old["status"] == "BLOCKED", old
    assert old["blocker"] == "PB-007-01"

    route = v15_route(model.classify_required_analytic_event(genuine))
    factor = route["factorization"]
    assert factor["multiplier_degree"] == 3
    assert factor["top_harmonic"] == 7
    assert factor["lambda_vector"] == ["4", "1/2", "-1/4", "1"]
    assert factor["normalized_highest_coefficient"] == "1"
    assert factor["strict_dominance_tail_sum"] == "7/4"
    assert factor["strict_dominance_margin"] == "9/4"
    assert factor["multiplier_sign"] == "POSITIVE"
    assert factor["source_coefficient_identities_verified_exactly"] is True
    assert factor["caller_factorization_trusted"] is False
    assert route["carrier_route_kind"] == "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"

    tail = sum(abs(x) for x in base_lambdas[1:])
    at_threshold = model.classify_required_analytic_event(factor_spec([tail, *base_lambdas[1:]]))
    assert at_threshold["status"] == "BLOCKED"
    assert any(
        span["route"].get("reason") == "FINITE_MULTIPLIER_STRICT_DOMINANCE_NOT_CERTIFIED"
        for span in at_threshold["spans"]
    )

    eps = Fraction(1, 1000000)
    above = v15_route(model.classify_required_analytic_event(factor_spec([tail + eps, *base_lambdas[1:]])))
    assert above["factorization"]["strict_dominance_margin"] == "1/1000000"
    below = model.classify_required_analytic_event(factor_spec([tail - eps, *base_lambdas[1:]]))
    assert below["status"] == "BLOCKED"

    negative = v15_route(model.classify_required_analytic_event(factor_spec([-4, Fraction(1, 2), Fraction(-1, 4), 1])))
    assert negative["factorization"]["multiplier_sign"] == "NEGATIVE"

    broader_lambdas = [Fraction(4), Fraction(1, 2), Fraction(0), Fraction(0), Fraction(1)]
    broader = factor_spec(broader_lambdas, omit={("c", 5), ("s", 5)})
    broad_route = v15_route(model.classify_required_analytic_event(broader))
    assert broad_route["factorization"]["multiplier_degree"] == 4
    assert broad_route["factorization"]["lambda_vector"] == ["4", "1/2", "0", "0", "1"]
    assert "5" not in broad_route["factorization"]["source_cos_polynomials"]
    assert "5" not in broad_route["factorization"]["source_sin_polynomials"]

    inconsistent = factor_spec(base_lambdas)
    inconsistent["cos_splines"]["3"]["controls"][0] = str(
        Fraction(inconsistent["cos_splines"]["3"]["controls"][0]) + eps
    )
    assert model.classify_required_analytic_event(inconsistent)["status"] == "BLOCKED"

    missing_top = factor_spec(base_lambdas)
    del missing_top["sin_splines"]["7"]
    assert model.classify_required_analytic_event(missing_top)["status"] == "BLOCKED"

    even_extra = factor_spec(base_lambdas)
    even_extra["cos_splines"]["2"] = constant(1)
    assert model.classify_required_analytic_event(even_extra)["status"] == "BLOCKED"

    wrong_lattice = factor_spec(base_lambdas)
    wrong_lattice["cos_splines"]["8"] = constant(1)
    assert model.classify_required_analytic_event(wrong_lattice)["status"] == "BLOCKED"

    prior_v14 = verify_v14.factor_spec(Fraction(2), Fraction(1, 2))
    prior_result = model.classify_required_analytic_event(prior_v14)
    assert prior_result["status"] == "CERTIFIED"
    assert not any(
        span.get("route_kind") == "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER"
        for span in prior_result.get("spans", [])
    )

    common_cos, common_sin = factor_polys(
        [Fraction(-1), Fraction(1)], [Fraction(-2), Fraction(2)], base_lambdas
    )
    common = model._finite_multiplier_route(
        common_cos, common_sin, Fraction(0), Fraction(1, 4), "source-time-t"
    )
    assert common["status"] == "BLOCKED"
    assert common["reason"] == "CARRIER_COMMON_FACTOR_REMAINS_OWNED_BY_PB00701_V8"

    mismatch = factor_spec(base_lambdas, parameter_projection="different-source")
    mismatch_result = model.classify_required_analytic_event(mismatch)
    assert mismatch_result["status"] == "SEMANTIC_BLOCKER"
    assert mismatch_result["reason"] == "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN"

    float_attack = factor_spec(base_lambdas)
    float_attack["cos_splines"]["1"]["controls"][0] = 0.1
    float_result = model.classify_required_analytic_event(float_attack)
    assert float_result["status"] == "SEMANTIC_BLOCKER"

    forged = factor_spec([tail, *base_lambdas[1:]], lambda_vector=["999"], factorization="CERTIFIED")
    forged_result = model.classify_required_analytic_event(forged)
    assert forged_result["status"] == "BLOCKED"

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False


def run_artifact_adversaries(artifact):
    bad = copy.deepcopy(artifact)
    bad["gate_state"] = "ESTABLISHED"
    assert_raises(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["historical_v14_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_raises(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["domain_operation_count"] = 25
    assert_raises(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["PB-007-01"] = "CLOSED"
    assert_raises(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["resources"]["production_authorized"] = True
    assert_raises(lambda: validate_artifact(bad, check_repo=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract or --self-test")

    artifact = load(ARTIFACT)
    if args.contract:
        validate_artifact(artifact)
        print("PB-007-01 v15 contract: PASS")
        return

    validate_artifact(artifact)
    run_model_controls()
    run_artifact_adversaries(artifact)
    print("PB-007-01 v15 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
