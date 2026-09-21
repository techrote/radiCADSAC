#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import product

Q = Fraction

def q(v):
    if isinstance(v, bool) or isinstance(v, float):
        raise TypeError('certifying scalars must not be bool/binary float')
    return v if isinstance(v, Fraction) else Fraction(v)

def v3(values):
    values=tuple(q(x) for x in values)
    if len(values)!=3: raise ValueError('expected 3-vector')
    return values

def det3(m):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
            -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
            +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

def matvec(m,p):
    return tuple(sum(q(m[i][j])*q(p[j]) for j in range(3)) for i in range(3))

def matmul(a,b):
    return tuple(tuple(sum(q(a[i][k])*q(b[k][j]) for k in range(3)) for j in range(3)) for i in range(3))

def transpose(m): return tuple(tuple(m[j][i] for j in range(3)) for i in range(3))

@dataclass(frozen=True)
class RigidTransform:
    """Exact bounded-control transform: p_parent = R p_child + t."""
    r: tuple[tuple[Fraction,...],...]
    t: tuple[Fraction,...]
    def __post_init__(self):
        r=tuple(tuple(q(x) for x in row) for row in self.r); t=v3(self.t)
        if len(r)!=3 or any(len(row)!=3 for row in r): raise ValueError('3x3 rotation required')
        if any(x not in (Fraction(-1),Fraction(0),Fraction(1)) for row in r for x in row):
            raise ValueError('control rotation must be exact signed permutation')
        if matmul(transpose(r),r) != ((Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0)),(Q(0),Q(0),Q(1))):
            raise ValueError('rotation must be orthogonal')
        if det3(r)!=1: raise ValueError('right-handed proper rotation required')
        object.__setattr__(self,'r',r); object.__setattr__(self,'t',t)
    @classmethod
    def identity(cls): return cls(((1,0,0),(0,1,0),(0,0,1)),(0,0,0))
    def apply(self,p):
        rp=matvec(self.r,v3(p)); return tuple(rp[i]+self.t[i] for i in range(3))
    def inverse(self):
        ri=transpose(self.r); nt=tuple(-x for x in matvec(ri,self.t)); return RigidTransform(ri,nt)
    def compose(self, child):
        """self(parent<-mid) o child(mid<-child) -> parent<-child."""
        r=matmul(self.r,child.r); rt=matvec(self.r,child.t)
        return RigidTransform(r,tuple(rt[i]+self.t[i] for i in range(3)))

@dataclass(frozen=True)
class Box:
    lo: tuple[Fraction,...]
    hi: tuple[Fraction,...]
    def __post_init__(self):
        lo=v3(self.lo); hi=v3(self.hi)
        if any(lo[i]>hi[i] for i in range(3)): raise ValueError('invalid box')
        object.__setattr__(self,'lo',lo); object.__setattr__(self,'hi',hi)
    def contains_closed(self,p):
        p=v3(p); return all(self.lo[i] <= p[i] <= self.hi[i] for i in range(3))
    def transform(self,T:RigidTransform):
        corners=[T.apply(c) for c in product(*[(self.lo[i],self.hi[i]) for i in range(3)])]
        return Box(tuple(min(c[i] for c in corners) for i in range(3)),tuple(max(c[i] for c in corners) for i in range(3)))

@dataclass(frozen=True)
class Body:
    body_id: str
    lineage_id: str
    stock: tuple[Box,...]
    removed: tuple[Box,...]=()
    def material_at(self,p):
        return any(b.contains_closed(p) for b in self.stock) and not any(b.contains_closed(p) for b in self.removed)

@dataclass(frozen=True)
class Setup:
    setup_id: str
    machine: str
    common_from_local: RigidTransform
    inherited_error: Fraction=Q(0)
    def __post_init__(self): object.__setattr__(self,'inherited_error',q(self.inherited_error))

@dataclass(frozen=True)
class Workpiece:
    revision: str
    bodies: tuple[Body,...]
    setup: Setup
    journal: tuple[str,...]=()
    def body(self,body_id):
        hits=[b for b in self.bodies if b.body_id==body_id]
        if len(hits)!=1: raise ValueError('durable target body must resolve exactly once')
        return hits[0]

@dataclass(frozen=True)
class Cut:
    operation_id: str
    input_revision: str
    target_body_id: str
    provider: str
    local_sweep: tuple[Box,...]


def _child_revision(state:Workpiece, op_id:str): return state.revision + '>' + op_id

def apply_cut(state:Workpiece, cut:Cut)->Workpiece:
    if cut.input_revision != state.revision: raise ValueError('stale or wrong input revision')
    target=state.body(cut.target_body_id)
    common=tuple(b.transform(state.setup.common_from_local) for b in cut.local_sweep)
    new_target=replace(target, removed=target.removed + common)
    new_bodies=tuple(new_target if b.body_id==target.body_id else b for b in state.bodies)
    return Workpiece(_child_revision(state,cut.operation_id),new_bodies,state.setup,state.journal+(cut.operation_id,))

def reclamp(state:Workpiece, operation_id:str, new_setup:Setup)->Workpiece:
    """Non-cutting immutable setup transition. It never rewrites prior setup/material records."""
    return Workpiece(_child_revision(state,operation_id),state.bodies,new_setup,state.journal+(operation_id,))

def actual_sweep_error_bound(e_inherited,e_translation,rho,e_rotation,e_tool):
    vals=[q(x) for x in (e_inherited,e_translation,rho,e_rotation,e_tool)]
    if any(x<0 for x in vals): raise ValueError('error bounds must be nonnegative')
    ei,et,r,er,eto=vals
    return ei+et+r*er+eto
