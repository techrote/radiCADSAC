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
TASK = MC / "tasks" / "MC-006"
CONTRACT = TASK / "algebraic-reference-route-v1.json"
MC002 = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
MC003 = MC / "tasks" / "MC-003" / "numeric-encoding-contract-v1.json"
OUTCOMES = MC / "outcomes-v1.json"

DEPENDENCY_BLOBS = {
    "MC-002": (MC / "tasks" / "MC-002" / "outcome.json", "930db704e9dd29955e7af99ba793c74e0cfda325"),
    "MC-003": (MC / "tasks" / "MC-003" / "outcome.json", "8f335f59f36c8761844806f9059af4a4f1671044"),
}
EXPECTED_DIRECT = {
    "mill_face", "mill_slot_pocket_freehand", "mill_drill_plunge", "mill_ball_rounded_xyz",
    "mill_form_chamfer_countersink", "mill_accessible_undercut", "mill_simultaneous_xyz",
    "mill_retrace_self_cross_stationary", "mill_cutthrough_multibody", "reclamp_reorient_continue",
    "lathe_mill_lathe_history", "machine_separated_retained_body", "complete_body_removal",
}
EXPECTED_CONDITIONAL = {
    "lathe_od_turning", "lathe_facing", "lathe_shoulder", "lathe_taper_chamfer_profile",
    "lathe_id_boring_internal", "lathe_axial_drilling", "lathe_grooving", "lathe_parting_cutthrough",
    "lathe_form_turning", "lathe_exact_retrace_finish",
}
EXPECTED_MC007 = {"lathe_threading_synchronized", "lathe_eccentric_turning", "mill_thread_helix_fixed_axis"}


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
    if obj.get("schema") != "radicadsac-mc006-algebraic-reference-route/1.0" or obj.get("task") != "MC-006":
        fail("schema/task mismatch")
    if obj.get("status") != "reviewed-conditional-reference-route":
        fail("MC-006 status drift")
    if obj.get("source_baseline") != "5b5db0e5b112e37111b42b4933af8469606337a0":
        fail("unexpected source baseline")
    if obj.get("native_geometry_claimed") is not False or obj.get("native_or_paid_execution") is not False:
        fail("MC-006 promoted planning/model evidence or authorized native execution")
    walk_no_float(obj)

    deps = {d.get("task"): d for d in obj.get("dependencies", [])}
    if set(deps) != set(DEPENDENCY_BLOBS):
        fail("dependency set drift")
    for task, (path, expected) in DEPENDENCY_BLOBS.items():
        if deps[task].get("git_blob_sha1") != expected or git_blob_sha1(path) != expected:
            fail(f"dependency binding drift for {task}")
        if load(path).get("result_kind") != "COMPLETED_RESEARCH":
            fail(f"dependency result kind drift for {task}")

    language = obj.get("effective_language", {})
    for key in ("bounded_material", "exact_signs_required", "floating_predicate_authority_forbidden", "global_epsilon_forbidden", "timeout_or_iteration_cap_is_not_a_mathematical_result"):
        if language.get(key) is not True:
            fail(f"exact-language guard weakened: {key}")

    source = {s.get("id"): s for s in obj.get("inspected_sources", [])}
    basu = source.get("T02-BASU-2014", {})
    result_ids = {r.get("id") for r in basu.get("results", [])}
    required_results = {"Theorem 2.1", "Definitions 2.2-2.3 + Theorem 2.4", "Definitions 2.11-2.12", "Definition 3.4, Proposition 3.5 and Theorem 3.6"}
    if not required_results <= result_ids:
        fail("inspected theorem/algorithm hypotheses are incomplete")
    if "STURM-EOM" not in source:
        fail("exact univariate root-count source missing")

    steps = obj.get("reference_route", [])
    if [s.get("step") for s in steps] != [f"AR-{i}" for i in range(1, 9)]:
        fail("reference route is incomplete or reordered")
    route_text = json.dumps(steps)
    for token in ("quantifier", "regularized removal", "Theorem 2.4", "positive-volume", "durable body"):
        if token not in route_text:
            fail(f"reference route lost required semantic: {token}")

    cls = obj.get("operation_classification", {})
    direct = set(cls.get("mc006_direct_semialgebraic_slice", []))
    conditional = set(cls.get("conditional_on_semialgebraic_reduction_or_tool_stock_representation", []))
    mc007 = set(cls.get("mc007_required_general_case", []))
    if direct != EXPECTED_DIRECT or conditional != EXPECTED_CONDITIONAL or mc007 != EXPECTED_MC007:
        fail("operation classification drift")
    if (direct & conditional) or (direct & mc007) or (conditional & mc007):
        fail("operation classifications overlap")
    admitted = {x["id"] for x in load(MC002).get("operation_map", []) if x.get("status") == "admitted"}
    if direct | conditional | mc007 != admitted or len(admitted) != 26:
        fail("MC-002 denominator was narrowed or expanded")
    if cls.get("denominator_count_preserved") != 26 or cls.get("domain_narrowed") is not False:
        fail("denominator/domain guard drift")

    uncovered = {x.get("constructor"): x for x in obj.get("constructor_coverage", {}).get("not_covered_general_case", [])}
    for name in ("helical_arc", "timed_phase_motion", "phase_synchronization"):
        if uncovered.get(name, {}).get("owner") != "MC-007":
            fail(f"{name} was not explicitly propagated to MC-007")

    lemmas = {x.get("id"): x for x in obj.get("local_lemma_dag", [])}
    if set(lemmas) != {f"L006-{i:02d}" for i in range(1, 8)}:
        fail("local lemma DAG incomplete")
    if lemmas["L006-07"].get("status") != "OPEN_FOR_INTEGRATION":
        fail("universal topology was prematurely claimed")
    # Acyclicity over local lemma edges.
    visiting, done = set(), set()
    def visit(node: str) -> None:
        if node in done:
            return
        if node in visiting:
            fail("cycle in local lemma DAG")
        visiting.add(node)
        for dep in lemmas[node].get("depends_on", []):
            if dep in lemmas:
                visit(dep)
        visiting.remove(node)
        done.add(node)
    for node in lemmas:
        visit(node)

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
        reg = load(OUTCOMES).get("tasks", {}).get("MC-006", {})
        if reg.get("state") != "COMPLETED_RESEARCH":
            fail("outcome registry not reconciled to completed research")
        if reg.get("blockers") != []:
            fail("completed MC-006 registry entry retains blockers")
        required_artifacts = {
            "research/machining-completeness/tasks/MC-006/algebraic-reference-route-v1.json",
            "research/machining-completeness/tasks/MC-006/report.md",
            "research/machining-completeness/tasks/MC-006/outcome.json",
            "research/machining-completeness/tasks/MC-006/verify.py",
        }
        if not required_artifacts <= set(reg.get("accepted_artifacts", [])):
            fail("outcome registry artifact binding incomplete")


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def deriv(p):
    return trim([Fraction(i) * p[i] for i in range(1, len(p))] or [Fraction(0)])


def poly_divmod(n, d):
    n, d = trim(n), trim(d)
    if d == [0]:
        raise ZeroDivisionError
    if len(n) < len(d):
        return [Fraction(0)], n
    q = [Fraction(0)] * (len(n) - len(d) + 1)
    r = n[:]
    while r != [0] and len(r) >= len(d):
        k = len(r) - len(d)
        c = r[-1] / d[-1]
        q[k] += c
        for i, dv in enumerate(d):
            r[i + k] -= c * dv
        r = trim(r)
    return trim(q), trim(r)


def monic(p):
    p = trim(p)
    if p == [0]:
        return p
    lead = p[-1]
    return [x / lead for x in p]


def poly_gcd(a, b):
    a, b = trim(a), trim(b)
    while b != [0]:
        _, r = poly_divmod(a, b)
        a, b = b, r
    return monic(a)


def square_free_part(p):
    p = trim(p)
    g = poly_gcd(p, deriv(p))
    q, r = poly_divmod(p, g)
    if r != [0]:
        fail("square-free division was not exact")
    return monic(q)


def poly_eval(p, x):
    out = Fraction(0)
    for c in reversed(p):
        out = out * x + c
    return out


def sturm_sequence(p):
    p = square_free_part(p)
    seq = [p, deriv(p)]
    while seq[-1] != [0]:
        _, r = poly_divmod(seq[-2], seq[-1])
        if r == [0]:
            break
        seq.append([-x for x in r])
    return seq


def variations(values):
    signs = [(v > 0) - (v < 0) for v in values if v != 0]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def root_count(p, a, b):
    if not a < b:
        fail("invalid root interval")
    seq = sturm_sequence(p)
    if poly_eval(seq[0], a) == 0 or poly_eval(seq[0], b) == 0:
        fail("Sturm control requires non-root endpoints")
    return variations([poly_eval(q, a) for q in seq]) - variations([poly_eval(q, b) for q in seq])


def box_volume(box):
    x0, x1, y0, y1, z0, z1 = box
    if not (x0 <= x1 and y0 <= y1 and z0 <= z1):
        fail("invalid box")
    return (x1 - x0) * (y1 - y0) * (z1 - z0)


def intersection_volume(a, b):
    dx = max(Fraction(0), min(a[1], b[1]) - max(a[0], b[0]))
    dy = max(Fraction(0), min(a[3], b[3]) - max(a[2], b[2]))
    dz = max(Fraction(0), min(a[5], b[5]) - max(a[4], b[4]))
    return dx * dy * dz


def full_cross_section_cut(stock, cutter):
    """Exact regularized difference for task-local controls where cutter spans stock Y/Z."""
    if intersection_volume(stock, cutter) == 0:
        return [stock]
    if not (cutter[2] <= stock[2] and cutter[3] >= stock[3] and cutter[4] <= stock[4] and cutter[5] >= stock[5]):
        fail("control cutter does not span stock cross-section")
    ix0, ix1 = max(stock[0], cutter[0]), min(stock[1], cutter[1])
    out = []
    if stock[0] < ix0:
        out.append((stock[0], ix0, stock[2], stock[3], stock[4], stock[5]))
    if ix1 < stock[1]:
        out.append((ix1, stock[1], stock[2], stock[3], stock[4], stock[5]))
    return [b for b in out if box_volume(b) > 0]


def exact_boundary_controls() -> None:
    x2m2 = [Fraction(-2), Fraction(0), Fraction(1)]
    if root_count(x2m2, Fraction(1), Fraction(2)) != 1 or root_count(x2m2, Fraction(-2), Fraction(-1)) != 1:
        fail("irrational-root isolation control failed")
    repeated = [Fraction(1), Fraction(-2), Fraction(1)]
    if root_count(repeated, Fraction(0), Fraction(2)) != 1:
        fail("repeated-root square-free control failed")

    F = Fraction
    stock = (F(0), F(3), F(0), F(1), F(0), F(1))
    tangent = (F(3), F(4), F(-1), F(2), F(-1), F(2))
    if full_cross_section_cut(stock, tangent) != [stock]:
        fail("tangency changed volumetric material")

    splitter = (F(1), F(2), F(-1), F(2), F(-1), F(2))
    pieces = full_cross_section_cut(stock, splitter)
    if len(pieces) != 2 or [box_volume(p) for p in pieces] != [F(1), F(1)]:
        fail("exact cut-through/body-split control failed")

    whole = (F(-1), F(4), F(-1), F(2), F(-1), F(2))
    if full_cross_section_cut(stock, whole) != []:
        fail("complete-removal control failed")

    sliver_cut = (F(0), F(2999999, 1000000), F(-1), F(2), F(-1), F(2))
    sliver = full_cross_section_cut(stock, sliver_cut)
    if len(sliver) != 1 or box_volume(sliver[0]) != F(1, 1000000):
        fail("positive-volume sliver was lost")

    disjoint = (F(4), F(5), F(-1), F(2), F(-1), F(2))
    if full_cross_section_cut(stock, disjoint) != [stock]:
        fail("disjoint exact no-op control failed")


def must_reject(base: dict, mutate, label: str) -> None:
    bad = copy.deepcopy(base)
    mutate(bad)
    try:
        validate(bad, check_registry=False)
    except AssertionError:
        return
    fail(f"adversarial control was not rejected: {label}")


def adversarial_self_test(base: dict) -> None:
    must_reject(base, lambda x: x.__setitem__("native_geometry_claimed", True), "model promoted to native geometry")
    must_reject(base, lambda x: x["effective_language"].__setitem__("global_epsilon_forbidden", False), "global epsilon admitted")
    must_reject(base, lambda x: x["operation_classification"]["mc006_direct_semialgebraic_slice"].append("mill_thread_helix_fixed_axis"), "helix smuggled into algebraic slice")
    must_reject(base, lambda x: x["operation_classification"].__setitem__("denominator_count_preserved", 25), "denominator shrinkage")
    must_reject(base, lambda x: x["constructor_coverage"]["not_covered_general_case"][0].__setitem__("owner", "MC-006"), "uncovered helix hidden")
    must_reject(base, lambda x: x["local_lemma_dag"][-1].__setitem__("status", "REVIEWED_REFERENCE_ROUTE"), "universal topology overclaim")
    must_reject(base, lambda x: x["proof_obligation_effect"].__setitem__("MC-B", "ACCEPTED"), "MC-B overclaim")
    must_reject(base, lambda x: x["protected_semantics"].__setitem__("journal_saved_meaning_preserved", False), "journal semantics weakened")
    must_reject(base, lambda x: x["inspected_sources"][0].__setitem__("results", []), "theorem hypotheses removed")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    args = ap.parse_args()
    if not args.contract:
        ap.error("--contract is required")
    obj = load(CONTRACT)
    validate(obj)
    exact_boundary_controls()
    adversarial_self_test(obj)
    print("MC-006 exact algebraic reference route, boundary controls and adversarial controls passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
