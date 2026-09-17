#!/usr/bin/env python3
"""Validate the RCS-016 frozen genesis handoff release.

The validator deliberately checks both documentation completeness and the most
important cross-project contract invariants.  It also verifies that RCS-016 did
not mutate either already-accepted handoff package: the package subtrees must
retain the exact Git tree IDs frozen from the joint baseline.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "handoffs" / "genesis-release-v1.json"
OPEN_MANIFEST = ROOT / "handoffs" / "opensimachinist" / "handoff-v1.json"
MSAC_MANIFEST = ROOT / "handoffs" / "msac" / "handoff-v1.json"
OPEN_SPEC = ROOT / "handoffs" / "opensimachinist" / "00-FOUNDING-SPEC.md"
MSAC_SPEC = ROOT / "handoffs" / "msac" / "00-FOUNDING-SPEC.md"
INDEX = ROOT / "handoffs" / "README.md"
OPEN_LAUNCH = ROOT / "handoffs" / "launch" / "opensimachinist-v1.md"
MSAC_LAUNCH = ROOT / "handoffs" / "launch" / "msac-v1.md"
ROOT_README = ROOT / "README.md"

failures: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def load_json(path: Path) -> dict:
    require(path.is_file(), f"missing JSON file: {path.relative_to(ROOT)}")
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        failures.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}


def text(path: Path) -> str:
    require(path.is_file(), f"missing text file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def git_output(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
        ).strip()
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        failures.append(f"git {' '.join(args)} failed: {exc.output.strip()}")
        return ""


release = load_json(RELEASE)
open_manifest = load_json(OPEN_MANIFEST)
msac_manifest = load_json(MSAC_MANIFEST)
index_text = text(INDEX)
open_spec = text(OPEN_SPEC)
msac_spec = text(MSAC_SPEC)
open_launch = text(OPEN_LAUNCH)
msac_launch = text(MSAC_LAUNCH)
root_readme = text(ROOT_README)

# Freeze identity and release metadata.
require(release.get("schema") == "radicadsac-genesis-freeze/1.0", "wrong release schema")
require(release.get("status") == "frozen-on-main", "release must declare frozen-on-main")
require(release.get("repository") == "techrote/radiCADSAC", "wrong genesis repository")
require(release.get("production_repository_creation_authorized") is False,
        "RCS-016 must not authorize production repository creation")
require(release.get("self_contained") is True, "freeze must declare self-contained handoff")

baseline = release.get("joint_freeze_baseline", {}).get("commit")
require(
    baseline == "7f16e4fe310ac3b5e5a4d08547273efaceff0c7f",
    "joint freeze baseline must be the accepted RCS-015 merge commit",
)

expected_packages = {
    "opensimachinist": {
        "tree": "d4793b03f31bd9fd58efcea94afba2f69fa3f7f3",
        "manifest_blob": "2d53fc62c8ec5866eff686483ac721983df03b64",
        "origin": "2e77ea087b01ac1415c4c76ff1dc0661aab286fb",
        "input": "23519b5989b14f1b0947dca77588729585150115",
        "schema": "opensimachinist-handoff/1.0",
        "path": "handoffs/opensimachinist",
        "manifest_path": "handoffs/opensimachinist/handoff-v1.json",
    },
    "msac": {
        "tree": "e04d53756dd83089d367d756253482bebe791f32",
        "manifest_blob": "2c195f9944f2710426ef7a20eb40d5c3f96bab6a",
        "origin": "7f16e4fe310ac3b5e5a4d08547273efaceff0c7f",
        "input": "2e77ea087b01ac1415c4c76ff1dc0661aab286fb",
        "schema": "msac-handoff/1.0",
        "path": "handoffs/msac",
        "manifest_path": "handoffs/msac/handoff-v1.json",
    },
}

for name, expected in expected_packages.items():
    package = release.get("packages", {}).get(name, {})
    require(package.get("schema") == expected["schema"], f"{name}: schema mismatch")
    require(package.get("origin_merge_commit") == expected["origin"], f"{name}: origin commit mismatch")
    require(package.get("manifest_declared_input_main") == expected["input"], f"{name}: input baseline mismatch")
    require(package.get("package_tree_sha") == expected["tree"], f"{name}: frozen tree metadata mismatch")
    require(package.get("manifest_blob_sha") == expected["manifest_blob"], f"{name}: manifest blob metadata mismatch")

    ls_tree = git_output("ls-tree", "HEAD", expected["path"])
    parts = ls_tree.split()
    actual_tree = parts[2] if len(parts) >= 3 else ""
    require(actual_tree == expected["tree"], f"{name}: accepted handoff subtree was modified ({actual_tree})")

    actual_blob = git_output("hash-object", expected["manifest_path"])
    require(actual_blob == expected["manifest_blob"], f"{name}: manifest content no longer matches frozen blob")

# Existing manifests must still describe their authoring inputs exactly.
require(open_manifest.get("schema") == "opensimachinist-handoff/1.0", "OpenSimachinist manifest schema changed")
require(msac_manifest.get("schema") == "msac-handoff/1.0", "MSAC manifest schema changed")
require(open_manifest.get("source_main") == "23519b5989b14f1b0947dca77588729585150115", "OpenSimachinist source_main drift")
require(msac_manifest.get("source_main") == "2e77ea087b01ac1415c4c76ff1dc0661aab286fb", "MSAC source_main drift")
require(open_manifest.get("architecture") == "semantic-provider-hybrid-v1", "OpenSimachinist architecture drift")
require(msac_manifest.get("backend_architecture") == "semantic-provider-hybrid-v1", "MSAC backend architecture drift")

# Cross-project shared contract paths must be identical.
open_contracts = open_manifest.get("programme_contracts", {})
msac_contracts = msac_manifest.get("programme_contracts", {})
for key in ("external_boundary", "journal", "step"):
    require(open_contracts.get(key) == msac_contracts.get(key), f"shared contract path mismatch: {key}")

shared = release.get("shared_contracts", {})
require(shared.get("external_boundary") == open_contracts.get("external_boundary"), "freeze external-boundary path mismatch")
require(shared.get("journal") == open_contracts.get("journal"), "freeze journal path mismatch")
require(shared.get("step") == open_contracts.get("step"), "freeze STEP path mismatch")
require(shared.get("journal_schema") == "msac-journal/1.0", "wrong journal schema")
require(shared.get("step_profile") == "msac-step-conformance/1.0", "wrong STEP conformance profile")
require(shared.get("backend_architecture") == "semantic-provider-hybrid-v1", "wrong backend architecture")
require(shared.get("preview_authoritative") is False, "preview must remain non-authoritative")
require(shared.get("step_primary_engineering_output") is True, "STEP must remain primary engineering output")
require(shared.get("backend_transport_frozen") is False, "transport must remain replaceable")
require(shared.get("backend_private_types_allowed_in_stable_api") is False, "private backend types leaked into stable API")
require(shared.get("process_isolation_founding_default") is True, "process isolation must remain founding safety default")

request_families = [
    "capabilities",
    "apply_canonical_operations",
    "commit_revision",
    "replay_revision",
    "query_material_state",
    "request_preview",
    "request_reconciliation",
    "inspect_reconciled_geometry",
    "export_step",
]
status_classes = [
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
]
require(shared.get("request_families") == request_families, "release request-family list drift")
require(shared.get("status_classes") == status_classes, "release status-class list drift")

for token in request_families + status_classes + ["msac-journal/1.0", "msac-step-conformance/1.0"]:
    require(token in open_spec, f"OpenSimachinist founding spec missing shared token: {token}")
    require(token in msac_spec, f"MSAC founding spec missing shared token: {token}")

for token in ("preview", "all material bodies", "STEP", "semantic"):
    require(token.lower() in open_spec.lower(), f"OpenSimachinist spec missing boundary concept: {token}")
    require(token.lower() in msac_spec.lower(), f"MSAC spec missing boundary concept: {token}")

# Evidence index must resolve to checked-in files and cover both consumers.
evidence = release.get("evidence_index", [])
require(len(evidence) >= 12, "evidence index is too small to cover the accepted architecture")
for entry in evidence:
    require(set(entry.get("consumers", [])) == {"opensimachinist", "msac"},
            f"evidence entry {entry.get('id')} must map to both handoffs")
    for source in entry.get("sources", []):
        require((ROOT / source).is_file(), f"evidence source missing: {source}")

# Classification must preserve the still-active research item and superseded plan.
classification = release.get("issue_classification", {})
require(classification.get("active_nonblocking_research") == ["RCS-017"], "RCS-017 must remain active non-blocking research")
require(classification.get("active_nonblocking_github_issues") == [20], "RCS-017 GitHub issue mapping must remain #20")
require(classification.get("freeze_issue") == "RCS-016", "wrong freeze issue")
require("docs/02-INITIAL-RESEARCH-PLAN.md" in release.get("document_classification", {}).get("superseded_historical", []),
        "initial plan must be marked superseded/historical")

# Launch wrappers must be self-contained enough to found clean production repos.
launch_requirements = {
    "opensimachinist": (
        open_launch,
        [
            "techrote/OpenSimachinist",
            "d4793b03f31bd9fd58efcea94afba2f69fa3f7f3",
            "README.md",
            "AGENTS.md",
            "CI",
            "OSM-001",
            "OSM-015",
            "licence",
            "provenance",
            "new Git history",
            "RCS-017",
        ],
    ),
    "msac": (
        msac_launch,
        [
            "techrote/MSAC",
            "e04d53756dd83089d367d756253482bebe791f32",
            "README.md",
            "AGENTS.md",
            "CI",
            "MSAC-001",
            "MSAC-015",
            "licence",
            "provenance",
            "new Git history",
        ],
    ),
}
for name, (launch_text, tokens) in launch_requirements.items():
    for token in tokens:
        require(token in launch_text, f"{name} launch wrapper missing: {token}")

# No instruction may rely on conversational context. Negative references that say
# the handoff does *not* depend on conversation are allowed.
forbidden_context_phrases = (
    "as discussed earlier",
    "as we discussed",
    "from our chat",
    "see the chat",
    "see conversation",
    "previous conversation for",
    "earlier conversation for",
)
for path in [
    INDEX,
    OPEN_LAUNCH,
    MSAC_LAUNCH,
    *sorted((ROOT / "handoffs" / "opensimachinist").glob("*.md")),
    *sorted((ROOT / "handoffs" / "msac").glob("*.md")),
]:
    body = text(path).lower()
    for phrase in forbidden_context_phrases:
        require(phrase not in body, f"inaccessible conversational dependency in {path.relative_to(ROOT)}: {phrase}")

# Release/tag procedure must be honest about post-merge creation.
tag_plan = release.get("tag_plan", {})
require(tag_plan.get("created_by_this_pr") is False, "PR must not claim future merge tags already exist")
for tag in ("radiCADSAC-genesis-v1", "opensimachinist-handoff-v1", "msac-handoff-v1"):
    require(tag in index_text, f"handoff index missing tag plan: {tag}")
require("RCS016_MERGE_SHA=$(git rev-parse origin/main)" in index_text, "handoff index missing exact post-merge tag procedure")

# Discoverability from repository root.
require("handoffs/README.md" in root_readme, "root README must link the frozen handoff index")
require("genesis-release-v1.json" in root_readme, "root README must link the machine-readable freeze manifest")

if failures:
    print("RCS-016 validation FAILED:")
    for failure in failures:
        print(f" - {failure}")
    sys.exit(1)

print("RCS-016 validation passed")
print("  frozen OpenSimachinist tree: d4793b03f31bd9fd58efcea94afba2f69fa3f7f3")
print("  frozen MSAC tree:           e04d53756dd83089d367d756253482bebe791f32")
print("  shared journal/API/status/STEP boundary: consistent")
print("  production repository creation: not authorized")
print("  RCS-017: preserved as active non-blocking research")
