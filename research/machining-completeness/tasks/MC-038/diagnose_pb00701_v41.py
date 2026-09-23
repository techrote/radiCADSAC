#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_orientation_root_partition_model as model
import pb00701_signed_b_anti_diagonal_model as v40
import test_pb00701_orientation_root_partition_adversarial as test

counts = Counter()
examples = {}
old_blocked = 0
new_certified = []
for ra, rb, sa, sb, offset, rate, spec in test._acceptance_candidates():
    old = v40.classify_required_analytic_event(spec)
    if old.get('status') == 'CERTIFIED':
        counts['baseline_certified'] += 1
        continue
    old_blocked += 1
    new = model.classify_required_analytic_event(spec)
    if new.get('status') == 'CERTIFIED':
        new_certified.append({
            'ra': str(ra), 'rb': str(rb), 'sa': str(sa), 'sb': str(sb),
            'offset': str(offset), 'rate': str(rate), 'result': new,
        })
        if len(new_certified) >= 3:
            break
    key = f"{new.get('status')}:{new.get('reason', new.get('relation', ''))}"
    # Pull the first v41 child blocker if the parent wrapper preserved it in spans.
    blocker = None
    for span in new.get('spans', []):
        route = span.get('route', {})
        if span.get('route_kind') == 'PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION':
            cb = route.get('child_blocker', {})
            blocker = cb.get('reason') or cb.get('relation') or route.get('reason')
            if blocker:
                key += f":child={blocker}"
            break
    counts[key] += 1
    examples.setdefault(key, {
        'ra': str(ra), 'rb': str(rb), 'sa': str(sa), 'sb': str(sb),
        'offset': str(offset), 'rate': str(rate),
        'status': new.get('status'), 'reason': new.get('reason'),
        'blocker': blocker,
    })

out = {
    'old_blocked_examined': old_blocked,
    'new_certified_count': len(new_certified),
    'new_certified': new_certified,
    'counts': dict(counts),
    'examples': examples,
    'theorem_observation': (
        'v39/v40 orientation and phase-gap predicates are strict on the closed child; '
        'a child boundary placed at the root of its own dominant coordinate cannot make that same route admissible merely by partitioning.'
    ),
}
Path('v41-diagnostics.json').write_text(json.dumps(out, indent=2, sort_keys=True))
