#!/usr/bin/env python3
"""Fail-closed MC-043 receipt *structure* and exact-byte binding preflight.

This does not parse STEP, run BRL-CAD, or certify native geometry/MC-E.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "radicadsac-mc043-consumer-receipt-preflight/1.0"
PROFILE = "MC-ENG-OUTPUT/1.0"
STRUCTURAL_ONLY = "STRUCTURAL_PREFLIGHT_ONLY"


class Rejected(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def is_digest(value: Any) -> bool:
    return (isinstance(value, str) and len(value) == 71 and
            value.startswith("sha256:") and
            all(c in "0123456789abcdef" for c in value[7:]))


def identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 256


def unique_ids(items: Any, key: str) -> set[str]:
    require(isinstance(items, list), f"{key} records must be a list")
    ids: set[str] = set()
    for item in items:
        require(isinstance(item, dict) and identifier(item.get(key)), f"invalid {key}")
        require(item[key] not in ids, f"duplicate {key}: {item[key]}")
        ids.add(item[key])
    return ids


def safe_file(root: Path, path: Any) -> Path:
    require(isinstance(path, str) and path and "\\" not in path and ":" not in path,
            "invalid STEP artifact relative path")
    p = Path(path)
    require(not p.is_absolute() and all(part not in (".", "..", "") for part in path.split("/")),
            "absolute or traversing artifact path")
    base = root.resolve(strict=True)
    candidate = base / p
    require(not any(segment.is_symlink() for segment in [base / Path(*p.parts[:i]) for i in range(1, len(p.parts) + 1)]),
            "symlink artifact path forbidden")
    require(candidate.is_file() and candidate.resolve().is_relative_to(base), "artifact missing or outside root")
    return candidate


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def check(manifest: dict[str, Any], receipt: dict[str, Any], manifest_bytes: bytes,
          artifact_root: Path) -> str:
    require(isinstance(manifest, dict) and isinstance(receipt, dict), "JSON roots must be objects")
    require(manifest.get("profile_id") == PROFILE, "wrong profile")
    require(receipt.get("schema") == SCHEMA, "wrong receipt schema")
    require(receipt.get("claim") == STRUCTURAL_ONLY, "receipt may not claim qualification")
    require(receipt.get("manifest_sha256") == digest(manifest_bytes), "manifest byte digest mismatch")
    for k in ("source_material_certificate_digest", "source_body_lineage_digest"):
        require(is_digest(manifest.get(k)), f"missing/invalid {k}")
        require(receipt.get(k) == manifest[k], f"receipt {k} binding mismatch")
    require(isinstance(manifest.get("contact_relations"), list), "contact relations absent")
    require("empty_transition" in manifest, "empty transition field absent")
    bodies = unique_ids(manifest.get("durable_bodies"), "durable_body_id")
    artifacts = manifest.get("step_artifacts")
    pieces = manifest.get("representation_pieces")
    require(isinstance(artifacts, list) and isinstance(pieces, list), "artifact/piece arrays required")
    imported = receipt.get("import")
    followon = receipt.get("follow_on")
    require(isinstance(imported, dict) and isinstance(followon, dict), "import/follow-on receipts required")
    state = manifest.get("material_state")

    if state == "EMPTY_MATERIAL":
        require(not bodies and not artifacts and not pieces and not manifest["contact_relations"],
                "empty material may not have retained geometry/body/contact items")
        transition = manifest["empty_transition"]
        require(isinstance(transition, dict), "empty lineage transition absent")
        require(is_digest(transition.get("lineage_digest")) and
                transition["lineage_digest"] == manifest["source_body_lineage_digest"],
                "empty transition not bound to lineage")
        exhausted = transition.get("exhausted_body_ids")
        require(isinstance(exhausted, list) and bool(exhausted) and
                all(identifier(x) for x in exhausted) and len(set(exhausted)) == len(exhausted),
                "empty material must retain distinct exhausted body IDs")
        require(imported.get("invoked") is False and
                imported.get("status") == "NOT_APPLICABLE_EMPTY" and
                imported.get("items") == [] and imported.get("files") == [],
                "empty path invoked or fabricated import")
        require(followon.get("invoked") is False and
                followon.get("status") == "EMPTY_NO_GEOMETRY" and
                followon.get("consumed_item_ids") == [],
                "empty path fabricated downstream geometry")
        return STRUCTURAL_ONLY

    require(state in ("NONEMPTY", "NONEMPTY_GROUPED"), "unsupported material state")
    require(bodies and artifacts, "nonempty material must retain bodies and STEP artifacts")
    require(manifest["empty_transition"] is None, "nonempty material has empty transition")
    artifact_paths: set[str] = set()
    expected_items: dict[str, str] = {}
    expected_files: dict[str, str] = {}
    for artifact in artifacts:
        require(isinstance(artifact, dict), "bad STEP artifact")
        path = artifact.get("path")
        require(isinstance(path, str) and path not in artifact_paths, "duplicate/bad STEP path")
        artifact_paths.add(path)
        require(is_digest(artifact.get("sha256")), "bad STEP byte digest")
        require(file_digest(safe_file(artifact_root, path)) == artifact["sha256"],
                "STEP bytes do not match manifest")
        expected_files[path] = artifact["sha256"]
        ids = unique_ids(artifact.get("items"), "item_id")
        require(ids, "STEP artifact has no declared items")
        for item in artifact["items"]:
            item_id, body_id = item["item_id"], item.get("durable_body_id")
            require(body_id in bodies and item_id not in expected_items, "unbound/duplicate STEP item")
            expected_items[item_id] = body_id
    require(set(expected_items.values()) == bodies, "durable body omitted from STEP item inventory")
    piece_ids = unique_ids(pieces, "piece_id")
    seen_piece_items: set[str] = set()
    for piece in pieces:
        require(piece.get("item_id") in expected_items and
                piece.get("durable_body_id") == expected_items[piece["item_id"]],
                "piece lacks source body/item binding")
        require(piece["item_id"] not in seen_piece_items,
                "multiple representation pieces share one STEP item")
        seen_piece_items.add(piece["item_id"])
        require(piece.get("seam_kind") in ("NONE", "NON_MATERIAL_PARTITION"),
                "unqualified material seam")
    require(len(piece_ids) == len(pieces), "duplicate decomposition piece")
    for contact in manifest["contact_relations"]:
        require(isinstance(contact, dict) and contact.get("kind") == "EXACT_ZERO", "unqualified contact kind")
        a, b = contact.get("body_a"), contact.get("body_b")
        require(a in bodies and b in bodies and a != b, "contact not between distinct bodies")
        require(contact.get("source_certificate_digest") == manifest["source_material_certificate_digest"],
                "contact not source-certificate-bound")
    require(imported.get("invoked") is True and imported.get("strict") is True and
            imported.get("exact") is True and imported.get("repair") == "none" and
            imported.get("reject_invalid") is True and imported.get("exit_code") == 0 and
            imported.get("status") == "complete", "import must be strict/complete/no-repair")
    files = imported.get("files")
    require(isinstance(files, dict) and files == expected_files, "import inputs not exact original STEP bytes")
    item_rows = imported.get("items")
    require(isinstance(item_rows, list), "import inventory absent")
    actual_ids = unique_ids(item_rows, "item_id")
    require(actual_ids == set(expected_items), "import lost, invented or fused STEP items")
    require(all(row.get("durable_body_id") == expected_items[row["item_id"]] for row in item_rows),
            "import item/body binding drift")
    require(followon.get("invoked") is True and followon.get("status") == "completed" and
            followon.get("operand_source") == "INDEPENDENT_IMPORTED_DATABASE",
            "downstream action did not explicitly consume independent import")
    consumed = followon.get("consumed_item_ids")
    require(isinstance(consumed, list) and len(consumed) == len(actual_ids) and
            set(consumed) == actual_ids, "downstream action omitted or duplicated imported items")
    return STRUCTURAL_ONLY


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json_bytes(data: bytes) -> dict[str, Any]:
    return json.loads(data, object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda x: (_ for _ in ()).throw(Rejected(f"nonfinite JSON: {x}")))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = args.manifest.read_bytes()
        result = check(read_json_bytes(raw), read_json_bytes(args.receipt.read_bytes()), raw,
                       args.artifact_root)
    except (Rejected, OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"REJECTED: {exc}\n")
    print(result)
    print("WARNING: structural/byte-custody preflight only; no STEP parse, native result or MC-E acceptance")


if __name__ == "__main__":
    main()
