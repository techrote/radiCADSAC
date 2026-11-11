"""B1 bounded same-source benchmark: published/reduced naive, incremental and
fully readmitted variants. Research Python only, not native/STEP speed evidence.
"""
import gc, hashlib, json, statistics, time
from fractions import Fraction as Q
from certificate_algebra import (Piece, EvidenceMeter, prove, check_seam,
                                 replace, verify_base, _state, events)
from experiment import snapshot

INITIAL = tuple(Piece(Q(i), Q(i+1), (Q(1),)) for i in range(32))
ORDER = 'ADBCEEC BDA'.replace(' ', '')

def reproof(pieces, meter):
    certs = tuple(prove(p, meter) for p in pieces)  # one Bernstein per piece
    for a, b in zip(pieces, pieces[1:]):
        check_seam(a, b, meter)
    return _state(pieces, certs, 0)

def arm(mode):
    meter = EvidenceMeter()
    s = snapshot(INITIAL, meter) if mode == 'A' else reproof(INITIAL, meter)
    steps = []
    start = time.perf_counter_ns()
    for k in range(64):
        index = k % 32
        coeff = (Q(1), Q(k+1, 16), -Q(k+1, 16))
        if mode in 'ADE':
            pieces = list(s.pieces)
            old = pieces[index]
            pieces[index] = Piece(old.left, old.right, coeff)
            fresh = snapshot(tuple(pieces), meter) if mode == 'A' else reproof(tuple(pieces), meter)
            s = _state(fresh.pieces, fresh.certs, s.generation+1)
        else:
            s = replace(s, index, coeff, meter)
        if mode in 'CE':
            v = EvidenceMeter()
            checked = verify_base([p.source() for p in s.pieces],
                                  [c.record() for c in s.certs], v)
            meter.full_leaf_checks += v.full_leaf_checks
            meter.seam_checks += v.seam_checks
            s = _state(checked.pieces, checked.certs, s.generation)
        assert events(s) == {'identity_intervals':[], 'isolated_points':[]}
        steps.append(s.hash)
    return {'arm':mode, 'ms':(time.perf_counter_ns()-start)/1e6,
            'leaf':meter.full_leaf_checks,'seam':meter.seam_checks,
            'trace':hashlib.sha256(repr(steps).encode()).hexdigest()}

def main():
    assert ORDER == 'ADBCEECBDA'
    for _ in range(2):
        assert len({arm(a)['trace'] for a in 'ADBCE'}) == 1
    readings=[]
    for _ in range(5):
        for a in ORDER:
            gc.collect()
            readings.append(arm(a))
    assert len({x['trace'] for x in readings}) == 1
    summary={a:{'median_ms':statistics.median(x['ms'] for x in readings if x['arm']==a),
                'samples_ms':[round(x['ms'],3) for x in readings if x['arm']==a],
                'leaf':next(x['leaf'] for x in readings if x['arm']==a)} for a in 'ADBCE'}
    print(json.dumps({'class':'PYTHON_MODEL_NOT_NATIVE', 'pieces':32,'updates':64,
                      'warmups':2,'repeats':5,'symmetric_order':ORDER,
                      'per_edit_hash_parity':True,'trace_sha256':readings[0]['trace'],
                      'arms':{'A':'published 3x-Bernstein snapshot',
                              'D':'single-pass fresh full proof',
                              'B':'trusted incremental',
                              'C':'incremental plus full strict readmission',
                              'E':'single-pass fresh full proof plus strict readmission'},
                      'results':summary},sort_keys=True,indent=2))
if __name__=='__main__':
    main()
