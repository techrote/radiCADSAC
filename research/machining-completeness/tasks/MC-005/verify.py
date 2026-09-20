#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-005"
CONTRACT = TASK / "domain-lock-review-v1.json"
MC002 = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
MC003 = MC / "tasks" / "MC-003" / "numeric-encoding-contract-v1.json"
MC004 = MC / "tasks" / "MC-004" / "qualification-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
OUTCOMES = MC / "outcomes-v1.json"
POS = MC / "proof-obligations-v1.json"

DEPENDENCY_BLOBS = {
    "MC-002": (MC / "tasks" / "MC-002" / "outcome.json", "930db704e9dd29955e7af99ba793c74e0cfda325"),
    "MC-003": (MC / "tasks" / "MC-003" / "outcome.json", "8f335f59f36c8761844806f9059af4a4f1671044"),
    "MC-004": (MC / "tasks" / "MC-004" / "outcome.json", "4f032ac5ff2584c48084fac3282c137a00731d40"),
    "MC-056": (MC / "tasks" / "MC-056" / "outcome.json", "e9b971c593ca1a90baf17f9ae9a5a568dd313ac3"),
}
BOUNDARY_IDS = {"DD-002-04", "DD-002-05"}
ACCURACY_IDS = {"A-SEMANTIC", "A-ENGINEERING", "A-PRECISION-BOUNDARY"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str) -> None:
    raise AssertionError(msg)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate(obj: dict, *, check_registries: bool = True) -> None:
    if obj.get("schema") != "radicadsac-mc-domain-lock-review/1.0" or obj.get("task") != "MC-005":
        fail("schema/task mismatch")
    if obj.get("status") != "accepted-domain-lock":
        fail("domain-lock status drift")
    if obj.get("native_geometry_claimed") is not False or obj.get("native_or_paid_execution") is not False:
        fail("MC-005 promoted planning evidence or authorized native execution")
    if obj.get("source_baseline") != "0ef8235ed9bd7e807a04f7ad048dae2929c131c3":
        fail("unexpected MC-005 source baseline")

    deps = {d.get("task"): d for d in obj.get("dependencies", [])}
    if set(deps) != set(DEPENDENCY_BLOBS):
        fail("dependency set drift")
    for task, (path, expected) in DEPENDENCY_BLOBS.items():
        if deps[task].get("git_blob_sha1") != expected:
            fail(f"declared dependency blob drift for {task}")
        if git_blob_sha1(path) != expected:
            fail(f"live dependency artifact drift for {task}")
        if load(path).get("result_kind") != "COMPLETED_RESEARCH":
            fail(f"dependency result kind no longer accepted for {task}")

    mc2 = load(MC002)
    admitted = [x["id"] for x in mc2.get("operation_map", []) if x.get("status") == "admitted"]
    lock = obj.get("domain_lock", {})
    if lock.get("operation_denominator") != admitted or lock.get("operation_count") != len(admitted):
        fail("integrated domain denominator differs from MC-002")
    if len(admitted) != 26 or len(set(admitted)) != 26:
        fail("unexpected admitted-operation count/duplicates")
    for key in (
        "physical_validity_is_candidate_independent",
        "provider_or_solver_refusal_does_not_remove_case",
        "positive_volume_material_may_not_be_deleted_by_tolerance_policy",
        "durable_body_identity_is_not_backend_topology_identity",
        "engaged_motion_must_be_continuous",
        "detached_material_requires_retention_or_explicit_reclamp_before_further_machining",
        "whole_body_removal_and_empty_material_are_valid",
    ):
        if lock.get(key) is not True:
            fail(f"domain invariant weakened: {key}")

    historical = {x.get("id"): x for x in mc2.get("named_domain_decisions", [])}
    if set(historical) < BOUNDARY_IDS:
        fail("historical MC-002 boundary decisions missing")
    if any(historical[i].get("status") != "open_product_domain_decision" for i in BOUNDARY_IDS):
        fail("historical boundary decision was rewritten instead of integrated")
    resolutions = {x.get("id"): x for x in obj.get("product_boundary_resolutions", [])}
    if set(resolutions) != BOUNDARY_IDS:
        fail("MC-005 must resolve exactly the two inherited open domain decisions")
    for did, row in resolutions.items():
        if row.get("historical_mc002_status") != "open_product_domain_decision":
            fail(f"historical status lost for {did}")
        if row.get("mc005_status") != "excluded_by_current_mc1_scope":
            fail(f"current-tranche scope resolution missing for {did}")
        if row.get("provider_or_solver_based") is not False:
            fail(f"provider/solver improperly decides {did}")
        if row.get("changes_current_denominator") is not False:
            fail(f"scope decision shrinks current denominator for {did}")
        if row.get("future_scope_requires_contract_revision") is not True:
            fail(f"future scope can silently mutate MC-A for {did}")
        basis = row.get("basis", "")
        if "current MC-1 tranche" not in basis or "remains in scope" not in basis:
            fail(f"scope basis lacks current-tranche/equivalent-history guard for {did}")

    programme_doc = (ROOT / "docs" / "machining-completeness" / "00-PROGRAMME.md").read_text(encoding="utf-8")
    founding = (ROOT / "docs" / "00-FOUNDING-BRIEF.md").read_text(encoding="utf-8")
    if "conventional lathe and fixed-axis three-axis mill domain" not in programme_doc:
        fail("programme domain authority drift")
    if "Only two machine families are in initial scope" not in founding:
        fail("founding machine-scope authority drift")

    mc3 = load(MC003)
    num = obj.get("numeric_lock", {})
    legacy = mc3.get("legacy_msac_journal_1_0", {})
    exact = mc3.get("mc1_exact_source_profile", {})
    if num.get("legacy_schema") != legacy.get("schema_id") or num.get("legacy_saved_meaning_preserved") is not True:
        fail("legacy journal meaning not preserved")
    if exact.get("id") != "mc-exact-source/1.0" or num.get("mc1_required_exact_source_profile") != exact.get("id"):
        fail("exact-source profile drift")
    rules = exact.get("rules", {})
    if rules.get("global_untyped_epsilon_forbidden") is not True or rules.get("tolerance_as_predicate_sign_forbidden") is not True:
        fail("numeric authority weakened")
    for key in (
        "finite_exact_semantics_required_for_admitted_trajectory_setup_and_phase_constructors",
        "unsupported_required_extension_rejects_instead_of_downcasts",
        "new_revision_only_migration",
        "lost_precision_is_not_fabricated",
        "dimensionally_untyped_global_epsilon_forbidden",
        "tolerance_as_predicate_sign_forbidden",
        "silent_integer_wrap_or_saturation_forbidden",
        "nonfinite_authority_values_forbidden",
    ):
        if num.get(key) is not True:
            fail(f"integrated numeric invariant weakened: {key}")

    mc4 = load(MC004)
    q = obj.get("qualification_lock", {})
    if mc4.get("required_operation_coverage") != admitted:
        fail("MC-004 denominator does not exactly match MC-002")
    if q.get("candidate_independent") is not True or q.get("candidate_specific_override_forbidden") is not True:
        fail("candidate-independent qualification weakened")
    if q.get("workload_generator") != mc4.get("workload_generation", {}).get("algorithm_id"):
        fail("workload generator identity drift")
    if q.get("seed_sha256") != mc4.get("workload_generation", {}).get("seed_sha256"):
        fail("workload seed drift")
    profiles = {x.get("id"): x for x in mc4.get("workload_profiles", [])}
    expected_counts = [profiles[f"T2-G{n}"].get("genuine_geometry_changing_sections") for n in (10, 100, 1000, 10000)]
    if q.get("required_t2_genuine_geometry_sections") != expected_counts or expected_counts != [10, 100, 1000, 10000]:
        fail("T2 genuine-geometry ladder drift")
    if q.get("separate_redundant_history_controls") is not True:
        fail("redundant-history controls lost")
    if set(q.get("accuracy_profiles", [])) != ACCURACY_IDS:
        fail("accuracy-profile set drift")
    if q.get("primary_reference_hardware") != mc4.get("reference_hardware", {}).get("primary", {}).get("id"):
        fail("reference hardware drift")
    ep = mc4.get("execution_protocol", {})
    if q.get("final_completed_repeats") != ep.get("final_required_completed_repeats") or q.get("final_completed_repeats") != 3:
        fail("repeat count drift")
    if q.get("repeats_are_sequential") is not True or ep.get("repeats_are_sequential") is not True:
        fail("sequential repeat rule weakened")
    if q.get("paid_or_native_execution_authorized") is not False or ep.get("paid_or_native_execution_authorized_by_this_contract") is not False:
        fail("qualification contract improperly authorizes native/paid execution")

    protected = obj.get("protected_semantics", {})
    if not protected or any(v is not True for v in protected.values()):
        fail("protected source/provenance/journal/body/negative-evidence semantics weakened")

    po = obj.get("po01", {})
    gate = obj.get("gate", {})
    if po.get("id") != "PO-01" or po.get("decision") != "ACCEPTED":
        fail("PO-01 decision missing")
    if gate.get("id") != "MC-A" or gate.get("owner") != "MC-005" or gate.get("decision") != "ACCEPTED":
        fail("MC-A decision missing")
    if gate.get("non_compensating") is not True:
        fail("MC-A became compensating")
    nonclaims = "\n".join(obj.get("claims_not_made", []))
    for token in ("MC-B remains NOT_ESTABLISHED", "no native", "no conventional B-rep/STEP", "no practical native", "no MC-1", "no production"):
        if token not in nonclaims:
            fail(f"required non-claim missing: {token}")

    if check_registries:
        programme = load(PROGRAMME)
        gates = {g["id"]: g for g in programme.get("gates", [])}
        if gates.get("MC-A", {}).get("state") != "ACCEPTED":
            fail("programme registry did not accept MC-A")
        if any(gates[x].get("state") != "NOT_ESTABLISHED" for x in ("MC-B", "MC-C", "MC-D", "MC-E", "MC-F", "MC-1")):
            fail("later gate was prematurely accepted")
        if programme.get("capability_status") != "NOT_ESTABLISHED" or programme.get("production_authorized") is not False or programme.get("expensive_execution_authorized") is not False:
            fail("programme/production state improperly advanced")

        outcomes = load(OUTCOMES).get("tasks", {})
        if outcomes.get("MC-005", {}).get("state") != "CAPABILITY_ACCEPTED":
            fail("MC-005 outcome registry not capability-accepted")
        if outcomes["MC-005"].get("blockers") != []:
            fail("accepted MC-005 retains blockers")

        pos = {p["id"]: p for p in load(POS).get("obligations", [])}
        if pos.get("PO-01", {}).get("state") != "ACCEPTED":
            fail("PO-01 registry not accepted")
        if "research/machining-completeness/tasks/MC-005/domain-lock-review-v1.json" not in pos["PO-01"].get("accepted_evidence", []):
            fail("PO-01 accepted evidence binding missing")
        if any(pos[f"PO-{i:02d}"].get("state") != "OPEN" for i in range(2, 13)):
            fail("later proof obligation was prematurely accepted")


def must_reject(base: dict, mutate, label: str) -> None:
    bad = copy.deepcopy(base)
    mutate(bad)
    try:
        validate(bad, check_registries=False)
    except AssertionError:
        return
    fail(f"adversarial control was not rejected: {label}")


def adversarial_self_test(base: dict) -> None:
    must_reject(base, lambda x: x["domain_lock"]["operation_denominator"].pop(), "dropped admitted operation")
    must_reject(base, lambda x: x["product_boundary_resolutions"][0].__setitem__("provider_or_solver_based", True), "provider-driven scope")
    must_reject(base, lambda x: x["product_boundary_resolutions"][0].__setitem__("changes_current_denominator", True), "scope shrinkage")
    must_reject(base, lambda x: x["product_boundary_resolutions"][0].__setitem__("mc005_status", "open_product_domain_decision"), "unresolved product boundary")
    must_reject(base, lambda x: x.__setitem__("native_geometry_claimed", True), "planning evidence promoted to native geometry")
    must_reject(base, lambda x: x["qualification_lock"].__setitem__("candidate_independent", False), "candidate-specific qualification")
    must_reject(base, lambda x: x["qualification_lock"].__setitem__("seed_sha256", "0" * 64), "workload seed mutation")
    must_reject(base, lambda x: x["numeric_lock"].__setitem__("mc1_required_exact_source_profile", "legacy-only"), "exact-source profile weakened")
    must_reject(base, lambda x: x["protected_semantics"].__setitem__("journal_saved_meaning_preserved", False), "journal semantics weakened")
    must_reject(base, lambda x: x["gate"].__setitem__("decision", "NOT_ESTABLISHED"), "gate decision drift")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    args = ap.parse_args()
    if not args.contract:
        ap.error("--contract is required")
    obj = load(CONTRACT)
    validate(obj)
    adversarial_self_test(obj)
    print("MC-005 integrated domain lock, PO-01, MC-A and adversarial controls passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
