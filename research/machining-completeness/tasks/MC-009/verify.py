#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / "research" / "machining-completeness"
TASK = MC / "tasks" / "MC-009"
CONTRACT = TASK / "verifier-contract-v1.json"
CATALOG = MC / "schema-catalog-v1.json"
OUTCOME = TASK / "outcome.json"
OUTCOMES = MC / "outcomes-v1.json"
FIXTURES = MC / "fixture-families-v1.json"
PROGRAMME = MC / "programme-v1.json"
DOC = ROOT / "docs" / "machining-completeness" / "11-FORMAT-CONTRACTS.md"
CENTRAL = ROOT / "tools" / "mc_evidence_verifier.py"

DEPENDENCIES = {
    "MC-001": (MC / "tasks" / "MC-001" / "outcome.json", "2efd52cf39102d5722c6bbf281828361e943d6a4", "COMPLETED_RESEARCH"),
    "MC-003": (MC / "tasks" / "MC-003" / "outcome.json", "8f335f59f36c8761844806f9059af4a4f1671044", "COMPLETED_RESEARCH"),
}
EXPECTED_SCHEMA_IDS = {
    "radicadsac-mc-fixture/1.0",
    "radicadsac-mc-result/1.0",
    "radicadsac-mc-task-outcome/1.0",
    "radicadsac-mc-claim/1.0",
    "radicadsac-mc-programme-verdict/1.0",
}
EXPECTED_GATES = {
    "MC-A": "ACCEPTED",
    "MC-B": "NOT_ESTABLISHED",
    "MC-C": "NOT_ESTABLISHED",
    "MC-D": "NOT_ESTABLISHED",
    "MC-E": "NOT_ESTABLISHED",
    "MC-F": "NOT_ESTABLISHED",
    "MC-1": "NOT_ESTABLISHED",
}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def fail(msg: str) -> None:
    raise AssertionError(msg)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def load_central():
    spec = importlib.util.spec_from_file_location("mc_evidence_verifier", CENTRAL)
    if spec is None or spec.loader is None:
        fail("cannot import central MC evidence verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def validate() -> None:
    obj = load(CONTRACT)
    if obj.get("schema") != "radicadsac-mc009-verifier-contract/1.0" or obj.get("task") != "MC-009":
        fail("MC-009 contract schema/task mismatch")
    if obj.get("status") != "reviewed-binding-contract":
        fail("MC-009 contract status drift")
    if obj.get("source_baseline") != "fa93162caa6e4e16c188674b19bac7a501c5f415":
        fail("MC-009 source baseline drift")

    deps = {d.get("task"): d for d in obj.get("dependencies", [])}
    if set(deps) != set(DEPENDENCIES):
        fail("MC-009 dependency set drift")
    for task, (path, expected_blob, expected_kind) in DEPENDENCIES.items():
        if deps[task].get("git_blob_sha1") != expected_blob or git_blob_sha1(path) != expected_blob:
            fail(f"{task} dependency identity drift")
        dep = load(path)
        if dep.get("result_kind") != expected_kind or deps[task].get("result_kind") != expected_kind:
            fail(f"{task} dependency result-kind drift")

    catalog = load(CATALOG)
    if catalog.get("schema") != "radicadsac-mc-schema-catalog/1.0" or catalog.get("programme") != "MC-1":
        fail("schema catalog identity drift")
    if sha256(CATALOG) != obj["schema_catalog"].get("sha256"):
        fail("schema catalog content hash drift")
    ids = {x.get("id") for x in catalog.get("schemas", {}).values()}
    if ids != EXPECTED_SCHEMA_IDS or set(obj["schema_catalog"].get("schemas", [])) != EXPECTED_SCHEMA_IDS:
        fail("MC-009 schema inventory drift")
    encoding = catalog.get("binding_encoding", {})
    if encoding.get("binary_float_forbidden") is not True or encoding.get("digest") != "sha256:<lower-case-hex> over the canonical bytes":
        fail("canonical evidence binding contract weakened")
    if catalog.get("verifier") != "tools/mc_evidence_verifier.py":
        fail("catalog no longer points to programme verifier")

    if sha256(CENTRAL) != obj["programme_verifier"].get("sha256"):
        fail("programme verifier content hash drift")
    if obj["programme_verifier"].get("authority") != "MC-1-programme":
        fail("programme verdict authority drift")
    central = load_central()
    central.self_test()

    families = load(FIXTURES).get("families", [])
    expected_families = [f"F{i:02d}" for i in range(1, 17)]
    if [f.get("id") for f in families] != expected_families:
        fail("F01-F16 fixture family denominator drift")
    if any(f.get("state") != "UNBUILT" or f.get("mandatory") is not True for f in families):
        fail("MC-009 improperly fabricated or weakened future mandatory fixture families")
    if obj["fixture_registry_guard"].get("families") != expected_families or obj["fixture_registry_guard"].get("required_state") != "UNBUILT":
        fail("fixture registry guard drift")

    outcome = load(OUTCOME)
    central.validate_outcome(outcome)
    if outcome.get("task") != "MC-009" or outcome.get("result_kind") != "COMPLETED_RESEARCH":
        fail("MC-009 task outcome drift")
    if outcome.get("native_execution") is not False:
        fail("MC-009 must remain non-native binding research")
    if outcome.get("open_claims") == []:
        fail("MC-009 improperly erased open capability claims")

    reg = load(OUTCOMES).get("tasks", {}).get("MC-009", {})
    if reg.get("state") != "COMPLETED_RESEARCH" or reg.get("issue") != 71 or reg.get("blockers") != []:
        fail("MC-009 outcome registry not reconciled")
    required_artifacts = {
        "research/machining-completeness/schema-catalog-v1.json",
        "tools/mc_evidence_verifier.py",
        "research/machining-completeness/tasks/MC-009/verifier-contract-v1.json",
        "research/machining-completeness/tasks/MC-009/report.md",
        "research/machining-completeness/tasks/MC-009/outcome.json",
        "research/machining-completeness/tasks/MC-009/verify.py",
        "docs/machining-completeness/11-FORMAT-CONTRACTS.md",
    }
    if not required_artifacts <= set(reg.get("accepted_artifacts", [])):
        fail("MC-009 accepted-artifact registry incomplete")

    programme = load(PROGRAMME)
    gates = {g.get("id"): g.get("state") for g in programme.get("gates", [])}
    if gates != EXPECTED_GATES:
        fail("MC-009 changed a programme capability gate")
    if programme.get("capability_status") != "NOT_ESTABLISHED" or programme.get("production_authorized") is not False or programme.get("expensive_execution_authorized") is not False:
        fail("MC-009 changed production/native authority")

    protected = obj.get("protected_semantics", {})
    if not protected or any(value is not True for value in protected.values()):
        fail("protected semantic guard weakened")
    guard = obj.get("capability_guard", {})
    for gate, state in EXPECTED_GATES.items():
        if guard.get(gate) != state:
            fail(f"MC-009 capability guard drift for {gate}")
    if guard.get("native_or_paid_execution") is not False or guard.get("production_authorized") is not False:
        fail("MC-009 capability guard authorized native/production work")

    text = DOC.read_text(encoding="utf-8")
    for marker in (
        "## MC-009 implemented binding contract",
        "`research/machining-completeness/schema-catalog-v1.json`",
        "`tools/mc_evidence_verifier.py`",
        "does not certify geometry",
        "candidate cannot self-authorize",
    ):
        if marker not in text:
            fail(f"format-contract documentation missing MC-009 marker: {marker}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    args = ap.parse_args()
    if not args.contract:
        ap.error("MC-009 exposes only the cheap --contract verifier; no native campaign is authorized")
    validate()
    print("MC-009 contract verification passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
