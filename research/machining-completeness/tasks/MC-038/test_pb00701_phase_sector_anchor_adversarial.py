#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_phase_sector_anchor_model as model  # noqa: E402
import pb00701_l1_sign_orthant_envelope_model as v21  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as v21test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="0", rate="1/12", **extra):
    return v21test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(anchor0=None, *, c2=None, amplitude=Fraction(1), offset="0", rate="1/12"):
    if anchor0 is None:
        anchor0 = [Fraction(-1, 4), Fraction(1, 1000), Fraction(-1, 1000)]
    if c2 is None:
        c2 = [0, Fraction(1, 1000)]
    return _spec(
        {0: anchor0, 2: c2},
        {1: [amplitude]},
        offset=offset,
        rate=rate,
    )


def _v22_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR"
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
    old = v21.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    route = _v22_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V22_ROUTE
    assert route["active_positive_harmonics"] == [1, 2]
    anchor = route["phase_anchor_certificate"]
    residual = route["residual_l1_certificate"]
    assert anchor["harmonic"] == 1
    assert anchor["component"] == "SIN"
    assert anchor["direction"] == "INCREASING"
    assert anchor["strict_rational_lower_bound"] == "1/4"
    assert anchor["sector_certificate"]["sector_interval"] == ["-1/6", "1/6"]
    assert anchor["sector_certificate"]["quadrature_magnitude_lower_bound"] == "1/2"
    assert anchor["pi_lower_theorem"] == "pi > 3"
    assert residual["relation"] == "EXACT_FINITE_SIGN_ORTHANT_RESIDUAL_L1_BELOW_PHASE_ANCHOR"
    assert any(term["kind"] == "P_prime" for term in residual["terms"])
    assert residual["orthant_count"] == 8
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in residual["orthant_certificates"])
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True
    assert route["numerical_trigonometry_used"] is False

    eps = Fraction(1, 1000000)
    boundary = model._phase_anchor_derivative_certificate(
        {}, {1: [1]}, Fraction(0), Fraction(1, 6), 1, "SIN"
    )
    inside = model._phase_anchor_derivative_certificate(
        {}, {1: [1]}, Fraction(0), Fraction(1, 6) - eps, 1, "SIN"
    )
    outside = model._phase_anchor_derivative_certificate(
        {}, {1: [1]}, Fraction(0), Fraction(1, 6) + eps, 1, "SIN"
    )
    assert boundary["status"] == "CERTIFIED"
    assert inside["status"] == "CERTIFIED"
    assert outside["status"] == "BLOCKED"
    assert outside["reason"] == "PHASE_ANCHOR_EXACT_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED"

    negative_sector = model._phase_anchor_derivative_certificate(
        {}, {1: [1]}, Fraction(1, 2), Fraction(1, 12), 1, "SIN"
    )
    assert negative_sector["status"] == "CERTIFIED"
    assert negative_sector["direction"] == "DECREASING"
    assert negative_sector["sector_certificate"]["quadrature_sign"] == "NEGATIVE"

    cosine_anchor = model._phase_anchor_derivative_certificate(
        {1: [1]}, {}, Fraction(1, 12), Fraction(1, 12), 1, "COS"
    )
    assert cosine_anchor["status"] == "CERTIFIED"
    assert cosine_anchor["direction"] == "DECREASING"
    assert cosine_anchor["sector_certificate"]["derivative_quadrature"] == "SINE"

    assert model._phase_anchor_derivative_certificate(
        {}, {1: [1, 1]}, 0, Fraction(1, 12), 1, "SIN"
    ) is None
    assert model._phase_anchor_derivative_certificate(
        {1: [Fraction(1, 100)]}, {1: [1]}, 0, Fraction(1, 12), 1, "SIN"
    ) is None

    anchor_cert = model._phase_anchor_derivative_certificate(
        {}, {1: [1]}, 0, Fraction(1, 12), 1, "SIN"
    )
    equality = model._residual_l1_certificate(
        {0: [0, Fraction(1, 4)]}, {1: [1]}, Fraction(1, 12), anchor_cert
    )
    below = model._residual_l1_certificate(
        {0: [0, Fraction(1, 4) - eps]}, {1: [1]}, Fraction(1, 12), anchor_cert
    )
    above = model._residual_l1_certificate(
        {0: [0, Fraction(1, 4) + eps]}, {1: [1]}, Fraction(1, 12), anchor_cert
    )
    assert equality["status"] == "BLOCKED"
    assert equality["reason"] == "PHASE_ANCHOR_RESIDUAL_L1_STRICT_DOMINANCE_NOT_CERTIFIED"
    assert below["status"] == "CERTIFIED"
    assert above["status"] == "BLOCKED"

    no_root = _v22_route(model.classify_required_analytic_event(
        _fixture([1, Fraction(1, 1000), Fraction(-1, 1000)])
    ))
    assert no_root["left_event"]["relation"] == "POSITIVE"
    assert no_root["right_event"]["relation"] == "POSITIVE"
    assert no_root["total_distinct_roots_closed"] == 0

    left_root = _v22_route(model.classify_required_analytic_event(
        _fixture([0, Fraction(1, 1000), Fraction(-1, 1000)])
    ))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}
    assert left_root["distinct_roots_open"] == 0

    prior_spec = v21test._l1_fixture()
    prior = model.classify_required_analytic_event(prior_spec)
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v22_phase_sector_partial_anchor_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V21_EXACT_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE"
        for span in prior.get("spans", [])
    )

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    mismatch_result = model.classify_required_analytic_event(mismatch)
    assert mismatch_result["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "phase_anchor": {"status": "CERTIFIED", "lower": "999"},
        "phase_sector": ["0", "1"],
        "derivative_lower_bound": "999",
        "partial_event_certificate": {"status": "CERTIFIED"},
        "residual_l1_certificate": {"status": "CERTIFIED"},
        "orthants": [{"margin": "999"}],
        "sturm_root_count": 0,
        "root_count": 99,
    })
    forged_route = _v22_route(model.classify_required_analytic_event(forged))
    assert forged_route["phase_anchor_certificate"] == route["phase_anchor_certificate"]
    assert forged_route["residual_l1_certificate"] == route["residual_l1_certificate"]
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["sin_splines"]["1"]["controls"][0] = 1.0
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
    print("PB-007-01 v22 phase-sector partial derivative anchor adversarial controls: PASS")


if __name__ == "__main__":
    run()
