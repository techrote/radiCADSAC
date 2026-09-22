#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha1
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

spec = importlib.util.spec_from_file_location("mc033_body_state", HERE / "body_state.py")
if spec is None or spec.loader is None:
    raise ImportError("cannot load MC-033 body_state.py")
BS = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BS
spec.loader.exec_module(BS)


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _bound(payload):
    return BS.bind_certificate(payload)


def _material(body_id, revision, relation="REMOVED_POSITIVE_VOLUME"):
    return _bound({
        "schema": BS.MATERIAL_SCHEMA,
        "input_digest": "input-digest",
        "canonical_digest": "canonical-digest",
        "sweep_digest": "sweep-digest",
        "body_id": body_id,
        "input_revision": revision,
        "configuration_digest": "config-digest",
        "challenge_id": "challenge-033",
        "result": {
            "status": "CERTIFIED",
            "relation": relation,
            "durable_transition_owner": "MC-033",
            "body_transition_committed": False,
        },
    })


def _event(revision, relation="CRITICAL_TOPOLOGY_EVENT"):
    status = "DECIDED" if relation == "TOUCHING_ONLY_NO_MATERIAL_TRANSITION" else "CERTIFIED"
    return _bound({
        "schema": BS.EVENT_SCHEMA,
        "input_digest": "input-digest",
        "canonical_digest": "canonical-digest",
        "sweep_digest": "sweep-digest",
        "challenge_id": "challenge-033",
        "configuration_digest": "config-digest",
        "decision": {
            "status": status,
            "relation": relation,
            "input_revision": revision,
            "durable_transition_owner": "MC-033",
            "body_transition_committed": False,
        },
    })


def _connectivity(kind, body_id, revision, material_digest, event_digest=None, **fields):
    payload = {
        "schema": BS.CONNECTIVITY_SCHEMA,
        "proof_status": "PROVED",
        "checker_authority": "independent_mc015_style_checker",
        "transition_kind": kind,
        "target_body_id": body_id,
        "input_revision": revision,
        "material_certificate_digest": material_digest,
        "identity_authority": BS.IDENTITY_AUTHORITY,
    }
    if event_digest is not None:
        payload["event_certificate_digest"] = event_digest
    payload.update(fields)
    return _bound(payload)


def _output(body_id, lineage_id, role, material_digest, component_id, volume="1"):
    return {
        "body_id": body_id,
        "lineage_id": lineage_id,
        "role": role,
        "component_certificate_id": component_id,
        "material_certificate_digest": material_digest,
        "identity_authority": BS.IDENTITY_AUTHORITY,
        "positive_volume_witness": volume,
    }


def _transition(state, *, kind, target_body_id, target_lineage_id, output_revision,
                outputs, positive_new_removal="1/1000000", other_body_id=None,
                relation="CRITICAL_TOPOLOGY_EVENT", connectivity_overrides=None,
                residual="0"):
    material_relation = ("TOUCHING_ONLY_NO_MATERIAL_TRANSITION"
                         if kind == "TOUCH_ONLY" else "REMOVED_POSITIVE_VOLUME")
    material = _material(target_body_id, state.revision, material_relation)
    material_digest = BS.digest_json(material)
    event = None
    event_digest = None
    if kind in {"SPLIT", "DISAPPEAR", "TOUCH_ONLY"}:
        event_relation = ("TOUCHING_ONLY_NO_MATERIAL_TRANSITION"
                          if kind == "TOUCH_ONLY" else relation)
        event = _event(state.revision, event_relation)
        event_digest = BS.digest_json(event)

    defaults = {}
    if kind == "SPLIT":
        defaults = {
            "component_count": len(outputs),
            "complete_remainder_partition": True,
            "pairwise_interior_disjoint": True,
            "component_certificate_ids": [item["component_certificate_id"] for item in outputs],
        }
    elif kind == "DISAPPEAR":
        defaults = {"component_count": 0, "exact_empty_material": True}
    elif kind == "TOUCH_ONLY":
        defaults = {"touch_only": True}
    else:
        defaults = {"continuity_proved": True}
    defaults.update(connectivity_overrides or {})
    connectivity = _connectivity(
        kind, target_body_id, state.revision, material_digest, event_digest, **defaults
    )

    payload = {
        "schema": BS.TRANSITION_SCHEMA,
        "status": "CERTIFIED",
        "kind": kind,
        "identity_authority": BS.IDENTITY_AUTHORITY,
        "common_frame": BS.COMMON_FRAME,
        "input_revision": state.revision,
        "output_revision": output_revision,
        "target_body_id": target_body_id,
        "target_lineage_id": target_lineage_id,
        "transition_id": f"transition-{output_revision}",
        "operation_id": "mc033-control-operation",
        "source_digest": "source-digest",
        "canonical_digest": "canonical-digest",
        "challenge_id": "challenge-033",
        "configuration_digest": "config-digest",
        "positive_new_removal": positive_new_removal,
        "outputs": outputs,
        "material_certificate": material,
        "material_certificate_digest": material_digest,
        "connectivity_certificate": connectivity,
        "connectivity_certificate_digest": BS.digest_json(connectivity),
    }
    if event is not None:
        payload["event_certificate"] = event
        payload["event_certificate_digest"] = event_digest
    if kind == "DISAPPEAR":
        payload["residual_positive_volume"] = residual
    if other_body_id is not None:
        payload["other_body_id"] = other_body_id
    return _bound(payload), material_digest


def _seed_state():
    return BS.initial_state(
        revision="r0",
        bodies=[
            {"body_id":"B0","lineage_id":"L0","material_certificate_digest":"seed-B0","identity_authority":BS.IDENTITY_AUTHORITY},
            {"body_id":"BX","lineage_id":"LX","material_certificate_digest":"seed-BX","identity_authority":BS.IDENTITY_AUTHORITY},
        ],
    )


def _rebind_nested_transition(transition):
    """Recompute nested connectivity/outer bindings after a deliberate test edit."""
    if "connectivity_certificate" in transition:
        conn = {k:v for k,v in transition["connectivity_certificate"].items() if k != "binding_sha256"}
        transition["connectivity_certificate"] = _bound(conn)
        transition["connectivity_certificate_digest"] = BS.digest_json(transition["connectivity_certificate"])
    return _bound({k:v for k,v in transition.items() if k != "binding_sha256"})


def self_test():
    state = _seed_state()
    _assert(state.material_state() == "NONEMPTY_MATERIAL", "seed must be nonempty")

    # Exact positive parting/split: explicit continuation plus fresh descendant.
    material = _material("B0", "r0")
    md = BS.digest_json(material)
    outputs = [
        _output("B0", "L0", "CONTINUATION", md, "component-main", "2"),
        _output("B1", "L1", "DESCENDANT", md, "component-parted", "1/1000000"),
    ]
    split, _ = _transition(
        state, kind="SPLIT", target_body_id="B0", target_lineage_id="L0",
        output_revision="r1", outputs=outputs, positive_new_removal="1/1000000"
    )
    result = BS.commit_transition(state, split)
    _assert(result.committed, f"exact split failed: {result.reason}")
    state = result.state
    _assert(set(state.active_body_ids()) == {"B0", "B1", "BX"}, "split dropped or invented body")
    _assert(len(state.lineage_edges) == 1, "split must record one descendant lineage edge")
    _assert(state.lineage_edges[0].parent_body_id == "B0" and state.lineage_edges[0].child_body_id == "B1",
            "split lineage edge wrong")

    # Remachining explicitly targets the descendant; no largest/nearest-body guess.
    material = _material("B1", "r1")
    md = BS.digest_json(material)
    continue_outputs = [_output("B1", "L1", "CONTINUATION", md, "component-B1", "1/2000000")]
    cont, _ = _transition(
        state, kind="CONTINUE", target_body_id="B1", target_lineage_id="L1",
        output_revision="r2", outputs=continue_outputs, positive_new_removal="1/2000000"
    )
    result = BS.commit_transition(state, cont)
    _assert(result.committed and result.state.body("B1").status == BS.ACTIVE, "descendant remachining failed")
    state = result.state

    # Exact-zero contact advances chronology but cannot merge durable identities.
    touch, _ = _transition(
        state, kind="TOUCH_ONLY", target_body_id="B0", target_lineage_id="L0",
        output_revision="r3", outputs=[], positive_new_removal="0", other_body_id="B1"
    )
    result = BS.commit_transition(state, touch)
    _assert(result.committed, f"touch control failed: {result.reason}")
    state = result.state
    _assert(set(state.active_body_ids()) == {"B0", "B1", "BX"}, "touch merged/dropped durable bodies")
    _assert(len(state.contacts) == 1, "touch relation not recorded")

    # Exact disappearance retains durable record/lineage but no active material.
    disappear, _ = _transition(
        state, kind="DISAPPEAR", target_body_id="B1", target_lineage_id="L1",
        output_revision="r4", outputs=[], positive_new_removal="1/2000000", residual="0"
    )
    result = BS.commit_transition(state, disappear)
    _assert(result.committed, f"disappearance failed: {result.reason}")
    state = result.state
    _assert(state.body("B1").status == BS.EXHAUSTED, "exhausted durable record was not retained")
    _assert(state.body("B1").lineage_id == "L1", "exhaustion lost lineage")
    _assert("B1" not in state.active_body_ids(), "empty body remained active")

    # An exhausted body cannot be remachined/revived by pure-removal machining.
    stale_revive = deepcopy(cont)
    stale_revive["input_revision"] = state.revision
    stale_revive["output_revision"] = "r5"
    stale_revive = _bound({k:v for k,v in stale_revive.items() if k != "binding_sha256"})
    rejected = BS.commit_transition(state, stale_revive)
    _assert(not rejected.committed and rejected.state == state, "exhausted body was revived")

    # Positive residual can never be rounded to empty.
    bad_empty, _ = _transition(
        state, kind="DISAPPEAR", target_body_id="B0", target_lineage_id="L0",
        output_revision="bad-empty", outputs=[], positive_new_removal="1", residual="1/1000000"
    )
    rejected = BS.commit_transition(state, bad_empty)
    _assert(rejected.status == "SEMANTIC_BLOCKER" and rejected.state == state,
            "positive residual was accepted as empty")

    # Missing connectivity proof is typed PB-007-04 boundary, not guessed topology.
    material = _material("B0", state.revision)
    md = BS.digest_json(material)
    blocked_outputs = [
        _output("B0", "L0", "CONTINUATION", md, "c-a", "1"),
        _output("B2", "L2", "DESCENDANT", md, "c-b", "1"),
    ]
    blocked, _ = _transition(
        state, kind="SPLIT", target_body_id="B0", target_lineage_id="L0",
        output_revision="blocked", outputs=blocked_outputs,
        connectivity_overrides={"proof_status":"UNKNOWN"}
    )
    rejected = BS.commit_transition(state, blocked)
    _assert(rejected.status == "BLOCKED" and rejected.state == state,
            "unproved connectivity was not blocked")

    # No merge transition exists in pure removal.
    merge = deepcopy(touch)
    merge["input_revision"] = state.revision
    merge["output_revision"] = "merge-attempt"
    merge["kind"] = "MERGE"
    merge = _bound({k:v for k,v in merge.items() if k != "binding_sha256"})
    rejected = BS.commit_transition(state, merge)
    _assert(rejected.status == "SEMANTIC_BLOCKER" and rejected.state == state,
            "pure-removal merge was accepted")

    # Backend identity/component-order/size/proximity may not become durable authority.
    backend = deepcopy(touch)
    backend["input_revision"] = state.revision
    backend["output_revision"] = "backend-attempt"
    backend["identity_authority"] = "backend_topology_id"
    backend = _bound({k:v for k,v in backend.items() if k != "binding_sha256"})
    rejected = BS.commit_transition(state, backend)
    _assert(rejected.status == "SEMANTIC_BLOCKER" and rejected.state == state,
            "backend topology became durable identity authority")

    # Zero-volume split children are not bodies.
    material = _material("B0", state.revision)
    md = BS.digest_json(material)
    zero_outputs = [
        _output("B0", "L0", "CONTINUATION", md, "z-a", "1"),
        _output("BZ", "LZ", "DESCENDANT", md, "z-b", "0"),
    ]
    zero_split, _ = _transition(
        state, kind="SPLIT", target_body_id="B0", target_lineage_id="L0",
        output_revision="zero-child", outputs=zero_outputs, positive_new_removal="1/1000000"
    )
    rejected = BS.commit_transition(state, zero_split)
    _assert(rejected.status == "SEMANTIC_BLOCKER", "zero-volume split child accepted")

    # Binary-float authority is rejected even at a plausible tiny positive value.
    float_split = deepcopy(zero_split)
    float_split["outputs"][1]["positive_volume_witness"] = 1e-6
    float_split = _bound({k:v for k,v in float_split.items() if k != "binding_sha256"})
    rejected = BS.commit_transition(state, float_split)
    _assert(rejected.status == "SEMANTIC_BLOCKER", "binary float became volume authority")

    # Incomplete partition evidence remains blocked.
    incomplete, _ = _transition(
        state, kind="SPLIT", target_body_id="B0", target_lineage_id="L0",
        output_revision="incomplete", outputs=blocked_outputs,
        connectivity_overrides={"complete_remainder_partition":False}
    )
    rejected = BS.commit_transition(state, incomplete)
    _assert(rejected.status == "BLOCKED" and rejected.state == state,
            "incomplete split partition was committed")

    # Mutating nested upstream evidence invalidates certificate chain.
    mutated = deepcopy(bad_empty)
    mutated["input_revision"] = state.revision
    mutated["output_revision"] = "mutated-material"
    mutated["material_certificate"]["result"]["relation"] = "NOT_IN_SWEEP"
    mutated = _bound({k:v for k,v in mutated.items() if k != "binding_sha256"})
    rejected = BS.commit_transition(state, mutated)
    _assert(rejected.status == "SEMANTIC_BLOCKER", "mutated MC-031 certificate accepted")

    # Resource refusal is finite non-success and leaves state untouched.
    refused = _bound({
        "schema": BS.TRANSITION_SCHEMA, "status":"RESOURCE_REFUSAL", "kind":"CONTINUE",
        "identity_authority":BS.IDENTITY_AUTHORITY, "common_frame":BS.COMMON_FRAME,
        "input_revision":state.revision, "output_revision":"refused",
        "target_body_id":"B0", "target_lineage_id":"L0", "transition_id":"refused",
        "operation_id":"op", "source_digest":"s", "canonical_digest":"c",
        "challenge_id":"ch", "configuration_digest":"cfg"
    })
    rejected = BS.commit_transition(state, refused)
    _assert(rejected.status == "RESOURCE_REFUSAL" and rejected.state == state,
            "resource refusal mutated durable state")

    # Durable IDs and lineage nodes are globally unique, including historical records.
    try:
        BS.BodyState(revision="dup", bodies=(state.body("B0"), state.body("B0")))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate durable body IDs accepted")

    try:
        BS.q(0.0)
    except TypeError:
        pass
    else:
        raise AssertionError("binary float exact authority accepted")

    print("MC-033 self-test: PASS")


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def contract_check():
    contract = json.loads((HERE / "durable-body-state-contract-v1.json").read_text())
    _assert(contract["task"] == "MC-033", "wrong contract task")
    _assert(contract["source_baseline"] == "46b84622bccc2ae68f4a68042480b3d2d5d6de9b", "baseline drift")
    _assert(contract["identity_authority"] == BS.IDENTITY_AUTHORITY, "identity authority drift")
    _assert(contract["regularization"]["zero_volume_artifacts_are_material"] is False,
            "regularization cannot promote lower-dimensional artifacts to material")
    _assert(contract["regularization"]["positive_volume_may_be_dropped"] is False,
            "positive volume cannot be dropped")
    _assert(contract["pure_removal"]["merge_supported"] is False, "pure removal cannot merge durable bodies")
    _assert(set(contract["transition_kinds"]) == BS.TRANSITION_KINDS, "transition-kind drift")

    for dep in contract["dependency_artifacts"]:
        path = ROOT / dep["path"]
        _assert(path.is_file(), f"missing dependency artifact {dep['path']}")
        _assert(_git_blob_sha(path) == dep["blob_sha"], f"dependency blob drift: {dep['task']}")
    for dep in contract["auxiliary_bound_inputs"]:
        path = ROOT / dep["path"]
        _assert(path.is_file(), f"missing auxiliary input {dep['path']}")
        _assert(_git_blob_sha(path) == dep["blob_sha"], f"auxiliary blob drift: {dep['task']}")

    graph = json.loads((ROOT / "research/machining-completeness/task-graph-v1.json").read_text())
    task = next(item for item in graph["tasks"] if item["id"] == "MC-033")
    deps = {(item["task"], item["type"]) for item in task["dependencies"]}
    _assert(deps == {("MC-005","capability"), ("MC-026","artifact"), ("MC-015","artifact")},
            "MC-033 dependency contract drift")
    _assert("MC-038" not in {item["task"] for item in task["dependencies"]},
            "pre-gate MC-038 cycle reintroduced")

    po = json.loads((ROOT / "research/machining-completeness/proof-obligations-v1.json").read_text())
    po07 = next(item for item in po["obligations"] if item["id"] == "PO-07")
    _assert(po07["state"] == "OPEN" and po07["integration_owner"] == "MC-032",
            "MC-033 must not self-close global PO-07")

    registry = json.loads((ROOT / "research/machining-completeness/outcomes-v1.json").read_text())
    entry = registry["tasks"]["MC-033"]
    _assert(entry["state"] == "COMPLETED_RESEARCH", "MC-033 not registered completed research")
    blocker_ids = {item["id"] for item in entry.get("blockers", [])}
    _assert("PB-007-04" in blocker_ids, "PB-007-04 was erased")

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text()
    _assert("tasks/MC-033/body_state.py" in workflow, "MC-033 implementation missing from compile gate")
    _assert("tasks/MC-033/verify.py" in workflow, "MC-033 verifier missing from compile gate")
    _assert("mc_workflow.py verify MC-033" in workflow, "MC-033 missing from completed-task gate")

    outcome = json.loads((HERE / "outcome.json").read_text())
    _assert(outcome["result_kind"] == "COMPLETED_RESEARCH", "outcome kind drift")
    _assert(any("PB-007-04" in claim for claim in outcome["open_claims"]), "PB-007-04 not preserved open")
    _assert(any("MC-B" in claim and "NOT_ESTABLISHED" in claim for claim in outcome["open_claims"]),
            "MC-B state not preserved")

    report = (HERE / "report.md").read_text()
    for token in ("PB-007-04", "RB-016-02", "RB-016-04", "RB-016-05", "NOT_ESTABLISHED", "canonical_journal"):
        _assert(token in report, f"report lost required boundary {token}")

    print("MC-033 contract: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--contract", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not args.contract:
        args.self_test = args.contract = True
    if args.self_test:
        self_test()
    if args.contract:
        contract_check()


if __name__ == "__main__":
    main()
