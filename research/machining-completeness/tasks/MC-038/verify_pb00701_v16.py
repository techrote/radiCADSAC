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
ARTIFACT = TASK / "pb00701-chebyshev-sturm-boundary-v16.json"
REPORT = TASK / "pb00701-report-v16.md"
DOC = ROOT / "docs" / "machining-completeness" / "42-PB00701-CHEBYSHEV-STURM-MULTIPLIER.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "e9f0d464581939b4de0c0dc766553c8672aecdf8"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V15_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-finite-multiplier-boundary-v15.json": "fb911c58b45d846c027bc0399e06faba900be727",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v15.md": "cd683ace27fb456337169e1527205f8676675bcd",
    "research/machining-completeness/tasks/MC-038/pb00701_finite_multiplier_model.py": "d2e48bbd5177c74678255c91c3600efdfc221461",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v15.py": "175fcf1af1c0a636e600f755a06fcab3a2be267b",
    "docs/machining-completeness/41-PB00701-FINITE-MULTIPLIER.md": "14dacadea94f6f8bc4e621dec8e0ee90da6473c4",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v15 as verify_v15  # noqa: E402
import pb00701_chebyshev_multiplier_model as model  # noqa: E402
import test_pb00701_chebyshev_multiplier_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-chebyshev-sturm-boundary/16.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 194
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_CHEBYSHEV_STURM_NONVANISHING_CERTIFICATE_ESTABLISHED_GENERAL_MULTIHARMONIC_ROUTE_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v15_evidence"]}
    assert set(history) == set(EXPECTED_V15_HISTORY)
    for path, sha in EXPECTED_V15_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_CHEBYSHEV_STURM_EVEN_COSINE_MULTIPLIER_NONVANISHING"
    for token in ("P(x)", "T_k(x)", "[-1,1]"):
        assert token in extension["chebyshev_reduction"]
    for token in ("endpoint", "Sturm", "zero", "sign"):
        assert token.lower() in extension["closed_interval_authority"].lower()
    assert "v15" in extension["precedence"]
    assert all(token in extension["carrier_dispatch"] for token in ("v10", "v11", "v12", "v8"))

    controls = artifact["boundary_controls"]
    for token in (
        "non-L1 positive", "non-L1 negative", "v15", "endpoint root", "simple interior",
        "repeated interior", "algebraic irrational", "1/1000000", "forged", "binary-float",
        "resource refusal", "historical v15", "26-operation", "MC-B",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "multi-harmonic" in review["residual_branch"]
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

    verify_v15.validate_artifact(verify_v15.load(verify_v15.ARTIFACT))
    for path, sha in EXPECTED_V15_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v15 historical evidence drift: {path}"
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
            "pb-007-01", "remains **open**", "chebyshev", "sturm", "[-1,1]",
            "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "verify_pb00701_v15.py --contract",
        "verify_pb00701_v15.py --self-test",
        "pb00701_chebyshev_multiplier_model.py",
        "verify_pb00701_v16.py --contract",
        "verify_pb00701_v16.py --self-test",
        "test_pb00701_chebyshev_multiplier_adversarial.py",
    ):
        assert token in workflow, f"workflow missing {token}"


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
    bad["historical_v15_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    assert model.chebyshev_polynomial([4, 3, 0, 1]) == [4, 0, 0, 4]
    print("PB-007-01 v16 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v16 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
