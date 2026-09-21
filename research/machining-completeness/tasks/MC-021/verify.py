#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

from rotational_reduction import (  # noqa: E402
    F,
    Line2,
    MeridianRect,
    REQUIRED_FALSE,
    REQUIRED_TRUE,
    admissible,
    admission_failures,
    exact_pi_volume_coeff,
    revolved_rect_contains_cartesian,
    subtract_rect,
    swept_rect_contains,
    swept_rect_contains_cartesian_rational_radius,
)

CONTRACT = HERE / "lathe-rotational-reduction-contract-v1.json"
OUTCOME = HERE / "outcome.json"
REPORT = HERE / "report.md"
DOC = ROOT / "docs/machining-completeness/16-MC021-LATHE-ROTATIONAL-REDUCTION.md"

EXPECTED_DEPS = {
    "MC-005": ("research/machining-completeness/tasks/MC-005/outcome.json", "adec886597a06345fdfdf65ee018596cd396d249", "CAPABILITY_ACCEPTED"),
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-058": ("research/machining-completeness/tasks/MC-058/outcome.json", "038fccda9142650ee7e29c626aeb8e4602420278", "COMPLETED_RESEARCH"),
}


class ContractError(RuntimeError):
    pass


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ContractError(msg)


def reject_floats(obj: Any, where: str = "root") -> None:
    if isinstance(obj, float):
        raise ContractError(f"binary JSON float forbidden at {where}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            reject_floats(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            reject_floats(v, f"{where}[{i}]")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def baseline_meta() -> dict[str, object]:
    meta: dict[str, object] = {key: True for key in REQUIRED_TRUE}
    meta.update({key: False for key in REQUIRED_FALSE})
    meta.update(
        phase_domain="FULL_S1_FOR_EACH_MERIDIAN_STATE",
        fallback_owner="MC-022",
        material_representation="EXACT_AXISYMMETRIC_MERIDIAN",
    )
    return meta


def validate_contract_obj(c: dict[str, Any]) -> None:
    reject_floats(c)
    require(c.get("schema") == "radicadsac-mc021-lathe-rotational-reduction/1.0", "schema drift")
    require(c.get("task") == "MC-021" and c.get("issue") == 83, "task/issue drift")
    require(c.get("source_baseline") == "11e7023edff0469b4b9f72193e8096512075afae", "source baseline drift")
    require(c.get("native_execution") is False, "native execution must remain false")

    deps = c.get("formal_dependencies")
    require(isinstance(deps, list) and len(deps) == 3, "formal dependency set drift")
    got = {d.get("task"): (d.get("path"), d.get("blob_sha"), d.get("result_kind")) for d in deps if isinstance(d, dict)}
    require(got == EXPECTED_DEPS, "formal dependency identity/result drift")

    auth = c.get("authority", {})
    for key in (
        "saved_operation_is_immutable",
        "engagement_boundaries_are_authoritative",
        "positive_volume_material_may_not_be_erased_by_tolerance",
        "durable_body_identity_is_not_backend_topology",
    ):
        require(auth.get(key) is True, f"authority weakened: {key}")
    require(auth.get("native_geometry_claimed") is False, "deterministic model promoted to native geometry")

    theorem = c.get("theorem", {})
    stmt = theorem.get("statement", "")
    require("K(q,theta)=R_theta A(q)" in stmt, "factorization theorem removed")
    require("Q x S1" in stmt and "regularized post-cut material" in stmt, "full-orbit/material theorem weakened")
    require("sufficient admission predicate" in theorem.get("scope", ""), "sufficiency scope missing")

    pred = c.get("admission_predicate", {})
    require(tuple(pred.get("required_true", [])) == REQUIRED_TRUE, "required-true admission set drift")
    require(tuple(pred.get("required_false", [])) == REQUIRED_FALSE, "required-false admission set drift")
    require(pred.get("phase_domain") == "FULL_S1_FOR_EACH_MERIDIAN_STATE", "full phase product weakened")
    require(pred.get("material_representation") == "EXACT_AXISYMMETRIC_MERIDIAN", "material quotient authority drift")
    require(pred.get("fallback_owner") == "MC-022", "phase-sensitive fallback owner drift")
    require(pred.get("operation_name_is_not_admission_evidence") is True, "operation labels promoted to proof")
    require(pred.get("ordinary_od_or_facing_label_alone_is_insufficient") is True, "ordinary turning label shortcut enabled")
    require(pred.get("nonaxisymmetric_target_material_rejects_material_domain_reduction") is True, "nonaxisymmetric target allowed")

    subtype = c.get("bounded_executable_subtype", {})
    require(subtype.get("name") == "exact_rational_meridian_rectangles_v1", "bounded subtype drift")
    require("one shared exact source parameter" in subtype.get("membership", ""), "shared source parameter lost")
    require("coefficient times pi" in subtype.get("volume", ""), "symbolic pi volume authority lost")

    forbidden = set(c.get("forbidden_shortcuts", []))
    needles = (
        "N sampled spindle angles",
        "eccentric or tilted setup",
        "nonaxisymmetric durable target body",
        "global epsilon",
        "merging durable bodies",
        "canonical operation journal",
        "native geometry evidence",
    )
    for needle in needles:
        require(any(needle in x for x in forbidden), f"forbidden shortcut missing: {needle}")

    routing = c.get("routing", {})
    require(routing.get("rejected_phase_sensitive_cases") == "MC-022", "MC-022 routing lost")
    require(routing.get("reclamp_reorientation_and_multi_setup_composition") == "MC-023", "MC-023 routing lost")

    retained = {x.get("id"): x.get("status") for x in c.get("retained_open_obligations", []) if isinstance(x, dict)}
    require(retained.get("PB-007-01") == "OPEN", "PB-007-01 closed or missing")
    require(retained.get("PB-007-02") == "OPEN", "PB-007-02 closed or missing")
    require(retained.get("PB-007-03") == "OPEN_PROPAGATED", "PB-007-03 closed or missing")

    pb = c.get("programme_boundary", {})
    for po in ("PO-02", "PO-04", "PO-05", "PO-06"):
        require(pb.get(po) == "OPEN", f"{po} must remain OPEN")
    for gate in ("MC-B", "MC-C", "MC-D", "MC-E", "MC-F", "MC-1"):
        require(pb.get(gate) == "NOT_ESTABLISHED", f"{gate} prematurely promoted")
    require(pb.get("native_or_paid_campaign_run") is False, "native/paid campaign falsely claimed")


def check_dependency_blobs(c: dict[str, Any]) -> None:
    for dep in c["formal_dependencies"]:
        path = ROOT / dep["path"]
        require(path.exists(), f"missing dependency artifact: {dep['path']}")
        require(git_blob_sha(path) == dep["blob_sha"], f"dependency blob drift: {dep['task']}")
        obj = json.loads(path.read_text(encoding="utf-8"))
        require(obj.get("task") == dep["task"], f"dependency task mismatch: {dep['task']}")
        require(obj.get("result_kind") == dep["result_kind"], f"dependency result mismatch: {dep['task']}")


def check_repo_artifacts(c: dict[str, Any]) -> None:
    check_dependency_blobs(c)
    outcome = json.loads(OUTCOME.read_text(encoding="utf-8"))
    require(outcome.get("task") == "MC-021", "outcome task mismatch")
    require(outcome.get("result_kind") == "COMPLETED_RESEARCH", "outcome result mismatch")
    require(outcome.get("native_execution") is False, "outcome native execution drift")
    for blocker in ("PB-007-01", "PB-007-02", "PB-007-03"):
        require(blocker in outcome.get("retained_external_blockers", []), f"outcome lost {blocker}")
    report = REPORT.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    for text in (report, doc):
        require("Q × S1" in text, "full-orbit product domain missing from documentation")
        require("MC-022" in text and "MC-023" in text, "downstream routing missing from documentation")
        require("NOT_ESTABLISHED" in text, "programme gate boundary missing from documentation")


def exact_controls() -> None:
    meta = baseline_meta()
    require(admissible(meta), f"baseline admission unexpectedly rejected: {admission_failures(meta)}")

    cutter = MeridianRect(F(4), F(5), F(2), F(3))
    z = F(5, 2)
    require(revolved_rect_contains_cartesian(cutter, F(12, 5), F(16, 5), z), "r=4 off-axis tangent must classify inside closed sweep")
    require(revolved_rect_contains_cartesian(cutter, F(3), F(4), z), "r=5 3-4-5 point must classify inside")
    require(revolved_rect_contains_cartesian(cutter, F(-3), F(-4), z), "rotation invariance failed")
    delta = F(1, 1_000_000)
    require(not revolved_rect_contains_cartesian(cutter, F(4) - delta, F(0), z), "signed radial outside neighbour accepted")
    require(revolved_rect_contains_cartesian(cutter, F(4) + delta, F(0), z), "signed radial inside neighbour rejected")

    rect = MeridianRect(F(1), F(2), F(0), F(1))
    motion = Line2(F(0), F(0), F(2), F(2))
    require(swept_rect_contains(rect, motion, F(2), F(1)), "shared-parameter equality control failed")
    require(not swept_rect_contains(rect, motion, F(1), F(3)), "decoupled endpoint-AABB false positive accepted")
    require(
        swept_rect_contains_cartesian_rational_radius(rect, motion, F(3, 2), F(2), F(3, 2)),
        "off-axis rational-radius simultaneous-feed control failed",
    )

    stock = MeridianRect(F(0), F(5), F(0), F(10))
    tangent = MeridianRect(F(5), F(6), F(2), F(3))
    tangent_result = subtract_rect(stock, tangent)
    require(tangent_result == [stock], "exact tangent deleted positive material")
    require(exact_pi_volume_coeff(tangent_result) == F(250), "tangent changed exact symbolic volume")
    penetration = MeridianRect(F(5) - delta, F(6), F(2), F(3))
    penetrated = subtract_rect(stock, penetration)
    require(exact_pi_volume_coeff(penetrated) < F(250), "signed penetration did not remove positive volume")

    part = MeridianRect(F(0), F(5), F(4), F(6))
    parted = subtract_rect(stock, part)
    require(parted == [MeridianRect(F(0), F(5), F(0), F(4)), MeridianRect(F(0), F(5), F(6), F(10))], "parting components incorrect")
    require(len(parted) == 2, "parting lost a component")
    require(exact_pi_volume_coeff(parted) == F(200), "parting symbolic volume mismatch")

    reject_cases = {
        "nonaxisymmetric target": ("target_axisymmetry_certificate", False),
        "certificate/body mismatch": ("certificate_bound_to_target_body", False),
        "certificate/setup mismatch": ("certificate_bound_to_setup_revision", False),
        "eccentric setup": ("eccentric_setup", True),
        "phase synchronization": ("phase_synchronization", True),
        "timed phase geometry": ("timed_phase_motion_required_for_geometry", True),
        "partial phase": ("partial_phase_engagement", True),
        "sampled angle": ("sampled_angle_authority", True),
        "global epsilon": ("global_epsilon_authority", True),
        "holder witness loss": ("holder_clearance_witness_present", False),
        "access witness loss": ("physical_access_witness_present", False),
    }
    for name, (key, value) in reject_cases.items():
        m = dict(meta)
        m[key] = value
        require(not admissible(m), f"inadmissible case accepted: {name}")
    m = dict(meta); m["phase_domain"] = "FINITE_SAMPLES"
    require(not admissible(m), "finite angular samples accepted as full S1")
    m = dict(meta); m["material_representation"] = "NONAXISYMMETRIC_3D"
    require(not admissible(m), "nonaxisymmetric material representation accepted")
    m = dict(meta); m["fallback_owner"] = "NONE"
    require(not admissible(m), "phase-sensitive fallback owner erased")


def expect_contract_reject(c: dict[str, Any], mutator, label: str) -> None:
    x = copy.deepcopy(c)
    mutator(x)
    try:
        validate_contract_obj(x)
    except ContractError:
        return
    raise ContractError(f"adversarial mutation accepted: {label}")


def adversarial_contract_controls(c: dict[str, Any]) -> None:
    attacks = [
        (lambda x: x["admission_predicate"]["required_true"].remove("target_axisymmetry_certificate"), "drop target axisymmetry certificate"),
        (lambda x: x["admission_predicate"].__setitem__("phase_domain", "N_SAMPLES"), "sample full orbit"),
        (lambda x: x["admission_predicate"]["required_false"].remove("eccentric_setup"), "admit eccentric setup"),
        (lambda x: x["admission_predicate"]["required_false"].remove("phase_synchronization"), "admit synchronized phase"),
        (lambda x: x["admission_predicate"].__setitem__("nonaxisymmetric_target_material_rejects_material_domain_reduction", False), "allow nonaxisymmetric target"),
        (lambda x: x["authority"].__setitem__("saved_operation_is_immutable", False), "rewrite saved operation"),
        (lambda x: x["authority"].__setitem__("durable_body_identity_is_not_backend_topology", False), "promote quotient topology to body identity"),
        (lambda x: x["programme_boundary"].__setitem__("MC-B", "ACCEPTED"), "premature MC-B promotion"),
        (lambda x: x["retained_open_obligations"][0].__setitem__("status", "CLOSED"), "close PB-007-01"),
        (lambda x: x["routing"].__setitem__("rejected_phase_sensitive_cases", "MC-021"), "erase MC-022 fallback"),
        (lambda x: x["bounded_executable_subtype"].__setitem__("tolerance", 1e-6), "binary float tolerance authority"),
    ]
    for mutator, label in attacks:
        expect_contract_reject(c, mutator, label)


def run_contract() -> None:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract_obj(c)
    check_repo_artifacts(c)
    exact_controls()
    print("MC-021 contract verification passed")


def run_self_test() -> None:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract_obj(c)
    exact_controls()
    adversarial_contract_controls(c)
    print("MC-021 adversarial self-test passed")


def main() -> int:
    ap = argparse.ArgumentParser()
    mx = ap.add_mutually_exclusive_group(required=True)
    mx.add_argument("--contract", action="store_true")
    mx.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        run_contract() if args.contract else run_self_test()
    except (ContractError, ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"MC-021 verification failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
