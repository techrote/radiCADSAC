#!/usr/bin/env python3
"""Deterministic contract, boundary and adversarial verification for MC-011."""
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
CONTRACT_PATH = TASK / "physical-corpus-f01-f04-v1.json"
ORACLE_PATH = TASK / "fixture_oracle.py"
CELL_ORACLE_PATH = ROOT / "research/machining-completeness/tasks/MC-010/independent_exact_oracle.py"
FAMILIES_PATH = ROOT / "research/machining-completeness/fixture-families-v1.json"
OUTCOMES_PATH = ROOT / "research/machining-completeness/outcomes-v1.json"


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


def flatten_box(box):
    if len(box) != 3 or any(len(pair) != 2 for pair in box):
        fail("stock box must be three [lo,hi] pairs")
    return [box[0][0], box[0][1], box[1][0], box[1][1], box[2][0], box[2][1]]


def operation(family, ident):
    for op in family.get("operations", []):
        if op.get("id") == ident:
            return op
    fail(f"{family['id']} missing operation {ident}")


def verify_dependencies(contract):
    for dep in contract["dependencies"]:
        got = git_blob(dep["path"])
        if got != dep["blob_sha"]:
            fail(f"dependency artifact drift for {dep['task']}: {got} != {dep['blob_sha']}")


def validate_independence_meta(meta):
    if meta.get("decisive_shared_geometry_imports") != []:
        fail("fixture-specific oracle declares decisive shared candidate geometry")
    if meta.get("candidate_output_used_for_expected_truth") is not False:
        fail("candidate output cannot define fixture expected truth")
    if meta.get("expected_truth_origin") != "preregistered exact MC-011 fixture literals and analytic rational geometry":
        fail("fixture expected-truth origin drift")


def verify_oracle_independence(contract):
    source = ORACLE_PATH.read_text(encoding="utf-8")
    meta = contract["oracle_independence"]["fixture_specific_path"]
    got = hashlib.sha256(source.encode()).hexdigest()
    if got != meta["source_sha256"]:
        fail(f"fixture oracle source digest drift: {got} != {meta['source_sha256']}")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    allowed = set(meta["allowed_import_roots"])
    if imported - allowed:
        fail(f"fixture oracle gained unapproved imports: {sorted(imported - allowed)}")
    validate_independence_meta(meta)
    lowered = source.lower()
    forbidden = ("research/rcs", "rcs-021", "material_oracle", "tridexel", "manifold_fallback", "opencascade")
    hits = [x for x in forbidden if x in lowered]
    if hits:
        fail(f"fixture-specific oracle leaked candidate/historical decisive implementation: {hits}")
    cell = contract["oracle_independence"]["cell_control_path"]
    if git_blob(cell["implementation"]) != cell["blob_sha"]:
        fail("MC-010 exact-cell control drift")


def verify_f01(family, oracle):
    xop = operation(family, "F01-X")
    expected = family["oracle_assertions"]["crossing_point"]
    got = oracle.flat_axis_sweep_removes(
        expected["point"], xop["path"], xop["radius"], xop["axis"], xop["axial_interval"]
    )
    if got is not expected["removed"]:
        fail("F01 self-crossing point witness mismatch")

    tangent = operation(family, "F01-T0")
    signed = family["oracle_assertions"]["tangent_signed_neighbour"]
    got0 = oracle.flat_axis_sweep_removes(
        signed["point"], tangent["path"], tangent["radius"], tangent["axis"], tangent["axial_interval"]
    )
    if got0 is not signed["tangent_removed"]:
        fail("F01 exact tangent acquired positive interior removal")
    penetrating = copy.deepcopy(tangent["path"])
    for point in penetrating:
        point[1] = signed["penetrating_path_y"]
    got1 = oracle.flat_axis_sweep_removes(
        signed["point"], penetrating, tangent["radius"], tangent["axis"], tangent["axial_interval"]
    )
    if got1 is not signed["penetrating_removed"] or got0 == got1:
        fail("F01 signed tangent neighbour collapsed")

    j1 = operation(family, "F01-J1")
    j2 = operation(family, "F01-J2")
    delta = abs(Fraction(j2["path"][0][1]) - Fraction(j1["path"][0][1]))
    if delta != Fraction(family["oracle_assertions"]["jitter_delta"]):
        fail("F01 exact jitter amplitude drift")


def f02_cell_result(family, case, cell):
    stock = cell.Box.make(*flatten_box(family["stock"]["box"]))
    cut = cell.Box.make(*case["cell_cut_box"])
    material = cell.subtract_many([stock], [cut])
    return cell.total_volume(material), cell.component_count(material)


def verify_f02(family, oracle, cell):
    cases = {case["id"]: case for case in family["boundary_cases"]}
    if set(cases) != {"WEB-POSITIVE", "WEB-ZERO", "WEB-NEGATIVE"}:
        fail("F02 signed threshold denominator drift")
    for case in cases.values():
        volume, components = f02_cell_result(family, case, cell)
        if volume != Fraction(case["expected_volume"]) or components != case["expected_components"]:
            fail(f"F02 {case['id']} cell oracle mismatch")

    probe = family["oracle_assertions"]["web_probe"]
    template = family["operation_template"]
    positive = cases["WEB-POSITIVE"]
    zero = cases["WEB-ZERO"]
    pos_removed = oracle.flat_axis_sweep_removes(
        probe,
        template["path"],
        template["radius"],
        template["axis"],
        [positive["tip_z"], template["upper_axial"]],
    )
    zero_removed = oracle.flat_axis_sweep_removes(
        probe,
        template["path"],
        template["radius"],
        template["axis"],
        [zero["tip_z"], template["upper_axial"]],
    )
    if pos_removed is not family["oracle_assertions"]["positive_case_probe_removed"]:
        fail("F02 positive-volume web probe was erased")
    if zero_removed is not family["oracle_assertions"]["zero_case_probe_removed"]:
        fail("F02 exact separation threshold probe mismatch")
    if not (cases["WEB-POSITIVE"]["expected_components"] == 1 and cases["WEB-ZERO"]["expected_components"] == 2):
        fail("F02 connectivity threshold no longer discriminates")


def _offset(point, unit, amount):
    return [
        str(Fraction(p) + Fraction(amount) * Fraction(n))
        for p, n in zip(point, unit)
    ]


def verify_f03(family, oracle):
    op = family["operation"]
    assertions = family["oracle_assertions"]
    tangent = assertions["tangent_point"]
    if oracle.ball_polyline_sweep_removes(tangent, op["path"], op["radius"]) is not assertions["tangent_removed"]:
        fail("F03 exact spherical tangent mismatch")
    inside = _offset(
        assertions["midpoint"],
        assertions["outward_unit_normal"],
        Fraction(assertions["radius"]) - Fraction(assertions["signed_delta"]),
    )
    outside = _offset(
        assertions["midpoint"],
        assertions["outward_unit_normal"],
        Fraction(assertions["radius"]) + Fraction(assertions["signed_delta"]),
    )
    if oracle.ball_polyline_sweep_removes(inside, op["path"], op["radius"]) is not assertions["inside_removed"]:
        fail("F03 inward signed neighbour mismatch")
    if oracle.ball_polyline_sweep_removes(outside, op["path"], op["radius"]) is not assertions["outside_removed"]:
        fail("F03 outward signed neighbour mismatch")

    full_edges = oracle.canonical_undirected_segments(op["path"])
    forward_edges = oracle.canonical_undirected_segments(op["unique_forward_path"])
    if (full_edges == forward_edges) is not assertions["reverse_segment_set_equals_forward"]:
        fail("F03 exact reversal/remachining relation drift")

    forward = [tuple(Fraction(x) for x in p) for p in op["unique_forward_path"]]
    for a, b in zip(forward, forward[1:]):
        if any(x == y for x, y in zip(a, b)):
            fail("F03 segment stopped being simultaneous XYZ motion")

    corrupt = copy.deepcopy(op["path"])
    for point in corrupt:
        point[2] = op["path"][0][2]
    probe = assertions["flattened_z_corruption_probe"]
    actual = oracle.ball_polyline_sweep_removes(probe, op["path"], op["radius"])
    flattened = oracle.ball_polyline_sweep_removes(probe, corrupt, op["radius"])
    if actual is not assertions["actual_removed"] or flattened is not assertions["flattened_z_removed"]:
        fail("F03 flattened-Z corruption is no longer discriminating")


def validate_f04_transform(family, oracle, matrix=None):
    side_setup = next(s for s in family["setups"] if s["id"] == "S-F04-SIDE")
    side = operation(family, "F04-SIDE-CROSS")
    tx = side_setup["machine_to_common"]
    matrix = matrix if matrix is not None else tx["matrix"]
    if not oracle.is_rotation_matrix(matrix):
        fail("F04 setup transform is not an exact proper rotation")
    common = [
        [str(v) for v in oracle.rigid_transform(matrix, tx["translation"], p)]
        for p in side["path_machine"]
    ]
    if common != side["path_common"]:
        fail("F04 machine/common path transform mismatch")
    axis = [str(v) for v in oracle.matrix_vec(matrix, ["0", "0", "1"])]
    if axis != ["1", "0", "0"]:
        fail("F04 reorientation no longer maps machine +Z to common +X")


def verify_f04(family, oracle):
    validate_f04_transform(family, oracle)
    top = operation(family, "F04-TOP-CROSS")
    side = operation(family, "F04-SIDE-CROSS")
    for name in ("top_only", "side_only", "both", "survivor"):
        row = family["oracle_assertions"][name]
        top_got = oracle.flat_axis_sweep_removes(
            row["point"], top["path_common"], top["radius"], top["axis_common"], top["axial_interval_common"]
        )
        side_got = oracle.flat_axis_sweep_removes(
            row["point"], side["path_common"], side["radius"], side["axis_common"], side["axial_interval_common"]
        )
        if top_got is not row["top_removed"] or side_got is not row["side_removed"]:
            fail(f"F04 {name} full-3D crossing witness mismatch")


def verify_registry(contract):
    families = load(FAMILIES_PATH)["families"]
    if [f["id"] for f in families] != [f"F{i:02d}" for i in range(1, 17)]:
        fail("fixture-family denominator drift")
    for row in families:
        expected = "BUILT" if row["id"] in {"F01", "F02", "F03", "F04"} else "UNBUILT"
        if row.get("state") != expected:
            fail(f"{row['id']} registry state mismatch: {row.get('state')} != {expected}")
        if row.get("mandatory") is not True:
            fail(f"{row['id']} stopped being mandatory")
    outcomes = load(OUTCOMES_PATH)["tasks"]
    if outcomes["MC-011"].get("state") != "COMPLETED_RESEARCH":
        fail("MC-011 outcome registry was not reconciled")
    if contract["programme_state"]["MC-B"] != "NOT_ESTABLISHED" or contract["programme_state"]["MC-1"] != "NOT_ESTABLISHED":
        fail("MC-011 cannot promote MC-B or MC-1")
    if contract["programme_state"]["native_or_paid_campaign_run"] is not False:
        fail("MC-011 unexpectedly claims native/paid execution")


def verify_no_protected_source_edits(contract):
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{contract['source_baseline']}..HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    forbidden = sorted(p for p in changed if p.startswith("research/rcs-"))
    if forbidden:
        fail(f"MC-011 edited protected historical sources: {forbidden}")


def adversarial_controls(contract, oracle, cell):
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

    f02 = next(f for f in contract["families"] if f["id"] == "F02")
    positive = next(c for c in f02["boundary_cases"] if c["id"] == "WEB-POSITIVE")
    zero = next(c for c in f02["boundary_cases"] if c["id"] == "WEB-ZERO")
    if f02_cell_result(f02, positive, cell) == f02_cell_result(f02, zero, cell):
        fail("rounding a positive web to exact zero became observationally invisible")

    f03 = next(f for f in contract["families"] if f["id"] == "F03")
    op = f03["operation"]
    corrupt_path = copy.deepcopy(op["path"])
    for point in corrupt_path:
        point[2] = op["path"][0][2]
    probe = f03["oracle_assertions"]["flattened_z_corruption_probe"]
    if oracle.ball_polyline_sweep_removes(probe, op["path"], op["radius"]) == oracle.ball_polyline_sweep_removes(probe, corrupt_path, op["radius"]):
        fail("flattening simultaneous XYZ to planar motion escaped F03 control")

    f04 = next(f for f in contract["families"] if f["id"] == "F04")
    identity = [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]]
    try:
        validate_f04_transform(f04, oracle, matrix=identity)
    except AssertionError:
        pass
    else:
        fail("dropping the F04 re-clamp rotation was accepted")

    subprocess.run(
        [sys.executable, str(ROOT / "tools/mc_evidence_verifier.py"), "--self-test"],
        cwd=ROOT,
        check=True,
    )


def verify_contract() -> None:
    contract = load(CONTRACT_PATH)
    if contract.get("schema") != "radicadsac-mc-physical-corpus/1.0" or contract.get("task") != "MC-011":
        fail("wrong MC-011 contract identity")
    if [f.get("id") for f in contract.get("families", [])] != ["F01", "F02", "F03", "F04"]:
        fail("MC-011 must build exactly F01-F04")
    if any(f.get("state") != "BUILT" for f in contract["families"]):
        fail("MC-011 family record is not BUILT")
    if contract["registry_transition"] != {
        "F01-F04": "BUILT",
        "F05-F16": "UNBUILT",
        "meaning": "BUILT records fixture/oracle construction only; it is not candidate PASS, native evidence, proof-obligation acceptance or MC-B acceptance.",
    }:
        fail("fixture-registry transition semantics drift")

    verify_dependencies(contract)
    verify_oracle_independence(contract)
    oracle = load_module("mc011_fixture_oracle", ORACLE_PATH)
    cell = load_module("mc010_exact_cell_oracle_for_mc011", CELL_ORACLE_PATH)
    by_id = {f["id"]: f for f in contract["families"]}
    verify_f01(by_id["F01"], oracle)
    verify_f02(by_id["F02"], oracle, cell)
    verify_f03(by_id["F03"], oracle)
    verify_f04(by_id["F04"], oracle)
    verify_registry(contract)
    verify_no_protected_source_edits(contract)
    adversarial_controls(contract, oracle, cell)
    print("MC-011 F01-F04 physical/adversarial corpus verification passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    args = parser.parse_args()
    if not args.contract:
        parser.error("--contract is required; MC-011 has no native campaign")
    verify_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
