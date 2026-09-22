#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00703-source-codec-boundary-v4.json"
REPORT = TASK / "pb00703-report-v4.md"
DOC = ROOT / "docs" / "machining-completeness" / "28-PB00703-EXACT-SOURCE-CODEC-BOUNDARY.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "c762ba3a7c5ceff81e7c8ec2f5c37c21e1aa758c"
EXPECTED_HISTORY = {
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json": "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/tasks/MC-003/numeric-encoding-contract-v1.json": "a5538cab698c806fdedcef7cf563b650638348e0",
    "research/machining-completeness/tasks/MC-006/outcome.json": "0319e00b492c57e4a11e3e78ef9a2e15ff67e52e",
    "research/machining-completeness/tasks/MC-020/outcome.json": "19504a35f47bca710bb6369abb723de83d1afede",
    "research/machining-completeness/tasks/MC-031/outcome.json": "dffac14b7e1381f966641485827b2df968d92144",
    "research/machining-completeness/tasks/MC-038/gate-scope-retry-v2.json": "76094029a264a5ce226694548b27896f9e0cd430",
    "research/machining-completeness/tasks/MC-038/pb00701-decision-boundary-v3.json": "ec2edaef5ef1cf838fc91e68b25147f41525ac2a",
}
RELEVANT_FAMILIES = {"imported_stock", "lathe_form_tool", "mill_form", "mill_accessible_undercut"}

sys.path.insert(0, str(TASK))
import pb00703_source_codec as codec  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def domain_operation_count() -> int:
    return len(load(DOMAIN)["coverage_rule"]["required_operation_ids"])


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00703-source-codec-boundary/4.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 166
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-03"
    assert artifact["decision"] == "BOUNDED_EXACT_SOURCE_CODEC_ESTABLISHED_FULL_BLOCKER_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_evidence"]}
    assert set(history) == set(EXPECTED_HISTORY)
    for path, sha in EXPECTED_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    required = artifact["required_source_domain"]
    assert required["domain_operation_count"] == 26
    assert required["domain_narrowed"] is False
    assert set(required["relevant_source_families"]) == RELEVANT_FAMILIES
    assert required["import_success_is_not_validity"] is True
    assert required["missing_constructor_is_gap_not_exclusion"] is True
    assert required["source_uncertainty_is_separate_from_nominal_geometry"] is True
    assert required["cutting_and_noncutting_tool_regions_remain_distinct"] is True
    assert required["finite_source_extent_required"] is True

    route = artifact["implemented_bounded_subroute"]
    assert route["id"] == "EXACT_RATIONAL_SEMIALGEBRAIC_SOURCE_V1"
    assert route["scalar_domain"] == "exact rational only"
    assert "ordered difference" in route["solid_grammar"]
    assert "source_uncertainty" in route["required_binding"]
    assert any("opaque STEP" in claim for claim in route["established_claims"])
    assert any("every admitted imported_stock" in claim for claim in route["not_claimed"])
    assert any("engineering-output" in claim for claim in route["not_claimed"])

    controls = artifact["boundary_controls"]
    for token in (
        "box", "unit-sphere", "nonconvex", "1/1000000", "holder", "binary-float",
        "units/frame/source", "opaque STEP", "UNCERTIFIED_SOURCE", "canonical source hashing", "fails closed",
    ):
        assert any(token in item for item in controls), f"missing control: {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert "missing-constructor-is-gap" in review["reason"]
    assert "universal finite source representation" in review["residual_obligation"]
    forbidden = set(review["authority_laundering_forbidden"])
    assert {"opaque importer success", "mesh/tessellation equality", "binary floating coordinates", "global tolerance"} <= forbidden

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDS_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"] == "OPEN_PROPAGATED"
    assert effect["PO-02"] == "OPEN"
    assert effect["PO-05"] == "OPEN"
    assert effect["MC-B"] == "NOT_ESTABLISHED"
    assert effect["MC-1"] == "NOT_ESTABLISHED"

    resources = artifact["resources"]
    assert resources and not any(resources.values())
    assert all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    assert domain_operation_count() == 26, "frozen operation denominator drift"
    for path, sha in EXPECTED_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"historical evidence drift: {path}"

    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False

    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    assert proofs["PO-02"]["state"] == "OPEN"
    assert proofs["PO-05"]["state"] == "OPEN"

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-03", "remains open", "mc-b", "not_established", "26-operation",
            "source/audio/provenance", "source uncertainty", "holder", "opaque", "step",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00703_source_codec.py" in workflow
    assert "verify_pb00703.py --contract" in workflow
    assert "verify_pb00703.py --self-test" in workflow


def atom(op, *terms):
    return {
        "op": op,
        "terms": [
            {"coefficient": coefficient, "exponents": list(exponents)}
            for coefficient, exponents in terms
        ],
    }


def source(source_id, role, solid, bounds=None, uncertainty="0"):
    return {
        "schema": codec.SCHEMA,
        "source_id": source_id,
        "role": role,
        "units": "mm",
        "frame_id": "workpiece-v1",
        "bounds": bounds or {"x": ["-2", "2"], "y": ["-2", "2"], "z": ["-2", "2"]},
        "solid": solid,
        "source_uncertainty": uncertainty,
    }


def run_model_controls():
    cube = source("cube", "stock", codec.box_solid("-1", "1", "-1", "1", "-1", "1"))
    assert codec.classify_certifying_point(cube, ["0", "0", "0"])["relation"] == "INSIDE"
    assert codec.classify_certifying_point(cube, ["3/2", "0", "0"])["relation"] == "OUTSIDE"
    boundary = codec.classify_certifying_point(cube, ["1", "0", "0"])
    assert boundary["relation"] == "BOUNDARY_CANDIDATE"
    assert boundary["closed_predicate_membership"] is True

    sphere = source("sphere", "stock", codec.unit_sphere_solid())
    exact = codec.classify_certifying_point(sphere, ["1", "0", "0"])
    inside = codec.classify_certifying_point(sphere, ["999999/1000000", "0", "0"])
    outside = codec.classify_certifying_point(sphere, ["1000001/1000000", "0", "0"])
    assert exact["relation"] == "BOUNDARY_CANDIDATE"
    assert inside["relation"] == "INSIDE"
    assert outside["relation"] == "OUTSIDE"

    # Reentrant L-shape: union of two thin rectangular arms, excluding the upper-right quadrant.
    lshape = source(
        "lshape", "cutting",
        {
            "op": "union",
            "children": [
                codec.box_solid("0", "2", "0", "1", "0", "1"),
                codec.box_solid("0", "1", "0", "2", "0", "1"),
            ],
        },
        bounds={"x": ["-1", "3"], "y": ["-1", "3"], "z": ["-1", "2"]},
    )
    assert codec.classify_certifying_point(lshape, ["3/2", "1/2", "1/2"])["relation"] == "INSIDE"
    assert codec.classify_certifying_point(lshape, ["1/2", "3/2", "1/2"])["relation"] == "INSIDE"
    assert codec.classify_certifying_point(lshape, ["3/2", "3/2", "1/2"])["relation"] == "OUTSIDE"

    micro = source(
        "micro-positive-volume", "cutting",
        codec.box_solid("0", "1/1000000", "0", "1/1000000", "0", "1/1000000"),
        bounds={"x": ["-1/1000000", "2/1000000"], "y": ["-1/1000000", "2/1000000"], "z": ["-1/1000000", "2/1000000"]},
    )
    assert codec.classify_certifying_point(micro, ["1/2000000", "1/2000000", "1/2000000"])["relation"] == "INSIDE"
    assert codec.classify_certifying_point(micro, ["0", "1/2000000", "1/2000000"])["relation"] == "BOUNDARY_CANDIDATE"
    assert codec.classify_certifying_point(micro, ["-1/2000000", "1/2000000", "1/2000000"])["relation"] == "OUTSIDE"

    holder = source("holder", "holder", codec.box_solid("-1", "1", "-1", "1", "1", "2"))
    bundle = codec.validate_tool_bundle(lshape, holder)
    assert bundle["status"] == "EXACT_NOMINAL_TOOL_BUNDLE"
    assert bundle["access_certified"] is False
    assert bundle["cutting_sha256"] != bundle["holder_sha256"]

    uncertain = copy.deepcopy(sphere)
    uncertain["source_id"] = "sphere-measured"
    uncertain["source_uncertainty"] = "1/1000000"
    cert = codec.classify_certifying_point(uncertain, ["0", "0", "0"])
    assert cert["status"] == "UNCERTIFIED_SOURCE"
    assert cert["is_exact_material_truth"] is False
    assert codec.classify_nominal_point(uncertain, ["0", "0", "0"])["relation"] == "INSIDE"

    # Canonicalization is invariant to commutative/term order but remains source-identity bound.
    reordered = copy.deepcopy(lshape)
    reordered["solid"]["children"].reverse()
    for child in reordered["solid"]["children"]:
        for atom_node in child["children"]:
            atom_node["terms"].reverse()
    assert codec.source_sha256(reordered) == codec.source_sha256(lshape)
    renamed = copy.deepcopy(lshape)
    renamed["source_id"] = "other-source"
    assert codec.source_sha256(renamed) != codec.source_sha256(lshape)

    for opaque in (
        {"representation": "STEP", "import_success": True},
        {"representation": "mesh", "manifold": True},
        {"representation": "AABB", "source_id": "shortcut"},
        {"representation": "NURBS_BREP", "kernel_valid": True},
    ):
        result = codec.classify_source_descriptor(opaque)
        assert result["status"] == "BLOCKED"
        assert result["blocker"] == "PB-007-03"

    float_source = copy.deepcopy(sphere)
    float_source["solid"]["terms"][0]["coefficient"] = 1.0
    result = codec.classify_source_descriptor(float_source)
    assert result["status"] == "SEMANTIC_BLOCKER"

    try:
        codec.classify_certifying_point(sphere, [1.0, 0, 0])
    except TypeError:
        pass
    else:
        raise AssertionError("binary-float point accepted as exact authority")

    missing = copy.deepcopy(sphere)
    del missing["frame_id"]
    assert codec.classify_source_descriptor(missing)["status"] == "SEMANTIC_BLOCKER"

    unbounded = copy.deepcopy(sphere)
    del unbounded["bounds"]
    assert codec.classify_source_descriptor(unbounded)["status"] == "SEMANTIC_BLOCKER"

    fake_holder = copy.deepcopy(holder)
    fake_holder["role"] = "cutting"
    try:
        codec.validate_tool_bundle(lshape, fake_holder)
    except ValueError:
        pass
    else:
        raise AssertionError("holder-role erasure accepted")


def expect_artifact_rejected(mutator):
    artifact = copy.deepcopy(load(ARTIFACT))
    mutator(artifact)
    try:
        validate_artifact(artifact, check_repo=False)
    except Exception:
        return
    raise AssertionError("adversarial artifact mutation accepted")


def run_adversarial_artifact_controls():
    expect_artifact_rejected(lambda a: a["full_blocker_review"].__setitem__("status", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("PB-007-03", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("MC-B", "ACCEPTED"))
    expect_artifact_rejected(lambda a: a["required_source_domain"].__setitem__("domain_operation_count", 25))
    expect_artifact_rejected(lambda a: a["required_source_domain"].__setitem__("domain_narrowed", True))
    expect_artifact_rejected(lambda a: a["required_source_domain"].__setitem__("source_uncertainty_is_separate_from_nominal_geometry", False))
    expect_artifact_rejected(lambda a: a["required_source_domain"].__setitem__("cutting_and_noncutting_tool_regions_remain_distinct", False))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign_run", True))
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("positive_volume_material_preserved", False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        args.contract = args.self_test = True
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-03 source-codec contract: PASS")
    if args.self_test:
        run_model_controls()
        run_adversarial_artifact_controls()
        print("PB-007-03 exact-source/adversarial controls: PASS")


if __name__ == "__main__":
    main()
