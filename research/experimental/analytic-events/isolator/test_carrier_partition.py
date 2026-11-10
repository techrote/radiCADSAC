"""A1-F4 deterministic exact rational adversarial controls."""
from fractions import Fraction as Q
import copy, unittest
import carrier_partition as cp

def poly(*p):return cp.trim(tuple(Q(x) for x in p))
def mul(a,b):
    r=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):r[i+j]+=x*y
    return cp.trim(r)
def factor(*pairs):
    p=(Q(1),)
    for root,multiplicity in pairs:
        for _ in range(multiplicity):p=mul(p,(-Q(root),Q(1)))
    return p

def row(l,h,p,h0=(Q(2),),c1=(Q(1,10),),s1=(),c2=(),s2=(Q(1,20),)):
    co=(h0,c1,s1,c2,s2)
    z={'lo':cp.fmt(Q(l)),'hi':cp.fmt(Q(h))}
    for k,q in zip(cp.KEYS,co):
        z[k]=list(map(cp.fmt,(mul(p,q) or (Q(0),)) if q else (Q(0),)))
    return z

def doc(*rows,a=Q(1,7),b=Q(1,2)):
    return {'a':cp.fmt(Q(a)),'b':cp.fmt(Q(b)),'pieces':list(rows)}

class CarrierTests(unittest.TestCase):
    def test_mixed_harmonic_complete_partition(self):
        p=factor((Q(1,3),2),(Q(2,3),1),(Q(1),1))
        d=doc(row(0,2,p))
        cert=cp.certify(d,bits=24)
        self.assertTrue(cp.verify(d,cert))
        events=cert['pieces'][0]['events']
        self.assertEqual([e['multiplicity'] for e in events],[2,1,1])
        self.assertEqual([e['kind'] for e in events],['TOUCH','CROSS','CROSS'])
        self.assertEqual(len(cert['pieces'][0]['cells']),4)
        for e in events:
            l,h=map(Q,e['bracket'])
            self.assertEqual(cp.roots_between(cp.sequence(cp.squarefree(p)),cp.squarefree(p),l,h),1)

    def test_arbitrarily_close_rational_pair(self):
        for bits in (8,16,32,48):
            eps=Q(1,2**bits)
            p=factor((Q(3,5),1),(Q(3,5)+eps,1),(Q(4,3),2))
            c=cp.certify(doc(row(0,2,p)),bits=min(bits+10,64),max_depth=8)
            events=c['pieces'][0]['events']
            self.assertEqual(len(events),3)
            self.assertEqual([e['multiplicity'] for e in events],[1,1,2])

    def test_endpoint_and_signed_knot_orders(self):
        # Two coefficient-continuous pieces with a true analytic-derivative kink at 1.
        a=row(0,1,factor((Q(1),2)),h0=(Q(4),),c1=(Q(1,20),),s2=())
        b=row(1,2,factor((Q(1),1)),h0=(Q(4),),c1=(Q(1,20),),s2=())
        d=doc(a,b,b=Q(-3,2))
        c=cp.certify(d)
        self.assertTrue(cp.verify(d,c))
        self.assertEqual(c['pieces'][0]['sided']['right']['multiplicity'],2)
        self.assertEqual(c['pieces'][1]['sided']['left']['multiplicity'],1)
        self.assertEqual(c['pieces'][0]['sided']['right']['left_germ_sign'],1)
        self.assertEqual(c['pieces'][1]['sided']['left']['right_germ_sign'],1)
        self.assertEqual(len(c['knots']),1)
        self.assertEqual(c['knots'][0]['kind'],'SINGLE_PHYSICAL_KNOT_ZERO')
        self.assertEqual((c['knots'][0]['left_order'],c['knots'][0]['right_order']),(2,1))
        corrupted=copy.deepcopy(d)
        corrupted['pieces'][1]['C1']=['2/1','-1/1']
        with self.assertRaisesRegex(cp.Refusal,'C0_CHANNEL_SEAM'):
            cp.certify(corrupted)

    def test_identity_zero_piece_preserved(self):
        z=row(0,1,(Q(0),)); p=row(1,2,factor((Q(1),1)))
        d=doc(z,p)
        c=cp.certify(d)
        self.assertEqual(c['pieces'][0]['kind'],'IDENTITY_ZERO_CONTINUUM')
        self.assertEqual(c['pieces'][1]['sided']['left']['multiplicity'],1)
        self.assertTrue(c['knots'][0]['left_continuum'])
        self.assertEqual(c['knots'][0]['right_order'],1)

    def test_root_free_signed_harmonic(self):
        d=doc(row(0,1,(Q(1),),h0=(Q(-2),),c1=(Q(1,10),),s2=()))
        c=cp.certify(d)
        self.assertEqual(c['pieces'][0]['events'],[])
        self.assertEqual(c['pieces'][0]['cofactor_sign'],-1)
        self.assertEqual(c['pieces'][0]['cells'][0]['sign'],-1)

    def test_refuse_cotranscendental_zero_not_absent(self):
        # No common polynomial factor, and H has a genuine phase zero t=1/2.
        d=doc(row(0,1,(Q(1),),h0=(Q(0),),c1=(Q(0),),s1=(Q(1),),s2=()),a=Q(-1,2),b=Q(1))
        with self.assertRaisesRegex(cp.Refusal,'COFACTOR_SIGN_BUDGET'):
            cp.certify(d,max_depth=5)

    def test_tamper_receipt_and_phase(self):
        d=doc(row(0,2,factor((Q(1,3),2))))
        c=cp.certify(d)
        for change in ('source','event','phase','cover','knot'):
            d1=copy.deepcopy(d); c1=copy.deepcopy(c)
            if change=='source':d1['pieces'][0]['H0'][0]='1/1'
            if change=='event':c1['pieces'][0]['events'][0]['multiplicity']=7
            if change=='phase':d1['a']='2/7'
            if change=='cover':c1['pieces'][0]['cover'][0][2]=-1
            if change=='knot':c1['pieces'][0]['interval'][1]='9/1'
            self.assertFalse(cp.verify(d1,c1),change)

    def test_parameterized_infinite_family_and_exact_root_oracle(self):
        # The proof covers all rational parameters; this finite run attacks 48.
        for n in range(1,49):
            r=Q(1,3)+Q(1,2**(n+3))
            p=factor((Q(1,3),2),(r,1),(Q(4,3),2))
            d=doc(row(0,2,p,h0=(Q(3+n,10),),c1=(Q(1,100),),s2=(Q(1,200),)),
                  a=Q(n,13),b=Q((-1)**n,2))
            c=cp.certify(d,bits=40)
            self.assertEqual([e['multiplicity'] for e in c['pieces'][0]['events']],[2,1,2])
            self.assertEqual(len(c['pieces'][0]['events']),3)
            self.assertTrue(cp.verify(d,c))
            for expected,e in zip((Q(1,3),r,Q(4,3)),c['pieces'][0]['events']):
                lo,hi=map(Q,e['bracket'])
                self.assertTrue(lo<expected<hi)

    def test_pure_harmonic_nonvanishing_cofactor(self):
        p=factor((Q(1,10),2))
        d=doc(row(0,Q(1,8),p,h0=(),c1=(Q(1),),s2=()),a=Q(0),b=Q(1,2))
        c=cp.certify(d)
        self.assertEqual(c['pieces'][0]['cofactor_sign'],1)
        self.assertEqual(c['pieces'][0]['events'][0]['multiplicity'],2)

    def test_disallow_invalid_grammar_and_limits(self):
        d=doc(row(0,2,factor((Q(1,2),1))))
        for mutate in ('gap','phase','bits','trailing','wrong_pieces'):
            x=copy.deepcopy(d)
            if mutate=='gap':x['pieces'].append(row(3,4,(Q(1),)))
            if mutate=='phase':x['b']='0/1'
            if mutate=='bits':x['pieces'][0]['H0'][0]='1/999999999999999999999999999999999999999999999'
            if mutate=='trailing':x['pieces'][0]['C1'].append('0/1')
            if mutate=='wrong_pieces':x['pieces']='bad'
            with self.assertRaises(cp.Refusal):cp.certify(x)

if __name__=='__main__':unittest.main()
