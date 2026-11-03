#!/usr/bin/env python3
"""Independent finite checks and adversaries for one domain-boundary fixture."""
from __future__ import annotations

import argparse
import ast
import copy
from fractions import Fraction as Q
import hashlib
import importlib.machinery
import importlib.util
from itertools import permutations, product
import json
import marshal
from pathlib import Path
import re
import struct
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MODEL = HERE / "pb00701_pfaffian_coefficient_boundary.py"
MODEL_BLOB = "2fe093dca21de8e6dc60e275825955ec0161f6ec"
MAX_CODE_BYTES = 128 * 1024
WORKFLOW = ".github/workflows/mc1-pb00701-pfaffian-coefficient-boundary.yml"
OWN_PATHS = {
    "research/machining-completeness/tasks/MC-038/pb00701_pfaffian_coefficient_boundary.py",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_pfaffian_coefficient_boundary.py",
    "research/machining-completeness/tasks/MC-038/pb00701-pfaffian-coefficient-boundary.json",
    "research/machining-completeness/tasks/MC-038/pb00701-pfaffian-coefficient-boundary-research.md",
    WORKFLOW,
}
_CONTEXT = None


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_code(path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_CODE_BYTES + 1)
    if len(raw) > MAX_CODE_BYTES:
        raise ValueError("Model byte budget")
    return raw


def checked_module(path=MODEL, expected_blob=MODEL_BLOB):
    if type(path) is not type(MODEL) or path.is_symlink() or path.resolve() != path:
        raise ValueError("Original model path required")
    raw = read_code(path)
    if blob(raw) != expected_blob:
        raise ValueError("Model blob changed")
    module = types.ModuleType("_pb00701_boundary_checked")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def exact_q(text):
    assert type(text) is str and 0 < len(text) <= 160
    assert re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", text, re.ASCII)
    value = Q(text)
    assert str(value) == text
    assert max(value.numerator.bit_length(), value.denominator.bit_length()) <= 256
    return value


def terms(records):
    """Independent decoding; no candidate polynomial routines are called."""
    assert type(records) is list and len(records) <= 64
    out, last = [], None
    for term in records:
        assert type(term) is dict and set(term) == {"powers_T_Y_K", "coefficient"}
        powers = term["powers_T_Y_K"]
        assert type(powers) is list and len(powers) == 3
        assert all(type(x) is int and 0 <= x <= 6 for x in powers) and sum(powers) <= 6
        key = tuple(powers)
        assert last is None or last < key
        last = key
        value = exact_q(term["coefficient"])
        assert value
        out.append((key, value))
    return out


def at(poly, t, y, k):
    return sum((value * t ** powers[0] * y ** powers[1] * k ** powers[2]
                for powers, value in poly), Q(0))


def determinant(matrix):
    """Leibniz permutation expansion, distinct from the model's cofactors."""
    total = Q(0)
    for order in permutations(range(3)):
        inversions = sum(order[i] > order[j] for i in range(3) for j in range(i + 1, 3))
        value = Q((-1) ** inversions)
        for row, column in enumerate(order):
            value *= matrix[row][column]
        total += value
    return total


def audit_symbolic(report):
    cert = report["symbolic_certificate"]
    fields = ("half_angle_denominator", "literal_cleared_numerator", "primitive_polynomial",
              "formal_chain_polynomial", "formal_chain_derivative_of_primitive", "step1_scaled_derivative",
              "division_quotient", "division_remainder", "sylvester_determinant",
              "literal_2P_quotient", "literal_2P_remainder", "literal_2P_resultant",
              "physical_derivative_numerator_over_denominator_squared", "equivalent_derivative_numerator")
    decoded = {name: terms(cert[name]) for name in fields}
    amplitudes = {name: terms(poly) for name, poly in cert["amplitude_polynomials"].items()}
    assert set(amplitudes) == {"C0", "C1", "S1"}
    recipe = cert["degree_one_recipe"]
    assert recipe["N"] == 1 and type(recipe["N"]) is int
    recipe_polys = {name: terms(recipe[name]) for name in ("R0", "R1", "tau0", "tau1", "rho2", "step3_partition_polynomial")}
    matrix = [[terms(cell) for cell in row] for row in cert["sylvester_matrix"]]
    assert len(matrix) == 3 and all(len(row) == 3 for row in matrix)
    assert cert["monomial_order"] == ["T", "Y", "K"]
    assert cert["step1_smallest_even_leading_power"] == 2
    assert type(cert["step1_smallest_even_leading_power"]) is int
    assert cert["positive_constant_normalization"] == "2"
    assert cert["literal_to_primitive_remainder_factor"] == "8"
    # Each admitted polynomial has total degree <=6. Equality on this complete
    # seven-point Cartesian grid establishes polynomial equality by induction
    # on variables; these are exact rational evaluations, not analytic samples.
    for ti, yi, ki in product(range(7), repeat=3):
        t, y, k = Q(ti), Q(yi), Q(ki)
        p, den, phi = t - y, 1 + y * y, k * (1 + y * y)
        dp, quotient, remainder = 1 - phi, k * (y + t), 1 - k * (1 + t * t)
        expected = {
            "half_angle_denominator": den, "literal_cleared_numerator": 2 * p,
            "primitive_polynomial": p, "formal_chain_polynomial": phi,
            "formal_chain_derivative_of_primitive": dp, "step1_scaled_derivative": dp,
            "division_quotient": quotient, "division_remainder": remainder,
            "sylvester_determinant": remainder, "literal_2P_quotient": 4 * quotient,
            "literal_2P_remainder": 8 * remainder, "literal_2P_resultant": 8 * remainder,
            "physical_derivative_numerator_over_denominator_squared": 2 * (dp * den - p * 2 * y * phi),
            "equivalent_derivative_numerator": 2 * (remainder + k * p * p) * den,
        }
        for name, value in expected.items():
            assert at(decoded[name], t, y, k) == value, name
        assert at(amplitudes["C0"], t, y, k) == t
        assert at(amplitudes["C1"], t, y, k) == t
        assert at(amplitudes["S1"], t, y, k) == -1
        assert t * den + t * (1 - y * y) - 2 * y == 2 * p
        evaluated_matrix = [[at(cell, t, y, k) for cell in row] for row in matrix]
        assert evaluated_matrix == [[-1, t, 0], [0, -1, t], [-k, 0, 1 - k]]
        assert determinant(evaluated_matrix) == remainder
        assert determinant([[-2, 2 * t, 0], [0, -2, 2 * t], [-2 * k, 0, 2 * (1 - k)]]) == 8 * remainder
        for name, value in {"R0": p, "R1": remainder, "tau0": -1, "tau1": remainder,
                            "rho2": remainder, "step3_partition_polynomial": remainder}.items():
            assert at(recipe_polys[name], t, y, k) == value, name
    return True


def audit_bounds(report):
    b = report["rational_enclosures"]
    def partial(d, n):
        return sum((Q((-1) ** j, (2 * j + 1) * d ** (2 * j + 1)) for j in range(n)), Q(0))
    a0, a1, z0, z1 = partial(5, 2), partial(5, 3), partial(239, 2), partial(239, 3)
    assert b["arctangent_reciprocal_bounds"] == {"5": [str(a0), str(a1)], "239": [str(z0), str(z1)]}
    assert b["gaussian_integer_identity"]["right"] == [476 * 239 + 480, 480 * 239 - 476]
    assert b["gaussian_integer_identity"]["left"] == "(5+i)^4*(239-i)"
    alo, ahi = 4 * a0 - z1, 4 * a1 - z0
    assert 0 < alo < ahi < Q(4, 5) < 1
    assert list(map(exact_q, b["selected_angle_strict_interval"])) == [alo, ahi]
    assert b["branch_argument"] == "0<4*atan(1/5)-atan(1/239)<4/5<1<pi/2; tangent=1"
    assert b["elementary_pi_lower_bound_premise"] == "pi=4*atan(1)>2 by the positive integral"
    lower, upper = 16 * a0 - 4 * z1, 16 * a1 - 4 * z0
    assert 3 < lower < upper < Q(22, 7)
    assert list(map(exact_q, b["pi_strict_interval"])) == [lower, upper]
    kl, ku = lower / 4, upper / 4
    assert list(map(exact_q, b["k_strict_interval"])) == [kl, ku]
    assert exact_q(b["r_at_one_half_strict_lower_bound"]) == 1 - ku * Q(5, 4) > Q(1, 56)
    assert exact_q(b["r_at_three_fifths_strict_upper_bound"]) == 1 - kl * Q(34, 25) < Q(-1, 50)
    sl, su = 4 / upper - 1, 4 / lower - 1
    assert Q(1, 4) < sl < su < Q(9, 25)
    assert list(map(exact_q, b["alpha_squared_strict_interval"])) == [sl, su]
    assert b["alpha_strict_interval"] == ["1/2", "3/5"]
    assert list(map(exact_q, b["source_left_first_derivative_strict_interval"])) == [2 * (1 - ku), 2 * (1 - kl)]
    assert list(map(exact_q, b["source_right_first_derivative_strict_interval"])) == [1 - 2 * ku, 1 - 2 * kl]
    assert 2 * (1 - ku) > 0 and 1 - 2 * kl < 0
    assert b["floating_point_used"] is False
    return True


def audit_scope(report):
    source = report["source"]
    assert source["scope"] == "NEW_RESEARCH_FIXTURE_OUTSIDE_FROZEN_FIFTY_SOURCE_COHORT"
    assert source["historical_source_completion_claimed"] is False
    spec = source["spec"]
    assert spec["source_parameter_id"] == "pb00701-pfaffian-coefficient-boundary-original-t"
    assert [spec[x] for x in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")] == ["0", "1", "0", "1/4"]
    for channel, h, controls in (("cos_splines", "0", ["0", "1"]),
                                  ("cos_splines", "1", ["0", "1"]),
                                  ("sin_splines", "1", ["-1", "-1"])):
        assert spec[channel][h] == {"degree": 1, "knots": ["0", "0", "1", "1"], "controls": controls}
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    assert hashlib.sha256(canonical).hexdigest() == source["source_sha256"]
    constant = report["constant_binding"]
    assert constant == {"formal_symbol": "K", "exact_meaning": "pi/4",
                        "derived_from_original_turn_rate": "1/4", "rational_approximation_substitution_allowed": False}
    cut = report["selected_partition_cut"]
    assert cut["definition"] == "positive sqrt(4/pi-1)" and cut["strict_interval"] == ["1/2", "3/5"]
    assert cut["algebraic_over_Q_pi"] is True and cut["algebraic_over_Q"] is False
    assert cut["external_theorem"] == "PI_IS_TRANSCENDENTAL_OVER_Q"
    for key in ("nonalgebraicity_inferred_from_numeric_enclosure", "physical_source_zero",
                "physical_source_critical_point", "event_or_sign_cell_boundary"):
        assert cut[key] is False
    app = report["algorithm_applicability"]
    assert app["primitive_P_in_Z_T_Y"] is True and app["chain_Phi_in_Z_T_Y"] is False
    assert app["cited_integer_coefficient_theorem_instantiated"] is False
    assert app["extension_with_sign_oracle_qualified"] is False
    assert app["general_Pfaffian_algorithm_implemented"] is False
    refusal = report["v46_domain_decision"]
    assert refusal["status"] == "UNSUPPORTED_COORDINATE_DOMAIN"
    assert refusal["proof_established"] is False and refusal["endpoint_value_established"] is False
    assert refusal["root_or_nonroot_result"] is None and refusal["v46_oracle_invoked"] is False
    physical = report["independent_source_sanity_proof"]
    assert physical["source_interior_sign"] == 1 and type(physical["source_interior_sign"]) is int
    assert physical["isolated_root_count"] == 2 and physical["strict_source_interior_root_count"] == 0
    assert physical["maximal_nonzero_components"] == [{"open_interval": ["0", "1"], "sign": 1}]
    events = physical["closed_source_zero_set"]
    assert len(events) == 2 and [e["coordinate"] for e in events] == ["0", "1"]
    assert [e["first_derivative"] for e in events] == ["2*(1-K)", "1-2*K"]
    assert events[0]["order"] == {"kind": "ONE_SIDED", "side": "RIGHT", "value": 1}
    assert events[1]["order"] == {"kind": "ONE_SIDED", "side": "LEFT", "value": 1}
    assert events[0]["left_sign"] is None and events[1]["right_sign"] is None
    assert physical["at_partition_cut"]["source_sign"] == physical["at_partition_cut"]["first_derivative_sign"] == 1
    rescale = report["rescaling_check"]
    assert rescale["new_primitive_polynomial"] == "U-K*Y" and rescale["new_interval"] == ["0", "K"]
    assert rescale["new_chain_has_integer_coefficients"] is True
    for field in ("new_source_polynomial_has_integer_coefficients", "new_right_endpoint_algebraic_over_Q", "cited_algorithm_assumptions_restored"):
        assert rescale[field] is False
    assert report["project_modules_imported_or_executed"] == []
    assert report["scope"]["frozen_corpus_additions"] == 0
    assert report["scope"]["all_26_operations_remain_required"] is True
    for key in ("PB-007-01", "PB-007-02", "PB-007-03", "PB-007-04"):
        assert report["gates"][key] == "OPEN"
    assert report["gates"]["MC-B"] == report["gates"]["MC-1"] == "NOT_ESTABLISHED"
    assert report["gates"]["production_authorized"] is False
    return True


def context():
    global _CONTEXT
    if _CONTEXT is None:
        model = checked_module()
        fresh = model.expected_report()
        expected = model.bounded_bytes(fresh)
        saved = model.read_report()
        model._compare_with_replayed_bytes(saved, expected)
        audit_symbolic(saved)
        audit_bounds(saved)
        audit_scope(saved)
        _CONTEXT = model, fresh, expected
    return _CONTEXT


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.report, cls.expected = context()

    def changed(self):
        return copy.deepcopy(self.report)

    def test_independent_complete_contract(self):
        self.assertEqual(self.m.bounded_bytes(self.report), self.expected)
        self.assertTrue(self.m.validate_report(self.report))

    def test_each_original_channel_is_bound(self):
        for channel, harmonic in (("cos_splines", "0"), ("cos_splines", "1"), ("sin_splines", "1")):
            spec = self.m.fixed_source()
            spec[channel][harmonic]["controls"][0] = "1"
            with self.assertRaises(self.m.Refusal):
                self.m.symbolic_certificate(spec)
        missing = self.m.fixed_source()
        del missing["cos_splines"]["0"]
        with self.assertRaises(self.m.Refusal):
            self.m.source_numerator(missing)

    def test_source_lowering_detects_an_omitted_harmonic_zero(self):
        spec = self.m.fixed_source()
        original, _, _ = self.m.source_numerator(spec)
        spec["cos_splines"]["0"]["controls"] = ["0", "0"]
        altered, _, _ = self.m.source_numerator(spec)
        self.assertNotEqual(original, altered)
        difference = self.m.add(original, self.m.scale(altered, -1))
        self.assertEqual(difference, self.m.add(self.m.monomial(1, t=1), self.m.monomial(1, t=1, y=2)))

    def test_original_global_phase_and_source_parameter(self):
        for field, value in (("phase_turn_rate", "1/8"), ("phase_turn_offset", "1/4"),
                             ("parameter_hi", "2"), ("source_parameter_id", "tail-local-t")):
            spec = self.m.fixed_source()
            spec[field] = value
            with self.assertRaises(self.m.Refusal):
                self.m.source_numerator(spec)

    def test_false_division_and_sign_flipped_remainder(self):
        c = self.report["symbolic_certificate"]
        dividend, divisor, quotient, remainder = [self.m.decode_polynomial(c[key]) for key in
            ("step1_scaled_derivative", "primitive_polynomial", "division_quotient", "division_remainder")]
        self.assertTrue(self.m.verify_division_witness(dividend, divisor, quotient, remainder))
        for bad in ({}, self.m.scale(remainder, -1), self.m.add(remainder, self.m.monomial(1, t=2, k=1))):
            with self.assertRaises(self.m.Refusal):
                self.m.verify_division_witness(dividend, divisor, quotient, bad)

    def test_actual_chain_derivative_changes_with_wrong_phi(self):
        c = self.report["symbolic_certificate"]
        p, phi, dp = [self.m.decode_polynomial(c[key]) for key in
            ("primitive_polynomial", "formal_chain_polynomial", "formal_chain_derivative_of_primitive")]
        wrong = self.m.chain_derivative(p, self.m.scale(phi, -1))
        self.assertNotEqual(dp, wrong)
        actual_r, _ = self.m.resultant_linear_quadratic(p, dp)
        wrong_r, _ = self.m.resultant_linear_quadratic(p, wrong)
        self.assertNotEqual(actual_r, wrong_r)

    def test_literal_factor_and_leading_exponent_are_material(self):
        c = self.report["symbolic_certificate"]
        literal = self.m.decode_polynomial(c["literal_cleared_numerator"])
        phi = self.m.decode_polynomial(c["formal_chain_polynomial"])
        dp = self.m.chain_derivative(literal, phi)
        _, without_power = self.m.divide_by_linear(dp, literal)
        _, with_power = self.m.divide_by_linear(self.m.scale(dp, 4), literal)
        self.assertNotEqual(without_power, with_power)
        self.assertEqual(self.m.scale(without_power, 4), with_power)
        bad = self.changed()
        bad["symbolic_certificate"]["literal_2P_remainder"] = copy.deepcopy(c["division_remainder"])
        with self.assertRaises(AssertionError):
            audit_symbolic(bad)

    def test_constant_in_y_partition_coefficient_cannot_be_dropped(self):
        bad = self.changed()
        bad["symbolic_certificate"]["degree_one_recipe"]["tau1"] = []
        with self.assertRaises(AssertionError):
            audit_symbolic(bad)
        bad = self.changed()
        bad["symbolic_certificate"]["degree_one_recipe"]["step3_partition_polynomial"] = []
        with self.assertRaises(AssertionError):
            audit_symbolic(bad)

    def test_sylvester_entry_and_physical_derivative_falsifiers(self):
        bad = self.changed()
        bad["symbolic_certificate"]["sylvester_matrix"][2][0][0]["coefficient"] = "1"
        with self.assertRaises(AssertionError):
            audit_symbolic(bad)
        bad = self.changed()
        bad["symbolic_certificate"]["equivalent_derivative_numerator"][0]["coefficient"] = "99"
        with self.assertRaises(AssertionError):
            audit_symbolic(bad)

    def test_pi_subtraction_direction_and_branch_are_required(self):
        bad = self.changed()
        bounds = bad["rational_enclosures"]
        low5 = exact_q(bounds["arctangent_reciprocal_bounds"]["5"][0])
        low239 = exact_q(bounds["arctangent_reciprocal_bounds"]["239"][0])
        bounds["pi_strict_interval"][0] = str(16 * low5 - 4 * low239)
        with self.assertRaises(AssertionError):
            audit_bounds(bad)
        bad = self.changed()
        del bad["rational_enclosures"]["branch_argument"]
        with self.assertRaises(KeyError):
            audit_bounds(bad)

    def test_cut_is_not_a_physical_event_or_critical_point(self):
        for field in ("physical_source_zero", "physical_source_critical_point", "event_or_sign_cell_boundary"):
            bad = self.changed()
            bad["selected_partition_cut"][field] = True
            with self.assertRaises(AssertionError):
                audit_scope(bad)
        bad = self.changed()
        bad["independent_source_sanity_proof"]["maximal_nonzero_components"].append(
            {"open_interval": ["alpha", "1"], "sign": 1})
        with self.assertRaises(AssertionError):
            audit_scope(bad)

    def test_exterior_orders_and_derivatives_belong_to_this_source(self):
        bad = self.changed()
        bad["independent_source_sanity_proof"]["closed_source_zero_set"][0]["first_derivative"] = "1-K"
        with self.assertRaises(AssertionError):
            audit_scope(bad)
        bad = self.changed()
        bad["independent_source_sanity_proof"]["closed_source_zero_set"].pop()
        with self.assertRaises(AssertionError):
            audit_scope(bad)

    def test_no_oracle_admission_from_coordinate_label_or_approximation(self):
        for section, field, value in (("selected_partition_cut", "algebraic_over_Q", True),
            ("constant_binding", "exact_meaning", "355/452"),
            ("algorithm_applicability", "cited_integer_coefficient_theorem_instantiated", True),
            ("v46_domain_decision", "proof_established", True)):
            bad = self.changed()
            bad[section][field] = value
            with self.assertRaises(AssertionError):
                audit_scope(bad)
        result = self.m.selected_cut_domain_probe()
        self.assertEqual(result["status"], "UNSUPPORTED_COORDINATE_DOMAIN")
        self.assertIs(result["proof_established"], False)
        self.assertIsNone(result["root_or_nonroot_result"])
        self.assertIs(result["v46_oracle_invoked"], False)

    def test_rational_k_is_a_different_conditional_algebraic_problem(self):
        # At K=3/4 the same formal remainder is (1-3*T^2)/4, whose positive
        # root is Q-algebraic. The source binds K=pi/4, so this substitution
        # cannot justify a claim about the original physical source.
        r = terms(self.report["symbolic_certificate"]["division_remainder"])
        for t in map(Q, range(7)):
            self.assertEqual(at(r, t, Q(0), Q(3, 4)), (1 - 3 * t * t) / 4)
        self.assertIs(self.report["constant_binding"]["rational_approximation_substitution_allowed"], False)

    def test_rescaling_keeps_coefficient_and_endpoint_obligations(self):
        for field in ("new_source_polynomial_has_integer_coefficients", "new_right_endpoint_algebraic_over_Q", "cited_algorithm_assumptions_restored"):
            bad = self.changed()
            bad["rescaling_check"][field] = True
            with self.assertRaises(AssertionError):
                audit_scope(bad)

    def test_actual_certificate_failure_is_typed_nontruth(self):
        with mock.patch.object(self.m, "divide_by_linear", side_effect=self.m.Refusal("injected failed identity")):
            result = self.m.selected_cut_domain_probe()
        self.assertEqual(result["status"], "UNESTABLISHED")
        self.assertIs(result["proof_established"], False)
        self.assertIsNone(result["root_or_nonroot_result"])
        self.assertNotIn("boundary_certificate_sha256", result)

    def test_rational_preflight_precedes_fraction_construction(self):
        for token in ("1e1000000000", "1/0", "1/01", "1/1", "2/4", "-0", "\u0661", "9" * 161, str(1 << 257), True, 1.0):
            with mock.patch.object(self.m, "Fraction", side_effect=AssertionError("constructor was reached")):
                with self.assertRaises(self.m.Refusal):
                    self.m.rational(token)

    def test_source_all_rationals_are_preflighted_before_construction(self):
        spec = self.m.fixed_source()
        spec["sin_splines"]["1"]["controls"][1] = "1e999999999"
        with mock.patch.object(self.m, "Fraction", side_effect=AssertionError("constructor was reached")):
            with self.assertRaises(self.m.Refusal):
                self.m.source_numerator(spec)

    def test_polynomial_type_degree_term_and_operand_budgets(self):
        for records in ([{"powers_T_Y_K": [True, 0, 0], "coefficient": "1"}],
                        [{"powers_T_Y_K": [7, 0, 0], "coefficient": "1"}],
                        [{"powers_T_Y_K": [0, 0, 0], "coefficient": "0"}],
                        [{"powers_T_Y_K": [0, 0, 0], "coefficient": "1/1"}]):
            with self.assertRaises(self.m.Refusal):
                self.m.decode_polynomial(records)
        with self.assertRaises(self.m.Refusal):
            self.m.monomial(1 << 1025)
        for value in (True, 1.0, "1e999999999"):
            with self.assertRaises(self.m.Refusal):
                self.m.monomial(value)
        with self.assertRaises(self.m.Refusal):
            self.m.multiply(self.m.monomial(1, t=6), self.m.monomial(1, t=1))

    def test_report_preflight_precedes_replay(self):
        cycle = []
        cycle.append(cycle)
        shared = []
        deep = 0
        for _ in range(26):
            deep = [deep]
        invalid = [cycle, [shared, shared], deep, {"x": 1.0}, {"x": "a" * 4097}, {"x": 1 << 257}]
        with mock.patch.object(self.m, "expected_report", side_effect=AssertionError("replay was reached")):
            for candidate in invalid:
                with self.assertRaises(self.m.Refusal):
                    self.m.validate_report(candidate)

    def test_json_alias_duplicate_and_scalar_rejections(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}', b'[' * 2000,
                    b'{"x":' + b'9' * 81 + b'}'):
            with self.assertRaises(self.m.Refusal):
                self.m.parse_json_bytes(raw)
        bad = self.changed()
        bad["scope"]["frozen_corpus_additions"] = False
        with self.assertRaises(self.m.Refusal):
            self.m._compare_with_replayed_bytes(bad, self.expected)

    def test_path_budget_precedes_read_and_missing_is_typed(self):
        with mock.patch.object(self.m, "_read_bounded", side_effect=AssertionError("read was reached")):
            for path in ("x" * 4097, Path("x" * 4097), "", "a\0b", 1, True):
                with self.assertRaises(self.m.Refusal):
                    self.m.read_report(path)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(self.m.Refusal):
                self.m.read_report(Path(directory) / "absent.json")

    def test_context_drift_and_oversize_do_not_fall_back(self):
        real_read = self.m._read_bounded
        def changed(path, limit):
            raw = real_read(path, limit)
            return raw + b"\n"
        with mock.patch.object(self.m, "_read_bounded", side_effect=changed):
            with self.assertRaises(self.m.Refusal):
                self.m.expected_report()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large"
            path.write_bytes(b"x" * (self.m.MAX_REFERENCE_BYTES + 1))
            with self.assertRaises(self.m.Refusal):
                self.m._read_bounded(path, self.m.MAX_REFERENCE_BYTES)

    def test_retained_report_buffer_is_not_reread(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"which":"original"}')
            reader = self.m._read_bounded
            def swapped(p, limit):
                raw = reader(p, limit)
                p.write_text('{"which":"replacement"}')
                return raw
            with mock.patch.object(self.m, "_read_bounded", side_effect=swapped):
                self.assertEqual(self.m.read_report(path), {"which": "original"})

    def test_context_is_pinned_reference_data_not_project_execution(self):
        records = self.report["context_reference_bytes"]
        self.assertEqual({r["path"]: r["git_blob"] for r in records}, self.m.REFERENCE_PINS)
        for record in records:
            raw = (ROOT / record["path"]).read_bytes()
            self.assertEqual(blob(raw), record["git_blob"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["sha256"])
            self.assertEqual(len(raw), record["bytes"])
            self.assertEqual(record["use"], "NONEXECUTED_SOURCE_AND_ORACLE_DOMAIN_REFERENCE")
        tree = ast.parse(MODEL.read_bytes())
        imported = {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        imported.update(alias.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names)
        self.assertLessEqual(imported, {"__future__", "argparse", "fractions", "hashlib", "json", "math", "pathlib", "re"})

    def test_exact_nine_path_literal_head_workflow(self):
        text = (ROOT / WORKFLOW).read_text()
        trigger_paths = re.findall(r"^      - '([^']+)'$", text, re.MULTILINE)
        expected = OWN_PATHS | set(self.m.REFERENCE_PINS)
        self.assertEqual(len(expected), 9)
        self.assertEqual(len(trigger_paths), 18)
        self.assertEqual(set(trigger_paths[:9]), expected)
        self.assertEqual(set(trigger_paths[9:]), expected)
        self.assertIn("ref: ${{ github.event.pull_request.head.sha || github.sha }}", text)
        self.assertNotIn("matrix:", text)
        self.assertIn("verify_pb00701_pfaffian_coefficient_boundary.py --contract --self-test", text)


class BootstrapTests(unittest.TestCase):
    def test_real_stale_timestamp_cache_is_bypassed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.py"
            source = b'VALUE = "source"\n'
            path.write_bytes(source)
            cache = Path(importlib.util.cache_from_source(str(path)))
            cache.parent.mkdir()
            payload = compile('VALUE = "cached"\n', str(path), "exec", dont_inherit=True, optimize=0)
            header = importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(path.stat().st_mtime), len(source))
            cache.write_bytes(header + marshal.dumps(payload))
            ordinary = types.ModuleType("ordinary_boundary_fixture")
            importlib.machinery.SourceFileLoader(ordinary.__name__, str(path)).exec_module(ordinary)
            self.assertEqual(ordinary.VALUE, "cached", "Positive control must actually accept stale bytecode")
            verified = checked_module(path, blob(source))
            self.assertEqual(verified.VALUE, "source")

    def test_preload_and_after_read_path_swap_do_not_replace_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.py"
            original = b'VALUE = "checked"\n'
            path.write_bytes(original)
            fake = types.ModuleType("_pb00701_boundary_checked")
            fake.VALUE = "preloaded"
            previous = sys.modules.get(fake.__name__)
            sys.modules[fake.__name__] = fake
            actual_reader = read_code
            def swapped(p):
                raw = actual_reader(p)
                p.write_bytes(b'VALUE = "changed"\n')
                return raw
            try:
                with mock.patch(__name__ + ".read_code", side_effect=swapped):
                    loaded = checked_module(path, blob(original))
                self.assertEqual(loaded.VALUE, "checked")
                self.assertIs(sys.modules[fake.__name__], fake)
            finally:
                if previous is None:
                    sys.modules.pop(fake.__name__, None)
                else:
                    sys.modules[fake.__name__] = previous

    def test_future_flags_and_assertions_have_source_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.py"
            for raw, exception in ((b'assert False, "source assertion"\n', AssertionError),
                                   (b'def f(x: Undefined): pass\n', NameError)):
                path.write_bytes(raw)
                with self.assertRaises(exception):
                    checked_module(path, blob(raw))
            raw = b'from __future__ import annotations\ndef f(x: Undefined): pass\n'
            path.write_bytes(raw)
            self.assertEqual(checked_module(path, blob(raw)).f.__annotations__, {"x": "Undefined"})

    def test_drift_symlink_and_oversize_refuse_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.py"
            raw = b'raise AssertionError("must not execute")\n'
            path.write_bytes(raw)
            with self.assertRaises(ValueError):
                checked_module(path, "0" * 40)
            link = Path(directory) / "alias.py"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                checked_module(link, blob(raw))
            path.write_bytes(b"#" * (MAX_CODE_BYTES + 1))
            with self.assertRaises(ValueError):
                checked_module(path, blob(path.read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("Select --contract and/or --self-test")
    if args.contract:
        _, report, _ = context()
        print("Fresh exact coefficient-boundary contract passed: one external fixture, two exterior zeros, one refused nonalgebraic partition cut")
        print("External pi transcendence and reviewed analytic arguments remain explicit premises")
    if args.self_test:
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)
                                   for cls in (CertificateTests, BootstrapTests))
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
