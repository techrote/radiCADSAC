"""A1-F4 research: bounded exact polynomial-carrier partition of signed Fourier pieces.

Requires sibling signed_cell.py from PR #470 for exact Machin/Taylor cofactor bounds.
No physical-source authorization, MC-1 or general exponential-polynomial decision.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
from signed_cell import cofactor_closed_sign, Refusal as SignRefusal

KEYS = ('H0', 'C1', 'S1', 'C2', 'S2')

class Refusal(ValueError):
    """Unsupported or unresolved, never a proof of a zero-free interval."""

def need(condition, why):
    if not condition:
        raise Refusal(why)

def token(v):
    need(type(v) is str and 0 < len(v) <= 120, 'RATIONAL_TOKEN')
    try: q = Q(v)
    except (ValueError, ZeroDivisionError) as exc: raise Refusal('RATIONAL_TOKEN') from exc
    need(v == f'{q.numerator}/{q.denominator}', 'NONCANONICAL_RATIONAL')
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 128, 'RATIONAL_BITS')
    return q

def fmt(v): return f'{v.numerator}/{v.denominator}'

def trim(p):
    p=list(p)
    while p and not p[-1]: p.pop()
    return tuple(p)

def evalp(p,x):
    acc=Q(0)
    for a in reversed(p): acc=acc*x+a
    return acc

def deriv(p): return trim(tuple(i*p[i] for i in range(1,len(p))))

def divide(p,q):
    p,q=trim(p),trim(q)
    need(bool(q), 'DIVIDE_ZERO')
    rem=list(p); out=[Q(0)]*max(0,len(p)-len(q)+1)
    while len(rem)>=len(q):
        k=len(rem)-len(q); c=rem[-1]/q[-1];out[k]=c
        for j,v in enumerate(q):rem[k+j]-=c*v
        rem=list(trim(rem))
    return trim(out),trim(rem)

def monic(p):
    p=trim(p)
    return tuple(a/p[-1] for a in p) if p else ()

def gcd(p,q):
    p,q=trim(p),trim(q)
    while q: _,r=divide(p,q);p,q=q,r
    return monic(p)

def carrier(channels):
    g=()
    for p in channels:
        if p:g=gcd(g,p)
    return g

def squarefree(p):
    if len(p)<=1: return (Q(1),)
    q,r=divide(p,gcd(p,deriv(p)));need(not r,'SQUAREFREE_EXACT')
    return monic(q)

def sequence(p):
    p=trim(p)
    if len(p)<=1:return (p,)
    s=[p,deriv(p)]
    while s[-1]:
        _,rem=divide(s[-2],s[-1])
        if not rem:break
        s.append(tuple(-x for x in rem))
    return tuple(s)

def variation(seq,x):
    signs=[1 if v>0 else -1 for p in seq if (v:=evalp(p,x))!=0]
    return sum(x!=y for x,y in zip(signs,signs[1:]))

def roots_between(seq,p,l,h):
    need(l<h and evalp(p,l)!=0 and evalp(p,h)!=0,'STURM_ENDPOINT')
    k=variation(seq,l)-variation(seq,h)
    need(k>=0,'NEGATIVE_STURM')
    return k

def clean_split(p,l,h):
    # Deterministic finite escape from rational roots at subdivision points.
    for j in range(2,len(p)+4):
        c=l+(h-l)/j
        if evalp(p,c):return c
    raise Refusal('RATIONAL_SPLIT_BUDGET')

def isolate(p,l,h,bits,limit=8192):
    """Disjoint open rational brackets for all DISTINCT interior roots."""
    if len(p)<=1:return []
    sf=squarefree(p); seq=sequence(sf)
    need(evalp(sf,l)!=0 and evalp(sf,h)!=0,'ISOLATE_ENDPOINT')
    output=[]; pending=[(l,h,roots_between(seq,sf,l,h))]; nodes=0
    while pending:
        a,b,n=pending.pop();nodes+=1
        need(nodes<=limit,'STURM_NODES_BUDGET')
        if n==0:continue
        if n==1 and b-a<=Q(1,2**bits):output.append((a,b));continue
        c=clean_split(sf,a,b)
        left=roots_between(seq,sf,a,c);right=roots_between(seq,sf,c,b)
        need(left+right==n,'STURM_CONSERVATION')
        pending.extend(((c,b,right),(a,c,left)))
    return sorted(output)

def endpoint_order(p,x):
    order=0
    while p and not evalp(p,x):
        p=deriv(p);order+=1
    return order

def interior_order(p,l,h):
    k=0
    while len(p)>1:
        sf=squarefree(p); seq=sequence(sf)
        if roots_between(seq,sf,l,h)==0:break
        k+=1
        p=gcd(p,deriv(p))
    need(k>=1,'MISSING_CARRIER_ROOT')
    return k

def source(doc):
    need(type(doc) is dict and set(doc)=={'a','b','pieces'},'SOURCE_FIELDS')
    a,b=token(doc['a']),token(doc['b'])
    need(b!=0,'ZERO_PHASE_RATE')
    data=doc['pieces'];need(type(data) is list and 1<=len(data)<=3,'PIECE_COUNT')
    output=[]
    for row in data:
        need(type(row) is dict and set(row)=={'lo','hi',*KEYS},'PIECE_FIELDS')
        lo,hi=token(row['lo']),token(row['hi'])
        need(-16<=lo<hi<=16,'PIECE_DOMAIN')
        coeff=[]
        for name in KEYS:
            v=row[name];need(type(v) is list and 1<=len(v)<=11,'POLYNOMIAL_DEGREE')
            p=tuple(token(x) for x in v)
            need(len(p)==1 or p[-1]!=0,'POLYNOMIAL_TRAILING_ZERO')
            coeff.append(trim(p))
        output.append((lo,hi,tuple(coeff)))
    for before,after in zip(output,output[1:]):
        need(before[1]==after[0],'PIECE_GAP')
        # Rational coefficient continuity implies physical C0, but is not
        # a verified origin of genuine B-spline knot/control vectors.
        need(all(evalp(x,before[1])==evalp(y,after[0]) for x,y in zip(before[2],after[2])),
             'C0_CHANNEL_SEAM')
    digest=sha256(json.dumps(doc,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
    return a,b,output,digest

def sign_cover(cofactor,a,b,l,h,terms,max_depth):
    leaves=[]
    def visit(x,y,depth):
        try:
            w=cofactor_closed_sign(cofactor,a,b,x,y,terms)
        except SignRefusal as exc:
            if str(exc)!='COFACTOR_SIGN_UNKNOWN':raise Refusal(f'SIGN_KERNEL_{exc}') from exc
            need(depth<max_depth,'COFACTOR_SIGN_BUDGET')
            m=(x+y)/2;visit(x,m,depth+1);visit(m,y,depth+1);return
        leaves.append((x,y,w['cofactor_sign']))
    visit(l,h,0)
    need(leaves and all(v[2]==leaves[0][2] for v in leaves),'COFACTOR_SIGN_INCONSISTENT')
    need(leaves[0][0]==l and leaves[-1][1]==h and all(u[1]==v[0] for u,v in zip(leaves,leaves[1:])),
         'COVERAGE_GAP')
    return leaves

def analyze_piece(a,b,l,h,channels,bits,terms,max_depth):
    if not any(channels):
        return {'interval':[fmt(l),fmt(h)],'kind':'IDENTITY_ZERO_CONTINUUM',
                'events':[],'cofactor_sign':None,'cover':[],'cells':[],'sided':{}}
    p=carrier(channels)
    need(bool(p),'CARRIER_IDENTITY')
    qs=[]
    for c in channels:
        q,r=divide(c,p);need(not r,'CARRIER_DIVISION')
        qs.append(q)
    qchannels=tuple(qs)
    cover=sign_cover(qchannels,a,b,l,h,terms,max_depth)
    sign=cover[0][2]
    # Remove endpoint linear factors from the polynomial used for interior isolation.
    interior=p; end_orders={}
    for x,key in ((l,'left'),(h,'right')):
        k=0
        while len(interior)>1 and evalp(interior,x)==0:
            interior,r=divide(interior,(-x,Q(1)));need(not r,'ENDPOINT_DIVISION');k+=1
        end_orders[key]=k
    brackets=isolate(interior,l,h,bits)
    events=[]
    for x,y in brackets:
        order=interior_order(interior,x,y)
        ls=sign*(1 if evalp(p,x)>0 else -1)
        rs=sign*(1 if evalp(p,y)>0 else -1)
        need((ls!=rs)==bool(order%2),'ROOT_PARITY')
        events.append({'locator':'ALGEBRAIC_STURM_BRACKET','bracket':[fmt(x),fmt(y)],
                       'multiplicity':order,'left_sign':ls,'right_sign':rs,
                       'kind':'CROSS' if order%2 else 'TOUCH'})
    sided={}
    for x,key in ((l,'left'),(h,'right')):
        k=end_orders[key]
        if k:
            derivp=p
            for _ in range(k):derivp=deriv(derivp)
            coeff=evalp(derivp,x)
            need(bool(coeff),'ENDPOINT_ORDER')
            right_sign=sign*(1 if coeff>0 else -1)
            sided[key]={'coordinate':fmt(x),'multiplicity':k,
                        'left_germ_sign':right_sign*((-1)**k),
                        'right_germ_sign':right_sign,
                        'physical_side':'RIGHT' if key=='left' else 'LEFT',
                        'kind':'CROSS' if k%2 else 'TOUCH'}
    # A strict sign on every polynomial zero-free open cell follows from the
    # Sturm atlas and any rational point inside it. Record such a witness.
    gaps=[]; bounds=[(l,l)]+brackets+[(h,h)]
    for (_,leftend),(rightstart,_) in zip(bounds,bounds[1:]):
        if leftend>rightstart:raise Refusal('NEGATIVE_GAP')
        if leftend==rightstart: continue
        mid=(leftend+rightstart)/2; v=evalp(p,mid)
        need(v!=0,'UNCERTIFIED_CELL_SAMPLE')
        gaps.append({'between':[fmt(leftend),fmt(rightstart)],
                     'sample':fmt(mid),'sign':sign*(1 if v>0 else -1)})
    return {'interval':[fmt(l),fmt(h)],'kind':'FINITE_POLYNOMIAL_CARRIER',
            'carrier':[fmt(v) for v in p], 'cofactor_sign':sign,
            'cover':[[fmt(x),fmt(y),s] for x,y,s in cover],
            'events':events,'sided':sided,'cells':gaps}

def certify(doc,*,bits=20,terms=16,max_depth=8):
    need(type(bits) is int and 2<=bits<=64,'ISOLATION_PRECISION')
    need(type(terms) is int and 4<=terms<=32,'TRIG_PRECISION')
    need(type(max_depth) is int and 0<=max_depth<=12,'COVER_BUDGET')
    a,b,pieces,digest=source(doc)
    result=[analyze_piece(a,b,l,h,cs,bits,terms,max_depth) for l,h,cs in pieces]
    # Exact maximal positive-length zero components: contiguous identity-zero
    # source pieces coalesce; a finite polynomial-carrier piece never does.
    zero_continua=[]
    for piece in result:
        if piece['kind']!='IDENTITY_ZERO_CONTINUUM':continue
        lo,hi=piece['interval']
        if zero_continua and zero_continua[-1][1]==lo:
            zero_continua[-1][1]=hi
        else:
            zero_continua.append([lo,hi])
    knots=[]
    for j in range(len(result)-1):
        left,right=result[j],result[j+1]
        lc=left['kind']=='IDENTITY_ZERO_CONTINUUM'
        rc=right['kind']=='IDENTITY_ZERO_CONTINUUM'
        lg=left['sided'].get('right')
        rg=right['sided'].get('left')
        lzero=lc or lg is not None
        rzero=rc or rg is not None
        need(lzero==rzero,'INCONSISTENT_KNOT_ZERO')
        at=left['interval'][1]
        if lzero:
            # A zero knot need not be an isolated zero.  Preserve the
            # component topology in a *typed* kind, not only optional flags.
            kind=('ZERO_CONTINUUM_INTERIOR' if lc and rc else
                  'ZERO_CONTINUUM_BOUNDARY' if lc or rc else
                  'ISOLATED_PHYSICAL_KNOT_ZERO')
            knots.append({'coordinate':at,'kind':kind,
                          'left_continuum':lc,'right_continuum':rc,
                          'left_order':None if lc else lg['multiplicity'],
                          'right_order':None if rc else rg['multiplicity'],
                          'left_sign':None if lc else lg['left_germ_sign'],
                          'right_sign':None if rc else rg['right_germ_sign']})
        else:
            x=Q(at)
            lp=tuple(Q(q) for q in left['carrier'])
            rp=tuple(Q(q) for q in right['carrier'])
            ls=left['cofactor_sign']*(1 if evalp(lp,x)>0 else -1)
            rs=right['cofactor_sign']*(1 if evalp(rp,x)>0 else -1)
            need(ls==rs,'INCONSISTENT_KNOT_SIGN')
            knots.append({'coordinate':at,'kind':'STRICT_NONZERO_KNOT','sign':ls})
    return {'schema':'a1-carrier-partition/2','source_sha256':digest,
            'zero_continua':zero_continua,
            'phase_units':'pi','physical_source_authentication':'UNVERIFIED',
            'bounds':{'bits':bits,'terms':terms,'max_depth':max_depth},
            'pieces':result,'knots':knots}

def verify(doc,receipt):
    try:
        return type(receipt) is dict and certify(doc,**receipt['bounds'])==receipt
    except (Refusal,SignRefusal,TypeError,ValueError,KeyError,ZeroDivisionError,OverflowError):
        return False
