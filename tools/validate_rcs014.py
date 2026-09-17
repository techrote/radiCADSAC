#!/usr/bin/env python3
"""Validate the clean OpenSimachinist founding handoff produced by RCS-014."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoffs/opensimachinist"

REQUIRED_FILES = (
    HANDOFF / "README.md",
    HANDOFF / "00-FOUNDING-SPEC.md",
    HANDOFF / "01-IMPLEMENTATION-ROADMAP.md",
    HANDOFF / "02-INITIAL-ISSUE-GRAPH.md",
    HANDOFF / "03-UNRESOLVED-RESEARCH-REGISTER.md",
    HANDOFF / "04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md",
    HANDOFF / "handoff-v1.json",
)

REQUIRED_GATE3 = {
    "initial_backend_architecture_decision",
    "stable_programme_facing_api_contract",
    "explicit_unresolved_research_register",
    "baseline_test_corpus_and_benchmark_design",
    "licensing_and_provenance_plan",
    "step_acceptance_contract",
    "staged_implementation_roadmap_with_measurable_milestones",
}

REQUIRED_ISSUES = {f"OSM-{i:03d}" for i in range(1, 16)}
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
    "live-tool-and-non-axisymmetric-lathe",
}

REQUIRED_EVIDENCE_KEYS = {
    "step_primary_output",
    "journal_is_durable_intent",
    "lathe_and_mill_initial_scope",
    "stable_backend_boundary",
    "pathological_inputs_are_normal",
    "canonical_numerics_frames",
    "bounded_canonicalization",
    "immutable_revisions_body_transitions",
    "separate_tolerance_channels",
    "semantic_lineage",
    "bounded_deferred_topology",
    "axisymmetric_lathe_provider",
    "mill_strategy_hierarchy",
    "bounded_hybrid_fallbacks",
    "selected_architecture",
}

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def load_object(path: Path) -> dict[str, Any]:
    text = read(path)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        error(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"JSON root must be object: {path.relative_to(ROOT)}")
        return {}
    return value


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

manifest_path = HANDOFF / "handoff-v1.json"
manifest = load_object(manifest_path)
if manifest:
    if manifest.get("schema") != "opensimachinist-handoff/1.0":
        error("handoff schema must be opensimachinist-handoff/1.0")
    if manifest.get("status") != "gate-3-candidate":
        error("handoff status must be gate-3-candidate before/through RCS-014 merge")
    if manifest.get("architecture") != "semantic-provider-hybrid-v1":
        error("handoff must inherit semantic-provider-hybrid-v1")
    source_main = manifest.get("source_main")
    if not isinstance(source_main, str) or not re.fullmatch(r"[0-9a-f]{40}", source_main):
        error("source_main must be a lowercase 40-character commit SHA")

    contracts = manifest.get("programme_contracts")
    if not isinstance(contracts, dict):
        error("programme_contracts must be an object")
    else:
        for key in ("external_boundary", "journal", "step", "architecture_decision"):
            path_text = contracts.get(key)
            if not isinstance(path_text, str) or not path_text:
                error(f"programme_contracts.{key} must be a path string")
            elif not (ROOT / path_text).is_file():
                error(f"programme contract path does not exist: {path_text}")

    listed_files = manifest.get("handoff_files")
    expected_paths = {str(path.relative_to(ROOT)) for path in REQUIRED_FILES if path.name != "handoff-v1.json"}
    if not isinstance(listed_files, list) or set(listed_files) != expected_paths:
        error("handoff_files must list exactly the six human-readable handoff documents")

    evidence = manifest.get("major_decision_evidence")
    if not isinstance(evidence, dict):
        error("major_decision_evidence must be an object")
    else:
        missing = REQUIRED_EVIDENCE_KEYS - set(evidence)
        if missing:
            error(f"major decision evidence missing keys: {sorted(missing)}")
        for key, paths in evidence.items():
            if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p for p in paths):
                error(f"major_decision_evidence.{key} must be a non-empty path list")
                continue
            for path_text in paths:
                if not (ROOT / path_text).is_file():
                    error(f"evidence source does not exist: {path_text}")

    gate3 = manifest.get("gate3")
    if not isinstance(gate3, dict):
        error("gate3 must be an object")
    else:
        criteria = gate3.get("criteria")
        if not isinstance(criteria, dict) or set(criteria) != REQUIRED_GATE3:
            error("gate3.criteria must contain exactly the roadmap Gate-3 requirements")
        elif any(value != "satisfied" for value in criteria.values()):
            error("every Gate-3 content criterion must be marked satisfied")
        assertion = str(gate3.get("assertion", ""))
        if "does not assert" not in assertion or "merged" not in assertion:
            error("Gate-3 assertion must distinguish handoff completion from unresolved research")

    issue_graph = manifest.get("production_issue_graph")
    issue_ids: set[str] = set()
    deps_by_id: dict[str, list[str]] = {}
    if not isinstance(issue_graph, list):
        error("production_issue_graph must be a list")
    else:
        for index, item in enumerate(issue_graph):
            if not isinstance(item, dict):
                error(f"production_issue_graph[{index}] must be an object")
                continue
            issue_id = item.get("id")
            title = item.get("title")
            deps = item.get("depends_on")
            if not isinstance(issue_id, str) or not re.fullmatch(r"OSM-\d{3}", issue_id):
                error(f"invalid issue id at production_issue_graph[{index}]")
                continue
            if issue_id in issue_ids:
                error(f"duplicate production issue id: {issue_id}")
            issue_ids.add(issue_id)
            if not isinstance(title, str) or not title.strip():
                error(f"{issue_id} title must be non-empty")
            if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
                error(f"{issue_id} depends_on must be a string list")
                deps_by_id[issue_id] = []
            else:
                deps_by_id[issue_id] = deps
        if issue_ids != REQUIRED_ISSUES:
            error(f"production issue set mismatch: expected {sorted(REQUIRED_ISSUES)}, got {sorted(issue_ids)}")
        for issue_id, deps in deps_by_id.items():
            for dep in deps:
                if dep not in issue_ids:
                    error(f"{issue_id} depends on unknown issue {dep}")
                if dep == issue_id:
                    error(f"{issue_id} cannot depend on itself")

        # DAG check.
        temporary: set[str] = set()
        permanent: set[str] = set()
        def visit(node: str) -> None:
            if node in permanent:
                return
            if node in temporary:
                error(f"production issue graph contains a dependency cycle at {node}")
                return
            temporary.add(node)
            for dep in deps_by_id.get(node, []):
                if dep in issue_ids:
                    visit(dep)
            temporary.remove(node)
            permanent.add(node)
        for issue_id in sorted(issue_ids):
            visit(issue_id)

    unresolved = manifest.get("unresolved_ids")
    if not isinstance(unresolved, list) or set(unresolved) != REQUIRED_UNRESOLVED:
        error("unresolved_ids must preserve the complete RCS-013 unresolved set")

readme = read(HANDOFF / "README.md")
for token in (
    "semantic-provider-hybrid-v1",
    "Gate 3",
    "production repository must be created separately",
    "Negative research",
):
    if token not in readme:
        error(f"handoff README missing required statement: {token!r}")

founding = read(HANDOFF / "00-FOUNDING-SPEC.md")
for heading in (
    "## Product and kernel brief",
    "## Non-negotiable invariants",
    "## Stable programme-facing API contract",
    "## Canonical journal expectations at backend ingress",
    "## Selected component architecture",
    "## Representation and reconciliation strategy",
    "## Axisymmetric lathe provider — initial scope",
    "## Mill provider — initial scope and hierarchy",
    "## Tolerance, uncertainty, provenance and topology policies",
    "## STEP conformance contract",
    "## Programme-facing error and status model",
    "## Benchmark and corpus strategy",
    "## Dependency, license and upstream provenance plan",
    "## Build and platform assumptions",
    "## Evidence map for inherited decisions",
):
    if heading not in founding:
        error(f"founding specification missing heading: {heading}")
for token in (
    "msac-journal/1.0",
    "msac-step-conformance/1.0",
    "b8f597c677811d1f9f4d8a97f5ae2825c0353a42",
    "interoperability_unqualified",
    "accepted_pending",
    "refused_unsupported",
    "MANIFOLD_SOLID_BREP",
    "all material bodies",
    "one fuzzy epsilon",
):
    if token not in founding:
        error(f"founding specification missing required term: {token!r}")

roadmap = read(HANDOFF / "01-IMPLEMENTATION-ROADMAP.md")
for stage in range(0, 8):
    if f"## Stage {stage}" not in roadmap:
        error(f"implementation roadmap missing Stage {stage}")
if "measurable vertical slices" not in roadmap.lower():
    error("implementation roadmap must explicitly start from measurable vertical slices")
if roadmap.count("Measurable exit:") < 8:
    error("every numbered roadmap stage must have a measurable exit")

issues_doc = read(HANDOFF / "02-INITIAL-ISSUE-GRAPH.md")
for issue_id in sorted(REQUIRED_ISSUES):
    if f"## {issue_id} —" not in issues_doc:
        error(f"initial issue document missing section for {issue_id}")
required_execution = (
    "Work on a branch. Open a PR. Add/repair automated checks. "
    "Merge only after all required checks pass. Verify the merge landed on `main`; "
    "close only when the acceptance criteria are genuinely satisfied."
)
if issues_doc.count(required_execution) < 15:
    error("every initial production issue must repeat the autonomous branch/PR/checks/merge/verify protocol")

unresolved_doc = read(HANDOFF / "03-UNRESOLVED-RESEARCH-REGISTER.md")
for label in (
    "Priority 1",
    "Priority 2",
    "Priority 3",
    "Priority 4",
    "Priority 5",
    "Priority 6",
    "Priority 7",
    "Priority 8",
    "Priority 9",
    "Priority 10",
    "Priority 11",
    "## Escape-route doctrine",
):
    if label not in unresolved_doc:
        error(f"unresolved register missing {label!r}")
for token in ("defer", "handoff", "bounded fallback", "refuse"):
    if token not in unresolved_doc.lower():
        error(f"unresolved register missing escape route {token!r}")

bootstrap = read(HANDOFF / "04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md")
for token in (
    "new Git history",
    "Do not copy obsolete/rejected",
    "Linux hosted CI",
    "Windows build path",
    "branch → PR → automated checks → merge → `main` verification",
    "No unresolved research question is asserted as solved",
):
    if token not in bootstrap:
        error(f"bootstrap checklist missing required control: {token!r}")

if errors:
    print("RCS-014 validation FAILED", file=sys.stderr)
    for item in errors:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

print("RCS-014 validation passed")
print(f"validated {len(REQUIRED_FILES)} handoff artifacts, {len(REQUIRED_ISSUES)} production issues, and {len(REQUIRED_UNRESOLVED)} unresolved items")
