"""B1-E3: complete union-of-breakpoints product, research only.

The B1 parent records/pins must come from trusted independent custody.
This module consumes verified rational C0 polynomial sources, NOT native
B-spline control vectors, A2 trigonometric germs, or topology receipts.
"""
from __future__ import annotations

import re
from certificate_algebra import (EvidenceMeter, Refusal, Verified, _state,
                                 enc, events, split, verify_base)
from product_cone import _combine
from receipt_integrity import admit

SCHEMA = "b1-refined-product-v1"
MAX_REFINED_PIECES = 128
_PIN = re.compile(r"[0-9a-f]{64}\Z")


def _parent(raw: dict, external_pin: str, meter: EvidenceMeter) -> Verified:
    if type(external_pin) is not str or _PIN.fullmatch(external_pin) is None:
        raise Refusal("independent 64-hex parent pin required")
    if type(raw) is not dict or set(raw) != {"pieces", "receipts", "hash"}:
        raise Refusal("invalid untrusted parent schema")
    if type(raw["pieces"]) is not list or type(raw["receipts"]) is not list:
        raise Refusal("invalid parent arrays")
    state = verify_base(raw["pieces"], raw["receipts"], meter)
    if raw["hash"] != state.hash or external_pin != state.hash:
        raise Refusal("stale or substituted parent source")
    return state


def _refine(s: Verified, boundaries: tuple, meter: EvidenceMeter) -> Verified:
    """Apply existing B1 rational de Casteljau split; never re-prove leaves."""
    for cut in boundaries[1:-1]:
        if any(p.left == cut or p.right == cut for p in s.pieces):
            continue
        indices = [i for i, p in enumerate(s.pieces) if p.left < cut < p.right]
        if len(indices) != 1:
            raise Refusal("missing physical coverage at refinement cut")
        s = split(s, indices[0], cut, meter)
    if tuple([s.pieces[0].left] + [p.right for p in s.pieces]) != boundaries:
        raise Refusal("refinement did not cover exact physical knots")
    return s


def derive(left: dict, right: dict, *, left_pin: str, right_pin: str):
    """Return (verified output, reproducible receipt, proof-work meter).

    Both externally pinned parents are replayed in full. Internal knot unions
    are deterministic; parent leaves are split by the existing B1 checker.
    Product coefficients use the existing B1 exact binomial convolution.
    """
    meter = EvidenceMeter()
    a = _parent(left, left_pin, meter)
    b = _parent(right, right_pin, meter)
    if a.pieces[0].left != b.pieces[0].left or a.pieces[-1].right != b.pieces[-1].right:
        raise Refusal("parents have different physical domains")
    knots = tuple(sorted({t for s in (a, b) for p in s.pieces
                          for t in (p.left, p.right)}))
    if len(knots) - 1 > MAX_REFINED_PIECES:
        raise Refusal("union partition exceeds bounded research budget")
    aa, bb = _refine(a, knots, meter), _refine(b, knots, meter)
    pairs = [_combine(p, c, q, d) for p, c, q, d in
             zip(aa.pieces, aa.certs, bb.pieces, bb.certs)]
    if len(pairs) != len(knots) - 1:
        raise Refusal("unmatched refined source leaves")
    out = _state(tuple(p for p, _ in pairs), tuple(c for _, c in pairs),
                 max(aa.generation, bb.generation) + 1)
    meter.transform_checks += len(pairs)
    proof = {"schema": SCHEMA, "original_pins": [a.hash, b.hash],
             "physical_knots": [enc(t) for t in knots],
             "aligned_hashes": [aa.hash, bb.hash], "product_hash": out.hash,
             "leaf_hashes": [p.hash for p in out.pieces],
             "leaf_signs": [c.sign for c in out.certs], "events": events(out)}
    return out, proof, meter


def verify(left: dict, right: dict, proposed: dict, *, left_pin: str,
           right_pin: str, expected_product_pin: str | None = None):
    """Replay an untrusted receipt. 'expected_product_pin' is external custody.

    A caller-authored new pin is not a producer signature or physical authority.
    """
    if type(proposed) is not dict:
        raise Refusal("missing proposed receipt")
    out, expected, meter = derive(left, right, left_pin=left_pin,
                                  right_pin=right_pin)
    admit(expected, proposed)
    if expected_product_pin is not None:
        if type(expected_product_pin) is not str or _PIN.fullmatch(expected_product_pin) is None or expected_product_pin != out.hash:
            raise Refusal("untrusted output source version")
    return out, meter
