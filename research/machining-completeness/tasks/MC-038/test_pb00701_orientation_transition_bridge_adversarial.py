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
import test_pb00701_signed_a_direct_rotated_coordinate_adversarial as v39test  # noqa: E402

EPS = Fraction(1, 1000000)
TINY = Fraction(1, 100000000)
C1 = [Fraction(-5, 6), Fraction(2)]
S1 = [Fraction(-1, 6)]


def _spec(cos_polys, sin_polys=None, *, offset="-1/8", rate="1/16", **extra):
    return v40test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="-1/8", rate="1/16", p0=Fraction(0)):
    return _spec({0: [-p0], 1: C1}, {1: S1}, offset=offset, rate=rate)


def _v42_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"]
        for span in result.get("spans", [])
        if span.get("route_kind")
        == "PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def _cs_from_ab(a0, a1, b0, b1):
    return [a0 + b0, a1 + b1], [a0 - b0, a1 - b1]


def run():
    source = _fixture()

    # classify_required_analytic_event always executes complete v40 first and can install
    # v42 only into a residual blocked span. Seeing a v42 route here is therefore executable
    # evidence that this source survived complete predecessor authority without duplicating
    # the expensive predecessor traversal in this focused gate.
    result = model.classify_required_analytic_event(source)
    route = _v42_route(result)
    assert route["relation"] == model.V42_ROUTE
    anchor = route["orientation_transition_bridge_certificate"]
    joint = anchor["orientation_transition_residual_certificate"]
    derived = joint["transition_coordinate_certificate"]
    assert anchor["direction"] == "INCREASING"
    assert anchor["sign_identity"] == "sign(D)=sign(B')*diagonal_projection_sign"
    assert anchor["proof_cut_is_physical_event"] is False
    assert derived["C_polynomial"] == ["-5/6", "2"]
    assert derived["S_polynomial"] == ["-1/6"]
    assert derived["A_polynomial"] == ["-1/2", "1"]
    assert derived["B_polynomial"] == ["-1/3", "1"]
    assert derived["A_derivative_polynomial"] == ["1"]
    assert derived["B_derivative_polynomial"] == ["1"]
    assert derived["sigma_B_prime"] == 1
    assert derived["B_prime_bar_polynomial"] == ["1"]
    cell = anchor["phase_cell_certificate"]
    assert cell["status"] == "CERTIFIED"
    assert cell["cell"] == ["-3/16", "-1/16"]
    assert cell["diagonal_projection_sign_number"] == 1
    assert joint["two_pi_upper_theorem"] == "2*pi < 44/7 (equivalently pi < 22/7)"
    assert joint["selected_A_prime_term_retained"] is True
    assert joint["selected_B_prime_term_retained"] is True
    consumed = {(x["harmonic"], x["kind"]) for x in joint["consumed_selected_amplitude_terms"]}
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed
    assert not any(
        x["harmonic"] == 1 and x["kind"] in ("C_prime", "S_prime", "phase_C", "phase_S")
        for x in joint["retained_residual_terms"]
    )
    assert joint["residual_term_count"] == 0
    assert joint["orthant_count"] == len(joint["orthant_certificates"])
    assert all(x["certificate"]["status"] == "CERTIFIED" for x in joint["orthant_certificates"])
    assert route["all_roots_simple"] is True

    # Both whole-span v39/v40 orientation prerequisites genuinely fail for the source-owned
    # A and B. The integrated classifier above then proves the bridge only after complete v40.
    assert v40.v39._derive_signed_a_orientation([Fraction(-1, 2), 1])["status"] == "BLOCKED"
    assert v40._derive_signed_b_orientation([Fraction(-1, 3), 1])["status"] == "BLOCKED"

    # Keep a live non-anchor derivative residual explicitly without another full predecessor pass.
    residual = model._transition_derivative_certificate(
        {1: C1, 2: [TINY]}, {1: S1}, Fraction(-1, 8), Fraction(1, 16), 1
    )
    assert residual["status"] == "CERTIFIED", residual
    residual_joint = residual["orientation_transition_residual_certificate"]
    assert any(
        x["harmonic"] == 2 and x["kind"] == "phase_C"
        for x in residual_joint["retained_residual_terms"]
    )

    # Exact A-orientation zero and signed rational neighbors remain admissible and event-neutral.
    assert Fraction(derived["A_polynomial"][0]) + Fraction(1, 2) * Fraction(derived["A_polynomial"][1]) == 0
    for delta in (-EPS, EPS):
        c, s = _cs_from_ab(Fraction(-1, 2) + delta, 1, Fraction(-1, 3), 1)
        cert = model._transition_derivative_certificate(
            {1: c}, {1: s}, Fraction(-1, 8), Fraction(1, 16), 1
        )
        assert cert["status"] == "CERTIFIED", cert
        assert cert["proof_cut_is_physical_event"] is False

    # Strict B' sign is source-derived; equality/sign-changing B' fail closed and both signs work.
    pos = model._derive_transition_coordinates(C1, S1)
    neg = model._derive_transition_coordinates([-x for x in C1], [-x for x in S1])
    equal = model._derive_transition_coordinates([1, 1], [-1, 1])
    crossing = model._derive_transition_coordinates([0, -1, 1], [0, 1, -1])
    assert pos["status"] == neg["status"] == "CERTIFIED"
    assert pos["sigma_B_prime"] == 1 and neg["sigma_B_prime"] == -1
    assert equal["status"] == crossing["status"] == "BLOCKED"
    assert equal["reason"] == crossing["reason"] == "ORIENTATION_TRANSITION_B_PRIME_NOT_STRICTLY_NONZERO"

    # Exact complete-margin equality and signed rational neighbors. A=0, B=s, B'=1
    # makes the limiting adverse-B orthant L-(44/7)|r|*U*s, equal at s=1.
    equal_rate = model.Y_LOWER / (model.TWO_PI_UPPER * model.X_UPPER)
    equal_margin = model._transition_orthant_certificate(
        {1: [0, 1]}, {1: [0, -1]}, equal_rate, 1, 1
    )
    inside_margin = model._transition_orthant_certificate(
        {1: [0, 1]}, {1: [0, -1]}, equal_rate - EPS, 1, 1
    )
    outside_margin = model._transition_orthant_certificate(
        {1: [0, 1]}, {1: [0, -1]}, equal_rate + EPS, 1, 1
    )
    assert equal_margin["status"] == "BLOCKED"
    assert "0" in equal_margin["failed_margin_polynomial"]
    assert inside_margin["status"] == "CERTIFIED", inside_margin
    assert outside_margin["status"] == "BLOCKED", outside_margin

    # Exact supported diagonal-cell endpoints and just-outside rational neighbors.
    exact_cell = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16))
    left_out = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16) - EPS, Fraction(-1, 16))
    left_in = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16) + EPS, Fraction(-1, 16))
    right_in = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) - EPS)
    right_out = model.v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) + EPS)
    assert exact_cell["status"] == left_in["status"] == right_in["status"] == "CERTIFIED"
    assert left_out["status"] == right_out["status"] == "BLOCKED"

    # Positive/negative phase rates and the opposite diagonal projection sign.
    forward = model._transition_derivative_certificate(
        {1: C1}, {1: S1}, Fraction(-1, 8), Fraction(1, 16), 1
    )
    reverse = model._transition_derivative_certificate(
        {1: C1}, {1: S1}, Fraction(-1, 16), Fraction(-1, 16), 1
    )
    opposite = model._transition_derivative_certificate(
        {1: C1}, {1: S1}, Fraction(3, 8), Fraction(1, 16), 1
    )
    assert forward["status"] == reverse["status"] == opposite["status"] == "CERTIFIED"
    assert forward["direction"] == reverse["direction"] == "INCREASING"
    assert opposite["phase_cell_certificate"]["diagonal_projection_sign_number"] == -1
    assert opposite["direction"] == "DECREASING"

    # Historical v39/v40 successes remain byte-for-byte owned by complete predecessor authority.
    v40_source = v40test._fixture()
    v40_result = v40.classify_required_analytic_event(v40_source)
    assert v40_result["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(v40_source) == v40_result
    v39_source = v39test._fixture()
    assert model.classify_required_analytic_event(v39_source) == v40.classify_required_analytic_event(v39_source)

    # Forged proof metadata cannot manufacture authority. Use the fast historical v40 fixture
    # so sanitation is tested without repeating the complete residual acceptance traversal.
    forged = copy.deepcopy(v40_source)
    forged.update({
        "A": [999], "B": [999], "B_prime": [999], "sigma_B_prime": -1,
        "orientation_certificate": {"status": "CERTIFIED"},
        "transition_margin": "999", "transition_margin_certificate": {"status": "CERTIFIED"},
        "root_count": 0, "multiplicity_certificate": 99,
    })
    assert model.classify_required_analytic_event(forged) == v40_result

    mismatch = copy.deepcopy(v40_source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(v40_source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    saved_strict = model._strict_positive
    try:
        model._strict_positive = lambda *args, **kwargs: {
            "status": "RESOURCE_REFUSAL", "reason": "TEST_RESOURCE_REFUSAL", "is_truth_value": False
        }
        refused = model._derive_transition_coordinates(C1, S1)
        assert refused["status"] == "RESOURCE_REFUSAL" and refused["is_truth_value"] is False
    finally:
        model._strict_positive = saved_strict
    assert model.resource_refusal()["is_truth_value"] is False

    assert result.get("mc_b_established") is not True
    assert result.get("mc_1_established") is not True
    assert model.V42_ROUTE.startswith("EXACT_")
    print("PB-007-01 v42 orientation-transition bridge adversarial tests: PASS")


if __name__ == "__main__":
    run()
