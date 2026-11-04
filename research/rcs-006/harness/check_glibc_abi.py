#!/usr/bin/env python3
"""Fail closed when a cached OCCT ELF installation requires a newer host glibc.

This guard only establishes dynamic-linker ABI compatibility. It does not verify
OCCT source provenance, solver correctness, geometry, or measured evidence.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

NEED = re.compile(r"\bGLIBC_(\d+(?:\.\d+){1,2})\b")
HOST = re.compile(r"^glibc\s+(\d+(?:\.\d+){1,2})$")


def version(value: str) -> tuple[int, ...]:
    """Make dotted versions comparable without lexical ordering errors."""
    return tuple(int(component) for component in value.split("."))


def needed_versions(readelf_output: str) -> set[tuple[int, ...]]:
    return {version(match) for match in NEED.findall(readelf_output)}


def installed_libraries(prefix: Path) -> list[Path]:
    """Inspect each actual shared ELF object once, including transitive OCCT DSOs."""
    libs: set[Path] = set()
    for directory in (prefix / "lib", prefix / "lib64"):
        if directory.is_dir():
            for candidate in directory.glob("lib*.so*"):
                if candidate.is_file():
                    libs.add(candidate.resolve())
    if not libs:
        raise ValueError(f"no shared OCCT libraries beneath {prefix}")
    return sorted(libs)


def check(prefix: Path) -> tuple[tuple[int, ...], tuple[int, ...], int]:
    try:
        host_text = os.confstr("CS_GNU_LIBC_VERSION")
    except (ValueError, OSError, AttributeError) as exc:
        raise ValueError("host glibc version unavailable") from exc
    match = HOST.fullmatch(host_text or "")
    if not match:
        raise ValueError(f"unrecognized GNU libc version: {host_text!r}")
    host = version(match.group(1))
    requirements: set[tuple[int, ...]] = set()
    libs = installed_libraries(prefix)
    for library in libs:
        try:
            output = subprocess.run(
                ["readelf", "--wide", "--version-info", str(library)],
                text=True, capture_output=True, check=False,
            )
        except OSError as exc:
            raise ValueError(f"cannot inspect ELF symbol versions in {library}: {exc}") from exc
        if output.returncode != 0:
            raise ValueError(
                f"readelf failed for {library}: {output.stderr.strip()}"
            )
        requirements.update(needed_versions(output.stdout))
    highest = max(requirements, default=(0, 0))
    if highest > host:
        raise ValueError(
            f"OCCT ELF requires GLIBC_{'.'.join(map(str, highest))} "
            f"but host provides {'.'.join(map(str, host))}; reject cached install"
        )
    return host, highest, len(libs)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check_glibc_abi.py <OCCT install prefix>", file=sys.stderr)
        return 2
    try:
        host, highest, count = check(Path(args[0]))
    except ValueError as exc:
        print(f"OCCT GLIBC ABI check failed: {exc}", file=sys.stderr)
        return 1
    print(f"OCCT GLIBC ABI compatible: host={host}, required_max={highest}, ELF_objects={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
