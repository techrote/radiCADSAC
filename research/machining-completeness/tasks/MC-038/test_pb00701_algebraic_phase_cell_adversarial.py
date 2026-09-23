#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_algebraic_phase_cell_model as model  # noqa: E402
import pb00701_phase_sector_partition_model as v27  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402
import test_pb00701_phase_sector_partition_adversarial as v27test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="0", rate="1/12", **extra):
    return v19test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="0", rate="1/12"):
    # v26's historical pointwise cone is deliberately too conservative:
    # S/2 = 1/2 <= |C| = 3/5. On the exact phase cell [0,1/12],
    # however, cos >= sqrt(3)/2 > 6/7 while sin <= 1/2.
    return _spec(
        {0: [Fraction(-4, 5)], 1: [Fraction(3, 5)], 2: [Fraction(1, 10000)]},
        {1: [1]},
        offset=offset,
        rate=rate,
    )


def _v28_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def run():
    source = _fixture()
    old = v27.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    assert any(span.get("route", {}).get("status") == "BLOCKED" for span in old.get("spans", []))

    result = model.classify_required_analytic_event(source)
    route = _v28_route(result)
    assert route["relation"] == model.V28_ROUTE
    anchor = route["algebraic_phase_cell_certificate"]
    cell = anchor["phase_cell_certificate"]
    combined = anchor["projection_residual_certificate"]
    assert anchor["dominant_component"] == "SIN"
    assert anchor["transverse_component"] == "COS"
    assert anchor["direction"] == "INCREASING"
    assert cell["relation"] == "EXACT_RATIONAL_TURN_ALGEBRAIC_PHASE_CELL"
    assert cell["dominant_quadrature"] == "COS"
    assert cell["dominant_exact_endpoint_magnitude"] == "sqrt(3)/2"
    assert cell["dominant_rational_lower_bound"] == "6/7"
    assert cell["transverse_exact_upper_bound"] == "1/2"
    assert "147 > 144" in cell["algebraic_comparison"]
    assert combined["relation"] == "EXACT_ALGEBRAIC_PHASE_CELL_PROJECTION_PLUS_RESIDUAL_ORTHANT_DOMINANCE"
    assert combined["dominant_rational_lower_bound"] == "6/7"
    assert combined["transverse_rational_upper_bound"] == "1/2"
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in combined["orthant_certificates"])
    assert not any(term["harmonic"] == 1 and term["kind"] == "C_prime" for term in combined["residual_terms"])
    assert not any(term["harmonic"] == 1 and term["kind"] == "S_prime" for term in combined["residual_terms"])
    assert any(term["harmonic"] == 2 and term["kind"] == "phase_C" for term in combined["residual_terms"])
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True
    assert route["sampling_used"] is False
    assert route["epsilon_used"] is False
    assert route["numerical_trigonometry_used"] is False

    eps = Fraction(1, 1000000)
    exact_cell = model._phase_cell_certificate("COS", Fraction(0), Fraction(1, 12))
    inside_cell = model._phase_cell_certificate("COS", Fraction(0), Fraction(1, 12) - eps)
    outside_cell = model._phase_cell_certificate("COS", Fraction(0), Fraction(1, 12) + eps)
    assert exact_cell["status"] == inside_cell["status"] == "CERTIFIED"
    assert outside_cell is None

    forward = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(3, 5)]}, {1: [1]}, Fraction(0), Fraction(1, 12), 1
    )
    reverse = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(3, 5)]}, {1: [1]}, Fraction(1, 12), Fraction(-1, 12), 1
    )
    assert forward["status"] == reverse["status"] == "CERTIFIED"
    assert forward["direction"] == "INCREASING"
    assert reverse["direction"] == "DECREASING"

    c_dominant = model._algebraic_phase_cell_derivative_certificate(
        {1: [1]}, {1: [Fraction(3, 5)]}, Fraction(1, 6), Fraction(1, 6), 1
    )
    assert c_dominant["status"] == "CERTIFIED", c_dominant
    assert c_dominant["dominant_component"] == "COS"
    assert c_dominant["phase_cell_certificate"]["dominant_quadrature"] == "SIN"
    assert c_dominant["phase_cell_certificate"]["quadrature_sign"] == "POSITIVE"
    assert c_dominant["direction"] == "DECREASING"

    neg_cos_cell = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(3, 5)]}, {1: [1]}, Fraction(5, 12), Fraction(1, 6), 1
    )
    neg_sin_cell = model._algebraic_phase_cell_derivative_certificate(
        {1: [1]}, {1: [Fraction(3, 5)]}, Fraction(2, 3), Fraction(1, 6), 1
    )
    assert neg_cos_cell["status"] == "CERTIFIED", neg_cos_cell
    assert neg_cos_cell["phase_cell_certificate"]["quadrature_sign"] == "NEGATIVE"
    assert neg_sin_cell["status"] == "CERTIFIED", neg_sin_cell
    assert neg_sin_cell["phase_cell_certificate"]["quadrature_sign"] == "NEGATIVE"

    equality = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(12, 7)]}, {1: [1]}, Fraction(0), Fraction(1, 12), 1
    )
    inside = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(12, 7)]}, {1: [Fraction(1) + eps]}, Fraction(0), Fraction(1, 12), 1
    )
    outside = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(12, 7)]}, {1: [Fraction(1) - eps]}, Fraction(0), Fraction(1, 12), 1
    )
    assert equality["status"] == "BLOCKED", equality
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    residual_eq = Fraction(39, 140)
    residual_equal = model._algebraic_phase_cell_derivative_certificate(
        {0: [0, residual_eq], 1: [Fraction(3, 5)]},
        {1: [1]}, Fraction(0), Fraction(1, 12), 1,
    )
    residual_inside = model._algebraic_phase_cell_derivative_certificate(
        {0: [0, residual_eq - eps], 1: [Fraction(3, 5)]},
        {1: [1]}, Fraction(0), Fraction(1, 12), 1,
    )
    residual_outside = model._algebraic_phase_cell_derivative_certificate(
        {0: [0, residual_eq + eps], 1: [Fraction(3, 5)]},
        {1: [1]}, Fraction(0), Fraction(1, 12), 1,
    )
    assert residual_equal["status"] == "BLOCKED", residual_equal
    assert residual_inside["status"] == "CERTIFIED", residual_inside
    assert residual_outside["status"] == "BLOCKED", residual_outside

    unsupported = model._algebraic_phase_cell_derivative_certificate(
        {1: [Fraction(3, 5)]}, {1: [1]}, Fraction(0), Fraction(1, 12) + eps, 1
    )
    assert unsupported["status"] == "BLOCKED", unsupported

    forged = copy.deepcopy(source)
    forged.update({
        "algebraic_phase_cell": ["0", "1"],
        "algebraic_endpoint_values": ["999"],
        "projection_lower_bound": "999",
        "transverse_upper_bound": "0",
        "separation_bound": "999",
        "projection_certificate": {"status": "CERTIFIED"},
        "root_count": 0,
        "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v28_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["algebraic_phase_cell_certificate"]["phase_cell_certificate"] == cell

    float_spec = copy.deepcopy(source)
    float_spec["phase_turn_rate"] = 1.0 / 12.0
    assert _rejected(float_spec)
    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)

    saved = model._algebraic_phase_cell_route
    try:
        model._algebraic_phase_cell_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model._algebraic_phase_cell_route = saved
    assert model.resource_refusal()["is_truth_value"] is False

    historical = v27test._fixture()
    historical_v27 = v27.classify_required_analytic_event(historical)
    assert historical_v27["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical) == historical_v27

    assert model.V28_ROUTE.startswith("EXACT_")
    print("PB-007-01 v28 algebraic rational-turn phase-cell adversarial tests passed")


if __name__ == "__main__":
    run()
