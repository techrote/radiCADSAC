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

HUMAN_FILES = (
    HANDOFF / "README.md",
    HANDOFF / "00-FOUNDING-SPEC.md",
    HANDOFF / "01-IMPLEMENTATION-ROADMAP.md",
    HANDOFF / "02-INITIAL-ISSUE-GRAPH.md",
    HANDOFF / "03-UNRESOLVED-RESEARCH-REGISTER.md",
    HANDOFF / "04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md",
)
MANIFEST = HANDOFF / "handoff-v1.json"
REQUIRED_FILES = HUMAN_FILES + (MANIFEST,)

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
    if manifest.get("schema") != "opensimachinist-handoff/1.0":
        fail("handoff schema must be opensimachinist-handoff/1.0")
    if manifest.get("status") != "gate-3-candidate":
        fail("handoff status must be gate-3-candidate")
    if manifest.get("architecture") != "semantic-provider-hybrid-v1":
        fail("handoff must inherit semantic-provider-hybrid-v1")
    source_main = manifest.get("source_main")
    if not isinstance(source_main, str) or not re.fullmatch(r"[0-9a-f]{40}", source_main):
        fail("source_main must be a lowercase 40-character commit SHA")

    contracts = manifest.get("programme_contracts")
    if not isinstance(contracts, dict):
        fail("programme_contracts must be an object")
    else:
        for key in ("external_boundary", "journal", "step", "architecture_decision"):
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

    gate3 = manifest.get("gate3")
    if not isinstance(gate3, dict):
        fail("gate3 must be an object")
    else:
        criteria = gate3.get("criteria")
        if not isinstance(criteria, dict) or set(criteria) != REQUIRED_GATE3:
            fail("gate3.criteria must contain exactly the roadmap Gate-3 requirements")
        elif any(value != "satisfied" for value in criteria.values()):
            fail("every Gate-3 content criterion must be marked satisfied")
        assertion = str(gate3.get("assertion", "")).casefold()
        if "does not assert" not in assertion or "merged" not in assertion:
            fail("Gate-3 assertion must distinguish merged handoff completion from unresolved research")

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
            if not isinstance(issue_id, str) or not re.fullmatch(r"OSM-\d{3}", issue_id):
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

    unresolved = manifest.get("unresolved_ids")
    if not isinstance(unresolved, list) or set(unresolved) != REQUIRED_UNRESOLVED:
        fail("unresolved_ids must preserve the complete RCS-013 unresolved set")

readme = read(HANDOFF / "README.md")
require_terms(
    readme,
    (
        "semantic-provider-hybrid-v1",
        "Gate 3",
        "production repository must be created separately",
        "Negative research",
    ),
    "handoff README",
)

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
        fail(f"founding specification missing heading: {heading}")
require_terms(
    founding,
    (
        "msac-journal/1.0",
        "msac-step-conformance/1.0",
        "b8f597c677811d1f9f4d8a97f5ae2825c0353a42",
        "interoperability_unqualified",
        "accepted_pending",
        "refused_unsupported",
        "MANIFOLD_SOLID_BREP",
        "all material bodies",
        "one fuzzy epsilon",
    ),
    "founding specification",
)

roadmap = read(HANDOFF / "01-IMPLEMENTATION-ROADMAP.md")
for stage in range(8):
    if f"## Stage {stage}" not in roadmap:
        fail(f"implementation roadmap missing Stage {stage}")
require_terms(roadmap, ("measurable vertical slices",), "implementation roadmap")
if roadmap.count("Measurable exit:") < 8:
    fail("every numbered roadmap stage must have a measurable exit")

issues_doc = read(HANDOFF / "02-INITIAL-ISSUE-GRAPH.md")
for issue_id in sorted(REQUIRED_ISSUES):
    if f"## {issue_id} —" not in issues_doc:
        fail(f"initial issue document missing section for {issue_id}")

# Validate execution semantics per issue rather than requiring identical prose.
sections = re.split(r"(?=^## OSM-\d{3} —)", issues_doc, flags=re.MULTILINE)
issue_sections = [section for section in sections if re.match(r"^## OSM-\d{3} —", section)]
if len(issue_sections) != len(REQUIRED_ISSUES):
    fail(f"expected 15 issue sections, observed {len(issue_sections)}")
for section in issue_sections:
    match = re.match(r"^## (OSM-\d{3}) —", section)
    issue_id = match.group(1) if match else "unknown"
    lower = section.casefold()
    for term in (
        "work on a branch",
        "open a pr",
        "automated checks",
        "merge only after all required checks pass",
        "verify the merge landed on `main`",
        "acceptance criteria",
    ):
        if term not in lower:
            fail(f"{issue_id} autonomous prompt missing execution requirement: {term!r}")

unresolved_doc = read(HANDOFF / "03-UNRESOLVED-RESEARCH-REGISTER.md")
for priority in range(1, 12):
    if f"Priority {priority}" not in unresolved_doc:
        fail(f"unresolved register missing Priority {priority}")
require_terms(
    unresolved_doc,
    ("## Escape-route doctrine", "defer", "handoff", "bounded fallback", "refuse"),
    "unresolved register",
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
    ),
    "bootstrap checklist",
)

if errors:
    print("RCS-014 validation FAILED", file=sys.stderr)
    for message in errors:
        print(f"- {message}", file=sys.stderr)
    raise SystemExit(1)

print("RCS-014 validation passed")
print(
    f"validated {len(REQUIRED_FILES)} handoff artifacts, "
    f"{len(REQUIRED_ISSUES)} production issues, and "
    f"{len(REQUIRED_UNRESOLVED)} unresolved items"
)
