#!/usr/bin/env python3
"""V49 rational-polynomial proofs at independently embedded real boundaries.

No common field, normalized algebraic width, numerical sample, or midpoint of
unrelated algebraic numbers is used. The source polynomial remains rational in
the original lowered-parent coordinate. See 73-PB00701-MIXED-MULTICUT.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as a

E, q, require = a.engine, a.q, a.require
L, U, W, K = Q(2856, 2197), Q(99, 182), Q(99, 70), Q(44, 7)
RESOURCE_ERRORS = (MemoryError, OverflowError, RecursionError)


def same(x, y):
    return a._json(x) == a._json(y)


def digest(x):
    return sha256(a._json(x).encode()).hexdigest()


def blocked(reason, **details):
    return {'status': 'BLOCKED', 'reason': reason, 'blocker': 'PB-007-01', **details}


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V49_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


@dataclass(frozen=True)
class Boundary:
    """Internal exact endpoint. Public consumers regenerate it from source."""
    rational: Q | None = None
    field: a.RealField | None = None

    def __post_init__(self):
        require((self.rational is None) != (self.field is None), 'ambiguous boundary representation')
        if self.rational is not None:
            require(type(self.rational) is Q, 'boundary must contain an exact Fraction')
        else:
            require(type(self.field) is a.RealField, 'boundary has no validated real embedding')

    @classmethod
    def at(cls, x):
        return cls(rational=q(x))

    @classmethod
    def from_source(cls, polynomial, certificate):
        return cls(field=a.RealField.from_source_certificate(polynomial, certificate))

    def record(self):
        if self.rational is not None:
            return {'kind': 'RATIONAL', 'value': str(self.rational)}
        return {'kind': 'ALGEBRAIC_IRRATIONAL', 'field': self.field.record(), 'value': ['0', '1']}

    def evaluate(self, polynomial):
        p = a.trim(polynomial)
        if self.rational is not None:
            return E.peval(p, self.rational)
        # Boundary is the selected generator, so polynomial reduction is exact.
        return self.field.element(p)

    def affine(self, offset, rate):
        return self.evaluate([q(offset), q(rate)])


def value_sign(value):
    return value.sign() if isinstance(value, a.Element) else E.sign(value)


def value_record(value):
    if isinstance(value, a.Element):
        return {'kind': 'FIELD_VALUE', 'field': value.field.record(), 'coefficients': value.record()}
    return {'kind': 'RATIONAL', 'value': str(q(value))}


def _refine(field, bounds):
    lo, hi = bounds
    mid = (lo + hi) / 2
    require(E.peval(field.minimal, mid) != 0, 'irrational root equals rational midpoint')
    return (lo, mid) if E.distinct_roots_open(field.minimal, lo, mid) == 1 else (mid, hi)


def order_certificate(left, right):
    """Exact order with no subtraction across real fields.

Different irreducible minimal polynomials cannot share a root. Equal minimal
polynomials use their real-root indices; otherwise disjoint rational isolations
are reached by finite root separation. Interval overlap is never equality.
    """
    require(type(left) is Boundary and type(right) is Boundary, 'unbound endpoint')
    proof = {'left': left.record(), 'right': right.record()}
    if left.rational is not None and right.rational is not None:
        sign = E.sign(left.rational - right.rational)
        return {**proof, 'method': 'EXACT_RATIONAL_ORDER', 'comparison': sign}
    if left.rational is not None:
        sign = -value_sign(right.affine(-left.rational, 1))
        return {**proof, 'method': 'EXACT_RATIONAL_TO_FIELD_ORDER', 'comparison': sign}
    if right.rational is not None:
        sign = value_sign(left.affine(-right.rational, 1))
        return {**proof, 'method': 'EXACT_FIELD_TO_RATIONAL_ORDER', 'comparison': sign}
    lf, rf = left.field, right.field
    if lf.minimal == rf.minimal:
        return {**proof, 'method': 'SELECTED_MINIMAL_FACTOR_ROOT_INDEX',
                'comparison': E.sign(lf.root_index - rf.root_index)}
    lb, rb, steps = lf.interval, rf.interval, [0, 0]
    while lb[1] > rb[0] and rb[1] > lb[0]:
        if lb[1] - lb[0] >= rb[1] - rb[0]:
            lb = _refine(lf, lb)
            steps[0] += 1
        else:
            rb = _refine(rf, rb)
            steps[1] += 1
    return {**proof, 'method': 'DISTINCT_MINIMAL_FACTORS_EXACT_ISOLATION_SEPARATION',
            'comparison': -1 if lb[1] <= rb[0] else 1,
            'refinement_steps': steps,
            'isolations': [[str(x) for x in b] for b in (lb, rb)]}


def side_jet(polynomial, boundary, side):
    require(side in ('left', 'right'), 'invalid inward direction')
    p, order = a.trim(polynomial), 0
    while p != [0]:
        value = boundary.evaluate(p)
        sign = value_sign(value)
        if sign:
            return {'order': order, 'value': value_record(value),
                    'sign': -sign if side == 'left' and order % 2 else sign}
        p, order = E.deriv(p), order + 1
    return {'order': None, 'value': value_record(boundary.evaluate([0])), 'sign': 0}


def polynomial_certificate(polynomial, left, right):
    order = order_certificate(left, right)
    require(order['comparison'] == -1, 'interval is not strictly ordered')
    p = a.trim(polynomial)
    header = {'polynomial': [str(x) for x in p], 'boundaries': [left.record(), right.record()],
              'order_certificate': order}
    if p == [0]:
        return {**header, 'identity_zero': True, 'distinct_roots_open': None,
                'strict_positive': False, 'weak_sign': 0}
    sequence = E.sturm_sequence(p)
    lj = [side_jet(s, left, 'right') for s in sequence]
    rj = [side_jet(s, right, 'left') for s in sequence]
    lv, rv = E._variations([j['sign'] for j in lj]), E._variations([j['sign'] for j in rj])
    count = lv - rv
    require(0 <= count <= E.degree(p), 'invalid boundary-local Sturm count')
    le, re = value_sign(left.evaluate(p)), value_sign(right.evaluate(p))
    lp, rp = side_jet(p, left, 'right'), side_jet(p, right, 'left')
    weak = lp['sign'] if count == 0 and lp['sign'] == rp['sign'] else None
    require(weak is None or (le in (0, weak) and re in (0, weak)), 'endpoint weak-sign inconsistency')
    return {**header, 'identity_zero': False,
            'sturm_sequence': [[str(x) for x in s] for s in sequence],
            'left_inward_jets': lj, 'right_inward_jets': rj, 'variations': [lv, rv],
            'distinct_roots_open': count, 'endpoint_signs': [le, re],
            'endpoint_multiplicities': [lp['order'], rp['order']],
            'strict_positive': le == re == 1 and count == 0, 'weak_sign': weak}


def validate_polynomial_certificate(candidate, polynomial, left, right):
    require(same(candidate, polynomial_certificate(polynomial, left, right)),
            'mixed-boundary Sturm/jet/source certificate mismatch')
    return True


def _floor_affine(boundary, offset, rate):
    """Exact floor of a rational-affine boundary value (not numerical rounding)."""
    offset, rate = q(offset), q(rate)
    value = boundary.affine(offset, rate)
    if not isinstance(value, a.Element) or len(value.coefficients) == 1:
        rational = value.coefficients[0] if isinstance(value, a.Element) else value
        return rational.numerator // rational.denominator
    # Here rate is nonzero and alpha irrational, so the affine value is not an
    # integer. Refinement reaches a unique floor; no resource cap implies truth.
    bounds = boundary.field.interval
    while True:
        lo, hi = sorted(offset + rate * x for x in bounds)
        fl, fh = lo.numerator // lo.denominator, hi.numerator // hi.denominator
        if fl == fh:
            return fl
        bounds = _refine(boundary.field, bounds)


def phase_cell(left, right, offset, rate, harmonic):
    require(type(harmonic) is int and harmonic > 0, 'invalid positive harmonic')
    require(order_certificate(left, right)['comparison'] == -1, 'invalid phase interval')
    offset, rate = q(offset), q(rate)
    require(rate != 0, 'zero phase belongs to predecessor')
    lower_endpoint = left if rate > 0 else right
    k = _floor_affine(lower_endpoint, 2 * (harmonic * offset + Q(3, 16)), 2 * harmonic * rate)
    lower, upper = Q(-3, 16) + Q(k, 2), Q(-1, 16) + Q(k, 2)
    values = [x.affine(harmonic * offset, harmonic * rate) for x in (left, right)]
    checks = [[value_sign(x.affine(harmonic * offset - lower, harmonic * rate)),
               value_sign(x.affine(upper - harmonic * offset, -harmonic * rate))]
              for x in (left, right)]
    return {'status': 'CERTIFIED' if all(sign >= 0 for pair in checks for sign in pair) else 'BLOCKED',
            'method': 'EXACT_BOUNDARY_LOCAL_AFFINE_PHASE_CONTAINMENT', 'harmonic': harmonic,
            'cell_index': k, 'bounds': [str(lower), str(upper)],
            'harmonic_phase_endpoints': [value_record(x) for x in values],
            'containment_signs': checks, 'diagonal_sign': -1 if k % 2 else 1,
            'boundaries': [left.record(), right.record()], 'parent_phase_rate': str(rate)}


def maps(material):
    return tuple({int(h): a.trim(p) for h, p in material[key].items()}
                 for key in ('cos_polynomials', 'sin_polynomials'))


def local_phase(material):
    lo, hi = map(q, material['parent_source_interval'])
    phase = material['phase_turn_law']
    return q(phase['offset']) + q(phase['rate']) * lo, q(phase['rate']) * (hi - lo)


def residual_channels(material, harmonic, rate):
    cos, sin = maps(material)
    terms = []
    def add(kind, h, p):
        p = a.trim(p)
        if p != [0]:
            terms.append({'kind': kind, 'harmonic': h, 'polynomial': [str(x) for x in p]})
    add('C0_prime', 0, E.deriv(cos.get(0, [0])))
    for h in sorted((set(cos) | set(sin)) - {0, harmonic}):
        for kind, source in (('C', cos), ('S', sin)):
            p = source.get(h, [0])
            add(kind + '_prime', h, E.deriv(p))
            add(kind + '_phase_upper', h, a.pscale(p, K * abs(h * rate)))
    return terms


def derivative_attempt(material, left, right, harmonic, mode):
    """Finite V42/V43 recipe, now using independent endpoint embeddings.

No monkeypatch to historical code; identical complete derivative inequalities
are reconstructed, and all finite sign orthants remain mandatory.
    """
    require(mode in ('V42', 'V43'), 'unsupported derivative recipe')
    require(type(harmonic) is int and harmonic > 0, 'invalid harmonic authority')
    require(order_certificate(Boundary.at(0), left)['comparison'] <= 0 and
            order_certificate(right, Boundary.at(1))['comparison'] <= 0, 'child outside parent')
    offset, rate = local_phase(material)
    if not rate:
        return blocked('ZERO_PHASE_PREDECESSOR_OWNERSHIP')
    cell = phase_cell(left, right, offset, rate, harmonic)
    if cell['status'] != 'CERTIFIED':
        return blocked('PHASE_CELL_NOT_CONTAINED', phase_cell=cell)
    cos, sin = maps(material)
    c, s = cos.get(harmonic, [Q(0)]), sin.get(harmonic, [Q(0)])
    if c == [0] or s == [0]:
        return blocked('TWO_SOURCE_QUADRATURES_REQUIRED')
    A, B = a.pscale(a.padd(c, s), Q(1, 2)), a.pscale(a.padd(c, a.pscale(s, -1)), Q(1, 2))
    Ap, Bp, hr = E.deriv(A), E.deriv(B), harmonic * rate
    constraints = []
    def proof(p, name):
        result = polynomial_certificate(p, left, right)
        constraints.append({'name': name, 'certificate': result})
        return result
    residuals = residual_channels(material, harmonic, rate)
    if mode == 'V42':
        bp = proof(Bp, 'STRICT_B_PRIME_SIGN')
        sigma = bp['weak_sign']
        if sigma not in (-1, 1) or bp.get('endpoint_signs') != [sigma, sigma]:
            return blocked('B_PRIME_NOT_STRICT', constraints=constraints)
        base = a.pscale(Bp, sigma * L)
        selected = [('A_prime_X', a.pscale(Ap, U)),
                    ('A_phase_Y_adverse', a.pscale(A, K * abs(hr) * W)),
                    ('B_phase_X', a.pscale(B, K * abs(hr) * U))]
        orientation = sigma
    else:
        pa = proof(A, 'WEAK_A_WITH_ENDPOINT_ZEROS')
        sigma = pa['weak_sign']
        if sigma not in (-1, 1):
            return blocked('A_NOT_WEAK_ONE_SIGN', constraints=constraints)
        orientation = sigma * (1 if hr > 0 else -1)
        oriented_bp = a.pscale(Bp, orientation)
        pb = proof(oriented_bp, 'WEAK_ORIENTED_B_PRIME')
        sb = pb['weak_sign']
        if sb not in (-1, 0, 1):
            return blocked('B_PRIME_NOT_WEAK_ONE_SIGN', constraints=constraints)
        base = a.padd(a.pscale(oriented_bp, L if sb >= 0 else W),
                      a.pscale(A, 6 * L * orientation * hr))
        selected = [('A_prime_X', a.pscale(Ap, U)), ('B_phase_X', a.pscale(B, K * hr * U))]
    terms = [{'kind': kind, 'harmonic': harmonic, 'polynomial': [str(x) for x in p]}
             for kind, p in selected] + residuals
    orthants = []
    for mask in range(1 << len(terms)):
        signs = [1 if (mask >> i) & 1 else -1 for i in range(len(terms))]
        margin = list(base)
        for sign, term in zip(signs, terms):
            margin = a.padd(margin, a.pscale(term['polynomial'], -sign))
        certificate = polynomial_certificate(margin, left, right)
        if not certificate['strict_positive']:
            return blocked('COMPLETE_STRICT_MARGIN_NOT_CERTIFIED', mode=mode,
                           failed_orthant=mask, failed_margin=certificate, constraints=constraints)
        orthants.append({'mask': mask, 'signs': signs, 'certificate': certificate})
    width = q(material['parent_source_interval'][1]) - q(material['parent_source_interval'][0])
    return {'status': 'CERTIFIED', 'method': 'V49_BOUNDARY_LOCAL_LIFT_' + mode,
            'mode': mode, 'harmonic': harmonic, 'phase_cell': cell,
            'source_parameter_id': material['source_parameter_id'], 'source_binding_sha256': digest(material),
            'boundaries': [left.record(), right.record()], 'parent_local_phase': [str(offset), str(rate)],
            'global_derivative_scale': str(Q(1) / width),
            'coordinates': {name: [str(x) for x in p] for name, p in
                            (('C', c), ('S', s), ('A', A), ('B', B), ('A_prime', Ap), ('B_prime', Bp))},
            'identity': "F'_anchor=A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)",
            'bounds': {'L': str(L), 'U': str(U), 'W': str(W), 'two_pi_lower': '6', 'two_pi_upper': str(K)},
            'orientation': orientation, 'derivative_sign': orientation * cell['diagonal_sign'],
            'constraints': constraints, 'margin_base': [str(x) for x in base],
            'orthant_terms': terms, 'retained_nonanchor_channels': residuals,
            'orthant_count': len(orthants), 'orthants': orthants}


def certify_derivative(material, left, right):
    cos, sin = maps(material)
    attempts = []
    for harmonic in sorted((set(cos) & set(sin)) - {0}):
        for mode in ('V42', 'V43'):
            result = derivative_attempt(material, left, right, harmonic, mode)
            if result['status'] == 'CERTIFIED':
                return result
            if result['status'] in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                return result
            attempts.append({'harmonic': harmonic, 'mode': mode, 'result': result})
    return blocked('NO_COMPLETE_MIXED_BOUNDARY_CHILD_DERIVATIVE', attempts=attempts)
