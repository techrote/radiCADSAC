#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_orientation_transition_bridge_model as model  # noqa: E402
import pb00701_signed_b_anti_diagonal_model as v40  # noqa: E402
import test_pb00701_signed_b_anti_diagonal_adversarial as v40test  # noqa: E402

C1 = [Fraction(-23, 6), Fraction(11)]
S1 = [Fraction(17, 6), Fraction(-9)]
TINY = Fraction(1, 10**10)
EPS = Fraction(1, 10**6)


def _spec(cos_polys, sin_polys=None, *, offset="-1/8", rate="1/1000", **extra):
    return v40test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="-1/8", rate="1/1000"):
    return _spec({1: C1, 2: [TINY]}, {1: S1}, offset=offset, rate=rate)


def _route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def run():
    source = _fixture()

    old = v40.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    result = model.classify_required_analytic_event(source)
    route = _route(result)
    assert route["relation"] == model.V42_ROUTE
    anchor = route["orientation_transition_bridge_certificate"]
    joint = anchor["orientation_transition_residual_certificate"]
    derived = joint["transition_coordinate_certificate"]

    assert derived["A_polynomial"] == ["-1/2", "1"]
    assert derived["B_polynomial"] == ["-10/3", "10"]
    assert derived["A_derivative_polynomial"] == ["1"]
    assert derived["B_derivative_polynomial"] == ["10"]
    assert derived["sigma_B_prime"] == 1
    assert anchor["direction"] == "INCREASING"
    assert anchor["sign_identity"] == "sign(D)=sign(B')*diagonal_projection_sign"
    assert anchor["proof_cut_is_physical_event"] is False
    assert joint["two_pi_upper_theorem"] == "2*pi < 44/7 (equivalently pi < 22/7)"
    assert joint["selected_A_prime_term_retained"] is True
    assert joint["selected_B_prime_term_retained"] is True
    assert joint["orthant_count"] == len(joint["orthant_certificates"])
    assert all(x["certificate"]["status"] == "CERTIFIED" for x in joint["orthant_certificates"])
    consumed = {(x["harmonic"], x["kind"]) for x in joint["consumed_selected_amplitude_terms"]}
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed
    assert any(x["harmonic"] == 2 for x in joint["retained_residual_terms"])
    assert route["all_roots_simple"] is True

    # Both whole-span orientation routes are genuinely unavailable.
    assert v40.v39._derive_signed_a_orientation([Fraction(-1, 2), 1])["status"] == "BLOCKED"
    assert v40._derive_signed_b_orientation([Fraction(-10, 3), 10])["status"] == "BLOCKED"

    # Strict B' sign is source-derived and equality/crossing fail closed.
    pos = model._derive_transition_coordinates(C1, S1)
    neg = model._derive_transition_coordinates([-x for x in C1], [-x for x in S1])
    assert pos["status"] == neg["status"] == "CERTIFIED"
    assert pos["sigma_B_prime"] == 1 and neg["sigma_B_prime"] == -1
    equal = model._derive_transition_coordinates([1, 1], [-1, 1])
    assert equal["status"] == "BLOCKED"
    crossing = model._derive_transition_coordinates([0, -1, 1], [0, 1, -1])
    assert crossing["status"] == "BLOCKED"

    # Supported cell endpoints are exact; just-outside rational neighbours fail containment.
    inside = model._transition_derivative_certificate({1: C1}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), 1)
    assert inside["status"] == "CERTIFIED", inside
    left_out = model._transition_derivative_certificate({1: C1}, {1: S1}, Fraction(-3, 16)-EPS, Fraction(1, 1000), 1)
    right_out = model._transition_derivative_certificate({1: C1}, {1: S1}, Fraction(-1, 16), Fraction(1, 1000), 1)
    assert left_out["status"] != "CERTIFIED"
    assert right_out["status"] != "CERTIFIED"

    # Reverse phase rate does not change B'Y-owned derivative sign when the same Y-sign cell is traversed.
    reverse = model.classify_required_analytic_event(_fixture(offset="-124/1000", rate="-1/1000"))
    reverse_route = _route(reverse)
    assert reverse_route["orientation_transition_bridge_certificate"]["direction"] == "INCREASING"

    # Opposite diagonal cell reverses physical derivative sign.
    opposite = model.classify_required_analytic_event(_fixture(offset="3/8", rate="1/1000"))
    opposite_route = _route(opposite)
    assert opposite_route["orientation_transition_bridge_certificate"]["direction"] == "DECREASING"

    # Historical v39/v40 ownership remains byte-for-byte unchanged.
    prior = v40test._fixture()
    prior_old = v40.classify_required_analytic_event(prior)
    assert prior_old["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(prior) == prior_old

    # Forged proof metadata is non-authoritative.
    forged = copy.deepcopy(source)
    forged.update({
        "A": [999], "B": [999], "B_prime": [999], "sigma_B_prime": -1,
        "orientation_certificate": {"status": "CERTIFIED"},
        "transition_margin": "999", "transition_margin_certificate": {"status": "CERTIFIED"},
    })
    assert model.classify_required_analytic_event(forged) == result

    # Exact refusal remains non-truth.
    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL" and refusal["is_truth_value"] is False

    # Global research gate is not promoted by this bounded repair.
    assert result.get("mc_b_established") is not True
    assert result.get("mc_1_established") is not True


if __name__ == "__main__":
    run()
    print("PB-007-01 v42 orientation-transition adversarial tests: PASS")
