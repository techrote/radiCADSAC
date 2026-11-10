"""Independent Fraction controls for A1-F6 complete projective H2 atlas."""
import copy
import unittest
from fractions import Fraction as Q

import projective_h2_atlas as mod


def multiply(a,b):
    result=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            result[i+j]+=x*y
    return tuple(result)


def poly_roots(*roots):
    p=(Q(1),)
    for root in roots:
        p=multiply(p,(-Q(root),Q(1)))
    return p


def coefficients_from_quartic(p):
    # Independent inverse linear transform of the Cayley H2 numerator.
    p=tuple(p)+(Q(0),)*(5-len(p))
    n0,n1,n2,n3,n4=p
    return ((3*(n0+n4)+n2)/8, (n0-n4)/2,
            (n1+n3)/4, (n0+n4-n2)/8, (n1-n3)/8)


def document(c, *,a=Q(0), b=Q(1),lo=Q(-1),hi=Q(1)):
    return dict(a=mod.fmt(Q(a)),b=mod.fmt(Q(b)),
                phase_lo=mod.fmt(Q(lo)),phase_hi=mod.fmt(Q(hi)),
                **{k:mod.fmt(v) for k,v in zip(mod.KEYS[4:],map(Q,c))})


def at_phase(coeff, x):
    # A second derivation via unit-circle rational parameterization:
    # cos(theta)=(1-x²)/(1+x²), sin(theta)=2x/(1+x²).
    h,c,s,d,e=coeff
    cos=(1-x*x)/(1+x*x)
    sin=2*x/(1+x*x)
    return h+c*cos+s*sin+d*(2*cos*cos-1)+e*(2*sin*cos)


class ProjectiveAtlasTests(unittest.TestCase):
    def test_inverse_fourier_quartic_and_direct_trig_identity(self):
        for n in range(-15,16):
            p=(Q(n,7), Q(n*n-4,11), Q(3*n+1,17), Q(n-5,19),Q(4-n,23))
            c=coefficients_from_quartic(p)
            self.assertEqual(mod.projective_numerator(c),mod.trim(p))
            for x in (Q(-7,3),Q(-1),Q(-1,7),Q(0),Q(1,2),Q(7,4)):
                self.assertEqual(at_phase(c,x),mod.val(p,x)/(1+x*x)**2)

    def test_quartic_four_distinct_crossings(self):
        roots=(Q(-3,4),Q(-1,8),Q(1,3),Q(3,4))
        d=document(coefficients_from_quartic(poly_roots(*roots)))
        c=mod.certify(d,bits=26)
        self.assertTrue(mod.verify(d,c))
        self.assertEqual(len(c['events']),4)
        self.assertEqual([e['order'] for e in c['events']],[1]*4)
        self.assertEqual([e['kind'] for e in c['events']],['CROSS']*4)
        self.assertEqual(len(c['charts'][0]['signed_cells']),5)
        for expected,e in zip(roots,c['events']):
            l,h=map(Q,e['bracket_x'])
            self.assertLess(l,expected)
            self.assertLess(expected,h)

    def test_quartic_high_multiplicity_and_signs(self):
        cases=(
          (poly_roots(Q(0),Q(0),Q(0),Q(0)),[(4,'TOUCH')]),
          (poly_roots(Q(1,2),Q(1,2),Q(1,2),Q(-1,2)),[(1,'CROSS'),(3,'CROSS')]),
          (poly_roots(Q(0),Q(0),Q(1,2),Q(1,2)),[(2,'TOUCH'),(2,'TOUCH')]),
        )
        for p,expected in cases:
            with self.subTest(p=p):
                d=document(coefficients_from_quartic(p))
                c=mod.certify(d,bits=26)
                self.assertEqual([(e['order'],e['kind']) for e in c['events']],expected)
                self.assertTrue(mod.verify(d,c))

    def test_exact_pole_orders_boundary_and_internal_not_duplicated(self):
        # H2 = 1-cos(2*pi*q) has double roots at every integer q,
        # including the projective poles at odd q.  Count each once.
        d=document((Q(1),Q(0),Q(0),Q(-1),Q(0)),lo=Q(-1),hi=Q(3))
        c=mod.certify(d,bits=18)
        self.assertEqual(len(c['charts']),2)
        self.assertEqual(len(c['events']),5)  # q=-1,0,1,2,3
        self.assertEqual([e['order'] for e in c['events']],[2]*5)
        self.assertEqual([e['phase'] for e in c['events'] if e['locator']=='PROJECTIVE_POLE'],
                         ['-1/1','1/1','3/1'])
        self.assertEqual([e['role'] for e in c['events'] if e['locator']=='PROJECTIVE_POLE'],
                         ['EXTERIOR_ENDPOINT','INTERNAL_POLE','EXTERIOR_ENDPOINT'])
        self.assertTrue(mod.verify(d,c))

    def test_half_integer_endpoint_zero_and_partial_sector(self):
        # 1-sin(pi*q) has an exact TOUCH at q=1/2 (x=1), endpoint.
        d=document((Q(1),Q(0),Q(-1),Q(0),Q(0)),lo=Q(1,2),hi=Q(1))
        c=mod.certify(d)
        self.assertEqual(len(c['events']),1)
        self.assertEqual(c['events'][0]['phase'],'1/2')
        self.assertEqual(c['events'][0]['physical_time'],'1/2')
        self.assertEqual(c['events'][0]['order'],2)
        self.assertEqual(c['events'][0]['locator'],'EXACT_HALF_TURN_PHASE')
        self.assertTrue(mod.verify(d,c))

    def test_negative_rate_reverses_order_and_sided_germs(self):
        p=poly_roots(Q(-1,3),Q(1,2),Q(3,4),Q(3,4))
        coeff=coefficients_from_quartic(p)
        forward=mod.certify(document(coeff,lo=Q(-1,2),hi=Q(1,2),a=Q(1,7),b=Q(2)))
        reverse=mod.certify(document(coeff,lo=Q(-1,2),hi=Q(1,2),a=Q(1,7),b=Q(-2)))
        self.assertEqual([e['bracket_x'] for e in forward['events']],
                         list(reversed([e['bracket_x'] for e in reverse['events']])))
        for f,r in zip(forward['events'], reversed(reverse['events'])):
            self.assertEqual((f['left_sign'],f['right_sign']),(r['right_sign'],r['left_sign']))
        self.assertTrue(mod.verify(document(coeff,lo=Q(-1,2),hi=Q(1,2),a=Q(1,7),b=Q(-2)),reverse))

    def test_close_rational_projective_roots(self):
        # No fixed minimum separation; different bounded precisions may refuse.
        for exponent in (8,16,32,48):
            eps=Q(1,2**exponent)
            p=poly_roots(Q(0),eps,Q(3,4),Q(3,4))
            d=document(coefficients_from_quartic(p))
            c=mod.certify(d,bits=min(70,exponent+12))
            self.assertEqual([e['order'] for e in c['events']],[1,1,2])
            left,right=map(lambda e:list(map(Q,e['bracket_x'])),c['events'][:2])
            self.assertLess(left[1],right[0])
            self.assertTrue(mod.verify(d,c))

    def test_near_pole_and_exact_pole_both_retained(self):
        # N(x)=x-2^30; finite root approaches q=1 from below,
        # while projective pole q=1 has genuine order 3.
        p=(-Q(2**30),Q(1))
        d=document(coefficients_from_quartic(p),lo=Q(0),hi=Q(1))
        c=mod.certify(d,bits=32)
        self.assertEqual([(e['order'],e['locator']) for e in c['events']],
                         [(1,'STURM_PROJECTIVE_ROOT'),(3,'PROJECTIVE_POLE')])
        l,h=map(Q,c['events'][0]['bracket_x'])
        self.assertLess(l,Q(2**30))
        self.assertLess(Q(2**30),h)
        self.assertTrue(mod.verify(d,c))

    def test_identity_continuum_and_nonzero_no_event(self):
        zero=document((0,0,0,0,0),a=Q(1,2),b=Q(-2),lo=Q(-1,2),hi=Q(1))
        z=mod.certify(zero)
        self.assertEqual(z['kind'],'IDENTITY_ZERO_CONTINUUM')
        self.assertEqual(z['zero_continua'],[['-1/4','1/2']])
        self.assertEqual(z['events'],[])
        self.assertTrue(mod.verify(zero,z))
        const=document((1,0,0,0,0),lo=Q(-1),hi=Q(3))
        c=mod.certify(const)
        self.assertEqual(c['events'],[])
        self.assertTrue(mod.verify(const,c))

    def test_forged_source_and_certificate_refusals(self):
        d=document(coefficients_from_quartic(poly_roots(Q(-1,2),Q(1,2))))
        c=mod.certify(d)
        self.assertTrue(mod.verify(d,c))
        for change in ('source','numerator','root','sign','role','extra','bounds','authentication'):
            src=copy.deepcopy(d);receipt=copy.deepcopy(c)
            if change=='source':src['a']='1/7'
            if change=='numerator':receipt['numerator'][0]='999/1'
            if change=='root':receipt['events'][0]['order']=4
            if change=='sign':receipt['charts'][0]['signed_cells'][0]['sign']*=-1
            if change=='role':receipt['events'][0]['locator']='EXACT_HALF_TURN_PHASE'
            if change=='extra':receipt['known_root_count']=123
            if change=='bounds':receipt['bounds']['bits']=999
            if change=='authentication':receipt['physical_source_authentication']='TRUSTED_BSPLINE'
            self.assertFalse(mod.verify(src,receipt),change)

    def test_typed_nontruth_on_unsupported_budgets_and_grammar(self):
        d=document((1,0,0,-1,0))
        variations=[]
        x=copy.deepcopy(d);x['b']='0/1';variations.append(x)
        x=copy.deepcopy(d);x['phase_lo']='1/3';variations.append(x)
        x=copy.deepcopy(d);x['phase_hi']='40/1';variations.append(x)
        x=copy.deepcopy(d);x['H0']='1';variations.append(x)
        x=copy.deepcopy(d);x['H0']='1.0/1';variations.append(x)
        x=copy.deepcopy(d);x['H0']='1/0';variations.append(x)
        x=copy.deepcopy(d);x['H0']=1;variations.append(x)
        x=copy.deepcopy(d);x['amplitude_polynomial']=['1/1','1/1'];variations.append(x)
        for x in variations:
            with self.subTest(x=x),self.assertRaises(mod.Refusal):
                mod.certify(x)
        with self.assertRaisesRegex(mod.Refusal,'ISOLATION_BITS_BUDGET'):
            mod.certify(d,bits=1000)

    def test_infinite_rational_parameter_family_finite_controls(self):
        # Four real roots all rational, varied affine phases, 72 members.
        for k in range(1,73):
            eps=Q(1,2**(k%28+5))
            p=poly_roots(Q(-1,4),Q(0),eps,Q(1,2))
            d=document(coefficients_from_quartic(p),a=Q(k,37),
                       b=Q(-3,2) if k%2 else Q(7,5),lo=Q(-1),hi=Q(1))
            c=mod.certify(d,bits=40)
            self.assertEqual(len(c['events']),4)
            self.assertEqual([e['order'] for e in c['events']],[1]*4)
            self.assertTrue(mod.verify(d,c))


if __name__=='__main__':
    unittest.main()
