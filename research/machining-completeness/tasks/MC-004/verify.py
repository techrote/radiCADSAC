#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-004"
CONTRACT = TASK / "qualification-contract-v1.json"
MC002 = ROOT / "research" / "machining-completeness" / "tasks" / "MC-002" / "domain-contract-v1.json"

T2_COUNTS = {
    "T2-G10": 10,
    "T2-G100": 100,
    "T2-G1000": 1000,
    "T2-G10000": 10000,
}
REQUIRED_ACCURACY = {"A-SEMANTIC", "A-ENGINEERING", "A-PRECISION-BOUNDARY"}
REQUIRED_OPEN = {"OQ-004-01", "OQ-004-02", "OQ-004-03", "OQ-004-04"}


def fail(msg: str) -> None:
    raise AssertionError(msg)


def validate(obj: dict) -> None:
    if obj.get("schema") != "radicadsac-mc-qualification-contract/1.0" or obj.get("task") != "MC-004":
        fail("schema/task mismatch")
    if obj.get("status") != "reviewed-qualification-artifact":
        fail("qualification artifact status drift")
    if obj.get("native_geometry_claimed") is not False:
        fail("planning contract promoted to native geometry evidence")
    if obj.get("candidate_independent") is not True or obj.get("retroactive_tuning_forbidden") is not True:
        fail("candidate independence weakened")
    if obj.get("evidence_class") != ["REQUIREMENT", "DESIGN_DECISION", "DOCUMENTATION_RECONCILIATION"]:
        fail("evidence class drift")

    deps = obj.get("dependency_inputs", [])
    if len(deps) != 1 or deps[0].get("task") != "MC-002":
        fail("MC-002 artifact dependency missing")
    if deps[0].get("blob_sha") != "930db704e9dd29955e7af99ba793c74e0cfda325":
        fail("MC-002 dependency blob drift")

    freeze = obj.get("freeze_policy", {})
    frozen = set(freeze.get("frozen_before_candidate_qualification", []))
    for name in (
        "required operation denominator",
        "workload profile identities and deterministic generation seed",
        "accuracy vectors",
        "reference hardware",
        "repeat protocol",
        "latency and memory envelopes",
        "timeout/resource verdict policy",
    ):
        if name not in frozen:
            fail(f"missing preregistration freeze: {name}")
    if freeze.get("candidate_specific_override_forbidden") is not True:
        fail("candidate-specific override permitted")
    if freeze.get("provider_or_solver_refusal_does_not_remove_case") is not True:
        fail("provider refusal can narrow denominator")
    if set(freeze.get("unresolved_product_domain_decisions_remain_open", [])) != {"DD-002-04", "DD-002-05"}:
        fail("inherited open domain decisions silently resolved")
    if "retroactively pass" not in freeze.get("allowed_prospective_change", ""):
        fail("prospective-only revision rule missing")

    mc2 = json.loads(MC002.read_text(encoding="utf-8"))
    admitted = {x["id"] for x in mc2["operation_map"] if x.get("status") == "admitted"}
    covered = set(obj.get("required_operation_coverage", []))
    if admitted != covered:
        fail(f"MC-002 admitted operation denominator drift: missing={sorted(admitted-covered)} extra={sorted(covered-admitted)}")

    gen = obj.get("workload_generation", {})
    if gen.get("algorithm_id") != "mc004-candidate-blind-workload-v1":
        fail("workload generator identity drift")
    seed = gen.get("seed_sha256", "")
    if len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed):
        fail("invalid deterministic seed")
    if gen.get("candidate_feedback_may_change_generated_cases") is not False:
        fail("candidate feedback may mutate workloads")
    if gen.get("source_order_is_semantically_preserved") is not True:
        fail("source order preservation weakened")
    if "positive-volume" not in gen.get("material_change_count_definition", ""):
        fail("geometry-changing section definition weakened")
    if "zero additional nominal removed volume" not in gen.get("redundant_history_definition", ""):
        fail("redundant-history control definition weakened")

    profiles = {x.get("id"): x for x in obj.get("workload_profiles", [])}
    if "T0-DECISIVE" not in profiles or "T1-DOMAIN" not in profiles:
        fail("T0/T1 workload profile missing")
    if profiles["T0-DECISIVE"].get("minimum_valid_cases", 0) < 12:
        fail("T0 decisive corpus weakened")
    if profiles["T1-DOMAIN"].get("minimum_valid_cases", 0) < len(admitted):
        fail("T1 cannot cover every admitted operation")
    if "every ID in required_operation_coverage" not in profiles["T1-DOMAIN"].get("coverage", ""):
        fail("T1 denominator linkage missing")
    for pid, count in T2_COUNTS.items():
        p = profiles.get(pid)
        if not p or p.get("required") is not True:
            fail(f"required T2 profile missing: {pid}")
        if p.get("genuine_geometry_changing_sections") != count:
            fail(f"wrong genuine geometry count for {pid}")
        if p.get("redundant_history_control_sections") != count:
            fail(f"wrong redundant-history control count for {pid}")

    acc = {x.get("id"): x for x in obj.get("accuracy_profiles", [])}
    if set(acc) != REQUIRED_ACCURACY:
        fail("accuracy profile set drift")
    semantic = acc["A-SEMANTIC"]["requirements"]
    if "positive-volume" not in semantic.get("material_state", ""):
        fail("positive-volume material protection weakened")
    if "exact" not in semantic.get("body_identity_and_count", ""):
        fail("body identity/count exactness weakened")
    engineering = acc["A-ENGINEERING"]["requirements"]
    for key in ("boundary_two_sided_hausdorff_um_max", "reported_dimension_error_um_max", "reported_angular_error_urad_max"):
        v = engineering.get(key)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0 or v > 5.0:
            fail(f"engineering accuracy weakened: {key}")
    if engineering.get("volume_relative_error_max", 1) > 0.000001:
        fail("volume relative-error limit weakened")
    if "does not authorize deleting or merging" not in engineering.get("small_feature_rule", ""):
        fail("accuracy tolerance became a topology/feature floor")
    precision = acc["A-PRECISION-BOUNDARY"]["requirements"]
    for key in ("boundary_two_sided_hausdorff_um_max", "reported_dimension_error_um_max", "reported_angular_error_urad_max"):
        v = precision.get(key)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0 or v > 0.5:
            fail(f"precision-boundary target weakened: {key}")

    hw = obj.get("reference_hardware", {})
    primary = hw.get("primary", {})
    if primary.get("id") != "MC-RH-Q1" or primary.get("cpu") != "AMD Ryzen 5 5600X":
        fail("primary reference hardware drift")
    if primary.get("physical_cores") != 6 or primary.get("hardware_threads") != 12 or primary.get("memory_gib") != 64:
        fail("primary reference resources drift")
    if primary.get("gpu_required") is not False or primary.get("qualification_cpu_thread_cap") != 12:
        fail("reference execution resource semantics drift")
    secondary = hw.get("secondary_baseline", {})
    if secondary.get("id") != "MC-RH-B1" or secondary.get("cpu") != "AMD Ryzen 5 2600X":
        fail("secondary reference hardware drift")

    ep = obj.get("execution_protocol", {})
    if ep.get("final_required_completed_repeats") != 3 or ep.get("repeats_are_sequential") is not True:
        fail("repeat protocol weakened")
    if ep.get("nested_parallelism_must_be_bounded_and_reported") is not True:
        fail("nested parallelism became unbounded")
    if ep.get("all_attempts_retained_including_crash_timeout_and_incomplete") is not True:
        fail("negative attempts may be lost")
    if ep.get("paid_or_native_execution_authorized_by_this_contract") is not False:
        fail("MC-004 improperly authorizes native/paid campaign")

    env = {x.get("profile"): x for x in obj.get("resource_envelopes_primary_reference", [])}
    if set(env) != {"T0-DECISIVE", "T1-DOMAIN", *T2_COUNTS}:
        fail("resource envelope profile set drift")
    for pid, row in env.items():
        if row.get("peak_rss_gib_max", 0) <= 0 or row.get("timeout_seconds", 0) <= 0:
            fail(f"unbounded resource envelope: {pid}")
        wall = row.get("per_case_wall_seconds_max", row.get("session_wall_seconds_max"))
        if not isinstance(wall, int) or wall <= 0 or row["timeout_seconds"] < wall:
            fail(f"invalid wall/timeout envelope: {pid}")
    if env["T2-G10000"]["session_wall_seconds_max"] > 1200 or env["T2-G10000"]["peak_rss_gib_max"] > 24:
        fail("T2-G10000 usability envelope weakened")

    verdict = obj.get("verdict_policy", {})
    for key in ("timeout_is_pass", "resource_exhaustion_is_pass", "pending_or_refusal_is_pass"):
        if verdict.get(key) is not False:
            fail(f"nonpass state promoted to pass: {key}")
    if verdict.get("smaller_scale_substitution_for_required_tier_forbidden") is not True:
        fail("required scale may be substituted")
    if verdict.get("candidate_success_is_not_oracle") is not True:
        fail("candidate success became oracle")

    oq = {x.get("id"): x for x in obj.get("open_questions", [])}
    if set(oq) != REQUIRED_OPEN:
        fail("open-question register drift")
    if oq["OQ-004-03"].get("status") != "propagated_from_MC-002" or oq["OQ-004-04"].get("status") != "propagated_from_MC-002":
        fail("MC-002 open domain questions silently resolved")
    if "no old or guessed price" not in oq["OQ-004-02"].get("status", ""):
        fail("guessed tariff permitted")


def must_reject(base: dict, mutate, label: str) -> None:
    bad = copy.deepcopy(base)
    mutate(bad)
    try:
        validate(bad)
    except AssertionError:
        return
    fail(f"adversarial control was not rejected: {label}")


def adversarial_self_test(base: dict) -> None:
    must_reject(base, lambda x: x.__setitem__("candidate_independent", False), "candidate-specific profile")
    must_reject(base, lambda x: x["freeze_policy"].__setitem__("candidate_specific_override_forbidden", False), "candidate override")
    must_reject(base, lambda x: x["required_operation_coverage"].pop(), "dropped admitted operation")
    must_reject(base, lambda x: x["workload_generation"].__setitem__("candidate_feedback_may_change_generated_cases", True), "feedback-tuned fixtures")
    must_reject(base, lambda x: next(p for p in x["workload_profiles"] if p["id"] == "T2-G10000").__setitem__("genuine_geometry_changing_sections", 1000), "shrunken 10k tier")
    must_reject(base, lambda x: next(a for a in x["accuracy_profiles"] if a["id"] == "A-ENGINEERING")["requirements"].__setitem__("boundary_two_sided_hausdorff_um_max", 50.0), "inflated tolerance")
    must_reject(base, lambda x: next(a for a in x["accuracy_profiles"] if a["id"] == "A-ENGINEERING")["requirements"].__setitem__("small_feature_rule", "features under tolerance may be deleted"), "tolerance as feature floor")
    must_reject(base, lambda x: x["reference_hardware"]["primary"].__setitem__("cpu", "candidate chooses"), "candidate-selected hardware")
    must_reject(base, lambda x: x["execution_protocol"].__setitem__("repeats_are_sequential", False), "parallel repeats")
    must_reject(base, lambda x: next(r for r in x["resource_envelopes_primary_reference"] if r["profile"] == "T2-G10000").__setitem__("peak_rss_gib_max", 64), "unusable memory expansion")
    must_reject(base, lambda x: x["verdict_policy"].__setitem__("timeout_is_pass", True), "timeout as pass")
    must_reject(base, lambda x: x["open_questions"][1].__setitem__("status", "assume historical tariff"), "guessed tariff")
    must_reject(base, lambda x: x.__setitem__("native_geometry_claimed", True), "planning evidence promoted to native geometry")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    args = ap.parse_args()
    if not args.contract:
        ap.error("--contract is required")
    obj = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate(obj)
    adversarial_self_test(obj)
    print("MC-004 qualification contract and adversarial controls passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
