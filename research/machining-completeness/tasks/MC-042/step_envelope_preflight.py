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


def visible_tokens(text: str, *, mark_strings: bool = False) -> str:
    """Mask comments and strings; optionally mark detached string payload.

    Section recognition needs quote-masked text so quoted marker decoys are
    ignored. Structural inspection needs one non-whitespace sentinel per
    quoted string so an otherwise detached literal cannot disappear as space.
    """
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
            if mark_strings:
                out[start] = "?"
        else:
            i += 1
    return "".join(out)


def _balanced_parentheses(segment: str) -> bool:
    """Cheap lexical refusal only; strings and comments have already been masked."""
    depth = 0
    for ch in segment:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


# Conservative lexical instance starts. Strings/comments have already been masked.
ENTITY_BEGIN_RE = re.compile(r"#[1-9][0-9]*\s*=\s*(?:[A-Za-z][A-Za-z0-9_]*\s*\(|\()")
HEADER_BEGIN_RE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*\(")


def _has_complete_header_inventory(header: str) -> bool:
    """Require every provisional HEADER constructor to terminate with ';'.

    Only a conservative lexical check on already masked strings/comments;
    not full Part-21 header-schema or AP242 parsing.
    """
    pos, n, schema_count = 0, len(header), 0
    while True:
        while pos < n and header[pos].isspace():
            pos += 1
        if pos == n:
            return schema_count == 1
        match = HEADER_BEGIN_RE.match(header, pos)
        if match is None:
            return False
        if match.group(1).upper() == "FILE_SCHEMA":
            schema_count += 1
            if schema_count > 1:
                return False
        depth = 1
        pos = match.end()
        while pos < n:
            ch = header[pos]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        if depth != 0:
            return False
        pos += 1
        while pos < n and header[pos].isspace():
            pos += 1
        if pos == n or header[pos] != ";":
            return False
        pos += 1


def _has_complete_entity_inventory(data: str) -> bool:
    """Require *every* top-level DATA item to finish, not merely the first.

    This is a bounded, deliberately incomplete lexical sentinel, not STEP
    entity-grammar validation. Reject any unsupported instance form/junk.
    """
    pos, n, found = 0, len(data), False
    while True:
        while pos < n and data[pos].isspace():
            pos += 1
        if pos == n:
            return found
        match = ENTITY_BEGIN_RE.match(data, pos)
        if match is None:
            return False
        depth = 1
        pos = match.end()  # Includes the constructor's opening '('.
        while pos < n:
            ch = data[pos]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        if depth != 0:
            return False
        pos += 1
        while pos < n and data[pos].isspace():
            pos += 1
        if pos == n or data[pos] != ";":
            return False
        pos += 1
        found = True


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
    structural = visible_tokens(text, mark_strings=True)
    # All five regions outside HEADER/DATA are comments-or-whitespace only.
    # The plain masked view previously erased detached quoted payload and
    # neglected the three inter-section gaps entirely.
    for start, end in (
        (0, found[0].start()),
        (found[0].end(), found[1].start()),
        (found[2].end(), found[3].start()),
        (found[4].end(), found[5].start()),
        (found[5].end(), len(text)),
    ):
        if structural[start:end].strip():
            raise Refused("STEP Part-21 envelope has detached or inter-section payload")
    header = structural[found[1].end():found[2].start()]
    if not _has_complete_header_inventory(header):
        raise Refused("STEP HEADER contains unfinished, duplicate-schema or trailing record text")
    data = structural[found[3].end():found[4].start()]
    if not _balanced_parentheses(header) or not _balanced_parentheses(data):
        raise Refused("STEP header or DATA contains unbalanced parentheses")
    if not _has_complete_entity_inventory(data):
        raise Refused("STEP DATA contains unfinished, unsupported or trailing entity text")
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
        # Additional complete HEADER record must not be mistaken for junk.
        accept(good.replace(b"FILE_SCHEMA(('AP242'));",
                            b"FILE_NAME('synthetic');\nFILE_SCHEMA(('AP242'));"))
        # Comments are still legal in every inter-section gap. Quoted section
        # decoys inside constructors also remain masked for section inventory.
        accept(good.replace(b"ISO-10303-21;\nHEADER;",
                            b"ISO-10303-21;\n/* pre-header */\nHEADER;")
                   .replace(b"ENDSEC;\nDATA;",
                            b"ENDSEC;\n/* pre-data */\nDATA;")
                   .replace(b"ENDSEC;\nEND-ISO-10303-21;",
                            b"ENDSEC;\n/* pre-footer */\nEND-ISO-10303-21;"))
        # The sentinel must admit a complete multiple-entity inventory,
        # including a complex instance, without interpreting the geometry.
        decoy = b"/* quoted decoy HEADER; ENDSEC; */"
        accept(good.replace(decoy, b"#2=SECOND('DATA; ENDSEC;');\n" + decoy))
        accept(good.replace(decoy, b"#2=(FIRST(),SECOND('HEADER;'));\n" + decoy))
        refuse(b"")
        refuse(good.replace(b"ISO-10303-21;", b"ISO-10303-20;", 1))
        refuse(good.replace(b"HEADER;", b"HEAD;", 1))
        refuse(good.replace(b"DATA;\n", b"BEGIN_DATA;\n", 1))
        refuse(good.replace(b"END-ISO-10303-21;", b"END-ISO-10303-20;"))
        refuse(good.replace(b"FILE_SCHEMA", b"NO_SCHEMA"))
        # Missing HEADER statement semicolons and arbitrary trailing payload
        # previously passed the FILE_SCHEMA presence-only search.
        refuse(good.replace(b"FILE_SCHEMA(('AP242'));", b"FILE_SCHEMA(('AP242'))"))
        refuse(good.replace(b"FILE_DESCRIPTION(('synthetic'),'2;1');",
                            b"FILE_DESCRIPTION(('synthetic'),'2;1')"))
        refuse(good.replace(b"ENDSEC;\nDATA;", b"JUNK_AFTER_SCHEMA\nENDSEC;\nDATA;"))
        refuse(good.replace(b"FILE_SCHEMA(('AP242'));",
                            b"FILE_SCHEMA(('AP242'));\nFILE_SCHEMA(('AP242'));"))
        # Source-matched gap/quote regression: formerly all these candidates
        # were admitted despite detached payload outside complete records.
        for before, after in (
            (b"ISO-10303-21;\nHEADER;", b"ISO-10303-21;\nJUNK\nHEADER;"),
            (b"ENDSEC;\nDATA;", b"ENDSEC;\nJUNK\nDATA;"),
            (b"ENDSEC;\nEND-ISO-10303-21;",
             b"ENDSEC;\nJUNK\nEND-ISO-10303-21;"),
        ):
            assert before in good
            refuse(good.replace(before, after, 1))
        for mutant in (
            b"'detached'\n" + good,
            good + b"\n'detached'",
            good.replace(b"ISO-10303-21;\nHEADER;",
                         b"ISO-10303-21;\n'detached'\nHEADER;", 1),
            good.replace(b"ENDSEC;\nDATA;",
                         b"ENDSEC;\n'detached'\nDATA;", 1),
            good.replace(b"ENDSEC;\nEND-ISO-10303-21;",
                         b"ENDSEC;\n'detached'\nEND-ISO-10303-21;", 1),
            good.replace(b"FILE_SCHEMA(('AP242'));",
                         b"FILE_SCHEMA(('AP242')); 'detached';", 1),
            good.replace(b"#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */');",
                         b"#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */'); 'detached';", 1),
        ):
            assert mutant != good
            refuse(mutant)
        refuse(good.replace(b"#1=", b"NO_ENTITY="))
        # A mere #number= token cannot count as an emitted STEP instance.
        refuse(good.replace(
            b"#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */');", b"#1=;"))
        # A present envelope cannot hide an unfinished constructor or missing
        # entity terminator, even though this is not a full STEP parser.
        original_entity = b"#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */');"
        refuse(good.replace(original_entity, b"#1=UNTERMINATED("))
        refuse(good.replace(original_entity,
                            b"#1=NOT_A_REAL_BREP('ENDSEC; DATA; /* not a comment */')"))
        refuse(good.replace(original_entity, original_entity + b")"))
        # Old "at least one terminated entity" logic admitted malformed
        # second instances or trailing text after an otherwise valid #1.
        # Each mutation is a genuine on-disk candidate with its own digest.
        for trailing in (
            b"#2=;\n",                       # Empty entity.
            b"#2=UNKNOWN\n",                  # No constructor/terminator.
            b"#2=SECOND()\n",                 # Missing ';'.
            b"#2=SECOND(1); #3=;\n",         # Valid second, invalid third.
            b"JUNK_AFTER_FIRST\n",           # Not an instance at all.
            b"#2=SECOND(1); EXTRA\n",        # Valid second, trailing junk.
        ):
            mutant = good.replace(decoy, trailing + decoy)
            assert mutant != good
            refuse(mutant)
        refuse(good.replace(b"FILE_SCHEMA(('AP242'));", b"FILE_SCHEMA(('AP242');"))
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
