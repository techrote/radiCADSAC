#!/usr/bin/env python3
"""V45 exact Q(alpha) child representation; not analytic event certification.

Rational-polynomial division/gcd/Sturm authority is the preserved MC-032 engine.
A square-free defining polynomial is NOT assumed irreducible. Finite Kronecker
factorization selects the minimal factor at the certified real root first.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import importlib.util
from itertools import product
import json
from math import gcd, isqrt, lcm
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
_engine_spec = importlib.util.spec_from_file_location(
    "pb00701_v45_mc032", HERE.parent / "MC-032" / "event_engine.py"
)
assert _engine_spec is not None and _engine_spec.loader is not None
engine = importlib.util.module_from_spec(_engine_spec)
_engine_spec.loader.exec_module(engine)
q, trim = engine.q, engine._trim
V45_RELATION = "EXACT_REAL_ALGEBRAIC_CHILD_MAP_REPRESENTATION"
ENDPOINT_BLOCKER = "ALGEBRAIC_IRRATIONAL_PHASE_ENDPOINT_AUTHORITY_NOT_ESTABLISHED"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def padd(a, b):
    out = [Fraction(0)] * max(len(a), len(b))
    for p in (a, b):
        for i, c in enumerate(p):
            out[i] += q(c)
    return trim(out)


def pscale(a, b):
    return trim([q(c) * q(b) for c in a])


def pmul(a, b):
    a, b = trim(a), trim(b)
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def primitive(p) -> tuple[int, ...]:
    p = trim(p)
    denominator = lcm(*(x.denominator for x in p))
    values = [int(x * denominator) for x in p]
    content = gcd(*values)
    if not content:
        return (0,)
    if values[-1] < 0:
        content = -content
    return tuple(x // content for x in values)


def _signed_divisors(n: int) -> tuple[int, ...]:
    require(n != 0, "divisors require a nonzero integer")
    n = abs(n)
    small = [d for d in range(1, isqrt(n) + 1) if n % d == 0]
    positive = sorted(set(small + [n // d for d in small]))
    return tuple(x for d in positive for x in (d, -d))


def _interpolate(points, values):
    result = [Fraction(0)]
    for i, (xi, yi) in enumerate(zip(points, values)):
        basis, denominator = [Fraction(1)], Fraction(1)
        for j, xj in enumerate(points):
            if i != j:
                basis = pmul(basis, [-xj, 1])
                denominator *= xi - xj
        result = padd(result, pscale(basis, Fraction(yi) / denominator))
    return result


@lru_cache(maxsize=128)
def _factor_primitive(p: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Complete finite factorization over Q, with no refinement/resource truth cap.

For a degree-k integer factor g, g(x_i) divides p(x_i) at k+1 nonroot
integer points. Enumerating all signed divisors and interpolating is finite
and exhaustive (Gauss's lemma). Recursive factor degrees strictly decrease.
Quadratic discriminants avoid unnecessary enumeration for the usual cuts.
    """
    n = len(p) - 1
    if n <= 1:
        return (p,)
    if n == 2:
        c, b, a = p
        discriminant = b * b - 4 * a * c
        if discriminant < 0 or isqrt(discriminant) ** 2 != discriminant:
            return (p,)
        root = Fraction(-b + isqrt(discriminant), 2 * a)
        g = primitive([-root, 1])
        quotient, remainder = engine.pdivmod(p, g)
        require(remainder == [0], "quadratic exact division failed")
        return tuple(sorted((g, primitive(quotient))))
    for k in range(1, n // 2 + 1):
        points, divisors, j = [], [], 0
        while len(points) < k + 1:
            x = 0 if j == 0 else (j + 1) // 2 * (1 if j % 2 else -1)
            j += 1
            value = engine.peval(p, x)
            if value:
                points.append(x)
                divisors.append(_signed_divisors(int(value)))
        for values in product(*divisors):
            candidate = _interpolate(points, values)
            if engine.degree(candidate) != k or any(c.denominator != 1 for c in candidate):
                continue
            g = primitive(candidate)
            quotient, remainder = engine.pdivmod(p, g)
            if remainder == [0]:
                return tuple(sorted(_factor_primitive(g) + _factor_primitive(primitive(quotient))))
    return (p,)


def irreducible_factors(p):
    return _factor_primitive(primitive(p))


def _multiplicity(source, lo, hi) -> int:
    current, count = trim(source), 0
    while engine.degree(current) > 0 and engine.distinct_roots_open(current, lo, hi):
        count += 1
        current = engine.pgcd(current, engine.deriv(current))
    return count


def _canonical_interval(p, index):
    lo, hi = Fraction(0), Fraction(1)
    count = engine.distinct_roots_open(p, lo, hi)
    require(0 <= index < count, "invalid real-root index")
    while count != 1 or lo == 0 or hi == 1:
        mid = (lo + hi) / 2
        require(engine.peval(p, mid) != 0, "irrational root cannot equal a rational midpoint")
        left_count = engine.distinct_roots_open(p, lo, mid)
        if index < left_count:
            hi, count = mid, left_count
        else:
            lo, index, count = mid, index - left_count, count - left_count
    return lo, hi


@dataclass(frozen=True)
class RealField:
    """Use from_source_certificate at the source boundary, not caller field data."""
    minimal: tuple[int, ...]
    interval: tuple[Fraction, Fraction]
    root_index: int

    def __post_init__(self):
        require(type(self.root_index) is int and self.root_index >= 0, "invalid embedding index")
        require(len(self.minimal) >= 3 and primitive(self.minimal) == self.minimal, "noncanonical field polynomial")
        require(irreducible_factors(self.minimal) == (self.minimal,), "a reducible modulus is not a field")
        require(tuple(map(q, self.interval)) == _canonical_interval(self.minimal, self.root_index), "noncanonical real embedding")

    @classmethod
    def from_source_certificate(cls, source, certificate):
        source = trim(source)
        require(source != [0], "zero source polynomial has no isolated orientation cut")
        defining = primitive(engine.square_free(source))
        require(certificate.get("root_type") == "REAL_ALGEBRAIC_IRRATIONAL", "wrong root type")
        require(primitive(certificate["source_polynomial_primitive"]) == primitive(source), "source polynomial mismatch")
        require(primitive(certificate["defining_square_free_polynomial"]) == defining and tuple(certificate["defining_square_free_polynomial"]) == defining, "defining polynomial mismatch")
        lo, hi = map(q, certificate["isolating_interval"])
        require(0 < lo < hi < 1, "algebraic cut must be strictly interior")
        require(engine.peval(defining, lo) != 0 and engine.peval(defining, hi) != 0, "isolation endpoint is a root")
        require(engine.distinct_roots_open(defining, lo, hi) == 1, "isolation is not source-root unique")
        require(type(certificate["multiplicity"]) is int, "multiplicity must be integer")
        require(certificate["multiplicity"] == _multiplicity(source, lo, hi), "source multiplicity mismatch")
        for flag in ("binary_float_used", "epsilon_used", "sampling_used", "approximate_root_used"):
            require(certificate.get(flag) is False, "non-exact root evidence")
        proof = certificate["unique_root_proof"]
        require(proof.get("method") == "EXACT_STURM_OPEN_INTERVAL_COUNT", "wrong unique-root method")
        require(type(proof.get("sturm_open_root_count")) is int and proof["sturm_open_root_count"] == 1, "forged root count")
        require(proof.get("rational_endpoints_are_not_roots") is True, "wrong endpoint evidence")
        selected = [p for p in irreducible_factors(defining) if engine.distinct_roots_open(p, lo, hi) == 1]
        require(len(selected) == 1 and len(selected[0]) >= 3, "root is not algebraic irrational")
        minimal = selected[0]
        index = engine.distinct_roots_open(minimal, 0, lo)
        return cls(minimal, _canonical_interval(minimal, index), index)

    def element(self, coefficients):
        if isinstance(coefficients, Element):
            require(coefficients.field == self, "different real field embeddings")
            return coefficients
        if isinstance(coefficients, (int, str, Fraction, float, bool)):
            coefficients = [q(coefficients)]
        remainder = engine.pdivmod(trim(coefficients), self.minimal)[1]
        return Element(self, tuple(remainder))

    def record(self):
        return {
            "minimal_polynomial": list(self.minimal),
            "isolating_interval": [str(x) for x in self.interval],
            "root_index_in_open_unit_interval": self.root_index,
            "authority": "FINITE_EXACT_KRONECKER_FACTORIZATION_AND_MC032_STURM",
        }


@dataclass(frozen=True)
class Element:
    field: RealField
    coefficients: tuple[Fraction, ...]

    def __post_init__(self):
        require(all(isinstance(x, Fraction) for x in self.coefficients), "non-exact field coefficient")
        require(tuple(engine.pdivmod(self.coefficients, self.field.minimal)[1]) == self.coefficients, "unreduced field coefficient")

    def __add__(self, other):
        other = self.field.element(other)
        return self.field.element(padd(self.coefficients, other.coefficients))

    def __neg__(self):
        return self.field.element(pscale(self.coefficients, -1))

    def __sub__(self, other):
        return self + (-self.field.element(other))

    def __mul__(self, other):
        other = self.field.element(other)
        return self.field.element(pmul(self.coefficients, other.coefficients))

    def __pow__(self, power):
        require(type(power) is int and power >= 0, "power must be a nonnegative integer")
        result, base = self.field.element(1), self
        while power:
            if power % 2:
                result = result * base
            base, power = base * base, power // 2
        return result

    def inverse(self):
        require(not self.is_zero(), "cannot invert zero field element")
        a, b = trim(self.field.minimal), list(self.coefficients)
        s0, s1 = [Fraction(0)], [Fraction(1)]
        while b != [0]:
            quotient, remainder = engine.pdivmod(a, b)
            a, b = b, remainder
            s0, s1 = s1, padd(s0, pscale(pmul(quotient, s1), -1))
        require(engine.degree(a) == 0, "minimal polynomial field invariant failed")
        return self.field.element(pscale(s0, 1 / a[0]))

    def is_zero(self):
        return self.coefficients == (Fraction(0),)

    def sign(self):
        if self.is_zero():
            return 0
        lo, hi = self.field.interval
        while True:
            lower = upper = Fraction(0)
            for c in reversed(self.coefficients):
                products = (lower * lo, lower * hi, upper * lo, upper * hi)
                lower, upper = min(products) + c, max(products) + c
            if lower > 0:
                return 1
            if upper < 0:
                return -1
            mid = (lo + hi) / 2
            if engine.distinct_roots_open(self.field.minimal, lo, mid) == 1:
                hi = mid
            else:
                lo = mid

    def record(self):
        return [str(x) for x in self.coefficients]


def _etrim(p):
    while len(p) > 1 and p[-1].is_zero():
        p.pop()
    return p


def compose_affine(coefficients, offset: Element, width: Element):
    field = offset.field
    width = field.element(width)
    out = [field.element(0)]
    for value in reversed(coefficients):
        new = [field.element(0) for _ in range(len(out) + 1)]
        for i, coefficient in enumerate(out):
            new[i] = new[i] + coefficient * offset
            new[i + 1] = new[i + 1] + coefficient * width
        new[0] = new[0] + field.element(value)
        out = _etrim(new)
    return out


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _material(cos_polys, sin_polys, source_parameter_id, parent_interval, phase_offset, phase_rate):
    require(isinstance(source_parameter_id, str) and bool(source_parameter_id), "missing source identity")
    left, right = map(q, parent_interval)
    require(left < right, "parent interval must have positive width")
    maps = []
    for source_map in (cos_polys, sin_polys):
        normal = {}
        for harmonic, polynomial in source_map.items():
            require(type(harmonic) is int and harmonic >= 0, "harmonics must be nonnegative integers")
            normal[str(harmonic)] = [str(x) for x in trim(polynomial)]
        maps.append(normal)
    require(trim(maps[1].get("0", [0])) == [0], "harmonic-zero sine channel must vanish")
    return {
        "source_parameter_id": source_parameter_id,
        "parent_source_interval": [str(left), str(right)],
        "cos_polynomials": maps[0], "sin_polynomials": maps[1],
        "phase_turn_law": {"offset": str(q(phase_offset)), "rate": str(q(phase_rate))},
    }


def _orientation(material, harmonic, coordinate):
    require(type(harmonic) is int and harmonic > 0 and coordinate in ("A", "B"), "invalid orientation owner")
    c = trim(material["cos_polynomials"].get(str(harmonic), [0]))
    s = trim(material["sin_polynomials"].get(str(harmonic), [0]))
    return pscale(padd(c, s if coordinate == "A" else pscale(s, -1)), Fraction(1, 2))


def _bisection(material, cut):
    """Internal adapter: only regenerated v44 cut records may select the root."""
    certificate, owners = cut["certificate"], cut["ownership"]
    require(bool(owners), "cut has no source owner")
    representative = None
    for owner in owners:
        polynomial = _orientation(material, owner["harmonic"], owner["coordinate"])
        if primitive(polynomial) == primitive(certificate["source_polynomial_primitive"]):
            representative = polynomial
            break
    require(representative is not None, "certificate is not bound to any actual source orientation")
    field = RealField.from_source_certificate(representative, certificate)
    alpha, zero, one = field.element([0, 1]), field.element(0), field.element(1)
    for owner in owners:
        polynomial = _orientation(material, owner["harmonic"], owner["coordinate"])
        require(field.element(polynomial).is_zero(), "false common A/B root")
        # The minimal-factor interval may contain other source roots: multiplicity
        # is the number of exact divisions by the selected irreducible factor.
        work, multiplicity = polynomial, 0
        while engine.degree(work) >= len(field.minimal) - 1:
            quotient, remainder = engine.pdivmod(work, field.minimal)
            if remainder != [0]:
                break
            work, multiplicity = quotient, multiplicity + 1
        require(type(owner["multiplicity"]) is int and owner["multiplicity"] == multiplicity, "owner multiplicity mismatch")
    require(alpha.sign() == 1 and (one - alpha).sign() == 1, "degenerate child width")
    parent_left, parent_right = map(q, material["parent_source_interval"])
    parent_width = parent_right - parent_left
    phase = material["phase_turn_law"]
    local_offset = q(phase["offset"]) + q(phase["rate"]) * parent_left
    local_rate = q(phase["rate"]) * parent_width
    children = []
    for side, offset, width in (("left", zero, alpha), ("right", alpha, one - alpha)):
        inverse = width.inverse()
        restricted = {}
        for channel in ("cos_polynomials", "sin_polynomials"):
            restricted[channel] = {}
            for harmonic, source_poly in material[channel].items():
                coefficients = compose_affine(source_poly, offset, width)
                reconstructed = compose_affine(coefficients, -offset * inverse, inverse)
                require(reconstructed == [field.element(x) for x in source_poly], "child-to-parent exact reconstruction failed")
                restricted[channel][harmonic] = [x.record() for x in coefficients]
        source_offset = field.element(parent_left) + offset * parent_width
        source_width = width * parent_width
        child_phase_offset = field.element(local_offset) + offset * local_rate
        child_phase_rate = width * local_rate
        children.append({
            "side": side, "local_parameter_interval": ["0", "1"],
            "parent_local_map": {"offset": offset.record(), "width": width.record()},
            "parent_source_map": {"offset": source_offset.record(), "width": source_width.record()},
            "parent_source_interval": [source_offset.record(), (source_offset + source_width).record()],
            "phase_turn_law": {"offset": child_phase_offset.record(), "rate": child_phase_rate.record()},
            "restricted_polynomials": restricted,
            "exact_polynomial_roundtrip": True,
        })
    cut_phase = field.element(local_offset) + alpha * local_rate
    return {
        "status": "REPRESENTATION_CERTIFIED", "field": field.record(),
        "source_parameter_id": material["source_parameter_id"],
        "source_binding_sha256": sha256(_json(material).encode()).hexdigest(),
        "orientation_ownership": owners, "children": children,
        "coverage": "EXACT_SINGLE_CUT_BISECTION_OF_PARENT_NO_GAP_OR_OVERLAP",
        "internal_phase_turn": cut_phase.record(),
        "internal_phase_kind": "RATIONAL" if local_rate == 0 else "ALGEBRAIC_IRRATIONAL",
        "endpoint_event_authority": "DEFER_TO_PREDECESSOR" if local_rate == 0 else ENDPOINT_BLOCKER,
        "physical_event_inferred_from_orientation_root": False,
        "analytic_cut_consumed": False,
    }


def resource_refusal(stage):
    return {"status": "RESOURCE_REFUSAL", "reason": "PB00701_V45_EXACT_RESOURCE_REFUSAL", "stage": stage, "is_truth_value": False}


def build_orientation_child_maps(cos_polys, sin_polys, source_parameter_id, parent_interval, phase_offset, phase_rate):
    """Regenerate v44 cuts; return independent bisections, not a multi-cut event.

Each alternative has one Q(alpha) embedding. No compositum Q(alpha,beta),
full multi-cut partition, or new analytic event/root result is asserted.
    """
    try:
        import pb00701_algebraic_orientation_cut_model as v44
        material = _material(cos_polys, sin_polys, source_parameter_id, parent_interval, phase_offset, phase_rate)
        cuts = v44.exact_algebraic_orientation_cut_certificate(cos_polys, sin_polys)
        if cuts.get("status") != "CERTIFIED":
            return cuts
        alternatives = [_bisection(material, cut) for cut in cuts["canonical_irrational_cuts"]]
        return {
            "status": "REPRESENTATION_CERTIFIED" if alternatives else "NOT_APPLICABLE",
            "relation": V45_RELATION, "source_material": material,
            "independent_single_cut_bisections": alternatives,
            "pairwise_exact_cut_order": cuts["pairwise_exact_order"],
            "analytic_cut_consumed": False,
            "consumption_decision": "DO_NOT_CONSUME_ANALYTIC_CUT",
        }
    except (MemoryError, RecursionError, OverflowError) as exc:
        return resource_refusal(type(exc).__name__)


def validate_child_maps(candidate, cos_polys, sin_polys, source_parameter_id, parent_interval, phase_offset, phase_rate):
    regenerated = build_orientation_child_maps(cos_polys, sin_polys, source_parameter_id, parent_interval, phase_offset, phase_rate)
    require(regenerated.get("status") == "REPRESENTATION_CERTIFIED", "no certified source representation to validate")
    require(_json(candidate) == _json(regenerated), "child representation/source binding mismatch")
    return True


def classify_required_analytic_event(spec):
    """Historical event results are returned untouched; no v45 event authority."""
    import pb00701_algebraic_orientation_cut_model as v44
    return v44.classify_required_analytic_event(spec)


def represent_required_event_children(spec):
    """Attach representation-only work to source-lowered v44 residual spans.

The predecessor's entire physical event result is retained, including every
BLOCKED/refusal outcome. No algebraic child is fed to a rational-only classifier.
    """
    import pb00701_algebraic_orientation_cut_model as v44
    baseline = v44.classify_required_analytic_event(spec)
    representations = []
    for span in baseline.get("spans", []):
        if span.get("route", {}).get("relation") != v44.V44_ROUTE:
            continue
        phase = baseline["phase_turn_law"]
        representation = build_orientation_child_maps(
            {int(h): p for h, p in span["cos_polynomials"].items()},
            {int(h): p for h, p in span["sin_polynomials"].items()},
            baseline["source_parameter_id"], span["source_interval"],
            phase["offset"], phase["rate"],
        )
        representations.append({"source_interval": span["source_interval"], "representation": representation})
    statuses = {r["representation"]["status"] for r in representations}
    status = ("RESOURCE_REFUSAL" if "RESOURCE_REFUSAL" in statuses else
              "REPRESENTATION_CERTIFIED" if statuses == {"REPRESENTATION_CERTIFIED"} else
              "BLOCKED" if representations else "NOT_APPLICABLE")
    return {
        "status": status, "relation": V45_RELATION,
        "predecessor_event_result": baseline, "span_representations": representations,
        "analytic_cut_consumed": False,
    }
