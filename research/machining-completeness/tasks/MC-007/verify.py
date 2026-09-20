#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-007"
CONTRACT = TASK / "transcendental-route-v1.json"
MC002 = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
OUTCOMES = MC / "outcomes-v1.json"

DEPENDENCY_BLOBS = {
    "MC-002": (MC / "tasks" / "MC-002" / "outcome.json", "930db704e9dd29955e7af99ba793c74e0cfda325"),
    "MC-003": (MC / "tasks" / "MC-003" / "outcome.json", "8f335f59f36c8761844806f9059af4a4f1671044"),
}
EXPECTED_TARGETS = {
    "helical_arc",
    "timed_phase_motion",
    "phase_synchronization",
    "spindle_rotation+turning_feed_correlation",
    "eccentric_setup+spindle_rotation_correlation",
}
EXPECTED_OPERATIONS = {
    "lathe_threading_synchronized",
    "lathe_eccentric_turning",
    "mill_thread_helix_fixed_axis",
}
EXPECTED_BLOCKERS = {"PB-007-01", "PB-007-02", "PB-007-03", "PB-007-04"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str) -> None:
    raise AssertionError(msg)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def walk_no_float(value, where="root") -> None:
    if isinstance(value, float):
        fail(f"binary float present in certifying research artifact at {where}")
    if isinstance(value, dict):
        for k, v in value.items():
            walk_no_float(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            walk_no_float(v, f"{where}[{i}]")


def validate(obj: dict, *, check_registry: bool = True) -> None:
    if obj.get("schema") != "radicadsac-mc007-transcendental-route/1.0" or obj.get("task") != "MC-007":
        fail("schema/task mismatch")
    if obj.get("status") != "reviewed-negative-result-with-fail-closed-conditional-route":
        fail("MC-007 status drift")
    if obj.get("source_baseline") != "66eb051dbd0f7ec030fbf005710582ee9d6ab36d":
        fail("unexpected source baseline")
    if obj.get("native_geometry_claimed") is not False or obj.get("native_or_paid_execution") is not False:
        fail("MC-007 promoted research/model evidence or authorized native execution")
    walk_no_float(obj)

    deps = {d.get("task"): d for d in obj.get("dependencies", [])}
    if set(deps) != set(DEPENDENCY_BLOBS):
        fail("dependency set drift")
    for task, (path, expected) in DEPENDENCY_BLOBS.items():
        if deps[task].get("git_blob_sha1") != expected or git_blob_sha1(path) != expected:
            fail(f"dependency binding drift for {task}")
        if load(path).get("result_kind") != "COMPLETED_RESEARCH":
            fail(f"dependency result-kind drift for {task}")

    if set(obj.get("targeted_constructors", [])) != EXPECTED_TARGETS:
        fail("targeted constructor set drift")

    guards = obj.get("exact_source_guards", {})
    for key in (
        "finite_exact_time_knots_required",
        "unwrapped_phase_retained",
        "path_phase_time_share_one_parameter",
        "independent_phase_coverage_forbidden",
        "binary_float_as_predicate_authority_forbidden",
        "global_untyped_epsilon_forbidden",
        "tolerance_as_predicate_sign_forbidden",
        "timeout_or_iteration_cap_is_not_a_mathematical_result",
        "finite_sampling_alone_cannot_certify_no_zero",
        "schanuel_conjecture_not_assumed_as_unconditional_authority",
    ):
        if guards.get(key) is not True:
            fail(f"analytic-source guard weakened: {key}")

    sources = {s.get("id"): s for s in obj.get("inspected_sources", [])}
    cow = sources.get("COW-2015-BOUND-CSP", {})
    source_results = {r.get("id") for r in cow.get("results", [])}
    if source_results != {"bounded-open", "conditional-schanuel", "section-2.1-zero-finding"}:
        fail("inspected analytic-zero source inventory drift")

    steps = obj.get("reference_route", [])
    if [s.get("step") for s in steps] != [f"TR-{i}" for i in range(1, 9)]:
        fail("transcendental reference route incomplete or reordered")
    route_text = json.dumps(steps)
    for token in (
        "shared exact parameter",
        "Never replace correlated motion",
        "derivative/transversality",
        "MC-006",
        "TRANSCENDENTAL_EVENT_BLOCKER",
        "Positive-volume",
        "26-operation denominator",
    ):
        if token not in route_text:
            fail(f"reference route lost required semantic: {token}")

    cls = obj.get("operation_classification", {})
    if set(cls.get("requires_mc007_general_case", [])) != EXPECTED_OPERATIONS:
        fail("MC-007 operation classification drift")
    admitted = {x["id"] for x in load(MC002).get("operation_map", []) if x.get("status") == "admitted"}
    if len(admitted) != 26 or not EXPECTED_OPERATIONS <= admitted:
        fail("MC-002 admitted denominator drift")
    if cls.get("denominator_count_preserved") != 26 or cls.get("domain_narrowed") is not False:
        fail("denominator/domain guard drift")

    decision = obj.get("decision_status", {})
    if decision.get("unconditional_full_route_established") is not False:
        fail("unconditional transcendental route was overclaimed")
    if decision.get("separated_or_transversal_analytic_events") != "CONDITIONAL_ROUTE":
        fail("conditional analytic route status drift")
    if decision.get("tangential_multiple_or_singular_transcendental_events") != "PROOF_BLOCKER":
        fail("tangent/multiple/singular blocker was hidden")

    blockers = {b.get("id"): b for b in obj.get("proof_blockers", [])}
    if set(blockers) != EXPECTED_BLOCKERS:
        fail("proof blocker set drift")
    required_desc = {"MC-008", "MC-022", "MC-024", "MC-038"}
    for bid in ("PB-007-01", "PB-007-02"):
        if blockers[bid].get("status") != "OPEN" or not required_desc <= set(blockers[bid].get("affected_descendants", [])):
            fail(f"required downstream analytic blocker weakened: {bid}")

    po = obj.get("proof_obligation_effect", {})
    for key in ("PO-02", "PO-03", "PO-04", "PO-05", "PO-07"):
        if not str(po.get(key, "")).startswith("OPEN"):
            fail(f"{key} was prematurely accepted")
    if po.get("MC-B") != "NOT_ESTABLISHED":
        fail("MC-B was prematurely accepted")

    protected = obj.get("protected_semantics", {})
    if not protected or any(v is not True for v in protected.values()):
        fail("protected semantics weakened")

    if check_registry:
        reg = load(OUTCOMES).get("tasks", {}).get("MC-007", {})
        if reg.get("state") != "NEGATIVE_RESULT":
            fail("outcome registry not reconciled to MC-007 negative research result")
        registry_blockers = {b.get("id") if isinstance(b, dict) else b for b in reg.get("blockers", [])}
        if not EXPECTED_BLOCKERS <= registry_blockers:
            fail("outcome registry lost MC-007 blockers")
        required_artifacts = {
            "research/machining-completeness/tasks/MC-007/transcendental-route-v1.json",
            "research/machining-completeness/tasks/MC-007/report.md",
            "research/machining-completeness/tasks/MC-007/outcome.json",
            "research/machining-completeness/tasks/MC-007/verify.py",
        }
        if not required_artifacts <= set(reg.get("accepted_artifacts", [])):
            fail("outcome registry artifact binding incomplete")


def exact_interp(t: Fraction, t0: Fraction, t1: Fraction, v0: Fraction, v1: Fraction) -> Fraction:
    if not t0 <= t <= t1 or not t0 < t1:
        fail("invalid exact interpolation interval")
    u = (t - t0) / (t1 - t0)
    return (Fraction(1) - u) * v0 + u * v1


def timed_phase_value(t: Fraction) -> tuple[Fraction, Fraction]:
    """Exact two-piece path/phase law retaining one shared t and unwrapped phase."""
    if Fraction(0) <= t <= Fraction(1, 3):
        return (
            exact_interp(t, Fraction(0), Fraction(1, 3), Fraction(0), Fraction(1, 3)),
            exact_interp(t, Fraction(0), Fraction(1, 3), Fraction(0), Fraction(2, 3)),
        )
    if Fraction(1, 3) <= t <= Fraction(1):
        return (
            exact_interp(t, Fraction(1, 3), Fraction(1), Fraction(1, 3), Fraction(1)),
            exact_interp(t, Fraction(1, 3), Fraction(1), Fraction(2, 3), Fraction(2)),
        )
    fail("time outside finite exact source interval")


def classify_event(
    value_interval: tuple[Fraction, Fraction],
    derivative_interval: tuple[Fraction, Fraction],
    *,
    endpoint_sign_change: bool = False,
    exact_symbolic_event: bool = False,
) -> str:
    vlo, vhi = value_interval
    dlo, dhi = derivative_interval
    if vlo > vhi or dlo > dhi:
        fail("invalid directed interval")
    if exact_symbolic_event:
        return "EXACT_SYMBOLIC_EVENT"
    if vhi < 0 or vlo > 0:
        return "SEPARATED"
    derivative_separated = dhi < 0 or dlo > 0
    if derivative_separated and endpoint_sign_change:
        return "SIMPLE_ROOT_CERTIFIED"
    return "TRANSCENDENTAL_EVENT_BLOCKER"


def exact_boundary_controls() -> None:
    F = Fraction
    if timed_phase_value(F(0)) != (F(0), F(0)):
        fail("timed phase start boundary drift")
    if timed_phase_value(F(1, 3)) != (F(1, 3), F(2, 3)):
        fail("timed phase knot drift")
    if timed_phase_value(F(1)) != (F(1), F(2)):
        fail("unwrapped phase endpoint drift")
    mid_path, mid_phase = timed_phase_value(F(1, 2))
    if (mid_path, mid_phase) != (F(1, 2), F(1)):
        fail("shared time/path/phase correlation drift")

    # Independent path × phase coverage would falsely admit this state; the shared law does not.
    false_product_state = (F(0), F(1, 2))
    sampled = {timed_phase_value(F(i, 24)) for i in range(25)}
    if false_product_state in sampled:
        fail("independent phase coverage leaked into correlated source law")

    if classify_event((F(1, 10), F(1, 5)), (F(-3), F(3))) != "SEPARATED":
        fail("separated analytic event control failed")
    if classify_event((F(-1, 100), F(1, 100)), (F(2), F(3)), endpoint_sign_change=True) != "SIMPLE_ROOT_CERTIFIED":
        fail("transversal/simple-root control failed")
    if classify_event((F(-1, 100), F(1, 100)), (F(-1, 100), F(1, 100))) != "TRANSCENDENTAL_EVENT_BLOCKER":
        fail("tangency/multiple-root case did not fail closed")
    if classify_event((F(0), F(0)), (F(0), F(0))) != "TRANSCENDENTAL_EVENT_BLOCKER":
        fail("singular exact-zero case did not fail closed")
    if classify_event((F(0), F(0)), (F(0), F(0)), exact_symbolic_event=True) != "EXACT_SYMBOLIC_EVENT":
        fail("exact symbolic dispatch control failed")


def expect_reject(mutator) -> None:
    obj = load(CONTRACT)
    mutator(obj)
    try:
        validate(obj, check_registry=False)
    except AssertionError:
        return
    fail("adversarial mutation was accepted")


def adversarial_controls() -> None:
    expect_reject(lambda o: o["decision_status"].__setitem__("unconditional_full_route_established", True))
    expect_reject(lambda o: o["exact_source_guards"].__setitem__("independent_phase_coverage_forbidden", False))
    expect_reject(lambda o: o.__setitem__("proof_blockers", [b for b in o["proof_blockers"] if b["id"] != "PB-007-01"]))
    expect_reject(lambda o: o["exact_source_guards"].__setitem__("global_untyped_epsilon_forbidden", False))
    expect_reject(lambda o: o["exact_source_guards"].__setitem__("schanuel_conjecture_not_assumed_as_unconditional_authority", False))
    expect_reject(lambda o: o["operation_classification"].__setitem__("denominator_count_preserved", 23))
    expect_reject(lambda o: o["proof_obligation_effect"].__setitem__("MC-B", "ACCEPTED"))
    expect_reject(lambda o: o.__setitem__("native_geometry_claimed", True))
    expect_reject(lambda o: o["protected_semantics"].__setitem__("durable_body_and_lineage_preserved", False))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    args = ap.parse_args()
    if not args.contract:
        ap.error("--contract is required")
    obj = load(CONTRACT)
    validate(obj)
    exact_boundary_controls()
    adversarial_controls()
    print("MC-007 contract, boundary and adversarial verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
