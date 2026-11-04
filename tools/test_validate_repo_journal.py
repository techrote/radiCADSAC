#!/usr/bin/env python3
"""Adversarial RCS-002 journal causal-lineage checks; no fixture edits."""
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import validate_repo as validator


def check(document: dict) -> list[str]:
    # add_error reports paths relative to the repository root. Keep the
    # temporary mutated fixture inside that root, never overwrite a source.
    with tempfile.TemporaryDirectory(prefix=".rcs002-lineage-", dir=validator.ROOT) as tmp:
        path = Path(tmp) / "journal.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        prior = validator.errors[:]
        try:
            validator.errors.clear()
            validator.validate_fixture(path)
            return validator.errors[:]
        finally:
            validator.errors[:] = prior


def assert_rejected(document: dict, expected: str) -> None:
    errors = check(document)
    assert any(expected in error for error in errors), (
        f"missing expected refusal {expected!r}; observed: {errors!r}"
    )


def main() -> None:
    fixture_dir = validator.ROOT / "research/rcs-002/fixtures"
    lathe = json.loads((fixture_dir / "lathe-finishing-pass-v1.json").read_text(encoding="utf-8"))
    mill = json.loads((fixture_dir / "mill-cut-through-v1.json").read_text(encoding="utf-8"))
    assert not check(lathe), "unchanged lathe journal must pass"
    assert not check(mill), "unchanged split-body mill journal must pass"

    # The previous validator checked that both references existed, but did
    # not compare them. All referenced revisions and body IDs still exist.
    wrong_op_parent = copy.deepcopy(lathe)
    wrong_op_parent["journal"]["operations"][2]["parent_revision_id"] = "rev:1"
    assert_rejected(wrong_op_parent, "parent disagrees with causing operation")

    wrong_revision_parent = copy.deepcopy(lathe)
    wrong_revision_parent["journal"]["revisions"][2]["parent_revision_id"] = "rev:0"
    assert_rejected(wrong_revision_parent, "parent disagrees with causing operation")

    # Forge BOTH pointers consistently. A naive parent-equality patch would
    # accept the circular rev:1 -> rev:3 -> rev:2 -> rev:1 graph.
    cycle = copy.deepcopy(lathe)
    cycle["journal"]["revisions"][1]["parent_revision_id"] = "rev:3"
    cycle["journal"]["operations"][0]["parent_revision_id"] = "rev:3"
    assert_rejected(cycle, "revision graph cycle detected")

    # A direct self-loop likewise must be rejected even with a matching
    # operation parent. Other operations/revisions remain unchanged.
    self_loop = copy.deepcopy(lathe)
    self_loop["journal"]["revisions"][2]["parent_revision_id"] = "rev:2"
    self_loop["journal"]["operations"][1]["parent_revision_id"] = "rev:2"
    assert_rejected(self_loop, "revision graph cycle detected")

    # A transition is allowed to be malformed input, not an excuse for an
    # unhandled KeyError or TypeError after the ordinary journal error.
    missing_parent = copy.deepcopy(mill)
    missing_parent["journal"]["operations"][1]["parent_revision_id"] = "rev:missing"
    assert_rejected(missing_parent, "references missing parent revision 'rev:missing'")

    invalid_parent_bodies = copy.deepcopy(mill)
    invalid_parent_bodies["journal"]["revisions"][1]["body_ids"] = None
    assert_rejected(invalid_parent_bodies, "parent revision has invalid body_ids")

    invalid_input = copy.deepcopy(mill)
    invalid_input["journal"]["material_body_transitions"][0]["input_body_ids"] = [["body:stock"]]
    assert_rejected(invalid_input, "has invalid/duplicate input body IDs")

    repeated_input = copy.deepcopy(mill)
    repeated_input["journal"]["material_body_transitions"][0]["input_body_ids"] = ["body:stock", "body:stock"]
    assert_rejected(repeated_input, "has invalid/duplicate input body IDs")

    invalid_output = copy.deepcopy(mill)
    invalid_output["journal"]["material_body_transitions"][0]["output_bodies"][0]["body_id"] = ["body:left"]
    assert_rejected(invalid_output, "has invalid/duplicate output bodies")

    invalid_committed_bodies = copy.deepcopy(mill)
    invalid_committed_bodies["journal"]["revisions"][2]["body_ids"] = None
    assert_rejected(invalid_committed_bodies, "committed revision has invalid body_ids")

    # Long legitimate immutable journals are normal engineering inputs.
    # This controls against introducing a recursive traversal limit.
    long_journal = copy.deepcopy(lathe)
    history = long_journal["journal"]
    setup = copy.deepcopy(history["operations"][0])
    history["operations"] = []
    history["revisions"] = [copy.deepcopy(history["revisions"][0])]
    for index in range(1, 1501):
        operation = copy.deepcopy(setup)
        operation["operation_id"] = f"op:long-{index}"
        operation["parent_revision_id"] = f"rev:{index - 1}"
        history["operations"].append(operation)
        history["revisions"].append({
            "revision_id": f"rev:{index}",
            "parent_revision_id": f"rev:{index - 1}",
            "caused_by_operation_id": f"op:long-{index}",
            "body_ids": ["body:stock"],
        })
    history["selected_head_revision_id"] = "rev:1500"
    long_journal["expected_journal_invariants"]["process_motion_count"] = 0
    assert not check(long_journal), "valid 1,500-revision history must pass without recursion errors"

    print("RCS-002 revision lineage: three accepted controls, ten adversarial refusals passed")


if __name__ == "__main__":
    main()
