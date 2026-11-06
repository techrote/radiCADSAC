#!/usr/bin/env python3
"""MC-042 provisional exact-byte STEP envelope guard; NO STEP geometry qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[4]
PROFILE = Path("research/machining-completeness/tasks/MC-054/engineering-output-profile-v1.json")
PROFILE_BLOB = "6d9d5924a39e5369a1999c48a9c508dc05fd818e"
MAX_BYTES = 1_048_576  # Provisional preflight limit, NOT a production STEP size policy.
MARKERS = ("ISO-10303-21", "HEADER", "ENDSEC", "DATA", "ENDSEC", "END-ISO-10303-21")
MARKER_RE = re.compile(r"\b(ISO-10303-21|HEADER|DATA|ENDSEC|END-ISO-10303-21)\s*;", re.I)
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class Refused(ValueError):
    """Expected fail-closed admission result, never an engineering verdict."""


def source_pin(expected: str = PROFILE_BLOB) -> None:
    """Bind to the accepted MC-054 profile bytes in this exact checkout."""
    path = ROOT / PROFILE
    if not path.is_file() or path.is_symlink():
        raise Refused("accepted MC-054 profile missing or aliased")
    try:
        result = subprocess.run(
            ["git", "hash-object", str(path)], cwd=ROOT,
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Refused("accepted MC-054 profile Git identity unavailable") from exc
    if result != expected:
        raise Refused("accepted MC-054 profile Git blob changed")


def _same_identity(a: os.stat_result, b: os.stat_result) -> bool:
    # Avoid comparing Windows st_ctime_ns (creation time, not POSIX change time).
    return (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_nlink) == (
        b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_nlink
    )


def bounded_file(path: Path, after_open: Callable[[], None] | None = None) -> bytes:
    """Read from one held descriptor, refuse aliases and pathname replacement.

    Cooperative filesystem custody only; not a hostile-writer atomic snapshot.
    """
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise Refused("STEP input is not a singly linked regular file")
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or not _same_identity(before, opened):
                raise Refused("STEP descriptor/path identity mismatch")
            if after_open is not None:
                after_open()  # Test-only deterministic replacement injection.
            raw = handle.read(MAX_BYTES + 1)
            closed = os.fstat(handle.fileno())
            if len(raw) > MAX_BYTES:
                raise Refused("STEP preflight byte budget exceeded")
            if not _same_identity(opened, closed):
                raise Refused("STEP descriptor changed during read")
        after = path.lstat()
        if not _same_identity(before, after):
            raise Refused("STEP pathname replaced during read")
        return raw
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        raise Refused("STEP input filesystem custody unavailable") from exc


def visible_tokens(text: str) -> str:
    """Mask quoted strings and /* comments */; never mistake their markers for sections."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                raise Refused("unterminated STEP comment")
            for j in range(i, end + 2):
                out[j] = " "
            i = end + 2
        elif text[i] == "'":
            start = i
            i += 1
            while i < n:
                if text[i] == "'":
                    if i + 1 < n and text[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            else:
                raise Refused("unterminated STEP quoted string")
            for j in range(start, i):
                out[j] = " "
        else:
            i += 1
    return "".join(out)


def lexical_envelope(raw: bytes) -> None:
    if not raw:
        raise Refused("empty STEP input is not the MC-054 EMPTY_MATERIAL contract")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise Refused("unsupported non-ASCII STEP envelope input") from exc
    visible = visible_tokens(text)
    found = list(MARKER_RE.finditer(visible))
    if tuple(x.group(1).upper() for x in found) != MARKERS:
        raise Refused("STEP Part-21 envelope sections incomplete or duplicated")
    if visible[:found[0].start()].strip() or visible[found[-1].end():].strip():
        raise Refused("STEP Part-21 envelope has leading or trailing payload")
    header = visible[found[1].end():found[2].start()]
    if not re.search(r"\bFILE_SCHEMA\s*\(", header, re.I):
        raise Refused("STEP header lacks FILE_SCHEMA declaration")
    data = visible[found[3].end():found[4].start()]
    if not re.search(r"#[1-9][0-9]*\s*=\s*(?:[A-Za-z][A-Za-z0-9_]*\s*\(|\()", data):
        raise Refused("STEP DATA lacks a populated entity constructor")
    # This is deliberately NOT a Part-21 parser, AP242 schema check, B-rep check,
    # model validation, geometry measurement, or proof of faithful material.


def inspect(path: Path, expected_sha256: str,
            after_open: Callable[[], None] | None = None) -> dict[str, object]:
    source_pin()
    if not HEX64.fullmatch(expected_sha256):
        raise Refused("expected STEP SHA-256 must be 64 lowercase hex characters")
    raw = bounded_file(path, after_open=after_open)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise Refused("STEP exact-byte SHA-256 mismatch")
    lexical_envelope(raw)
    return {
        "schema": "radicadsac-mc042-step-byte-envelope-preflight/1.0",
        "status": "STRUCTURAL_ENVELOPE_ONLY_NOT_STEP_QUALIFIED",
        "evidence_class": "DETERMINISTIC_MODEL",
        "profile_source_git_blob": PROFILE_BLOB,
        "input_sha256": digest,
        "bytes_inspected": len(raw),
        "native_step_parsed": False,
        "geometry_qualified": False,
        "mc_e_established": False,
        "mc_1_established": False,
        "production_authorized": False,
    }


def self_test() -> None:
    source_pin()
    checks = 0
    good = (
        "ISO-10303-21;\nHEADER;\n"
        "FILE_DESCRIPTION(('synthetic'),'2;1');\n"
        "FILE_SCHEMA(('AP242'));\nENDSEC;\nDATA;\n"
        "#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */');\n"
        "/* quoted decoy HEADER; ENDSEC; */\n"
        "ENDSEC;\nEND-ISO-10303-21;\n"
    ).encode("ascii")
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        path = root / "case.step"

        def accept(blob: bytes) -> None:
            nonlocal checks
            path.write_bytes(blob)
            result = inspect(path, hashlib.sha256(blob).hexdigest())
            assert result["status"] == "STRUCTURAL_ENVELOPE_ONLY_NOT_STEP_QUALIFIED"
            assert result["native_step_parsed"] is False
            assert result["geometry_qualified"] is False
            assert result["production_authorized"] is False
            checks += 1

        def refuse(blob: bytes, *, digest: str | None = None) -> None:
            nonlocal checks
            path.write_bytes(blob)
            try:
                inspect(path, digest if digest is not None else hashlib.sha256(blob).hexdigest())
            except Refused:
                checks += 1
                return
            raise AssertionError("unexpectedly admitted malformed/unsupported STEP input")

        accept(good)
        accept(good.replace(b"HEADER;\n", b"HEADER;\n/* fake DATA; ENDSEC; */\n"))
        accept(good.replace(b"NOT_A_REAL_BREP", b"SYNTHETIC_PLACEHOLDER"))
        refuse(b"")
        refuse(good.replace(b"ISO-10303-21;", b"ISO-10303-20;", 1))
        refuse(good.replace(b"HEADER;", b"HEAD;", 1))
        refuse(good.replace(b"DATA;\n", b"BEGIN_DATA;\n", 1))
        refuse(good.replace(b"END-ISO-10303-21;", b"END-ISO-10303-20;"))
        refuse(good.replace(b"FILE_SCHEMA", b"NO_SCHEMA"))
        refuse(good.replace(b"#1=", b"NO_ENTITY="))
        # A mere #number= token cannot count as an emitted STEP instance.
        refuse(good.replace(
            b"#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */');", b"#1=;"))
        refuse(good.replace(b"ENDSEC;\nDATA;", b"ENDSEC;\nENDSEC;\nDATA;"))
        refuse(good + b"EXTRA;")
        refuse(b"LEADING;" + good)
        refuse(good.replace(b"NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */')",
                            b"NOT_A_REAL_BREP('unterminated)"))
        refuse(good + b"/* unterminated")
        refuse(good.replace(b"FILE_SCHEMA", b"FILE_SCHEM\xff"))
        refuse(good + b" " * (MAX_BYTES + 1))
        refuse(good, digest="0" * 64)
        refuse(good, digest="SHA256-NOT-HEX")
        try:
            source_pin("0" * 40)
        except Refused:
            checks += 1
        else:
            raise AssertionError("changed MC-054 source pin admitted")
        path.write_bytes(good)
        alias = root / "hardlink.step"
        try:
            os.link(path, alias)
        except OSError:
            pass  # Do not claim unsupported platform test exercised.
        else:
            try:
                try:
                    inspect(path, hashlib.sha256(good).hexdigest())
                except Refused:
                    checks += 1
                else:
                    raise AssertionError("hard-linked STEP input accepted")
            finally:
                alias.unlink()
        alias = root / "symlink.step"
        try:
            alias.symlink_to(path)
        except (OSError, NotImplementedError):
            pass
        else:
            try:
                try:
                    inspect(alias, hashlib.sha256(good).hexdigest())
                except Refused:
                    checks += 1
                else:
                    raise AssertionError("symlinked STEP input accepted")
            finally:
                alias.unlink()
        # Inject a real after-open pathname substitution on platforms that allow it.
        path.write_bytes(good)
        replacement = root / "replacement.step"
        replacement.write_bytes(good)
        def swap() -> None:
            replacement.replace(path)
        try:
            inspect(path, hashlib.sha256(good).hexdigest(), after_open=swap)
        except Refused:
            if not replacement.exists():
                checks += 1  # Actual replacement succeeded and was refused.
        else:
            # The bytes were identical; identity, not content digest, MUST
            # detect the real successful pathname substitution.
            if not replacement.exists():
                raise AssertionError("same-byte pathname substitution accepted")
        # On Windows, replacement while descriptor open may be OS-denied; do not
        # count that as an exercised successful substitution.
        print(f"MC-042 source-pinned synthetic byte-envelope preflight: {checks} controls passed; "
              "NO real STEP, geometry or engineering qualification")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--step", type=Path)
    parser.add_argument("--sha256")
    args = parser.parse_args()
    try:
        if args.self_test:
            if args.step is not None or args.sha256 is not None:
                raise Refused("self-test cannot include external STEP inputs")
            self_test()
        else:
            if args.step is None or args.sha256 is None:
                raise Refused("--step and --sha256 are both required")
            print(json.dumps(inspect(args.step, args.sha256), sort_keys=True))
        return 0
    except Refused as exc:
        print(f"MC-042 REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
