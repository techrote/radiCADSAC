#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-038"
ARTIFACT = TASK / "pb00701-mixed-quadrature-phase-anchor-boundary-v24.json"
REPORT = TASK / "pb00701-report-v24.md"
DOC = ROOT / "docs" / "machining-completeness" / "50-PB00701-MIXED-QUADRATURE-PHASE-ANCHOR.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V23_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v23.yml"
V24_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v24.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "2fedcc3ac66a08b82df41a3a68ad2425bf77f8a5"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V23_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-nonconstant-phase-anchor-boundary-v23.json": "294259e253f642dda59c8f142a075992556b9f08",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v23.md": "16d479d011aeea00c7f436a41a1420643c0e58ad",
    "research/machining-completeness/tasks/MC-038/pb00701_nonconstant_phase_anchor_model.py": "1eb91cd3274256fdff7b1e3d296508bdcf7a87e2",
    "research/machining-completeness/tasks/MC-038/test_pb00701_nonconstant_phase_anchor_adversarial.py": "4d7ee8145b83910a8979e0bcb4c4645084507a4c",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v23.py": "3fee3f4a7628900c47eac948bf59571fe7f909f7",
    "docs/machining-completeness/49-PB00701-NONCONSTANT-AMPLITUDE-PHASE-ANCHOR.md": "72e56c84d0650986b1a508f4e5a6d8c05a61bcc9",
    ".github/workflows/mc1-pb00701-v23.yml": "d2b48d0d673917f002571da3676a9269ffe5ce07",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v23 as verify_v23  # noqa: E402
import pb00701_mixed_quadrature_phase_anchor_model as model  # noqa: E402
import test_pb00701_mixed_quadrature_phase_anchor_adversarial as adversarial  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def assert_rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError("expected adversarial contract mutation to be rejected")


def validate_artifact(artifact, *, check_repo=True):
    assert artifact["schema"] == "radicadsac-mc038-pb00701-mixed-quadrature-phase-anchor-boundary/24.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 210
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_MIXED_QUADRATURE_PHASE_ANCHOR_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v23_evidence"]}
    assert set(history) == set(EXPECTED_V23_HISTORY)
    for path, sha in EXPECTED_V23_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == model.V24_ROUTE
    for token in ("both", "c_h", "s_h", "multi-harmonic"):
        assert token in ext["scope"].lower()
    for token in ("fixed sign", "strict rational floor", "bernstein"):
        assert token in ext["component_authority"].lower()
    for token in ("both", "sin", "cos", "1/2"):
        assert token in ext["phase_sector_authority"].lower()
    for token in ("-c*sin", "s*cos", "pi>3", "l_anchor"):
        assert token in ext["projection_authority"].lower()
    for token in ("c'", "s'", "p'", "44/7"):
        assert token in ext["residual_terms"].lower()
    for token in ("max", "{-1,+1}", "sum_i"):
        assert token in ext["l1_identity"].lower()
    for token in ("strictly positive", "closed [0,1]", "mc-032", "sturm"):
        assert token in ext["dominance_authority"].lower()
    assert "v8-v23" in ext["precedence"]

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in (
        "caller mixed phase anchor", "caller component floor", "binary float", "epsilon",
        "sampling", "numerical trigonometry", "approximate minimization", "root ordering",
        "subdivision", "timeout", "resource refusal",
    ):
        assert token in forbidden

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "blocked by v23", "positive and negative", "sign patterns", "constant/nonconstant",
        "sector endpoint equality", "zero bernstein", "misaligned", "residual l1 equality",
        "endpoint", "v23 prior-route", "source-parameter", "forged", "binary-float",
        "resource refusal", "historical v23", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v24" in review["residual_branch"]
    assert review["not_an_impossibility_theorem"] is True

    effect = artifact["programme_effect"]
    assert effect["PB-007-01"] == "OPEN"
    assert effect["PB-007-02"] == "OPEN_DEPENDENT_ON_PB-007-01"
    assert effect["PB-007-03"] == "OPEN"
    assert effect["PB-007-04"] == "OPEN_PROPAGATED"
    for po in OPEN_POS:
        assert effect[po] == "OPEN"
    assert effect["MC-B"] == "NOT_ESTABLISHED"
    assert effect["MC-1"] == "NOT_ESTABLISHED"
    assert effect["domain_operation_count"] == 26
    assert effect["domain_narrowed"] is False
    assert effect["next_pre_gate_priority"].startswith("PB-007-01")
    assert artifact["resources"] == {
        "native_campaign_run": False,
        "paid_campaign_run": False,
        "production_authorized": False,
        "expensive_execution_authorized": False,
    }
    assert artifact["protected_semantics"] and all(artifact["protected_semantics"].values())

    if not check_repo:
        return

    verify_v23.validate_artifact(verify_v23.load(verify_v23.ARTIFACT))
    for path, sha in EXPECTED_V23_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v23 historical evidence drift: {path}"

    assert len(load(DOMAIN)["coverage_rule"]["required_operation_ids"]) == 26
    programme = load(PROGRAMME)
    gates = {gate["id"]: gate for gate in programme["gates"]}
    assert gates["MC-B"]["state"] == "NOT_ESTABLISHED"
    assert programme["capability_status"] == "NOT_ESTABLISHED"
    assert programme["production_authorized"] is False
    assert programme["expensive_execution_authorized"] is False
    proofs = {entry["id"]: entry for entry in load(PROOFS)["obligations"]}
    for po in OPEN_POS:
        assert proofs[po]["state"] == "OPEN"

    for text in (REPORT.read_text(encoding="utf-8").lower(), DOC.read_text(encoding="utf-8").lower()):
        for token in (
            "pb-007-01", "remains open", "mixed", "bernstein", "pi > 3", "44/7", "l1",
            "sturm", "tangent-half", "mc-b", "not_established", "26", "source/audio/provenance",
            "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v23_workflow = V23_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v23.py --contract", "verify_pb00701_v23.py --self-test"):
        assert token in v23_workflow
    v24_workflow = V24_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_mixed_quadrature_phase_anchor_model.py",
        "test_pb00701_mixed_quadrature_phase_anchor_adversarial.py",
        "verify_pb00701_v24.py --contract",
        "verify_pb00701_v24.py --self-test",
    ):
        assert token in v24_workflow, f"v24 workflow missing {token}"
    static = STATIC_WORKFLOW.read_text(encoding="utf-8")
    assert "research/machining-completeness/**" in static
    assert "docs/machining-completeness/**" in static
    assert "name: mc1-static" in static


def run_self_test():
    adversarial.run()
    artifact = load(ARTIFACT)
    validate_artifact(artifact, check_repo=True)

    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["domain_operation_count"] = 25
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["programme_effect"]["MC-B"] = "ESTABLISHED"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["historical_v23_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    eps = Fraction(1, 1000000)
    exact = model._mixed_sector_certificate(Fraction(1, 12), Fraction(1, 6))
    inside = model._mixed_sector_certificate(Fraction(1, 12), Fraction(1, 6) - eps)
    outside = model._mixed_sector_certificate(Fraction(1, 12), Fraction(1, 6) + eps)
    assert exact["status"] == "CERTIFIED"
    assert inside["status"] == "CERTIFIED"
    assert outside is None
    print("PB-007-01 v24 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v24 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
