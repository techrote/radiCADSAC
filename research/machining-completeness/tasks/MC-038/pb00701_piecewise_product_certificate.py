#!/usr/bin/env python3
"""Finite V52 checker: regenerate lowering from ORIGINAL B-spline source.

No source/carrier classifier, derivative selector or endpoint sign search is
called here. The separately retained predecessor envelope is not truth evidence.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_piecewise_product_model as m


def validate_piecewise_certificate(candidate, spec):
    stage = 'source-lowering'
    try:
        lowering = m.lower_source(spec)
        m.require(m.b.same(candidate['source_lowering'], lowering),
                  'original spline controls/knots/degree/phase/lowering mismatch')
        stage = 'span-checking'
        proofs = candidate['span_proofs']
        checked = m.check_spans(lowering, proofs)
        if checked is not True:
            return checked
        stage = 'knot-continuity'
        joins = m.build_joins(lowering, proofs)
        if isinstance(joins, dict):
            if joins.get('status') == 'RESOURCE_REFUSAL':
                return joins
            m.require(False, 'physical source is not proved continuous at every knot')
        m.require(m.b.same(candidate['knot_evidence'], joins),
                  'physical knot equality/orders/signs/source identity mismatch')
        stage = 'global-composition'
        expected = m.assemble(lowering, proofs, joins)
        m.require(m.b.same(candidate, expected),
                  'global root union/sign-cell coverage/count/source/capability mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.refusal('checker:' + stage + ':' + type(exc).__name__)
