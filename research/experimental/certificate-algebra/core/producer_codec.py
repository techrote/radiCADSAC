"""B1-D2: fail-closed adapter for A1/A2 *canonical producer serializations*.

It proves attachment to trusted external SHA-256 source and window pins; it does
not verify who supplied the pins, execute the producer, or authenticate Git code.
"""
from __future__ import annotations

import copy

from phase_bridge import PRODUCERS, SCHEMA, Refusal, digest, exact, prove_equivalent
from certificate_algebra import Refusal as PrimitiveRefusal
from receipt_integrity import validate as validate_primitive_source

CODEC = "b1-source-serialization-codec-v1"


def _require(ok, message):
    if not ok:
        raise Refusal(message)


def _snapshot_source(raw):
    """Capture one bounded primitive source for both parsing and source pin.

    A caller can mutate a producer dict after admission. Parsing the old
    coefficients then hashing the new dict authenticates neither source.
    This local snapshot is NOT independent upstream producer custody.
    """
    try:
        # Guard types/budget before invoking deepcopy or indexing keys.
        validate_primitive_source(raw)
        if type(raw) is not dict:
            raise Refusal("producer source must be a primitive mapping")
        owned = copy.deepcopy(raw)
        validate_primitive_source(owned)
    except PrimitiveRefusal as exc:
        raise Refusal("nonprimitive/overbudget producer source") from exc
    return owned


def _q(x):
    return str(exact(x))


def _window(raw, pinned):
    _require(type(raw) is list and len(raw) == 2, "untrusted physical window")
    lo, hi = map(_q, raw)
    _require(exact(lo) < exact(hi) and digest([lo, hi]) == pinned,
             "missing/mismatched trusted physical window pin")
    return [lo, hi]


def _p(raw, *, a1):
    cap = 17 if a1 else 4
    _require(type(raw) is list and (0 if a1 else 1) <= len(raw) <= cap,
             "invalid polynomial length")
    out = [_q(v) for v in raw]
    _require(not out or out[-1] != "0" or (not a1 and len(out) == 1),
             "noncanonical zero/trailing coefficient")
    return out or ["0"]


def _pin(source, pinned):
    # All nested structures must be validated and bounded BEFORE serialization.
    _require(type(pinned) is str and len(pinned) == 64 and
             all(c in "0123456789abcdef" for c in pinned), "invalid source pin")
    _require(digest(source) == pinned, "source serialization/pin mismatch")


def a1_envelope(raw, window, *, source_pin, window_pin):
    """Bind canonical A1 Source.source_sha JSON and separately pinned domain."""
    raw = _snapshot_source(raw)
    _require(type(raw) is dict and set(raw) == {
        "c0", "cos", "sin", "phase_offset", "phase_rate"}, "bad A1 source fields")
    c0 = _p(raw["c0"], a1=True)
    cos, sin = raw["cos"], raw["sin"]
    _require(type(cos) is list and type(sin) is list and
             len(cos) == len(sin) and len(cos) <= 2, "bad A1 channels")
    terms = {"0": [c0, ["0"]]}
    for i, (p, q) in enumerate(zip(cos, sin), 1):
        terms[str(i)] = [_p(p, a1=True), _p(q, a1=True)]
    offset, rate = _q(raw["phase_offset"]), _q(raw["phase_rate"])
    _pin(raw, source_pin)
    w = _window(window, window_pin)
    return {"schema": SCHEMA, "producer": "A1-470",
            "producer_head": PRODUCERS["A1-470"][0],
            "origin_source_sha": source_pin, "interval": w,
            "offset": offset, "rate": rate, "terms": terms}


def a2_envelope(raw, *, source_pin, window_pin):
    """Bind canonical A2 source_dict()/digest serialization and own domain."""
    raw = _snapshot_source(raw)
    _require(type(raw) is dict and set(raw) == {"interval", "phase", "terms"},
             "bad A2 source fields")
    w = _window(raw["interval"], window_pin)
    phase = raw["phase"]
    _require(type(phase) is list and len(phase) == 2, "bad A2 phase")
    offset, rate = map(_q, phase)
    _require(exact(rate) != 0, "A2 zero phase rate")
    ts = raw["terms"]
    _require(type(ts) is dict and 1 <= len(ts) <= 8 and "0" in ts,
             "bad A2 terms")
    terms = {}
    for h, pair in ts.items():
        _require(type(h) is str and h in [str(i) for i in range(9)] and
                 type(pair) is list and len(pair) == 2, "bad A2 harmonic")
        terms[h] = [_p(pair[0], a1=False), _p(pair[1], a1=False)]
        if h == "0":
            _require(terms[h][1] == ["0"], "noncanonical A2 H0 sine")
    # The current phase bridge is more restrictive than A2's full grammar:
    # unsupported gaps/extra harmonics must fail rather than silently vanish.
    _pin(raw, source_pin)
    return {"schema": SCHEMA, "producer": "A2-471",
            "producer_head": PRODUCERS["A2-471"][0],
            "origin_source_sha": source_pin, "interval": w,
            "offset": offset, "rate": rate, "terms": terms}


def certified_pair(a1_raw, a2_raw, window, *, a1_pin, a2_pin, window_pin):
    """Check equality from raw producer serializations under three EXTERNAL pins."""
    left = a1_envelope(a1_raw, window, source_pin=a1_pin, window_pin=window_pin)
    right = a2_envelope(a2_raw, source_pin=a2_pin, window_pin=window_pin)
    return {"schema": CODEC, "source_pin": a1_pin, "target_pin": a2_pin,
            "physical_window_pin": window_pin,
            "phase_equivalence": prove_equivalent(left, right)}
