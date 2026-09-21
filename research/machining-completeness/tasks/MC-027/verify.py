#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-027"
CONTRACT = TASK / "directional-material-falsification-v1.json"
OUTCOME = TASK / "outcome.json"
DOC = ROOT / "docs" / "machining-completeness" / "19-MC027-DIRECTIONAL-MATERIAL.md"
REGISTRY = ROOT / "research" / "machining-completeness" / "outcomes-v1.json"

EXPECTED_BASELINE = "263b5e35f6a0d9a6c9695a926cbb37e3f65b9606"
EXPECTED_DEPS = {
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-016": ("research/machining-completeness/tasks/MC-016/outcome.json", "606a7d0b8be61131b2272f2eb161d6a4dbba703a", "COMPLETED_RESEARCH"),
    "MC-019": ("research/machining-completeness/tasks/MC-019/outcome.json", "4456c964315c10b46ce61a5a8d4a45e8025730b7", "COMPLETED_RESEARCH"),
    "MC-023": ("research/machining-completeness/tasks/MC-023/outcome.json", "15cd3b128cdaa14370594debd490e76a4a0d6b23", "COMPLETED_RESEARCH"),
}
EXPECTED_BLOCKERS = {"RB-016-02", "RB-016-04"}
EXPECTED_CONTROLS = {
    "CTRL-027-MULTI-AXIS-CAVITY",
    "CTRL-027-REORIENTATION",
    "CTRL-027-MICROFEATURE",
    "CTRL-027-TANGENCY",
}
AXES = ("x", "y", "z")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def reject_binary_float(value) -> None:
    if isinstance(value, float):
        raise AssertionError("binary floating values are forbidden in decisive MC-027 contract data")
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


def interval(raw: list[str]) -> tuple[Fraction, Fraction]:
    assert isinstance(raw, list) and len(raw) == 2
    a, b = q(raw[0]), q(raw[1])
    assert a <= b
    return a, b


def parse_box(raw: dict) -> dict[str, tuple[Fraction, Fraction]]:
    assert set(raw) == set(AXES)
    box = {axis: interval(raw[axis]) for axis in AXES}
    assert all(a < b for a, b in box.values())
    return box


def merge_intervals(items: list[tuple[Fraction, Fraction]]) -> list[tuple[Fraction, Fraction]]:
    if not items:
        return []
    items = sorted(items)
    out = [items[0]]
    for a, b in items[1:]:
        pa, pb = out[-1]
        if a <= pb:
            out[-1] = (pa, max(pb, b))
        else:
            out.append((a, b))
    return out


def line_intervals(raw_boxes: list[dict], axis: str, transverse: dict[str, str]) -> list[tuple[Fraction, Fraction]]:
    assert axis in AXES
    other = [a for a in AXES if a != axis]
    assert set(transverse) == set(other)
    fixed = {a: q(transverse[a]) for a in other}
    hits: list[tuple[Fraction, Fraction]] = []
    for raw in raw_boxes:
        box = parse_box(raw)
        if all(box[a][0] <= fixed[a] <= box[a][1] for a in other):
            hits.append(box[axis])
    return merge_intervals(hits)


def expected_intervals(raw: list[list[str]]) -> list[tuple[Fraction, Fraction]]:
    return [interval(x) for x in raw]


def determinant3(m: list[list[Fraction]]) -> Fraction:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def parse_proper_signed_permutation(raw: list[list[str]]) -> list[list[Fraction]]:
    assert len(raw) == 3 and all(len(row) == 3 for row in raw)
    m = [[q(v) for v in row] for row in raw]
    for row in m:
        assert sum(v != 0 for v in row) == 1
        assert all(v in {Fraction(-1), Fraction(0), Fraction(1)} for v in row)
    for col in range(3):
        assert sum(m[row][col] != 0 for row in range(3)) == 1
    assert determinant3(m) == 1, "reorientation control must be right-handed"
    return m


def transform_point(m: list[list[Fraction]], t: list[Fraction], p: tuple[Fraction, Fraction, Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(sum(m[r][c] * p[c] for c in range(3)) + t[r] for r in range(3))  # type: ignore[return-value]


def transform_box(raw_box: dict, transform: dict) -> dict[str, tuple[Fraction, Fraction]]:
    box = parse_box(raw_box)
    m = parse_proper_signed_permutation(transform["matrix"])
    t = [q(v) for v in transform["translation"]]
    assert len(t) == 3
    corners = []
    for xyz in itertools.product(*[(box[a][0], box[a][1]) for a in AXES]):
        corners.append(transform_point(m, t, xyz))
    return {
        axis: (min(p[i] for p in corners), max(p[i] for p in corners))
        for i, axis in enumerate(AXES)
    }


def box_volume(raw: dict) -> Fraction:
    box = parse_box(raw)
    out = Fraction(1)
    for axis in AXES:
        out *= box[axis][1] - box[axis][0]
    return out


def assert_probe(raw_boxes: list[dict], probe: dict) -> None:
    got = line_intervals(raw_boxes, probe["axis"], probe["transverse"])
    want = expected_intervals(probe["expected"])
    assert got == want, f"{probe}: got {got}, want {want}"


def validate_finite_sampling_obstruction(obj: dict) -> None:
    stock = parse_box(obj["stock"])
    hidden = parse_box(obj["hidden_cavity"])
    for axis in AXES:
        assert stock[axis][0] < hidden[axis][0] < hidden[axis][1] < stock[axis][1]
    samples = [q(x) for x in obj["sample_transverse_values"]]
    assert samples and len(samples) == len(set(samples))
    expected = interval(obj["expected_sampled_line_interval"])
    assert expected == stock["x"] == stock["y"] == stock["z"]
    for axis in AXES:
        other = [a for a in AXES if a != axis]
        for a, b in itertools.product(samples, repeat=2):
            fixed = {other[0]: a, other[1]: b}
            intersects_hidden = all(hidden[k][0] <= fixed[k] <= hidden[k][1] for k in other)
            assert not intersects_hidden, f"sampled {axis}-line unexpectedly intersects hidden cavity"
    assert box_volume(obj["hidden_cavity"]) == q(obj["expected_hidden_volume"]) == Fraction(1, 125000)
    assert obj["all_sampled_lines_miss_hidden_cavity"] is True
    assert obj["same_sampled_data_implies_same_material"] is False
    assert "any finite family" in obj["generalization"].lower()
    assert "positive-volume" in obj["generalization"].lower()


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    reject_binary_float(contract)
    assert contract["schema"] == "radicadsac-mc027-directional-material-falsification/1.0"
    assert contract["task"] == "MC-027"
    assert contract["issue"] == 89
    assert contract["source_baseline"] == EXPECTED_BASELINE
    assert contract["result"] == "NEGATIVE_RESULT_AS_TOTAL_MATERIAL_AUTHORITY"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob, result_kind) in EXPECTED_DEPS.items():
        assert deps[task] == {"task": task, "path": path, "blob_sha": blob, "result_kind": result_kind}
        if check_files:
            dep_path = ROOT / path
            assert dep_path.is_file()
            assert git_blob_sha1(dep_path) == blob, f"{task} dependency drift"
            assert load(dep_path)["result_kind"] == result_kind

    candidate = contract["candidate"]
    assert candidate["id"] == "MULTI_TRI_DIRECTIONAL_INTERVAL_MATERIAL"
    assert candidate["role"] == "BOUNDED_DERIVED_INDEX_AFTER_CERTIFIED_3D_RELATION"
    assert candidate["general_material_authority_qualified"] is False
    admission = candidate["admission_predicate"]
    required = {
        "canonical full-3D material relation is independently authoritative",
        "every stored line interval is derived from that relation with exact or outward-certified endpoints",
        "transverse event boundaries where interval count or ordering changes are certified",
        "all positive-volume material is preserved",
        "MC-023 common-frame transform semantics are preserved",
        "MC-019 complete finite cutter and simultaneous-XYZ semantics are preserved",
        "unknown classification remains explicit and fail-closed",
    }
    assert required <= set(admission["requirements"])
    assert admission["finite_direction_set_is_completeness_proof"] is False
    assert admission["finite_sampled_lines_may_define_material"] is False
    assert admission["binary_float_predicates_allowed"] is False
    assert admission["global_epsilon_predicates_allowed"] is False
    assert admission["majority_vote_between_directions_allowed"] is False
    assert "uncertified" in admission["on_failure"].lower()
    assert "cycle" in admission["on_failure"].lower()

    rep = contract["representation_contract"]
    assert rep["multiple_intervals_required"] is True
    assert rep["directional_indexes_are_material_authority"] is False
    assert rep["canonical_relation_resolves_direction_conflict"] is True
    assert rep["missing_or_unknown_line_is_material"] is False
    assert rep["boundary_equality_must_be_preserved"] is True
    assert rep["positive_volume_may_be_deleted_by_tolerance"] is False
    assert rep["durable_body_identity_is_interval_identity"] is False
    assert rep["lineage_is_interval_connectivity"] is False

    matrix = {x["id"]: x for x in contract["coverage_matrix"]}
    assert set(matrix) == {f"DI-027-{i:02d}" for i in range(1, 7)}
    assert matrix["DI-027-01"]["status"] == "DERIVED_INDEX_ELIGIBLE"
    assert matrix["DI-027-02"]["status"] == "MODEL_REFERENCE_ELIGIBLE"
    assert matrix["DI-027-03"]["status"] == "MODEL_REFERENCE_ELIGIBLE"
    assert matrix["DI-027-04"]["status"] == "FALSIFIED"
    assert "positive-volume hidden cavity" in matrix["DI-027-04"]["guard"]
    assert matrix["DI-027-05"]["status"] == "NOT_SELF_SUFFICIENT"
    assert "full-3d relation" in matrix["DI-027-05"]["basis"].lower()
    assert matrix["DI-027-06"]["status"] == "MATERIAL_MODEL_ONLY_OUTPUT_BLOCKED"
    assert "RB-016-02" in matrix["DI-027-06"]["basis"] and "RB-016-04" in matrix["DI-027-06"]["basis"]

    controls = {x["id"]: x for x in contract["exact_controls"]}
    assert set(controls) == EXPECTED_CONTROLS
    cavity = controls["CTRL-027-MULTI-AXIS-CAVITY"]
    for probe in cavity["probes"]:
        assert_probe(cavity["boxes"], probe)
    assert all(len(expected_intervals(p["expected"])) == 2 for p in cavity["probes"])

    reoriented = controls["CTRL-027-REORIENTATION"]
    got_box = transform_box(reoriented["boxes"][0], reoriented["transform"])
    want_box = parse_box(reoriented["expected_box"])
    assert got_box == want_box
    transformed_raw = {a: [str(got_box[a][0]), str(got_box[a][1])] for a in AXES}
    assert_probe([transformed_raw], reoriented["probe"])

    micro = controls["CTRL-027-MICROFEATURE"]
    assert_probe(micro["boxes"], micro["probe"])
    got_micro = line_intervals(micro["boxes"], micro["probe"]["axis"], micro["probe"]["transverse"])
    assert got_micro[0][1] - got_micro[0][0] == q(micro["expected_length"]) == Fraction(1, 1_000_000)

    tangent = controls["CTRL-027-TANGENCY"]
    for probe in tangent["probes"]:
        assert_probe(tangent["boxes"], probe)
    assert line_intervals(tangent["boxes"], "x", {"y": "1", "z": "1/2"}) == [(Fraction(0), Fraction(1))]
    assert line_intervals(tangent["boxes"], "x", {"y": "1000001/1000000", "z": "1/2"}) == []

    validate_finite_sampling_obstruction(contract["finite_sampling_obstruction"])

    continuous = contract["continuous_field_obstruction"]
    assert {
        "finite transverse partition",
        "certified event boundaries where interval topology changes",
        "exact or outward-certified endpoint relations",
        "independent full-3D relation for unresolved points",
    } <= set(continuous["finite_self_sufficient_representation_requires"])
    assert continuous["directional_index_alone_supplies_these"] is False
    assert continuous["sampling_density_may_replace_event_certificate"] is False
    assert continuous["timeout_may_be_reported_as_success"] is False

    dispatch = contract["total_dispatch_conclusion"]
    assert dispatch["candidate_can_be_general_material_authority"] is False
    assert dispatch["candidate_can_be_bounded_derived_index"] is True
    assert dispatch["candidate_can_be_optional_accelerator_after_admission"] is True
    assert dispatch["finite_sampled_rays_are_complete"] is False
    assert dispatch["continuous_directional_field_eliminates_need_for_full_3d_relation"] is False
    assert dispatch["unresolved_required_case_is_success"] is False
    assert "may not cycle" in dispatch["noncycling_requirement"].lower()

    blockers = {b["id"]: b for b in contract["retained_blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in blockers.values())
    assert all(b["source_task"] == "MC-016" for b in blockers.values())
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

    if check_files:
        outcome = load(OUTCOME)
        assert outcome["task"] == "MC-027"
        assert outcome["result_kind"] == "NEGATIVE_RESULT"
        assert outcome["source_baseline"] == EXPECTED_BASELINE
        assert {x["id"] for x in outcome["blockers"]} == EXPECTED_BLOCKERS

        registry = load(REGISTRY)["tasks"]["MC-027"]
        assert registry["state"] == "NEGATIVE_RESULT"
        assert registry["issue"] == 89
        assert "research/machining-completeness/tasks/MC-027/directional-material-falsification-v1.json" in registry["accepted_artifacts"]
        assert {x["id"] for x in registry["blockers"]} == EXPECTED_BLOCKERS

        doc = DOC.read_text(encoding="utf-8")
        assert "MC-027" in doc
        assert "NEGATIVE_RESULT" in doc
        assert "finite sampled" in doc.lower()
        assert "RB-016-02" in doc and "RB-016-04" in doc
        assert "MC-B" in doc and "NOT_ESTABLISHED" in doc


def adversarial_self_test(contract: dict) -> None:
    mutations = []

    bad = copy.deepcopy(contract)
    bad["candidate"]["general_material_authority_qualified"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["finite_sampled_lines_may_define_material"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["majority_vote_between_directions_allowed"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["representation_contract"]["positive_volume_may_be_deleted_by_tolerance"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["representation_contract"]["durable_body_identity_is_interval_identity"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["coverage_matrix"][3]["status"] = "DERIVED_INDEX_ELIGIBLE"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["finite_sampling_obstruction"]["same_sampled_data_implies_same_material"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["continuous_field_obstruction"]["sampling_density_may_replace_event_certificate"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["total_dispatch_conclusion"]["continuous_directional_field_eliminates_need_for_full_3d_relation"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["retained_blockers"] = [b for b in bad["retained_blockers"] if b["id"] != "RB-016-04"]
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-B"] = "ACCEPTED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["exact_controls"][2]["expected_length"] = 0.000001
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["exact_controls"][0]["probes"][0]["expected"] = [["0", "3"]]
    mutations.append(bad)

    for i, mutation in enumerate(mutations, 1):
        try:
            validate_contract(mutation, check_files=False)
        except (AssertionError, ValueError, KeyError, TypeError):
            continue
        raise AssertionError(f"adversarial mutation {i} was not rejected")


def main() -> int:
    ap = argparse.ArgumentParser()
    mx = ap.add_mutually_exclusive_group(required=True)
    mx.add_argument("--contract", action="store_true")
    mx.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    contract = load(CONTRACT)
    if args.contract:
        validate_contract(contract, check_files=True)
        print("MC-027 directional material contract verification passed")
    else:
        validate_contract(contract, check_files=True)
        adversarial_self_test(contract)
        print("MC-027 adversarial self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
