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
ARTIFACT = TASK / "pb00701-phase-sector-anchor-boundary-v22.json"
REPORT = TASK / "pb00701-report-v22.md"
DOC = ROOT / "docs" / "machining-completeness" / "48-PB00701-PHASE-SECTOR-PARTIAL-DERIVATIVE-ANCHOR.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V21_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v21.yml"
V22_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v22.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "d98bce801e4ba1e95ec6d4fe8b709eb05a1c8c87"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V21_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-l1-sign-orthant-envelope-boundary-v21.json": "3df8b847c45a41713be1b4535a4c9c26ff49c945",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v21.md": "754dd1ca51f5a36b7f68b848b4051ee78870262b",
    "research/machining-completeness/tasks/MC-038/pb00701_l1_sign_orthant_envelope_model.py": "f97e5c18e27fd8021362f24b62a11c889b5b6ce1",
    "research/machining-completeness/tasks/MC-038/test_pb00701_l1_sign_orthant_envelope_adversarial.py": "254e49801aebe146b4f187a5a815195642d7220f",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v21.py": "1ba0c0fe78b6b21707f06a6cf94330ab338034ce",
    "docs/machining-completeness/47-PB00701-L1-SIGN-ORTHANT-DERIVATIVE-ENVELOPE.md": "49d3461e1dbe12de067bde3609d6de0547119c4a",
    ".github/workflows/mc1-pb00701-v21.yml": "2b5d6b13db011183711f458dfa7b898488a12f11",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v21 as verify_v21  # noqa: E402
import pb00701_phase_sector_anchor_model as model  # noqa: E402
import test_pb00701_phase_sector_anchor_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-phase-sector-anchor-boundary/22.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 206
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v21_evidence"]}
    assert set(history) == set(EXPECTED_V21_HISTORY)
    for path, sha in EXPECTED_V21_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == "EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR_WITH_RESIDUAL_L1_DOMINANCE"
    for token in ("harmonic-0", "sign", "constant-amplitude", "phase"):
        assert token in ext["scope"].lower()
    for token in ("sin", "cos", "1/2", "pi>3", "3*|amplitude*h*r|"):
        assert token in ext["phase_anchor_authority"].lower()
    for token in ("v10", "v11", "v12", "uniform derivative lower bound"):
        assert token in ext["historical_event_relation"].lower()
    for token in ("harmonic-0", "p'", "44/7", "source-derived"):
        assert token in ext["residual_terms"].lower()
    for token in ("max", "{-1,+1}", "sum_i"):
        assert token in ext["l1_identity"].lower()
    for token in ("l_anchor", "strictly positive", "closed [0,1]", "mc-032", "sturm"):
        assert token in ext["dominance_authority"].lower()
    assert "v8-v21" in ext["precedence"]

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in (
        "caller phase anchor", "caller phase-sector", "caller derivative lower bound",
        "binary float", "epsilon", "sampling", "numerical trigonometry", "root ordering",
        "subdivision", "timeout", "resource refusal",
    ):
        assert token in forbidden

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "blocked by v21", "harmonic-0 derivative", "positive and negative", "sin/cosine-derivative",
        "cos/sine-derivative", "phase-sector boundary equality", "1/1000000", "residual l1 equality",
        "endpoint-root", "nonconstant anchor amplitude", "v21 prior-route", "source-parameter",
        "forged", "binary-float", "resource refusal", "historical v21", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v22" in review["residual_branch"]
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

    verify_v21.validate_artifact(verify_v21.load(verify_v21.ARTIFACT))
    for path, sha in EXPECTED_V21_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v21 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "phase-sector", "pi > 3", "44/7", "l1", "sturm",
            "tangent-half", "mc-b", "not_established", "26", "source/audio/provenance", "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v21_workflow = V21_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v21.py --contract", "verify_pb00701_v21.py --self-test"):
        assert token in v21_workflow
    v22_workflow = V22_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_phase_sector_anchor_model.py",
        "test_pb00701_phase_sector_anchor_adversarial.py",
        "verify_pb00701_v22.py --contract",
        "verify_pb00701_v22.py --self-test",
    ):
        assert token in v22_workflow, f"v22 workflow missing {token}"
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
    bad["historical_v21_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    eps = Fraction(1, 1000000)
    exact = model._phase_anchor_derivative_certificate({}, {1: [1]}, 0, Fraction(1, 6), 1, "SIN")
    outside = model._phase_anchor_derivative_certificate({}, {1: [1]}, 0, Fraction(1, 6) + eps, 1, "SIN")
    assert exact["status"] == "CERTIFIED"
    assert outside["status"] == "BLOCKED"
    anchor = model._phase_anchor_derivative_certificate({}, {1: [1]}, 0, Fraction(1, 12), 1, "SIN")
    equality = model._residual_l1_certificate({0: [0, Fraction(1, 4)]}, {1: [1]}, Fraction(1, 12), anchor)
    below = model._residual_l1_certificate({0: [0, Fraction(1, 4) - eps]}, {1: [1]}, Fraction(1, 12), anchor)
    assert equality["status"] == "BLOCKED"
    assert below["status"] == "CERTIFIED"
    print("PB-007-01 v22 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v22 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
