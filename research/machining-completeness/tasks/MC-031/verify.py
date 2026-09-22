#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
from material_evaluator import *

Q = Fraction


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def base_request(operation_id: str, *, witness="1/1000000") -> dict:
    return {
        "operation_id": operation_id,
        "source_bound": True,
        "common_frame": "workpiece_common",
        "input_revision": "rev-17",
        "body_id": "body-A",
        "durable_identity_source": "canonical_journal",
        "positive_volume_witness": witness,
        "error_terms": {
            "inherited": "1/1000",
            "translation": "1/2000",
            "support_radius": "2",
            "rotation_radians": "1/10000",
            "tool": "1/3000",
        },
    }


def axisymmetry_meta() -> dict:
    meta = {key: True for key in MC021.REQUIRED_TRUE}
    meta.update({key: False for key in MC021.REQUIRED_FALSE})
    meta.update(
        phase_domain="FULL_S1_FOR_EACH_MERIDIAN_STATE",
        fallback_owner="MC-022",
        material_representation="EXACT_AXISYMMETRIC_MERIDIAN",
    )
    return meta


def make_workpiece(error=Q(1, 1000)):
    setup = MC023.Setup("setup-0", "mill", MC023.RigidTransform.identity(), error)
    stock = MC023.Box((0, 0, 0), (3, 3, 3))
    body = MC023.Body("body-A", "lineage-A", (stock,))
    return MC023.Workpiece("rev-17", (body,), setup)


def self_test():
    # Frozen denominator and actual constructor ownership.
    manifest = coverage_manifest()
    require(set(manifest) == set(MC026.REQUIRED_OPERATIONS), "26-operation denominator coverage")
    require(len(manifest) == 26, "frozen denominator must remain 26")
    require(set(owner for owners in manifest.values() for owner in owners) == {"MC-018", "MC-019", "MC-020", "MC-021", "MC-022", "MC-023"}, "all actual sweep/setup owners represented")

    eps = Q(1, 1_000_000)

    # MC-018: exact closed sweep boundary is touching only; signed neighbours
    # require independent positive-volume evidence before material is removed.
    flat = MC018.FlatEndMill.make(1, 2)
    flat_leaf = MC018.Leaf.make((0, 0, 0), (0, 0, 0), source_class="stationary")
    tangent = {**base_request("mill_face", witness="0"), "tool": flat, "leaves": (flat_leaf,), "point": (1, 0, 1)}
    tr = evaluate_removed_point(tangent)
    require(tr["status"] == "DECIDED" and tr["relation"] == "TOUCHING_ONLY_NO_MATERIAL_TRANSITION" and not tr["removed"], "MC018 tangent must not remove positive volume")
    inside = {**base_request("mill_face"), "tool": flat, "leaves": (flat_leaf,), "point": (Q(1)-eps, 0, 1)}
    ir = evaluate_removed_point(inside)
    require(ir["relation"] == "REMOVED_POSITIVE_VOLUME" and ir["removed"], "MC018 signed penetration")
    outside = {**base_request("mill_face"), "tool": flat, "leaves": (flat_leaf,), "point": (Q(1)+eps, 0, 1)}
    require(evaluate_removed_point(outside)["relation"] == "NOT_IN_SWEEP", "MC018 signed separation")

    # A bounded nonlinear MC-058 leaf remains uncertified in its enclosure band;
    # refinement/error width is not silently promoted to truth.
    bounded_leaf = MC018.Leaf.make((0, 0, 0), (0, 0, 0), translation_error="1/10", source_class="circular_arc")
    bounded = {**base_request("mill_simultaneous_xyz"), "tool": flat, "leaves": (bounded_leaf,), "point": (Q(21,20), 0, 1)}
    br = evaluate_removed_point(bounded)
    require(br["status"] == "UNCERTIFIED" and br["is_truth_value"] is False, "bounded sweep enclosure must fail closed")

    # MC-019 curved boundary and signed neighbours.
    ball = MC019.BallRoundEndMill.make(1, 2)
    ball_leaf = MC019.Leaf.make((0, 0, 0), (0, 0, 0), source_class="stationary")
    b_tan = {**base_request("mill_ball_rounded_xyz", witness="0"), "tool": ball, "leaves": (ball_leaf,), "point": (1, 0, 1)}
    require(evaluate_removed_point(b_tan)["relation"] == "TOUCHING_ONLY_NO_MATERIAL_TRANSITION", "MC019 curved tangent")
    b_in = {**base_request("mill_ball_rounded_xyz"), "tool": ball, "leaves": (ball_leaf,), "point": (Q(1)-eps, 0, 1)}
    require(evaluate_removed_point(b_in)["removed"], "MC019 curved penetration")
    b_out = {**base_request("mill_ball_rounded_xyz"), "tool": ball, "leaves": (ball_leaf,), "point": (Q(1)+eps, 0, 1)}
    require(evaluate_removed_point(b_out)["relation"] == "NOT_IN_SWEEP", "MC019 curved separation")

    # MC-020 exact box-union source and complete cutter+holder access witness.
    cutter_box = MC020.Box.make(-1, 1, -1, 1, 0, 1)
    form_tool = MC020.Tool.make("mill_form", (cutter_box,))
    form_leaf = MC020.Leaf.make((0, 0, 0), (0, 0, 0), source_class="stationary")
    form = {**base_request("mill_form_chamfer_countersink"), "source_codec_complete": True, "tool": form_tool, "leaves": (form_leaf,), "point": (Q(1)-eps, 0, Q(1,2))}
    require(evaluate_removed_point(form)["removed"], "MC020 bounded exact source")
    form_gap = dict(form); form_gap["source_codec_complete"] = False
    fg = evaluate_removed_point(form_gap)
    require(fg["status"] == "BLOCKED" and fg["blocker"] == "PB-007-03", "arbitrary form source gap preserved")

    holder = MC020.Box.make(Q(-1,2), Q(1,2), Q(-1,2), Q(1,2), 1, 2)
    undercut_tool = MC020.Tool.make("mill_accessible_undercut", (cutter_box,), (holder,))
    obstacle = MC020.Box.make(Q(-1,4), Q(1,4), Q(-1,4), Q(1,4), Q(3,2), Q(7,4))
    undercut = {
        **base_request("mill_accessible_undercut"),
        "source_codec_complete": True,
        "tool": undercut_tool,
        "leaves": (form_leaf,),
        "point": (0, 0, Q(1,2)),
        "approach_points": ((0,0,0),(0,0,0)),
        "obstacles": (obstacle,),
    }
    ur = evaluate_removed_point(undercut)
    require(ur["status"] == "SEMANTIC_BLOCKER" and "HOLDER" in ur["reason"], "complete holder access must not be dropped")

    # MC-021 exact meridian reduction: tangent does not remove positive volume;
    # radial neighbours discriminate at exactly 1e-6.
    rect = MC021.MeridianRect(Q(0), Q(1), Q(0), Q(1))
    motion = MC021.Line2(Q(0), Q(0), Q(0), Q(0))
    lathe_base = {
        **base_request("lathe_od_turning"),
        "axisymmetry_meta": axisymmetry_meta(),
        "meridian_rects": (rect,),
        "motion": motion,
        "z": Q(1,2),
    }
    l_tan = {**lathe_base, "r": Q(1), "positive_volume_witness": "0"}
    require(evaluate_removed_point(l_tan)["relation"] == "TOUCHING_ONLY_NO_MATERIAL_TRANSITION", "MC021 tangent")
    l_in = {**lathe_base, "r": Q(1)-eps}
    require(evaluate_removed_point(l_in)["removed"], "MC021 radial penetration")
    l_out = {**lathe_base, "r": Q(1)+eps}
    require(evaluate_removed_point(l_out)["relation"] == "NOT_IN_SWEEP", "MC021 radial separation")
    phase_bad = deepcopy(l_in); phase_bad["axisymmetry_meta"]["phase_synchronization"] = True
    pbr = evaluate_removed_point(phase_bad)
    require(pbr["status"] == "BLOCKED" and pbr["blocker"] == "PB-007-02", "phase-dependent case cannot be laundered through axisymmetry")

    lathe_form_tool = MC020.Tool.make("lathe_form_tool", (cutter_box,))
    lathe_form = {**l_in, "operation_id": "lathe_form_turning", "source_codec_complete": True, "form_tool": lathe_form_tool}
    require(evaluate_removed_point(lathe_form)["removed"], "bounded MC020+MC021 lathe form integration")

    # MC-022 synchronized feed/phase uses one shared source time.  The same phase
    # with the wrong feed location is not removed.
    timed = MC022.TimedSegment(Q(0),Q(1),Q(1),Q(1),Q(0),Q(1),Q(0),Q(1))
    thread = {
        **base_request("lathe_threading_synchronized"),
        "bounded_phase_subtype": True,
        "timed_segment": timed,
        "body_theta_turns": Q(1,2),
        "z": Q(1,2),
        "radius": Q(2),
        "axial_half_width": Q(0),
        "final_radius": Q(1),
        "event_bounds": ("1/10","1/5","1","2"),
    }
    require(evaluate_removed_point(thread)["removed"], "MC022 synchronized midpoint")
    wrong_feed = dict(thread); wrong_feed["z"] = Q(2,5)
    require(evaluate_removed_point(wrong_feed)["relation"] == "NOT_IN_SWEEP", "phase and feed must remain correlated")
    unresolved = dict(thread); unresolved["event_bounds"] = ("-1","1","-1","1")
    uer = evaluate_removed_point(unresolved)
    require(uer["status"] == "BLOCKED" and uer["blocker"] == "PB-007-01", "unresolved analytic event remains PB-007-01")

    eccentric = MC022.EccentricLaw(Q(0),Q(0),Q(1),Q(0),timed)
    ereq = {**base_request("lathe_eccentric_turning"), "bounded_phase_subtype": True, "eccentric_law": eccentric, "sample_t": Q(1,4)}
    er = evaluate_removed_point(ereq)
    require(er["status"] == "BLOCKED" and er["blocker"] == "PB-007-02", "finite symbolic eccentric construction cannot become universal membership")

    # MC-023 finite history preview keeps durable IDs, exact revision order and
    # inherited error. Backend component order/size is never consulted.
    state = make_workpiece()
    cut1 = MC023.Cut("mill-1", "rev-17", "body-A", "MC-018", (MC023.Box((0,0,0),(1,1,1)),))
    setup2 = MC023.Setup("setup-1", "lathe", MC023.RigidTransform.identity(), Q(1,1000))
    cut2 = MC023.Cut("lathe-1", "rev-17>mill-1>reclamp-1", "body-A", "MC-021", (MC023.Box((1,1,1),(2,2,2)),))
    steps = (
        {"kind":"cut", "cut":cut1},
        {"kind":"reclamp", "operation_id":"reclamp-1", "setup":setup2},
        {"kind":"cut", "cut":cut2},
    )
    history = {**base_request("lathe_mill_lathe_history"), "state":state, "history_steps":steps}
    hr = evaluate_removed_point(history)
    require(hr["status"] == "CERTIFIED" and hr["durable_body_ids"] == ["body-A"] and hr["lineage_ids"] == ["lineage-A"], "MC023 durable history preview")
    stale_cut = MC023.Cut("bad", "stale-revision", "body-A", "MC-018", (MC023.Box((0,0,0),(1,1,1)),))
    stale_history = {**base_request("reclamp_reorient_continue"), "state":state, "history_steps":({"kind":"cut","cut":stale_cut},)}
    shr = evaluate_removed_point(stale_history)
    require(shr["status"] == "SEMANTIC_BLOCKER", "stale revision must fail")
    reset_setup = MC023.Setup("bad-setup", "mill", MC023.RigidTransform.identity(), Q(0))
    reset_history = {**base_request("reclamp_reorient_continue"), "state":state, "history_steps":({"kind":"reclamp","operation_id":"bad-reclamp","setup":reset_setup},)}
    rhr = evaluate_removed_point(reset_history)
    require(rhr["status"] == "SEMANTIC_BLOCKER" and "reset inherited error" in rhr.get("detail", ""), "reclamp must not reset inherited uncertainty")
    transition = {**base_request("machine_separated_retained_body"), "state":state, "history_steps":steps[:1]}
    trn = evaluate_removed_point(transition)
    require(trn["status"] == "BLOCKED" and trn["blocker"] == "PB-007-04" and not trn["body_transition_committed"], "durable connectivity transition remains MC033")

    # Complete MC-058 error transfer is nonlinear and inherited error cannot be
    # silently dropped.
    terms = base_request("mill_face")["error_terms"]
    expected = MC023.actual_sweep_error_bound(Q(1,1000),Q(1,2000),Q(2),Q(1,10000),Q(1,3000))
    require(certified_error_bound(terms) == expected, "complete error formula")
    missing = dict(terms); missing.pop("inherited")
    try:
        certified_error_bound(missing)
        raise AssertionError("missing inherited error accepted")
    except ValueError:
        pass
    try:
        certified_error_bound({**terms, "translation": 0.1})
        raise AssertionError("binary float authority accepted")
    except TypeError:
        pass

    # Source/common-frame/body identity attacks fail before geometry.
    bad_frame = dict(inside); bad_frame["common_frame"] = "machine_local"
    require(evaluate_removed_point(bad_frame)["status"] == "SEMANTIC_BLOCKER", "wrong frame")
    bad_identity = dict(inside); bad_identity["durable_identity_source"] = "backend_topology_id"
    require(evaluate_removed_point(bad_identity)["reason"] == "BACKEND_TOPOLOGY_IS_NOT_DURABLE_IDENTITY", "backend topology identity")
    unbound = dict(inside); unbound["source_bound"] = False
    require(evaluate_removed_point(unbound)["status"] == "SEMANTIC_BLOCKER", "unbound source")

    # Regularized material algebra is monotone: touching/no-hit preserves state,
    # positive-volume removal can only go MATERIAL -> VOID, and uncertainty does
    # not mutate canonical state.
    require(material_after("MATERIAL", tr)["material_state"] == "MATERIAL", "touching preserves material")
    require(material_after("MATERIAL", ir)["material_state"] == "VOID", "positive removal subtracts")
    require(material_after("VOID", ir)["material_state"] == "VOID", "machining cannot add material")
    require(material_after("MATERIAL", br)["material_state"] == "UNCERTIFIED", "uncertainty cannot mutate material")
    rr = resource_refusal()
    require(terminal_status(rr) == "RESOURCE_REFUSAL" and rr["is_truth_value"] is False, "resource refusal semantics")

    # Certificate binds source/canonical/sweep/body/revision/configuration and
    # challenge identity; staleness or mutation is rejected.
    cert = bind_material_certificate(
        input_digest="i"*64,
        canonical_digest="c"*64,
        sweep_digest="s"*64,
        body_id="body-A",
        input_revision="rev-17",
        configuration_digest="g"*64,
        challenge_id="MC049-017",
        result={"status":"DECIDED","relation":"REMOVED_POSITIVE_VOLUME"},
    )
    require(verify_material_certificate(cert, body_id="body-A", input_revision="rev-17", challenge_id="MC049-017"), "valid certificate binding")
    mutated = deepcopy(cert); mutated["body_id"] = "body-B"
    require(not verify_material_certificate(mutated, body_id="body-B"), "body mutation rejected")
    require(not verify_material_certificate(cert, input_revision="rev-18"), "stale revision rejected")
    require(not verify_material_certificate(cert, configuration_digest="x"*64), "configuration mismatch rejected")
    return True


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def contract_test(root: Path):
    contract = json.loads((HERE / "material-evaluator-contract-v1.json").read_text())
    outcome = json.loads((HERE / "outcome.json").read_text())
    require(contract["task"] == "MC-031" and outcome["task"] == "MC-031", "task identity")
    require(contract["source_baseline"] == "8cac00439bec4b8c6032be9709f81ac1bed21a7d", "exact source baseline")
    require(contract["selected_primary"] == PRIMARY, "selected primary drift")
    require(contract["ownership"] == ["MC031-A","MC031-B","MC031-C"], "MC-026 ownership")
    require(contract["capability_promotions"] == [], "no capability promotion")
    require(contract["native_or_paid_campaign_run"] is False and contract["production_authorized"] is False, "no native/paid/production authorization")

    truth = contract["truth_authority"]
    require(truth["actual_qualified_sweep_constructors"] is True, "actual sweeps are authority input")
    for key in ("binary_float","epsilon_or_global_tolerance","sampling_pitch_or_refinement_depth","timeout_or_resource_budget","accelerator_observation","backend_topology_identity"):
        require(truth[key] is False, f"forbidden truth authority: {key}")
    material = contract["material_semantics"]
    require(material["positive_volume_witness_required"] is True and material["touching_is_positive_volume_removal"] is False and material["machining_can_add_material"] is False, "material semantics")
    require(contract["error_composition"]["all_terms_required"] is True and contract["error_composition"]["inherited_error_may_reset"] is False, "error propagation")
    require(contract["body_state_boundary"]["durable_connectivity_transition_owner"] == "MC-033", "body transition ownership")
    require(contract["body_state_boundary"]["durable_identity_authority"] == "canonical_journal_body_lineage", "durable identity authority")

    manifest = coverage_manifest()
    ccoverage = {op: tuple(owners) for op, owners in contract["operation_coverage"].items()}
    require(ccoverage == manifest and len(ccoverage) == 26, "contract denominator/owner drift")
    require(set(ccoverage) == set(MC026.REQUIRED_OPERATIONS), "MC026 denominator drift")

    # Freeze consumption to the actual reviewed constructor blobs.  Any silent
    # edit to an accepted sweep invalidates this integration and forces review.
    for task, spec in contract["qualified_sweep_modules"].items():
        path = root / spec["path"]
        require(path.is_file(), f"missing {task} qualified sweep module")
        require(git_blob_sha(path) == spec["blob_sha"], f"{task} sweep blob drift")

    deps = {
        "MC-005": ("CAPABILITY_ACCEPTED", "adec886597a06345fdfdf65ee018596cd396d249"),
        "MC-018": ("COMPLETED_RESEARCH", "085f864b4bd58b38f154b6c9d58d9e68b60ee7ec"),
        "MC-019": ("COMPLETED_RESEARCH", "4456c964315c10b46ce61a5a8d4a45e8025730b7"),
        "MC-020": ("COMPLETED_RESEARCH", "19504a35f47bca710bb6369abb723de83d1afede"),
        "MC-021": ("COMPLETED_RESEARCH", "442397474c596bc3a73e9442e4ab2f955e19b0e6"),
        "MC-022": ("COMPLETED_RESEARCH", "8ca7cfd0d098d746394cab71257b1dfc6e3a7250"),
        "MC-023": ("COMPLETED_RESEARCH", "15cd3b128cdaa14370594debd490e76a4a0d6b23"),
        "MC-026": ("COMPLETED_RESEARCH", "185693afc30b77097031ced218c9ae19fb1653ac"),
    }
    for task, (kind, blob) in deps.items():
        path = root / "research" / "machining-completeness" / "tasks" / task / "outcome.json"
        obj = json.loads(path.read_text())
        require(obj["task"] == task and obj["result_kind"] == kind, f"{task} dependency result")
        require(git_blob_sha(path) == blob, f"{task} dependency outcome drift")

    proof = json.loads((root / "research/machining-completeness/proof-obligations-v1.json").read_text())
    obligations = {entry["id"]: entry for entry in proof["obligations"]}
    require(obligations["PO-02"]["integration_owner"] == "MC-031" and obligations["PO-02"]["state"] == "OPEN", "PO-02 must remain open while PB-007-02/03 survive")

    programme = json.loads((root / "research/machining-completeness/programme-v1.json").read_text())
    gates = {gate["id"]: gate for gate in programme["gates"]}
    require(gates["MC-A"]["state"] == "ACCEPTED", "MC-A capability dependency")
    require(gates["MC-B"]["state"] == "NOT_ESTABLISHED", "MC-B must not be promoted")
    require(programme["production_authorized"] is False and programme["expensive_execution_authorized"] is False, "execution authority unchanged")

    blockers = {b["id"]: b["status"] for b in outcome["blockers"]}
    require(blockers == {"PB-007-02":"OPEN","PB-007-03":"OPEN_PROPAGATED","PB-007-04":"OPEN_PROPAGATED"}, "outcome blocker state")
    require(outcome["result_kind"] == "COMPLETED_RESEARCH" and outcome["native_execution"] is False, "bounded outcome")

    registry = json.loads((root / "research/machining-completeness/outcomes-v1.json").read_text())
    reg = registry["tasks"]["MC-031"]
    require(reg["state"] == "COMPLETED_RESEARCH", "registry state")
    require(any(path.endswith("MC-031/outcome.json") for path in reg["accepted_artifacts"]), "registry outcome artifact")
    reg_blockers = {b["id"]: b["status"] for b in reg["blockers"]}
    require(reg_blockers == blockers, "registry blocker drift")

    workflow = (root / ".github/workflows/mc1-static.yml").read_text()
    require("tasks/MC-031/material_evaluator.py" in workflow and "tasks/MC-031/verify.py" in workflow, "MC031 compile wiring")
    require("mc_workflow.py verify MC-031" in workflow, "MC031 workflow verification")

    report = (HERE / "report.md").read_text().lower()
    for token in ("actual qualified", "26", "pb-007-02", "pb-007-03", "pb-007-04", "positive-volume", "source/audio/provenance", "mc-b"):
        require(token in report, f"report missing boundary token {token}")

    # Contract mutation attacks: each forbidden promotion must be detectable.
    attacks = [
        ("float", lambda x: x["truth_authority"].__setitem__("binary_float", True)),
        ("epsilon", lambda x: x["truth_authority"].__setitem__("epsilon_or_global_tolerance", True)),
        ("accelerator", lambda x: x["truth_authority"].__setitem__("accelerator_observation", True)),
        ("touch", lambda x: x["material_semantics"].__setitem__("touching_is_positive_volume_removal", True)),
        ("backend-id", lambda x: x["body_state_boundary"].__setitem__("durable_identity_authority", "backend_topology_id")),
        ("mc033", lambda x: x["body_state_boundary"].__setitem__("durable_connectivity_transition_owner", "MC-031")),
        ("promotion", lambda x: x.__setitem__("capability_promotions", ["MC-B"])),
        ("denominator", lambda x: x["operation_coverage"].pop("lathe_eccentric_turning")),
    ]
    def invariant(x):
        return (
            x["truth_authority"]["binary_float"] is False
            and x["truth_authority"]["epsilon_or_global_tolerance"] is False
            and x["truth_authority"]["accelerator_observation"] is False
            and x["material_semantics"]["touching_is_positive_volume_removal"] is False
            and x["body_state_boundary"]["durable_identity_authority"] == "canonical_journal_body_lineage"
            and x["body_state_boundary"]["durable_connectivity_transition_owner"] == "MC-033"
            and x["capability_promotions"] == []
            and set(x["operation_coverage"]) == set(MC026.REQUIRED_OPERATIONS)
        )
    require(invariant(contract), "baseline contract invariant")
    for name, mutate in attacks:
        attacked = deepcopy(contract); mutate(attacked)
        require(not invariant(attacked), f"contract attack not discriminated: {name}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        args.contract = args.self_test = True
    if args.self_test:
        self_test()
        print("MC-031 material evaluator self-test passed")
    if args.contract:
        contract_test(ROOT)
        self_test()
        print("MC-031 material evaluator contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
