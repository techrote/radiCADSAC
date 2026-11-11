"""B1-E5: exact sided rational-quotient germ transport (RESEARCH ONLY).

This module imports existing B1 E4 verification; it does not elevate
computational cuts to authenticated physical B-spline knots. Python 3.11+.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q
from math import comb

from certificate_algebra import MAX_BITS, Refusal, digest, enc, frac, piece
from rational_quotient import verify as verify_quotient
from receipt_integrity import admit, validate

SCHEMA = "b1-quotient-sided-germ-v1"


def _enc_bounded(value: Q) -> str:
    """Bound every newly derived exact rational before decimal serialization.

    B1 input budgets do not bound derivatives or signed-affine powers;
    unchecked output can overflow CPython's integer-to-string limit or
    create receipts larger than the primitive admission format permits.
    """
    if (type(value) is not Q or
            max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_BITS):
        raise Refusal("derived sided germ exceeds exact-rational resource budget")
    return enc(value)


def taylor(p, point: Q) -> tuple[Q, ...]:
    """Exact coefficients of P(point+h) in physical-time powers h."""
    if not (p.left <= point <= p.right):
        raise Refusal("jet point outside verified source cell")
    h = (point-p.left)/(p.right-p.left)
    inv = 1/(p.right-p.left)
    return tuple(inv**j * sum(p.coeff[k]*comb(k,j)*h**(k-j)
                 for k in range(j,len(p.coeff)))
                 for j in range(len(p.coeff)))


def _side(ps, t: Q, direction: str):
    if direction == "left":
        found = [p for p in ps if p.left < t <= p.right]
    else:
        found = [p for p in ps if p.left <= t < p.right]
    if len(found) > 1:
        raise Refusal("overlapping source cells")
    return found[0] if found else None


def _germ(n, d, point: Q, direction: str) -> dict:
    pn, pd = _side(n, point, direction), _side(d, point, direction)
    if pn is None or pd is None:
        if pn is not None or pd is not None:
            raise Refusal("mismatched numerator and denominator domains")
        return {"kind": "ABSENT"}
    numerator = taylor(pn, point)
    denominator = taylor(pd, point)
    if denominator[0] == 0:
        raise Refusal("denominator zero at a requested side")
    if all(x == 0 for x in numerator):
        return {"kind": "IDENTITY_ZERO_SIDE"}
    degree = next(j for j, c in enumerate(numerator) if c != 0)
    return {"kind": "FINITE_ORDER", "order": degree,
            "leading": _enc_bounded(numerator[degree]/denominator[0])}


def _seams(ps, t: Q) -> bool:
    return any(a.right == t == b.left for a, b in zip(ps, ps[1:]))


def derive(numerator: dict, denominator: dict, quotient: dict, *,
           numerator_pin: str, denominator_pin: str, time: str):
    """Verify E4 whole-domain receipt before deriving local sided claims.

    External custody of original pins is a caller obligation. The output never
    asserts that a source piece boundary is a genuine structural spline knot.
    """
    # E4 replays complete parents, but E5 previously re-read caller-owned
    # piece dictionaries AFTER that replay. Mutating a coefficient at the E5
    # read produced a false sided germ under the OLD independently held pin.
    # Capture each bounded parent once and use its private values for BOTH
    # E4 admission and local Taylor analysis. No external source custody is
    # claimed by an in-process snapshot.
    validate(numerator)
    validate(denominator)
    if type(numerator) is not dict or type(denominator) is not dict:
        raise Refusal("nonprimitive parent source mapping")
    n_owned, d_owned = copy.deepcopy(numerator), copy.deepcopy(denominator)
    validate(n_owned)
    validate(d_owned)
    original, meter = verify_quotient(n_owned, d_owned, quotient,
                                     numerator_pin=numerator_pin,
                                     denominator_pin=denominator_pin)
    t = frac(time)
    np = tuple(piece(x) for x in n_owned["pieces"])
    dp = tuple(piece(x) for x in d_owned["pieces"])
    if not (np[0].left <= t <= np[-1].right):
        raise Refusal("germ outside authenticated closed source domain")
    actual = {
        "schema": SCHEMA,
        "quotient_hash": original["quotient_hash"],
        "numerator_pin": numerator_pin,
        "denominator_pin": denominator_pin,
        "time": enc(t),
        "left": _germ(np, dp, t, "left"),
        "right": _germ(np, dp, t, "right"),
        "source_piece_boundary_membership": {
            "numerator": _seams(np, t), "denominator": _seams(dp, t)},
        "partition_boundaries": original["physical_knots"],
        "genuine_structural_knot": "UNVERIFIED",
        "source_custody": "EXTERNALLY_PINNED_CONTENT_ONLY",
        "representation": "RATIONAL_C0_LOCAL_GERM_NOT_POLYNOMIAL",
    }
    return {**actual, "germ_hash": digest(actual)}, meter


def verify(numerator: dict, denominator: dict, quotient: dict, proposed: dict,
           *, numerator_pin: str, denominator_pin: str, time: str,
           expected_germ_hash: str | None = None):
    """Independently replay both parent receipt and local formal Taylor germ."""
    if type(proposed) is not dict:
        raise Refusal("missing exact sided-germ receipt")
    actual, meter = derive(numerator, denominator, quotient,
                           numerator_pin=numerator_pin,
                           denominator_pin=denominator_pin, time=time)
    admit(actual, proposed)
    if expected_germ_hash is not None and (
            type(expected_germ_hash) is not str or
            expected_germ_hash != actual["germ_hash"]):
        raise Refusal("expected external germ digest mismatch")
    return actual, meter


def project_signed_affine(germ: dict, *, offset: str, rate: str) -> dict:
    """Pure mathematical projection, NOT authenticated transformed-source proof.

    For physical t=offset+rate*x, rate<0 swaps sides. To promote, independently
    reprove source/denominator and invoke derive on the transformed source.
    """
    admit(germ, germ)  # Reject subclass hooks before accessing untrusted fields.
    # A caller-owned mutable dict may change after the self-hash is checked.
    # Project the exact same bounded primitive snapshot that was authenticated
    # by the self-hash, rather than re-reading the caller\'s later values.
    germ = copy.deepcopy(germ)
    admit(germ, germ)
    if germ.get("schema") != SCHEMA:
        raise Refusal("invalid germ schema")
    if set(germ) != {"schema", "quotient_hash", "numerator_pin", "denominator_pin",
                     "time", "left", "right", "source_piece_boundary_membership",
                     "partition_boundaries", "genuine_structural_knot", "source_custody",
                     "representation", "germ_hash"} or digest(
            {k:v for k,v in germ.items() if k != "germ_hash"}) != germ["germ_hash"]:
        raise Refusal("malformed or modified predecessor germ")
    a, b = frac(offset), frac(rate)
    if not b:
        raise Refusal("noninvertible time map")
    point = frac(germ["time"])
    transformed = []
    for key in (("left", "right") if b > 0 else ("right", "left")):
        side = germ[key]
        if side["kind"] == "FINITE_ORDER":
            k = side["order"]
            if type(k) is not int or not (0 <= k <= 24):
                raise Refusal("invalid or unsupported sided order")
            transformed.append({"kind": "FINITE_ORDER", "order": k,
                                "leading": _enc_bounded(frac(side["leading"])*b**k)})
        elif side["kind"] in ("ABSENT", "IDENTITY_ZERO_SIDE") and set(side) == {"kind"}:
            transformed.append(side)
        else:
            raise Refusal("invalid sided germ record")
    return {"schema": "b1-affine-germ-prediction-v1",
            "input_germ_hash": germ["germ_hash"],
            "time": _enc_bounded((point-a)/b), "left": transformed[0],
            "right": transformed[1],
            "status": "UNBOUND_PREDICTION_REVERIFY_TRANSFORMED_SOURCE",
            "genuine_structural_knot": "UNVERIFIED"}
