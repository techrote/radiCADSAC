#!/usr/bin/env python3
"""Finite source-bound V49 checker; no derivative-route or endpoint sign search."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_multicut_model as m


def validate_multicut_event(candidate, *source_args):
    stage = 'partition'
    try:
        partition, points = m._partition(*source_args)
        if partition['status'] == 'RESOURCE_REFUSAL':
            return partition
        m.require(partition['status'] == 'PARTITION_CERTIFIED', 'no source-bound mixed partition')
        m.require(m.b.same(candidate['partition'], partition), 'partition/source/field/order/map corruption')
        material = partition['source_material']
        children = candidate['children']
        m.require(len(children) == len(points) - 1, 'missing or extra closed child')
        derivatives = []
        for i, (child, lo, hi) in enumerate(zip(children, points, points[1:])):
            stage = 'derivative:' + str(i)
            proof = child['derivative_certificate']
            expected = m.b.derivative_attempt(material, lo, hi, proof['harmonic'], proof['mode'])
            m.require(expected['status'] == 'CERTIFIED', 'a complete closed-child margin failed')
            m.require(m.b.same(expected, proof), 'derivative/source/Sturm/orthant witness mismatch')
            derivatives.append(expected)
        endpoints = candidate['endpoint_evidence']
        m.require(len(endpoints) == len(points), 'physical endpoint cardinality mismatch')
        for i, (point, record, event) in enumerate(zip(points, partition['boundaries'], endpoints)):
            stage = 'endpoint:' + str(i)
            if point.rational is not None:
                expected = m._rational_endpoint(material, point)
                if expected.get('status') == 'RESOURCE_REFUSAL':
                    return expected
                m.require(expected.get('status') == 'DECIDED' and m.b.same(event, expected),
                          'rational boundary event corruption')
            else:
                import pb00701_algebraic_endpoint_certificate as epcheck
                epcheck._validate_endpoint(event, material, record['endpoint_bisection'])
        stage = 'composition'
        expected = m._assemble(partition, derivatives, endpoints)
        m.require(expected['status'] == 'CERTIFIED' and m.b.same(candidate, expected),
                  'source/cell/root/multiplicity composition mismatch')
        return True
    except m.b.RESOURCE_ERRORS as exc:
        return m.b.refusal('certificate:' + stage + ':' + type(exc).__name__)
