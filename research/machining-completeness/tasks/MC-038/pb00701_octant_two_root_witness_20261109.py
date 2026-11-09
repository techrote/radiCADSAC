#!/usr/bin/env python3
"""Exact sufficient two-root certificate inside one source-time phase octant.

MC-038/PB-007-01; prospective DETERMINISTIC_MODEL only. No frozen-original,
source-knot, whole-source, native, STEP or MC-B completeness claims.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
from math import factorial
import unittest

MAX_BITS = 512
PI_TERMS = 28
TAYLOR_TERMS = 25
HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "pb00701-octant-two-root-witness-20261109.json"
MAX_RECEIPT_BYTES = 16_384


class RefusedNontruth(ValueError):
    """Unsupported input or sign undecidable under certified finite budget."""


def rational(value: Q | int) -> Q:
    if type(value) is int:
        value = Q(value)
    if type(value) is not Q:
        raise RefusedNontruth("NON_CANONICAL_RATIONAL")
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_BITS:
        raise RefusedNontruth("INPUT_BIT_BUDGET")
    return value


def atan_bounds(reciprocal: int, count: int) -> tuple[Q, Q]:
    """Alternating arctan series with next-term strict rational error bound."""
    partial = sum(((-1) ** i * Q(1, (2*i+1) * reciprocal**(2*i+1))
                   for i in range(count)), Q(0))
    next_term = Q(1, (2*count+1) * reciprocal**(2*count+1))
    return ((partial, partial + next_term) if count % 2 == 0
            else (partial - next_term, partial))


def pi_bounds() -> tuple[Q, Q]:
    a_low, a_high = atan_bounds(5, PI_TERMS)
    b_low, b_high = atan_bounds(239, PI_TERMS)
    # Machin identity: pi = 16*atan(1/5) - 4*atan(1/239).
    return (16*a_low - 4*b_high, 16*a_high - 4*b_low)


def strict_sign(h: Q, c: Q, s: Q, phase_turns: Q) -> dict[str, str]:
    """Bound h+c*cos(2*pi*q)+s*sin(2*pi*q) by exact rational intervals.

    pi is bounded with Machin alternating series. The midpoint angular
    error is bounded via the 1-Lipschitz property of sine and cosine.
    Taylor remainder uses |theta| < 4 following rational 3 < pi < 4.
    """
    phase_turns = rational(phase_turns)
    q = phase_turns % 1
    if q > Q(1, 2):
        q -= 1
    pl, ph = pi_bounds()
    if not (Q(3) < pl < ph < Q(4)):
        raise AssertionError("broken internal pi interval")
    theta = (pl + ph) * q   # 2*pi_mid*q
    angle_error = abs(q) * (ph - pl)
    sin_poly = sum(((-1)**i * theta**(2*i+1) / factorial(2*i+1)
                    for i in range(TAYLOR_TERMS+1)), Q(0))
    cos_poly = sum(((-1)**i * theta**(2*i) / factorial(2*i)
                    for i in range(TAYLOR_TERMS+1)), Q(0))
    sin_err = angle_error + Q(4)**(2*TAYLOR_TERMS+3) / factorial(2*TAYLOR_TERMS+3)
    cos_err = angle_error + Q(4)**(2*TAYLOR_TERMS+2) / factorial(2*TAYLOR_TERMS+2)
    midpoint = h + c*cos_poly + s*sin_poly
    error = abs(c)*cos_err + abs(s)*sin_err
    lower, upper = midpoint-error, midpoint+error
    if lower > 0:
        sign = "POSITIVE"
    elif upper < 0:
        sign = "NEGATIVE"
    else:
        raise RefusedNontruth("ZERO_OR_SIGN_UNDECIDED")
    # Retain rigorous but compact outward dyadic bounds; do not serialize
    # the enormous unreduced Taylor/Machin intermediate denominators.
    scale = 1 << 40
    lo_dyadic = Q((lower * scale).__floor__(), scale)
    hi_dyadic = Q(-((-upper * scale).__floor__()), scale)
    if (sign == "POSITIVE" and lo_dyadic <= 0 or
        sign == "NEGATIVE" and hi_dyadic >= 0):
        raise RefusedNontruth("DYADIC_RECEIPT_NOT_STRICT")
    return {"sign": sign, "strict_lower": str(lo_dyadic), "strict_upper": str(hi_dyadic)}


def certify(h: Q, c: Q, s: Q, offset: Q, rate: Q,
            left: Q, pivot: Q, right: Q) -> dict:
    """Certify exactly two ordered simple roots bracketed (left,pivot),(pivot,right).

    This is a *sufficient* witness, not a complete procedure for deciding
    arbitrary first-harmonic zeros. Every refusal is NONTRUTH.
    """
    h, c, s, offset, rate, left, pivot, right = (
        rational(x) for x in (h, c, s, offset, rate, left, pivot, right))
    if rate == 0 or c*c+s*s == 0 or not left < pivot < right:
        raise RefusedNontruth("UNSUPPORTED_SOURCE_OR_WITNESS")
    q0, q1 = offset + rate*left, offset + rate*right
    if (abs(q1-q0) != Q(1, 8) or
        (8*q0).denominator != 1 or (8*q1).denominator != 1):
        raise RefusedNontruth("NOT_EXACTLY_ONE_PHASE_OCTANT")
    evaluations = [strict_sign(h,c,s,offset+rate*t) for t in (left,pivot,right)]
    signs = [e["sign"] for e in evaluations]
    if signs[0] != signs[2] or signs[1] == signs[0]:
        raise RefusedNontruth("NO_STRICT_TWO_ROOT_WITNESS")
    values = dict(zip(("h", "c", "s", "offset", "rate", "left", "pivot", "right"),
                      (h, c, s, offset, rate, left, pivot, right)))
    source = {k: str(v) for k,v in values.items()}
    digest = hashlib.sha256(json.dumps(source,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "radicadsac-pb00701-octant-two-root-witness/1.0",
        "status": "COMPLETE_RESTRICTED_SPAN_TWO_SIMPLE_EVENTS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_spec_sha256": digest,
        "source_spec": source,
        "root_count": 2,
        "root_orders": [1, 1],
        "strict_rational_root_brackets": [[str(left),str(pivot)],[str(pivot),str(right)]],
        "ordered_signed_regions": [signs[0],signs[1],signs[2]],
        "point_interval_proofs": dict(zip(("left","pivot","right"),evaluations)),
        "proof": "IVT_TWICE_PLUS_ROLLE_AT_MOST_ONE_INTERIOR_STATIONARY_POINT",
        "source_knot_provenance": "NOT_CLAIMED",
        "historical_new_closures": 0,
        "required_pb_po_discharges": 0,
        "mc_b": "NOT_ESTABLISHED",
        "mc_1": "NOT_ESTABLISHED",
    }


def verify_receipt(receipt: dict) -> bool:
    """Replay the source-bound complete receipt, including every numeric claim.

    This reuses the implementation's interval evaluator; it is source-integrity
    qualification, NOT an independent mathematical oracle.
    """
    if type(receipt) is not dict or type(receipt.get("source_spec")) is not dict:
        raise RefusedNontruth("MALFORMED_RECEIPT")
    source = receipt["source_spec"]
    keys = ("h", "c", "s", "offset", "rate", "left", "pivot", "right")
    if set(source) != set(keys):
        raise RefusedNontruth("RECEIPT_SOURCE_FIELDS")
    args = []
    for k in keys:
        value = source[k]
        if (type(value) is not str or len(value) > 165 or
            re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value) is None):
            raise RefusedNontruth("NONCANONICAL_RECEIPT_RATIONAL")
        try:
            fraction = rational(Q(value))
        except (ValueError, ZeroDivisionError, OverflowError) as error:
            raise RefusedNontruth("NONCANONICAL_RECEIPT_RATIONAL") from error
        if str(fraction) != value:
            raise RefusedNontruth("NONCANONICAL_RECEIPT_RATIONAL")
        args.append(fraction)
    expected = certify(*args)
    if json.dumps(receipt, sort_keys=True, separators=(",", ":")) != json.dumps(
            expected, sort_keys=True, separators=(",", ":")):
        raise RefusedNontruth("RECEIPT_CLAIM_SUBSTITUTION")
    return True


def read_receipt(path: Path = RECEIPT) -> dict:
    """Bound, decode and reject duplicate-key JSON before proof replay."""
    with path.open("rb") as handle:
        raw = handle.read(MAX_RECEIPT_BYTES + 1)
    if len(raw) > MAX_RECEIPT_BYTES:
        raise RefusedNontruth("RECEIPT_BYTE_BUDGET")
    def unique(pairs):
        result={}
        for key, value in pairs:
            if key in result:
                raise RefusedNontruth("DUPLICATE_RECEIPT_KEY")
            result[key]=value
        return result
    def bad_float(value):
        raise RefusedNontruth("RECEIPT_NONINTEGER_JSON_NUMBER")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                          parse_float=bad_float, parse_constant=bad_float)
    except (ValueError, UnicodeDecodeError, RecursionError) as error:
        raise RefusedNontruth("RECEIPT_JSON_REFUSED") from error


def witness(rate=Q(1,8), offset=Q(1,8), pivot=Q(1,4),
            h=Q(199,200), c=Q(-3,5), s=Q(-4,5)):
    return certify(h,c,s,offset,rate,Q(0),pivot,Q(1))


class CertifyTests(unittest.TestCase):
    def test_positive_hidden_two_roots_same_octant(self):
        r = witness()
        self.assertEqual(r["root_count"],2)
        self.assertEqual(r["root_orders"],[1,1])
        self.assertEqual(r["ordered_signed_regions"],["POSITIVE","NEGATIVE","POSITIVE"])
        self.assertEqual(r["strict_rational_root_brackets"],[["0","1/4"],["1/4","1"]])
        self.assertEqual(len(r["source_spec_sha256"]),64)
        for k,sg in zip(("left","pivot","right"),("POSITIVE","NEGATIVE","POSITIVE")):
            e=r["point_interval_proofs"][k]
            self.assertEqual(e["sign"],sg)
            if sg=="POSITIVE": self.assertGreater(Q(e["strict_lower"]),0)
            else: self.assertLess(Q(e["strict_upper"]),0)

    def test_reversed_phase_uses_source_time_order(self):
        r=witness(offset=Q(1,4),rate=-Q(1,8),pivot=Q(3,4))
        self.assertEqual(r["strict_rational_root_brackets"],[["0","3/4"],["3/4","1"]])
        self.assertEqual(r["ordered_signed_regions"],["POSITIVE","NEGATIVE","POSITIVE"])

    def test_maximum_mirrored_signs(self):
        r=witness(h=-Q(199,200),c=Q(3,5),s=Q(4,5))
        self.assertEqual(r["ordered_signed_regions"],["NEGATIVE","POSITIVE","NEGATIVE"])

    def test_periodicity_exact_turns(self):
        r=witness(offset=Q(1,8)+123456789)
        self.assertEqual(r["root_count"],2)

    def test_missing_pivot_sign_refuses(self):
        with self.assertRaisesRegex(RefusedNontruth,"NO_STRICT_TWO_ROOT_WITNESS"):
            witness(pivot=Q(1,2))

    def test_wrong_octant_width_refuses(self):
        with self.assertRaisesRegex(RefusedNontruth,"NOT_EXACTLY_ONE_PHASE_OCTANT"):
            witness(rate=Q(1,4))

    def test_no_harmonic_and_zero_rate_refuse(self):
        with self.assertRaises(RefusedNontruth):
            witness(c=Q(0),s=Q(0))
        with self.assertRaises(RefusedNontruth):
            witness(rate=Q(0))

    def test_boundary_zero_not_misclassified(self):
        with self.assertRaisesRegex(RefusedNontruth,"ZERO_OR_SIGN_UNDECIDED"):
            certify(Q(1),Q(-1),Q(0),Q(0),Q(1,8),Q(0),Q(1,2),Q(1))

    def test_bad_pivot_and_type_refuse(self):
        with self.assertRaises(RefusedNontruth): witness(pivot=Q(0))
        with self.assertRaisesRegex(RefusedNontruth,"NON_CANONICAL_RATIONAL"):
            witness(h=0.995)
        with self.assertRaisesRegex(RefusedNontruth,"INPUT_BIT_BUDGET"):
            witness(h=Q(2**513))

    def test_dyadic_outward_rounding_refuses_if_it_erases_strictness(self):
        eps=Q(1,2**100)
        with self.assertRaisesRegex(RefusedNontruth,"DYADIC_RECEIPT_NOT_STRICT"):
            strict_sign(Q(1)+eps,Q(-1),Q(0),Q(0))
        with self.assertRaisesRegex(RefusedNontruth,"DYADIC_RECEIPT_NOT_STRICT"):
            strict_sign(-Q(1)-eps,Q(1),Q(0),Q(0))

    def test_full_receipt_replay_and_adversarial_substitution(self):
        import copy
        original=witness()
        self.assertTrue(verify_receipt(original))
        for path, false_value in [
            (("root_count",), True),
            (("root_orders",), [2, 1]),
            (("ordered_signed_regions",), ["POSITIVE","POSITIVE","POSITIVE"]),
            (("point_interval_proofs","pivot","sign"), "POSITIVE"),
            (("source_spec_sha256",), "0"*64),
            (("required_pb_po_discharges",), True),
            (("mc_b",), "ESTABLISHED")]:
            bad=copy.deepcopy(original)
            dest=bad
            for key in path[:-1]: dest=dest[key]
            dest[path[-1]]=false_value
            with self.assertRaisesRegex(RefusedNontruth,"RECEIPT_CLAIM_SUBSTITUTION"):
                verify_receipt(bad)

    def test_canonical_input_receipt_rationals_refuse_zero_denominator(self):
        x=witness()
        x["source_spec"]["h"]="1/0"
        with self.assertRaisesRegex(RefusedNontruth,"NONCANONICAL_RECEIPT_RATIONAL"):
            verify_receipt(x)

    def test_duplicate_json_and_receipt_bytes_refuse(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"bad.json"
            file.write_text('{"source_spec":{},"source_spec":{}}', encoding="utf-8")
            with self.assertRaisesRegex(RefusedNontruth,"RECEIPT_JSON_REFUSED"):
                read_receipt(file)
            file.write_bytes(b" "*(MAX_RECEIPT_BYTES+1))
            with self.assertRaisesRegex(RefusedNontruth,"RECEIPT_BYTE_BUDGET"):
                read_receipt(file)

    def test_committed_receipt_exact_replay(self):
        self.assertTrue(verify_receipt(read_receipt()))

    def test_not_source_identity_or_gate_promotion(self):
        r=witness()
        self.assertEqual(r["source_knot_provenance"],"NOT_CLAIMED")
        self.assertEqual(r["historical_new_closures"],0)
        self.assertEqual(r["required_pb_po_discharges"],0)
        self.assertEqual(r["mc_b"],"NOT_ESTABLISHED")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true")
    group.add_argument("--contract",action="store_true")
    group.add_argument("--demo",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(CertifyTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)
    elif args.contract:
        r=read_receipt()
        verify_receipt(r)
        assert r["root_count"]==2 and r["mc_b"]=="NOT_ESTABLISHED"
        print("PASS: rational sign enclosures, strict disjoint two-root witness, nonpromotion",r["source_spec_sha256"])
    else:
        print(json.dumps(witness(),indent=2))


if __name__=="__main__":
    main()
