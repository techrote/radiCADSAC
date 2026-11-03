#!/usr/bin/env python3
"""Generic bounded original-source proof for coprime squared amplitudes.

Every admitted source is reconstructed from its supplied clamped B-splines.
Polynomial Bezout and an exhaustive rational phase lattice establish all roots;
strictly positive quadratic jets establish order two without transcendence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import comb, gcd
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK_DIR = "research/machining-completeness/tasks/MC-038/"
REPORT = HERE / "pb00701-coprime-square-source.json"
SCHEMA = "radicadsac-mc038-coprime-square-source/1.0"
BASE_MAIN = "8190ae2c474fcb6fa9a54851abc03f481a5685d3"
MAX_BYTES = 2 * 1024 * 1024
MAX_REFERENCE_BYTES = 256 * 1024
MAX_CODE_BYTES = 256 * 1024
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 4096
MAX_INPUT_BITS = 128
MAX_INTERMEDIATE_BITS = 4096
MAX_DERIVED_TOKEN = 2500
MAX_HINT_DEGREE = 3
MAX_SOURCE_DEGREE = 6
MAX_POLY_DEGREE = 12
MAX_CANDIDATES = 65
_FractionType = Fraction
REFERENCE_PINS = {'docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md': '6005fc55e2d18e71639e6bc31cfbc1597bf4a915',
 'research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary.json': '4840bbca3847962b537684e0dffa871bd6de82a2',
 'research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
 'research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py': '4f9000549834c8f9b60ebc9925fadb71e9f96acf'}
REFERENCE_RECORDS = [{'bytes': 2255,
  'git_blob': '6005fc55e2d18e71639e6bc31cfbc1597bf4a915',
  'path': 'docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md',
  'sha256': '7cc6704ee4636e498d4f8575dfaea35462f33effc20fbef6d45d994b416f4515',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 18930,
  'git_blob': '4840bbca3847962b537684e0dffa871bd6de82a2',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary.json',
  'sha256': 'c645a88dc54232de9cf64c542b83c5d38caf835401f4eaec3cedc9744f7a3ff3',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 18701,
  'git_blob': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py',
  'sha256': '2813a99ecc2bc179bf31f6c9166f9c3564516e67f2f256c0a984deee4ed0f692',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 32020,
  'git_blob': '4f9000549834c8f9b60ebc9925fadb71e9f96acf',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py',
  'sha256': '29fb8a0b8ddbece891b31504aa1e661d2471a3a9fea22f1f630d9564da91886d',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'}]
MTP_SOURCE_SPEC = {'cos_splines': {'0': {'controls': ['5/8', '3/8', '5/8'],
                       'degree': 2,
                       'knots': ['1/2', '1/2', '1/2', '3/2', '3/2', '3/2']},
                 '1': {'controls': ['-3/8', '-5/8', '-3/8'],
                       'degree': 2,
                       'knots': ['1/2', '1/2', '1/2', '3/2', '3/2', '3/2']}},
 'grammar': 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
 'parameter_hi': '3/2',
 'parameter_lo': '1/2',
 'phase_turn_offset': '0',
 'phase_turn_rate': '1',
 'sin_splines': {},
 'source_parameter_id': 'pb00701-mtp-irreducible-boundary-original-t'}


class Refusal(ValueError):
    def __init__(self, reason, code="UNESTABLISHED"):
        super().__init__(reason)
        self.reason = str(reason)[:512]
        self.code = code

    def as_record(self):
        return {"status": "REFUSED", "code": self.code, "reason": self.reason,
                "proof_established": False, "source_zero_set_established": False,
                "source_zero_set": None, "production_authorized": False}


def need(condition, reason, code="UNESTABLISHED"):
    if not condition:
        raise Refusal(reason, code)


def bounded_bytes(value):
    """Iterative exact JSON preflight before recursive serialization."""
    stack = [(value, 0)]
    seen = set()
    nodes = estimate = 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        need(nodes <= MAX_NODES and depth <= MAX_DEPTH,
             "JSON node/depth budget", "RESOURCE_REFUSAL")
        if type(item) in (dict, list):
            need(id(item) not in seen, "Cyclic or aliased JSON container", "RESOURCE_REFUSAL")
            seen.add(id(item))
            need(len(item) <= 1024, "JSON container budget", "RESOURCE_REFUSAL")
            estimate += 2 + len(item)*2
            if type(item) is dict:
                for key, child in item.items():
                    need(type(key) is str and len(key) <= 256, "Exact bounded JSON key", "RESOURCE_REFUSAL")
                    estimate += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth+1))
            else:
                stack.extend((child, depth+1) for child in item)
        elif type(item) is str:
            need(len(item) <= MAX_STRING, "JSON string budget", "RESOURCE_REFUSAL")
            estimate += len(json.dumps(item, ensure_ascii=True))
        elif type(item) is int:
            need(item.bit_length() <= 256, "JSON integer budget", "RESOURCE_REFUSAL")
            estimate += 80
        else:
            need(item is None or type(item) is bool, "Exact JSON scalar required", "RESOURCE_REFUSAL")
            estimate += 5
        need(estimate <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(raw) <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    return raw


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def clone(value):
    return json.loads(bounded_bytes(value))


def _pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "Duplicate JSON key", "RESOURCE_REFUSAL")
        result[key] = value
    return result


def _json_integer(token):
    need(len(token) <= 80, "JSON integer token budget", "RESOURCE_REFUSAL")
    result = int(token)
    need(result.bit_length() <= 256, "JSON integer operand budget", "RESOURCE_REFUSAL")
    return result


def _nonexact_json(token):
    raise Refusal("Nonexact JSON number: " + token[:40], "RESOURCE_REFUSAL")


def parse_json_bytes(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=_json_integer, parse_float=_nonexact_json, parse_constant=_nonexact_json)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError, OverflowError) as error:
        raise Refusal("Malformed or exhausted JSON input", "RESOURCE_REFUSAL") from error
    bounded_bytes(value)
    return value


def _read_bounded(path, limit):
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit+1)
    except (OSError, ValueError) as error:
        raise Refusal("Bounded file read failed: " + type(error).__name__) from error
    need(len(raw) <= limit, "File byte budget", "RESOURCE_REFUSAL")
    return raw


def git_blob_bytes(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _invoke(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Requested proof computation exhausted resources", "RESOURCE_REFUSAL") from error
    except Exception as error:
        code = getattr(error, "code", "UNESTABLISHED")
        need(type(code) is str and len(code) <= 80, "Malformed upstream refusal code")
        raise Refusal("Requested proof computation failed: " + type(error).__name__ + ": " +
                      str(error)[:200], code) from error


ZERO, ONE, TWO = Fraction(0), Fraction(1), Fraction(2)


def rational_parts(token, max_bits=MAX_INPUT_BITS, max_chars=128):
    need(type(max_bits) is int and 1 <= max_bits <= MAX_INTERMEDIATE_BITS and
         type(max_chars) is int and 1 <= max_chars <= MAX_DERIVED_TOKEN,
         "Rational parser controls exceed the finite derived ceilings", "RESOURCE_REFUSAL")
    need(type(token) is str and 0 < len(token) <= max_chars,
         "Bounded exact rational token required", "RESOURCE_REFUSAL")
    need(re.fullmatch(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?", token, flags=re.ASCII) is not None,
         "Canonical ASCII integer/ratio required", "RESOURCE_REFUSAL")
    parts = token.split("/")
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    need(max(numerator.bit_length(), denominator.bit_length()) <= max_bits,
         "Rational operand bit budget", "RESOURCE_REFUSAL")
    need(gcd(abs(numerator), denominator) == 1 and (len(parts) == 1 or denominator > 1),
         "Reduced canonical rational required", "RESOURCE_REFUSAL")
    return numerator, denominator


def rational(token, max_bits=MAX_INPUT_BITS, max_chars=128):
    return Fraction(*rational_parts(token, max_bits, max_chars))


def _derived(token):
    return rational(token, MAX_INTERMEDIATE_BITS, MAX_DERIVED_TOKEN)


def _coefficient(value):
    need(type(value) is _FractionType and
         max(value.numerator.bit_length(), value.denominator.bit_length()) <= MAX_INTERMEDIATE_BITS,
         "Exact bounded internal rational required", "RESOURCE_REFUSAL")
    return value


def _number(value):
    if type(value) is int:
        need(value.bit_length() <= MAX_INTERMEDIATE_BITS, "Internal integer budget", "RESOURCE_REFUSAL")
        value = Fraction(value)
    return _coefficient(value)


def _safe(a, b, operation):
    a, b = _coefficient(a), _coefficient(b)
    need(operation in ("add", "sub", "mul", "div"), "Unknown bounded arithmetic operation")
    need(operation != "div" or b != ZERO, "Exact division by zero")
    if operation in ("add", "sub") and b == ZERO:
        return a
    if operation == "mul" and (a == ZERO or b == ZERO):
        return ZERO
    if operation == "div" and a == ZERO:
        return ZERO
    an, ad = a.numerator.bit_length(), a.denominator.bit_length()
    bn, bd = b.numerator.bit_length(), b.denominator.bit_length()
    if operation in ("add", "sub"):
        nbits, dbits = max(an+bd, bn+ad)+1, ad+bd
    elif operation == "mul":
        nbits, dbits = an+bn, ad+bd
    else:
        nbits, dbits = an+bd, ad+bn
    need(max(nbits, dbits) <= MAX_INTERMEDIATE_BITS,
         "Polynomial/phase arithmetic growth budget", "RESOURCE_REFUSAL")
    return _coefficient(a+b if operation == "add" else a-b if operation == "sub" else
                        a*b if operation == "mul" else a/b)


def _trim(poly):
    need(type(poly) in (tuple, list) and 1 <= len(poly) <= MAX_POLY_DEGREE+1,
         "Internal polynomial length budget", "RESOURCE_REFUSAL")
    values = [_coefficient(value) for value in poly]
    while len(values) > 1 and values[-1] == ZERO:
        values.pop()
    return tuple(values)


def _degree(poly):
    poly = _trim(poly)
    return -1 if poly == (ZERO,) else len(poly)-1


def encode_poly(poly):
    return [str(value) for value in _trim(poly)]


def decode_poly(tokens, *, max_degree=MAX_POLY_DEGREE, derived=True):
    need(type(max_degree) is int and 0 <= max_degree <= MAX_POLY_DEGREE and type(derived) is bool,
         "Polynomial parser controls exceed the finite ceilings", "RESOURCE_REFUSAL")
    need(type(tokens) is list and 1 <= len(tokens) <= max_degree+1,
         "Polynomial coefficient-list budget", "RESOURCE_REFUSAL")
    parts = [rational_parts(token, MAX_INTERMEDIATE_BITS if derived else MAX_INPUT_BITS,
                            MAX_DERIVED_TOKEN if derived else 128) for token in tokens]
    return _trim(tuple(Fraction(n, d) for n, d in parts))


def poly_add(left, right):
    left, right = _trim(left), _trim(right)
    return _trim(tuple(_safe(left[i] if i < len(left) else ZERO,
                            right[i] if i < len(right) else ZERO, "add")
                       for i in range(max(len(left), len(right)))))


def poly_scale(poly, scalar):
    return _trim(tuple(_safe(value, _coefficient(scalar), "mul") for value in _trim(poly)))


def poly_sub(left, right):
    return poly_add(left, poly_scale(right, -ONE))


def poly_mul(left, right):
    left, right = _trim(left), _trim(right)
    need(len(left)+len(right)-2 <= MAX_POLY_DEGREE,
         "Polynomial product degree budget", "RESOURCE_REFUSAL")
    values = [ZERO]*(len(left)+len(right)-1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            values[i+j] = _safe(values[i+j], _safe(a, b, "mul"), "add")
    return _trim(values)


def poly_pow(poly, exponent):
    poly = _trim(poly)
    need(type(exponent) is int and 0 <= exponent <= MAX_SOURCE_DEGREE and
         max(0, _degree(poly))*exponent <= MAX_POLY_DEGREE,
         "Polynomial exponent budget", "RESOURCE_REFUSAL")
    result = (ONE,)
    for _ in range(exponent):
        result = poly_mul(result, poly)
    return result


def poly_derivative(poly):
    poly = _trim(poly)
    return _trim(tuple(_safe(_number(i), poly[i], "mul") for i in range(1, len(poly))) or (ZERO,))


def poly_eval(poly, coordinate):
    coordinate = _coefficient(coordinate)
    result = ZERO
    for coefficient in reversed(_trim(poly)):
        result = _safe(_safe(result, coordinate, "mul"), coefficient, "add")
    return result


def poly_divmod(numerator, denominator):
    numerator, denominator = _trim(numerator), _trim(denominator)
    need(denominator != (ZERO,), "Polynomial division by zero")
    if _degree(numerator) < _degree(denominator):
        return (ZERO,), numerator
    quotient = [ZERO]*(len(numerator)-len(denominator)+1)
    remainder = numerator
    steps = 0
    while remainder != (ZERO,) and _degree(remainder) >= _degree(denominator):
        steps += 1
        need(steps <= MAX_POLY_DEGREE+1, "Polynomial division did not terminate within degree bound")
        old_degree = _degree(remainder)
        power = len(remainder)-len(denominator)
        factor = _safe(remainder[-1], denominator[-1], "div")
        quotient[power] = _safe(quotient[power], factor, "add")
        term = tuple([ZERO]*power + list(poly_scale(denominator, factor)))
        remainder = poly_sub(remainder, term)
        need(_degree(remainder) < old_degree, "Exact division failed leading-term cancellation")
    return _trim(quotient), remainder


def _source_preflight(spec):
    bounded_bytes(spec)
    need(type(spec) is dict and set(spec) == {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
         "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"}, "Exact source fields required")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and 0 < len(spec["source_parameter_id"]) <= 128 and
         "\0" not in spec["source_parameter_id"], "Source grammar or bounded original parameter ID invalid")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"0", "1"} and
         type(spec["sin_splines"]) is dict and not spec["sin_splines"],
         "This source theorem requires both explicit cosine channels0/1 and no sine channels")
    tokens = [spec[key] for key in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    for harmonic in ("0", "1"):
        spline = spec["cos_splines"][harmonic]
        need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"}, "Exact spline fields required")
        degree = spline["degree"]
        need(type(degree) is int and 0 <= degree <= MAX_SOURCE_DEGREE,
             "Exact source degree in0..6 required", "RESOURCE_REFUSAL")
        need(type(spline["controls"]) is list and len(spline["controls"]) == degree+1 and
             type(spline["knots"]) is list and len(spline["knots"]) == 2*(degree+1),
             "One full-clamped source span is required")
        tokens.extend(spline["knots"])
        tokens.extend(spline["controls"])
    parts = [rational_parts(token) for token in tokens]
    lo, hi, offset, rate = parts[:4]
    need(lo[0]*hi[1] < hi[0]*lo[1], "Source interval must have positive length")
    need(abs(lo[0]) <= 2*lo[1] and abs(hi[0]) <= 2*hi[1] and
         abs(offset[0]) <= 8*offset[1] and abs(rate[0]) <= 8*rate[1],
         "Original coordinate/phase parameter range budget", "RESOURCE_REFUSAL")
    need(rate[0] != 0, "Stationary phase is outside the moving-phase theorem", "UNSUPPORTED_STATIONARY_PHASE")
    for spline in spec["cos_splines"].values():
        count = spline["degree"]+1
        need(spline["knots"] == [spec["parameter_lo"]]*count + [spec["parameter_hi"]]*count,
             "Original coefficient is not fully clamped on the whole supplied source interval")
    return parts


def _hint_preflight(tokens):
    need(type(tokens) is list and 1 <= len(tokens) <= MAX_HINT_DEGREE+1,
         "P/Q hint degree budget", "RESOURCE_REFUSAL")
    return [rational_parts(token) for token in tokens]


def _input_preflight(spec, p_coefficients, q_coefficients):
    # All source/hint tokens are checked before the first numeric constructor.
    _source_preflight(spec)
    _hint_preflight(p_coefficients)
    _hint_preflight(q_coefficients)
    bounded_bytes(p_coefficients)
    bounded_bytes(q_coefficients)


def lower_source(spec):
    """Actual whole-source Bernstein lowering in the original global parameter."""
    _source_preflight(spec)
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    width = _safe(hi, lo, "sub")
    reciprocal = _safe(ONE, width, "div")
    u = poly_scale((-lo, ONE), reciprocal)
    v = poly_scale((hi, -ONE), reciprocal)
    result = {"source_sha256": digest(spec), "source_parameter_id": spec["source_parameter_id"],
              "original_source_interval": [str(lo), str(hi)],
              "global_phase_turn_law": {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]},
              "channels": []}
    for harmonic in ("0", "1"):
        spline = spec["cos_splines"][harmonic]
        degree = spline["degree"]
        controls = tuple(map(rational, spline["controls"]))
        basis = [poly_scale(poly_mul(poly_pow(u, i), poly_pow(v, degree-i)), _number(comb(degree, i)))
                 for i in range(degree+1)]
        unity = (ZERO,)
        polynomial = (ZERO,)
        for control, term in zip(controls, basis):
            unity = poly_add(unity, term)
            polynomial = poly_add(polynomial, poly_scale(term, control))
        need(unity == (ONE,), "Original Bernstein basis failed exact partition of unity")
        result["C"+harmonic] = encode_poly(polynomial)
        result["channels"].append({"harmonic": int(harmonic), "degree": degree,
            "original_knots": clone(spline["knots"]), "original_controls": clone(spline["controls"]),
            "bernstein_basis_in_original_parameter": [encode_poly(term) for term in basis],
            "global_power_coefficients": encode_poly(polynomial), "partition_of_unity_verified": True,
            "left_endpoint_value": str(poly_eval(polynomial, lo)),
            "right_endpoint_value": str(poly_eval(polynomial, hi))})
        need(poly_eval(polynomial, lo) == controls[0] and poly_eval(polynomial, hi) == controls[-1],
             "Original clamped endpoint states do not agree with the reconstructed polynomial")
    return result


def compute_bezout(p, q):
    """Actual bounded extended Euclid; the caller also verifies the final identity."""
    p, q = _trim(p), _trim(q)
    need(max(_degree(p), _degree(q)) <= MAX_HINT_DEGREE, "Bezout hint degree budget", "RESOURCE_REFUSAL")
    old_r, r = p, q
    old_s, s = (ONE,), (ZERO,)
    old_t, t = (ZERO,), (ONE,)
    trace = []
    while r != (ZERO,):
        need(len(trace) <= MAX_HINT_DEGREE+1, "Euclidean degree-descent budget")
        quotient, remainder = poly_divmod(old_r, r)
        need(remainder == (ZERO,) or _degree(remainder) < _degree(r), "Euclidean remainder did not descend")
        trace.append({"dividend": encode_poly(old_r), "divisor": encode_poly(r),
                      "quotient": encode_poly(quotient), "remainder": encode_poly(remainder)})
        old_r, r = r, remainder
        old_s, s = s, poly_sub(old_s, poly_mul(quotient, s))
        old_t, t = t, poly_sub(old_t, poly_mul(quotient, t))
    need(_degree(old_r) == 0 and old_r[0] != ZERO,
         "P/Q have a nonconstant common divisor or are both zero", "COPRIMALITY_NOT_ESTABLISHED")
    inverse = _safe(ONE, old_r[0], "div")
    a, b = poly_scale(old_s, inverse), poly_scale(old_t, inverse)
    identity = poly_add(poly_mul(a, p), poly_mul(b, q))
    need(identity == (ONE,), "Executed Euclid result failed its coefficientwise Bezout identity")
    return {"A": encode_poly(a), "B": encode_poly(b), "normalized_gcd": ["1"],
            "identity_coefficients": encode_poly(identity), "identity_verified_coefficientwise": True,
            "euclidean_trace": trace, "common_complex_zero_excluded_by_identity": True}


def _verify_bezout(p, q, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"A", "B", "normalized_gcd", "identity_coefficients",
         "identity_verified_coefficientwise", "euclidean_trace", "common_complex_zero_excluded_by_identity"},
         "Bezout proof fields changed")
    a, b = decode_poly(proof["A"]), decode_poly(proof["B"])
    need(poly_add(poly_mul(a, p), poly_mul(b, q)) == (ONE,) and
         proof["normalized_gcd"] == proof["identity_coefficients"] == ["1"] and
         proof["identity_verified_coefficientwise"] is True and
         proof["common_complex_zero_excluded_by_identity"] is True,
         "Actual Bezout coefficients do not establish coprimality")
    trace = proof["euclidean_trace"]
    need(type(trace) is list and len(trace) <= MAX_HINT_DEGREE+2, "Bezout trace budget", "RESOURCE_REFUSAL")
    dividend, divisor = p, q
    for item in trace:
        need(type(item) is dict and set(item) == {"dividend", "divisor", "quotient", "remainder"},
             "Euclidean trace fields changed")
        need(decode_poly(item["dividend"]) == dividend and decode_poly(item["divisor"]) == divisor and
             divisor != (ZERO,), "Euclidean trace lost its actual consecutive inputs")
        quotient, remainder = decode_poly(item["quotient"]), decode_poly(item["remainder"])
        need(poly_add(poly_mul(quotient, divisor), remainder) == dividend and
             (remainder == (ZERO,) or _degree(remainder) < _degree(divisor)),
             "Euclidean trace has an inaccurate quotient/remainder or nondecreasing degree")
        dividend, divisor = divisor, remainder
    need(divisor == (ZERO,) and _degree(dividend) == 0, "Euclidean trace does not reach a nonzero constant gcd")
    return True


def _phase_range(lo, hi, offset, rate):
    lo, hi, offset, rate = map(_coefficient, (lo, hi, offset, rate))
    need(-TWO <= lo < hi <= TWO and abs(offset) <= _number(8) and
         ZERO < abs(rate) <= _number(8), "Moving source coordinate/phase bounds not established")
    left = _safe(offset, _safe(rate, lo, "mul"), "add")
    right = _safe(offset, _safe(rate, hi, "mul"), "add")
    low, high = sorted((left, right))
    need(-_number(16) <= low <= high <= _number(16), "Closed phase range budget", "RESOURCE_REFUSAL")
    twice_low, twice_high = _safe(TWO, low, "mul"), _safe(TWO, high, "mul")
    first = -((-twice_low.numerator)//twice_low.denominator)
    last = twice_high.numerator//twice_high.denominator
    count = max(0, last-first+1)
    need(count <= MAX_CANDIDATES, "Half-integer candidate-count budget before enumeration", "RESOURCE_REFUSAL")
    return {"original_left_phase": str(left), "original_right_phase": str(right),
            "closed_phase_range": [str(low), str(high)], "first_phase_index": first,
            "last_phase_index": last, "candidate_count": count,
            "negative_rate_reverses_phase_order": rate < ZERO}


def enumerate_phase_candidates(lo, hi, offset, rate, p, q):
    """Exhaustive theorem candidates, never a numerical sampling argument."""
    p, q = _trim(p), _trim(q)
    bounds = _phase_range(lo, hi, offset, rate)
    candidates = []
    for index in range(bounds["first_phase_index"], bounds["last_phase_index"]+1):
        phase = Fraction(index, 2)
        coordinate = _safe(_safe(phase, offset, "sub"), rate, "div")
        need(lo <= coordinate <= hi, "Phase candidate failed original closed-source membership")
        pv, qv = poly_eval(p, coordinate), poly_eval(q, coordinate)
        branch = "INTEGER_PHASE_P_ZERO" if index % 2 == 0 else "ODD_HALF_PHASE_Q_ZERO"
        candidates.append({"phase_index": index, "phase_turn": str(phase), "coordinate": str(coordinate),
                           "P_value": str(pv), "Q_value": str(qv), "branch": branch,
                           "is_physical_zero": (pv == ZERO if index % 2 == 0 else qv == ZERO)})
    candidates.sort(key=lambda item: _derived(item["coordinate"]))
    return {"phase_range": bounds, "candidates": candidates}


def _verify_candidates(lo, hi, offset, rate, p, q, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"phase_range", "candidates"}, "Candidate proof fields changed")
    bounds = _phase_range(lo, hi, offset, rate)
    need(bounded_bytes(proof["phase_range"]) == bounded_bytes(bounds), "Exact phase range or finite candidate bound changed")
    rows = proof["candidates"]
    need(type(rows) is list and len(rows) == bounds["candidate_count"], "An exhaustive phase candidate was lost or duplicated")
    indices = list(range(bounds["first_phase_index"], bounds["last_phase_index"]+1))
    if rate < ZERO:
        indices.reverse()
    previous = None
    for item, index in zip(rows, indices):
        need(type(item) is dict and set(item) == {"phase_index", "phase_turn", "coordinate", "P_value",
             "Q_value", "branch", "is_physical_zero"} and type(item["phase_index"]) is int and
             item["phase_index"] == index, "Phase candidate is missing, repeated or in the wrong original order")
        coordinate, phase = _derived(item["coordinate"]), _derived(item["phase_turn"])
        need(phase == Fraction(index, 2) and lo <= coordinate <= hi and
             _safe(offset, _safe(rate, coordinate, "mul"), "add") == phase and
             (previous is None or previous < coordinate), "Candidate lost exact original coordinate/phase binding")
        pv, qv = poly_eval(p, coordinate), poly_eval(q, coordinate)
        need(item["P_value"] == str(pv) and item["Q_value"] == str(qv), "Candidate amplitude values are not exact")
        expected_zero = pv == ZERO if index % 2 == 0 else qv == ZERO
        need(type(item["is_physical_zero"]) is bool and item["is_physical_zero"] is expected_zero and
             item["branch"] == ("INTEGER_PHASE_P_ZERO" if index % 2 == 0 else "ODD_HALF_PHASE_Q_ZERO"),
             "Candidate physical-zero predicate or phase parity is wrong")
        previous = coordinate
    return True


def _jet_coefficients(p, q, offset, rate, candidate):
    bounded_bytes(candidate)
    need(type(candidate) is dict and type(candidate.get("phase_index")) is int and
         candidate.get("is_physical_zero") is True, "A proven physical candidate is required for a root jet")
    coordinate = _derived(candidate["coordinate"])
    phase = _safe(offset, _safe(rate, coordinate, "mul"), "add")
    need(rate != ZERO and phase == Fraction(candidate["phase_index"], 2) and
         candidate["phase_turn"] == str(phase), "Root jet lost the original moving phase")
    integer = candidate["phase_index"] % 2 == 0
    vanishing, opposite = (p, q) if integer else (q, p)
    zero_value, other_value = poly_eval(vanishing, coordinate), poly_eval(opposite, coordinate)
    need(zero_value == ZERO and other_value != ZERO, "Root jet lacks vanishing and nonvanishing amplitude premises")
    derivative = poly_eval(poly_derivative(vanishing), coordinate)
    rational_coefficient = _safe(derivative, derivative, "mul")
    rate_other = _safe(rate, other_value, "mul")
    pi_squared_coefficient = _safe(rate_other, rate_other, "mul")
    need(rational_coefficient >= ZERO and pi_squared_coefficient > ZERO,
         "The quadratic root jet is not strictly positive")
    return coordinate, phase, derivative, other_value, rational_coefficient, pi_squared_coefficient


def prove_root_jet(p, q, offset, rate, candidate):
    coordinate, phase, derivative, other, constant, pi_squared = _jet_coefficients(p, q, offset, rate, candidate)
    integer = candidate["phase_index"] % 2 == 0
    return {"coordinate": str(coordinate), "phase_turn": str(phase), "phase_index": candidate["phase_index"],
            "vanishing_amplitude": "P" if integer else "Q", "vanishing_amplitude_value": "0",
            "vanishing_amplitude_first_derivative": str(derivative),
            "opposite_amplitude": "Q" if integer else "P", "opposite_amplitude_value": str(other),
            "original_phase_rate": str(rate), "exact_function_value": "0", "exact_first_derivative": "0",
            "quadratic_taylor_coefficient": {"rational": str(constant), "pi_squared": str(pi_squared)},
            "pi_squared_coefficient_strictly_positive": True,
            "first_nonzero_order": 2, "pi_nonzero_is_sufficient": True,
            "pi_irrationality_or_transcendence_used": False}


def _verify_jet(p, q, offset, rate, candidate, jet):
    bounded_bytes(jet)
    coordinate, phase, derivative, other, constant, pi_squared = _jet_coefficients(p, q, offset, rate, candidate)
    need(type(jet) is dict and set(jet) == {"coordinate", "phase_turn", "phase_index", "vanishing_amplitude",
         "vanishing_amplitude_value", "vanishing_amplitude_first_derivative", "opposite_amplitude",
         "opposite_amplitude_value", "original_phase_rate", "exact_function_value", "exact_first_derivative",
         "quadratic_taylor_coefficient", "pi_squared_coefficient_strictly_positive", "first_nonzero_order",
         "pi_nonzero_is_sufficient", "pi_irrationality_or_transcendence_used"}, "Root jet fields changed")
    integer = candidate["phase_index"] % 2 == 0
    need(jet["coordinate"] == str(coordinate) and jet["phase_turn"] == str(phase) and
         type(jet["phase_index"]) is int and jet["phase_index"] == candidate["phase_index"] and
         jet["vanishing_amplitude"] == ("P" if integer else "Q") and
         jet["opposite_amplitude"] == ("Q" if integer else "P") and
         jet["vanishing_amplitude_value"] == jet["exact_function_value"] == jet["exact_first_derivative"] == "0" and
         jet["vanishing_amplitude_first_derivative"] == str(derivative) and
         jet["opposite_amplitude_value"] == str(other) and jet["original_phase_rate"] == str(rate),
         "Root jet amplitude, original phase or exact vanishing values changed")
    need(bounded_bytes(jet["quadratic_taylor_coefficient"]) ==
         bounded_bytes({"rational": str(constant), "pi_squared": str(pi_squared)}) and
         type(jet["first_nonzero_order"]) is int and jet["first_nonzero_order"] == 2 and
         jet["pi_squared_coefficient_strictly_positive"] is True and jet["pi_nonzero_is_sufficient"] is True and
         jet["pi_irrationality_or_transcendence_used"] is False,
         "Actual quadratic coefficient does not justify the claimed exact order two")
    return True


def capture_references():
    """Bounded context custody only; no referenced project code is executed."""
    records = []
    for name, expected in sorted(REFERENCE_PINS.items()):
        path = ROOT / name
        need(path.resolve() == path.absolute(), "Context reference is a symlink alias")
        raw = _read_bounded(path, MAX_REFERENCE_BYTES)
        need(git_blob_bytes(raw) == expected, "Pinned nonexecuted context reference drift: "+name)
        records.append({"path": name, "git_blob": expected, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "use": "PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT"})
    need(bounded_bytes(records) == bounded_bytes(REFERENCE_RECORDS),
         "Exact context reference byte-count/SHA256 identity changed")
    return records


def _verify_lowering(spec, proof):
    """Check returned basis/linear-combination evidence against every original control."""
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"source_sha256", "source_parameter_id",
         "original_source_interval", "global_phase_turn_law", "channels", "C0", "C1"},
         "Whole-source lowering fields changed")
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    need(proof["source_sha256"] == digest(spec) and proof["source_parameter_id"] == spec["source_parameter_id"] and
         proof["original_source_interval"] == [str(lo), str(hi)] and
         bounded_bytes(proof["global_phase_turn_law"]) == bounded_bytes(
             {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]}),
         "Lowering certificate is detached from the complete supplied source/phase/parameter")
    channels = proof["channels"]
    need(type(channels) is list and len(channels) == 2, "Both whole-source coefficient proofs required")
    reciprocal = _safe(ONE, _safe(hi, lo, "sub"), "div")
    u, v = poly_scale((-lo, ONE), reciprocal), poly_scale((hi, -ONE), reciprocal)
    for harmonic, item in zip(("0", "1"), channels):
        spline = spec["cos_splines"][harmonic]
        degree = spline["degree"]
        need(type(item) is dict and set(item) == {"harmonic", "degree", "original_knots", "original_controls",
             "bernstein_basis_in_original_parameter", "global_power_coefficients", "partition_of_unity_verified",
             "left_endpoint_value", "right_endpoint_value"}, "Coefficient proof fields changed")
        need(type(item["harmonic"]) is int and item["harmonic"] == int(harmonic) and
             type(item["degree"]) is int and item["degree"] == degree and
             bounded_bytes(item["original_knots"]) == bounded_bytes(spline["knots"]) and
             bounded_bytes(item["original_controls"]) == bounded_bytes(spline["controls"]) and
             item["partition_of_unity_verified"] is True,
             "Original degree, knot vector or complete control vector was changed or omitted")
        basis = item["bernstein_basis_in_original_parameter"]
        need(type(basis) is list and len(basis) == degree+1, "Complete original Bernstein basis required")
        total, polynomial = (ZERO,), (ZERO,)
        for i, (encoded, control) in enumerate(zip(basis, spline["controls"])):
            term = decode_poly(encoded, max_degree=MAX_SOURCE_DEGREE)
            expected = poly_scale(poly_mul(poly_pow(u, i), poly_pow(v, degree-i)), _number(comb(degree, i)))
            need(term == expected, "Returned Bernstein basis is not in the original global parameter")
            total = poly_add(total, term)
            polynomial = poly_add(polynomial, poly_scale(term, rational(control)))
        need(total == (ONE,) and decode_poly(item["global_power_coefficients"]) == polynomial and
             decode_poly(proof["C"+harmonic]) == polynomial,
             "Returned coefficient does not reconstruct every original control")
        need(item["left_endpoint_value"] == str(poly_eval(polynomial, lo)) == spline["controls"][0] and
             item["right_endpoint_value"] == str(poly_eval(polynomial, hi)) == spline["controls"][-1],
             "Whole-source clamped endpoint identity changed")
    return True


def _source_identity(spec, p, q, lowered):
    _verify_lowering(spec, lowered)
    p2, q2 = poly_mul(p, p), poly_mul(q, q)
    c0 = poly_scale(poly_add(p2, q2), Fraction(1, 2))
    c1 = poly_scale(poly_sub(p2, q2), Fraction(1, 2))
    need(decode_poly(lowered["C0"]) == c0 and decode_poly(lowered["C1"]) == c1,
         "Supplied P/Q squares do not reconstruct the complete original source amplitudes",
         "SOURCE_IDENTITY_NOT_ESTABLISHED")
    return {"P_squared": encode_poly(p2), "Q_squared": encode_poly(q2),
            "C0_equals_half_sum_of_squares": encode_poly(c0),
            "C1_equals_half_difference_of_squares": encode_poly(c1),
            "identities_verified_coefficientwise": True,
            "original_source_equals_nonnegative_square_sum": True,
            "all_original_channels_reconstructed": True,
            "phase_used_in_original_parameter": True}


def _zero_set(spec, enumeration, jets):
    source_hash = digest(spec)
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    roots = [item for item in enumeration["candidates"] if item["is_physical_zero"]]
    need(len(roots) == len(jets), "Each actual physical root requires its own nonzero quadratic jet")
    events = []
    for i, (root, jet) in enumerate(zip(roots, jets)):
        coordinate = _derived(root["coordinate"])
        at_left, at_right = coordinate == lo, coordinate == hi
        location = "LEFT_EXTERIOR" if at_left else "RIGHT_EXTERIOR" if at_right else "SPAN_INTERIOR"
        order = ({"kind": "ONE_SIDED", "side": "RIGHT" if at_left else "LEFT", "value": 2,
                  "outside_order": None, "global_smooth_multiplicity_claimed": False}
                 if at_left or at_right else {"kind": "SMOOTH", "value": 2})
        events.append({"event_id": "ROOT_"+str(i), "source_sha256": source_hash,
            "source_parameter_id": spec["source_parameter_id"],
            "coordinate": {"kind": "RATIONAL", "value": str(coordinate)},
            "location": location, "source_piece_indices": [0], "classification": "TOUCHING",
            "phase_index": root["phase_index"], "phase_turn": root["phase_turn"], "branch": root["branch"],
            "order": order, "left_sign": None if at_left else 1, "right_sign": None if at_right else 1,
            "quadratic_jet": clone(jet)})
    by_coordinate = {event["coordinate"]["value"]: event for event in events}
    need(len(by_coordinate) == len(events), "Moving-phase roots are not distinct original coordinates")

    def node(q):
        if str(q) in by_coordinate:
            return {"kind": "PHYSICAL_ZERO_EVENT", "event_id": by_coordinate[str(q)]["event_id"],
                    "coordinate": str(q), "source_sha256": source_hash,
                    "source_parameter_id": spec["source_parameter_id"]}
        return {"kind": "SOURCE_EXTERIOR", "coordinate": str(q), "side": "LEFT" if q == lo else "RIGHT"}

    boundaries = [lo, *[_derived(event["coordinate"]["value"]) for event in events
                       if event["location"] == "SPAN_INTERIOR"], hi]
    cells = []
    for i, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        need(left < right, "A zero-length nonzero component was introduced")
        cells.append({"cell_id": "CELL_"+str(i), "interval": [str(left), str(right)],
                      "left_boundary": node(left), "right_boundary": node(right),
                      "left_included": str(left) not in by_coordinate,
                      "right_included": str(right) not in by_coordinate,
                      "sign": 1, "source_piece_indices": [0], "crossed_nonzero_source_knots": []})
    offset, rate = rational(spec["phase_turn_offset"]), rational(spec["phase_turn_rate"])
    exteriors = []
    for side, coordinate in (("LEFT", lo), ("RIGHT", hi)):
        event = by_coordinate.get(str(coordinate))
        phase = _safe(offset, _safe(rate, coordinate, "mul"), "add")
        exteriors.append({"side": side, "coordinate": str(coordinate), "phase_turn": str(phase),
            "is_zero": event is not None, "event_ref": event["event_id"] if event else None,
            "value_sign": 0 if event else 1, "exact_value": "0" if event else None,
            "nonzero_exact_scalar_value_claimed": False,
            "positive_sign_from_complete_nonnegative_square_proof": event is None,
            "inward_sign": 1, "inward_order": 2 if event else 0,
            "outside_sign": None, "outside_order": None, "global_smooth_multiplicity_claimed": False})
    return {"kind": "FINITE_ORIGINAL_SOURCE_ZERO_SET", "complete_for_original_closed_source": True,
            "source_interval": [str(lo), str(hi)], "closed_root_count": len(events), "events": events,
            "source_open_root_count": sum(event["location"] == "SPAN_INTERIOR" for event in events),
            "exterior_root_count": sum(event["location"] != "SPAN_INTERIOR" for event in events),
            "true_source_knots": [], "exterior_points": exteriors, "maximal_nonzero_cells": cells,
            "finite_event_list_applicable": True, "nonzero_sign_cells_applicable": True,
            "all_physical_roots_have_order_two": True, "nonzero_source_points_strictly_positive": True,
            "continuum_excluded_by_coprime_and_moving_phase_premises": True,
            "global_cross_source_zero_deduplication_performed": False}


def _assemble_certificate(spec, p_coefficients, q_coefficients, lowered, bezout, enumeration, jets, references):
    _input_preflight(spec, p_coefficients, q_coefficients)
    need(bounded_bytes(references) == bounded_bytes(REFERENCE_RECORDS), "Nonexecuted reference custody changed")
    p = decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    lo, hi, offset, rate = [rational(spec[key]) for key in
                            ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    identity = _source_identity(spec, p, q, lowered)
    _verify_bezout(p, q, bezout)
    _verify_candidates(lo, hi, offset, rate, p, q, enumeration)
    roots = [item for item in enumeration["candidates"] if item["is_physical_zero"]]
    bounded_bytes(jets)
    need(type(jets) is list and len(jets) == len(roots), "Physical-root jet coverage is incomplete")
    for root, jet in zip(roots, jets):
        _verify_jet(p, q, offset, rate, root, jet)
    source_zero_set = _zero_set(spec, enumeration, jets)
    supplied = {"P": clone(p_coefficients), "Q": clone(q_coefficients)}
    result = {"schema": SCHEMA+"/certificate", "status": "ESTABLISHED_COPRIME_SQUARE_ORIGINAL_SOURCE",
        "proof_established": True, "source_zero_set_established": True,
        "evidence_class": "DETERMINISTIC_MODEL", "original_source": clone(spec),
        "source_sha256": digest(spec), "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [str(lo), str(hi)], "phase_turn_law": {"offset": str(offset), "rate": str(rate)},
        "supplied_witness": supplied, "witness_sha256": digest(supplied),
        "normalized_witness": {"P": encode_poly(p), "Q": encode_poly(q)},
        "whole_source_lowering": clone(lowered), "source_identity": identity,
        "bezout_identity": clone(bezout), "phase_candidates": clone(enumeration), "root_jets": clone(jets),
        "source_zero_set": source_zero_set, "context_references": clone(references),
        "theorem_premises": {"both_summands_nonnegative": True,
            "sine_and_cosine_never_vanish_simultaneously": True,
            "no_common_amplitude_zero_from_verified_bezout": True,
            "half_integer_phase_candidates_are_exhaustive": True,
            "nonzero_phase_rate_makes_candidates_finite_and_distinct": True,
            "pi_nonzero_suffices_for_positive_quadratic_jets": True,
            "numerical_sampling_used_as_completeness_authority": False,
            "pi_irrationality_or_transcendence_used": False},
        "scope": {"generic_supplied_source_and_witness_checked": True, "fixture_allowlist_used_for_admission": False,
            "one_original_clamped_span": True, "valid_degree_elevation_admitted": True,
            "original_parameter_and_global_phase_preserved": True, "frozen_corpus_addition": False,
            "historical_source_completion_claimed": False, "generic_owner_route_repaired": False,
            "native_geometry_evidence": False}, "production_authorized": False}
    bounded_bytes(result)
    return result


def _certify_source(spec, p_coefficients, q_coefficients, references):
    _input_preflight(spec, p_coefficients, q_coefficients)
    p = decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    lo, hi, offset, rate = [rational(spec[key]) for key in
                            ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    # Check finite candidate bounds before polynomial Euclid or enumeration.
    _phase_range(lo, hi, offset, rate)
    lowered = lower_source(spec)
    _source_identity(spec, p, q, lowered)
    bezout = compute_bezout(p, q)
    _verify_bezout(p, q, bezout)
    enumeration = enumerate_phase_candidates(lo, hi, offset, rate, p, q)
    _verify_candidates(lo, hi, offset, rate, p, q, enumeration)
    jets = [prove_root_jet(p, q, offset, rate, row) for row in enumeration["candidates"] if row["is_physical_zero"]]
    return _assemble_certificate(spec, p_coefficients, q_coefficients, lowered, bezout, enumeration, jets, references)


def certify_source(spec, p_coefficients, q_coefficients):
    """Fresh generic original-source proof; no saved certificate is a fallback."""
    _input_preflight(spec, p_coefficients, q_coefficients)
    references = capture_references()
    return _invoke(_certify_source, spec, p_coefficients, q_coefficients, references)


def check_source(spec, p_coefficients, q_coefficients):
    try:
        return _invoke(certify_source, spec, p_coefficients, q_coefficients)
    except Refusal as error:
        return error.as_record()


def validate_certificate(spec, p_coefficients, q_coefficients, candidate):
    bounded_bytes(candidate)
    _input_preflight(spec, p_coefficients, q_coefficients)
    expected = certify_source(spec, p_coefficients, q_coefficients)
    need(bounded_bytes(candidate) == bounded_bytes(expected),
         "Submitted certificate differs from a fresh proof of the supplied source/witness")
    return True


def source_from_polynomials(p_coefficients, q_coefficients, lo, hi, offset, rate, source_parameter_id, *, degrees=None):
    """Bounded fixture constructor only; admission always reconstructs its output."""
    _hint_preflight(p_coefficients)
    _hint_preflight(q_coefficients)
    for token in (lo, hi, offset, rate):
        rational_parts(token)
    need(type(source_parameter_id) is str and 0 < len(source_parameter_id) <= 128 and "\0" not in source_parameter_id,
         "Bounded source parameter ID required")
    if degrees is not None:
        need(type(degrees) in (tuple, list) and len(degrees) == 2 and
             all(type(d) is int and 0 <= d <= MAX_SOURCE_DEGREE for d in degrees),
             "Two bounded exact Bernstein degrees required", "RESOURCE_REFUSAL")
    p = decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    low, high, b, r = map(rational, (lo, hi, offset, rate))
    _phase_range(low, high, b, r)
    width = _safe(high, low, "sub")
    p2, q2 = poly_mul(p, p), poly_mul(q, q)
    coefficients = (poly_scale(poly_add(p2, q2), Fraction(1, 2)),
                    poly_scale(poly_sub(p2, q2), Fraction(1, 2)))
    splines = {}
    for harmonic, polynomial in enumerate(coefficients):
        natural_degree = max(0, _degree(polynomial))
        degree = natural_degree if degrees is None else degrees[harmonic]
        need(natural_degree <= degree <= MAX_SOURCE_DEGREE,
             "Requested Bernstein degree cannot represent the amplitude polynomial")
        local = (ZERO,)
        for power, coefficient in enumerate(polynomial):
            local = poly_add(local, poly_scale(poly_pow((low, width), power), coefficient))
        controls = []
        for i in range(degree+1):
            control = ZERO
            for k in range(min(i, len(local)-1)+1):
                factor = Fraction(comb(i, k), comb(degree, k))
                control = _safe(control, _safe(local[k], factor, "mul"), "add")
            controls.append(str(control))
        splines[str(harmonic)] = {"degree": degree, "knots": [lo]*(degree+1)+[hi]*(degree+1), "controls": controls}
    spec = {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE", "source_parameter_id": source_parameter_id,
            "parameter_lo": lo, "parameter_hi": hi, "phase_turn_offset": offset, "phase_turn_rate": rate,
            "cos_splines": splines, "sin_splines": {}}
    _input_preflight(spec, p_coefficients, q_coefficients)
    return spec


def default_cases():
    definitions = [
        ("mtp-irreducible-boundary:quadratic-touch", "Qualified MTP quadratic touch, re-proved by the new class", ["-1", "1"], ["1"], "1/2", "3/2", "0", "1"),
        ("coprime-square:nonmatching-amplitude", "An amplitude zero at a nonmatching phase is not a source zero", ["-1/2", "1"], ["1/4", "1"], "0", "1", "0", "1"),
        ("coprime-square:interior-exterior", "One interior and one right exterior touch", ["-1", "1"], ["-1/2", "1"], "0", "1", "0", "1"),
        ("coprime-square:three-closed-touches", "Two exterior touches and one interior touch", ["0", "-1", "1"], ["-1/2", "1"], "0", "1", "0", "1"),
        ("coprime-square:zero-p", "Zero P and nonzero constant Q", ["0"], ["1"], "0", "2", "0", "1"),
        ("coprime-square:zero-q", "Nonzero constant P and zero Q", ["1"], ["0"], "0", "2", "0", "1"),
        ("coprime-square:negative-rate", "Original root order survives reversed phase order", ["0", "-1", "1"], ["-1/2", "1"], "0", "1", "1", "-1"),
        ("coprime-square:phase-offset", "Nonzero phase offset with two interior touches", ["-3/2", "1"], ["-1/2", "1"], "0", "2", "1/4", "1/2"),
    ]
    cases = []
    for index, (suffix, description, p, q, lo, hi, offset, rate) in enumerate(definitions):
        spec = (clone(MTP_SOURCE_SPEC) if index == 0 else
                source_from_polynomials(p, q, lo, hi, offset, rate, "pb00701-"+suffix+"-original-t"))
        cases.append({"case_id": "research:pb00701:"+suffix, "description": description,
                      "spec": spec, "P": p, "Q": q})
    return cases


def replay_sources():
    references = capture_references()
    results = []
    for case in default_cases():
        certificate = _invoke(_certify_source, case["spec"], case["P"], case["Q"], references)
        result = clone(case)
        result["certificate"] = certificate
        results.append(result)
    return {"context_references": references, "cases": results}


def report_from_replay(replay):
    bounded_bytes(replay)
    need(type(replay) is dict and set(replay) == {"context_references", "cases"} and
         bounded_bytes(replay["context_references"]) == bounded_bytes(REFERENCE_RECORDS),
         "Default proof context or reference custody changed")
    actual, expected = replay["cases"], default_cases()
    need(type(actual) is list and len(actual) == len(expected), "A default supplied-source case was omitted or duplicated")
    cases = []
    counts = Counter()
    for candidate, case in zip(actual, expected):
        need(type(candidate) is dict and set(candidate) == set(case) | {"certificate"}, "Default case fields changed")
        for key in case:
            need(bounded_bytes(candidate[key]) == bounded_bytes(case[key]), "Default source/witness/label changed: "+key)
        certificate = candidate["certificate"]
        need(type(certificate) is dict, "Actual complete source certificate required")
        rebuilt = _assemble_certificate(case["spec"], case["P"], case["Q"], certificate.get("whole_source_lowering"),
            certificate.get("bezout_identity"), certificate.get("phase_candidates"), certificate.get("root_jets"),
            replay["context_references"])
        need(bounded_bytes(certificate) == bounded_bytes(rebuilt),
             "Actual certificate/source topology does not follow from the checked source proof premises")
        cases.append(clone(candidate))
        zeros = rebuilt["source_zero_set"]
        counts["original_research_sources"] += 1
        counts["phase_candidates"] += rebuilt["phase_candidates"]["phase_range"]["candidate_count"]
        counts["per_source_closed_physical_roots"] += zeros["closed_root_count"]
        counts["original_exterior_roots"] += zeros["exterior_root_count"]
        counts["strict_source_interior_roots"] += zeros["source_open_root_count"]
        counts["maximal_positive_nonzero_cells"] += len(zeros["maximal_nonzero_cells"])
        counts["root_free_sources"] += int(zeros["closed_root_count"] == 0)
        counts["order_two_root_jets"] += len(rebuilt["root_jets"])
    result = {"schema": SCHEMA, "status": "ESTABLISHED_BOUNDED_COPRIME_SQUARE_SOURCE_CHECKER_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL", "qualified_base_main": BASE_MAIN,
        "context_references": clone(replay["context_references"]), "cases": cases,
        "summary": dict(sorted(counts.items())),
        "supplied_source_contract": {"generic_admission_by_reconstruction_and_verified_bezout": True,
            "fixture_allowlist_used_for_admission": False, "closed_finite_phase_lattice_is_exhaustive": True,
            "original_phase_and_parameter_preserved": True, "all_admitted_physical_roots_order_two": True,
            "nonzero_points_strictly_positive": True, "noncardinal_exterior_exact_values_not_fabricated": True,
            "valid_degree_elevation_admitted": True, "pi_irrationality_or_transcendence_used": False,
            "stationary_phase_or_nonconstant_gcd_admitted": False,
            "failed_proofs_return_atomic_nontruth": True},
        "budgets": {"input_rational_bits": MAX_INPUT_BITS, "input_rational_token_characters": 128,
            "derived_rational_bits": MAX_INTERMEDIATE_BITS, "derived_rational_token_characters": MAX_DERIVED_TOKEN,
            "hint_degree": MAX_HINT_DEGREE, "original_coefficient_degree": MAX_SOURCE_DEGREE,
            "maximum_half_integer_phase_candidates": MAX_CANDIDATES,
            "original_coordinate_absolute_bound": 2, "offset_and_rate_absolute_bound": 8,
            "phase_endpoint_absolute_bound": 16, "report_bytes": MAX_BYTES,
            "json_value_nodes": MAX_NODES, "json_depth": MAX_DEPTH},
        "scope": {"prior_qualified_research_source_reproved": 1, "new_research_sources": 7,
            "all_examples_outside_frozen_fifty_source_cohort": True,
            "frozen_corpus_additions": 0, "historical_route_or_source_completions_claimed": 0,
            "generic_owner_route_repaired": False, "project_context_code_executed": False,
            "python_and_standard_library_trusted": True, "hostile_python_sandbox_claimed": False,
            "native_geometry_evidence": False},
        "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN", "PB-007-04": "OPEN",
            "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED", "production_authorized": False,
            "frozen_fifty_source_cohort_unchanged": True, "frozen_121_source_corpus_unchanged": True,
            "historical_20_blocked_and_30_order_gap_dispositions_unchanged": True,
            "all_26_operations_unchanged": True}}
    bounded_bytes(result)
    return result


def expected_report():
    return _invoke(report_from_replay, _invoke(replay_sources))


def read_report(path=REPORT):
    need(type(path) in (str, type(REPORT)), "Exact bounded report path required", "RESOURCE_REFUSAL")
    text = str(path)
    need(0 < len(text) <= 4096 and "\0" not in text, "Report path text budget", "RESOURCE_REFUSAL")
    return parse_json_bytes(_read_bounded(Path(path), MAX_BYTES))


def _compare_with_replayed_bytes(candidate, expected_bytes):
    need(type(expected_bytes) is bytes and len(expected_bytes) <= MAX_BYTES,
         "Bounded expected report required", "RESOURCE_REFUSAL")
    need(bounded_bytes(candidate) == expected_bytes, "Submitted report differs from fresh complete supplied-source proofs")
    return True


def validate_report(candidate):
    bounded_bytes(candidate)
    return _compare_with_replayed_bytes(candidate, bounded_bytes(expected_report()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--contract", action="store_true")
    options = parser.parse_args()
    if not (options.write_report or options.contract):
        parser.error("choose --write-report and/or --contract")
    result = expected_report()
    if options.write_report:
        REPORT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True)+"\n")
    if options.contract:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(result))
        print("PASS: each complete original source has verified coprime-square identities and an exhaustive order-two zero set")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()


