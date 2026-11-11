"""B1-E4: rational C0 quotient sign/zero transport, research only.

This is a NEW typed rational-function consumer. It never constructs a
Bernstein polynomial receipt for the quotient or authenticates a spline
producer. Exact parent receipts and *independently held* source pins required.
"""
from __future__ import annotations

import re
from certificate_algebra import EvidenceMeter, Refusal, digest, enc, events
from closed_nonzero import _closed
from refined_product import MAX_REFINED_PIECES, _parent, _refine
from receipt_integrity import admit

SCHEMA = 'b1-rational-quotient-v1'
_HEX = re.compile(r'[0-9a-f]{64}\Z')
_FLIP = {'POS': 'NEG', 'NEG': 'POS', 'ZERO': 'ZERO', None: None}


def _external_pin(value: str) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise Refusal('missing canonical externally held parent pin')
    return value


def _event_signs(source_events: dict, denominator_sign: str) -> dict:
    """Carry exact ZERO and CROSS/TOUCH while changing sided signs.

    The denominator is uniformly nonzero even at all genuine/new knots.
    Nothing here asserts a *multiplicity* order for a physical source.
    """
    if denominator_sign not in ('POS', 'NEG'):
        raise Refusal('no closed nonzero denominator witness')
    if denominator_sign == 'POS':
        return source_events
    return {
        'identity_intervals': source_events['identity_intervals'],
        'isolated_points': [
            dict(ev, left=_FLIP[ev['left']], right=_FLIP[ev['right']])
            for ev in source_events['isolated_points']
        ],
    }


def derive(numerator: dict, denominator: dict, *, numerator_pin: str,
           denominator_pin: str):
    """Derive typed rational quotient receipt by independent parent replay.

    Pinned C0 rational-polynomial sources N,D must share a closed domain.
    D must be strictly nonzero on the *closed* domain in the admitted
    Bernstein weak-cone grammar (closed_nonzero B1-E2).

    Returns (receipt, ProofWorkMeter); source-hash custody is external.
    """
    n_pin, d_pin = _external_pin(numerator_pin), _external_pin(denominator_pin)
    meter = EvidenceMeter()
    n = _parent(numerator, n_pin, meter)
    d = _parent(denominator, d_pin, meter)
    if n.pieces[0].left != d.pieces[0].left or n.pieces[-1].right != d.pieces[-1].right:
        raise Refusal('incompatible physical closed domains')
    knots = tuple(sorted({t for s in (n, d) for p in s.pieces
                          for t in (p.left, p.right)}))
    if len(knots) - 1 > MAX_REFINED_PIECES:
        raise Refusal('refinement piece budget exceeded')
    nn, dd = _refine(n, knots, meter), _refine(d, knots, meter)
    # _closed is called ONLY on an already replayed/refined B1 Verified object.
    strict = _closed(dd, 'REFINED_BASE', (d_pin,))
    sign = strict['closed_sign']
    if sign not in ('POS', 'NEG'):
        raise Refusal('unproved denominator sign')
    zero_set = _event_signs(events(nn), sign)
    piece_signs = [c.sign if sign == 'POS' else _FLIP[c.sign] for c in nn.certs]
    identity = {
        'schema': SCHEMA,
        'numerator_pin': n_pin, 'denominator_pin': d_pin,
        'numerator_generation': n.generation, 'denominator_generation': d.generation,
        'physical_knots': [enc(x) for x in knots],
        'aligned_numerator': nn.hash, 'aligned_denominator': dd.hash,
        'denominator_closed_sign': sign,
        'numerator_leaf_hashes': [p.hash for p in nn.pieces],
        'denominator_leaf_hashes': [p.hash for p in dd.pieces],
    }
    receipt = {**identity, 'quotient_hash': digest(identity),
               'representation': 'RATIONAL_C0_NOT_BERNSTEIN_POLYNOMIAL',
               'open_piece_signs': piece_signs, 'events': zero_set}
    # This is one logical rational expression receipt per leaf, not a full
    # Bernstein proof or a timed simulation performance observation.
    meter.transform_checks += len(knots) - 1
    return receipt, meter


def verify(numerator: dict, denominator: dict, proposed: dict, *,
           numerator_pin: str, denominator_pin: str,
           expected_quotient_hash: str | None = None):
    """Replay all algebra and refuse altered, incomplete or stale receipts."""
    if type(proposed) is not dict:
        raise Refusal('missing typed rational quotient receipt')
    receipt, meter = derive(numerator, denominator,
                            numerator_pin=numerator_pin,
                            denominator_pin=denominator_pin)
    admit(receipt, proposed)
    if expected_quotient_hash is not None and (
        _external_pin(expected_quotient_hash) != receipt['quotient_hash']
    ):
        raise Refusal('externally pinned quotient expression has changed')
    return receipt, meter
