#!/usr/bin/env python3
"""A rational-turn boundary for direct MTP irreducibility-lemma transfer.

Exact source lowering, identities and jets are executable. Irreducibility and
standard trigonometric facts are reviewed mathematical premises, explicitly
distinguished from these finite computations. No general root solver is claimed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REPORT = HERE / "pb00701-mtp-irreducible-boundary.json"
SCHEMA = "pb00701.mtp-irreducible-boundary.v1"
BASE_MAIN = "9eea5786f93c71090d4a3d4c7478d65a3f066d42"
SOURCE_ID = "research:pb00701:mtp-irreducible-boundary:quadratic-touch"
PARAMETER = "pb00701-mtp-irreducible-boundary-original-t"
MAX_BYTES = 512 * 1024
MAX_REFERENCE_BYTES = 64 * 1024
MAX_CODE_BYTES = 128 * 1024
MAX_NODES = 16384
MAX_DEPTH = 24
MAX_STRING = 4096
MAX_TERMS = 64
MAX_DEGREE = 6
MAX_RATIONAL_BITS = 256
MAX_INTERMEDIATE_BITS = 1024
REFERENCE_PINS = {
    "docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md":
        "6005fc55e2d18e71639e6bc31cfbc1597bf4a915",
    "research/machining-completeness/tasks/MC-038/pb00701_pfaffian_coefficient_boundary.py":
        "2fe093dca21de8e6dc60e275825955ec0161f6ec",
    "research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py":
        "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    "research/machining-completeness/tasks/MC-038/pb00701-pfaffian-coefficient-boundary.json":
        "fe82029ab0360d422a9aea716157cf70b6fc9ec1",
}


class Refusal(ValueError):
    def __init__(self, reason, code="UNESTABLISHED"):
        super().__init__(reason)
        self.reason, self.code = reason, code

    def as_record(self):
        return {"status": self.code, "reason": self.reason,
                "boundary_certificate_established": False,
                "direct_theorem_transfer_established": False,
                "source_zero_set_established": False, "source_zero_set": None,
                "production_authorized": False}


def need(condition, reason, code="UNESTABLISHED"):
    if not condition:
        raise Refusal(reason, code)


def bounded_bytes(value):
    """Exact JSON preflight before recursive serialization."""
    stack, seen, nodes, estimate = [(value, 0)], set(), 0, 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        need(nodes <= MAX_NODES and depth <= MAX_DEPTH,
             "JSON node/depth budget", "RESOURCE_REFUSAL")
        kind = type(item)
        if kind in (dict, list):
            need(id(item) not in seen, "Cyclic or shared JSON container", "RESOURCE_REFUSAL")
            seen.add(id(item))
            need(len(item) <= MAX_NODES, "JSON container budget", "RESOURCE_REFUSAL")
            estimate += 2 + 2 * len(item)
            if kind is dict:
                need(all(type(k) is str for k in item), "Exact JSON string keys required")
                stack.extend((k, depth + 1) for k in item)
                stack.extend((v, depth + 1) for v in item.values())
            else:
                stack.extend((v, depth + 1) for v in item)
        elif kind is str:
            need(len(item) <= MAX_STRING, "JSON string budget", "RESOURCE_REFUSAL")
            estimate += 6 * len(item) + 2
        elif kind is int:
            need(item.bit_length() <= MAX_RATIONAL_BITS,
                 "JSON integer budget", "RESOURCE_REFUSAL")
            estimate += 80
        elif kind in (bool, type(None)):
            estimate += 5
        else:
            raise Refusal("Nonexact JSON value", "RESOURCE_REFUSAL")
        need(estimate <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(raw) <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    return raw


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def rational_parts(token):
    need(type(token) is str and 0 < len(token) <= 160,
         "Bounded exact rational token required", "RESOURCE_REFUSAL")
    need(re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", token, re.ASCII) is not None,
         "Canonical ASCII integer/ratio required")
    parts = token.split("/")
    numerator, denominator = int(parts[0]), int(parts[1]) if len(parts) == 2 else 1
    need(max(numerator.bit_length(), denominator.bit_length()) <= MAX_RATIONAL_BITS,
         "Rational operand budget", "RESOURCE_REFUSAL")
    need(token != "-0" and gcd(abs(numerator), denominator) == 1 and
         (len(parts) == 1 or (denominator > 1 and numerator != 0)),
         "Noncanonical rational token")
    return numerator, denominator


def rational(token):
    return Fraction(*rational_parts(token))


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def _integer(token):
    need(len(token) <= 80, "JSON integer text budget", "RESOURCE_REFUSAL")
    result = int(token)
    need(result.bit_length() <= MAX_RATIONAL_BITS, "JSON integer budget", "RESOURCE_REFUSAL")
    return result


def parse_json_bytes(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES,
         "JSON input byte budget", "RESOURCE_REFUSAL")
    def reject(_):
        raise Refusal("Nonexact JSON numeric token")
    try:
        result = json.loads(raw, object_pairs_hook=_pairs, parse_int=_integer,
                            parse_float=reject, parse_constant=reject)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise Refusal("Invalid bounded JSON") from error
    bounded_bytes(result)
    return result


def _read_bounded(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "File byte budget", "RESOURCE_REFUSAL")
    return raw


def git_blob(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "Bounded exact blob bytes required", "RESOURCE_REFUSAL")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def capture_references():
    """Pin context only. None of these project files is imported or executed."""
    records = []
    for name, expected in sorted(REFERENCE_PINS.items()):
        path = ROOT / name
        need(not path.is_symlink() and path.resolve() == path,
             "Reference path is not the original regular path")
        try:
            raw = _read_bounded(path, MAX_REFERENCE_BYTES)
        except OSError as error:
            raise Refusal("Missing bounded reference: " + name) from error
        need(git_blob(raw) == expected, "Reference bytes changed: " + name)
        records.append({"path": name, "git_blob": expected,
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                        "use": "NONEXECUTED_SOURCE_GRAMMAR_AND_PRIOR_BOUNDARY_REFERENCE"})
    return records


# Sparse monomials use (T exponent, Y exponent, K exponent). All arithmetic is
# rational. K remains a formal indeterminate here; its meaning pi is bound
# separately in the source theorem, never replaced by a rational approximation.
def _coefficient(value):
    need(type(value) is Fraction, "Exact internal rational coefficient required")
    need(max(value.numerator.bit_length(), value.denominator.bit_length()) <= MAX_INTERMEDIATE_BITS,
         "Polynomial arithmetic budget", "RESOURCE_REFUSAL")
    return value


def _number(value):
    need(type(value) in (int, Fraction), "Exact internal integer/rational required")
    if type(value) is int:
        need(value.bit_length() <= MAX_INTERMEDIATE_BITS,
             "Integer operand budget", "RESOURCE_REFUSAL")
        value = Fraction(value)
    return _coefficient(value)


def check_polynomial(poly):
    need(type(poly) is dict and len(poly) <= MAX_TERMS,
         "Sparse polynomial term budget", "RESOURCE_REFUSAL")
    for powers, value in poly.items():
        need(type(powers) is tuple and len(powers) == 3 and
             all(type(p) is int and 0 <= p <= MAX_DEGREE for p in powers) and
             sum(powers) <= MAX_DEGREE, "Polynomial degree budget", "RESOURCE_REFUSAL")
        need(_coefficient(value) != 0, "Sparse polynomial contains zero term")
    return poly


def monomial(value, t=0, y=0, k=0):
    value = _number(value)
    return check_polynomial({(t, y, k): value} if value else {})


def add(*polynomials):
    result = {}
    need(len(polynomials) <= 8, "Polynomial sum budget", "RESOURCE_REFUSAL")
    for poly in polynomials:
        check_polynomial(poly)
        for powers, value in poly.items():
            result[powers] = _coefficient(result.get(powers, Fraction(0)) + value)
            if not result[powers]:
                del result[powers]
        check_polynomial(result)
    return result


def scale(poly, value):
    check_polynomial(poly)
    value = _number(value)
    return check_polynomial({p: _coefficient(c * value) for p, c in poly.items() if c * value})


def multiply(left, right):
    check_polynomial(left)
    check_polynomial(right)
    result = {}
    for lp, lv in left.items():
        for rp, rv in right.items():
            powers = tuple(a + b for a, b in zip(lp, rp))
            need(sum(powers) <= MAX_DEGREE, "Product degree budget", "RESOURCE_REFUSAL")
            value = _coefficient(lv * rv)
            result[powers] = _coefficient(result.get(powers, Fraction(0)) + value)
            if not result[powers]:
                del result[powers]
        check_polynomial(result)
    return result


def derivative(poly, variable):
    check_polynomial(poly)
    need(type(variable) is int and variable in (0, 1, 2), "Unknown polynomial variable")
    result = {}
    for powers, value in poly.items():
        exponent = powers[variable]
        if exponent:
            reduced = list(powers)
            reduced[variable] -= 1
            result[tuple(reduced)] = _coefficient(value * exponent)
    return check_polynomial(result)


def substitute(poly, variable, replacement):
    """Finite polynomial substitution, with every product checked."""
    check_polynomial(poly)
    check_polynomial(replacement)
    need(type(variable) is int and variable in (0, 1, 2), "Unknown substitution variable")
    result = {}
    for powers, coefficient in poly.items():
        rest = list(powers)
        exponent = rest[variable]
        rest[variable] = 0
        term = {tuple(rest): coefficient}
        for _ in range(exponent):
            term = multiply(term, replacement)
        result = add(result, term)
    return result


def encode_polynomial(poly):
    return [{"powers_T_Y_K": list(p), "coefficient": str(c)}
            for p, c in sorted(check_polynomial(poly).items())]


def decode_polynomial(records):
    bounded_bytes(records)
    need(type(records) is list and len(records) <= MAX_TERMS,
         "Sparse polynomial term budget", "RESOURCE_REFUSAL")
    prepared, previous = [], None
    for item in records:
        need(type(item) is dict and set(item) == {"powers_T_Y_K", "coefficient"},
             "Polynomial term fields changed")
        powers = item["powers_T_Y_K"]
        need(type(powers) is list and len(powers) == 3 and
             all(type(p) is int and 0 <= p <= MAX_DEGREE for p in powers) and
             sum(powers) <= MAX_DEGREE, "Polynomial degree budget", "RESOURCE_REFUSAL")
        key = tuple(powers)
        need(previous is None or previous < key, "Polynomial terms must be unique and ordered")
        previous = key
        numerator, denominator = rational_parts(item["coefficient"])
        need(numerator != 0, "Sparse zero coefficient")
        prepared.append((key, numerator, denominator))
    return check_polynomial({key: Fraction(n, d) for key, n, d in prepared})


def fixed_source():
    def spline(controls):
        return {"degree": 2,
                "knots": ["1/2", "1/2", "1/2", "3/2", "3/2", "3/2"],
                "controls": controls}
    return {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": PARAMETER,
            "parameter_lo": "1/2", "parameter_hi": "3/2",
            "phase_turn_offset": "0", "phase_turn_rate": "1",
            "cos_splines": {"0": spline(["5/8", "3/8", "5/8"]),
                            "1": spline(["-3/8", "-5/8", "-3/8"])},
            "sin_splines": {}}


def lower_source(spec):
    """Conditional exact quadratic lowering; public admission remains fixed."""
    bounded_bytes(spec)
    need(type(spec) is dict and set(spec) == set(fixed_source()), "Source fields changed")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec["source_parameter_id"] == PARAMETER, "Source grammar or parameter changed")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"0", "1"} and
         type(spec["sin_splines"]) is dict and not spec["sin_splines"],
         "Every original harmonic channel is required")
    tokens = [spec[name] for name in
              ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    controls = []
    for harmonic in ("0", "1"):
        spline = spec["cos_splines"][harmonic]
        need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
             "Spline fields changed")
        need(type(spline["degree"]) is int and spline["degree"] == 2,
             "Selected source requires exact quadratic degree")
        need(type(spline["knots"]) is list and len(spline["knots"]) == 6 and
             type(spline["controls"]) is list and len(spline["controls"]) == 3,
             "Selected clamped spline dimensions changed")
        tokens.extend(spline["knots"])
        tokens.extend(spline["controls"])
        controls.append(spline["controls"])
    # Validate EVERY raw token before constructing the first Fraction.
    for token in tokens:
        rational_parts(token)
    need([spec[x] for x in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
         == ["1/2", "3/2", "0", "1"], "Original source interval or global phase changed")
    for spline in spec["cos_splines"].values():
        need(spline["knots"] == ["1/2"] * 3 + ["3/2"] * 3,
             "Original fully clamped knots changed")
    t = monomial(1, t=1)
    u = add(t, monomial(Fraction(-1, 2)))  # unit span length; ORIGINAL T retained
    v = add(monomial(1), scale(u, -1))
    basis = (multiply(v, v), scale(multiply(u, v), 2), multiply(u, u))
    need(add(*basis) == monomial(1), "Bernstein partition identity failed")
    output = {}
    for name, values in zip(("C0", "C1"), controls):
        output[name] = add(*(scale(b, rational(c)) for b, c in zip(basis, values)))
    return output


def fixed_source_identity(spec):
    """No caller source is admitted by matching only a few polynomial values."""
    lower_source(spec)
    need(bounded_bytes(spec) == bounded_bytes(fixed_source()),
         "Selected original source identity changed")
    return digest(spec)


def selected_irreducibility_certificate(poly):
    """Check the exact premises of the reviewed ordered-field argument."""
    t, y, one = monomial(1, t=1), monomial(1, y=1), monomial(1)
    delta = add(t, monomial(-1))
    delta2 = multiply(delta, delta)
    expected = add(delta2, multiply(y, y))
    need(check_polynomial(poly) == expected, "Not the selected irreducible quadratic")
    translated = substitute(poly, 0, add(t, one))
    need(translated == add(monomial(1, t=2), monomial(1, y=2)),
         "Quadratic translation failed")
    discriminant = scale(delta2, -4)
    need(substitute(discriminant, 0, one) == {}, "Discriminant center changed")
    return {
        "polynomial": encode_polynomial(poly),
        "translated_polynomial": encode_polynomial(translated),
        "translation": "T=D+1; translated T slot denotes D",
        "degree_in_Y": 2, "leading_coefficient_in_Y": "1",
        "linear_coefficient_in_Y": "0",
        "constant_coefficient_in_Y": encode_polynomial(delta2),
        "discriminant_in_Y": encode_polynomial(discriminant),
        "coefficient_field": "Q(T)", "primitive_in_Q_T_Y": True,
        "nonsquare_argument": "A square equal to -(T-1)^2 would make -1 a square in the ordered field Q(T)",
        "algebraic_premises": ["Q(T) admits an ordering", "a square is nonnegative in an ordered field",
                               "quadratic factor criterion over a field of characteristic not two", "Gauss lemma"],
        "irreducible_over_Q_T_Y": True,
        "irreducible_over_complex_coefficients_claimed": False,
        "proof_kind": "EXACT_PREMISES_WITH_REVIEWED_ALGEBRAIC_ARGUMENT",
    }


def jet_at_one(poly):
    """Taylor coefficients through degree two, retaining formal K exactly."""
    check_polynomial(poly)
    need(all(p[1] == 0 for p in poly), "Jet requires no auxiliary Y")
    values = []
    current = poly
    for order in range(3):
        value = substitute(current, 0, monomial(1))
        values.append(scale(value, Fraction(1, 2) if order == 2 else 1))
        current = derivative(current, 0)
    return values


def jet_product(left, right):
    need(type(left) is list and type(right) is list and len(left) == len(right) == 3,
         "Three-term Taylor jets required")
    for entry in left + right:
        check_polynomial(entry)
        need(all(p[0] == p[1] == 0 for p in entry), "Jet coefficients must be polynomials in K")
    return [add(*(multiply(left[j], right[order-j]) for j in range(order+1)))
            for order in range(3)]


def source_certificate(spec):
    """Execute all finite source, algebraic, endpoint and jet obligations."""
    source_sha = fixed_source_identity(spec)
    amplitudes = lower_source(spec)
    one, t, y, k = monomial(1), monomial(1, t=1), monomial(1, y=1), monomial(1, k=1)
    delta = add(t, monomial(-1))
    delta2 = multiply(delta, delta)
    need(amplitudes["C0"] == scale(add(delta2, one), Fraction(1, 2)) and
         amplitudes["C1"] == scale(add(delta2, monomial(-1)), Fraction(1, 2)),
         "Original amplitude identity failed")
    y2 = multiply(y, y)
    denominator = add(one, y2)
    cleared = add(multiply(amplitudes["C0"], denominator),
                  multiply(amplitudes["C1"], add(one, scale(y2, -1))))
    g = add(delta2, y2)
    need(cleared == g, "Tangent denominator clearing lost an original amplitude")
    irreducibility = selected_irreducibility_certificate(g)
    p, q = delta, y
    need(substitute(p, 0, one) == {} and substitute(q, 0, one) == y,
         "Coprime linear-pair remainder failed")
    need(substitute(substitute(p, 0, one), 1, {}) == {} and
         substitute(substitute(q, 0, one), 1, {}) == {}, "Selected common point failed")
    # F = delta^2 + (1-delta^2)*sin(pi*T)^2, with sin^2=(1-cos(2*pi*T))/2.
    remainder = add(one, scale(delta2, -1))
    need(add(delta2, scale(remainder, Fraction(1, 2))) == amplitudes["C0"] and
         scale(remainder, Fraction(-1, 2)) == amplitudes["C1"], "Positivity decomposition failed")
    delta_lo, delta_hi = rational(spec["parameter_lo"]) - 1, rational(spec["parameter_hi"]) - 1
    need((delta_lo, delta_hi) == (Fraction(-1, 2), Fraction(1, 2)), "Original domain bound failed")
    max_square = max(delta_lo * delta_lo, delta_hi * delta_hi)
    margin = 1 - max_square
    need(max_square == Fraction(1, 4) and margin == Fraction(3, 4) > 0,
         "Positive squared-sine coefficient margin failed")
    # Original phase is in turns. At T=1 its radian harmonic is 2*pi.
    c0_jet, c1_jet = jet_at_one(amplitudes["C0"]), jet_at_one(amplitudes["C1"])
    cosine_jet = [one, {}, scale(multiply(k, k), -2)]
    product = jet_product(c1_jet, cosine_jet)
    source_jet = [add(c0_jet[j], product[j]) for j in range(3)]
    need(source_jet == [{}, {}, add(one, monomial(1, k=2))], "Original-phase source jet failed")
    second = scale(source_jet[2], 2)
    endpoints = []
    for coordinate in ("1/2", "3/2"):
        at_t = monomial(rational(coordinate))
        c0 = substitute(amplitudes["C0"], 0, at_t)
        c1 = substitute(amplitudes["C1"], 0, at_t)
        value = add(c0, scale(c1, -1))  # cos(2*pi*T)=-1 at both original exteriors
        need(value == one, "Original clamped exterior value failed")
        endpoints.append({"coordinate": coordinate, "original_turns": coordinate,
                          "cosine": "-1", "C0": encode_polynomial(c0),
                          "C1": encode_polynomial(c1), "value": "1", "sign": 1,
                          "auxiliary_tangent_chart_has_pole": True,
                          "original_source_value_established": True})
    # Formal X=K*T rescaling after multiplication by K^2. T slot now denotes X.
    radian_poly = add(multiply(add(t, scale(k, -1)), add(t, scale(k, -1))),
                      multiply(multiply(k, k), y2))
    returned = substitute(radian_poly, 0, multiply(k, t))
    need(returned == multiply(multiply(k, k), g), "Exact phase rescaling identity failed")
    need(radian_poly.get((2, 0, 0)) == 1 and radian_poly.get((1, 0, 1)) == -2,
         "Nonrational coefficient-ratio witness failed")
    return {
        "source_sha256": source_sha,
        "monomial_order": ["T", "Y", "K"], "formal_K_meaning": "pi",
        "amplitudes": {name: encode_polynomial(poly) for name, poly in amplitudes.items()},
        "original_tangent_chart": "Y=tan(pi*T), valid for 1/2<T<3/2",
        "tangent_denominator": encode_polynomial(denominator),
        "cleared_numerator": encode_polynomial(cleared),
        "irreducibility": irreducibility,
        "coprime_pair": {"p": encode_polynomial(p), "q": encode_polynomial(q),
                         "q_remainder_mod_p": encode_polynomial(y),
                         "rational_common_point": {"T": "1", "Y": "0"},
                         "analytic_binding": "tan(pi)=0", "coprime_over_Q_T_Y": True,
                         "argument": "T-1 is irreducible and does not divide Y; substituting T=1 leaves Y"},
        "positivity": {"delta": encode_polynomial(delta), "delta_squared": encode_polynomial(delta2),
                       "squared_sine_coefficient": encode_polynomial(remainder),
                       "identity": "F(T)=(T-1)^2+(1-(T-1)^2)*sin(pi*T)^2",
                       "delta_interval": [str(delta_lo), str(delta_hi)],
                       "delta_squared_upper_bound": str(max_square),
                       "squared_sine_coefficient_lower_bound": str(margin),
                       "source_lower_bound": "(T-1)^2", "strict_unless_T_equals": "1"},
        "jet": {"center": "1", "local_symbol": "D=T-1; original phase remains T",
                "C0_coefficients": [encode_polynomial(v) for v in c0_jet],
                "C1_coefficients": [encode_polynomial(v) for v in c1_jet],
                "cos_2piT_coefficients": [encode_polynomial(v) for v in cosine_jet],
                "source_coefficients": [encode_polynomial(v) for v in source_jet],
                "first_derivative": [], "second_derivative": encode_polynomial(second),
                "second_derivative_positive_reason": "2*(1+pi^2)>=2>0",
                "physical_root_multiplicity": 2},
        "endpoints": endpoints,
        "rescaling": {"new_coordinate": "X=K*T; polynomial T slot below denotes X",
                      "clearing_factor": "K^2", "polynomial": encode_polynomial(radian_poly),
                      "substituting_X_equals_KT": encode_polynomial(returned),
                      "coefficient_X_squared": "1", "coefficient_X": "-2*K",
                      "coefficient_ratio": "-2*pi", "coefficient_field": "Q(pi)",
                      "displayed_polynomial_in_Q_X_Y": False,
                      "scalar_rationalization_possible": False,
                      "scalar_argument": "Any scalar making the X^2 coefficient rational is rational; its nonzero X coefficient would then force pi rational",
                      "external_premise": "pi is irrational",
                      "other_reductions_excluded": False},
    }


def expected_report():
    try:
        references = capture_references()
        spec = fixed_source()
        certificate = source_certificate(spec)
        event = {"event_id": "ROOT_0", "coordinate": {"kind": "RATIONAL", "value": "1"},
                 "location": "SOURCE_SPAN_INTERIOR", "original_source_piece_index": 0,
                 "order": {"kind": "SMOOTH_MULTIPLICITY", "value": 2},
                 "left_sign": 1, "right_sign": 1}
        source_zero_set = {
            "kind": "FINITE_ORIGINAL_SOURCE_ZERO_SET", "closed_domain": ["1/2", "3/2"],
            "closed_root_count": 1, "physical_zeros": [event], "true_interior_source_knots": [],
            "source_exteriors": [{"coordinate": "1/2", "side": "LEFT", "value": "1", "sign": 1},
                                 {"coordinate": "3/2", "side": "RIGHT", "value": "1", "sign": 1}],
            "maximal_nonzero_components": [
                {"component_id": "CELL_0", "interval": ["1/2", "1"],
                 "left_included": True, "right_included": False, "sign": 1},
                {"component_id": "CELL_1", "interval": ["1", "3/2"],
                 "left_included": False, "right_included": True, "sign": 1}],
        }
        result = {
            "schema": SCHEMA, "status": "ESTABLISHED_SELECTED_DOMAIN_BOUNDARY",
            "basis_main": BASE_MAIN, "source": {"case_id": SOURCE_ID, "spec": spec,
                "source_sha256": certificate["source_sha256"],
                "scope": "NEW_RESEARCH_FIXTURE_OUTSIDE_FROZEN_FIFTY_SOURCE_COHORT",
                "historical_source_completion_claimed": False},
            "context_references": references, "symbolic_certificate": certificate,
            "source_zero_set": source_zero_set,
            "primary_theorem_scope": {
                "url": "https://arxiv.org/pdf/2301.05847", "checked_version": "arXiv:2301.05847v1",
                "published_doi": "10.1016/j.jsc.2023.102250",
                "published_title": "Isolating all the real roots of a mixed trigonometric-polynomial",
                "checked_statement_locations": ["Proposition 5.1, printed page 30 (PDF index 29)",
                                                "Proposition 5.2, printed page 31 (PDF index 30)"],
                "original_polynomial_domain": "Q[X,Y]", "original_analytic_substitution": "Y=tan(X)",
                "selected_polynomial_domain": "Q[T,Y]", "selected_analytic_substitution": "Y=tan(pi*T)",
                "original_theorems_disproved": False,
                "direct_rational_turn_simple_root_transfer_refuted": True,
                "direct_rational_turn_coprime_no_common_root_transfer_refuted": True,
                "published_full_algorithm_implemented": False,
                "paper_rational_coefficient_hypotheses_restored_by_rescaling": False},
            "broader_literature_boundary": {
                "url": "https://doi.org/10.4230/LIPIcs.MFCS.2026.65",
                "unbounded_problem_domain": "[0,infinity)",
                "bounded_question_location": "Open Problem 1, printed page 65:16",
                "bounded_question_scope": "ETPs over a computable discrete real subfield, rational bounded endpoints",
                "hardness_reduction_to_our_bounded_commensurate_grammar_supplied": False,
                "our_bounded_grammar_undecidable_claimed": False},
            "proof_premises": {
                "machine_checked": ["all original Bernstein controls and phase identity", "exact global polynomial lowering",
                    "tangent denominator clearing", "irreducibility discriminant/translation premises",
                    "coprime pair remainder and common point", "positive square coefficient margin",
                    "original-source second-order Taylor jet", "both original closed endpoint values",
                    "exact rescaling and nonrational coefficient ratio"],
                "reviewed_mathematical": ["Gauss lemma and the quadratic criterion over ordered Q(T)",
                    "squares are nonnegative", "standard sine/cosine/tangent identities and exact cardinal values",
                    "standard trigonometric differentiation", "continuity and connected components after removal of a point"],
                "external_theorems": ["pi is irrational"], "proof_assistant_formalization_claimed": False,
                "numeric_sampling_supplies_completeness": False},
            "scope": {"selected_new_fixture_count": 1, "frozen_corpus_additions": 0,
                      "generic_owner_route_repaired": False, "new_universal_analytic_solver": False,
                      "all_exact_methods_excluded": False, "general_impossibility_claimed": False,
                      "all_26_operations_remain_required": True, "native_evidence_claimed": False},
            "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN",
                      "PB-007-04": "OPEN", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                      "production_authorized": False},
            "resource_limits": {"json_bytes": MAX_BYTES, "nodes": MAX_NODES, "depth": MAX_DEPTH,
                "rational_operand_bits": MAX_RATIONAL_BITS, "arithmetic_result_bits": MAX_INTERMEDIATE_BITS,
                "polynomial_terms": MAX_TERMS, "polynomial_total_degree": MAX_DEGREE},
        }
        bounded_bytes(result)
        return result
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Certificate resource failure", "RESOURCE_REFUSAL") from error
    except Exception as error:
        raise Refusal("Certificate failure: " + type(error).__name__) from error


def selected_transfer_probe():
    """Refuse the specific theorem transfer, after actual boundary proof replay."""
    try:
        report = expected_report()
        return {"status": "UNSUPPORTED_DIRECT_MTP_THEOREM_TRANSFER",
                "direct_theorem_transfer_established": False, "boundary_certificate_established": True,
                "boundary_certificate_sha256": digest(report), "source_zero_set_established": True,
                "source_case_id": SOURCE_ID, "source_sha256": report["source"]["source_sha256"],
                "production_authorized": False}
    except Refusal as error:
        return error.as_record()


def read_report(path=REPORT):
    need(type(path) in (str, type(REPORT)), "Exact report path required", "RESOURCE_REFUSAL")
    text = str(path)
    need(0 < len(text) <= 4096 and "\0" not in text, "Report path budget or syntax", "RESOURCE_REFUSAL")
    try:
        return parse_json_bytes(_read_bounded(Path(text), MAX_BYTES))
    except OSError as error:
        raise Refusal("Unable to read bounded report") from error


def _compare_with_replayed_bytes(candidate, expected_bytes):
    need(type(expected_bytes) is bytes and len(expected_bytes) <= MAX_BYTES,
         "Exact bounded replay bytes required", "RESOURCE_REFUSAL")
    need(bounded_bytes(candidate) == expected_bytes, "Candidate differs from the fresh bounded certificate")
    return True


def validate_report(candidate):
    bounded_bytes(candidate)
    return _compare_with_replayed_bytes(candidate, bounded_bytes(expected_report()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = expected_report()
    if args.write_report:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("Wrote selected rational-turn MTP boundary certificate")
    else:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(report))
        print("Selected rational-turn MTP certificate matches fresh exact replay")


if __name__ == "__main__":
    main()

