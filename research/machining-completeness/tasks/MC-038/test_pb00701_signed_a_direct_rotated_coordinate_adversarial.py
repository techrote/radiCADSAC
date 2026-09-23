#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_signed_a_direct_rotated_coordinate_model as model  # noqa: E402
import pb00701_direct_rotated_coordinate_model as v38  # noqa: E402
import pb00701_phase_correlated_two_polynomial_shared_factor_model as v37  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import test_pb00701_direct_rotated_coordinate_adversarial as v38test  # noqa: E402
import test_pb00701_phase_correlated_two_polynomial_shared_factor_adversarial as v37test  # noqa: E402
import test_pb00701_source_adaptive_separator_adversarial as v30test  # noqa: E402

C1 = [Fraction(-1), Fraction(-6, 5)]
S1 = [Fraction(-11, 10), Fraction(-6, 5)]
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)
MARGIN_EQUALITY = Fraction(862623, 2460640)


def _spec(cos_polys, sin_polys=None, *, offset="-3/16", rate="1/8", **extra):
    return v38test._spec(cos_polys, {} if sin_polys is None else sin_polys, offset=offset, rate=rate, **extra)


def _fixture(*, offset="-3/16", rate="1/8", p0=Fraction(0)):
    return _spec({0: [-p0], 1: C1, 2: [-TINY]}, {1: S1}, offset=offset, rate=rate)


def _v39_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [span["route"] for span in result.get("spans", []) if span.get("route_kind") == "PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE"]
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

    old = v38.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    old_dump = json.dumps(old, sort_keys=True)
    assert "DIRECT_ROTATED_A_NOT_STRICTLY_POSITIVE" in old_dump, old_dump
    assert v37._poly_gcd_monic(C1, S1) == [Fraction(1)]

    result = model.classify_required_analytic_event(source)
    route = _v39_route(result)
    assert route["relation"] == model.V39_ROUTE
    anchor = route["phase_correlated_signed_direct_rotated_coordinate_certificate"]
    joint = anchor["phase_correlated_signed_direct_residual_certificate"]
    derived = joint["signed_direct_rotated_coordinate_certificate"]
    cell = anchor["phase_cell_certificate"]
    assert anchor["direction"] == "DECREASING"
    assert anchor["sigma_A"] == -1
    assert anchor["sign_identity"] == "sign(D)=sigma_A*sign(h*r)*diagonal_projection_sign"
    assert anchor["orientation_is_proof_bookkeeping_only"] is True
    assert cell["cell"] == ["-3/16", "-1/16"] and cell["k"] == 0
    assert derived["C_polynomial"] == ["-1", "-6/5"]
    assert derived["S_polynomial"] == ["-11/10", "-6/5"]
    assert derived["A_polynomial"] == ["-21/20", "-6/5"]
    assert derived["B_polynomial"] == ["1/20"]
    assert derived["A_derivative_polynomial"] == ["-6/5"]
    assert derived["B_derivative_polynomial"] == ["0"]
    assert derived["sigma_A"] == -1
    assert derived["Abar_polynomial"] == ["21/20", "6/5"]
    assert derived["Bbar_polynomial"] == ["-1/20"]
    assert derived["Abar_derivative_polynomial"] == ["6/5"]
    assert derived["Bbar_derivative_polynomial"] == ["0"]
    assert derived["signed_A_orientation_certificate"]["sigma_A"] == -1
    assert derived["source_coordinates_regenerated"] is True
    assert derived["caller_orientation_trusted"] is False
    assert len(derived["phase_gap_sign_family"]["phase_gap_certificates"]) == 2
    assert all(x["certificate"]["status"] == "CERTIFIED" for x in derived["phase_gap_sign_family"]["phase_gap_certificates"])
    assert joint["selected_Abar_prime_term_retained"] is True
    assert "sigma_A*D=" in joint["oriented_selected_harmonic_identity"]
    assert "D=A'(s)*X+B'(s)*Y" in joint["physical_selected_harmonic_identity"]
    consumed = {(item["harmonic"], item["kind"]) for item in joint["consumed_selected_amplitude_terms"]}
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed
    assert not any(item["harmonic"] == 1 and item["kind"] in ("C_prime", "S_prime", "phase_C", "phase_S") for item in joint["retained_residual_terms"])
    assert any(item["harmonic"] == 2 and item["kind"] == "phase_C" for item in joint["retained_residual_terms"])
    assert joint["phase_gap_sigma_B_count"] == 2
    assert joint["orthant_count"] == 2 * joint["orthant_count_per_sigma_B"]
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in joint["orthant_certificates"])
    assert route["distinct_roots_open"] == 1 and route["all_roots_simple"] is True

    positive_source = v38test._fixture()
    positive_old = v38.classify_required_analytic_event(positive_source)
    assert positive_old["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(positive_source) == positive_old
    positive_low = model._derive_signed_direct_rotated_coordinates([Fraction(1), Fraction(6, 5)], [Fraction(11, 10), Fraction(6, 5)])
    assert positive_low["status"] == "CERTIFIED" and positive_low["sigma_A"] == 1

    pos = model._derive_signed_a_orientation([EPS])
    neg = model._derive_signed_a_orientation([-EPS])
    zero = model._derive_signed_a_orientation([0])
    crossing = model._derive_signed_a_orientation([-1, 2])
    assert pos["status"] == neg["status"] == "CERTIFIED"
    assert pos["sigma_A"] == 1 and neg["sigma_A"] == -1
    assert zero["status"] == "BLOCKED" and crossing["status"] == "BLOCKED"

    forward = model._phase_correlated_signed_direct_derivative_certificate({1: C1, 2: [-TINY]}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), 1)
    reverse = model._phase_correlated_signed_direct_derivative_certificate({1: C1, 2: [-TINY]}, {1: S1}, Fraction(-1, 16), Fraction(-1, 8), 1)
    opposite = model._phase_correlated_signed_direct_derivative_certificate({1: C1, 2: [-TINY]}, {1: S1}, Fraction(5, 16), Fraction(1, 8), 1)
    assert forward["status"] == reverse["status"] == opposite["status"] == "CERTIFIED"
    assert forward["direction"] == "DECREASING" and reverse["direction"] == "INCREASING"
    assert opposite["phase_cell_certificate"]["k"] == 1
    assert opposite["phase_cell_certificate"]["diagonal_projection_sign_number"] == -1
    assert opposite["direction"] == "INCREASING"

    exact_cell = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16))
    left_out = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16) - EPS, Fraction(-1, 16))
    left_in = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16) + EPS, Fraction(-1, 16))
    right_in = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) - EPS)
    right_out = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) + EPS)
    assert exact_cell["status"] == left_in["status"] == right_in["status"] == "CERTIFIED"
    assert left_out["status"] == right_out["status"] == "BLOCKED"

    boundary_b = model.JOINT_Y_LOWER / model.JOINT_X_UPPER
    gap_equal = model._derive_signed_direct_rotated_coordinates([-(1 + boundary_b)], [-(1 - boundary_b)])
    gap_inside = model._derive_signed_direct_rotated_coordinates([-(1 + boundary_b - EPS)], [-(1 - boundary_b + EPS)])
    gap_outside = model._derive_signed_direct_rotated_coordinates([-(1 + boundary_b + EPS)], [-(1 - boundary_b - EPS)])
    assert gap_equal["status"] == "BLOCKED" and gap_equal["phase_gap_polynomial"] == ["0"]
    assert gap_inside["status"] == "CERTIFIED"
    assert gap_outside["status"] == "BLOCKED"

    equal = model._phase_correlated_signed_direct_orthant_certificate({0: [0, MARGIN_EQUALITY], 1: C1}, {1: S1}, Fraction(1, 8), 1)
    inside = model._phase_correlated_signed_direct_orthant_certificate({0: [0, MARGIN_EQUALITY - EPS], 1: C1}, {1: S1}, Fraction(1, 8), 1)
    outside = model._phase_correlated_signed_direct_orthant_certificate({0: [0, MARGIN_EQUALITY + EPS], 1: C1}, {1: S1}, Fraction(1, 8), 1)
    assert equal["status"] == "BLOCKED", equal
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    open_route = model._phase_correlated_signed_direct_route({1: C1, 2: [-TINY]}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), "s")
    no_root = model._phase_correlated_signed_direct_route({0: [-10], 1: C1, 2: [-TINY]}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), "s")
    assert open_route["status"] == "CERTIFIED" and open_route["distinct_roots_open"] == 1
    assert no_root["status"] == "CERTIFIED" and no_root["total_distinct_roots_closed"] == 0

    left_spec = v38test.v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-1/8", rate="1/16")
    right_spec = v38test.v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-3/16", rate="1/16")
    for endpoint_spec in (left_spec, right_spec):
        assert model.classify_required_analytic_event(endpoint_spec) == v38.classify_required_analytic_event(endpoint_spec)

    unsupported = model._phase_correlated_signed_direct_derivative_certificate({1: C1}, {1: S1}, Fraction(0), Fraction(1, 16), 1)
    assert unsupported["status"] == "BLOCKED"

    forged = copy.deepcopy(source)
    forged.update({
        "sigma_A": 1, "A_sign": "POSITIVE", "orientation": 1,
        "Abar": ["999"], "Bbar": ["0"], "Abar_polynomial": ["999"], "Bbar_polynomial": ["0"],
        "Abar_derivative_polynomial": ["0"], "Bbar_derivative_polynomial": ["0"],
        "orientation_certificate": {"status": "CERTIFIED"}, "signed_A_orientation_certificate": {"status": "CERTIFIED", "sigma_A": 1},
        "rotated_coordinate_certificate": {"status": "CERTIFIED"}, "derivative_certificate": {"status": "CERTIFIED"},
        "phase_gap_sign_family": {"status": "CERTIFIED"}, "diagonal_phase_cell_certificate": {"status": "CERTIFIED"},
        "joint_margin_certificate": {"status": "CERTIFIED"}, "root_count": 0, "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v39_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["phase_correlated_signed_direct_rotated_coordinate_certificate"] == anchor

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    saved_route = model._phase_correlated_signed_direct_route
    try:
        model._phase_correlated_signed_direct_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL"
    finally:
        model._phase_correlated_signed_direct_route = saved_route

    saved_strict = model._strict_positive
    try:
        model._strict_positive = lambda *args, **kwargs: {"status": "RESOURCE_REFUSAL", "reason": "TEST_RESOURCE_REFUSAL", "is_truth_value": False}
        refused_sign = model._derive_signed_a_orientation([-1])
        assert refused_sign["status"] == "RESOURCE_REFUSAL" and refused_sign["is_truth_value"] is False
    finally:
        model._strict_positive = saved_strict
    assert model.resource_refusal()["is_truth_value"] is False

    for prior, fixture in ((v30, v30test._fixture()), (v37, v37test._fixture()), (v38, v38test._fixture())):
        historical = prior.classify_required_analytic_event(fixture)
        assert historical["status"] == "CERTIFIED"
        assert model.classify_required_analytic_event(fixture) == historical

    assert model.V39_ROUTE.startswith("EXACT_")
    print("PB-007-01 v39 signed-A direct rotated-coordinate adversarial tests passed")


if __name__ == "__main__":
    run()
