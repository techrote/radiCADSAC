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
DOC = ROOT / "docs" / "machining-completeness" / "67-PB00701-ORIENTATION-ROOT-PARTITION.md"
ARTIFACT = TASK / "pb00701-orientation-root-partition-v41.json"
REPORT = TASK / "pb00701-report-v41.md"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v41.yml"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
EXPECTED_BASE = "99abe3973d46af670693875e5a554239e89be283"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701_correlated_closed_handoff_model.py": "d47b8dd8fe8b4b91fd12c1e76974a5a4e85b03b2",
    "research/machining-completeness/tasks/MC-038/test_pb00701_correlated_closed_handoff_adversarial.py": "5128cc2ea69c2b567f57dc5578114bd6e9fd2faa",
    "research/machining-completeness/tasks/MC-038/pb00701-correlated-closed-handoff-v43.json": "095414925836ad23893eedcfe8b1c1e466fbccb1",
    "research/machining-completeness/tasks/MC-038/pb00701_phase_sector_partition_model.py": "6211e658621af7100c2509dcafdaeaf348e48d46",
}
OPEN_POS = {"PO-04", "PO-05", "PO-08"}

sys.path.insert(0, str(TASK))
import test_pb00701_orientation_root_partition_adversarial as adversarial  # noqa: E402


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
    raise AssertionError("expected adversarial mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-orientation-root-partition-boundary/41.2"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 245
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["required_predecessor"]["v43_merge"] == EXPECTED_BASE
    assert artifact["required_predecessor"]["pull_request"] == 251
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_V43_AWARE_ORIENTATION_ROOT_PARTITION_COMPOSITION_ESTABLISHED_PB00701_OPEN"

    pins = {entry["path"]: entry["git_blob_sha1"] for entry in artifact["historical_evidence"]}
    assert pins == EXPECTED_HISTORY

    ext = artifact["implemented_extension"]
    assert "through v43 first" in ext["precedence"]
    assert "complete v43 classifier" in ext["child_authority"]
    assert "does not make" in ext["zero_adjacent_contract"]
    assert "source identity" in ext["composition"]
    assert "blocked by complete v43" in ext["acceptance"]
    assert ext["caller_partition_trusted"] is False
    assert ext["caller_reparameterization_trusted"] is False
    assert ext["exact_resource_refusal_is_truth"] is False
    for key in (
        "binary_float_authority", "epsilon_or_tolerance_authority",
        "sampling_authority", "approximate_root_ordering_authority",
        "adaptive_refinement_authority",
    ):
        assert ext[key] is False

    controls = " ".join(artifact["boundary_controls"]).lower()
    for token in (
        "nearby", "even-multiplicity", "endpoint", "coincident", "v27",
        "irrational algebraic", "v43", "simple b", "zero-adjacent",
        "negative phase-rate", "source-parameter", "reparameterization",
        "physical internal root", "multiplicity mismatch", "resource refusal",
        "26-operation", "mc-b",
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
        assert blob(ROOT / path) == sha, f"verified v43 historical evidence drift: {path}"
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
            "pb-007-01", "remains open", "v43", "orientation", "sturm",
            "zero-adjacent", "source", "reparameterization", "resource",
            "26 operations", "mc-b",
        ):
            assert token in text, (path, token)

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_orientation_root_partition_model.py",
        "test_pb00701_orientation_root_partition_adversarial.py",
        "verify_pb00701_v41.py --contract",
        "t.run_roots()",
        "t.run_acceptance()",
        "t.run_precedence()",
        "t.run_composition()",
        "verify_pb00701_v41.py --self-test",
    ):
        assert token in workflow, token


def self_test():
    adversarial.run()
    artifact = load(ARTIFACT)
    validate_artifact(artifact, check_repo=True)

    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["MC-B"] = "ESTABLISHED"
    rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["implemented_extension"]["caller_partition_trusted"] = True
    rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["implemented_extension"]["child_authority"] = "trust caller children"
    rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_evidence"][0]["git_blob_sha1"] = "0" * 40
    rejected(lambda: validate_artifact(bad, check_repo=False))
    print("PB-007-01 v41 v43-aware orientation-root verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v41 v43-aware contract: PASS")
    if args.self_test:
        self_test()


if __name__ == "__main__":
    main()
