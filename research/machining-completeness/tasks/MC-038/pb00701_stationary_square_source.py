#!/usr/bin/env python3
"""Bounded exact original-source proofs for stationary squared amplitudes.

The original zero rate is retained. Positive stationary weights reduce the
physical zero set to a checked polynomial, with a distinct continuum type.
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
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK_DIR = "research/machining-completeness/tasks/MC-038/"
REPORT = HERE / "pb00701-stationary-square-source.json"
SCHEMA = "radicadsac-mc038-stationary-square-source/1.0"
BASE_MAIN = '61ede6367fde4ea90bc396d4e0dfd14d484c78b3'
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
MAX_MIDPOINT_OPERATIONS = 128
MAX_PHYSICAL_EVENTS = 3
SHARED_MODEL = TASK_DIR + "pb00701_shared_square_source.py"
SHARED_BLOB = 'e445aae10a2a0eab49b4e958d030fa19f0cd3f7a'
COPRIME_MODEL = TASK_DIR + "pb00701_coprime_square_source.py"
COPRIME_BLOB = "4db47f79acff3c036e67ba03dd11b9bfb0a96bdb"
# Assigned from exact qualified dependency buffers before this leaf is executed.
DEPENDENCY_PINS = {'docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md': '6005fc55e2d18e71639e6bc31cfbc1597bf4a915',
 'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
 'research/machining-completeness/tasks/MC-038/pb00701-mtp-irreducible-boundary.json': '4840bbca3847962b537684e0dffa871bd6de82a2',
 'research/machining-completeness/tasks/MC-038/pb00701_coprime_square_source.py': '4db47f79acff3c036e67ba03dd11b9bfb0a96bdb',
 'research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
 'research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py': '4f9000549834c8f9b60ebc9925fadb71e9f96acf',
 'research/machining-completeness/tasks/MC-038/pb00701_shared_square_source.py': 'e445aae10a2a0eab49b4e958d030fa19f0cd3f7a'}
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
  'use': 'EXECUTED_QUALIFIED_CONDITIONAL_POLYNOMIAL_ARITHMETIC'},
 {'bytes': 18701,
  'git_blob': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py',
  'sha256': '2813a99ecc2bc179bf31f6c9166f9c3564516e67f2f256c0a984deee4ed0f692',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 32020,
  'git_blob': '4f9000549834c8f9b60ebc9925fadb71e9f96acf',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py',
  'sha256': '29fb8a0b8ddbece891b31504aa1e661d2471a3a9fea22f1f630d9564da91886d',
  'use': 'PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT'},
 {'bytes': 79017,
  'git_blob': 'e445aae10a2a0eab49b4e958d030fa19f0cd3f7a',
  'path': 'research/machining-completeness/tasks/MC-038/pb00701_shared_square_source.py',
  'sha256': '45f7eac1147edab761d9ba4ff13326373fe152589bbd52801e68959cdf4b48d9',
  'use': 'EXECUTED_QUALIFIED_CONDITIONAL_GCD_STURM_ISOLATION'}]
ZERO, ONE, TWO = Fraction(0), Fraction(1), Fraction(2)


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


def qualified_modules():
    """Capture the complete closure before compiling the exact checked sources."""
    need(len(DEPENDENCY_PINS) == len(INPUT_RECORDS) == 7 and
         DEPENDENCY_PINS.get(SHARED_MODEL) == SHARED_BLOB and
         DEPENDENCY_PINS.get(COPRIME_MODEL) == COPRIME_BLOB,
         "Qualified shared/coprime dependency closure is unavailable")
    buffers, records = {}, []
    for relative, pin in sorted(DEPENDENCY_PINS.items()):
        path = ROOT / relative
        need(path.resolve() == path.absolute(), "Pinned input has a symlink alias")
        limit = MAX_CODE_BYTES if relative in (SHARED_MODEL, COPRIME_MODEL) else MAX_REFERENCE_BYTES
        raw = _read_bounded(path, limit)
        need(git_blob_bytes(raw) == pin, "Pinned dependency drift: " + relative)
        expected = next(row for row in INPUT_RECORDS if row["path"] == relative)
        records.append({"path": relative, "git_blob": pin, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(), "use": expected["use"]})
        buffers[relative] = raw
    need(bounded_bytes(records) == bounded_bytes(INPUT_RECORDS), "Input byte/SHA256 custody changed")
    module = types.ModuleType("_radicadsac_stationary_shared_" + SHARED_BLOB)
    module.__file__ = str(ROOT / SHARED_MODEL)
    module.__package__ = ""
    exec(compile(buffers[SHARED_MODEL], module.__file__, "exec", dont_inherit=True, optimize=0), module.__dict__)
    expected_parent_pins = {key: value for key, value in DEPENDENCY_PINS.items() if key != SHARED_MODEL}
    need(module.DEPENDENCY_PINS == expected_parent_pins and module.COPRIME_BLOB == COPRIME_BLOB,
         "Qualified shared model's complete dependency closure changed")
    retained = {str(ROOT / key): value for key, value in buffers.items() if key != SHARED_MODEL}

    def retained_read(path, limit):
        need(type(limit) is int and 0 <= limit <= MAX_CODE_BYTES,
             "Retained-read budget changed", "RESOURCE_REFUSAL")
        key = str(path)
        need(key in retained, "Shared dependency requested an undeclared input")
        raw = retained[key]
        need(len(raw) <= limit, "Retained input exceeds requested budget", "RESOURCE_REFUSAL")
        return raw

    module._read_bounded = retained_read
    need(module.MAX_MIDPOINT_OPERATIONS == MAX_MIDPOINT_OPERATIONS and
         module.MAX_INTERMEDIATE_BITS == MAX_INTERMEDIATE_BITS and module.MAX_INPUT_BITS == MAX_INPUT_BITS,
         "Qualified conditional arithmetic/isolation envelope changed")
    coprime = _invoke(module.qualified_coprime_module)
    need(coprime._shared_input_custody == module.INPUT_RECORDS,
         "Qualified conditional arithmetic did not retain its complete input custody")
    module._stationary_input_custody = clone(records)
    coprime._stationary_input_custody = clone(records)
    return module, coprime


def _source_preflight(spec):
    """Validate the actual stationary grammar without altering its original rate."""
    bounded_bytes(spec)
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
        "Exact original source fields required")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and 0 < len(spec["source_parameter_id"]) <= 128 and
         "\0" not in spec["source_parameter_id"], "Source grammar or bounded parameter ID invalid")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"0", "1"} and
         type(spec["sin_splines"]) is dict and not spec["sin_splines"],
         "Both explicit cosine channels 0/1 and no sine channels are required")
    tokens = [spec[key] for key in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")]
    for harmonic in ("0", "1"):
        spline = spec["cos_splines"][harmonic]
        need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
             "Exact original spline fields required")
        degree = spline["degree"]
        need(type(degree) is int and 0 <= degree <= MAX_SOURCE_DEGREE,
             "Source degree must be an exact integer in 0..6", "RESOURCE_REFUSAL")
        need(type(spline["controls"]) is list and len(spline["controls"]) == degree+1 and
             type(spline["knots"]) is list and len(spline["knots"]) == 2*(degree+1),
             "One complete fully clamped source span is required")
        tokens.extend(spline["knots"])
        tokens.extend(spline["controls"])
    parts = [rational_parts(token) for token in tokens]
    lo, hi, offset, rate = parts[:4]
    need(lo[0]*hi[1] < hi[0]*lo[1], "Original source interval must have positive length")
    need(abs(lo[0]) <= 2*lo[1] and abs(hi[0]) <= 2*hi[1] and abs(offset[0]) <= 8*offset[1],
         "Original domain/phase range budget", "RESOURCE_REFUSAL")
    need(rate == (0, 1), "This theorem requires the original phase rate exactly zero",
         "UNSUPPORTED_MOVING_PHASE")
    for spline in spec["cos_splines"].values():
        count = spline["degree"]+1
        need(spline["knots"] == [spec["parameter_lo"]]*count + [spec["parameter_hi"]]*count,
             "Original coefficient is not fully clamped on the complete source interval")
    return parts


def _hint_preflight(tokens):
    bounded_bytes(tokens)
    need(type(tokens) is list and 1 <= len(tokens) <= MAX_HINT_DEGREE+1,
         "P/Q coefficient degree budget", "RESOURCE_REFUSAL")
    return [rational_parts(token) for token in tokens]


def _input_preflight(spec, p_coefficients, q_coefficients):
    _source_preflight(spec)
    _hint_preflight(p_coefficients)
    _hint_preflight(q_coefficients)


def lower_stationary_source(c, spec):
    """Lower the complete supplied source in global t with its actual zero rate."""
    _source_preflight(spec)
    lo, hi = c.rational(spec["parameter_lo"]), c.rational(spec["parameter_hi"])
    reciprocal = c._safe(ONE, c._safe(hi, lo, "sub"), "div")
    u = c.poly_scale((-lo, ONE), reciprocal)
    v = c.poly_scale((hi, -ONE), reciprocal)
    result = {"source_sha256": digest(spec), "source_parameter_id": spec["source_parameter_id"],
              "original_source_interval": [str(lo), str(hi)],
              "global_phase_turn_law": {"offset": spec["phase_turn_offset"], "rate": "0"},
              "channels": []}
    for harmonic in ("0", "1"):
        spline = spec["cos_splines"][harmonic]
        degree = spline["degree"]
        controls = tuple(map(c.rational, spline["controls"]))
        basis = [c.poly_scale(c.poly_mul(c.poly_pow(u, i), c.poly_pow(v, degree-i)),
                              c._number(comb(degree, i))) for i in range(degree+1)]
        total, polynomial = (ZERO,), (ZERO,)
        for control, term in zip(controls, basis):
            total = c.poly_add(total, term)
            polynomial = c.poly_add(polynomial, c.poly_scale(term, control))
        need(total == (ONE,), "Original Bernstein basis failed partition of unity")
        result["C"+harmonic] = c.encode_poly(polynomial)
        result["channels"].append({"harmonic": int(harmonic), "degree": degree,
            "original_knots": clone(spline["knots"]), "original_controls": clone(spline["controls"]),
            "bernstein_basis_in_original_parameter": [c.encode_poly(term) for term in basis],
            "global_power_coefficients": c.encode_poly(polynomial), "partition_of_unity_verified": True,
            "left_endpoint_value": str(c.poly_eval(polynomial, lo)),
            "right_endpoint_value": str(c.poly_eval(polynomial, hi))})
        need(c.poly_eval(polynomial, lo) == controls[0] and c.poly_eval(polynomial, hi) == controls[-1],
             "Original clamped endpoints disagree with complete lowering")
    # This conditional coefficient validator has no moving-phase premise and
    # checks the actual source hash/phase, every basis and every original control.
    _invoke(c._verify_lowering, spec, result)
    return result


def _phase_receipt(c, offset):
    b = c.rational(offset)
    integer = b.denominator == 1
    half = b.denominator == 2
    branch = ("INTEGER_COSINE_WEIGHT_ONE" if integer else "ODD_HALF_SINE_WEIGHT_ONE" if half
              else "BOTH_WEIGHTS_STRICTLY_POSITIVE")
    return {"phase_turn_offset": str(b), "phase_turn_rate": "0", "branch": branch,
            "reduced_offset_numerator": str(b.numerator), "reduced_offset_denominator": str(b.denominator),
            "cos_squared_exact_value": "1" if integer else "0" if half else None,
            "sin_squared_exact_value": "0" if integer else "1" if half else None,
            "cos_squared_strictly_positive": not half, "sin_squared_strictly_positive": not integer,
            "both_weights_sum_to_one": True, "floating_angle_tolerance_used": False,
            "noncardinal_weight_field_or_exact_value_required": False}


def classify_stationary_phase(c, offset):
    """Exact reduced-denominator classification; negative phases need no rounding."""
    rational_parts(offset)
    return _phase_receipt(c, offset)


def _verify_phase(c, spec, proof):
    bounded_bytes(proof)
    expected = _phase_receipt(c, spec["phase_turn_offset"])
    need(bounded_bytes(proof) == bounded_bytes(expected), "Stationary phase/weight classification changed")
    return expected["branch"]


def select_stationary_polynomial(s, c, p, q, lowered, phase):
    """Actual active-polynomial or checked common-factor/positive-residual proof."""
    branch = phase["branch"]
    if branch in ("INTEGER_COSINE_WEIGHT_ONE", "ODD_HALF_SINE_WEIGHT_ONE"):
        active = "P" if branch == "INTEGER_COSINE_WEIGHT_ONE" else "Q"
        selected = p if active == "P" else q
        return {"branch": branch, "selection_kind": "ACTIVE_AMPLITUDE", "active_amplitude": active,
                "selected_polynomial": c.encode_poly(selected), "decomposition": None, "residual_bezout": None,
                "original_source_equals_selected_square": True,
                "remaining_factor_strictly_positive": selected != (ZERO,),
                "selected_polynomial_identically_zero": selected == (ZERO,)}
    need(branch == "BOTH_WEIGHTS_STRICTLY_POSITIVE", "Unproved stationary weight branch")
    if p == q == (ZERO,):
        return {"branch": branch, "selection_kind": "BOTH_AMPLITUDES_ZERO", "active_amplitude": None,
                "selected_polynomial": ["0"], "decomposition": None, "residual_bezout": None,
                "original_source_equals_selected_square": True,
                "remaining_factor_strictly_positive": False, "selected_polynomial_identically_zero": True}
    decomposition = _invoke(s.decompose_amplitudes, c, p, q)
    g, p0, q0 = _invoke(s._verify_decomposition, c, p, q, lowered, decomposition)
    bezout = _invoke(c.compute_bezout, p0, q0)
    _invoke(c._verify_bezout, p0, q0, bezout)
    return {"branch": branch, "selection_kind": "COMMON_FACTOR_WITH_POSITIVE_WEIGHTED_RESIDUAL",
            "active_amplitude": None, "selected_polynomial": c.encode_poly(g),
            "decomposition": clone(decomposition), "residual_bezout": clone(bezout),
            "original_source_equals_selected_square": False,
            "remaining_factor_strictly_positive": True, "selected_polynomial_identically_zero": False}


def _verify_selection(s, c, p, q, lowered, phase, proof):
    bounded_bytes(proof)
    fields = {"branch", "selection_kind", "active_amplitude", "selected_polynomial", "decomposition",
              "residual_bezout", "original_source_equals_selected_square", "remaining_factor_strictly_positive",
              "selected_polynomial_identically_zero"}
    need(type(proof) is dict and set(proof) == fields and proof["branch"] == phase["branch"],
         "Selected polynomial fields or exact phase branch changed")
    branch = phase["branch"]
    if branch in ("INTEGER_COSINE_WEIGHT_ONE", "ODD_HALF_SINE_WEIGHT_ONE"):
        active = "P" if branch == "INTEGER_COSINE_WEIGHT_ONE" else "Q"
        selected = p if active == "P" else q
        kind, is_square, positive = "ACTIVE_AMPLITUDE", True, selected != (ZERO,)
        need(proof["decomposition"] is None and proof["residual_bezout"] is None,
             "Inactive amplitude cannot invent common-factor or moving residual authority")
    elif p == q == (ZERO,):
        need(branch == "BOTH_WEIGHTS_STRICTLY_POSITIVE", "Unproved all-zero phase branch")
        selected, active, kind, is_square, positive = (ZERO,), None, "BOTH_AMPLITUDES_ZERO", True, False
        need(proof["decomposition"] is None and proof["residual_bezout"] is None,
             "All-zero source must not invent a finite residual")
    else:
        need(branch == "BOTH_WEIGHTS_STRICTLY_POSITIVE", "Unproved positive-weight phase branch")
        selected, p0, q0 = _invoke(s._verify_decomposition, c, p, q, lowered, proof["decomposition"])
        _invoke(c._verify_bezout, p0, q0, proof["residual_bezout"])
        active, kind, is_square, positive = None, "COMMON_FACTOR_WITH_POSITIVE_WEIGHTED_RESIDUAL", False, True
    need(proof["selection_kind"] == kind and proof["active_amplitude"] == active and
         c.decode_poly(proof["selected_polynomial"], max_degree=MAX_HINT_DEGREE) == selected and
         proof["selected_polynomial"] == c.encode_poly(selected) and
         proof["original_source_equals_selected_square"] is is_square and
         proof["remaining_factor_strictly_positive"] is positive and
         proof["selected_polynomial_identically_zero"] is (selected == (ZERO,)),
         "Physical polynomial/continuum selection does not follow from the actual original amplitudes")
    return selected


def isolate_stationary_polynomial(s, c, selected, lo, hi):
    """Conditional polynomial stage, with no moving carrier or altered source."""
    return _invoke(s.isolate_polynomial_roots, c, selected, lo, hi, [])


def _finite_zero_set(s, c, spec, phase, selected, polynomial_proof):
    lo, hi = c.rational(spec["parameter_lo"]), c.rational(spec["parameter_hi"])
    roots = _invoke(s._verify_isolation, c, selected, lo, hi, [], polynomial_proof)
    need(len(roots) <= MAX_PHYSICAL_EVENTS, "Stationary polynomial root budget", "RESOURCE_REFUSAL")
    source_hash = digest(spec)
    events, previous = [], None
    for index, root in enumerate(roots):
        coordinate = root["coordinate"]
        left, right = _invoke(s._coordinate_bounds, c, coordinate)
        need(lo <= left <= right <= hi, "Polynomial root left the original closed source")
        if previous is not None:
            pl, pr = previous
            need(pr <= left and not (pl == pr == left == right), "Stationary root order/distinctness failed")
        previous = left, right
        at_left, at_right = left == right == lo, left == right == hi
        location = "LEFT_EXTERIOR" if at_left else "RIGHT_EXTERIOR" if at_right else "SPAN_INTERIOR"
        multiplicity = root["multiplicity"]
        need(type(multiplicity) is int and 1 <= multiplicity <= MAX_HINT_DEGREE,
             "Exact selected-polynomial multiplicity required")
        physical_order = 2*multiplicity
        order = ({"kind": "ONE_SIDED", "side": "RIGHT" if at_left else "LEFT", "inward_order": physical_order,
                  "outside_order": None, "global_smooth_multiplicity_claimed": False} if at_left or at_right else
                 {"kind": "SMOOTH", "multiplicity": physical_order})
        events.append({"event_id": "ZERO_"+str(index), "source_sha256": source_hash,
            "source_parameter_id": spec["source_parameter_id"], "coordinate": clone(coordinate),
            "location": location, "source_piece_indices": [0], "classification": "TOUCHING", "order": order,
            "physical_order": physical_order, "polynomial_root_id": root["polynomial_root_id"],
            "polynomial_multiplicity": multiplicity, "stationary_weight_branch": phase["branch"],
            "order_derivation": {"selected_polynomial_multiplicity": multiplicity,
                                 "squared_polynomial_order": physical_order, "remaining_factor_order": 0},
            "moving_carrier_root_order_added": False,
            "left_sign": None if at_left else 1, "right_sign": None if at_right else 1})
    exteriors_by_coordinate = {event["coordinate"]["value"]: event for event in events
                              if event["location"] != "SPAN_INTERIOR"}

    def event_boundary(event):
        return {"kind": "PHYSICAL_ZERO_EVENT", "event_id": event["event_id"], "coordinate": clone(event["coordinate"]),
                "source_sha256": source_hash, "source_parameter_id": spec["source_parameter_id"]}

    def exterior_boundary(point, side):
        event = exteriors_by_coordinate.get(str(point))
        return event_boundary(event) if event else {
            "kind": "SOURCE_EXTERIOR", "side": side, "coordinate": {"kind": "RATIONAL", "value": str(point)},
            "source_sha256": source_hash, "source_parameter_id": spec["source_parameter_id"]}

    boundaries = [exterior_boundary(lo, "LEFT")]
    boundaries += [event_boundary(event) for event in events if event["location"] == "SPAN_INTERIOR"]
    boundaries.append(exterior_boundary(hi, "RIGHT"))
    cells = [{"cell_id": "CELL_"+str(index), "left_boundary": clone(left), "right_boundary": clone(right),
              "left_included": left["kind"] == "SOURCE_EXTERIOR", "right_included": right["kind"] == "SOURCE_EXTERIOR",
              "sign": 1, "source_piece_indices": [0], "crossed_nonzero_source_knots": [],
              "positive_from_selected_square_and_stationary_weight_proof": True}
             for index, (left, right) in enumerate(zip(boundaries, boundaries[1:]))]
    need(len(cells) <= MAX_PHYSICAL_EVENTS+1, "Stationary nonzero component budget", "RESOURCE_REFUSAL")
    exterior_points = []
    for side, point in (("LEFT", lo), ("RIGHT", hi)):
        event = exteriors_by_coordinate.get(str(point))
        exterior_points.append({"side": side, "coordinate": str(point), "phase_turn": spec["phase_turn_offset"],
            "is_zero": event is not None, "event_ref": event["event_id"] if event else None,
            "value_sign": 0 if event else 1, "exact_value": "0" if event else None,
            "nonzero_exact_scalar_value_claimed": False,
            "positive_sign_from_stationary_weight_and_complete_polynomial_proof": event is None,
            "inward_sign": 1, "inward_order": event["physical_order"] if event else 0,
            "outside_sign": None, "outside_order": None, "global_smooth_multiplicity_claimed": False})
    return {"kind": "FINITE_ORIGINAL_SOURCE_ZERO_SET", "complete_for_original_closed_source": True,
            "source_interval": [str(lo), str(hi)], "closed_root_count": len(events), "events": events,
            "source_open_root_count": sum(event["location"] == "SPAN_INTERIOR" for event in events),
            "exterior_root_count": len(exteriors_by_coordinate), "true_source_knots": [],
            "exterior_points": exterior_points, "maximal_nonzero_cells": cells,
            "finite_event_list_applicable": True, "nonzero_sign_cells_applicable": True,
            "all_physical_roots_have_even_order": True, "nonzero_source_points_strictly_positive": True,
            "continuum_excluded_by_nonzero_selected_polynomial": True,
            "global_cross_source_zero_deduplication_performed": False,
            "isolator_endpoints_substituted_for_physical_root_boundaries": False}


def assemble_stationary_zero_set(s, c, spec, phase, selected, polynomial_proof):
    return _finite_zero_set(s, c, spec, phase, selected, polynomial_proof)


def _continuum(spec, phase, selection):
    return {"kind": "CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET", "complete_for_original_closed_source": True,
            "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
            "zero_interval": {"interval": [spec["parameter_lo"], spec["parameter_hi"]],
                              "left_included": True, "right_included": True},
            "original_source_identically_zero": True, "stationary_weight_branch": phase["branch"],
            "identity_selection_kind": selection["selection_kind"],
            "inactive_amplitude_may_be_nonzero": selection["selection_kind"] == "ACTIVE_AMPLITUDE",
            "closed_root_count": None, "events": None, "source_open_root_count": None,
            "exterior_root_count": None, "true_source_knots": [],
            "exterior_points": [{"side": side, "coordinate": spec[key], "is_zero": True, "exact_value": "0",
                                 "isolated_root_order": None, "outside_sign": None, "outside_order": None}
                                for side, key in (("LEFT", "parameter_lo"), ("RIGHT", "parameter_hi"))],
            "maximal_nonzero_cells": None, "finite_event_list_applicable": False,
            "nonzero_sign_cells_applicable": False, "finite_root_cardinality_claimed": False,
            "polynomial_isolator_applicable": False, "moving_source_producer_called": False}


def _assemble_certificate(s, c, spec, p_coefficients, q_coefficients, lowered, phase,
                          selection, polynomial_proof, zero_set, custody):
    _input_preflight(spec, p_coefficients, q_coefficients)
    need(bounded_bytes(custody) == bounded_bytes(INPUT_RECORDS), "Complete dependency custody changed")
    p = c.decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = c.decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    identity = _invoke(c._source_identity, spec, p, q, lowered)
    _verify_phase(c, spec, phase)
    selected = _verify_selection(s, c, p, q, lowered, phase, selection)
    continuum = selected == (ZERO,)
    if continuum:
        need(polynomial_proof is None, "Continuum cannot carry a finite polynomial root certificate")
        rebuilt = _continuum(spec, phase, selection)
    else:
        rebuilt = _finite_zero_set(s, c, spec, phase, selected, polynomial_proof)
    need(bounded_bytes(zero_set) == bounded_bytes(rebuilt),
         "Stationary physical zero set does not follow from the actual complete source/phase/polynomial proof")
    supplied = {"P": clone(p_coefficients), "Q": clone(q_coefficients)}
    result = {"schema": SCHEMA+"/certificate", "status": "ESTABLISHED_STATIONARY_SQUARE_ORIGINAL_SOURCE",
        "proof_established": True, "source_zero_set_established": True, "evidence_class": "DETERMINISTIC_MODEL",
        "original_source": clone(spec), "source_sha256": digest(spec), "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
        "phase_turn_law": {"offset": spec["phase_turn_offset"], "rate": "0"},
        "supplied_witness": supplied, "witness_sha256": digest(supplied),
        "normalized_witness": {"P": c.encode_poly(p), "Q": c.encode_poly(q)},
        "whole_source_lowering": clone(lowered), "source_identity": clone(identity),
        "stationary_phase_proof": clone(phase), "stationary_polynomial_selection": clone(selection),
        "polynomial_root_proof": clone(polynomial_proof), "source_zero_set": rebuilt,
        "input_custody": clone(custody),
        "theorem_premises": {"complete_original_coefficients_equal_supplied_square_sum": True,
            "actual_original_rate_is_zero": True, "stationary_weights_classified_exactly": True,
            "finite_roots_equal_selected_polynomial_roots": not continuum,
            "physical_order_is_twice_polynomial_multiplicity": not continuum,
            "zero_active_polynomial_gives_closed_continuum": continuum,
            "inactive_amplitude_remains_bound_by_full_source_identity": True,
            "moving_carrier_order_added": False, "moving_source_certifier_used": False,
            "numerical_samples_or_saved_reports_used_as_completeness_authority": False,
            "exact_noncardinal_trig_weight_field_required": False,
            "pi_irrationality_or_transcendence_used": False},
        "scope": {"generic_supplied_source_and_witness_checked": True,
            "fixture_allowlist_used_for_admission": False, "one_original_clamped_span": True,
            "valid_degree_elevation_admitted": True, "original_parameter_and_zero_rate_preserved": True,
            "legacy_quarter_turn_stationary_overlap_acknowledged": True,
            "algebraic_descriptors_do_not_claim_minimality_or_irrationality": True,
            "only_conditional_polynomial_stages_reused": True,
            "derived_residual_source_or_raw_control_conversion_required": False,
            "frozen_corpus_addition": False, "historical_source_completion_claimed": False,
            "generic_owner_route_repaired": False, "native_geometry_evidence": False},
        "production_authorized": False}
    bounded_bytes(result)
    return result


def _certify_source(s, c, spec, p_coefficients, q_coefficients):
    _input_preflight(spec, p_coefficients, q_coefficients)
    p = c.decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = c.decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    lowered = _invoke(lower_stationary_source, c, spec)
    _invoke(c._source_identity, spec, p, q, lowered)
    phase = _invoke(classify_stationary_phase, c, spec["phase_turn_offset"])
    _verify_phase(c, spec, phase)
    selection = _invoke(select_stationary_polynomial, s, c, p, q, lowered, phase)
    selected = _verify_selection(s, c, p, q, lowered, phase, selection)
    if selected == (ZERO,):
        polynomial_proof = None
        zero_set = _continuum(spec, phase, selection)
    else:
        lo, hi = c.rational(spec["parameter_lo"]), c.rational(spec["parameter_hi"])
        polynomial_proof = _invoke(isolate_stationary_polynomial, s, c, selected, lo, hi)
        _invoke(s._verify_isolation, c, selected, lo, hi, [], polynomial_proof)
        zero_set = _invoke(assemble_stationary_zero_set, s, c, spec, phase, selected, polynomial_proof)
    return _assemble_certificate(s, c, spec, p_coefficients, q_coefficients, lowered, phase,
                                 selection, polynomial_proof, zero_set, s._stationary_input_custody)


def certify_source(spec, p_coefficients, q_coefficients):
    _input_preflight(spec, p_coefficients, q_coefficients)
    s, c = _invoke(qualified_modules)
    return _invoke(_certify_source, s, c, spec, p_coefficients, q_coefficients)


def check_source(spec, p_coefficients, q_coefficients):
    try:
        return _invoke(certify_source, spec, p_coefficients, q_coefficients)
    except Refusal as error:
        return error.as_record()


def validate_certificate(spec, p_coefficients, q_coefficients, candidate):
    _input_preflight(spec, p_coefficients, q_coefficients)
    candidate_bytes = bounded_bytes(candidate)
    expected = _invoke(certify_source, spec, p_coefficients, q_coefficients)
    need(candidate_bytes == bounded_bytes(expected), "Certificate changed from the fresh actual stationary-source proof")
    return {"valid": True, "source_sha256": expected["source_sha256"], "scope": "FRESH_ORIGINAL_STATIONARY_SOURCE"}


def _fixture_preflight(p, q, lo, hi, offset, rate, parameter, degrees):
    _hint_preflight(p)
    _hint_preflight(q)
    parts = [rational_parts(token) for token in (lo, hi, offset, rate)]
    need(parts[3] == (0, 1), "Stationary fixture must retain an exact zero original rate", "UNSUPPORTED_MOVING_PHASE")
    need(type(parameter) is str and 0 < len(parameter) <= 128 and "\0" not in parameter,
         "Bounded original source parameter ID required")
    if degrees is not None:
        need(type(degrees) in (tuple, list) and len(degrees) == 2 and
             all(type(value) is int and 0 <= value <= MAX_SOURCE_DEGREE for value in degrees),
             "Two exact bounded source degrees required", "RESOURCE_REFUSAL")


def _source_from_polynomials(c, p_coefficients, q_coefficients, lo, hi, offset, rate, parameter, *, degrees=None):
    """Fixture construction in the actual stationary source, not admission authority."""
    _fixture_preflight(p_coefficients, q_coefficients, lo, hi, offset, rate, parameter, degrees)
    p = c.decode_poly(p_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    q = c.decode_poly(q_coefficients, max_degree=MAX_HINT_DEGREE, derived=False)
    low, high = c.rational(lo), c.rational(hi)
    width = c._safe(high, low, "sub")
    need(width > ZERO, "Stationary fixture interval must have positive length")
    p2, q2 = c.poly_mul(p, p), c.poly_mul(q, q)
    half = c._safe(ONE, TWO, "div")
    coefficients = (c.poly_scale(c.poly_add(p2, q2), half), c.poly_scale(c.poly_sub(p2, q2), half))
    splines = {}
    for harmonic, polynomial in enumerate(coefficients):
        natural_degree = max(0, c._degree(polynomial))
        degree = natural_degree if degrees is None else degrees[harmonic]
        need(natural_degree <= degree <= MAX_SOURCE_DEGREE, "Requested source degree cannot represent the amplitude")
        local = (ZERO,)
        for power, coefficient in enumerate(polynomial):
            local = c.poly_add(local, c.poly_scale(c.poly_pow((low, width), power), coefficient))
        controls = []
        for i in range(degree+1):
            control = ZERO
            for k in range(min(i, len(local)-1)+1):
                factor = c._safe(c._number(comb(i, k)), c._number(comb(degree, k)), "div")
                control = c._safe(control, c._safe(local[k], factor, "mul"), "add")
            controls.append(str(control))
        splines[str(harmonic)] = {"degree": degree, "knots": [lo]*(degree+1)+[hi]*(degree+1), "controls": controls}
    spec = {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE", "source_parameter_id": parameter,
            "parameter_lo": lo, "parameter_hi": hi, "phase_turn_offset": offset, "phase_turn_rate": rate,
            "cos_splines": splines, "sin_splines": {}}
    _input_preflight(spec, p_coefficients, q_coefficients)
    return spec


def source_from_polynomials(p_coefficients, q_coefficients, lo, hi, offset, rate, source_parameter_id, *, degrees=None):
    _fixture_preflight(p_coefficients, q_coefficients, lo, hi, offset, rate, source_parameter_id, degrees)
    _, c = _invoke(qualified_modules)
    return _invoke(_source_from_polynomials, c, p_coefficients, q_coefficients, lo, hi, offset, rate,
                   source_parameter_id, degrees=degrees)


def _default_cases(c):
    rows = [
        ("integer_active_polynomial", "Integer phase retains only P's physical roots", ["-1/3", "1"], ["1"], "0", "1", "0"),
        ("half_integer_active_polynomial", "Odd half-integer phase retains only Q's physical roots", ["1"], ["-1/2", "1"], "0", "1", "1/2"),
        ("positive_weights_algebraic_roots", "General rational phase with two exact algebraic-format roots", ["-1/2", "0", "1"], ["-1/2", "0", "1"], "-1", "1", "1/5"),
        ("positive_weights_repeated_common_root", "Stationary common-factor order four without a moving contribution", ["-1", "3", "-3", "1"], ["1", "-2", "1"], "1/2", "3/2", "1/3"),
        ("positive_weights_disjoint_amplitudes", "Separate amplitude zeros are not physical zeros", ["-1/3", "1"], ["-2/3", "1"], "0", "1", "1/5"),
        ("integer_inactive_amplitude_continuum", "Nonzero Q and nonzero original channels cancel at integer phase", ["0"], ["1"], "0", "1", "2"),
        ("negative_half_inactive_amplitude_continuum", "Nonzero P and original channels cancel at negative half-integer phase", ["1"], ["0"], "0", "1", "-1/2"),
        ("positive_weights_both_zero_continuum", "Both original amplitudes vanish identically", ["0"], ["0"], "0", "1", "-1/3"),
    ]
    return [{"case_id": case_id, "description": description, "P": clone(p), "Q": clone(q),
             "spec": _source_from_polynomials(c, p, q, lo, hi, offset, "0", "stationary-square:"+case_id)}
            for case_id, description, p, q, lo, hi, offset in rows]


def default_cases():
    _, c = _invoke(qualified_modules)
    return _invoke(_default_cases, c)


def replay_sources():
    s, c = _invoke(qualified_modules)
    cases = []
    for case in _default_cases(c):
        certificate = _invoke(_certify_source, s, c, case["spec"], case["P"], case["Q"])
        cases.append({**clone(case), "certificate": certificate})
    return {"input_custody": clone(s._stationary_input_custody), "cases": cases}


def _report_from_replay(replay):
    bounded_bytes(replay)
    need(type(replay) is dict and set(replay) == {"input_custody", "cases"},
         "Complete stationary replay fields required")
    s, c = _invoke(qualified_modules)
    need(bounded_bytes(replay["input_custody"]) == bounded_bytes(s._stationary_input_custody),
         "Retained stationary replay input custody changed")
    expected_cases = _default_cases(c)
    need(type(replay["cases"]) is list and len(replay["cases"]) == len(expected_cases),
         "Default stationary demonstration population changed")
    rows, finite, continua, phase_counts = [], [], [], Counter()
    for row, expected_case in zip(replay["cases"], expected_cases):
        need(type(row) is dict and set(row) == set(expected_case) | {"certificate"},
             "Actual demonstration input/certificate fields required")
        need(bounded_bytes({key: row[key] for key in expected_case}) == bounded_bytes(expected_case),
             "Default original source, phase, parameter or hints changed")
        certificate = row["certificate"]
        need(type(certificate) is dict, "Actual stationary source proof is missing")
        rebuilt = _assemble_certificate(s, c, row["spec"], row["P"], row["Q"],
            certificate["whole_source_lowering"], certificate["stationary_phase_proof"],
            certificate["stationary_polynomial_selection"], certificate["polynomial_root_proof"],
            certificate["source_zero_set"], certificate["input_custody"])
        need(bounded_bytes(certificate) == bounded_bytes(rebuilt),
             "Retained certificate changed from its actual source and stationary proof premises")
        rows.append({**clone(expected_case), "certificate": rebuilt})
        phase_counts[rebuilt["stationary_phase_proof"]["branch"]] += 1
        zero_set = rebuilt["source_zero_set"]
        (continua if zero_set["kind"] == "CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET" else finite).append(zero_set)
    events = [event for zeros in finite for event in zeros["events"]]
    result = {"schema": SCHEMA, "status": "ESTABLISHED_BOUNDED_STATIONARY_SQUARE_SOURCE_CLASS",
        "evidence_class": "DETERMINISTIC_MODEL", "qualified_base_main": BASE_MAIN,
        "scope": {"generic_supplied_source_checker": True, "default_examples_are_not_admission_allowlist": True,
            "new_historical_original_source_completions": 0, "frozen_fifty_source_cohort_changed": False,
            "frozen_121_source_corpus_changed": False, "legacy_quarter_turn_stationary_overlap_acknowledged": True,
            "general_stationary_harmonic_algebra_established": False, "generic_analytic_route_repaired": False,
            "native_or_paid_campaign_run": False, "production_authorized": False},
        "supplied_source_contract": {"formula": "P^2*cos(pi*b)^2 + Q^2*sin(pi*b)^2",
            "original_phase_rate": "0", "integer_phase": "F=P^2; zero P gives a closed continuum",
            "odd_half_integer_phase": "F=Q^2; zero Q gives a closed continuum",
            "both_weights_strictly_positive": "Physical roots are the checked common polynomial roots; both-zero amplitudes give a continuum",
            "finite_root_order": "twice selected polynomial multiplicity; no moving-carrier order",
            "inactive_amplitudes_still_bound_by_complete_original_source_identity": True,
            "nonzero_component_sign": 1, "constant_weight_exact_value_or_algebraic_field_required": False,
            "moving_public_source_certifier_called": False, "derived_residual_source_constructed": False},
        "executed_byte_custody": {"inputs": clone(replay["input_custody"]),
            "executed_project_modules": [SHARED_MODEL, COPRIME_MODEL],
            "shared_model_git_blob": SHARED_BLOB, "coprime_model_git_blob": COPRIME_BLOB,
            "captured_before_project_execution": True, "compiled_exact_checked_buffers": True,
            "transitive_reads_from_same_retained_buffers": True, "stale_bytecode_or_preloads_used": False,
            "saved_moving_report_replayed": False, "python_and_standard_library_trusted": True,
            "hostile_python_sandbox_claimed": False},
        "budgets": {"raw_rational_operand_bits": MAX_INPUT_BITS,
            "derived_pre_operation_rational_bits": MAX_INTERMEDIATE_BITS,
            "hint_degree": MAX_HINT_DEGREE, "source_degree": MAX_SOURCE_DEGREE,
            "original_endpoint_absolute_value": "2", "phase_offset_absolute_value": "8",
            "phase_rate": "0", "maximum_physical_events": MAX_PHYSICAL_EVENTS,
            "maximum_positive_components": MAX_PHYSICAL_EVENTS+1,
            "global_midpoint_operations": MAX_MIDPOINT_OPERATIONS,
            "json_bytes": MAX_BYTES, "json_nodes": MAX_NODES, "json_depth": MAX_DEPTH},
        "summary": {"original_research_sources": len(rows), "finite_sources": len(finite),
            "closed_continuum_sources": len(continua), "per_source_closed_physical_roots": len(events),
            "original_exterior_roots": sum(zeros["exterior_root_count"] for zeros in finite),
            "strict_source_interior_roots": sum(zeros["source_open_root_count"] for zeros in finite),
            "root_free_finite_sources": sum(not zeros["events"] for zeros in finite),
            "maximal_positive_nonzero_cells": sum(len(zeros["maximal_nonzero_cells"]) for zeros in finite),
            "rational_root_coordinates": sum(event["coordinate"]["kind"] == "RATIONAL" for event in events),
            "algebraic_format_root_coordinates": sum(event["coordinate"]["kind"] == "REAL_ALGEBRAIC_ISOLATOR" for event in events),
            "physical_order_histogram": {str(order): sum(event["physical_order"] == order for event in events)
                                         for order in sorted({event["physical_order"] for event in events})},
            "stationary_weight_branches": dict(sorted(phase_counts.items()))},
        "cases": rows,
        "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN", "PB-007-04": "OPEN",
                  "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED", "production_authorized": False,
                  "required_operation_count": 26}}
    bounded_bytes(result)
    return result


def report_from_replay(replay):
    return _invoke(_report_from_replay, replay)


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
    need(bounded_bytes(candidate) == expected_bytes, "Submitted report differs from fresh complete stationary-source proofs")
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
        raw = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True)+"\n").encode("ascii")
        need(len(raw) <= MAX_BYTES, "Pretty report file byte budget", "RESOURCE_REFUSAL")
        REPORT.write_bytes(raw)
    if options.contract:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(result))
        print("PASS: complete original stationary sources have checked polynomial roots or typed closed continua")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
