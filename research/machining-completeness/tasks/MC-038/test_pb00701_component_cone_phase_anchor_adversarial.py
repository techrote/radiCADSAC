#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_component_cone_phase_anchor_model as model  # noqa: E402
import pb00701_mixed_quadrature_phase_anchor_model as v24  # noqa: E402
import test_pb00701_mixed_quadrature_phase_anchor_adversarial as v24test  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as v21test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="-1/12", rate="1/6", **extra):
    return v21test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(anchor0=None, *, c1=None, s1=None, c2=None, offset="-1/12", rate="1/6"):
    if anchor0 is None:
        anchor0 = [0]
    if c1 is None:
        c1 = [Fraction(-1, 20), Fraction(1, 10)]
    if s1 is None:
        s1 = [4]
    if c2 is None:
        c2 = [Fraction(1, 1000)]
    return _spec(
        {0: anchor0, 1: c1, 2: c2},
        {1: s1},
        offset=offset,
        rate=rate,
    )


def _c_dominant_fixture(anchor0=None, *, offset="1/12", rate="1/4"):
    if anchor0 is None:
        anchor0 = [0]
    return _spec(
        {0: anchor0, 1: [4], 2: [Fraction(1, 1000)]},
        {1: [Fraction(-1, 20), Fraction(1, 10)]},
        offset=offset,
        rate=rate,
    )


def _v25_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR"
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
    old = v24.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    route = _v25_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V25_ROUTE
    anchor = route["component_cone_phase_anchor_certificate"]
    residual = route["residual_l1_certificate"]
    assert anchor["harmonic"] == 1
    assert anchor["dominant_component"] == "SIN"
    assert anchor["transverse_component"] == "COS"
    assert anchor["direction"] == "INCREASING"
    assert anchor["strict_rational_cone_gap"] == "39/20"
    assert anchor["strict_rational_lower_bound"] == "39/20"
    assert anchor["dominant_floor_certificate"]["strict_rational_amplitude_floor"] == "4"
    assert anchor["transverse_ceiling_certificate"]["exact_rational_absolute_ceiling"] == "1/20"
    assert anchor["transverse_ceiling_certificate"]["sign_change_allowed"] is True
    assert anchor["sector_certificate"]["component"] == "COS"
    assert anchor["sector_certificate"]["quadrature_sign"] == "POSITIVE"
    assert any(term["harmonic"] == 1 and term["kind"] == "C_prime" for term in residual["terms"])
    assert not any(
        term["harmonic"] == 1 and term["kind"] in ("phase_C", "phase_S")
        for term in residual["terms"]
    )
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True

    decreasing = _v25_route(model.classify_required_analytic_event(
        _fixture(offset="1/12", rate="-1/6")
    ))
    assert decreasing["component_cone_phase_anchor_certificate"]["direction"] == "DECREASING"
    assert decreasing["left_event"]["relation"] == "POSITIVE"
    assert decreasing["right_event"]["relation"] == "NEGATIVE"
    assert decreasing["distinct_roots_open"] == 1

    c_dom_source = _c_dominant_fixture()
    assert v24.classify_required_analytic_event(c_dom_source)["status"] == "BLOCKED"
    c_dom = _v25_route(model.classify_required_analytic_event(c_dom_source))
    c_anchor = c_dom["component_cone_phase_anchor_certificate"]
    assert c_anchor["dominant_component"] == "COS"
    assert c_anchor["transverse_component"] == "SIN"
    assert c_anchor["sector_certificate"]["component"] == "SIN"
    assert c_anchor["sector_certificate"]["quadrature_sign"] == "POSITIVE"
    assert c_anchor["direction"] == "DECREASING"
    assert c_anchor["transverse_ceiling_certificate"]["sign_change_allowed"] is True
    assert c_dom["distinct_roots_open"] == 1

    nonconstant_dominant = model._component_cone_phase_anchor_derivative_certificate(
        {1: [Fraction(1, 20)]},
        {1: [4, Fraction(1, 1000)]},
        Fraction(-1, 12), Fraction(1, 6), 1,
    )
    assert nonconstant_dominant["status"] == "CERTIFIED", nonconstant_dominant
    assert nonconstant_dominant["dominant_component"] == "SIN"
    assert nonconstant_dominant["dominant_floor_certificate"]["relation"] == "EXACT_BERNSTEIN_CONVEX_HULL_NONZERO_AMPLITUDE_FLOOR"

    eps = Fraction(1, 1000000)
    exact_cos_sector = model._half_magnitude_sector_certificate("COS", Fraction(-1, 6), Fraction(1, 6))
    inside_cos_sector = model._half_magnitude_sector_certificate("COS", Fraction(-1, 6), Fraction(1, 6) - eps)
    outside_cos_sector = model._half_magnitude_sector_certificate("COS", Fraction(-1, 6), Fraction(1, 6) + eps)
    assert exact_cos_sector["status"] == "CERTIFIED"
    assert inside_cos_sector["status"] == "CERTIFIED"
    assert outside_cos_sector is None

    exact_sin_sector = model._half_magnitude_sector_certificate("SIN", Fraction(1, 12), Fraction(5, 12))
    outside_sin_sector = model._half_magnitude_sector_certificate("SIN", Fraction(1, 12) - eps, Fraction(5, 12))
    assert exact_sin_sector["status"] == "CERTIFIED"
    assert outside_sin_sector is None

    upper = model._component_abs_upper_certificate([Fraction(-1, 20), Fraction(1, 10)], "COS")
    assert upper["status"] == "CERTIFIED"
    assert upper["bernstein_coefficients"] == ["-1/20", "1/20"]
    assert upper["exact_rational_absolute_ceiling"] == "1/20"

    equality = model._component_cone_phase_anchor_derivative_certificate(
        {1: [1]}, {1: [2]}, Fraction(-1, 12), Fraction(1, 6), 1
    )
    inside = model._component_cone_phase_anchor_derivative_certificate(
        {1: [1]}, {1: [Fraction(2) + eps]}, Fraction(-1, 12), Fraction(1, 6), 1
    )
    outside = model._component_cone_phase_anchor_derivative_certificate(
        {1: [1]}, {1: [Fraction(2) - eps]}, Fraction(-1, 12), Fraction(1, 6), 1
    )
    assert equality["status"] == "BLOCKED"
    assert inside["status"] == "CERTIFIED"
    assert outside["status"] == "BLOCKED"

    floor_failure = model._component_cone_phase_anchor_derivative_certificate(
        {1: [Fraction(1, 10)]}, {1: [0, 1]}, Fraction(-1, 12), Fraction(1, 6), 1
    )
    assert floor_failure["status"] == "BLOCKED"

    anchor_cert = model._component_cone_phase_anchor_derivative_certificate(
        {1: [Fraction(1, 20)]}, {1: [4]}, Fraction(-1, 12), Fraction(1, 6), 1
    )
    assert anchor_cert["status"] == "CERTIFIED"
    lower = Fraction(anchor_cert["strict_rational_lower_bound"])
    l1_equal = v24._mixed_residual_l1_certificate(
        {0: [0, lower], 1: [Fraction(1, 20)]}, {1: [4]}, Fraction(1, 6), anchor_cert
    )
    l1_below = v24._mixed_residual_l1_certificate(
        {0: [0, lower - eps], 1: [Fraction(1, 20)]}, {1: [4]}, Fraction(1, 6), anchor_cert
    )
    l1_above = v24._mixed_residual_l1_certificate(
        {0: [0, lower + eps], 1: [Fraction(1, 20)]}, {1: [4]}, Fraction(1, 6), anchor_cert
    )
    assert l1_equal["status"] == "BLOCKED"
    assert l1_below["status"] == "CERTIFIED"
    assert l1_above["status"] == "BLOCKED"

    no_root = _v25_route(model.classify_required_analytic_event(_fixture(anchor0=[Fraction(21, 10)])))
    assert no_root["total_distinct_roots_closed"] == 0

    left_root_source = _fixture(anchor0=[Fraction(49, 1000)], offset="0", rate="1/12")
    left_root = _v25_route(model.classify_required_analytic_event(left_root_source))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}

    right_root_source = _fixture(anchor0=[Fraction(-51, 1000)], offset="-1/12", rate="1/12")
    right_root = _v25_route(model.classify_required_analytic_event(right_root_source))
    assert right_root["right_event"]["relation"] == "ZERO"
    assert right_root["right_endpoint_root"] is True
    assert right_root["endpoint_root_multiplicity"] == {"right": 1}

    prior = model.classify_required_analytic_event(v24test._fixture())
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v25_component_cone_phase_anchor_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR"
        for span in prior.get("spans", [])
    )

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    assert model.classify_required_analytic_event(mismatch)["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "component_cone": {"status": "CERTIFIED"},
        "component_cone_certificate": {"status": "CERTIFIED", "strict_rational_cone_gap": "999"},
        "dominant_component": "COS",
        "dominant_floor_certificate": {"status": "CERTIFIED", "floor": "999"},
        "transverse_ceiling_certificate": {"status": "CERTIFIED", "ceiling": "0"},
        "phase_sector": ["0", "1"],
        "derivative_lower_bound": "999",
        "residual_l1_certificate": {"status": "CERTIFIED"},
        "sturm_root_count": 0,
        "root_count": 99,
    })
    forged_route = _v25_route(model.classify_required_analytic_event(forged))
    assert forged_route["component_cone_phase_anchor_certificate"] == anchor
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["1"]["controls"][0] = -0.05
    assert _rejected(floating)

    original_positive = model.v24.v20._strict_positive_certificate
    try:
        def refuse(*_args, **_kwargs):
            return {
                "status": "RESOURCE_REFUSAL",
                "reason": "adversarial exact Sturm refusal",
                "is_truth_value": False,
            }
        model.v24.v20._strict_positive_certificate = refuse
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model.v24.v20._strict_positive_certificate = original_positive

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v25 component-cone mixed-projection adversarial controls: PASS")


if __name__ == "__main__":
    run()
