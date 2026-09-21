#!/usr/bin/env python3
"""Deterministic contract, physical-boundary and adversarial verification for MC-014."""
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
CONTRACT_PATH = TASK / "physical-corpus-f13-f16-v1.json"
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


def validate_independence_meta(meta):
    if meta.get("decisive_shared_geometry_imports") != []:
        fail("fixture oracle declares shared decisive candidate/historical geometry")
    if meta.get("candidate_output_used_for_expected_truth") is not False:
        fail("candidate output cannot define expected truth")
    if meta.get("expected_truth_origin") != "preregistered exact MC-014 fixture literals and analytic rational geometry":
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


def box_x_interval(box):
    return Fraction(box[0][0]), Fraction(box[0][1])


def verify_pairwise_x_disjoint(boxes, label):
    intervals = sorted(box_x_interval(box) for box in boxes)
    for (_, prev_hi), (next_lo, _) in zip(intervals, intervals[1:]):
        if prev_hi > next_lo:
            fail(f"{label} boxes overlap in x and are no longer independently additive")


def verify_f13(row, oracle):
    assertions = row["oracle_assertions"]
    tiers = row["tiers"]
    counts = [tier["new_cut_count"] for tier in tiers]
    if counts != assertions["tier_counts"]:
        fail("F13 tier count contract drift")
    if tuple(counts) != oracle.geometric_tier_counts(len(tiers)):
        fail("F13 tier counts are no longer geometric")
    ops = row["operations"]
    if len(ops) != assertions["total_distinct_pockets"] or len({op["id"] for op in ops}) != len(ops):
        fail("F13 distinct-pocket denominator drift")
    verify_pairwise_x_disjoint([op["box"] for op in ops], "F13")
    by_id = {op["id"]: op for op in ops}
    seen = set()
    cumulative = Fraction(0)
    got_new, got_cumulative = [], []
    for tier in tiers:
        ids = tier["new_cut_ids"]
        if len(ids) != tier["new_cut_count"] or len(set(ids)) != len(ids):
            fail("F13 tier contains duplicate/padded event identities")
        if seen.intersection(ids):
            fail("F13 tier reuses old work instead of adding genuine geometry")
        boxes = []
        for ident in ids:
            if ident not in by_id:
                fail("F13 tier references unknown pocket")
            boxes.append(by_id[ident]["box"])
        added = oracle.disjoint_box_volume(boxes)
        if added <= 0:
            fail("F13 tier stopped removing positive material")
        cumulative += added
        got_new.append(str(added))
        got_cumulative.append(str(cumulative))
        seen.update(ids)
    if got_new != assertions["new_removed_volumes"] or got_cumulative != assertions["cumulative_removed_volumes"]:
        fail("F13 exact material-growth witnesses drifted")
    for prev, nxt in zip(map(Fraction, got_new), map(Fraction, got_new[1:])):
        if nxt != 2 * prev:
            fail("F13 new removed volume no longer doubles per tier")
    if str(cumulative) != assertions["total_removed_volume"]:
        fail("F13 total removed volume drift")


def verify_f14(row, oracle):
    assertions = row["oracle_assertions"]
    history = row["history"]
    cuts = row["cut_definitions"]
    if len(history) != assertions["history_length"]:
        fail("F14 history length drift")
    boxes = [item["box"] for item in cuts.values()]
    verify_pairwise_x_disjoint(boxes, "F14")
    cut_volumes = {}
    for ident, item in cuts.items():
        volume = oracle.box_volume(item["box"])
        if str(volume) != item["volume"]:
            fail(f"F14 cut volume drift for {ident}")
        cut_volumes[ident] = item["volume"]
    flags = oracle.first_occurrence_change_flags(history)
    change_steps = [idx for idx, changed in enumerate(flags, 1) if changed]
    if change_steps != assertions["first_change_steps"]:
        fail("F14 independently established change steps drifted")
    if sum(flags) != len(assertions["unique_cut_ids"]):
        fail("F14 unique material-change count drift")
    if len(history) - sum(flags) != assertions["retrace_count"]:
        fail("F14 exact retrace count drift")
    unique_volume = oracle.unique_history_volume(history, cut_volumes)
    if str(unique_volume) != assertions["unique_removed_volume"]:
        fail("F14 idempotent unique removed volume drift")
    naive = sum(Fraction(cut_volumes[ident]) for ident in history)
    if str(naive) != assertions["naive_event_count_volume_forbidden"]:
        fail("F14 event-count corruption control drift")
    if naive == unique_volume:
        fail("F14 no longer discriminates retrace inflation from material truth")


def verify_f15(row, oracle):
    assertions = row["oracle_assertions"]
    planes = assertions["planes"]
    segments = oracle.partition_interval(assertions["x_interval"][0], assertions["x_interval"][1], planes)
    got_segments = [[str(a), str(b)] for a, b in segments]
    if got_segments != assertions["expected_segments"]:
        fail("F15 exact interface partition drift")
    if not oracle.partition_is_exact_cover(assertions["x_interval"][0], assertions["x_interval"][1], got_segments):
        fail("F15 reconstructed segments no longer exactly cover source feature")
    channel = row["operations"][0]["box"]
    y_len = oracle.interval_length(channel[1])
    z_len = oracle.interval_length(channel[2])
    volumes = [((b - a) * y_len * z_len) for a, b in segments]
    if [str(v) for v in volumes] != assertions["segment_removed_volumes"]:
        fail("F15 segment material volumes drift")
    if str(sum(volumes, Fraction(0))) != assertions["whole_removed_volume"]:
        fail("F15 partition reconstruction changed whole removed volume")
    iface = assertions["provider_interface"]
    for key in ("exact", "gap", "overlap"):
        case = iface[key]
        delta = oracle.signed_interface_delta(case["left_end"], case["right_start"])
        if key != "exact" and str(delta) != case["delta"]:
            fail(f"F15 {key} interface signed delta drift")
        if oracle.classify_interface(delta) != case["state"]:
            fail(f"F15 {key} interface classification drift")
    kinds = [item["kind"] for item in row["reconstruction_interfaces"]]
    if kinds != ["patch_boundary", "adaptive_cell_boundary", "provider_boundary"]:
        fail("F15 stopped crossing all required interface classes")


def verify_f16(row, oracle):
    assertions = row["oracle_assertions"]
    bodies = row["stock"]["bodies"]
    if len(bodies) != 2 or len({body["body_id"] for body in bodies}) != 2:
        fail("F16 durable body denominator drift")
    for body in bodies:
        if str(oracle.box_volume(body["box"])) != assertions["initial_body_volume"]:
            fail("F16 initial body volume drift")
    prior_ops = [op for op in row["operations"] if op["id"].startswith("F16-PRE-")]
    if len(prior_ops) != 2:
        fail("F16 prior-machining denominator drift")
    for op in prior_ops:
        prior = oracle.box_volume(op["box"])
        if str(prior) != assertions["prior_pocket_volume"]:
            fail("F16 prior positive-volume machining drift")
        remaining = Fraction(assertions["initial_body_volume"]) - prior
        if str(remaining) != assertions["post_prior_material_volume"] or remaining <= 0:
            fail("F16 prior machining no longer leaves positive material")
    for key in ("residual_positive", "exact_empty", "overtravel"):
        case = assertions[key]
        volume = oracle.remaining_slab_volume(["0", "10"], ["0", "10"], case["thickness"])
        if str(volume) != case["volume"]:
            fail(f"F16 {key} residual volume drift")
        if oracle.exhaustion_state(case["thickness"]) != case["state"]:
            fail(f"F16 {key} exhaustion classification drift")
    transition = row["body_transition"]
    if transition.get("retain_exhausted_identity_records") is not True:
        fail("F16 permits exhausted durable identities to disappear")
    if sorted(assertions["exhausted_body_ids"]) != sorted(body["body_id"] for body in bodies):
        fail("F16 exhausted-body identity set drift")
    if set(transition["after_exhaust_all"].values()) != {"EXACT_EMPTY"}:
        fail("F16 final all-body exhaustion state drift")
    if transition["after_exhaust_a"]["B-F16-B"] != "POSITIVE_MATERIAL":
        fail("F16 one-body exhaustion no longer preserves the other body")


def verify_registry(contract):
    rows = load(FAMILIES_PATH)["families"]
    expected_ids = [f"F{i:02d}" for i in range(1, 17)]
    if [row["id"] for row in rows] != expected_ids:
        fail("fixture-family denominator drift")
    outcomes = load(OUTCOMES_PATH)["tasks"]
    for row in rows:
        if row.get("mandatory") is not True:
            fail(f"{row['id']} stopped being mandatory")
        if row.get("state") != "BUILT":
            fail(f"{row['id']} is not BUILT after final corpus-construction tranche")
        if outcomes.get(row.get("owner"), {}).get("state") not in {"COMPLETED_RESEARCH", "CAPABILITY_ACCEPTED"}:
            fail(f"{row['id']} advanced without completed owner {row.get('owner')}")
    if outcomes["MC-014"].get("state") != "COMPLETED_RESEARCH":
        fail("MC-014 outcome registry was not reconciled")
    scope = contract["construction_scope"]
    if scope["built_by_this_task"] != ["F13", "F14", "F15", "F16"] or scope["still_unbuilt"] != []:
        fail("MC-014 construction scope drift")
    if scope.get("all_mandatory_families_built") is not True:
        fail("MC-014 failed to record final mandatory fixture construction")
    if contract["programme_state"]["MC-B"] != "NOT_ESTABLISHED" or contract["programme_state"]["MC-1"] != "NOT_ESTABLISHED":
        fail("fixture construction cannot promote MC-B or MC-1")
    if contract["programme_state"]["native_or_paid_campaign_run"] is not False:
        fail("MC-014 unexpectedly claims native/paid execution")


def verify_protected_sources(contract):
    for path, expected in PROTECTED_BLOBS.items():
        if git_blob(path) != expected:
            fail(f"protected historical source drift: {path}")
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{contract['source_baseline']}..HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    forbidden = sorted(path for path in changed if path.startswith("research/rcs-"))
    if forbidden:
        fail(f"MC-014 edited protected historical sources: {forbidden}")


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

    f13 = family(contract, "F13")
    vols = list(map(Fraction, f13["oracle_assertions"]["new_removed_volumes"]))
    if any(b != 2 * a for a, b in zip(vols, vols[1:])):
        fail("F13 geometric real-work growth corruption escaped")
    if len({op["id"] for op in f13["operations"]}) != 31:
        fail("F13 event-padding/duplicate-work corruption escaped")

    f14 = family(contract, "F14")
    cut_volumes = {ident: item["volume"] for ident, item in f14["cut_definitions"].items()}
    if oracle.unique_history_volume(f14["history"], cut_volumes) != Fraction("32"):
        fail("F14 exact-retrace idempotence corruption escaped")
    if sum(oracle.first_occurrence_change_flags(f14["history"])) != 4:
        fail("F14 redundant history became event-count truth")

    f15 = family(contract, "F15")
    iface = f15["oracle_assertions"]["provider_interface"]
    states = [
        oracle.classify_interface(oracle.signed_interface_delta(iface[key]["left_end"], iface[key]["right_start"]))
        for key in ("gap", "exact", "overlap")
    ]
    if states != ["GAP", "EXACT", "OVERLAP"]:
        fail("F15 signed interface neighbours collapsed")
    if oracle.partition_is_exact_cover("12", "28", [["12", "16"], ["16", "20"], ["20", "24001/1000"], ["24001/1000", "28"]]):
        fail("F15 gap-corrupted reconstruction escaped exact-cover control")

    f16 = family(contract, "F16")
    if oracle.exhaustion_state("1/1000000000") != "POSITIVE_MATERIAL":
        fail("F16 tiny positive residual was rounded to empty")
    if oracle.exhaustion_state("0") != "EXACT_EMPTY":
        fail("F16 exact empty state drift")
    if f16["body_transition"].get("retain_exhausted_identity_records") is not True:
        fail("F16 exhausted identity deletion escaped")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if not (args.contract or args.self_test):
        args.contract = True

    contract = load(CONTRACT_PATH)
    if contract.get("task") != "MC-014" or contract.get("schema") != "radicadsac-mc-physical-corpus/1.0":
        fail("MC-014 corpus identity/schema drift")
    if [row["id"] for row in contract["families"]] != ["F13", "F14", "F15", "F16"]:
        fail("MC-014 family denominator/order drift")

    verify_dependencies(contract)
    verify_oracle_independence(contract)
    oracle = load_module("mc014_fixture_oracle", ORACLE_PATH)
    verify_f13(family(contract, "F13"), oracle)
    verify_f14(family(contract, "F14"), oracle)
    verify_f15(family(contract, "F15"), oracle)
    verify_f16(family(contract, "F16"), oracle)
    verify_registry(contract)
    verify_protected_sources(contract)
    adversarial_controls(contract, oracle)
    print("MC-014 contract, physical-boundary and adversarial verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
