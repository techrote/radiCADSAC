#!/usr/bin/env python3
"""MC-043 provisional receipt preflight structural + adversarial contract tests."""
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path

from consumer_receipt_preflight import (PROFILE, SCHEMA, STRUCTURAL_ONLY, Rejected,
                                       check, digest, read_json_bytes)


D1 = "sha256:" + "1" * 64
D2 = "sha256:" + "2" * 64


def as_bytes(doc: dict) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")


def make_nonempty(root: Path) -> tuple[dict, dict]:
    (root / "body-a.step").write_bytes(b"SYNTHETIC_NON_STEP_A\n")
    (root / "body-b.step").write_bytes(b"SYNTHETIC_NON_STEP_B\n")
    artifacts = [
        {"path": "body-a.step", "sha256": digest((root / "body-a.step").read_bytes()),
         "items": [{"item_id": "a-1", "durable_body_id": "body-a"}]},
        {"path": "body-b.step", "sha256": digest((root / "body-b.step").read_bytes()),
         "items": [{"item_id": "b-1", "durable_body_id": "body-b"}]},
    ]
    manifest = {
        "profile_id": PROFILE, "material_state": "NONEMPTY_GROUPED",
        "source_material_certificate_digest": D1, "source_body_lineage_digest": D2,
        "step_artifacts": artifacts,
        "representation_pieces": [
            {"piece_id": "piece-a", "item_id": "a-1", "durable_body_id": "body-a", "seam_kind": "NONE"},
            {"piece_id": "piece-b", "item_id": "b-1", "durable_body_id": "body-b", "seam_kind": "NONE"},
        ],
        "durable_bodies": [{"durable_body_id": "body-a"}, {"durable_body_id": "body-b"}],
        "contact_relations": [{"kind": "EXACT_ZERO", "body_a": "body-a", "body_b": "body-b",
                               "source_certificate_digest": D1}],
        "empty_transition": None,
    }
    receipt = {
        "schema": SCHEMA, "claim": STRUCTURAL_ONLY,
        "manifest_sha256": digest(as_bytes(manifest)),
        "source_material_certificate_digest": D1, "source_body_lineage_digest": D2,
        "import": {"invoked": True, "strict": True, "exact": True, "repair": "none",
                   "reject_invalid": True, "exit_code": 0, "status": "complete",
                   "files": {a["path"]: a["sha256"] for a in artifacts},
                   "items": [{"item_id": "a-1", "durable_body_id": "body-a"},
                             {"item_id": "b-1", "durable_body_id": "body-b"}]},
        "follow_on": {"invoked": True, "status": "completed",
                      "operand_source": "INDEPENDENT_IMPORTED_DATABASE",
                      "consumed_item_ids": ["a-1", "b-1"]},
    }
    return manifest, receipt


def make_empty() -> tuple[dict, dict]:
    manifest = {
        "profile_id": PROFILE, "material_state": "EMPTY_MATERIAL",
        "source_material_certificate_digest": D1, "source_body_lineage_digest": D2,
        "step_artifacts": [], "representation_pieces": [], "durable_bodies": [],
        "contact_relations": [],
        "empty_transition": {"lineage_digest": D2, "exhausted_body_ids": ["body-a"]},
    }
    receipt = {
        "schema": SCHEMA, "claim": STRUCTURAL_ONLY,
        "manifest_sha256": digest(as_bytes(manifest)),
        "source_material_certificate_digest": D1, "source_body_lineage_digest": D2,
        "import": {"invoked": False, "status": "NOT_APPLICABLE_EMPTY", "items": [], "files": []},
        "follow_on": {"invoked": False, "status": "EMPTY_NO_GEOMETRY", "consumed_item_ids": []},
    }
    return manifest, receipt


def run_case(manifest: dict, receipt: dict, root: Path, *, rebind: bool = True) -> str:
    raw = as_bytes(manifest)
    if rebind:
        receipt["manifest_sha256"] = digest(raw)
    return check(manifest, receipt, raw, root)


def reject_case(label: str, manifest: dict, receipt: dict, root: Path, *, rebind: bool = True) -> None:
    try:
        run_case(manifest, receipt, root, rebind=rebind)
    except (Rejected, TypeError, KeyError, OSError):
        return
    raise AssertionError(f"negative mutation was accepted: {label}")


def self_test() -> int:
    rejected = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        nonempty, valid = make_nonempty(root)
        empty, valid_empty = make_empty()
        assert run_case(copy.deepcopy(nonempty), copy.deepcopy(valid), root) == STRUCTURAL_ONLY
        assert run_case(copy.deepcopy(empty), copy.deepcopy(valid_empty), root) == STRUCTURAL_ONLY

        def mutate(label: str, *, empty_case: bool = False, mutate_manifest=None,
                   mutate_receipt=None, rebind: bool = True) -> None:
            nonlocal rejected
            m, r = copy.deepcopy((empty, valid_empty) if empty_case else (nonempty, valid))
            if mutate_manifest:
                mutate_manifest(m)
            if mutate_receipt:
                mutate_receipt(r)
            reject_case(label, m, r, root, rebind=rebind)
            rejected += 1

        mutate("profile mismatch", mutate_manifest=lambda m: m.update(profile_id="WRONG"))
        mutate("manifest digest drift", mutate_manifest=lambda m: m.update(profile_id="WRONG"), rebind=False)
        mutate("source certificate binding drift", mutate_receipt=lambda r: r.update(source_material_certificate_digest=D2))
        mutate("nonempty body omitted", mutate_manifest=lambda m: m["durable_bodies"].pop())
        mutate("duplicate STEP item", mutate_manifest=lambda m: m["step_artifacts"][1]["items"].append(
            {"item_id": "a-1", "durable_body_id": "body-b"}))
        mutate("STEP path traversal", mutate_manifest=lambda m: m["step_artifacts"][0].update(path="../body-a.step"))
        mutate("wrong artifact byte hash", mutate_manifest=lambda m: m["step_artifacts"][0].update(sha256=D1))
        mutate("untracked importer STEP byte hash", mutate_receipt=lambda r: r["import"]["files"].update({"body-a.step": D2}))
        mutate("partial STEP import", mutate_receipt=lambda r: r["import"].update(status="partial"))
        mutate("healed STEP import", mutate_receipt=lambda r: r["import"].update(repair="heal"))
        mutate("non-strict import", mutate_receipt=lambda r: r["import"].update(strict=False))
        mutate("invalid objects preserved", mutate_receipt=lambda r: r["import"].update(reject_invalid=False))
        mutate("nonzero importer exit", mutate_receipt=lambda r: r["import"].update(exit_code=2))
        mutate("import dropped body", mutate_receipt=lambda r: r["import"]["items"].pop())
        mutate("import body fusion", mutate_receipt=lambda r: r["import"]["items"][1].update(durable_body_id="body-a"))
        mutate("import fabricated item", mutate_receipt=lambda r: r["import"]["items"].append(
            {"item_id": "fake", "durable_body_id": "body-a"}))
        mutate("producer authority replay", mutate_receipt=lambda r: r["follow_on"].update(operand_source="PRODUCER_BREP"))
        mutate("follow-on omitted imported item", mutate_receipt=lambda r: r["follow_on"].update(consumed_item_ids=["a-1"]))
        mutate("follow-on duplicated imported item", mutate_receipt=lambda r: r["follow_on"].update(consumed_item_ids=["a-1", "a-1"]))
        mutate("uncertified seam type", mutate_manifest=lambda m: m["representation_pieces"][0].update(seam_kind="PHYSICAL_MATERIAL_BOUNDARY"))
        mutate("contact certificate drift", mutate_manifest=lambda m: m["contact_relations"][0].update(source_certificate_digest=D2))
        mutate("nonempty has empty transition", mutate_manifest=lambda m: m.update(empty_transition={}))
        mutate("capability PASS claim", mutate_receipt=lambda r: r.update(claim="MC-E_ACCEPTED"))
        mutate("empty placeholder geometry", empty_case=True,
               mutate_manifest=lambda m: m["step_artifacts"].append({"path": "body-a.step", "sha256": D1, "items": []}))
        mutate("empty importer invoked", empty_case=True, mutate_receipt=lambda r: r["import"].update(invoked=True))
        mutate("empty follow-on invoked", empty_case=True, mutate_receipt=lambda r: r["follow_on"].update(invoked=True))
        mutate("empty missing exhausted lineage", empty_case=True,
               mutate_manifest=lambda m: m["empty_transition"].update(exhausted_body_ids=[]))
        mutate("empty lost lineage binding", empty_case=True,
               mutate_manifest=lambda m: m["empty_transition"].update(lineage_digest=D1))
        mutate("empty false import status", empty_case=True,
               mutate_receipt=lambda r: r["import"].update(status="complete"))
        mutate("empty false downstream status", empty_case=True,
               mutate_receipt=lambda r: r["follow_on"].update(status="completed"))

        (root / "body-a.step").write_bytes(b"TAMPERED_SYNTHETIC_BYTES\n")
        reject_case("mutated bytes after recorded digest", copy.deepcopy(nonempty), copy.deepcopy(valid), root)
        rejected += 1
        try:
            read_json_bytes(b'{"profile_id":"A","profile_id":"B"}')
        except Rejected:
            rejected += 1
        else:
            raise AssertionError("duplicate JSON key admitted")
        (root / "body-a.step").unlink()
        (root / "body-a.step").symlink_to(root / "body-b.step")
        reject_case("symlink artifact path", copy.deepcopy(nonempty), copy.deepcopy(valid), root)
        rejected += 1
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("select --contract and/or --self-test")
    rejected = self_test()
    assert rejected >= 32, rejected
    print(f"MC-043 PROVISIONAL STRUCTURAL_PREFLIGHT_ONLY: 2 positive synthetic controls; {rejected} rejected corruptions")
    print("No real STEP file, independent consumer process, native permit or MC-E capability qualified")


if __name__ == "__main__":
    main()
