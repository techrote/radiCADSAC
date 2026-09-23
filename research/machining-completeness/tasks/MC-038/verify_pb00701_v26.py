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
ARTIFACT = TASK / "pb00701-pointwise-component-cone-boundary-v26.json"
REPORT = TASK / "pb00701-report-v26.md"
DOC = ROOT / "docs" / "machining-completeness" / "52-PB00701-POINTWISE-COMPONENT-CONE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V25_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v25.yml"
V26_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v26.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "f668790f648eb9a6815d30fbacf982765cd3bed3"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V25_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-component-cone-phase-anchor-boundary-v25.json": "8e6ce2fed319a0bd1e3cc8ab89f6b37553042eaf",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v25.md": "2c60ce1d682a6e743ef34d7a734c8d1721759cf8",
    "research/machining-completeness/tasks/MC-038/pb00701_component_cone_phase_anchor_model.py": "fc1f940f5b9b2b6fd8570b36a91c4389453e29b2",
    "research/machining-completeness/tasks/MC-038/test_pb00701_component_cone_phase_anchor_adversarial.py": "ba78f2b3ab85f698ca066d984417ef08c4f6e636",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v25.py": "c853f1ee48660693562a778e1ab063bf02ea928d",
    "docs/machining-completeness/51-PB00701-COMPONENT-CONE-PHASE-ANCHOR.md": "ed9e464b506c48a9bd6c703b3f88da5d72a238ed",
    ".github/workflows/mc1-pb00701-v25.yml": "fa6ab2fff77fe4276a2a7fdd0d8f78b12a2e704d",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v25 as verify_v25  # noqa: E402
import pb00701_pointwise_component_cone_model as model  # noqa: E402
import test_pb00701_pointwise_component_cone_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-pointwise-component-cone-boundary/26.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 214
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v25_evidence"]}
    assert set(history) == set(EXPECTED_V25_HISTORY)
    for path, sha in EXPECTED_V25_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == model.V26_ROUTE
    for token in ("v25-blocked", "multi-harmonic", "pointwise", "global"):
        assert token in ext["scope"].lower()
    for token in ("strict sign", "closed [0,1]", "mc-032", "sturm"):
        assert token in ext["dominant_sign_authority"].lower()
    for token in ("1/2", "fixed sign", "single-quadrature"):
        assert token in ext["phase_sector_authority"].lower()
    for token in ("6*", "sigma", "strict"):
        assert token in ext["pointwise_cone_authority"].lower()
    for token in ("c'", "s'", "p'", "44/7"):
        assert token in ext["residual_terms"].lower()
    for token in ("|t|", "sum_i", "pointwise"):
        assert token in ext["orthant_identity"].lower()
    for token in ("pi>3", "2*pi>6", "dominates"):
        assert token in ext["derivative_authority"].lower()
    for token in ("finite", "2^(1+n)", "mc-032", "sturm"):
        assert token in ext["termination"].lower()
    assert "v8-v25" in ext["precedence"]

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in (
        "caller pointwise cone", "caller component floor", "binary float", "epsilon",
        "sampling", "numerical trigonometry", "approximate minimization", "root ordering",
        "subdivision", "timeout", "resource refusal",
    ):
        assert token in forbidden

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "blocked by v25", "s-dominant", "c-dominant", "sturm proof",
        "sign-changing transverse", "sector endpoint equality", "pointwise cone equality",
        "combined residual equality", "dominant zero", "amplitude derivatives", "endpoint",
        "v25 prior-route", "source-parameter", "forged", "binary-float", "resource refusal",
        "historical v25", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v26" in review["residual_branch"]
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

    verify_v25.validate_artifact(verify_v25.load(verify_v25.ARTIFACT))
    for path, sha in EXPECTED_V25_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v25 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "pointwise", "component", "orthant", "pi > 3",
            "44/7", "sturm", "rational-turn", "mc-b", "not_established", "26",
            "source/audio/provenance", "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v25_workflow = V25_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v25.py --contract", "verify_pb00701_v25.py --self-test"):
        assert token in v25_workflow
    v26_workflow = V26_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_pointwise_component_cone_model.py",
        "test_pb00701_pointwise_component_cone_adversarial.py",
        "verify_pb00701_v26.py --contract",
        "verify_pb00701_v26.py --self-test",
    ):
        assert token in v26_workflow, f"v26 workflow missing {token}"
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
    bad["historical_v25_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    eps = Fraction(1, 1000000)
    equality = model._pointwise_component_cone_derivative_certificate(
        {1: [1]}, {1: [2]}, Fraction(-1, 6), Fraction(1, 3), 1
    )
    accepted = model._pointwise_component_cone_derivative_certificate(
        {1: [1]}, {1: [Fraction(2) + eps]}, Fraction(-1, 6), Fraction(1, 3), 1
    )
    assert equality["status"] == "BLOCKED"
    assert accepted["status"] == "CERTIFIED"
    print("PB-007-01 v26 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v26 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
