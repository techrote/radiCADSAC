#!/usr/bin/env python3
"""Finite source-derived nonconvex shell adversaries; python3 ... --self-test."""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
import subprocess
from pathlib import Path
import sys

TASK=Path(__file__).resolve().parent
ROOT=TASK.parents[3]  # repo root if file is in research/machining-completeness/tasks/MC-038
sys.path.insert(0,str(TASK))
import pb00703_parametric_patch as patch
import pb00703_trimmed_shell as v6
import pb00703_nonconvex_shell_20261109 as nc

MC020_REL='research/machining-completeness/tasks/MC-020/form-undercut-sweep-contract-v1.json'
MC020=ROOT/MC020_REL
MC020_SHA='6fca79b5d70329346e2c4ceab292c1be3fc3e528'


def git_blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()



def _strict_json(raw):
    """Reject duplicate keys/non-JSON constants; never silently reinterpret custody."""
    def unique_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result:
                raise ValueError('duplicate key in original MC-020 fixture: '+key)
            result[key]=value
        return result
    def illegal_constant(value):
        raise ValueError('non-JSON constant in source: '+value)
    return json.loads(raw,object_pairs_hook=unique_pairs,parse_constant=illegal_constant)


def verify_mc020_checkout(committed_bytes,worktree_bytes,head_object_id):
    """Verify three separate authorities: HEAD Git object, checkout, consumed JSON.

    The only permitted worktree difference is platform CRLF checkout conversion.
    Do not substitute a worktree SHA-1 for the immutable Git-object identity.
    """
    if head_object_id!=MC020_SHA or git_blob_sha(committed_bytes)!=MC020_SHA:
        raise ValueError('HEAD MC-020 source Git object differs from frozen authority')
    if worktree_bytes!=committed_bytes and worktree_bytes.replace(b'\r\n',b'\n')!=committed_bytes:
        raise ValueError('MC-020 worktree differs beyond permitted checkout CRLF conversion')
    committed_doc=_strict_json(committed_bytes)
    checkout_doc=_strict_json(worktree_bytes)
    if checkout_doc!=committed_doc:
        raise ValueError('MC-020 consumed original-source semantics changed')
    return checkout_doc


def authenticated_original_mc020():
    """Bind original geometry to the current checkout's immutable pinned Git blob."""
    try:
        head_id=subprocess.check_output(
            ['git','rev-parse','HEAD:'+MC020_REL],cwd=ROOT,stderr=subprocess.PIPE
        ).decode('ascii').strip()
        committed=subprocess.check_output(
            ['git','cat-file','blob','HEAD:'+MC020_REL],cwd=ROOT,stderr=subprocess.PIPE
        )
    except (OSError,subprocess.CalledProcessError) as exc:
        raise ValueError('cannot authenticate checked-out MC-020 Git source') from exc
    return verify_mc020_checkout(committed,MC020.read_bytes(),head_id)


def fmt(x):
    return patch.qtext(x)


def q3(p):
    return [fmt(t) for t in p]


def original_cutter():
    fixture=authenticated_original_mc020()['boundary_controls']['undercut_access']
    return [[Q(x) for x in fixture[name]] for name in ('cutting_head','cutting_neck')]


def original_member(cubes,p):
    return any(b[0]<p[0]<b[1] and b[2]<p[1]<b[3] and b[4]<p[2]<b[5] for b in cubes)


def shear(p):
    return (p[0]+p[2]/5,p[1],p[2])


def inverse(p):
    return (p[0]-p[2]/5,p[1],p[2])


def patch_for_triangle(face_id,tri,role='cutting'):
    a,b,c=tri
    d=tuple(b[i]+c[i]-a[i] for i in range(3))
    return {
        'schema':patch.SCHEMA,'source_id':'MC-020-82-undercut-tool',
        'patch_id':face_id,'role':role,'units':'mm','frame_id':'tool-local-v1',
        'u_parameter_id':face_id+'-u','v_parameter_id':face_id+'-v',
        'degree_u':1,'degree_v':1,
        'knots_u':['0','0','1','1'],'knots_v':['0','0','1','1'],
        'parameter_domain_u':['0','1'],'parameter_domain_v':['0','1'],
        'control_points':[[q3(a),q3(c)],[q3(b),q3(d)]],
        'weights':[['1','1'],['1','1']],
        'source_uncertainty':'0','authority_kind':'BOUNDARY_PATCH_ONLY',
    }


def cutter_shell():
    """Exact face construction from original MC-020 head/neck, not an inferred mesh.

    Partition the original box walls at all x/y/z source planes to remove
    T-junctions; omit faces internal to the union; shear exact source coordinates
    x' = x+z/5 to exercise non-axis-aligned nominal patch authority.
    """
    cubes=original_cutter()
    xcuts=sorted(set(c[i] for c in cubes for i in (0,1)))
    ycuts=sorted(set(c[i] for c in cubes for i in (2,3)))
    zcuts=sorted(set(c[i] for c in cubes for i in (4,5)))
    def in_cube(p):
        return original_member(cubes,p)
    # Exact adjacent-cell probes. These are derived from the finite source
    # coordinate grid, not a global geometric tolerance.
    dx=min(b-a for a,b in zip(xcuts,xcuts[1:]))/4
    dy=min(b-a for a,b in zip(ycuts,ycuts[1:]))/4
    dz=min(b-a for a,b in zip(zcuts,zcuts[1:]))/4
    faces=[]
    for ix,(xl,xh) in enumerate(zip(xcuts,xcuts[1:])):
        for iy,(yl,yh) in enumerate(zip(ycuts,ycuts[1:])):
            for iz,(zl,zh) in enumerate(zip(zcuts,zcuts[1:])):
                mid=((xl+xh)/2,(yl+yh)/2,(zl+zh)/2)
                if not in_cube(mid):
                    continue
                # Each quad cycles outward when viewed from outside.
                quads=[
                    ([(xl,yl,zl),(xl,yl,zh),(xl,yh,zh),(xl,yh,zl)],(xl-dx,mid[1],mid[2])),
                    ([(xh,yl,zl),(xh,yh,zl),(xh,yh,zh),(xh,yl,zh)],(xh+dx,mid[1],mid[2])),
                    ([(xl,yl,zl),(xh,yl,zl),(xh,yl,zh),(xl,yl,zh)],(mid[0],yl-dy,mid[2])),
                    ([(xl,yh,zl),(xl,yh,zh),(xh,yh,zh),(xh,yh,zl)],(mid[0],yh+dy,mid[2])),
                    ([(xl,yl,zl),(xl,yh,zl),(xh,yh,zl),(xh,yl,zl)],(mid[0],mid[1],zl-dz)),
                    ([(xl,yl,zh),(xh,yl,zh),(xh,yh,zh),(xl,yh,zh)],(mid[0],mid[1],zh+dz)),
                ]
                for side,(quad,neighbour) in enumerate(quads):
                    if in_cube(neighbour):
                        continue
                    for half,ids in enumerate(((0,1,2),(0,2,3))):
                        tri=tuple(shear(quad[i]) for i in ids)
                        fid=f'orig-{ix}-{iy}-{iz}-{side}-{half}'
                        desc=patch_for_triangle(fid,tri)
                        faces.append({'face_id':fid,'patch':desc,
                                      'patch_sha256':patch.source_sha256(desc),
                                      'trim_uv':[['0','0'],['1','0'],['0','1']]})
    return {
        'schema':nc.SCHEMA,'authority_kind':nc.KIND,
        'shell_id':'mc020-exact-nonconvex-sheared-head-neck','source_id':'MC-020-82-undercut-tool',
        'role':'cutting','units':'mm','frame_id':'tool-local-v1',
        'revision_id':'MC020-source-fixture-bound','configuration_id':'no-opaque-kernel',
        'faces':faces,
    }


def rejected(source):
    res=nc.classify_descriptor(source)
    assert res['status'] in ('SEMANTIC_BLOCKER','BLOCKED'),res
    assert res['blocker']=='PB-007-03'
    return res



def source_custody_adversaries():
    """Positive LF/CRLF checkout and negative Git-object/geometry mutation controls."""
    # This object is the committed source, not a normalized worktree approximation.
    committed=subprocess.check_output(
        ['git','cat-file','blob','HEAD:'+MC020_REL],cwd=ROOT
    )
    checked=MC020.read_bytes()
    original=verify_mc020_checkout(committed,checked,MC020_SHA)
    assert original['boundary_controls']['undercut_access']['cutting_head'][-1]=='3/4'
    assert verify_mc020_checkout(committed,committed,MC020_SHA)==original
    assert verify_mc020_checkout(committed,committed.replace(b'\n',b'\r\n'),MC020_SHA)==original

    def refuses(committed_arg,worktree_arg,head_id,reason):
        try:
            verify_mc020_checkout(committed_arg,worktree_arg,head_id)
        except (ValueError,UnicodeError):
            return
        raise AssertionError('original-source custody accepted '+reason)

    # One *physical* cutting-head coordinate changes (the bounded exact oracle).
    marker=b'"cutting_head":["-1","1","-1","1","0","3/4"]'
    assert committed.count(marker)==1, 'original MC-020 witness layout changed'
    changed=committed.replace(marker,marker.replace(b'"3/4"',b'"7/8"'),1)
    assert _strict_json(changed)['boundary_controls']['undercut_access']['cutting_head'][-1]=='7/8'
    refuses(committed,changed,MC020_SHA,'modified head geometry')
    refuses(committed,changed.replace(b'\n',b'\r\n'),MC020_SHA,'modified geometry plus CRLF')
    refuses(changed,changed,MC020_SHA,'forged canonical Git object')
    refuses(committed,committed,'0'*40,'forged HEAD source identity')
    refuses(committed,committed+b' ',MC020_SHA,'unrecorded worktree text edit')
    refuses(committed,committed.replace(b'\n',b'\r\r\n'),MC020_SHA,'unexpected checkout filter')
    # Exact original source semantics must not be parsed with duplicate-key override.
    duplicate=b'{"source":"A","source":"B"}'
    try:
        _strict_json(duplicate)
    except ValueError:
        pass
    else:
        raise AssertionError('duplicate JSON identity accepted')
    print('PB-007-03 MC-020 custody: pinned HEAD Git blob, LF/CRLF, and altered-source refusals PASS')


def run_controls():
    s=cutter_shell()
    cert=nc.certify_shell(s)
    assert cert['status']=='EXACT_NONCONVEX_PLANAR_PATCH_SHELL'
    assert cert['oriented_six_volume']!='0/1'
    assert cert['topology']['euler']==2
    assert nc.certify_shell(copy.deepcopy(s))==cert
    original=original_cutter()
    # Source-derived negative: former v6 convex half-space route cannot admit
    # this strictly reentrant shell even though all source faces are exact.
    older=copy.deepcopy(s)
    older['schema']=v6.SCHEMA
    older['authority_kind']=v6.AUTHORITY_KIND
    older['interior_witness']=[fmt(v) for v in shear((Q(0),Q(0),Q(1,2)))]
    assert v6.classify_shell_descriptor(older)['status']=='SEMANTIC_BLOCKER'
    def relation(p):
        return nc.classify_point(s,q3(p),cert)['relation']
    # MC-020's original reentrant void probe must stay outside (never hull-filled).
    for local,expect in [
        ((Q(0),Q(0),Q(1,2)),'INSIDE'),
        ((Q(0),Q(0),Q(2)),'INSIDE'),
        ((Q(3,4),Q(0),Q(3,2)),'OUTSIDE'),
        ((Q(2),Q(0),Q(1,2)),'OUTSIDE'),
        ((Q(1),Q(0),Q(1,2)),'BOUNDARY'),
        ((Q(1)-Q(1,1_000_000),Q(0),Q(1,2)),'INSIDE'),
        ((Q(1)+Q(1,1_000_000),Q(0),Q(1,2)),'OUTSIDE'),
        ((Q(0),Q(0),Q(0)),'BOUNDARY'),
        ((Q(0),Q(0),Q(-1,1_000_000)),'OUTSIDE'),
    ]:
        actual=relation(shear(local))
        assert actual==expect,(local,expect,actual)
    # Independent original-box oracle for strict nonboundary samples:
    for x in (Q(-3,2),Q(-9,10),Q(-1,5),Q(0),Q(1,5),Q(9,10),Q(3,2)):
        for z in (Q(1,5),Q(1),Q(2)):
            y=Q(1,10)
            original_point=(x,y,z)
            assert relation(shear(original_point))==('INSIDE' if original_member(original,original_point) else 'OUTSIDE')
    # Exact certificate binding and adversarial source authority.
    t=copy.deepcopy(s);t['faces'][0]['patch_sha256']='0'*64;rejected(t)
    t=copy.deepcopy(s);t['faces'].pop();rejected(t)
    t=copy.deepcopy(s);t['faces'][0]['trim_uv'][0]=[0.5,'0'];rejected(t)
    t=copy.deepcopy(s);t['faces'][0]['patch']['source_uncertainty']='1/1000000';rejected(t)
    t=copy.deepcopy(s);t['faces'][0]['patch']['role']='holder';t['faces'][0]['patch_sha256']=patch.source_sha256(t['faces'][0]['patch']);rejected(t)
    t=copy.deepcopy(s);t['role']='holder';rejected(t)
    t=copy.deepcopy(s);t['frame_id']='fixture-v2';rejected(t)
    t=copy.deepcopy(s);t['faces'][0]['trim_uv']=[['0','0'],['0','1'],['1','0']];rejected(t)
    t=copy.deepcopy(s);t['faces'].append(copy.deepcopy(t['faces'][0]));t['faces'][-1]['face_id']='duplicated';rejected(t)
    t=copy.deepcopy(s);t['importer_success']=True;rejected(t)
    t=copy.deepcopy(s);t['faces']*=3
    assert nc.classify_descriptor(t)['status']=='BLOCKED', 'budget must not call valid physical input invalid'
    t=copy.deepcopy(s);t['configuration_id']='changed'
    assert nc.classify_point(t,q3(shear((Q(0),Q(0),Q(1,2)))),cert)['status']=='BLOCKED'
    # Independent crossing witness: two nonincident overlapping faces forbidden.
    a=((Q(0),Q(0),Q(0)),(Q(2),Q(0),Q(0)),(Q(0),Q(2),Q(0)))
    b=((Q(1),Q(-1),Q(-1)),(Q(1),Q(1),Q(1)),(Q(1),Q(1),Q(-1)))
    assert nc._triangle_intersections(a,b)
    try:
        nc._check_nonintersections([a,b],10)
    except ValueError:
        pass
    else:
        raise AssertionError('crossing facets accepted')
    print('PB-007-03 NONCONVEX source-derived patch certification: PASS; faces=',len(s['faces']), 'original fixture sha=',MC020_SHA)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--contract',action='store_true')
    parser.add_argument('--self-test',action='store_true')
    a=parser.parse_args()
    if not a.contract and not a.self_test:
        parser.error('specify --contract or --self-test')
    assert MC020.exists(),MC020
    authenticated_original_mc020()
    source_custody_adversaries()
    if a.self_test:
        run_controls()
    else:
        s=cutter_shell()
        assert nc.certify_shell(s)['full_pb00703_closed'] is False
        print('PB-007-03 source/fixture contract: PASS')

if __name__=='__main__':
    main()
