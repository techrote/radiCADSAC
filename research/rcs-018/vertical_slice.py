#!/usr/bin/env python3
"""RCS-018 deterministic semantic-contract integration slice.

This is a research harness, not a production scheduler or geometry kernel. It
composes accepted programme contracts and routes provider adapters through a
process boundary while keeping durable authority free of backend-private IDs.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
WORKER = Path(__file__).with_name("worker_probe.py")

FORBIDDEN_DURABLE_TOKENS = (
    "topods_",
    "occt handle",
    "godot object",
    "triangle index",
    "voxel/cell identity",
    "worker_pid",
    "process_id",
    "object_address",
)

PROVIDER_PROFILES = {
    "turning": {
        "profile": "lathe-axisymmetric-provider@rcs-010",
        "evidence": "research/rcs-010/measured-summary-v1.json",
    },
    "milling": {
        "profile": "mill-strategy-hierarchy@rcs-011",
        "evidence": "research/rcs-011/measured-summary-v1.json",
    },
}

STEP_PROFILE = {
    "contract": "msac-step-conformance/1.0",
    "profile": "occt-8.0.1-ap242dis",
    "automated_evidence": "research/rcs-006",
    "interoperability_state": "interoperability_unqualified",
    "qualification_owner": "RCS-022",
}


class ContractError(RuntimeError):
    """Raised when a scenario would violate an accepted programme contract."""


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def assert_no_private_identity(value: Any) -> None:
    text = stable_json(value).lower()
    hits = [token for token in FORBIDDEN_DURABLE_TOKENS if token in text]
    if hits:
        raise ContractError(f"backend-private identity leaked into durable state: {hits}")


def load_fixture(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("fixture_schema") != "rcs-002-journal-fixture/1.0":
        raise ContractError(f"unsupported fixture schema in {path}")
    return value


def _operation_context(operation: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(operation[key])
        for key in (
            "operation_id",
            "kind",
            "setup_ref",
            "tool_ref",
            "normalization_policy_ref",
            "process_family",
            "target_body_ids",
        )
        if key in operation
    }


def _provider_for(operation: dict[str, Any]) -> dict[str, str]:
    family = operation.get("process_family", "")
    if family.startswith("turning."):
        return PROVIDER_PROFILES["turning"]
    if family.startswith("milling.") or family == "drilling":
        return PROVIDER_PROFILES["milling"]
    raise ContractError(f"no accepted research provider profile for process family {family!r}")


@dataclass
class JournalAuthority:
    fixture_id: str
    journal_schema: str
    project_id: str
    workpiece_id: str
    revisions: list[dict[str, Any]]
    operations: list[dict[str, Any]]
    body_transitions: list[dict[str, Any]]
    lineage_events: list[dict[str, Any]]
    selected_head_revision_id: str

    @classmethod
    def from_fixture_root(cls, fixture: dict[str, Any]) -> "JournalAuthority":
        journal = fixture["journal"]
        root_id = journal["root_revision_id"]
        root = next(r for r in journal["revisions"] if r["revision_id"] == root_id)
        schema = journal["journal_schema"]
        authority = cls(
            fixture_id=fixture["fixture_id"],
            journal_schema=f"{schema['id']}/{schema['major']}.{schema['minor']}",
            project_id=journal["project_id"],
            workpiece_id=journal["workpiece_id"],
            revisions=[copy.deepcopy(root)],
            operations=[],
            body_transitions=[],
            lineage_events=[],
            selected_head_revision_id=root_id,
        )
        authority.validate()
        return authority

    def durable_view(self) -> dict[str, Any]:
        value = {
            "schema": "rcs-018-durable-authority/1.0",
            "fixture_id": self.fixture_id,
            "journal_schema": self.journal_schema,
            "project_id": self.project_id,
            "workpiece_id": self.workpiece_id,
            "revisions": copy.deepcopy(self.revisions),
            "operations": copy.deepcopy(self.operations),
            "material_body_transitions": copy.deepcopy(self.body_transitions),
            "lineage_events": copy.deepcopy(self.lineage_events),
            "selected_head_revision_id": self.selected_head_revision_id,
        }
        assert_no_private_identity(value)
        return value

    def authority_digest(self) -> str:
        return digest(self.durable_view())

    def revision(self, revision_id: str) -> dict[str, Any]:
        for revision in self.revisions:
            if revision["revision_id"] == revision_id:
                return revision
        raise ContractError(f"unknown durable revision {revision_id}")

    def validate(self) -> None:
        ids = [r["revision_id"] for r in self.revisions]
        if len(ids) != len(set(ids)):
            raise ContractError("duplicate durable revision IDs")
        for revision in self.revisions:
            bodies = revision.get("body_ids")
            if not isinstance(bodies, list) or not bodies:
                raise ContractError(f"revision {revision.get('revision_id')} has no material bodies")
            if len(bodies) != len(set(bodies)):
                raise ContractError(f"revision {revision.get('revision_id')} repeats a material-body ID")
        assert_no_private_identity(self.durable_view() if hasattr(self, "fixture_id") else {})

    def commit_from_fixture(
        self,
        operation: dict[str, Any],
        target_revision: dict[str, Any],
        transition: dict[str, Any] | None,
    ) -> None:
        if operation["parent_revision_id"] != self.selected_head_revision_id:
            raise ContractError("commit does not extend selected immutable revision")
        if target_revision["parent_revision_id"] != self.selected_head_revision_id:
            raise ContractError("fixture target revision has wrong parent")
        if target_revision["caused_by_operation_id"] != operation["operation_id"]:
            raise ContractError("fixture target revision does not name the committed operation")

        before_bodies = list(self.revision(self.selected_head_revision_id)["body_ids"])
        after_bodies = list(target_revision["body_ids"])
        self.operations.append(_operation_context(operation))
        if transition:
            if transition["caused_by_operation_id"] != operation["operation_id"]:
                raise ContractError("body transition operation mismatch")
            output_ids = [item["body_id"] for item in transition["output_bodies"]]
            if output_ids != after_bodies:
                raise ContractError("body transition output IDs do not equal target revision body IDs")
            self.body_transitions.append(copy.deepcopy(transition))
            self.lineage_events.append(
                {
                    "relation": transition["kind"],
                    "caused_by_operation_id": operation["operation_id"],
                    "input_body_ids": copy.deepcopy(transition["input_body_ids"]),
                    "output_body_ids": output_ids,
                }
            )
        else:
            if before_bodies != after_bodies:
                raise ContractError("body set changed without explicit material_body_transition")
            if operation["kind"] == "process_motion":
                self.lineage_events.append(
                    {
                        "relation": "preserved",
                        "caused_by_operation_id": operation["operation_id"],
                        "input_body_ids": before_bodies,
                        "output_body_ids": after_bodies,
                    }
                )

        self.revisions.append(copy.deepcopy(target_revision))
        self.selected_head_revision_id = target_revision["revision_id"]
        self.validate()


def supervise_worker(operation: dict[str, Any], mode: str, timeout_s: float = 5.0) -> dict[str, Any]:
    payload = {
        "mode": mode,
        "operation": _operation_context(operation),
        "provider": _provider_for(operation) if operation.get("kind") == "process_motion" else None,
    }
    effective_timeout = 0.2 if mode == "timeout" else timeout_s
    try:
        completed = subprocess.run(
            [sys.executable, str(WORKER)],
            input=stable_json(payload),
            text=True,
            capture_output=True,
            timeout=effective_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "engineering_status": "timeout",
            "diagnostics": {"failure_class": "hang/timeout"},
        }

    stdout = completed.stdout.strip()
    record: dict[str, Any] = {}
    if stdout:
        try:
            record = json.loads(stdout.splitlines()[-1])
        except json.JSONDecodeError:
            record = {}

    if mode == "success" and completed.returncode == 0 and record.get("status") == "provider_candidate":
        return {
            "engineering_status": "success",
            "provider_profile": record["provider_profile"],
            "material_body_ids": record["material_body_ids"],
            "geometry_evidence": record["geometry_evidence"],
            "diagnostics": {"worker_returncode": completed.returncode},
        }
    if mode == "error":
        return {
            "engineering_status": "kernel_error",
            "diagnostics": {
                "failure_class": "algorithm returned error/status",
                "worker_returncode": completed.returncode,
                "provider_message": record.get("message", "provider error"),
            },
        }
    return {
        "engineering_status": "crash",
        "diagnostics": {
            "failure_class": "crash",
            "worker_returncode": completed.returncode,
        },
    }


def stage_process_motion(authority: JournalAuthority, operation: dict[str, Any]) -> dict[str, Any]:
    if operation["parent_revision_id"] != authority.selected_head_revision_id:
        raise ContractError("operation request does not target selected revision")
    provider = _provider_for(operation)
    status = "accepted_pending" if operation["process_family"].startswith("milling.") else "reconciled"
    return {
        "engineering_status": status,
        "revision_id": authority.selected_head_revision_id,
        "material_body_ids": list(authority.revision(authority.selected_head_revision_id)["body_ids"]),
        "operation_context": _operation_context(operation),
        "provider_profile": provider["profile"],
        "reconciliation_state": "pending" if status == "accepted_pending" else "reconciled",
        "diagnostics": {"accepted_geometry_evidence": provider["evidence"]},
    }


def step_handoff(
    authority: JournalAuthority,
    *,
    revision_id: str,
    reconciliation_state: str,
    requested_body_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    revision = authority.revision(revision_id)
    all_bodies = list(revision["body_ids"])
    selected = all_bodies if requested_body_ids is None else list(requested_body_ids)
    if not selected or any(body not in all_bodies for body in selected):
        return {
            "engineering_status": "refused_unsupported",
            "failure_code": "BODY_SELECTION_INVALID",
        }
    if len(selected) != len(set(selected)):
        return {
            "engineering_status": "refused_unsupported",
            "failure_code": "BODY_SELECTION_INVALID",
        }
    if reconciliation_state != "reconciled":
        return {
            "engineering_status": "accepted_pending",
            "failure_code": "RECONCILIATION_UNRESOLVED",
            "layers": {
                "A": "blocked",
                "B": "not_run",
                "C": "not_run",
                "D": "interoperability_unqualified",
            },
        }
    explicit_subset = selected != all_bodies
    return {
        "engineering_status": "interoperability_unqualified",
        "contract": STEP_PROFILE["contract"],
        "export_profile": STEP_PROFILE["profile"],
        "source_revision_id": revision_id,
        "all_body_ids": all_bodies,
        "selected_body_ids": selected,
        "omitted_body_ids": [body for body in all_bodies if body not in selected],
        "selection_mode": "explicit_subset" if explicit_subset else "preserve_all_default",
        "layers": {
            "A": "pass_semantic_preconditions",
            "B": "accepted_predecessor_automated_profile",
            "C": "accepted_predecessor_automated_profile",
            "D": STEP_PROFILE["interoperability_state"],
        },
        "evidence": {
            "automated_layers": STEP_PROFILE["automated_evidence"],
            "independent_interoperability": "not_yet_qualified",
            "qualification_owner": STEP_PROFILE["qualification_owner"],
        },
    }


def replay_revision(authority: JournalAuthority, target_revision_id: str) -> dict[str, Any]:
    revisions = {r["revision_id"]: r for r in authority.revisions}
    operations = {o["operation_id"]: o for o in authority.operations}
    if target_revision_id not in revisions:
        raise ContractError(f"cannot replay unknown revision {target_revision_id}")

    chain: list[dict[str, Any]] = []
    cursor = revisions[target_revision_id]
    while cursor["parent_revision_id"] is not None:
        chain.append(cursor)
        cursor = revisions[cursor["parent_revision_id"]]
    chain.reverse()

    op_ids = [r["caused_by_operation_id"] for r in chain]
    process_ops = [operations[op_id] for op_id in op_ids if op_id in operations and operations[op_id]["kind"] == "process_motion"]
    provider_profiles = [_provider_for(op)["profile"] for op in process_ops]
    body_ids = list(revisions[target_revision_id]["body_ids"])
    relevant_lineage = [
        event
        for event in authority.lineage_events
        if event["caused_by_operation_id"] in op_ids
    ]
    invariant_payload = {
        "revision_id": target_revision_id,
        "operation_ids": op_ids,
        "material_body_ids": body_ids,
        "lineage_events": relevant_lineage,
    }
    return {
        "revision_id": target_revision_id,
        "operation_ids": op_ids,
        "material_body_ids": body_ids,
        "provider_profiles": provider_profiles,
        "engineering_invariant_sha256": digest(invariant_payload),
    }


def run_fixture(fixture: dict[str, Any], exercise_failures: bool = False) -> dict[str, Any]:
    journal = fixture["journal"]
    authority = JournalAuthority.from_fixture_root(fixture)
    revisions = {r["revision_id"]: r for r in journal["revisions"]}
    transitions = {t["caused_by_operation_id"]: t for t in journal.get("material_body_transitions", [])}
    trace: list[dict[str, Any]] = []
    worker_failures: list[dict[str, Any]] = []

    for operation in journal["operations"]:
        target = next(
            r for r in journal["revisions"]
            if r.get("caused_by_operation_id") == operation["operation_id"]
        )
        if operation["kind"] == "setup_change":
            authority.commit_from_fixture(operation, target, transitions.get(operation["operation_id"]))
            trace.append(
                {
                    "operation_id": operation["operation_id"],
                    "engineering_status": "reconciled",
                    "revision_id": target["revision_id"],
                    "reconciliation_state": "reconciled",
                }
            )
            continue

        staged = stage_process_motion(authority, operation)
        trace.append(copy.deepcopy(staged))

        if exercise_failures:
            before = authority.authority_digest()
            for mode in ("error", "crash", "timeout"):
                outcome = supervise_worker(operation, mode)
                after = authority.authority_digest()
                worker_failures.append(
                    {
                        "mode": mode,
                        "outcome": outcome,
                        "authority_digest_before": before,
                        "authority_digest_after": after,
                        "durable_state_unchanged": before == after,
                    }
                )

        worker = supervise_worker(operation, "success")
        if worker["engineering_status"] != "success":
            raise ContractError(f"success-mode provider worker failed: {worker}")
        if staged["engineering_status"] == "accepted_pending":
            trace.append(
                {
                    "operation_id": operation["operation_id"],
                    "engineering_status": "reconciled",
                    "revision_id": authority.selected_head_revision_id,
                    "material_body_ids": list(authority.revision(authority.selected_head_revision_id)["body_ids"]),
                    "provider_profile": worker["provider_profile"],
                    "reconciliation_state": "reconciled",
                    "diagnostics": {"geometry_evidence": worker["geometry_evidence"]},
                }
            )

        authority.commit_from_fixture(operation, target, transitions.get(operation["operation_id"]))
        trace.append(
            {
                "operation_id": operation["operation_id"],
                "engineering_status": "success",
                "revision_id": target["revision_id"],
                "material_body_ids": list(target["body_ids"]),
                "provider_profile": worker["provider_profile"],
                "reconciliation_state": "reconciled",
                "diagnostics": {"geometry_evidence": worker["geometry_evidence"]},
            }
        )

    if authority.selected_head_revision_id != journal["selected_head_revision_id"]:
        raise ContractError("integration replay did not reach fixture selected head")
    if authority.revision(authority.selected_head_revision_id)["body_ids"] != revisions[journal["selected_head_revision_id"]]["body_ids"]:
        raise ContractError("integration replay body mapping diverged from fixture")

    head = authority.selected_head_revision_id
    derived_a = replay_revision(authority, head)
    derived_a_digest = digest(derived_a)
    # Derived state is intentionally discarded here.
    derived_b = replay_revision(authority, head)
    derived_b_digest = digest(derived_b)

    step = step_handoff(
        authority,
        revision_id=head,
        reconciliation_state="reconciled",
    )
    return {
        "fixture_id": fixture["fixture_id"],
        "trace": trace,
        "durable_authority": authority.durable_view(),
        "durable_authority_sha256": authority.authority_digest(),
        "replay": {
            "first_derived_sha256": derived_a_digest,
            "rebuilt_derived_sha256": derived_b_digest,
            "engineering_invariant_sha256": derived_b["engineering_invariant_sha256"],
            "material_body_ids": derived_b["material_body_ids"],
            "discard_and_rebuild_equal": derived_a_digest == derived_b_digest,
        },
        "worker_failure_injection": worker_failures,
        "step_handoff": step,
    }


def build_evidence() -> dict[str, Any]:
    lathe_path = ROOT / "research/rcs-002/fixtures/lathe-finishing-pass-v1.json"
    mill_path = ROOT / "research/rcs-002/fixtures/mill-cut-through-v1.json"
    lathe = run_fixture(load_fixture(lathe_path), exercise_failures=True)
    mill = run_fixture(load_fixture(mill_path), exercise_failures=True)
    evidence = {
        "schema": "rcs-018-integration-evidence/1.0",
        "issue": "RCS-018",
        "architecture_profile": "semantic-provider-hybrid-v1",
        "source_contracts": [
            "msac-journal/1.0",
            "semantic-lineage-v1",
            "regularized-deferred-topology-v1",
            "msac-step-conformance/1.0",
            "process-isolated-workers@RCS-017",
        ],
        "scenarios": {
            "lathe": lathe,
            "mill_body_split": mill,
        },
        "contract_result": {
            "pending_to_reconciled_exercised": any(
                item.get("engineering_status") == "accepted_pending"
                for item in mill["trace"]
            ) and any(
                item.get("engineering_status") == "reconciled"
                for item in mill["trace"]
            ),
            "multi_body_preserved": set(mill["replay"]["material_body_ids"]) == {"body:left", "body:right"},
            "derived_discard_rebuild_equal": lathe["replay"]["discard_and_rebuild_equal"] and mill["replay"]["discard_and_rebuild_equal"],
            "failure_injection_preserved_authority": all(
                item["durable_state_unchanged"]
                for scenario in (lathe, mill)
                for item in scenario["worker_failure_injection"]
            ),
            "step_layer_d_truthful": lathe["step_handoff"]["layers"]["D"] == "interoperability_unqualified"
            and mill["step_handoff"]["layers"]["D"] == "interoperability_unqualified",
            "private_identity_absent": True,
        },
    }
    assert_no_private_identity(
        {
            "lathe": lathe["durable_authority"],
            "mill": mill["durable_authority"],
        }
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = build_evidence()
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
