#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_pythagorean_phase_cell_model as model  # noqa: E402
import pb00701_algebraic_phase_cell_model as v28  # noqa: E402
import test_pb00701_algebraic_phase_cell_adversarial as v28test  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="0", rate="1/16", **extra):
    return v19test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="0", rate="1/16"):
    # This source is deliberately beyond v28's 6/7,1/2 projection bound:
    # at s=0, (6/7)S-(1/2)C = 6/7-9/10 < 0.  The nested 1/16-turn
    # cell instead gives (12/13)S-(5/13)C = 3/13 > 0.  S is source-
    # modulated so historical constant-modulation authority cannot claim it;
    # S'=1/100 remains an explicit residual.  A tiny h=2 term keeps the
    # acceptance source genuinely multi-harmonic.
    return _spec(
        {0: [Fraction(-19, 10)], 1: [Fraction(9, 5)], 2: [Fraction(1, 10000)]},
        {1: [1, Fraction(1, 100)]},
        offset=offset,
        rate=rate,
    )


def _v29_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION"
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
    old = v28.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    assert any(span.get("route", {}).get("status") == "BLOCKED" for span in old.get("spans", []))

    result = model.classify_required_analytic_event(source)
    route = _v29_route(result)
    assert route["relation"] == model.V29_ROUTE
    anchor = route["pythagorean_phase_cell_certificate"]
    cell = anchor["phase_cell_certificate"]
    combined = anchor["projection_residual_certificate"]
    assert anchor["dominant_component"] == "SIN"
    assert anchor["transverse_component"] == "COS"
    assert anchor["direction"] == "INCREASING"
    assert cell["relation"] == "EXACT_5_12_13_RATIONAL_TURN_ALGEBRAIC_PHASE_CELL"
    assert cell["dominant_quadrature"] == "COS"
    assert cell["dominant_exact_endpoint_magnitude"] == "sqrt(2+sqrt(2))/2"
    assert cell["transverse_exact_endpoint_magnitude"] == "sqrt(2-sqrt(2))/2"
    assert cell["dominant_rational_lower_bound"] == "12/13"
    assert cell["transverse_rational_upper_bound"] == "5/13"
    assert "57122>56644" in cell["algebraic_comparison"].replace(" ", "")
    assert combined["relation"] == "EXACT_5_12_13_PHASE_CELL_PROJECTION_PLUS_RESIDUAL_ORTHANT_DOMINANCE"
    assert combined["dominant_rational_lower_bound"] == "12/13"
    assert combined["transverse_rational_upper_bound"] == "5/13"
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in combined["orthant_certificates"])
    assert not any(term["harmonic"] == 1 and term["kind"] == "C_prime" for term in combined["residual_terms"])
    assert any(term["harmonic"] == 1 and term["kind"] == "S_prime" for term in combined["residual_terms"])
    assert any(term["harmonic"] == 2 and term["kind"] == "phase_C" for term in combined["residual_terms"])
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True
    assert route["sampling_used"] is False
    assert route["epsilon_used"] is False
    assert route["numerical_trigonometry_used"] is False

    eps = Fraction(1, 1000000)
    exact_cell = model._phase_cell_certificate("COS", Fraction(0), Fraction(1, 16))
    inside_cell = model._phase_cell_certificate("COS", Fraction(0), Fraction(1, 16) - eps)
    outside_cell = model._phase_cell_certificate("COS", Fraction(0), Fraction(1, 16) + eps)
    assert exact_cell["status"] == inside_cell["status"] == "CERTIFIED"
    assert outside_cell is None

    forward = model._phase_cell_derivative_certificate(
        {1: [Fraction(9, 5)]}, {1: [1]}, Fraction(0), Fraction(1, 16), 1
    )
    reverse = model._phase_cell_derivative_certificate(
        {1: [Fraction(9, 5)]}, {1: [1]}, Fraction(1, 16), Fraction(-1, 16), 1
    )
    assert forward["status"] == reverse["status"] == "CERTIFIED"
    assert forward["direction"] == "INCREASING"
    assert reverse["direction"] == "DECREASING"

    c_dominant = model._phase_cell_derivative_certificate(
        {1: [1]}, {1: [Fraction(9, 5)]}, Fraction(3, 16), Fraction(1, 8), 1
    )
    assert c_dominant["status"] == "CERTIFIED", c_dominant
    assert c_dominant["dominant_component"] == "COS"
    assert c_dominant["phase_cell_certificate"]["dominant_quadrature"] == "SIN"
    assert c_dominant["phase_cell_certificate"]["quadrature_sign"] == "POSITIVE"
    assert c_dominant["direction"] == "DECREASING"

    neg_cos_cell = model._phase_cell_derivative_certificate(
        {1: [Fraction(9, 5)]}, {1: [1]}, Fraction(7, 16), Fraction(1, 8), 1
    )
    neg_sin_cell = model._phase_cell_derivative_certificate(
        {1: [1]}, {1: [Fraction(9, 5)]}, Fraction(11, 16), Fraction(1, 8), 1
    )
    assert neg_cos_cell["status"] == "CERTIFIED", neg_cos_cell
    assert neg_cos_cell["phase_cell_certificate"]["quadrature_sign"] == "NEGATIVE"
    assert neg_sin_cell["status"] == "CERTIFIED", neg_sin_cell
    assert neg_sin_cell["phase_cell_certificate"]["quadrature_sign"] == "NEGATIVE"

    equality = model._phase_cell_derivative_certificate(
        {1: [Fraction(12, 5)]}, {1: [1]}, Fraction(0), Fraction(1, 16), 1
    )
    inside = model._phase_cell_derivative_certificate(
        {1: [Fraction(12, 5)]}, {1: [Fraction(1) + eps]}, Fraction(0), Fraction(1, 16), 1
    )
    outside = model._phase_cell_derivative_certificate(
        {1: [Fraction(12, 5)]}, {1: [Fraction(1) - eps]}, Fraction(0), Fraction(1, 16), 1
    )
    assert equality["status"] == "BLOCKED", equality
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    residual_eq = Fraction(9, 104)
    residual_equal = model._phase_cell_derivative_certificate(
        {0: [0, residual_eq], 1: [Fraction(9, 5)]},
        {1: [1]}, Fraction(0), Fraction(1, 16), 1,
    )
    residual_inside = model._phase_cell_derivative_certificate(
        {0: [0, residual_eq - eps], 1: [Fraction(9, 5)]},
        {1: [1]}, Fraction(0), Fraction(1, 16), 1,
    )
    residual_outside = model._phase_cell_derivative_certificate(
        {0: [0, residual_eq + eps], 1: [Fraction(9, 5)]},
        {1: [1]}, Fraction(0), Fraction(1, 16), 1,
    )
    assert residual_equal["status"] == "BLOCKED", residual_equal
    assert residual_inside["status"] == "CERTIFIED", residual_inside
    assert residual_outside["status"] == "BLOCKED", residual_outside

    unsupported = model._phase_cell_derivative_certificate(
        {1: [Fraction(9, 5)]}, {1: [1]}, Fraction(0), Fraction(1, 16) + eps, 1
    )
    assert unsupported["status"] == "BLOCKED", unsupported

    forged = copy.deepcopy(source)
    forged.update({
        "pythagorean_phase_cell": ["0", "1"],
        "algebraic_endpoint_values": ["999"],
        "projection_lower_bound": "999",
        "transverse_upper_bound": "0",
        "separation_bound": "999",
        "projection_certificate": {"status": "CERTIFIED"},
        "root_count": 0,
        "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v29_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["pythagorean_phase_cell_certificate"]["phase_cell_certificate"] == cell

    float_spec = copy.deepcopy(source)
    float_spec["phase_turn_rate"] = 1.0 / 16.0
    assert _rejected(float_spec)
    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)

    saved = model._phase_cell_route
    try:
        model._phase_cell_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model._phase_cell_route = saved
    assert model.resource_refusal()["is_truth_value"] is False

    historical = v28test._fixture()
    historical_v28 = v28.classify_required_analytic_event(historical)
    assert historical_v28["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical) == historical_v28

    assert model.V29_ROUTE.startswith("EXACT_")
    print("PB-007-01 v29 5-12-13 nested algebraic phase-cell adversarial tests passed")


if __name__ == "__main__":
    run()
