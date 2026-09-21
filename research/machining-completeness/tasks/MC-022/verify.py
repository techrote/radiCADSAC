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
HERE = Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "phase-sensitive-lathe-contract-v1.json"
IMPL_PATH = HERE / "phase_sensitive_lathe.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def validate_contract(c: dict) -> list[str]:
    e: list[str] = []
    if c.get("schema") != "radicadsac-mc022-phase-sensitive-lathe/1.0": e.append("schema")
    if c.get("task") != "MC-022" or c.get("issue") != 84: e.append("identity")
    if c.get("source_baseline") != "b01a2665ef8e5b83200260dcd0815b990544ef31": e.append("source_baseline")
    if c.get("native_execution") is not False: e.append("native_execution")
    deps = {d.get("task"): d for d in c.get("formal_dependencies", [])}
    expected = {
        "MC-005": ("adec886597a06345fdfdf65ee018596cd396d249", "CAPABILITY_ACCEPTED"),
        "MC-010": ("4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
        "MC-007": ("8d54872292dfd9f632c79c76994a467d26eaaf9c", "NEGATIVE_RESULT"),
        "MC-058": ("038fccda9142650ee7e29c626aeb8e4602420278", "COMPLETED_RESEARCH"),
    }
    if set(deps) != set(expected): e.append("formal_dependencies")
    else:
        for task, (sha, kind) in expected.items():
            if deps[task].get("blob_sha") != sha or deps[task].get("result_kind") != kind: e.append(f"dependency:{task}")
    s = c.get("source_semantics", {})
    if set(s.get("required_operations", [])) != {"lathe_threading_synchronized", "lathe_eccentric_turning"}: e.append("required_operations")
    for key in ("shared_time_parameter","unwrapped_phase_preserved","phase_feed_correlation_authoritative","saved_operation_immutable","exact_engagement_boundaries","semantic_knots_preserved"):
        if s.get(key) is not True: e.append(key)
    for key in ("independent_phase_product_allowed","global_epsilon_predicate_authority","binary_float_certifying_authority"):
        if s.get(key) is not False: e.append(key)
    constructors = c.get("constructors", {})
    if constructors.get("lathe_threading_synchronized", {}).get("route") != "FINITE_EXACT_RATIONAL_TIMED_SEGMENTS": e.append("threading_route")
    if constructors.get("lathe_eccentric_turning", {}).get("route") != "FINITE_SYMBOLIC_TIMED_ECCENTRIC_PLACEMENT": e.append("eccentric_route")
    for op in ("lathe_threading_synchronized", "lathe_eccentric_turning"):
        if constructors.get(op, {}).get("full_angle_substitution") != "FORBIDDEN": e.append(f"full_angle:{op}")
    route = c.get("event_route", {})
    if route.get("finite_source_decomposition") is not True: e.append("finite_source_decomposition")
    if route.get("tangent_multiple_singular") != "TRANSCENDENTAL_EVENT_BLOCKER": e.append("event_blocker")
    if route.get("blocker_is_success") is not False or route.get("blocker_is_empty_sweep") is not False: e.append("blocker_semantics")
    if route.get("unbounded_refinement_required") is not False: e.append("unbounded_refinement")
    transfer = c.get("mc058_transfer", {})
    if transfer.get("formula") != "e_total = e_inherited + e_translation + rho*e_rotation + e_tool": e.append("mc058_formula")
    if transfer.get("complete_cutter_support_radius_required") is not True: e.append("support_radius")
    if transfer.get("centreline_only_certificate_allowed") is not False: e.append("centreline_only")
    if transfer.get("error_reset_at_piece_boundary") is not False: e.append("error_reset")
    p = c.get("protected_semantics", {})
    for key in ("historical_source_audio_provenance_unchanged","canonical_journal_unchanged","positive_volume_preserved","durable_body_lineage_separate_from_sweep_parameterization"):
        if p.get(key) is not True: e.append(key)
    if p.get("native_geometry_claim") is not False: e.append("native_geometry_claim")
    blockers = {b.get("id"): b.get("status") for b in c.get("blockers", [])}
    if blockers.get("PB-007-01") != "OPEN" or blockers.get("PB-007-02") != "OPEN": e.append("inherited_blockers")
    ps = c.get("programme_state", {})
    if ps.get("MC-A") != "ACCEPTED": e.append("mc_a")
    for gate in ("MC-B","MC-C","MC-D","MC-E","MC-F","MC-1"):
        if ps.get(gate) != "NOT_ESTABLISHED": e.append(gate)
    acc = c.get("acceptance", {})
    if acc.get("required_timed_constructors_have_finite_validated_routes") is not True: e.append("acceptance_constructors")
    if acc.get("negative_results_and_unresolved_claims_preserved") is not True: e.append("acceptance_negative")
    ctrl = c.get("supplementary_independent_control", {})
    if (ctrl.get("task") != "MC-013" or ctrl.get("family") != "F09" or ctrl.get("blob_sha") != "cc02473bc7afc47dface7812f9fbbbc3f41b9fa4" or ctrl.get("oracle_blob_sha") != "f0e64a7ced8e57de21a24fffa55609e2dff04aca" or ctrl.get("candidate_output_used_for_expected_truth") is not False): e.append("independent_f09")
    return e


def check_bound_files(c: dict) -> None:
    for dep in c["formal_dependencies"]:
        path = ROOT / dep["path"]
        assert path.exists(), dep["path"]
        assert _git_blob_sha(path) == dep["blob_sha"], dep["task"]
    ctrl = c["supplementary_independent_control"]
    p = ROOT / ctrl["path"]
    o = ROOT / ctrl["oracle_path"]
    assert _git_blob_sha(p) == ctrl["blob_sha"], "MC-013 F09 corpus drift"
    assert _git_blob_sha(o) == ctrl["oracle_blob_sha"], "MC-013 oracle drift"


def exact_controls() -> None:
    m = _load_module(IMPL_PATH, "mc022_impl")
    seg = m.TimedSegment(Fraction(0), Fraction(1), Fraction(22), Fraction(18), Fraction(20), Fraction(40), Fraction(1,8), Fraction(1,4))
    mid = seg.sample(Fraction(1,2))
    assert mid.r == Fraction(20) and mid.z == Fraction(30) and mid.phase_turns_unwrapped == Fraction(3,16)
    assert seg.lead_per_turn() == Fraction(160)
    assert m.alignment_times(seg, Fraction(13,16)) == (Fraction(1,2),)
    assert m.synchronized_band_removes(seg, Fraction(13,16), 30, 19, 1, 18)
    assert not m.synchronized_band_removes(seg, Fraction(13,16), 32, 19, 1, 18)
    assert m.synchronized_band_removes(seg, Fraction(7,8), 20, 19, 1, 18)
    assert m.synchronized_band_removes(seg, Fraction(3,4), 40, 19, 1, 18)
    assert m.synchronized_band_removes(seg, Fraction(3001,4000), Fraction(999,25), 19, 1, 18)
    assert not m.synchronized_band_removes(seg, Fraction(2999,4000), 40, 19, 1, 18)
    multi = m.TimedSegment(Fraction(0), Fraction(1), Fraction(5), Fraction(5), Fraction(0), Fraction(4), Fraction(0), Fraction(2))
    assert m.alignment_times(multi, Fraction(3,4)) == (Fraction(1,8), Fraction(5,8))
    assert multi.sample(Fraction(1)).phase_turns_unwrapped == 2 and m.normalize_turn(multi.sample(Fraction(1)).phase_turns_unwrapped) == 0
    reverse = m.TimedSegment(Fraction(0), Fraction(1), Fraction(5), Fraction(5), Fraction(0), Fraction(1), Fraction(1), Fraction(0))
    assert m.alignment_times(reverse, Fraction(3,4)) == (Fraction(3,4),)
    a = m.TimedSegment(Fraction(0),Fraction(1),Fraction(5),Fraction(5),Fraction(0),Fraction(2),Fraction(0),Fraction(1,4))
    b = m.TimedSegment(Fraction(1),Fraction(2),Fraction(5),Fraction(4),Fraction(2),Fraction(3),Fraction(1,4),Fraction(1,2))
    s = m.TimedProgram((a,b)).sample(1)
    assert (s.r,s.z,s.phase_turns_unwrapped) == (Fraction(5),Fraction(2),Fraction(1,4))
    eccseg = m.TimedSegment(Fraction(0),Fraction(1),Fraction(0),Fraction(0),Fraction(0),Fraction(0),Fraction(0),Fraction(1))
    law = m.EccentricLaw(Fraction(10),Fraction(20),Fraction(2),Fraction(1),eccseg)
    assert law.cardinal_center(0) == (Fraction(12),Fraction(21))
    assert law.cardinal_center(Fraction(1,4)) == (Fraction(9),Fraction(22))
    assert law.cardinal_center(Fraction(1,2)) == (Fraction(8),Fraction(19))
    assert law.cardinal_center(Fraction(3,4)) == (Fraction(11),Fraction(18))
    assert law.symbolic_center(Fraction(1,8))["phase_turns_unwrapped"] == Fraction(1,8)
    try: law.cardinal_center(Fraction(1,8))
    except ValueError: pass
    else: raise AssertionError("non-cardinal trig must not become exact authority")
    assert m.classify_certified_event(1,2,-1,1) == "SEPARATED"
    assert m.classify_certified_event(-1,1,2,3) == "TRANSVERSAL"
    assert m.classify_certified_event(-1,1,-1,1) == "TRANSCENDENTAL_EVENT_BLOCKER"
    assert m.actual_sweep_error_bound(Fraction(1,4000), Fraction(1,1000), 5, Fraction(1,10000), Fraction(1,2000)) == Fraction(9,4000)
    for bad in (0.5, True):
        try: m.q(bad)
        except TypeError: pass
        else: raise AssertionError("binary/bool authority admitted")


def independent_f09_control(c: dict) -> None:
    m = _load_module(IMPL_PATH, "mc022_impl_f09")
    o = _load_module(ROOT / c["supplementary_independent_control"]["oracle_path"], "mc013_oracle")
    seg = m.TimedSegment(Fraction(0), Fraction(1), Fraction(22), Fraction(18), Fraction(20), Fraction(40), Fraction(1,8), Fraction(1,4))
    probes = [("13/16","30","19"),("13/16","32","19"),("7/8","20","19"),("3/4","40","19"),("3001/4000","999/25","19"),("2999/4000","40","19"),("1/2","30","19")]
    for theta,z,r in probes:
        ours = m.synchronized_band_removes(seg, theta, z, r, 1, 18)
        theirs = o.synchronized_turning_removes(theta,z,r,"1/8","1/4","20","40","1","18")
        assert ours == theirs, (theta,z,r,ours,theirs)


def adversarial_contract_controls(c: dict) -> None:
    mutations = []
    def mut(fn):
        x = copy.deepcopy(c); fn(x); mutations.append(x)
    mut(lambda x: x["source_semantics"].__setitem__("shared_time_parameter", False))
    mut(lambda x: x["source_semantics"].__setitem__("independent_phase_product_allowed", True))
    mut(lambda x: x["source_semantics"].__setitem__("unwrapped_phase_preserved", False))
    mut(lambda x: x["source_semantics"].__setitem__("global_epsilon_predicate_authority", True))
    mut(lambda x: x["source_semantics"].__setitem__("saved_operation_immutable", False))
    mut(lambda x: x["source_semantics"].__setitem__("exact_engagement_boundaries", False))
    mut(lambda x: x["source_semantics"].__setitem__("required_operations", ["lathe_threading_synchronized"]))
    mut(lambda x: x["constructors"]["lathe_threading_synchronized"].__setitem__("full_angle_substitution", "ALLOWED"))
    mut(lambda x: x["constructors"]["lathe_eccentric_turning"].__setitem__("route", "SAMPLED_ANGLES"))
    mut(lambda x: x["event_route"].__setitem__("tangent_multiple_singular", "NO_EVENT"))
    mut(lambda x: x["event_route"].__setitem__("blocker_is_success", True))
    mut(lambda x: x["mc058_transfer"].__setitem__("centreline_only_certificate_allowed", True))
    mut(lambda x: x["mc058_transfer"].__setitem__("error_reset_at_piece_boundary", True))
    mut(lambda x: x["protected_semantics"].__setitem__("positive_volume_preserved", False))
    mut(lambda x: x["protected_semantics"].__setitem__("native_geometry_claim", True))
    mut(lambda x: x["blockers"][0].__setitem__("status", "CLOSED"))
    mut(lambda x: x["programme_state"].__setitem__("MC-B", "ACCEPTED"))
    mut(lambda x: x["supplementary_independent_control"].__setitem__("candidate_output_used_for_expected_truth", True))
    for i, bad in enumerate(mutations): assert validate_contract(bad), f"mutation {i} escaped validation"


def main() -> int:
    ap = argparse.ArgumentParser(); mx = ap.add_mutually_exclusive_group(required=True)
    mx.add_argument("--contract", action="store_true"); mx.add_argument("--self-test", action="store_true")
    a = ap.parse_args(); c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    errors = validate_contract(c)
    if errors: raise SystemExit("MC-022 contract invalid: " + ", ".join(errors))
    exact_controls(); adversarial_contract_controls(c)
    if a.contract: check_bound_files(c); independent_f09_control(c)
    print("MC-022 verification passed"); return 0


if __name__ == "__main__": raise SystemExit(main())
