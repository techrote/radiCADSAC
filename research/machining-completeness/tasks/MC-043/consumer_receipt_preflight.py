#!/usr/bin/env python3
"""Fail-closed MC-043 receipt *structure* and exact-byte binding preflight.

This does not parse STEP, run BRL-CAD, or certify native geometry/MC-E.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
from pathlib import Path
from typing import Any

SCHEMA = "radicadsac-mc043-consumer-receipt-preflight/1.0"
PROFILE = "MC-ENG-OUTPUT/1.0"
STRUCTURAL_ONLY = "STRUCTURAL_PREFLIGHT_ONLY"

MAX_JSON_BYTES = 1024 * 1024
MAX_JSON_DEPTH = 32
MAX_JSON_INT_DIGITS = 128


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
    """Hash a checked regular-file descriptor, not a separately verified pathname.

    Reject external hard-link aliases and detectable same-byte inode swaps.
    This is bounded local custody, NOT atomic hostile-filesystem attestation.
    """
    def identity(s: Any) -> tuple[int, int, int, int, int, int]:
        # Windows lstat and fstat need not report the same st_ctime_ns.
        # Compare only portable identity fields ACROSS those APIs.
        return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
                s.st_mtime_ns)

    def snapshot(s: Any) -> tuple[int, int, int, int, int, int, int]:
        # Compare ctime WITHIN each API independently to detect mutations.
        return (*identity(s), s.st_ctime_ns)

    try:
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_ino != 0 and
                before.st_nlink == 1, "STEP artifact custody: nonregular, linked or unidentified")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            opened = os.fstat(fd)
            require(stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1 and
                    identity(opened) == identity(before),
                    f"STEP artifact custody: identity changed before open; "
                    f"path={identity(before)!r} fd={identity(opened)!r}")
            h = hashlib.sha256()
            with os.fdopen(fd, "rb", closefd=False) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(chunk)
            finished = os.fstat(fd)
            after = path.lstat()
            require(snapshot(finished) == snapshot(opened) and
                    snapshot(after) == snapshot(before) and
                    identity(after) == identity(opened),
                    "STEP artifact custody: identity changed during hash")
            return "sha256:" + h.hexdigest()
        finally:
            os.close(fd)
    except OSError as exc:
        raise Rejected(f"STEP artifact custody: filesystem refusal: {exc}") from exc


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
    # MC-ENG-OUTPUT/1.0 distinguishes the regular single durable-body state
    # from the explicit grouped multi-body/singular output envelope. A fully
    # bound item inventory alone cannot make a falsely ungrouped manifest valid.
    require(state != "NONEMPTY" or len(bodies) == 1,
            "NONEMPTY state requires exactly one durable body")
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
    # Python considers False == 0 and 0.0 == 0. A process exit receipt must
    # retain its integer type, not merely compare equal to successful exit 0.
    require(type(imported.get("exit_code")) is int and imported["exit_code"] == 0,
            "import exit_code must be integer zero")
    require(imported.get("invoked") is True and imported.get("strict") is True and
            imported.get("exact") is True and imported.get("repair") == "none" and
            imported.get("reject_invalid") is True and
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


def finite_json_float(token: str) -> float:
    # JSON rejects NaN/Infinity lexemes, but Python's ordinary float parser
    # also converts a syntactically valid exponent such as 1e999 to infinity.
    value = float(token)
    require(math.isfinite(value), "nonfinite JSON exponent")
    return value


def reject_unpaired_surrogates(document: Any) -> None:
    # json.loads accepts escaped lone UTF-16 surrogate code points even though
    # they are not Unicode scalar values. Check both keys and values, and
    # traverse iteratively so source nesting adds no second recursion limit.
    pending = [document]
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            require(not any(0xD800 <= ord(ch) <= 0xDFFF for ch in value),
                    "unpaired Unicode surrogate in JSON")
        elif isinstance(value, dict):
            pending.extend(value.keys())
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)


def read_json_bytes(data: bytes) -> dict[str, Any]:
    document = json.loads(
        data, object_pairs_hook=no_duplicate_keys, parse_float=finite_json_float,
        parse_constant=lambda x: (_ for _ in ()).throw(Rejected(f"nonfinite JSON: {x}")))
    reject_unpaired_surrogates(document)
    return document


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
