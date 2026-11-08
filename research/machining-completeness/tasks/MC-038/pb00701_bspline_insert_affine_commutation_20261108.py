#!/usr/bin/env python3
"""Source-bound commuting square: exact B-spline insertion and affine time maps.

Prospective, bounded DETERMINISTIC_MODEL only. A commuting representation
diagram is not an original-corpus, native machining or STEP certificate.
"""
from __future__ import annotations

import argparse
import copy
import functools
import unittest
from fractions import Fraction as Q

import pb00701_generic_interval_events_20261108 as core
import pb00701_genuine_bspline_knot_bridge_20261108 as bridge
import pb00701_bspline_knot_insertion_lineage_20261108 as insertion
import pb00701_bspline_affine_time_covariance_20261108 as affine

need = core.need
Nontruth = core.Nontruth

STATUS = "COMPLETE_RESTRICTED_BSPLINE_INSERT_AFFINE_COMMUTING_SQUARE"
TOP_KEYS = {
    "status", "evidence_class", "field", "insert_at_old",
    "time_map", "insert_at_new", "bits", "original_supplied_sha256",
    "terminal_supplied_sha256", "terminal_derived_sha256",
    "physical_root_count", "insertion_then_affine",
    "affine_then_insertion", "historical_corpus_membership_claimed",
    "new_historical_closures", "required_pb_po_discharges",
    "pb00701_established", "mc_b_established", "mc1_established",
    "production_authorized",
}


def exact_insert_source(spec, field, at):
    """Representation operation only; no complete-event proof requested."""
    need(type(field) is str and field in core.KEYS, "SQUARE_FIELD")
    need(type(at) is str, "SQUARE_POINT_ENCODING")
    updated = copy.deepcopy(spec)
    updated["splines"][field], _ = insertion.insert_exact(
        updated["splines"][field], at)
    bridge.source_to_pieces(updated)
    return updated


def square_sources(spec, field, at, offset, slope):
    """Construct both paths and require identical exact supplied vectors.

    Insertion-at-old-time followed by affine map must equal affine map
    followed by insertion at (old_time-a)/b, including b<0 reversal.
    """
    need(type(at) is str, "SQUARE_POINT_ENCODING")
    t = core.fraction(at)
    need(at == str(t), "SQUARE_POINT_NONCANONICAL")
    a, b = affine.parse_map(offset, slope)
    mapped_t = str((t-a)/b)

    left_intermediate = exact_insert_source(spec, field, at)
    left_final, _, _ = affine.remap(left_intermediate, offset, slope)
    right_intermediate, _, _ = affine.remap(spec, offset, slope)
    right_final = exact_insert_source(right_intermediate, field, mapped_t)

    need(core.canonical(left_final) == core.canonical(right_final),
         "SQUARE_SUPPLIED_VECTOR_DRIFT")
    left_doc, left_parsed, left_knots = bridge.source_to_pieces(left_final)
    right_doc, right_parsed, right_knots = bridge.source_to_pieces(right_final)
    need(core.canonical(left_doc) == core.canonical(right_doc) and
         left_parsed.identity == right_parsed.identity and
         left_knots == right_knots,
         "SQUARE_EXACT_POLYNOMIAL_OR_KNOT_DRIFT")
    insertion.certify_polynomial_equivalence(spec, left_intermediate)
    insertion.certify_polynomial_equivalence(
        right_intermediate, right_final)
    # Both exact affine whole-piece correspondences also replay independently.
    prior = bridge.source_to_pieces(spec)[1]
    mapped = bridge.source_to_pieces(right_intermediate)[1]
    affine.coefficient_witness(prior, mapped, a, b)
    after_insert = bridge.source_to_pieces(left_intermediate)[1]
    affine.coefficient_witness(after_insert, left_parsed, a, b)
    return mapped_t, left_final, right_final


def child_square(spec, field, at, offset, slope, bits):
    """Each of four edges receives a source-bound *complete* parent proof."""
    old_insert = insertion.certify(spec, field, at, bits=bits)
    after_insert_map = affine.certify(
        old_insert["post_edit_source"], offset, slope, bits=bits)
    old_map = affine.certify(spec, offset, slope, bits=bits)
    a, b = affine.parse_map(offset, slope)
    mapped_at = str((core.fraction(at)-a)/b)
    after_map_insert = insertion.certify(
        old_map["transformed_source"], field, mapped_at, bits=bits)
    return {
        "insertion_then_affine": {
            "insertion": old_insert, "affine": after_insert_map},
        "affine_then_insertion": {
            "affine": old_map, "insertion": after_map_insert},
    }


def verified_edges(spec, field, at, offset, slope, bits, edges):
    """Check both chains independently: receipts are not trusted on input."""
    need(type(edges) is dict and set(edges) ==
         {"insertion_then_affine", "affine_then_insertion"},
         "SQUARE_CHILD_FIELDS")
    left, right = edges["insertion_then_affine"], edges["affine_then_insertion"]
    need(type(left) is dict and set(left) == {"insertion", "affine"} and
         type(right) is dict and set(right) == {"affine", "insertion"},
         "SQUARE_EDGE_FIELDS")
    li, la = left["insertion"], left["affine"]
    ra, ri = right["affine"], right["insertion"]

    a, b = affine.parse_map(offset, slope)
    mapped_at = str((core.fraction(at)-a)/b)
    insertion.verify(spec, li)
    affine.verify(li["post_edit_source"], la)
    affine.verify(spec, ra)
    insertion.verify(ra["transformed_source"], ri)
    need(li["field"] == ri["field"] == field and
         li["insert_at"] == at and ri["insert_at"] == mapped_at,
         "SQUARE_INSERTION_EDGE_IDENTITY")
    need(la["time_map"]["old_t_offset"] ==
         ra["time_map"]["old_t_offset"] == offset and
         la["time_map"]["old_t_slope"] ==
         ra["time_map"]["old_t_slope"] == slope,
         "SQUARE_AFFINE_EDGE_IDENTITY")
    # The source verifier authenticates the difference between an original
    # structural knot and one introduced by this operation. Reversal does
    # not magically make the new knot a pre-edit historical knot.
    for key in ("old_field_multiplicity", "new_field_multiplicity",
                "was_pre_edit_field_knot", "new_coordinate_in_field"):
        need(li["insertion_lineage"][key] ==
             ri["insertion_lineage"][key],
             "SQUARE_INSERTION_PROVENANCE_DRIFT")
    affine.structural_witness(
        li["post_edit_structural_knot_witnesses"],
        ri["post_edit_structural_knot_witnesses"], a, b)
    final_left = la["transformed_source"]
    final_right = ri["post_edit_source"]
    need(core.canonical(final_left) == core.canonical(final_right),
         "SQUARE_TERMINAL_SOURCE_DRIFT")
    left_doc, left_src, left_knots = bridge.source_to_pieces(final_left)
    right_doc, right_src, right_knots = bridge.source_to_pieces(final_right)
    need(core.canonical(left_doc) == core.canonical(right_doc) and
         left_src.identity == right_src.identity and
         left_knots == right_knots,
         "SQUARE_TERMINAL_DERIVED_DRIFT")

    roots = [
        li["pre_edit_complete_events"]["physical_events"]["physical_root_count"],
        li["post_edit_complete_events"]["physical_events"]["physical_root_count"],
        la["original_complete_events"]["physical_events"]["physical_root_count"],
        la["transformed_complete_events"]["physical_events"]["physical_root_count"],
        ra["original_complete_events"]["physical_events"]["physical_root_count"],
        ra["transformed_complete_events"]["physical_events"]["physical_root_count"],
        ri["pre_edit_complete_events"]["physical_events"]["physical_root_count"],
        ri["post_edit_complete_events"]["physical_events"]["physical_root_count"],
    ]
    need(all(type(n) is int and n == roots[0] for n in roots),
         "SQUARE_PHYSICAL_COUNT_DRIFT")
    for parent in (li["pre_edit_complete_events"],
                   li["post_edit_complete_events"],
                   la["original_complete_events"],
                   la["transformed_complete_events"],
                   ra["original_complete_events"],
                   ra["transformed_complete_events"],
                   ri["pre_edit_complete_events"],
                   ri["post_edit_complete_events"]):
        need(parent["physical_events"]["target_binary_bits"] == bits,
             "SQUARE_CHILD_PRECISION_DRIFT")
    return {
        "insert_at_new": mapped_at,
        "original_supplied_sha256": bridge.source_hash(spec),
        "terminal_supplied_sha256": bridge.source_hash(final_left),
        "terminal_derived_sha256": left_src.identity,
        "physical_root_count": roots[0],
    }


def produce(spec, field, at, offset, slope, bits=10):
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS,
         "SQUARE_BITS_BUDGET")
    need(type(field) is str and field in core.KEYS, "SQUARE_FIELD")
    need(type(at) is str and at == str(core.fraction(at)),
         "SQUARE_POINT_NONCANONICAL")
    a, b = affine.parse_map(offset, slope)
    edges = child_square(spec, field, at, offset, slope, bits)
    cross = verified_edges(spec, field, at, offset, slope, bits, edges)
    # A separate direct full-source construction challenges both nested
    # producers, not just agreement among four supplied receipt fields.
    direct_at, direct_left, _ = square_sources(
        spec, field, at, offset, slope)
    need(direct_at == cross["insert_at_new"] and
         bridge.source_hash(direct_left) == cross["terminal_supplied_sha256"],
         "SQUARE_INDEPENDENT_CONSTRUCTION_DRIFT")
    return {
        "status": STATUS, "evidence_class": "DETERMINISTIC_MODEL",
        "field": field, "insert_at_old": at,
        "time_map": {"old_t_offset": str(a), "old_t_slope": str(b)},
        "bits": bits, **cross, **edges,
        "historical_corpus_membership_claimed": False,
        "new_historical_closures": [], "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def verify(spec, receipt):
    """Verify receipt without regenerating expensive complete root searches."""
    try:
        need(type(receipt) is dict and set(receipt) == TOP_KEYS,
             "SQUARE_RECEIPT_FIELDS")
        field, at, bits = (receipt["field"], receipt["insert_at_old"],
                           receipt["bits"])
        need(type(field) is str and field in core.KEYS, "SQUARE_FIELD")
        need(type(at) is str and at == str(core.fraction(at)),
             "SQUARE_POINT_NONCANONICAL")
        need(type(bits) is int and 1 <= bits <= core.MAX_BITS,
             "SQUARE_BITS_BUDGET")
        m = receipt["time_map"]
        need(type(m) is dict and set(m) ==
             {"old_t_offset", "old_t_slope"}, "SQUARE_TIME_MAP_FIELDS")
        a, b = affine.parse_map(m["old_t_offset"], m["old_t_slope"])
        edges = {
            "insertion_then_affine": receipt["insertion_then_affine"],
            "affine_then_insertion": receipt["affine_then_insertion"],
        }
        check = verified_edges(
            spec, field, at, str(a), str(b), bits, edges)
        # Replay exact source transformations independently from the four
        # children, without calling certificate generators in the verifier.
        direct_at, direct_final, _ = square_sources(
            spec, field, at, str(a), str(b))
        need(direct_at == check["insert_at_new"] and
             bridge.source_hash(direct_final) ==
             check["terminal_supplied_sha256"],
             "SQUARE_REPLAY_SOURCE_DRIFT")
        expected = {
            "status": STATUS, "evidence_class": "DETERMINISTIC_MODEL",
            "field": field, "insert_at_old": at,
            "time_map": {"old_t_offset": str(a), "old_t_slope": str(b)},
            "bits": bits, **check,
            "historical_corpus_membership_claimed": False,
            "new_historical_closures": [], "required_pb_po_discharges": 0,
            "pb00701_established": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False,
        }
        for k, v in expected.items():
            need(core.canonical(receipt[k]) == core.canonical(v),
                 "SQUARE_RECEIPT_REPLAY_DRIFT:" + k)
        return True
    except Nontruth:
        raise
    except (KeyError, IndexError, TypeError, AttributeError, ValueError,
            OverflowError, RecursionError) as exc:
        raise Nontruth("SQUARE_MALFORMED_RECEIPT") from exc


def certify(spec, field, at, offset, slope, bits=10):
    receipt = produce(spec, field, at, offset, slope, bits)
    verify(spec, receipt)
    return receipt


@functools.lru_cache(maxsize=1)
def reference():
    return certify(bridge.POSITIVE_TANGENCY, "H0", "1/2", "3/2", "-1/2")


class Tests(unittest.TestCase):
    def test_reversed_time_genuine_tangency_both_certified_routes(self):
        rec = copy.deepcopy(reference())
        self.assertTrue(verify(bridge.POSITIVE_TANGENCY, rec))
        self.assertEqual(rec["insert_at_new"], "2")
        self.assertEqual(rec["physical_root_count"], 1)
        self.assertTrue(rec["insertion_then_affine"]["insertion"]
                        ["insertion_lineage"]["new_coordinate_in_field"])
        self.assertFalse(rec["historical_corpus_membership_claimed"])

    def test_forward_half_rate_both_certified_routes(self):
        rec = certify(bridge.POSITIVE_TANGENCY, "H0", "1/2", "0", "1/2")
        self.assertEqual(rec["insert_at_new"], "1")
        self.assertEqual(rec["physical_root_count"], 1)

    def test_preexisting_simple_knot_identity_both_routes(self):
        spec = copy.deepcopy(bridge.POSITIVE_TANGENCY)
        spec["splines"]["H0"] = bridge.spline(
            2, ["0", "0", "0", "1", "2", "2", "2"], ["3"] * 4)
        rec = certify(spec, "H0", "1", "2", "-1")
        self.assertFalse(rec["insertion_then_affine"]["insertion"]
                         ["insertion_lineage"]["new_coordinate_in_field"])
        self.assertEqual(rec["physical_root_count"], 0)

    def test_bounded_direct_exact_paths_and_sided_orientation(self):
        total = 0
        for field, points in (
            ("H0", ("1/4", "1/2", "3/4", "5/4", "3/2", "7/4")),
            ("S1", ("1/2", "3/2")),
        ):
            for at in points:
                for offset, slope in (
                    ("0", "1/2"), ("2", "-1"),
                    ("3/2", "-1/2"), ("1/2", "1")):
                    mapped, left, right = square_sources(
                        bridge.POSITIVE_TANGENCY,
                        field, at, offset, slope)
                    self.assertEqual(left, right)
                    self.assertEqual(Q(mapped),
                                     (Q(at)-Q(offset))/Q(slope))
                    total += 1
        self.assertEqual(total, 32)

    def test_source_child_precision_and_promotion_forgery_refuse(self):
        correct = reference()
        for name, field, value in (
            ("top_precision_down", "bits", 9),
            ("top_precision_up", "bits", 11),
            ("false_original", "historical_corpus_membership_claimed", True),
            ("fake_pb", "required_pb_po_discharges", 1),
            ("fake_mcb", "mc_b_established", True),
            ("fake_time", "insert_at_new", "3/2"),
            ("wrong_hash", "terminal_supplied_sha256", "0"*64),
            ("wrong_count", "physical_root_count", 5),
        ):
            with self.subTest(name=name):
                forged = copy.deepcopy(correct)
                forged[field] = value
                with self.assertRaises(Nontruth):
                    verify(bridge.POSITIVE_TANGENCY, forged)
        for edge, child, subkey, path, value in (
            ("insertion_then_affine", "insertion", "insertion_lineage",
             "old_field_multiplicity", 1),
            ("affine_then_insertion", "insertion", "insertion_lineage",
             "new_coordinate_in_field", False),
        ):
            forged = copy.deepcopy(correct)
            forged[edge][child][subkey][path] = value
            with self.assertRaises(Nontruth):
                verify(bridge.POSITIVE_TANGENCY, forged)
        forged = copy.deepcopy(correct)
        forged["affine_then_insertion"]["affine"][
            "transformed_complete_events"]["physical_events"][
                "physical_root_count"] = 8
        with self.assertRaises(Nontruth):
            verify(bridge.POSITIVE_TANGENCY, forged)
        forged = copy.deepcopy(correct)
        forged["insertion_then_affine"]["affine"][
            "transformed_complete_events"]["physical_events"][
                "target_binary_bits"] = 9
        with self.assertRaises(Nontruth):
            verify(bridge.POSITIVE_TANGENCY, forged)
        changed = copy.deepcopy(bridge.POSITIVE_TANGENCY)
        changed["splines"]["H0"]["controls"][0] = "13/8"
        with self.assertRaises(Nontruth):
            verify(changed, copy.deepcopy(correct))

    def test_invalid_map_and_insertion_refuse(self):
        for at, offset, slope in (
            ("1/2", "0", "0"),
            ("1/2", "0", "-0"),
            ("2/4", "2", "-1"),
            ("1/2", "0", "2/4"),
            ("1", "2", "-1"),  # true H0 double knot is saturated
            ("0", "2", "-1"),
        ):
            with self.subTest(at=at, offset=offset, slope=slope):
                with self.assertRaises(Nontruth):
                    produce(bridge.POSITIVE_TANGENCY,
                            "H0", at, offset, slope)
        with self.assertRaises(Nontruth):
            produce(bridge.POSITIVE_TANGENCY,
                    "H0", "1/2", "2", "-1", bits=True)


def contract():
    r = reference()
    need(r["physical_root_count"] == 1 and
         r["insert_at_new"] == "2" and
         not r["historical_corpus_membership_claimed"] and
         r["required_pb_po_discharges"] == 0 and
         not r["mc_b_established"] and
         not r["production_authorized"],
         "SQUARE_CONTRACT_DRIFT")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("EXACT_BSPLINE_INSERT_AFFINE_COMMUTATION_CONTRACT_PASS")
    if args.self_test:
        unittest.main(argv=["unittest"], exit=False)
