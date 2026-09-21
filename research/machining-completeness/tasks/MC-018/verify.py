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
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-018"
CONTRACT_PATH = TASK / "fixed-axis-sweep-contract-v1.json"
IMPL_PATH = TASK / "fixed_axis_sweep.py"
EXPECTED_BASE = "b85b8081dd83ca35f81e6e1a9495bd5f88589ee0"
EXPECTED_DEPS = {
    "MC-005": ("research/machining-completeness/tasks/MC-005/outcome.json", "adec886597a06345fdfdf65ee018596cd396d249", "CAPABILITY_ACCEPTED"),
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-058": ("research/machining-completeness/tasks/MC-058/outcome.json", "038fccda9142650ee7e29c626aeb8e4602420278", "COMPLETED_RESEARCH"),
}


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def implementation():
    spec = importlib.util.spec_from_file_location("mc018_fixed_axis_sweep", IMPL_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def validate_contract(c: dict, *, check_files: bool = True) -> None:
    assert c["schema"] == "radicadsac-mc018-fixed-axis-sweep/1.0"
    assert c["task"] == "MC-018" and c["issue"] == 80
    assert c["source_baseline"] == EXPECTED_BASE
    assert c["result"] == "COMPLETED_RESEARCH_FIXED_AXIS_SWEEP_CONSTRUCTION"
    assert c["native_execution"] is False
    deps = {d["task"]: d for d in c["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, sha, kind) in EXPECTED_DEPS.items():
        d = deps[task]
        assert (d["path"], d["blob_sha"], d["result_kind"]) == (path, sha, kind)
        if check_files:
            p = ROOT / path
            assert p.is_file() and blob_sha(p) == sha, f"dependency drift: {task}"

    a = c["authority"]
    for key in ("fixed_axis", "saved_operation_is_immutable", "engagement_boundaries_are_authoritative", "retrace_is_not_deleted_from_journal", "binary_float_authority_forbidden", "global_epsilon_predicate_forbidden"):
        assert a[key] is True
    assert "closure(union" in a["sweep_semantics"]
    assert "exactly zero" in a["orientation_error_in_this_task"]

    cutters = c["cutters"]
    assert set(cutters) == {"mill_flat_end", "mill_corner_radius"}
    assert "x^2+y^2 <= R^2" in cutters["mill_flat_end"]["local_set"]
    assert "4*a^2*rho^2" in cutters["mill_corner_radius"]["local_set"]
    assert cutters["mill_corner_radius"]["ball_round_excluded_to"] == "MC-019"

    exact = c["exact_construction"]
    assert set(exact["source_classes"]) == {"stationary", "line", "polyline"}
    for key in ("varying_z_supported", "stationary_supported", "reversal_and_retrace_supported", "continuity_required", "engaged_teleportation_rejected", "equality_is_not_epsilonized"):
        assert exact[key] is True
    assert "Sturm" in exact["corner_algorithm"]

    bounded = c["mc058_leaf_construction"]
    assert set(bounded["source_classes"]) == {"circular_arc", "helical_arc", "spline", "piecewise_motion", "timed_phase_motion"}
    assert bounded["classification"] == ["INSIDE", "OUTSIDE", "UNCERTIFIED"]
    assert bounded["uncertified_is_not_failure_or_pass"] is True
    assert bounded["missing_or_unbound_leaf_certificate_is_rejected"] is True
    assert bounded["topology_or_exact_zero_claim_implied"] is False
    assert "R+e" in bounded["outer_rule"] and "core_radius-e" in bounded["inner_rule"]

    forbidden = set(c["forbidden"])
    required = {
        "CENTRELINE_ONLY_SWEEP", "CORNER_RADIUS_REPLACED_BY_FLAT_CYLINDER", "DROP_VARYING_Z",
        "DELETE_RETRACE_FROM_SOURCE_JOURNAL", "ENGAGED_TELEPORTATION", "BINARY_FLOAT_OR_GLOBAL_EPSILON_EQUALITY",
        "TREAT_MC058_TRANSLATION_ERROR_AS_ZERO", "UNBOUND_NONLINEAR_LEAF", "PROMOTE_UNCERTIFIED_TO_INSIDE_OR_OUTSIDE",
        "PROMOTE_MODEL_EVIDENCE_TO_NATIVE_GEOMETRY", "PREMATURE_MC_B_ACCEPTANCE"
    }
    assert required <= forbidden
    pb = c["proof_boundary"]
    assert pb["MC-B"] == "NOT_ESTABLISHED" and pb["MC-1"] == "NOT_ESTABLISHED"
    assert pb["PO-02"].startswith("OPEN") and pb["PO-04"].startswith("OPEN") and pb["PO-05"].startswith("OPEN") and pb["PO-06"].startswith("OPEN")


def run_controls() -> None:
    m = implementation()
    for bad in (1.0, True):
        try:
            m.q(bad)
        except TypeError:
            pass
        else:
            raise AssertionError("binary/bool authority input accepted")

    flat = m.FlatEndMill.make(1, 2)
    varying = m.Leaf.make((0,0,0), (2,0,2))
    assert m.exact_sweep_contains((1,1,2), flat, [varying])
    assert m.exact_sweep_contains((1,"99/100",2), flat, [varying])
    assert not m.exact_sweep_contains((1,"101/100",2), flat, [varying])
    assert Fraction(2) - (Fraction(0) + Fraction(1,2)*2) == 1

    corner = m.CornerRadiusEndMill.make(2,1,4)
    stationary = m.Leaf.make((0,0,0),(0,0,0), source_class="stationary")
    p = (Fraction(9,5), Fraction(0), Fraction(2,5))
    assert (p[0]-1)**2 + (p[2]-1)**2 == 1
    assert m.exact_sweep_contains(p, corner, [stationary])
    assert m.exact_sweep_contains(("179/100",0,"2/5"), corner, [stationary])
    assert not m.exact_sweep_contains(("181/100",0,"2/5"), corner, [stationary])

    rounded_vary = m.Leaf.make((0,0,0),(2,0,2))
    assert m.exact_sweep_contains(("14/5",0,"7/5"), corner, [rounded_vary])

    fwd = m.swept_path((m.Leaf.make((0,0,0),(2,0,0)),))
    retrace = m.swept_path((m.Leaf.make((0,0,0),(2,0,0)), m.Leaf.make((2,0,0),(0,0,0))))
    assert len(retrace) == 2
    probes = [(0,0,1),(1,1,1),(2,0,0),(3,0,1),(1,"101/100",1)]
    assert [m.exact_sweep_contains(x, flat, fwd) for x in probes] == [m.exact_sweep_contains(x, flat, retrace) for x in probes]

    try:
        m.swept_path((m.Leaf.make((0,0,0),(1,0,0)), m.Leaf.make((2,0,0),(3,0,0))))
    except ValueError:
        pass
    else:
        raise AssertionError("engaged teleportation accepted")
    bad_leaf = m.Leaf.make((0,0,0),(1,0,0), translation_error="1/10", source_class="spline", engagement_bound=False)
    try:
        m.certified_classify((0,0,0), flat, [bad_leaf])
    except ValueError:
        pass
    else:
        raise AssertionError("unbound nonlinear leaf accepted")

    zero_spline = m.Leaf.make((0,0,0),(2,0,0), translation_error=0, source_class="spline")
    try:
        m.exact_sweep_contains((1,0,1), flat, [zero_spline])
    except ValueError:
        pass
    else:
        raise AssertionError("nonlinear source accepted by exact-line path")
    assert m.certified_classify((1,0,1), corner, [zero_spline]) == "INSIDE"
    assert m.certified_classify((1,"3/2","1/10"), corner, [zero_spline]) == "UNCERTIFIED"

    try:
        m.Leaf.make((0,0,0),(1,0,0), source_class="invented_curve")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown source class accepted")

    leaf = m.Leaf.make((0,0,0),(2,0,0), translation_error="1/10", source_class="circular_arc")
    assert m.certified_classify((1,0,1), flat, [leaf]) == "INSIDE"
    assert m.certified_classify((1,2,1), flat, [leaf]) == "OUTSIDE"
    assert m.certified_classify((1,"21/20",1), flat, [leaf]) == "UNCERTIFIED"

    huge = m.Leaf.make((0,0,0),(2,0,0), translation_error="3/2", source_class="spline")
    assert m.certified_classify((1,0,1), flat, [huge]) == "UNCERTIFIED"

    assert m.cylinder_segment_contains(("19/10",0,"1/10"), m.Cylinder(Fraction(2), Fraction(0), Fraction(4)), stationary.p0, stationary.p1)
    assert not m.corner_segment_contains(("19/10",0,"1/10"), corner, stationary.p0, stationary.p1)


def adversarial_contract_tests(c: dict) -> None:
    def reject(mutator):
        x = copy.deepcopy(c); mutator(x)
        try: validate_contract(x, check_files=False)
        except (AssertionError, KeyError): return
        raise AssertionError("adversarial contract mutation was accepted")

    reject(lambda x: x["authority"].__setitem__("binary_float_authority_forbidden", False))
    reject(lambda x: x["authority"].__setitem__("retrace_is_not_deleted_from_journal", False))
    reject(lambda x: x["exact_construction"].__setitem__("varying_z_supported", False))
    reject(lambda x: x["mc058_leaf_construction"].__setitem__("classification", ["INSIDE","OUTSIDE"]))
    reject(lambda x: x["mc058_leaf_construction"].__setitem__("topology_or_exact_zero_claim_implied", True))
    reject(lambda x: x["proof_boundary"].__setitem__("MC-B", "ACCEPTED"))
    reject(lambda x: x["forbidden"].remove("CORNER_RADIUS_REPLACED_BY_FLAT_CYLINDER"))
    reject(lambda x: x["formal_dependencies"][2].__setitem__("blob_sha", "0"*40))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--contract", action="store_true"); ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    c = load(CONTRACT_PATH)
    validate_contract(c)
    run_controls()
    if args.self_test:
        adversarial_contract_tests(c)
    print("MC-018 fixed-axis sweep contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
