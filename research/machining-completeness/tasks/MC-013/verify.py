#!/usr/bin/env python3
"""Deterministic contract, physical-boundary and adversarial verification for MC-013."""
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
CONTRACT_PATH = TASK / "physical-corpus-f09-f12-v1.json"
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
    proc = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
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
    if meta.get("expected_truth_origin") != "preregistered exact MC-013 fixture literals and analytic rational geometry":
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
    forbidden = (
        "research/rcs",
        "rcs-021",
        "material_oracle",
        "tridexel",
        "manifold_fallback",
        "opencascade",
    )
    hits = [x for x in forbidden if x in lowered]
    if hits:
        fail(f"fixture oracle leaked decisive historical/candidate implementation: {hits}")


def synchronized_result(row, oracle, probe):
    op = operation(row, "F09-SYNC")
    return oracle.synchronized_turning_removes(
        probe["body_theta_turns"],
        probe["z"],
        probe["radius"],
        op["spindle_phase_turns"][0],
        op["spindle_phase_turns"][1],
        op["feed_z"][0],
        op["feed_z"][1],
        op["axial_half_width"],
        op["radial_approach"][1],
    )


def verify_f09(row, oracle):
    op = operation(row, "F09-SYNC")
    stock_radius = Fraction(row["stock"]["radius"])
    radial = [Fraction(x) for x in op["radial_approach"]]
    if not (radial[0] > stock_radius and radial[1] < stock_radius):
        fail("F09 radial tool no longer approaches from exterior and enters stock")
    if not (Fraction(op["spindle_phase_turns"][0]) < Fraction(op["spindle_phase_turns"][1])):
        fail("F09 phase gate stopped being an ordered non-wrapping interval")
    assertions = row["oracle_assertions"]
    for key in ("mid_correlated", "same_phase_wrong_feed", "start_equality", "end_equality", "end_inside", "end_outside"):
        probe = assertions[key]
        if synchronized_result(row, oracle, probe) is not probe["removed"]:
            fail(f"F09 {key} phase/feed witness mismatch")
    pair = assertions["phase_averaging_forbidden"]
    removed = {"body_theta_turns": pair["body_theta_removed"], "z": pair["same_z"], "radius": pair["same_radius"]}
    survivor = {"body_theta_turns": pair["body_theta_survivor"], "z": pair["same_z"], "radius": pair["same_radius"]}
    if synchronized_result(row, oracle, removed) is not True or synchronized_result(row, oracle, survivor) is not False:
        fail("F09 phase averaging no longer changes same-radius/same-z material truth")


def verify_f10(row, oracle):
    assertions = row["oracle_assertions"]
    slots = assertions["slot_x_intervals"]
    widths = tuple(str(v) for v in oracle.retained_slab_widths(row["stock"]["box"][0][0], row["stock"]["box"][0][1], slots))
    if list(widths) != assertions["expected_retained_widths"]:
        fail("F10 retained slab widths drifted")
    if len(widths) != 8:
        fail("F10 no longer yields eight positive retained slabs")
    for key in ("through", "positive_web", "negative_overtravel"):
        case = assertions[key]
        got = oracle.cross_slot_component_count(len(slots), case["remaining_web"])
        if got != case["components"]:
            fail(f"F10 {key} component boundary mismatch")
    if len(assertions["retained_body_ids"]) != 8 or len(set(assertions["retained_body_ids"])) != 8:
        fail("F10 retained body identities are not eight unique durable bodies")
    transition = row["body_transition"]["through_slots"]
    if transition.get("retain_all_positive_volume_bodies") is not True:
        fail("F10 permits deletion of positive-volume separated bodies")
    if transition["to"] != assertions["retained_body_ids"]:
        fail("F10 body transition identities drifted")


def pair_classification(oracle, item):
    signed = oracle.signed_pair_clearance2(item["center_a"], item["radius_a"], item["center_b"], item["radius_b"])
    return oracle.classify_signed(signed)


def verify_f11(row, oracle):
    assertions = row["oracle_assertions"]
    for key in ("base_pair", "separated_pair", "penetrating_pair"):
        item = assertions[key]
        if pair_classification(oracle, item) != item["classification"]:
            fail(f"F11 {key} singular-boundary classification mismatch")
    if [assertions[k]["classification"] for k in ("separated_pair", "base_pair", "penetrating_pair")] != ["SEPARATED", "TANGENT", "PENETRATING"]:
        fail("F11 signed/equality ordering drifted")
    tangent = assertions["tangent_point"]
    base = assertions["base_pair"]
    a = oracle.signed_circle_clearance2(tangent["point_yz"], base["center_a"], base["radius_a"])
    b = oracle.signed_circle_clearance2(tangent["point_yz"], base["center_b"], base["radius_b"])
    if str(a) != tangent["to_a_clearance2"] or str(b) != tangent["to_b_clearance2"]:
        fail("F11 tangent point stopped lying exactly on both cutter boundaries")
    if assertions.get("positive_volume_not_deletable") is not True:
        fail("F11 lost positive-volume preservation rule")


def verify_f12(row, oracle):
    assertions = row["oracle_assertions"]
    local = assertions["local"]
    translated = assertions["translated"]
    zero = assertions["zero"]
    negative = assertions["negative"]
    if oracle.retained_web(local["left_end"], local["right_start"]) != Fraction(local["gap"]):
        fail("F12 local exact gap drift")
    if oracle.web_connectivity(local["left_end"], local["right_start"]) != local["state"]:
        fail("F12 local positive-web state drift")
    translated_gap = oracle.translated_gap(local["left_end"], local["right_start"], translated["translation"])
    if translated_gap != Fraction(translated["gap"]):
        fail("F12 exact translation consumed precision")
    if Fraction(local["left_end"]) + Fraction(translated["translation"]) != Fraction(translated["left_end"]):
        fail("F12 translated left endpoint mismatch")
    if Fraction(local["right_start"]) + Fraction(translated["translation"]) != Fraction(translated["right_start"]):
        fail("F12 translated right endpoint mismatch")
    if oracle.web_connectivity(translated["left_end"], translated["right_start"]) != translated["state"]:
        fail("F12 translated positive-web state drift")
    for case, expected in ((zero, "ZERO_WIDTH_LIMIT"), (negative, "OVERLAP_NO_WEB")):
        if oracle.retained_web(case["left_end"], case["right_start"]) != Fraction(case["gap"]):
            fail("F12 signed boundary gap drift")
        if oracle.web_connectivity(case["left_end"], case["right_start"]) != expected:
            fail("F12 zero/negative precision boundary collapsed")
    rot = assertions["rotation_probe"]
    got = [str(v) for v in oracle.rotate90_xy(rot["input"])]
    if got != rot["expected"]:
        fail("F12 exact rotation witness drift")
    stock_extent = Fraction(row["stock"]["box"][0][1]) - Fraction(row["stock"]["box"][0][0])
    ratio = stock_extent / Fraction(local["gap"])
    if str(ratio) != assertions["scale_ratio_stock_to_gap"]:
        fail("F12 scale/precision ratio drift")
    selected = [setup["selected_body_id"] for setup in row["setups"]]
    if selected != [row["stock"]["body_id"], row["stock"]["body_id"]]:
        fail("F12 durable body identity changed across rotated setup")


def verify_registry(contract):
    rows = load(FAMILIES_PATH)["families"]
    expected_ids = [f"F{i:02d}" for i in range(1, 17)]
    if [row["id"] for row in rows] != expected_ids:
        fail("fixture-family denominator drift")
    outcomes = load(OUTCOMES_PATH)["tasks"]
    for row in rows:
        if row.get("mandatory") is not True:
            fail(f"{row['id']} stopped being mandatory")
        num = int(row["id"][1:])
        if num <= 12:
            if row.get("state") != "BUILT":
                fail(f"{row['id']} regressed from required BUILT state")
            continue
        if row.get("state") not in {"UNBUILT", "BUILT"}:
            fail(f"{row['id']} has unknown later-owner state {row.get('state')}")
        if row.get("state") == "BUILT" and outcomes.get(row.get("owner"), {}).get("state") not in {"COMPLETED_RESEARCH", "CAPABILITY_ACCEPTED"}:
            fail(f"{row['id']} advanced to BUILT without completed owner {row.get('owner')}")
    if outcomes["MC-013"].get("state") != "COMPLETED_RESEARCH":
        fail("MC-013 outcome registry was not reconciled")
    if contract["construction_scope"]["still_unbuilt"] != [f"F{i:02d}" for i in range(13, 17)]:
        fail("MC-013 narrowed or skipped the remaining corpus denominator")
    if contract["programme_state"]["MC-B"] != "NOT_ESTABLISHED" or contract["programme_state"]["MC-1"] != "NOT_ESTABLISHED":
        fail("fixture construction cannot promote MC-B or MC-1")
    if contract["programme_state"]["native_or_paid_campaign_run"] is not False:
        fail("MC-013 unexpectedly claims native/paid execution")


def verify_protected_sources(contract):
    for path, expected in PROTECTED_BLOBS.items():
        if git_blob(path) != expected:
            fail(f"protected historical source drift: {path}")
    proc = subprocess.run(["git", "diff", "--name-only", f"{contract['source_baseline']}..HEAD"], cwd=ROOT, check=True, capture_output=True, text=True)
    changed = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    forbidden = sorted(path for path in changed if path.startswith("research/rcs-"))
    if forbidden:
        fail(f"MC-013 edited protected historical sources: {forbidden}")


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

    f09 = family(contract, "F09")
    pair = f09["oracle_assertions"]["phase_averaging_forbidden"]
    removed = {"body_theta_turns": pair["body_theta_removed"], "z": pair["same_z"], "radius": pair["same_radius"]}
    survivor = {"body_theta_turns": pair["body_theta_survivor"], "z": pair["same_z"], "radius": pair["same_radius"]}
    if synchronized_result(f09, oracle, removed) == synchronized_result(f09, oracle, survivor):
        fail("F09 phase-collapsing corruption escaped")
    if oracle.phase_window_contains("1001/4000", "1/8", "1/4"):
        fail("F09 outside signed phase neighbour was epsilon-rounded into gate")

    f10 = family(contract, "F10")
    slots = len(f10["oracle_assertions"]["slot_x_intervals"])
    if oracle.cross_slot_component_count(slots, "1/1000000000") != 1:
        fail("F10 tiny positive support web was rounded into eight components")
    if oracle.cross_slot_component_count(slots, "0") != 8:
        fail("F10 exact separation threshold lost component multiplicity")

    f11 = family(contract, "F11")
    a = f11["oracle_assertions"]
    if pair_classification(oracle, a["base_pair"]) != "TANGENT":
        fail("F11 exact tangency collapsed")
    if pair_classification(oracle, a["separated_pair"]) == pair_classification(oracle, a["penetrating_pair"]):
        fail("F11 signed singular neighbours became indistinguishable")

    f12 = family(contract, "F12")
    local = f12["oracle_assertions"]["local"]
    translated = f12["oracle_assertions"]["translated"]
    if oracle.retained_web(local["left_end"], local["right_start"]) != oracle.retained_web(translated["left_end"], translated["right_start"]):
        fail("F12 translation changed exact local precision witness")
    if oracle.web_connectivity("999", "9990000001/10000000") != "CONNECTED_POSITIVE_WEB":
        fail("F12 smaller positive translated web was rounded away")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if not (args.contract or args.self_test):
        args.contract = True

    contract = load(CONTRACT_PATH)
    if contract.get("task") != "MC-013" or contract.get("schema") != "radicadsac-mc-physical-corpus/1.0":
        fail("MC-013 corpus identity/schema drift")
    if [row["id"] for row in contract["families"]] != ["F09", "F10", "F11", "F12"]:
        fail("MC-013 family denominator/order drift")

    verify_dependencies(contract)
    verify_oracle_independence(contract)
    oracle = load_module("mc013_fixture_oracle", ORACLE_PATH)
    verify_f09(family(contract, "F09"), oracle)
    verify_f10(family(contract, "F10"), oracle)
    verify_f11(family(contract, "F11"), oracle)
    verify_f12(family(contract, "F12"), oracle)
    verify_registry(contract)
    verify_protected_sources(contract)
    adversarial_controls(contract, oracle)
    print("MC-013 contract, physical-boundary and adversarial verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
