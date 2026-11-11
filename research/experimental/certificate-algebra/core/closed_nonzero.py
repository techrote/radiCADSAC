"""B1-E2: endpoint-complete, closed-domain nonvanishing certificates.

Research only. B1 POS/NEG proves sign on OPEN cells, not knots.
Replays untrusted base/journal/product against external hash pins; pins are
content bindings, NOT signatures or authenticated source-producer custody.
"""
from __future__ import annotations

import re
from typing import Any

from certificate_algebra import EvidenceMeter, Refusal, Verified, enc, replay, verify_base
from receipt_integrity import admit, validate
from product_cone import verify_product

SCHEMA = "b1-closed-nonzero-v1"
_HEX = re.compile(r"[0-9a-f]{64}\Z")


def _pin(value: Any) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise Refusal("external 64-hex snapshot pin required")
    return value


def _closed(s: Verified, provenance: str, pins: tuple[str, ...]) -> dict:
    """Only call on a state already verified by one of the public replay paths.

    The cone gives strict sign in each OPEN piece. B_0 and B_n are exact
    endpoint values. Their strict sign is NECESSARY AND SUFFICIENT for the
    source to retain that sign on each CLOSED piece, within this grammar.
    """
    if not s.pieces or len(s.pieces) != len(s.certs):
        raise Refusal("incomplete verified partition")
    signs = []
    for p, c in zip(s.pieces, s.certs):
        if c.source_hash != p.hash or len(c.b) != len(p.coeff):
            raise Refusal("source/certificate attachment mismatch")
        if c.sign not in ("POS", "NEG") or not c.b:
            raise Refusal("identity-zero or uncertified leaf is not closed-nonzero")
        if c.sign == "POS" and not (c.b[0] > 0 and c.b[-1] > 0):
            raise Refusal("positive open-cell certificate has a zero boundary")
        if c.sign == "NEG" and not (c.b[0] < 0 and c.b[-1] < 0):
            raise Refusal("negative open-cell certificate has a zero boundary")
        signs.append(c.sign)
    # Independently verified C0 forbids a sign change without a zero knot.
    if len(set(signs)) != 1:
        raise Refusal("inconsistent signs across nonzero C0 seams")
    return {
        "schema": SCHEMA,
        "source_class": provenance,
        "parent_pins": list(pins),
        "snapshot_hash": s.hash,
        "generation": s.generation,
        "physical_interval": [enc(s.pieces[0].left), enc(s.pieces[-1].right)],
        "closed_sign": signs[0],
        "pieces": len(s.pieces),
    }


def _expected(actual: dict, proposed: dict | None) -> None:
    if proposed is not None:
        admit(actual, proposed)


def verify_closed_base(raw: dict, *, source_pin: str,
                       proposed: dict | None = None):
    """Replay B1 source/receipts, then prove GLOBAL closed nonvanishing.

    Returns (Verified, receipt, EvidenceMeter); a consumer MUST hold the
    trusted expected pin separately from caller-provided raw fields.
    """
    pin = _pin(source_pin)
    validate(raw)  # Include top-level hash; verify_base guards only child arrays.
    if type(raw) is not dict or set(raw) != {"pieces", "receipts", "hash"}:
        raise Refusal("invalid base record schema")
    ps, cs = raw["pieces"], raw["receipts"]
    if (not isinstance(ps, list) or not isinstance(cs, list)
            or not (1 <= len(ps) <= 512) or len(ps) != len(cs)):
        raise Refusal("invalid bounded base arrays")
    meter = EvidenceMeter()
    s = verify_base(ps, cs, meter)
    if raw["hash"] != s.hash or pin != s.hash:
        raise Refusal("untrusted base source or stale external pin")
    cert = _closed(s, "BASE", (pin,))
    _expected(cert, proposed)
    return s, cert, meter


def verify_closed_journal(log: dict, *, base_pin: str, final_pin: str,
                          proposed: dict | None = None):
    """Replay all split/affine/material-replace steps, binding both epochs.

    This does NOT confer native material dependencies or physical authority.
    """
    before, after = _pin(base_pin), _pin(final_pin)
    # Audit the entire untrusted journal BEFORE .get(), [] or comparisons:
    # a dict/str subclass otherwise invokes hostile Python hooks at this
    # consumer boundary, before replay() can perform its own validation.
    validate(log)
    if (type(log) is not dict or type(log.get("base")) is not dict
            or log["base"].get("hash") != before):
        raise Refusal("journal lacks independently pinned base source")
    meter = EvidenceMeter()
    s, meter = replay(log, meter)
    if s.hash != after:
        raise Refusal("journal terminal state not independently pinned")
    cert = _closed(s, "JOURNAL", (before, after))
    _expected(cert, proposed)
    return s, cert, meter


def verify_closed_product(left: dict, right: dict, product_witness: dict, *,
                          left_pin: str, right_pin: str, product_pin: str,
                          proposed: dict | None = None):
    """Derive endpoint-complete closed sign from a verified B1 product law.

    The product witness must be recomputed by B1's independent verifier;
    no output Bernstein conversion or output seam re-proof is introduced.
    """
    a, b, out = _pin(left_pin), _pin(right_pin), _pin(product_pin)
    s, meter = verify_product(left, right, product_witness,
                              left_pin=a, right_pin=b)
    if s.hash != out:
        raise Refusal("stale or untrusted output product pin")
    cert = _closed(s, "PRODUCT", (a, b, out))
    _expected(cert, proposed)
    return s, cert, meter
