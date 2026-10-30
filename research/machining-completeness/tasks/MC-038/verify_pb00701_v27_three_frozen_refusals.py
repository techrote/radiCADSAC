#!/usr/bin/env python3
"""Three original v54 V27-refused sources: exact case-specific physical events.

The source proofs are in pb00701-v27-three-frozen-refusals-research.md.
DETERMINISTIC_MODEL only: no generic V27 admission, native geometry, or MC-B gate.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

CORPUS = "5841c331579489b25caef38cd412bdbf286f9134"
AUDITOR = "12c6efeb667a954ffc5a7e27849ae815d466580a"
DOMAIN = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTHORITY = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
SCHEMA = "radicadsac-mc038-v27-three-frozen-sources/1.0"
MACHINE = HERE / "pb00701-v27-three-frozen-refusals-witness.json"
V27 = "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"
V8 = "PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION"
REFUSAL = "V27_CHILD_NOT_CERTIFIED"

H = "harvested:verify_pb00701_v9:1a5fd052a155"
T0 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0"
T100 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100"

# Canonical SHA-256 of the *original source spec* (not a later reconstruction).
CASES = {
    H: {
        "kind": "HARVESTED", "origin": "verify_pb00701_v9",
        "source_sha256": "710259612833cfe40e73ae528e0d0e944a87123c9bb4b3f4f76cef33c45bcf4d",
        "phase": ("0", "1/8"), "interval": ("0", "1"),
        "owners": [[V27, "BLOCKED", REFUSAL]],
        "cos": {"0": [("0", "1")]}, "sin": {"1": [("1", "0")]},
    },
    T0: {
        "kind": "COMPOSITE_TAIL", "origin": "verify_pb00701_v8",
        "source_sha256": "9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af",
        "phase": ("-1/4", "1/2"), "interval": ("0", "2"),
        "owners": [[V8, "CERTIFIED", None], [V27, "BLOCKED", REFUSAL]],
        "cos": {"0": [("0", "0"), ("0", "0")]},
        "sin": {"1": [("-1/2", "1"), ("1/2", "0")]},
    },
    T100: {
        "kind": "COMPOSITE_TAIL", "origin": "verify_pb00701_v8",
        "source_sha256": "8e3af5a5e74c3fc3f364607f5c3c4b03cd1adc2e2dd6e16bfc03ddf870de0d2b",
        "phase": ("-1/4", "1/2"), "interval": ("0", "2"),
        "owners": [[V8, "CERTIFIED", None], [V27, "BLOCKED", REFUSAL]],
        "cos": {"0": [("0", "0"), ("-100", "100")]},
        "sin": {"1": [("-1/2", "1"), ("1/2", "0")]},
    },
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def pin(path, sha):
    require(path.is_file(), "missing pinned source: " + str(path))
    data = path.read_bytes()
    found = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    require(found == sha, "pinned Git blob mismatch: " + str(path))


def exact(s):
    require(type(s) is str, "non-string coefficient")
    try:
        q = Q(s)
    except (ValueError, ZeroDivisionError, TypeError) as e:
        raise ValueError("invalid rational coefficient") from e
    require(str(q) == s, "noncanonical rational coefficient")
    return q


def lower_bspline(spline, endpoints):
    """Independent original degree-0/1, fully-clamped B-spline to power basis.

    Returns exact global-source-coordinate polynomials (constant, slope).
    Does not execute a historical V8/V27 route or take a supplied root count.
    """
    require(type(spline) is dict and
            set(spline) == {"degree", "knots", "controls"},
            "unsupported original B-spline shape")
    degree = spline["degree"]
    require(type(degree) is int and degree in (0, 1), "unsupported degree")
    require(type(spline["knots"]) is list and
            spline["knots"] == [str(q) for q in endpoints for _ in range(degree + 1)],
            "source knots or multiplicity altered")
    controls = spline["controls"]
    require(type(controls) is list and
            len(controls) == (len(endpoints) - 1) * (degree + 1),
            "source control count changed")
    coeffs = [exact(x) for x in controls]
    pieces = []
    for i, (a, b) in enumerate(zip(endpoints, endpoints[1:])):
        width = b - a
        require(width > 0, "nonpositive original source span")
        c = coeffs[i * (degree + 1)]
        if degree == 0:
            pieces.append((c, Q(0)))
        else:
            d = coeffs[i * 2 + 1] - c
            pieces.append((c - d * a / width, d / width))
    return pieces


def inspect_original(row):
    require(type(row) is dict and set(row) == {"id", "origin", "kind", "spec", "expected"},
            "source archive record shape drift")
    name = row["id"]
    require(type(name) is str and name in CASES, "unregistered original source")
    meta = CASES[name]
    require(row["origin"] == meta["origin"] and row["kind"] == meta["kind"],
            "original source provenance changed")
    require(row["expected"] == {
        "id": name,
        "observed": {"status": "BLOCKED", "spans": meta["owners"]},
        "v54_disposition": "BLOCKED"
    }, "historical V27 refusal/owner/disposition changed")

    spec = row["spec"]
    require(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"
    }, "original source grammar fields changed")
    require(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
            spec["source_parameter_id"] == "source-time-t", "source grammar/parameter changed")
    raw = json.dumps(spec, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    require(hashlib.sha256(raw).hexdigest() == meta["source_sha256"],
            "original source SHA-256 mismatch")
    lo, hi = (exact(spec[k]) for k in ("parameter_lo", "parameter_hi"))
    offset, rate = (exact(spec[k]) for k in ("phase_turn_offset", "phase_turn_rate"))
    require((lo, hi) == tuple(map(exact, meta["interval"])) and
            (offset, rate) == tuple(map(exact, meta["phase"])),
            "source interval/phase drift")
    endpoints = [Q(0), Q(1)] if name == H else [Q(0), Q(1), Q(2)]
    require((lo, hi) == (endpoints[0], endpoints[-1]), "source span coverage drift")
    lowered = {}
    for channel in ("cos", "sin"):
        splines = spec[channel + "_splines"]
        require(type(splines) is dict and set(splines) == set(meta[channel]),
                "harmonic inventory changed")
        lowered[channel] = {}
        for harmonic, spline in splines.items():
            require(harmonic.isdecimal() and str(int(harmonic)) == harmonic,
                    "noncanonical harmonic index")
            pieces = lower_bspline(spline, endpoints)
            expected = [tuple(map(exact, p)) for p in meta[channel][harmonic]]
            require(pieces == expected, "original harmonic polynomial changed")
            lowered[channel][harmonic] = pieces
    return {"name": name, "lo": lo, "hi": hi, "offset": offset,
            "rate": rate, "endpoints": endpoints, "channels": lowered,
            "source_sha256": meta["source_sha256"]}


def cardinal_sin(turn):
    """Only certified exact rational quarter-turn values are evaluated."""
    residue = turn % 1
    table = {Q(0): Q(0), Q(1, 4): Q(1),
             Q(1, 2): Q(0), Q(3, 4): Q(-1)}
    require(residue in table, "no cardinal exact source-point authority")
    return table[residue]


def exact_value_at(source, t, side=None):
    """Exact *source-coordinate* values at cardinal-phase points only."""
    require(source["lo"] <= t <= source["hi"], "point outside original source")
    ends = source["endpoints"]
    candidates = [i for i in range(len(ends) - 1) if ends[i] <= t <= ends[i + 1]]
    if side == "left":
        candidates = candidates[:1]
    elif side == "right":
        candidates = candidates[-1:]
    require(candidates, "no original piece at point")
    values = []
    for i in candidates:
        cos = source["channels"]["cos"]["0"][i]
        sine = source["channels"]["sin"]["1"][i]
        values.append(cos[0] + cos[1] * t +
                      (sine[0] + sine[1] * t) *
                      cardinal_sin(source["offset"] + source["rate"] * t))
    require(all(v == values[0] for v in values), "source knot discontinuity")
    return values[0]


def derivative_margin(slope):
    """Exact sufficient bound for A*u + 1/2*cos(pi*u) on u in [0,1].

    D = A - (pi/2)*sin(pi*u) >= A - pi/2 > A - 2, since 0<pi<4.
    Failed bound is refusal, not a physical negative/nonmonotonicity verdict.
    """
    require(type(slope) is Q, "nonrational derivative slope")
    require(slope > 2, "RESOURCE_REFUSAL: insufficient strict slope margin")
    return slope - 2


def prove_bound_source(source):
    name = source["name"]
    if name == H:
        require(exact_value_at(source, Q(0)) == 0, "wrong harvested endpoint zero")
        # t+sin(pi*t/4) > 0 for every 0<t<=1; derivative at t=0:
        # 1+pi/4 > 0. The only root is one-sided simple at t=0.
        return {
            "events": [{"t": "0", "location": "SOURCE_LEFT_ENDPOINT",
                        "one_sided_order": 1, "kind": "SIMPLE_BOUNDARY",
                        "right_sign": "POSITIVE"}],
            "strict_span_open_root_counts": [0],
            "maximal_open_signs": ["POSITIVE"],
            "source_endpoint_values": {"0": "0", "1": "1+sqrt(2)/2"},
            "physical_formula": ["t + sin(pi*t/4) on 0<=t<=1"],
        }

    require(name in (T0, T100), "unrecognized bounded source")
    require(exact_value_at(source, Q(0)) == Q(1, 2) and
            exact_value_at(source, Q(1, 2)) == 0 and
            exact_value_at(source, Q(1)) == Q(1, 2),
            "V8 shared first-span values or knot value wrong")
    # F=(t-1/2)sin(pi*(t-1/2)) on [0,1].
    # Its only zero t=1/2 has quadratic order: F''(1/2)=2*pi>0;
    # F>0 on both sides since x and sin(pi*x) share sign for |x|<=1/2.
    events = [{"t": "1/2", "location": "SPAN_OPEN",
               "order": 2, "kind": "TOUCHING",
               "left_sign": "POSITIVE", "right_sign": "POSITIVE"}]
    if name == T0:
        require(exact_value_at(source, Q(3, 2)) == 0 and
                exact_value_at(source, Q(2)) == Q(-1, 2),
                "tail0 physical crossing/end sign changed")
        # F=1/2*cos(pi*(t-1)) on [1,2], unique simple decreasing
        # crossing at 3/2, derivative there -pi/2 < 0.
        events.append({"t": "3/2", "location": "SPAN_OPEN",
                       "order": 1, "kind": "CROSSING",
                       "left_sign": "POSITIVE", "right_sign": "NEGATIVE"})
        return {
            "events": events, "strict_span_open_root_counts": [1, 1],
            "maximal_open_signs": ["POSITIVE", "POSITIVE", "NEGATIVE"],
            "source_endpoint_values": {"0": "1/2", "1": "1/2", "2": "-1/2"},
            "physical_formula": [
                "(t-1/2)*sin(pi*(t-1/2)) on 0<=t<=1",
                "1/2*cos(pi*(t-1)) on 1<=t<=2",
            ],
            "source_knot": {"t": "1", "zero": False, "value": "1/2"},
        }

    require(exact_value_at(source, Q(3, 2)) == 50 and
            exact_value_at(source, Q(2)) == Q(199, 2),
            "tail100 exact source values changed")
    c0_tail = source["channels"]["cos"]["0"][1]
    slope = c0_tail[1]
    require(slope == 100 and c0_tail[0] == -100 and
            derivative_margin(slope) == 98,
            "tail100 strict derivative margin changed")
    # F=100*u+1/2*cos(pi*u), u=t-1 on [0,1].
    # F'(u)>=100-pi/2>98>0; F(0)=1/2>0, hence no tail root.
    return {
        "events": events, "strict_span_open_root_counts": [1, 0],
        "maximal_open_signs": ["POSITIVE", "POSITIVE"],
        "source_endpoint_values": {"0": "1/2", "1": "1/2", "2": "199/2"},
        "physical_formula": [
            "(t-1/2)*sin(pi*(t-1/2)) on 0<=t<=1",
            "100*(t-1)+1/2*cos(pi*(t-1)) on 1<=t<=2",
        ],
        "strict_tail_derivative_lower": "98",
        "source_knot": {"t": "1", "zero": False, "value": "1/2"},
    }


def load_frozen():
    pin(HERE / "pb00701-finite-owner-corpus-v54.json", CORPUS)
    pin(HERE / "verify_pb00701_post_v54_frontier.py", AUDITOR)
    pin(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
        DOMAIN)
    pin(ROOT / "handoffs/current-authority.json", AUTHORITY)
    import verify_pb00701_post_v54_frontier as audit
    corpus, inventory, boundary = audit.inputs()
    census = audit.audit(corpus, inventory, boundary)
    require(census["cases"] == 121 and
            census["v54_dispositions"]["BLOCKED"] == 20 and
            census["v54_dispositions"][
                "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
            "historical census drift")
    auth = json.loads((ROOT / "handoffs/current-authority.json").read_text())
    domain = json.loads((ROOT / "research/machining-completeness/tasks/MC-002/"
                         "domain-contract-v1.json").read_text())
    require(auth["production_authorized"] is False and
            auth["capability_status"] == "NOT_ESTABLISHED",
            "production/MC-1 authority was promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "original domain denominator changed")
    rows = {r["id"]: r for r in corpus["cases"] if r.get("id") in CASES}
    require(len(rows) == 3 and len(set(rows)) == 3,
            "missing/duplicated frozen V27 source cases")
    return rows


def expected_report(rows):
    proofs = {}
    for name in (H, T0, T100):
        source = inspect_original(rows[name])
        proofs[name] = {
            "original_source_sha256": source["source_sha256"],
            "historical_v54_status": "BLOCKED:V27_CHILD_NOT_CERTIFIED",
            "physical_event_proof": prove_bound_source(source),
        }
    return {
        "schema": SCHEMA,
        "task": "MC-038",
        "evidence_class": "DETERMINISTIC_MODEL",
        "original_corpus_git_blob": CORPUS,
        "historical_v54": {
            "total_source_cases": 121, "route_refusals": 20,
            "missing_ordered_premises": 30, "dispositions_unchanged": True,
        },
        "supplemental_only": {
            "source_specific_new_witnesses": 3,
            "remaining_in_this_three_claim_overlay": {
                "route_refusals": 17, "missing_ordered_premises": 30,
                "original_cases": 121,
            },
            "not_exhaustive_post_v54_census": True,
            "generic_v27_route_repaired": False,
        },
        "sources": proofs,
        "gates": {
            "pb00701_closed": False, "pb00702_closed": False,
            "pb00703_closed": False, "pb00704_closed": False,
            "mc_b_established": False, "mc1_established": False,
            "native_material_or_step_qualified": False,
            "production_authorized": False,
        },
    }


def bounded_canonical_json(obj):
    """Reject untrusted cycles/depth/huge lists BEFORE serialization."""
    stack = [(obj, 0, False)]
    live = set()
    count = 0
    while stack:
        node, depth, leaving = stack.pop()
        if leaving:
            live.remove(id(node))
            continue
        count += 1
        require(count <= 4096 and depth <= 18,
                "RESOURCE_REFUSAL: report depth/item budget")
        if type(node) in (dict, list):
            require(id(node) not in live, "RESOURCE_REFUSAL: cyclic report")
            require(len(node) <= 128, "RESOURCE_REFUSAL: oversized report container")
            live.add(id(node))
            stack.append((node, depth, True))
            if type(node) is dict:
                for key, value in node.items():
                    require(type(key) is str and len(key) <= 256,
                            "RESOURCE_REFUSAL: report key")
                    stack.append((value, depth + 1, False))
            else:
                stack.extend((value, depth + 1, False) for value in node)
        elif type(node) is str:
            require(len(node) <= 1024, "RESOURCE_REFUSAL: oversized report string")
        elif type(node) is int:
            require(abs(node) < 10 ** 64, "RESOURCE_REFUSAL: oversized report integer")
        else:
            require(node is None or type(node) is bool,
                    "invalid report scalar (including float)")
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    require(len(raw) <= 65536, "RESOURCE_REFUSAL: report byte budget")
    return raw


def verify_report(report, rows):
    expected = expected_report(rows)
    require(bounded_canonical_json(report) == bounded_canonical_json(expected),
            "forged/mismatched proof report")
    return expected


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_frozen()
        cls.proofs = expected_report(cls.rows)

    def test_01_frozen_sources_and_proof(self):
        self.assertEqual(len(self.rows), 3)
        self.assertEqual(verify_report(self.proofs, self.rows), self.proofs)

    def test_02_harvested_boundary_root(self):
        p = self.proofs["sources"][H]["physical_event_proof"]
        self.assertEqual(p["strict_span_open_root_counts"], [0])
        self.assertEqual(p["events"][0]["one_sided_order"], 1)

    def test_03_exact_shared_v8_tangency(self):
        for name in (T0, T100):
            src = inspect_original(self.rows[name])
            self.assertEqual(exact_value_at(src, Q(1, 2)), 0)
            self.assertEqual(exact_value_at(src, Q(1)), Q(1, 2))
            self.assertEqual(prove_bound_source(src)["events"][0]["order"], 2)

    def test_04_separate_tail_crossing_and_positive_ramp(self):
        self.assertEqual(len(self.proofs["sources"][T0]["physical_event_proof"]["events"]), 2)
        self.assertEqual(len(self.proofs["sources"][T100]["physical_event_proof"]["events"]), 1)
        self.assertEqual(derivative_margin(Q(100)), Q(98))

    def test_05_source_coefficient_mutations_refuse(self):
        for name in CASES:
            changed = copy.deepcopy(self.rows[name])
            channel = "sin_splines"
            spline = next(iter(changed["spec"][channel].values()))
            spline["controls"][0] = "9"
            with self.assertRaises(ValueError):
                inspect_original(changed)

    def test_06_source_phase_provenance_refuse(self):
        for name in CASES:
            for key, value in (("phase_turn_rate", "0"),
                               ("source_parameter_id", "substituted")):
                changed = copy.deepcopy(self.rows[name])
                changed["spec"][key] = value
                with self.assertRaises(ValueError):
                    inspect_original(changed)

    def test_07_historical_v27_refusals_retained(self):
        for name in CASES:
            changed = copy.deepcopy(self.rows[name])
            changed["expected"]["observed"]["spans"][-1][1] = "CERTIFIED"
            with self.assertRaises(ValueError):
                inspect_original(changed)

    def test_08_knots_degrees_and_noncanonical_rationals_refuse(self):
        for name in CASES:
            for key, value in (("degree", 3), ("knots", ["0", "1"]),
                               ("controls", ["0.0"])):
                changed = copy.deepcopy(self.rows[name])
                spline = next(iter(changed["spec"]["sin_splines"].values()))
                spline[key] = value
                with self.assertRaises(ValueError):
                    inspect_original(changed)

    def test_09_forged_multiplicity_and_sign_refuse(self):
        for name in (H, T0, T100):
            changed = copy.deepcopy(self.proofs)
            ev = changed["sources"][name]["physical_event_proof"]["events"][0]
            key = "one_sided_order" if name == H else "order"
            ev[key] += 1
            with self.assertRaises(ValueError):
                verify_report(changed, self.rows)
        changed = copy.deepcopy(self.proofs)
        changed["sources"][T0]["physical_event_proof"]["maximal_open_signs"][-1] = "POSITIVE"
        with self.assertRaises(ValueError):
            verify_report(changed, self.rows)

    def test_10_count_and_gate_promotion_refuse(self):
        for location, key, bad in (
            ("historical_v54", "route_refusals", 17),
            ("supplemental_only", "generic_v27_route_repaired", True),
            ("gates", "mc_b_established", True),
            ("gates", "production_authorized", True),
        ):
            changed = copy.deepcopy(self.proofs)
            changed[location][key] = bad
            with self.assertRaises(ValueError):
                verify_report(changed, self.rows)

    def test_11_bad_slopes_fail_closed_not_event_claim(self):
        # At A=1/4 the synthetic V8 second endpoint is A-1/2 < 0.
        self.assertEqual(Q(1, 4) - Q(1, 2), Q(-1, 4))
        for a in (Q(1, 4), Q(2), Q(0)):
            with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
                derivative_margin(a)
        self.assertGreater(derivative_margin(Q(2) + Q(1, 2 ** 128)), 0)
        with self.assertRaises(ValueError):
            derivative_margin(2.1)

    def test_12_identity_zero_substitution_refused(self):
        changed = copy.deepcopy(self.rows[T0])
        changed["spec"]["sin_splines"]["1"]["controls"] = ["0"] * 4
        with self.assertRaises(ValueError):
            inspect_original(changed)

    def test_13_untrusted_resource_envelope(self):
        samples = [{}, {"x": float("nan")}, {"x": [1] * 129},
                   {"x": "v" * 65537}, {"x": 10 ** 100}]
        circular = {}
        circular["self"] = circular
        samples.append(circular)
        deep = root = {}
        for _ in range(20):
            child = {}
            root["next"] = child
            root = child
        samples.append(deep)
        for obj in samples:
            with self.assertRaises(ValueError):
                verify_report(obj, self.rows)

    def test_14_exact_quarter_turn_boundary_semantics(self):
        src = inspect_original(self.rows[T0])
        with self.assertRaisesRegex(ValueError, "no cardinal"):
            exact_value_at(src, Q(1, 3))
        self.assertEqual(exact_value_at(src, Q(1), "left"),
                         exact_value_at(src, Q(1), "right"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("require --contract and/or --self-test")
    if args.contract:
        report = json.loads(MACHINE.read_text())
        verify_report(report, load_frozen())
        print("PASS: 3 distinct original frozen V27-refused sources; exact physical")
        print("events/one-sided orders/signs; historical 20+30 remain unchanged")
        print("SUPPLEMENTAL-ONLY 3-witness overlay: route cases 20 -> 17;")
        print("PB-007-01 OPEN; MC-B/MC-1 NOT_ESTABLISHED; no native/STEP claim")
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
