#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-038"
DOC = ROOT / "docs" / "machining-completeness" / "67-PB00701-ORIENTATION-ROOT-PARTITION.md"
ARTIFACT = TASK / "pb00701-orientation-root-partition-v41.json"
REPORT = TASK / "pb00701-report-v41.md"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v41.yml"
EXPECTED_BASE = "494a29091fcd9afadad006cded4a71b74349c824"
sys.path.insert(0, str(TASK))
import test_pb00701_orientation_root_partition_adversarial as adversarial  # noqa: E402


def contract():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["schema"] == "radicadsac-mc038-pb00701-orientation-root-partition-boundary/41.0"
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["gate_state"] == "NOT_ESTABLISHED"
    assert artifact["programme_effect"]["domain_operation_count"] == 26
    assert artifact["programme_effect"]["MC-B"] == "NOT_ESTABLISHED"
    assert artifact["programme_effect"]["PB-007-01"] == "OPEN"
    assert artifact["implemented_extension"]["caller_partition_trusted"] is False
    assert artifact["implemented_extension"]["exact_resource_refusal_is_truth"] is False
    for path in (DOC, REPORT):
        text = path.read_text(encoding="utf-8")
        for token in ("PB-007-01", "NOT_ESTABLISHED", "26"):
            assert token in text, (path, token)
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_orientation_root_partition_model.py",
        "test_pb00701_orientation_root_partition_adversarial.py",
        "verify_pb00701_v41.py --contract",
        "verify_pb00701_v41.py --self-test",
    ):
        assert token in workflow, token


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
    if args.self_test:
        adversarial.run()
    if not args.contract and not args.self_test:
        parser.error("choose --contract or --self-test")


if __name__ == "__main__":
    main()
