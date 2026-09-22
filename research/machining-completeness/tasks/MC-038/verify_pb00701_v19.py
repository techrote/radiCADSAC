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
ARTIFACT = TASK / "pb00701-multiharmonic-monotone-anchor-boundary-v19.json"
REPORT = TASK / "pb00701-report-v19.md"
DOC = ROOT / "docs" / "machining-completeness" / "45-PB00701-MULTIHARMONIC-MONOTONE-ANCHOR.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V18_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v18.yml"
V19_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v19.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "4e337136731a423fbdf3aa6fd1952f372de5601a"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V18_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-source-laurent-module-boundary-v18.json": "48d6eb9b144407064708b9b805f57611815d7f65",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v18.md": "5ea9aa4c7c5e58b888d584394b70267922811c33",
    "research/machining-completeness/tasks/MC-038/pb00701_source_laurent_factor_model.py": "4e656c95a13858ee8ed496149d200a0a321a61a0",
    "research/machining-completeness/tasks/MC-038/test_pb00701_source_laurent_factor_adversarial.py": "591a95afc8e5893742c99e3339086d21dd87f45a",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v18.py": "0a0359a5909eb7152966082ea0c39ef63aaeb1fa",
    "docs/machining-completeness/44-PB00701-SOURCE-LAURENT-MODULE-FACTORIZATION.md": "dd7ae014f083a7529c8ecd2b41e2f39bacd1e030",
    ".github/workflows/mc1-pb00701-v18.yml": "97bf76f178b3a70183023e37e03fec6ff25d78b7",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v18 as verify_v18  # noqa: E402
import pb00701_multiharmonic_monotone_anchor_model as model  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-multiharmonic-monotone-anchor-boundary/19.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 200
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v18_evidence"]}
    assert set(history) == set(EXPECTED_V18_HISTORY)
    for path, sha in EXPECTED_V18_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE"
    for token in ("harmonic-0", "two active positive harmonics", "v18"):
        assert token in extension["scope"].lower()
    for token in ("bernstein", "convex-hull", "exact rational"):
        assert token in extension["bernstein_authority"].lower()
    for token in ("44/7", "pi < 22/7", "c_h", "s_h"):
        assert token in extension["derivative_bound"].lower()
    for token in ("min_bernstein", "max_bernstein", "equality", "margin"):
        assert token in extension["strict_monotonicity"].lower()
    for token in ("v6", "tangent-half", "(-1)^h"):
        assert token in extension["endpoint_authority"].lower()
    for token in ("zero or one", "simple", "bounded away from zero"):
        assert token in extension["root_decision"].lower()
    assert "v8-v18" in extension["precedence"]
    assert "factor removal" in extension["precedence"].lower()

    controls = artifact["boundary_controls"]
    for token in (
        "two active positive harmonics", "positive and negative", "zero-root",
        "left-endpoint-root", "right-endpoint-root", "half-turn", "1/1000000",
        "nonconstant positive-harmonic", "constant anchor", "v18", "source-parameter",
        "forged", "binary-float", "resource refusal", "historical v18", "26-operation", "MC-B",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "multi-harmonic" in review["residual_branch"]
    assert "monotone" in review["residual_branch"]
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

    verify_v18.validate_artifact(verify_v18.load(verify_v18.ARTIFACT))
    for path, sha in EXPECTED_V18_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v18 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "multi-harmonic", "bernstein", "pi < 22/7",
            "tangent-half", "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"

    v18_workflow = V18_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v18.py --contract", "verify_pb00701_v18.py --self-test"):
        assert token in v18_workflow, f"v18 workflow missing historical gate {token}"

    v19_workflow = V19_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_multiharmonic_monotone_anchor_model.py",
        "test_pb00701_multiharmonic_monotone_anchor_adversarial.py",
        "verify_pb00701_v19.py --contract",
        "verify_pb00701_v19.py --self-test",
    ):
        assert token in v19_workflow, f"v19 workflow missing {token}"

    static_workflow = STATIC_WORKFLOW.read_text(encoding="utf-8")
    assert "research/machining-completeness/**" in static_workflow
    assert "docs/machining-completeness/**" in static_workflow
    assert "name: mc1-static" in static_workflow


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
    bad["historical_v18_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    assert model._bernstein_coefficients([0, 1]) == [Fraction(0), Fraction(1)]
    assert model._bernstein_coefficients([1, -2, 1]) == [Fraction(1), Fraction(0), Fraction(0)]
    exact = model._derivative_dominance_certificate(
        {0: [0, 1], 1: [1]}, {}, Fraction(7, 44)
    )
    assert exact["status"] == "BLOCKED"
    assert exact["oscillatory_derivative_bound"] == "1"
    print("PB-007-01 v19 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v19 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
