#!/usr/bin/env python3
"""Exact, finite-budget certificates for a restricted polynomial/H1/H2 event grammar.

DETERMINISTIC_MODEL / research only. A returned COMPLETE means a checkable
partition; an exhausted search is NONTRUTH and establishes no root count.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
import unittest

MAX_COEFF_BITS = 128
MAX_PIECES = 4
MAX_DEGREE = 3
MAX_NODES = 256
MAX_DEPTH = 28
MAX_BITS = 16
PRECISIONS = (6, 10, 16, 24)
KEYS = ("H0", "C1", "S1", "C2", "S2")


class Nontruth(ValueError):
    """An unsupported or unproved assertion must not become a truth receipt."""


def need(condition: bool, reason: str):
    if not condition:
        raise Nontruth(reason)


def fraction(raw: str) -> Q:
    need(type(raw) is str and 0 < len(raw) <= 100 and
         all(ch in "-0123456789/" for ch in raw), "RATIONAL_TOKEN")
    try:
        result = Q(raw)
    except (ZeroDivisionError, ValueError) as exc:
        raise Nontruth("INVALID_RATIONAL") from exc
    need(str(result) == raw, "NONCANONICAL_RATIONAL")
    need(max(abs(result.numerator).bit_length(), result.denominator.bit_length())
         <= MAX_COEFF_BITS, "RATIONAL_BIT_BUDGET")
    return result


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


@dataclass(frozen=True)
class Piece:
    lo: Q
    hi: Q
    polys: tuple[tuple[Q, ...], ...]


@dataclass(frozen=True)
class Source:
    phase_offset: Q
    phase_slope: Q
    pieces: tuple[Piece, ...]
    identity: str


def parse_source(doc: dict) -> Source:
    need(type(doc) is dict and set(doc) ==
         {"phase_offset_pi", "phase_slope_pi", "pieces"}, "SOURCE_FIELDS")
    a, b = fraction(doc["phase_offset_pi"]), fraction(doc["phase_slope_pi"])
    rows = doc["pieces"]
    need(type(rows) is list and 1 <= len(rows) <= MAX_PIECES, "PIECE_BUDGET")
    pieces = []
    for row in rows:
        need(type(row) is dict and set(row) == {"lo", "hi", *KEYS},
             "PIECE_FIELDS")
        lo, hi = fraction(row["lo"]), fraction(row["hi"])
        need(Q(-8) <= lo < hi <= Q(8), "PIECE_DOMAIN")
        polys = []
        for key in KEYS:
            value = row[key]
            need(type(value) is list and 1 <= len(value) <= MAX_DEGREE + 1,
                 "POLYNOMIAL_GRAMMAR")
            polys.append(tuple(fraction(x) for x in value))
        pieces.append(Piece(lo, hi, tuple(polys)))
    for left, right in zip(pieces, pieces[1:]):
        need(left.hi == right.lo, "NONCONTIGUOUS_SPANS")
        # Coefficient continuity is a deliberately strong sufficient rule;
        # actual spline controls/source grammar require separate authority.
        for p, q in zip(left.polys, right.polys):
            need(poly_at(p, left.hi) == poly_at(q, right.lo),
                 "KNOT_COEFFICIENT_DISCONTINUITY")
    return Source(a, b, tuple(pieces), hashlib.sha256(canonical(doc)).hexdigest())


def poly_at(coeff: tuple[Q, ...], t: Q) -> Q:
    out = Q(0)
    for c in reversed(coeff):
        out = out*t + c
    return out


def derivative(coeff: tuple[Q, ...]) -> tuple[Q, ...]:
    return tuple(i*c for i, c in enumerate(coeff) if i) or (Q(0),)


def add(*intervals):
    return (sum((v[0] for v in intervals), Q(0)),
            sum((v[1] for v in intervals), Q(0)))


def mul(x, y):
    products = (x[0]*y[0], x[0]*y[1], x[1]*y[0], x[1]*y[1])
    return min(products), max(products)


def point(value):
    return value, value


def poly_interval(coeff: tuple[Q, ...], lo: Q, hi: Q):
    out = point(Q(0))
    for c in reversed(coeff):
        out = add(mul(out, (lo, hi)), point(c))
    return out


@lru_cache(maxsize=8)
def pi_interval(terms: int):
    """Exact Machin bounds, each pair has an alternating arctan remainder."""
    need(type(terms) is int and terms in PRECISIONS, "PI_BUDGET")

    def atan(k):
        x = Q(1, k)
        lower = sum(((-1)**j*x**(2*j+1)/Q(2*j+1)
                     for j in range(2*terms)), Q(0))
        upper = lower + x**(4*terms+1)/Q(4*terms+1)
        return lower, upper

    al, ah = atan(5)
    bl, bh = atan(239)
    lower, upper = 16*al - 4*bh, 16*ah - 4*bl
    need(Q(3) < lower < upper < Q(22, 7), "PI_ENCLOSURE")
    return lower, upper


@lru_cache(maxsize=4096)
def trig_point(k: Q, terms: int):
    """Enclose sin(pi*k), cos(pi*k) by exact rational Taylor/Lagrange bounds.

    Exact reduction modulo 2 is valid for the point argument, and phase
    movement over cells is handled separately using global Lipschitz bounds.
    """
    k = k % 2
    if k > 1:
        k -= 2
    pl, ph = pi_interval(terms)
    x, y = sorted((k*pl, k*ph))
    z, rho = (x+y)/2, (y-x)/2
    need(abs(z) < Q(22, 7), "TAYLOR_ARGUMENT")
    sine = sum(((-1)**j*z**(2*j+1)/factorial(2*j+1)
                for j in range(terms+1)), Q(0))
    cosine = sum(((-1)**j*z**(2*j)/factorial(2*j)
                  for j in range(terms+1)), Q(0))
    # Lagrange remainder (absolute derivative <= 1), not a sampled error.
    se = abs(z)**(2*terms+2)/factorial(2*terms+2) + rho
    ce = abs(z)**(2*terms+1)/factorial(2*terms+1) + rho
    return (sine-se, sine+se), (cosine-ce, cosine+ce)


def trig_cell(source: Source, harmonic: int, lo: Q, hi: Q, terms: int):
    mid = (lo+hi)/2
    sine, cosine = trig_point(harmonic*(source.phase_offset +
                                       source.phase_slope*mid), terms)
    _, pi_hi = pi_interval(terms)
    radius = abs(harmonic*source.phase_slope) * pi_hi * (hi-lo)/2
    return ((sine[0]-radius, sine[1]+radius),
            (cosine[0]-radius, cosine[1]+radius))


def bounds(source: Source, piece: Piece, lo: Q, hi: Q, terms: int):
    need(piece.lo <= lo <= hi <= piece.hi, "CELL_OUTSIDE_SOURCE_SPAN")
    vals = [poly_interval(p, lo, hi) for p in piece.polys]
    deriv = [poly_interval(derivative(p), lo, hi) for p in piece.polys]
    f, df = vals[0], deriv[0]
    for harmonic, ci, si in ((1, 1, 2), (2, 3, 4)):
        if not (any(piece.polys[ci]) or any(piece.polys[si])):
            continue
        sine, cosine = trig_cell(source, harmonic, lo, hi, terms)
        f = add(f, mul(vals[ci], cosine), mul(vals[si], sine))
        kpi = mul(point(harmonic*source.phase_slope), pi_interval(terms))
        df = add(df, mul(deriv[ci], cosine), mul(deriv[si], sine),
                 mul(kpi, add(mul(vals[si], cosine),
                              mul(point(Q(-1)), mul(vals[ci], sine)))))
    return f, df


def strict_sign(interval):
    return 1 if interval[0] > 0 else -1 if interval[1] < 0 else 0


@lru_cache(maxsize=8192)
def point_sign(source: Source, piece: Piece, t: Q):
    for n in PRECISIONS:
        f, _ = bounds(source, piece, t, t, n)
        sign = strict_sign(f)
        if sign:
            return sign
    return 0


def classify(source: Source, bits=12, max_nodes=MAX_NODES,
             max_depth=MAX_DEPTH):
    need(type(bits) is int and 1 <= bits <= MAX_BITS, "BITS_BUDGET")
    need(type(max_nodes) is int and 1 <= max_nodes <= MAX_NODES and
         type(max_depth) is int and 1 <= max_depth <= MAX_DEPTH,
         "SEARCH_BUDGET")
    leaves = []
    count = 0
    for idx, piece in enumerate(source.pieces):
        left, right = point_sign(source, piece, piece.lo), point_sign(
            source, piece, piece.hi)
        need(left != 0 and right != 0, "KNOT_OR_EXTERIOR_SIGN_NONTRUTH")
        if idx:
            need(leaves[-1]["right_sign"] == left,
                 "KNOT_SIGN_MISMATCH")

        def walk(a: Q, b: Q, depth: int):
            nonlocal count
            count += 1
            need(count <= max_nodes and depth <= max_depth,
                 "REFINEMENT_BUDGET_NONTRUTH")
            for n in PRECISIONS:
                f, d = bounds(source, piece, a, b, n)
                fs = strict_sign(f)
                if fs:
                    la, rb = fs, fs  # Cell enclosure proves both endpoints as well.
                    leaves.append({"piece": idx, "lo": str(a), "hi": str(b),
                                   "kind": "ROOT_FREE_INTERVAL", "precision": n,
                                   "left_sign": fs, "right_sign": fs})
                    return
                ds = strict_sign(d)
                if ds:
                    la, rb = point_sign(source, piece, a), point_sign(source, piece, b)
                    if la and rb:
                        if la == rb:
                            leaves.append({"piece": idx, "lo": str(a), "hi": str(b),
                                           "kind": "ROOT_FREE_MONOTONE", "precision": n,
                                           "left_sign": la, "right_sign": rb,
                                           "derivative_sign": ds})
                            return
                        need(la == -rb and la == -ds and rb == ds,
                             "MONOTONE_CROSSING_INVARIANT")
                        if b-a <= Q(1, 2**bits):
                            leaves.append({"piece": idx, "lo": str(a), "hi": str(b),
                                           "kind": "ONE_SIMPLE_CROSSING", "precision": n,
                                           "left_sign": la, "right_sign": rb,
                                           "derivative_sign": ds})
                            return
            # No certificate at this cell width. Split only at a rational
            # pivot with a proven nonzero value, avoiding missed knot roots.
            pivot = None
            for t in ((a+b)/2, (2*a+b)/3, (a+2*b)/3):
                if point_sign(source, piece, t):
                    pivot = t
                    break
            need(pivot is not None, "PIVOT_SIGN_NONTRUTH")
            walk(a, pivot, depth+1)
            walk(pivot, b, depth+1)

        walk(piece.lo, piece.hi, 0)

    output = {"status": "COMPLETE_RESTRICTED_INTERVAL_CERTIFICATE",
              "evidence_class": "DETERMINISTIC_MODEL",
              "source_sha256": source.identity,
              "target_binary_bits": bits,
              "physical_root_count": sum(c["kind"] == "ONE_SIMPLE_CROSSING"
                                         for c in leaves),
              "signed_partition": leaves,
              "pb00701_established": False, "mc_b_established": False,
              "mc1_established": False, "production_authorized": False}
    verify_certificate(source, output)
    return output


def verify_certificate(source: Source, receipt: dict):
    """Independent per-cell replay and exhaustive source coverage check.

    This rechecks certificate leaves and their exact intervals; it does not
    infer any undocumented root from a numerical grid or a solver guess.
    """
    need(type(receipt) is dict and set(receipt) == {
        "status", "evidence_class", "source_sha256", "target_binary_bits",
        "physical_root_count", "signed_partition", "pb00701_established",
        "mc_b_established", "mc1_established", "production_authorized"},
         "RECEIPT_FIELDS")
    need(receipt["status"] == "COMPLETE_RESTRICTED_INTERVAL_CERTIFICATE" and
         receipt["evidence_class"] == "DETERMINISTIC_MODEL" and
         receipt["source_sha256"] == source.identity and
         all(receipt[x] is False for x in ("pb00701_established",
             "mc_b_established", "mc1_established", "production_authorized")),
         "RECEIPT_PROVENANCE_OR_PROMOTION")
    bits = receipt["target_binary_bits"]
    need(type(bits) is int and 1 <= bits <= MAX_BITS, "RECEIPT_BIT_BUDGET")
    rows = receipt["signed_partition"]
    need(type(rows) is list and 1 <= len(rows) <= MAX_NODES + 1,
         "RECEIPT_CELL_BUDGET")
    cursors = [p.lo for p in source.pieces]
    count = 0
    previous = None
    for row in rows:
        need(type(row) is dict and set(row) in (
            {"piece", "lo", "hi", "kind", "precision", "left_sign", "right_sign"},
            {"piece", "lo", "hi", "kind", "precision", "left_sign",
             "right_sign", "derivative_sign"}), "RECEIPT_CELL_FIELDS")
        i, n = row["piece"], row["precision"]
        need(type(i) is int and 0 <= i < len(source.pieces) and
             type(n) is int and n in PRECISIONS, "RECEIPT_CELL_INDEX")
        piece = source.pieces[i]
        a, b = fraction(row["lo"]), fraction(row["hi"])
        need(cursors[i] == a and a < b <= piece.hi, "RECEIPT_PARTITION_GAP")
        if previous is not None and previous["piece"] != i:
            need(i == previous["piece"]+1 and
                 previous["right_sign"] == row["left_sign"],
                 "RECEIPT_KNOT_SIGN_INCONSISTENT")
        la, rb = point_sign(source, piece, a), point_sign(source, piece, b)
        need(type(row["left_sign"]) is int and
             type(row["right_sign"]) is int and
             la == row["left_sign"] and rb == row["right_sign"] and
             la != 0 and rb != 0, "RECEIPT_ENDPOINT_SIGNS")
        f, d = bounds(source, piece, a, b, n)
        kind = row["kind"]
        if kind == "ROOT_FREE_INTERVAL":
            need(strict_sign(f) == la == rb and
                 "derivative_sign" not in row, "RECEIPT_ZERO_EXCLUSION")
        elif kind in ("ROOT_FREE_MONOTONE", "ONE_SIMPLE_CROSSING"):
            ds = strict_sign(d)
            need("derivative_sign" in row and type(row["derivative_sign"]) is int
                 and ds != 0 and ds == row["derivative_sign"],
                 "RECEIPT_DERIVATIVE_PROOF")
            if kind == "ONE_SIMPLE_CROSSING":
                need(b-a <= Q(1, 2**bits) and la == -ds and rb == ds,
                     "RECEIPT_ROOT_EXISTENCE_UNIQUENESS")
                count += 1
            else:
                need(la == rb, "RECEIPT_MONOTONE_EMPTY")
        else:
            raise Nontruth("UNKNOWN_CERTIFICATE_LEAF")
        cursors[i] = b
        previous = row
    need(all(c == p.hi for c, p in zip(cursors, source.pieces)),
         "RECEIPT_INCOMPLETE_COVERAGE")
    need(type(receipt["physical_root_count"]) is int and
         count == receipt["physical_root_count"], "RECEIPT_ROOT_COUNT_DRIFT")
    return True


SAMPLES = {
    "no_root": {"phase_offset_pi": "0", "phase_slope_pi": "2",
                "pieces": [{"lo": "0", "hi": "1", "H0": ["3"],
                            "C1": ["1"], "S1": ["0"], "C2": ["0"], "S2": ["0"]}]},
    "one_h1": {"phase_offset_pi": "0", "phase_slope_pi": "1",
               "pieces": [{"lo": "0", "hi": "1", "H0": ["-1/3"],
                           "C1": ["1"], "S1": ["0"], "C2": ["0"], "S2": ["0"]}]},
    "two_h2": {"phase_offset_pi": "0", "phase_slope_pi": "1",
               "pieces": [{"lo": "0", "hi": "1", "H0": ["1/2"],
                           "C1": ["0"], "S1": ["0"], "C2": ["1"], "S2": ["0"]}]},
    "poly_two": {"phase_offset_pi": "0", "phase_slope_pi": "0",
                 "pieces": [{"lo": "0", "hi": "1", "H0": ["2/9", "-1", "1"],
                             "C1": ["0"], "S1": ["0"], "C2": ["0"], "S2": ["0"]}]},
    "two_piece": {"phase_offset_pi": "1/8", "phase_slope_pi": "1/4",
                  "pieces": [
                      {"lo": "0", "hi": "1", "H0": ["-1/2", "1"],
                       "C1": ["0"], "S1": ["0"], "C2": ["0"], "S2": ["0"]},
                      {"lo": "1", "hi": "2", "H0": ["3/2", "-1"],
                       "C1": ["0"], "S1": ["0"], "C2": ["0"], "S2": ["0"]}]},
    "both_harmonics": {"phase_offset_pi": "0", "phase_slope_pi": "1",
                  "pieces": [{"lo": "0", "hi": "1", "H0": ["-1/2", "1"],
                              "C1": ["1/10"], "S1": ["0"],
                              "C2": ["0"], "S2": ["1/20"]}]},
    "v44_shape": {"phase_offset_pi": "-1/4", "phase_slope_pi": "1/8",
                  "pieces": [{"lo": "0", "hi": "1", "H0": ["0"],
                              "C1": ["-3/2", "1", "2"],
                              "S1": ["-1/2", "-1", "2"],
                              "C2": ["1/100000000"], "S2": ["0"]}]},
}


# Authentication is deliberately independent of any source-specific
# uniqueness theorem. No frozen source file is ever modified.
HERE = Path(__file__).resolve().parent
V44_ID = "harvested:verify_pb00701_v44:ffaea08e30c9"
V44_SPEC_SHA256 = "d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2"
V44_ROW_SHA256 = "7423adadf8c52ff28d47d9f63effbc5a2a7a630bdaf7efe6f8eeb1d2a85c5600"
FROZEN_V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
FROZEN_V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"


def frozen_json(name, blob_sha1, byte_limit):
    path = HERE / name
    try:
        with path.open("rb") as stream:
            raw = stream.read(byte_limit + 1)
    except OSError as exc:
        raise Nontruth("FROZEN_FILE_UNAVAILABLE") from exc
    need(len(raw) <= byte_limit, "FROZEN_BYTE_BUDGET")
    digest = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(digest == blob_sha1, "FROZEN_BLOB_IDENTITY_DRIFT")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Nontruth("FROZEN_JSON_INVALID") from exc


def frozen_quadratic(poly):
    """Exact clamped quadratic Bernstein/B-spline -> global t polynomial."""
    need(type(poly) is dict and poly.get("degree") == 2 and
         poly.get("knots") == ["0", "0", "0", "1", "1", "1"] and
         type(poly.get("controls")) is list and
         len(poly["controls"]) == 3, "ORIGINAL_QUADRATIC_SPLINE_GRAMMAR")
    c0, c1, c2 = map(fraction, poly["controls"])
    return [str(c0), str(2*(c1-c0)), str(c0-2*c1+c2)]


def verify_authenticated_v44():
    """Rebuild the model's exact physical coefficients from frozen original."""
    corpus = frozen_json("pb00701-finite-owner-corpus-v54.json",
                         FROZEN_V54_BLOB, 240000)
    v2 = frozen_json("pb00701-post-v54-evidence-reconciliation-v2.json",
                     FROZEN_V2_BLOB, 190000)
    matches = [r for r in corpus["cases"] if r.get("id") == V44_ID]
    need(len(matches) == 1, "ORIGINAL_V44_ID_UNIQUE")
    row = matches[0]
    spec = row["spec"]
    need(hashlib.sha256(canonical(spec)).hexdigest() == V44_SPEC_SHA256 and
         hashlib.sha256(canonical(row)).hexdigest() == V44_ROW_SHA256,
         "ORIGINAL_V44_SOURCE_HASH")
    need(spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
         and spec.get("source_parameter_id") == "pb00701-v44-algebraic-orientation"
         and (spec.get("parameter_lo"), spec.get("parameter_hi")) == ("0", "1")
         and set(spec.get("cos_splines", {})) == {"1", "2"}
         and set(spec.get("sin_splines", {})) == {"1"},
         "ORIGINAL_V44_SOURCE_GRAMMAR")
    h2 = spec["cos_splines"]["2"]
    need(h2 == {"degree": 0, "knots": ["0", "1"],
                "controls": ["1/100000000"]}, "ORIGINAL_V44_NONZERO_H2")
    doc = {
        "phase_offset_pi": str(2*fraction(spec["phase_turn_offset"])),
        "phase_slope_pi": str(2*fraction(spec["phase_turn_rate"])),
        "pieces": [{
            "lo": spec["parameter_lo"], "hi": spec["parameter_hi"],
            "H0": ["0"], "C1": frozen_quadratic(spec["cos_splines"]["1"]),
            "S1": frozen_quadratic(spec["sin_splines"]["1"]),
            "C2": [h2["controls"][0]], "S2": ["0"]
        }]
    }
    need(doc == SAMPLES["v44_shape"], "SOURCE_CONVERSION_NOT_EXACT")
    witnesses = [r for r in v2["source_cases"] if r.get("case_id") == V44_ID]
    need(len(witnesses) == 1 and
         witnesses[0].get("source_sha256") == V44_SPEC_SHA256 and
         witnesses[0].get("original_row_sha256") == V44_ROW_SHA256 and
         witnesses[0].get("registered_evidence_level") ==
         "COMPLETE_SOURCE_SPECIFIC" and
         row["expected"]["v54_disposition"] == "BLOCKED",
         "EXISTING_ORIGINAL_EVIDENCE_CUSTODY")
    source = parse_source(doc)
    receipt = classify(source, bits=12)
    need(receipt["physical_root_count"] == 1,
         "AUTHENTIC_V44_EVENT_COUNT")
    root = next(r for r in receipt["signed_partition"]
                if r["kind"] == "ONE_SIMPLE_CROSSING")
    # The previously published exact V44 40-bit bracket is a separate
    # existing result: use it only to challenge this complete partition.
    previous_lo = Q(317223013097, 549755813888)
    previous_hi = Q(634446026195, 1099511627776)
    need(fraction(root["lo"]) < previous_lo < previous_hi <
         fraction(root["hi"]), "V44_PRIOR_BRACKET_DISAGREEMENT")
    return {
        "case_id": V44_ID, "source_sha256": V44_SPEC_SHA256,
        "source_row_sha256": V44_ROW_SHA256,
        "existing_v2_complete": True, "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "certificate": receipt
    }



class Tests(unittest.TestCase):
    def test_exact_machin_and_trig_enclosures(self):
        for n in (6, 10, 16):
            a, b = pi_interval(n)
            self.assertTrue(3 < a < b < Q(22, 7))
        # Exact specials checked independently of Taylor output construction.
        for k, expected_s, expected_c in ((Q(0), Q(0), Q(1)),
                                          (Q(1,2), Q(1), Q(0)),
                                          (Q(1), Q(0), Q(-1))):
            sine, cosine = trig_point(k, 10)
            self.assertTrue(sine[0] <= expected_s <= sine[1])
            self.assertTrue(cosine[0] <= expected_c <= cosine[1])

    def test_all_sample_source_partitions(self):
        for name, expected in (("no_root", 0), ("one_h1", 1),
                               ("two_h2", 2), ("poly_two", 2),
                               ("two_piece", 2), ("both_harmonics", 1), ("v44_shape", 1)):
            with self.subTest(name=name):
                src = parse_source(SAMPLES[name])
                cert = classify(src, bits=9)
                self.assertEqual(cert["physical_root_count"], expected)
                self.assertTrue(verify_certificate(src, cert))
                if name == "v44_shape":
                    roots = [c for c in cert["signed_partition"]
                             if c["kind"] == "ONE_SIMPLE_CROSSING"]
                    self.assertEqual(len(roots), 1)
                    self.assertLess(fraction(roots[0]["lo"]), Q(58,100))
                    self.assertGreater(fraction(roots[0]["hi"]), Q(57,100))

    def test_certificate_mutation_refusal(self):
        import copy
        src = parse_source(SAMPLES["two_h2"])
        certificate = classify(src, bits=8)
        mutants = []
        obj = copy.deepcopy(certificate)
        obj["physical_root_count"] += 1
        mutants.append(obj)
        obj = copy.deepcopy(certificate)
        obj["signed_partition"][0]["right_sign"] *= -1
        mutants.append(obj)
        obj = copy.deepcopy(certificate)
        obj["signed_partition"].pop()
        mutants.append(obj)
        obj = copy.deepcopy(certificate)
        obj["mc1_established"] = True
        mutants.append(obj)
        for obj in mutants:
            with self.assertRaises(Nontruth):
                verify_certificate(src, obj)

    def test_exact_factored_polynomial_challenges(self):
        # Thirty exact algebraic truth controls with varied rational root
        # positions, plus metamorphic positive amplitude multiplication.
        from random import Random
        rng = Random(20261108)
        for iteration in range(30):
            a = Q(rng.randint(2, 13), 36)
            b = Q(rng.randint(22, 34), 36)
            coeff = (a*b, -(a+b), Q(1))
            for factor in (Q(1), Q(7, 3)):
                row = {"phase_offset_pi": "0", "phase_slope_pi": "0",
                       "pieces": [{"lo": "0", "hi": "1",
                                   "H0": [str(factor*x) for x in coeff],
                                   "C1": ["0"], "S1": ["0"],
                                   "C2": ["0"], "S2": ["0"]}]}
                result = classify(parse_source(row), bits=7)
                self.assertEqual(result["physical_root_count"], 2,
                                 msg=f"case {iteration} {factor}")
                roots = [leaf for leaf in result["signed_partition"]
                         if leaf["kind"] == "ONE_SIMPLE_CROSSING"]
                self.assertEqual(len(roots), 2)
                self.assertTrue(fraction(roots[0]["lo"]) < a <
                                fraction(roots[0]["hi"]))
                self.assertTrue(fraction(roots[1]["lo"]) < b <
                                fraction(roots[1]["hi"]))

    def test_large_period_phase_reduction(self):
        import copy
        original = parse_source(SAMPLES["one_h1"])
        shifted = copy.deepcopy(SAMPLES["one_h1"])
        shifted["phase_offset_pi"] = "120"
        a, b = classify(original, bits=7), classify(parse_source(shifted), bits=7)
        self.assertEqual(a["physical_root_count"], b["physical_root_count"])
        self.assertEqual([(r["lo"], r["hi"], r["kind"])
                          for r in a["signed_partition"]],
                         [(r["lo"], r["hi"], r["kind"])
                          for r in b["signed_partition"]])

    def test_tangency_and_endpoint_refusal(self):
        import copy
        tangent = copy.deepcopy(SAMPLES["poly_two"])
        tangent["pieces"][0]["H0"] = ["1/9", "-2/3", "1"]
        with self.assertRaises(Nontruth):
            classify(parse_source(tangent), bits=6, max_depth=12)
        endpoint = copy.deepcopy(SAMPLES["poly_two"])
        endpoint["pieces"][0]["H0"] = ["0", "1"]
        with self.assertRaisesRegex(Nontruth, "KNOT_OR_EXTERIOR_SIGN_NONTRUTH"):
            classify(parse_source(endpoint), bits=6)

    def test_malformed_source_and_discontinuous_knot_refuse(self):
        import copy
        for text in ("01", "0/1", "1e3", "1/0", "1/"+"0"*200):
            with self.assertRaises(Nontruth):
                fraction(text)
        mutant = copy.deepcopy(SAMPLES["two_piece"])
        mutant["pieces"][1]["H0"] = ["3", "-1"]
        with self.assertRaisesRegex(Nontruth, "KNOT_COEFFICIENT_DISCONTINUITY"):
            parse_source(mutant)
        mutant = copy.deepcopy(SAMPLES["v44_shape"])
        mutant["pieces"][0]["C2"] = ["1/2", "1", "1", "1", "1"]
        with self.assertRaisesRegex(Nontruth, "POLYNOMIAL_GRAMMAR"):
            parse_source(mutant)

    def test_original_v44_frozen_blob_custody_and_generic_certificate(self):
        # The historical corpus is guaranteed in repository CI, but is not
        # copied into a standalone local model-only sandbox.
        if not (HERE / "pb00701-finite-owner-corpus-v54.json").exists():
            self.skipTest("frozen original corpus not present outside repository")
        result = verify_authenticated_v44()
        self.assertEqual(result["case_id"], V44_ID)
        self.assertEqual(result["certificate"]["physical_root_count"], 1)
        self.assertEqual(result["new_historical_closures"], [])
        self.assertEqual(result["required_pb_po_discharges"], 0)

    def test_nonpromotion_and_source_identity(self):
        src = parse_source(SAMPLES["v44_shape"])
        receipt = classify(src, bits=8)
        self.assertEqual(receipt["evidence_class"], "DETERMINISTIC_MODEL")
        self.assertTrue(all(receipt[k] is False for k in
                            ("pb00701_established", "mc_b_established",
                             "mc1_established", "production_authorized")))
        mutant = dict(receipt, source_sha256="0"*64)
        with self.assertRaises(Nontruth):
            verify_certificate(src, mutant)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.contract:
        # The producing contract must also authenticate the original frozen
        # source before it may describe its V44-shaped test as source-matched.
        authenticated = verify_authenticated_v44()
        print(json.dumps({"case": "authenticated_frozen_v44",
                          "original_case_id": authenticated["case_id"],
                          "source_sha256": authenticated["source_sha256"],
                          "roots": authenticated["certificate"]["physical_root_count"],
                          "new_historical_closures": []}, sort_keys=True))
        for name in SAMPLES:
            src = parse_source(SAMPLES[name])
            cert = classify(src, bits=9)
            print(json.dumps({"case": name, "status": cert["status"],
                              "roots": cert["physical_root_count"],
                              "cells": len(cert["signed_partition"]),
                              "sha256": cert["source_sha256"]}, sort_keys=True))
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        p.error("pass --contract and/or --self-test")


if __name__ == "__main__":
    main()
