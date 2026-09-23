#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-038"
DOC = ROOT / "docs" / "machining-completeness" / "67-PB00701-ORIENTATION-ROOT-PARTITION.md"
ARTIFACT = TASK / "pb00701-orientation-root-partition-v41.json"
REPORT = TASK / "pb00701-report-v41.md"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v41.yml"
EXPECTED_BASE = "ab9bc9e52a7db184f10bb6d4b7101cf0682a48d2"
EXPECTED_V42 = {
    "research/machining-completeness/tasks/MC-038/pb00701_orientation_transition_bridge_model.py": "a0930d7bfddd619bf930a51bbfa14570e2450fe5",
    "research/machining-completeness/tasks/MC-038/test_pb00701_orientation_transition_bridge_adversarial.py": "21e12227262229c095276d0fa6d6656ca49418a3",
    "research/machining-completeness/tasks/MC-038/pb00701-orientation-transition-v42.json": "e622d5b2f13bfe59d5e80310632d90d35b9d351a"
}

sys.path.insert(0, str(TASK))
import test_pb00701_orientation_root_partition_adversarial as adversarial  # noqa: E402


def _blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def contract():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["schema"] == "radicadsac-mc038-pb00701-orientation-root-partition-boundary/41.1"
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["required_predecessor"]["v42_merge"] == EXPECTED_BASE
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    ext = artifact["implemented_extension"]
    assert "through v42 first" in ext["precedence"]
    assert "complete v42 classifier" in ext["child_authority"]
    assert "does not make" in ext["zero_adjacent_contract"]
    assert "blocked by complete v42" in ext["acceptance"]
    assert ext["caller_partition_trusted"] is False
    assert ext["exact_resource_refusal_is_truth"] is False
    effect = artifact["programme_effect"]
    assert effect["domain_operation_count"] == 26
    assert effect["MC-B"] == effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["PB-007-01"] == "OPEN"

    for path, sha in EXPECTED_V42.items():
        assert _blob(ROOT / path) == sha, f"verified v42 predecessor drift: {path}"

    for path in (DOC, REPORT):
        text = path.read_text(encoding="utf-8")
        for token in ("PB-007-01", "NOT_ESTABLISHED", "26", "v42", "zero-adjacent"):
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
    ):
        assert token in workflow, token


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("PB-007-01 v41 v42-aware contract: PASS")
    if args.self_test:
        adversarial.run()
    if not args.contract and not args.self_test:
        parser.error("choose --contract or --self-test")


if __name__ == "__main__":
    main()
