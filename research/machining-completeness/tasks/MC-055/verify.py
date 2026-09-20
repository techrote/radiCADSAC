#!/usr/bin/env python3
"""Static identity, boundary and adversarial verification for MC-055."""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
CONTRACT_PATH = TASK / "historical-corpus-import-v1.json"
RCS021_PLAN = ROOT / "research/rcs-021/experiment-plan-v1.json"
RCS021_SUMMARY = ROOT / "research/rcs-021/measured-summary-v1.json"
RCS003_CORPUS = ROOT / "research/rcs-003/corpus-v1.json"
RCS011_SUMMARY = ROOT / "research/rcs-011/measured-summary-v1.json"
RCS012_SUMMARY = ROOT / "research/rcs-012/measured-summary-v1.json"
FAMILIES = ROOT / "research/machining-completeness/fixture-families-v1.json"


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


def source_family_index(corpus):
    records = corpus.get("fixture_families", [])
    index = {}
    for record in records:
        key = (record.get("id"), record.get("revision"))
        if None in key or key in index:
            fail(f"invalid/duplicate RCS-003 record identity {key}")
        index[key] = record
    return index


def validate_structure(contract, *, verify_files: bool) -> None:
    if contract.get("schema") != "radicadsac-mc-historical-corpus-import/1.0":
        fail("wrong MC-055 schema")
    if contract.get("task") != "MC-055":
        fail("wrong MC-055 task identity")

    sources = contract.get("historical_sources", [])
    if not sources:
        fail("historical source set is empty")
    paths = [x.get("path") for x in sources]
    if None in paths or len(paths) != len(set(paths)):
        fail("historical source paths must be unique and non-null")
    for item in sources:
        if len(item.get("blob_sha", "")) != 40:
            fail(f"historical source lacks a full blob SHA: {item.get('path')}")
        if verify_files:
            got = git_blob(item["path"])
            if got != item["blob_sha"]:
                fail(f"historical source identity drift: {item['path']} {got} != {item['blob_sha']}")

    rcs = contract.get("rcs021_import", {})
    case_ids = rcs.get("case_ids_in_profile_order", [])
    if rcs.get("required_case_count") != 14 or len(case_ids) != 14 or len(set(case_ids)) != 14:
        fail("RCS-021 import must contain exactly fourteen unique historical cases")
    frozen = rcs.get("frozen_measured_identity", {})
    for key in ("head_sha", "workflow_run_id", "artifact_id", "artifact_zip_sha256"):
        if not frozen.get(key):
            fail(f"RCS-021 frozen measured identity missing {key}")
    if frozen.get("availability") not in {"IDENTITY_PINNED_NOT_REDOWLOADED_BY_MC-055", "UNAVAILABLE"}:
        fail("RCS-021 hosted artifact availability must be explicit")

    dispositions = rcs.get("historical_dispositions", {})
    if dispositions.get("bounded_candidate_pass_at_0_5mm_count") != 5:
        fail("historical RCS-021 0.5 mm pass count was rewritten")
    if dispositions.get("accepted_pending_refinement_at_0_5mm_count") != 9:
        fail("historical RCS-021 pending count was rewritten")
    if dispositions.get("external_resource_bound_not_executed_count") != 1:
        fail("historical RCS-021 unexecuted resource-bound cell was erased")
    if dispositions.get("external_resolution_refusal_count") != 1:
        fail("historical RCS-021 resolution refusal was erased")
    if set(dispositions.get("still_outside_150mm3_budget_at_0_25mm", [])) != {"simultaneous-xyz", "cut-through"}:
        fail("historical RCS-021 out-of-budget cells were rewritten")

    mapping = contract.get("strengthened_version_map", [])
    if {x.get("family") for x in mapping} != {f"F{i:02d}" for i in range(1, 17)}:
        fail("strengthened-version map must cover F01-F16 exactly once")
    if len(mapping) != 16:
        fail("strengthened-version map contains duplicate family records")
    for item in mapping:
        status = item.get("status", "")
        if "NEW_RECORD_REQUIRED" not in status:
            fail(f"historical seed was promoted in-place for {item.get('family')}")
        if not item.get("owner", "").startswith("MC-0"):
            fail(f"missing current owner for {item.get('family')}")

    if contract.get("unavailable_inherited_identities") is None:
        fail("unavailable identity list must be explicit even when empty")
    state = contract.get("programme_state", {})
    if state.get("F01-F16") != "UNBUILT":
        fail("MC-055 cannot fabricate mandatory corpus completion")
    if state.get("MC-B") != "NOT_ESTABLISHED" or state.get("MC-1") != "NOT_ESTABLISHED":
        fail("MC-055 cannot promote geometry/programme capability")
    if state.get("native_or_paid_campaign_run") is not False or state.get("production_authorized") is not False:
        fail("MC-055 unexpectedly claims execution/production authority")


def verify_rcs021(contract) -> None:
    plan = load(RCS021_PLAN)
    summary = load(RCS021_SUMMARY)
    imported = contract["rcs021_import"]
    expected = imported["case_ids_in_profile_order"]
    if plan.get("profiles", {}).get("ci") != expected or plan.get("profiles", {}).get("baseline") != expected:
        fail("RCS-021 profile order/denominator drift")
    cases = {x["id"]: x for x in plan.get("cases", [])}
    if list(cases) != expected:
        fail("RCS-021 source case order differs from immutable import")

    w = imported["high_risk_parameter_witnesses"]
    rj = cases["retrace-jitter"]
    if rj["paths"][1][0][1] != float(w["retrace-jitter"]["second_path_y_mm"]):
        fail("retrace-jitter old parameterization drift")
    if rj.get("rcs011_revisit") != w["retrace-jitter"]["rcs011_revisit"]:
        fail("retrace-jitter comparison strategies drift")
    if cases["tangent-zero"]["paths"][0][0][1] != float(w["tangent-zero"]["path_y_mm"]):
        fail("exact tangent historical member drift")
    if cases["tangent-overlap"]["paths"][0][0][1] != float(w["tangent-overlap"]["path_y_mm"]):
        fail("penetrating tangent-neighbour historical member drift")
    if cases["plunge-1um"].get("minimum_positive_feature_mm") != float(w["plunge-1um"]["minimum_positive_feature_mm"]):
        fail("positive 1 um plunge witness drift")
    if cases["cut-through"].get("expected_body_count") != 2:
        fail("historical cut-through lost two-body expectation")
    if cases["high-segment-freehand"].get("generated_path", {}).get("segments") != 160:
        fail("historical high-segment case count drift")

    frozen = imported["frozen_measured_identity"]
    source = summary.get("source", {})
    for key in ("head_sha", "workflow_run_id", "artifact_id", "artifact_zip_sha256", "representation_artifact_id", "representation_artifact_zip_sha256"):
        if source.get(key) != frozen.get(key):
            fail(f"frozen RCS-021 producing identity drift: {key}")
    campaign = summary.get("campaign", {})
    if campaign.get("case_count") != 14 or campaign.get("bounded_candidate_pass_at_0_5mm_count") != 5 or campaign.get("accepted_pending_refinement_at_0_5mm_count") != 9:
        fail("historical RCS-021 measured denominator/disposition drift")
    capability = summary.get("capability", {})
    if set(capability.get("still_outside_150mm3_budget_at_0_25mm", [])) != {"simultaneous-xyz", "cut-through"}:
        fail("historical unresolved refinement evidence was erased")


def verify_inherited_corpus(contract) -> None:
    corpus = load(RCS003_CORPUS)
    records = source_family_index(corpus)
    if contract["inherited_control_corpus"].get("selection") != "ALL fixture_families records in the pinned source are imported by source-local id and revision; category indexes below are views, not copies":
        fail("RCS-003 import no longer covers the full immutable family set")

    views = {
        "lathe": lambda r: r.get("domain") == "lathe",
        "retrace": lambda r: "retrace" in r.get("tags", []),
        "contact": lambda r: bool(set(r.get("tags", [])) & {"tangency", "lower-dimensional-contact", "point-contact", "edge-contact", "face-contact", "coincidence", "coplanarity"}),
        "sub_tolerance": lambda r: bool(set(r.get("tags", [])) & {"sub-tolerance", "sliver", "small-removal", "small-feature", "tiny-cusp"}),
        "separation": lambda r: bool(set(r.get("tags", [])) & {"separation", "cut-through", "multi-body", "connectivity-transition"}),
    }
    for name, predicate in views.items():
        matched = [key for key, record in records.items() if predicate(record)]
        if not matched:
            fail(f"required historical category {name} has no records")

    rcs003_ids = {key[0] for key in records}
    rcs021_ids = set(contract["rcs021_import"]["case_ids_in_profile_order"])
    for row in contract["strengthened_version_map"]:
        for seed in row.get("historical_seeds", []):
            prefix, _, ident = seed.partition(":")
            if prefix == "rcs003" and ident not in rcs003_ids:
                fail(f"strengthened map cites unknown RCS-003 record: {seed}")
            if prefix == "rcs021" and ident not in rcs021_ids:
                fail(f"strengthened map cites unknown RCS-021 case: {seed}")


def verify_measured_negative_controls(contract) -> None:
    r11 = load(RCS011_SUMMARY)
    r12 = load(RCS012_SUMMARY)
    controls = {x["id"]: x for x in contract["decisive_prior_measured_controls"]}

    bad = r11["selected_findings"]["retrace_jitter_freehand_batch"]
    if bad.get("candidate_valid_brep") is not True or bad.get("classification") != "geometric tolerance breach":
        fail("RCS-011 valid-but-wrong negative control was reclassified")
    if bad.get("reference_volume_mm3") != 11490.990138 or bad.get("candidate_volume_mm3") != 12000.0:
        fail("RCS-011 retrace measured values drift")
    timeout = r11["selected_findings"]["sampled_pose_fallback"]
    if timeout.get("attempt_count") != 10 or timeout.get("timeout_count") != 10 or timeout.get("timeout_s") != 30.0:
        fail("RCS-011 timeout evidence drift")

    plunge = r12["decisive_cases"]["tiny-plunge-1um"]
    cusp = r12["decisive_cases"]["tiny-cusp-1um"]
    split = r12["decisive_cases"]["cut-through-two-bodies"]
    if plunge["exact_cell"]["material_volume_mm3"] != "3999.9" or plunge["voxel_0p5"]["material_volume_mm3"] != "4000":
        fail("RCS-012 tiny-plunge evidence drift")
    if cusp["exact_cell"]["body_count"] != 1 or cusp["voxel_0p5"]["body_count"] != 0:
        fail("RCS-012 tiny-cusp body-existence evidence drift")
    if split["exact_cell"]["body_count"] != 2 or split["voxel_0p5"]["body_count"] != 2:
        fail("RCS-012 cut-through body evidence drift")

    required = {"RCS-011-RETRACE-JITTER-VALID-BUT-WRONG", "RCS-011-SAMPLED-POSE-TIMEOUT", "RCS-012-TINY-PLUNGE-1UM", "RCS-012-TINY-CUSP-1UM", "RCS-012-CUT-THROUGH-TWO-BODIES"}
    if set(controls) != required:
        fail("decisive measured-control import is incomplete")


def verify_current_families_unbuilt() -> None:
    families = load(FAMILIES).get("families", [])
    if {x.get("id") for x in families} != {f"F{i:02d}" for i in range(1, 17)}:
        fail("current fixture-family denominator drift")
    if any(x.get("state") != "UNBUILT" for x in families):
        fail("MC-055 must not mark a strengthened fixture family built")


def verify_no_historical_source_edits(contract) -> None:
    baseline = contract["source_baseline"]
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{baseline}..HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    forbidden = sorted(path for path in changed if path.startswith("research/rcs-"))
    if forbidden:
        fail(f"MC-055 edited protected historical RCS sources: {forbidden}")


def expect_rejected(contract, mutate, label: str) -> None:
    bad = copy.deepcopy(contract)
    mutate(bad)
    try:
        validate_structure(bad, verify_files=False)
    except AssertionError:
        return
    fail(f"adversarial corruption accepted: {label}")


def adversarial_controls(contract) -> None:
    expect_rejected(contract, lambda x: x["rcs021_import"]["case_ids_in_profile_order"].pop(), "drop one RCS-021 case")
    expect_rejected(contract, lambda x: x["rcs021_import"]["historical_dispositions"].__setitem__("accepted_pending_refinement_at_0_5mm_count", 0), "erase pending historical cells")
    expect_rejected(contract, lambda x: x["rcs021_import"]["historical_dispositions"].__setitem__("external_resolution_refusal_count", 0), "erase historical refusal")
    expect_rejected(contract, lambda x: x["strengthened_version_map"][0].__setitem__("status", "BUILT_FROM_HISTORICAL_PASS"), "promote historical seed in place")
    expect_rejected(contract, lambda x: x["programme_state"].__setitem__("F01-F16", "BUILT"), "fabricate strengthened corpus completion")
    expect_rejected(contract, lambda x: x["programme_state"].__setitem__("MC-B", "ACCEPTED"), "promote geometry capability")
    expect_rejected(contract, lambda x: x["historical_sources"][0].__setitem__("blob_sha", "0" * 39), "weaken historical source identity")


def verify_contract() -> None:
    contract = load(CONTRACT_PATH)
    validate_structure(contract, verify_files=True)
    verify_rcs021(contract)
    verify_inherited_corpus(contract)
    verify_measured_negative_controls(contract)
    verify_current_families_unbuilt()
    verify_no_historical_source_edits(contract)
    adversarial_controls(contract)
    print("MC-055 immutable historical corpus import passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    args = parser.parse_args()
    if not args.contract:
        parser.error("--contract is required; MC-055 has no native campaign")
    verify_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
