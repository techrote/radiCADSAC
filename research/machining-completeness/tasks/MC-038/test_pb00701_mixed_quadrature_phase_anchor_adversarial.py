#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_mixed_quadrature_phase_anchor_model as model  # noqa: E402
import pb00701_nonconstant_phase_anchor_model as v23  # noqa: E402
import test_pb00701_nonconstant_phase_anchor_adversarial as v23test  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as v21test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="1/12", rate="1/24", **extra):
    return v21test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(anchor0=None, *, c1=None, s1=None, c2=None, offset="1/12", rate="1/24"):
    if anchor0 is None:
        anchor0 = [Fraction(1, 10)]
    if c1 is None:
        c1 = [-1, Fraction(-1, 1000)]
    if s1 is None:
        s1 = [1, Fraction(1, 1000)]
    if c2 is None:
        c2 = [0, Fraction(1, 1000)]
    return _spec(
        {0: anchor0, 1: c1, 2: c2},
        {1: s1},
        offset=offset,
        rate=rate,
    )


def _endpoint_fixture(*, offset, rate, anchor0=None):
    if anchor0 is None:
        anchor0 = [0]
    return _spec(
        {0: anchor0, 1: [-1, Fraction(-1, 1000)], 2: [Fraction(1, 1000)]},
        {1: [1, Fraction(1, 1000)]},
        offset=offset,
        rate=rate,
    )


def _v24_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR"
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
    old = v23.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    route = _v24_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V24_ROUTE
    anchor = route["mixed_phase_anchor_certificate"]
    residual = route["residual_l1_certificate"]
    assert anchor["harmonic"] == 1
    assert anchor["direction"] == "INCREASING"
    assert anchor["projection_terms_aligned"] is True
    assert anchor["strict_rational_lower_bound"] == "1/4"
    assert anchor["cos_component_floor_certificate"]["strict_rational_amplitude_floor"] == "1"
    assert anchor["sin_component_floor_certificate"]["strict_rational_amplitude_floor"] == "1"
    assert anchor["sector_certificate"]["sin_sign"] == "POSITIVE"
    assert anchor["sector_certificate"]["cos_sign"] == "POSITIVE"
    assert any(term["harmonic"] == 1 and term["kind"] == "C_prime" for term in residual["terms"])
    assert any(term["harmonic"] == 1 and term["kind"] == "S_prime" for term in residual["terms"])
    assert not any(
        term["harmonic"] == 1 and term["kind"] in ("phase_C", "phase_S")
        for term in residual["terms"]
    )
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True

    decreasing = _v24_route(model.classify_required_analytic_event(
        _fixture(offset="1/8", rate="-1/24")
    ))
    assert decreasing["mixed_phase_anchor_certificate"]["direction"] == "DECREASING"
    assert decreasing["left_event"]["relation"] == "POSITIVE"
    assert decreasing["right_event"]["relation"] == "NEGATIVE"
    assert decreasing["distinct_roots_open"] == 1

    q2 = model._mixed_phase_anchor_derivative_certificate(
        {1: [1, Fraction(1, 1000)]},
        {1: [1, Fraction(1, 1000)]},
        Fraction(1, 3), Fraction(1, 24), 1,
    )
    assert q2["status"] == "CERTIFIED", q2
    assert q2["sector_certificate"]["sin_sign"] == "POSITIVE"
    assert q2["sector_certificate"]["cos_sign"] == "NEGATIVE"
    assert q2["direction"] == "DECREASING"

    constant_mixed = model._mixed_phase_anchor_derivative_certificate(
        {1: [-1]}, {1: [1, Fraction(1, 1000)]},
        Fraction(1, 12), Fraction(1, 24), 1,
    )
    assert constant_mixed["status"] == "CERTIFIED"
    assert constant_mixed["cos_component_floor_certificate"]["relation"] == "EXACT_CONSTANT_NONZERO_COMPONENT_FLOOR"
    assert constant_mixed["sin_component_floor_certificate"]["relation"] == "EXACT_BERNSTEIN_CONVEX_HULL_NONZERO_AMPLITUDE_FLOOR"

    eps = Fraction(1, 1000000)
    exact_sector = model._mixed_sector_certificate(Fraction(1, 12), Fraction(1, 6))
    inside_sector = model._mixed_sector_certificate(Fraction(1, 12), Fraction(1, 6) - eps)
    outside_sector = model._mixed_sector_certificate(Fraction(1, 12), Fraction(1, 6) + eps)
    assert exact_sector["status"] == "CERTIFIED"
    assert inside_sector["status"] == "CERTIFIED"
    assert outside_sector is None

    c_zero = model._component_floor_certificate([0, 1], "COS")
    c_inside = model._component_floor_certificate([eps, 1], "COS")
    c_outside = model._component_floor_certificate([-eps, 1], "COS")
    s_zero = model._component_floor_certificate([0, 1], "SIN")
    s_inside = model._component_floor_certificate([eps, 1], "SIN")
    s_outside = model._component_floor_certificate([-eps, 1], "SIN")
    assert c_zero["status"] == "BLOCKED" and s_zero["status"] == "BLOCKED"
    assert c_inside["status"] == "CERTIFIED" and s_inside["status"] == "CERTIFIED"
    assert c_outside["status"] == "BLOCKED" and s_outside["status"] == "BLOCKED"

    misaligned = model._mixed_phase_anchor_derivative_certificate(
        {1: [1]}, {1: [1]}, Fraction(1, 12), Fraction(1, 24), 1
    )
    assert misaligned["status"] == "BLOCKED"
    assert misaligned["reason"] == "MIXED_QUADRATURE_PHASE_PROJECTION_SIGN_ALIGNMENT_NOT_CERTIFIED"

    anchor_cert = model._mixed_phase_anchor_derivative_certificate(
        {1: [-1]}, {1: [1]}, Fraction(1, 12), Fraction(1, 24), 1
    )
    assert anchor_cert["status"] == "CERTIFIED"
    equality = model._mixed_residual_l1_certificate(
        {0: [0, Fraction(1, 4)], 1: [-1]}, {1: [1]}, Fraction(1, 24), anchor_cert
    )
    below = model._mixed_residual_l1_certificate(
        {0: [0, Fraction(1, 4) - eps], 1: [-1]}, {1: [1]}, Fraction(1, 24), anchor_cert
    )
    above = model._mixed_residual_l1_certificate(
        {0: [0, Fraction(1, 4) + eps], 1: [-1]}, {1: [1]}, Fraction(1, 24), anchor_cert
    )
    assert equality["status"] == "BLOCKED"
    assert below["status"] == "CERTIFIED"
    assert above["status"] == "BLOCKED"

    no_root = _v24_route(model.classify_required_analytic_event(_fixture(anchor0=[1])))
    assert no_root["total_distinct_roots_closed"] == 0

    left_root = _v24_route(model.classify_required_analytic_event(
        _endpoint_fixture(offset="1/8", rate="1/48")
    ))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}

    right_root = _v24_route(model.classify_required_analytic_event(
        _endpoint_fixture(offset="5/48", rate="1/48")
    ))
    assert right_root["right_event"]["relation"] == "ZERO"
    assert right_root["right_endpoint_root"] is True
    assert right_root["endpoint_root_multiplicity"] == {"right": 1}

    prior = model.classify_required_analytic_event(v23test._fixture())
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v24_mixed_quadrature_phase_anchor_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR"
        for span in prior.get("spans", [])
    )

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    assert model.classify_required_analytic_event(mismatch)["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "mixed_phase_anchor": {"status": "CERTIFIED"},
        "mixed_phase_anchor_certificate": {"status": "CERTIFIED", "strict_rational_lower_bound": "999"},
        "cos_component_floor_certificate": {"status": "CERTIFIED", "floor": "999"},
        "sin_component_floor_certificate": {"status": "CERTIFIED", "floor": "999"},
        "phase_sector": ["0", "1"],
        "derivative_lower_bound": "999",
        "residual_l1_certificate": {"status": "CERTIFIED"},
        "sturm_root_count": 0,
        "root_count": 99,
    })
    forged_route = _v24_route(model.classify_required_analytic_event(forged))
    assert forged_route["mixed_phase_anchor_certificate"] == anchor
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["1"]["controls"][0] = -1.0
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
    print("PB-007-01 v24 mixed-quadrature phase anchor adversarial controls: PASS")


if __name__ == "__main__":
    run()
