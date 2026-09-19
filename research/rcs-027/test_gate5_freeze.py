from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_HEAD = "2a79aa17600e86d2ec2678e9522781b32fbae930"
EXPECTED_RUN = 35417316840
EXPECTED_ARTIFACT = 10577237158
EXPECTED_ARTIFACT_DIGEST = "sha256:8132c933649644c675781b610deb0c002189da8974ea7f3850e1f14c4055272a"
EXPECTED_LIVE_SHA = "7266e6d6d9095532abc8d0f4531b0bd9ef99c8fcb2a25b8422c4a97e8b118121"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def valid_freeze(q: dict, ev: dict, rel: dict) -> bool:
    binding = q.get("evidence_binding", {})
    probe = ev.get("rcs027_closure_probe", {})
    release_binding = rel.get("gate5_evidence_binding", {})
    return all(
        [
            q.get("status") == "accepted",
            q.get("gate5_closure") is True,
            q.get("qualification_status") == "interoperability_unqualified",
            q.get("live_repetitions") == 3,
            q.get("positive_case_count") == 11,
            q.get("negative_controls_passed") == 7,
            q.get("occt_commit") == "b8f597c677811d1f9f4d8a97f5ae2825c0353a42",
            q.get("toolchain", {}).get("compiler_family") == "MSVC",
            q.get("toolchain", {}).get("compiler_version_numeric") == 1951,
            binding.get("source_head_sha") == EXPECTED_HEAD,
            binding.get("workflow_run_id") == EXPECTED_RUN,
            binding.get("artifact_id") == EXPECTED_ARTIFACT,
            binding.get("artifact_digest") == EXPECTED_ARTIFACT_DIGEST,
            binding.get("live_summary_sha256") == EXPECTED_LIVE_SHA,
            ev.get("gate5_status") == "accepted",
            probe.get("status") == "accepted",
            probe.get("qualification_status") == "interoperability_unqualified",
            probe.get("workflow_run_id") == EXPECTED_RUN,
            rel.get("gate5_status") == "accepted",
            rel.get("status") == "gate5_foundation_qualified",
            rel.get("production_repository_creation_authorized") is False,
            rel.get("shared_contracts", {}).get("step_layer_d_status") == "interoperability_unqualified",
            release_binding.get("workflow_run_id") == EXPECTED_RUN,
            release_binding.get("artifact_digest") == EXPECTED_ARTIFACT_DIGEST,
        ]
    )


class Gate5FreezeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.q = load("research/rcs-027/windows-step-qualification-v1.json")
        self.ev = load("research/rcs-027/evidence-matrix-v1.json")
        self.rel = load("handoffs/genesis-release-v2.json")

    def test_accepted_freeze_is_cross_file_coherent(self) -> None:
        self.assertTrue(valid_freeze(self.q, self.ev, self.rel))

    def test_provenance_binding_is_complete_and_hash_shaped(self) -> None:
        b = self.q["evidence_binding"]
        self.assertEqual(b["workflow"], "rcs027-genesis-v2-gate5")
        self.assertEqual(b["workflow_run_number"], 8)
        self.assertEqual(len(b["repetition_summary_sha256"]), 3)
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", x) for x in b["repetition_summary_sha256"]))
        self.assertRegex(b["artifact_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertRegex(b["live_summary_sha256"], r"^[0-9a-f]{64}$")

    def test_rcs026_blocker_is_resolved_without_rewriting_rcs026_history(self) -> None:
        r26 = next(x for x in self.ev["items"] if x["id"] == "RCS-026")
        self.assertEqual(r26["classification"], "accepted_with_gate5_blocker")
        self.assertEqual(r26["blocker_resolution"]["status"], "cleared_by_rcs027")
        self.assertEqual(r26["blocker_resolution"]["workflow_run_id"], EXPECTED_RUN)

    def test_adversarial_layer_d_promotion_invalidates_freeze(self) -> None:
        bad = copy.deepcopy(self.q)
        bad["qualification_status"] = "interoperability_qualified"
        self.assertFalse(valid_freeze(bad, self.ev, self.rel))

    def test_adversarial_artifact_swap_invalidates_freeze(self) -> None:
        bad = copy.deepcopy(self.q)
        bad["evidence_binding"]["artifact_digest"] = "sha256:" + "0" * 64
        self.assertFalse(valid_freeze(bad, self.ev, self.rel))

    def test_adversarial_run_or_pin_drift_invalidates_freeze(self) -> None:
        bad_run = copy.deepcopy(self.q)
        bad_run["evidence_binding"]["workflow_run_id"] += 1
        self.assertFalse(valid_freeze(bad_run, self.ev, self.rel))
        bad_pin = copy.deepcopy(self.q)
        bad_pin["occt_commit"] = "0" * 40
        self.assertFalse(valid_freeze(bad_pin, self.ev, self.rel))

    def test_release_cannot_authorize_production_repo_creation(self) -> None:
        bad = copy.deepcopy(self.rel)
        bad["production_repository_creation_authorized"] = True
        self.assertFalse(valid_freeze(self.q, self.ev, bad))


if __name__ == "__main__":
    unittest.main()
