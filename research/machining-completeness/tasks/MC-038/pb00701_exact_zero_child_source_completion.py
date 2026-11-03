#!/usr/bin/env python3
"""Complete three pinned sources with exact zeros refused by a transverse engine.

Whole-source derivative/sign arguments supply completeness; the unchanged
rational-phase point primitive supplies exact local zero and sided-jet evidence.
Two physical knot zeros have unequal sided derivatives and no globally smooth
multiplicity claim. Only bounded, byte-matched original rows reach old parsers.
"""
from __future__ import annotations

import argparse
import builtins
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK = "research/machining-completeness/tasks/MC-038/"
SCHEMA = "radicadsac-mc038-exact-zero-child-source-completion/1.0"
REPORT = HERE / "pb00701-exact-zero-child-source-completion-witness.json"
BASE_MAIN = "e0514500aeca59afa4924dcc2da3ca0c2688d9ac"
MAX_DEPENDENCY_BYTES = 1024 * 1024

PINS = {
    TASK + "pb00701_post_v54_evidence_reconciliation.py":
        "33efd291bdd9265ca6ecce7124a46f2a003b59f1",
    TASK + "pb00701-post-v54-evidence-reconciliation.json":
        "9f62dd6edc37206317eec054b2969bade02d7728",
    TASK + "pb00701_coupled_bspline_model.py":
        "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    TASK + "pb00701_rational_turn_model.py":
        "a1316ff0f71b2d7aa80807843a74fd8280779cb2",
    TASK + "pb00701_event_model.py":
        "104c0e7a459cd7da5025853b246faff244a5948e",
    TASK + "pb00701_transverse_trig_interval.py":
        "2320f92efe4316d865a89f6d848737e2c000ca4d",
    TASK + "pb00701_rational_phase_point.py":
        "9fc344e045fa800fb24d30902a641e534a1e197b",
    "research/machining-completeness/tasks/MC-032/event_engine.py":
        "789a709c5141479a343035d1b7055dd4e53534e1",
    TASK + "pb00701-finite-owner-corpus-v54.json":
        "5841c331579489b25caef38cd412bdbf286f9134",
    TASK + "pb00701-finite-owner-inventory-v54.json":
        "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    TASK + "pb00701-finite-owner-coverage-v54.json":
        "600ba29786f50397f29fd435fc5e2c57076088f9",
    TASK + "verify_pb00701_post_v54_frontier.py":
        "12c6efeb667a954ffc5a7e27849ae815d466580a",
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/programme-v1.json":
        "dee7045a1790b2870744df8ae7693429bd1d81a6",
    "handoffs/current-authority.json":
        "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}


def _pinned_bytes(path, expected):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_DEPENDENCY_BYTES + 1)
    if len(raw) > MAX_DEPENDENCY_BYTES:
        raise ValueError("RESOURCE_REFUSAL: dependency byte budget")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != expected:
        raise ValueError("PINNED_DEPENDENCY_DRIFT: " + str(path))
    return raw


def pin_dependencies():
    for name, expected in PINS.items():
        _pinned_bytes(ROOT / name, expected)


class _PinnedRuntime:
    """Finite private project-module graph, compiled from verified byte buffers.

    Repository imports and the event engine's dynamic import resolve only to
    this graph. Python caches and preloaded project modules are never read.
    Standard-library imports retain the ordinary interpreter trust boundary.
    """
    def __init__(self, root, pins):
        self.paths = {str((Path(root) / name).resolve()): expected
                      for name, expected in pins.items() if name.endswith(".py")}
        self.names = {Path(path).stem: path for path in self.paths}
        if len(self.names) != len(self.paths):
            raise ValueError("AMBIGUOUS_PINNED_MODULE_NAME")
        self.modules = {}
        self.loading = set()
        self.local_sys = types.SimpleNamespace(**vars(sys))
        self.local_sys.path = list(sys.path)
        self.importlib = types.SimpleNamespace(util=types.SimpleNamespace(
            spec_from_file_location=self._spec,
            module_from_spec=lambda spec: self.load(spec.origin)))

    def _spec(self, name, path):
        resolved = str(Path(path).resolve())
        if resolved not in self.paths:
            raise ValueError("UNPINNED_DYNAMIC_MODULE")

        def checked_execution(module):
            if module is not self.load(resolved):
                raise ValueError("PINNED_DYNAMIC_MODULE_IDENTITY_CHANGED")

        return types.SimpleNamespace(name=name, origin=resolved,
                                     loader=types.SimpleNamespace(exec_module=checked_execution))

    def _import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if level:
            raise ValueError("UNREVIEWED_RELATIVE_PROJECT_IMPORT")
        if name in self.names:
            return self.load(self.names[name])
        if name == "importlib.util":
            if fromlist:
                raise ValueError("UNREVIEWED_IMPORTLIB_INTERFACE")
            return self.importlib
        if name == "sys":
            return self.local_sys
        if name.startswith(("pb00701_", "verify_pb00701_")) or name == "event_engine":
            raise ValueError("UNPINNED_PROJECT_MODULE")
        return builtins.__import__(name, globals, locals, fromlist, level)

    def load(self, path):
        resolved = str(Path(path).resolve())
        if resolved not in self.paths:
            raise ValueError("UNPINNED_PROJECT_MODULE")
        if resolved in self.modules:
            return self.modules[resolved]
        if resolved in self.loading:
            raise ValueError("UNREVIEWED_CYCLIC_PROJECT_IMPORT")
        raw = _pinned_bytes(resolved, self.paths[resolved])
        module = types.ModuleType("exact_zero_private_" + Path(resolved).stem)
        module.__file__ = resolved
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=self._import)
        self.loading.add(resolved)
        try:
            exec(compile(raw, resolved, "exec"), module.__dict__)
        finally:
            self.loading.remove(resolved)
        self.modules[resolved] = module
        return module


pin_dependencies()
_runtime = _PinnedRuntime(ROOT, PINS)
guards = _runtime.load(HERE / "pb00701_post_v54_evidence_reconciliation.py")
lower = _runtime.load(HERE / "pb00701_coupled_bspline_model.py")
interval = _runtime.load(HERE / "pb00701_transverse_trig_interval.py")
point = _runtime.load(HERE / "pb00701_rational_phase_point.py")
auditor = _runtime.load(HERE / "verify_pb00701_post_v54_frontier.py")

Refusal = guards.Refusal
need = guards.need


def _decode_json(raw):
    need(type(raw) is bytes and len(raw) <= guards.MAX_BYTES,
         "RESOURCE_REFUSAL: JSON byte budget")

    def exact_integer(token):
        need(len(token) <= 78, "RESOURCE_REFUSAL: JSON integer digits")
        value = int(token)
        need(value.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer bits")
        return value

    def nonexact(_):
        raise Refusal("NONEXACT_JSON_SCALAR")

    try:
        value = json.loads(raw, object_pairs_hook=guards.unique_pairs,
                           parse_int=exact_integer, parse_float=nonexact,
                           parse_constant=nonexact)
    except (RecursionError, ValueError, UnicodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    guards.bounded_bytes(value)
    return value


def _pinned_json(path):
    resolved = Path(path).resolve()
    allowed = {(ROOT / name).resolve(): sha for name, sha in PINS.items()
               if name.endswith(".json")}
    need(resolved in allowed, "UNPINNED_JSON_INPUT")
    return _decode_json(_pinned_bytes(resolved, allowed[resolved]))


def _original_corpus():
    corpus, inventory, coverage = [_pinned_json(HERE / name) for name in (
        "pb00701-finite-owner-corpus-v54.json", "pb00701-finite-owner-inventory-v54.json",
        "pb00701-finite-owner-coverage-v54.json")]
    census = auditor.audit(corpus, inventory, coverage)
    need(census["cases"] == 121 and census["v54_dispositions"]["BLOCKED"] == 20
         and census["v54_dispositions"][guards.ORDER_GAP] == 30,
         "HISTORICAL_121_20_30_DENOMINATOR_CHANGED")
    auth = _pinned_json(ROOT / "handoffs/current-authority.json")
    programme = _pinned_json(ROOT / "research/machining-completeness/programme-v1.json")
    domain = _pinned_json(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
    need(auth["capability_status"] == programme["capability_status"] == "NOT_ESTABLISHED"
         and auth["production_authorized"] is False
         and programme["production_authorized"] is False,
         "PROGRAMME_AUTHORITY_PROMOTION")
    need({g["id"]: g["state"] for g in programme["gates"]}["MC-B"] == "NOT_ESTABLISHED",
         "MC_B_PROMOTION")
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "MACHINING_DOMAIN_CHANGED")
    indexed = {row["id"]: row for row in corpus["cases"]}
    need(len(indexed) == 121, "DUPLICATE_ORIGINAL_SOURCE_ID")
    return indexed

SOURCES = {
    "v23": {
        "id": "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0",
        "source_sha256": "e8d2451833854ee7eaf73d4fb70b78b86ba72194b2688876f3bb9ee6ab132ffd",
        "row_sha256": "e52a27e5c3dcdf984919cdcd7bb925c52d2865550035da357cd87178b9fbfc89",
    },
    "v25": {
        "id": "composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0",
        "source_sha256": "d7bf5969875c5ae44fa83f80d217fe17b02aca4db58545dc943c43e744ef68b6",
        "row_sha256": "90642204b36339c0bea36a1196c4b1045f4b0fa360d25493eb59b23881579ab8",
    },
    "v40": {
        "id": "composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0",
        "source_sha256": "90a5df370094bcd8cef37be171f9bb12264c15a32237300b5435dc8871c6c2bf",
        "row_sha256": "8291b11b51d2109451ba852185bf6d9504c9d7e46473bf01be5924508ded5fad",
    },
}
CASE_IDS = tuple(v["id"] for v in SOURCES.values())


def check_module_locations():
    modules = ((guards, HERE / "pb00701_post_v54_evidence_reconciliation.py"),
               (lower, HERE / "pb00701_coupled_bspline_model.py"),
               (interval, HERE / "pb00701_transverse_trig_interval.py"),
               (point, HERE / "pb00701_rational_phase_point.py"),
               (lower.v6, HERE / "pb00701_rational_turn_model.py"),
               (lower.v6.base, HERE / "pb00701_event_model.py"),
               (lower.EE, ROOT / "research/machining-completeness/tasks/MC-032/event_engine.py"),
               (point.interval, HERE / "pb00701_transverse_trig_interval.py"),
               (auditor, HERE / "verify_pb00701_post_v54_frontier.py"))
    for module, expected in modules:
        need(Path(module.__file__).resolve() == expected.resolve(),
             "IMPORTED_DEPENDENCY_PATH_CHANGED")
    need(point.interval is interval, "POINT_INTERVAL_RUNTIME_IDENTITY_CHANGED")


def original_rows():
    pin_dependencies()
    check_module_locations()
    indexed = _original_corpus()
    prior = _pinned_json(HERE / "pb00701-post-v54-evidence-reconciliation.json")
    receipts = {r["case_id"]: r for r in prior["source_cases"]}
    rows = {}
    for label, source in SOURCES.items():
        row = indexed[source["id"]]
        need(guards.digest(row["spec"]) == source["source_sha256"] and
             guards.digest(row) == source["row_sha256"], "ORIGINAL_SOURCE_OR_ROW_DRIFT")
        receipt = receipts[row["id"]]
        need(receipt["registered_evidence_level"] == guards.CHILD and
             receipt["source_sha256"] == source["source_sha256"] and
             receipt["original_row_sha256"] == source["row_sha256"],
             "PRIOR_PARTIAL_CHILD_BINDING_CHANGED")
        need(row["expected"]["v54_disposition"] == guards.ORDER_GAP,
             "HISTORICAL_ORDERED_PREMISE_DISPOSITION_CHANGED")
        rows[label] = row
    return rows


def check_original(candidate):
    packed = guards.bounded_bytes(candidate)
    need(type(candidate) is dict and candidate.get("id") in CASE_IDS,
         "UNSUPPORTED_ORIGINAL_SOURCE")
    for label, original in original_rows().items():
        if candidate["id"] == original["id"]:
            need(packed == guards.bounded_bytes(original), "ORIGINAL_SOURCE_RECORD_CHANGED")
            return label, original
    raise Refusal("ORIGINAL_SOURCE_NOT_FOUND")


def _trim(values):
    values = tuple(values)
    while len(values) > 1 and values[-1] == 0:
        values = values[:-1]
    return values


def _normal_terms(terms):
    return {h: (_trim(p), _trim(q)) for h, (p, q) in terms.items()}


def lower_original(row):
    """Only exact byte-matched original data reaches the legacy source parser."""
    label, original = check_original(row)
    source = original["spec"]
    cos = lower._normalise_harmonic_splines(source["cos_splines"], "cos_splines")
    sin = lower._normalise_harmonic_splines(source["sin_splines"], "sin_splines")
    edges = lower._master_boundaries(list(cos.values()) + list(sin.values()),
                                    Q(source["parameter_lo"]), Q(source["parameter_hi"]))
    need(edges == [Q(0), Q(1), Q(2)], "ACTUAL_SOURCE_PIECE_COVERAGE_CHANGED")
    spans = []
    for left, right in zip(edges, edges[1:]):
        terms = {}
        for harmonic in sorted(set(cos) | set(sin)):
            cp = lower._piece_from_normal(cos[harmonic], left, right)["coefficients"] \
                if harmonic in cos else (Q(0),)
            sp = lower._piece_from_normal(sin[harmonic], left, right)["coefficients"] \
                if harmonic in sin else (Q(0),)
            terms[int(harmonic)] = (cp, sp)
        spans.append(interval.Span(left, right, source["phase_turn_offset"],
                                   source["phase_turn_rate"], _normal_terms(terms)))
    require_continuous_pair(spans)
    _require_analytic_identities(label, spans)
    return label, original, spans


def require_continuous_pair(spans):
    need(type(spans) is list and len(spans) == 2 and
         all(type(s) is interval.Span for s in spans), "TWO_ORIGINAL_SPANS_REQUIRED")
    left, right = spans
    need((left.left, left.right, right.left, right.right) == (0, 1, 1, 2),
         "ORIGINAL_SOURCE_GAP_OR_OVERLAP")
    need((left.offset, left.rate) == (right.offset, right.rate),
         "ORIGINAL_SOURCE_PHASE_MISMATCH")
    need(set(left.terms) == set(right.terms), "ORIGINAL_SOURCE_CHANNEL_MISMATCH")
    for h in left.terms:
        for side in (0, 1):
            need(interval.polynomial(left.terms[h][side], Q(1)) ==
                 interval.polynomial(right.terms[h][side], Q(1)),
                 "ORIGINAL_SOURCE_COEFFICIENT_DISCONTINUITY")


def _require_analytic_identities(label, spans):
    z = (Q(0),)
    if label == "v23":
        e = Q(1, 1000)
        phase = (Q(0), Q(1, 12))
        first = {0: ((Q(-501, 1000),), z), 1: (z, (Q(1), e)),
                 2: ((Q(0), e), z)}
        second = {0: ((Q(-501, 1000),), z), 1: (z, (1 + e,)), 2: ((e,), z)}
    elif label == "v25":
        e = Q(1, 1000)
        phase = (Q(-1, 12), Q(1, 12))
        first = {0: ((Q(-51, 1000),), z),
                 1: ((Q(-1, 20), Q(1, 10)), (Q(4),)), 2: ((e,), z)}
        second = {0: ((Q(-51, 1000),), z),
                  1: ((Q(1, 20),), (Q(4),)), 2: ((e,), z)}
    elif label == "v40":
        e = Q(1, 100000000)
        phase = (Q(1, 16), Q(1, 8))
        first = {0: (z, z),
                 1: ((Q(19, 20), Q(1, 10)), (Q(-21, 20), Q(1, 10))),
                 2: ((-e,), z)}
        second = {0: (z, z), 1: ((Q(21, 20),), (Q(-19, 20),)), 2: ((-e,), z)}
    else:
        raise Refusal("UNSUPPORTED_ANALYTIC_IDENTITY")
    for span, expected in zip(spans, (first, second)):
        need((span.offset, span.rate) == phase and
             _normal_terms(span.terms) == _normal_terms(expected),
             "ORIGINAL_ANALYTIC_FACTOR_OR_PHASE_IDENTITY_FAILED")


def _bounded_q(value):
    need(type(value) is Q and max(value.numerator.bit_length(),
                                 value.denominator.bit_length()) <= 128,
         "BOUNDED_FORMAL_RATIONAL_REQUIRED")
    return value


def v23_derivative_lower(epsilon):
    """Conditional sector lemma: omega=pi/6, cos>=1/2, residual<=2e."""
    e = _bounded_q(epsilon)
    need(e >= 0, "V23_NONNEGATIVE_AMPLITUDE_PREMISE")
    bound = Q(1, 4) - e
    need(bound > 0, "V23_STRICT_DERIVATIVE_PREMISE_UNAVAILABLE")
    return bound


def v25_derivative_lower(amplitude_abs, sine_amplitude, epsilon):
    """Conditional sector lemma: positive sine amplitude and nonnegative slope."""
    a, b, e = map(_bounded_q, (amplitude_abs, sine_amplitude, epsilon))
    need(a >= 0 and b > 0 and e >= 0, "V25_AMPLITUDE_SIGN_PREMISE")
    bound = (b / 2 - a - 2 * e) / 2
    need(bound > 0, "V25_STRICT_DERIVATIVE_PREMISE_UNAVAILABLE")
    return bound


def v40_derivative_upper(minimum_amplitude, common_slope, epsilon):
    """Conditional first-span lemma, cos+sin>=1 and 3/4<omega<11/14."""
    m, slope, e = map(_bounded_q, (minimum_amplitude, common_slope, epsilon))
    need(m > 0 and slope >= 0 and e >= 0, "V40_AMPLITUDE_SIGN_PREMISE")
    coefficient_upper = slope - 3 * m / 4
    need(coefficient_upper < 0, "V40_NEGATIVE_COS_PLUS_SIN_COEFFICIENT_REQUIRED")
    bound = coefficient_upper + 11 * e / 7
    need(bound < 0, "V40_STRICT_DERIVATIVE_PREMISE_UNAVAILABLE")
    return bound


def _point_receipt(span, coordinate):
    proof = point.point(span, coordinate, max_order=1)
    need(proof["source_binding_sha256"] == point.span_binding(span),
         "EXACT_POINT_SOURCE_BINDING_CHANGED")
    keys = ("status", "source_binding_sha256", "coordinate", "phase_turn",
            "cyclotomic_order", "exact_vanishing_derivatives",
            "first_nonzero_derivative_order", "first_nonzero_derivative_sign",
            "exact_zero_decision")
    receipt = {key: proof[key] for key in keys}
    receipt["replayed_point_witness_sha256"] = guards.digest(proof)
    if proof["status"] == "EXACT_NONZERO_RATIONAL_POINT":
        receipt["value_sign"] = proof["value_sign"]
    else:
        receipt.update({key: proof[key] for key in
                        ("one_sided_order", "left_sign", "right_sign", "event_kind")})
    return receipt


def _span_record(span):
    return {"interval": [str(span.left), str(span.right)],
            "phase_turn_law": [str(span.offset), str(span.rate)],
            "source_binding_sha256": point.span_binding(span),
            "global_parameter_power_coefficients": {
                str(h): [list(map(str, p)), list(map(str, q))]
                for h, (p, q) in sorted(span.terms.items())}}


def source_proof(candidate):
    label, original, spans = lower_original(candidate)
    left, right = spans
    pi_lo, pi_hi = interval.pi_bounds()
    need(Q(3) < pi_lo < pi_hi < Q(22, 7), "CERTIFIED_PI_ENCLOSURE_CHANGED")
    start, end = _point_receipt(left, Q(0)), _point_receipt(right, Q(2))
    need(start["status"] == end["status"] == "EXACT_NONZERO_RATIONAL_POINT",
         "EXTERIOR_ENDPOINT_ZERO_OR_UNRESOLVED")
    knot = point.compose_knot(left, right, Q(1), max_order=1)
    negative_control = interval.attempt(left, max_depth=12, max_nodes=2000)
    expected_reason = ("UNDECIDED_ISOLATION_CUT" if label == "v40"
                       else "UNDECIDED_EVENT_OR_TANGENCY")
    need(negative_control.get("is_truth_value") is False and
         negative_control.get("status") == "RESOURCE_REFUSAL" and
         negative_control.get("reason") == expected_reason,
         "EXPECTED_TRANSVERSE_REFUSAL_CHANGED")
    negative_control = {"source_binding_sha256": point.span_binding(left),
                        "budget": {"max_depth": 12, "max_nodes": 2000},
                        "status": negative_control["status"],
                        "reason": negative_control["reason"], "is_truth_value": False}

    if label in ("v23", "v25"):
        if label == "v23":
            e = left.terms[2][0][1]
            bound = v23_derivative_lower(e)
            expressions = ["1/1000 + 999*pi*sqrt(3)/12000",
                           "999*pi*sqrt(3)/12000"]
            phase_sectors = [["0", "1/12"], ["1/12", "1/6"]]
            lemma = "V23_NONCONSTANT_AMPLITUDE_SECTOR_DERIVATIVE"
        else:
            e = left.terms[2][0][0]
            a = max(abs(interval.polynomial(left.terms[1][0], x)) for x in (Q(0), Q(1)))
            b = left.terms[1][1][0]
            bound = v25_derivative_lower(a, b, e)
            expressions = ["1/10 + 2*pi/3", "2*pi/3"]
            phase_sectors = [["-1/12", "0"], ["0", "1/12"]]
            lemma = "V25_COMPONENT_CONE_SECTOR_DERIVATIVE"
        exact_left, exact_right = _point_receipt(left, Q(1)), _point_receipt(right, Q(1))
        need(knot["status"] == "EXACT_SINGLE_SOURCE_KNOT_ZERO" and
             knot["physical_zero_events"] == 1 and
             knot["left_one_sided_order"] == knot["right_one_sided_order"] == 1 and
             knot["left_sign"] == -1 and knot["right_sign"] == 1 and
             knot["global_smooth_multiplicity_claimed"] is False,
             "EXACT_SINGLE_KNOT_EVENT_NOT_ESTABLISHED")
        validated = [point.validate(s, Q(1), 1) for s in spans]
        jets = [point.jet(v[0], v[1], 1, v[3], v[4]) for v in validated]
        need(jets[0] != jets[1], "SIDED_DERIVATIVE_JUMP_NOT_ESTABLISHED")
        signs = [-1, 1]
        cells = [{"interval": ["0", "1"], "open_at_event": "RIGHT", "sign": -1},
                 {"interval": ["1", "2"], "open_at_event": "LEFT", "sign": 1}]
        event = {"kind": "EXACT_PHYSICAL_SOURCE_KNOT_ZERO", "coordinate": "1",
                 "left_one_sided_order": 1, "right_one_sided_order": 1,
                 "left_sign": -1, "right_sign": 1,
                 "global_smooth_multiplicity_claimed": False,
                 "exact_sided_derivatives_unequal": True,
                 "sided_derivative_expressions": expressions,
                 "local_point_receipts": [exact_left, exact_right]}
        completeness = {"lemma": lemma, "phase_sectors_in_turns": phase_sectors,
                        "strict_derivative_lower_bound_on_each_span": str(bound),
                        "entire_original_closed_interval_covered": True,
                        "method": "EXACT_ZERO_PLUS_STRICT_INCREASE_ON_BOTH_CONTINUOUS_PIECES"}
    else:
        epsilon = -left.terms[2][0][0]
        minimum = min(left.terms[1][0][0], -interval.polynomial(left.terms[1][1], Q(1)))
        slope = left.terms[1][0][1]
        bound = v40_derivative_upper(minimum, slope, epsilon)
        tail_upper = right.terms[1][0][0] / 2 + right.terms[1][1][0] * Q(4, 5) + epsilon
        need(tail_upper < 0 and Q(3, 4) > Q(16, 25),
             "V40_TAIL_SECTOR_SIGN_PREMISE_UNAVAILABLE")
        exact_root = _point_receipt(left, Q(1, 2))
        need(exact_root["status"] == "EXACT_RATIONAL_POINT_EVENT" and
             exact_root["one_sided_order"] == 1 and
             exact_root["left_sign"] == 1 and exact_root["right_sign"] == -1,
             "V40_EXACT_SIMPLE_ROOT_NOT_ESTABLISHED")
        need(knot["status"] == "EXACT_NONZERO_SOURCE_KNOT" and
             knot["physical_zero_events"] == 0 and knot["sign"] == -1,
             "V40_NONZERO_SOURCE_KNOT_NOT_ESTABLISHED")
        signs = [1, -1]
        cells = [{"interval": ["0", "1/2"], "open_at_event": "RIGHT", "sign": 1},
                 {"interval": ["1/2", "2"], "open_at_event": "LEFT", "sign": -1}]
        event = {"kind": "EXACT_SMOOTH_INTERIOR_ZERO", "coordinate": "1/2",
                 "source_span": ["0", "1"], "smooth_multiplicity": 1,
                 "left_sign": 1, "right_sign": -1,
                 "is_original_source_knot": False, "local_point_receipt": exact_root}
        completeness = {"lemma": "V40_ANTI_DIAGONAL_STRICT_DECREASE_AND_NEGATIVE_TAIL",
                        "first_span_phase_sector_in_turns": ["1/16", "3/16"],
                        "strict_first_span_derivative_upper_bound": str(bound),
                        "tail_phase_sector_in_turns": ["3/16", "5/16"],
                        "tail_enclosing_sector_in_turns": ["1/6", "1/3"],
                        "tail_function_upper_bound": str(tail_upper),
                        "entire_original_closed_interval_covered": True}
    need([start["value_sign"], end["value_sign"]] == signs,
         "COMPLETE_SIGN_CHAIN_EXTERIOR_MISMATCH")
    pin_dependencies()
    return {"case_id": original["id"], **guards.source_metadata(original),
            "historical_v54_disposition": original["expected"]["v54_disposition"],
            "historical_source_and_span_observations": original["expected"]["observed"],
            "historical_disposition_changed": False,
            "source_spans": [_span_record(s) for s in spans],
            "exterior_endpoint_receipts": [start, end],
            "source_knot_receipt": knot,
            "physical_events": [event], "physical_zero_set": [event["coordinate"]],
            "complete_original_source_zero_set": True,
            "complete_finite_physical_event_count": 1,
            "ordered_nonzero_signs": signs, "maximal_nonzero_cells": cells,
            "whole_source_completeness_proof": completeness,
            "retained_transverse_negative_control": negative_control,
            "evidence_class": "DETERMINISTIC_MODEL", "production_authorized": False}


def expected_report():
    rows = original_rows()
    proofs = [source_proof(rows[label]) for label in SOURCES]
    report = {"schema": SCHEMA, "evidence_class": "DETERMINISTIC_MODEL",
              "source_authority_main": BASE_MAIN,
              "claim": "THREE_PINNED_ORIGINAL_SOURCES_COMPLETE_EXACT_ZERO_AND_SIGN_PROOFS",
              "dependency_git_blobs": dict(PINS),
              "historical_v54": {"original_source_cases": 121, "route_refusals": 20,
                                  "missing_ordered_span_premises": 30,
                                  "dispositions_changed": False},
              "source_specific_proofs": proofs,
              "summary": {"complete_original_sources": 3, "physical_zero_events": 3,
                          "nonsmooth_source_knot_events": 2, "smooth_interior_events": 1,
                          "exterior_zero_events": 0, "continuum_sources": 0},
              "generic_transverse_engine_changed": False,
              "universal_event_interface_established": False,
              "historical_owner_routes_repaired": False,
              "mc_b_established": False, "mc1_established": False,
              "production_authorized": False}
    guards.bounded_bytes(report)
    return report


def validate_report(candidate):
    packed = guards.bounded_bytes(candidate)
    expected = expected_report()
    need(packed == guards.bounded_bytes(expected),
         "SUBMITTED_WITNESS_DISAGREES_WITH_FRESH_ORIGINAL_SOURCE_PROOF")
    return expected


def read_report(path=REPORT):
    return guards.read_json(Path(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = expected_report()
    if args.write_report:
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        need(guards.bounded_bytes(read_report()) == guards.bounded_bytes(report),
             "SAVED_WITNESS_DISAGREES_WITH_FRESH_PROOF")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
