#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_source_adaptive_separator_model as model  # noqa: E402
import pb00701_pythagorean_phase_cell_model as v29  # noqa: E402
import test_pb00701_pythagorean_phase_cell_adversarial as v29test  # noqa: E402
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
    # Source-adaptive projective ceiling beta = 1/(200/83) = 83/200.
    # This is strictly above tan(pi/8)=sqrt(2)-1 but strictly below v29's
    # fixed 5/12 slope.  Therefore v29's worst-case projection is negative:
    # 12/13 - (5/13)*(200/83) = -4/1079 < 0.
    # The selected SIN amplitude is nonconstant, so S'=1/100000 is retained
    # as an active residual.  A tiny h=2 phase term keeps the fixture genuinely
    # multi-harmonic and materially exercises the non-anchor residual path.
    return _spec(
        {
            0: [Fraction(-49, 20)],
            1: [Fraction(200, 83)],
            2: [Fraction(1, 100000000)],
        },
        {1: [1, Fraction(1, 100000)]},
        offset=offset,
        rate=rate,
    )


def _v30_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR"
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
    old = v29.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    assert any(span.get("route", {}).get("status") == "BLOCKED" for span in old.get("spans", []))

    result = model.classify_required_analytic_event(source)
    route = _v30_route(result)
    assert route["relation"] == model.V30_ROUTE
    anchor = route["source_adaptive_projective_separator_certificate"]
    sep = anchor["source_adaptive_separator_certificate"]
    cell = anchor["phase_cell_certificate"]
    combined = anchor["projection_residual_certificate"]
    assert anchor["dominant_component"] == "SIN"
    assert anchor["transverse_component"] == "COS"
    assert anchor["direction"] == "INCREASING"
    assert sep["relation"] == "EXACT_SOURCE_DERIVED_CLOSED_FORM_RATIONAL_SEPARATOR_ABOVE_TAN_PI_8"
    assert sep["source_projective_ceiling"] == "83/200"
    assert sep["rational_separator"] == "93867/226400"
    m = Fraction(sep["rational_separator"])
    assert Fraction(70, 169) < m < Fraction(83, 200) < Fraction(5, 12)
    assert sep["separator_algebraic_comparison"]["above_boundary"] is True
    assert sep["iterative_separator_search_used"] is False
    assert cell["relation"] == "EXACT_5_12_13_RATIONAL_TURN_ALGEBRAIC_PHASE_CELL"
    assert combined["relation"] == "EXACT_SOURCE_ADAPTIVE_PROJECTIVE_SEPARATOR_PLUS_RESIDUAL_ORTHANT_DOMINANCE"
    assert combined["rational_separator"] == sep["rational_separator"]
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in combined["orthant_certificates"])
    assert any(term["harmonic"] == 1 and term["kind"] == "S_prime" for term in combined["residual_terms"])
    assert any(term["harmonic"] == 2 and term["kind"] == "phase_C" for term in combined["residual_terms"])
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True
    assert route["sampling_used"] is False
    assert route["epsilon_used"] is False
    assert route["numerical_trigonometry_used"] is False
    assert route["iterative_separator_search_used"] is False

    # Exact algebraic-bound controls immediately below and above sqrt(2)-1.
    below = model._tan_pi_8_comparison(Fraction(70, 169))
    above = model._tan_pi_8_comparison(Fraction(169, 408))
    assert below["above_boundary"] is False, below
    assert above["above_boundary"] is True, above
    assert Fraction(70, 169) < Fraction(169, 408)

    # The same exact boundary is enforced when the source-owned projective
    # ceiling itself straddles the algebraic limit.
    source_below = model._source_adaptive_separator_certificate(
        [1], [Fraction(169, 70)], "SIN", "COS"
    )
    source_above = model._source_adaptive_separator_certificate(
        [1], [Fraction(408, 169)], "SIN", "COS"
    )
    assert source_below["status"] == "BLOCKED", source_below
    assert source_above["status"] == "CERTIFIED", source_above

    # Positive/negative phase rate preserve the same source certificate while
    # reversing the complete derivative direction.
    forward = model._source_adaptive_derivative_certificate(
        {1: [Fraction(200, 83)]}, {1: [1]}, Fraction(0), Fraction(1, 16), 1
    )
    reverse = model._source_adaptive_derivative_certificate(
        {1: [Fraction(200, 83)]}, {1: [1]}, Fraction(1, 16), Fraction(-1, 16), 1
    )
    assert forward["status"] == reverse["status"] == "CERTIFIED"
    assert forward["direction"] == "INCREASING"
    assert reverse["direction"] == "DECREASING"

    # Symmetric C-dominant orientation and both negative-quadrature cells.
    c_dominant = model._source_adaptive_derivative_certificate(
        {1: [1]}, {1: [Fraction(200, 83)]}, Fraction(3, 16), Fraction(1, 16), 1
    )
    neg_cos_cell = model._source_adaptive_derivative_certificate(
        {1: [Fraction(200, 83)]}, {1: [1]}, Fraction(7, 16), Fraction(1, 16), 1
    )
    neg_sin_cell = model._source_adaptive_derivative_certificate(
        {1: [1]}, {1: [Fraction(200, 83)]}, Fraction(11, 16), Fraction(1, 16), 1
    )
    assert c_dominant["status"] == "CERTIFIED", c_dominant
    assert c_dominant["dominant_component"] == "COS"
    assert c_dominant["phase_cell_certificate"]["dominant_quadrature"] == "SIN"
    assert c_dominant["direction"] == "DECREASING"
    assert neg_cos_cell["status"] == "CERTIFIED", neg_cos_cell
    assert neg_cos_cell["phase_cell_certificate"]["quadrature_sign"] == "NEGATIVE"
    assert neg_sin_cell["status"] == "CERTIFIED", neg_sin_cell
    assert neg_sin_cell["phase_cell_certificate"]["quadrature_sign"] == "NEGATIVE"

    # Exact full source-margin equality fails closed; signed rational neighbours
    # exercise the strict MC-032 orthant boundary.
    eps = Fraction(1, 1000000)
    sep_const = model._source_adaptive_separator_certificate(
        [1], [Fraction(200, 83)], "SIN", "COS"
    )
    m_const = Fraction(sep_const["rational_separator"])
    residual_eq = Fraction(6, 16) * Fraction(12, 13) * (
        Fraction(1) - m_const * Fraction(200, 83)
    )
    residual_equal = model._source_adaptive_derivative_certificate(
        {0: [0, residual_eq], 1: [Fraction(200, 83)]},
        {1: [1]}, Fraction(0), Fraction(1, 16), 1,
    )
    residual_inside = model._source_adaptive_derivative_certificate(
        {0: [0, residual_eq - eps], 1: [Fraction(200, 83)]},
        {1: [1]}, Fraction(0), Fraction(1, 16), 1,
    )
    residual_outside = model._source_adaptive_derivative_certificate(
        {0: [0, residual_eq + eps], 1: [Fraction(200, 83)]},
        {1: [1]}, Fraction(0), Fraction(1, 16), 1,
    )
    assert residual_equal["status"] == "BLOCKED", residual_equal
    assert residual_inside["status"] == "CERTIFIED", residual_inside
    assert residual_outside["status"] == "BLOCKED", residual_outside

    # A genuinely adverse projective source remains blocked rather than being
    # rescued by the separator machinery.
    adverse = model._source_adaptive_derivative_certificate(
        {1: [Fraction(169, 70)]}, {1: [1]}, Fraction(0), Fraction(1, 16), 1
    )
    assert adverse["status"] == "BLOCKED", adverse

    forged = copy.deepcopy(source)
    forged.update({
        "source_adaptive_separator": "0",
        "rational_separator": "0",
        "source_projective_ceiling": "999",
        "tan_pi_8": "0",
        "algebraic_boundary": "caller-forged",
        "projection_certificate": {"status": "CERTIFIED"},
        "root_count": 0,
        "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v30_route(forged_result)
    forged_sep = forged_route["source_adaptive_projective_separator_certificate"]["source_adaptive_separator_certificate"]
    assert forged_result["status"] == result["status"]
    assert forged_sep["rational_separator"] == sep["rational_separator"]
    assert forged_sep["source_projective_ceiling"] == sep["source_projective_ceiling"]

    float_spec = copy.deepcopy(source)
    float_spec["phase_turn_rate"] = 1.0 / 16.0
    assert _rejected(float_spec)
    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)

    saved = model._source_adaptive_route
    try:
        model._source_adaptive_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model._source_adaptive_route = saved
    assert model.resource_refusal()["is_truth_value"] is False

    # Complete v8-v29 precedence remains byte-for-byte semantic precedence for
    # the historical v29 success fixture.
    historical = v29test._fixture()
    historical_v29 = v29.classify_required_analytic_event(historical)
    assert historical_v29["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical) == historical_v29

    assert model.V30_ROUTE.startswith("EXACT_")
    print("PB-007-01 v30 source-adaptive projective separator adversarial tests passed")


if __name__ == "__main__":
    run()
