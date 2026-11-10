"""Deterministic exact A1-F7 prospective controls; no native/STEP claims."""
from fractions import Fraction as Q
import copy
import unittest
from zero_capacity import FIELDS, Refusal, certify, piece_capacity, spline_pieces, verify


def fixture(controls=None, b='1', l='0', k='1', r='2'):
    c = {f: ['0']*5 for f in FIELDS}
    for f, seq in (controls or {}).items():
        c[f] = seq
    return {'schema':'a1-c0-quadratic-bspline/1', 'L':l,'K':k,'R':r,
            'a':'0','b':b,'controls':c}


class CapacityTests(unittest.TestCase):
    def test_two_span_genuine_knot_zero_continuum(self):
        s = fixture({'H0':['0','0','0','0','1']})
        p = spline_pieces(s)
        self.assertEqual(p[0]['H0'], ['0'])
        self.assertEqual(p[1]['H0'], ['1', '-2', '1'])
        c = certify(s)
        self.assertEqual(c['maximal_identity_zero_continua'], [['0','1']])
        self.assertEqual(c['pieces'][1]['max_zeros_counted_with_multiplicity'], 2)
        self.assertTrue(verify(s, c))

    def test_high_order_sided_multiplicity(self):
        # Each constructed quadratic can have order 2 at K independently;
        # different coefficients must not be collapsed to a global Taylor jet.
        s = fixture({'H0':['1','0','0','0','2']})
        p = spline_pieces(s)
        self.assertEqual(p[0]['H0'], ['1','-2','1'])
        self.assertEqual(p[1]['H0'], ['2','-4','2'])
        self.assertEqual(certify(s)['knot_topology'],'SIDED_GERMS_REQUIRED')

    def test_short_window_repeated_root_capacity(self):
        # 1-cos(2*pi*t), exact double root at t=0, n=3, short width <1/2.
        p={'lo':'-1/8','hi':'1/8','a':'0','b':'1','H0':['1'],
           'C1':['0'],'S1':['0'],'C2':['-1'],'S2':['0']}
        c=piece_capacity(p)
        self.assertEqual((c['dimension'],c['windows'],c['max_zeros_counted_with_multiplicity']), (3,1,2))
        p['b']='-1'
        self.assertEqual(piece_capacity(p)['max_zeros_counted_with_multiplicity'],2)

    def test_polynomial_arbitrarily_close_and_double(self):
        for k in (4,12,24,48,96):
            eps=Q(1,2**k)
            p={'lo':'-1','hi':'1','a':'0','b':'1','H0':['0',str(-eps),'1'],
               'C1':['0'],'S1':['0'],'C2':['0'],'S2':['0']}
            c=piece_capacity(p)
            self.assertEqual(c['max_zeros_counted_with_multiplicity'],2)
            self.assertEqual((Q(0), eps), (Q(0),Q(1,2**k)))
        p['H0']=['0','0','1']
        self.assertEqual(piece_capacity(p)['max_zeros_counted_with_multiplicity'],2)

    def test_frequency_partition_and_budget(self):
        p={'lo':'0','hi':'1','a':'9/5','b':'-7/3','H0':['0'],
           'C1':['0'],'S1':['1'],'C2':['0'],'S2':['0']}
        c=piece_capacity(p)
        self.assertEqual(c['windows'],3)
        self.assertEqual(c['cuts'],['0','1/3','2/3','1'])
        p['b']='300'
        with self.assertRaises(Refusal):
            piece_capacity(p)

    def test_reject_noncanonical_and_source_forgery(self):
        s=fixture({'H0':['0','0','0','0','1']})
        c=certify(s)
        for key,val in [('knot','0'),('claim','COMPLETE'),('source_sha256','fake')]:
            forged=copy.deepcopy(c); forged[key]=val
            self.assertFalse(verify(s,forged))
        changed=copy.deepcopy(s); changed['controls']['H0'][4]='2'
        self.assertFalse(verify(changed,c))
        class EqualAlways(str):
            def __eq__(self,other):return True
            __hash__=str.__hash__
        forged=copy.deepcopy(c); forged['claim']=EqualAlways('arbitrary')
        self.assertFalse(verify(s,forged))
        changed=copy.deepcopy(s); changed['b']='0'
        self.assertFalse(verify(changed,c))
        changed=copy.deepcopy(s); changed['controls']['H0'][0]='1/1'
        self.assertFalse(verify(changed,c))

    def test_identity_and_nonidentity_fourier_splines(self):
        z=fixture()
        c=certify(z)
        self.assertEqual(c['maximal_identity_zero_continua'],[['0','2']])
        self.assertEqual([p['type'] for p in c['pieces']],['IDENTITY_ZERO_CONTINUUM']*2)
        s=fixture({'S1':['1']*5})
        cs=certify(s)
        self.assertTrue(all(x['dimension']==2 and x['max_zeros_counted_with_multiplicity']>=1 for x in cs['pieces']))
        self.assertEqual(cs['maximal_identity_zero_continua'],[])

    def test_exact_factored_polynomial_infinite_family_samples(self):
        # Exact constructed roots, not numerical sampling; d roots saturate n-1.
        cases = 0
        for d in range(1, 13):
            for k in range(1, 7):
                roots = [Q(i - d//2, 2**(k+3)) for i in range(d)]
                coeffs = [Q(1)]
                for root in roots:
                    nxt = [Q(0)] * (len(coeffs)+1)
                    for j, v in enumerate(coeffs):
                        nxt[j] -= root*v
                        nxt[j+1] += v
                    coeffs = nxt
                p = {'lo':'-1/2','hi':'1/2','a':'0','b':'1',
                     'H0':[str(x) for x in coeffs],
                     'C1':['0'],'S1':['0'],'C2':['0'],'S2':['0']}
                c = piece_capacity(p)
                self.assertEqual(c['max_zeros_counted_with_multiplicity'], d)
                self.assertEqual(sum((Q(0) if not roots else Q(1) for _ in roots)), d)
                cases += 1
        self.assertEqual(cases, 72)

    def test_nonphysical_join_refused(self):
        s=fixture({'C1':['0','0','1','0','0']}, l='0',k='1/2',r='2')
        p=spline_pieces(s)
        def value(coeff,t):
            return sum(Q(v)*t**i for i,v in enumerate(coeff))
        self.assertEqual(value(p[0]['C1'],Q(1,2)),Q(1))
        self.assertEqual(value(p[1]['C1'],Q(1,2)),Q(1))
        bad=copy.deepcopy(s); bad['controls']['C1']=['0']*4
        with self.assertRaises(Refusal): certify(bad)

if __name__=='__main__': unittest.main()
