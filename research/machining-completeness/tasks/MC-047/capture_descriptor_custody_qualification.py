#!/usr/bin/env python3
"""MC-047 retained-capture descriptor custody adversarial MODEL_ONLY controls.

No native campaign, manufacturing, recovery mutation or external attestation.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import tempfile
from unittest.mock import patch


CORE_PATH = Path(__file__).resolve().parent.parent / "MC-045" / "campaign_harness.py"


def source_module():
    spec = importlib.util.spec_from_file_location("mc045_capture_descriptor_custody", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("accepted MC-045 capture verifier source unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract() -> None:
    h = source_module()
    checks = 0
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        captures = root / "captures"
        captures.mkdir()
        victim = captures / "000000.stdout.bin"
        stderr = captures / "000000.stderr.bin"
        displaced = root / "preserved-original.stdout.bin"
        row = {
            "stdout_sha256": h.sha256_bytes(b"AAAA"),
            "stderr_sha256": h.sha256_bytes(b""),
        }
        victim.write_bytes(b"AAAA")
        stderr.write_bytes(b"")
        h.verify_retained_captures([row], captures)
        checks += 1

        victim.write_bytes(b"BBBB")
        try:
            h.verify_retained_captures([row], captures)
        except h.ContractError as exc:
            assert "retained capture digest mismatch" in str(exc), exc
        else:
            raise AssertionError("ordinary digest corruption accepted")
        victim.write_bytes(b"AAAA")
        checks += 1

        # Pathname substitution after verifier lstat but before the real
        # descriptor open. New inode has SAME CONTENT AND DIGEST: only a
        # source-bound identity check can discriminate this attack.
        original_open = os.open
        injected = [False]
        before = victim.lstat()
        def substitute_before_open(path, flags, *args, **kwargs):
            if os.fspath(path) == os.fspath(victim) and not injected[0]:
                os.replace(victim, displaced)
                victim.write_bytes(b"AAAA")
                injected[0] = True
            return original_open(path, flags, *args, **kwargs)

        with patch.object(h.os, "open", side_effect=substitute_before_open):
            try:
                h.verify_retained_captures([row], captures)
            except h.ContractError as exc:
                assert "retained capture identity changed before read" in str(exc), exc
            else:
                raise AssertionError("same-digest inode substitution admitted")
        assert injected[0], "pre-open substitution was not executed"
        assert victim.read_bytes() == displaced.read_bytes() == b"AAAA"
        assert victim.lstat().st_ino != before.st_ino, "different inode was not introduced"
        victim.unlink()
        os.replace(displaced, victim)
        h.verify_retained_captures([row], captures)
        checks += 1

        if os.name == "posix":
            # A symlink placed exactly at the descriptor open must fail
            # closed. POSIX O_NOFOLLOW is defense in depth, not the only gate.
            injected = [False]
            def substitute_symlink(path, flags, *args, **kwargs):
                if os.fspath(path) == os.fspath(victim) and not injected[0]:
                    os.replace(victim, displaced)
                    victim.symlink_to(displaced)
                    injected[0] = True
                return original_open(path, flags, *args, **kwargs)
            with patch.object(h.os, "open", side_effect=substitute_symlink):
                try:
                    h.verify_retained_captures([row], captures)
                except h.ContractError as exc:
                    assert "descriptor open refused" in str(exc) or "identity changed" in str(exc), exc
                else:
                    raise AssertionError("symlink substitution admitted")
            assert injected[0] and victim.is_symlink()
            victim.unlink()
            os.replace(displaced, victim)
            checks += 1

            # After the descriptor has been pinned, the pathname is replaced
            # with another identical-byte inode while os.read streams the
            # original descriptor. The final pathname check must refuse.
            original_read = os.read
            injected = [False]
            def substitute_during_read(fd, count):
                if not injected[0]:
                    os.replace(victim, displaced)
                    victim.write_bytes(b"AAAA")
                    injected[0] = True
                return original_read(fd, count)
            with patch.object(h.os, "read", side_effect=substitute_during_read):
                try:
                    h.verify_retained_captures([row], captures)
                except h.ContractError as exc:
                    assert "retained capture changed during read" in str(exc), exc
                else:
                    raise AssertionError("post-open same-digest path substitution admitted")
            assert injected[0] and victim.read_bytes() == displaced.read_bytes() == b"AAAA"
            victim.unlink()
            os.replace(displaced, victim)
            checks += 1

        h.verify_retained_captures([row], captures)
        checks += 1
        assert not displaced.exists()
        assert row["stdout_sha256"] == h.sha256_bytes(victim.read_bytes())
    print(f"MC-047 capture-descriptor custody PASS ({checks} source-bound controls; "
          f"platform={os.name}; MODEL_ONLY, no native/production claim)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true", required=True)
    parser.parse_args()
    contract()


if __name__ == "__main__":
    main()
