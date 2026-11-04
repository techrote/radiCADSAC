#!/usr/bin/env python3
"""Deterministic/falsifying controls for cached OCCT GLIBC ABI guard."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_glibc_abi as guard


class GlibcCacheTests(unittest.TestCase):
    def fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        libdir = root / "lib"
        libdir.mkdir()
        (libdir / "libTKMath.so.8.0").write_bytes(b"mock elf")
        (libdir / "libTKMath.so").symlink_to("libTKMath.so.8.0")
        return root

    def evaluate(self, root: Path, host: str, need: str, status: int = 0):
        output = f"Version needs section: Name: GLIBC_{need}\n"
        completed = subprocess.CompletedProcess([], status, output, "invalid ELF")
        with patch.object(guard.os, "confstr", return_value=f"glibc {host}"), \
             patch.object(guard.subprocess, "run", return_value=completed) as reader:
            result = guard.check(root)
        self.assertEqual(reader.call_count, 1, "SONAME symlinks must not cause duplicate probes")
        return result

    def test_acceptable_older_binary_and_equal_host_version(self):
        self.assertEqual(self.evaluate(self.fixture(), "2.39", "2.17")[1], (2, 17))
        self.assertEqual(self.evaluate(self.fixture(), "2.39", "2.39")[1], (2, 39))

    def test_rejects_26_04_glibc_binary_on_24_04(self):
        with self.assertRaisesRegex(ValueError, r"requires GLIBC_2.43.*host provides 2.39"):
            self.evaluate(self.fixture(), "2.39", "2.43")

    def test_numeric_version_comparison_not_lexical(self):
        with self.assertRaisesRegex(ValueError, r"GLIBC_2.10"):
            self.evaluate(self.fixture(), "2.9", "2.10")
        self.evaluate(self.fixture(), "2.10", "2.9")

    def test_rejects_unreadable_elf(self):
        with self.assertRaisesRegex(ValueError, "readelf failed"):
            self.evaluate(self.fixture(), "2.39", "2.17", status=1)

    def test_rejects_missing_libraries(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(guard.os, "confstr", return_value="glibc 2.39"):
            with self.assertRaisesRegex(ValueError, "no shared OCCT libraries"):
                guard.check(Path(directory))

    def test_rejects_unavailable_glibc_version(self):
        with patch.object(guard.os, "confstr", return_value="musl 1.2"):
            with self.assertRaisesRegex(ValueError, "unrecognized GNU libc"):
                guard.check(self.fixture())

    def test_parser_recognizes_transitive_lib_versions(self):
        self.assertEqual(guard.needed_versions("Name: GLIBC_2.17\nName: GLIBC_2.43"), {(2, 17), (2, 43)})
        self.assertEqual(guard.needed_versions("GLIBCXX_3.4.33 CXXABI_1.3"), set())


if __name__ == "__main__":
    unittest.main()
