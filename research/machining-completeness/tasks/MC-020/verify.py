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
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-020"
CONTRACT_PATH = TASK / "form-undercut-sweep-contract-v1.json"
IMPL_PATH = TASK / "form_undercut_sweep.py"
EXPECTED_BASE = "a5b6905bb212afed21a7747cd80a0bf87ee34cca"
EXPECTED_DEPS = {
    "MC-005": ("research/machining-completeness/tasks/MC-005/outcome.json", "adec886597a06345fdfdf65ee018596cd396d249", "CAPABILITY_ACCEPTED"),
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-058": ("research/machining-completeness/tasks/MC-058/outcome.json", "038fccda9142650ee7e29c626aeb8e4602420278", "COMPLETED_RESEARCH"),
}
EXPECTED_CONTROL = ("research/machining-completeness/tasks/MC-010/independent_exact_oracle.py", "cfb5a8def57e8f4bb5109982da456621766a2b22")


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
    return load_module("mc020_form_undercut_sweep", IMPL_PATH)


def independent_oracle():
    return load_module("mc010_exact_oracle_for_mc020", ROOT / EXPECTED_CONTROL[0])


def validate_contract(c: dict, *, check_files: bool = True) -> None:
    assert c["schema"] == "radicadsac-mc020-form-undercut-sweep/1.0"
    assert c["task"] == "MC-020" and c["issue"] == 82
    assert c["source_baseline"] == EXPECTED_BASE
    assert c["result"] == "COMPLETED_RESEARCH_BOUNDED_FORM_UNDERCUT_SWEEP_CONSTRUCTION"
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
    assert "not imported by the MC-020 implementation" in ctl["role"]
    if check_files:
        p = ROOT / ctl["path"]
        assert p.is_file() and blob_sha(p) == ctl["blob_sha"], "independent control drift"

    a = c["authority"]
    for key in (
        "saved_operation_is_immutable", "engagement_boundaries_are_authoritative",
        "cutting_and_noncutting_regions_are_distinct", "access_is_independent_of_candidate_success",
        "binary_float_authority_forbidden", "global_epsilon_predicate_forbidden",
    ):
        assert a[key] is True
    assert "closure(union" in a["sweep_semantics"]

    codec = c["bounded_cutter_codec"]
    assert codec["id"] == "exact_rational_box_union_v1"
    for key in ("nonconvexity_preserved_by_union_not_hull", "reentrant_voids_are_not_filled", "complete_finite_extent_required"):
        assert codec[key] is True
    assert codec["universal_form_codec_claimed"] is False
    assert "PB-007-03" in codec["scope_boundary"]

    cov = c["constructor_coverage"]
    assert set(k for k in cov if k.startswith("mill_") or k.startswith("lathe_")) == {"mill_form", "mill_accessible_undercut", "lathe_form_tool"}
    assert cov["mill_form"]["status"] == "EXECUTABLE_BOUNDED_ROUTE"
    assert cov["mill_accessible_undercut"]["status"] == "EXECUTABLE_BOUNDED_ROUTE_WITH_ACCESS_WITNESS"
    assert cov["lathe_form_tool"]["status"] == "LOCAL_CUTTER_CODEC_EXECUTABLE_PROCESS_SWEEP_DEFERRED"
    assert cov["lathe_form_tool"]["process_owner"] == ["MC-021", "MC-022"]
    assert cov["frozen_domain_denominator_unchanged"] is True
    assert cov["no_constructor_excluded_for_provider_convenience"] is True
    for key in ("mill_form", "mill_accessible_undercut", "lathe_form_tool"):
        assert cov[key]["outside_codec"] == "PB-007-03"

    exact = c["exact_construction"]
    assert set(exact["source_classes"]) == {"stationary", "line", "polyline"}
    for key in ("shared_xyz_parameter_required", "simultaneous_xyz_supported", "aabb_or_convex_hull_substitution_forbidden", "stationary_supported", "reversal_and_retrace_supported", "continuity_required", "engaged_teleportation_rejected", "equality_is_not_epsilonized"):
        assert exact[key] is True
    assert "one shared source parameter" in exact["algorithm"]

    bounded = c["mc058_leaf_construction"]
    assert set(bounded["source_classes"]) == {"circular_arc", "helical_arc", "spline", "piecewise_motion", "timed_phase_motion"}
    assert bounded["classification"] == ["INSIDE", "OUTSIDE", "UNCERTIFIED"]
    assert bounded["uncertified_is_not_failure_or_pass"] is True
    assert bounded["missing_or_unbound_leaf_certificate_is_rejected"] is True
    assert bounded["topology_or_exact_zero_claim_implied"] is False
    assert "inflate" in bounded["outer_rule"] and "erode" in bounded["inner_rule"]

    access = c["access_witness"]
    assert "cutting region plus" in access["complete_body"]
    assert access["candidate_success_is_not_access_oracle"] is True
    assert access["cutting_region_only_clearance_is_insufficient"] is True
    assert access["contact_policy"].startswith("closed-set contact")

    blockers = {b["id"]: b for b in c["blockers"]}
    assert set(blockers) == {"PB-007-03"}
    assert blockers["PB-007-03"]["status"] == "OPEN_PROPAGATED"
    assert "universal finite exact source codec" in blockers["PB-007-03"]["reason"]
    assert "MC-020" not in blockers["PB-007-03"]["affected_descendants"]

    forbidden = set(c["forbidden"])
    required = {
        "AABB_OR_CONVEX_HULL_AS_TOOL_TRUTH", "FILL_REENTRANT_VOID", "DROP_HOLDER_FROM_ACCESS_WITNESS",
        "CUTTING_REGION_ONLY_CLEARANCE", "CANDIDATE_SUCCESS_AS_ACCESS_ORACLE", "ENGAGED_TELEPORTATION",
        "DELETE_RETRACE_FROM_SOURCE_JOURNAL", "BINARY_FLOAT_OR_GLOBAL_EPSILON_EQUALITY",
        "TREAT_MC058_TRANSLATION_ERROR_AS_ZERO", "UNBOUND_NONLINEAR_LEAF",
        "PROMOTE_UNCERTIFIED_TO_INSIDE_OR_OUTSIDE", "CLAIM_UNIVERSAL_ARBITRARY_FORM_CODEC",
        "CLAIM_LATHE_ROTATIONAL_OR_TIMED_SWEEP_FROM_LOCAL_TOOL_CODEC", "REUSE_CANDIDATE_GEOMETRY_AS_INDEPENDENT_ORACLE",
        "PROMOTE_MODEL_EVIDENCE_TO_NATIVE_GEOMETRY", "CLOSE_PB_007_03", "PREMATURE_MC_B_ACCEPTANCE",
    }
    assert required <= forbidden

    pb = c["proof_boundary"]
    assert pb["MC-B"] == "NOT_ESTABLISHED" and pb["MC-1"] == "NOT_ESTABLISHED"
    for po in ("PO-02", "PO-04", "PO-05", "PO-06"):
        assert pb[po].startswith("OPEN")


def run_controls() -> None:
    m = implementation()
    for bad in (1.0, True):
        try:
            m.q(bad)
        except TypeError:
            pass
        else:
            raise AssertionError("binary/bool authority input accepted")

    # Nonconvex stepped form: the reentrant space must remain void rather than
    # being filled by a bounding box or convex-hull shortcut.
    form = m.Tool.make(
        "mill_form",
        (
            m.Box.make(-1, 1, -1, 1, 0, 1),
            m.Box.make("-1/2", "1/2", -1, 1, 1, 2),
        ),
    )
    stationary = m.Leaf.make((0, 0, 0), (0, 0, 0), source_class="stationary")
    assert m.exact_sweep_contains((1, 0, "1/2"), form, (stationary,))
    assert m.exact_sweep_contains(("99/100", 0, "1/2"), form, (stationary,))
    assert not m.exact_sweep_contains(("101/100", 0, "1/2"), form, (stationary,))
    assert not m.exact_sweep_contains(("3/4", 0, "3/2"), form, (stationary,)), "reentrant void was filled"

    # One source parameter must satisfy all coordinates. An endpoint AABB would
    # falsely contain (2,0,1), but no single t does.
    cube_tool = m.Tool.make("mill_form", (m.Box.make(0, 1, 0, 1, 0, 1),))
    diagonal = m.Leaf.make((0, 0, 0), (1, 1, 1))
    assert m.exact_sweep_contains(("3/2", "3/2", "3/2"), cube_tool, (diagonal,))
    assert not m.exact_sweep_contains((2, 0, 1), cube_tool, (diagonal,)), "XYZ path correlation was lost"

    # Independent MC-010 axis-parallel box-sweep comparison. The implementation
    # does not import this oracle.
    oracle = independent_oracle()
    local = m.Box.make("-1/2", "1/2", "-1/4", "1/4", 0, 1)
    axis_tool = m.Tool.make("mill_form", (local,))
    axis_leaf = m.Leaf.make((0, 0, 0), (2, 0, 0))
    obox = oracle.Box.make("-1/2", "1/2", "-1/4", "1/4", 0, 1)
    osweep = oracle.swept_box_axis_parallel(obox, "x", 0, 2)
    probes = [
        ("-1/2", 0, "1/2"), ("5/2", 0, "1/2"), (1, "1/4", 1),
        (1, "26/100", "1/2"), (3, 0, "1/2"),
    ]
    for p in probes:
        expected = oracle.contains_point(osweep, p)
        assert m.exact_sweep_contains(p, axis_tool, (axis_leaf,)) is expected

    # Accessible undercut: wide cutting head can arrive from the side below the
    # lips while the narrow neck/holder remains in the clearance slot. A vertical
    # plunge collides with the retained lips. Clearance checks the complete body.
    undercut = m.Tool.make(
        "mill_accessible_undercut",
        (
            m.Box.make(-1, 1, -1, 1, 0, "3/4"),
            m.Box.make("-1/4", "1/4", "-1/4", "1/4", "3/4", "5/2"),
        ),
        (m.Box.make("-1/4", "1/4", "-1/4", "1/4", "5/2", "7/2"),),
    )
    lips = (
        m.Box.make(-2, 2, -3, "-1/2", 1, 2),
        m.Box.make(-2, 2, "1/2", 3, 1, 2),
    )
    assert m.access_is_clear(undercut, ((-4, 0, 0), (0, 0, 0)), lips)
    assert not m.access_is_clear(undercut, ((0, 0, 3), (0, 0, 0)), lips)

    # Holder-only obstruction catches the forbidden cutting-region-only shortcut.
    holder_obstacle = (m.Box.make(-1, 1, -1, 1, 3, "13/4"),)
    assert not m.access_is_clear(undercut, ((-4, 0, 0), (0, 0, 0)), holder_obstacle)
    cutting_only = m.Tool.make("mill_accessible_undercut", undercut.cutting)
    assert m.access_is_clear(cutting_only, ((-4, 0, 0), (0, 0, 0)), holder_obstacle)

    # Nonlinear source is fail-closed through a source-bound MC-058 sandwich.
    bounded_tool = m.Tool.make("mill_form", (m.Box.make(-1, 1, -1, 1, 0, 1),))
    bounded = m.Leaf.make((0, 0, 0), (1, 0, 0), translation_error="1/10", source_class="spline")
    assert m.certified_classify(("1/2", 0, "1/2"), bounded_tool, (bounded,)) == "INSIDE"
    assert m.certified_classify((3, 0, "1/2"), bounded_tool, (bounded,)) == "OUTSIDE"
    assert m.certified_classify(("41/20", 0, "1/2"), bounded_tool, (bounded,)) == "UNCERTIFIED"

    bad_leaf = m.Leaf.make((0, 0, 0), (1, 0, 0), translation_error="1/10", source_class="spline", engagement_bound=False)
    try:
        m.certified_classify((0, 0, 0), bounded_tool, (bad_leaf,))
    except ValueError:
        pass
    else:
        raise AssertionError("unbound nonlinear leaf accepted")

    try:
        m.exact_sweep_contains((0, 0, 0), bounded_tool, (bounded,))
    except ValueError:
        pass
    else:
        raise AssertionError("uncertain nonlinear leaf accepted by exact route")

    fwd = m.swept_path((m.Leaf.make((0, 0, 0), (2, 0, 0)),))
    retrace = m.swept_path((m.Leaf.make((0, 0, 0), (2, 0, 0)), m.Leaf.make((2, 0, 0), (0, 0, 0))))
    assert len(retrace) == 2
    retrace_tool = m.Tool.make("mill_form", (m.Box.make("-1/2", "1/2", "-1/2", "1/2", 0, 1),))
    for p in ((0, 0, "1/2"), (1, 0, "1/2"), ("5/2", 0, "1/2"), (1, 1, "1/2")):
        assert m.exact_sweep_contains(p, retrace_tool, fwd) == m.exact_sweep_contains(p, retrace_tool, retrace)

    try:
        m.swept_path((m.Leaf.make((0, 0, 0), (1, 0, 0)), m.Leaf.make((2, 0, 0), (3, 0, 0))))
    except ValueError:
        pass
    else:
        raise AssertionError("engaged teleportation accepted")

    # The bounded codec may encode a lathe form cutter locally, but this task
    # deliberately does not synthesize spindle/timed lathe process semantics.
    lathe = m.Tool.make("lathe_form_tool", (m.Box.make("-1/4", "1/4", "-1/2", "1/2", 0, 1),))
    assert m.exact_sweep_contains((0, 0, "1/2"), lathe, (stationary,))


def adversarial_contract_tests(c: dict) -> None:
    def reject(mutator):
        x = copy.deepcopy(c)
        mutator(x)
        try:
            validate_contract(x, check_files=False)
        except (AssertionError, KeyError):
            return
        raise AssertionError("adversarial contract mutation was accepted")

    reject(lambda x: x["authority"].__setitem__("binary_float_authority_forbidden", False))
    reject(lambda x: x["authority"].__setitem__("access_is_independent_of_candidate_success", False))
    reject(lambda x: x["bounded_cutter_codec"].__setitem__("universal_form_codec_claimed", True))
    reject(lambda x: x["bounded_cutter_codec"].__setitem__("reentrant_voids_are_not_filled", False))
    reject(lambda x: x["exact_construction"].__setitem__("shared_xyz_parameter_required", False))
    reject(lambda x: x["access_witness"].__setitem__("cutting_region_only_clearance_is_insufficient", False))
    reject(lambda x: x["mc058_leaf_construction"].__setitem__("classification", ["INSIDE", "OUTSIDE"]))
    reject(lambda x: x["constructor_coverage"]["lathe_form_tool"].__setitem__("status", "EXECUTABLE_COMPLETE_LATHE_SWEEP"))
    reject(lambda x: x["constructor_coverage"]["mill_form"].__setitem__("outside_codec", "SOLVED"))
    reject(lambda x: x["blockers"].clear())
    reject(lambda x: x["blockers"][0].__setitem__("status", "CLOSED"))
    reject(lambda x: x["proof_boundary"].__setitem__("MC-B", "ACCEPTED"))
    reject(lambda x: x["forbidden"].remove("DROP_HOLDER_FROM_ACCESS_WITNESS"))
    reject(lambda x: x["formal_dependencies"][2].__setitem__("blob_sha", "0" * 40))
    reject(lambda x: x["independent_control"].__setitem__("blob_sha", "0" * 40))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    c = load(CONTRACT_PATH)
    validate_contract(c)
    run_controls()
    if args.self_test:
        adversarial_contract_tests(c)
    print("MC-020 bounded form/undercut sweep contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
