#!/usr/bin/env python3
"""One coefficient-domain counterexample; no general Pfaffian algorithm.

The exact polynomial identities and rational bounds below are executable.
The analytic convexity and pi-transcendence arguments are reviewed mathematical
premises, explicitly distinguished in the report and accompanying memo.
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
REPORT = HERE / "pb00701-pfaffian-coefficient-boundary.json"
SCHEMA = "pb00701.pfaffian-coefficient-boundary.v1"
BASE_MAIN = "828df02d3d61b57bd46b0c4a796ce58685d9c987"
SOURCE_ID = "research:pb00701:pfaffian-coefficient-boundary:half-angle"
PARAMETER = "pb00701-pfaffian-coefficient-boundary-original-t"
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
    "docs/machining-completeness/70-PB00701-ALGEBRAIC-ENDPOINT.md":
        "3d8b6e0c23f1a5488f791e8bb04a4ee76ab8885a",
    "research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py":
        "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    "research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py":
        "77c18cb5c8c0700072c65969c973e8f3c4c12a99",
}


class Refusal(ValueError):
    def __init__(self, reason, code="UNESTABLISHED"):
        super().__init__(reason)
        self.reason, self.code = reason, code

    def as_record(self):
        return {"status": self.code, "reason": self.reason,
                "proof_established": False, "endpoint_value_established": False,
                "root_or_nonroot_result": None, "v46_oracle_invoked": False,
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
                        "use": "NONEXECUTED_SOURCE_AND_ORACLE_DOMAIN_REFERENCE"})
    return records


# Sparse monomials use (T exponent, Y exponent, K exponent). All arithmetic is
# rational. K remains a formal indeterminate here; its meaning pi/4 is bound
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


def y_degree(poly):
    check_polynomial(poly)
    return max((p[1] for p in poly), default=-1)


def y_coefficient(poly, degree):
    return check_polynomial({(p[0], 0, p[2]): c for p, c in check_polynomial(poly).items()
                             if p[1] == degree})


def divide_by_linear(dividend, divisor):
    """Exact finite division for the fixture's rational leading coefficient."""
    need(y_degree(divisor) == 1, "Only the selected linear divisor is admitted")
    leading = y_coefficient(divisor, 1)
    need(set(leading) == {(0, 0, 0)}, "Nonrational leading coefficient is outside this helper")
    leading_value = leading[(0, 0, 0)]
    rest, quotient = dict(check_polynomial(dividend)), {}
    for _ in range(MAX_DEGREE + 1):
        degree = y_degree(rest)
        if degree < 1:
            need(add(multiply(quotient, divisor), rest) == dividend, "Polynomial division identity failed")
            return quotient, rest
        term = {(p[0], degree - 1, p[2]): _coefficient(c / leading_value)
                for p, c in y_coefficient(rest, degree).items()}
        quotient = add(quotient, term)
        rest = add(rest, scale(multiply(term, divisor), -1))
    raise Refusal("Finite polynomial division budget exhausted", "RESOURCE_REFUSAL")


def determinant3(matrix):
    need(type(matrix) is list and len(matrix) == 3 and
         all(type(row) is list and len(row) == 3 for row in matrix), "Expected 3 by 3 Sylvester matrix")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return add(multiply(a, add(multiply(e, i), scale(multiply(f, h), -1))),
               scale(multiply(b, add(multiply(d, i), scale(multiply(f, g), -1))), -1),
               multiply(c, add(multiply(d, h), scale(multiply(e, g), -1))))


def resultant_linear_quadratic(first, second):
    need(y_degree(first) == 1 and y_degree(second) == 2,
         "Selected resultant needs degrees one and two")
    a1, a0 = y_coefficient(first, 1), y_coefficient(first, 0)
    b2, b1, b0 = (y_coefficient(second, j) for j in (2, 1, 0))
    matrix = [[a1, a0, {}], [{}, a1, a0], [b2, b1, b0]]
    return determinant3(matrix), matrix


def encode_polynomial(poly):
    return [{"powers_T_Y_K": list(p), "coefficient": str(c)}
            for p, c in sorted(check_polynomial(poly).items())]


def decode_polynomial(records):
    bounded_bytes(records)
    need(type(records) is list and len(records) <= MAX_TERMS,
         "Sparse polynomial term budget", "RESOURCE_REFUSAL")
    prepared = []
    previous = None
    for item in records:
        need(type(item) is dict and set(item) == {"powers_T_Y_K", "coefficient"},
             "Polynomial term fields changed")
        powers = item["powers_T_Y_K"]
        need(type(powers) is list and len(powers) == 3 and
             all(type(p) is int and 0 <= p <= MAX_DEGREE for p in powers) and
             sum(powers) <= MAX_DEGREE, "Polynomial degree budget", "RESOURCE_REFUSAL")
        powers = tuple(powers)
        need(previous is None or previous < powers, "Polynomial terms must be unique and ordered")
        previous = powers
        numerator, denominator = rational_parts(item["coefficient"])
        need(numerator != 0, "Sparse zero coefficient")
        prepared.append((powers, numerator, denominator))
    return check_polynomial({p: Fraction(n, d) for p, n, d in prepared})


def verify_division_witness(dividend, divisor, quotient, remainder):
    for poly in (dividend, divisor, quotient, remainder):
        check_polynomial(poly)
    need(y_degree(remainder) < y_degree(divisor), "Remainder degree was not reduced")
    need(add(multiply(quotient, divisor), remainder) == dividend,
         "Submitted polynomial division is false")
    return True


def fixed_source():
    def spline(controls):
        return {"degree": 1, "knots": ["0", "0", "1", "1"], "controls": controls}
    return {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": PARAMETER, "parameter_lo": "0", "parameter_hi": "1",
            "phase_turn_offset": "0", "phase_turn_rate": "1/4",
            "cos_splines": {"0": spline(["0", "1"]), "1": spline(["0", "1"])},
            "sin_splines": {"1": spline(["-1", "-1"])}}


def source_numerator(spec):
    """Conditional exact lowering for this one fully clamped affine grammar."""
    bounded_bytes(spec)
    need(type(spec) is dict and set(spec) == set(fixed_source()), "Source fields changed")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec["source_parameter_id"] == PARAMETER, "Source grammar or parameter changed")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"0", "1"} and
         type(spec["sin_splines"]) is dict and set(spec["sin_splines"]) == {"1"},
         "Every original harmonic channel is required")
    source_tokens = [spec[k] for k in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    control_parts = []
    for spline in (spec["cos_splines"]["0"], spec["cos_splines"]["1"], spec["sin_splines"]["1"]):
        need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"} and
             type(spline["degree"]) is int and spline["degree"] == 1 and
             type(spline["knots"]) is list and spline["knots"] == ["0", "0", "1", "1"] and
             type(spline["controls"]) is list and len(spline["controls"]) == 2,
             "Selected fully clamped affine spline structure changed")
        control_parts.append([rational_parts(x) for x in spline["controls"]])
    phase_parts = [rational_parts(x) for x in source_tokens]
    lo, hi, offset, rate = [Fraction(*p) for p in phase_parts]
    need((lo, hi, offset, rate) == (0, 1, 0, Fraction(1, 4)),
         "Original interval or global turn phase changed")
    channels = []
    for pair in control_parts:
        first, last = [Fraction(*p) for p in pair]
        channels.append(add(monomial(first), monomial(last - first, t=1)))
    one, y2 = monomial(1), monomial(1, y=2)
    denominator = add(one, y2)
    numerator = add(multiply(channels[0], denominator),
                    multiply(channels[1], add(one, scale(y2, -1))),
                    multiply(channels[2], monomial(2, y=1)))
    return numerator, denominator, channels


def chain_derivative(poly, phi):
    return add(derivative(poly, 0), multiply(derivative(poly, 1), phi))


def symbolic_certificate(spec):
    need(digest(spec) == digest(fixed_source()), "This certificate admits exactly its registered source")
    numerator, denominator, channels = source_numerator(spec)
    primitive = scale(numerator, Fraction(1, 2))
    need(primitive == add(monomial(1, t=1), monomial(-1, y=1)),
         "Half-angle numerator is not twice the registered primitive")
    phi = multiply(monomial(1, k=1), denominator)
    derived = chain_derivative(primitive, phi)
    threshold = 1 + y_degree(derived) - y_degree(primitive)
    even_power = threshold if threshold % 2 == 0 else threshold + 1
    leading = y_coefficient(primitive, 1)[(0, 0, 0)]
    scaled_derived = scale(derived, leading ** even_power)
    quotient, remainder = divide_by_linear(scaled_derived, primitive)
    verify_division_witness(scaled_derived, primitive, quotient, remainder)
    resultant, matrix = resultant_linear_quadratic(primitive, derived)
    need(resultant == remainder and y_degree(remainder) == 0,
         "Selected subresultant and division disagree")
    literal_derivative = chain_derivative(numerator, phi)
    literal_leading = y_coefficient(numerator, 1)[(0, 0, 0)]
    literal_quotient, literal_remainder = divide_by_linear(
        scale(literal_derivative, literal_leading ** even_power), numerator)
    literal_resultant, _ = resultant_linear_quadratic(numerator, literal_derivative)
    need(literal_remainder == literal_resultant == scale(remainder, 8),
         "Positive normalization scale was lost")
    # Quotient-rule identity for H=2P/(1+Y^2), before imposing r=0.
    derivative_numerator = scale(add(multiply(derived, denominator),
        scale(multiply(primitive, chain_derivative(denominator, phi)), -1)), 2)
    positive_square_part = multiply(monomial(1, k=1), multiply(primitive, primitive))
    reduced_derivative_numerator = scale(multiply(add(remainder, positive_square_part), denominator), 2)
    need(derivative_numerator == reduced_derivative_numerator, "Physical derivative identity failed")
    return {
        "monomial_order": ["T", "Y", "K"],
        "amplitude_polynomials": {name: encode_polynomial(poly)
                                  for name, poly in zip(("C0", "C1", "S1"), channels)},
        "half_angle_denominator": encode_polynomial(denominator),
        "literal_cleared_numerator": encode_polynomial(numerator),
        "positive_constant_normalization": "2",
        "primitive_polynomial": encode_polynomial(primitive),
        "formal_chain_polynomial": encode_polynomial(phi),
        "formal_chain_derivative_of_primitive": encode_polynomial(derived),
        "step1_smallest_even_leading_power": even_power,
        "step1_scaled_derivative": encode_polynomial(scaled_derived),
        "division_quotient": encode_polynomial(quotient),
        "division_remainder": encode_polynomial(remainder),
        "sylvester_matrix": [[encode_polynomial(cell) for cell in row] for row in matrix],
        "sylvester_determinant": encode_polynomial(resultant),
        "degree_one_recipe": {
            "N": 1, "R0": encode_polynomial(primitive), "R1": encode_polynomial(remainder),
            "tau0": encode_polynomial(y_coefficient(primitive, 1)),
            "tau1": encode_polynomial(remainder), "rho2": encode_polynomial(remainder),
            "step3_partition_polynomial": encode_polynomial(remainder)},
        "literal_2P_quotient": encode_polynomial(literal_quotient),
        "literal_2P_remainder": encode_polynomial(literal_remainder),
        "literal_2P_resultant": encode_polynomial(literal_resultant),
        "literal_to_primitive_remainder_factor": "8",
        "physical_derivative_numerator_over_denominator_squared": encode_polynomial(derivative_numerator),
        "equivalent_derivative_numerator": encode_polynomial(reduced_derivative_numerator),
        "physical_derivative_identity": "H'=2*(r(T)+K*(T-Y)^2)/(1+Y^2)",
    }


def atan_reciprocal_bounds(denominator):
    need(type(denominator) is int and 2 <= denominator <= 512,
         "Finite reciprocal arctangent budget", "RESOURCE_REFUSAL")
    x = Fraction(1, denominator)
    lower = x - x ** 3 / 3
    upper = lower + x ** 5 / 5
    need(0 < lower < upper < x, "Alternating arctangent enclosure failed")
    return lower, upper


def gaussian_multiply(left, right):
    need(type(left) is tuple and type(right) is tuple and len(left) == len(right) == 2,
         "Exact Gaussian integer pairs required")
    need(all(type(n) is int and n.bit_length() <= 32 for n in (*left, *right)),
         "Gaussian integer budget", "RESOURCE_REFUSAL")
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def machin_certificate():
    z = (1, 0)
    for _ in range(4):
        z = gaussian_multiply(z, (5, 1))
    z = gaussian_multiply(z, (239, -1))
    need(z == (114244, 114244), "Machin Gaussian integer identity failed")
    a_lower, a_upper = atan_reciprocal_bounds(5)
    b_lower, b_upper = atan_reciprocal_bounds(239)
    angle_lower, angle_upper = 4 * a_lower - b_upper, 4 * a_upper - b_lower
    need(0 < angle_lower < angle_upper < Fraction(4, 5) < 1,
         "Machin angle branch enclosure failed")
    pi_lower, pi_upper = 16 * a_lower - 4 * b_upper, 16 * a_upper - 4 * b_lower
    need(3 < pi_lower < pi_upper < Fraction(22, 7), "Required exact pi bounds failed")
    k_lower, k_upper = pi_lower / 4, pi_upper / 4
    left_lower = 1 - k_upper * Fraction(5, 4)
    right_upper = 1 - k_lower * Fraction(34, 25)
    square_lower, square_upper = 4 / pi_upper - 1, 4 / pi_lower - 1
    need(left_lower > 0 and right_upper < 0 and
         Fraction(1, 4) < square_lower < square_upper < Fraction(9, 25),
         "Positive partition cut is not strictly enclosed")
    left_derivative = (2 * (1 - k_upper), 2 * (1 - k_lower))
    right_derivative = (1 - 2 * k_upper, 1 - 2 * k_lower)
    need(left_derivative[0] > 0 and right_derivative[1] < 0,
         "Source exterior first derivatives are not strict")
    return {
        "gaussian_integer_identity": {"left": "(5+i)^4*(239-i)", "right": list(z)},
        "arctangent_reciprocal_bounds": {
            "5": [str(a_lower), str(a_upper)], "239": [str(b_lower), str(b_upper)]},
        "alternating_bounds_are_strict": True,
        "selected_angle_strict_interval": [str(angle_lower), str(angle_upper)],
        "branch_argument": "0<4*atan(1/5)-atan(1/239)<4/5<1<pi/2; tangent=1",
        "elementary_pi_lower_bound_premise": "pi=4*atan(1)>2 by the positive integral",
        "pi_strict_interval": [str(pi_lower), str(pi_upper)],
        "coarse_pi_strict_interval": ["3", "22/7"],
        "k_strict_interval": [str(k_lower), str(k_upper)],
        "r_at_one_half_strict_lower_bound": str(left_lower),
        "r_at_three_fifths_strict_upper_bound": str(right_upper),
        "alpha_squared_strict_interval": [str(square_lower), str(square_upper)],
        "alpha_strict_interval": ["1/2", "3/5"],
        "source_left_first_derivative_strict_interval": list(map(str, left_derivative)),
        "source_right_first_derivative_strict_interval": list(map(str, right_derivative)),
        "floating_point_used": False,
    }


def expected_report():
    try:
        references = capture_references()
        source = fixed_source()
        symbolic, bounds = symbolic_certificate(source), machin_certificate()
        result = {
            "schema": SCHEMA,
            "status": "BOUNDED_PFAFFIAN_COEFFICIENT_DOMAIN_COUNTEREXAMPLE",
            "evidence_class": "DETERMINISTIC_MODEL",
            "qualified_context_main": BASE_MAIN,
            "source": {"case_id": SOURCE_ID, "spec": source, "source_sha256": digest(source),
                       "scope": "NEW_RESEARCH_FIXTURE_OUTSIDE_FROZEN_FIFTY_SOURCE_COHORT",
                       "historical_source_completion_claimed": False},
            "constant_binding": {"formal_symbol": "K", "exact_meaning": "pi/4",
                                 "derived_from_original_turn_rate": "1/4",
                                 "rational_approximation_substitution_allowed": False},
            "context_reference_bytes": references,
            "project_modules_imported_or_executed": [],
            "symbolic_certificate": symbolic,
            "rational_enclosures": bounds,
            "selected_partition_cut": {
                "definition": "positive sqrt(4/pi-1)", "strict_interval": ["1/2", "3/5"],
                "defining_equation": "1-(pi/4)*(1+alpha^2)=0",
                "unique_positive_root": True,
                "algebraic_over_Q_pi": True, "algebraic_over_Q": False,
                "nonalgebraicity_basis": "If alpha were Q-algebraic, pi=4/(1+alpha^2) would be Q-algebraic",
                "external_theorem": "PI_IS_TRANSCENDENTAL_OVER_Q",
                "nonalgebraicity_inferred_from_numeric_enclosure": False,
                "physical_source_zero": False, "physical_source_critical_point": False,
                "event_or_sign_cell_boundary": False},
            "algorithm_applicability": {
                "reference": "Barbagallo-Jeronimo-Sabia 2016, Algorithm ZeroCounting Steps 1-3",
                "operation_performed": "FINITE_ALGEBRAIC_RECIPE_UNDER_FORMAL_Q_K_COEFFICIENT_EXTENSION",
                "cited_integer_coefficient_theorem_instantiated": False,
                "primitive_P_in_Z_T_Y": True, "chain_Phi_in_Z_T_Y": False,
                "actual_chain_coefficient_domain": "Q(pi)",
                "extension_with_sign_oracle_qualified": False,
                "general_Pfaffian_algorithm_implemented": False},
            "v46_domain_decision": {
                "status": "UNSUPPORTED_COORDINATE_DOMAIN", "proof_established": False,
                "endpoint_value_established": False, "root_or_nonroot_result": None,
                "required_coordinate_domain": "REAL_ALGEBRAIC_OVER_Q",
                "actual_coordinate_domain": "TRANSCENDENTAL_OVER_Q_ALGEBRAIC_OVER_Q_PI",
                "original_source_grammar_preserved": True,
                "v46_oracle_invoked": False,
                "reason": "The selected partition cut is outside the qualified coordinate domain"},
            "independent_source_sanity_proof": {
                "argument_kind": "REVIEWED_ANALYTIC_ARGUMENT_WITH_EXACT_ALGEBRAIC_CERTIFICATE",
                "half_angle_chart": "Y(t)=tan(pi*t/4)",
                "chart_pole_free_on_closed_source": True,
                "strict_convexity_premise": "tan''(x)=2*tan(x)*sec(x)^2>0 for 0<x<pi/4",
                "endpoint_chord": {"Y_at_0": "0", "Y_at_1": "1"},
                "interior_inequality": "Y(t)<t for 0<t<1",
                "source_interior_sign": 1,
                "closed_source_zero_set": [
                    {"coordinate": "0", "location": "SOURCE_LEFT_ENDPOINT",
                     "order": {"kind": "ONE_SIDED", "side": "RIGHT", "value": 1},
                     "left_sign": None, "right_sign": 1, "first_derivative": "2*(1-K)"},
                    {"coordinate": "1", "location": "SOURCE_RIGHT_ENDPOINT",
                     "order": {"kind": "ONE_SIDED", "side": "LEFT", "value": 1},
                     "left_sign": 1, "right_sign": None, "first_derivative": "1-2*K"}],
                "isolated_root_count": 2, "strict_source_interior_root_count": 0,
                "maximal_nonzero_components": [{"open_interval": ["0", "1"], "sign": 1}],
                "at_partition_cut": {"source_sign": 1, "first_derivative_sign": 1,
                                     "positive_derivative_identity": "2*K*(alpha-Y(alpha))^2/(1+Y(alpha)^2)"},
                "physical_proof_obtained_by_v46_oracle": False},
            "rescaling_check": {
                "new_coordinate": "U=K*T", "new_chain": "dY/dU=1+Y^2",
                "positive_normalization": "multiply P(U/K,Y) by K>0",
                "new_primitive_polynomial": "U-K*Y", "new_interval": ["0", "K"],
                "new_chain_has_integer_coefficients": True,
                "new_source_polynomial_has_integer_coefficients": False,
                "new_right_endpoint_algebraic_over_Q": False,
                "cited_algorithm_assumptions_restored": False},
            "proof_premises": {
                "machine_checked": ["all original affine channels in the cleared numerator",
                    "formal chain derivative and exact polynomial division", "Sylvester determinant",
                    "primitive r versus literal 8*r normalization", "degree-one leading-coefficient cut",
                    "Machin integer identity and strict rational enclosures", "physical derivative identity"],
                "reviewed_analytic": ["standard half-angle trigonometric identities",
                    "Machin branch selection and alternating arctangent remainder",
                    "strict tangent convexity and its endpoint chord", "continuity and derivative sign implications"],
                "external_theorems": ["pi is transcendental over Q"],
                "proof_assistant_formalization_claimed": False},
            "scope": {
                "registered_new_fixture_count": 1, "frozen_corpus_additions": 0,
                "generic_owner_route_repaired": False, "old_endpoint_domain_widened": False,
                "general_method_impossible": False, "undecidability_claimed": False,
                "conjecture_necessity_claimed": False, "alternate_exact_methods_excluded": False,
                "all_26_operations_remain_required": True, "native_evidence_claimed": False},
            "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN",
                      "PB-007-04": "OPEN", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                      "production_authorized": False},
            "resource_limits": {"json_bytes": MAX_BYTES, "nodes": MAX_NODES, "depth": MAX_DEPTH,
                                "rational_operand_bits": MAX_RATIONAL_BITS,
                                "arithmetic_operand_bits": MAX_INTERMEDIATE_BITS,
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


def selected_cut_domain_probe():
    """A typed refusal by the existing oracle domain, never an oracle call."""
    try:
        report = expected_report()
        result = dict(report["v46_domain_decision"])
        result.update(source_case_id=SOURCE_ID, source_sha256=report["source"]["source_sha256"],
                      boundary_certificate_sha256=digest(report), production_authorized=False)
        return result
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
    need(bounded_bytes(candidate) == expected_bytes,
         "Candidate differs from the fresh bounded certificate")
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
        print("Wrote bounded coefficient-domain research certificate")
    else:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(report))
        print("Bounded coefficient-domain certificate matches fresh exact replay")


if __name__ == "__main__":
    main()
