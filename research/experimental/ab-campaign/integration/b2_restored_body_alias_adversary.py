#!/usr/bin/env python3
"""B5: exact-source B2 restored-body alias adversary (research only).

Requires a local CyberSand checkout at the exact B2 source blob below.
No native engine, workers, paid runs or production source are invoked.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

RELATIVE = "research/solver-certificates/invalidation/sparse_fence.py"
EXPECTED_GIT_BLOB = "247974c57ac4e45ac5dc087e387a6920c76bf6d7"
EXPECTED_B2_HEAD = "a7103e7ff74caf4d557a55cefa3b8e3244f6e04b"


def load_exact(root: Path):
    file = root / RELATIVE
    data = file.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()
    if blob != EXPECTED_GIT_BLOB:
        raise RuntimeError("REFUSE: exact B2 module blob mismatch: " + blob)
    spec = importlib.util.spec_from_file_location("b2_source_pinned", file)
    if spec is None or spec.loader is None:
        raise RuntimeError("REFUSE: B2 source module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture(m, workers: int, variant: str) -> dict:
    cells = [m.ROCK] * 16
    cells[0] = m.SAND
    cells[4] = m.EMPTY
    mask = frozenset({0}) if variant == "immutable" else {0}
    restored = m.State(4, 4, cells, body=mask)
    engine = m.Sparse(m.State(4, 4, cells.copy()), tile_size=2)
    fence = m.Fence(engine, workers)
    fence.restore(restored)
    if engine.active:
        raise AssertionError("blocked-pair fixture not certified at restore")
    # Independent full-reference state. State.copy() shares body by identity.
    full = restored.copy()
    if variant == "aliased-unwitnessed":
        mask.clear()
        if engine.state.body is not mask:
            raise AssertionError("restored snapshot unexpectedly deep-owned body")
    events = (("body", ()),) if variant == "witnessed-clear" else ()
    for shard in range(workers):
        event_part = events if shard == 0 else ()
        fence.accept(m.Packet.make(fence.generation, engine.state.tick,
                                   shard, event_part))
    if fence.advance() != "COMMITTED":
        raise AssertionError("complete logical barrier did not commit")
    m.full_step(full, events)
    matching = engine.state == full
    return {
        "variant": variant, "logical_partitions": workers,
        "full_cell_4": full.cells[4], "cached_cell_4": engine.state.cells[4],
        "exact_state_parity": matching, "complete_barrier": True
    }


def run(root: Path):
    m = load_exact(root)
    rows = [fixture(m, w, v) for w in (1, 4)
            for v in ("immutable", "witnessed-clear", "aliased-unwitnessed")]
    for x in rows:
        if x["variant"] == "aliased-unwitnessed":
            assert not x["exact_state_parity"]
            assert x["full_cell_4"] == m.SAND and x["cached_cell_4"] == m.EMPTY
        else:
            assert x["exact_state_parity"]
    return {"status": "EXPECTED_MODEL_BOUNDARY_FALSIFIER",
            "b2_head": EXPECTED_B2_HEAD, "source_blob": EXPECTED_GIT_BLOB,
            "native_parity": "NOT_RUN", "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cybersand-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.cybersand_root), sort_keys=True, indent=2))
