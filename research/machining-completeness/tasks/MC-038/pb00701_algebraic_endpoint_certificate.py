#!/usr/bin/env python3
"""Finite certificate checker. Never trusts endpoint signs, jets or remainders.

The complete source/field/phase bindings and jets are regenerated. Checking a
sign proof uses its finite precision as witness size, NOT a search cap or truth
criterion. Scalar series/remainders are also audited by direct summation rather
than the generator's recurrence. No transcendental floating-point evaluation.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_endpoint_model as m


def _audit_series(proof):
    pi = proof['pi']
    n = proof['precision']
    m.require(type(n) is int and n > 0, 'invalid finite witness size')
    # (5+i)^4(239-i) = 114244(1+i), computed without complex floats.
    re, im = 1, 0
    for _ in range(4):
        re, im = 5*re-im, re+5*im
    re, im = 239*re+im, -re+239*im
    m.require(pi['gaussian_identity'] == [re, im] == [114244, 114244], 'Machin identity corruption')
    for name, d in (('atan_1_5',5), ('atan_1_239',239)):
        a = pi[name]
        total = sum((Q((-1)**k, (2*k+1)*d**(2*k+1)) for k in range(n)), Q(0))
        tail = Q((-1)**n, (2*n+1)*d**(2*n+1))
        expected = {'denominator':d, 'terms':n, 'sum':str(total),
                    'signed_next_term':str(tail), 'interval':m._record(tuple(sorted((total,total+tail))))}
        m.require(m._same(a, expected), 'arctan rational sum/tail mismatch')
    for component in proof['components']:
        if component['harmonic'] == 0:
            continue
        t = component['trig']
        center = m.q(t['center'])
        lo, hi = map(m.q, t['radians'])
        m.require(center == (lo+hi)/2 and m.q(t['radius']) == (hi-lo)/2, 'Taylor center/radius mismatch')
        parity = 1 if component['kind'] == 'SIN' else 0
        degree = 2*(n-1)+parity
        total = sum(((-1)**k * center**(2*k+parity)/factorial(2*k+parity) for k in range(n)), Q(0))
        remainder = abs(center)**(degree+1)/factorial(degree+1)
        m.require(t['taylor_degree'] == degree and m.q(t['taylor_sum']) == total, 'Taylor polynomial corruption')
        m.require(m.q(t['lagrange_remainder']) == remainder, 'Lagrange remainder corruption')
        m.require(t['lipschitz_constant'] == '1', 'unproved Lipschitz constant')


def _validate_endpoint(candidate, material, split):
    header, field, values, offset, rate = m._endpoint_header(material, split)
    m.require(header.get('status') == 'ENDPOINT_CERTIFIED', 'no finite endpoint theorem')
    if header['physical_multiplicity']:
        m.require(m._same(candidate, header), 'zero endpoint/multiplicity/jet binding mismatch')
        return
    proof = candidate['sign_certificate']
    _audit_series(proof)
    # Rebuild all root/phase/pi/amplitude intervals and every contribution.
    # Omitted channels or forged isolation/field/order cannot pass regeneration.
    regenerated = m.sign_enclosure(field, values, offset, rate, proof['precision'])
    m.require(m._same(proof, regenerated), 'source-derived sign enclosure mismatch')
    relation = m._separated(regenerated)
    m.require(relation is not None, 'enclosure does not strictly exclude zero')
    expected = {**header, 'relation':relation, 'sign_certificate':regenerated}
    m.require(m._same(candidate, expected), 'endpoint/source/phase/Laurent binding mismatch')


def validate_source_endpoint_evidence(candidate, *source_args):
    """True only for a completely regenerated proof; resource refusal is non-truth."""
    try:
        representation = m.v45.build_orientation_child_maps(*source_args)
        if representation.get('status') == 'RESOURCE_REFUSAL':
            return representation
        m.require(representation.get('status') == 'REPRESENTATION_CERTIFIED', 'no exact source representation')
        material = representation['source_material']
        m.require(m.q(material['phase_turn_law']['rate']) != 0, 'zero phase remains predecessor-owned')
        endpoints = candidate['endpoints']
        splits = representation['independent_single_cut_bisections']
        m.require(len(endpoints) == len(splits) and len(splits) > 0, 'endpoint count mismatch')
        for endpoint, split in zip(endpoints, splits):
            _validate_endpoint(endpoint, material, split)
        expected = {'status':'ENDPOINTS_CERTIFIED', 'method':m.RELATION,
                    'source_binding_sha256':m._digest(material), 'endpoints':endpoints,
                    'analytic_cut_consumed':False, 'whole_span_certified':False}
        m.require(m._same(candidate, expected), 'endpoint-only capability boundary mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.resource_refusal('certificate:'+type(exc).__name__)
