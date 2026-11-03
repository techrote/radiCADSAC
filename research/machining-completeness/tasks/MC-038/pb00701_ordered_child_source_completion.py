#!/usr/bin/env python3
"""Complete fifteen pinned original sources formerly represented by one V6 child.

The unchanged exact B-spline lowerer and transverse interval kernel prove both
actual source spans. A checked finite cover and exact channel continuity then
compose complete physical root/sign sets. This is a finite research consumer,
not a generic owner adapter, historical disposition change or capability gate.
Only checksum-bound originals reach legacy constructors. Caller reports are
bounded typed data compared with fresh replay, never source or proof authority.
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
SCHEMA = "radicadsac-mc038-ordered-child-source-completion/1.0"
BASE_MAIN = "e0514500aeca59afa4924dcc2da3ca0c2688d9ac"
MACHINE = HERE / "pb00701-ordered-child-source-completion-witness.json"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
V6 = "DELEGATED_V6_CONSTANT_MODULATION"
MAX_BYTES, MAX_NODES, MAX_DEPTH, MAX_STRING = 1048576, 65536, 32, 8192
PROOF_DEPTH, PROOF_NODES = 12, 2000
TASK_PREFIX = "research/machining-completeness/tasks/MC-038/"
PINS = {
    TASK_PREFIX + "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    TASK_PREFIX + "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    TASK_PREFIX + "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    TASK_PREFIX + "pb00701-post-v54-evidence-reconciliation.json": "9f62dd6edc37206317eec054b2969bade02d7728",
    TASK_PREFIX + "pb00701_coupled_bspline_model.py": "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    TASK_PREFIX + "pb00701_rational_turn_model.py": "a1316ff0f71b2d7aa80807843a74fd8280779cb2",
    TASK_PREFIX + "pb00701_event_model.py": "104c0e7a459cd7da5025853b246faff244a5948e",
    TASK_PREFIX + "pb00701_transverse_trig_interval.py": "2320f92efe4316d865a89f6d848737e2c000ca4d",
    "research/machining-completeness/tasks/MC-032/event_engine.py": "789a709c5141479a343035d1b7055dd4e53534e1",
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json": "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/programme-v1.json": "dee7045a1790b2870744df8ae7693429bd1d81a6",
    "handoffs/current-authority.json": "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}
MODULE_PATHS = {
    "pb00701_coupled_bspline_model": TASK_PREFIX + "pb00701_coupled_bspline_model.py",
    "pb00701_rational_turn_model": TASK_PREFIX + "pb00701_rational_turn_model.py",
    "pb00701_event_model": TASK_PREFIX + "pb00701_event_model.py",
    "pb00701_transverse_trig_interval": TASK_PREFIX + "pb00701_transverse_trig_interval.py",
    "radicadsac_mc032_event_engine": "research/machining-completeness/tasks/MC-032/event_engine.py",
}
ENGINE_MODULE = "radicadsac_mc032_event_engine"

# Exact original specification and complete original-record SHA-256 pairs.
CASE_PINS = {'composite:PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR:tail0': ('4304ce6d31b385ce3e3c1af3f31e677d91099f244a7befdcff9170367d4aace9',
                                                                              '1b9853fb48e5fe91dab9856c75f43fb3591f1272367f895e7f382d00a58c9edd'),
 'composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0': ('e8d2451833854ee7eaf73d4fb70b78b86ba72194b2688876f3bb9ee6ab132ffd',
                                                                                 'e52a27e5c3dcdf984919cdcd7bb925c52d2865550035da357cd87178b9fbfc89'),
 'composite:PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR:tail0': ('e565ddf6bb0bab080128aeda16be5ea60466b3b971aa98d0408ea9a96da3d052',
                                                                     '696718a819afa68c7a7122e9fba85eae3b5a8b8be905f94836f666fd74d9298b'),
 'composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0': ('d7bf5969875c5ae44fa83f80d217fe17b02aca4db58545dc943c43e744ef68b6',
                                                                              '90642204b36339c0bea36a1196c4b1045f4b0fa360d25493eb59b23881579ab8'),
 'composite:PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION:tail0': ('7f2984f588215067297eeabe4f5b6c57d993c3ce2c33374e551982ed43de3093',
                                                                                     '4bb9b1fd7c9b5e6ae47c3f52cfd1eb6374136c4621ba3220d44b2456c1a0964a'),
 'composite:PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION:tail0': ('ea2259d594a90d9523a46250e5ed8023dd081a3bf283bf8c2b410f0b18cfa25a',
                                                                                      '7312b290c7d1246f15cefe92b5d1694b6dcac5f6143b2dfd270b7cd1920f64a2'),
 'composite:PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR:tail0': ('7e637ad3528fa5d55ae7cdd9aee3b3d8f2716d089203896a24d80a823f1e969d',
                                                                                     'b3df7d07a1386f1e0b64c611d67def143692b95ef10da6a8c6b104ce83a9e1d0'),
 'composite:PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR:tail0': ('404a68c1f2624abb29b700250807b43c466cab18c049c8e78a1049ce5fee10da',
                                                                      '5437a61eaf745a9c5ef5f4405934815db26d147c9d3524a8db66a1146e7d298a'),
 'composite:PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR:tail0': ('6e7d4ae0dcd4303243772ec7cb1914c590ed91b6b5b27af5262f24ee8e493f19',
                                                                                   '0caac73bf90d76a5c83f1faa60c2122959a1ad3109e53318c3e975505db1830d'),
 'composite:PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR:tail0': ('78cb3259190ca810d825690303e33b69f7a63f6ca7bc4fba7d705e470a90695f',
                                                                                    '2a7abe39076a67f824b394913e225054168c7a5e4d8e35cd2fa36a8618b8a2e8'),
 'composite:PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR:tail0': ('cde19c3ac184e59bf8914f130c3e9b1a988b529467e39bc6b8493764a0feb0fa',
                                                                                     'a9d612e237f7277daa3d85f4218fc774cdf391a1761da33e1eb980bf4a35f286'),
 'composite:PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE:tail0': ('9b7429ae290de259b2990b39740f40495c02b407e4e906e7eece77ea65c43f03',
                                                                                'a8d5801d40c97979d8a49124ddb286c59be91b41bb0cf52c9047e60163e12982'),
 'composite:PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE:tail0': ('daeafb37dd81d27fbba1c97dd09b14767531e37046237449aab3eaa9adfc1061',
                                                                          '7a5ae576818a753fb0b0afb1f09058b58b468da8fc884f528166c05bf1c0b176'),
 'composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0': ('90a5df370094bcd8cef37be171f9bb12264c15a32237300b5435dc8871c6c2bf',
                                                                                        '8291b11b51d2109451ba852185bf6d9504c9d7e46473bf01be5924508ded5fad'),
 'composite:PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE:tail0': ('95a977a9d300218fa2bd45cd54b752f2bb976b3c73c934d3c1aa715a25d6faed',
                                                                                        'c0e0cea514ac59ef80d492b8feb255efd2a7883926a8f95ff9ddb9e472901b97'),
 'composite:PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF:tail0': ('28cd4b4be4c74e6404b1a307d2217b2dc5a8b708b28c5ad75309c35e48092efd',
                                                                 '98057a188fdf320d0238600f3b8a4c10dcb60f9a569010b44cda06a32970a9c4'),
 'composite:PB00701_V48_MIXED_ROOT_SINGLE_CUT:tail0': ('0435a131c257bb5d453932f3692a45f787f83c9cc073fb38c879570f1f60ebfd',
                                                       '90bee5b127f42eca93118f3b5effdb46f305824271cb703e9d990ffa8d956058'),
 'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0': ('4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2',
                                                                     '406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279')}
DEFERRED = {
    "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0": "UNDECIDED_EVENT_OR_TANGENCY",
    "composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0": "UNDECIDED_EVENT_OR_TANGENCY",
    "composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0": "UNDECIDED_ISOLATION_CUT",
}
CASES = tuple(sorted(set(CASE_PINS) - set(DEFERRED)))


class Refusal(ValueError):
    """Malformed, contradicted or exhausted evidence is never proof."""


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def bounded_bytes(value):
    """Check resources/types before recursive JSON or any numeric parsing."""
    stack, active, visited, size = [(value, 0, False)], set(), 0, 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        visited += 1
        need(visited <= MAX_NODES and depth <= MAX_DEPTH, "JSON_NODE_OR_DEPTH_LIMIT")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 1024, "JSON_CYCLE_OR_CONTAINER_LIMIT")
            active.add(id(obj))
            size += 2 + 2 * len(obj)
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, child in obj.items():
                    need(type(key) is str and len(key) <= MAX_STRING, "JSON_KEY_LIMIT")
                    size += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth + 1, False))
            else:
                stack.extend((child, depth + 1, False) for child in obj)
        elif type(obj) is str:
            need(len(obj) <= MAX_STRING, "JSON_STRING_LIMIT")
            size += len(json.dumps(obj, ensure_ascii=True))
        elif type(obj) is int:
            need(obj.bit_length() <= 256, "JSON_INTEGER_LIMIT")
            size += len(str(obj))
        else:
            need(obj is None or type(obj) is bool, "NONEXACT_JSON_SCALAR")
            size += 5
        need(size <= MAX_BYTES, "JSON_AGGREGATE_BYTE_LIMIT")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(raw) <= MAX_BYTES, "JSON_BYTE_LIMIT")
    return raw


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def _unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _json_integer(text):
    need(len(text) <= 79, "JSON_INTEGER_LIMIT")
    value = int(text)
    need(value.bit_length() <= 256, "JSON_INTEGER_LIMIT")
    return value


def _reject_json_number(_):
    raise Refusal("NONEXACT_JSON_SCALAR")


def read_bytes(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "FILE_BYTE_LIMIT")
    return raw


def _decode_json(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "FILE_BYTE_LIMIT")
    try:
        value = json.loads(raw, object_pairs_hook=_unique_pairs,
                           parse_int=_json_integer, parse_float=_reject_json_number,
                           parse_constant=_reject_json_number)
    except Refusal:
        raise
    except (RecursionError, ValueError, UnicodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    bounded_bytes(value)
    return value


def read_json(path):
    return _decode_json(read_bytes(path))


def git_blob(path):
    raw = read_bytes(path)
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _pinned_bytes(path, expected):
    need(Path(path).is_file(), "PINNED_INPUT_DRIFT:" + str(path))
    raw = read_bytes(path)
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(actual == expected, "PINNED_INPUT_DRIFT:" + str(path))
    return raw


def pin(path, expected):
    _pinned_bytes(path, expected)


def read_pinned_json(path):
    """Decode the exact checked bytes of one finite repository JSON input."""
    resolved = Path(path).resolve()
    allowed = {(ROOT / name).resolve(): expected for name, expected in PINS.items()
               if name.endswith(".json")}
    need(resolved in allowed, "JSON_PATH_OUTSIDE_PINNED_INPUTS")
    return _decode_json(_pinned_bytes(resolved, allowed[resolved]))


def check_pins():
    for path, expected in PINS.items():
        pin(ROOT / path, expected)


def exact_rational(value):
    """Bounded canonical ratios; exponent/decimal strings never reach Fraction."""
    need(type(value) is str and 0 < len(value) <= 80 and value.isascii(), "RATIONAL_SYNTAX")
    parts = value.split("/")
    need(len(parts) in (1, 2), "RATIONAL_SYNTAX")
    numerator = parts[0]
    digits = numerator[1:] if numerator.startswith("-") else numerator
    denominator = parts[1] if len(parts) == 2 else "1"
    need(0 < len(digits) <= 39 and digits.isdigit() and
         0 < len(denominator) <= 39 and denominator.isdigit(), "RATIONAL_SYNTAX")
    n, d = int(numerator), int(denominator)
    need(n.bit_length() <= 128 and 0 < d and d.bit_length() <= 128, "RATIONAL_RESOURCE_LIMIT")
    result = Q(n, d)
    need(str(result) == value, "NONCANONICAL_RATIONAL")
    return result


class _PinnedImplementation:
    """One fresh finite module graph, compiled from its checked source buffers.

    Project imports never consult sys.modules or filesystem bytecode caches.
    The legacy event model's sole dynamic import receives a module-local
    importlib.util facade. No global importer or module cache is replaced.
    """

    def __init__(self):
        self.buffers = {name: _pinned_bytes(ROOT / relative, PINS[relative])
                        for name, relative in MODULE_PATHS.items()}
        self.modules, self.loading = {}, set()
        self.original_import = builtins.__import__
        self.local_sys = types.SimpleNamespace(path=list(sys.path))
        self.engine_spec = types.SimpleNamespace(
            name=ENGINE_MODULE, origin=str(ROOT / MODULE_PATHS[ENGINE_MODULE]),
            loader=types.SimpleNamespace(exec_module=self._execute_engine))
        self.importlib = types.SimpleNamespace(util=types.SimpleNamespace(
            spec_from_file_location=self._engine_spec,
            module_from_spec=self._module_from_spec))

    def _engine_spec(self, name, path):
        need(name == ENGINE_MODULE and Path(path).resolve() ==
             (ROOT / MODULE_PATHS[ENGINE_MODULE]).resolve(), "UNPINNED_DYNAMIC_MODULE")
        return self.engine_spec

    def _module_from_spec(self, spec):
        need(spec is self.engine_spec, "UNPINNED_DYNAMIC_MODULE")
        return types.ModuleType(ENGINE_MODULE)

    def _execute_engine(self, module):
        return self._execute(ENGINE_MODULE, module)

    def _import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in MODULE_PATHS:
            need(not fromlist, "UNREVIEWED_PROJECT_IMPORT_INTERFACE")
            return self.load(name)
        if level == 0 and name == "importlib.util":
            need(not fromlist, "UNREVIEWED_IMPORTLIB_INTERFACE")
            return self.importlib
        if level == 0 and name == "sys":
            need(not fromlist, "UNREVIEWED_SYS_INTERFACE")
            return self.local_sys
        need(not name.startswith(("pb00701_", "radicadsac_")), "UNPINNED_PROJECT_IMPORT")
        return self.original_import(name, globals, locals, fromlist, level)

    def _execute(self, name, module):
        need(name in MODULE_PATHS and type(module) is types.ModuleType and
             module.__name__ == name, "UNPINNED_PROJECT_MODULE")
        need(name not in self.modules and name not in self.loading, "DUPLICATE_OR_CYCLIC_MODULE")
        self.loading.add(name)
        path = ROOT / MODULE_PATHS[name]
        module.__file__ = str(path)
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=self._import)
        try:
            exec(compile(self.buffers[name], str(path), "exec"), module.__dict__)
        finally:
            self.loading.remove(name)
        self.modules[name] = module
        return module

    def load(self, name):
        need(name in MODULE_PATHS and name not in self.loading, "UNPINNED_OR_CYCLIC_MODULE")
        if name not in self.modules:
            self._execute(name, types.ModuleType(name))
        return self.modules[name]


def implementation():
    check_pins()
    session = _PinnedImplementation()
    lower = session.load("pb00701_coupled_bspline_model")
    trig = session.load("pb00701_transverse_trig_interval")
    for module, relative in (
        (lower, TASK_PREFIX + "pb00701_coupled_bspline_model.py"),
        (lower.v6, TASK_PREFIX + "pb00701_rational_turn_model.py"),
        (lower.v6.base, TASK_PREFIX + "pb00701_event_model.py"),
        (lower.EE, "research/machining-completeness/tasks/MC-032/event_engine.py"),
        (trig, TASK_PREFIX + "pb00701_transverse_trig_interval.py"),
    ):
        need(Path(module.__file__).resolve() == (ROOT / relative).resolve(), "IMPORTED_MODULE_PATH_DRIFT")
    need(lower.v6 is session.modules["pb00701_rational_turn_model"] and
         lower.v6.base is session.modules["pb00701_event_model"] and
         lower.EE is lower.v6.EE is lower.v6.base.EE is session.modules[ENGINE_MODULE],
         "TRANSITIVE_MODULE_IDENTITY_DRIFT")
    check_pins()
    return lower, trig


def check_source_row(row, *, include_deferred=False):
    bounded_bytes(row)
    need(type(row) is dict and type(row.get("id")) is str, "INVALID_SOURCE_RECORD")
    cid = row["id"]
    allowed = CASE_PINS if include_deferred else CASES
    need(cid in allowed, "SOURCE_OUTSIDE_SELECTED_FINITE_SET")
    source_hash, row_hash = CASE_PINS[cid]
    need(digest(row) == row_hash, "ORIGINAL_RECORD_HASH_DRIFT")
    need(digest(row["spec"]) == source_hash, "ORIGINAL_SPECIFICATION_HASH_DRIFT")
    need(row["kind"] == "COMPOSITE_TAIL" and
         row["expected"]["v54_disposition"] == ORDER_GAP and
         row["expected"]["observed"]["status"] == "CERTIFIED" and
         len(row["expected"]["observed"]["spans"]) == 2 and
         row["expected"]["observed"]["spans"][1] == [V6, "CERTIFIED", None],
         "HISTORICAL_PROVENANCE_DRIFT")
    return row


def original_rows():
    check_pins()
    auth = read_pinned_json(ROOT / "handoffs/current-authority.json")
    programme = read_pinned_json(ROOT / "research/machining-completeness/programme-v1.json")
    domain = read_pinned_json(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
    need(auth["capability_status"] == programme["capability_status"] == "NOT_ESTABLISHED"
         and auth["production_authorized"] is False
         and programme["production_authorized"] is False
         and {g["id"]: g["state"] for g in programme["gates"]}["MC-B"] == "NOT_ESTABLISHED",
         "PROGRAMME_AUTHORITY_PROMOTION")
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26, "DOMAIN_DENOMINATOR_DRIFT")
    corpus = read_pinned_json(HERE / "pb00701-finite-owner-corpus-v54.json")
    indexed = {row["id"]: row for row in corpus["cases"]}
    need(len(corpus["cases"]) == len(indexed) == 121, "FROZEN_SOURCE_DENOMINATOR_DRIFT")
    counts = corpus["summary"]["v54_dispositions"]
    need(counts["BLOCKED"] == 20 and counts[ORDER_GAP] == 30, "HISTORICAL_DISPOSITIONS_DRIFT")
    baseline = read_pinned_json(HERE / "pb00701-post-v54-evidence-reconciliation.json")
    child_ids = {r["case_id"] for r in baseline["source_cases"]
                 if r["registered_evidence_level"] == "PARTIAL_ORDERED_CHILD"}
    need(len(CASES) == 15 and len(DEFERRED) == 3 and
         child_ids == set(CASE_PINS) and len(child_ids) == 18, "CHILD_COHORT_DRIFT")
    for cid in CASE_PINS:
        check_source_row(indexed[cid], include_deferred=True)
    return {cid: indexed[cid] for cid in CASE_PINS}


def lower_original(row, lower, trig, *, include_deferred=False):
    check_source_row(row, include_deferred=include_deferred)
    source = row["spec"]
    lo, hi = map(exact_rational, (source["parameter_lo"], source["parameter_hi"]))
    offset, rate = map(exact_rational, (source["phase_turn_offset"], source["phase_turn_rate"]))
    cos = lower._normalise_harmonic_splines(source["cos_splines"], "cos_splines")
    sin = lower._normalise_harmonic_splines(source["sin_splines"], "sin_splines")
    edges = lower._master_boundaries(list(cos.values()) + list(sin.values()), lo, hi)
    need(edges == [Q(0), Q(1), Q(2)], "ORIGINAL_PIECE_BOUNDARIES_DRIFT")
    views = []
    for index, (left, right) in enumerate(zip(edges, edges[1:])):
        terms = {}
        for harmonic in sorted(set(cos) | set(sin)):
            p = lower._piece_from_normal(cos[harmonic], left, right)["coefficients"] if harmonic in cos else [Q(0)]
            q = lower._piece_from_normal(sin[harmonic], left, right)["coefficients"] if harmonic in sin else [Q(0)]
            terms[int(harmonic)] = (tuple(p), tuple(q))
        views.append({"index": index, "interval": (left, right),
                      "source_parameter_id": source["source_parameter_id"],
                      "phase": (offset, rate), "terms": terms,
                      "historical_owner": row["expected"]["observed"]["spans"][index][0],
                      "span": trig.Span(left, right, offset, rate, terms)})
    check_source_cover(row, views, trig)
    return views


def check_source_cover(row, views, trig):
    """Coverage and actual channel continuity; proof cuts cannot become knots."""
    need(type(views) is list and len(views) == 2, "INCOMPLETE_OR_DUPLICATE_SOURCE_SPANS")
    source = row["spec"]
    phase = tuple(map(exact_rational, (source["phase_turn_offset"], source["phase_turn_rate"])))
    cursor = exact_rational(source["parameter_lo"])
    for index, view in enumerate(views):
        left, right = view["interval"]
        need(view["index"] == index and left == cursor and left < right,
             "SOURCE_SPAN_GAP_OVERLAP_OR_ORDER")
        need((left, right) == (Q(index), Q(index + 1)), "NOT_AN_ORIGINAL_SOURCE_PIECE")
        need(view["source_parameter_id"] == source["source_parameter_id"] and
             view["phase"] == phase, "SOURCE_PARAMETER_OR_PHASE_MISMATCH")
        span = view["span"]
        need((span.left, span.right, span.offset, span.rate) == (left, right, *phase)
             and span.terms == view["terms"], "LOWERED_FUNCTION_BINDING_MISMATCH")
        cursor = right
    need(cursor == exact_rational(source["parameter_hi"]), "INCOMPLETE_SOURCE_COVER")
    first, second = views
    need(set(first["terms"]) == set(second["terms"]), "CHANNEL_SET_CHANGED_AT_KNOT")
    for harmonic in first["terms"]:
        for channel in (0, 1):
            left_value = trig.polynomial(first["terms"][harmonic][channel], Q(1))
            right_value = trig.polynomial(second["terms"][harmonic][channel], Q(1))
            need(left_value == right_value, "ORIGINAL_CHANNEL_KNOT_DISCONTINUITY")


def _sign(value):
    need(type(value) is int and value in (-1, 1), "INVALID_STRICT_SIGN")
    return value


def check_partition(view, proof, trig):
    """Recheck the finite proof cover against the actual lowered function.

    This private routine consumes only fresh kernel output in the public path.
    Point signs, Lipschitz sign/derivative bounds, isolation and physical order
    are nevertheless checked, rather than trusting a count/status assertion.
    """
    bounded_bytes(proof)
    need(type(proof) is dict and proof.get("status") == "RESEARCH_ONLY_CHECKED"
         and proof.get("is_truth_value") is True, "INTERVAL_REPLAY_NOT_PROOF")
    need(proof.get("schema") == trig.SCHEMA and
         proof.get("evidence_class") == "DETERMINISTIC_MODEL" and
         proof.get("historical_child_certified") is False and
         proof.get("production_authorized") is False,
         "INTERVAL_PROOF_AUTHORITY_MISMATCH")
    need(type(proof.get("nodes")) is int and 1 <= proof["nodes"] <= PROOF_NODES,
         "INTERVAL_PROOF_NODE_BUDGET")
    need(proof.get("source_interval") == [str(x) for x in view["interval"]]
         and proof.get("source_phase_turns") == [str(x) for x in view["phase"]],
         "PARTITION_SOURCE_OR_PHASE_MISMATCH")
    parts = proof.get("partition")
    endpoints = proof.get("endpoint_signs")
    need(type(parts) is list and 0 < len(parts) <= PROOF_NODES and
         type(endpoints) is list and len(endpoints) == 2, "INVALID_FINITE_PARTITION")
    start_sign, end_sign = map(_sign, endpoints)
    span, cursor, state, roots = view["span"], view["interval"][0], start_sign, []
    need(trig.strict_sign(span.evaluate(cursor)) == start_sign and
         trig.strict_sign(span.evaluate(view["interval"][1])) == end_sign,
         "EXTERIOR_ENDPOINT_SIGN_CONTRADICTION")
    for cell in parts:
        need(type(cell) is dict and type(cell.get("interval")) is list and
             len(cell["interval"]) == 2, "INVALID_PARTITION_CELL")
        left, right = map(exact_rational, cell["interval"])
        need(cursor == left < right <= view["interval"][1], "PARTITION_GAP_OVERLAP_OR_ORDER")
        midpoint, radius = (left + right) / 2, (right - left) / 2
        f_sign = trig.strict_sign(trig.widen(span.evaluate(midpoint), span.m1 * radius))
        d_sign = trig.strict_sign(trig.widen(span.evaluate(midpoint, True), span.m2 * radius))
        actual_left = trig.strict_sign(span.evaluate(left))
        actual_right = trig.strict_sign(span.evaluate(right))
        if cell.get("kind") == "NO_ROOT":
            sign = _sign(cell.get("sign"))
            need(sign == state == actual_left == actual_right and
                 (f_sign == sign or (d_sign != 0 and actual_left == actual_right)),
                 "NO_ROOT_CELL_NOT_PROVED")
        else:
            need(cell.get("kind") == "ONE_SIMPLE_ROOT" and
                 type(cell.get("smooth_multiplicity")) is int and
                 cell["smooth_multiplicity"] == 1, "UNSUPPORTED_PHYSICAL_EVENT")
            left_sign, right_sign = _sign(cell.get("left_sign")), _sign(cell.get("right_sign"))
            claimed_derivative = _sign(cell.get("derivative_sign"))
            need(state == left_sign == actual_left and right_sign == actual_right
                 and left_sign == -right_sign and claimed_derivative == d_sign
                 and (right_sign - left_sign) * d_sign > 0,
                 "SIMPLE_ROOT_DERIVATIVE_OR_SIGN_CONTRADICTION")
            bracket = cell.get("strict_isolation")
            need(type(bracket) is list and len(bracket) == 2, "INVALID_ROOT_ISOLATION")
            lo, hi = map(exact_rational, bracket)
            need(left <= lo < hi <= right and
                 trig.strict_sign(span.evaluate(lo)) == left_sign and
                 trig.strict_sign(span.evaluate(hi)) == right_sign,
                 "ROOT_BRACKET_NOT_STRICT_OR_NOT_SOURCE_BOUND")
            roots.append({"strict_bracket": list(bracket), "left_sign": left_sign,
                          "right_sign": right_sign, "smooth_multiplicity": 1,
                          "derivative_sign": d_sign})
            state = right_sign
        cursor = right
    need(cursor == view["interval"][1] and state == end_sign, "INCOMPLETE_PARTITION_OR_SIGN_CHAIN")
    need(type(proof.get("complete_simple_root_count")) is int and
         proof["complete_simple_root_count"] == len(roots), "ROOT_COUNT_DISAGREES_WITH_PROOF")
    return roots


def compose(row, views, proofs, trig):
    """Private composition of freshly regenerated original-span proofs."""
    check_source_cover(row, views, trig)
    need(type(proofs) is list and len(proofs) == len(views), "MISSING_OR_DUPLICATE_SPAN_PROOF")
    events, signs, span_rows, state = [], [], [], None
    for view, proof in zip(views, proofs):
        roots = check_partition(view, proof, trig)
        first_sign, last_sign = proof["endpoint_signs"]
        if state is None:
            signs.append(first_sign)
        else:
            need(state == first_sign, "TRUE_SOURCE_KNOT_SIGN_MISMATCH")
        state = first_sign
        for root in roots:
            need(root["left_sign"] == state, "GLOBAL_ROOT_SIGN_ORDER_MISMATCH")
            if events:
                need(exact_rational(events[-1]["strict_bracket"][1]) <=
                     exact_rational(root["strict_bracket"][0]), "GLOBAL_ROOT_ORDER_OVERLAP")
            events.append({"root_ref": "ROOT_" + str(len(events) + 1),
                           "descriptor": "UNIQUE_SIMPLE_ZERO_OF_PINNED_ORIGINAL_SOURCE",
                           "source_span_index": view["index"],
                           "source_interval": [str(x) for x in view["interval"]],
                           "historical_owner": view["historical_owner"], **root})
            state = root["right_sign"]
            signs.append(state)
        need(state == last_sign, "SPAN_FINAL_SIGN_MISMATCH")
        span_rows.append({"source_span_index": view["index"],
                          "original_interval": [str(x) for x in view["interval"]],
                          "historical_owner": view["historical_owner"],
                          "original_global_power_coefficients": {
                              str(h): {"cos": [str(c) for c in p], "sin": [str(c) for c in q]}
                              for h, (p, q) in sorted(view["terms"].items())},
                          "interval_proof": proof})
    boundaries = ["ORIGINAL_SOURCE_START"] + [e["root_ref"] for e in events] + ["ORIGINAL_SOURCE_END"]
    return {
        "case_id": row["id"], "origin": row["origin"], "provenance_kind": row["kind"],
        "source_sha256": digest(row["spec"]), "original_row_sha256": digest(row),
        "source_parameter_id": row["spec"]["source_parameter_id"], "source_interval": ["0", "2"],
        "phase_turn_law": {"offset": row["spec"]["phase_turn_offset"], "rate": row["spec"]["phase_turn_rate"]},
        "original_source_piece_edges": ["0", "1", "2"],
        "historical_v54_disposition": row["expected"]["v54_disposition"],
        "historical_spans": row["expected"]["observed"]["spans"],
        "status": "COMPLETE_PINNED_ORIGINAL_SOURCE_PROOF_RESEARCH_ONLY",
        "complete_closed_zero_set_kind": "FINITE", "complete_closed_root_count": len(events),
        "ordered_root_events": events,
        "maximal_open_physical_sign_cells": [
            {"left": boundaries[i], "right": boundaries[i + 1], "sign": sign}
            for i, sign in enumerate(signs)],
        "true_source_knots": [{"position": "1", "channel_continuous": True,
                              "left_sign": proofs[0]["endpoint_signs"][1],
                              "right_sign": proofs[1]["endpoint_signs"][0],
                              "is_physical_zero": False, "is_physical_event": False}],
        "exterior_endpoint_signs": [proofs[0]["endpoint_signs"][0], proofs[-1]["endpoint_signs"][1]],
        "complete_original_source_zero_set": True, "original_spans": span_rows,
        "certificate_partition_cuts_are_not_physical_events": True,
        "historical_disposition_changed": False,
    }


def prove_original(row, lower, trig):
    views = lower_original(row, lower, trig)
    try:
        proofs = [view["span"].prove(max_depth=PROOF_DEPTH, max_nodes=PROOF_NODES) for view in views]
    except (trig.Refusal, MemoryError, OverflowError, RecursionError) as exc:
        raise Refusal("INTERVAL_REPLAY_REFUSAL:" + str(exc)) from exc
    return compose(row, views, proofs, trig)


def deferred_controls(rows, lower, trig):
    controls = []
    for cid, expected_reason in sorted(DEFERRED.items()):
        views = lower_original(rows[cid], lower, trig, include_deferred=True)
        try:
            views[0]["span"].prove(max_depth=8, max_nodes=256)
        except trig.Refusal as exc:
            need(str(exc) == expected_reason, "DEFERRED_NEGATIVE_BOUNDARY_CHANGED")
        else:
            raise Refusal("DEFERRED_CASE_UNEXPECTEDLY_ACCEPTED")
        controls.append({"case_id": cid, "source_sha256": CASE_PINS[cid][0],
                         "original_row_sha256": CASE_PINS[cid][1],
                         "tested_original_interval": ["0", "1"],
                         "kernel_status": "REFUSAL", "reason": expected_reason,
                         "included_in_complete_sources": False,
                         "mathematical_impossibility_claimed": False})
    return controls


def expected_report():
    try:
        rows = original_rows()
        lower, trig = implementation()
        sources = [prove_original(rows[cid], lower, trig) for cid in CASES]
        deferred = deferred_controls(rows, lower, trig)
        need(len(sources) == 15 and sum(r["complete_closed_root_count"] for r in sources) == 8
             and sum(r["complete_closed_root_count"] == 0 for r in sources) == 8,
             "FIXED_SOURCE_RESULT_CHANGED")
        check_pins()
        report = {
            "schema": SCHEMA, "task": "MC-038 / PB-007-01", "evidence_class": "DETERMINISTIC_MODEL",
            "source_snapshot_main": BASE_MAIN,
            "purpose": "Complete fifteen original sources with only one registered V6 child, using exact two-span proofs and original-knot composition.",
            "dependency_git_blobs": PINS,
            "historical_v54": {"original_source_cases": 121, "route_refusals": 20,
                               "missing_ordered_span_premises": 30, "dispositions_changed": False},
            "scope": {"selected_original_sources": 15, "historical_child_only_cohort": 18,
                      "deferred_exact_zero_cases": 3, "all_possible_source_proofs_claimed": False,
                      "generic_owner_adapter_established": False,
                      "previous_evidence_registry_modified": False},
            "proof_method": {"original_global_polynomial_lowering": True,
                             "both_actual_source_spans_replayed": True,
                             "finite_cover_predicates_rechecked": True,
                             "coefficient_continuity_checked_at_true_knot": True,
                             "max_depth_per_span": PROOF_DEPTH, "max_nodes_per_span": PROOF_NODES,
                             "root_bracket_width": "1/64", "float_or_sample_authority": False},
            "summary": {"complete_original_source_witnesses": 15, "finite_simple_roots": 8,
                        "root_free_sources": 8, "nonzero_true_source_knots": 15,
                        "nonzero_exterior_endpoints": 30},
            "source_cases": sources, "preserved_negative_controls": deferred,
            "gates": {"PB-007-01": "OPEN", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                      "required_machining_operations": 26, "native_geometry_or_STEP_qualified": False,
                      "production_authorized": False},
        }
        bounded_bytes(report)
        return report
    except (MemoryError, OverflowError, RecursionError) as exc:
        raise Refusal("REPLAY_RESOURCE_REFUSAL") from exc


def _compare_with_replayed_bytes(candidate, reference):
    need(bounded_bytes(candidate) == reference, "REPORT_DISAGREES_WITH_FRESH_SOURCE_PROOF")
    return True


def validate_report(candidate):
    supplied = bounded_bytes(candidate)
    need(supplied == bounded_bytes(expected_report()), "REPORT_DISAGREES_WITH_FRESH_SOURCE_PROOF")
    return True


def read_report():
    return read_json(MACHINE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    if not args.write_report:
        parser.error("use --write-report, or run the dedicated --contract verifier")
    report = expected_report()
    MACHINE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
