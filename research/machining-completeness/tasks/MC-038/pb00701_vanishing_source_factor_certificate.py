#!/usr/bin/env python3
"""V50 original-source checker: no replacement carrier/derivative/sign search."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_vanishing_source_factor_model as m


def validate_product_event(candidate, *source_args):
    stage = 'factorization'
    try:
        factorization = m.factor_source(*source_args)
        if factorization['status'] == 'RESOURCE_REFUSAL':
            return factorization
        m.require(factorization['status'] == 'FACTORIZATION_CERTIFIED', 'no nonconstant source factor')
        m.require(m.b.same(candidate['factorization'], factorization), 'source/GCD/quotient/regeneration mismatch')
        stage = 'carrier'
        carrier = candidate['carrier_evidence']
        checked = m.validate_carrier(carrier, factorization['carrier_material'])
        if checked is not True:
            return checked
        stage = 'factor-roots-and-coincidence'
        factors = m.factor_root_events(factorization)
        if factors['status'] == 'RESOURCE_REFUSAL':
            return factors
        m.require(factors['status'] == 'FACTOR_ROOTS_CERTIFIED', 'incomplete full-source factor root evidence')
        m.require(m.b.same(candidate['factor_root_evidence'], factors), 'root/field/order/coincidence/multiplicity mismatch')
        stage = 'exteriors'
        exteriors = m.physical_exteriors(factorization, carrier)
        if exteriors['status'] == 'RESOURCE_REFUSAL':
            return exteriors
        m.require(exteriors['status'] == 'EXTERIORS_CERTIFIED', 'unproved physical exteriors')
        m.require(m.b.same(candidate['physical_exterior_evidence'], exteriors), 'exterior sign or product multiplicity mismatch')
        stage = 'composition'
        expected = m.assemble_product(factorization, carrier, factors, exteriors)
        m.require(m.b.same(candidate, expected), 'physical product union/capability mismatch')
        return True
    except m.RESOURCE_ERRORS as exc:
        return m.refusal('checker:' + stage + ':' + type(exc).__name__)
