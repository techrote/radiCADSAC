#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-008"
CONTRACT = TASK / "termination-proof-dag-v1.json"
PROOF = MC / "proof-obligations-v1.json"
OUTCOMES = MC / "outcomes-v1.json"

DEPENDENCY_BLOBS = {
    "MC-003": (MC / "tasks" / "MC-003" / "outcome.json", "8f335f59f36c8761844806f9059af4a4f1671044", "COMPLETED_RESEARCH"),
    "MC-006": (MC / "tasks" / "MC-006" / "outcome.json", "0319e00b492c57e4a11e3e78ef9a2e15ff67e52e", "COMPLETED_RESEARCH"),
    "MC-007": (MC / "tasks" / "MC-007" / "outcome.json", "8d54872292dfd9f632c79c76994a467d26eaaf9c", "NEGATIVE_RESULT"),
}
EXPECTED_PO_OWNERS = {
    "PO-01": "MC-005", "PO-02": "MC-031", "PO-03": "MC-039", "PO-04": "MC-032",
    "PO-05": "MC-038", "PO-06": "MC-037", "PO-07": "MC-032", "PO-08": "MC-030",
    "PO-09": "MC-037", "PO-10": "MC-044", "PO-11": "MC-050", "PO-12": "MC-048",
}
EXPECTED_BLOCKERS = {"PB-007-01", "PB-007-02", "PB-007-03", "PB-007-04"}
EXPECTED_INTERNAL = {f"L008-{i:02d}" for i in range(1, 9)}
EXPECTED_EVENT_CASES = {
    "exact-source-or-algebraically-reducible",
    "analytic-proved-separated",
    "analytic-proved-transversal-with-finite-isolation-bound",
    "analytic-tangential-multiple-singular-or-no-stopping-proof",
    "missing-exact-source-or-universal-topology-route",
}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def fail(msg: str) -> None:
    raise AssertionError(msg)

def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def walk_no_float(value, where="root") -> None:
    if isinstance(value, float):
        fail(f"binary float present in certifying artifact at {where}")
    if isinstance(value, dict):
        for k, v in value.items():
            walk_no_float(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            walk_no_float(v, f"{where}[{i}]")

def assert_acyclic(nodes: list[dict], label: str) -> None:
    ids = [n.get("id") for n in nodes]
    if None in ids or len(ids) != len(set(ids)):
        fail(f"{label} IDs missing or duplicated")
    known = set(ids)
    indeg = {i: 0 for i in ids}
    rev = {i: [] for i in ids}
    for n in nodes:
        for d in n.get("depends_on", []):
            if d not in known:
                fail(f"{label} dependency {d} is not a node")
            indeg[n["id"]] += 1
            rev[d].append(n["id"])
    q = sorted(i for i, n in indeg.items() if n == 0)
    seen = []
    while q:
        x = q.pop(0)
        seen.append(x)
        for y in sorted(rev[x]):
            indeg[y] -= 1
            if indeg[y] == 0:
                q.append(y)
                q.sort()
    if len(seen) != len(ids):
        fail(f"{label} contains a dependency cycle")

def validate(obj: dict, *, check_shared: bool = True) -> None:
    if obj.get("schema") != "radicadsac-mc008-termination-proof-dag/1.0" or obj.get("task") != "MC-008":
        fail("schema/task mismatch")
    if obj.get("status") != "reviewed-integration-contract-with-open-proof-blockers":
        fail("MC-008 status drift")
    if obj.get("source_baseline") != "cd42f951191489284d3ab2aaba2cdc05c035cda9":
        fail("unexpected source baseline")
    if obj.get("native_geometry_claimed") is not False or obj.get("native_or_paid_execution") is not False:
        fail("MC-008 promoted research evidence or authorized native execution")
    walk_no_float(obj)

    deps = {d.get("task"): d for d in obj.get("dependencies", [])}
    if set(deps) != set(DEPENDENCY_BLOBS):
        fail("dependency set drift")
    for task, (path, expected_blob, expected_kind) in DEPENDENCY_BLOBS.items():
        if deps[task].get("git_blob_sha1") != expected_blob:
            fail(f"declared dependency blob drift for {task}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"live dependency blob drift for {task}")
        if load(path).get("result_kind") != expected_kind or deps[task].get("result_kind") != expected_kind:
            fail(f"dependency result-kind drift for {task}")

    scope = obj.get("scope_guard", {})
    if scope.get("operation_denominator_preserved") != 26 or scope.get("domain_narrowed") is not False:
        fail("operation denominator/domain guard drift")
    if scope.get("universal_constructive_capability_claimed") is not False:
        fail("MC-008 overclaimed universal constructive capability")
    if scope.get("MC-B") != "NOT_ESTABLISHED" or scope.get("MC-1") != "NOT_ESTABLISHED":
        fail("later capability gate was prematurely accepted")

    tiers = obj.get("arithmetic_escalation", [])
    if [x.get("tier") for x in tiers] != ["A0", "A1", "A2", "A3"]:
        fail("arithmetic escalation tiers incomplete or reordered")
    if tiers[-1].get("name") != "fail-closed-proof-blocker":
        fail("arithmetic escalation no longer terminates fail-closed")

    guards = obj.get("arithmetic_guards", {})
    required_guards = {
        "binary_float_as_predicate_authority_forbidden",
        "global_untyped_epsilon_forbidden",
        "tolerance_as_predicate_sign_forbidden",
        "silent_overflow_or_saturation_forbidden",
        "timeout_or_iteration_cap_is_not_semantic_success",
        "finite_sampling_alone_cannot_certify_no_event",
        "provider_retry_cycles_forbidden",
        "unknown_error_component_forbids_final_numeric_certificate",
        "numeric_tolerance_cannot_delete_positive_volume_or_change_topology",
        "open_proof_blocker_cannot_be_relabelled_out_of_domain",
        "open_proof_blocker_never_satisfies_required_po",
    }
    if set(guards) != required_guards or any(guards[k] is not True for k in required_guards):
        fail("arithmetic fail-closed guards weakened")

    cases = obj.get("event_decision_cases", [])
    if {x.get("case") for x in cases} != EXPECTED_EVENT_CASES:
        fail("event decision case inventory drift")
    blocked = {x.get("case"): x for x in cases}
    if blocked["analytic-tangential-multiple-singular-or-no-stopping-proof"].get("terminal") != "TRANSCENDENTAL_EVENT_BLOCKER":
        fail("tangential/multiple/singular analytic case no longer fails closed")
    if blocked["missing-exact-source-or-universal-topology-route"].get("terminal") != "PROOF_BLOCKER":
        fail("missing source/topology route no longer fails closed")

    progress = {x.get("id"): x for x in obj.get("finite_progress", [])}
    if set(progress) != {f"FP-008-{i:02d}" for i in range(1, 5)}:
        fail("finite progress witness inventory drift")
    for p in progress.values():
        for key in ("domain", "measure", "strict_progress", "terminal", "owner_po"):
            if not p.get(key):
                fail(f"finite progress witness missing {key}")
    forbidden = set(obj.get("forbidden_progress_substitutes", []))
    required_forbidden = {
        "jitter-until-success", "provider-cycle-until-one-accepts",
        "refine-until-timeout-then-pass",
        "fixed-depth-subdivision-used-as-proof-without-derived-bound",
        "drop-operation-or-body-after-refusal",
    }
    if forbidden != required_forbidden:
        fail("forbidden finite-progress substitutes drift")

    err = obj.get("error_composition", {})
    if err.get("stage_order") != ["source_decode", "transform", "sweep_material", "classification_topology", "reconstruction", "step_export"]:
        fail("error composition stage order drift")
    for key in ("topology_is_noncompensating", "positive_volume_is_noncompensating", "body_identity_and_lineage_are_noncompensating"):
        if err.get(key) is not True:
            fail(f"non-compensating correctness guard weakened: {key}")
    if err.get("unknown_component_terminal") != "UNCERTIFIED":
        fail("unknown error component was converted to a numeric certificate")

    lemmas = obj.get("internal_lemma_dag", [])
    if {x.get("id") for x in lemmas} != EXPECTED_INTERNAL:
        fail("internal lemma inventory drift")
    if any(x.get("owner") != "MC-008" or x.get("status") != "REVIEWED_CONTRACT" for x in lemmas):
        fail("internal lemma ownership/status drift")
    assert_acyclic(lemmas, "internal lemma DAG")

    pos = obj.get("proof_obligation_dag", [])
    if [x.get("id") for x in pos] != [f"PO-{i:02d}" for i in range(1, 13)]:
        fail("PO-01..12 inventory/order drift")
    assert_acyclic(pos, "proof-obligation DAG")
    for p in pos:
        pid = p["id"]
        if p.get("integration_owner") != EXPECTED_PO_OWNERS[pid]:
            fail(f"{pid} integration owner drift")
        expected_state = "ACCEPTED" if pid == "PO-01" else "OPEN"
        if p.get("state") != expected_state:
            fail(f"{pid} state was improperly changed")
        if "For every" not in p.get("quantified_statement", ""):
            fail(f"{pid} lost quantified statement")
        if not p.get("premises"):
            fail(f"{pid} premises missing")
    by_po = {p["id"]: p for p in pos}
    if "keeps PO-05 OPEN" not in by_po["PO-05"]["quantified_statement"] or "certified result" not in by_po["PO-05"]["quantified_statement"]:
        fail("PO-05 acceptance semantics were weakened by treating blockers as success")
    if "keeps PO-08 OPEN" not in by_po["PO-08"]["quantified_statement"] or "terminating successful route" not in by_po["PO-08"]["quantified_statement"]:
        fail("PO-08 total-dispatch acceptance semantics were weakened")
    if "keeps PO-09 OPEN" not in by_po["PO-09"]["quantified_statement"] or "yields finite conventional usable engineering geometry" not in by_po["PO-09"]["quantified_statement"]:
        fail("PO-09 realization acceptance semantics were weakened")

    blockers = {b.get("id"): b for b in obj.get("proof_blockers", [])}
    if set(blockers) != EXPECTED_BLOCKERS:
        fail("propagated proof-blocker set drift")
    if blockers["PB-007-01"].get("status") != "OPEN" or blockers["PB-007-02"].get("status") != "OPEN":
        fail("MC-007 analytic blockers were hidden")
    if "MC-038" not in blockers["PB-007-01"].get("affected_descendants", []) or "MC-038" not in blockers["PB-007-04"].get("affected_descendants", []):
        fail("required MC-B blocker propagation drift")

    protected = obj.get("protected_semantics", {})
    if not protected or any(v is not True for v in protected.values()):
        fail("protected source/provenance/journal/body semantics weakened")

    if check_shared:
        shared = load(PROOF)
        if shared.get("contract_revision") != "MC-008-integrated-1":
            fail("shared PO register revision not reconciled")
        if shared.get("contract_evidence") != "research/machining-completeness/tasks/MC-008/termination-proof-dag-v1.json":
            fail("shared PO register evidence binding drift")
        shared_pos = shared.get("obligations", [])
        if len(shared_pos) != 12:
            fail("shared PO register count drift")
        contract_by_id = {x["id"]: x for x in pos}
        for p in shared_pos:
            pid = p.get("id")
            if pid not in contract_by_id:
                fail("shared PO register contains unexpected obligation")
            c = contract_by_id[pid]
            for key in ("integration_owner", "state", "depends_on", "quantified_statement", "premises"):
                if p.get(key) != c.get(key):
                    fail(f"shared PO register mismatch for {pid}.{key}")
            if p.get("contract_evidence") != shared.get("contract_evidence"):
                fail(f"shared PO evidence binding missing for {pid}")
            if pid == "PO-01":
                if not p.get("accepted_evidence"):
                    fail("PO-01 lost accepted evidence")
            elif p.get("accepted_evidence"):
                fail(f"{pid} gained accepted evidence while still open")
        assert_acyclic(shared_pos, "shared proof-obligation DAG")

        reg = load(OUTCOMES).get("tasks", {}).get("MC-008", {})
        if reg.get("state") != "COMPLETED_RESEARCH":
            fail("MC-008 outcome registry not reconciled")
        required_artifacts = {
            "research/machining-completeness/tasks/MC-008/termination-proof-dag-v1.json",
            "research/machining-completeness/tasks/MC-008/report.md",
            "research/machining-completeness/tasks/MC-008/outcome.json",
            "research/machining-completeness/tasks/MC-008/verify.py",
            "research/machining-completeness/proof-obligations-v1.json",
            "docs/machining-completeness/02-COMPLETENESS-ARGUMENT.md",
        }
        if not required_artifacts <= set(reg.get("accepted_artifacts", [])):
            fail("MC-008 outcome registry artifact binding incomplete")
        registry_blockers = {b.get("id") if isinstance(b, dict) else b for b in reg.get("blockers", [])}
        if registry_blockers != EXPECTED_BLOCKERS:
            fail("MC-008 outcome registry blocker propagation drift")

def interval_add(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    if a[0] > a[1] or b[0] > b[1]:
        fail("invalid directed interval")
    return a[0] + b[0], a[1] + b[1]

def interval_scale_nonnegative(a: tuple[Fraction, Fraction], factor: Fraction) -> tuple[Fraction, Fraction]:
    if a[0] > a[1] or factor < 0:
        fail("invalid nonnegative interval scale")
    return factor * a[0], factor * a[1]

def compose_error(inherited: tuple[Fraction, Fraction] | None, local: tuple[Fraction, Fraction] | None, *, transfer: Fraction = Fraction(1)) -> tuple[Fraction, Fraction] | None:
    if inherited is None or local is None:
        return None
    return interval_add(interval_scale_nonnegative(inherited, transfer), local)

def bounded_refinement(*, certified_depth: int | None, completed_steps: int, semantic_success: bool) -> str:
    if certified_depth is None:
        return "PROOF_BLOCKER"
    if certified_depth < 0 or completed_steps < 0:
        fail("negative refinement count")
    if completed_steps > certified_depth:
        fail("refinement exceeded its proved finite bound")
    if semantic_success:
        return "CERTIFIED"
    if completed_steps == certified_depth:
        return "PROOF_BLOCKER"
    return "REFINE"

def boundary_controls() -> None:
    F = Fraction
    if interval_add((F(0), F(0)), (F(0), F(0))) != (F(0), F(0)):
        fail("zero error composition boundary failed")
    if compose_error((F(1, 10), F(1, 5)), (F(1, 100), F(1, 50)), transfer=F(2)) != (F(21, 100), F(21, 50)):
        fail("exact rational error composition failed")
    if compose_error(None, (F(0), F(1, 10))) is not None or compose_error((F(0), F(1, 10)), None) is not None:
        fail("unknown error component was silently certified")
    if bounded_refinement(certified_depth=0, completed_steps=0, semantic_success=True) != "CERTIFIED":
        fail("zero-depth certified boundary failed")
    if bounded_refinement(certified_depth=5, completed_steps=4, semantic_success=False) != "REFINE":
        fail("bounded refinement progress failed")
    if bounded_refinement(certified_depth=5, completed_steps=5, semantic_success=False) != "PROOF_BLOCKER":
        fail("exhausted proved bound did not fail closed")
    if bounded_refinement(certified_depth=None, completed_steps=0, semantic_success=False) != "PROOF_BLOCKER":
        fail("missing stopping proof did not fail closed")

def expect_reject(mutator) -> None:
    obj = load(CONTRACT)
    mutator(obj)
    try:
        validate(obj, check_shared=False)
    except AssertionError:
        return
    fail("adversarial mutation was accepted")

def adversarial_controls() -> None:
    expect_reject(lambda o: o["scope_guard"].__setitem__("operation_denominator_preserved", 23))
    expect_reject(lambda o: o["scope_guard"].__setitem__("universal_constructive_capability_claimed", True))
    expect_reject(lambda o: o["arithmetic_guards"].__setitem__("global_untyped_epsilon_forbidden", False))
    expect_reject(lambda o: o["arithmetic_guards"].__setitem__("timeout_or_iteration_cap_is_not_semantic_success", False))
    expect_reject(lambda o: o.__setitem__("proof_blockers", [b for b in o["proof_blockers"] if b["id"] != "PB-007-01"]))
    expect_reject(lambda o: o["error_composition"].__setitem__("topology_is_noncompensating", False))
    expect_reject(lambda o: o["error_composition"].__setitem__("unknown_component_terminal", "ZERO"))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-05").__setitem__("state", "ACCEPTED"))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-04").__setitem__("integration_owner", "MC-008"))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-03").__setitem__("quantified_statement", "Finite composition works."))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-05").__setitem__("quantified_statement", "For every query, return a result or blocker."))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-08").__setitem__("quantified_statement", "For every query, dispatch or block."))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-09").__setitem__("quantified_statement", "For every state, return geometry or an open obligation."))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-01").__setitem__("depends_on", ["PO-11"]))
    expect_reject(lambda o: next(x for x in o["proof_obligation_dag"] if x["id"] == "PO-11").__setitem__("depends_on", ["PO-11"]))
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
    boundary_controls()
    adversarial_controls()
    print("MC-008 termination, arithmetic, PO-DAG, boundary and adversarial verification passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
