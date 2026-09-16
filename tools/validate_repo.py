#!/usr/bin/env python3
"""Lightweight deterministic validation for the radiCADSAC genesis repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "docs/00-FOUNDING-BRIEF.md",
    "docs/01-MSAC-GEOMETRY-CONTRACT.md",
    "docs/04-REVISED-RESEARCH-ROADMAP.md",
    "docs/05-SOURCE-BASELINE.md",
    "docs/06-RESEARCH-METHOD.md",
    "docs/07-RESEARCH-ISSUE-GRAPH.md",
    "docs/08-TERMINOLOGY.md",
    "docs/09-FOUNDATION-AUDIT.md",
    "docs/10-CANONICAL-JOURNAL-CONTRACT.md",
    "docs/decisions/DR-0001-step-is-primary-output.md",
    "docs/decisions/DR-0002-journal-is-durable-intent.md",
    "docs/decisions/DR-0003-initial-scope-lathe-mill.md",
    "docs/decisions/DR-0004-stable-backend-boundary.md",
    "docs/decisions/DR-0005-pathological-geometry-is-normal-input.md",
    "docs/decisions/DR-0006-canonical-journal-numerics-and-frames.md",
    "docs/decisions/DR-0007-bounded-deterministic-canonicalization.md",
    "docs/decisions/DR-0008-immutable-revisions-and-body-transitions.md",
    "research/rcs-002/README.md",
    "research/rcs-002/fixtures/lathe-finishing-pass-v1.json",
    "research/rcs-002/fixtures/mill-cut-through-v1.json",
]

RCS002_FIXTURES = [
    ROOT / "research/rcs-002/fixtures/lathe-finishing-pass-v1.json",
    ROOT / "research/rcs-002/fixtures/mill-cut-through-v1.json",
]

DECISION_REQUIRED_HEADINGS = (
    "## Context",
    "## Decision",
    "## Alternatives considered",
    "## Evidence",
    "## Consequences",
    "## Reversibility",
)

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1
Q15_SCALE = 10**15
NUMERIC_KEY_SUFFIXES = (
    "_nm",
    "_nrad",
    "_ns",
    "_nm_s",
    "_nrad_s",
)

errors: list[str] = []


def add_error(path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def is_int64(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and INT64_MIN <= value <= INT64_MAX


def validate_int64_tree(path: Path, node: Any, key: str = "") -> None:
    if isinstance(node, dict):
        for child_key, child in node.items():
            validate_int64_tree(path, child, child_key)
        return
    if isinstance(node, list):
        if key.endswith(NUMERIC_KEY_SUFFIXES):
            for value in node:
                if not is_int64(value):
                    add_error(path, f"{key} contains non-int64 value {value!r}")
        else:
            for child in node:
                validate_int64_tree(path, child, key)
        return
    if key.endswith(NUMERIC_KEY_SUFFIXES) and not is_int64(node):
        add_error(path, f"{key} is not a signed int64: {node!r}")


def validate_quaternion(path: Path, value: Any, where: str) -> None:
    if not isinstance(value, list) or len(value) != 4 or not all(is_int64(v) for v in value):
        add_error(path, f"{where} must contain four signed int64 q15 components")
        return
    if value == [0, 0, 0, 0]:
        add_error(path, f"{where} must not be the zero quaternion")
        return
    first_nonzero = next(v for v in value if v != 0)
    if first_nonzero < 0:
        add_error(path, f"{where} violates canonical quaternion sign rule")
    norm2 = sum(v * v for v in value)
    # Fixture encodings should be very close to unit length before semantic normalization.
    if abs(norm2 - Q15_SCALE * Q15_SCALE) > Q15_SCALE * 1_000_000_000:
        add_error(path, f"{where} is too far from unit length for q15 encoding")


def validate_xyz(path: Path, value: Any, where: str) -> None:
    if not isinstance(value, list) or len(value) != 3 or not all(is_int64(v) for v in value):
        add_error(path, f"{where} must contain three signed int64 coordinates")


def validate_fixture(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add_error(path, f"cannot parse JSON: {exc}")
        return

    if data.get("fixture_schema") != "rcs-002-journal-fixture/1.0":
        add_error(path, "unexpected fixture_schema")

    journal = data.get("journal")
    if not isinstance(journal, dict):
        add_error(path, "missing journal object")
        return

    schema = journal.get("journal_schema")
    if schema != {"id": "msac-journal", "major": 1, "minor": 0}:
        add_error(path, "journal_schema must be msac-journal/1.0")
    if journal.get("numeric_convention") != "nm-nrad-ns-q15-v1":
        add_error(path, "unexpected numeric_convention")

    validate_int64_tree(path, journal)

    definitions = journal.get("definitions")
    if not isinstance(definitions, dict):
        add_error(path, "missing definitions object")
        return

    frames = definitions.get("frames", [])
    if not isinstance(frames, list) or not frames:
        add_error(path, "definitions.frames must be a non-empty list")
        return

    frame_by_id: dict[str, dict[str, Any]] = {}
    frame_refs: set[str] = set()
    for frame in frames:
        if not isinstance(frame, dict):
            add_error(path, "frame entry is not an object")
            continue
        frame_id = frame.get("frame_id")
        revision = frame.get("revision")
        if not isinstance(frame_id, str) or not isinstance(revision, str):
            add_error(path, "frame must have string frame_id and revision")
            continue
        if frame_id in frame_by_id:
            add_error(path, f"duplicate frame_id {frame_id}")
        frame_by_id[frame_id] = frame
        frame_refs.add(f"{frame_id}@{revision}")
        parent = frame.get("parent_frame_id")
        transform = frame.get("transform_parent_from_child")
        if parent is None:
            if transform is not None:
                add_error(path, f"root frame {frame_id} must have null transform")
        else:
            if not isinstance(transform, dict):
                add_error(path, f"non-root frame {frame_id} must define transform")
            else:
                validate_xyz(path, transform.get("translation_nm"), f"{frame_id}.translation_nm")
                validate_quaternion(
                    path,
                    transform.get("rotation_q15_wxyz"),
                    f"{frame_id}.rotation_q15_wxyz",
                )

    for frame_id, frame in frame_by_id.items():
        parent = frame.get("parent_frame_id")
        if parent is not None and parent not in frame_by_id:
            add_error(path, f"frame {frame_id} references missing parent {parent}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit_frame(frame_id: str) -> None:
        if frame_id in visited:
            return
        if frame_id in visiting:
            add_error(path, f"frame graph cycle detected at {frame_id}")
            return
        visiting.add(frame_id)
        parent = frame_by_id[frame_id].get("parent_frame_id")
        if isinstance(parent, str) and parent in frame_by_id:
            visit_frame(parent)
        visiting.remove(frame_id)
        visited.add(frame_id)

    for frame_id in frame_by_id:
        visit_frame(frame_id)

    def build_refs(collection: str, id_key: str) -> set[str]:
        refs: set[str] = set()
        items = definitions.get(collection, [])
        if not isinstance(items, list):
            add_error(path, f"definitions.{collection} must be a list")
            return refs
        for item in items:
            if not isinstance(item, dict):
                add_error(path, f"definitions.{collection} contains non-object")
                continue
            item_id = item.get(id_key)
            revision = item.get("revision")
            if not isinstance(item_id, str) or not isinstance(revision, str):
                add_error(path, f"definitions.{collection} entry lacks string ID/revision")
                continue
            ref = f"{item_id}@{revision}"
            if ref in refs:
                add_error(path, f"duplicate definition ref {ref}")
            refs.add(ref)
        return refs

    setup_refs = build_refs("setups", "setup_id")
    tool_refs = build_refs("tools", "tool_id")
    policy_refs = build_refs("normalization_policies", "policy_id")

    for stock in definitions.get("stocks", []):
        if isinstance(stock, dict):
            frame_ref = stock.get("frame_ref")
            if frame_ref not in frame_refs:
                add_error(path, f"stock references missing frame {frame_ref!r}")

    for setup in definitions.get("setups", []):
        if isinstance(setup, dict):
            for field in ("workpiece_frame_ref", "machine_frame_ref"):
                if setup.get(field) not in frame_refs:
                    add_error(path, f"setup references missing frame {setup.get(field)!r}")

    for tool in definitions.get("tools", []):
        if isinstance(tool, dict) and tool.get("tool_frame_ref") not in frame_refs:
            add_error(path, f"tool references missing frame {tool.get('tool_frame_ref')!r}")

    operations = journal.get("operations", [])
    revisions = journal.get("revisions", [])
    transitions = journal.get("material_body_transitions", [])
    if not isinstance(operations, list) or not isinstance(revisions, list) or not isinstance(transitions, list):
        add_error(path, "operations/revisions/material_body_transitions must be lists")
        return

    operation_by_id: dict[str, dict[str, Any]] = {}
    for op in operations:
        if not isinstance(op, dict):
            add_error(path, "operation entry is not an object")
            continue
        op_id = op.get("operation_id")
        if not isinstance(op_id, str):
            add_error(path, "operation missing string operation_id")
            continue
        if op_id in operation_by_id:
            add_error(path, f"duplicate operation_id {op_id}")
        operation_by_id[op_id] = op
        if op.get("kind") not in {"setup_change", "process_motion"}:
            add_error(path, f"operation {op_id} has unsupported core kind {op.get('kind')!r}")

    revision_by_id: dict[str, dict[str, Any]] = {}
    for revision in revisions:
        if not isinstance(revision, dict):
            add_error(path, "revision entry is not an object")
            continue
        revision_id = revision.get("revision_id")
        if not isinstance(revision_id, str):
            add_error(path, "revision missing string revision_id")
            continue
        if revision_id in revision_by_id:
            add_error(path, f"duplicate revision_id {revision_id}")
        revision_by_id[revision_id] = revision
        body_ids = revision.get("body_ids")
        if not isinstance(body_ids, list) or not body_ids or not all(isinstance(v, str) for v in body_ids):
            add_error(path, f"revision {revision_id} must have non-empty string body_ids")
        elif len(body_ids) != len(set(body_ids)):
            add_error(path, f"revision {revision_id} contains duplicate body_ids")

    root_revision_id = journal.get("root_revision_id")
    head_revision_id = journal.get("selected_head_revision_id")
    if root_revision_id not in revision_by_id:
        add_error(path, "root_revision_id does not resolve")
    if head_revision_id not in revision_by_id:
        add_error(path, "selected_head_revision_id does not resolve")

    caused_ops: set[str] = set()
    for revision_id, revision in revision_by_id.items():
        parent = revision.get("parent_revision_id")
        caused = revision.get("caused_by_operation_id")
        if revision_id == root_revision_id:
            if parent is not None or caused is not None:
                add_error(path, "root revision must have null parent and cause")
        else:
            if parent not in revision_by_id:
                add_error(path, f"revision {revision_id} references missing parent {parent!r}")
            if caused not in operation_by_id:
                add_error(path, f"revision {revision_id} references missing operation {caused!r}")
            elif caused in caused_ops:
                add_error(path, f"operation {caused} causes more than one revision")
            else:
                caused_ops.add(caused)

    if set(operation_by_id) != caused_ops:
        missing = sorted(set(operation_by_id) - caused_ops)
        if missing:
            add_error(path, f"operations without resulting revision: {missing}")

    for op_id, op in operation_by_id.items():
        parent_id = op.get("parent_revision_id")
        if parent_id not in revision_by_id:
            add_error(path, f"operation {op_id} references missing parent revision {parent_id!r}")
            continue
        parent_bodies = set(revision_by_id[parent_id].get("body_ids", []))
        targets = op.get("target_body_ids", [])
        if not isinstance(targets, list) or not all(isinstance(v, str) for v in targets):
            add_error(path, f"operation {op_id} target_body_ids must be strings")
        elif not set(targets).issubset(parent_bodies):
            add_error(path, f"operation {op_id} targets body not present in parent revision")

        if op.get("setup_ref") not in setup_refs:
            add_error(path, f"operation {op_id} references missing setup {op.get('setup_ref')!r}")

        if op.get("kind") != "process_motion":
            continue
        if op.get("tool_ref") not in tool_refs:
            add_error(path, f"operation {op_id} references missing tool {op.get('tool_ref')!r}")
        if op.get("normalization_policy_ref") not in policy_refs:
            add_error(path, f"operation {op_id} references missing normalization policy")

        trajectory = op.get("trajectory")
        if not isinstance(trajectory, dict):
            add_error(path, f"operation {op_id} missing trajectory")
            continue
        if trajectory.get("frame_ref") not in frame_refs:
            add_error(path, f"operation {op_id} trajectory references missing frame")
        validate_quaternion(
            path,
            trajectory.get("orientation_q15_wxyz"),
            f"{op_id}.trajectory.orientation_q15_wxyz",
        )

        bounds = trajectory.get("guaranteed_bounds")
        required_bounds = (
            "max_translation_error_nm",
            "max_orientation_error_nrad",
            "max_event_time_shift_ns",
        )
        if not isinstance(bounds, dict):
            add_error(path, f"operation {op_id} missing guaranteed_bounds")
        else:
            for bound in required_bounds:
                value = bounds.get(bound)
                if not is_int64(value) or value < 0:
                    add_error(path, f"operation {op_id} has invalid bound {bound}")

        sections = trajectory.get("sections")
        if not isinstance(sections, list) or not sections:
            add_error(path, f"operation {op_id} trajectory must have sections")
            continue
        previous_end: int | None = None
        section_ids: set[str] = set()
        for section in sections:
            if not isinstance(section, dict):
                add_error(path, f"operation {op_id} contains non-object section")
                continue
            section_id = section.get("section_id")
            if not isinstance(section_id, str) or section_id in section_ids:
                add_error(path, f"operation {op_id} has missing/duplicate section_id")
            else:
                section_ids.add(section_id)
            if section.get("engagement") not in {"neutral", "remove", "add", "probe"}:
                add_error(path, f"operation {op_id} has unsupported engagement")
            start = section.get("start_time_ns")
            end = section.get("end_time_ns")
            if not is_int64(start) or not is_int64(end) or start < 0 or end <= start:
                add_error(path, f"operation {op_id} has invalid section time interval")
            elif previous_end is not None and start < previous_end:
                add_error(path, f"operation {op_id} sections are not time ordered")
            if is_int64(end):
                previous_end = end
            curve = section.get("curve")
            if not isinstance(curve, dict):
                add_error(path, f"operation {op_id} section missing curve")
                continue
            if curve.get("kind") != "line":
                add_error(path, f"fixture validator currently expects line curves, got {curve.get('kind')!r}")
            validate_xyz(path, curve.get("start_nm"), f"{op_id}.{section_id}.start_nm")
            validate_xyz(path, curve.get("end_nm"), f"{op_id}.{section_id}.end_nm")

    transition_by_id: dict[str, dict[str, Any]] = {}
    for transition in transitions:
        if not isinstance(transition, dict):
            add_error(path, "material_body_transition entry is not an object")
            continue
        transition_id = transition.get("transition_id")
        if not isinstance(transition_id, str) or transition_id in transition_by_id:
            add_error(path, "material_body_transition has missing/duplicate transition_id")
            continue
        transition_by_id[transition_id] = transition
        op_id = transition.get("caused_by_operation_id")
        revision_id = transition.get("committed_revision_id")
        if op_id not in operation_by_id or revision_id not in revision_by_id:
            add_error(path, f"transition {transition_id} has missing operation/revision reference")
            continue
        if transition.get("kind") not in {"split", "merge", "replace", "classification_only"}:
            add_error(path, f"transition {transition_id} has unsupported kind")
        input_bodies = transition.get("input_body_ids")
        output_bodies = transition.get("output_bodies")
        if not isinstance(input_bodies, list) or not input_bodies:
            add_error(path, f"transition {transition_id} needs input_body_ids")
            continue
        if not isinstance(output_bodies, list) or not output_bodies:
            add_error(path, f"transition {transition_id} needs output_bodies")
            continue
        parent_id = operation_by_id[op_id].get("parent_revision_id")
        parent_body_ids = set(revision_by_id[parent_id].get("body_ids", []))
        if not set(input_bodies).issubset(parent_body_ids):
            add_error(path, f"transition {transition_id} input body not present in parent")
        output_ids = [item.get("body_id") for item in output_bodies if isinstance(item, dict)]
        if len(output_ids) != len(output_bodies) or len(output_ids) != len(set(output_ids)):
            add_error(path, f"transition {transition_id} has invalid/duplicate output bodies")
        if set(output_ids) != set(revision_by_id[revision_id].get("body_ids", [])):
            add_error(path, f"transition {transition_id} outputs do not match committed revision")
        if revision_by_id[revision_id].get("caused_by_operation_id") != op_id:
            add_error(path, f"transition {transition_id} revision cause does not match operation")

    expected = data.get("expected_journal_invariants", {})
    if isinstance(expected, dict) and "process_motion_count" in expected:
        actual = sum(1 for op in operations if isinstance(op, dict) and op.get("kind") == "process_motion")
        if expected["process_motion_count"] != actual:
            add_error(path, "process_motion_count expectation does not match fixture")
    if isinstance(expected, dict) and "body_count_at_head" in expected and head_revision_id in revision_by_id:
        actual = len(revision_by_id[head_revision_id].get("body_ids", []))
        if expected["body_count_at_head"] != actual:
            add_error(path, "body_count_at_head expectation does not match fixture")


for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        errors.append(f"missing required file: {rel}")

markdown_files = sorted(ROOT.rglob("*.md"))
if not markdown_files:
    errors.append("repository contains no Markdown research corpus")

local_link = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)")

for path in markdown_files:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    if "\t" in text:
        errors.append(f"{rel}: contains tab characters")
    for lineno, line in enumerate(text.splitlines(), 1):
        trailing_spaces = len(line) - len(line.rstrip(" "))
        # Two trailing spaces are the standard Markdown hard-line-break syntax.
        if trailing_spaces not in (0, 2):
            errors.append(
                f"{rel}:{lineno}: accidental trailing whitespace "
                f"({trailing_spaces} spaces)"
            )
    for match in local_link.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("plugin://", "sandbox:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{rel}: local link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{rel}: broken local link: {target}")

for path in sorted((ROOT / "docs" / "decisions").glob("*.md")):
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    if "Status:" not in text:
        errors.append(f"{rel}: decision record has no Status field")
    for heading in DECISION_REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{rel}: decision record missing heading {heading!r}")

for fixture in RCS002_FIXTURES:
    if fixture.is_file():
        validate_fixture(fixture)

if errors:
    print("radiCADSAC validation failed:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print(
    f"radiCADSAC validation passed ({len(markdown_files)} Markdown files checked, "
    f"{len(RCS002_FIXTURES)} RCS-002 fixtures validated)"
)
