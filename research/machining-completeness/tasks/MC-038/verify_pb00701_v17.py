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
ARTIFACT = TASK / "pb00701-even-trig-multiplier-boundary-v17.json"
REPORT = TASK / "pb00701-report-v17.md"
DOC = ROOT / "docs" / "machining-completeness" / "43-PB00701-EVEN-TRIG-PROJECTIVE-MULTIPLIER.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V16_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v16.yml"
V17_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v17.yml"
EXPECTED_BASE = "12e65ad2b032fcb9c4ac84b28b2b53195f9f194a"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V16_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-chebyshev-sturm-boundary-v16.json": "d5236f68be1effcffab28e814649936b259b0ede",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v16.md": "a3913c6cedc3effa2930a8c2478c4a774e318fe0",
    "research/machining-completeness/tasks/MC-038/pb00701_chebyshev_multiplier_model.py": "d07abb52bf6a7236d49a80774c40be3459f03fb5",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v16.py": "6cf047e02d3465f931441d273b25734642683b0b",
    "docs/machining-completeness/42-PB00701-CHEBYSHEV-STURM-MULTIPLIER.md": "a94a322375fa41b7afca4c3d765eefab4b8d890e",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v16 as verify_v16  # noqa: E402
import pb00701_even_trig_multiplier_model as model  # noqa: E402
import test_pb00701_even_trig_multiplier_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-even-trig-projective-boundary/17.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 196
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_SOURCE_DERIVED_EVEN_TRIG_PROJECTIVE_STURM_ROUTE_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate"] == "MC-B"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v16_evidence"]}
    assert set(history) == set(EXPECTED_V16_HISTORY)
    for path, sha in EXPECTED_V16_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    extension = artifact["implemented_extension"]
    assert extension["id"] == "EXACT_SOURCE_DERIVED_EVEN_TRIG_PROJECTIVE_STURM_MULTIPLIER"
    for token in ("q=A-iB", "p_r=q*m_r", "rho", "regenerate"):
        assert token in extension["source_inversion"]
    for token in ("t=tan(alpha)", "(1+t^2)^m", "projective"):
        assert token in extension["projective_reduction"]
    for token in ("infinity", "cauchy", "sturm", "sign"):
        assert token in extension["projective_authority"].lower()
    assert "v15/v16" in extension["precedence"]
    assert all(token in extension["carrier_dispatch"] for token in ("v10", "v11", "v12", "v8"))

    controls = artifact["boundary_controls"]
    for token in (
        "sine multiplier", "positive and negative", "infinity root", "repeated finite",
        "algebraic irrational", "1/1000000", "malformed", "underdetermined", "v15/v16",
        "common factor", "source-parameter", "forged", "binary-float", "resource refusal",
        "historical v16", "26-operation", "MC-B",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "underdetermined" in review["residual_branch"]
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

    verify_v16.validate_artifact(verify_v16.load(verify_v16.ARTIFACT))
    for path, sha in EXPECTED_V16_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v16 historical evidence drift: {path}"
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
            "pb-007-01", "remains open", "projective", "sturm", "infinity",
            "mc-b", "not_established", "26", "source/audio/provenance",
        ):
            assert token in text, f"documentation missing {token}"

    v16_workflow = V16_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v16.py --contract", "verify_pb00701_v16.py --self-test"):
        assert token in v16_workflow, f"v16 workflow missing historical gate {token}"
    v17_workflow = V17_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_even_trig_multiplier_model.py",
        "test_pb00701_even_trig_multiplier_adversarial.py",
        "verify_pb00701_v17.py --contract",
        "verify_pb00701_v17.py --self-test",
    ):
        assert token in v17_workflow, f"v17 workflow missing {token}"


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
    bad["historical_v16_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    numerator = model.projective_numerator([2, 0], [0, 1])
    assert numerator == [2, 2, 2]
    print("PB-007-01 v17 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v17 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
