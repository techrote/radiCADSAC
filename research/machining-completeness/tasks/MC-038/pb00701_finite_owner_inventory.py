#!/usr/bin/env python3
"""V54 executable finite owner inventory for the admitted PB-007-01 B-spline chain.

Two independent enumerations must agree with the single canonical owner table:
static literal route_kind emitters in the implemented historical modules, and
owners actually observed by running the frozen admitted-source corpus through
the complete unchanged predecessor chain. Observation never classifies a span
into a category; it only looks the observed identifier up in the table.
"""
import ast
import json
from pathlib import Path
import sys

TASK = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK))
import pb00701_finite_owner_span_model as m

SCHEMA = 'radicadsac-pb00701-finite-owner-inventory/54.0'
CORPUS = TASK / 'pb00701-finite-owner-corpus-v54.json'
CATEGORY_NAMES = {1: 'ALREADY_SUPPORTED_ORDERED', 2: 'FINITE_OWNER_ORDERED_VIEW_ADAPTED',
                  3: 'EXACT_OWNER_LACKING_ORDERED_SPAN_PREMISE', 4: 'BLOCKER_REFUSAL_OR_NON_EVENT'}


def emitter_paths():
    # Only implemented historical owner producers; V54 itself emits no owner.
    return [path for path in sorted(TASK.glob('pb00701_*.py'))
            if not path.name.startswith('pb00701_finite_owner_')]


def static_emitters():
    """Every literal string assigned to a route_kind name or ['route_kind'] subscript."""
    found = {}
    for path in emitter_paths():
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                pairs = (zip(target.elts, node.value.elts) if isinstance(target, ast.Tuple) and
                         isinstance(node.value, ast.Tuple) else [(target, node.value)])
                for left, value in pairs:
                    key = (left.slice.value if isinstance(left, ast.Subscript) and isinstance(left.slice, ast.Constant)
                           else left.id if isinstance(left, ast.Name) else None)
                    if key == 'route_kind' and isinstance(value, ast.Constant) and isinstance(value.value, str):
                        found.setdefault(value.value, set()).add(path.name)
    return {owner: sorted(paths) for owner, paths in found.items()}


def owner_row(owner, emitters):
    number = m.category(owner)
    m.require(number is not None, 'unclassified historical owner: ' + owner)
    row = {'owner': owner, 'category': number, 'category_name': CATEGORY_NAMES[number],
           'emitter_modules': emitters[owner]}
    if number == 1:
        entry = m.ALREADY_ORDERED[owner]
        row.update(version=entry['version'], view_kind=entry['view_kind'], adapter=None)
    elif number == 2:
        entry = m.SIGN_ADAPTERS.get(owner) or m.STRICT_ADAPTERS[owner]
        row.update(version=entry['version'], adapter=entry['adapter'],
                   view_kind='SIGN_SPAN' if owner in m.SIGN_ADAPTERS else 'OWNER_STRICT_SPAN',
                   owner_recipe=entry['module'] + '.' + entry['recipe'],
                   ordered_premise=('CLOSED_SPAN_EXACT_RATIONAL_AMPLITUDE_DOMINANCE_ROOT_FREE_SIGN'
                                    if owner in m.SIGN_ADAPTERS else
                                    'WHOLE_CLOSED_SPAN_STRICT_COMPLETE_DERIVATIVE:' + entry['direction_certificate']))
    elif number == 3:
        version, premise = m.LACKING_PREMISE[owner]
        row.update(version=version, view_kind=None, adapter=None, missing_premise=premise)
    else:
        version, disposition = m.BLOCKED_OWNERS[owner]
        row.update(version=version, view_kind=None, adapter=None, disposition=disposition)
    return row


def inventory():
    emitters = static_emitters()
    table = {**m.ALREADY_ORDERED, **m.SIGN_ADAPTERS, **m.STRICT_ADAPTERS, **m.LACKING_PREMISE, **m.BLOCKED_OWNERS}
    m.require(set(emitters) == set(table), 'static emitters and canonical owner table disagree')
    rows = [owner_row(owner, emitters) for owner in sorted(table, key=lambda o: (m.category(o), o))]
    counts = {str(n): sum(row['category'] == n for row in rows) for n in CATEGORY_NAMES}
    return {'schema': SCHEMA, 'owner_count': len(rows), 'category_counts': counts,
            'category_names': {str(k): v for k, v in CATEGORY_NAMES.items()}, 'owners': rows,
            'one_category_per_owner': True, 'counts_promoted_to_order': False,
            'unknown_owner_disposition': 'SPAN_OWNER_OUTSIDE_FINITE_V54_INVENTORY'}


def observe_spans(spec):
    """Per-span owners from the complete unchanged physical chain (V51-V53 keep owners)."""
    result = m.v50.classify_required_analytic_event(spec)
    if not isinstance(result, dict) or 'spans' not in result:
        return {'status': result.get('status') if isinstance(result, dict) else None, 'spans': []}
    return {'status': result['status'],
            'spans': [[span.get('route_kind'), span.get('route', {}).get('status'),
                       None if span.get('route', {}).get('status') == 'CERTIFIED' else span.get('route', {}).get('reason')]
                      for span in result['spans']]}


def disposition(result):
    """Outcome label of the complete V54 source wrapper; never a new truth value."""
    status = result.get('status') if isinstance(result, dict) else None
    reason = result.get('reason') if isinstance(result, dict) else None
    return status if reason is None else status + ':' + reason


def load_corpus():
    return json.loads(CORPUS.read_text())


def run_case(case):
    observed = observe_spans(case['spec'])
    result = m.build_finite_owner_source_evidence(case['spec'])
    row = {'id': case['id'], 'observed': observed, 'v54_disposition': disposition(result)}
    if isinstance(result, dict) and result.get('status') == 'FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED':
        certificate = result['certificate']
        row['view_kinds'] = certificate['span_evidence_kinds']
        row['global_root_summary'] = certificate['global_root_summary']
        row['maximal_signs'] = [cell['physical_sign'] for cell in certificate['maximal_open_sign_cells']]
    return row


def corpus_summary(rows):
    observed = sorted({span[0] for row in rows for span in row['observed']['spans']})
    unknown = [owner for owner in observed if m.category(owner) is None]
    m.require(not unknown, 'observed owner outside canonical table')
    by_category = {str(n): sorted(o for o in observed if m.category(o) == n) for n in CATEGORY_NAMES}
    dispositions = {}
    for row in rows:
        dispositions[row['v54_disposition']] = dispositions.get(row['v54_disposition'], 0) + 1
    remaining = {}
    for row in rows:
        for owner, status, reason in row['observed']['spans']:
            if status != 'CERTIFIED':
                key = owner + ':' + str(reason)
                remaining[key] = remaining.get(key, 0) + 1
    return {'cases': len(rows), 'observed_owner_count': len(observed),
            'observed_by_category': by_category, 'v54_dispositions': dict(sorted(dispositions.items())),
            'remaining_uncertified_span_owner_reasons': dict(sorted(remaining.items()))}


if __name__ == '__main__':
    print(json.dumps(inventory()['category_counts']))
