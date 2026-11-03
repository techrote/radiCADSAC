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
from itertools import product
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
MODEL = HERE / "pb00701_mtp_irreducible_boundary.py"
MODEL_BLOB = "4f9000549834c8f9b60ebc9925fadb71e9f96acf"
MAX_CODE_BYTES = 128 * 1024
WORKFLOW = ".github/workflows/mc1-pb00701-mtp-irreducible-boundary.yml"
OWN_PATHS = {
    "research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_mtp_irreducible_boundary.py",
    "research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary.json",
    "research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary-research.md",
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
    module = types.ModuleType("_pb00701_mtp_boundary_checked")
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


def bernstein(controls, t):
    """Independent direct quadratic Bernstein value and global derivatives."""
    a, b, c = map(exact_q, controls)
    u = t - Q(1, 2)
    return (a * (1-u)**2 + 2*b*u*(1-u) + c*u**2,
            2*((b-a)*(1-u)+(c-b)*u), 2*(c-2*b+a))


def audit_source(report):
    source, cert = report["source"], report["symbolic_certificate"]
    assert source["case_id"] == "research:pb00701:mtp-irreducible-boundary:quadratic-touch"
    assert source["scope"] == "NEW_RESEARCH_FIXTURE_OUTSIDE_FROZEN_FIFTY_SOURCE_COHORT"
    assert source["historical_source_completion_claimed"] is False
    spec = source["spec"]
    assert set(spec) == {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
                         "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"}
    assert spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
    assert spec["source_parameter_id"] == "pb00701-mtp-irreducible-boundary-original-t"
    assert [spec[k] for k in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")] == ["1/2", "3/2", "0", "1"]
    assert spec["sin_splines"] == {} and set(spec["cos_splines"]) == {"0", "1"}
    for h, controls in (("0", ["5/8", "3/8", "5/8"]), ("1", ["-3/8", "-5/8", "-3/8"])):
        spline = spec["cos_splines"][h]
        assert type(spline["degree"]) is int and spline["degree"] == 2
        assert spline == {"degree": 2, "controls": controls,
                          "knots": ["1/2"]*3 + ["3/2"]*3}
    raw = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    assert hashlib.sha256(raw).hexdigest() == source["source_sha256"] == cert["source_sha256"]
    assert cert["monomial_order"] == ["T", "Y", "K"] and cert["formal_K_meaning"] == "pi"
    amplitudes = {name: terms(poly) for name, poly in cert["amplitudes"].items()}
    assert set(amplitudes) == {"C0", "C1"}
    # The submitted polynomials have degree <=6; seven exact values identify
    # them. This establishes polynomial equality, not analytic root sampling.
    for t in map(Q, range(7)):
        for name, h in (("C0", "0"), ("C1", "1")):
            expected, _, _ = bernstein(spec["cos_splines"][h]["controls"], t)
            assert at(amplitudes[name], t, Q(0), Q(0)) == expected
            assert all(p[1] == p[2] == 0 for p, _ in amplitudes[name])
    assert cert["original_tangent_chart"] == "Y=tan(pi*T), valid for 1/2<T<3/2"
    return True


def audit_symbolic(report):
    c = report["symbolic_certificate"]
    ir, co, pos, scale = c["irreducibility"], c["coprime_pair"], c["positivity"], c["rescaling"]
    fields = {
        "denominator": terms(c["tangent_denominator"]), "cleared": terms(c["cleared_numerator"]),
        "g": terms(ir["polynomial"]), "translated": terms(ir["translated_polynomial"]),
        "constant": terms(ir["constant_coefficient_in_Y"]), "discriminant": terms(ir["discriminant_in_Y"]),
        "p": terms(co["p"]), "q": terms(co["q"]), "remainder": terms(co["q_remainder_mod_p"]),
        "delta": terms(pos["delta"]), "delta2": terms(pos["delta_squared"]),
        "positive_coefficient": terms(pos["squared_sine_coefficient"]),
        "radian": terms(scale["polynomial"]), "returned": terms(scale["substituting_X_equals_KT"]),
    }
    # Finite interpolation identity test. Degree <=6 in each variable is checked
    # independently above; the full 7^3 Cartesian grid is sufficient.
    for ti, yi, ki in product(range(7), repeat=3):
        t, y, k = Q(ti), Q(yi), Q(ki)
        d2, g = (t-1)**2, (t-1)**2+y*y
        wanted = {"denominator": 1+y*y, "cleared": g, "g": g,
                  "translated": t*t+y*y, "constant": d2, "discriminant": -4*d2,
                  "p": t-1, "q": y, "remainder": y,
                  "delta": t-1, "delta2": d2, "positive_coefficient": 1-d2,
                  "radian": (t-k)**2+k*k*y*y, "returned": k*k*g}
        for name, value in wanted.items():
            assert at(fields[name], t, y, k) == value, name
        c0, c1 = (d2+1)/2, (d2-1)/2
        assert c0*(1+y*y)+c1*(1-y*y) == g
        assert d2+(1-d2)*(1-y)/2 == c0+c1*y
    assert ir["translation"] == "T=D+1; translated T slot denotes D"
    assert ir["degree_in_Y"] == 2 and type(ir["degree_in_Y"]) is int
    assert ir["leading_coefficient_in_Y"] == "1" and ir["linear_coefficient_in_Y"] == "0"
    assert ir["coefficient_field"] == "Q(T)" and ir["primitive_in_Q_T_Y"] is True
    assert ir["irreducible_over_Q_T_Y"] is True
    assert ir["irreducible_over_complex_coefficients_claimed"] is False
    assert ir["proof_kind"] == "EXACT_PREMISES_WITH_REVIEWED_ALGEBRAIC_ARGUMENT"
    assert ir["algebraic_premises"] == ["Q(T) admits an ordering", "a square is nonnegative in an ordered field",
                                       "quadratic factor criterion over a field of characteristic not two", "Gauss lemma"]
    assert co["rational_common_point"] == {"T": "1", "Y": "0"}
    assert co["analytic_binding"] == "tan(pi)=0" and co["coprime_over_Q_T_Y"] is True
    assert at(fields["p"], Q(1), Q(0), Q(0)) == at(fields["q"], Q(1), Q(0), Q(0)) == 0
    assert fields["remainder"] != []
    assert pos["identity"] == "F(T)=(T-1)^2+(1-(T-1)^2)*sin(pi*T)^2"
    assert list(map(exact_q, pos["delta_interval"])) == [Q(-1, 2), Q(1, 2)]
    upper = max(abs(v) for v in map(exact_q, pos["delta_interval"]))**2
    assert upper == exact_q(pos["delta_squared_upper_bound"]) == Q(1, 4)
    assert 1-upper == exact_q(pos["squared_sine_coefficient_lower_bound"]) == Q(3, 4) > 0
    assert pos["source_lower_bound"] == "(T-1)^2" and pos["strict_unless_T_equals"] == "1"
    assert scale["clearing_factor"] == "K^2" and scale["coefficient_field"] == "Q(pi)"
    assert scale["coefficient_X_squared"] == "1" and scale["coefficient_X"] == "-2*K"
    assert scale["coefficient_ratio"] == "-2*pi"
    assert scale["displayed_polynomial_in_Q_X_Y"] is False
    assert scale["scalar_rationalization_possible"] is False and scale["other_reductions_excluded"] is False
    assert scale["external_premise"] == "pi is irrational"
    return True


def audit_jet_and_endpoints(report):
    cert, source = report["symbolic_certificate"], report["source"]["spec"]
    j = cert["jet"]
    assert j["center"] == "1" and j["local_symbol"] == "D=T-1; original phase remains T"
    arrays = {name: [terms(poly) for poly in j[name]] for name in
              ("C0_coefficients", "C1_coefficients", "cos_2piT_coefficients", "source_coefficients")}
    assert all(len(row) == 3 for row in arrays.values())
    second = terms(j["second_derivative"])
    a = bernstein(source["cos_splines"]["0"]["controls"], Q(1))
    b = bernstein(source["cos_splines"]["1"]["controls"], Q(1))
    assert a == (Q(1, 2), Q(0), Q(1)) and b == (Q(-1, 2), Q(0), Q(1))
    for k in map(Q, range(7)):
        expected = {"C0_coefficients": [a[0], a[1], a[2]/2],
                    "C1_coefficients": [b[0], b[1], b[2]/2],
                    "cos_2piT_coefficients": [Q(1), Q(0), -2*k*k],
                    "source_coefficients": [Q(0), Q(0), 1+k*k]}
        for name, row in arrays.items():
            assert [at(poly, Q(0), Q(0), k) for poly in row] == expected[name]
            assert all(p[0] == p[1] == 0 for poly in row for p, _ in poly)
        # Direct second derivative, independent of candidate jet multiplication.
        direct_second = a[2] + b[2] - 4*k*k*b[0]
        assert at(second, Q(0), Q(0), k) == direct_second == 2*(1+k*k)
    assert all(p[0] == p[1] == 0 for p, _ in second)
    assert j["first_derivative"] == [] and j["physical_root_multiplicity"] == 2
    assert type(j["physical_root_multiplicity"]) is int
    assert j["second_derivative_positive_reason"] == "2*(1+pi^2)>=2>0"
    assert len(cert["endpoints"]) == 2
    for e, t in zip(cert["endpoints"], [Q(1, 2), Q(3, 2)]):
        assert e["coordinate"] == e["original_turns"] == str(t)
        assert e["cosine"] == "-1" and e["value"] == "1" and e["sign"] == 1
        v0 = bernstein(source["cos_splines"]["0"]["controls"], t)[0]
        v1 = bernstein(source["cos_splines"]["1"]["controls"], t)[0]
        assert v0-v1 == 1
        assert terms(e["C0"]) == [((0, 0, 0), v0)] and terms(e["C1"]) == [((0, 0, 0), v1)]
        assert e["auxiliary_tangent_chart_has_pole"] is True
        assert e["original_source_value_established"] is True
    return True


def audit_scope(report):
    assert report["schema"] == "pb00701.mtp-irreducible-boundary.v1"
    assert report["status"] == "ESTABLISHED_SELECTED_DOMAIN_BOUNDARY"
    z = report["source_zero_set"]
    assert z == {"kind": "FINITE_ORIGINAL_SOURCE_ZERO_SET", "closed_domain": ["1/2", "3/2"],
        "closed_root_count": 1, "physical_zeros": [{"event_id": "ROOT_0",
            "coordinate": {"kind": "RATIONAL", "value": "1"}, "location": "SOURCE_SPAN_INTERIOR",
            "original_source_piece_index": 0, "order": {"kind": "SMOOTH_MULTIPLICITY", "value": 2},
            "left_sign": 1, "right_sign": 1}], "true_interior_source_knots": [],
        "source_exteriors": [{"coordinate": "1/2", "side": "LEFT", "value": "1", "sign": 1},
                             {"coordinate": "3/2", "side": "RIGHT", "value": "1", "sign": 1}],
        "maximal_nonzero_components": [
            {"component_id": "CELL_0", "interval": ["1/2", "1"], "left_included": True, "right_included": False, "sign": 1},
            {"component_id": "CELL_1", "interval": ["1", "3/2"], "left_included": False, "right_included": True, "sign": 1}]}
    p = report["primary_theorem_scope"]
    assert p["checked_version"] == "arXiv:2301.05847v1"
    assert p["checked_statement_locations"] == ["Proposition 5.1, printed page 30 (PDF index 29)",
                                                 "Proposition 5.2, printed page 31 (PDF index 30)"]
    assert p["original_polynomial_domain"] == "Q[X,Y]" and p["original_analytic_substitution"] == "Y=tan(X)"
    assert p["selected_polynomial_domain"] == "Q[T,Y]" and p["selected_analytic_substitution"] == "Y=tan(pi*T)"
    for key in ("original_theorems_disproved", "published_full_algorithm_implemented",
                "paper_rational_coefficient_hypotheses_restored_by_rescaling"):
        assert p[key] is False
    for key in ("direct_rational_turn_simple_root_transfer_refuted", "direct_rational_turn_coprime_no_common_root_transfer_refuted"):
        assert p[key] is True
    lit = report["broader_literature_boundary"]
    assert lit["unbounded_problem_domain"] == "[0,infinity)"
    assert lit["bounded_question_location"] == "Open Problem 1, printed page 65:16"
    assert lit["hardness_reduction_to_our_bounded_commensurate_grammar_supplied"] is False
    assert lit["our_bounded_grammar_undecidable_claimed"] is False
    assert report["proof_premises"]["external_theorems"] == ["pi is irrational"]
    assert report["proof_premises"]["proof_assistant_formalization_claimed"] is False
    assert report["proof_premises"]["numeric_sampling_supplies_completeness"] is False
    s = report["scope"]
    assert s["selected_new_fixture_count"] == 1 and type(s["selected_new_fixture_count"]) is int
    assert s["frozen_corpus_additions"] == 0 and type(s["frozen_corpus_additions"]) is int
    for key in ("generic_owner_route_repaired", "new_universal_analytic_solver", "all_exact_methods_excluded",
                "general_impossibility_claimed", "native_evidence_claimed"):
        assert s[key] is False
    assert s["all_26_operations_remain_required"] is True
    assert report["gates"] == {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN",
        "PB-007-04": "OPEN", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED", "production_authorized": False}
    return True


def context():
    global _CONTEXT
    if _CONTEXT is None:
        module = checked_module()
        report = module.expected_report()
        raw = module.bounded_bytes(report)
        module._compare_with_replayed_bytes(module.read_report(), raw)
        for audit in (audit_source, audit_symbolic, audit_jet_and_endpoints, audit_scope):
            audit(report)
        _CONTEXT = module, report, raw
    return _CONTEXT


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.report, cls.expected = context()

    def changed(self):
        return copy.deepcopy(self.report)

    def test_fresh_contract_and_independent_identities(self):
        for audit in (audit_source, audit_symbolic, audit_jet_and_endpoints, audit_scope):
            self.assertTrue(audit(self.report))

    def test_every_original_coefficient_is_material(self):
        for h in ("0", "1"):
            for i in range(3):
                spec = self.m.fixed_source()
                value = Q(spec["cos_splines"][h]["controls"][i])
                spec["cos_splines"][h]["controls"][i] = str(value+Q(1, 128))
                with self.assertRaises(self.m.Refusal):
                    self.m.source_certificate(spec)

    def test_original_phase_parameter_knots_and_all_channels_bound(self):
        for field, value in (("phase_turn_offset", "-1"), ("phase_turn_rate", "1/2"),
                             ("parameter_lo", "0"), ("source_parameter_id", "replaced-parameter")):
            spec = self.m.fixed_source()
            spec[field] = value
            with self.assertRaises(self.m.Refusal):
                self.m.source_certificate(spec)
        for change in ("knot", "harmonic", "sine", "degree", "boolean_degree"):
            spec = self.m.fixed_source()
            if change == "knot": spec["cos_splines"]["0"]["knots"][1] = "0"
            if change == "harmonic": del spec["cos_splines"]["1"]
            if change == "sine": spec["sin_splines"]["1"] = copy.deepcopy(spec["cos_splines"]["0"])
            if change == "degree": spec["cos_splines"]["1"]["degree"] = 1
            if change == "boolean_degree": spec["cos_splines"]["1"]["degree"] = True
            with self.assertRaises(self.m.Refusal): self.m.source_certificate(spec)

    def test_tangent_denominator_retains_original_source(self):
        bad = self.changed()
        bad["symbolic_certificate"]["cleared_numerator"] = copy.deepcopy(bad["symbolic_certificate"]["amplitudes"]["C0"])
        with self.assertRaises(AssertionError): audit_symbolic(bad)

    def test_factored_quadratic_is_not_irreducible_fixture(self):
        m = self.m
        delta = m.add(m.monomial(1, t=1), m.monomial(-1))
        factored = m.add(m.multiply(delta, delta), m.monomial(-1, y=2))
        # (T-1-Y)(T-1+Y) is a real rational factorization.
        self.assertEqual(factored, m.multiply(m.add(delta, m.monomial(-1, y=1)),
                                              m.add(delta, m.monomial(1, y=1))))
        with self.assertRaises(m.Refusal): m.selected_irreducibility_certificate(factored)
        bad = self.changed()
        bad["symbolic_certificate"]["irreducibility"]["discriminant_in_Y"] = m.encode_polynomial(m.scale(m.multiply(delta, delta), 4))
        with self.assertRaises(AssertionError): audit_symbolic(bad)

    def test_coprime_pair_common_point_is_not_origin(self):
        c = self.report["symbolic_certificate"]["coprime_pair"]
        self.assertEqual(at(terms(c["p"]), Q(0), Q(0), Q(0)), -1)
        self.assertEqual(at(terms(c["p"]), Q(1), Q(0), Q(0)), 0)
        self.assertEqual(at(terms(c["q"]), Q(1), Q(0), Q(0)), 0)
        bad = self.changed()
        bad["symbolic_certificate"]["coprime_pair"]["q_remainder_mod_p"] = []
        with self.assertRaises(AssertionError): audit_symbolic(bad)

    def test_touch_cannot_be_relabelled_crossing_or_merged_cell(self):
        for change in ("order", "sign", "merged", "root_boundary"):
            bad = self.changed(); z = bad["source_zero_set"]
            if change == "order": z["physical_zeros"][0]["order"]["value"] = 1
            if change == "sign": z["physical_zeros"][0]["right_sign"] = -1
            if change == "merged": z["maximal_nonzero_components"] = [{"interval": ["1/2", "3/2"], "sign": 1}]
            if change == "root_boundary": z["maximal_nonzero_components"][0]["right_included"] = True
            with self.assertRaises(AssertionError): audit_scope(bad)

    def test_auxiliary_poles_do_not_remove_closed_endpoints(self):
        for index in range(2):
            bad = self.changed(); bad["source_zero_set"]["source_exteriors"].pop(index)
            with self.assertRaises(AssertionError): audit_scope(bad)
            bad = self.changed(); bad["symbolic_certificate"]["endpoints"][index]["value"] = "0"
            with self.assertRaises(AssertionError): audit_jet_and_endpoints(bad)

    def test_positive_remainder_margin_is_required(self):
        for field, wrong in (("delta_squared_upper_bound", "4"),
                             ("squared_sine_coefficient_lower_bound", "-3/4"),
                             ("delta_interval", ["-2", "2"])):
            bad = self.changed(); bad["symbolic_certificate"]["positivity"][field] = wrong
            with self.assertRaises(AssertionError): audit_symbolic(bad)

    def test_original_phase_second_jet_retains_pi_factor(self):
        bad = self.changed()
        bad["symbolic_certificate"]["jet"]["second_derivative"] = self.m.encode_polynomial(self.m.monomial(4))
        with self.assertRaises(AssertionError): audit_jet_and_endpoints(bad)
        bad = self.changed(); bad["symbolic_certificate"]["jet"]["physical_root_multiplicity"] = 4
        with self.assertRaises(AssertionError): audit_jet_and_endpoints(bad)

    def test_rescaling_cannot_drop_nonrational_coefficients(self):
        m = self.m
        bad = self.changed()
        wrong = m.add(m.multiply(m.add(m.monomial(1,t=1),m.monomial(-1)),
                                m.add(m.monomial(1,t=1),m.monomial(-1))),m.monomial(1,y=2))
        bad["symbolic_certificate"]["rescaling"]["polynomial"] = m.encode_polynomial(wrong)
        with self.assertRaises(AssertionError): audit_symbolic(bad)
        for field in ("displayed_polynomial_in_Q_X_Y", "scalar_rationalization_possible", "other_reductions_excluded"):
            bad = self.changed(); bad["symbolic_certificate"]["rescaling"][field] = True
            with self.assertRaises(AssertionError): audit_symbolic(bad)

    def test_radian_and_rational_turn_theorem_domains_stay_distinct(self):
        for field, wrong in (("selected_analytic_substitution", "Y=tan(T)"),
                             ("original_theorems_disproved", True),
                             ("paper_rational_coefficient_hypotheses_restored_by_rescaling", True)):
            bad = self.changed(); bad["primary_theorem_scope"][field] = wrong
            with self.assertRaises(AssertionError): audit_scope(bad)
        bad = self.changed(); bad["broader_literature_boundary"]["our_bounded_grammar_undecidable_claimed"] = True
        with self.assertRaises(AssertionError): audit_scope(bad)

    def test_successful_boundary_probe_still_refuses_direct_transfer(self):
        result = self.m.selected_transfer_probe()
        self.assertEqual(result["status"], "UNSUPPORTED_DIRECT_MTP_THEOREM_TRANSFER")
        self.assertIs(result["direct_theorem_transfer_established"], False)
        self.assertIs(result["boundary_certificate_established"], True)
        self.assertIs(result["source_zero_set_established"], True)
        self.assertEqual(result["boundary_certificate_sha256"], hashlib.sha256(self.expected).hexdigest())

    def test_actual_proof_failure_has_no_success_digest(self):
        for function in ("lower_source", "selected_irreducibility_certificate", "jet_product"):
            with mock.patch.object(self.m, function, side_effect=self.m.Refusal("injected actual proof failure")):
                result = self.m.selected_transfer_probe()
            self.assertEqual(result["status"], "UNESTABLISHED")
            self.assertIs(result["boundary_certificate_established"], False)
            self.assertIs(result["source_zero_set_established"], False)
            self.assertIsNone(result["source_zero_set"])
            self.assertNotIn("boundary_certificate_sha256", result)

    def test_saved_success_cannot_override_failed_fresh_proof(self):
        with mock.patch.object(self.m, "jet_product", side_effect=self.m.Refusal("fresh proof failed")):
            with self.assertRaises(self.m.Refusal): self.m.validate_report(self.report)

    def test_rational_preflight_precedes_fraction_construction(self):
        for token in ("1e1000000000", "1/0", "1/01", "1/1", "2/4", "-0", "\u0661", "9"*161, str(1<<257), True, 1.0):
            with mock.patch.object(self.m, "Fraction", side_effect=AssertionError("constructor reached")):
                with self.assertRaises(self.m.Refusal): self.m.rational(token)

    def test_all_source_tokens_preflight_before_numerical_work(self):
        spec = self.m.fixed_source(); spec["cos_splines"]["1"]["controls"][2] = "1e999999999"
        with mock.patch.object(self.m, "Fraction", side_effect=AssertionError("constructor reached")):
            with self.assertRaises(self.m.Refusal): self.m.lower_source(spec)

    def test_polynomial_budgets_and_exact_types(self):
        for records in ([{"powers_T_Y_K": [True,0,0], "coefficient": "1"}],
                        [{"powers_T_Y_K": [7,0,0], "coefficient": "1"}],
                        [{"powers_T_Y_K": [0,0,0], "coefficient": "0"}],
                        [{"powers_T_Y_K": [0,0,0], "coefficient": "1/1"}]):
            with self.assertRaises(self.m.Refusal): self.m.decode_polynomial(records)
        for value in (1<<1025, True, 1.0, "1e99999999"):
            with self.assertRaises(self.m.Refusal): self.m.monomial(value)
        with self.assertRaises(self.m.Refusal): self.m.multiply(self.m.monomial(1,t=6), self.m.monomial(1,t=1))
        with self.assertRaises(self.m.Refusal): self.m.substitute(self.m.monomial(1,t=6), 0, self.m.monomial(1,t=2))

    def test_report_preflight_precedes_replay(self):
        cycle=[]; cycle.append(cycle); shared=[]; deep=0
        for _ in range(26): deep=[deep]
        with mock.patch.object(self.m,"expected_report",side_effect=AssertionError("replay reached")):
            for candidate in (cycle,[shared,shared],deep,{"x":1.0},{"x":"a"*4097},{"x":1<<257}):
                with self.assertRaises(self.m.Refusal): self.m.validate_report(candidate)

    def test_duplicate_keys_scalars_and_bool_int_substitution(self):
        for raw in (b'{"x":1,"x":2}',b'{"x":1.0}',b'{"x":NaN}',b'['*2000,b'{"x":'+b'9'*81+b'}'):
            with self.assertRaises(self.m.Refusal): self.m.parse_json_bytes(raw)
        bad=self.changed(); bad["scope"]["frozen_corpus_additions"]=False
        with self.assertRaises(self.m.Refusal): self.m._compare_with_replayed_bytes(bad,self.expected)

    def test_path_budget_and_missing_report(self):
        with mock.patch.object(self.m,"_read_bounded",side_effect=AssertionError("read reached")):
            for path in ("x"*4097,Path("x"*4097),"","a\0b",1,True):
                with self.assertRaises(self.m.Refusal): self.m.read_report(path)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(self.m.Refusal): self.m.read_report(Path(directory)/"absent.json")

    def test_changed_or_oversized_reference_refuses(self):
        reader=self.m._read_bounded
        with mock.patch.object(self.m,"_read_bounded",side_effect=lambda path,limit:reader(path,limit)+b"\n"):
            with self.assertRaises(self.m.Refusal): self.m.expected_report()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"large"; path.write_bytes(b"x"*(self.m.MAX_REFERENCE_BYTES+1))
            with self.assertRaises(self.m.Refusal): self.m._read_bounded(path,self.m.MAX_REFERENCE_BYTES)

    def test_retained_report_buffer_survives_path_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"report.json"; path.write_text('{"which":"original"}')
            reader=self.m._read_bounded
            def swapped(p,limit):
                raw=reader(p,limit); p.write_text('{"which":"replacement"}'); return raw
            with mock.patch.object(self.m,"_read_bounded",side_effect=swapped):
                self.assertEqual(self.m.read_report(path),{"which":"original"})

    def test_context_is_checked_data_and_no_project_code_is_imported(self):
        records=self.report["context_references"]
        self.assertEqual({r["path"]:r["git_blob"] for r in records},self.m.REFERENCE_PINS)
        for r in records:
            raw=(ROOT/r["path"]).read_bytes()
            self.assertEqual(blob(raw),r["git_blob"])
            self.assertEqual(len(raw),r["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),r["sha256"])
            self.assertEqual(r["use"],"NONEXECUTED_SOURCE_GRAMMAR_AND_PRIOR_BOUNDARY_REFERENCE")
        tree=ast.parse(MODEL.read_bytes())
        imported={n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}
        imported.update(a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names)
        self.assertLessEqual(imported,{"__future__","argparse","fractions","hashlib","json","math","pathlib","re"})

    def test_exact_nine_path_literal_head_workflow(self):
        text=(ROOT/WORKFLOW).read_text()
        trigger_paths=re.findall(r"^      - '([^']+)'$",text,re.MULTILINE)
        expected=OWN_PATHS|set(self.m.REFERENCE_PINS)
        self.assertEqual(len(expected),9); self.assertEqual(len(trigger_paths),18)
        self.assertEqual(set(trigger_paths[:9]),expected); self.assertEqual(set(trigger_paths[9:]),expected)
        self.assertIn("ref: ${{ github.event.pull_request.head.sha || github.sha }}",text)
        self.assertNotIn("matrix:",text)
        self.assertIn("verify_pb00701_mtp_irreducible_boundary.py --contract --self-test",text)


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
            fake = types.ModuleType("_pb00701_mtp_boundary_checked")
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
        context()
        print("Fresh MTP boundary contract passed: one exact double root, two positive components, both closed endpoints")
        print("The original rational-radian theorems remain valid; the direct rational-turn transfer is refused")
    if args.self_test:
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)
                                   for cls in (CertificateTests, BootstrapTests))
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
