#!/usr/bin/env python3
"""Validate the durable RCS-013 architecture synthesis and Gate-2 decision."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ROOT / "docs/20-OPENSIMACHINIST-ARCHITECTURE-SYNTHESIS.md",
    ROOT / "docs/decisions/DR-0015-gate-2-semantic-provider-hybrid-architecture.md",
    ROOT / "research/rcs-013/README.md",
    ROOT / "research/rcs-013/architecture-v1.json",
    ROOT / "research/rcs-013/unresolved-v1.json",
)

REQUIRED_OPTIONS = {
    "deep-occt-fork",
    "monolithic-occt-brep-core",
    "whole-model-discrete-core",
    "semantic-provider-hybrid",
}

REQUIRED_COMPONENTS = {
    "journal-ingress",
    "semantic-lineage",
    "policy-dispatch",
    "lathe-axisymmetric-provider",
    "mill-provider",
    "generic-brep-provider",
    "deferred-material-coordinator",
    "bounded-fallback-adapter",
    "brep-reconciler",
    "step-conformance-adapter",
    "worker-supervisor",
}

REQUIRED_TOLERANCE_CHANNELS = {
    "input_sampling_resolution",
    "machine_control_resolution",
    "manufacturing_tolerance",
    "numerical_uncertainty",
    "topological_equivalence",
    "contact_classification",
    "preview_tolerance",
    "export_tolerance",
    "validation_tolerance",
}

REQUIRED_REQUEST_FAMILIES = {
    "capabilities",
    "apply_canonical_operations",
    "commit_revision",
    "replay_revision",
    "query_material_state",
    "request_preview",
    "request_reconciliation",
    "inspect_reconciled_geometry",
    "export_step",
}

REQUIRED_RESPONSE_FIELDS = {
    "contract_version",
    "engineering_status",
    "revision_id",
    "material_body_ids",
    "lineage_events",
    "provider_profile",
    "reconciliation_state",
    "diagnostics",
}

REQUIRED_STATUSES = {
    "accepted_pending",
    "reconciled",
    "success",
    "refused_unsupported",
    "refused_unresolved_ambiguity",
    "invalid_topology",
    "wrong_geometry",
    "tolerance_breach",
    "kernel_error",
    "crash",
    "timeout",
    "nondeterministic_result",
    "step_writer_failure",
    "step_roundtrip_failure",
    "interoperability_unqualified",
}

REQUIRED_EVIDENCE = {
    "step": "docs/decisions/DR-0009-step-conformance-and-body-preservation.md",
    "tolerance": "research/rcs-007/measured-summary-v1.json",
    "lineage": "research/rcs-008/measured-summary-v1.json",
    "deferred_topology": "research/rcs-009/measured-summary-v1.json",
    "lathe": "research/rcs-010/measured-summary-v1.json",
    "mill": "research/rcs-011/measured-summary-v1.json",
    "hybrid": "research/rcs-012/measured-summary-v1.json",
    "occt_audit": "docs/12-OCCT-8.0.1-AUDIT.md",
}

REQUIRED_UNRESOLVED = {
    "mill-pathological-freehand-fallback",
    "lathe-real-tool-envelope",
    "production-step-interoperability-profile",
    "hybrid-reconciliation-curved-geometry",
    "occt-thread-global-state-boundary",
    "provider-handoff-reconciliation-frequency",
    "semantic-lineage-persistence-encoding",
    "bounded-deferred-resource-policy",
    "targeted-exact-arithmetic-seams",
    "distribution-license-compliance",
}

REQUIRED_BLOCK_CLASSES = {
    "mvp-capability",
    "mvp-implementation",
    "step-integrity",
    "performance",
    "reliability",
    "later-capability",
    "release",
}

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"{label} is not valid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"{label} root must be an object")
        return {}
    return value


def require_string(obj: dict[str, Any], key: str, where: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        error(f"{where}.{key} must be a non-empty string")
        return ""
    return value


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

architecture_path = ROOT / "research/rcs-013/architecture-v1.json"
architecture = load_object(architecture_path, "architecture")
if architecture:
    if architecture.get("schema") != "rcs-013-architecture/1.0":
        error("architecture schema must be rcs-013-architecture/1.0")
    if architecture.get("status") != "gate-2-accepted":
        error("architecture status must record gate-2-accepted")
    source_main = architecture.get("source_main")
    if not isinstance(source_main, str) or len(source_main) != 40:
        error("architecture source_main must be a 40-character commit SHA")

    selected_arch = architecture.get("architecture")
    if not isinstance(selected_arch, dict):
        error("architecture.architecture must be an object")
    else:
        if selected_arch.get("id") != "semantic-provider-hybrid-v1":
            error("selected architecture must be semantic-provider-hybrid-v1")
        summary = require_string(selected_arch, "summary", "architecture")
        if "OCCT" not in summary or "process-specialized" not in summary:
            error("selected architecture summary must state the OCCT/provider hybrid boundary")
        durable = selected_arch.get("durable_authority")
        if not isinstance(durable, list) or not all(isinstance(x, str) for x in durable):
            error("durable_authority must be a string list")
        else:
            durable_text = " ".join(durable).lower()
            for term in ("journal", "semantic lineage", "material-body"):
                if term not in durable_text:
                    error(f"durable_authority missing {term!r}")
        derived = selected_arch.get("replaceable_derived_state")
        if not isinstance(derived, list) or not all(isinstance(x, str) for x in derived):
            error("replaceable_derived_state must be a string list")
        else:
            derived_text = " ".join(derived).lower()
            for term in ("topods", "preview mesh", "voxel", "b-rep"):
                if term not in derived_text:
                    error(f"replaceable_derived_state missing {term!r}")
        deployment = require_string(selected_arch, "deployment_default", "architecture")
        if "process-isolated" not in deployment or "RCS-017" not in deployment:
            error("deployment default must preserve process isolation pending RCS-017")

    options = architecture.get("options")
    option_ids: set[str] = set()
    selected_count = 0
    if not isinstance(options, list):
        error("options must be a list")
    else:
        for index, item in enumerate(options):
            if not isinstance(item, dict):
                error(f"options[{index}] must be an object")
                continue
            option_id = require_string(item, "id", f"options[{index}]")
            require_string(item, "decision", f"options[{index}]")
            require_string(item, "reason", f"options[{index}]")
            option_ids.add(option_id)
            if item.get("decision") == "selected":
                selected_count += 1
                if option_id != "semantic-provider-hybrid":
                    error("only semantic-provider-hybrid may be selected")
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                error(f"options[{index}].evidence must be a non-empty list")
        missing_options = REQUIRED_OPTIONS - option_ids
        if missing_options:
            error(f"missing architecture options: {sorted(missing_options)}")
        if selected_count != 1:
            error(f"architecture options must select exactly one option, observed {selected_count}")

    components = architecture.get("components")
    component_ids: set[str] = set()
    if not isinstance(components, list):
        error("components must be a list")
    else:
        for index, item in enumerate(components):
            if not isinstance(item, dict):
                error(f"components[{index}] must be an object")
                continue
            component_ids.add(require_string(item, "id", f"components[{index}]"))
            require_string(item, "role", f"components[{index}]")
            require_string(item, "authority", f"components[{index}]")
        missing_components = REQUIRED_COMPONENTS - component_ids
        if missing_components:
            error(f"missing architecture components: {sorted(missing_components)}")

    dispatch = architecture.get("solver_dispatch")
    if not isinstance(dispatch, dict):
        error("solver_dispatch must be an object")
    else:
        for key in ("lathe", "mill", "forbidden_shortcuts"):
            value = dispatch.get(key)
            if not isinstance(value, list) or not value or not all(isinstance(x, str) for x in value):
                error(f"solver_dispatch.{key} must be a non-empty string list")
        lathe_text = " ".join(dispatch.get("lathe", [])).lower()
        mill_text = " ".join(dispatch.get("mill", [])).lower()
        forbidden_text = " ".join(dispatch.get("forbidden_shortcuts", [])).lower()
        if "axisymmetric" not in lathe_text or "refuse" not in lathe_text:
            error("lathe dispatch must include axisymmetric support and refusal")
        for term in ("analytic", "segment", "fallback", "refuse"):
            if term not in mill_text:
                error(f"mill dispatch missing {term!r}")
        for term in ("global fuzzy", "freehand", "sampled-pose", "mesh/voxel", "largest/first"):
            if term not in forbidden_text:
                error(f"forbidden shortcuts missing {term!r}")

    boundaries = architecture.get("reconciliation_boundaries")
    if not isinstance(boundaries, list) or not all(isinstance(x, str) for x in boundaries):
        error("reconciliation_boundaries must be a string list")
    else:
        boundary_text = " ".join(boundaries).lower()
        for term in ("connectivity", "topology-dependent", "provider handoff", "step export"):
            if term not in boundary_text:
                error(f"reconciliation boundaries missing {term!r}")

    tolerance = architecture.get("tolerance_policy")
    if not isinstance(tolerance, dict):
        error("tolerance_policy must be an object")
    else:
        channels = tolerance.get("separate_channels")
        if not isinstance(channels, list) or set(channels) != REQUIRED_TOLERANCE_CHANNELS:
            error("tolerance policy must contain exactly the nine accepted channels")
        if "defer/reconcile" not in str(tolerance.get("uncertain_contact", "")):
            error("uncertain contact must defer/reconcile")
        if "never silently" not in str(tolerance.get("positive_removal", "")):
            error("positive removal rule must prohibit silent no-op conversion")
        if "semantic-lineage" not in str(tolerance.get("retrace_elision", "")):
            error("retrace elision must require semantic-lineage proof")

    api = architecture.get("external_api")
    if not isinstance(api, dict):
        error("external_api must be an object")
    else:
        if "not selected" not in str(api.get("transport", "")):
            error("RCS-013 must not prematurely select an RPC/ABI transport")
        request_families = api.get("request_families")
        if not isinstance(request_families, list) or set(request_families) != REQUIRED_REQUEST_FAMILIES:
            error("external_api request_families mismatch")
        response_fields = api.get("common_response_fields")
        if not isinstance(response_fields, list) or set(response_fields) != REQUIRED_RESPONSE_FIELDS:
            error("external_api common_response_fields mismatch")
        forbidden = api.get("private_types_forbidden")
        if not isinstance(forbidden, list):
            error("external_api.private_types_forbidden must be a list")
        else:
            forbidden_text = " ".join(str(x) for x in forbidden)
            for term in ("TopoDS_", "OCCT Handle", "Godot Object", "triangle", "voxel"):
                if term not in forbidden_text:
                    error(f"external API private-type prohibition missing {term!r}")

    statuses = architecture.get("engineering_status_model")
    if not isinstance(statuses, list) or set(statuses) != REQUIRED_STATUSES:
        error("engineering_status_model must contain the accepted status vocabulary")

    evidence = architecture.get("evidence")
    if not isinstance(evidence, dict):
        error("evidence must be an object")
    else:
        for key, path_text in REQUIRED_EVIDENCE.items():
            if evidence.get(key) != path_text:
                error(f"evidence.{key} must point to {path_text}")
            if not (ROOT / path_text).is_file():
                error(f"evidence source does not exist: {path_text}")

    dependencies = architecture.get("dependency_strategy")
    if not isinstance(dependencies, dict):
        error("dependency_strategy must be an object")
    else:
        occt = str(dependencies.get("occt", ""))
        if "pinned" not in occt or "Do not deep-fork" not in occt:
            error("OCCT dependency strategy must pin/isolate and reject premature deep fork")
        if "GPL-3+" not in str(dependencies.get("cgal_nef", "")):
            error("dependency strategy must retain CGAL Nef GPL-3+ constraint")

unresolved_path = ROOT / "research/rcs-013/unresolved-v1.json"
unresolved = load_object(unresolved_path, "unresolved register")
if unresolved:
    if unresolved.get("schema") != "rcs-013-unresolved/1.0":
        error("unresolved register schema must be rcs-013-unresolved/1.0")
    items = unresolved.get("items")
    ids: set[str] = set()
    priorities: list[int] = []
    block_classes: set[str] = set()
    if not isinstance(items, list) or len(items) < 10:
        error("unresolved register must contain at least ten ranked items")
    else:
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                error(f"unresolved.items[{index}] must be an object")
                continue
            item_id = require_string(item, "id", f"unresolved.items[{index}]")
            ids.add(item_id)
            priority = item.get("priority")
            if not isinstance(priority, int) or priority < 1:
                error(f"unresolved.items[{index}].priority must be a positive integer")
            else:
                priorities.append(priority)
            if item.get("severity") not in {"high", "medium", "low"}:
                error(f"unresolved.items[{index}].severity invalid")
            for field in ("question", "current_safe_policy", "owner"):
                require_string(item, field, f"unresolved.items[{index}]")
            blocks = item.get("blocks")
            if not isinstance(blocks, list) or not blocks or not all(isinstance(x, str) for x in blocks):
                error(f"unresolved.items[{index}].blocks must be a non-empty string list")
            else:
                block_classes.update(blocks)
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                error(f"unresolved.items[{index}].evidence must be a non-empty list")
        missing = REQUIRED_UNRESOLVED - ids
        if missing:
            error(f"unresolved register missing required items: {sorted(missing)}")
        if len(priorities) != len(set(priorities)):
            error("unresolved priorities must be unique")
        if priorities != sorted(priorities):
            error("unresolved items must be stored in ascending priority order")
        missing_blocks = REQUIRED_BLOCK_CLASSES - block_classes
        if missing_blocks:
            error(f"unresolved register missing blocker classifications: {sorted(missing_blocks)}")

report_path = ROOT / "docs/20-OPENSIMACHINIST-ARCHITECTURE-SYNTHESIS.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    required_report_terms = (
        "## Executive decision",
        "## Gate-2 evidence assessment",
        "## Architecture options matrix",
        "## Programme-owned versus implementation-private state",
        "## Component architecture and data flow",
        "## Stable programme-facing API proposal",
        "## Tolerance, uncertainty and equivalence",
        "## Provenance and semantic identity",
        "## Regularized material and deferred topology",
        "## Lathe provider policy",
        "## Mill strategy hierarchy",
        "## Bounded hybrid fallbacks",
        "## Reconciliation and STEP boundary",
        "## Preview, incremental engineering state and replay",
        "## Error and status model",
        "## Versioning and replay strategy",
        "## Concurrency and process-isolation boundary",
        "## Dependency, licensing and upstream-sync strategy",
        "## Contradictory findings reconciled",
        "## Unresolved research register",
        "## Gate-2 conclusion",
        "Gate 2 — architecture-choice ready — is satisfied",
        "7.5396",
        "1137 to 16",
        "process-isolated",
        "RCS-017",
        "writer returned OK",
    )
    for term in required_report_terms:
        if term not in report:
            error(f"architecture report missing required term/section {term!r}")

record_path = ROOT / "docs/decisions/DR-0015-gate-2-semantic-provider-hybrid-architecture.md"
if record_path.is_file():
    record = record_path.read_text(encoding="utf-8")
    required_record_terms = (
        "Status: accepted",
        "## Context",
        "## Decision",
        "## Alternatives considered",
        "## Evidence",
        "## Consequences",
        "## Reversibility",
        "## Reconsideration trigger",
        "semantic-provider-hybrid-v1",
        "Gate 2 — architecture-choice ready — satisfied",
        "process isolation",
        "RCS-017",
        "RCS-005",
    )
    for term in required_record_terms:
        if term not in record:
            error(f"Gate-2 decision record missing required term/section {term!r}")

if errors:
    print("RCS-013 architecture validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print(
    "RCS-013 architecture validation passed "
    f"({len(REQUIRED_COMPONENTS)} components, {len(REQUIRED_STATUSES)} statuses, "
    f"{len(REQUIRED_UNRESOLVED)} mandatory unresolved items)"
)
