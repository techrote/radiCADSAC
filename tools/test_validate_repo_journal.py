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

    print("RCS-002 revision lineage: two accepted controls, four adversarial refusals passed")


if __name__ == "__main__":
    main()
