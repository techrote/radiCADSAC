#!/usr/bin/env python3
"""Independent exact-rational PB-007-03 source/frame controls incl original MC-012 F07."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys
import unittest

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
MC012 = ROOT / "research" / "machining-completeness" / "tasks" / "MC-012"
sys.path.insert(0, str(TASK))
sys.path.insert(0, str(MC012))
import pb00703_rigid_pose_20261109 as posecodec
import pb00703_source_codec as v4
import fixture_oracle as physical

F07_BLOB = "8bb04fd5c643d02c42d2b58e49192ddb346b5b3f"
ORACLE_BLOB = "2f0c7f5ff91ce9f82b591267d3ba1b3070c34e54"
V4_BLOB = "87429f3aa42692222287e62762d08c01b989a61c"


def git_blob(path):
    b = path.read_bytes()
    return hashlib.sha1(("blob %d\0" % len(b)).encode()+b).hexdigest()


def source(solid, role="cutting", uncertainty="0"):
    return {
        "schema": v4.SCHEMA, "source_id": "local-source-01",
        "role": role, "units": "mm", "frame_id": "machine",
        "bounds": {"x": ["-5", "5"], "y": ["-5", "5"], "z": ["-5", "5"]},
        "solid": solid, "source_uncertainty": uncertainty,
    }


def rotation():
    return {
        "matrix": [["3/5", "-4/5", "0"], ["4/5", "3/5", "0"], ["0", "0", "1"]],
        "translation": ["2/3", "-7/5", "1/9"],
        "source_frame": "machine", "target_frame": "workpiece",
    }


def exact_inverse(pose, point):
    R = [[Q(v) for v in row] for row in pose["matrix"]]
    t = [Q(v) for v in pose["translation"]]
    return [sum((R[j][i]*(Q(point[j])-t[j]) for j in range(3)), Q(0))
            for i in range(3)]


def exact_forward(pose, point):
    R = [[Q(v) for v in row] for row in pose["matrix"]]
    t = [Q(v) for v in pose["translation"]]
    return [t[i]+sum((R[i][j]*Q(point[j]) for j in range(3)), Q(0))
            for i in range(3)]


def f07_original():
    corpus_path = MC012 / "physical-corpus-f05-f08-v1.json"
    assert git_blob(corpus_path) == F07_BLOB, "original F07 fixture source mutated"
    assert git_blob(MC012 / "fixture_oracle.py") == ORACLE_BLOB, "original independent oracle mutated"
    assert git_blob(TASK / "pb00703_source_codec.py") == V4_BLOB, "accepted v4 codec mutated"
    corpus = json.loads(corpus_path.read_text())
    f07 = next(v for v in corpus["families"] if v["id"] == "F07")
    op = next(v for v in f07["operations"] if v["id"] == "F07-M1")
    setup = next(v for v in f07["setups"] if v["id"] == op["setup"])
    assert op["axis_common"] == "x" and setup["machine_plus_z_maps_common"] == "+X"
    R = setup["common_from_machine"]["matrix"]
    p = {"matrix": R, "translation": ["0", "0", "0"],
         "source_frame": "machine", "target_frame": "common"}
    assert physical.is_rotation_matrix(R)
    common_c = [Q(0), Q(op["center_common_yz"][0]), Q(op["center_common_yz"][1])]
    local_c = exact_inverse(p, common_c)
    assert local_c[1] == 0
    radius = Q(op["radius"])
    lo, hi = [Q(x) for x in op["axial_interval_common"]]
    assert lo < hi
    # Derive machine-frame cutter from original source operation, not a synthetic
    # alternative expected truth. Positive witness is the original F07-M1 mill.
    c0, c1 = local_c[:2]
    radial = {
        "op": "poly_le",
        "terms": [
            {"coefficient": str(x), "exponents": e}
            for x, e in [
                (Q(1), [2, 0, 0]), (Q(1), [0, 2, 0]),
                (-2*c0, [1, 0, 0]), (-2*c1, [0, 1, 0]),
                (c0*c0+c1*c1-radius*radius, [0, 0, 0]),
            ]
            if x
        ],
    }
    solid = {
        "op": "intersection",
        "children": [radial, v4.linear_le(2, -1, lo), v4.linear_le(2, 1, -hi)]
    }
    cutter = source(solid)
    cutter["source_id"] = "MC-012/F07-M1/cutting-local"
    cutter["bounds"] = {
        "x": [str(c0-radius-1), str(c0+radius+1)],
        "y": [str(c1-radius-1), str(c1+radius+1)],
        "z": [str(lo-1), str(hi+1)],
    }
    return f07, op, cutter, p


class ExactRigidPoseTest(unittest.TestCase):
    def test_01_original_f07_and_independent_oracle(self):
        f07, op, src, p = f07_original()
        out, receipt = posecodec.lower_exact_source(src, p, "F07-M1/common/cutting")
        self.assertTrue(posecodec.verify_exact_receipt(src, p, "F07-M1/common/cutting", out, receipt))
        self.assertEqual(out["role"], "cutting")
        self.assertEqual(out["frame_id"], "common")
        self.assertEqual(receipt["original_sha256"], v4.source_sha256(src))
        self.assertFalse(receipt["access_certified"])
        cases = f07["oracle_assertions"]["broken_symmetry"]
        for name, truth in [("removed_point", True), ("same_radius_survivor", False)]:
            point = cases[name]
            self.assertEqual(physical.finite_cylinder_contains(point, op["axis_common"],
                op["center_common_yz"], op["axial_interval_common"], op["radius"]), truth)
            self.assertEqual(v4.classify_nominal_point(out, point)["closed_predicate_membership"], truth)
        # Original cylindrical boundary and exact signed 1/1e6 perturbations.
        eps = Q(1, 1000000)
        for yy, expected in [(Q(3)-eps, True), (Q(3), True), (Q(3)+eps, False)]:
            pt = [Q(17), yy, Q(30)]
            self.assertEqual(physical.finite_cylinder_contains(pt, "x", [0,30], [14,22], 3), expected)
            self.assertEqual(v4.classify_nominal_point(out, pt)["closed_predicate_membership"], expected)
        rng = random.Random(700703)
        for _ in range(800):
            pt = [Q(rng.randint(-250, 250),10), Q(rng.randint(-250,250),10),
                  Q(rng.randint(-10, 700),10)]
            expected = physical.finite_cylinder_contains(pt, op["axis_common"],
                        op["center_common_yz"], op["axial_interval_common"], op["radius"])
            actual = v4.classify_nominal_point(out, pt)["closed_predicate_membership"] if "closed_predicate_membership" in v4.classify_nominal_point(out, pt) else False
            self.assertEqual(actual, expected, pt)

    def test_02_generic_nonconvex_difference_complement_exact(self):
        L = {"op": "union", "children": [v4.box_solid(0, 2, 0, 1, 0, 1),
                                      v4.box_solid(0, 1, 0, 2, 0, 1)]}
        solid = {"op": "difference", "left": L,
                 "right": {"op": "intersection", "children": [
                     v4.box_solid("1/4", "1/2", "1/4", "1/2", 0, 1),
                     {"op": "complement", "child": v4.box_solid(3, 4, 3, 4, 3, 4)}
                 ]}}
        src = source(solid, "stock")
        transformed, receipt = posecodec.lower_exact_source(src, rotation(), "stock-reclamped")
        self.assertEqual(receipt["role"], "stock")
        r = random.Random(319)
        for _ in range(340):
            local = [Q(r.randrange(-10, 30),10), Q(r.randrange(-10, 30),10),
                     Q(r.randrange(-10, 20),10)]
            world = exact_forward(rotation(), local)
            baseline = v4.classify_nominal_point(src, local)
            remapped = v4.classify_nominal_point(transformed, world)
            self.assertEqual(baseline.get("closed_predicate_membership", False),
                             remapped.get("closed_predicate_membership", False))
        # Reentrant quadrant cannot be filled by convex hull or bounds.
        for local, truth in [([Q(3,2),Q(3,2),Q(1,2)], False),
                             ([Q(3,2),Q(1,2),Q(1,2)], True),
                             ([Q(3,8),Q(3,8),Q(1,2)], False)]:
            world = exact_forward(rotation(), local)
            self.assertEqual(v4.classify_nominal_point(transformed, world).get(
                             "closed_predicate_membership",False), truth)

    def test_03_any_role_and_nonzero_uncertainty(self):
        for role in ("stock", "cutting", "holder"):
            src = source(v4.unit_sphere_solid(), role, "1/1000000")
            transformed, receipt = posecodec.lower_exact_source(src, rotation(), role+"-posed")
            self.assertEqual(receipt["role"], role)
            self.assertEqual(receipt["source_uncertainty"], "1/1000000")
            self.assertFalse(receipt["access_certified"])
            self.assertEqual(v4.classify_certifying_point(transformed,
                exact_forward(rotation(), [0,0,0]))["status"], "UNCERTIFIED_SOURCE")
            self.assertFalse(posecodec.attempt(src, rotation(), role+"-posed")["certifying_exactness"])

    def test_04_forged_receipt_output_source_pose_and_metadata(self):
        src = source(v4.unit_sphere_solid())
        p = rotation()
        out, rec = posecodec.lower_exact_source(src, p, "posed")
        self.assertTrue(posecodec.verify_exact_receipt(src, p, "posed", out, rec))
        for change in ("output", "receipt", "role", "pose", "frame", "source_id"):
            oo, rr, ss, pp = deepcopy(out), deepcopy(rec), deepcopy(src), deepcopy(p)
            if change == "output": oo["solid"] = v4.box_solid(-1,1,-1,1,-1,1)
            if change == "receipt": rr["access_certified"] = True
            if change == "role": ss["role"] = "holder"
            if change == "pose": pp["translation"][0] = "1"
            if change == "frame": oo["frame_id"] = "unbound"
            if change == "source_id": rr["original_source_id"] = "other"
            with self.assertRaises(ValueError, msg=change):
                posecodec.verify_exact_receipt(ss, pp, "posed", oo, rr)

    def test_05_bad_geometry_rejected_without_epsilon(self):
        src = source(v4.unit_sphere_solid())
        for mutation in ("mirror", "skew", "float", "translation_float", "missing_frame", "extra", "near_orthogonal"):
            p = rotation()
            if mutation == "mirror": p["matrix"] = [["-1","0","0"],["0","1","0"],["0","0","1"]]
            if mutation == "skew": p["matrix"] = [["1","1","0"],["0","1","0"],["0","0","1"]]
            if mutation == "float": p["matrix"][0][0] = 0.6
            if mutation == "translation_float": p["translation"][2] = 0.0
            if mutation == "missing_frame": p["source_frame"] = "different"
            if mutation == "extra": p["approximate"] = True
            if mutation == "near_orthogonal": p["matrix"][0][0] = "600000000000000001/1000000000000000000"
            self.assertEqual(posecodec.attempt(src, p, "posed")["status"],
                             "SEMANTIC_BLOCKER", mutation)

    def test_06_open_resource_budget_not_invalid_domain(self):
        highdegree = source({"op": "poly_le", "terms": [
            {"coefficient": "1", "exponents": [13,0,0]},
            {"coefficient": "-1", "exponents": [0,0,0]}]})
        result = posecodec.attempt(highdegree, rotation(), "posed")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["blocker"], "PB-007-03")
        self.assertEqual(result["reason"], "RESOURCE_BUDGET_OPEN")
        self.assertEqual(posecodec.attempt(source(v4.unit_sphere_solid()), rotation(),
            "local-source-01")["status"], "SEMANTIC_BLOCKER")

    def test_07_exact_identity_and_inverse_rotation(self):
        src = source(v4.unit_sphere_solid())
        identity = {"matrix":[["1","0","0"],["0","1","0"],["0","0","1"]],
                    "translation":["0","0","0"], "source_frame":"machine", "target_frame":"common"}
        out, rec = posecodec.lower_exact_source(src, identity, "ident")
        for x in ("-1000001/1000000", "-1", "0", "1", "1000001/1000000"):
            expected = v4.classify_nominal_point(src,[x,0,0]).get("closed_predicate_membership",False)
            actual = v4.classify_nominal_point(out,[x,0,0]).get("closed_predicate_membership",False)
            self.assertEqual(expected, actual)
        self.assertEqual(rec["output_sha256"], v4.source_sha256(out))

    def test_08_opaque_sources_and_invalid_rationals_fail_closed(self):
        src = source(v4.unit_sphere_solid())
        for bad in ({"format":"STEP","path":"unreviewed.step"}, None, [], {"schema":"opaque"}):
            self.assertNotEqual(posecodec.attempt(bad, rotation(), "posed")["status"],
                                "EXACT_NOMINAL_SOURCE")
        src["solid"]["terms"][0]["coefficient"] = 0.1
        self.assertEqual(posecodec.attempt(src, rotation(), "posed")["status"], "SEMANTIC_BLOCKER")


if __name__ == "__main__":
    if sys.argv[1:] != ["--self-test"]:
        raise SystemExit("usage: python3 test_pb00703_rigid_pose_20261109.py --self-test")
    unittest.main(argv=[sys.argv[0]], verbosity=2)
