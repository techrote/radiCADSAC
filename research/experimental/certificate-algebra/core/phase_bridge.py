"""B1-D1: source-typed exact phase-unit equivalence contract (research only).

Pure Fraction/JSON verifier. It does NOT authenticate external A1/A2/MC-038
producer objects or grant authority to their receipts.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
import re

SCHEMA = "b1-typed-phase-source-v1"
RECEIPT = "b1-phase-equivalence-v1"
PRODUCERS = {
    "A1-470": ("281705e947fd7812300d1d2605d3cdf60cdb005e", 1),
    "A2-471": ("38b45dbd028742cca3758a86666d366e9b5df66b", 2),
    "MC038-main": ("48222d6c40b15ad42cc36d56e6d25f3b284e7fc9", 2),
}
HEX = re.compile(r"[0-9a-f]{64}\Z")
CANON = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


class Refusal(ValueError):
    """Failed source contract or resource cap, never a zero/nonzero decision."""


def exact(x):
    if not isinstance(x, str) or len(x) > 90 or not CANON.fullmatch(x):
        raise Refusal("noncanonical or overlong rational")
    try:
        q = Fraction(x)
    except (ValueError, ZeroDivisionError) as e:
        raise Refusal("invalid rational") from e
    if str(q) != x or max(q.numerator.bit_length(), q.denominator.bit_length()) > 128:
        raise Refusal("rational not canonical or exceeds 128-bit cap")
    return q


def encoded(q):
    if max(q.numerator.bit_length(), q.denominator.bit_length()) > 128:
        raise Refusal("transformed rational exceeds 128-bit cap")
    return str(q)


def digest(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def canonical(source):
    """Independently normalize the exact source's native phase units to pi units.

    Returns semantic form only; producer SHA is claimed, not externally verified.
    The coefficient arrays are in physical t, so this does NOT change time or
    knot-sided event orientation. All inputs are strict finite JSON records.
    """
    keys = {"schema", "producer", "producer_head", "origin_source_sha",
            "interval", "offset", "rate", "terms"}
    if not isinstance(source, dict) or set(source) != keys or source["schema"] != SCHEMA:
        raise Refusal("unknown source schema")
    who = source["producer"]
    if not isinstance(who, str) or who not in PRODUCERS:
        raise Refusal("unknown phase convention")
    head, phase_scale = PRODUCERS[who]
    if source["producer_head"] != head:
        raise Refusal("unreviewed producer revision")
    if not isinstance(source["origin_source_sha"], str) or not HEX.fullmatch(source["origin_source_sha"]):
        raise Refusal("malformed producer-supplied source identity")
    interval = source["interval"]
    if not isinstance(interval, list) or len(interval) != 2:
        raise Refusal("bad interval")
    left, right = (exact(v) for v in interval)
    if left >= right:
        raise Refusal("empty/reversed physical domain")
    offset, rate = exact(source["offset"]), exact(source["rate"])
    # Do not admit envelope instances a named producer's actual grammar refuses.
    if who == "A2-471" and rate == 0:
        raise Refusal("A2 refuses stationary phase")
    if who != "A1-470" and (left < -4 or right > 4 or abs(rate) > 4):
        raise Refusal("source exceeds A2/MC038 physical domain")
    max_h, max_poly = ((2, 17) if who == "A1-470" else (8, 4))
    terms = source["terms"]
    if not isinstance(terms, dict) or not 1 <= len(terms) <= (9 if who == "A1-470" else 8):
        raise Refusal("bad harmonic map")
    # Strict zero-mode convention; zero c0 must be explicitly represented.
    if "0" not in terms:
        raise Refusal("missing explicit constant harmonic")
    if who == "A1-470":
        positives = sorted(int(k) for k in terms if k != "0" and k.isdigit())
        if positives != list(range(1, len(positives) + 1)):
            raise Refusal("noncontiguous A1 harmonic channels")
    admitted = {}
    for key, pair in terms.items():
        if not isinstance(key, str) or not re.fullmatch(r"(?:0|[1-8])", key) or int(key) > max_h:
            raise Refusal("bad harmonic index")
        if not isinstance(pair, list) or len(pair) != 2:
            raise Refusal("bad harmonic pair")
        arrays = []
        for poly in pair:
            if not isinstance(poly, list) or not 1 <= len(poly) <= max_poly:
                raise Refusal("bad polynomial length")
            coeff = tuple(exact(v) for v in poly)
            if len(coeff) > 1 and coeff[-1] == 0:
                raise Refusal("noncanonical trailing coefficient")
            arrays.append(tuple(encoded(v) for v in coeff))
        if key == "0" and arrays[1] != ("0",):
            raise Refusal("dead h0 sine is not canonical")
        admitted[key] = (arrays[0], arrays[1])
    return {
        "interval": [encoded(left), encoded(right)],
        "pi_phase": [encoded(phase_scale * offset), encoded(phase_scale * rate)],
        "terms": {k: [list(p), list(q)] for k, (p, q) in sorted(admitted.items(), key=lambda kv: int(kv[0]))},
    }


def prove_equivalent(source, target):
    """Build a reproducible, untrusted semantic-equivalence receipt."""
    a, b = canonical(source), canonical(target)
    if a != b:
        raise Refusal("phase-normalized functions are not proven identical")
    return {"schema": RECEIPT, "source_hash": digest(source),
            "target_hash": digest(target), "semantic_hash": digest(a)}


def verify(source, target, claim, *, pinned_source_hash, pinned_target_hash):
    """Check a receipt under *caller-supplied trusted* envelope hash pins.

    These pins are NOT a replacement for producer object/codec authentication.
    """
    if not isinstance(pinned_source_hash, str) or not HEX.fullmatch(pinned_source_hash):
        raise Refusal("invalid trusted source pin")
    if not isinstance(pinned_target_hash, str) or not HEX.fullmatch(pinned_target_hash):
        raise Refusal("invalid trusted target pin")
    # Admit and bound both records *before* JSON hashing untrusted payloads.
    expected = prove_equivalent(source, target)
    if digest(source) != pinned_source_hash or digest(target) != pinned_target_hash:
        raise Refusal("source/target envelope substitution")
    if not isinstance(claim, dict) or claim != expected:
        raise Refusal("forged or stale equivalence receipt")
    return True
