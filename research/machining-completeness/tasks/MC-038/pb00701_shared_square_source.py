#!/usr/bin/env python3
"""Bounded complete original-source proofs for shared squared amplitudes.

Exact source reconstruction, a freshly proved coprime residual, checked Sturm
isolation and additive orders preserve every common polynomial factor.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK_DIR = "research/machining-completeness/tasks/MC-038/"
REPORT = HERE / "pb00701-shared-square-source.json"
SCHEMA = "radicadsac-mc038-shared-square-source/1.0"
BASE_MAIN = "384521e111d684a55fe09edfd5ab17c3b41fd426"
MAX_BYTES = 4 * 1024 * 1024
MAX_REFERENCE_BYTES = 256 * 1024
MAX_CODE_BYTES = 256 * 1024
MAX_NODES = 131072
MAX_DEPTH = 48
MAX_STRING = 4096
MAX_INPUT_BITS = 128
MAX_INTERMEDIATE_BITS = 4096
MAX_DERIVED_TOKEN = 2500
MAX_HINT_DEGREE = 3
MAX_SOURCE_DEGREE = 6
MAX_POLY_DEGREE = 12
MAX_CANDIDATES = 65
MAX_MIDPOINT_OPERATIONS = 128
MAX_PHYSICAL_EVENTS = 68
_FractionType = Fraction
COPRIME_MODEL = 'research/machining-completeness/tasks/MC-038/pb00701_coprime_square_source.py'
COPRIME_BLOB = '4db47f79acff3c036e67ba03dd11b9bfb0a96bdb'
MC032_REFERENCE = 'research/machining-completeness/tasks/MC-032/event_engine.py'
DEPENDENCY_PINS = {'docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md': '6005fc55e2d18e71639e6bc31cfbc1597bf4a915',
 'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
 'research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary.json': '4840bbca3847962b537684e0dffa871bd6de82a2',
 'research/machining-completeness/tasks/MC-038/pb00701_coprime_square_source.py': '4db47f79acff3c036e67ba03dd11b9bfb0a96bdb',
 'research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
 'research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py': '4f9000549834c8f9b60ebc9925fadb71e9f96acf'}
INPUT_RECORDS = [{'bytes': 2255,
  'git_blob': '6005fc55e2d18e71639e6bc31cfbc1597bf4a915',
  'path': 'docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md',
  'sha256': '7cc6704ee4636e498d4f8575dfaea35462f33effc20fbef6d45d994b416f4515',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 10017,
  'git_blob': '789a709c5141479a343035d1b7055dd4e53534e1',
  'path': 'research/machining-completeness/tasks/MC-032/event_engine.py',
  'sha256': '0463db3b5d3ada72c40ca5aa3025f4234fd120887714416d2b39b790cb27fac8',
  'use': 'PINNED_NONEXECUTED_ALGORITHM_REFERENCE'},
 {'bytes': 18930,
  'git_blob': '4840bbca3847962b537684e0dffa871bd6de82a2',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary.json',
  'sha256': 'c645a88dc54232de9cf64c542b83c5d38caf835401f4eaec3cedc9744f7a3ff3',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 57398,
  'git_blob': '4db47f79acff3c036e67ba03dd11b9bfb0a96bdb',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701_coprime_square_source.py',
  'sha256': '5fcde62b1d66ae82ded6b1960c45713af2cd0bf731338b6c8a29c2ac5c0c2940',
  'use': 'EXECUTED_QUALIFIED_COPRIME_PRODUCER'},
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



def qualified_coprime_module():
    """Compile exactly the bounded checked buffer; retain every consumed input."""
    buffers = {}
    records = []
    for relative, pin in sorted(DEPENDENCY_PINS.items()):
        path = ROOT / relative
        need(path.resolve() == path.absolute(), "Pinned input has a symlink alias")
        limit = MAX_CODE_BYTES if relative == COPRIME_MODEL else MAX_REFERENCE_BYTES
        raw = _read_bounded(path, limit)
        need(git_blob_bytes(raw) == pin, "Pinned dependency drift: " + relative)
        buffers[relative] = raw
        expected = next(item for item in INPUT_RECORDS if item["path"] == relative)
        records.append({"path": relative, "git_blob": pin, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(), "use": expected["use"]})
    need(bounded_bytes(records) == bounded_bytes(INPUT_RECORDS), "Input byte/SHA256 custody changed")
    name = "_radicadsac_shared_square_coprime_" + COPRIME_BLOB
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / COPRIME_MODEL)
    module.__package__ = ""
    exec(compile(buffers[COPRIME_MODEL], module.__file__, "exec", dont_inherit=True, optimize=0), module.__dict__)
    need(module.REFERENCE_PINS == {key: value for key, value in DEPENDENCY_PINS.items()
                                 if key not in (COPRIME_MODEL, MC032_REFERENCE)},
         "Qualified producer reference closure changed")
    retained = {str(ROOT / key): raw for key, raw in buffers.items()
                if key not in (COPRIME_MODEL, MC032_REFERENCE)}

    def retained_read(path, limit):
        need(type(limit) is int and 0 <= limit <= MAX_REFERENCE_BYTES, "Retained-read bound changed", "RESOURCE_REFUSAL")
        key = str(path)
        need(key in retained, "Producer requested an undeclared input")
        raw = retained[key]
        need(len(raw) <= limit, "Retained input exceeds requested read budget", "RESOURCE_REFUSAL")
        return raw

    # The generic producer still executes its own reference comparison, using
    # the identical original bytes captured before its code was compiled.
    module._read_bounded = retained_read
    module._shared_input_custody = clone(records)
    return module


def _typed(function):
    def wrapped(*args, **kwargs):
        return _invoke(function, *args, **kwargs)
    wrapped.__name__ = function.__name__
    wrapped.__doc__ = function.__doc__
    return wrapped


def _poly(c, values):
    result = c._trim(values)
    need(c._degree(result) <= MAX_HINT_DEGREE, "Sturm/gcd polynomial degree budget", "RESOURCE_REFUSAL")
    return result


def _decode(c, tokens):
    return _poly(c, c.decode_poly(tokens, max_degree=MAX_HINT_DEGREE))


def _sign(value):
    return 1 if value > ZERO else -1 if value < ZERO else 0


def _verify_division(c, dividend, divisor, row):
    bounded_bytes(row)
    need(type(row) is dict and set(row) == {"dividend", "divisor", "quotient", "remainder"}, "Exact division receipt fields required")
    need(_decode(c, row["dividend"]) == dividend and _decode(c, row["divisor"]) == divisor and divisor != (ZERO,),
         "Division receipt lost consecutive actual inputs")
    quotient, remainder = _decode(c, row["quotient"]), _decode(c, row["remainder"])
    need(c.poly_add(c.poly_mul(quotient, divisor), remainder) == dividend and
         (remainder == (ZERO,) or c._degree(remainder) < c._degree(divisor)),
         "Exact division identity or strict degree descent failed")
    return quotient, remainder


@_typed
def checked_gcd(c, p, q):
    """Monic gcd with bounded actual Euclidean divisions, including zero arms."""
    p, q = _poly(c, p), _poly(c, q)
    need(p != (ZERO,) or q != (ZERO,), "Both-zero gcd is handled by the original continuum branch")
    a, b, trace = p, q, []
    while b != (ZERO,):
        need(len(trace) <= MAX_HINT_DEGREE+1, "Euclid degree-descent budget", "RESOURCE_REFUSAL")
        quotient, remainder = c.poly_divmod(a, b)
        row = {"dividend": c.encode_poly(a), "divisor": c.encode_poly(b),
               "quotient": c.encode_poly(quotient), "remainder": c.encode_poly(remainder)}
        _verify_division(c, a, b, row)
        trace.append(row)
        a, b = b, remainder
    scale = c._safe(ONE, a[-1], "div")
    normalized = c.poly_scale(a, scale)
    return {"left_polynomial": c.encode_poly(p), "right_polynomial": c.encode_poly(q),
            "euclidean_trace": trace, "last_nonzero_remainder": c.encode_poly(a),
            "monic_scale": str(scale), "monic_gcd": c.encode_poly(normalized),
            "all_divisions_and_degree_descents_verified": True}


def _verify_gcd(c, p, q, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"left_polynomial", "right_polynomial", "euclidean_trace",
         "last_nonzero_remainder", "monic_scale", "monic_gcd", "all_divisions_and_degree_descents_verified"},
         "Gcd receipt fields changed")
    need(_decode(c, proof["left_polynomial"]) == p and _decode(c, proof["right_polynomial"]) == q and
         (p != (ZERO,) or q != (ZERO,)), "Gcd receipt lost its actual polynomial pair")
    trace = proof["euclidean_trace"]
    need(type(trace) is list and len(trace) <= MAX_HINT_DEGREE+2, "Gcd trace budget", "RESOURCE_REFUSAL")
    a, b = p, q
    for row in trace:
        _, remainder = _verify_division(c, a, b, row)
        a, b = b, remainder
    need(b == (ZERO,) and a != (ZERO,) and _decode(c, proof["last_nonzero_remainder"]) == a,
         "Gcd trace does not terminate at its declared last nonzero remainder")
    scale = c._derived(proof["monic_scale"])
    g = _decode(c, proof["monic_gcd"])
    need(scale == c._safe(ONE, a[-1], "div") and g == c.poly_scale(a, scale) and g[-1] == ONE and
         proof["all_divisions_and_degree_descents_verified"] is True,
         "Gcd monic normalization lost its exact nonzero scale")
    return g


@_typed
def sturm_sequence(c, polynomial):
    """A checked square-free part and its exact negative-remainder sequence."""
    p = _poly(c, polynomial)
    need(p != (ZERO,), "Zero polynomial does not have a finite Sturm root count")
    derivative = c.poly_derivative(p)
    gcd_proof = checked_gcd(c, p, derivative)
    repeated = _verify_gcd(c, p, derivative, gcd_proof)
    square_free, remainder = c.poly_divmod(p, repeated)
    division = {"dividend": c.encode_poly(p), "divisor": c.encode_poly(repeated),
                "quotient": c.encode_poly(square_free), "remainder": c.encode_poly(remainder)}
    _verify_division(c, p, repeated, division)
    need(remainder == (ZERO,), "Square-free quotient is not exact")
    sequence = [square_free]
    if c._degree(square_free) > 0:
        sequence.append(c.poly_derivative(square_free))
    trace = []
    while len(sequence) > 1:
        a, b = sequence[-2:]
        quotient, remainder = c.poly_divmod(a, b)
        row = {"dividend": c.encode_poly(a), "divisor": c.encode_poly(b),
               "quotient": c.encode_poly(quotient), "remainder": c.encode_poly(remainder)}
        _verify_division(c, a, b, row)
        trace.append(row)
        if remainder == (ZERO,):
            break
        sequence.append(c.poly_scale(remainder, -ONE))
        need(len(sequence) <= MAX_HINT_DEGREE+1, "Sturm sequence degree budget", "RESOURCE_REFUSAL")
    return {"polynomial": c.encode_poly(p), "gcd_with_derivative": gcd_proof,
            "square_free_division": division, "square_free_polynomial": c.encode_poly(square_free),
            "sequence": [c.encode_poly(member) for member in sequence], "division_trace": trace,
            "negative_remainders_without_sign_changing_rescaling": True,
            "square_free_part_verified": True}


def _verify_sturm(c, polynomial, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"polynomial", "gcd_with_derivative", "square_free_division",
         "square_free_polynomial", "sequence", "division_trace", "negative_remainders_without_sign_changing_rescaling",
         "square_free_part_verified"}, "Sturm receipt fields changed")
    p = _poly(c, polynomial)
    need(p != (ZERO,) and _decode(c, proof["polynomial"]) == p, "Sturm receipt lost its nonzero polynomial")
    repeated = _verify_gcd(c, p, c.poly_derivative(p), proof["gcd_with_derivative"])
    square_free, remainder = _verify_division(c, p, repeated, proof["square_free_division"])
    need(remainder == (ZERO,) and _decode(c, proof["square_free_polynomial"]) == square_free,
         "Incorrect square-free quotient")
    encoded = proof["sequence"]
    need(type(encoded) is list and 1 <= len(encoded) <= MAX_HINT_DEGREE+1,
         "Sturm sequence length budget", "RESOURCE_REFUSAL")
    sequence = [_decode(c, row) for row in encoded]
    need(all(member != (ZERO,) for member in sequence) and sequence[0] == square_free,
         "Sturm sequence starts at the wrong polynomial or contains zero")
    trace = proof["division_trace"]
    need(type(trace) is list and len(trace) <= MAX_HINT_DEGREE, "Sturm division trace budget", "RESOURCE_REFUSAL")
    if c._degree(square_free) == 0:
        need(len(sequence) == 1 and not trace, "Constant polynomial acquired false Sturm members")
    else:
        need(len(sequence) >= 2 and sequence[1] == c.poly_derivative(square_free) and
             len(trace) == len(sequence)-1, "Sturm derivative/terminal division coverage changed")
        for index, row in enumerate(trace):
            _, remainder = _verify_division(c, sequence[index], sequence[index+1], row)
            if index+2 < len(sequence):
                need(remainder != (ZERO,) and sequence[index+2] == c.poly_scale(remainder, -ONE),
                     "Sturm member is not the exact negative remainder")
            else:
                need(remainder == (ZERO,) and c._degree(sequence[-1]) == 0,
                     "Square-free Sturm sequence did not end at a nonzero constant")
    need(proof["negative_remainders_without_sign_changing_rescaling"] is True and
         proof["square_free_part_verified"] is True, "Sturm mathematical premise flags changed")
    return square_free, sequence


@_typed
def one_sided_sign(c, polynomial, coordinate, side):
    p, q = _poly(c, polynomial), c._coefficient(coordinate)
    need(p != (ZERO,) and type(side) is str and side in ("LEFT", "RIGHT"), "Nonzero polynomial and exact side required")
    member = p
    for order in range(c._degree(p)+1):
        value = c.poly_eval(member, q)
        if value != ZERO:
            sign = _sign(value) * (-1 if side == "LEFT" and order % 2 else 1)
            return {"polynomial": c.encode_poly(p), "coordinate": str(q), "side": side,
                    "first_nonzero_derivative_order": order, "first_nonzero_derivative_value": str(value),
                    "sign": sign, "exact_taylor_side_sign": True}
        member = c.poly_derivative(member)
    raise Refusal("Nonzero polynomial lacked a finite Taylor leading term")


def _verify_side_sign(c, polynomial, coordinate, side, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"polynomial", "coordinate", "side", "first_nonzero_derivative_order",
         "first_nonzero_derivative_value", "sign", "exact_taylor_side_sign"}, "One-sided sign receipt fields changed")
    need(_decode(c, proof["polynomial"]) == polynomial and proof["coordinate"] == str(coordinate) and
         proof["side"] == side and type(proof["first_nonzero_derivative_order"]) is int and
         0 <= proof["first_nonzero_derivative_order"] <= c._degree(polynomial),
         "One-sided sign lost its polynomial/point/side/order binding")
    member = polynomial
    for order in range(proof["first_nonzero_derivative_order"]):
        need(c.poly_eval(member, coordinate) == ZERO, "A lower nonzero derivative was skipped")
        member = c.poly_derivative(member)
    value = c.poly_eval(member, coordinate)
    sign = _sign(value) * (-1 if side == "LEFT" and proof["first_nonzero_derivative_order"] % 2 else 1)
    need(value != ZERO and proof["first_nonzero_derivative_value"] == str(value) and
         type(proof["sign"]) is int and proof["sign"] == sign and proof["exact_taylor_side_sign"] is True,
         "Claimed one-sided sign does not follow from the first nonzero derivative")
    return sign


def _variations(signs):
    need(type(signs) is list and all(type(sign) is int and sign in (-1, 1) for sign in signs),
         "Exact nonzero Sturm signs required")
    return sum(left != right for left, right in zip(signs, signs[1:]))


def _count_from_sturm(c, polynomial, sturm, lo, hi):
    _, sequence = _verify_sturm(c, polynomial, sturm)
    lo, hi = c._coefficient(lo), c._coefficient(hi)
    need(lo < hi, "Strict open counting interval required")
    left = [one_sided_sign(c, member, lo, "RIGHT") for member in sequence]
    right = [one_sided_sign(c, member, hi, "LEFT") for member in sequence]
    ls = [_verify_side_sign(c, member, lo, "RIGHT", row) for member, row in zip(sequence, left)]
    rs = [_verify_side_sign(c, member, hi, "LEFT", row) for member, row in zip(sequence, right)]
    lv, rv = _variations(ls), _variations(rs)
    count = lv-rv
    need(0 <= count <= max(0, c._degree(polynomial)), "Sturm count is outside the polynomial degree")
    return {"polynomial": c.encode_poly(polynomial), "interval": [str(lo), str(hi)],
            "sturm": clone(sturm), "left_right_limit_signs": left, "right_left_limit_signs": right,
            "left_variations": lv, "right_variations": rv, "open_root_count": count,
            "both_interval_endpoints_excluded": True}


@_typed
def count_roots_open(c, polynomial, lo, hi):
    polynomial = _poly(c, polynomial)
    return _count_from_sturm(c, polynomial, sturm_sequence(c, polynomial), lo, hi)


def _verify_count(c, polynomial, lo, hi, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"polynomial", "interval", "sturm", "left_right_limit_signs",
         "right_left_limit_signs", "left_variations", "right_variations", "open_root_count",
         "both_interval_endpoints_excluded"}, "Open-root count receipt fields changed")
    need(_decode(c, proof["polynomial"]) == polynomial and proof["interval"] == [str(lo), str(hi)] and lo < hi,
         "Open-root count lost its original polynomial or strict interval")
    _, sequence = _verify_sturm(c, polynomial, proof["sturm"])
    left, right = proof["left_right_limit_signs"], proof["right_left_limit_signs"]
    need(type(left) is list and type(right) is list and len(left) == len(right) == len(sequence),
         "One-sided Sturm signs do not cover the complete sequence")
    ls = [_verify_side_sign(c, p, lo, "RIGHT", row) for p, row in zip(sequence, left)]
    rs = [_verify_side_sign(c, p, hi, "LEFT", row) for p, row in zip(sequence, right)]
    lv, rv = _variations(ls), _variations(rs)
    need(all(type(proof[key]) is int for key in ("left_variations", "right_variations", "open_root_count")) and
         proof["left_variations"] == lv and proof["right_variations"] == rv and
         proof["open_root_count"] == lv-rv and 0 <= lv-rv <= max(0, c._degree(polynomial)) and
         proof["both_interval_endpoints_excluded"] is True, "Sturm variations do not prove the claimed strict count")
    return lv-rv


def _actual_count(c, polynomial, lo, hi):
    receipt = count_roots_open(c, polynomial, lo, hi)
    return receipt, _verify_count(c, polynomial, lo, hi, receipt)

def _budget():
    need(type(MAX_MIDPOINT_OPERATIONS) is int and 0 <= MAX_MIDPOINT_OPERATIONS <= 128,
         "Isolation midpoint budget may not exceed the hard ceiling128", "RESOURCE_REFUSAL")
    return MAX_MIDPOINT_OPERATIONS


def _boundaries(c, g, lo, hi, residual_events):
    bounded_bytes(residual_events)
    need(type(residual_events) is list and len(residual_events) <= MAX_CANDIDATES,
         "Bounded actual residual event list required", "RESOURCE_REFUSAL")
    indexed, ids, previous = {}, set(), None
    for event in residual_events:
        need(type(event) is dict and type(event.get("event_id")) is str and
             0 < len(event["event_id"]) <= 256 and event["event_id"] not in ids and
             type(event.get("coordinate")) is dict and set(event["coordinate"]) == {"kind", "value"} and
             event["coordinate"]["kind"] == "RATIONAL", "Residual event identity or rational coordinate changed")
        coordinate = c._derived(event["coordinate"]["value"])
        need(lo <= coordinate <= hi and (previous is None or previous < coordinate),
             "Residual events are not distinct ordered original-source points")
        indexed[coordinate] = event["event_id"]
        ids.add(event["event_id"])
        previous = coordinate
    rows = []
    for coordinate in sorted({lo, hi, *indexed}):
        value = c.poly_eval(g, coordinate)
        rows.append({"coordinate": str(coordinate), "G_value": str(value), "is_G_root": value == ZERO,
                     "residual_event_id": indexed.get(coordinate),
                     "source_exterior_side": "LEFT" if coordinate == lo else "RIGHT" if coordinate == hi else None})
    return rows


def _rational_coordinate(value):
    return {"kind": "RATIONAL", "value": str(value)}


def _algebraic_coordinate(c, square_free, lo, hi):
    return {"kind": "REAL_ALGEBRAIC_ISOLATOR", "defining_polynomial": c.encode_poly(square_free),
            "isolating_interval": [str(lo), str(hi)], "unique_root_in_open_interval": True,
            "defining_polynomial_square_free": True, "defining_polynomial_irreducible_claimed": False,
            "coordinate_irrationality_claimed": False}


def _coordinate_bounds(c, coordinate):
    bounded_bytes(coordinate)
    need(type(coordinate) is dict, "Exact coordinate descriptor required")
    if coordinate.get("kind") == "RATIONAL":
        need(set(coordinate) == {"kind", "value"}, "Rational coordinate fields changed")
        value = c._derived(coordinate["value"])
        return value, value
    need(set(coordinate) == {"kind", "defining_polynomial", "isolating_interval", "unique_root_in_open_interval",
         "defining_polynomial_square_free", "defining_polynomial_irreducible_claimed", "coordinate_irrationality_claimed"} and
         coordinate["kind"] == "REAL_ALGEBRAIC_ISOLATOR" and type(coordinate["isolating_interval"]) is list and
         len(coordinate["isolating_interval"]) == 2 and coordinate["unique_root_in_open_interval"] is True and
         coordinate["defining_polynomial_square_free"] is True and
         coordinate["defining_polynomial_irreducible_claimed"] is False and
         coordinate["coordinate_irrationality_claimed"] is False,
         "Algebraic descriptor fields or unclaimed minimality/rationality changed")
    lo, hi = map(c._derived, coordinate["isolating_interval"])
    need(lo < hi, "An algebraic root requires a strict positive-width isolator")
    return lo, hi


@_typed
def build_multiplicity_chain(c, g):
    member = _poly(c, g)
    result = []
    while c._degree(member) > 0:
        need(len(result) < MAX_HINT_DEGREE, "Multiplicity chain degree budget", "RESOURCE_REFUSAL")
        sturm = sturm_sequence(c, member)
        _verify_sturm(c, member, sturm)
        following = checked_gcd(c, member, c.poly_derivative(member))
        next_member = _verify_gcd(c, member, c.poly_derivative(member), following)
        need(c._degree(next_member) < c._degree(member), "Multiplicity gcd chain did not descend")
        result.append({"level": len(result), "polynomial": c.encode_poly(member),
                       "sturm": sturm, "next_gcd": following})
        member = next_member
    return result


def _verify_chain(c, g, chain):
    bounded_bytes(chain)
    need(type(chain) is list and len(chain) <= MAX_HINT_DEGREE, "Multiplicity chain budget", "RESOURCE_REFUSAL")
    member = g
    for index, row in enumerate(chain):
        need(type(row) is dict and set(row) == {"level", "polynomial", "sturm", "next_gcd"} and
             type(row["level"]) is int and row["level"] == index and c._degree(member) > 0 and
             _decode(c, row["polynomial"]) == member, "Multiplicity chain lost its actual consecutive member")
        _verify_sturm(c, member, row["sturm"])
        following = _verify_gcd(c, member, c.poly_derivative(member), row["next_gcd"])
        need(c._degree(following) < c._degree(member), "Multiplicity gcd chain failed strict degree descent")
        member = following
    need(c._degree(member) == 0, "Multiplicity chain is incomplete")
    return True


def _multiplicity_from_chain(c, g, chain, coordinate):
    _verify_chain(c, g, chain)
    left, right = _coordinate_bounds(c, coordinate)
    rows, seen_absent = [], False
    for index, member in enumerate(chain):
        poly = _decode(c, member["polynomial"])
        if left == right:
            value = c.poly_eval(poly, left)
            count = int(value == ZERO)
            row = {"level": index, "root_count": count, "rational_value": str(value), "open_count_receipt": None}
        else:
            receipt = _count_from_sturm(c, poly, member["sturm"], left, right)
            count = _verify_count(c, poly, left, right, receipt)
            need(count in (0, 1), "A divisor has multiple roots in a unique G isolator")
            row = {"level": index, "root_count": count, "rational_value": None, "open_count_receipt": receipt}
        need(not (seen_absent and count), "Gcd-chain root membership is not nested")
        seen_absent = seen_absent or count == 0
        rows.append(row)
    multiplicity = sum(row["root_count"] for row in rows)
    need(1 <= multiplicity <= MAX_HINT_DEGREE and rows[0]["root_count"] == 1,
         "Coordinate is not a root of the original G")
    derivative = None
    if left == right:
        member = g
        for order in range(multiplicity):
            need(c.poly_eval(member, left) == ZERO, "A lower nonzero G derivative contradicts multiplicity")
            member = c.poly_derivative(member)
        value = c.poly_eval(member, left)
        need(value != ZERO, "Claimed rational-root multiplicity is too small")
        derivative = {"first_nonzero_order": multiplicity, "first_nonzero_derivative_value": str(value)}
    return {"multiplicity": multiplicity, "chain_membership": rows,
            "rational_derivative_cross_check": derivative, "multiplicity_counted_from_actual_gcd_chain": True}


@_typed
def prove_polynomial_multiplicity(c, g, chain, coordinate):
    return _multiplicity_from_chain(c, g, chain, coordinate)


def _ordered_root_records(c, g, chain, raw_roots, *, use_hook):
    rows = sorted(raw_roots, key=lambda item: _coordinate_bounds(c, item["coordinate"])[0])
    result, previous = [], None
    for index, row in enumerate(rows):
        left, right = _coordinate_bounds(c, row["coordinate"])
        if previous is not None:
            need(previous <= left, "Polynomial roots have overlapping or reversed coordinate locators")
            need(not (previous == left == right), "A polynomial rational root was duplicated")
        evidence = (prove_polynomial_multiplicity(c, g, chain, row["coordinate"]) if use_hook else
                    _multiplicity_from_chain(c, g, chain, row["coordinate"]))
        expected = _multiplicity_from_chain(c, g, chain, row["coordinate"])
        need(bounded_bytes(evidence) == bounded_bytes(expected), "Actual polynomial multiplicity receipt is inaccurate")
        result.append({"polynomial_root_id": "GROOT_"+str(index), "coordinate": clone(row["coordinate"]),
                       "discovery": clone(row["discovery"]), "multiplicity": evidence["multiplicity"],
                       "multiplicity_evidence": evidence})
        previous = right
    return result


@_typed
def isolate_polynomial_roots(c, g, lo, hi, residual_events):
    g, lo, hi = _poly(c, g), c._coefficient(lo), c._coefficient(hi)
    need(g != (ZERO,) and -TWO <= lo < hi <= TWO, "Bounded nonzero G and original interval required")
    budget = _budget()
    sturm = sturm_sequence(c, g)
    square_free, _ = _verify_sturm(c, g, sturm)
    boundaries = _boundaries(c, g, lo, hi, residual_events)
    closed_receipt, open_count = _actual_count(c, g, lo, hi)
    closed_count = open_count + int(c.poly_eval(g, lo) == ZERO) + int(c.poly_eval(g, hi) == ZERO)
    raw_roots = [{"coordinate": _rational_coordinate(c._derived(row["coordinate"])),
                  "discovery": {"kind": "PARTITION_BOUNDARY", "boundary_index": i}}
                 for i, row in enumerate(boundaries) if row["is_G_root"]]
    gaps, queue, trace = [], [], []
    for index, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        a, b = c._derived(left["coordinate"]), c._derived(right["coordinate"])
        receipt, count = _actual_count(c, g, a, b)
        node = "GAP_"+str(index)
        gaps.append({"node_id": node, "interval": [str(a), str(b)], "count_receipt": receipt})
        queue.append((node, a, b, receipt, count))
    midpoint_operations = 0
    while queue:
        node, a, b, receipt, count = queue.pop(0)
        av, bv = c.poly_eval(g, a), c.poly_eval(g, b)
        row = {"node_id": node, "interval": [str(a), str(b)], "open_root_count": count,
               "left_G_value": str(av), "right_G_value": str(bv), "count_receipt": clone(receipt)}
        if count == 0:
            row["action"] = "EMPTY_OPEN_INTERVAL"
        elif count == 1 and c._degree(square_free) == 1:
            coordinate = c._safe(-square_free[0], square_free[1], "div")
            need(a < coordinate < b and c.poly_eval(g, coordinate) == ZERO, "Linear square-free coordinate is not the unique open G root")
            row.update({"action": "LINEAR_EXACT_ROOT", "coordinate": _rational_coordinate(coordinate)})
            raw_roots.append({"coordinate": clone(row["coordinate"]), "discovery": {"kind": row["action"], "node_id": node}})
        elif count == 1 and av != ZERO and bv != ZERO:
            row.update({"action": "STRICT_UNIQUE_OPEN_ISOLATOR", "coordinate": _algebraic_coordinate(c, square_free, a, b)})
            raw_roots.append({"coordinate": clone(row["coordinate"]), "discovery": {"kind": row["action"], "node_id": node}})
        else:
            need(midpoint_operations < budget, "Global isolation midpoint budget exhausted before the next split", "RESOURCE_REFUSAL")
            midpoint_operations += 1
            midpoint = c._safe(c._safe(a, b, "add"), TWO, "div")
            value = c.poly_eval(g, midpoint)
            left_receipt, nl = _actual_count(c, g, a, midpoint)
            right_receipt, nr = _actual_count(c, g, midpoint, b)
            need(count == nl+int(value == ZERO)+nr, "Bisection failed exact open-count conservation")
            row.update({"action": "EXACT_MIDPOINT_SPLIT", "midpoint": str(midpoint), "midpoint_G_value": str(value),
                        "midpoint_is_G_root": value == ZERO, "left_count_receipt": left_receipt,
                        "right_count_receipt": right_receipt})
            if value == ZERO:
                raw_roots.append({"coordinate": _rational_coordinate(midpoint),
                                  "discovery": {"kind": "EXACT_MIDPOINT", "node_id": node}})
            queue.append((node+":L", a, midpoint, left_receipt, nl))
            queue.append((node+":R", midpoint, b, right_receipt, nr))
        trace.append(row)
        need(len(trace) <= MAX_CANDIDATES+1+2*budget, "Isolation trace structural budget", "RESOURCE_REFUSAL")
    chain = build_multiplicity_chain(c, g)
    _verify_chain(c, g, chain)
    roots = _ordered_root_records(c, g, chain, raw_roots, use_hook=True)
    need(len(roots) == closed_count and closed_count <= max(0, c._degree(g)),
         "Exported polynomial roots do not equal the complete closed Sturm count")
    return {"G": c.encode_poly(g), "source_interval": [str(lo), str(hi)], "sturm": sturm,
            "square_free_polynomial": c.encode_poly(square_free), "partition_boundaries": boundaries,
            "initial_gap_searches": gaps, "isolation_trace": trace,
            "midpoint_operations": midpoint_operations, "global_midpoint_budget": budget,
            "all_endpoint_cleaning_splits_counted": True, "multiplicity_chain": chain,
            "closed_interval_open_count_receipt": closed_receipt, "closed_polynomial_root_count": closed_count,
            "roots": roots, "all_original_gaps_searched": True,
            "closed_count_equals_boundary_plus_isolated_roots": True,
            "no_residual_root_inside_exported_open_isolator": True,
            "minimal_polynomial_or_irrationality_claimed": False}


def _verify_isolation(c, g, lo, hi, residual_events, proof):
    bounded_bytes(proof)
    fields = {"G", "source_interval", "sturm", "square_free_polynomial", "partition_boundaries", "initial_gap_searches",
              "isolation_trace", "midpoint_operations", "global_midpoint_budget", "all_endpoint_cleaning_splits_counted",
              "multiplicity_chain", "closed_interval_open_count_receipt", "closed_polynomial_root_count", "roots",
              "all_original_gaps_searched", "closed_count_equals_boundary_plus_isolated_roots",
              "no_residual_root_inside_exported_open_isolator", "minimal_polynomial_or_irrationality_claimed"}
    need(type(proof) is dict and set(proof) == fields and _decode(c, proof["G"]) == g and
         proof["source_interval"] == [str(lo), str(hi)], "Polynomial isolation source/fields changed")
    square_free, _ = _verify_sturm(c, g, proof["sturm"])
    need(_decode(c, proof["square_free_polynomial"]) == square_free, "Isolation defining polynomial changed")
    boundaries = _boundaries(c, g, lo, hi, residual_events)
    need(bounded_bytes(proof["partition_boundaries"]) == bounded_bytes(boundaries), "Original/residual search boundaries changed")
    count = _verify_count(c, g, lo, hi, proof["closed_interval_open_count_receipt"])
    closed_count = count+int(c.poly_eval(g, lo) == ZERO)+int(c.poly_eval(g, hi) == ZERO)
    need(type(proof["closed_polynomial_root_count"]) is int and proof["closed_polynomial_root_count"] == closed_count,
         "Complete closed polynomial count changed")
    budget = _budget()
    need(type(proof["global_midpoint_budget"]) is int and proof["global_midpoint_budget"] == budget and
         type(proof["midpoint_operations"]) is int and 0 <= proof["midpoint_operations"] <= budget,
         "Isolation resource receipt exceeds or aliases the actual fixed budget", "RESOURCE_REFUSAL")
    raw_roots = [{"coordinate": _rational_coordinate(c._derived(row["coordinate"])),
                  "discovery": {"kind": "PARTITION_BOUNDARY", "boundary_index": i}}
                 for i, row in enumerate(boundaries) if row["is_G_root"]]
    gaps = proof["initial_gap_searches"]
    need(type(gaps) is list and len(gaps) == len(boundaries)-1, "An original open search gap was omitted or duplicated")
    queue = []
    for index, (gap, left, right) in enumerate(zip(gaps, boundaries, boundaries[1:])):
        a, b = c._derived(left["coordinate"]), c._derived(right["coordinate"])
        node = "GAP_"+str(index)
        need(type(gap) is dict and set(gap) == {"node_id", "interval", "count_receipt"} and
             gap["node_id"] == node and gap["interval"] == [str(a), str(b)], "Open search gap identity changed")
        count = _verify_count(c, g, a, b, gap["count_receipt"])
        queue.append((node, a, b, gap["count_receipt"], count))
    trace = proof["isolation_trace"]
    need(type(trace) is list and len(trace) <= MAX_CANDIDATES+1+2*budget, "Isolation trace length budget", "RESOURCE_REFUSAL")
    midpoint_operations = 0
    for row in trace:
        need(queue, "Isolation trace invented an unsearched node")
        node, a, b, receipt, count = queue.pop(0)
        av, bv = c.poly_eval(g, a), c.poly_eval(g, b)
        base = {"node_id": node, "interval": [str(a), str(b)], "open_root_count": count,
                "left_G_value": str(av), "right_G_value": str(bv), "count_receipt": clone(receipt)}
        need(type(row) is dict, "Exact isolation node required")
        for key, value in base.items():
            need(key in row and bounded_bytes(row[key]) == bounded_bytes(value), "Isolation node changed its actual pending state")
        if count == 0:
            expected = {**base, "action": "EMPTY_OPEN_INTERVAL"}
        elif count == 1 and c._degree(square_free) == 1:
            coordinate = c._safe(-square_free[0], square_free[1], "div")
            need(a < coordinate < b and c.poly_eval(g, coordinate) == ZERO, "Incorrect exact linear root")
            expected = {**base, "action": "LINEAR_EXACT_ROOT", "coordinate": _rational_coordinate(coordinate)}
            raw_roots.append({"coordinate": clone(expected["coordinate"]), "discovery": {"kind": expected["action"], "node_id": node}})
        elif count == 1 and av != ZERO and bv != ZERO:
            expected = {**base, "action": "STRICT_UNIQUE_OPEN_ISOLATOR", "coordinate": _algebraic_coordinate(c, square_free, a, b)}
            raw_roots.append({"coordinate": clone(expected["coordinate"]), "discovery": {"kind": expected["action"], "node_id": node}})
        else:
            need(midpoint_operations < budget, "Global endpoint-cleaning/split budget exhausted", "RESOURCE_REFUSAL")
            midpoint_operations += 1
            midpoint = c._safe(c._safe(a, b, "add"), TWO, "div")
            value = c.poly_eval(g, midpoint)
            need("left_count_receipt" in row and "right_count_receipt" in row, "Split omitted a strict child count")
            nl = _verify_count(c, g, a, midpoint, row["left_count_receipt"])
            nr = _verify_count(c, g, midpoint, b, row["right_count_receipt"])
            need(count == nl+int(value == ZERO)+nr, "Actual split count conservation failed")
            expected = {**base, "action": "EXACT_MIDPOINT_SPLIT", "midpoint": str(midpoint), "midpoint_G_value": str(value),
                        "midpoint_is_G_root": value == ZERO, "left_count_receipt": clone(row["left_count_receipt"]),
                        "right_count_receipt": clone(row["right_count_receipt"])}
            if value == ZERO:
                raw_roots.append({"coordinate": _rational_coordinate(midpoint), "discovery": {"kind": "EXACT_MIDPOINT", "node_id": node}})
            queue.append((node+":L", a, midpoint, row["left_count_receipt"], nl))
            queue.append((node+":R", midpoint, b, row["right_count_receipt"], nr))
        need(bounded_bytes(row) == bounded_bytes(expected), "Isolation action or exact midpoint evidence changed")
    need(not queue and midpoint_operations == proof["midpoint_operations"], "Isolation trace left an unsearched branch or inaccurate work count")
    _verify_chain(c, g, proof["multiplicity_chain"])
    roots = _ordered_root_records(c, g, proof["multiplicity_chain"], raw_roots, use_hook=False)
    need(len(roots) == closed_count and bounded_bytes(proof["roots"]) == bounded_bytes(roots),
         "Exported G roots/multiplicities do not match all actual isolation branches")
    need(all(proof[key] is True for key in ("all_endpoint_cleaning_splits_counted", "all_original_gaps_searched",
         "closed_count_equals_boundary_plus_isolated_roots", "no_residual_root_inside_exported_open_isolator")) and
         proof["minimal_polynomial_or_irrationality_claimed"] is False, "Polynomial completeness/coordinate scope flags changed")
    return roots

@_typed
def decompose_amplitudes(c, p, q):
    p, q = _poly(c, p), _poly(c, q)
    proof = checked_gcd(c, p, q)
    g = _verify_gcd(c, p, q, proof)
    p0, pr = c.poly_divmod(p, g)
    q0, qr = c.poly_divmod(q, g)
    pd = {"dividend": c.encode_poly(p), "divisor": c.encode_poly(g), "quotient": c.encode_poly(p0), "remainder": c.encode_poly(pr)}
    qd = {"dividend": c.encode_poly(q), "divisor": c.encode_poly(g), "quotient": c.encode_poly(q0), "remainder": c.encode_poly(qr)}
    _verify_division(c, p, g, pd)
    _verify_division(c, q, g, qd)
    need(pr == qr == (ZERO,), "The computed common factor does not divide both original amplitudes")
    g2 = c.poly_mul(g, g)
    p02, q02 = c.poly_mul(p0, p0), c.poly_mul(q0, q0)
    h0 = c.poly_scale(c.poly_add(p02, q02), Fraction(1, 2))
    h1 = c.poly_scale(c.poly_sub(p02, q02), Fraction(1, 2))
    return {"G": c.encode_poly(g), "P0": c.encode_poly(p0), "Q0": c.encode_poly(q0),
            "gcd_proof": proof, "P_division": pd, "Q_division": qd, "G_squared": c.encode_poly(g2),
            "residual_C0": c.encode_poly(h0), "residual_C1": c.encode_poly(h1),
            "original_C0_product": c.encode_poly(c.poly_mul(g2, h0)),
            "original_C1_product": c.encode_poly(c.poly_mul(g2, h1)),
            "original_parameter_and_scale_preserved": True, "factor_square_not_discarded": True}


def _verify_decomposition(c, p, q, lowered, proof):
    bounded_bytes(proof)
    need(type(proof) is dict and set(proof) == {"G", "P0", "Q0", "gcd_proof", "P_division", "Q_division",
         "G_squared", "residual_C0", "residual_C1", "original_C0_product", "original_C1_product",
         "original_parameter_and_scale_preserved", "factor_square_not_discarded"}, "Shared-factor decomposition fields changed")
    g = _verify_gcd(c, p, q, proof["gcd_proof"])
    p0, pr = _verify_division(c, p, g, proof["P_division"])
    q0, qr = _verify_division(c, q, g, proof["Q_division"])
    need(pr == qr == (ZERO,) and _decode(c, proof["G"]) == g and _decode(c, proof["P0"]) == p0 and
         _decode(c, proof["Q0"]) == q0, "Exact quotient or shared-factor scale changed")
    g2 = c.poly_mul(g, g)
    p02, q02 = c.poly_mul(p0, p0), c.poly_mul(q0, q0)
    h0 = c.poly_scale(c.poly_add(p02, q02), Fraction(1, 2))
    h1 = c.poly_scale(c.poly_sub(p02, q02), Fraction(1, 2))
    c0, c1 = c.poly_mul(g2, h0), c.poly_mul(g2, h1)
    need(c.decode_poly(proof["G_squared"]) == g2 and c.decode_poly(proof["residual_C0"]) == h0 and
         c.decode_poly(proof["residual_C1"]) == h1 and c.decode_poly(proof["original_C0_product"]) == c0 and
         c.decode_poly(proof["original_C1_product"]) == c1 and c.decode_poly(lowered["C0"]) == c0 and
         c.decode_poly(lowered["C1"]) == c1 and proof["original_parameter_and_scale_preserved"] is True and
         proof["factor_square_not_discarded"] is True, "Original full coefficients are not exactly G squared times the residual")
    return g, p0, q0


def _residual_source(c, spec, p0, q0):
    # This actual qualified constructor enforces its unchanged raw128-bit
    # envelope on both quotient hints and every converted residual control.
    return c.source_from_polynomials(c.encode_poly(p0), c.encode_poly(q0),
        spec["parameter_lo"], spec["parameter_hi"], spec["phase_turn_offset"], spec["phase_turn_rate"],
        spec["source_parameter_id"])


@_typed
def prove_residual_source(c, spec, p0, q0):
    source = _residual_source(c, spec, p0, q0)
    certificate = c.certify_source(source, c.encode_poly(p0), c.encode_poly(q0))
    return {"source": source, "source_sha256": digest(source), "P0": c.encode_poly(p0), "Q0": c.encode_poly(q0),
            "certificate": certificate, "producer_code": COPRIME_MODEL, "producer_git_blob": COPRIME_BLOB,
            "actual_generic_producer_called": True, "saved_report_used_as_proof": False}


def _verify_residual(c, spec, p0, q0, residual):
    bounded_bytes(residual)
    need(type(residual) is dict and set(residual) == {"source", "source_sha256", "P0", "Q0", "certificate",
         "producer_code", "producer_git_blob", "actual_generic_producer_called", "saved_report_used_as_proof"},
         "Fresh residual certificate is missing or malformed")
    source = _residual_source(c, spec, p0, q0)
    need(bounded_bytes(residual["source"]) == bounded_bytes(source) and residual["source_sha256"] == digest(source) and
         residual["P0"] == c.encode_poly(p0) and residual["Q0"] == c.encode_poly(q0) and
         residual["producer_code"] == COPRIME_MODEL and residual["producer_git_blob"] == COPRIME_BLOB and
         residual["actual_generic_producer_called"] is True and residual["saved_report_used_as_proof"] is False,
         "Residual source, phase, parameter, quotients or producer custody changed")
    certificate = residual["certificate"]
    need(type(certificate) is dict, "Actual complete coprime residual certificate required")
    rebuilt = c._assemble_certificate(source, c.encode_poly(p0), c.encode_poly(q0),
        certificate.get("whole_source_lowering"), certificate.get("bezout_identity"),
        certificate.get("phase_candidates"), certificate.get("root_jets"), certificate.get("context_references"))
    need(bounded_bytes(certificate) == bounded_bytes(rebuilt), "Actual residual certificate failed its qualified proof contract")
    return rebuilt


def _physical_zero_set(c, spec, g_proof, residual_certificate):
    bounded_bytes(g_proof)
    bounded_bytes(residual_certificate)
    source_hash = digest(spec)
    lo, hi = c.rational(spec["parameter_lo"]), c.rational(spec["parameter_hi"])
    g = _decode(c, g_proof["G"])
    h_events = residual_certificate["source_zero_set"]["events"]
    _verify_isolation(c, g, lo, hi, h_events, g_proof)
    h_by_point = {event["coordinate"]["value"]: event for event in h_events}
    rows, used_h = [], set()
    for groot in g_proof["roots"]:
        coordinate = groot["coordinate"]
        h = h_by_point.get(coordinate["value"]) if coordinate["kind"] == "RATIONAL" else None
        if h is not None:
            need(c.poly_eval(g, c._derived(h["coordinate"]["value"])) == ZERO, "False G/H coincidence")
            used_h.add(h["event_id"])
        else:
            left, right = _coordinate_bounds(c, coordinate)
            need(all(not left < c._derived(event["coordinate"]["value"]) < right for event in h_events),
                 "An algebraic-format G root is not separated from a distinct residual root")
        rows.append({"coordinate": clone(coordinate), "polynomial_root_id": groot["polynomial_root_id"],
                     "polynomial_multiplicity": groot["multiplicity"], "residual_event_id": h["event_id"] if h else None})
    for event in h_events:
        if event["event_id"] not in used_h:
            need(c.poly_eval(g, c._derived(event["coordinate"]["value"])) != ZERO,
                 "A true G/H coincidence was omitted from the polynomial root set")
            rows.append({"coordinate": clone(event["coordinate"]), "polynomial_root_id": None,
                         "polynomial_multiplicity": 0, "residual_event_id": event["event_id"]})
    need(len(rows) <= MAX_PHYSICAL_EVENTS, "Physical event structural budget", "RESOURCE_REFUSAL")
    rows.sort(key=lambda item: (_coordinate_bounds(c, item["coordinate"])[0],
                               0 if item["coordinate"]["kind"] == "RATIONAL" else 1))
    events, previous = [], None
    for index, row in enumerate(rows):
        left, right = _coordinate_bounds(c, row["coordinate"])
        need(lo <= left <= right <= hi, "A physical root left its original closed source")
        if previous is not None:
            pl, pr = previous
            need(pr <= left and not (pl == pr == left == right), "Physical root ordering or distinctness failed")
        previous = left, right
        at_left, at_right = left == right == lo, left == right == hi
        location = "LEFT_EXTERIOR" if at_left else "RIGHT_EXTERIOR" if at_right else "SPAN_INTERIOR"
        residual_order = 2 if row["residual_event_id"] is not None else 0
        physical_order = 2*row["polynomial_multiplicity"]+residual_order
        need(physical_order in (2, 4, 6, 8), "The physical product order lacks a positive even leading order")
        order = ({"kind": "ONE_SIDED", "side": "RIGHT" if at_left else "LEFT", "inward_order": physical_order,
                  "outside_order": None, "global_smooth_multiplicity_claimed": False} if at_left or at_right else
                 {"kind": "SMOOTH", "multiplicity": physical_order})
        events.append({"event_id": "ZERO_"+str(index), "source_sha256": source_hash,
            "source_parameter_id": spec["source_parameter_id"], "coordinate": clone(row["coordinate"]),
            "location": location, "source_piece_indices": [0], "classification": "TOUCHING", "order": order,
            "physical_order": physical_order, "polynomial_root_id": row["polynomial_root_id"],
            "polynomial_multiplicity": row["polynomial_multiplicity"], "residual_event_id": row["residual_event_id"],
            "residual_root_order": residual_order, "residual_source_sha256": residual_certificate["source_sha256"],
            "order_addition": {"squared_G_order": 2*row["polynomial_multiplicity"], "H_order": residual_order,
                               "physical_order": physical_order},
            "left_sign": None if at_left else 1, "right_sign": None if at_right else 1,
            "complete_residual_positivity_used_away_from_its_roots": row["residual_event_id"] is None})
    at_exterior = {event["coordinate"]["value"]: event for event in events
                   if event["location"] != "SPAN_INTERIOR"}

    def event_boundary(event):
        return {"kind": "PHYSICAL_ZERO_EVENT", "event_id": event["event_id"], "coordinate": clone(event["coordinate"]),
                "source_sha256": source_hash, "source_parameter_id": spec["source_parameter_id"]}

    def exterior_boundary(coordinate, side):
        event = at_exterior.get(str(coordinate))
        return event_boundary(event) if event else {"kind": "SOURCE_EXTERIOR", "side": side,
                "coordinate": _rational_coordinate(coordinate), "source_sha256": source_hash,
                "source_parameter_id": spec["source_parameter_id"]}

    boundaries = [exterior_boundary(lo, "LEFT")]
    boundaries += [event_boundary(event) for event in events if event["location"] == "SPAN_INTERIOR"]
    boundaries.append(exterior_boundary(hi, "RIGHT"))
    cells = [{"cell_id": "CELL_"+str(index), "left_boundary": clone(left), "right_boundary": clone(right),
              "left_included": left["kind"] == "SOURCE_EXTERIOR", "right_included": right["kind"] == "SOURCE_EXTERIOR",
              "sign": 1, "source_piece_indices": [0], "crossed_nonzero_source_knots": [],
              "positive_from_G_squared_times_complete_residual": True}
             for index, (left, right) in enumerate(zip(boundaries, boundaries[1:]))]
    b, r = c.rational(spec["phase_turn_offset"]), c.rational(spec["phase_turn_rate"])
    exteriors = []
    for side, coordinate in (("LEFT", lo), ("RIGHT", hi)):
        event = at_exterior.get(str(coordinate))
        phase = c._safe(b, c._safe(r, coordinate, "mul"), "add")
        exteriors.append({"side": side, "coordinate": str(coordinate), "phase_turn": str(phase),
            "is_zero": event is not None, "event_ref": event["event_id"] if event else None,
            "value_sign": 0 if event else 1, "exact_value": "0" if event else None,
            "nonzero_exact_scalar_value_claimed": False, "positive_sign_from_complete_nonnegative_square_proof": event is None,
            "inward_sign": 1, "inward_order": event["physical_order"] if event else 0,
            "outside_sign": None, "outside_order": None, "global_smooth_multiplicity_claimed": False})
    return {"kind": "FINITE_ORIGINAL_SOURCE_ZERO_SET", "complete_for_original_closed_source": True,
            "source_interval": [str(lo), str(hi)], "closed_root_count": len(events), "events": events,
            "source_open_root_count": sum(event["location"] == "SPAN_INTERIOR" for event in events),
            "exterior_root_count": len(at_exterior), "true_source_knots": [], "exterior_points": exteriors,
            "maximal_nonzero_cells": cells, "finite_event_list_applicable": True, "nonzero_sign_cells_applicable": True,
            "all_physical_roots_have_even_order": True, "nonzero_source_points_strictly_positive": True,
            "continuum_excluded_by_nonzero_G_and_coprime_moving_residual": True,
            "global_cross_source_zero_deduplication_performed": False,
            "isolator_endpoints_substituted_for_physical_root_boundaries": False}


@_typed
def assemble_physical_union(c, spec, g_proof, residual_certificate):
    return _physical_zero_set(c, spec, g_proof, residual_certificate)


def _continuum(spec):
    return {"kind": "CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET", "complete_for_original_closed_source": True,
            "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
            "zero_interval": {"interval": [spec["parameter_lo"], spec["parameter_hi"]], "left_included": True, "right_included": True},
            "original_source_identically_zero": True, "closed_root_count": None, "events": None,
            "source_open_root_count": None, "exterior_root_count": None, "true_source_knots": [],
            "exterior_points": [{"side": side, "coordinate": spec[key], "is_zero": True, "exact_value": "0",
                                 "isolated_root_order": None, "outside_sign": None, "outside_order": None}
                                for side, key in (("LEFT", "parameter_lo"), ("RIGHT", "parameter_hi"))],
            "maximal_nonzero_cells": None, "finite_event_list_applicable": False, "nonzero_sign_cells_applicable": False,
            "finite_root_cardinality_claimed": False, "residual_producer_applicable": False}


def _assemble_certificate(c, spec, p_coefficients, q_coefficients, lowered, decomposition, residual, g_proof, zero_set, custody):
    _input_preflight(spec, p_coefficients, q_coefficients)
    need(bounded_bytes(custody) == bounded_bytes(INPUT_RECORDS), "Complete consumed dependency custody changed")
    p = c.decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = c.decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    lo, hi, b, r = [c.rational(spec[key]) for key in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    c._phase_range(lo, hi, b, r)
    identity = c._source_identity(spec, p, q, lowered)
    continuum = p == q == (ZERO,)
    if continuum:
        need(decomposition is None and residual is None and g_proof is None,
             "Identity-zero branch must not invent a finite residual or polynomial root list")
        rebuilt_zero_set = _continuum(spec)
    else:
        g, p0, q0 = _verify_decomposition(c, p, q, lowered, decomposition)
        residual_certificate = _verify_residual(c, spec, p0, q0, residual)
        _verify_isolation(c, g, lo, hi, residual_certificate["source_zero_set"]["events"], g_proof)
        rebuilt_zero_set = _physical_zero_set(c, spec, g_proof, residual_certificate)
    need(bounded_bytes(zero_set) == bounded_bytes(rebuilt_zero_set),
         "Physical zero set does not follow from actual original-source/G/residual proof premises")
    supplied = {"P": clone(p_coefficients), "Q": clone(q_coefficients)}
    result = {"schema": SCHEMA+"/certificate", "status": "ESTABLISHED_SHARED_SQUARE_ORIGINAL_SOURCE",
        "proof_established": True, "source_zero_set_established": True, "evidence_class": "DETERMINISTIC_MODEL",
        "original_source": clone(spec), "source_sha256": digest(spec), "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [str(lo), str(hi)], "phase_turn_law": {"offset": str(b), "rate": str(r)},
        "supplied_witness": supplied, "witness_sha256": digest(supplied),
        "normalized_witness": {"P": c.encode_poly(p), "Q": c.encode_poly(q)},
        "whole_source_lowering": clone(lowered), "source_identity": clone(identity),
        "decomposition": clone(decomposition), "residual": clone(residual), "polynomial_root_proof": clone(g_proof),
        "source_zero_set": rebuilt_zero_set, "input_custody": clone(custody),
        "theorem_premises": {"original_source_equals_G_squared_times_fresh_coprime_residual": not continuum,
            "shared_polynomial_factor_is_retained": not continuum, "complete_polynomial_roots_from_checked_sturm": not continuum,
            "residual_roots_and_positive_complement_freshly_proved": not continuum,
            "analytic_product_orders_add": not continuum, "identity_zero_proved_from_complete_original_controls": continuum,
            "numerical_samples_or_saved_reports_used_as_completeness_authority": False,
            "pi_irrationality_or_transcendence_used": False},
        "scope": {"generic_supplied_source_and_witness_checked": True, "fixture_allowlist_used_for_admission": False,
            "one_original_clamped_span": True, "valid_degree_elevation_admitted": True,
            "original_parameter_and_global_phase_preserved": True,
            "algebraic_descriptors_do_not_claim_minimality_or_irrationality": True,
            "residual_raw_input_envelope_unchanged": True, "MC032_reference_executed": False,
            "frozen_corpus_addition": False, "historical_source_completion_claimed": False,
            "generic_owner_route_repaired": False, "native_geometry_evidence": False}, "production_authorized": False}
    bounded_bytes(result)
    return result


def _certify_source(c, spec, p_coefficients, q_coefficients):
    _input_preflight(spec, p_coefficients, q_coefficients)
    p = c.decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = c.decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    lo, hi, b, r = [c.rational(spec[key]) for key in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    c._phase_range(lo, hi, b, r)
    lowered = c.lower_source(spec)
    c._source_identity(spec, p, q, lowered)
    if p == q == (ZERO,):
        decomposition = residual = g_proof = None
        zeros = _continuum(spec)
    else:
        decomposition = decompose_amplitudes(c, p, q)
        g, p0, q0 = _verify_decomposition(c, p, q, lowered, decomposition)
        residual = prove_residual_source(c, spec, p0, q0)
        certificate = _verify_residual(c, spec, p0, q0, residual)
        g_proof = isolate_polynomial_roots(c, g, lo, hi, certificate["source_zero_set"]["events"])
        _verify_isolation(c, g, lo, hi, certificate["source_zero_set"]["events"], g_proof)
        zeros = assemble_physical_union(c, spec, g_proof, certificate)
    return _assemble_certificate(c, spec, p_coefficients, q_coefficients, lowered, decomposition, residual, g_proof,
                                 zeros, c._shared_input_custody)


def certify_source(spec, p_coefficients, q_coefficients):
    """Fresh original-source proof, including the unchanged residual input limits."""
    _input_preflight(spec, p_coefficients, q_coefficients)
    c = _invoke(qualified_coprime_module)
    return _invoke(_certify_source, c, spec, p_coefficients, q_coefficients)


def check_source(spec, p_coefficients, q_coefficients):
    try:
        return _invoke(certify_source, spec, p_coefficients, q_coefficients)
    except Refusal as error:
        return error.as_record()


def validate_certificate(spec, p_coefficients, q_coefficients, candidate):
    bounded_bytes(candidate)
    _input_preflight(spec, p_coefficients, q_coefficients)
    expected = certify_source(spec, p_coefficients, q_coefficients)
    need(bounded_bytes(candidate) == bounded_bytes(expected), "Certificate differs from a fresh complete proof of the supplied source")
    return True


def source_from_polynomials(p_coefficients, q_coefficients, lo, hi, offset, rate, source_parameter_id, *, degrees=None):
    _hint_preflight(p_coefficients)
    _hint_preflight(q_coefficients)
    for token in (lo, hi, offset, rate):
        rational_parts(token)
    need(type(source_parameter_id) is str and 0 < len(source_parameter_id) <= 128 and "\0" not in source_parameter_id,
         "Bounded original parameter required", "RESOURCE_REFUSAL")
    if degrees is not None:
        need(type(degrees) in (tuple, list) and len(degrees) == 2 and
             all(type(d) is int and 0 <= d <= MAX_SOURCE_DEGREE for d in degrees), "Bounded degree-elevation controls required", "RESOURCE_REFUSAL")
    c = _invoke(qualified_coprime_module)
    return _invoke(c.source_from_polynomials, p_coefficients, q_coefficients, lo, hi, offset, rate,
                   source_parameter_id, degrees=degrees)

def _default_cases(c):
    definitions = [
        ("hidden-noncardinal-rational", "A common factor retains the noncardinal original root", ["-1/3", "1"], ["-1/3", "1"], "0", "1"),
        ("polynomial-carrier-coincidence", "One original root combines common-factor and residual orders", ["1", "-2", "1"], ["-1", "1"], "1/2", "3/2"),
        ("two-algebraic-roots", "Two exact roots use square-free polynomial and unique open isolators", ["-1/2", "0", "1"], ["-1/2", "0", "1"], "-1", "1"),
        ("algebraic-rational-ordered-union", "Two algebraic-format roots surround a distinct rational residual root", ["0", "-1/2", "0", "1"], ["-1/2", "0", "1"], "-1", "1"),
        ("repeated-common-root", "A repeated common root has original order four away from residual zeros", ["1/4", "-1", "1"], ["1/4", "-1", "1"], "0", "1"),
        ("sixth-order-coincidence", "Common multiplicity two and residual order two combine to physical order six", ["-1", "3", "-3", "1"], ["1", "-2", "1"], "1/2", "3/2"),
        ("closed-continuum", "Complete original zero identity has no finite event-list semantics", ["0"], ["0"], "0", "1"),
        ("cubic-common-source-exterior", "Cubic common roots include an exact original right exterior", ["0", "-1/2", "-1/2", "1"], ["0", "-1", "-1", "2"], "-1", "1"),
    ]
    result = []
    for suffix, description, p, q, lo, hi in definitions:
        parameter = "pb00701-shared-square-"+suffix+"-original-t"
        spec = c.source_from_polynomials(p, q, lo, hi, "0", "1", parameter)
        result.append({"case_id": "research:pb00701:shared-square:"+suffix, "description": description, "spec": spec, "P": p, "Q": q})
    return result


def default_cases():
    return _invoke(_default_cases, _invoke(qualified_coprime_module))


def replay_sources():
    c = _invoke(qualified_coprime_module)
    cases = []
    for case in _default_cases(c):
        certificate = _invoke(_certify_source, c, case["spec"], case["P"], case["Q"])
        row = clone(case)
        row["certificate"] = certificate
        cases.append(row)
    return {"input_custody": clone(c._shared_input_custody), "cases": cases}


def report_from_replay(replay):
    bounded_bytes(replay)
    need(type(replay) is dict and set(replay) == {"input_custody", "cases"} and
         bounded_bytes(replay["input_custody"]) == bounded_bytes(INPUT_RECORDS), "Default replay/source custody changed")
    c = _invoke(qualified_coprime_module)
    actual, expected = replay["cases"], _default_cases(c)
    need(type(actual) is list and len(actual) == len(expected), "A default original-source case was omitted or duplicated")
    results, counts, orders = [], Counter(), Counter()
    for row, definition in zip(actual, expected):
        need(type(row) is dict and set(row) == set(definition) | {"certificate"}, "Default source row fields changed")
        for key in definition:
            need(bounded_bytes(row[key]) == bounded_bytes(definition[key]), "Default original source/witness/identity changed: "+key)
        certificate = row["certificate"]
        need(type(certificate) is dict, "A complete actual source certificate is required")
        rebuilt = _assemble_certificate(c, definition["spec"], definition["P"], definition["Q"],
            certificate.get("whole_source_lowering"), certificate.get("decomposition"), certificate.get("residual"),
            certificate.get("polynomial_root_proof"), certificate.get("source_zero_set"), replay["input_custody"])
        need(bounded_bytes(certificate) == bounded_bytes(rebuilt), "Source certificate/physical topology differs from its actual checked proof premises")
        results.append(clone(row))
        counts["original_research_sources"] += 1
        zeros = rebuilt["source_zero_set"]
        if zeros["kind"] == "CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET":
            counts["closed_continuum_sources"] += 1
            continue
        counts["finite_sources"] += 1
        counts["per_source_closed_physical_roots"] += zeros["closed_root_count"]
        counts["strict_source_interior_roots"] += zeros["source_open_root_count"]
        counts["original_exterior_roots"] += zeros["exterior_root_count"]
        counts["maximal_positive_nonzero_cells"] += len(zeros["maximal_nonzero_cells"])
        counts["root_free_finite_sources"] += int(zeros["closed_root_count"] == 0)
        counts["common_polynomial_roots"] += rebuilt["polynomial_root_proof"]["closed_polynomial_root_count"]
        counts["actual_residual_proofs"] += 1
        counts["residual_physical_roots"] += rebuilt["residual"]["certificate"]["source_zero_set"]["closed_root_count"]
        counts["residual_half_integer_phase_candidates"] += rebuilt["residual"]["certificate"]["phase_candidates"]["phase_range"]["candidate_count"]
        counts["actual_midpoint_operations"] += rebuilt["polynomial_root_proof"]["midpoint_operations"]
        for event in zeros["events"]:
            counts["G_H_coincident_physical_roots"] += int(event["polynomial_root_id"] is not None and event["residual_event_id"] is not None)
            counts["rational_coordinate_events" if event["coordinate"]["kind"] == "RATIONAL" else "algebraic_isolator_coordinate_events"] += 1
            orders[str(event["physical_order"])] += 1
    result = {"schema": SCHEMA, "status": "ESTABLISHED_BOUNDED_SHARED_SQUARE_SOURCE_CHECKER_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL", "qualified_base_main": BASE_MAIN,
        "input_custody": clone(replay["input_custody"]), "cases": results, "summary": dict(sorted(counts.items())),
        "finite_physical_order_distribution": dict(sorted(orders.items())),
        "supplied_source_contract": {"generic_source_and_full_factor_identity_verified": True,
            "complete_common_polynomial_roots_preserved": True, "actual_qualified_coprime_residual_reproved": True,
            "source_order_is_twice_G_multiplicity_plus_H_order": True, "physical_order_eight_admissible": True,
            "physical_populations_above_thirty_three_admissible": True,
            "algebraic_descriptors_need_no_minimality_or_irrationality_claim": True,
            "whole_closed_interval_including_exteriors_proved": True, "continuum_and_empty_finite_types_distinguished": True,
            "positive_cells_split_at_even_order_touches": True, "residual_raw_input_envelope_unchanged": True,
            "failed_proofs_return_atomic_nontruth": True, "numerical_completeness_authority_used": False},
        "budgets": {"original_input_rational_bits": MAX_INPUT_BITS, "original_input_token_characters": 128,
            "derived_rational_bits_before_arithmetic": MAX_INTERMEDIATE_BITS, "derived_token_characters": MAX_DERIVED_TOKEN,
            "hint_and_polynomial_isolation_degree": MAX_HINT_DEGREE, "original_coefficient_degree": MAX_SOURCE_DEGREE,
            "maximum_residual_half_integer_candidates": MAX_CANDIDATES, "global_midpoint_operations_including_endpoint_cleaning": 128,
            "structural_physical_event_budget": MAX_PHYSICAL_EVENTS, "maximum_physical_order": 8,
            "derived_residual_raw_rational_bits": 128, "report_bytes": MAX_BYTES, "json_value_nodes": MAX_NODES,
            "json_depth": MAX_DEPTH, "residual_may_refuse_valid_original_with_oversized_derived_controls": True},
        "scope": {"all_eight_examples_outside_frozen_fifty_source_cohort": True, "frozen_corpus_additions": 0,
            "historical_route_or_source_completions_claimed": 0, "generic_owner_route_repaired": False,
            "only_qualified_coprime_project_module_executed": True, "MC032_is_nonexecuted_algorithm_reference": True,
            "saved_coprime_report_consumed": False, "legacy_unguarded_root_engine_executed": False,
            "python_and_standard_library_trusted": True, "hostile_python_sandbox_claimed": False, "native_geometry_evidence": False},
        "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN", "PB-007-04": "OPEN",
            "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED", "production_authorized": False,
            "frozen_fifty_source_cohort_unchanged": True, "frozen_121_source_corpus_unchanged": True,
            "historical_20_blocked_and_30_order_gap_dispositions_unchanged": True, "all_26_operations_unchanged": True}}
    bounded_bytes(result)
    return result


def expected_report():
    return _invoke(report_from_replay, _invoke(replay_sources))


def read_report(path=REPORT):
    need(type(path) in (str, type(REPORT)), "Exact bounded report path required", "RESOURCE_REFUSAL")
    value = str(path)
    need(0 < len(value) <= 4096 and "\0" not in value, "Report path text budget", "RESOURCE_REFUSAL")
    return parse_json_bytes(_read_bounded(Path(path), MAX_BYTES))


def _compare_with_replayed_bytes(candidate, expected_bytes):
    need(type(expected_bytes) is bytes and len(expected_bytes) <= MAX_BYTES,
         "Bounded expected report bytes required", "RESOURCE_REFUSAL")
    need(bounded_bytes(candidate) == expected_bytes, "Submitted report differs from fresh complete shared-factor source proofs")
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
        print("PASS: complete original shared-square source roots, orders, exteriors and maximal positive cells")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
