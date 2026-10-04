#!/usr/bin/env python3
"""V51 finite original-lowered-source checker, with no replacement proof search."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_ordered_product_model as m


def validate_factor_carrier_sign(candidate, certificate, *source_args):
    try:
        return m._check_factor_sign(candidate, m._factorization(source_args), certificate)
    except m.RESOURCE_ERRORS as exc:
        return m.refusal('checker:factor-sign:' + type(exc).__name__)


def validate_ordered_product_event(candidate, *source_args):
    """True only after the supplied product and all finite sign proofs regenerate.

The source arguments are the unchanged rational polynomial channels, source ID,
original global interval and rational-affine phase of ONE lowered source span.
No call to the source wrapper/classifier is needed or permitted in this checker.
    """
    import pb00701_vanishing_source_factor_certificate as product_check
    stage = 'product'
    try:
        product = candidate['physical_event_result']
        checked = product_check.validate_product_event(product, *source_args)
        if checked is not True:
            return checked
        factorization = product['factorization']
        events = product['factor_root_evidence']['factor_events']
        signs = candidate['factor_carrier_signs']
        m.require(len(signs) == len(events), 'missing/extra factor sign witness')
        regenerated = []
        for i, (event, row) in enumerate(zip(events, signs)):
            stage = 'factor-sign:' + str(i)
            proof = row['sign_evidence']
            if event['source_cut']['kind'] == 'ALGEBRAIC_IRRATIONAL':
                certificate = event['algebraic_disjointness_evidence']['factor_root_certificate']
                m._check_factor_sign(proof, factorization, certificate)
            expected = m._sign_row(i, event, proof)
            m.require(m.b.same(row, expected), 'factor sign position/coincidence/order metadata mismatch')
            regenerated.append(expected)
        stage = 'ordered-composition'
        expected = m._assemble_ordered(product, regenerated)
        m.require(m.b.same(candidate, expected), 'ordered event/sign-cell/source/capability mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.refusal('checker:' + stage + ':' + type(exc).__name__)
