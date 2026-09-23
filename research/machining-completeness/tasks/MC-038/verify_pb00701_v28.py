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
ARTIFACT = TASK / "pb00701-algebraic-phase-cell-boundary-v28.json"
REPORT = TASK / "pb00701-report-v28.md"
DOC = ROOT / "docs" / "machining-completeness" / "54-PB00701-ALGEBRAIC-PHASE-CELL.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V27_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v27.yml"
V28_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v28.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "bafe1f73ba254e9d1695a870f1434b586b775f4f"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V27_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-phase-sector-partition-boundary-v27.json": "7a938ad02d0f32cceba060276d75f02f08130bca",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v27.md": "bc92a9ac32ea0ad8b0880718de81f1b533b2e390",
    "research/machining-completeness/tasks/MC-038/pb00701_phase_sector_partition_model.py": "6211e658621af7100c2509dcafdaeaf348e48d46",
    "research/machining-completeness/tasks/MC-038/test_pb00701_phase_sector_partition_adversarial.py": "76428e191fd7f97634dadb959171071623b6a953",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v27.py": "02cd8c8557ffc18612e0f47fe4128ac4f2402f50",
    "docs/machining-completeness/53-PB00701-PHASE-SECTOR-PARTITION.md": "d829de845a49fadaa56c5681d4c5228d403b7439",
    ".github/workflows/mc1-pb00701-v27.yml": "73af59b3853fdb1a88b9a41a30d8f6dda9de967a",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v27 as verify_v27  # noqa: E402
import pb00701_algebraic_phase_cell_model as model  # noqa: E402
import test_pb00701_algebraic_phase_cell_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-algebraic-phase-cell-boundary/28.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 219
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v27_evidence"]}
    assert set(history) == set(EXPECTED_V27_HISTORY)
    for path, sha in EXPECTED_V27_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == model.V28_ROUTE
    for token in ("v8-v27", "multi-harmonic", "half-magnitude", "conservative"):
        assert token in ext["scope"].lower(), token
    for token in ("rational-turn", "sqrt(3)/2", "6/7", "147 > 144"):
        assert token in ext["phase_cell_authority"].lower(), token
    for token in ("sin-dominant", "cos-dominant", "negative"):
        assert token in ext["projection"].lower(), token
    for token in ("amplitude derivatives", "finite signed margins", "mc-032", "sturm"):
        assert token in ext["residual_authority"].lower(), token
    for token in ("exact rational-turn", "endpoint", "simple-root"):
        assert token in ext["endpoint_authority"].lower(), token
    assert "v8-v27" in ext["precedence"]
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
        "v8-v27-blocked", "zero-separation", "plus/minus 1/1000000",
        "residual-l1 equality", "positive and negative phase rate",
        "sin-dominant", "negative dominant", "external source endpoint",
        "internal certificate-boundary", "source spline knot", "unsupported wider",
        "forged caller", "binary-float", "source-parameter", "resource refusal",
        "historical v8-v27", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v28" in review["residual_branch"]
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

    verify_v27.validate_artifact(verify_v27.load(verify_v27.ARTIFACT))
    for path, sha in EXPECTED_V27_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v27 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "algebraic", "rational-turn", "sqrt(3)/2",
            "6/7", "complete v8–v27", "mc-032", "sturm", "mc-b",
            "not_established", "26", "source/audio/provenance", "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v27_workflow = V27_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_phase_sector_partition_model.py",
        "verify_pb00701_v27.py --contract",
        "verify_pb00701_v27.py --self-test",
    ):
        assert token in v27_workflow, f"v27 workflow missing {token}"
    v28_workflow = V28_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_algebraic_phase_cell_model.py",
        "test_pb00701_algebraic_phase_cell_adversarial.py",
        "verify_pb00701_v28.py --contract",
        "verify_pb00701_v28.py --self-test",
    ):
        assert token in v28_workflow, f"v28 workflow missing {token}"
    static = STATIC_WORKFLOW.read_text(encoding="utf-8")
    assert "research/machining-completeness/**" in static
    assert "docs/machining-completeness/**" in static
    assert "name: mc1-static" in static


def run_self_test():
    verify_v27.run_self_test()
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
    bad["historical_v27_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))
    bad = copy.deepcopy(artifact)
    bad["implemented_extension"]["phase_cell_authority"] = "caller float trig"
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    print("PB-007-01 v28 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v28 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
