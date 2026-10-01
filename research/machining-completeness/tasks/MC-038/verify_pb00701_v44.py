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
DOC = ROOT / "docs" / "machining-completeness" / "68-PB00701-ALGEBRAIC-ORIENTATION-CUT.md"
ARTIFACT = TASK / "pb00701-algebraic-orientation-cut-v44.json"
REPORT = TASK / "pb00701-report-v44.md"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v44.yml"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"

EXPECTED_BASE = "ad3271b72d4cd1965c32af7ed45de83aa9f211e5"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_orientation_root_partition_model.py": "2f96622b5c69655279d66fe2b36f8f3e03414660",
    "research/machining-completeness/tasks/MC-038/test_pb00701_orientation_root_partition_adversarial.py": "fc15314284c8cbce4cb4949f719c5a14bdc78988",
    "research/machining-completeness/tasks/MC-038/pb00701-orientation-root-partition-v41.json": "c169c0c7db5629ee4d8dd6a57cb6ce9ff9dd1d84",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v41.py": "2b1bab5398197dace7326ad2c34f5aa7ab255d64",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import test_pb00701_algebraic_orientation_cut_adversarial as adversarial
import test_pb00701_algebraic_orientation_cut_authority as authority


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected mutation rejection")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-algebraic-orientation-cut-boundary/44.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 253
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["required_predecessor"]["pull_request"] == 252
    assert artifact["required_predecessor"]["v41_merge"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["investigation_outcome"] == "BOUNDED_NEGATIVE_RESULT"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    assert "CONSUMPTION_AUTHORITY_MISSING" in artifact["decision"]

    pins = {path: sha for path, sha in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    boundary = artifact["implemented_boundary"]
    assert "square-free" in boundary["coordinate_authority"]
    assert "Sturm" in boundary["coordinate_authority"]
    assert "BLOCKED" in boundary["normalized_child_reparameterization"]
    assert "BLOCKED" in boundary["phase_endpoint_authority"]
    assert boundary["consumption_decision"] == "DO_NOT_PARTITION"
    assert boundary["caller_metadata_trusted"] is False
    assert boundary["exact_resource_refusal_is_truth"] is False
    for key in (
        "binary_float_authority",
        "epsilon_or_tolerance_authority",
        "sampling_authority",
        "numerical_trigonometry_authority",
        "approximate_root_ordering_authority",
    ):
        assert boundary[key] is False

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "simple", "even-multiplicity", "nearby", "common a/b", "v41 residual",
        "defining polynomial", "isolating interval", "binary float",
        "resource refusal", "26-operation", "mc-b",
    ):
        assert token in controls, token

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDENT_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"] == "OPEN_PROPAGATED"
    for po in OPEN_POS:
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["domain_operation_count"] == 26
    assert effect["domain_narrowed"] is False
    assert "do not retry MC-B" in effect["next_pre_gate_priority"]

    assert artifact["resources"] == {
        "native_campaign_run": False,
        "paid_campaign_run": False,
        "production_authorized": False,
        "expensive_execution_authorized": False,
    }
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    for path, sha in EXPECTED_HISTORY.items():
        assert blob(ROOT / path) == sha, f"v41 historical evidence drift: {path}"

    assert len(load(DOMAIN)["coverage_rule"]["required_operation_ids"]) == 26
    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False

    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    for po in OPEN_POS:
        assert proofs[po]["state"] == "OPEN"

    for path in (DOC, REPORT):
        text = path.read_text(encoding="utf-8").lower()
        for token in (
            "pb-007-01", "open", "algebraic", "sturm", "multiplicity",
            "child", "endpoint", "not_established", "26", "mc-b",
        ):
            assert token in text, (path, token)

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_algebraic_orientation_cut_model.py",
        "test_pb00701_algebraic_orientation_cut_adversarial.py",
        "test_pb00701_algebraic_orientation_cut_authority.py",
        "verify_pb00701_v44.py --contract",
        "run_algebraic_roots()",
        "run_genuine_residual()",
        "run_precedence()",
        "run_authority_controls()",
        "verify_pb00701_v44.py --self-test",
    ):
        assert token in workflow, token


def self_test():
    adversarial.run()
    authority.run_authority_controls()
    artifact = load(ARTIFACT)
    validate_artifact(artifact, check_repo=True)

    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["MC-B"] = "ESTABLISHED"
    rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["implemented_boundary"]["caller_metadata_trusted"] = True
    rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["implemented_boundary"]["phase_endpoint_authority"] = "ESTABLISHED"
    rejected(lambda: validate_artifact(bad, check_repo=False))

    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0][1] = "0" * 40
    rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v44 algebraic orientation-cut verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v44 contract: PASS")
    if args.self_test:
        self_test()


if __name__ == "__main__":
    main()
