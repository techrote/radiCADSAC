#!/usr/bin/env python3
"""Deterministic contract, physical-boundary and adversarial verification for MC-012."""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
CONTRACT_PATH = TASK / "physical-corpus-f05-f08-v1.json"
ORACLE_PATH = TASK / "fixture_oracle.py"
FAMILIES_PATH = ROOT / "research/machining-completeness/fixture-families-v1.json"
OUTCOMES_PATH = ROOT / "research/machining-completeness/outcomes-v1.json"

PROTECTED_BLOBS = {
    "research/rcs-003/corpus-v1.json": "da56bfa89653dd8c7886d48e4c29f9653e2872f4",
    "research/rcs-002/fixtures/lathe-finishing-pass-v1.json": "f87b160d4d78d8a608969d183b6b165a9e57a0d4",
    "research/rcs-002/fixtures/mill-cut-through-v1.json": "cb93d31e3e0c018c0e971ec1a8144be085f6e5fd",
    "research/rcs-011/measured-summary-v1.json": "56be7de5a5b848007053597a437aaccbae4ed434",
    "research/rcs-012/measured-summary-v1.json": "45ce54d553a711e7249998fc18cca586e36569fd",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: str) -> str:
    proc = subprocess.run(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def family(contract, ident):
    rows = [row for row in contract["families"] if row["id"] == ident]
    if len(rows) != 1:
        fail(f"{ident} family multiplicity mismatch")
    return rows[0]


def operation(row, ident):
    rows = [op for op in row.get("operations", []) if op["id"] == ident]
    if len(rows) != 1:
        fail(f"{row['id']} missing or duplicates operation {ident}")
    return rows[0]


def validate_independence_meta(meta):
    if meta.get("decisive_shared_geometry_imports") != []:
        fail("fixture oracle declares shared decisive candidate/historical geometry")
    if meta.get("candidate_output_used_for_expected_truth") is not False:
        fail("candidate output cannot define expected truth")
    if meta.get("expected_truth_origin") != "preregistered exact MC-012 fixture literals and analytic rational geometry":
        fail("expected-truth origin drift")


def verify_dependencies(contract):
    for dep in contract["dependencies"]:
        got = git_blob(dep["path"])
        if got != dep["blob_sha"]:
            fail(f"dependency artifact drift for {dep['task']}: {got} != {dep['blob_sha']}")


def verify_oracle_independence(contract):
    source = ORACLE_PATH.read_text(encoding="utf-8")
    meta = contract["oracle_independence"]["fixture_specific_path"]
    if hashlib.sha256(source.encode()).hexdigest() != meta["source_sha256"]:
        fail("fixture oracle source digest drift")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    if imported - set(meta["allowed_import_roots"]):
        fail(f"fixture oracle gained unapproved imports: {sorted(imported - set(meta['allowed_import_roots']))}")
    validate_independence_meta(meta)
    lowered = source.lower()
    forbidden = ("research/rcs", "rcs-021", "material_oracle", "tridexel", "manifold_fallback", "opencascade")
    hits = [x for x in forbidden if x in lowered]
    if hits:
        fail(f"fixture oracle leaked decisive historical/candidate implementation: {hits}")


def verify_f05(row, oracle):
    pocket = operation(row, "F05-P")
    v1 = operation(row, "F05-V1")
    v2 = operation(row, "F05-V2")
    x1 = operation(row, "F05-X1")
    a = row["oracle_assertions"]
    top = Fraction(row["stock"]["box"][2][1])
    xmin = Fraction(row["stock"]["box"][0][0])
    if not (Fraction(v1["axial_interval"][1]) > top and Fraction(v2["axial_interval"][1]) > top):
        fail("F05 vertical tools no longer have exterior top approach")
    if not Fraction(x1["axial_interval"][0]) < xmin:
        fail("F05 cross-bore no longer has exterior side approach")
    if oracle.point_in_box(a["access_pocket_probe"]["point"], pocket["box"]) is not a["access_pocket_probe"]["removed"]:
        fail("F05 access-pocket witness mismatch")
    for key, vop in (("junction_v1", v1), ("junction_v2", v2)):
        probe = a[key]
        vertical = oracle.finite_cylinder_contains(probe["point"], vop["axis"], vop["center"], vop["axial_interval"], vop["radius"])
        cross = oracle.finite_cylinder_contains(probe["point"], x1["axis"], x1["center"], x1["axial_interval"], x1["radius"])
        if vertical is not True or cross is not True or probe["removed"] is not True:
            fail(f"F05 {key} stopped witnessing an intersecting passage")
    wall = a["thin_wall"]
    actual = oracle.finite_cylinder_contains(wall["probe"], v2["axis"], [wall["actual_second_center_x"], v2["center"][1]], v2["axial_interval"], v2["radius"]) or oracle.finite_cylinder_contains(wall["probe"], v1["axis"], v1["center"], v1["axial_interval"], v1["radius"])
    zero = oracle.finite_cylinder_contains(wall["probe"], v2["axis"], [wall["zero_wall_second_center_x"], v2["center"][1]], v2["axial_interval"], v2["radius"]) or oracle.finite_cylinder_contains(wall["probe"], v1["axis"], v1["center"], v1["axial_interval"], v1["radius"])
    if actual is not wall["actual_removed"] or zero is not wall["zero_wall_removed"] or actual == zero:
        fail("F05 positive thin-wall boundary collapsed")
    spacing = Fraction(v2["center"][0]) - Fraction(v1["center"][0])
    thickness = spacing - Fraction(v1["radius"]) - Fraction(v2["radius"])
    if thickness != Fraction(wall["thickness"]) or thickness <= 0:
        fail("F05 exact positive wall thickness drift")


def verify_f06(row, oracle):
    p1 = operation(row, "F06-FINISH-1")
    p2 = operation(row, "F06-FINISH-2")
    part = operation(row, "F06-PART")
    a = row["oracle_assertions"]
    if not (Fraction(part["radial_approach"][0]) > Fraction(row["stock"]["radius"]) and Fraction(part["radial_approach"][1]) == 0):
        fail("F06 parting tool no longer approaches from outside and reaches the axis")
    if max(Fraction(x) for x in p1["z_interval"] + p2["z_interval"]) >= Fraction("72"):
        fail("F06 finish path entered the stated jaw region")
    probe = a["nose_overlap"]
    got1 = oracle.lathe_nose_sweep_removes(probe["radius"], probe["z"], p1["nose_center_radius"], p1["z_interval"], p1["nose_radius"])
    got2 = oracle.lathe_nose_sweep_removes(probe["radius"], probe["z"], p2["nose_center_radius"], p2["z_interval"], p2["nose_radius"])
    sharp = oracle.lathe_nose_sweep_removes(probe["radius"], probe["z"], p1["nose_center_radius"], p1["z_interval"], "0")
    if got1 is not probe["pass1_removed"] or got2 is not probe["pass2_removed"] or sharp is not probe["sharp_point_removed"]:
        fail("F06 finite nose-radius/overlap witness mismatch")
    boundary = a["parting_boundary"]
    if oracle.parting_component_count(boundary["complete_remaining_core_radius"]) != boundary["complete_components"]:
        fail("F06 complete parting did not yield two bodies")
    if oracle.parting_component_count(boundary["short_remaining_core_radius"]) != boundary["short_components"]:
        fail("F06 short-of-axis parting incorrectly separated bodies")
    if set(row["body_transition"]["at_complete_parting"]["to"]) != set(a["head_body_ids"]):
        fail("F06 durable output body identities drifted")
    if row["body_transition"]["at_complete_parting"]["retain_all_positive_volume_bodies"] is not True:
        fail("F06 allows positive-volume cutoff body deletion")


def final_removed_f07(row, oracle, point):
    t1 = operation(row, "F07-T1")
    mill = operation(row, "F07-M1")
    t2 = operation(row, "F07-T2")
    return oracle.lathe_od_removes(point, t1["final_radius"], t1["z_interval"]) or oracle.finite_cylinder_contains(point, mill["axis_common"], mill["center_common_yz"], mill["axial_interval_common"], mill["radius"]) or oracle.lathe_od_removes(point, t2["final_radius"], t2["z_interval"])


def verify_f07(row, oracle):
    setups = {s["id"]: s for s in row["setups"]}
    mill_setup = setups["S-F07-M"]
    matrix = mill_setup["common_from_machine"]["matrix"]
    mill = operation(row, "F07-M1")
    if not (Fraction(mill["axial_interval_common"][1]) > Fraction(row["stock"]["radius"]) and Fraction(mill["axial_interval_common"][0]) < Fraction(operation(row, "F07-T1")["final_radius"])):
        fail("F07 mill no longer approaches from exterior and penetrates the turned surface")
    if not oracle.is_rotation_matrix(matrix):
        fail("F07 mill handoff transform is not a proper exact rotation")
    axis = [str(v) for v in oracle.matrix_vec(matrix, ["0", "0", "1"])]
    if axis != row["oracle_assertions"]["mill_rotation_axis"]:
        fail("F07 machine +Z no longer maps to common +X")
    selected = [s["selected_body_id"] for s in row["setups"]]
    if selected != [row["oracle_assertions"]["durable_body_id"]] * 3:
        fail("F07 durable body identity was not preserved across setup changes")
    sym = row["oracle_assertions"]["broken_symmetry"]
    removed = final_removed_f07(row, oracle, sym["removed_point"])
    survivor = final_removed_f07(row, oracle, sym["same_radius_survivor"])
    if removed is not sym["removed_final"] or survivor is not sym["survivor_final"] or removed == survivor:
        fail("F07 broken-symmetry witness was lost on lathe return")
    active = row["oracle_assertions"]["return_lathe_active"]
    t1 = operation(row, "F07-T1")
    t2 = operation(row, "F07-T2")
    g1 = oracle.lathe_od_removes(active["point"], t1["final_radius"], t1["z_interval"])
    gm = oracle.finite_cylinder_contains(active["point"], mill["axis_common"], mill["center_common_yz"], mill["axial_interval_common"], mill["radius"])
    g2 = oracle.lathe_od_removes(active["point"], t2["final_radius"], t2["z_interval"])
    if (g1, gm, g2) != (active["after_first_lathe_removed"], active["after_mill_removed"], active["after_second_lathe_removed"]):
        fail("F07 second lathe pass activity witness mismatch")


def verify_f08(row, oracle):
    starter = operation(row, "F08-ACCESS")
    ts = operation(row, "F08-TSLOT")
    a = row["oracle_assertions"]
    stock_top = Fraction(row["stock"]["box"][2][1])
    if not Fraction(starter["axial_interval"][1]) > stock_top:
        fail("F08 starter pocket no longer enters from above stock")
    if ts["path_xy"][0] != starter["center"]:
        fail("F08 T-slot head no longer starts inside the prepared access pocket")
    access = a["access"]
    if oracle.t_slot_accessible(access["radius"], access["head_radius"], access["neck_radius"]) is not access["accessible"]:
        fail("F08 valid starter-access witness rejected")
    if oracle.t_slot_accessible(access["too_small_access_radius"], access["head_radius"], access["neck_radius"]) is not access["too_small_accessible"]:
        fail("F08 inaccessible-head corruption escaped")
    if Fraction(access["radius"]) - Fraction(access["head_radius"]) != Fraction(access["margin"]):
        fail("F08 insertion clearance margin drift")
    shadow = a["undercut_shadow"]
    full = oracle.t_slot_sweep_removes(shadow["point"], ts["path_xy"], ts["head_radius"], ts["head_z"], ts["neck_radius"], ts["neck_z"])
    p = shadow["point"]
    d2 = oracle.distance2_point_segment_2d((p[0], p[1]), ts["path_xy"][0], ts["path_xy"][1])
    neck_only = d2 <= Fraction(ts["neck_radius"]) ** 2
    if full is not shadow["full_tslot_removed"] or neck_only is not shadow["neck_only_removed"] or full == neck_only:
        fail("F08 undercut shadow no longer distinguishes wide head from neck-only cutter")
    for key in ("roof_survivor", "neck_slot"):
        probe = a[key]
        got = oracle.t_slot_sweep_removes(probe["point"], ts["path_xy"], ts["head_radius"], ts["head_z"], ts["neck_radius"], ts["neck_z"])
        if got is not probe["full_tslot_removed"]:
            fail(f"F08 {key} witness mismatch")


def verify_registry(contract):
    rows = load(FAMILIES_PATH)["families"]
    expected_ids = [f"F{i:02d}" for i in range(1, 17)]
    if [row["id"] for row in rows] != expected_ids:
        fail("fixture-family denominator drift")
    outcomes = load(OUTCOMES_PATH)["tasks"]
    for row in rows:
        if row.get("mandatory") is not True:
            fail(f"{row['id']} stopped being mandatory")
        if row["id"] in {f"F{i:02d}" for i in range(1, 9)}:
            if row.get("state") != "BUILT":
                fail(f"{row['id']} regressed from MC-012 BUILT state")
            continue
        if row.get("state") not in {"UNBUILT", "BUILT"}:
            fail(f"{row['id']} has unknown later-owner state {row.get('state')}")
        if row.get("state") == "BUILT" and outcomes.get(row.get("owner"), {}).get("state") not in {"COMPLETED_RESEARCH", "CAPABILITY_ACCEPTED"}:
            fail(f"{row['id']} advanced to BUILT without completed owner {row.get('owner')}")
    if outcomes["MC-012"].get("state") != "COMPLETED_RESEARCH":
        fail("MC-012 outcome registry was not reconciled")
    if contract["construction_scope"]["still_unbuilt"] != [f"F{i:02d}" for i in range(9, 17)]:
        fail("MC-012 narrowed or skipped the remaining corpus denominator")
    if contract["programme_state"]["MC-B"] != "NOT_ESTABLISHED" or contract["programme_state"]["MC-1"] != "NOT_ESTABLISHED":
        fail("fixture construction cannot promote MC-B or MC-1")
    if contract["programme_state"]["native_or_paid_campaign_run"] is not False:
        fail("MC-012 unexpectedly claims native/paid execution")


def verify_protected_sources(contract):
    for path, expected in PROTECTED_BLOBS.items():
        if git_blob(path) != expected:
            fail(f"protected historical source drift: {path}")
    proc = subprocess.run(["git", "diff", "--name-only", f"{contract['source_baseline']}..HEAD"], cwd=ROOT, check=True, capture_output=True, text=True)
    changed = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    forbidden = sorted(path for path in changed if path.startswith("research/rcs-"))
    if forbidden:
        fail(f"MC-012 edited protected historical sources: {forbidden}")


def adversarial_controls(contract, oracle):
    try:
        oracle.q(0.1)
    except TypeError:
        pass
    else:
        fail("binary float accepted as authority-path coordinate")
    corrupt = copy.deepcopy(contract["oracle_independence"]["fixture_specific_path"])
    corrupt["candidate_output_used_for_expected_truth"] = True
    try:
        validate_independence_meta(corrupt)
    except AssertionError:
        pass
    else:
        fail("candidate-defined expected truth corruption escaped")
    corrupt = copy.deepcopy(contract["oracle_independence"]["fixture_specific_path"])
    corrupt["decisive_shared_geometry_imports"] = ["research/rcs-021/field.py"]
    try:
        validate_independence_meta(corrupt)
    except AssertionError:
        pass
    else:
        fail("shared decisive geometry corruption escaped")
    f05 = family(contract, "F05")
    wall = f05["oracle_assertions"]["thin_wall"]
    if Fraction(wall["thickness"]) <= 0:
        fail("F05 no longer contains a positive wall")
    v2 = operation(f05, "F05-V2")
    if not oracle.finite_cylinder_contains(wall["probe"], v2["axis"], [wall["zero_wall_second_center_x"], v2["center"][1]], v2["axial_interval"], v2["radius"]):
        fail("F05 zero-wall adversarial member stopped erasing the wall probe")
    f06 = family(contract, "F06")
    nose = f06["oracle_assertions"]["nose_overlap"]
    p1 = operation(f06, "F06-FINISH-1")
    if oracle.lathe_nose_sweep_removes(nose["radius"], nose["z"], p1["nose_center_radius"], p1["z_interval"], "0"):
        fail("F06 sharp-point corruption became equivalent to finite nose radius")
    if oracle.parting_component_count("1/1000000") != 1:
        fail("F06 arbitrarily small positive core was rounded into separation")
    f07 = family(contract, "F07")
    sym = f07["oracle_assertions"]["broken_symmetry"]
    if final_removed_f07(f07, oracle, sym["removed_point"]) == final_removed_f07(f07, oracle, sym["same_radius_survivor"]):
        fail("F07 axisymmetry-reset corruption no longer discriminates")
    identity = [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]]
    if [str(v) for v in oracle.matrix_vec(identity, ["0", "0", "1"])] == f07["oracle_assertions"]["mill_rotation_axis"]:
        fail("F07 identity-transform corruption escaped")
    f08 = family(contract, "F08")
    access = f08["oracle_assertions"]["access"]
    if oracle.t_slot_accessible(access["too_small_access_radius"], access["head_radius"], access["neck_radius"]):
        fail("F08 cutter head teleports through undersized access")
    ts = operation(f08, "F08-TSLOT")
    shadow = f08["oracle_assertions"]["undercut_shadow"]["point"]
    d2 = oracle.distance2_point_segment_2d((shadow[0], shadow[1]), ts["path_xy"][0], ts["path_xy"][1])
    if d2 <= Fraction(ts["neck_radius"]) ** 2:
        fail("F08 undercut witness accidentally fits a neck-only cutter")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if not (args.contract or args.self_test):
        args.contract = True
    contract = load(CONTRACT_PATH)
    if contract.get("task") != "MC-012" or contract.get("schema") != "radicadsac-mc-physical-corpus/1.0":
        fail("MC-012 corpus identity/schema drift")
    if [row["id"] for row in contract["families"]] != ["F05", "F06", "F07", "F08"]:
        fail("MC-012 family denominator/order drift")
    verify_dependencies(contract)
    verify_oracle_independence(contract)
    oracle = load_module("mc012_fixture_oracle", ORACLE_PATH)
    verify_f05(family(contract, "F05"), oracle)
    verify_f06(family(contract, "F06"), oracle)
    verify_f07(family(contract, "F07"), oracle)
    verify_f08(family(contract, "F08"), oracle)
    verify_registry(contract)
    verify_protected_sources(contract)
    adversarial_controls(contract, oracle)
    print("MC-012 contract, physical-boundary and adversarial verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
