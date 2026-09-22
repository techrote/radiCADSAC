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
ARTIFACT = TASK / "pb00701-pointwise-derivative-envelope-boundary-v20.json"
REPORT = TASK / "pb00701-report-v20.md"
DOC = ROOT / "docs" / "machining-completeness" / "46-PB00701-POINTWISE-DERIVATIVE-ENVELOPE.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V19_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v19.yml"
V20_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v20.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "ac3d034633f9f50d216b0afdec4958a8ed005d40"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V19_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-multiharmonic-monotone-anchor-boundary-v19.json": "56ac3cb745c0b34de7bdb1221d31e649ef50ec9b",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v19.md": "b1a6602536d7310ebaa675bf1c12f7a1a137d183",
    "research/machining-completeness/tasks/MC-038/pb00701_multiharmonic_monotone_anchor_model.py": "38db0b5f1f4549f7ea632db27a5347b3aadd7b1a",
    "research/machining-completeness/tasks/MC-038/test_pb00701_multiharmonic_monotone_anchor_adversarial.py": "5a588809d2f2510ba77b5299de38f57a3d6e679c",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v19.py": "5cbbfd3512c8c6429ae0ed08d3820f4b37f1456f",
    "docs/machining-completeness/45-PB00701-MULTIHARMONIC-MONOTONE-ANCHOR.md": "28d3fcc73f232e0726362732355d95890e989147",
    ".github/workflows/mc1-pb00701-v19.yml": "da3992655fd2e71b8f9e32259de4e1dbae43574a",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v19 as verify_v19  # noqa: E402
import pb00701_pointwise_derivative_envelope_model as model  # noqa: E402
import test_pb00701_pointwise_derivative_envelope_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-pointwise-derivative-envelope-boundary/20.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 202
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_POINTWISE_POLYNOMIAL_DERIVATIVE_ENVELOPE_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v19_evidence"]}
    assert set(history) == set(EXPECTED_V19_HISTORY)
    for path, sha in EXPECTED_V19_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_MULTI_HARMONIC_POINTWISE_POLYNOMIAL_DERIVATIVE_ENVELOPE"
    for token in ("v19", "whole-span", "two active positive harmonics"):
        assert token in extension["scope"].lower()
    for token in ("c'_h", "s'_h", "44/7", "source"):
        assert token in extension["source_derived_terms"].lower()
    for token in ("cauchy-schwarz", "sqrt", "sum_i"):
        assert token in extension["pointwise_authority"].lower()
    for token in ("q(s)", "p'(s)^2", "strict"):
        assert token in extension["dominance_polynomial"].lower()
    for token in ("mc-032", "sturm", "endpoint", "root"):
        assert token in extension["sturm_authority"].lower()
    for token in ("finite", "two", "subdivision", "timeout"):
        assert token in extension["termination"].lower()
    for token in ("v19", "v6", "tangent-half", "(-1)^h"):
        assert token in extension["endpoint_authority"].lower()
    assert "v8-v19" in extension["precedence"]

    forbidden = " ".join(extension["forbidden_authority"]).lower()
    for token in ("binary float", "epsilon", "sampling", "subdivision", "timeout", "resource refusal"):
        assert token in forbidden

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "blocked by v19", "positive and negative", "endpoint-root", "q=0", "1/1000000",
        "anchor derivative", "q roots", "single-positive-harmonic", "v19 prior-route",
        "source-parameter", "forged", "binary-float", "resource refusal", "historical v19",
        "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "multi-harmonic" in review["residual_branch"]
    assert "v8-v20" in review["residual_branch"]
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

    verify_v19.validate_artifact(verify_v19.load(verify_v19.ARTIFACT))
    for path, sha in EXPECTED_V19_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v19 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "pointwise", "cauchy", "q(s)", "sturm",
            "pi < 22/7", "tangent-half", "mc-b", "not_established", "26",
            "source/audio/provenance", "subdivision",
        ):
            assert token in text, f"documentation missing {token}"

    v19_workflow = V19_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v19.py --contract", "verify_pb00701_v19.py --self-test"):
        assert token in v19_workflow, f"v19 workflow missing historical gate {token}"

    v20_workflow = V20_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_pointwise_derivative_envelope_model.py",
        "test_pb00701_pointwise_derivative_envelope_adversarial.py",
        "verify_pb00701_v20.py --contract",
        "verify_pb00701_v20.py --self-test",
    ):
        assert token in v20_workflow, f"v20 workflow missing {token}"

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
    bad["historical_v19_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    equality = model._pointwise_derivative_envelope_certificate(
        {0: [0, 10], 1: [1], 7: [1]}, {}, Fraction(7, 44)
    )
    assert equality["status"] == "BLOCKED"
    assert equality["q_polynomial"] == ["0"]
    above = model._pointwise_derivative_envelope_certificate(
        {0: [0, Fraction(10000001, 1000000)], 1: [1], 7: [1]}, {}, Fraction(7, 44)
    )
    assert above["status"] == "CERTIFIED"
    assert above["q_positivity_certificate"]["distinct_roots_open"] == 0
    print("PB-007-01 v20 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v20 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
