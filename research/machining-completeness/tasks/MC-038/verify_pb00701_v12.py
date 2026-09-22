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
ARTIFACT = TASK / "pb00701-component-root-partition-boundary-v12.json"
REPORT = TASK / "pb00701-report-v12.md"
DOC = ROOT / "docs" / "machining-completeness" / "38-PB00701-COMPONENT-ROOT-PARTITION.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "72617ed78a3b98779ac5812346616dc21394e26f"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V11_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-phase-dominance-boundary-v11.json": "402fc6f6de953b0d42c36b6cda098da908ce692f",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v11.md": "8be35910b129f0b6387d139b96a5c02f8c59c7a2",
    "research/machining-completeness/tasks/MC-038/pb00701_phase_dominance_model.py": "bd0ee3d04a05134778905d690985d78acf347c84",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v11.py": "6251182de02b0fbf2910e427858593a1aaface62",
    "docs/machining-completeness/37-PB00701-PHASE-DOMINANCE.md": "2d931d9977fde2a61c314c179eb66245e4bdfbe0",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v11 as verify_v11  # noqa: E402
import pb00701_component_partition_model as model  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-component-root-partition-boundary/12.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 186
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == (
        "EXACT_FINITE_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC_SUBGRAMMAR_ESTABLISHED_"
        "GENERAL_COUPLED_ROUTE_OPEN"
    )
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v11_evidence"]}
    assert set(history) == set(EXPECTED_V11_HISTORY)
    for path, sha in EXPECTED_V11_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_FINITE_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC_REDUCTION"
    assert "Sturm" in extension["root_authority"]
    assert "v10" in extension["local_dispatch"] and "v11" in extension["local_dispatch"]
    assert "u in Z" in extension["component_root_event_rule"]
    assert "exact global rational source" in extension["shared_boundary_rule"]

    controls = artifact["boundary_controls"]
    for token in (
        "A/B", "A-zero", "B-zero", "off-lattice", "algebraic-irrational",
        "repeated", "1/1000000", "shared partition boundary", "forged",
        "coincident", "source-parameter", "binary-float", "resource refusal",
        "historical", "26-operation", "MC-B",
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

    verify_v11.validate_artifact(verify_v11.load(verify_v11.ARTIFACT))
    for path, sha in EXPECTED_V11_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v11 historical evidence drift: {path}"
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
            "pb-007-01", "remains **open**", "component-root", "sturm",
            "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701_v11.py --contract",
        "pb00701_component_partition_model.py",
        "verify_pb00701_v12.py --contract",
        "verify_pb00701_v12.py --self-test",
    ):
        assert token in workflow


def v12_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span["route_kind"] == "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"
    ]
    assert routes, result
    route = routes[0]
    assert route["status"] == "CERTIFIED"
    assert route["relation"] == "EXACT_FINITE_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC_EVENT_DECISION"
    return route


def both_root_spec(*, offset="0", rate="1/4", **extra):
    return spec(
        cos={"1": linear(Fraction(-1, 3), 1)},
        sin={"1": linear(Fraction(2, 3), -1)},
        offset=offset,
        rate=rate,
        **extra,
    )


def component_event(route, owner):
    matches = [event for event in route["component_root_event_classification"] if event["owner"] == owner]
    assert len(matches) == 1, matches
    return matches[0]


def run_model_controls():
    base_spec = both_root_spec()
    old = verify_v11.model.classify_required_analytic_event(base_spec)
    assert old["status"] == "BLOCKED", old
    assert any(
        span["route"].get("reason") == "NO_ZERO_FREE_PROJECTIVE_COMPONENT_FOR_DUAL_RATIO_ROUTE"
        for span in old["spans"]
    )
    route = v12_route(model.classify_required_analytic_event(base_spec))
    partition = route["component_root_partition"]
    assert partition["total_distinct_component_roots_closed"] == 2
    assert len(partition["root_neighborhoods"]) == 2
    assert {entry["owner"] for entry in partition["root_neighborhoods"]} == {"A", "B"}
    assert model.verify_partition_certificate(
        partition,
        [Fraction(-1, 3), Fraction(1)],
        [Fraction(2, 3), Fraction(-1)],
    )
    charts = {cell["route"]["projective_chart"] for cell in route["cell_decisions"]}
    assert charts == {"TANGENT", "COTANGENT"}

    a_event_route = v12_route(model.classify_required_analytic_event(both_root_spec(offset="-1/12")))
    a_event = component_event(a_event_route, "A")
    assert a_event["relation"] == "EXACT_COMPONENT_ROOT_EVENT"
    assert a_event["source"] == "1/3"
    assert a_event["projective_phase"] == "0"
    assert a_event["event_multiplicity"] == 1

    b_event_route = v12_route(model.classify_required_analytic_event(both_root_spec(offset="1/12")))
    b_event = component_event(b_event_route, "B")
    assert b_event["relation"] == "EXACT_COMPONENT_ROOT_EVENT"
    assert b_event["source"] == "2/3"
    assert b_event["projective_phase"] == "1/2"
    assert b_event["event_multiplicity"] == 1

    eps = Fraction(1, 1000000)
    for shifted in (Fraction(-1, 12) - eps, Fraction(-1, 12) + eps):
        neighbor = v12_route(model.classify_required_analytic_event(both_root_spec(offset=str(shifted))))
        assert component_event(neighbor, "A")["relation"] == "COMPONENT_ROOT_IS_NOT_AN_EVENT"

    repeated_a = [Fraction(1, 9), Fraction(-2, 3), Fraction(1)]
    repeated_b = [Fraction(2, 3), Fraction(-1)]
    repeated_partition = model.build_component_root_partition(repeated_a, repeated_b)
    assert repeated_partition["status"] == "CERTIFIED"
    a_neighborhood = next(n for n in repeated_partition["root_neighborhoods"] if n["owner"] == "A")
    repeated_event = model._component_root_event(
        a_neighborhood, repeated_a, repeated_b, Fraction(-1, 6), Fraction(1, 2)
    )
    assert repeated_event["relation"] == "EXACT_COMPONENT_ROOT_EVENT"
    assert repeated_event["component_root_multiplicity"] == 2
    assert repeated_event["event_multiplicity"] == 1

    irrational_a = [Fraction(-1, 2), Fraction(0), Fraction(1)]
    irrational_b = [Fraction(-1, 3), Fraction(1)]
    irrational_partition = model.build_component_root_partition(irrational_a, irrational_b)
    assert irrational_partition["status"] == "CERTIFIED"
    irrational_neighborhood = next(n for n in irrational_partition["root_neighborhoods"] if n["owner"] == "A")
    irrational_event = model._component_root_event(
        irrational_neighborhood, irrational_a, irrational_b, Fraction(0), Fraction(1, 2)
    )
    assert irrational_event["relation"] == "COMPONENT_ROOT_IS_NOT_AN_EVENT"

    off_lattice = component_event(route, "A")
    assert off_lattice["relation"] == "COMPONENT_ROOT_IS_NOT_AN_EVENT"

    shared = v12_route(model.classify_required_analytic_event(both_root_spec(offset="-1/4", rate="1/4")))
    reported = [
        endpoint["source"]
        for cell in shared["cell_decisions"]
        for endpoint in cell["global_endpoint_events"]
    ]
    assert reported.count("1/2") == 2, reported
    unique = [event["source"] for event in shared["unique_partition_endpoint_events"]]
    assert unique.count("1/2") == 1, unique

    multiharmonic = model.classify_required_analytic_event(spec(
        cos={"1": linear(Fraction(-1, 3), 1), "2": constant(1)},
        sin={"1": linear(Fraction(2, 3), -1)},
    ))
    assert multiharmonic["status"] == "BLOCKED"
    assert multiharmonic["blocker"] == "PB-007-01"

    mismatch = model.classify_required_analytic_event(both_root_spec(parameter_projection="other-source"))
    assert mismatch["status"] == "SEMANTIC_BLOCKER"

    float_input = model.classify_required_analytic_event(spec(
        cos={"1": {
            "degree": 1,
            "knots": ["0", "0", "1", "1"],
            "controls": [0.5, "2/3"],
        }},
        sin={"1": linear(Fraction(2, 3), -1)},
    ))
    assert float_input["status"] == "SEMANTIC_BLOCKER"

    coincident = model.build_component_root_partition(
        [Fraction(-1, 3), 1], [Fraction(-1, 3), 1]
    )
    assert coincident["status"] == "BLOCKED"
    assert coincident["reason"] == "COMPONENT_ROOTS_NOT_COPRIME"

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
    historical["historical_v11_evidence"][0]["git_blob_sha1"] = "0" * 40
    mutations.append(historical)

    paid = copy.deepcopy(artifact)
    paid["resources"]["paid_campaign_run"] = True
    mutations.append(paid)

    for mutation in mutations:
        assert_raises(lambda mutation=mutation: validate_artifact(mutation, check_repo=False))

    a_poly = [Fraction(-1, 3), Fraction(1)]
    b_poly = [Fraction(2, 3), Fraction(-1)]
    partition = model.build_component_root_partition(a_poly, b_poly)
    assert partition["status"] == "CERTIFIED"

    missing = copy.deepcopy(partition)
    missing["cells"] = missing["cells"][:-1]
    assert not model.verify_partition_certificate(missing, a_poly, b_poly)

    forged_owner = copy.deepcopy(partition)
    forged_owner["root_neighborhoods"][0]["owner"] = (
        "B" if forged_owner["root_neighborhoods"][0]["owner"] == "A" else "A"
    )
    assert not model.verify_partition_certificate(forged_owner, a_poly, b_poly)

    epsilon_launder = copy.deepcopy(partition)
    epsilon_launder["epsilon_used"] = True
    assert not model.verify_partition_certificate(epsilon_launder, a_poly, b_poly)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("select --contract or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT))
        print("PB-007-01 v12 contract: PASS")
    if args.self_test:
        validate_artifact(load(ARTIFACT))
        run_model_controls()
        run_adversarial_controls()
        print("PB-007-01 v12 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
