#!/usr/bin/env python3
"""Run the RCS-008 provenance/semantic-identity research campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = ROOT / "research/rcs-008/experiment-plan-v1.json"
EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"


def canonical_id(kind: str, semantic_key: dict[str, Any]) -> str:
    payload = json.dumps(
        {"kind": kind, "semantic_key": semantic_key},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return f"{kind}:{hashlib.sha256(payload).hexdigest()[:24]}"


def run_worker(worker: Path, mode: str, timeout_s: float) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [str(worker), "--mode", mode],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "mode": mode,
            "exit_code": None,
            "stderr": (exc.stderr or "") if isinstance(exc.stderr, str) else "",
        }

    record: dict[str, Any] = {
        "mode": mode,
        "exit_code": completed.returncode,
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        record["status"] = "worker_error"
        record["stdout"] = completed.stdout.strip()
        return record
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        record["status"] = "protocol_error"
        record["stdout"] = completed.stdout.strip()
        record["error"] = str(exc)
        return record
    record["status"] = "measured"
    record["payload"] = payload
    return record


def relation(relation_type: str, parents: list[str], children: list[str], evidence: str, **extra: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "relation_type": relation_type,
        "parents": parents,
        "children": children,
        "evidence": evidence,
    }
    value.update(extra)
    return value


def build_semantic_model(worker_records: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode = {item["mode"]: item for item in worker_records if item.get("status") == "measured"}

    stock = canonical_id("material_body", {"workpiece": "fixture", "revision": "stock", "body_role": "stock"})
    split_op = canonical_id("operation", {"journal_operation": "split_material", "ordinal": 1})
    left = canonical_id("material_body", {"parent": stock, "operation": split_op, "branch_role": "negative_x"})
    right = canonical_id("material_body", {"parent": stock, "operation": split_op, "branch_role": "positive_x"})

    mill_stock = canonical_id("material_body", {"workpiece": "mill_fixture", "revision": "stock", "body_role": "retained"})
    mill_op1 = canonical_id("operation", {"journal_operation": "overlapping_slot", "ordinal": 1})
    mill_op2 = canonical_id("operation", {"journal_operation": "overlapping_slot", "ordinal": 2})
    boundary_1 = canonical_id("material_boundary_role", {"body": mill_stock, "operation": mill_op1, "role": "slot_floor"})
    boundary_2 = canonical_id("material_boundary_role", {"body": mill_stock, "operation": mill_op2, "role": "overlap_reconciled_floor"})

    merge_op = canonical_id("reconciliation_event", {"kind": "same_domain_unification", "fixture": "adjacent_boxes"})
    merge_parent_a = canonical_id("material_boundary_role", {"fixture": "adjacent_boxes", "source": "left_top"})
    merge_parent_b = canonical_id("material_boundary_role", {"fixture": "adjacent_boxes", "source": "right_top"})
    merge_child = canonical_id("material_boundary_role", {"fixture": "adjacent_boxes", "reconciliation": merge_op, "role": "unified_top"})

    retrace_envelope = canonical_id(
        "tool_envelope",
        {
            "process": "lathe_od_finish",
            "target_radius_nm": 19_999_000,
            "z_start_nm": 0,
            "z_end_nm": 60_000_000,
            "tool_revision": "tool:od-finish:v1",
            "setup_revision": "setup:lathe:v1",
        },
    )
    retrace_body = canonical_id("material_body", {"workpiece": "lathe_fixture", "body_role": "retained"})
    retrace_proof = {
        "proof_schema": "rcs-008-retrace-proof/1.0",
        "target_material_body": retrace_body,
        "setup_revision": "setup:lathe:v1",
        "tool_revision": "tool:od-finish:v1",
        "material_removal_envelope": retrace_envelope,
        "canonical_operation_semantics_equal": True,
        "intervening_intersecting_material_mutation": False,
        "journal_event_preserved": True,
        "geometry_recompute_elision_candidate": bool(
            by_mode.get("repeated_finish", {}).get("payload", {}).get("engineering_equivalent", False)
        ),
        "note": "Eligibility is semantic/provenance based; measured geometry equivalence corroborates but does not define identity.",
    }

    ambiguous_parent = canonical_id("material_boundary_role", {"fixture": "symmetric_split", "role": "undifferentiated_parent"})
    ambiguous_a = canonical_id("material_boundary_role", {"fixture": "symmetric_split", "candidate": "A"})
    ambiguous_b = canonical_id("material_boundary_role", {"fixture": "symmetric_split", "candidate": "B"})

    events = [
        relation("split", [stock, split_op], [left, right], "split_cut worker + journal operation semantics"),
        relation("replaced", [boundary_1, mill_op2], [boundary_2], "overlap_cuts worker + operation order"),
        relation("merged", [merge_parent_a, merge_parent_b, merge_op], [merge_child], "same_domain_merge worker + reconciliation semantics"),
        relation(
            "ambiguous",
            [ambiguous_parent],
            [ambiguous_a, ambiguous_b],
            "symmetric fixture has no manufacturing-semantic discriminator",
            resolution="unresolved",
            forbidden_action="choose a descendant by transient backend order/address",
        ),
    ]

    return {
        "model_schema": "rcs-008-semantic-lineage/1.0",
        "identity_rule": "Durable identity names manufacturing semantics/events; concrete backend topology is a derived attachment and may be replaced.",
        "stable_across_replay": [
            "canonical journal operation identity",
            "material-body lineage identity",
            "immutable setup/tool definition revisions",
            "semantic boundary roles when uniquely justified",
            "lineage relation/event identity",
        ],
        "not_stable_by_contract": [
            "OCCT TopoDS object identity",
            "face/edge enumeration order",
            "kernel object address/handle",
            "topology entity identity after genuine split/merge/replacement",
        ],
        "events": events,
        "retrace_proof": retrace_proof,
        "ambiguity_policy": {
            "case": "symmetric_ambiguous_split",
            "result": "ambiguous",
            "candidate_count": 2,
            "arbitrary_numeric_topology_name_forbidden": True,
        },
    }


def markdown_summary(results: dict[str, Any]) -> str:
    summary = results["summary"]
    lines = [
        "# RCS-008 provenance smoke summary",
        "",
        f"- Worker cases: {summary['worker_cases']}",
        f"- Worker failures: {summary['worker_failures']}",
        f"- Independent replay engineering-equivalent: {summary['replay_engineering_equivalent']}",
        f"- Independent replay `IsSame` face matches: {summary['replay_same_face_identity_matches']}",
        f"- Split result solids: {summary['split_result_solids']}",
        f"- Split one-to-many source faces: {summary['split_one_to_many_source_faces']}",
        f"- Overlap-cut modified/generated face relations: {summary['overlap_face_relations']}",
        f"- Same-domain faces before/after: {summary['same_domain_faces_before']} → {summary['same_domain_faces_after']}",
        f"- Same-domain many-to-one descendants reported: {summary['same_domain_many_to_one_descendants']}",
        f"- Repeated finishing engineering-equivalent: {summary['repeated_finish_engineering_equivalent']}",
        f"- Explicit ambiguous semantic cases: {summary['explicit_ambiguous_cases']}",
        f"- Retrace semantic proof candidate: {summary['retrace_proof_candidate']}",
        "",
        "The campaign treats OCCT history as operation-local evidence. Programme identity is the separate semantic-lineage graph in `results.json`; no OCCT object ID is promoted to durable identity.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--profile", choices=("smoke", "baseline"), default="smoke")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args()

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    selected_ids = set(plan["profiles"][args.profile]["worker_cases"])
    worker_cases = [item for item in plan["worker_cases"] if item["id"] in selected_ids]

    records: list[dict[str, Any]] = []
    for case in worker_cases:
        record = run_worker(args.worker.resolve(), case["mode"], args.timeout_seconds)
        record["case_id"] = case["id"]
        record["purpose"] = case["purpose"]
        records.append(record)

    semantic_model = build_semantic_model(records)
    by_mode = {item["mode"]: item for item in records if item.get("status") == "measured"}

    replay = by_mode.get("replay_cut", {}).get("payload", {})
    split = by_mode.get("split_cut", {}).get("payload", {})
    overlap = by_mode.get("overlap_cuts", {}).get("payload", {})
    merge = by_mode.get("same_domain_merge", {}).get("payload", {})
    repeated = by_mode.get("repeated_finish", {}).get("payload", {})

    split_history = split.get("history", {})
    overlap_history = overlap.get("history", {})
    merge_history = merge.get("history", {})

    summary = {
        "worker_cases": len(records),
        "worker_failures": sum(item.get("status") != "measured" for item in records),
        "replay_engineering_equivalent": replay.get("engineering_equivalent"),
        "replay_same_face_identity_matches": replay.get("same_face_identity_matches"),
        "split_result_solids": split.get("result", {}).get("solids"),
        "split_one_to_many_source_faces": split_history.get("one_to_many_source_faces"),
        "overlap_face_relations": int(overlap_history.get("modified_face_relations", 0) or 0)
        + int(overlap_history.get("generated_face_relations", 0) or 0),
        "same_domain_faces_before": merge.get("before_unify", {}).get("faces"),
        "same_domain_faces_after": merge.get("after_unify", {}).get("faces"),
        "same_domain_many_to_one_descendants": merge_history.get("many_to_one_descendants"),
        "repeated_finish_engineering_equivalent": repeated.get("engineering_equivalent"),
        "repeated_finish_same_face_identity_matches": repeated.get("same_face_identity_matches"),
        "explicit_ambiguous_cases": 1,
        "retrace_proof_candidate": semantic_model["retrace_proof"]["geometry_recompute_elision_candidate"],
    }

    results = {
        "results_schema": "rcs-008-results/1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "backend": {
            "id": "occt",
            "version": "8.0.1",
            "tag": "V8_0_1",
            "commit": EXPECTED_COMMIT,
        },
        "worker_records": records,
        "semantic_lineage": semantic_model,
        "summary": summary,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out_dir / "summary.md").write_text(markdown_summary(results), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))

    return 3 if summary["worker_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
