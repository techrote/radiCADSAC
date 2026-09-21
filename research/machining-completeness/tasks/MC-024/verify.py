#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-024"
CONTRACT = TASK / "exact-cell-falsification-v1.json"

EXPECTED_BASELINE = "07ea9c6c07b2836473162fa1f9dda18695b9a549"
EXPECTED_DEPS = {
    "MC-006": ("research/machining-completeness/tasks/MC-006/outcome.json", "0319e00b492c57e4a11e3e78ef9a2e15ff67e52e", "COMPLETED_RESEARCH"),
    "MC-007": ("research/machining-completeness/tasks/MC-007/outcome.json", "8d54872292dfd9f632c79c76994a467d26eaaf9c", "NEGATIVE_RESULT"),
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-016": ("research/machining-completeness/tasks/MC-016/outcome.json", "606a7d0b8be61131b2272f2eb161d6a4dbba703a", "COMPLETED_RESEARCH"),
}
EXPECTED_BLOCKERS = {"PB-007-01", "PB-007-02", "PB-007-03", "RB-016-02", "RB-016-04"}
EXPECTED_CONTROLS = {
    "CTRL-024-TANGENT",
    "CTRL-024-MICROWEB",
    "CTRL-024-SPLIT",
    "CTRL-024-EMPTY",
    "CTRL-024-RETRACE",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def reject_binary_float(value) -> None:
    if isinstance(value, float):
        raise AssertionError("binary floating values are forbidden in decisive MC-024 contract data")
    if isinstance(value, dict):
        for item in value.values():
            reject_binary_float(item)
    elif isinstance(value, list):
        for item in value:
            reject_binary_float(item)


def q(token: str) -> Fraction:
    if not isinstance(token, str):
        raise AssertionError("exact quantities must be JSON strings")
    return Fraction(token)


def parse_box(raw: list[str]) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    assert isinstance(raw, list) and len(raw) == 6
    vals = tuple(q(x) for x in raw)
    assert vals[0] < vals[1] and vals[2] < vals[3] and vals[4] < vals[5]
    return vals  # type: ignore[return-value]


def inside_box(point: tuple[Fraction, Fraction, Fraction],
               box: tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]) -> bool:
    x, y, z = point
    return box[0] <= x <= box[1] and box[2] <= y <= box[3] and box[4] <= z <= box[5]


def intervals(points: Iterable[Fraction]) -> list[tuple[Fraction, Fraction]]:
    pts = sorted(set(points))
    return [(a, b) for a, b in zip(pts, pts[1:]) if a < b]


def clip_coord(v: Fraction, lo: Fraction, hi: Fraction) -> Fraction | None:
    return v if lo <= v <= hi else None


def material_cells(stock_raw: list[str], cutter_raws: list[list[str]]):
    stock = parse_box(stock_raw)
    cutters = [parse_box(c) for c in cutter_raws]

    xs = {stock[0], stock[1]}
    ys = {stock[2], stock[3]}
    zs = {stock[4], stock[5]}
    for c in cutters:
        for v in (c[0], c[1]):
            clipped = clip_coord(v, stock[0], stock[1])
            if clipped is not None:
                xs.add(clipped)
        for v in (c[2], c[3]):
            clipped = clip_coord(v, stock[2], stock[3])
            if clipped is not None:
                ys.add(clipped)
        for v in (c[4], c[5]):
            clipped = clip_coord(v, stock[4], stock[5])
            if clipped is not None:
                zs.add(clipped)

    cells = []
    for xa, xb in intervals(xs):
        for ya, yb in intervals(ys):
            for za, zb in intervals(zs):
                p = ((xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2)
                if any(inside_box(p, c) for c in cutters):
                    continue
                cells.append((xa, xb, ya, yb, za, zb))
    return cells


def cell_volume(cell) -> Fraction:
    return (cell[1] - cell[0]) * (cell[3] - cell[2]) * (cell[5] - cell[4])


def overlap_positive(a0: Fraction, a1: Fraction, b0: Fraction, b1: Fraction) -> bool:
    return min(a1, b1) > max(a0, b0)


def face_adjacent(a, b) -> bool:
    x_touch = a[1] == b[0] or b[1] == a[0]
    y_touch = a[3] == b[2] or b[3] == a[2]
    z_touch = a[5] == b[4] or b[5] == a[4]
    axes = int(x_touch) + int(y_touch) + int(z_touch)
    if axes != 1:
        return False
    if x_touch:
        return overlap_positive(a[2], a[3], b[2], b[3]) and overlap_positive(a[4], a[5], b[4], b[5])
    if y_touch:
        return overlap_positive(a[0], a[1], b[0], b[1]) and overlap_positive(a[4], a[5], b[4], b[5])
    return overlap_positive(a[0], a[1], b[0], b[1]) and overlap_positive(a[2], a[3], b[2], b[3])


def component_count(cells) -> int:
    if not cells:
        return 0
    seen = set()
    count = 0
    for i in range(len(cells)):
        if i in seen:
            continue
        count += 1
        stack = [i]
        seen.add(i)
        while stack:
            j = stack.pop()
            for k in range(len(cells)):
                if k not in seen and face_adjacent(cells[j], cells[k]):
                    seen.add(k)
                    stack.append(k)
    return count


def run_control(control: dict) -> tuple[Fraction, int]:
    cells = material_cells(control["stock"], control["cutters"])
    volume = sum((cell_volume(c) for c in cells), Fraction(0))
    return volume, component_count(cells)


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    reject_binary_float(contract)
    assert contract["schema"] == "radicadsac-mc024-exact-cell-falsification/1.0"
    assert contract["task"] == "MC-024"
    assert contract["issue"] == 86
    assert contract["source_baseline"] == EXPECTED_BASELINE
    assert contract["result"] == "NEGATIVE_RESULT_AS_GENERAL_FALLBACK"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob, result_kind) in EXPECTED_DEPS.items():
        assert deps[task] == {
            "task": task,
            "path": path,
            "blob_sha": blob,
            "result_kind": result_kind,
        }
        if check_files:
            dep_path = ROOT / path
            assert dep_path.is_file()
            assert git_blob_sha1(dep_path) == blob, f"{task} dependency drift"
            assert load(dep_path)["result_kind"] == result_kind

    candidate = contract["candidate"]
    assert candidate["id"] == "EXACT-ARRANGEMENT-CELL"
    assert candidate["role"] == "BOUNDED_REFERENCE_OR_OPTIONAL_PROVIDER"
    assert candidate["general_fallback_qualified"] is False
    admission = candidate["admission_predicate"]
    req = set(admission["requirements"])
    assert {
        "finite_semialgebraic_encoding_proved",
        "rational_or_real_algebraic_coefficients",
        "all_denominator_and_sign_side_conditions_proved",
        "shared_time_feed_phase_correlation_preserved",
        "finite_history",
        "regularized_removal_semantics_preserved",
    } <= req
    assert admission["binary_float_predicates_allowed"] is False
    assert admission["global_epsilon_predicates_allowed"] is False
    assert admission["may_drop_required_operation"] is False
    assert "typed_blocker" in admission["on_failure"].lower() or "typed blocker" in admission["on_failure"].lower()
    theory = candidate["theory_binding"]
    assert theory["reviewed_source_owner"] == "MC-006"
    assert "quantifier elimination" in theory["reference_route"].lower()
    assert "doubly exponential" in theory["complexity_guard"].lower()

    matrix = {x["id"]: x for x in contract["coverage_matrix"]}
    assert set(matrix) == {f"EC-024-{i:02d}" for i in range(1, 7)}
    assert matrix["EC-024-01"]["status"] == "REFERENCE_ELIGIBLE"
    assert matrix["EC-024-02"]["status"] == "BLOCKED" and "PB-007-01" in matrix["EC-024-02"]["basis"]
    assert matrix["EC-024-03"]["status"] == "BLOCKED" and "PB-007-02" in matrix["EC-024-03"]["basis"]
    assert "independent angular coverage is forbidden" in matrix["EC-024-03"]["guard"].lower()
    assert matrix["EC-024-04"]["status"] == "BLOCKED" and "PB-007-03" in matrix["EC-024-04"]["basis"]
    assert matrix["EC-024-05"]["status"] == "MATERIAL_REFERENCE_ONLY_OUTPUT_UNQUALIFIED"
    assert "RB-016-02" in matrix["EC-024-05"]["basis"]
    assert "may not replace durable body identity" in matrix["EC-024-05"]["guard"].lower()
    assert matrix["EC-024-06"]["status"] == "MATERIAL_REFERENCE_ONLY_OUTPUT_PROFILE_BLOCKED"
    assert "RB-016-04" in matrix["EC-024-06"]["basis"]
    assert "no healing" in matrix["EC-024-06"]["guard"].lower()

    controls = {c["id"]: c for c in contract["machining_controls"]}
    assert set(controls) == EXPECTED_CONTROLS
    for cid, control in controls.items():
        volume, components = run_control(control)
        assert volume == q(control["expected_material_volume"]), f"{cid} material volume mismatch"
        assert components == control["expected_components"], f"{cid} component mismatch"
    retrace = controls["CTRL-024-RETRACE"]
    assert retrace["expected_same_as_single_cut"] is True
    single = copy.deepcopy(retrace)
    single["cutters"] = single["cutters"][:1]
    assert run_control(retrace) == run_control(single), "exact retrace must be idempotent"

    resource = contract["resource_obstruction"]
    assert resource["practical_status"] == "NOT_QUALIFIED_AS_DEFAULT_OR_GENERAL_PRODUCTION_ROUTE"
    assert "doubly-exponential" in resource["reason"].lower() or "doubly exponential" in resource["reason"].lower()
    assert resource["timeout_may_be_reported_as_success"] is False

    guards = contract["identity_and_output_guards"]
    assert guards == {
        "cell_identity_is_body_identity": False,
        "component_identity_is_durable_lineage": False,
        "tolerance_may_delete_positive_volume": False,
        "healing_may_bridge_exact_zero_contact": False,
        "largest_body_only_output_allowed": False,
    }

    dispatch = contract["total_dispatch_conclusion"]
    assert dispatch["candidate_can_be_general_fallback"] is False
    assert dispatch["candidate_can_be_bounded_reference"] is True
    assert dispatch["candidate_can_be_optional_provider_after_admission"] is True
    assert dispatch["unresolved_required_case_is_success"] is False
    assert "may not cycle" in dispatch["noncycling_requirement"].lower()

    blockers = {b["id"]: b for b in contract["retained_blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert blockers["PB-007-01"]["status"] == "OPEN"
    assert blockers["PB-007-02"]["status"] == "OPEN"
    assert blockers["PB-007-03"]["status"] == "PROPAGATED_FROM_MC-006"
    assert blockers["RB-016-02"]["status"] == "OPEN"
    assert blockers["RB-016-04"]["status"] == "OPEN"
    assert all(b["affected_descendants"] for b in blockers.values())

    assert contract["capability_guard"] == {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }


def adversarial_self_test(contract: dict) -> None:
    mutations = []

    bad = copy.deepcopy(contract)
    bad["candidate"]["general_fallback_qualified"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["requirements"].remove("shared_time_feed_phase_correlation_preserved")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["global_epsilon_predicates_allowed"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["coverage_matrix"][1]["status"] = "REFERENCE_ELIGIBLE"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["coverage_matrix"][2]["guard"] = "independent angular coverage is acceptable"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["coverage_matrix"][4]["guard"] = "cell identity is durable body identity"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["resource_obstruction"]["practical_status"] = "QUALIFIED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["identity_and_output_guards"]["tolerance_may_delete_positive_volume"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["identity_and_output_guards"]["healing_may_bridge_exact_zero_contact"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["retained_blockers"] = [b for b in bad["retained_blockers"] if b["id"] != "PB-007-01"]
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["formal_dependencies"][1]["blob_sha"] = "0" * 40
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-B"] = "ACCEPTED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["machining_controls"][1]["expected_material_volume"] = "0"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["machining_controls"][0]["stock"][0] = 0.0
    mutations.append(bad)

    rejected = 0
    for bad in mutations:
        try:
            validate_contract(bad, check_files=False)
        except (AssertionError, KeyError, TypeError, ValueError, ZeroDivisionError):
            rejected += 1
    assert rejected == len(mutations), f"accepted {len(mutations) - rejected} adversarial corruption(s)"


def verify_integration() -> None:
    contract = load(CONTRACT)
    validate_contract(contract, check_files=True)
    adversarial_self_test(contract)

    outcome = load(TASK / "outcome.json")
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
    assert outcome["task"] == "MC-024"
    assert outcome["result_kind"] == "NEGATIVE_RESULT"
    assert outcome["native_execution"] is False
    assert {b["id"] for b in outcome["blockers"]} == EXPECTED_BLOCKERS
    assert outcome["review"]["gate_changed"] is False
    assert outcome["review"]["programme_capability_changed"] is False

    outcomes = load(ROOT / "research/machining-completeness/outcomes-v1.json")
    record = outcomes["tasks"]["MC-024"]
    assert record["state"] == "NEGATIVE_RESULT"
    assert {b["id"] for b in record["blockers"]} == EXPECTED_BLOCKERS
    required_artifacts = {
        "research/machining-completeness/tasks/MC-024/exact-cell-falsification-v1.json",
        "research/machining-completeness/tasks/MC-024/report.md",
        "research/machining-completeness/tasks/MC-024/outcome.json",
        "research/machining-completeness/tasks/MC-024/verify.py",
        "docs/machining-completeness/02-COMPLETENESS-ARGUMENT.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])

    doc = (ROOT / "docs/machining-completeness/02-COMPLETENESS-ARGUMENT.md").read_text(encoding="utf-8")
    assert "MC-024 exact/cell candidate falsification" in doc
    assert "NEGATIVE_RESULT" in doc
    assert "bounded reference" in doc.lower()
    assert "PB-007-01" in doc and "PB-007-02" in doc and "PB-007-03" in doc
    assert "RB-016-02" in doc and "RB-016-04" in doc
    assert "MC-B remains `NOT_ESTABLISHED`" in doc

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text(encoding="utf-8")
    assert "research/machining-completeness/tasks/MC-024/verify.py" in workflow
    assert "python3 tools/mc_workflow.py verify MC-024" in workflow


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    verify_integration()
    if args.self_test:
        adversarial_self_test(load(CONTRACT))
    print("MC-024 exact/cell candidate falsification verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
