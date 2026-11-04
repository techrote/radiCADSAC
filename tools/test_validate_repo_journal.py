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

    # JSON permits arrays and objects where an ID or enum string belongs.
    # These previously raised TypeError on dict/set membership, sometimes
    # after an unrelated error had already been recorded. Every case below
    # must instead return a structured, field-specific refusal.
    assert_rejected(["not a fixture object"], "fixture root must be an object")
    malformed_reference_cases = [
        (lathe, ("journal", "root_revision_id"), ["rev:0"], "root_revision_id does not resolve"),
        (lathe, ("journal", "selected_head_revision_id"), {"revision": "rev:3"}, "selected_head_revision_id does not resolve"),
        (lathe, ("journal", "revisions", 1, "parent_revision_id"), ["rev:0"], "references missing parent"),
        (lathe, ("journal", "revisions", 1, "caused_by_operation_id"), {"op": "op:setup-1"}, "references missing operation"),
        (lathe, ("journal", "operations", 0, "parent_revision_id"), ["rev:0"], "references missing parent revision"),
        (lathe, ("journal", "operations", 0, "kind"), ["setup_change"], "unsupported core kind"),
        (lathe, ("journal", "operations", 0, "setup_ref"), ["setup:lathe-1@1"], "references missing setup"),
        (lathe, ("journal", "operations", 1, "tool_ref"), {"tool": "tool:turning-od@1"}, "references missing tool"),
        (lathe, ("journal", "operations", 1, "normalization_policy_ref"), ["policy"], "references missing normalization policy"),
        (lathe, ("journal", "operations", 1, "trajectory", "frame_ref"), ["frame:workpiece@1"], "trajectory references missing frame"),
        (lathe, ("journal", "operations", 1, "trajectory", "sections", 0, "engagement"), ["neutral"], "unsupported engagement"),
        (lathe, ("journal", "definitions", "stocks", 0, "frame_ref"), ["frame:workpiece@1"], "stock references missing frame"),
        (lathe, ("journal", "definitions", "setups", 0, "workpiece_frame_ref"), ["frame:workpiece@1"], "setup references missing frame"),
        (lathe, ("journal", "definitions", "tools", 0, "tool_frame_ref"), ["frame:tool-tip@1"], "tool references missing frame"),
        (mill, ("journal", "material_body_transitions", 0, "caused_by_operation_id"), ["op:cut-through"], "missing operation/revision reference"),
        (mill, ("journal", "material_body_transitions", 0, "committed_revision_id"), {"rev": "rev:2"}, "missing operation/revision reference"),
        (mill, ("journal", "material_body_transitions", 0, "kind"), ["split"], "unsupported kind"),
        (lathe, ("journal", "definitions", "stocks"), {"stock": "invalid"}, "definitions.stocks must be a list"),
        (lathe, ("journal", "definitions", "setups"), {"setup": "invalid"}, "definitions.setups must be a list"),
        (lathe, ("journal", "definitions", "tools"), {"tool": "invalid"}, "definitions.tools must be a list"),
        (lathe, ("journal", "definitions", "stocks"), [None], "definitions.stocks contains non-object"),
        (lathe, ("journal", "definitions", "tools"), [None], "definitions.tools contains non-object"),
    ]
    for original, access_path, malformed, expected_error in malformed_reference_cases:
        mutated = copy.deepcopy(original)
        target = mutated
        for key in access_path[:-1]:
            target = target[key]
        target[access_path[-1]] = malformed
        assert_rejected(mutated, expected_error)

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

    # Frame ancestry must be fail-closed for malformed parent IDs rather
    # than raising TypeError for an unhashable JSON list.
    invalid_frame_parent = copy.deepcopy(lathe)
    invalid_frame_parent["journal"]["definitions"]["frames"][1]["parent_frame_id"] = ["frame:workpiece"]
    assert_rejected(invalid_frame_parent, "has invalid parent_frame_id")

    # The same frame cycle must be rejected without recursive DFS.
    cyclic_frames = copy.deepcopy(lathe)
    cyclic_frames["journal"]["definitions"]["frames"][1]["parent_frame_id"] = "frame:tool-tip"
    assert_rejected(cyclic_frames, "frame graph cycle detected")

    # A valid 1,500-level frame chain is legitimate independent of the
    # revision count and must not depend on Python's recursion limit.
    long_frames = copy.deepcopy(lathe)
    frames = long_frames["journal"]["definitions"]["frames"]
    template = frames[1]
    prior_frame = "frame:tool-tip"
    for index in range(1, 1501):
        frame = copy.deepcopy(template)
        frame["frame_id"] = f"frame:deep-{index}"
        frame["parent_frame_id"] = prior_frame
        frames.append(frame)
        prior_frame = frame["frame_id"]
    assert not check(long_frames), "valid 1,500-frame hierarchy must pass without recursion errors"

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

    print(
        "RCS-002 revision lineage: four accepted controls, twelve prior and "
        f"{len(malformed_reference_cases) + 1} malformed-type refusals passed"
    )


if __name__ == "__main__":
    main()
