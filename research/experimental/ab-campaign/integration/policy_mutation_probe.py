#!/usr/bin/env python3
"""B5 research-only, exact-source B3 policy mutation challenge.

Run against a local checkout of CyberSand PR #555 at the pinned head:
  python3 policy_mutation_probe.py /path/to/cybersand/research/solver-certificates/handoff/handoff_contract.py

No native/CyberSand dependency is installed; the cited research Python module is
loaded read-only after verifying its exact Git blob. No production claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

B3_HEAD = "aedb37ab671888a2c9914ad01d8c33c330cbc3f1"
MODEL_BLOB = "523810bee1d9b219a421557181ecae108d222ef2"
BASE = "d4b18e7f06839b35c8f6a66195206da0f33c5fa3"

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def load_pinned(path: Path):
    content = path.read_bytes()
    actual = git_blob_sha(content)
    if actual != MODEL_BLOB:
        raise RuntimeError(f"REFUSE: expected B3 blob {MODEL_BLOB}; got {actual}")
    name = "b3_pinned_policy_mutation_challenge"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("REFUSE: cannot import pinned B3 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def run(m):
    # Same prepared token, same current generation, epoch and source revision.
    # Only a direct, unversioned research-World policy field mutation differs.
    w = m.World.start(3, [m.Record("water", m.Owner.FREE_MASS, m.WHOLE_CELL)],
                      signed_inertial_world_enabled=False)
    intent = m.prepare(w, token="policy-flip", source_id="water",
                       target=m.Owner.INERTIAL, amount=m.WHOLE_CELL,
                       next_velocity_q256=(0, -8),
                       allow_signed_inertial=True)
    source_before = m.source_signature(w.records["water"])
    identity_before = w.material_identity()
    first = m.commit(w, intent, fenced=True)
    if (first.status != m.ReceiptStatus.REFUSED
            or first.reason != m.Refusal.UNSIGNED_UPWARD):
        raise AssertionError(f"unsigned negative-vertical baseline changed: {first}")
    if w.material_identity() != identity_before:
        raise AssertionError("refusal unexpectedly modified World")
    w.signed_inertial_world_enabled = True
    if (w.generation, w.epoch, m.source_signature(w.records["water"])) != (3, 0, source_before):
        raise AssertionError("unintended epoch/source mutation")
    # The model's full identity changes, but prepare/commit have not pinned
    # that full identity. The subsequent permit is not native policy evidence.
    identity_changed = w.material_identity() != identity_before
    second = m.commit(w, intent, fenced=True)
    bypass = (second.status == m.ReceiptStatus.COMMITTED
              and w.records["water"].owner == m.Owner.INERTIAL
              and w.records["water"].velocity_q256 == (0, -8))
    w.assert_invariants()
    # Ordinary signed construction must remain a positive control.
    signed = m.World.start(4, [m.Record("water", m.Owner.FREE_MASS, m.WHOLE_CELL)],
                           signed_inertial_world_enabled=True)
    positive = m.prepare(signed, token="valid-signed", source_id="water",
                         target=m.Owner.INERTIAL, amount=m.WHOLE_CELL,
                         next_velocity_q256=(0, -8), allow_signed_inertial=True)
    valid_signed = m.commit(signed, positive, fenced=True).status == m.ReceiptStatus.COMMITTED
    if not valid_signed:
        raise AssertionError("legitimate signed World unexpectedly refused")
    return {
        "model_blob": MODEL_BLOB, "b3_head": B3_HEAD, "base_main": BASE,
        "baseline_unsigned_refused": True,
        "policy_changed_without_epoch_or_source_revision": True,
        "full_model_identity_noticed_policy_change": identity_changed,
        "same_prepared_intent_committed_after_untrusted_policy_flip": bypass,
        "valid_signed_control": valid_signed,
        "disposition": "MODEL_POLICY_AUTHORITY_GAP" if bypass else "NO_BYPASS_ON_PINNED_SOURCE",
        "production_authority": "NOT_ESTABLISHED",
        "native_runtime_claim": False,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_path", type=Path)
    args = parser.parse_args()
    result = run(load_pinned(args.model_path))
    print(json.dumps(result, sort_keys=True, indent=2))
