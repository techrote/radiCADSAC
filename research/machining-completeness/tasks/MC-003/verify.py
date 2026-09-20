#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-003"
CONTRACT = TASK / "numeric-encoding-contract-v1.json"
MC002 = ROOT / "research" / "machining-completeness" / "tasks" / "MC-002" / "domain-contract-v1.json"
LEGACY = [
    ROOT / "research" / "rcs-002" / "fixtures" / "lathe-finishing-pass-v1.json",
    ROOT / "research" / "rcs-002" / "fixtures" / "mill-cut-through-v1.json",
]
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
CANON_INT = re.compile(r"^(0|-?[1-9][0-9]*)$")

REQUIRED_TRAJECTORY = {
    "stationary", "line", "circular_arc", "helical_arc",
    "polyline", "spline", "piecewise_motion", "timed_phase_motion",
}
REQUIRED_LATHE = {"spindle_rotation", "turning_feed", "phase_synchronization", "eccentric_setup"}
REQUIRED_SETUP = {"rigid_setup_transform", "reclamp", "machine_transition"}
REQUIRED_DIMENSIONS = {
    "dimensionless", "length", "angle", "time", "linear_rate",
    "angular_rate", "squared_length", "volume",
}


def fail(msg: str) -> None:
    raise AssertionError(msg)


def validate_rational(token: dict) -> None:
    if set(token) != {"numerator", "denominator"}:
        fail("rational shape drift")
    n, d = token["numerator"], token["denominator"]
    if not isinstance(n, str) or not CANON_INT.fullmatch(n):
        fail("noncanonical rational numerator")
    if not isinstance(d, str) or not re.fullmatch(r"[1-9][0-9]*", d):
        fail("noncanonical rational denominator")
    ni, di = int(n), int(d)
    if di <= 0 or math.gcd(abs(ni), di) != 1:
        fail("rational not reduced/positive denominator")
    if ni == 0 and d != "1":
        fail("zero rational must be 0/1")


def walk_legacy_ints(value, path="root"):
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if not INT64_MIN <= value <= INT64_MAX:
            fail(f"legacy integer outside int64: {path}")
        return
    if isinstance(value, float):
        fail(f"legacy fixture unexpectedly contains JSON floating number: {path}")
    if isinstance(value, dict):
        for k, v in value.items():
            walk_legacy_ints(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            walk_legacy_ints(v, f"{path}[{i}]")


def validate_legacy_fixture(path: Path) -> None:
    obj = json.loads(path.read_text(encoding="utf-8"))
    journal = obj.get("journal", {})
    if journal.get("journal_schema") != {"id": "msac-journal", "major": 1, "minor": 0}:
        fail(f"legacy schema drift: {path.name}")
    if journal.get("numeric_convention") != "nm-nrad-ns-q15-v1":
        fail(f"legacy numeric convention drift: {path.name}")
    if journal.get("required_extensions") != []:
        fail(f"legacy fixture was retrofitted with an extension: {path.name}")
    walk_legacy_ints(obj)
    for frame in journal.get("definitions", {}).get("frames", []):
        t = frame.get("transform_parent_from_child")
        if t is None:
            continue
        q = t.get("rotation_q15_wxyz")
        if not isinstance(q, list) or len(q) != 4 or not all(isinstance(x, int) and not isinstance(x, bool) for x in q):
            fail(f"legacy quaternion token invalid: {path.name}")
        if not any(q):
            fail(f"legacy zero quaternion: {path.name}")


def validate(obj: dict) -> None:
    if obj.get("schema") != "radicadsac-mc-numeric-encoding-contract/1.0" or obj.get("task") != "MC-003":
        fail("schema/task mismatch")
    if obj.get("status") != "reviewed-numeric-artifact":
        fail("numeric artifact not reviewable")
    if obj.get("native_geometry_claimed") is not False:
        fail("contract evidence promoted to native geometry")
    if obj.get("evidence_class") != ["REQUIREMENT", "DESIGN_DECISION", "DOCUMENTATION_RECONCILIATION"]:
        fail("evidence class drift")

    deps = obj.get("dependency_inputs", [])
    if len(deps) != 1 or deps[0].get("task") != "MC-002":
        fail("MC-002 dependency missing")
    if deps[0].get("blob_sha") != "930db704e9dd29955e7af99ba793c74e0cfda325":
        fail("MC-002 dependency blob drift")

    legacy = obj.get("legacy_msac_journal_1_0", {})
    if legacy.get("preserve_saved_meaning") is not True:
        fail("legacy meaning preservation weakened")
    if legacy.get("schema_id") != "msac-journal/1.0" or legacy.get("numeric_convention") != "nm-nrad-ns-q15-v1":
        fail("legacy identity drift")
    if legacy.get("signed_integer_bits") != 64 or legacy.get("overflow_policy") != "reject-never-wrap":
        fail("legacy integer/overflow semantics weakened")
    if legacy.get("source_rounding_when_canonicalizing") != "round-to-nearest-ties-to-even":
        fail("legacy rounding semantics changed")
    if legacy.get("quantization_is_part_of_normalization_error") is not True:
        fail("legacy quantization omitted from error")
    tokens = legacy.get("tokens", {})
    for name in ("length_nm", "angle_nrad", "time_ns", "rate_nm_s", "angular_rate_nrad_s", "q15"):
        if tokens.get(name, {}).get("exact") is not True:
            fail(f"legacy exact token semantics missing: {name}")
    q = legacy.get("quaternion", {})
    if q.get("zero_rejected") is not True or q.get("floating_backend_does_not_change_durable_meaning") is not True:
        fail("quaternion exactness weakened")
    tr = legacy.get("transform", {})
    if "right-handed" not in tr.get("frames", "") or "column vector" not in tr.get("point_convention", ""):
        fail("transform convention drift")
    comp = legacy.get("compatibility", {})
    for key in (
        "existing_v1_document_never_reinterpreted_under_mc_extension",
        "lost_subquantum_information_is_not_recoverable",
        "unknown_required_extension_must_be_rejected_not_downcast",
        "migration_requires_new_revision_and_source_identity",
    ):
        if comp.get(key) is not True:
            fail(f"compatibility rule weakened: {key}")

    profile = obj.get("mc1_exact_source_profile", {})
    if profile.get("id") != "mc-exact-source/1.0" or profile.get("finite_source_only") is not True:
        fail("exact source profile identity/rule drift")
    if profile.get("json_number_for_certifying_quantity_forbidden") is not True:
        fail("ordinary JSON float permitted for certifying quantity")
    if set(profile.get("dimensions", [])) != REQUIRED_DIMENSIONS:
        fail("dimensional type set drift")
    rules = profile.get("rules", {})
    for key in (
        "units_are_explicit", "dimension_mismatch_is_error", "nonfinite_tokens_forbidden",
        "global_untyped_epsilon_forbidden", "tolerance_as_predicate_sign_forbidden",
        "flush_to_zero_in_authority_path_forbidden", "integer_overflow_or_silent_saturation_forbidden",
        "nominal_geometry_and_source_measurement_uncertainty_are_separate",
    ):
        if rules.get(key) is not True:
            fail(f"numeric safety rule weakened: {key}")

    sc = profile.get("scalar_encodings", {})
    if set(sc) != {"rational", "turn_fraction", "directed_interval"}:
        fail("scalar encoding set drift")
    validate_rational({"numerator": "0", "denominator": "1"})
    validate_rational({"numerator": "-3", "denominator": "7"})

    constructors = obj.get("constructor_semantics", {})
    if not REQUIRED_TRAJECTORY.issubset(constructors):
        fail("trajectory constructor semantics incomplete")
    if "exact sweep as turn_fraction" not in constructors["circular_arc"].get("encoding", []):
        fail("circular arc lost exact symbolic sweep")
    if "exact axial_delta along the same axis" not in constructors["helical_arc"].get("encoding", []):
        fail("helix lost axial progression")
    if "no knot epsilon" not in constructors["spline"].get("meaning", ""):
        fail("spline knot semantics became epsilon-defined")
    if "phase" not in " ".join(constructors["timed_phase_motion"].get("encoding", [])).lower():
        fail("timed phase motion lost phase binding")

    phase = obj.get("phase_and_time", {})
    if "exact turn_fraction" not in phase.get("mc1_phase", ""):
        fail("phase was decimalized/approximated")
    if "same exact time/phase law" not in phase.get("threading_and_eccentric_turning", ""):
        fail("phase-sensitive operations lost correlation")

    boundary = obj.get("curve_and_transform_boundary_rules", {})
    for key in (
        "endpoints_are_authoritative", "engagement_boundaries_are_not_fitted_across",
        "setup_tool_target_policy_boundaries_are_not_fitted_across", "exact_retrace_not_deleted_from_journal",
        "subquantum_derived_features_are_not_clamped_to_input_quantum",
        "exact_predicates_do_not_imply_exact_constructions",
        "certified_filter_fallback_must_preserve_exact_source_semantics",
        "transform_composition_checks_units_order_and_handedness",
    ):
        if boundary.get(key) is not True:
            fail(f"boundary rule weakened: {key}")

    ser = obj.get("serialization", {})
    if "never binary floating JSON numbers" not in ser.get("certifying_values", ""):
        fail("serialization guarantee weakened")
    mig = obj.get("migration_and_extension", {})
    for key in ("base_v1_is_frozen", "new_revision_only", "no_in_place_reinterpretation", "no_fake_precision_recovery"):
        if mig.get(key) is not True:
            fail(f"migration safety rule weakened: {key}")
    fixtures = mig.get("legacy_fixture_expectations", [])
    expected = {
        "research/rcs-002/fixtures/lathe-finishing-pass-v1.json": "f87b160d4d78d8a608969d183b6b165a9e57a0d4",
        "research/rcs-002/fixtures/mill-cut-through-v1.json": "cb93d31e3e0c018c0e971ec1a8144be085f6e5fd",
    }
    if {x.get("path"): x.get("blob_sha") for x in fixtures} != expected:
        fail("legacy fixture identity drift")
    if any(x.get("required_extensions") != [] for x in fixtures):
        fail("legacy extension retrofit detected")

    coverage = obj.get("mc002_constructor_coverage", {})
    if set(coverage.get("required_trajectory_ids", [])) != REQUIRED_TRAJECTORY:
        fail("MC-002 trajectory coverage mismatch")
    if set(coverage.get("required_lathe_kinematic_ids", [])) != REQUIRED_LATHE:
        fail("MC-002 lathe kinematic coverage mismatch")
    if set(coverage.get("required_setup_ids", [])) != REQUIRED_SETUP:
        fail("MC-002 setup coverage mismatch")

    oq = {x.get("id"): x for x in obj.get("open_questions", [])}
    if set(oq) != {"OQ-003-01", "OQ-003-02", "OQ-003-03", "OQ-003-04"}:
        fail("open-question register drift")
    if oq["OQ-003-03"].get("status") != "propagated_from_MC-002" or oq["OQ-003-04"].get("status") != "propagated_from_MC-002":
        fail("MC-002 open domain decisions were silently resolved")


def must_reject(base: dict, mutate, label: str) -> None:
    bad = copy.deepcopy(base)
    mutate(bad)
    try:
        validate(bad)
    except AssertionError:
        return
    fail(f"adversarial control was not rejected: {label}")


def adversarial_self_test(base: dict) -> None:
    must_reject(base, lambda x: x["legacy_msac_journal_1_0"].__setitem__("preserve_saved_meaning", False), "reinterpret legacy journal")
    must_reject(base, lambda x: x["legacy_msac_journal_1_0"].__setitem__("overflow_policy", "wrap"), "integer wrap")
    must_reject(base, lambda x: x["legacy_msac_journal_1_0"]["compatibility"].__setitem__("lost_subquantum_information_is_not_recoverable", False), "fake precision recovery")
    must_reject(base, lambda x: x["mc1_exact_source_profile"].__setitem__("json_number_for_certifying_quantity_forbidden", False), "float certificate quantity")
    must_reject(base, lambda x: x["mc1_exact_source_profile"]["rules"].__setitem__("global_untyped_epsilon_forbidden", False), "global epsilon")
    must_reject(base, lambda x: x["constructor_semantics"].pop("helical_arc"), "dropped helix")
    must_reject(base, lambda x: x["constructor_semantics"]["spline"].__setitem__("meaning", "approximate knots with epsilon"), "knot epsilon")
    must_reject(base, lambda x: x["phase_and_time"].__setitem__("mc1_phase", "decimal radians"), "phase decimalization")
    must_reject(base, lambda x: x["curve_and_transform_boundary_rules"].__setitem__("subquantum_derived_features_are_not_clamped_to_input_quantum", False), "feature floor")
    must_reject(base, lambda x: x["migration_and_extension"].__setitem__("new_revision_only", False), "in-place migration")
    must_reject(base, lambda x: x["open_questions"].pop(), "silently resolved inherited domain question")
    must_reject(base, lambda x: x.__setitem__("native_geometry_claimed", True), "contract promoted to native geometry")


def verify_mc002_alignment(obj: dict) -> None:
    mc2 = json.loads(MC002.read_text(encoding="utf-8"))
    ids = {e["id"] for e in mc2["constructors"]["trajectory"]}
    if ids != set(obj["mc002_constructor_coverage"]["required_trajectory_ids"]):
        fail(f"MC-002 trajectory IDs changed: {sorted(ids)}")
    lathe = {e["id"] for e in mc2["constructors"]["lathe_kinematics"]}
    if lathe != set(obj["mc002_constructor_coverage"]["required_lathe_kinematic_ids"]):
        fail("MC-002 lathe kinematic IDs changed")
    setup = {e["id"] for e in mc2["constructors"]["setup"]}
    if setup != set(obj["mc002_constructor_coverage"]["required_setup_ids"]):
        fail("MC-002 setup IDs changed")
    decisions = {e["id"]: e["status"] for e in mc2["named_domain_decisions"]}
    if decisions.get("DD-002-04") != "open_product_domain_decision" or decisions.get("DD-002-05") != "open_product_domain_decision":
        fail("MC-002 inherited open domain decisions changed")


def verify_repository_bindings() -> None:
    outcome = json.loads((TASK / "outcome.json").read_text(encoding="utf-8"))
    if outcome.get("task") != "MC-003" or outcome.get("result_kind") != "COMPLETED_RESEARCH":
        fail("MC-003 outcome state mismatch")
    shared = (ROOT / "docs" / "machining-completeness" / "01-DOMAIN-AND-SEMANTICS.md").read_text(encoding="utf-8")
    for marker in (
        "MC-003 reviewed numeric/encoding artifact",
        "mc-exact-source/1.0",
        "Existing `msac-journal/1.0` documents are not migrated in place",
        "MC-A remains `NOT_ESTABLISHED`",
    ):
        if marker not in shared:
            fail(f"shared domain/numeric spec lacks reconciliation marker: {marker}")
    for path in LEGACY:
        validate_legacy_fixture(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.parse_args()
    obj = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate(obj)
    adversarial_self_test(obj)
    verify_mc002_alignment(obj)
    verify_repository_bindings()
    print("MC-003 numeric/curve/transform/encoding contract and adversarial controls passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
