#!/usr/bin/env python3
"""Boehm knot insertion with exact physical-event and input-lineage certificates.

Research-only deterministic model. An inserted structural knot is NOT evidence
of a knot in the pre-edit source, still less membership in the frozen corpus.
"""
from __future__ import annotations

import argparse
import copy
import functools
import random
import unittest
from fractions import Fraction as Q

import pb00701_generic_interval_events_20261108 as core
import pb00701_genuine_bspline_knot_bridge_20261108 as bridge

Nontruth = core.Nontruth
need = core.need

MAX_INSERTION_STEPS = 1  # Explicit bounded interface. Extend by a new proof, not a loop.


def insert_exact(raw, at):
    """Insert one interior rational knot without changing a B-spline function.

    Standard one-knot de Boor/Boehm recurrence. Equality of every polynomial
    source coefficient is checked independently in the consumer, not assumed
    from this recurrence.
    """
    p, u, c, multiplicities = bridge.spline_parse(raw)
    t = core.fraction(at)
    need(u[0] < t < u[-1], "INSERTION_NOT_INTERIOR")
    s = multiplicities.get(t, 0)
    need(s < max(p, 1), "INSERTION_MULTIPLICITY_EXHAUSTED")
    k = max(i for i in range(len(u)-1) if u[i] <= t < u[i+1])
    n = len(c)-1
    need(0 <= k <= n, "INSERTION_SPAN_INDEX")
    need(n+2 <= bridge.MAX_CONTROLS, "INSERTION_CONTROL_BUDGET")

    updated = [None]*(n+2)
    for i in range(k-p+1):
        updated[i] = c[i]
    for i in range(k-s+1, n+2):
        updated[i] = c[i-1]
    for i in range(k-p+1, k-s+1):
        den = u[i+p]-u[i]
        need(den > 0, "INSERTION_ALPHA_DENOMINATOR")
        alpha = (t-u[i])/den
        need(Q(0) <= alpha <= Q(1), "INSERTION_ALPHA_RANGE")
        updated[i] = (Q(1)-alpha)*c[i-1]+alpha*c[i]
    need(all(x is not None for x in updated), "INSERTION_UNASSIGNED_CONTROL")

    knots = u[:k+1]+(t,)+u[k+1:]
    result = {
        "degree": p,
        "knots": [str(x) for x in knots],
        "controls": [str(x) for x in updated],
    }
    # Independently parse the result, including clamping and multiplicity.
    bridge.spline_parse(result)
    return result, {
        "insert_at": str(t),
        "old_field_multiplicity": s,
        "new_field_multiplicity": s+1,
        "was_pre_edit_field_knot": s != 0,
        "new_coordinate_in_field": s == 0,
        "span_index_before_insertion": k,
    }


def certify_polynomial_equivalence(old, new):
    """Exact equality of all five reconstructed coefficients on every new span.

    The parent authenticates both supplied knot/control vectors independently.
    A new representation can split an old polynomial span; identities of the
    canonical piece sources will differ even when physical functions agree.
    """
    _, before, _ = bridge.source_to_pieces(old)
    _, after, _ = bridge.source_to_pieces(new)
    need(before.pieces[0].lo == after.pieces[0].lo and
         before.pieces[-1].hi == after.pieces[-1].hi,
         "REFINEMENT_DOMAIN_MISMATCH")
    proof = []
    for i, piece in enumerate(after.pieces):
        covering = [(j, prior) for j, prior in enumerate(before.pieces)
                    if prior.lo <= piece.lo and piece.hi <= prior.hi]
        need(len(covering) == 1, "REFINEMENT_OLD_SPAN_NOT_UNIQUE")
        j, old_piece = covering[0]
        need(piece.polys == old_piece.polys,
             "REFINEMENT_COEFFICIENT_POLYNOMIAL_DRIFT")
        proof.append({"new_piece_index": i, "old_piece_index": j,
                      "lo": str(piece.lo), "hi": str(piece.hi)})
    need(proof and len(proof) == len(after.pieces),
         "REFINEMENT_INCOMPLETE_PARTITION")
    return proof


def produce(spec, field, at, bits=10):
    need(type(field) is str and field in core.KEYS,
         "INSERTION_COEFFICIENT_FIELD")
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS,
         "INSERTION_EVENT_BITS_BUDGET")
    need(type(at) is str, "INSERTION_POINT_ENCODING")
    # Source parser authenticates all field grammars and common domain.
    old_doc, old_parsed, old_knots = bridge.source_to_pieces(spec)
    before = bridge.certify(spec, bits=bits)
    updated = copy.deepcopy(spec)
    replacement, step = insert_exact(updated["splines"][field], at)
    updated["splines"][field] = replacement

    new_doc, new_parsed, new_knots = bridge.source_to_pieces(updated)
    proof = certify_polynomial_equivalence(spec, updated)
    after = bridge.certify(updated, bits=bits)
    need(before["physical_events"]["physical_root_count"] ==
         after["physical_events"]["physical_root_count"],
         "REFINEMENT_PHYSICAL_EVENT_COUNT_DRIFT")
    need(old_parsed.identity != new_parsed.identity or old_doc == new_doc,
         "REFINEMENT_DERIVED_IDENTITY_COLLISION")
    need(bridge.source_hash(spec) != bridge.source_hash(updated),
         "REFINEMENT_SOURCE_IDENTITY_COLLISION")
    return {
        "status": "COMPLETE_EXACT_BSPLINE_REFINEMENT_WITH_EVENT_PROOFS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "field": field,
        "insert_at": step["insert_at"],
        "bits": bits,
        "pre_edit_supplied_source_sha256": bridge.source_hash(spec),
        "post_edit_supplied_source_sha256": bridge.source_hash(updated),
        "pre_edit_derived_piece_sha256": old_parsed.identity,
        "post_edit_derived_piece_sha256": new_parsed.identity,
        "insertion_lineage": step,
        "pre_edit_structural_knot_witnesses": old_knots,
        "post_edit_structural_knot_witnesses": new_knots,
        "post_edit_source": updated,
        "exact_polynomial_refinement_witness": proof,
        "pre_edit_complete_events": before,
        "post_edit_complete_events": after,
        "historical_corpus_knot_membership_claimed": False,
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def verify(spec, receipt):
    """Reconstruct source lineage; independently replay both supplied proofs.

    No numerical recertification is necessary here: the inherited verifier
    checks every cell and event of each independently supplied certificate.
    This avoids recomputing expensive complete event search in a verifier.
    """
    need(type(receipt) is dict and set(receipt) == {
        "status", "evidence_class", "field", "insert_at", "bits",
        "pre_edit_supplied_source_sha256", "post_edit_supplied_source_sha256",
        "pre_edit_derived_piece_sha256", "post_edit_derived_piece_sha256",
        "insertion_lineage", "pre_edit_structural_knot_witnesses",
        "post_edit_structural_knot_witnesses", "post_edit_source",
        "exact_polynomial_refinement_witness", "pre_edit_complete_events",
        "post_edit_complete_events", "historical_corpus_knot_membership_claimed",
        "new_historical_closures", "required_pb_po_discharges",
        "pb00701_established", "mc_b_established", "mc1_established",
        "production_authorized"}, "REFINEMENT_RECEIPT_FIELDS")
    field, at, bits = receipt["field"], receipt["insert_at"], receipt["bits"]
    need(type(field) is str and field in core.KEYS,
         "INSERTION_COEFFICIENT_FIELD")
    need(type(at) is str, "INSERTION_POINT_ENCODING")
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS,
         "INSERTION_EVENT_BITS_BUDGET")
    old_doc, old_parsed, old_knots = bridge.source_to_pieces(spec)
    refined = copy.deepcopy(spec)
    new_field, step = insert_exact(refined["splines"][field], at)
    refined["splines"][field] = new_field
    new_doc, new_parsed, new_knots = bridge.source_to_pieces(refined)
    witness = certify_polynomial_equivalence(spec, refined)
    need(old_parsed.identity != new_parsed.identity or old_doc == new_doc,
         "REFINEMENT_DERIVED_IDENTITY_COLLISION")
    need(bridge.source_hash(spec) != bridge.source_hash(refined),
         "REFINEMENT_SOURCE_IDENTITY_COLLISION")
    expected = {
        "status": "COMPLETE_EXACT_BSPLINE_REFINEMENT_WITH_EVENT_PROOFS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "field": field, "insert_at": step["insert_at"], "bits": bits,
        "pre_edit_supplied_source_sha256": bridge.source_hash(spec),
        "post_edit_supplied_source_sha256": bridge.source_hash(refined),
        "pre_edit_derived_piece_sha256": old_parsed.identity,
        "post_edit_derived_piece_sha256": new_parsed.identity,
        "insertion_lineage": step,
        "pre_edit_structural_knot_witnesses": old_knots,
        "post_edit_structural_knot_witnesses": new_knots,
        "post_edit_source": refined,
        "exact_polynomial_refinement_witness": witness,
        "historical_corpus_knot_membership_claimed": False,
        "new_historical_closures": [], "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }
    for key, value in expected.items():
        try:
            good = core.canonical(receipt[key]) == core.canonical(value)
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise Nontruth("REFINEMENT_RECEIPT_MALFORMED") from exc
        need(good, "REFINEMENT_RECEIPT_REPLAY_DRIFT:" + key)
    before, after = (receipt["pre_edit_complete_events"],
                     receipt["post_edit_complete_events"])
    bridge.verify(spec, before)
    bridge.verify(refined, after)
    need(before["physical_events"]["physical_root_count"] ==
         after["physical_events"]["physical_root_count"],
         "REFINEMENT_PHYSICAL_EVENT_COUNT_DRIFT")
    return True


def certify(spec, field, at, bits=10):
    receipt = produce(spec, field, at, bits)
    verify(spec, receipt)
    return receipt


@functools.lru_cache(maxsize=1)
def qualified_positive():
    """One immutable reference receipt; mutation tests deep-copy it."""
    return certify(bridge.POSITIVE_TANGENCY, "H0", "1/2")


class Tests(unittest.TestCase):
    def test_insertion_preserves_full_h1_h2_tangency(self):
        rec = copy.deepcopy(qualified_positive())
        self.assertEqual(rec["insertion_lineage"]["new_coordinate_in_field"],
                         True)
        self.assertEqual(rec["insertion_lineage"]["old_field_multiplicity"], 0)
        self.assertEqual(rec["pre_edit_structural_knot_witnesses"],
                         [{"t": "1", "field_multiplicities": {"H0": 2}}])
        self.assertEqual([r["t"] for r in
                          rec["post_edit_structural_knot_witnesses"]],
                         ["1/2", "1"])
        self.assertEqual(rec["post_edit_complete_events"]["physical_events"]
                         ["physical_root_count"], 1)
        self.assertEqual(rec["pre_edit_complete_events"]["physical_events"]
                         ["physical_root_count"], 1)
        self.assertTrue(verify(bridge.POSITIVE_TANGENCY, rec))

    def test_inserting_degree_zero_coefficient_is_a_refinement(self):
        rec = certify(bridge.POSITIVE_TANGENCY, "S1", "1/2")
        self.assertEqual(rec["post_edit_source"]["splines"]["S1"]["controls"],
                         ["0", "0"])
        self.assertEqual(rec["insertion_lineage"]["new_field_multiplicity"], 1)
        self.assertFalse(rec["historical_corpus_knot_membership_claimed"])

    def test_existing_simple_knot_refinement_preserves_derived_source(self):
        """A pre-existing source knot gains multiplicity but is not introduced."""
        data = copy.deepcopy(bridge.POSITIVE_TANGENCY)
        data["splines"]["H0"] = bridge.spline(
            2, ["0", "0", "0", "1", "2", "2", "2"],
            ["3", "3", "3", "3"])
        rec = certify(data, "H0", "1")
        self.assertEqual(rec["insertion_lineage"]["old_field_multiplicity"], 1)
        self.assertEqual(rec["insertion_lineage"]["new_field_multiplicity"], 2)
        self.assertFalse(rec["insertion_lineage"]["new_coordinate_in_field"])
        self.assertTrue(rec["insertion_lineage"]["was_pre_edit_field_knot"])
        self.assertNotEqual(rec["pre_edit_supplied_source_sha256"],
                            rec["post_edit_supplied_source_sha256"])
        self.assertEqual(rec["pre_edit_derived_piece_sha256"],
                         rec["post_edit_derived_piece_sha256"])
        self.assertEqual(rec["pre_edit_complete_events"]["physical_events"]
                         ["physical_root_count"], 0)
        self.assertEqual(rec["post_edit_complete_events"]["physical_events"]
                         ["physical_root_count"], 0)
        self.assertTrue(verify(data, rec))

    def test_existing_double_knot_fails_closed(self):
        with self.assertRaisesRegex(Nontruth, "INSERTION_MULTIPLICITY_EXHAUSTED"):
            produce(bridge.POSITIVE_TANGENCY, "H0", "1")

    def test_noncanonical_insertion_point_and_unknown_field(self):
        for point in ("2/4", "1.0", "0", "2", "1000000000000000000000000"):
            with self.subTest(point=point), self.assertRaises(Nontruth):
                produce(bridge.POSITIVE_TANGENCY, "H0", point)
        with self.assertRaises(Nontruth):
            produce(bridge.POSITIVE_TANGENCY, "ZZ", "1/2")
        with self.assertRaises(Nontruth):
            produce(bridge.POSITIVE_TANGENCY, "H0", "1/2", bits=True)

    def test_tamper_lineage_event_source_and_gate_refuse(self):
        rec = copy.deepcopy(qualified_positive())
        mutations = [
            ("historical_corpus_knot_membership_claimed", True),
            ("required_pb_po_discharges", False),
            ("new_historical_closures", ["forged"]),
            ("pre_edit_supplied_source_sha256", "0"*64),
            ("exact_polynomial_refinement_witness", []),
            ("field", "C1"),
        ]
        for name, value in mutations:
            with self.subTest(name=name):
                bad = copy.deepcopy(rec)
                bad[name] = value
                with self.assertRaises(Nontruth):
                    verify(bridge.POSITIVE_TANGENCY, bad)
        bad = copy.deepcopy(rec)
        bad["post_edit_complete_events"]["physical_events"]["physical_root_count"] = 9
        with self.assertRaises(Nontruth):
            verify(bridge.POSITIVE_TANGENCY, bad)

    def test_changed_original_source_refuses_receipt(self):
        rec = copy.deepcopy(qualified_positive())
        forged = copy.deepcopy(bridge.POSITIVE_TANGENCY)
        forged["splines"]["H0"]["controls"][0] = "3"
        with self.assertRaises(Nontruth):
            verify(forged, rec)

    def test_random_exact_boehm_basis_invariance(self):
        rng = random.Random(20261108)
        checked = 0
        points = [Q(i, 20) for i in range(21)]
        for degree in range(4):
            for _ in range(80):
                knots = sorted(rng.sample(
                    [Q(1, 4), Q(1, 2), Q(3, 4), Q(1), Q(5, 4),
                     Q(3, 2), Q(7, 4)], rng.randrange(0, 4)))
                full = [Q(0)]*(degree+1) + knots + [Q(2)]*(degree+1)
                controls = [Q(rng.randint(-10, 10), rng.randint(1, 9))
                            for _ in range(len(full)-degree-1)]
                source = {"degree": degree,
                          "knots": [str(x) for x in full],
                          "controls": [str(x) for x in controls]}
                at = str(rng.choice([Q(1, 8), Q(1, 3), Q(5, 6),
                                      Q(7, 6), Q(11, 8)]))
                refined, _ = insert_exact(source, at)
                before = bridge.spline_parse(source)
                after = bridge.spline_parse(refined)
                for t in points + knots + [core.fraction(at)]:
                    self.assertEqual(bridge.spline_value(before, t),
                                     bridge.spline_value(after, t))
                    checked += 1
        self.assertGreater(checked, 6000)


def contract():
    # The authentic frozen V44 check is inherited and must still execute.
    bridge.contract()
    rec = qualified_positive()
    need(rec["pre_edit_complete_events"]["physical_events"]
         ["physical_root_count"] == 1 and
         rec["post_edit_complete_events"]["physical_events"]
         ["physical_root_count"] == 1 and
         not rec["historical_corpus_knot_membership_claimed"],
         "REFINEMENT_CONTRACT_DRIFT")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("EXACT_KNOT_INSERTION_LINEAGE_CONTRACT_PASS")
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        need(result.wasSuccessful(), "SELF_TEST_FAILED")
    if not (args.contract or args.self_test):
        parser.error("select --contract or --self-test")
