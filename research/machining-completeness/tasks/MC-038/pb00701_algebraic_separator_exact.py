#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction
from math import gcd
from pathlib import Path
from hashlib import sha256
import json
import sys

HERE=Path(__file__).resolve().parent
MC032=HERE.parent / 'MC-032'
sys.path.insert(0,str(MC032))
import event_engine as ee
q=ee.q

V32_ROUTE='EXACT_ALGEBRAIC_CRITICAL_VALUE_RATIONAL_SEPARATOR_FOUNDATION'
ALPHA_MINPOLY=[Fraction(-1),Fraction(2),Fraction(1)]  # x^2+2x-1

class ExactAlgebraRefusal(RuntimeError): pass

def _trim(p): return ee._trim([q(x) for x in p])
def _degree(p): return ee.degree(p)
def _add(a,b):
    a=_trim(a);b=_trim(b);n=max(len(a),len(b));out=[Fraction(0)]*n
    for i in range(n):out[i]=(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)
    return _trim(out)
def _sub(a,b): return _add(a,[-x for x in b])
def _scale(a,c): c=q(c);return _trim([c*x for x in _trim(a)])
def _mul(a,b):
    a=_trim(a);b=_trim(b)
    if a==[0] or b==[0]:return [Fraction(0)]
    out=[Fraction(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return _trim(out)
def _exact_div(a,b):
    quo,rem=ee.pdivmod(a,b)
    if rem!=[0]:raise ArithmeticError('non-exact polynomial division')
    return _trim(quo)

def _lcm(a,b): return abs(a*b)//gcd(a,b) if a and b else 0

def _primitive_integer_poly(poly):
    p=_trim(poly)
    den=1
    for c in p:den=_lcm(den,c.denominator)
    nums=[int(c*den) for c in p]
    g=0
    for n in nums:g=gcd(g,abs(n))
    if g>1:nums=[n//g for n in nums]
    if nums and nums[-1]<0:nums=[-n for n in nums]
    return nums

def _root_separation_lower(poly):
    """Conservative rational corollary of the Mignotte root-separation bound."""
    p=ee.square_free(_trim(poly));n=_degree(p)
    if n<=1:return Fraction(1)
    ints=_primitive_integer_poly(p);height=max(1,max(abs(v) for v in ints))
    return Fraction(1,(n+1)**(n+1)*height**n)

def _root_bound(poly):
    ints=_primitive_integer_poly(poly);n=len(ints)-1
    if n<=0:return Fraction(0)
    lead=abs(ints[-1]);other=max([abs(x) for x in ints[:-1]] or [0])
    return Fraction(1)+Fraction(other,lead)

def _ceil_fraction(x): return x.numerator//x.denominator + (1 if x.numerator%x.denominator else 0)

def _depth_for_width(width,target):
    width=q(width);target=q(target)
    if target<=0:raise ValueError
    depth=0;w=width
    while w>=target:
        w/=2;depth+=1
    return depth+2

def _isolate_open_roots(poly,a,b):
    p=ee.square_free(_trim(poly));a=q(a);b=q(b)
    if _degree(p)<=0:return []
    total=ee.distinct_roots_open(p,a,b)
    if total==0:return []
    sep=_root_separation_lower(p);max_depth=_depth_for_width(b-a,sep/2)
    out=[]
    def rec(lo,hi,count,depth):
        if count<=0:return
        if depth>max_depth:
            raise ExactAlgebraRefusal('derived Mignotte isolation depth exhausted')
        mid=(lo+hi)/2
        if ee.peval(p,mid)==0:
            out.append({'kind':'point','value':mid})
            lc=ee.distinct_roots_open(p,lo,mid);rc=ee.distinct_roots_open(p,mid,hi)
            rec(lo,mid,lc,depth+1);rec(mid,hi,rc,depth+1);return
        if count==1:
            out.append({'kind':'interval','lo':lo,'hi':hi});return
        lc=ee.distinct_roots_open(p,lo,mid);rc=ee.distinct_roots_open(p,mid,hi)
        if lc+rc!=count:raise ArithmeticError('Sturm split mismatch')
        rec(lo,mid,lc,depth+1);rec(mid,hi,rc,depth+1)
    rec(a,b,total,0)
    return sorted(out,key=lambda r:r['value'] if r['kind']=='point' else r['lo'])

def _root_contains(poly,rep):
    p=_trim(poly)
    if _degree(p)<=0:return False
    if rep['kind']=='point':return ee.peval(p,rep['value'])==0
    return ee.distinct_roots_open(p,rep['lo'],rep['hi'])>0

def _multiplicity(poly,rep):
    p=_trim(poly)
    if rep['kind']=='point':return ee.multiplicity_at(p,rep['value'])
    m=1;g=ee.pgcd(p,ee.deriv(p))
    while _degree(g)>0 and _root_contains(g,rep):
        m+=1;g=ee.pgcd(g,ee.deriv(g))
    return m

def _isolate_closed_roots(poly,a=Fraction(0),b=Fraction(1)):
    p=_trim(poly);a=q(a);b=q(b);out=[]
    if _degree(p)<=0:return out
    if ee.peval(p,a)==0:out.append({'kind':'point','value':a,'multiplicity':ee.multiplicity_at(p,a)})
    for rep in _isolate_open_roots(p,a,b):
        rep=dict(rep);rep['multiplicity']=_multiplicity(p,rep);out.append(rep)
    if ee.peval(p,b)==0:out.append({'kind':'point','value':b,'multiplicity':ee.multiplicity_at(p,b)})
    return sorted(out,key=lambda r:r['value'] if r['kind']=='point' else r['lo'])

def _refine_root(poly,rep,target_width):
    p=ee.square_free(_trim(poly));target=q(target_width)
    if rep['kind']=='point':return dict(rep)
    lo,hi=rep['lo'],rep['hi']
    max_depth=_depth_for_width(hi-lo,target)
    for _ in range(max_depth+1):
        if hi-lo<target:return {'kind':'interval','lo':lo,'hi':hi,'multiplicity':rep.get('multiplicity',1)}
        mid=(lo+hi)/2
        if ee.peval(p,mid)==0:return {'kind':'point','value':mid,'multiplicity':rep.get('multiplicity',1)}
        lc=ee.distinct_roots_open(p,lo,mid)
        if lc==1:hi=mid
        else:
            rc=ee.distinct_roots_open(p,mid,hi)
            if rc!=1:raise ArithmeticError('lost isolated root during refinement')
            lo=mid
    raise ExactAlgebraRefusal('derived root refinement depth exhausted')

def _sign_at_algebraic_root(base_poly,rep,test_poly):
    base=ee.square_free(_trim(base_poly));test=_trim(test_poly)
    if test==[0]:return 0
    if rep['kind']=='point':return ee.sign(ee.peval(test,rep['value']))
    common=ee.pgcd(base,ee.square_free(test))
    if _degree(common)>0 and _root_contains(common,rep):return 0
    product=ee.square_free(_mul(base,ee.square_free(test)))
    sep=_root_separation_lower(product)
    lo,hi=rep['lo'],rep['hi']
    max_depth=_depth_for_width(hi-lo,sep/4)
    for _ in range(max_depth+1):
        # Once the test polynomial has no root in the isolating interval its sign
        # at the unique base root is exactly the sign at any rational sample.
        endpoint_zero = ee.peval(test,lo)==0 or ee.peval(test,hi)==0
        test_roots = ee.distinct_roots_open(test,lo,hi) if _degree(test)>0 else 0
        if not endpoint_zero and test_roots==0:
            value=ee.peval(test,(lo+hi)/2)
            if value==0:raise ArithmeticError('root-free sign interval has zero sample')
            return ee.sign(value)
        mid=(lo+hi)/2
        if ee.peval(base,mid)==0:return ee.sign(ee.peval(test,mid))
        if ee.distinct_roots_open(base,lo,mid)==1:hi=mid
        else:lo=mid
    raise ExactAlgebraRefusal('derived sign-at-algebraic-root depth exhausted')

def _compare_rational_alpha(value):
    x=q(value)
    if x<0:return -1
    f=x*x+2*x-1
    return 1 if f>0 else -1 if f<0 else 0

def _strict_positive(poly):
    p=_trim(poly)
    if p==[0] or ee.peval(p,0)<=0 or ee.peval(p,1)<=0:return False
    return ee.distinct_roots_open(p,0,1)==0

def _poly_of_poly_const(c): return [q(c)]
def _pp_trim(p):
    p=[_trim(c) for c in p]
    while len(p)>1 and p[-1]==[0]:p.pop()
    return p or [[Fraction(0)]]
def _pp_add(a,b):
    a=_pp_trim(a);b=_pp_trim(b);n=max(len(a),len(b));out=[]
    for i in range(n):out.append(_add(a[i] if i<len(a) else [0],b[i] if i<len(b) else [0]))
    return _pp_trim(out)
def _pp_sub(a,b):return _pp_add(a,[ _scale(c,-1) for c in b])
def _pp_mul(a,b):
    a=_pp_trim(a);b=_pp_trim(b)
    if a==[[0]] or b==[[0]]:return [[Fraction(0)]]
    out=[[Fraction(0)] for _ in range(len(a)+len(b)-1)]
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]=_add(out[i+j],_mul(x,y))
    return _pp_trim(out)
def _pp_div_exact(a,b):
    a=_pp_trim(a);b=_pp_trim(b)
    if b==[[0]]:raise ZeroDivisionError
    if len(a)<len(b):return [[Fraction(0)]]
    out=[[Fraction(0)] for _ in range(len(a)-len(b)+1)];r=[c[:] for c in a]
    while r!=[[0]] and len(r)>=len(b):
        k=len(r)-len(b)
        # exact division of leading z-polynomials
        lc=_exact_div(r[-1],b[-1])
        out[k]=_add(out[k],lc)
        for i,bc in enumerate(b):r[i+k]=_sub(r[i+k],_mul(lc,bc))
        r=_pp_trim(r)
    if r!=[[0]]:raise ArithmeticError('non-exact Bareiss polynomial division')
    return _pp_trim(out)

def _bareiss_det(matrix):
    n=len(matrix)
    if n==0:return [Fraction(1)]
    a=[[ _trim(cell) for cell in row] for row in matrix]
    sign=1;prev=[Fraction(1)]
    for k in range(n-1):
        pivot=k
        while pivot<n and a[pivot][k]==[0]:pivot+=1
        if pivot==n:return [Fraction(0)]
        if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign*=-1
        pk=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=_sub(_mul(a[i][j],pk),_mul(a[i][k],a[k][j]))
                a[i][j]=num if k==0 else _exact_div(num,prev)
            a[i][k]=[Fraction(0)]
        prev=pk
    det=a[-1][-1]
    return _scale(det,sign)

def _resultant_s(f_s,g_s_z):
    f=_trim(f_s);g=_pp_trim(g_s_z);m=_degree(f);n=len(g)-1
    if m<0 or n<0:return [Fraction(0)]
    if m==0:return _scale([Fraction(1)],f[0]**n)
    if n==0:
        # g coefficient is polynomial in z; resultant = g^m
        out=[Fraction(1)]
        for _ in range(m):out=_mul(out,g[0])
        return out
    fdesc=[_poly_of_poly_const(c) for c in reversed(f)];gdesc=list(reversed(g));size=m+n;mat=[]
    for r in range(n):
        row=[[Fraction(0)] for _ in range(size)]
        for j,c in enumerate(fdesc):row[r+j]=c
        mat.append(row)
    for r in range(m):
        row=[[Fraction(0)] for _ in range(size)]
        for j,c in enumerate(gdesc):row[r+j]=c
        mat.append(row)
    return _bareiss_det(mat)

def _critical_value_polynomial(a,t,h):
    factors=[]
    if _degree(h)>0:
        a2=_mul(a,a);t2=_mul(t,t);deg=max(len(a2),len(t2));g=[]
        for i in range(deg):
            ac=a2[i] if i<len(a2) else 0;tc=t2[i] if i<len(t2) else 0
            g.append([ac,-tc]) # coefficient in s is ac - z*tc
        rz=_resultant_s(ee.square_free(h),g)
        if rz!=[0]:factors.append(rz)
    for endpoint in (Fraction(0),Fraction(1)):
        tv=ee.peval(t,endpoint)
        if tv!=0:
            av=ee.peval(a,endpoint);factors.append([av*av,-tv*tv])
    qz=[Fraction(1)]
    for f in factors:qz=_mul(qz,f)
    vy=[Fraction(0)]*(2*(len(qz)-1)+1)
    for i,c in enumerate(qz):vy[2*i]=c
    return _trim(vy)

def _minpoly_divides(poly,minpoly=ALPHA_MINPOLY):
    _,rem=ee.pdivmod(_trim(poly),_trim(minpoly));return rem==[0]

def _relation_root_to_alpha(poly,rep,*,return_refined=False):
    p=ee.square_free(_trim(poly))
    if _minpoly_divides(p) and _root_contains(ALPHA_MINPOLY,rep):
        return (0,rep) if return_refined else 0
    if rep['kind']=='point':
        rel=_compare_rational_alpha(rep['value']);return (rel,rep) if return_refined else rel
    combined=ee.square_free(_mul(p,ALPHA_MINPOLY));sep=_root_separation_lower(combined)
    lo,hi=rep['lo'],rep['hi'];max_depth=_depth_for_width(hi-lo,sep/4)
    for _ in range(max_depth+1):
        if _compare_rational_alpha(lo)>0:
            rr={'kind':'interval','lo':lo,'hi':hi,'multiplicity':rep.get('multiplicity',1)}
            return (1,rr) if return_refined else 1
        if _compare_rational_alpha(hi)<0:
            rr={'kind':'interval','lo':lo,'hi':hi,'multiplicity':rep.get('multiplicity',1)}
            return (-1,rr) if return_refined else -1
        mid=(lo+hi)/2
        if ee.peval(p,mid)==0:
            rr={'kind':'point','value':mid,'multiplicity':rep.get('multiplicity',1)}
            rel=_compare_rational_alpha(mid);return (rel,rr) if return_refined else rel
        if ee.distinct_roots_open(p,lo,mid)==1:hi=mid
        else:lo=mid
    raise ExactAlgebraRefusal('derived algebraic root-ordering depth exhausted')

def _closed_form_separator_below(beta):
    beta=q(beta)
    if _compare_rational_alpha(beta)<=0:raise ValueError('beta must exceed sqrt(2)-1')
    f=beta*beta+2*beta-1
    m=beta-f/(4*(beta+1))
    if not (_compare_rational_alpha(m)>0 and m<beta):raise ArithmeticError('separator construction failed')
    return m

def _serial_rep(rep):
    if rep['kind']=='point':return {'kind':'POINT','value':str(rep['value']),'multiplicity':rep.get('multiplicity',1),'independently_checkable':True}
    return {'kind':'RATIONAL_ISOLATING_INTERVAL','lo':str(rep['lo']),'hi':str(rep['hi']),'multiplicity':rep.get('multiplicity',1),'sturm_distinct_root_count':1,'independently_checkable':True}



__all__ = [name for name in globals() if not name.startswith('__')]
