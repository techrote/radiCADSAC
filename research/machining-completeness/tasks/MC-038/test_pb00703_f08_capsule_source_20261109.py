#!/usr/bin/env python3
"""Original MC-012 F08 physical oracle vs independent exact curved-source lowering."""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
from pathlib import Path
import random
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research/machining-completeness/tasks/MC-012"))
import pb00703_f08_capsule_source_20261109 as candidate  # noqa: E402
import pb00703_source_codec as codec  # noqa: E402
import fixture_oracle as oracle  # noqa: E402

ORACLE_BLOB = "2f0c7f5ff91ce9f82b591267d3ba1b3070c34e54"
CODEC_BLOB = "87429f3aa42692222287e62762d08c01b989a61c"


def git_blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def checked_dependencies():
    for path, sha in ((ROOT / candidate.FIXTURE_PATH, candidate.FIXTURE_BLOB),
                      (ROOT / "research/machining-completeness/tasks/MC-012/fixture_oracle.py", ORACLE_BLOB),
                      (ROOT / "research/machining-completeness/tasks/MC-038/pb00703_source_codec.py", CODEC_BLOB)):
        assert git_blob(path.read_bytes()) == sha, f"protected source changed: {path}"


def member(source, point):
    verdict = codec.classify_certifying_point(source, point)
    assert verdict["status"] == "EXACT_NOMINAL"
    if verdict["relation"] == "OUTSIDE" and "closed_predicate_membership" not in verdict:
        return False
    return verdict["closed_predicate_membership"]


class SourceProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        checked_dependencies()
        cls.fixture, cls.sources, cls.margin = candidate.load_original_f08(ROOT)
        cls.f08 = next(f for f in cls.fixture["families"] if f["id"] == "F08")
        cls.access, cls.slot = cls.f08["operations"]

    def test_original_source_authentication_and_nominal_codec(self):
        self.assertEqual(self.margin, Fraction(1, 2))
        self.assertEqual(set(self.sources), {"F08-ACCESS", "F08-TSLOT"})
        for sid, source in self.sources.items():
            self.assertEqual(source["role"], "cutting")
            self.assertEqual(source["units"], "mm")
            self.assertIn(candidate.FIXTURE_BLOB, source["source_id"])
            self.assertEqual(codec.classify_source_descriptor(source)["status"], "EXACT_NOMINAL_SOURCE")
            self.assertEqual(len(codec.source_sha256(source)), 64)
            self.assertEqual(source["schema"], codec.SCHEMA)
        self.assertNotEqual(codec.source_sha256(self.sources["F08-ACCESS"]),
                            codec.source_sha256(self.sources["F08-TSLOT"]))

    def test_direct_adapter_original_identity_forgery_regression(self):
        original, original_margin = candidate.lower_f08_operations(copy.deepcopy(self.fixture))
        self.assertEqual(original_margin, Fraction(1, 2))
        for operation in ("F08-ACCESS", "F08-TSLOT"):
            self.assertEqual(original[operation]["source_id"],
                             f"MC-012:{operation}:{candidate.FIXTURE_BLOB}")
            self.assertEqual(original[operation]["source_id"], self.sources[operation]["source_id"])
        # Reordering map keys cannot silently change semantic source identity.
        reordered = dict(reversed(list(self.fixture.items())))
        reordered_sources, _ = candidate.lower_f08_operations(reordered)
        for operation in original:
            self.assertEqual(reordered_sources[operation]["source_id"],
                             original[operation]["source_id"])

        changed = copy.deepcopy(self.fixture)
        changed_slot = next(f for f in changed["families"] if f["id"] == "F08")["operations"][1]
        self.assertEqual(changed_slot["head_radius"], "3")
        changed_slot["head_radius"] = "13/4"
        altered, margin = candidate.lower_f08_operations(changed)
        self.assertEqual(margin, Fraction(1, 4))
        point = [Fraction(15), Fraction(105, 8), Fraction(5)]
        self.assertEqual(Fraction(25, 8) ** 2, Fraction(625, 64))
        self.assertLess(Fraction(3) ** 2, Fraction(625, 64))
        self.assertGreater(Fraction(13, 4) ** 2, Fraction(625, 64))
        self.assertFalse(member(original["F08-TSLOT"], point))
        self.assertTrue(member(altered["F08-TSLOT"], point))
        self.assertFalse(oracle.t_slot_sweep_removes(
            point, self.slot["path_xy"], self.slot["head_radius"], self.slot["head_z"],
            self.slot["neck_radius"], self.slot["neck_z"]))
        self.assertTrue(oracle.t_slot_sweep_removes(
            point, changed_slot["path_xy"], changed_slot["head_radius"], changed_slot["head_z"],
            changed_slot["neck_radius"], changed_slot["neck_z"]))
        digest = hashlib.sha256(candidate._canonical_fixture_bytes(changed)).hexdigest()
        for operation in original:
            self.assertEqual(altered[operation]["source_id"],
                             f"PB-007-03:derived-canonical-sha256:{digest}:{operation}")
            self.assertNotEqual(altered[operation]["source_id"],
                                original[operation]["source_id"])
            self.assertEqual(codec.classify_source_descriptor(altered[operation])["status"],
                             "EXACT_NOMINAL_SOURCE")
        self.assertNotEqual(codec.source_sha256(altered["F08-TSLOT"]),
                            codec.source_sha256(original["F08-TSLOT"]))
        replay, _ = candidate.lower_f08_operations(copy.deepcopy(changed))
        self.assertEqual(replay["F08-TSLOT"]["source_id"], altered["F08-TSLOT"]["source_id"])
        changed["families"][0]["title"] += " changed outside F08"
        independent_change, _ = candidate.lower_f08_operations(changed)
        self.assertNotEqual(independent_change["F08-TSLOT"]["source_id"],
                            altered["F08-TSLOT"]["source_id"])
        for fixture in (self.fixture, changed):
            for asserted in (candidate.FIXTURE_BLOB, "forged-source"):
                with self.assertRaises(candidate.InvalidSource):
                    candidate.lower_f08_operations(fixture, provenance=asserted)

    def test_actual_original_physical_witnesses(self):
        slot = self.sources["F08-TSLOT"]
        assertions = self.f08["oracle_assertions"]
        for key in ("undercut_shadow", "roof_survivor", "neck_slot"):
            witness = assertions[key]
            self.assertEqual(member(slot, witness["point"]), witness["full_tslot_removed"], key)
        self.assertTrue(member(self.sources["F08-ACCESS"], ["5", "10", "8"]))
        a = assertions["access"]
        self.assertTrue(oracle.t_slot_accessible(a["radius"], a["head_radius"], a["neck_radius"]))
        self.assertFalse(oracle.t_slot_accessible(a["too_small_access_radius"], a["head_radius"], a["neck_radius"]))
        self.assertEqual(candidate.q(a["radius"]) - candidate.q(a["head_radius"]), self.margin)

    def test_exact_random_points_vs_independent_original_oracle(self):
        rng = random.Random(0xF0803)
        slot = self.slot
        for i in range(1400):
            p = [Fraction(rng.randrange(0, 30001), 1000),
                 Fraction(rng.randrange(0, 20001), 1000),
                 Fraction(rng.randrange(0, 14001), 1000)]
            expected_slot = oracle.t_slot_sweep_removes(
                p, slot["path_xy"], slot["head_radius"], slot["head_z"], slot["neck_radius"], slot["neck_z"])
            expected_access = oracle.finite_cylinder_contains(
                p, "z", self.access["center"], self.access["axial_interval"], self.access["radius"])
            self.assertEqual(member(self.sources["F08-TSLOT"], p), expected_slot, (i, p))
            self.assertEqual(member(self.sources["F08-ACCESS"], p), expected_access, (i, p))

    def test_exact_contacts_microneighbours_and_rounded_end(self):
        eps = Fraction(1, 1000000)
        slot = self.sources["F08-TSLOT"]
        for y, z in ((Fraction(13), 5), (Fraction(11), 8)):
            exact = [Fraction(15), y, Fraction(z)]
            self.assertTrue(member(slot, exact))
            self.assertTrue(member(slot, [15, y - eps, z]))
            self.assertFalse(member(slot, [15, y + eps, z]))
            self.assertEqual(codec.classify_certifying_point(slot, exact)["relation"], "BOUNDARY_CANDIDATE")
        self.assertTrue(member(slot, [28, 10, 5]))
        self.assertFalse(member(slot, [28 + eps, 10, 5]))
        self.assertFalse(member(slot, [28, 13, 5]))
        self.assertFalse(member(slot, [15, Fraction(25, 2), 8]))

    def test_general_polyline_reverse_and_retrace(self):
        path = [["0", "0"], ["3", "0"], ["3", "4"]]
        solid, bounds = candidate.swept_disk_path(path, "1/2", ["0", "1"])
        src = candidate.make_source("prospective-polyline", solid, bounds)
        bs, bb = candidate.swept_disk_path(list(reversed(path)), "1/2", ["1", "0"])
        back = candidate.make_source("prospective-polyline-back", bs, bb)
        rs, rb = candidate.swept_disk_path(path + list(reversed(path)), "1/2", ["0", "1"])
        retrace = candidate.make_source("prospective-polyline-retrace", rs, rb)
        rng = random.Random(1605)
        for i in range(450):
            pt = [Fraction(rng.randrange(-20, 61), 10),
                  Fraction(rng.randrange(-20, 61), 10), Fraction(1, 2)]
            distance2 = min(oracle.distance2_point_segment_2d(pt[:2], a, b)
                            for a, b in zip(path, path[1:]))
            expected = distance2 <= Fraction(1, 4)
            self.assertEqual(member(src, pt), expected, (i, pt))
            self.assertEqual(member(back, pt), expected)
            self.assertEqual(member(retrace, pt), expected)
        self.assertNotEqual(codec.source_sha256(src), codec.source_sha256(back))
        ds, db = candidate.swept_disk_path([["0", "0"], ["0", "0"]], "1", ["0", "2"])
        self.assertTrue(member(candidate.make_source("stationary", ds, db), ["1", "0", "1"]))

    def test_no_convex_hull_or_bounding_box_shortcut(self):
        slot = self.sources["F08-TSLOT"]
        for p in (["15", "13", "8"], ["27", "13", "5"], ["2", "13", "5"]):
            self.assertFalse(member(slot, p))
        self.assertTrue(member(slot, ["15", "12", "5"]))
        self.assertTrue(member(slot, ["15", "10", "8"]))
        self.assertEqual(slot["bounds"]["x"], ["2/1", "28/1"])

    def test_source_uncertainty_and_binding_fail_closed(self):
        src = copy.deepcopy(self.sources["F08-TSLOT"])
        original = codec.source_sha256(src)
        src["source_uncertainty"] = "1/1000000"
        self.assertEqual(codec.classify_certifying_point(src, ["15", "10", "5"])["status"], "UNCERTIFIED_SOURCE")
        self.assertNotEqual(codec.source_sha256(src), original)
        src["source_uncertainty"] = "0"
        src["role"] = "holder"
        self.assertNotEqual(codec.source_sha256(src), original)
        src["role"] = "cutting"
        src["frame_id"] = "other-setup"
        self.assertNotEqual(codec.source_sha256(src), original)
        src["frame_id"] = "F08:S-F08:common"
        src["solid"] = {"op": "opaque_STEP", "import_success": True}
        self.assertEqual(codec.classify_source_descriptor(src)["status"], "SEMANTIC_BLOCKER")

    def test_invalid_source_vs_open_resource_or_degenerate_grammar(self):
        with self.assertRaises(candidate.InvalidSource):
            candidate.swept_disk_path([["0", "0"], [1.5, "0"]], "1", ["0", "1"])
        with self.assertRaises(candidate.InvalidSource):
            candidate.swept_disk_path([["0", "0"], ["1", "0"]], "-1", ["0", "1"])
        with self.assertRaises(candidate.OpenSource):
            candidate.swept_disk_path([[str(i), "0"] for i in range(66)], "1", ["0", "1"])
        with self.assertRaises(candidate.OpenSource):
            candidate.swept_disk_path([["0", "0"], [str(2**1030), "0"]], "1", ["0", "1"])
        with self.assertRaises(candidate.OpenSource):
            candidate.swept_disk_path([["0", "0"], ["1", "0"]], "0", ["0", "1"])
        with self.assertRaises(candidate.OpenSource):
            candidate.swept_disk_path([["0", "0"], ["1", "0"]], "1", ["0", "0"])
        bad = copy.deepcopy(self.fixture)
        bad["families"][-1]["operations"][1]["kind"] = "unreviewed_motion"
        with self.assertRaises(candidate.OpenSource):
            candidate.lower_f08_operations(bad)
        bad = copy.deepcopy(self.fixture)
        bad["families"][-1]["operations"].reverse()
        with self.assertRaises(candidate.InvalidSource):
            candidate.lower_f08_operations(bad)

    def test_original_fixture_mutation_fails_identity_check(self):
        raw = (ROOT / candidate.FIXTURE_PATH).read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / candidate.FIXTURE_PATH
            dest.parent.mkdir(parents=True)
            dest.write_bytes(raw)
            self.assertEqual(candidate.load_original_f08(Path(folder))[2], Fraction(1, 2))
            changed = raw.replace(b'"head_radius": "3"', b'"head_radius": "4"', 1)
            self.assertNotEqual(raw, changed)
            dest.write_bytes(changed)
            with self.assertRaises(candidate.InvalidSource):
                candidate.load_original_f08(Path(folder))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--contract", action="store_true")
    args = p.parse_args()
    if not (args.self_test or args.contract):
        p.error("provide --self-test or --contract")
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(SourceProofTests)
    sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful() else 1)
