#!/usr/bin/env python3
"""Source-regenerating v47 checker: no cut/route or transcendental sign search."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_monotone_cut_model as m
import pb00701_algebraic_endpoint_certificate as epcheck


def validate_single_cut_event(candidate, *source_args):
    try:
        representation = m.a.build_orientation_child_maps(*source_args)
        if representation.get('status') == 'RESOURCE_REFUSAL':
            return representation
        m.require(representation.get('status') == 'REPRESENTATION_CERTIFIED', 'source has no exact algebraic bisection')
        material = representation['source_material']
        splits = [s for s in representation['independent_single_cut_bisections']
                  if m.ip.same(s, candidate['bisection'])]
        m.require(len(splits) == 1, 'forged field/cut/map/source binding')
        split = splits[0]
        m.require(m.ip.same(candidate['source_material'], material), 'different physical source material')
        field = m.field_from_split(split)
        zero, one, alpha = field.element(0), field.element(1), field.element([0, 1])
        m.require(len(candidate['children']) == 2, 'missing/extra closed child')
        derivatives = []
        for child, (lo, hi) in zip(candidate['children'], ((zero, alpha), (alpha, one))):
            proof = child['derivative_certificate']
            # Finite witness-specified v42/v43 recipe; do not search candidate
            # modes, skip a failed orthant, or trust caller Sturm counts.
            expected = m.derivative_attempt(material, field, lo, hi, proof['harmonic'], proof['mode'])
            m.require(expected['status'] == 'CERTIFIED', 'closed derivative not established')
            m.require(m.ip.same(proof, expected), 'source/phase/Sturm/orthant proof mismatch')
            derivatives.append(expected)
        endpoints = candidate['endpoint_evidence']
        m.require(len(endpoints) == 3, 'endpoint cardinality mismatch')
        epcheck._validate_endpoint(endpoints[1], material, split)
        for i, j in ((0, 0), (2, 1)):
            expected = m.rational_endpoint(material, j)
            if expected.get('status') == 'RESOURCE_REFUSAL':
                return expected
            m.require(m.ip.same(endpoints[i], expected), 'rational external endpoint mismatch')
        expected = m._assemble(material, split, derivatives, endpoints)
        m.require(expected['status'] == 'CERTIFIED', 'inconsistent physical composition')
        m.require(m.ip.same(candidate, expected), 'child/endpoint/root/multiplicity composition mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.resource_refusal('certificate:' + type(exc).__name__)
