"""B1-E1: source-bound Bernstein product closure (research only).

Input is two *untrusted* B1 base records and external snapshot pins. This
module independently verifies each parent, then composes exact certificates.
It does not authenticate who supplied the pins or any MC/solver event receipt.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb

from receipt_integrity import admit

from certificate_algebra import (
    MAX_BITS, MAX_DEGREE, Certificate, EvidenceMeter, Piece, Refusal,
    Verified, _state, kind, verify_base,
)

SCHEMA = "b1-bernstein-product-v1"


def _parent(raw: dict, pin: str, meter: EvidenceMeter) -> Verified:
    if not isinstance(raw, dict) or set(raw) != {"pieces", "receipts", "hash"}:
        raise Refusal("parent record schema mismatch")
    if not isinstance(raw["pieces"], list) or not isinstance(raw["receipts"], list):
        raise Refusal("parent record arrays required")
    if not isinstance(pin, str) or len(pin) != 64:
        raise Refusal("missing exact external source pin")
    s = verify_base(raw["pieces"], raw["receipts"], meter)
    if s.hash != raw["hash"] or s.hash != pin:
        raise Refusal("untrusted or stale parent source snapshot")
    return s


def _combine(p: Piece, c: Certificate, q: Piece, d: Certificate):
    if (p.left, p.right) != (q.left, q.right):
        raise Refusal("identical ordered physical partitions required")
    n, m = len(c.b) - 1, len(d.b) - 1
    if n + m > MAX_DEGREE:
        raise Refusal("product exceeds polynomial degree budget")
    if c.sign == "ZERO" or d.sign == "ZERO":
        out = Piece(p.left, p.right, (Q(0),))
        return out, Certificate(out.hash, "ZERO", (Q(0),))
    power = tuple(sum(p.coeff[i] * q.coeff[k - i]
                      for i in range(max(0, k - m), min(n, k) + 1))
                  for k in range(n + m + 1))
    out = Piece(p.left, p.right, power)
    b = tuple(sum(c.b[i] * d.b[k - i] * Q(comb(n, i) * comb(m, k - i), comb(n + m, k))
                  for i in range(max(0, k - m), min(n, k) + 1))
              for k in range(n + m + 1))
    if any(max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_BITS for x in b):
        raise Refusal("product Bernstein proof exceeds rational budget")
    sign = "POS" if c.sign == d.sign else "NEG"
    if kind(b) != sign:
        raise Refusal("Bernstein product sign invariant violated")
    return out, Certificate(out.hash, sign, b)


def product(raw_left: dict, raw_right: dict, *, left_pin: str, right_pin: str,
            meter: EvidenceMeter | None = None):
    """Verify both parents and compose a source-bound product witness.

    No fresh output-leaf Bernstein conversion is needed: binomial convolution
    and input proof validity justify the output's Bernstein coefficient array.
    This is a *static source* product, not a Boolean/material operation.
    """
    meter = meter if meter is not None else EvidenceMeter()
    a, b = _parent(raw_left, left_pin, meter), _parent(raw_right, right_pin, meter)
    if len(a.pieces) != len(b.pieces):
        raise Refusal("partition size mismatch")
    pairs = [_combine(p, c, q, d)
             for p, c, q, d in zip(a.pieces, a.certs, b.pieces, b.certs)]
    ps, cs = tuple(x[0] for x in pairs), tuple(x[1] for x in pairs)
    # C0 follows from C0 of each parent and equal cell endpoints: (fg)_-=(fg)_+.
    meter.transform_checks += len(pairs)
    s = _state(ps, cs, max(a.generation, b.generation) + 1)
    witness = {"schema": SCHEMA, "left": a.hash, "right": b.hash,
               "product": s.hash, "leaf_hashes": [p.hash for p in ps],
               "signs": [c.sign for c in cs]}
    return s, witness, meter


def verify_product(raw_left: dict, raw_right: dict, witness: dict, *,
                   left_pin: str, right_pin: str):
    """Independent deterministic replay; never trusts a supplied output sign."""
    # The untrusted witness must NOT be enumerated or compared before exact
    # primitive-tree admission (even set(witness) can run custom key hooks).
    s, reconstructed, meter = product(raw_left, raw_right,
                                      left_pin=left_pin, right_pin=right_pin)
    admit(reconstructed, witness)
    return s, meter
