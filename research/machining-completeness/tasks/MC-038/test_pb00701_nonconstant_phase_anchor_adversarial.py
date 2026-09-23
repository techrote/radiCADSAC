#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_nonconstant_phase_anchor_model as model  # noqa: E402
import pb00701_phase_sector_anchor_model as v22  # noqa: E402
import test_pb00701_phase_sector_anchor_adversarial as v22test  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as v21test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="0", rate="1/12", **extra):
    return v21test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(anchor0=None, *, c2=None, amplitude=None, offset="0", rate="1/12"):
    if anchor0 is None:
        anchor0 = [Fraction(-1, 4), Fraction(1, 1000), Fraction(-1, 1000)]
    if c2 is None:
        c2 = [0, Fraction(1, 1000)]
    if amplitude is None:
        amplitude = [1, Fraction(1, 1000)]
    return _spec(
        {0: anchor0, 2: c2},
        {1: amplitude},
        offset=offset,
        rate=rate,
    )


def _v23_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR"
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
    old = v22.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    route = _v23_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V23_ROUTE
    anchor = route["nonconstant_phase_anchor_certificate"]
    residual = route["residual_l1_certificate"]
    assert anchor["harmonic"] == 1
    assert anchor["component"] == "SIN"
    assert anchor["direction"] == "INCREASING"
    floor = anchor["amplitude_floor_certificate"]
    assert floor["relation"] == "EXACT_BERNSTEIN_CONVEX_HULL_NONZERO_AMPLITUDE_FLOOR"
    assert floor["bernstein_coefficients"] == ["1", "1001/1000"]
    assert floor["strict_rational_amplitude_floor"] == "1"
    assert anchor["strict_rational_lower_bound"] == "1/4"
    assert anchor["amplitude_derivative_is_residual"] is True
    assert any(term["harmonic"] == 1 and term["kind"] == "S_prime" for term in residual["terms"])
    assert not any(term["harmonic"] == 1 and term["kind"] == "phase_S" for term in residual["terms"])
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True

    eps = Fraction(1, 1000000)
    exact_sector = model._nonconstant_phase_anchor_derivative_certificate(
        {}, {1: [1, Fraction(1, 1000)]}, 0, Fraction(1, 6), 1, "SIN"
    )
    inside_sector = model._nonconstant_phase_anchor_derivative_certificate(
        {}, {1: [1, Fraction(1, 1000)]}, 0, Fraction(1, 6) - eps, 1, "SIN"
    )
    outside_sector = model._nonconstant_phase_anchor_derivative_certificate(
        {}, {1: [1, Fraction(1, 1000)]}, 0, Fraction(1, 6) + eps, 1, "SIN"
    )
    assert exact_sector["status"] == "CERTIFIED"
    assert inside_sector["status"] == "CERTIFIED"
    assert outside_sector["status"] == "BLOCKED"
    assert outside_sector["reason"] == "NONCONSTANT_ANCHOR_EXACT_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED"

    negative_sector = model._nonconstant_phase_anchor_derivative_certificate(
        {}, {1: [1, Fraction(1, 1000)]}, Fraction(1, 2), Fraction(1, 12), 1, "SIN"
    )
    assert negative_sector["status"] == "CERTIFIED"
    assert negative_sector["direction"] == "DECREASING"

    cosine_anchor = model._nonconstant_phase_anchor_derivative_certificate(
        {1: [1, Fraction(1, 1000)]}, {}, Fraction(1, 12), Fraction(1, 12), 1, "COS"
    )
    assert cosine_anchor["status"] == "CERTIFIED"
    assert cosine_anchor["direction"] == "DECREASING"

    zero_floor = model._amplitude_floor_certificate([0, 1])
    positive_neighbour = model._amplitude_floor_certificate([eps, 1])
    negative_neighbour = model._amplitude_floor_certificate([-eps, 1])
    assert zero_floor["status"] == "BLOCKED"
    assert zero_floor["zero_bernstein_coefficient"] is True
    assert positive_neighbour["status"] == "CERTIFIED"
    assert positive_neighbour["strict_rational_amplitude_floor"] == "1/1000000"
    assert negative_neighbour["status"] == "BLOCKED"

    conservative = model._amplitude_floor_certificate([1, -3, 3])
    assert conservative["status"] == "BLOCKED"
    assert conservative["mixed_bernstein_signs"] is True
    assert model.v19._peval([1, -3, 3], Fraction(1, 2)) == Fraction(1, 4)

    anchor_cert = model._nonconstant_phase_anchor_derivative_certificate(
        {}, {1: [1, Fraction(1, 1000)]}, 0, Fraction(1, 12), 1, "SIN"
    )
    p_equal = Fraction(1, 4) - Fraction(1, 1000)
    equality = model.v22._residual_l1_certificate(
        {0: [0, p_equal]}, {1: [1, Fraction(1, 1000)]}, Fraction(1, 12), anchor_cert
    )
    below = model.v22._residual_l1_certificate(
        {0: [0, p_equal - eps]}, {1: [1, Fraction(1, 1000)]}, Fraction(1, 12), anchor_cert
    )
    above = model.v22._residual_l1_certificate(
        {0: [0, p_equal + eps]}, {1: [1, Fraction(1, 1000)]}, Fraction(1, 12), anchor_cert
    )
    assert equality["status"] == "BLOCKED"
    assert below["status"] == "CERTIFIED"
    assert above["status"] == "BLOCKED"

    no_root = _v23_route(model.classify_required_analytic_event(
        _fixture(anchor0=[1])
    ))
    assert no_root["total_distinct_roots_closed"] == 0

    left_root = _v23_route(model.classify_required_analytic_event(
        _fixture(anchor0=[0])
    ))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}

    right_root = _v23_route(model.classify_required_analytic_event(
        _fixture(anchor0=[Fraction(-501, 1000)])
    ))
    assert right_root["right_event"]["relation"] == "ZERO"
    assert right_root["right_endpoint_root"] is True
    assert right_root["endpoint_root_multiplicity"] == {"right": 1}

    prior = model.classify_required_analytic_event(v22test._fixture())
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v23_nonconstant_amplitude_phase_anchor_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR"
        for span in prior.get("spans", [])
    )

    non_pure = _spec(
        {0: [Fraction(-1, 4)], 1: [Fraction(1, 100)], 2: [0, Fraction(1, 1000)]},
        {1: [1, Fraction(1, 1000)]},
        rate="1/12",
    )
    assert _rejected(non_pure)

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    assert model.classify_required_analytic_event(mismatch)["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "phase_anchor": {"status": "CERTIFIED"},
        "amplitude_floor": "999",
        "amplitude_floor_certificate": {"status": "CERTIFIED", "floor": "999"},
        "bernstein_coefficients": ["999"],
        "phase_sector": ["0", "1"],
        "derivative_lower_bound": "999",
        "residual_l1_certificate": {"status": "CERTIFIED"},
        "sturm_root_count": 0,
        "root_count": 99,
    })
    forged_route = _v23_route(model.classify_required_analytic_event(forged))
    assert forged_route["nonconstant_phase_anchor_certificate"] == anchor
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["sin_splines"]["1"]["controls"][0] = 1.0
    assert _rejected(floating)

    original_positive = model.v22.v20._strict_positive_certificate
    try:
        def refuse(*_args, **_kwargs):
            return {
                "status": "RESOURCE_REFUSAL",
                "reason": "adversarial exact Sturm refusal",
                "is_truth_value": False,
            }
        model.v22.v20._strict_positive_certificate = refuse
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model.v22.v20._strict_positive_certificate = original_positive

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v23 nonconstant-amplitude phase anchor adversarial controls: PASS")


if __name__ == "__main__":
    run()
