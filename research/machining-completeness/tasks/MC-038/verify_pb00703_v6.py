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
ARTIFACT = TASK / "pb00703-trimmed-shell-v6.json"
REPORT = TASK / "pb00703-report-v6.md"
DOC = ROOT / "docs" / "machining-completeness" / "33-PB00703-EXACT-TRIMMED-CONVEX-SHELL.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASE = "c9c3a41877ec4c4e4c842873a291e746b3239a3e"
EXPECTED_V5 = {
    "research/machining-completeness/tasks/MC-038/pb00703-parametric-patch-boundary-v5.json": "ffcb920514048684f17880ba47a18479b38ea68a",
    "research/machining-completeness/tasks/MC-038/pb00703_parametric_patch.py": "5d3b350bfa77dfaac46b90a5a42194419c904b3d",
    "research/machining-completeness/tasks/MC-038/verify_pb00703_v5.py": "e6519ad171151e930ff16009f4b224be1808615c",
    "research/machining-completeness/tasks/MC-038/pb00703-report-v5.md": "8f0b505b19b41a21a7bf37a10b3f559b3e0462ce",
}

sys.path.insert(0, str(TASK))
import pb00703_parametric_patch as patch  # noqa: E402
import pb00703_trimmed_shell as shell  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00703-trimmed-shell/6.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 176
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-03"
    assert artifact["decision"] == "EXACT_TRIMMED_CONVEX_SHELL_AND_MEMBERSHIP_SUBROUTE_ESTABLISHED_FULL_BLOCKER_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v5_evidence"]}
    assert set(history) == set(EXPECTED_V5)
    for path, sha in EXPECTED_V5.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    required = artifact["required_source_domain"]
    assert required["domain_operation_count"] == 26
    assert required["domain_narrowed"] is False
    assert set(required["relevant_source_families"]) == {
        "imported_stock", "lathe_form_tool", "mill_form", "mill_accessible_undercut"
    }
    assert required["missing_constructor_is_gap_not_exclusion"] is True
    assert required["opaque_import_success_is_not_exact_source_authority"] is True

    route = artifact["implemented_bounded_subroute"]
    assert route["id"] == "EXACT_RATIONAL_TRIMMED_CONVEX_SHELL_V1"
    assert "exact rational" in route["trim_authority"]
    assert "exactly two opposite-oriented" in route["seam_authority"]
    assert "V-E+F=2" in route["topology_authority"]
    assert "INSIDE" in route["membership_authority"]
    assert any("opaque STEP" in item for item in route["not_claimed"])
    assert any("durable body_id" in item for item in route["not_claimed"])

    controls = artifact["boundary_controls"]
    for token in (
        "unit cube", "1/1000000", "trim-domain", "bow-tie", "rational weighted",
        "source uncertainty", "micro-gap", "duplicate seam", "inward", "interior-witness",
        "source/role/units/frame", "patch_sha256", "binary-float", "watertight/kernel",
        "body/lineage", "denominator shrinkage", "MC-B promotion",
    ):
        assert any(token in item for item in controls), f"missing control: {token}"

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert review["not_an_impossibility_theorem"] is True
    assert "arbitrary curved" in review["reason"]
    assert "source-solid" in review["residual_obligation"]
    assert {
        "opaque importer success", "kernel-valid B-rep", "fake watertight flag",
        "binary-float tolerance", "backend topology identity",
    } <= set(review["authority_laundering_forbidden"])

    assert artifact["programme_effect"] == {
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
    for path, sha in EXPECTED_V5.items():
        assert git_blob_sha(ROOT / path) == sha, f"historical v5 drift: {path}"

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
            "source/audio/provenance", "source uncertainty", "positive-volume",
            "holder/access", "durable body/lineage", "step", "trim", "seam",
            "inside", "boundary", "outside", "1/1000000",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pb00703_trimmed_shell.py" in workflow
    assert "verify_pb00703_v6.py --contract" in workflow
    assert "verify_pb00703_v6.py --self-test" in workflow
    # Historical verifiers remain wired as regression gates.
    assert "verify_pb00703.py --self-test" in workflow
    assert "verify_pb00703_v5.py --self-test" in workflow


def _p3_add(a, b):
    return [str(int(a[i]) + int(b[i])) for i in range(3)]


def make_patch(face_id, origin, uaxis, vaxis):
    p00 = list(origin)
    p01 = _p3_add(origin, vaxis)
    p10 = _p3_add(origin, uaxis)
    p11 = _p3_add(p10, vaxis)
    return {
        "schema": patch.SCHEMA,
        "source_id": "cube-source",
        "patch_id": face_id,
        "role": "stock",
        "units": "mm",
        "frame_id": "workpiece-v1",
        "u_parameter_id": f"{face_id}-u",
        "v_parameter_id": f"{face_id}-v",
        "degree_u": 1,
        "degree_v": 1,
        "knots_u": ["0", "0", "1", "1"],
        "knots_v": ["0", "0", "1", "1"],
        "parameter_domain_u": ["0", "1"],
        "parameter_domain_v": ["0", "1"],
        "control_points": [[p00, p01], [p10, p11]],
        "weights": [["1", "1"], ["1", "1"]],
        "source_uncertainty": "0",
        "authority_kind": "BOUNDARY_PATCH_ONLY",
    }


def sample_cube():
    # Basis choice makes [00,10,11,01] an outward loop on every face.
    specs = [
        ("xmin", ["0", "0", "0"], ["0", "0", "1"], ["0", "1", "0"]),
        ("xmax", ["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]),
        ("ymin", ["0", "0", "0"], ["1", "0", "0"], ["0", "0", "1"]),
        ("ymax", ["0", "1", "0"], ["0", "0", "1"], ["1", "0", "0"]),
        ("zmin", ["0", "0", "0"], ["0", "1", "0"], ["1", "0", "0"]),
        ("zmax", ["0", "0", "1"], ["1", "0", "0"], ["0", "1", "0"]),
    ]
    faces = []
    for face_id, origin, uaxis, vaxis in specs:
        descriptor = make_patch(face_id, origin, uaxis, vaxis)
        faces.append({
            "face_id": face_id,
            "patch": descriptor,
            "patch_sha256": patch.source_sha256(descriptor),
            "trim_uv": [["0", "0"], ["1", "0"], ["1", "1"], ["0", "1"]],
        })
    return {
        "schema": shell.SCHEMA,
        "authority_kind": shell.AUTHORITY_KIND,
        "shell_id": "unit-cube-shell",
        "source_id": "cube-source",
        "role": "stock",
        "units": "mm",
        "frame_id": "workpiece-v1",
        "revision_id": "rev-7",
        "configuration_id": "cfg-exact",
        "interior_witness": ["1/2", "1/2", "1/2"],
        "faces": faces,
    }


def refresh_face_hash(source, index):
    source["faces"][index]["patch_sha256"] = patch.source_sha256(source["faces"][index]["patch"])


def expect_shell_rejected(mutator):
    source = sample_cube()
    mutator(source)
    result = shell.classify_shell_descriptor(source)
    assert result["status"] == "SEMANTIC_BLOCKER", result
    assert result["blocker"] == "PB-007-03"


def run_model_controls():
    source = sample_cube()
    cert = shell.certify_shell(source)
    assert cert["status"] == "EXACT_CERTIFIED_TRIMMED_CONVEX_SHELL"
    assert cert["topology"] == {
        "vertex_count": 8,
        "edge_count": 12,
        "face_count": 6,
        "euler_characteristic": 2,
        "closed_opposite_oriented_seams": True,
        "connected": True,
        "genus": 0,
    }
    assert shell.classify_point(source, ["1/2", "1/2", "1/2"], cert)["relation"] == "INSIDE"
    assert shell.classify_point(source, ["0", "1/2", "1/2"], cert)["relation"] == "BOUNDARY"
    assert shell.classify_point(source, ["-1/1000000", "1/2", "1/2"], cert)["relation"] == "OUTSIDE"
    assert shell.classify_point(source, ["1/1000000", "1/2", "1/2"], cert)["relation"] == "INSIDE"
    assert shell.classify_point(source, ["1000001/1000000", "1/2", "1/2"], cert)["relation"] == "OUTSIDE"
    assert shell.classify_point(source, ["999999/1000000", "1/2", "1/2"], cert)["relation"] == "INSIDE"

    reordered = copy.deepcopy(source)
    reordered["faces"] = list(reversed(reordered["faces"]))
    assert shell.shell_sha256(reordered) == shell.shell_sha256(source)

    stale = copy.deepcopy(cert)
    stale["configuration_id"] = "forged"
    blocked = shell.classify_point(source, ["1/2", "1/2", "1/2"], stale)
    assert blocked["status"] == "BLOCKED" and blocked["solid_membership_certified"] is False

    for opaque in (
        {"representation": "STEP", "kernel_valid": True, "watertight": True},
        {"representation": "NURBS_BREP", "import_success": True, "closed": True},
        {"representation": "mesh", "watertight": True},
    ):
        blocked = shell.classify_shell_descriptor(opaque)
        assert blocked["status"] == "BLOCKED" and blocked["blocker"] == "PB-007-03"

    try:
        shell.classify_point(source, [0.5, "1/2", "1/2"], cert)
    except TypeError:
        pass
    else:
        raise AssertionError("binary-float point accepted as exact authority")

    expect_shell_rejected(lambda s: s["faces"][0]["trim_uv"].__setitem__(0, ["-1/1000000", "0"]))
    expect_shell_rejected(lambda s: s["faces"][0].__setitem__("trim_uv", [["0", "0"], ["1", "1"], ["1", "0"], ["0", "1"]]))
    expect_shell_rejected(lambda s: s["faces"][0]["trim_uv"][0].__setitem__(0, 0.0))

    def weighted(s):
        s["faces"][0]["patch"]["weights"][1][1] = "2"
        refresh_face_hash(s, 0)
    expect_shell_rejected(weighted)

    def non_affine(s):
        s["faces"][0]["patch"]["control_points"][1][1][0] = "1/1000000"
        refresh_face_hash(s, 0)
    expect_shell_rejected(non_affine)

    def uncertain(s):
        s["faces"][0]["patch"]["source_uncertainty"] = "1/1000000"
        refresh_face_hash(s, 0)
    expect_shell_rejected(uncertain)

    def micro_gap(s):
        face = s["faces"][1]
        for row in face["patch"]["control_points"]:
            for point in row:
                point[0] = "1000001/1000000"
        refresh_face_hash(s, 1)
    expect_shell_rejected(micro_gap)

    expect_shell_rejected(lambda s: s["faces"].pop())
    expect_shell_rejected(lambda s: s["faces"][0].__setitem__("trim_uv", list(reversed(s["faces"][0]["trim_uv"]))))
    expect_shell_rejected(lambda s: s.__setitem__("interior_witness", ["2", "1/2", "1/2"]))
    expect_shell_rejected(lambda s: s.__setitem__("source_id", "other-source"))
    expect_shell_rejected(lambda s: s.__setitem__("role", "holder"))
    expect_shell_rejected(lambda s: s.__setitem__("units", "inch"))
    expect_shell_rejected(lambda s: s.__setitem__("frame_id", "other-frame"))
    expect_shell_rejected(lambda s: s["faces"][0].__setitem__("patch_sha256", "forged"))
    expect_shell_rejected(lambda s: s.__setitem__("watertight", True))
    expect_shell_rejected(lambda s: s["faces"][-1].__setitem__("face_id", s["faces"][0]["face_id"]))


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
    expect_artifact_rejected(lambda a: a["protected_semantics"].__setitem__("source_audio_provenance", False))
    expect_artifact_rejected(lambda a: a["historical_v5_evidence"][0].__setitem__("git_blob_sha1", "forged"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-03 v6 contract: PASS")
    if args.self_test:
        run_model_controls()
        run_artifact_controls()
        print("PB-007-03 v6 adversarial self-test: PASS")


if __name__ == "__main__":
    main()
