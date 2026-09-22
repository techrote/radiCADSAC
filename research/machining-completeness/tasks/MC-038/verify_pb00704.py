#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00704-topology-dependency-v5.json"
REPORT = TASK / "pb00704-report-v5.md"
DOC = ROOT / "docs" / "machining-completeness" / "29-PB00704-TOPOLOGY-DEPENDENCY-BOUNDARY.md"
PROOFS = MC / "proof-obligations-v1.json"
PROGRAMME = MC / "programme-v1.json"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "2f588da9f4315bed73be2700eccb34288accc82f"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-007/outcome.json": "8d54872292dfd9f632c79c76994a467d26eaaf9c",
    "research/machining-completeness/tasks/MC-032/outcome.json": "bc42e0f824621af10354534dc83aa03765a893ed",
    "research/machining-completeness/tasks/MC-033/outcome.json": "5bd663c1aa098224f5909d8781009c13f50e40e4",
    "research/machining-completeness/proof-obligations-v1.json": "97b023c5ea550f598b16ba9a1aeaabbf95ecba6f",
    "research/machining-completeness/tasks/MC-038/gate-scope-retry-v2.json": "76094029a264a5ce226694548b27896f9e0cd430",
    "research/machining-completeness/tasks/MC-038/pb00701-decision-boundary-v3.json": "ec2edaef5ef1cf838fc91e68b25147f41525ac2a",
    "research/machining-completeness/tasks/MC-038/pb00703-source-codec-boundary-v4.json": "1a69ad4073a38d0448474fa8046657266a3b79e8",
}

sys.path.insert(0, str(TASK))
import pb00704_topology_checker as topology  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def domain_operation_count() -> int:
    return len(load(DOMAIN)["coverage_rule"]["required_operation_ids"])


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00704-topology-dependency/5.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 168
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-04"
    assert artifact["decision"] == "BOUNDED_EXACT_CONNECTIVITY_CHECKER_ESTABLISHED_FULL_BLOCKER_DEPENDENCY_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    review = artifact["dependency_review"]
    assert review["full_blocker_status"] == "OPEN_PROPAGATED"
    assert review["po07_status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert set(review["dependency_edges"]["PB-007-04"]) == {"PB-007-01", "PB-007-02", "PB-007-03", "PO-02", "PO-04"}
    assert any("independently certified complete finite partition" in claim for claim in review["independently_constructive_now"])
    assert any("PB-007-01" in claim for claim in review["not_independently_constructive_yet"])
    assert any("PB-007-02" in claim for claim in review["not_independently_constructive_yet"])
    assert any("PB-007-03" in claim for claim in review["not_independently_constructive_yet"])

    route = artifact["implemented_bounded_subroute"]
    assert route["id"] == "EXACT_RATIONAL_AXIS_ALIGNED_COMPLETE_PARTITION_V1"
    assert "positive-area face adjacency" in route["connectivity_rule"]
    assert "TOUCH_ONLY" in route["touch_rule"]
    assert route["scalar_authority"].startswith("exact rationals only")
    assert route["universal_claim"] is False
    assert "body_id" in route["identity_rule"] and "lineage_id" in route["identity_rule"]

    controls = artifact["boundary_controls"]
    for token in (
        "face adjacency",
        "edge-only",
        "point-only",
        "1/1000000 positive-volume bridge",
        "1/1000000 positive gap",
        "empty partition",
        "interior overlap",
        "zero-thickness",
        "binary-float",
        "backend/kernel",
        "stale or mismatched",
        "forged complete=true",
        "self-certified",
    ):
        assert any(token in item for item in controls), f"missing control: {token}"

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDS_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"].startswith("OPEN_PROPAGATED")
    for po in ("PO-02", "PO-04", "PO-05", "PO-07", "PO-08"):
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == "NOT_ESTABLISHED"
    assert effect["MC-1"] == "NOT_ESTABLISHED"
    assert set(artifact["downstream_non_prerequisites_unchanged"]) == {
        "RB-016-01", "RB-016-02", "RB-016-03", "RB-016-04", "RB-016-05", "PO-03", "PO-06", "PO-09"
    }
    assert artifact["next_routing"]["mc_b_retry_allowed"] is False
    assert not any(artifact["resources"].values())
    assert all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    assert domain_operation_count() == 26, "frozen operation denominator drift"
    for path, sha in EXPECTED_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"historical evidence drift: {path}"

    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    assert proofs["PO-02"]["state"] == "OPEN"
    assert proofs["PO-04"]["state"] == "OPEN"
    assert proofs["PO-05"]["state"] == "OPEN"
    assert proofs["PO-07"]["state"] == "OPEN"
    assert proofs["PO-07"]["integration_owner"] == "MC-032"
    assert set(proofs["PO-07"]["depends_on"]) == {"PO-01", "PO-02", "PO-03", "PO-04"}
    assert proofs["PO-08"]["state"] == "OPEN"

    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-04",
            "open",
            "po-07",
            "mc-b",
            "not_established",
            "1/1000000",
            "source/audio/provenance",
            "positive-volume",
            "body_id",
            "lineage_id",
            "step",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00704_topology_checker.py" in workflow
    assert "verify_pb00704.py --contract" in workflow
    assert "verify_pb00704.py --self-test" in workflow


def cert(partition):
    return topology.certify_connectivity(partition, topology.expected_binding(partition))


def expect_rejected(callable_):
    try:
        callable_()
    except Exception:
        return
    raise AssertionError("adversarial input was accepted")


def run_model_controls():
    face = topology.make_partition([
        topology.box("a", "0", "1", "0", "1", "0", "1"),
        topology.box("b", "1", "2", "0", "1", "0", "1"),
    ])
    face_cert = cert(face)
    assert face_cert["component_count"] == 1
    assert face_cert["components"] == [["a", "b"]]
    assert face_cert["contact_counts"]["FACE_ADJACENT"] == 1
    assert face_cert["durable_identity_authority"] is False
    assert face_cert["universal_topology_claim"] is False

    edge = topology.make_partition([
        topology.box("a", "0", "1", "0", "1", "0", "1"),
        topology.box("b", "1", "2", "1", "2", "0", "1"),
    ])
    edge_cert = cert(edge)
    assert edge_cert["component_count"] == 2
    assert edge_cert["contact_counts"]["EDGE_TOUCH_ONLY"] == 1

    point = topology.make_partition([
        topology.box("a", "0", "1", "0", "1", "0", "1"),
        topology.box("b", "1", "2", "1", "2", "1", "2"),
    ])
    point_cert = cert(point)
    assert point_cert["component_count"] == 2
    assert point_cert["contact_counts"]["POINT_TOUCH_ONLY"] == 1

    micro_bridge = topology.make_partition([
        topology.box("left", "0", "1", "0", "1", "0", "1"),
        topology.box("bridge", "1", "1000001/1000000", "0", "1", "0", "1"),
        topology.box("right", "1000001/1000000", "2", "0", "1", "0", "1"),
    ])
    bridge_cert = cert(micro_bridge)
    assert bridge_cert["component_count"] == 1
    assert bridge_cert["components"] == [["bridge", "left", "right"]]

    micro_gap = topology.make_partition([
        topology.box("left", "0", "1", "0", "1", "0", "1"),
        topology.box("right", "1000001/1000000", "2", "0", "1", "0", "1"),
    ])
    gap_cert = cert(micro_gap)
    assert gap_cert["component_count"] == 2
    assert gap_cert["contact_counts"]["DISJOINT"] == 1

    disconnected = topology.make_partition([
        topology.box("c", "10", "11", "0", "1", "0", "1"),
        topology.box("a", "0", "1", "0", "1", "0", "1"),
        topology.box("b", "1", "2", "0", "1", "0", "1"),
    ])
    disconnected_cert = cert(disconnected)
    assert disconnected_cert["components"] == [["a", "b"], ["c"]]

    reordered = copy.deepcopy(disconnected)
    reordered["cells"].reverse()
    assert cert(reordered)["certificate_digest"] == disconnected_cert["certificate_digest"]

    empty = topology.make_partition([])
    empty_cert = cert(empty)
    assert empty_cert["exact_empty_material"] is True
    assert empty_cert["component_count"] == 0
    assert empty_cert["components"] == []

    overlapping = topology.make_partition([
        topology.box("a", "0", "2", "0", "1", "0", "1"),
        topology.box("b", "1", "3", "0", "1", "0", "1"),
    ])
    expect_rejected(lambda: cert(overlapping))

    zero = topology.make_partition([topology.box("z", "0", "0", "0", "1", "0", "1")])
    expect_rejected(lambda: cert(zero))

    floating = topology.make_partition([topology.box("f", 0.0, "1", "0", "1", "0", "1")])
    expect_rejected(lambda: cert(floating))

    scientific = topology.make_partition([topology.box("f", "0", "1e-6", "0", "1", "0", "1")])
    expect_rejected(lambda: cert(scientific))

    backend = topology.make_partition([topology.box("k", "0", "1", "0", "1", "0", "1")])
    backend["cells"][0]["kernel_id"] = "opaque-7"
    expect_rejected(lambda: cert(backend))

    durable = topology.make_partition([topology.box("d", "0", "1", "0", "1", "0", "1")])
    durable["cells"][0]["body_id"] = "body-1"
    expect_rejected(lambda: cert(durable))

    stale = topology.make_partition([topology.box("s", "0", "1", "0", "1", "0", "1")])
    stale_binding = topology.expected_binding(stale)
    stale_binding["revision"] += 1
    expect_rejected(lambda: topology.certify_connectivity(stale, stale_binding))

    forged = topology.make_partition([topology.box("q", "0", "1", "0", "1", "0", "1")])
    forged["completeness_certificate"] = {"complete": True}
    expect_rejected(lambda: cert(forged))

    self_certified = topology.make_partition([topology.box("q", "0", "1", "0", "1", "0", "1")])
    self_certified["completeness_certificate"]["independent_of_connectivity_checker"] = False
    expect_rejected(lambda: cert(self_certified))

    duplicate = topology.make_partition([
        topology.box("dup", "0", "1", "0", "1", "0", "1"),
        topology.box("dup", "1", "2", "0", "1", "0", "1"),
    ])
    expect_rejected(lambda: cert(duplicate))


def expect_artifact_rejected(mutator):
    artifact = copy.deepcopy(load(ARTIFACT))
    mutator(artifact)
    try:
        validate_artifact(artifact, check_repo=False)
    except Exception:
        return
    raise AssertionError("adversarial artifact mutation accepted")


def run_adversarial_artifact_controls():
    expect_artifact_rejected(lambda a: a["dependency_review"].__setitem__("full_blocker_status", "CLOSED"))
    expect_artifact_rejected(lambda a: a["dependency_review"].__setitem__("po07_status", "ACCEPTED"))
    expect_artifact_rejected(lambda a: a["implemented_bounded_subroute"].__setitem__("universal_claim", True))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("MC-B", "ACCEPTED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("PB-007-01", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("PB-007-03", "CLOSED"))
    expect_artifact_rejected(lambda a: a["next_routing"].__setitem__("mc_b_retry_allowed", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("durable_body_lineage_preserved", False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("select --contract and/or --self-test")

    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-04 contract: PASS")
    if args.self_test:
        validate_artifact(load(ARTIFACT), check_repo=False)
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-04 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
