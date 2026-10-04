#!/usr/bin/env python3
"""Finite V53 checking from ORIGINAL source and supplied historical witnesses.

Owner-specific witness recipes and exact rational-turn decisions are finite
regeneration, not searches for another classifier, derivative mode or sign proof.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_owner_span_model as m


def validate_ordered_span_view(candidate, *source_args):
    try:
        expected = m.regenerate_view(candidate['kind'], candidate['owner'],
                                     candidate['underlying_witness'], *source_args)
        if expected.get('status') != 'ORDERED_SPAN_VIEW_CERTIFIED':
            return expected
        m.require(m.b.same(candidate, expected), 'normalized span view/source/owner/witness mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.refusal('checker:span-view:' + type(exc).__name__)


def validate_mixed_certificate(candidate, spec):
    stage = 'source-lowering'
    try:
        lowering = m.v52.lower_source(spec)
        m.require(m.b.same(candidate['source_lowering'], lowering), 'original spline source/lowering mismatch')
        stage = 'span-checking'
        views = candidate['span_proofs']
        checked = m.check_views(lowering, views)
        if checked is not True:
            return checked
        stage = 'source-knot-continuity'
        joins = m.v52.build_joins(lowering, views)
        if isinstance(joins, dict):
            if joins.get('status') == 'RESOURCE_REFUSAL':
                return joins
            m.require(False, 'original physical source is not proved continuous')
        m.require(m.b.same(candidate['knot_evidence'], joins), 'source-knot value/orders/signs mismatch')
        stage = 'global-composition'
        expected = m.assemble(lowering, views, joins)
        m.require(m.b.same(candidate, expected), 'global root union/cell coverage/owner/capability mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.refusal('checker:' + stage + ':' + type(exc).__name__)
