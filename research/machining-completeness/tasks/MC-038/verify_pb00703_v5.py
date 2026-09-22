#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00703-parametric-patch-boundary-v5.json"
REPORT = TASK / "pb00703-report-v5.md"
DOC = ROOT / "docs" / "machining-completeness" / "32-PB00703-EXACT-PARAMETRIC-PATCH-BOUNDARY.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "a4ca147c54827ef30f1192a4a29b72980a91722c"
EXPECTED_V4 = {
    "research/machining-completeness/tasks/MC-038/pb00703-source-codec-boundary-v4.json": "1a69ad4073a38d0448474fa8046657266a3b79e8",
    "research/machining-completeness/tasks/MC-038/pb00703_source_codec.py": "87429f3aa42692222287e62762d08c01b989a61c",
    "research/machining-completeness/tasks/MC-038/verify_pb00703.py": "722b709f16fc719e5a47b46d4693eae270e1a376",
    "research/machining-completeness/tasks/MC-038/pb00703-report-v4.md": "03b76486a581ab10fc9c7fd89d4903192400cb7b",
    "docs/machining-completeness/28-PB00703-EXACT-SOURCE-CODEC-BOUNDARY.md": "7ae0df2ff8ac9b9733c60a0d3629dffa4ebf00e8",
}

sys.path.insert(0, str(TASK))
import pb00703_parametric_patch as patch  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00703-parametric-patch-boundary/5.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 174
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-03"
    assert artifact["decision"] == "EXACT_RATIONAL_PARAMETRIC_BOUNDARY_SUBROUTE_ESTABLISHED_FULL_BLOCKER_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v4_evidence"]}
    assert set(history) == set(EXPECTED_V4)
    for path, sha in EXPECTED_V4.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    required = artifact["required_source_domain"]
    assert required["domain_operation_count"] == 26
    assert required["domain_narrowed"] is False
    assert set(required["relevant_source_families"]) == {
        "imported_stock", "lathe_form_tool", "mill_form", "mill_accessible_undercut"
    }
    assert required["opaque_import_success_is_not_exact_source_authority"] is True
    assert required["missing_constructor_is_gap_not_exclusion"] is True

    route = artifact["implemented_bounded_subroute"]
    assert route["id"] == "EXACT_RATIONAL_TENSOR_PRODUCT_PARAMETRIC_BOUNDARY_V1"
    assert route["scalar_domain"] == "exact rational"
    assert "Cox-de Boor" in route["basis"]
    assert "source_uncertainty" in route["required_binding"]
    assert any("inside/outside" in claim for claim in route["not_claimed"])
    assert any("opaque STEP" in claim for claim in route["not_claimed"])

    controls = artifact["boundary_controls"]
    for token in (
        "bilinear", "rational weighted", "1/1000000", "repeated knots",
        "zero-width", "ragged", "nonpositive", "binary-float",
        "parameter-domain", "unsupported trims", "opaque STEP", "UNCERTIFIED_SOURCE",
        "MC-B promotion",
    ):
        assert any(token in item for item in controls), f"missing control: {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert "closed oriented shell" in review["reason"]
    assert "source-solid" in review["residual_obligation"]
    assert {"opaque importer success", "kernel-valid B-rep", "fake watertight flag"} <= set(review["authority_laundering_forbidden"])

    effect = artifact["programme_effect"]
    assert effect == {
        "PB-007-01": "OPEN",
        "PB-007-02": "OPEN_DEPENDS_ON_PB-007-01",
        "PB-007-03": "OPEN",
        "PB-007-04": "OPEN_PROPAGATED",
        "PO-02": "OPEN",
        "PO-05": "OPEN",
        "MC-B": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }
    assert artifact["resources"] and not any(artifact["resources"].values())
    assert all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    domain = load(DOMAIN)
    assert len(domain["coverage_rule"]["required_operation_ids"]) == 26
    for path, sha in EXPECTED_V4.items():
        assert git_blob_sha(ROOT / path) == sha, f"historical v4 drift: {path}"

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
            "pb-007-03", "remains open", "not_established", "26-operation",
            "source/audio/provenance", "source uncertainty", "holder/access",
            "step", "trim", "shell", "boundary",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00703_parametric_patch.py" in workflow
    assert "verify_pb00703_v5.py --contract" in workflow
    assert "verify_pb00703_v5.py --self-test" in workflow


def sample_patch():
    return {
        "schema": patch.SCHEMA,
        "source_id": "weighted-source",
        "patch_id": "weighted-patch",
        "role": "cutting",
        "units": "mm",
        "frame_id": "workpiece-v1",
        "u_parameter_id": "u-source",
        "v_parameter_id": "v-source",
        "degree_u": 1,
        "degree_v": 1,
        "knots_u": ["0", "0", "1", "1"],
        "knots_v": ["0", "0", "1", "1"],
        "parameter_domain_u": ["0", "1"],
        "parameter_domain_v": ["0", "1"],
        "control_points": [
            [["0", "0", "0"], ["0", "1", "0"]],
            [["1", "0", "0"], ["1", "1", "1"]],
        ],
        "weights": [["1", "1"], ["1", "2"]],
        "source_uncertainty": "0",
        "authority_kind": "BOUNDARY_PATCH_ONLY",
    }


def expect_rejected(mutator):
    src = sample_patch()
    mutator(src)
    result = patch.classify_source_descriptor(src)
    assert result["status"] == "SEMANTIC_BLOCKER", result


def run_model_controls():
    src = sample_patch()
    mid = patch.evaluate_patch(src, "1/2", "1/2")
    assert mid["point"] == ["3/5", "3/5", "2/5"]
    assert mid["solid_membership_certified"] is False
    assert patch.evaluate_patch(src, "1", "1")["point"] == ["1/1", "1/1", "1/1"]

    lo = patch.evaluate_patch(src, "499999/1000000", "1/2")["point"]
    hi = patch.evaluate_patch(src, "500001/1000000", "1/2")["point"]
    assert lo != hi

    rep = copy.deepcopy(src)
    rep["source_id"] = "repeated-knot"
    rep["degree_u"] = 2
    rep["knots_u"] = ["0", "0", "0", "1/2", "1/2", "1", "1", "1"]
    rep["control_points"] = [
        [["0", "0", "0"], ["0", "1", "0"]],
        [["1/4", "0", "0"], ["1/4", "1", "0"]],
        [["1/2", "0", "0"], ["1/2", "1", "0"]],
        [["3/4", "0", "0"], ["3/4", "1", "0"]],
        [["1", "0", "0"], ["1", "1", "0"]],
    ]
    rep["weights"] = [["1", "1"] for _ in range(5)]
    assert patch.evaluate_patch(rep, "1/2", "1/2")["point"] == ["1/2", "1/2", "0/1"]
    assert patch.evaluate_patch(rep, "499999/1000000", "1/2")["point"] != patch.evaluate_patch(rep, "500001/1000000", "1/2")["point"]

    equiv = copy.deepcopy(src)
    equiv["weights"][0][0] = "2/2"
    equiv["control_points"][0][0][0] = "0/7"
    assert patch.source_sha256(equiv) == patch.source_sha256(src)
    changed = copy.deepcopy(src)
    changed["frame_id"] = "other-frame"
    assert patch.source_sha256(changed) != patch.source_sha256(src)

    uncertain = copy.deepcopy(src)
    uncertain["source_id"] = "uncertain"
    uncertain["source_uncertainty"] = "1/1000000"
    assert patch.evaluate_patch(uncertain, "1/2", "1/2")["status"] == "UNCERTIFIED_SOURCE"

    for opaque in (
        {"representation": "STEP", "kernel_valid": True},
        {"representation": "NURBS_BREP", "import_success": True},
        {"representation": "mesh", "watertight": True},
    ):
        result = patch.classify_source_descriptor(opaque)
        assert result["status"] == "BLOCKED" and result["blocker"] == "PB-007-03"

    membership = patch.request_solid_membership(src, ["0", "0", "0"], shell_certificate={"watertight": True})
    assert membership["status"] == "BLOCKED"
    assert membership["shell_certificate_consumed"] is False

    expect_rejected(lambda s: s.__setitem__("trim_curves", []))
    expect_rejected(lambda s: s.__setitem__("closed_shell", True))
    expect_rejected(lambda s: s["weights"][0].__setitem__(0, "0"))
    expect_rejected(lambda s: s["weights"][0].__setitem__(0, "-1"))
    expect_rejected(lambda s: s["weights"][0].__setitem__(0, 1.0))
    expect_rejected(lambda s: s["control_points"][0][0].__setitem__(0, 0.0))
    expect_rejected(lambda s: s["knots_u"].__setitem__(2, 0.5))
    expect_rejected(lambda s: s["knots_u"].__setitem__(2, "2"))
    expect_rejected(lambda s: s.__setitem__("knots_u", ["0", "0", "1"]))
    expect_rejected(lambda s: s["control_points"].__setitem__(1, s["control_points"][1][:-1]))
    expect_rejected(lambda s: s.__setitem__("parameter_domain_u", ["0", "2"]))
    expect_rejected(lambda s: s.__setitem__("role", "geometry"))
    expect_rejected(lambda s: s.__setitem__("units", ""))
    expect_rejected(lambda s: s.__setitem__("frame_id", ""))
    expect_rejected(lambda s: s.__setitem__("u_parameter_id", s["v_parameter_id"]))

    try:
        patch.evaluate_patch(src, 0.5, "1/2")
    except TypeError:
        pass
    else:
        raise AssertionError("binary-float parameter accepted as exact authority")


def expect_artifact_rejected(mutator):
    artifact = copy.deepcopy(load(ARTIFACT))
    mutator(artifact)
    try:
        validate_artifact(artifact, check_repo=False)
    except Exception:
        return
    raise AssertionError("adversarial artifact mutation accepted")


def run_artifact_controls():
    expect_artifact_rejected(lambda a: a["full_blocker_review"].__setitem__("status", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("PB-007-03", "CLOSED"))
    expect_artifact_rejected(lambda a: a["programme_effect"].__setitem__("MC-B", "ACCEPTED"))
    expect_artifact_rejected(lambda a: a["required_source_domain"].__setitem__("domain_operation_count", 25))
    expect_artifact_rejected(lambda a: a["required_source_domain"].__setitem__("domain_narrowed", True))
    expect_artifact_rejected(lambda a: a["resources"].__setitem__("native_campaign", True))
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("holder_access", False))
    expect_artifact_rejected(lambda a: a["historical_v4_evidence"][0].__setitem__("git_blob_sha1", "forged"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-03 v5 contract: PASS")
    if args.self_test:
        validate_artifact(load(ARTIFACT), check_repo=False)
        run_model_controls()
        run_artifact_controls()
        print("PB-007-03 v5 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
