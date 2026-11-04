"""Exact rational-Cayley event atlas for constant H0+H1 cosine/sine moving-phase spans.

Research certificate only. Refusal != mathematical nonexistence. No floating-point
math is used; implicit roots remain specified by exact quadratic radicals.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from math import floor, ceil

class Refusal(ValueError):
    pass

def sgn(x):
    return (x > 0) - (x < 0)

def surd_sign(b, eps, d):
    """Sign of rational b + eps*sqrt(d), d>=0, eps in {-1,0,1}."""
    if d < 0 or eps not in (-1, 0, 1):
        raise Refusal('bad radical')
    if eps == 0 or d == 0:
        return sgn(b)
    if eps == 1:
        if b >= 0: return 1
        return sgn(d - b*b)
    if b <= 0: return -1
    return sgn(b*b - d)

@dataclass(frozen=True)
class Root:
    numerator: Q
    radical_sign: int
    radical_square: Q
    denominator: Q
    order: int
    def sign(self):
        return self.compare(Q(0))
    def compare(self, rational):
        """Exact sign of this signed-radical z minus a rational tan boundary."""
        return surd_sign(self.numerator-rational*self.denominator,
                         self.radical_sign,self.radical_square)*sgn(self.denominator)
    def as_dict(self):
        return dict(numerator=str(self.numerator),radical_sign=self.radical_sign,radical_square=str(self.radical_square),denominator=str(self.denominator),order=self.order)

def finite_cayley_roots(A,C,S):
    """P(z)=(A-C)z^2+2Sz+(A+C); in increasing z order."""
    a=A-C; d=C*C+S*S-A*A
    if a:
        if d<0: return []
        if d==0: return [Root(-S,0,Q(0),a,2)]
        lo=Root(-S,-sgn(a),d,a,1)
        hi=Root(-S,sgn(a),d,a,1)
        return [lo,hi]
    if S:
        return [Root(-A,0,Q(0),S,1)]  # z=-A/S
    return []

def integer_quarter(v): return (4*v).denominator==1

def phase_cmp_root_to_boundary(n,root,endpoint):
    """Compare n+atan(z)/pi with an exact integer-quarter phase boundary."""
    if endpoint<=Q(2*n-1,2): return 1
    if endpoint>=Q(2*n+1,2): return -1
    offset=endpoint-Q(n)
    if offset==Q(-1,4): return root.compare(Q(-1))
    if offset==Q(0): return root.sign()
    if offset==Q(1,4): return root.compare(Q(1))
    raise Refusal('endpoint not an admitted quarter-turn')

def source_sign(A,C,S,p,on_right):
    """Physical one-sided nonzero germ at integer-quarter phase, no division."""
    if not integer_quarter(p): raise Refusal('endpoint not quarter-turn')
    residue=(4*p).numerator%4
    co,si={0:(1,0),1:(0,1),2:(-1,0),3:(0,-1)}[residue]
    f=A+co*C+si*S
    if f: return sgn(f)
    deriv=co*S-si*C
    if deriv: return sgn(deriv)*(1 if on_right else -1)
    if A: return sgn(A)  # exact second order and same-sided sign
    raise Refusal('identity must be handled separately')

def certify_span(*,lo,hi,offset,rate,A,C,S,max_strips=64):
    vals=[lo,hi,offset,rate,A,C,S]
    if not all(isinstance(v,Q) for v in vals): raise Refusal('all input must be exact Fractions')
    if lo>=hi or rate<=0: raise Refusal('invalid domain/rate')
    p0=offset+rate*lo; p1=offset+rate*hi
    if not (integer_quarter(p0) and integer_quarter(p1)): raise Refusal('phase endpoints not in 1/4 Z')
    if p1-p0>max_strips: raise Refusal('bounded-resource refusal; not a mathematical zero claim')
    if A==C==S==0:
        return dict(kind='IDENTITY_ZERO',phase_interval=[str(p0),str(p1)],events=[],sign_cells=[],zero_component=[str(lo),str(hi)],phase_rate=str(rate))
    roots=finite_cayley_roots(A,C,S)
    events=[]
    # Fully exact algebraic root locators within tan(pi*(phase-n)) branches.
    for n in range(floor(p0)-1,ceil(p1)+2):
        if Q(2*n+1,2)<=p0 or Q(2*n-1,2)>=p1: continue
        for ix,root in enumerate(roots):
            cmp_lo=phase_cmp_root_to_boundary(n,root,p0)
            cmp_hi=phase_cmp_root_to_boundary(n,root,p1)
            if cmp_lo>=0 and cmp_hi<=0:
                events.append(dict(kind='CAYLEY_ROOT',branch=n,branch_rank=ix,order=root.order,
                                   root=root.as_dict(),position=('interior' if cmp_lo>0 and cmp_hi<0 else 'endpoint')))
    # Pole at phase=k+1/2 is part of original function, NOT a removed singularity.
    if A==C:
        pole_order=1 if S else 2
        for k in range(floor(p0)-1,ceil(p1)+2):
            phase=Q(2*k+1,2)
            if p0<=phase<=p1:
                events.append(dict(kind='PHASE_POLE_ZERO',branch=k,branch_rank=2,phase=str(phase),
                                   order=pole_order, position=('interior' if p0<phase<p1 else 'endpoint')))
    events.sort(key=lambda e:(e['branch'],e['branch_rank']))
    first=source_sign(A,C,S,p0,True)
    last=source_sign(A,C,S,p1,False)
    signs=[first]
    for event in events:
        if event['position']=='interior':
            signs.append(signs[-1]*(-1 if event['order']%2 else 1))
    if signs[-1]!=last: raise AssertionError('analytic sign transfer inconsistent')
    return dict(kind='FINITE_EVENTS',phase_interval=[str(p0),str(p1)],phase_rate=str(rate),
                coefficient_triple=[str(A),str(C),str(S)],
                events=events,sign_cells=signs,
                endpoint_zeros=[any(e['position']=='endpoint' and
                                    ((e['kind']=='PHASE_POLE_ZERO' and e['phase']==str(p)) or
                                     (e['kind']=='CAYLEY_ROOT' and
                                      (phase_cmp_root_to_boundary(e['branch'],
                                        Root(Q(e['root']['numerator']),e['root']['radical_sign'],Q(e['root']['radical_square']),Q(e['root']['denominator']),e['order']),p)==0)))
                                    for e in events) for p in (p0,p1)])

def self_test():
    def c(a,c,s,phase0,phase1):
        return certify_span(lo=Q(0),hi=Q(1),offset=Q(phase0),rate=Q(phase1)-Q(phase0),A=Q(a),C=Q(c),S=Q(s))
    v10=certify_span(lo=Q(1),hi=Q(2),offset=Q(-1,2),rate=Q(2),A=Q(0),C=Q(1),S=Q(-1,2))
    assert len(v10['events'])==4 and [e['order'] for e in v10['events']]==[1]*4
    assert v10['sign_cells']==[-1,1,-1,1,-1]
    v11=certify_span(lo=Q(1),hi=Q(2),offset=Q(0),rate=Q(2),A=Q(0),C=Q(1,8),S=Q(1))
    assert len(v11['events'])==4 and v11['sign_cells']==[1,-1,1,-1,1]
    # Original frozen V8 tail0 V27-refused child: finite-z-only Cayley misses
    # its physical simple root at tan(pi*phase) = infinity.
    v8=certify_span(lo=Q(1),hi=Q(2),offset=Q(-1,4),rate=Q(1,2),A=Q(0),C=Q(0),S=Q(1,2))
    assert len(v8['events'])==1 and v8['events'][0]['kind']=='PHASE_POLE_ZERO'
    assert v8['events'][0]['phase']=='1/2' and v8['events'][0]['order']==1
    assert v8['sign_cells']==[1,-1] and v8['endpoint_zeros']==[False,False]
    assert len(finite_cayley_roots(Q(0),Q(0),Q(1,2)))==1  # finite root z=0 lies OUTSIDE this child
    assert c(0,0,0,0,1)['kind']=='IDENTITY_ZERO'
    assert c(2,1,0,0,1)['events']==[]
    assert c(-2,1,0,0,1)['sign_cells']==[-1]
    tangent=c(1,1,0,0,1)
    assert len(tangent['events'])==1 and tangent['events'][0]['order']==2 and tangent['sign_cells']==[1,1]
    cross_pole=c(1,1,1,0,1)
    assert len(cross_pole['events'])==2 and cross_pole['sign_cells']==[1,-1,1]
    near=c(Q(1)-Q(1,2**200),1,0,0,1)
    assert len(near['events'])==2 and near['sign_cells']==[1,-1,1]
    ep=c(1,0,1,Q(-1,2),Q(1,2))
    assert len(ep['events'])==1 and ep['events'][0]['order']==2 and ep['sign_cells']==[1,1]
    for p0,p1 in [(Q(0),Q(1,8)),(Q(0),Q(100)),(Q(1),Q(0))]:
        try: c(0,1,0,p0,p1); assert False
        except Refusal: pass
    assert surd_sign(Q(-1),1,Q(1))==0
    assert surd_sign(Q(-2),1,Q(1))==-1
    assert surd_sign(Q(2),-1,Q(1))==1
    return v10,v11

if __name__=='__main__':
    from pprint import pprint
    a,b=self_test(); pprint(a);pprint(b)
