#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-019"
CONTRACT_PATH = TASK / "ball-round-sweep-contract-v1.json"
IMPL_PATH = TASK / "ball_round_sweep.py"
EXPECTED_BASE = "dfda6423da5ae5d779b143e07c0ffe18c0925cd0"
EXPECTED_DEPS = {
    "MC-005": ("research/machining-completeness/tasks/MC-005/outcome.json", "adec886597a06345fdfdf65ee018596cd396d249", "CAPABILITY_ACCEPTED"),
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-058": ("research/machining-completeness/tasks/MC-058/outcome.json", "038fccda9142650ee7e29c626aeb8e4602420278", "COMPLETED_RESEARCH"),
}
EXPECTED_CONTROL = ("research/machining-completeness/tasks/MC-011/fixture_oracle.py", "6e1092976ec7c4379193c0ee6897578c3f0cddb7")


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def implementation():
    return load_module("mc019_ball_round_sweep", IMPL_PATH)


def independent_oracle():
    return load_module("mc011_fixture_oracle_for_mc019", ROOT / EXPECTED_CONTROL[0])


def validate_contract(c: dict, *, check_files: bool = True) -> None:
    assert c["schema"] == "radicadsac-mc019-ball-round-sweep/1.0"
    assert c["task"] == "MC-019" and c["issue"] == 81
    assert c["source_baseline"] == EXPECTED_BASE
    assert c["result"] == "COMPLETED_RESEARCH_BALL_ROUND_XYZ_SWEEP_CONSTRUCTION"
    assert c["native_execution"] is False
    deps = {d["task"]: d for d in c["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, sha, kind) in EXPECTED_DEPS.items():
        d = deps[task]
        assert (d["path"], d["blob_sha"], d["result_kind"]) == (path, sha, kind)
        if check_files:
            p = ROOT / path
            assert p.is_file() and blob_sha(p) == sha, f"dependency drift: {task}"

    ctl = c["independent_control"]
    assert (ctl["path"], ctl["blob_sha"]) == EXPECTED_CONTROL
    assert "not imported by the MC-019 implementation" in ctl["role"]
    if check_files:
        p = ROOT / ctl["path"]
        assert p.is_file() and blob_sha(p) == ctl["blob_sha"], "independent control drift"

    a = c["authority"]
    for key in ("fixed_axis", "saved_operation_is_immutable", "engagement_boundaries_are_authoritative", "retrace_is_not_deleted_from_journal", "binary_float_authority_forbidden", "global_epsilon_predicate_forbidden"):
        assert a[key] is True
    assert "closure(union" in a["sweep_semantics"]
    assert "exactly zero" in a["orientation_error_in_this_task"]

    cutter = c["cutter"]
    assert cutter["id"] == "mill_ball_round"
    assert cutter["complete_finite_cutting_region"] is True
    assert cutter["constant_z_projection_forbidden"] is True
    assert "rho^2+(z-R)^2<=R^2" in cutter["local_set"]
    assert "R<=z<=L" in cutter["local_set"]
    assert "c=R" in cutter["relation_to_mc018"]

    exact = c["exact_construction"]
    assert set(exact["source_classes"]) == {"stationary", "line", "polyline"}
    for key in ("varying_z_supported", "simultaneous_xyz_supported", "stationary_supported", "reversal_and_retrace_supported", "continuity_required", "engaged_teleportation_rejected", "equality_is_not_epsilonized"):
        assert exact[key] is True
    assert "3-D squared distance" in exact["lower_nose_algorithm"]
    assert "XY distance" in exact["upper_algorithm"]

    bounded = c["mc058_leaf_construction"]
    assert set(bounded["source_classes"]) == {"circular_arc", "helical_arc", "spline", "piecewise_motion", "timed_phase_motion"}
    assert bounded["classification"] == ["INSIDE", "OUTSIDE", "UNCERTIFIED"]
    assert bounded["uncertified_is_not_failure_or_pass"] is True
    assert bounded["missing_or_unbound_leaf_certificate_is_rejected"] is True
    assert bounded["topology_or_exact_zero_claim_implied"] is False
    assert "R+e" in bounded["outer_rule"] and "R/2-e" in bounded["inner_rule"]

    f03 = c["boundary_controls"]["simultaneous_xyz_f03_style"]
    assert f03["independent_oracle"].startswith("MC-011 F03")
    assert f03["tip_path"][1][2] != f03["flattened_z_corruption_tip_path"][1][2]

    forbidden = set(c["forbidden"])
    required = {
        "CENTRELINE_ONLY_SWEEP", "BALL_NOSE_REPLACED_BY_FLAT_CYLINDER", "DROP_VARYING_Z", "CONSTANT_Z_PROJECTION",
        "DELETE_RETRACE_FROM_SOURCE_JOURNAL", "ENGAGED_TELEPORTATION", "BINARY_FLOAT_OR_GLOBAL_EPSILON_EQUALITY",
        "TREAT_MC058_TRANSLATION_ERROR_AS_ZERO", "UNBOUND_NONLINEAR_LEAF", "PROMOTE_UNCERTIFIED_TO_INSIDE_OR_OUTSIDE",
        "REUSE_CANDIDATE_GEOMETRY_AS_INDEPENDENT_ORACLE", "PROMOTE_MODEL_EVIDENCE_TO_NATIVE_GEOMETRY", "PREMATURE_MC_B_ACCEPTANCE"
    }
    assert required <= forbidden
    pb = c["proof_boundary"]
    assert pb["MC-B"] == "NOT_ESTABLISHED" and pb["MC-1"] == "NOT_ESTABLISHED"
    assert pb["PO-02"].startswith("OPEN") and pb["PO-04"].startswith("OPEN") and pb["PO-05"].startswith("OPEN") and pb["PO-06"].startswith("OPEN")


def run_controls() -> None:
    m = implementation()
    for bad in (1.0, True):
        try: m.q(bad)
        except TypeError: pass
        else: raise AssertionError("binary/bool authority input accepted")

    try: m.BallRoundEndMill.make(1, "1/2")
    except ValueError: pass
    else: raise AssertionError("ball/round cutter shorter than nose radius accepted")

    tool = m.BallRoundEndMill.make(1, 3)
    stationary = m.Leaf.make((0,0,0), (0,0,0), source_class="stationary")
    tangent = ("3/5",0,"1/5")
    assert m.exact_sweep_contains(tangent, tool, [stationary])
    assert m.exact_sweep_contains(("59/100",0,"1/5"), tool, [stationary])
    assert not m.exact_sweep_contains(("61/100",0,"1/5"), tool, [stationary])
    assert Fraction(3,5)**2 + (Fraction(1,5)-1)**2 == 1

    assert m.exact_sweep_contains((0,0,0), tool, [stationary])
    assert not m.exact_sweep_contains((0,0,"-1/100"), tool, [stationary])
    assert m.exact_sweep_contains((0,0,3), tool, [stationary])
    assert not m.exact_sweep_contains((0,0,"301/100"), tool, [stationary])
    assert m.cylinder_segment_contains(("9/10",0,"1/10"), m.Cylinder(Fraction(1), Fraction(0), Fraction(3)), stationary.p0, stationary.p1)
    assert not m.ball_round_segment_contains(("9/10",0,"1/10"), tool, stationary.p0, stationary.p1)

    varying = m.Leaf.make((0,0,0), (2,0,-2))
    p_tan, p_in, p_out = ("1/3","1/3","-2/3"), ("1/3","3/10","-2/3"), ("1/3","2/5","-2/3")
    assert m.exact_sweep_contains(p_tan, tool, [varying])
    assert m.exact_sweep_contains(p_in, tool, [varying])
    assert not m.exact_sweep_contains(p_out, tool, [varying])
    flattened = m.Leaf.make((0,0,0), (2,0,0))
    assert not m.exact_sweep_contains(p_tan, tool, [flattened]), "constant-Z projection corruption survived"

    oracle = independent_oracle()
    centre_path = ((0,0,1),(2,0,-1))
    for point, expected in ((p_tan, True), (p_in, True), (p_out, False)):
        assert oracle.ball_polyline_sweep_removes(point, centre_path, 1) is expected
        assert m.exact_sweep_contains(point, tool, [varying]) is expected

    fwd = m.swept_path((m.Leaf.make((0,0,0),(2,0,-2)),))
    retrace = m.swept_path((m.Leaf.make((0,0,0),(2,0,-2)), m.Leaf.make((2,0,-2),(0,0,0))))
    assert len(retrace) == 2
    probes = [("1/3","1/3","-2/3"),("1/3","2/5","-2/3"),(0,0,0),(2,0,-2),(1,0,1)]
    assert [m.exact_sweep_contains(x, tool, fwd) for x in probes] == [m.exact_sweep_contains(x, tool, retrace) for x in probes]

    try: m.swept_path((m.Leaf.make((0,0,0),(1,0,0)), m.Leaf.make((2,0,0),(3,0,0))))
    except ValueError: pass
    else: raise AssertionError("engaged teleportation accepted")

    bad_leaf = m.Leaf.make((0,0,0),(1,0,0), translation_error="1/10", source_class="spline", engagement_bound=False)
    try: m.certified_classify((0,0,0), tool, [bad_leaf])
    except ValueError: pass
    else: raise AssertionError("unbound nonlinear leaf accepted")

    zero_spline = m.Leaf.make((0,0,0),(2,0,0), translation_error=0, source_class="spline")
    try: m.exact_sweep_contains((1,0,1), tool, [zero_spline])
    except ValueError: pass
    else: raise AssertionError("nonlinear source accepted by exact-line path")
    assert m.certified_classify((1,0,1), tool, [zero_spline]) == "INSIDE"
    assert m.certified_classify((1,"3/4","1/10"), tool, [zero_spline]) == "UNCERTIFIED"

    try: m.Leaf.make((0,0,0),(1,0,0), source_class="invented_curve")
    except ValueError: pass
    else: raise AssertionError("unknown source class accepted")

    leaf = m.Leaf.make((0,0,0),(2,0,0), translation_error="1/10", source_class="circular_arc")
    assert m.certified_classify((1,0,1), tool, [leaf]) == "INSIDE"
    assert m.certified_classify((1,2,1), tool, [leaf]) == "OUTSIDE"
    assert m.certified_classify((1,"21/20",1), tool, [leaf]) == "UNCERTIFIED"

    huge = m.Leaf.make((0,0,0),(2,0,0), translation_error="3/2", source_class="spline")
    assert m.certified_classify((1,0,1), tool, [huge]) == "UNCERTIFIED"


def adversarial_contract_tests(c: dict) -> None:
    def reject(mutator):
        x = copy.deepcopy(c); mutator(x)
        try: validate_contract(x, check_files=False)
        except (AssertionError, KeyError): return
        raise AssertionError("adversarial contract mutation was accepted")

    reject(lambda x: x["authority"].__setitem__("binary_float_authority_forbidden", False))
    reject(lambda x: x["authority"].__setitem__("retrace_is_not_deleted_from_journal", False))
    reject(lambda x: x["cutter"].__setitem__("constant_z_projection_forbidden", False))
    reject(lambda x: x["exact_construction"].__setitem__("varying_z_supported", False))
    reject(lambda x: x["exact_construction"].__setitem__("simultaneous_xyz_supported", False))
    reject(lambda x: x["mc058_leaf_construction"].__setitem__("classification", ["INSIDE","OUTSIDE"]))
    reject(lambda x: x["mc058_leaf_construction"].__setitem__("topology_or_exact_zero_claim_implied", True))
    reject(lambda x: x["proof_boundary"].__setitem__("MC-B", "ACCEPTED"))
    reject(lambda x: x["forbidden"].remove("BALL_NOSE_REPLACED_BY_FLAT_CYLINDER"))
    reject(lambda x: x["formal_dependencies"][2].__setitem__("blob_sha", "0"*40))
    reject(lambda x: x["independent_control"].__setitem__("blob_sha", "0"*40))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--contract", action="store_true"); ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    c = load(CONTRACT_PATH)
    validate_contract(c)
    run_controls()
    if args.self_test:
        adversarial_contract_tests(c)
    print("MC-019 ball/round simultaneous-XYZ sweep contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
