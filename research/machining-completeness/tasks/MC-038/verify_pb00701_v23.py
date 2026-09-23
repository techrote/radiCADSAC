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
ARTIFACT = TASK / "pb00701-nonconstant-phase-anchor-boundary-v23.json"
REPORT = TASK / "pb00701-report-v23.md"
DOC = ROOT / "docs" / "machining-completeness" / "49-PB00701-NONCONSTANT-AMPLITUDE-PHASE-ANCHOR.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V22_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v22.yml"
V23_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v23.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "5a2d500a4c2956254fa17c89be884ca08ded0324"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V22_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-phase-sector-anchor-boundary-v22.json": "3cb6f009aed5edfbfd629a43ee7589d7e12fc86f",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v22.md": "396cf233a1546fe77a5e0a246aa4b249e99c5f20",
    "research/machining-completeness/tasks/MC-038/pb00701_phase_sector_anchor_model.py": "923e9d63e3950a705923b9b5e619fee43c2819eb",
    "research/machining-completeness/tasks/MC-038/test_pb00701_phase_sector_anchor_adversarial.py": "4e45a1d80c3d03dcfc692ab65342fa00717e8d96",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v22.py": "a1596c32d1a8343ab2bbeb53c81755c5508ff399",
    "docs/machining-completeness/48-PB00701-PHASE-SECTOR-PARTIAL-DERIVATIVE-ANCHOR.md": "9a9d94563561d032c5e15e7b06c7032470cdac2f",
    ".github/workflows/mc1-pb00701-v22.yml": "019359876ef2d36e0afc4b614cb8cde480ef22ff",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v22 as verify_v22  # noqa: E402
import pb00701_nonconstant_phase_anchor_model as model  # noqa: E402
import test_pb00701_nonconstant_phase_anchor_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-nonconstant-phase-anchor-boundary/23.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 208
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v22_evidence"]}
    assert set(history) == set(EXPECTED_V22_HISTORY)
    for path, sha in EXPECTED_V22_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == model.V23_ROUTE
    for token in ("nonconstant", "pure sin", "cos"):
        assert token in ext["scope"].lower()
    for token in ("bernstein", "strict sign", "a_floor"):
        assert token in ext["amplitude_authority"].lower()
    for token in ("pi>3", "l_anchor", "a_floor"):
        assert token in ext["phase_anchor_authority"].lower()
    for token in ("amplitude derivative", "p'", "44/7"):
        assert token in ext["residual_terms"].lower()
    for token in ("max", "{-1,+1}", "sum_i"):
        assert token in ext["l1_identity"].lower()
    for token in ("strictly positive", "closed [0,1]", "mc-032", "sturm"):
        assert token in ext["dominance_authority"].lower()
    assert "v8-v22" in ext["precedence"]

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in (
        "caller phase anchor", "caller amplitude floor", "binary float", "epsilon",
        "sampling", "numerical trigonometry", "approximate minimization", "root ordering",
        "subdivision", "timeout", "resource refusal",
    ):
        assert token in forbidden

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "blocked by v22", "positive and negative", "sin and cos", "phase-sector boundary equality",
        "zero bernstein", "pointwise-positive", "residual l1 equality", "endpoint",
        "v22 prior-route", "source-parameter", "forged", "binary-float", "resource refusal",
        "historical v22", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v23" in review["residual_branch"]
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

    verify_v22.validate_artifact(verify_v22.load(verify_v22.ARTIFACT))
    for path, sha in EXPECTED_V22_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v22 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "nonconstant", "bernstein", "pi > 3", "44/7", "l1",
            "sturm", "tangent-half", "mc-b", "not_established", "26", "source/audio/provenance",
            "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v22_workflow = V22_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v22.py --contract", "verify_pb00701_v22.py --self-test"):
        assert token in v22_workflow
    v23_workflow = V23_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_nonconstant_phase_anchor_model.py",
        "test_pb00701_nonconstant_phase_anchor_adversarial.py",
        "verify_pb00701_v23.py --contract",
        "verify_pb00701_v23.py --self-test",
    ):
        assert token in v23_workflow, f"v23 workflow missing {token}"
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
    bad["historical_v22_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    eps = Fraction(1, 1000000)
    zero = model._amplitude_floor_certificate([0, 1])
    inside = model._amplitude_floor_certificate([eps, 1])
    outside = model._amplitude_floor_certificate([-eps, 1])
    assert zero["status"] == "BLOCKED"
    assert inside["status"] == "CERTIFIED"
    assert outside["status"] == "BLOCKED"
    print("PB-007-01 v23 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v23 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
