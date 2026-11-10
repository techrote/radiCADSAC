"""B1-D1: source-typed exact phase-unit equivalence contract (research only).

Pure Fraction/JSON verifier. It does NOT authenticate external A1/A2/MC-038
producer objects or grant authority to their receipts.
"""
from __future__ import annotations

import copy
from fractions import Fraction
from hashlib import sha256
import json
import re
from certificate_algebra import Refusal as PrimitiveRefusal
from receipt_integrity import (admit as admit_primitive_receipt,
                               validate as validate_primitive_source)

SCHEMA = "b1-typed-phase-source-v1"
RECEIPT = "b1-phase-equivalence-v1"
PRODUCERS = {
    "A1-470": ("281705e947fd7812300d1d2605d3cdf60cdb005e", 1),
    "A2-471": ("3b6eaf70e1e7422b7ac8e8e9ff6f0fef85281978", 2),
    "MC038-main": ("48222d6c40b15ad42cc36d56e6d25f3b284e7fc9", 2),
}
HEX = re.compile(r"[0-9a-f]{64}\Z")
CANON = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


class Refusal(ValueError):
    """Failed source contract or resource cap, never a zero/nonzero decision."""


def exact(x):
    if type(x) is not str or len(x) > 90 or not CANON.fullmatch(x):
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


def _owned(source):
    """One bounded owned primitive tree for BOTH semantic analysis and hashing.

    This is an in-process snapshot, not a trusted external producer/lifetime
    witness. It prevents a caller's later edit from changing only the hash side.
    """
    try:
        validate_primitive_source(source)
        if type(source) is not dict:
            raise Refusal("phase source must be a primitive mapping")
        captured = copy.deepcopy(source)
        validate_primitive_source(captured)
    except PrimitiveRefusal as exc:
        raise Refusal("nonprimitive/overbudget source record") from exc
    return captured


def canonical(source):
    """Normalize one bounded owned source snapshot to pi phase units."""
    return _canonical_owned(_owned(source))


def _canonical_owned(source):
    # Caller has already copied and revalidated exact builtin primitives.
    keys = {"schema", "producer", "producer_head", "origin_source_sha",
            "interval", "offset", "rate", "terms"}
    if type(source) is not dict or set(source) != keys or source["schema"] != SCHEMA:
        raise Refusal("unknown source schema")
    who = source["producer"]
    if not isinstance(who, str) or who not in PRODUCERS:
        raise Refusal("unknown phase convention")
    head, phase_scale = PRODUCERS[who]
    if source["producer_head"] != head:
        raise Refusal("unreviewed producer revision")
    if not isinstance(source["origin_source_sha"], str) or len(source["origin_source_sha"]) != 64 or not HEX.fullmatch(source["origin_source_sha"]):
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
        positives = sorted(int(k) for k in terms if isinstance(k, str) and k != "0" and k.isdigit())
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


def _prove_owned(source, target):
    a, b = _canonical_owned(source), _canonical_owned(target)
    if a != b:
        raise Refusal("phase-normalized functions are not proven identical")
    return {"schema": RECEIPT, "source_hash": digest(source),
            "target_hash": digest(target), "semantic_hash": digest(a)}


def prove_equivalent(source, target):
    """Recompute a model receipt from ONE captured value per original source."""
    return _prove_owned(_owned(source), _owned(target))


def verify(source, target, claim, *, pinned_source_hash, pinned_target_hash):
    """Check a receipt under *caller-supplied trusted* envelope hash pins.

    These pins are NOT a replacement for producer object/codec authentication.
    """
    if type(pinned_source_hash) is not str or len(pinned_source_hash) != 64 or not HEX.fullmatch(pinned_source_hash):
        raise Refusal("invalid trusted source pin")
    if type(pinned_target_hash) is not str or len(pinned_target_hash) != 64 or not HEX.fullmatch(pinned_target_hash):
        raise Refusal("invalid trusted target pin")
    # Admit and bound both records *before* JSON hashing untrusted payloads.
    # Capture before semantics. Reuse the SAME snapshots for proof and pins;
    # re-reading mutable external mappings permits semantic/hash torn reads.
    source_copy, target_copy = _owned(source), _owned(target)
    expected = _prove_owned(source_copy, target_copy)
    if digest(source_copy) != pinned_source_hash or digest(target_copy) != pinned_target_hash:
        raise Refusal("source/target envelope substitution")
    # The submitted receipt is untrusted Python, not necessarily plain JSON.
    # Ordinary dict equality executes hostile __eq__ and confuses bool/int.
    # Reuse E6 bounded builtin-only admission rather than adding another codec.
    try:
        admit_primitive_receipt(expected, claim)
    except PrimitiveRefusal as exc:
        raise Refusal("forged or stale equivalence receipt") from exc
    return True
