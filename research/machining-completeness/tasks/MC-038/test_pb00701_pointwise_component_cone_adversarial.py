#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_pointwise_component_cone_model as model  # noqa: E402
import pb00701_component_cone_phase_anchor_model as v25  # noqa: E402
import pb00701_mixed_quadrature_phase_anchor_model as v24  # noqa: E402
import test_pb00701_component_cone_phase_anchor_adversarial as v25test  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as v21test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="-1/6", rate="1/3", **extra):
    return v21test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


# Degree-4 source polynomials expressed in the power basis. Their exact Bernstein
# controls are respectively
#   S: [10.81, 10.76, 10.84, 11.35, 10.76]
#   C: [4.15, 4.25, 5.42, 4.03, 4.03]
# so v25 has S_floor/2=5.38 <= C_ceiling=5.42 and must fail closed. Pointwise,
# however, the correlated polynomials plus their amplitude derivatives retain a
# strict exact margin, which v26 proves with finite Sturm-certified orthants.
S_POINTWISE = [
    Fraction(1081, 100), Fraction(-1, 5), Fraction(39, 50),
    Fraction(6, 5), Fraction(-183, 100),
]
C_POINTWISE = [
    Fraction(83, 20), Fraction(2, 5), Fraction(321, 50),
    Fraction(-363, 25), Fraction(379, 50),
]


def _fixture(*, offset="-1/6", rate="1/3", swap=False):
    if not swap:
        cos = {0: [0], 1: C_POINTWISE, 2: [Fraction(1, 10000)]}
        sin = {1: S_POINTWISE}
    else:
        cos = {0: [0], 1: S_POINTWISE, 2: [Fraction(1, 10000)]}
        sin = {1: C_POINTWISE}
    return _spec(cos, sin, offset=offset, rate=rate)


def _v26_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS"
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
    old = v25.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    assert any(
        span.get("route", {}).get("reason") in {
            "MIXED_PROJECTION_COMPONENT_CONE_PHASE_ANCHOR_NOT_CERTIFIED",
            "POINTWISE_COMPONENT_CONE_RESIDUAL_EVENT_NOT_CERTIFIED",
        }
        or any(
            attempt.get("reason") == "MIXED_PROJECTION_COMPONENT_CONE_STRICT_SEPARATION_NOT_CERTIFIED"
            for attempt in span.get("route", {}).get("attempts", [])
            if isinstance(attempt, dict)
        )
        for span in old.get("spans", [])
    ), old

    route = _v26_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V26_ROUTE
    anchor = route["pointwise_component_cone_certificate"]
    combined = anchor["pointwise_cone_residual_certificate"]
    assert anchor["harmonic"] == 1
    assert anchor["dominant_component"] == "SIN"
    assert anchor["transverse_component"] == "COS"
    assert anchor["direction"] == "INCREASING"
    assert anchor["dominant_sign_certificate"]["amplitude_sign"] == "POSITIVE"
    assert anchor["dominant_sign_certificate"]["relation"] == "EXACT_CLOSED_INTERVAL_STURM_FIXED_COMPONENT_SIGN"
    assert combined["relation"] == "EXACT_POINTWISE_COMPONENT_CONE_PLUS_RESIDUAL_SIGN_ORTHANT_DOMINANCE"
    assert combined["phase_scale"] == "2"
    assert combined["orthant_count"] == 16
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in combined["orthant_certificates"])
    assert any(term["harmonic"] == 1 and term["kind"] == "C_prime" for term in combined["residual_terms"])
    assert any(term["harmonic"] == 1 and term["kind"] == "S_prime" for term in combined["residual_terms"])
    assert not any(
        term["harmonic"] == 1 and term["kind"] in ("phase_C", "phase_S")
        for term in combined["residual_terms"]
    )
    assert any(term["harmonic"] == 2 and term["kind"] == "phase_C" for term in combined["residual_terms"])
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True

    # v25's separate bounds overlap exactly as intended for the acceptance source.
    v25_floor = v24._component_floor_certificate(S_POINTWISE, "SIN")
    v25_ceiling = v25._component_abs_upper_certificate(C_POINTWISE, "COS")
    assert v25_floor["status"] == "CERTIFIED"
    assert v25_ceiling["status"] == "CERTIFIED"
    assert Fraction(v25_floor["strict_rational_amplitude_floor"]) / 2 <= Fraction(
        v25_ceiling["exact_rational_absolute_ceiling"]
    )

    decreasing = _v26_route(model.classify_required_analytic_event(
        _fixture(offset="1/6", rate="-1/3")
    ))
    assert decreasing["pointwise_component_cone_certificate"]["direction"] == "DECREASING"
    assert decreasing["left_event"]["relation"] == "POSITIVE"
    assert decreasing["right_event"]["relation"] == "NEGATIVE"
    assert decreasing["distinct_roots_open"] == 1

    c_source = _fixture(offset="1/12", rate="1/3", swap=True)
    assert v25.classify_required_analytic_event(c_source)["status"] == "BLOCKED"
    c_route = _v26_route(model.classify_required_analytic_event(c_source))
    c_anchor = c_route["pointwise_component_cone_certificate"]
    assert c_anchor["dominant_component"] == "COS"
    assert c_anchor["transverse_component"] == "SIN"
    assert c_anchor["sector_certificate"]["component"] == "SIN"
    assert c_anchor["sector_certificate"]["quadrature_sign"] == "POSITIVE"
    assert c_anchor["direction"] == "DECREASING"
    assert c_route["distinct_roots_open"] == 1

    # Exact fixed-sign authority is broader than the old strict Bernstein-floor test.
    positive_but_bernstein_boundary = [1, -2, 2]  # 1-2s+2s^2 >= 1/2
    old_floor = v24._component_floor_certificate(positive_but_bernstein_boundary, "SIN")
    assert old_floor["status"] != "CERTIFIED", old_floor
    sign_cert = model._fixed_sign_sturm_certificate(positive_but_bernstein_boundary, "SIN")
    assert sign_cert["status"] == "CERTIFIED", sign_cert
    assert sign_cert["amplitude_sign"] == "POSITIVE"

    sign_changing_transverse = model._pointwise_component_cone_derivative_certificate(
        {1: [Fraction(-1, 10), Fraction(1, 5)], 2: [Fraction(1, 10000)]},
        {1: [10]},
        Fraction(-1, 6), Fraction(1, 3), 1,
    )
    assert sign_changing_transverse["status"] == "CERTIFIED", sign_changing_transverse
    assert sign_changing_transverse["dominant_component"] == "SIN"

    eps = Fraction(1, 1000000)
    exact_sector = v25._half_magnitude_sector_certificate("COS", Fraction(-1, 6), Fraction(1, 6))
    inside_sector = v25._half_magnitude_sector_certificate("COS", Fraction(-1, 6), Fraction(1, 6) - eps)
    outside_sector = v25._half_magnitude_sector_certificate("COS", Fraction(-1, 6), Fraction(1, 6) + eps)
    assert exact_sector["status"] == "CERTIFIED"
    assert inside_sector["status"] == "CERTIFIED"
    assert outside_sector is None

    equality = model._pointwise_component_cone_derivative_certificate(
        {1: [1]}, {1: [2]}, Fraction(-1, 6), Fraction(1, 3), 1
    )
    inside = model._pointwise_component_cone_derivative_certificate(
        {1: [1]}, {1: [Fraction(2) + eps]}, Fraction(-1, 6), Fraction(1, 3), 1
    )
    outside = model._pointwise_component_cone_derivative_certificate(
        {1: [1]}, {1: [Fraction(2) - eps]}, Fraction(-1, 6), Fraction(1, 3), 1
    )
    assert equality["status"] == "BLOCKED"
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED"

    residual_equal = model._pointwise_combined_orthant_certificate(
        {0: [0, 2], 1: [1]}, {1: [4]}, Fraction(1, 3), 1, "SIN", 1
    )
    residual_below = model._pointwise_combined_orthant_certificate(
        {0: [0, Fraction(2) - eps], 1: [1]}, {1: [4]}, Fraction(1, 3), 1, "SIN", 1
    )
    residual_above = model._pointwise_combined_orthant_certificate(
        {0: [0, Fraction(2) + eps], 1: [1]}, {1: [4]}, Fraction(1, 3), 1, "SIN", 1
    )
    assert residual_equal["status"] == "BLOCKED"
    assert residual_below["status"] == "CERTIFIED"
    assert residual_above["status"] == "BLOCKED"

    sign_failure = model._fixed_sign_sturm_certificate([0, 1], "SIN")
    assert sign_failure["status"] == "BLOCKED"

    # Historical v25 ownership and its endpoint/no-root contracts remain intact.
    prior = model.classify_required_analytic_event(v25test._fixture())
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v26_pointwise_component_cone_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR"
        for span in prior.get("spans", [])
    )
    no_root = model.classify_required_analytic_event(v25test._fixture(anchor0=[Fraction(21, 10)]))
    assert no_root["status"] == "CERTIFIED"
    left_root = model.classify_required_analytic_event(
        v25test._fixture(anchor0=[Fraction(49, 1000)], offset="0", rate="1/12")
    )
    left_routes = [span["route"] for span in left_root["spans"] if span.get("route", {}).get("status") == "CERTIFIED"]
    assert left_routes and any(r.get("left_endpoint_root") is True for r in left_routes)
    right_root = model.classify_required_analytic_event(
        v25test._fixture(anchor0=[Fraction(-51, 1000)], offset="-1/12", rate="1/12")
    )
    right_routes = [span["route"] for span in right_root["spans"] if span.get("route", {}).get("status") == "CERTIFIED"]
    assert right_routes and any(r.get("right_endpoint_root") is True for r in right_routes)

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    assert model.classify_required_analytic_event(mismatch)["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "pointwise_component_cone": {"status": "CERTIFIED"},
        "pointwise_component_cone_certificate": {"status": "CERTIFIED"},
        "dominant_sign_certificate": {"status": "CERTIFIED", "amplitude_sign_number": -1},
        "combined_orthant_certificates": [{"status": "CERTIFIED"}],
        "pointwise_margins": ["999"],
        "component_cone_certificate": {"status": "CERTIFIED"},
        "phase_sector": ["0", "1"],
        "sturm_root_count": 0,
        "root_count": 99,
    })
    forged_route = _v26_route(model.classify_required_analytic_event(forged))
    assert forged_route["pointwise_component_cone_certificate"] == anchor
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["1"]["controls"][0] = 4.15
    assert _rejected(floating)

    original_positive = model.v20._strict_positive_certificate
    try:
        def refuse(*_args, **_kwargs):
            return {
                "status": "RESOURCE_REFUSAL",
                "reason": "adversarial exact Sturm refusal",
                "is_truth_value": False,
            }
        model.v20._strict_positive_certificate = refuse
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model.v20._strict_positive_certificate = original_positive

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v26 pointwise component-cone/residual orthant adversarial controls: PASS")


if __name__ == "__main__":
    run()
