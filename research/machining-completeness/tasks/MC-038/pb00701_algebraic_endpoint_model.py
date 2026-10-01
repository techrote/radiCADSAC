#!/usr/bin/env python3
"""V46: source-bound algebraic-irrational endpoints, NOT whole-span events.

Equality is a finite algebraic-coefficient Laurent test using Gelfond-Schneider.
Multiplicity is the minimum amplitude vanishing order. Only a proved nonzero
endpoint enters rational enclosure refinement. See the v46 proof/report.
"""
from __future__ import annotations

from fractions import Fraction as Q
from hashlib import sha256
from math import factorial
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as v45

q, require = v45.q, v45.require
RELATION = "EXACT_ALGEBRAIC_IRRATIONAL_PHASE_ENDPOINT_DECISION"
RESOURCE_ERRORS = (MemoryError, OverflowError, RecursionError)


def _same(a, b):
    # JSON equality is type-sensitive (True is not the integer 1).
    return v45._json(a) == v45._json(b)


def _digest(value):
    return sha256(v45._json(value).encode()).hexdigest()


def interval(lo, hi=None):
    lo, hi = q(lo), q(lo if hi is None else hi)
    require(lo <= hi, "reversed rational interval")
    return lo, hi


def iadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def imul(a, b):
    terms = [x * y for x in a for y in b]
    return min(terms), max(terms)


def iscale(a, scale):
    return imul(a, interval(scale))


def ipoly(coefficients, bounds):
    out = interval(0)
    for coefficient in reversed(coefficients):
        out = iadd(imul(out, bounds), interval(coefficient))
    return out


def _record(bounds):
    return [str(x) for x in bounds]


def alpha_interval(field, steps):
    require(type(steps) is int and steps >= 0, "invalid isolation step count")
    lo, hi = field.interval
    for _ in range(steps):
        mid = (lo + hi) / 2
        # Minimal polynomial is irreducible of degree >= 2: no rational zero.
        require(v45.engine.peval(field.minimal, mid) != 0, "invalid irrational embedding")
        if v45.engine.distinct_roots_open(field.minimal, lo, mid) == 1:
            hi = mid
        else:
            lo = mid
    return lo, hi


def arctan_reciprocal(denominator, n):
    require(type(denominator) is int and denominator > 1, "invalid arctan argument")
    require(type(n) is int and n > 0, "invalid series length")
    x = Q(1, denominator)
    power, total = x, Q(0)
    for k in range(n):
        total += (-1 if k % 2 else 1) * power / (2 * k + 1)
        power *= x * x
    next_term = (-1 if n % 2 else 1) * power / (2 * n + 1)
    bounds = tuple(sorted((total, total + next_term)))
    return {"denominator": denominator, "terms": n, "sum": str(total),
            "signed_next_term": str(next_term), "interval": _record(bounds)}


def machin_pi(n):
    a, b = arctan_reciprocal(5, n), arctan_reciprocal(239, n)
    bounds = iadd(iscale(tuple(map(q, a["interval"])), 16),
                  iscale(tuple(map(q, b["interval"])), -4))
    # Exact Gaussian integer identity; branch proof is documented in v46.
    return {"method": "MACHIN_ALTERNATING_SERIES", "terms": n,
            "atan_1_5": a, "atan_1_239": b, "interval": _record(bounds),
            "gaussian_identity": [114244, 114244],
            "identity": "pi=16*atan(1/5)-4*atan(1/239)"}


def trig_enclosure(radians, n, kind):
    require(type(n) is int and n > 0 and kind in ("COS", "SIN"), "invalid Taylor request")
    lo, hi = radians
    center, radius = (lo + hi) / 2, (hi - lo) / 2
    parity = 1 if kind == "SIN" else 0
    term, total = (center if parity else Q(1)), Q(0)
    for k in range(n):
        total += term
        degree = 2 * k + parity
        term *= -center * center / ((degree + 1) * (degree + 2))
    degree = 2 * (n - 1) + parity
    # Lagrange remainder for the actual Taylor degree; |f^(j)| <= 1.
    remainder = abs(center) ** (degree + 1) / factorial(degree + 1)
    error = remainder + radius  # Lipschitz-1 extension to the entire interval.
    bounds = max(Q(-1), total - error), min(Q(1), total + error)
    require(bounds[0] <= bounds[1], "inconsistent analytic enclosure")
    return {"kind": kind, "terms": n, "radians": _record(radians),
            "center": str(center), "radius": str(radius), "taylor_degree": degree,
            "taylor_sum": str(total), "lagrange_remainder": str(remainder),
            "lipschitz_constant": "1", "interval": _record(bounds)}


def _channels(field, cos_polys, sin_polys):
    channels = []
    for kind, source in (("COS", cos_polys), ("SIN", sin_polys)):
        for h in sorted(source):
            require(type(h) is int and h >= 0, "noncommensurate or invalid harmonic")
            p = v45.trim(source[h])
            if kind == "SIN" and h == 0:
                require(p == [0], "harmonic-zero sine must vanish")
                continue
            channels.append((kind, h, p))
    return channels


def _laurent(field, values):
    zero = field.element(0)
    table = {}
    for kind, harmonic, value in values:
        if harmonic == 0:
            re, im = table.get(0, (zero, zero))
            table[0] = re + value, im
        elif kind == "COS":
            for h in (-harmonic, harmonic):
                re, im = table.get(h, (zero, zero))
                table[h] = re + value * Q(1, 2), im
        else:
            for h, sign in ((-harmonic, 1), (harmonic, -1)):
                re, im = table.get(h, (zero, zero))
                table[h] = re, im + value * Q(sign, 2)
    return [{"power": h, "real": re.record(), "imaginary": im.record()}
            for h, (re, im) in sorted(table.items()) if not (re.is_zero() and im.is_zero())]


def algebraic_jets(field, cos_polys, sin_polys):
    """Finite exact equality and first nonzero jets; no trig/precision search."""
    channels = _channels(field, cos_polys, sin_polys)
    orders = []
    for kind, h, polynomial in channels:
        if polynomial == [0]:
            order = None
        else:
            work, order = polynomial, 0
            while field.element(work).is_zero():
                work, order = v45.engine.deriv(work), order + 1
                require(work != [0], "nonzero polynomial lost its finite jet")
        orders.append({"kind": kind, "harmonic": h, "order": order})
    finite = [item["order"] for item in orders if item["order"] is not None]
    if not finite:
        return {"status": "BLOCKED", "reason": "DEGENERATE_IDENTITY_ZERO",
                "physical_multiplicity": None}, []
    m = min(finite)
    values = [(kind, h, field.element(p)) for kind, h, p in channels]
    leading = []
    for kind, h, p in channels:
        for _ in range(m):
            p = v45.engine.deriv(p)
        leading.append((kind, h, field.element(p) * Q(1, factorial(m))))
    initial_laurent, leading_laurent = _laurent(field, values), _laurent(field, leading)
    require(bool(leading_laurent) and (bool(initial_laurent) == (m == 0)), "jet/Laurent inconsistency")
    return {"status": "ALGEBRAIC_JETS_CERTIFIED", "channel_orders": orders,
            "endpoint_laurent": initial_laurent, "first_nonzero_jet_laurent": leading_laurent,
            "physical_multiplicity": m, "all_lower_amplitude_jets_zero": True,
            "jet_normalization": "p^(m)(alpha)/m!"}, values


def sign_enclosure(field, values, phase_offset, phase_rate, n):
    """One finite, independently checkable rational enclosure; not a sign guess."""
    require(type(n) is int and n > 0, "invalid precision")
    root = alpha_interval(field, 2 * n)
    pi = machin_pi(n)
    pi_bounds = tuple(map(q, pi["interval"]))
    phase = iadd(interval(phase_offset), iscale(root, phase_rate))
    total, components = interval(0), []
    for kind, h, value in values:
        if value.is_zero():
            continue
        amplitude = ipoly(value.coefficients, root)
        component = {"kind": kind, "harmonic": h, "field_value": value.record(),
                     "amplitude_interval": _record(amplitude)}
        if h == 0:
            term = amplitude
        else:
            turns = iscale(phase, h)
            midpoint = (turns[0] + turns[1]) / 2
            shift = midpoint.numerator // midpoint.denominator
            reduced = iadd(turns, interval(-shift))
            radians = imul(iscale(pi_bounds, 2), reduced)
            trig = trig_enclosure(radians, n, kind)
            component.update({"integer_turn_shift": shift, "turn_interval": _record(reduced), "trig": trig})
            term = imul(amplitude, tuple(map(q, trig["interval"])))
        component["contribution_interval"] = _record(term)
        components.append(component)
        total = iadd(total, term)
    return {"method": "RATIONAL_MACHIN_TAYLOR_LAGRANGE_LIPSCHITZ", "precision": n,
            "alpha_interval": _record(root), "phase_interval": _record(phase),
            "pi": pi, "components": components, "total_interval": _record(total)}


def _separated(enclosure):
    lo, hi = map(q, enclosure["total_interval"])
    return "POSITIVE" if lo > 0 else "NEGATIVE" if hi < 0 else None


def _endpoint_header(material, split):
    field_record = split["field"]
    field = v45.RealField(tuple(field_record["minimal_polynomial"]),
                          tuple(map(q, field_record["isolating_interval"])),
                          field_record["root_index_in_open_unit_interval"])
    left, right = map(q, material["parent_source_interval"])
    phase = material["phase_turn_law"]
    offset, rate = q(phase["offset"]) + q(phase["rate"]) * left, q(phase["rate"]) * (right - left)
    require(rate != 0, "zero phase rate belongs to predecessor")
    cos = {int(h): p for h, p in material["cos_polynomials"].items()}
    sin = {int(h): p for h, p in material["sin_polynomials"].items()}
    alpha = field.element([0, 1])
    tau = field.element(offset) + alpha * rate
    require(len(tau.coefficients) > 1, "rational phase must not enter transcendence route")
    jets, values = algebraic_jets(field, cos, sin)
    if jets["status"] != "ALGEBRAIC_JETS_CERTIFIED":
        return jets, field, values, offset, rate
    m = jets["physical_multiplicity"]
    header = {
        "status": "ENDPOINT_CERTIFIED", "method": RELATION,
        "source_parameter_id": material["source_parameter_id"],
        "source_binding_sha256": _digest(material), "bisection_binding_sha256": _digest(split),
        "parent_source_interval": list(material["parent_source_interval"]), "field": field.record(),
        "source_cut": (field.element(left) + alpha * (right - left)).record(),
        "phase_turn": tau.record(),
        "transcendence": {"theorem": "GELFOND_SCHNEIDER_NIVEN_10_1",
                           "base": "-1", "exponent": (tau * 2).record(), "chosen_logarithm": "i*pi",
                           "coefficient_field": "Q(alpha,i)", "exponent_algebraic_irrational": True},
        "jets": jets, "physical_multiplicity": m,
        "global_jet_scale": str(Q(1) / (right - left) ** m),
        "relation": "ZERO" if m else "NONZERO_PENDING_ENCLOSURE",
        "sign_change": bool(m % 2), "analytic_cut_consumed": False,
        "whole_span_certified": False,
    }
    return header, field, values, offset, rate


def _decide_endpoint(material, split):
    # material/split must be regenerated by v45; raw caller records are not a source.
    header, field, values, offset, rate = _endpoint_header(material, split)
    if header.get("status") != "ENDPOINT_CERTIFIED" or header["physical_multiplicity"]:
        return header
    n = 1
    while True:
        bounds = sign_enclosure(field, values, offset, rate, n)
        relation = _separated(bounds)
        if relation:
            return {**header, "relation": relation, "sign_certificate": bounds}
        n *= 2  # No depth/precision cap; algebraic NONZERO proof supplies termination.


def resource_refusal(stage):
    return {"status": "RESOURCE_REFUSAL", "reason": "PB00701_V46_EXACT_RESOURCE_REFUSAL",
            "stage": stage, "is_truth_value": False, "analytic_cut_consumed": False}


def _decide_representation(representation):
    if representation.get("status") != "REPRESENTATION_CERTIFIED":
        return representation
    material = representation["source_material"]
    if q(material["phase_turn_law"]["rate"]) == 0:
        return {"status": "NOT_APPLICABLE", "reason": "RATIONAL_PHASE_PREDECESSOR_OWNERSHIP",
                "analytic_cut_consumed": False}
    endpoints = [_decide_endpoint(material, split)
                 for split in representation["independent_single_cut_bisections"]]
    return {"status": "ENDPOINTS_CERTIFIED" if endpoints and all(e["status"] == "ENDPOINT_CERTIFIED" for e in endpoints) else "BLOCKED",
            "method": RELATION, "source_binding_sha256": _digest(material), "endpoints": endpoints,
            "analytic_cut_consumed": False, "whole_span_certified": False}


def build_source_endpoint_evidence(*args):
    """Low-level exact lowered-source adapter; no arbitrary certificate is accepted."""
    try:
        return _decide_representation(v45.build_orientation_child_maps(*args))
    except RESOURCE_ERRORS as exc:
        return resource_refusal(type(exc).__name__)


def decide_required_event_endpoints(spec):
    """Run complete predecessor first; attach only unresolved endpoint evidence."""
    try:
        represented = v45.represent_required_event_children(spec)
        baseline = represented["predecessor_event_result"]
        if represented["status"] != "REPRESENTATION_CERTIFIED":
            return {"status": represented["status"], "method": RELATION,
                    "predecessor_event_result": baseline, "span_endpoint_evidence": [],
                    "analytic_cut_consumed": False}
        evidence = [{"source_interval": item["source_interval"],
                     "endpoint_evidence": _decide_representation(item["representation"])}
                    for item in represented["span_representations"]]
        statuses = {item["endpoint_evidence"]["status"] for item in evidence}
        status = ("RESOURCE_REFUSAL" if "RESOURCE_REFUSAL" in statuses else
                  "ENDPOINTS_CERTIFIED" if statuses == {"ENDPOINTS_CERTIFIED"} else "BLOCKED")
        return {"status": status, "method": RELATION, "predecessor_event_result": baseline,
                "span_endpoint_evidence": evidence, "analytic_cut_consumed": False}
    except RESOURCE_ERRORS as exc:
        return resource_refusal(type(exc).__name__)


def classify_required_analytic_event(spec):
    return v45.classify_required_analytic_event(spec)
