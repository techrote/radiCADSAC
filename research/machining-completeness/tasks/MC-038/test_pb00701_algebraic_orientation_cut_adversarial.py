#!/usr/bin/env python3
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_algebraic_orientation_cut_model as model
import pb00701_orientation_root_partition_model as v41
import test_pb00701_correlated_closed_handoff_adversarial as v43test
import test_pb00701_multiharmonic_monotone_anchor_adversarial as base_test


def _source():
    a = [Fraction(-1), Fraction(0), Fraction(2)]
    b = [Fraction(-1, 2), Fraction(1)]
    c = v41._trim(v41.v22._padd(a, b))
    s = v41._trim(v41.v22._padd(a, v41.v22._pscale(b, -1)))
    return base_test._spec(
        {1: c, 2: [v43test.TINY]},
        {1: s},
        offset=str(v43test.OFFSET),
        rate=str(v43test.RATE),
        source_parameter_id="pb00701-v44-algebraic-orientation",
    )


def run_algebraic_roots():
    simple = model.exact_algebraic_orientation_roots([-1, 0, 2], "SIMPLE")
    assert simple["status"] == "CERTIFIED", simple
    assert simple["irrational_open_root_count"] == 1
    cert = simple["irrational_open_roots"][0]
    assert cert["multiplicity"] == 1
    assert model.validate_algebraic_root_certificate(cert, [-1, 0, 2])

    repeated = model.exact_algebraic_orientation_roots([1, 0, -4, 0, 4], "REPEATED")
    assert repeated["status"] == "CERTIFIED", repeated
    assert repeated["irrational_open_roots"][0]["multiplicity"] == 2

    lower = model.exact_algebraic_orientation_roots([-4999, 0, 10000], "LOWER")["irrational_open_roots"][0]
    higher = model.exact_algebraic_orientation_roots([-5001, 0, 10000], "HIGHER")["irrational_open_roots"][0]
    assert model.compare_exact_algebraic_roots(lower, higher) == -1

    p = [Fraction(-1), Fraction(0), Fraction(2)]
    a, b = p, v41.v22._pscale(p, 3)
    c = v41._trim(v41.v22._padd(a, b))
    s = v41._trim(v41.v22._padd(a, v41.v22._pscale(b, -1)))
    common = model.exact_algebraic_orientation_cut_certificate({1: c}, {1: s})
    assert common["status"] == "CERTIFIED", common
    assert len(common["canonical_irrational_cuts"]) == 1
    owners = common["canonical_irrational_cuts"][0]["ownership"]
    assert {item["coordinate"] for item in owners} == {"A", "B"}


def run_genuine_residual():
    source = _source()
    predecessor = v41.classify_required_analytic_event(source)
    assert predecessor["status"] != "CERTIFIED", predecessor
    assert any(
        span.get("route", {}).get("reason") == model.IRRATIONAL_V41_REASON
        for span in predecessor.get("spans", [])
    ), predecessor

    result = model.classify_required_analytic_event(source)
    assert result["status"] == "BLOCKED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY"
    ]
    assert routes, result
    route = routes[0]
    assert route["reason"] == model.V44_BLOCKER
    assert route["algebraic_cut_coordinate_authority"]["status"] == "CERTIFIED"
    assert route["source_interval_restriction"]["status"] == "CERTIFIED"
    assert route["normalized_child_reparameterization"]["status"] == "BLOCKED"
    assert route["phase_endpoint_blockers"]
    for item in route["phase_endpoint_blockers"]:
        endpoint = item["phase_endpoint_authority"]
        assert endpoint["status"] == "BLOCKED"
        assert endpoint["numerical_trigonometry_used"] is False
        assert endpoint["approximation_used"] is False


def run_precedence():
    source = v43test._spec()
    prior = v41.classify_required_analytic_event(source)
    assert prior["status"] == "CERTIFIED", prior
    assert model.classify_required_analytic_event(source) == prior
    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False


def run():
    run_algebraic_roots()
    run_genuine_residual()
    run_precedence()


if __name__ == "__main__":
    run()
