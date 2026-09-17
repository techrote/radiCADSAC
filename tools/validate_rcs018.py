#!/usr/bin/env python3
"""Validate RCS-018 semantic vertical-slice artifacts and adversarial guards."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research/rcs-018/vertical_slice.py"
WORKER = ROOT / "research/rcs-018/worker_probe.py"

REQUIRED = (
    ROOT / "docs/26-INTEGRATED-SEMANTIC-CONTRACT-VERTICAL-SLICE.md",
    ROOT / "research/rcs-018/README.md",
    ROOT / "research/rcs-018/experiment-plan-v1.json",
    ROOT / "research/rcs-018/evidence-schema-v1.json",
    HARNESS,
    WORKER,
    ROOT / ".github/workflows/rcs018.yml",
)

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        error(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"{path.relative_to(ROOT)} root must be an object")
        return {}
    return value


for path in REQUIRED:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

plan = load_json(ROOT / "research/rcs-018/experiment-plan-v1.json")
if plan:
    if plan.get("schema") != "rcs-018-experiment-plan/1.0":
        error("experiment plan schema mismatch")
    required_scenarios = {
        "lathe_trace",
        "mill_pending_reconcile",
        "two_body_split",
        "undo_replay",
        "worker_failure_mapping",
        "step_handoff",
    }
    actual = {item.get("id") for item in plan.get("scenarios", []) if isinstance(item, dict)}
    missing = required_scenarios - actual
    if missing:
        error(f"experiment plan missing scenarios: {sorted(missing)}")
    if plan.get("production_boundary") != "research-only":
        error("experiment plan must remain research-only")
    protected = set(plan.get("protected_semantics", []))
    for required in (
        "canonical-journal-authority",
        "durable-material-body-identity",
        "semantic-lineage",
        "preserve-all-default-step-body-selection",
        "genesis-v1-handoff-immutability",
    ):
        if required not in protected:
            error(f"experiment plan missing protected semantic {required}")

schema = load_json(ROOT / "research/rcs-018/evidence-schema-v1.json")
if schema:
    if schema.get("$id") != "rcs-018-integration-evidence/1.0":
        error("evidence schema $id mismatch")
    required_top = set(schema.get("required", []))
    if not {"schema", "issue", "architecture_profile", "scenarios", "contract_result"} <= required_top:
        error("evidence schema does not require the core top-level fields")


def run_harness() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(HARNESS)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        error(f"vertical slice exited {completed.returncode}: {completed.stderr.strip()}")
        return {}
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        error(f"vertical slice did not emit JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error("vertical slice output root must be an object")
        return {}
    return value


first = run_harness()
second = run_harness()
if first and second:
    if first != second:
        error("vertical slice output is not deterministic across two clean executions")
    if first.get("schema") != "rcs-018-integration-evidence/1.0":
        error("integration evidence schema mismatch")
    if first.get("architecture_profile") != "semantic-provider-hybrid-v1":
        error("integration evidence must exercise semantic-provider-hybrid-v1")

    result = first.get("contract_result")
    if not isinstance(result, dict):
        error("contract_result must be an object")
    else:
        expected_true = {
            "pending_to_reconciled_exercised",
            "multi_body_preserved",
            "derived_discard_rebuild_equal",
            "failure_injection_preserved_authority",
            "step_layer_d_truthful",
            "private_identity_absent",
        }
        for key in expected_true:
            if result.get(key) is not True:
                error(f"contract_result.{key} must be true")

    scenarios = first.get("scenarios")
    if not isinstance(scenarios, dict):
        error("scenarios must be an object")
    else:
        lathe = scenarios.get("lathe", {})
        mill = scenarios.get("mill_body_split", {})
        lathe_statuses = [x.get("engineering_status") for x in lathe.get("trace", [])]
        mill_statuses = [x.get("engineering_status") for x in mill.get("trace", [])]
        if "success" not in lathe_statuses:
            error("lathe scenario never reaches success")
        try:
            pending_i = mill_statuses.index("accepted_pending")
            reconciled_i = mill_statuses.index("reconciled", pending_i + 1)
            success_i = mill_statuses.index("success", reconciled_i + 1)
            if not pending_i < reconciled_i < success_i:
                error("mill status order is not pending -> reconciled -> success")
        except ValueError:
            error("mill scenario must contain pending -> reconciled -> success")

        bodies = set(mill.get("replay", {}).get("material_body_ids", []))
        if bodies != {"body:left", "body:right"}:
            error(f"mill replay must preserve both split bodies, observed {sorted(bodies)}")

        for name, scenario in (("lathe", lathe), ("mill", mill)):
            failures = scenario.get("worker_failure_injection", [])
            mapping = {
                item.get("mode"): item.get("outcome", {}).get("engineering_status")
                for item in failures
            }
            if mapping != {"error": "kernel_error", "crash": "crash", "timeout": "timeout"}:
                error(f"{name} worker failure mapping mismatch: {mapping}")
            if not all(item.get("durable_state_unchanged") is True for item in failures):
                error(f"{name} worker failure mutated durable authority")

            step = scenario.get("step_handoff", {})
            layers = step.get("layers", {})
            if layers.get("A") != "pass_semantic_preconditions":
                error(f"{name} STEP Layer A semantic gate did not pass")
            if layers.get("B") != "accepted_predecessor_automated_profile":
                error(f"{name} STEP Layer B must point to accepted predecessor automation")
            if layers.get("C") != "accepted_predecessor_automated_profile":
                error(f"{name} STEP Layer C must point to accepted predecessor automation")
            if layers.get("D") != "interoperability_unqualified":
                error(f"{name} STEP Layer D must remain interoperability_unqualified")
            if step.get("selection_mode") != "preserve_all_default":
                error(f"{name} STEP default must preserve all material bodies")

        durable_text = json.dumps(
            {
                "lathe": lathe.get("durable_authority"),
                "mill": mill.get("durable_authority"),
            },
            sort_keys=True,
        ).lower()
        for token in ("topods_", "occt handle", "godot object", "worker_pid", "process_id", "object_address"):
            if token in durable_text:
                error(f"durable evidence leaks forbidden private identity token {token!r}")

if HARNESS.is_file():
    spec = importlib.util.spec_from_file_location("rcs018_vertical_slice", HARNESS)
    module = importlib.util.module_from_spec(spec)
    sys.modules["rcs018_vertical_slice"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

    leaked = {"lineage_events": [{"relation": "preserved", "backend_id": "TopoDS_Face@0x1234"}]}
    try:
        module.assert_no_private_identity(leaked)
    except module.ContractError:
        pass
    else:
        error("private identity guard accepted a TopoDS-derived durable ID")

    mill_fixture = module.load_fixture(ROOT / "research/rcs-002/fixtures/mill-cut-through-v1.json")
    root_authority = module.JournalAuthority.from_fixture_root(mill_fixture)

    pending_step = module.step_handoff(
        root_authority,
        revision_id=root_authority.selected_head_revision_id,
        reconciliation_state="pending",
    )
    if pending_step.get("failure_code") != "RECONCILIATION_UNRESOLVED":
        error("pending STEP request did not fail closed at reconciliation boundary")

    unknown = module.step_handoff(
        root_authority,
        revision_id=root_authority.selected_head_revision_id,
        reconciliation_state="reconciled",
        requested_body_ids=["body:missing"],
    )
    if unknown.get("failure_code") != "BODY_SELECTION_INVALID":
        error("unknown STEP body selection was not refused")
    duplicate = module.step_handoff(
        root_authority,
        revision_id=root_authority.selected_head_revision_id,
        reconciliation_state="reconciled",
        requested_body_ids=["body:stock", "body:stock"],
    )
    if duplicate.get("failure_code") != "BODY_SELECTION_INVALID":
        error("duplicate STEP body selection was not refused")

    broken = copy.deepcopy(root_authority)
    broken.revisions[0]["body_ids"] = ["body:stock", "body:stock"]
    try:
        broken.validate()
    except module.ContractError:
        pass
    else:
        error("duplicate material-body identity was accepted")

docs = ROOT / "docs/26-INTEGRATED-SEMANTIC-CONTRACT-VERTICAL-SLICE.md"
if docs.is_file():
    text = docs.read_text(encoding="utf-8")
    for phrase in (
        "accepted_pending",
        "interoperability_unqualified",
        "body:left",
        "body:right",
        "process-isolated",
        "no foundational contradiction",
        "RCS-025",
        "RCS-026",
    ):
        if phrase not in text:
            error(f"integration report missing required phrase {phrase!r}")

if errors:
    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)
    raise SystemExit(1)

print("RCS-018 validation passed")
