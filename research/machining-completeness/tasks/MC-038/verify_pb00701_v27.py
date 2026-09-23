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
ARTIFACT = TASK / "pb00701-phase-sector-partition-boundary-v27.json"
REPORT = TASK / "pb00701-report-v27.md"
DOC = ROOT / "docs" / "machining-completeness" / "53-PB00701-PHASE-SECTOR-PARTITION.md"
DOMAIN = MC / "tasks" / "MC-002" / "domain-contract-v1.json"
PROGRAMME = MC / "programme-v1.json"
PROOFS = MC / "proof-obligations-v1.json"
V26_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v26.yml"
V27_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-pb00701-v27.yml"
STATIC_WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"
EXPECTED_BASE = "cad06a39b2ba28d3b560dff409940473f4a3c186"
OPEN_POS = {"PO-04", "PO-05", "PO-08"}
EXPECTED_V26_HISTORY = {
    "research/machining-completeness/tasks/MC-038/pb00701-pointwise-component-cone-boundary-v26.json": "13d53fdff086bda2937684d6e7b4cd6b431b0441",
    "research/machining-completeness/tasks/MC-038/pb00701-report-v26.md": "cc68b7f105b738f5fe0d03e520d718f5f8781cc9",
    "research/machining-completeness/tasks/MC-038/pb00701_pointwise_component_cone_model.py": "a303bba600fa83a1b55c8e113ce1ec7d06f68590",
    "research/machining-completeness/tasks/MC-038/test_pb00701_pointwise_component_cone_adversarial.py": "b94998804a72f439824b0db3383c1b942446c7cc",
    "research/machining-completeness/tasks/MC-038/verify_pb00701_v26.py": "b64ff4b82f2caa04bbf0128a0cb2a757ee7af2f7",
    "docs/machining-completeness/52-PB00701-POINTWISE-COMPONENT-CONE.md": "1897bd75602588048202547c57d47ed7a7a98f36",
    ".github/workflows/mc1-pb00701-v26.yml": "a2a2c834cefb57620ef09b7fbdfa9ea809aaac60",
}

sys.path.insert(0, str(TASK))
import verify_pb00701_v26 as verify_v26  # noqa: E402
import pb00701_phase_sector_partition_model as model  # noqa: E402
import test_pb00701_phase_sector_partition_adversarial as adversarial  # noqa: E402


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
    assert artifact["schema"] == "radicadsac-mc038-pb00701-phase-sector-partition-boundary/27.0"
    assert artifact["task"] == "MC-038"
    assert artifact["corrective_issue"] == 216
    assert artifact["source_baseline"] == EXPECTED_BASE
    assert artifact["target_blocker"] == "PB-007-01"
    assert artifact["decision"] == "EXACT_FINITE_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION_ESTABLISHED_GENERAL_COUPLED_ROUTE_OPEN"
    assert artifact["gate_state"] == "NOT_ESTABLISHED"

    history = {entry["path"]: entry for entry in artifact["historical_v26_evidence"]}
    assert set(history) == set(EXPECTED_V26_HISTORY)
    for path, sha in EXPECTED_V26_HISTORY.items():
        assert history[path]["git_blob_sha1"] == sha
        assert history[path]["preserved"] is True

    ext = artifact["implemented_extension"]
    assert ext["id"] == model.V27_ROUTE
    for token in ("v26-blocked", "affine-phase", "finite", "exact rational"):
        assert token in ext["scope"].lower()
    for token in ("affine preimage", "half-magnitude", "coincident", "exact"):
        assert token in ext["cut_authority"].lower()
    for token in ("s=a+(b-a)u", "rational", "source parameter"):
        assert token in ext["reparameterization"].lower()
    for token in ("v8-v26", "certified", "fail-closed"):
        assert token in ext["child_authority"].lower()
    for token in ("zero", "once", "multiplicity one"):
        assert token in ext["composition"].lower()
    for token in ("finite", "no adaptive subdivision", "once"):
        assert token in ext["termination"].lower()
    assert "v8-v26" in ext["precedence"]

    forbidden = " ".join(ext["forbidden_authority"]).lower()
    for token in (
        "caller partition", "binary float", "epsilon", "sampling", "numerical trigonometry",
        "approximate root ordering", "adaptive subdivision", "timeout", "resource refusal",
    ):
        assert token in forbidden

    acceptance = artifact["acceptance_case"]
    assert acceptance["whole_span_v26"] == "BLOCKED"
    assert acceptance["exact_cut"] == "1/2"
    assert acceptance["expected_children"] == 2
    for token in ("v24", "v25/v26", "simple open"):
        assert token in (acceptance["description"] + " " + acceptance["global_event"]).lower()

    controls = [item.lower() for item in artifact["boundary_controls"]]
    for token in (
        "v26-blocked", "positive and negative", "external", "1/1000000",
        "coincident", "internal-cut zero", "relation mismatch", "multiplicity",
        "blocked child", "resource refusal", "forged", "binary-float",
        "source-parameter", "historical v26", "26-operation", "mc-b",
    ):
        assert any(token in item for item in controls), token

    review = artifact["full_blocker_review"]
    assert review["status"] == "OPEN"
    assert "v8-v27" in review["residual_branch"]
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

    verify_v26.validate_artifact(verify_v26.load(verify_v26.ARTIFACT))
    for path, sha in EXPECTED_V26_HISTORY.items():
        assert git_blob_sha(ROOT / path) == sha, f"v26 historical evidence drift: {path}"

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
            "pb-007-01", "remains open", "phase-sector", "exact rational", "certificate cut",
            "reparameter", "internal", "deduplic", "v8", "v26", "mc-b",
            "not_established", "26", "source/audio/provenance", "resource refusal",
        ):
            assert token in text, f"documentation missing {token}"

    v26_workflow = V26_WORKFLOW.read_text(encoding="utf-8")
    for token in ("verify_pb00701_v26.py --contract", "verify_pb00701_v26.py --self-test"):
        assert token in v26_workflow

    v27_workflow = V27_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "pb00701_phase_sector_partition_model.py",
        "test_pb00701_phase_sector_partition_adversarial.py",
        "verify_pb00701_v27.py --contract",
        "verify_pb00701_v27.py --self-test",
    ):
        assert token in v27_workflow, f"v27 workflow missing {token}"

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
    bad["historical_v26_evidence"][0]["git_blob_sha1"] = "0" * 40
    assert_rejected(lambda: validate_artifact(bad, check_repo=False))

    exact = model._exact_sector_partition(Fraction(1, 12), Fraction(1, 6), [1])
    assert exact["status"] == "CERTIFIED"
    assert exact["cuts"] == ["1/2"]
    print("PB-007-01 v27 contract/adversarial verifier: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        validate_artifact(load(ARTIFACT), check_repo=True)
        print("PB-007-01 v27 contract: PASS")
    if args.self_test:
        run_self_test()


if __name__ == "__main__":
    main()
