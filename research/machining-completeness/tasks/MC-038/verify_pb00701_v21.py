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
ARTIFACT = TASK / "pb00701-l1-sign-orthant-envelope-boundary-v21.json"
REPORT = TASK / "pb00701-report-v21.md"
DOC = ROOT / "docs" / "machining-completeness" / "47-PB00701-L1-SIGN-ORTHANT-DERIVATIVE-ENVELOPE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V20_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v20.yml"
V21_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v21.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "b9444116b4856c606bdcb0040d439ba893f47c85"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V20_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-derivative-envelope-boundary-v20.json": "926be00a6847246c00d999615bc5783ef805d9e1",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v20.md": "b6ed47a1d7fbf076c16ab6f82c3f1844e11c4971",
    "research/machining-completeness/tasks/MC-038/pb00701_pointwise_derivative_envelope_model.py": "a0bbc30f5a26e2f2991c96640cf4410763ef2eb4",
    "research/machining-completeness/tasks/MC-038/test_pb00701_pointwise_derivative_envelope_adversarial.py": "5b933a0948ca13212dc3de424782de61ac3ea96f",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v20.py": "283a856e4a5967731ac16c02753d3dd3bca49d7f",
    "docs/machining-completeness/46-PB00701-POINTWISE-DERIVATIVE-ENVELOPE.md": "3aae781b9172e1c1e303fa5d3ba46601bfcfe1a8",
    ".github/workflows/mc1-pb00701-v20.yml": "71034c48bc46266988c77501cc029fec8d3962ba",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v20 as verify_v20  # noqa: E402
import pb00701_l1_sign_orthant_envelope_model as model  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-l1-sign-orthant-envelope-boundary/21.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 204
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_FINITE_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v20_evidence"]}
    assert set(history) == set(EXPECTED_V20_HISTORY)
    for path, sha in EXPECTED_V20_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == "EXACT_MULTI_HARMONIC_FINITE_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE"
    for token in ("v20", "cauchy", "two active positive harmonics"):
        assert token in ext["scope"].lower()
    for token in ("c'_h", "s'_h", "44/7", "source"):
        assert token in ext["source_derived_terms"].lower()
    for token in ("max", "{-1,+1}", "sum_i"):
        assert token in ext["l1_identity"].lower()
    for token in ("margin", "strictly positive", "closed [0,1]"):
        assert token in ext["orthant_authority"].lower()
    for token in ("mc-032", "sturm", "endpoint", "root"):
        assert token in ext["sturm_authority"].lower()
    for token in ("sign cell", "algebraic", "ordering"):
        assert token in ext["sign_cell_relation"].lower()
    for token in ("2^n", "finite", "resource refusal"):
        assert token in ext["termination"].lower()
    assert "v8-v20" in ext["precedence"]

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in ("binary float", "epsilon", "sampling", "root ordering", "subdivision", "timeout", "resource refusal"):
        assert token in forbidden

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "blocked by both v19 and v20", "positive and negative", "endpoint-root", "l1 equality", "1/1000000",
        "algebraic-irrational", "anchor derivative", "v20 prior-route", "source-parameter", "forged",
        "binary-float", "resource refusal", "historical v20", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v21" in review["residual_branch"]
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

    verify_v20.validate_artifact(verify_v20.load(verify_v20.ARTIFACT))
    for path, sha in EXPECTED_V20_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v20 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "l1", "orthant", "sturm", "pi < 22/7",
            "tangent-half", "mc-b", "not_established", "26", "source/audio/provenance", "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v20_workflow = V20_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v20.py --contract", "verify_pb00701_v20.py --self-test"):
        assert token in v20_workflow
    v21_workflow = V21_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_l1_sign_orthant_envelope_model.py",
        "test_pb00701_l1_sign_orthant_envelope_adversarial.py",
        "verify_pb00701_v21.py --contract",
        "verify_pb00701_v21.py --self-test",
    ):
        assert token in v21_workflow, f"v21 workflow missing {token}"
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
    bad["historical_v20_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    eps = Fraction(1, 1000000)
    equality = model._l1_sign_orthant_derivative_certificate(
        {0: [0, 3], 1: [1], 2: [1]}, {}, Fraction(7, 44)
    )
    assert equality["status"] == "BLOCKED"
    above = model._l1_sign_orthant_derivative_certificate(
        {0: [0, Fraction(3000001, 1000000)], 1: [1], 2: [1]}, {}, Fraction(7, 44)
    )
    assert above["status"] == "CERTIFIED"
    assert above["orthant_count"] == 4
    print("PB-007-01 v21 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v21 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
