#!/usr/bin/env python3
"""V54 finite, supplied-witness-guided validation of historical owner routes.

The historical *_route functions are CONSTRUCTORS that select a successful
anchor/harmonic. Calling them while checking allows replacement proof search.
Here the supplied certificate fixes the owner, harmonic and quadrature. Only
that branch's exact source-owned polynomial/sector/orthant arithmetic executes.

Historical route source is parsed (not executed) for its pinned, literal
metadata; the mathematical fields are independently rebuilt from the exact
source and the submitted selection. This prevents both unreviewed extra fields
and forged textual/capability metadata without invoking a historical selector.
"""
from __future__ import annotations

import ast
from functools import lru_cache
from importlib import import_module
from pathlib import Path

import pb00701_finite_owner_span_model as m

# One finite, deterministic leaf checker per historical strict owner. In
# particular, these are NOT the route-level anchor/harmonic selection functions.
LEAVES = {
    20: '_pointwise_derivative_envelope_certificate',
    21: '_l1_sign_orthant_derivative_certificate',
    22: '_phase_anchor_derivative_certificate',
    23: '_nonconstant_phase_anchor_derivative_certificate',
    24: '_mixed_phase_anchor_derivative_certificate',
    25: '_dominance_attempt',
    26: '_dominance_attempt',
    28: '_dominance_attempt',
    29: '_dominance_attempt',
    30: '_dominance_attempt',
    34: '_phase_correlated_derivative_certificate',
    35: '_phase_correlated_proportional_derivative_certificate',
    36: '_phase_correlated_varying_ratio_derivative_certificate',
    37: '_phase_correlated_two_polynomial_derivative_certificate',
    38: '_phase_correlated_direct_derivative_certificate',
    39: '_phase_correlated_signed_direct_derivative_certificate',
    40: '_phase_correlated_signed_b_derivative_certificate',
    42: '_transition_derivative_certificate',
    43: '_correlated_derivative_certificate',
}
DOMINANCE = {25, 26, 28, 29, 30}
COMPONENT = {22, 23}
RESIDUAL = {22, 23, 24, 25}


@lru_cache(maxsize=None)
def _static_route_shape(owner):
    """Freeze literal historical fields from source, without calling its selector.

    All nonliteral fields must be in the explicit source-derived witness schema.
    The historical modules are Git-blob pinned by verify_pb00701_v54.py.
    """
    entry = m.STRICT_ADAPTERS[owner]
    module = import_module(entry['module'])
    tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == entry['recipe']]
    m.require(len(functions) == 1, 'pinned owner route function not unique')

    matches = []
    for node in ast.walk(functions[0]):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        fields = {k.value: v for k, v in zip(node.value.keys, node.value.values)
                  if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        status = fields.get('status')
        if (isinstance(status, ast.Constant) and status.value == 'CERTIFIED'
                and {'relation', 'source_parameter_id', 'left_event', 'right_event'} <= set(fields)):
            matches.append(node.value)
    m.require(len(matches) == 1, 'pinned owner has no unique certified route constructor')
    static, dynamic = {}, set()
    expansions = 0
    for key_node, value in zip(matches[0].keys, matches[0].values):
        if key_node is None:
            m.require(isinstance(value, ast.Name) and value.id == 'root_summary',
                      'unreviewed route dictionary expansion')
            expansions += 1
            continue
        m.require(isinstance(key_node, ast.Constant) and isinstance(key_node.value, str),
                  'unreviewed route metadata key')
        key = key_node.value
        if isinstance(value, ast.Constant):
            static[key] = value.value
        elif key == 'relation' and isinstance(value, ast.Name):
            m.require(value.id.startswith('V') and value.id.endswith('_ROUTE'),
                      'unexpected historical relation authority')
            static[key] = getattr(module, value.id)
        else:
            dynamic.add(key)
    m.require(expansions == 1 and static.get('status') == 'CERTIFIED',
              'owner route does not expand one exact root summary')
    selected = entry['direction_certificate']
    expected_dynamic = {'source_parameter_id', 'active_positive_harmonics',
                        'phase_turn_law_local', 'left_event', 'right_event', selected}
    if entry['version'] in RESIDUAL:
        expected_dynamic.add('residual_l1_certificate')
    m.require(dynamic == expected_dynamic,
              'historical owner route has unreviewed dynamic source/proof fields')
    return static


def _selected_certificate(owner, route, c, s, offset, rate):
    entry = m.STRICT_ADAPTERS[owner]
    version = entry['version']
    module = import_module(entry['module'])
    selected = route[entry['direction_certificate']]
    m.require(isinstance(selected, dict) and selected.get('status') == 'CERTIFIED',
              'missing source-bound selected strict derivative witness')
    leaf = getattr(module, LEAVES[version])
    if version in (20, 21):
        produced = leaf(c, s, rate)
    else:
        harmonic = selected['harmonic']
        m.require(type(harmonic) is int and harmonic > 0,
                  'selected harmonic must be a strictly positive integer')
        if version in COMPONENT:
            m.require(selected['component'] in ('SIN', 'COS'),
                      'invalid selected pure quadrature')
            produced = leaf(c, s, offset, rate, harmonic, selected['component'])
        elif version in DOMINANCE:
            dominant = selected['dominant_component']
            m.require(dominant in ('SIN', 'COS'), 'unrecognized selected quadrature')
            # Validate the submitted single branch, never scan for a replacement.
            produced = leaf(c, s, offset, rate, harmonic, dominant)
            if isinstance(produced, dict) and produced.get('status') == 'CERTIFIED':
                previous = []
                if dominant == 'COS':
                    # Historical SIN-first diagnostics belong to the witness;
                    # check that earlier specific failure, not an alternative win.
                    failed_sin = leaf(c, s, offset, rate, harmonic, 'SIN')
                    if isinstance(failed_sin, dict) and failed_sin.get('status') == 'RESOURCE_REFUSAL':
                        return failed_sin
                    m.require(isinstance(failed_sin, dict) and failed_sin.get('status') != 'CERTIFIED',
                              'a purported COS witness bypasses a successful earlier SIN branch')
                    previous = [failed_sin]
                produced = {**produced, 'alternate_dominance_attempts_before_success': previous}
        else:
            produced = leaf(c, s, offset, rate, harmonic)
    if isinstance(produced, dict) and produced.get('status') == 'RESOURCE_REFUSAL':
        return produced
    m.require(isinstance(produced, dict) and produced.get('status') == 'CERTIFIED',
              'selected witness leaf did not certify the original source')
    m.require(m.b.same(selected, produced), 'supplied selected strict certificate differs from exact leaf')
    if version == 39:
        m.require(selected.get('sigma_A') == -1,
                  'signed-A V39 owner requires the source-derived negative orientation')
    return produced


def validate_owner_witness(owner, route, material):
    """True or typed non-truth refusal. No historical _route or classifier call."""
    m.require(isinstance(route, dict), 'missing owner witness')
    c, s = m._fraction_maps(material)
    if owner == m.SIGN_OWNER:
        entry = m.SIGN_ADAPTERS[owner]
        module = import_module(entry['module'])
        expected = getattr(module, entry['recipe'])(c, s)  # V7 finite dominance bound
        if isinstance(expected, dict) and expected.get('status') == 'RESOURCE_REFUSAL':
            return expected
        m.require(isinstance(expected, dict) and expected.get('status') == 'CERTIFIED'
                  and m.b.same(route, expected),
                  'V7 root-free sign/margin witness does not match the original source')
        return True

    m.require(owner in m.STRICT_ADAPTERS, 'owner lacks supplied-witness finite checking')
    entry = m.STRICT_ADAPTERS[owner]
    static = _static_route_shape(owner)
    offset, rate = m.b.local_phase(material)
    m.require(rate != 0, 'strict historical owner requires nonzero source phase rate')
    leaf = _selected_certificate(owner, route, c, s, offset, rate)
    if isinstance(leaf, dict) and leaf.get('status') == 'RESOURCE_REFUSAL':
        return leaf

    import pb00701_multiharmonic_monotone_anchor_model as v19
    left = v19._endpoint_relation(c, s, m.q(0), offset)
    right = v19._endpoint_relation(c, s, m.q(1), offset + rate)
    for event in (left, right):
        if event.get('status') == 'RESOURCE_REFUSAL':
            return event
        m.require(event.get('status') == 'DECIDED', 'undecided original-source endpoint')

    summary = v19._root_summary(leaf['direction'], left, right)
    m.require(summary.get('status') == 'CERTIFIED',
              'supplied selected strict derivative contradicts exact endpoints')
    active = sorted(int(h) for h in set(c) | set(s) if int(h) > 0
                    and (m.a.trim(c.get(h, [0])) != [0]
                         or m.a.trim(s.get(h, [0])) != [0]))
    expected = {
        **static,
        'source_parameter_id': material['source_parameter_id'],
        'active_positive_harmonics': active,
        'phase_turn_law_local': {'offset': str(offset), 'rate': str(rate)},
        entry['direction_certificate']: leaf,
        'left_event': left, 'right_event': right,
        **summary,
    }
    version = entry['version']
    if version in RESIDUAL:
        module = import_module(entry['module'])
        if version == 22:
            residual = module._residual_l1_certificate(c, s, rate, leaf)
        elif version == 23:
            residual = module.v22._residual_l1_certificate(c, s, rate, leaf)
        elif version == 24:
            residual = module._mixed_residual_l1_certificate(c, s, rate, leaf)
        else:
            residual = module.v24._mixed_residual_l1_certificate(c, s, rate, leaf)
        if isinstance(residual, dict) and residual.get('status') == 'RESOURCE_REFUSAL':
            return residual
        m.require(isinstance(residual, dict) and residual.get('status') == 'CERTIFIED',
                  'selected anchor lacks exact whole-derivative residual dominance')
        expected['residual_l1_certificate'] = residual

    m.require(m.b.same(route, expected),
              'historical owner route/source/selected witness/metadata mismatch')
    return True
