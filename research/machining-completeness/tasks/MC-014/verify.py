#!/usr/bin/env python3
"""Deterministic contract, boundary and adversarial verification for MC-014."""
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
    p = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    )
    return p.stdout.strip()


def load_oracle():
    spec = importlib.util.spec_from_file_location("mc014_fixture_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        fail("cannot load MC-014 oracle")
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
        fail("shared decisive geometry declared")
    if meta.get("candidate_output_used_for_expected_truth") is not False:
        fail("candidate output defines expected truth")
    if meta.get("expected_truth_origin") != "preregistered exact MC-014 fixture literals and analytic rational geometry":
        fail("expected-truth origin drift")


def verify_dependencies(contract):
    for dep in contract["dependencies"]:
        if git_blob(dep["path"]) != dep["blob_sha"]:
            fail(f"dependency artifact drift: {dep['task']}")


def verify_oracle_independence(contract):
    source = ORACLE_PATH.read_text(encoding="utf-8")
    meta = contract["oracle_independence"]["fixture_specific_path"]
    if hashlib.sha256(source.encode()).hexdigest() != meta["source_sha256"]:
        fail("fixture oracle source digest drift")
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    extra = imports - set(meta["allowed_import_roots"])
    if extra:
        fail(f"unapproved oracle imports: {sorted(extra)}")
    validate_independence_meta(meta)
    lowered = source.lower()
    forbidden = ("research/rcs", "rcs-021", "material_oracle", "tridexel", "manifold_fallback", "opencascade")
    hits = [term for term in forbidden if term in lowered]
    if hits:
        fail(f"oracle leaked historical/candidate geometry: {hits}")


def disjoint_x(boxes):
    intervals = sorted((Fraction(b[0][0]), Fraction(b[0][1])) for b in boxes)
    return all(a_hi <= b_lo for (_, a_hi), (b_lo, _) in zip(intervals, intervals[1:]))


def verify_f13(row, oracle):
    a = row["oracle_assertions"]
    tiers = row["tiers"]
    ops = row["operations"]
    if [t["new_cut_count"] for t in tiers] != [1, 2, 4, 8, 16]:
        fail("F13 geometric tier counts drift")
    if tuple(t["new_cut_count"] for t in tiers) != oracle.geometric_tier_counts(5):
        fail("F13 oracle geometric counts drift")
    if len(ops) != 31 or len({op["id"] for op in ops}) != 31 or not disjoint_x([op["box"] for op in ops]):
        fail("F13 distinct disjoint work denominator drift")
    by_id = {op["id"]: op for op in ops}
    seen = set()
    new_volumes = []
    cumulative = Fraction(0)
    cumulative_volumes = []
    for tier in tiers:
        ids = tier["new_cut_ids"]
        if len(ids) != tier["new_cut_count"] or len(set(ids)) != len(ids) or seen.intersection(ids):
            fail("F13 tier contains duplicate/reused work")
        if any(ident not in by_id for ident in ids):
            fail("F13 tier references unknown work")
        added = oracle.disjoint_box_volume([by_id[ident]["box"] for ident in ids])
        if added <= 0:
            fail("F13 tier does not change positive material")
        cumulative += added
        new_volumes.append(str(added))
        cumulative_volumes.append(str(cumulative))
        seen.update(ids)
    if new_volumes != a["new_removed_volumes"] or cumulative_volumes != a["cumulative_removed_volumes"]:
        fail("F13 exact growth evidence drift")
    if any(Fraction(b) != 2 * Fraction(a0) for a0, b in zip(new_volumes, new_volumes[1:])):
        fail("F13 new material removal no longer doubles per tier")
    if str(cumulative) != a["total_removed_volume"] or len(seen) != a["total_distinct_pockets"]:
        fail("F13 final real-work witness drift")


def verify_f14(row, oracle):
    a = row["oracle_assertions"]
    history = row["history"]
    cuts = row["cut_definitions"]
    if len(history) != a["history_length"] or set(cuts) != set(a["unique_cut_ids"]):
        fail("F14 history/cut denominator drift")
    if not disjoint_x([v["box"] for v in cuts.values()]):
        fail("F14 independent changes overlap")
    volumes = {}
    for ident, spec in cuts.items():
        got = oracle.box_volume(spec["box"])
        if str(got) != spec["volume"]:
            fail(f"F14 cut volume drift: {ident}")
        volumes[ident] = spec["volume"]
    flags = oracle.first_occurrence_change_flags(history)
    change_steps = [i for i, changed in enumerate(flags, 1) if changed]
    if change_steps != a["first_change_steps"]:
        fail("F14 independent change steps drift")
    if len(history) - sum(flags) != a["retrace_count"]:
        fail("F14 retrace count drift")
    exact = oracle.unique_history_volume(history, volumes)
    naive = sum((Fraction(volumes[ident]) for ident in history), Fraction(0))
    if str(exact) != a["unique_removed_volume"] or str(naive) != a["naive_event_count_volume_forbidden"]:
        fail("F14 idempotent/event-count witness drift")
    if exact == naive:
        fail("F14 no longer discriminates retrace inflation")


def verify_f15(row, oracle):
    a = row["oracle_assertions"]
    segs = oracle.partition_interval(a["x_interval"][0], a["x_interval"][1], a["planes"])
    rendered = [[str(lo), str(hi)] for lo, hi in segs]
    if rendered != a["expected_segments"] or not oracle.partition_is_exact_cover(a["x_interval"][0], a["x_interval"][1], rendered):
        fail("F15 exact reconstruction cover drift")
    channel = row["operations"][0]["box"]
    yz = oracle.interval_length(channel[1]) * oracle.interval_length(channel[2])
    vols = [(hi - lo) * yz for lo, hi in segs]
    if [str(v) for v in vols] != a["segment_removed_volumes"] or str(sum(vols, Fraction(0))) != a["whole_removed_volume"]:
        fail("F15 reconstruction material-volume drift")
    if [item["kind"] for item in row["reconstruction_interfaces"]] != ["patch_boundary", "adaptive_cell_boundary", "provider_boundary"]:
        fail("F15 required interface classes drift")
    iface = a["provider_interface"]
    for key in ("exact", "gap", "overlap"):
        case = iface[key]
        delta = oracle.signed_interface_delta(case["left_end"], case["right_start"])
        if key != "exact" and str(delta) != case["delta"]:
            fail(f"F15 {key} signed delta drift")
        if oracle.classify_interface(delta) != case["state"]:
            fail(f"F15 {key} classification drift")


def verify_f16(row, oracle):
    a = row["oracle_assertions"]
    bodies = row["stock"]["bodies"]
    if len(bodies) != 2 or len({b["body_id"] for b in bodies}) != 2:
        fail("F16 durable body denominator drift")
    if any(str(oracle.box_volume(b["box"])) != a["initial_body_volume"] for b in bodies):
        fail("F16 initial body volume drift")
    prior_ops = [op for op in row["operations"] if op["id"].startswith("F16-PRE-")]
    if len(prior_ops) != 2:
        fail("F16 prior-machining denominator drift")
    for op in prior_ops:
        removed = oracle.box_volume(op["box"])
        if str(removed) != a["prior_pocket_volume"]:
            fail("F16 prior pocket volume drift")
        if str(Fraction(a["initial_body_volume"]) - removed) != a["post_prior_material_volume"]:
            fail("F16 post-prior positive material drift")
    for key in ("residual_positive", "exact_empty", "overtravel"):
        case = a[key]
        volume = oracle.remaining_slab_volume(["0", "10"], ["0", "10"], case["thickness"])
        if str(volume) != case["volume"] or oracle.exhaustion_state(case["thickness"]) != case["state"]:
            fail(f"F16 {key} boundary drift")
    tr = row["body_transition"]
    if tr.get("retain_exhausted_identity_records") is not True:
        fail("F16 allows exhausted identity deletion")
    if sorted(a["exhausted_body_ids"]) != sorted(b["body_id"] for b in bodies):
        fail("F16 exhausted identity set drift")
    if set(tr["after_exhaust_all"].values()) != {"EXACT_EMPTY"}:
        fail("F16 all-body exhaustion drift")
    if tr["after_exhaust_a"] != {"B-F16-A": "EXACT_EMPTY", "B-F16-B": "POSITIVE_MATERIAL"}:
        fail("F16 one-body exhaustion drift")


def verify_registry(contract):
    rows = load(FAMILIES_PATH)["families"]
    outcomes = load(OUTCOMES_PATH)["tasks"]
    if [row["id"] for row in rows] != [f"F{i:02d}" for i in range(1, 17)]:
        fail("fixture-family denominator drift")
    for row in rows:
        if row.get("mandatory") is not True or row.get("state") != "BUILT":
            fail(f"{row['id']} not mandatory BUILT")
        if outcomes.get(row["owner"], {}).get("state") not in {"COMPLETED_RESEARCH", "CAPABILITY_ACCEPTED"}:
            fail(f"{row['id']} has incomplete owner")
    if outcomes["MC-014"].get("state") != "COMPLETED_RESEARCH":
        fail("MC-014 registry state drift")
    scope = contract["construction_scope"]
    if scope["built_by_this_task"] != ["F13", "F14", "F15", "F16"] or scope["still_unbuilt"] != [] or scope.get("all_mandatory_families_built") is not True:
        fail("MC-014 construction-scope drift")
    p = contract["programme_state"]
    if p["MC-B"] != "NOT_ESTABLISHED" or p["MC-1"] != "NOT_ESTABLISHED" or p["native_or_paid_campaign_run"] is not False:
        fail("MC-014 overclaims capability/native execution")


def verify_protected_sources(contract):
    for path, expected in PROTECTED_BLOBS.items():
        if git_blob(path) != expected:
            fail(f"protected historical source drift: {path}")
    p = subprocess.run(
        ["git", "diff", "--name-only", f"{contract['source_baseline']}..HEAD"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    changed = {line.strip() for line in p.stdout.splitlines() if line.strip()}
    forbidden = sorted(path for path in changed if path.startswith("research/rcs-"))
    if forbidden:
        fail(f"MC-014 edited protected historical sources: {forbidden}")


def expect_reject(fn, label):
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    fail(f"adversarial corruption escaped: {label}")


def adversarial_controls(contract, oracle):
    expect_reject(lambda: oracle.q(0.1), "binary-float authority")

    bad_meta = copy.deepcopy(contract["oracle_independence"]["fixture_specific_path"])
    bad_meta["candidate_output_used_for_expected_truth"] = True
    expect_reject(lambda: validate_independence_meta(bad_meta), "candidate-defined truth")
    bad_meta = copy.deepcopy(contract["oracle_independence"]["fixture_specific_path"])
    bad_meta["decisive_shared_geometry_imports"] = ["research/rcs-021/field.py"]
    expect_reject(lambda: validate_independence_meta(bad_meta), "shared decisive geometry")

    bad = copy.deepcopy(family(contract, "F13"))
    bad["tiers"][1]["new_cut_ids"][0] = bad["tiers"][0]["new_cut_ids"][0]
    expect_reject(lambda: verify_f13(bad, oracle), "F13 duplicate/reused event padding")

    bad = copy.deepcopy(family(contract, "F14"))
    bad["history"][1] = "B"
    expect_reject(lambda: verify_f14(bad, oracle), "F14 retrace/change corruption")

    if oracle.partition_is_exact_cover("12", "28", [["12", "16"], ["16", "20"], ["20", "24"], ["24001/1000", "28"]]):
        fail("F15 gap-corrupted reconstruction escaped exact-cover control")
    if oracle.partition_is_exact_cover("12", "28", [["12", "16"], ["16", "20"], ["20", "24001/1000"], ["24", "28"]]):
        fail("F15 overlap-corrupted reconstruction escaped exact-cover control")
    bad = copy.deepcopy(family(contract, "F15"))
    bad["oracle_assertions"]["provider_interface"]["exact"]["right_start"] = "24001/1000"
    expect_reject(lambda: verify_f15(bad, oracle), "F15 provider continuity corruption")

    if oracle.exhaustion_state("1/1000000000") != "POSITIVE_MATERIAL":
        fail("F16 tiny positive residual rounded to empty")
    bad = copy.deepcopy(family(contract, "F16"))
    bad["body_transition"]["retain_exhausted_identity_records"] = False
    expect_reject(lambda: verify_f16(bad, oracle), "F16 exhausted identity deletion")


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
    oracle = load_oracle()
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
