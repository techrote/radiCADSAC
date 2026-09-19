#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rcs026_campaign", HERE / "run_campaign.py")
assert spec and spec.loader
campaign = importlib.util.module_from_spec(spec)
sys.modules["rcs026_campaign"] = campaign
spec.loader.exec_module(campaign)


class RCS026BoundaryTests(unittest.TestCase):
    def test_canonicalizer_is_repeat_stable(self):
        result = campaign.canonicalizer_campaign(repeats=2)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["repeat_signature_count"], 1)

    def test_pending_guard_is_bounded_at_threshold(self):
        result = campaign.run_stream("mixed", 1000)
        self.assertLessEqual(result["reconciliation"]["peak_pending_units"], campaign.PENDING_LIMIT)
        self.assertGreater(result["reconciliation"]["reconciliation_count"], 0)
        self.assertEqual(result["reconciliation"]["final_status"], "reconciled")

    def test_100k_replay_signature_is_deterministic(self):
        first = campaign.run_stream("mill", 100_000)
        second = campaign.run_stream("mill", 100_000)
        self.assertEqual(first["authority_signature_sha256"], second["authority_signature_sha256"])
        self.assertEqual(first["authority"]["journal_sha256"], second["authority"]["journal_sha256"])

    def test_cache_corruption_and_deletion_do_not_change_authority(self):
        result = campaign.cache_recovery_campaign(count=256)
        self.assertTrue(result["delete_recovery"])
        self.assertTrue(result["corruption_recovery"])
        self.assertFalse(result["cache_is_authoritative"])

    def test_crash_is_distinct_from_timeout_and_followed_by_success(self):
        kind, rc, _ = campaign.invoke_worker("crash", 1.0)
        self.assertEqual(kind, "crash")
        self.assertNotEqual(rc, 0)
        kind2, rc2, _ = campaign.invoke_worker("success", 1.0)
        self.assertEqual((kind2, rc2), ("success", 0))

    def test_timeout_is_contained(self):
        kind, rc, _ = campaign.invoke_worker("timeout", 0.05)
        self.assertEqual(kind, "timeout")
        self.assertIsNone(rc)

    def test_forced_kill_is_contained(self):
        kind, rc, _ = campaign.forced_kill_worker()
        self.assertEqual(kind, "forced_kill")
        self.assertIsNotNone(rc)

    def test_step_baseline_preserves_negative_layer_d_status(self):
        result = campaign.step_baseline_contract()
        self.assertEqual(result["qualification_status"], "interoperability_unqualified")
        self.assertEqual(result["occt_baseline"], "8.0.1")


if __name__ == "__main__":
    unittest.main()
