#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_source_adaptive_separator_model as v30  # noqa: E402


def _margin(dominant, transverse, m, sigma):
    return v30._trim(v30.v22._padd(
        dominant,
        v30.v22._pscale(transverse, -Fraction(sigma) * Fraction(m)),
    ))


def run():
    # Diagnostic decorrelated-extrema source. In power basis:
    # D(s)=1+2s and T(s)=2+3s. Their Bernstein coefficients are [1,3]
    # and [2,5], so v30's separate global bound is 1/5 and fails well
    # below tan(pi/8). Yet the supplied diagnostic m=5/12 is strictly
    # above tan(pi/8), and both exact pointwise margins are positive.
    # The supplied m is deliberately diagnostic only: caller separators
    # remain non-authoritative under PB-007-01.
    d = [Fraction(1), Fraction(2)]
    t = [Fraction(2), Fraction(3)]
    old = v30._source_adaptive_separator_certificate(d, t, "SIN", "COS")
    assert old["status"] == "BLOCKED", old
    assert old["source_projective_ceiling"] == "1/5", old

    m = Fraction(5, 12)
    cmp_m = v30._tan_pi_8_comparison(m)
    assert cmp_m["above_boundary"] is True, cmp_m
    assert cmp_m["exact_polynomial_value"] == "1/144", cmp_m

    minus = _margin(d, t, m, 1)
    plus = _margin(d, t, m, -1)
    assert minus == [Fraction(1, 6), Fraction(3, 4)], minus
    assert plus == [Fraction(11, 6), Fraction(13, 4)], plus
    cert_minus = v30.v20._strict_positive_certificate(minus, "PB00701_V31_DIAGNOSTIC_MINUS")
    cert_plus = v30.v20._strict_positive_certificate(plus, "PB00701_V31_DIAGNOSTIC_PLUS")
    assert cert_minus["status"] == cert_plus["status"] == "CERTIFIED"

    # Exact separator-margin equality and rational neighbours. Strict
    # equality fails closed under existing MC-032 authority.
    eps = Fraction(1, 1_000_000)
    d0 = [Fraction(1)]
    t0 = [Fraction(2)]
    eq = v30.v20._strict_positive_certificate(_margin(d0, t0, Fraction(1, 2), 1), "PB00701_V31_EQ")
    inside = v30.v20._strict_positive_certificate(_margin(d0, t0, Fraction(1, 2) - eps, 1), "PB00701_V31_IN")
    outside = v30.v20._strict_positive_certificate(_margin(d0, t0, Fraction(1, 2) + eps, 1), "PB00701_V31_OUT")
    assert eq["status"] != "CERTIFIED", eq
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] != "CERTIFIED", outside

    # The algebraic boundary remains exact; no float/trigonometric estimate
    # is needed even in this diagnostic investigation.
    below = v30._tan_pi_8_comparison(Fraction(70, 169))
    above = v30._tan_pi_8_comparison(Fraction(169, 408))
    assert below["above_boundary"] is False
    assert above["above_boundary"] is True

    # Resource refusal remains explicitly non-truth-valued.
    refusal = v30.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL"
    assert refusal["is_truth_value"] is False

    print("PB-007-01 v31 pointwise-separator blocker adversarial diagnostics passed")


if __name__ == "__main__":
    run()
