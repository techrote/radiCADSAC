#!/usr/bin/env python3
"""Validate the clean MSAC founding handoff produced by RCS-015."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoffs/msac"

HUMAN_FILES = (
    HANDOFF / "README.md",
    HANDOFF / "00-FOUNDING-SPEC.md",
    HANDOFF / "01-IMPLEMENTATION-ROADMAP.md",
    HANDOFF / "02-INITIAL-ISSUE-GRAPH.md",
    HANDOFF / "03-INTEGRATION-ESCAPE-ROUTES.md",
    HANDOFF / "04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md",
)
MANIFEST = HANDOFF / "handoff-v1.json"
REQUIRED_FILES = HUMAN_FILES + (MANIFEST,)

REQUIRED_GATE4 = {
    "backend_boundary_stable_enough_to_consume",
    "operation_journal_and_canonicalization_contract",
    "preview_engineering_state_reconciliation_model",
    "error_and_status_model",
    "machine_module_geometry_provider_extension_contract",
    "initial_lathe_mill_capabilities_and_limitations",
    "productive_core_loop_plan",
}
REQUIRED_ISSUES = {f"MSAC-{i:03d}" for i in range(1, 16)}
REQUIRED_ESCAPE_ROUTES = {
    "replaceable-backend-transport",
    "capability-version-discovery",
    "pathological-mill-pending-fallback-refusal",
    "lathe-tool-envelope-capability-gating",
    "step-interoperability-qualification-status",
    "deferred-reconciliation-state",
    "process-isolated-worker-tolerance",
    "backend-crash-replay-recovery",
    "semantic-lineage-not-topology-persistence",
    "backend-private-hybrid-representations",
    "explicit-version-migration",
    "remappable-control-profiles",
    "camera-presentation-only",
    "unsupported-operation-authority-label",
}
REQUIRED_EVIDENCE_KEYS = {
    "sac_product_intent",
    "target_user",
    "lathe_and_mill_initial_scope",
    "journal_is_durable_intent",
    "stable_backend_boundary",
    "canonical_numerics_frames",
    "bounded_canonicalization",
    "immutable_revisions_body_transitions",
    "step_primary_and_body_preserving",
    "separate_tolerance_channels",
    "semantic_lineage",
    "backend_architecture",
    "backend_clean_handoff",
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def load_object(path: Path) -> dict[str, Any]:
    text = read(path)
    if not text:
        return {}
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(obj, dict):
        fail(f"JSON root must be object: {path.relative_to(ROOT)}")
        return {}
    return obj


def require_terms(text: str, terms: tuple[str, ...], label: str, *, casefold: bool = True) -> None:
    haystack = text.casefold() if casefold else text
    for term in terms:
        needle = term.casefold() if casefold else term
        if needle not in haystack:
            fail(f"{label} missing required term: {term!r}")


for path in REQUIRED_FILES:
    if not path.is_file():
        fail(f"missing required file: {path.relative_to(ROOT)}")

manifest = load_object(MANIFEST)
if manifest:
    if manifest.get("schema") != "msac-handoff/1.0":
        fail("handoff schema must be msac-handoff/1.0")
    if manifest.get("status") != "gate-4-candidate":
        fail("handoff status must be gate-4-candidate")
    if manifest.get("frontend_architecture") != "sac-machine-module-client-v1":
        fail("handoff must declare sac-machine-module-client-v1")
    if manifest.get("backend_architecture") != "semantic-provider-hybrid-v1":
        fail("handoff must consume semantic-provider-hybrid-v1")
    source_main = manifest.get("source_main")
    if not isinstance(source_main, str) or not re.fullmatch(r"[0-9a-f]{40}", source_main):
        fail("source_main must be a lowercase 40-character commit SHA")

    contracts = manifest.get("programme_contracts")
    if not isinstance(contracts, dict):
        fail("programme_contracts must be an object")
    else:
        for key in (
            "founding_brief",
            "external_boundary",
            "journal",
            "step",
            "backend_architecture_decision",
            "backend_handoff",
        ):
            path_text = contracts.get(key)
            if not isinstance(path_text, str) or not path_text:
                fail(f"programme_contracts.{key} must be a path string")
            elif not (ROOT / path_text).is_file():
                fail(f"programme contract path does not exist: {path_text}")

    listed = manifest.get("handoff_files")
    expected = {str(path.relative_to(ROOT)) for path in HUMAN_FILES}
    if not isinstance(listed, list) or set(listed) != expected:
        fail("handoff_files must list exactly the six human-readable handoff documents")

    evidence = manifest.get("major_decision_evidence")
    if not isinstance(evidence, dict):
        fail("major_decision_evidence must be an object")
    else:
        missing = REQUIRED_EVIDENCE_KEYS - set(evidence)
        extra = set(evidence) - REQUIRED_EVIDENCE_KEYS
        if missing:
            fail(f"major decision evidence missing keys: {sorted(missing)}")
        if extra:
            fail(f"major decision evidence has unexpected keys: {sorted(extra)}")
        for key, paths in evidence.items():
            if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p for p in paths):
                fail(f"major_decision_evidence.{key} must be a non-empty path list")
                continue
            for path_text in paths:
                if not (ROOT / path_text).is_file():
                    fail(f"evidence source does not exist: {path_text}")

    gate4 = manifest.get("gate4")
    if not isinstance(gate4, dict):
        fail("gate4 must be an object")
    else:
        criteria = gate4.get("criteria")
        if not isinstance(criteria, dict) or set(criteria) != REQUIRED_GATE4:
            fail("gate4.criteria must contain exactly the roadmap Gate-4 requirements")
        elif any(value != "satisfied" for value in criteria.values()):
            fail("every Gate-4 content criterion must be marked satisfied")
        assertion = str(gate4.get("assertion", "")).casefold()
        for term in ("does not assert", "validated", "merged"):
            if term not in assertion:
                fail(f"Gate-4 assertion missing scope term: {term!r}")

    graph = manifest.get("production_issue_graph")
    ids: set[str] = set()
    deps_by_id: dict[str, list[str]] = {}
    if not isinstance(graph, list):
        fail("production_issue_graph must be a list")
    else:
        for index, item in enumerate(graph):
            if not isinstance(item, dict):
                fail(f"production_issue_graph[{index}] must be an object")
                continue
            issue_id = item.get("id")
            title = item.get("title")
            deps = item.get("depends_on")
            if not isinstance(issue_id, str) or not re.fullmatch(r"MSAC-\d{3}", issue_id):
                fail(f"invalid issue id at production_issue_graph[{index}]")
                continue
            if issue_id in ids:
                fail(f"duplicate production issue id: {issue_id}")
            ids.add(issue_id)
            if not isinstance(title, str) or not title.strip():
                fail(f"{issue_id} title must be non-empty")
            if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
                fail(f"{issue_id} depends_on must be a string list")
                deps_by_id[issue_id] = []
            else:
                deps_by_id[issue_id] = deps
        if ids != REQUIRED_ISSUES:
            fail(f"production issue set mismatch: expected {sorted(REQUIRED_ISSUES)}, got {sorted(ids)}")
        for issue_id, deps in deps_by_id.items():
            for dep in deps:
                if dep not in ids:
                    fail(f"{issue_id} depends on unknown issue {dep}")
                if dep == issue_id:
                    fail(f"{issue_id} cannot depend on itself")

        temporary: set[str] = set()
        permanent: set[str] = set()

        def visit(node: str) -> None:
            if node in permanent:
                return
            if node in temporary:
                fail(f"production issue graph contains a dependency cycle at {node}")
                return
            temporary.add(node)
            for dep in deps_by_id.get(node, []):
                if dep in ids:
                    visit(dep)
            temporary.remove(node)
            permanent.add(node)

        for issue_id in sorted(ids):
            visit(issue_id)

    escape_routes = manifest.get("integration_escape_routes")
    if not isinstance(escape_routes, list) or set(escape_routes) != REQUIRED_ESCAPE_ROUTES:
        fail("integration_escape_routes must preserve the complete founding escape-route set")

readme = read(HANDOFF / "README.md")
require_terms(
    readme,
    (
        "sac-machine-module-client-v1",
        "semantic-provider-hybrid-v1",
        "Gate 4",
        "production repository must be created separately",
        "lathe/mill → canonical journal → backend → valid STEP",
    ),
    "handoff README",
)

founding = read(HANDOFF / "00-FOUNDING-SPEC.md")
for heading in (
    "## Product brief and SAC philosophy",
    "## Target user and product test",
    "## Anti-chore and asymmetric-realism doctrine",
    "## Product architecture",
    "## Machine-module architecture and contract surface",
    "## Gamepad and manual-control principles",
    "## Camera and spatial-navigation concept",
    "## Canonical operation-journal producer contract",
    "## Immutable project history, undo and redo",
    "## MSAC↔OpenSimachinist boundary",
    "## Programme-facing status and failure presentation",
    "## Preview versus authoritative engineering geometry",
    "## Initial lathe capability and limitations",
    "## Initial mill capability and limitations",
    "## Dimensional inspection and DRO requirements",
    "## STEP export UX and conformance/status presentation",
    "## Save, project and versioning model",
    "## Initial productive vertical slice",
    "## Explicit first-implementation non-goals",
):
    if heading not in founding:
        fail(f"founding specification missing heading: {heading}")
require_terms(
    founding,
    (
        "msac-journal/1.0",
        "nm-nrad-ns-q15-v1",
        "msac-step-conformance/1.0",
        "first-person machinist",
        "workpiece-follow/free-flight",
        "accepted_pending",
        "reconciled",
        "interoperability_unqualified",
        "capabilities",
        "apply_canonical_operations",
        "commit_revision",
        "replay_revision",
        "query_material_state",
        "request_preview",
        "request_reconciliation",
        "inspect_reconciled_geometry",
        "export_step",
        "all material bodies",
        "no implicit largest/first/primary-body rule",
        "atomic save",
        "conventional sketch/extrude/feature-tree cad",
    ),
    "founding specification",
)

roadmap = read(HANDOFF / "01-IMPLEMENTATION-ROADMAP.md")
for stage in range(9):
    if f"## Stage {stage}" not in roadmap:
        fail(f"implementation roadmap missing Stage {stage}")
require_terms(
    roadmap,
    (
        "productive engineering loop first",
        "journal → backend → valid STEP",
        "game/publication polish",
        "canonical journal → backend → conventional valid STEP",
    ),
    "implementation roadmap",
)
if roadmap.count("Measurable exit:") < 9:
    fail("every numbered roadmap stage must have a measurable exit")

issues_doc = read(HANDOFF / "02-INITIAL-ISSUE-GRAPH.md")
for issue_id in sorted(REQUIRED_ISSUES):
    if f"## {issue_id} —" not in issues_doc:
        fail(f"initial issue document missing section for {issue_id}")

sections = re.split(r"(?=^## MSAC-\d{3} —)", issues_doc, flags=re.MULTILINE)
issue_sections = [section for section in sections if re.match(r"^## MSAC-\d{3} —", section)]
if len(issue_sections) != len(REQUIRED_ISSUES):
    fail(f"expected 15 issue sections, observed {len(issue_sections)}")
for section in issue_sections:
    match = re.match(r"^## (MSAC-\d{3}) —", section)
    issue_id = match.group(1) if match else "unknown"
    lower = section.casefold()
    for term in (
        "work on a branch",
        "automated tests",
        "open a pr",
        "merge only after all required checks pass",
        "verify the merge landed on `main`",
        "acceptance criteria",
    ):
        if term not in lower:
            fail(f"{issue_id} autonomous prompt missing execution requirement: {term!r}")

escape_doc = read(HANDOFF / "03-INTEGRATION-ESCAPE-ROUTES.md")
for priority in range(1, 15):
    if f"Priority {priority}" not in escape_doc:
        fail(f"integration escape-route register missing Priority {priority}")
require_terms(
    escape_doc,
    (
        "## Escape-route doctrine",
        "defer",
        "reconcile",
        "handoff",
        "bounded fallback",
        "refuse",
        "visual-only",
        "silently widening tolerance",
    ),
    "integration escape-route register",
)

bootstrap = read(HANDOFF / "04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md")
require_terms(
    bootstrap,
    (
        "new Git history",
        "Do not copy obsolete/rejected",
        "Linux hosted CI",
        "Windows build path",
        "branch → PR → automated checks → merge → `main` verification",
        "No unresolved research question is asserted as solved",
        "msac-journal/1.0",
        "STEP",
    ),
    "bootstrap checklist",
)

if errors:
    print("RCS-015 validation FAILED", file=sys.stderr)
    for message in errors:
        print(f"- {message}", file=sys.stderr)
    raise SystemExit(1)

print("RCS-015 validation passed")
print(
    f"validated {len(REQUIRED_FILES)} handoff artifacts, "
    f"{len(REQUIRED_ISSUES)} production issues, and "
    f"{len(REQUIRED_ESCAPE_ROUTES)} integration escape routes"
)
