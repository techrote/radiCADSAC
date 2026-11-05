#!/usr/bin/env python3
"""MC-043 provisional receipt preflight structural + adversarial contract tests."""
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
from unittest.mock import patch
import consumer_receipt_preflight as custody
import tempfile
from pathlib import Path

from consumer_receipt_preflight import (PROFILE, SCHEMA, STRUCTURAL_ONLY, Rejected,
                                       MAX_JSON_BYTES, MAX_JSON_DEPTH, MAX_JSON_INT_DIGITS,
                                       check, digest, read_json_bytes, read_json_file)


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
    except Rejected:
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

        # MC-ENG-OUTPUT/1.0 also admits a regular single-body NONEMPTY path.
        # Construct a fully source/receipt-consistent example, rather than
        # relying on a bare predicate that bypasses check() or artifact bytes.
        single = copy.deepcopy(nonempty)
        single_receipt = copy.deepcopy(valid)
        single["material_state"] = "NONEMPTY"
        single["durable_bodies"] = single["durable_bodies"][:1]
        single["step_artifacts"] = single["step_artifacts"][:1]
        single["representation_pieces"] = single["representation_pieces"][:1]
        single["contact_relations"] = []
        single_receipt["import"]["files"].pop("body-b.step")
        single_receipt["import"]["items"] = single_receipt["import"]["items"][:1]
        single_receipt["follow_on"]["consumed_item_ids"] = ["a-1"]
        assert run_case(single, single_receipt, root) == STRUCTURAL_ONLY

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

        # Valid two-body grouped evidence must not become a false ungrouped
        # one-body state by mutating only material_state. This previously passed.
        mislabelled = copy.deepcopy(nonempty)
        mislabelled["material_state"] = "NONEMPTY"
        try:
            run_case(mislabelled, copy.deepcopy(valid), root)
        except Rejected as exc:
            assert "NONEMPTY state requires exactly one durable body" in str(exc), str(exc)
        else:
            raise AssertionError("two durable bodies accepted as single-body NONEMPTY")
        rejected += 1

        mutate("profile mismatch", mutate_manifest=lambda m: m.update(profile_id="WRONG"))
        mutate("manifest digest drift", mutate_manifest=lambda m: m.update(test_nonce="byte-drift"), rebind=False)
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
        # Exercise actual receipt admission, not a stand-alone equality assertion:
        # both JSON boolean false and JSON real 0.0 compare equal to Python 0.
        mutate("boolean false is not an integer process exit", mutate_receipt=lambda r: r["import"].update(exit_code=False))
        mutate("JSON real 0.0 is not an integer process exit", mutate_receipt=lambda r: r["import"].update(exit_code=0.0))
        mutate("import dropped body", mutate_receipt=lambda r: r["import"]["items"].pop())
        mutate("import body fusion", mutate_receipt=lambda r: r["import"]["items"][1].update(durable_body_id="body-a"))
        mutate("import fabricated item", mutate_receipt=lambda r: r["import"]["items"].append(
            {"item_id": "fake", "durable_body_id": "body-a"}))
        mutate("producer authority replay", mutate_receipt=lambda r: r["follow_on"].update(operand_source="PRODUCER_BREP"))
        mutate("follow-on omitted imported item", mutate_receipt=lambda r: r["follow_on"].update(consumed_item_ids=["a-1"]))
        mutate("follow-on duplicated imported item", mutate_receipt=lambda r: r["follow_on"].update(consumed_item_ids=["a-1", "a-1"]))
        mutate("two pieces share a single STEP item", mutate_manifest=lambda m: m["representation_pieces"][1].update(item_id="a-1", durable_body_id="body-a"))
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

        # Actual unchanged synthetic bytes cannot authorize a hard-linked
        # STEP artifact: another pathname may rewrite the same inode.
        target = root / "body-a.step"
        original_bytes = target.read_bytes()
        alias = root / "unlisted-hardlink.step"
        os.link(target, alias)
        try:
            try:
                run_case(copy.deepcopy(nonempty), copy.deepcopy(valid), root)
            except Rejected as exc:
                assert "STEP artifact custody:" in str(exc), str(exc)
            else:
                raise AssertionError("hard-linked same-byte STEP artifact admitted")
            rejected += 1
        finally:
            alias.unlink()
            # Windows can retain alias-related metadata across the immediately
            # following handle open. Each fault scenario must start from a
            # clean synthetic inode, not from the previous alias experiment.
            target.unlink()
            target.write_bytes(original_bytes)
        assert target.read_bytes() == original_bytes
        assert run_case(copy.deepcopy(nonempty), copy.deepcopy(valid), root) == STRUCTURAL_ONLY, (
            "hard-link alias cleanup did not restore positive receipt")

        # Deterministically replace the pathname with a fresh same-byte inode
        # AFTER lstat and BEFORE descriptor acquisition; the digest still matches.
        real_open = os.open
        displaced = root / "previous-body-a.step"
        swapped = [False]
        observations = []

        def before_open_swap(path, flags, *args, **kwargs):
            if Path(path).name == target.name and not swapped[0]:
                swapped[0] = True
                before_meta = target.lstat()
                target.replace(displaced)
                target.write_bytes(original_bytes)
                after_meta = target.lstat()
                observations.append((
                    (before_meta.st_dev, before_meta.st_ino, before_meta.st_size,
                     before_meta.st_mtime_ns, before_meta.st_ctime_ns),
                    (after_meta.st_dev, after_meta.st_ino, after_meta.st_size,
                     after_meta.st_mtime_ns, after_meta.st_ctime_ns)))
            return real_open(path, flags, *args, **kwargs)

        try:
            with patch.object(custody.os, "open", side_effect=before_open_swap):
                try:
                    run_case(copy.deepcopy(nonempty), copy.deepcopy(valid), root)
                except Rejected as exc:
                    assert swapped[0], f"pre-open refusal before injected swap: {exc}"
                    assert "STEP artifact custody:" in str(exc), str(exc)
                else:
                    raise AssertionError(
                        f"same-byte STEP inode substitution before open admitted; "
                        f"platform metadata before/after={observations!r}")
            assert swapped[0], "inode-swap injection was not executed"
            assert target.read_bytes() == original_bytes
            rejected += 1
        finally:
            if swapped[0]:
                target.unlink()
                displaced.replace(target)

        # Another adversarial ordering: replace the pathname AFTER the checked
        # fd is opened but BEFORE reading. The fd still sees original bytes.
        real_fdopen = os.fdopen
        attempted = [False]
        os_blocked = [False]

        def during_hash_swap(fd, *args, **kwargs):
            if not attempted[0]:
                attempted[0] = True
                try:
                    target.replace(displaced)
                except OSError:
                    # Windows can deny renaming a file while its checked fd
                    # is live. This is an OS-enforced refusal, not a successful
                    # injection or evidence of the Python metadata guard.
                    os_blocked[0] = True
                    raise
                target.write_bytes(original_bytes)
            return real_fdopen(fd, *args, **kwargs)

        try:
            with patch.object(custody.os, "fdopen", side_effect=during_hash_swap):
                try:
                    run_case(copy.deepcopy(nonempty), copy.deepcopy(valid), root)
                except Rejected as exc:
                    assert "STEP artifact custody:" in str(exc), str(exc)
                else:
                    raise AssertionError("same-byte STEP inode substitution during read admitted")
            assert attempted[0], "during-hash attack was not attempted"
            assert os_blocked[0] or displaced.is_file(), (
                "neither OS refusal nor actual during-hash swap observed")
            assert target.read_bytes() == original_bytes
            rejected += 1
        finally:
            if displaced.exists():
                target.unlink()
                displaced.replace(target)

        # Validate the real raw-byte JSON admission path, not a parsed dict
        # assembled by the fixture. Extra fields are deliberately outside the
        # consumed schema: unsafe scalar decoding must refuse before check().
        def wire_check(manifest_data: bytes, receipt_data: bytes) -> str:
            return check(read_json_bytes(manifest_data), read_json_bytes(receipt_data),
                         manifest_data, root)

        def with_aux(document: bytes, literal: bytes) -> bytes:
            assert document.endswith(b"}"), document
            return document[:-1] + b',"auxiliary":' + literal + b"}"

        original_manifest = as_bytes(nonempty)
        original_receipt = as_bytes(valid)
        good_manifest = with_aux(
            original_manifest, b'{"finite":1.25,"scalar":"\\ud83d\\ude00"}')
        good_receipt = copy.deepcopy(valid)
        good_receipt["manifest_sha256"] = digest(good_manifest)
        assert wire_check(good_manifest, as_bytes(good_receipt)) == STRUCTURAL_ONLY
        assert read_json_bytes(good_manifest)["auxiliary"]["scalar"] == "\U0001f600"
        # This remains a structural-only synthetic test, not STEP qualification.

        def reject_wire(label: str, *, manifest_data: bytes | None = None,
                        receipt_data: bytes | None = None) -> None:
            nonlocal rejected
            raw = original_manifest if manifest_data is None else manifest_data
            rebound = copy.deepcopy(valid)
            rebound["manifest_sha256"] = digest(raw)
            receipt_raw = as_bytes(rebound) if receipt_data is None else receipt_data
            try:
                wire_check(raw, receipt_raw)
            except Rejected:
                rejected += 1
                return
            raise AssertionError(f"ambiguous JSON wire input admitted: {label}")

        reject_wire("positive overflowing exponent in manifest",
                    manifest_data=with_aux(original_manifest, b'1e999'))
        reject_wire("negative overflowing exponent in nested receipt",
                    receipt_data=with_aux(original_receipt, b'{"layer":[-1e999]}'))
        reject_wire("lone high surrogate value in manifest",
                    manifest_data=with_aux(original_manifest, b'"\\ud800"'))
        reject_wire("lone low surrogate as nested receipt key",
                    receipt_data=with_aux(original_receipt, b'{"\\udfff":"x"}'))
        reject_wire("lone high surrogate as nested manifest key",
                    manifest_data=with_aux(original_manifest, b'{"layer":{"\\ud800":2}}'))
        reject_wire("explicit NaN constant still refused",
                    manifest_data=with_aux(original_manifest, b'NaN'))
        reject_wire("explicit Infinity constant still refused",
                    receipt_data=with_aux(original_receipt, b'Infinity'))
        # Raw resource budgets must reject before full JSON allocation/parse,
        # including the actual on-disk CLI ingestion path.
        def reject_ingress(label: str, raw_data: bytes) -> None:
            nonlocal rejected
            try:
                read_json_bytes(raw_data)
            except Rejected:
                rejected += 1
                return
            raise AssertionError(f"pathological raw JSON admitted: {label}")

        over = b'{"padding":"' + b'x' * MAX_JSON_BYTES + b'"}'
        assert len(over) > MAX_JSON_BYTES
        reject_ingress("oversized in-memory JSON", over)
        reject_ingress("over-depth JSON containers",
                       b'{"nested":' + b'[' * MAX_JSON_DEPTH + b'0' +
                       b']' * MAX_JSON_DEPTH + b'}')
        reject_ingress("oversized integer token",
                       b'{"n":' + b'9' * (MAX_JSON_INT_DIGITS + 1) + b'}')
        reject_ingress("unbalanced raw closing delimiter", b'{"n":0}]')

        # Equality boundaries remain accepted, and delimiters inside strings
        # are not containers. These are structural—not engineering—controls.
        at_limit = b'{"padding":"' + b'x' * (MAX_JSON_BYTES - len(b'{"padding":""}')) + b'"}'
        assert len(at_limit) == MAX_JSON_BYTES
        assert len(read_json_bytes(at_limit)["padding"]) > 1000
        at_depth = b'{"nested":' + b'[' * (MAX_JSON_DEPTH - 1) + b'0' + b']' * (MAX_JSON_DEPTH - 1) + b'}'
        assert "nested" in read_json_bytes(at_depth)
        assert read_json_bytes(b'{"n":' + b'9' * MAX_JSON_INT_DIGITS + b'}')["n"] > 0
        assert read_json_bytes(b'{"literal":"[[[{{{"}')["literal"] == "[[[{{{"

        # Python's json.loads(bytes) admits UTF-16/32; the depth scanner
        # must not mistake a non-ASCII code point's low byte for a quote.
        false_quote = "\u0122" + "[" * (MAX_JSON_DEPTH + 8)
        alternate_wire = json.dumps({"literal": false_quote, "n": [1]},
                                    ensure_ascii=False)
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be",
                         "utf-16", "utf-32"):
            recovered = read_json_bytes(alternate_wire.encode(encoding))
            assert recovered["literal"] == false_quote and recovered["n"] == [1]

        # Genuine over-depth JSON must still refuse when encoded as UTF-16/32.
        deep_wire = ('{"nested":' + "[" * MAX_JSON_DEPTH + "0" +
                     "]" * MAX_JSON_DEPTH + "}")
        reject_ingress("UTF-16LE over-depth JSON", deep_wire.encode("utf-16-le"))
        reject_ingress("UTF-32BE over-depth JSON", deep_wire.encode("utf-32-be"))
        reject_ingress("invalid UTF-8 byte sequence",
                       b'{"n":"' + bytes([255]) + b'"}')

        oversized_path = root / "oversized-manifest.json"
        receipt_path = root / "valid-structural-receipt.json"
        oversized_path.write_bytes(over)
        receipt_path.write_bytes(as_bytes(valid))
        try:
            try:
                read_json_file(oversized_path, "manifest")
            except Rejected as exc:
                assert "raw-byte budget" in str(exc), str(exc)
            else:
                raise AssertionError("overbudget disk manifest admitted")
            rejected += 1
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("consumer_receipt_preflight.py")),
                 "--manifest", str(oversized_path), "--receipt", str(receipt_path),
                 "--artifact-root", str(root)],
                capture_output=True, text=True, timeout=15, check=False)
            assert result.returncode == 2 and "REJECTED:" in result.stderr, (
                f"actual CLI did not refuse overbudget file: {result.returncode} {result.stderr!r}")
            rejected += 1
            # The *other* command-line input must obey the same budget.
            oversized_path.write_bytes(as_bytes(nonempty))
            receipt_path.write_bytes(over)
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("consumer_receipt_preflight.py")),
                 "--manifest", str(oversized_path), "--receipt", str(receipt_path),
                 "--artifact-root", str(root)],
                capture_output=True, text=True, timeout=15, check=False)
            assert result.returncode == 2 and "REJECTED:" in result.stderr, (
                f"actual CLI did not refuse overbudget receipt: {result.returncode} {result.stderr!r}")
            rejected += 1
            oversized_path.write_bytes(at_limit)
            parsed, exact_raw = read_json_file(oversized_path, "manifest")
            assert len(exact_raw) == MAX_JSON_BYTES and "padding" in parsed
        finally:
            oversized_path.unlink()
            receipt_path.unlink()

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
    assert rejected == 57, rejected
    print(f"MC-043 PROVISIONAL STRUCTURAL_PREFLIGHT_ONLY: 4 positive synthetic controls; {rejected} rejected corruptions")
    print("No real STEP file, independent consumer process, native permit or MC-E capability qualified")


if __name__ == "__main__":
    main()
