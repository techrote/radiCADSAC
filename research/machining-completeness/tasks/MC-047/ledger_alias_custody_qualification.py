#!/usr/bin/env python3
"""MC-047 ledger-alias read-only custody qualification; synthetic MODEL_ONLY.

Runs the actual accepted MC-045 and MC-047 auditors against temporary
filesystem fixtures. No native process, campaign dispatch, or production use.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "MC-045" / "campaign_harness.py"
PREFLIGHT = HERE / "verify.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unavailable actual source: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def qualification() -> None:
    h = load(CORE, "mc045_alias_qualification_source")
    v = load(PREFLIGHT, "mc047_alias_qualification_source")
    permit, plan = v.synthetic_contract()
    h.validate_plan(permit, plan)
    row = h._attempt(permit, plan, 0, 0, "SUCCEEDED")
    checks: list[str] = []

    with tempfile.TemporaryDirectory(prefix="mc047-ledger-alias-") as temp:
        root = Path(temp)
        ledger = root / "ledger.jsonl"
        captures = root / "captures"
        captures.mkdir()
        expected = h.canonical_bytes(row) + b"\n"
        ledger.write_bytes(expected)
        for stream in ("stdout", "stderr"):
            (captures / f"000000.{stream}.bin").write_bytes(b"")

        def positive(label: str) -> None:
            mc045 = h.audit_ledger(permit, plan, ledger, captures)
            mc047 = v.audit(permit, plan, ledger, captures)
            assert mc045["status"] == "LEDGER_REPLAY_VALIDATED_NOT_NATIVE_QUALIFICATION"
            assert mc047["status"] == "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"
            assert mc047["resumption_authorized"] is False
            assert mc047["programme_acceptance_established"] is False
            checks.append(label)

        def must_refuse(func, why: str, label: str) -> None:
            try:
                func()
            except (ValueError, OSError) as exc:
                if why not in str(exc).lower():
                    raise AssertionError(
                        f"{label}: wrong refusal (not the specific alias guard): {exc}"
                    ) from exc
            else:
                raise AssertionError(f"{label}: accepted aliased ledger evidence")
            checks.append(label)

        def mc045(path: Path):
            return h.audit_ledger(permit, plan, path, captures)

        def mc047(path: Path):
            return v.audit(permit, plan, path, captures)

        positive("ordinary unique regular ledger accepted without programme claim")

        alias = root / "external-hard-link.jsonl"
        os.link(ledger, alias)
        try:
            assert alias.stat().st_ino == ledger.stat().st_ino
            assert ledger.stat().st_nlink >= 2
            must_refuse(lambda: mc045(alias), "identity", "MC-045 external hard-link refused")
            must_refuse(lambda: mc047(alias), "hard-linked", "MC-047 external hard-link refused")
            must_refuse(lambda: mc045(ledger), "identity", "MC-045 canonical name with external alias refused")
            must_refuse(lambda: mc047(ledger), "hard-linked", "MC-047 canonical name with external alias refused")
            assert ledger.read_bytes() == expected
        finally:
            alias.unlink()
        positive("ordinary ledger accepted after external alias removed")

        link = root / "symlink-ledger.jsonl"
        symlink_supported = True
        try:
            link.symlink_to(ledger.name)
        except (OSError, NotImplementedError):
            symlink_supported = False
        if symlink_supported:
            try:
                assert link.is_symlink()
                must_refuse(lambda: mc045(link), "symlink", "MC-045 symbolic ledger link refused")
                must_refuse(lambda: mc047(link), "symlink", "MC-047 symbolic ledger link refused")
            finally:
                link.unlink()
        positive("canonical ledger unaffected by symbolic alias test")

        # A same-byte replacement after both initial reads must not pass
        # merely because JSONL syntax and SHA-256 digest are identical.
        # Inject at the real second ledger read inside MC-045 audit_ledger.
        original_loader = h.load_ledger_with_digest
        injection = {"reads": 0, "mutated": False, "old_inode": ledger.stat().st_ino}

        def replace_before_second_read(path: Path):
            injection["reads"] += 1
            if injection["reads"] == 2:
                replacement = root / "same-byte-replacement.jsonl"
                replacement.write_bytes(expected)
                assert replacement.stat().st_ino != injection["old_inode"]
                os.replace(replacement, ledger)
                injection["mutated"] = True
            return original_loader(path)

        h.load_ledger_with_digest = replace_before_second_read
        try:
            must_refuse(
                lambda: mc045(ledger),
                "filesystem identity changed",
                "MC-045 same-bytes ledger inode substitution refused",
            )
            assert injection["reads"] == 2 and injection["mutated"]
        finally:
            h.load_ledger_with_digest = original_loader
        assert ledger.read_bytes() == expected
        positive("new regular ledger after completed deliberate replacement accepted")
        assert not list(root.glob("*.append.lock"))
        for stream in ("stdout", "stderr"):
            assert (captures / f"000000.{stream}.bin").read_bytes() == b""

    assert len(checks) == (12 if symlink_supported else 10), checks
    print(
        f"MC-047 real-source ledger alias custody: {len(checks)} controls PASS; "
        f"symlink={'EXECUTED' if symlink_supported else 'UNAVAILABLE'}; "
        "MODEL_ONLY; no native, STEP, MC-B or MC-1 claim"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if not (args.contract or args.self_test):
        ap.error("explicit --contract or --self-test required; no implicit dispatch")
    qualification()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
