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
ARTIFACT = TASK / "pb00701-pythagorean-phase-cell-boundary-v29.json"
REPORT = TASK / "pb00701-report-v29.md"
DOC = ROOT / "docs" / "machining-completeness" / "55-PB00701-PYTHAGOREAN-PHASE-CELL.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V28_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v28.yml"
V29_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v29.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "77cbe474927f66ebb49c13a1733dfa7359b3f3b7"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V28_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-algebraic-phase-cell-boundary-v28.json": "ea6599571aca2fad0a1e8050ac1b529756588df2",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v28.md": "fbfd3f31e7121b92f42a8c76421513661e1d7308",
    "research/machining-completeness/tasks/MC-038/pb00701_algebraic_phase_cell_model.py": "117dafa3073dd2a5dc00c288089fd88d41628fae",
    "research/machining-completeness/tasks/MC-038/test_pb00701_algebraic_phase_cell_adversarial.py": "6390eb45df036b5f14077717b54606e04918f83a",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v28.py": "288078e80b1e123bfbb936b2295943ae73e62c9a",
    "docs/machining-completeness/54-PB00701-ALGEBRAIC-PHASE-CELL.md": "0cbad28e5afdcee6ecde40d005ebac8b8197593d",
    ".github/workflows/mc1-pb00701-v28.yml": "00a871f70209f9adfcb9be3f8683a5a1c0497936",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v28 as verify_v28  # noqa: E402
import pb00701_pythagorean_phase_cell_model as model  # noqa: E402
import test_pb00701_pythagorean_phase_cell_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-pythagorean-phase-cell-boundary/29.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 221
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v28_evidence"]}
    assert set(history) == set(EXPECTED_V28_HISTORY)
    for path, sha in EXPECTED_V28_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == model.V29_ROUTE
    for token in ("v8-v28", "multi-harmonic", "6/7", "1/2", "conservative"):
        assert token in ext["scope"].lower(), token
    for token in ("1/16-turn", "sqrt(2+sqrt(2))/2", "sqrt(2-sqrt(2))/2", "12/13", "5/13", "57122>56644"):
        assert token in ext["phase_cell_authority"].lower().replace(" ", ""), token
    for token in ("sin-dominant", "cos-dominant", "negative"):
        assert token in ext["projection"].lower(), token
    for token in ("amplitude derivatives", "finite signed margins", "mc-032", "sturm"):
        assert token in ext["residual_authority"].lower(), token
    for token in ("exact rational-turn", "endpoint", "simple-root"):
        assert token in ext["endpoint_authority"].lower(), token
    assert "v8-v28" in ext["precedence"]
    for token in ("finite", "2^(1+n)", "no subdivision", "sampling"):
        assert token in ext["termination"].lower(), token

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in (
        "caller phase", "caller projection", "caller root", "binary float",
        "epsilon", "sampling", "numerical trigonometry", "algebraic comparison",
        "root ordering", "adaptive subdivision", "depth", "timeout", "resource refusal",
    ):
        assert token in forbidden, token

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "v8-v28-blocked", "1/16-turn", "plus/minus 1/1000000",
        "projection-bound equality", "residual-l1 equality", "positive and negative phase rate",
        "sin-dominant", "negative dominant", "unsupported wider", "historical v28",
        "certificate-cut", "forged caller", "binary-float", "source-parameter",
        "resource refusal", "blob hashes", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v29" in review["residual_branch"]
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

    verify_v28.validate_artifact(verify_v28.load(verify_v28.ARTIFACT))
    for path, sha in EXPECTED_V28_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v28 historical evidence drift: {path}"

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
        compact = text.replace(" ", "")
        for token in (
            "pb-007-01", "remains open", "1/16-turn", "12/13", "5/13",
            "complete v8–v28", "mc-032", "sturm", "mc-b", "not_established",
            "26", "source/audio/provenance", "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"
        assert "57122>56644" in compact

    v28_workflow = V28_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_algebraic_phase_cell_model.py",
        "verify_pb00701_v28.py --contract",
        "verify_pb00701_v28.py --self-test",
    ):
        assert token in v28_workflow, f"v28 workflow missing {token}"
    v29_workflow = V29_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_pythagorean_phase_cell_model.py",
        "test_pb00701_pythagorean_phase_cell_adversarial.py",
        "verify_pb00701_v29.py --contract",
        "verify_pb00701_v29.py --self-test",
    ):
        assert token in v29_workflow, f"v29 workflow missing {token}"
    static = STATIC_WORKFLOW.read_text(encoding="utf-8")
    assert "research/machining-completeness/**" in static
    assert "docs/machining-completeness/**" in static
    assert "name: mc1-static" in static


def run_self_test():
    verify_v28.run_self_test()
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
    bad["historical_v28_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["implemented_extension"]["phase_cell_authority"] = "caller float trig"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v29 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v29 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
