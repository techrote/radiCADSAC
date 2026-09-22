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
ARTIFACT = TASK / "pb00701-multiharmonic-multiplier-boundary-v13.json"
REPORT = TASK / "pb00701-report-v13.md"
DOC = ROOT / "docs" / "machining-completeness" / "39-PB00701-MULTIHARMONIC-MULTIPLIER.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "423d742d3f615f448d58d30332dacc60c51313ba"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V12_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-component-root-partition-boundary-v12.json": "f307a323c660d2475c03466737230b4a5bdb1873",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v12.md": "697f6b7327594fcfc43c99dc99bcfffb09e94bf0",
    "research/machining-completeness/tasks/MC-038/pb00701_component_partition_model.py": "da8d48b44e866aa52746f9d551c5a1617225b308",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v12.py": "36c09cb5a888522d291407356bb4fb9caf0e9d28",
    "docs/machining-completeness/38-PB00701-COMPONENT-ROOT-PARTITION.md": "b4a45ef8e0dec4208540ea07568653e52ea15e2c",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v12 as verify_v12  # noqa: E402
import pb00701_multiharmonic_multiplier_model as model  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def bspline(controls):
    return {
        "degree": 1,
        "knots": ["0", "0", "1", "1"],
        "controls": [str(value) for value in controls],
    }


def linear(intercept, slope):
    intercept = Fraction(intercept)
    slope = Fraction(slope)
    return bspline([intercept, intercept + slope])


def constant(value):
    return bspline([value, value])


def scale_linear(intercept, slope, scalar):
    scalar = Fraction(scalar)
    return linear(Fraction(intercept) * scalar, Fraction(slope) * scalar)


def factor_spec(multiplier_lambda=Fraction(2), *, harmonic=1, offset="0", rate="1/4", **extra):
    multiplier_lambda = Fraction(multiplier_lambda)
    a0, a1 = Fraction(-1, 3), Fraction(1)
    b0, b1 = Fraction(2, 3), Fraction(-1)
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {
            str(harmonic): scale_linear(a0, a1, multiplier_lambda + Fraction(1, 2)),
            str(3 * harmonic): scale_linear(a0, a1, Fraction(1, 2)),
        },
        "sin_splines": {
            str(harmonic): scale_linear(b0, b1, multiplier_lambda - Fraction(1, 2)),
            str(3 * harmonic): scale_linear(b0, b1, Fraction(1, 2)),
        },
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "source-time-t",
    }
    value.update(extra)
    return value


def factor_polys(a_poly, b_poly, multiplier_lambda=Fraction(2), harmonic=1):
    lam = Fraction(multiplier_lambda)
    return (
        {
            harmonic: model.v7._pscale(a_poly, lam + Fraction(1, 2)),
            3 * harmonic: model.v7._pscale(a_poly, Fraction(1, 2)),
        },
        {
            harmonic: model.v7._pscale(b_poly, lam - Fraction(1, 2)),
            3 * harmonic: model.v7._pscale(b_poly, Fraction(1, 2)),
        },
    )


def assert_raises(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected adversarial mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-multiharmonic-multiplier-boundary/13.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 188
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == (
        "EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC_SUBGRAMMAR_ESTABLISHED_"
        "GENERAL_MULTIHARMONIC_ROUTE_OPEN"
    )
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v12_evidence"]}
    assert set(history) == set(EXPECTED_V12_HISTORY)
    for path, sha in EXPECTED_V12_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC_REDUCTION"
    assert "{h,3h}" in extension["harmonic_family"]
    assert "C_h=(lambda+1/2)A" in extension["source_derived_factorization"]
    assert "|lambda|>1" in extension["multiplier_authority"]
    assert all(token in extension["carrier_dispatch"] for token in ("v10", "v11", "v12"))

    controls = artifact["boundary_controls"]
    for token in (
        "multi-harmonic", "lambda=1", "1/1000000", "negative", "perturbed",
        "extra, missing, and wrong", "v8", "carrier residual", "source-parameter",
        "binary-float", "resource refusal", "historical v12", "26-operation", "MC-B",
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

    verify_v12.validate_artifact(verify_v12.load(verify_v12.ARTIFACT))
    for path, sha in EXPECTED_V12_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v12 historical evidence drift: {path}"
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
            "pb-007-01", "remains **open**", "multi-harmonic", "|lambda|>1",
            "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701_v12.py --contract",
        "pb00701_multiharmonic_multiplier_model.py",
        "verify_pb00701_v13.py --contract",
        "verify_pb00701_v13.py --self-test",
    ):
        assert token in workflow


def v13_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span["route_kind"] == "PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC"
    ]
    assert routes, result
    route = routes[0]
    assert route["status"] == "CERTIFIED"
    assert route["relation"] == "EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC_EVENT_REDUCTION"
    return route


def run_model_controls():
    genuine = factor_spec(Fraction(2))
    old = verify_v12.model.classify_required_analytic_event(genuine)
    assert old["status"] == "BLOCKED", old
    assert old["blocker"] == "PB-007-01"

    route = v13_route(model.classify_required_analytic_event(genuine))
    factor = route["factorization"]
    assert factor["lambda"] == "2"
    assert factor["multiplier_sign"] == "POSITIVE"
    assert factor["multiplier_nonvanishing_bound"] == "|lambda|-1=1"
    assert factor["product_to_sum_verified_exactly"] is True
    assert route["carrier_route_kind"] == "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"
    assert route["carrier"]["relation"] == "EXACT_FINITE_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC_EVENT_DECISION"

    at_threshold = model.classify_required_analytic_event(factor_spec(Fraction(1)))
    assert at_threshold["status"] == "BLOCKED"
    assert any(
        span["route"].get("reason") == "EVEN_MULTIPLIER_NOT_PROVED_GLOBALLY_NONVANISHING"
        for span in at_threshold["spans"]
    )

    eps = Fraction(1, 1000000)
    above = v13_route(model.classify_required_analytic_event(factor_spec(Fraction(1) + eps)))
    assert above["factorization"]["multiplier_nonvanishing_bound"] == "|lambda|-1=1/1000000"
    below = model.classify_required_analytic_event(factor_spec(Fraction(1) - eps))
    assert below["status"] == "BLOCKED"

    negative = v13_route(model.classify_required_analytic_event(factor_spec(Fraction(-2))))
    assert negative["factorization"]["multiplier_sign"] == "NEGATIVE"
    assert negative["factorization"]["multiplier_nonvanishing_bound"] == "|lambda|-1=1"

    perturbed = factor_spec(Fraction(2))
    perturbed["cos_splines"]["1"]["controls"][0] = str(Fraction(-5, 6) + eps)
    perturbed_result = model.classify_required_analytic_event(perturbed)
    assert perturbed_result["status"] == "BLOCKED"
    assert not any(
        span["route_kind"] == "PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC"
        for span in perturbed_result["spans"]
    )

    extra = factor_spec(Fraction(2))
    extra["cos_splines"]["2"] = constant(1)
    assert model.classify_required_analytic_event(extra)["status"] == "BLOCKED"

    missing = factor_spec(Fraction(2))
    del missing["sin_splines"]["3"]
    assert model.classify_required_analytic_event(missing)["status"] == "BLOCKED"

    wrong = factor_spec(Fraction(2))
    wrong["sin_splines"]["4"] = wrong["sin_splines"].pop("3")
    assert model.classify_required_analytic_event(wrong)["status"] == "BLOCKED"

    common_a = [Fraction(-1, 3), Fraction(1)]
    common_b = [Fraction(-2, 3), Fraction(2)]
    common_cos, common_sin = factor_polys(common_a, common_b)
    common = model._multiharmonic_factor_route(
        common_cos, common_sin, Fraction(0), Fraction(1, 4), "source-time-t"
    )
    assert common["status"] == "BLOCKED"
    assert common["reason"] == "CARRIER_COMMON_FACTOR_REMAINS_OWNED_BY_PB00701_V8"

    hard_a = [Fraction(0), Fraction(-10)]
    hard_b = [Fraction(1)]
    hard_cos, hard_sin = factor_polys(hard_a, hard_b)
    hard = model._multiharmonic_factor_route(
        hard_cos, hard_sin, Fraction(0), Fraction(1, 4), "source-time-t"
    )
    assert hard["status"] == "BLOCKED", hard
    assert hard["blocker"] == "PB-007-01"

    mismatch = model.classify_required_analytic_event(
        factor_spec(Fraction(2), parameter_projection="other-source")
    )
    assert mismatch["status"] == "SEMANTIC_BLOCKER"

    floated = factor_spec(Fraction(2))
    floated["cos_splines"]["1"]["controls"][0] = 0.5
    assert model.classify_required_analytic_event(floated)["status"] == "SEMANTIC_BLOCKER"

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

    historical = copy.deepcopy(artifact)
    historical["historical_v12_evidence"][0]["git_blob_sha1"] = "0" * 40
    mutations.append(historical)

    paid = copy.deepcopy(artifact)
    paid["resources"]["paid_campaign_run"] = True
    mutations.append(paid)

    for mutation in mutations:
        assert_raises(lambda mutation=mutation: validate_artifact(mutation, check_repo=False))

    cos_polys, sin_polys = factor_polys(
        [Fraction(-1, 3), Fraction(1)],
        [Fraction(2, 3), Fraction(-1)],
        Fraction(2),
    )
    detected = model.detect_nonvanishing_even_multiplier(cos_polys, sin_polys)
    assert detected["status"] == "CERTIFIED"

    perturbed = copy.deepcopy(cos_polys)
    perturbed[1] = list(perturbed[1])
    perturbed[1][0] += Fraction(1, 1000000)
    assert model.detect_nonvanishing_even_multiplier(perturbed, sin_polys) is None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("select --contract or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT))
        print("PB-007-01 v13 contract: PASS")
    if args.self_test:
        validate_artifact(load(ARTIFACT))
        run_model_controls()
        run_adversarial_controls()
        print("PB-007-01 v13 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
