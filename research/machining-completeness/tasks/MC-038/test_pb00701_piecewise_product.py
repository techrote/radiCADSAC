#!/usr/bin/env python3
"""Original B-spline source controls; no pre-lowered truth input or mock oracle."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import copy
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_piecewise_product_model as m

a, E = m.a, m.E


def power(p, n):
    result = [Q(1)]
    for _ in range(n):
        result = a.pmul(result, p)
    return result


def bernstein(p, degree):
    p = a.trim(p)
    assert len(p)-1 <= degree
    return [str(sum((p[k]*Q(comb(j,k),comb(degree,k))
                     for k in range(min(j,len(p)-1)+1)), Q(0))) for j in range(degree+1)]


def encode(pieces, bounds=None, offset='0', rate='1/4', ident='v52-original-source'):
    """Exact test source encoder: independent Bernstein identities are checked below."""
    bounds = list(map(Q, range(len(pieces)+1) if bounds is None else bounds))
    assert len(bounds) == len(pieces)+1 and all(x<y for x,y in zip(bounds,bounds[1:]))
    spec = {'grammar': m.GRAMMAR, 'source_parameter_id': ident,
            'parameter_lo': str(bounds[0]), 'parameter_hi': str(bounds[-1]),
            'phase_turn_offset': str(Q(offset)), 'phase_turn_rate': str(Q(rate))}
    for axis, key in enumerate(('cos_splines','sin_splines')):
        harmonics = sorted(set().union(*(set(piece[axis]) for piece in pieces)))
        mapping = {}
        for h in harmonics:
            polynomials = [a.trim(piece[axis].get(h,[0])) for piece in pieces]
            degree = max(len(p)-1 for p in polynomials)
            mapping[str(h)] = {'degree':degree,
                              'knots':[str(x) for x in bounds for _ in range(degree+1)],
                              'controls':[c for p in polynomials for c in bernstein(p,degree)]}
        spec[key] = mapping
    return spec


def physical_piece(factor, scale=1):
    carrier = ({0:[-Q(1,2),1],1:[Q(1,100)]},{2:[Q(1,200)]})
    return tuple({h:a.pscale(a.pmul(factor,p),scale) for h,p in mapping.items()} for mapping in carrier)


def fixture(kind='cross', irrational=True, exterior=False):
    common = power([-1,0,2],2) if irrational else [Q(1)]
    if kind in ('cross','touch'):
        left = a.pmul(power([-1,1],2),common)
        right = a.pmul(power([0,1],3),common)
        if exterior:
            left = a.pmul(left,power([0,1],2))
            right = a.pmul(right,power([-1,1],3))
        pieces = [physical_piece(left),physical_piece(right,-1 if kind=='touch' else 1)]
    else:
        assert kind == 'nonzero'
        pieces = [physical_piece(common),physical_piece(common,-1)]
    return encode(pieces)


def reverse_source(spec):
    result = copy.deepcopy(spec)
    lo,hi = Q(spec['parameter_lo']),Q(spec['parameter_hi'])
    for key in ('cos_splines','sin_splines'):
        for spline in result[key].values():
            spline['knots'] = [str(lo+hi-Q(k)) for k in reversed(spline['knots'])]
            spline['controls'].reverse()
    result['phase_turn_offset'] = str(Q(spec['phase_turn_offset'])+Q(spec['phase_turn_rate'])*(lo+hi))
    result['phase_turn_rate'] = str(-Q(spec['phase_turn_rate']))
    return result


def affine_source(spec, shift=2, scale=3):
    assert scale>0
    result = copy.deepcopy(spec)
    for key in ('cos_splines','sin_splines'):
        for spline in result[key].values():
            spline['knots'] = [str(Q(shift)+Q(scale)*Q(k)) for k in spline['knots']]
    result['parameter_lo'] = str(Q(shift)+Q(scale)*Q(spec['parameter_lo']))
    result['parameter_hi'] = str(Q(shift)+Q(scale)*Q(spec['parameter_hi']))
    rate = Q(spec['phase_turn_rate'])/scale
    result['phase_turn_offset'] = str(Q(spec['phase_turn_offset'])-rate*shift)
    result['phase_turn_rate'] = str(rate)
    return result


def mutate(value, path, replacement):
    result = copy.deepcopy(value); cursor = result
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement
    return result


class SourceLoweringTests(unittest.TestCase):
    def test_bernstein_coefficients_and_exact_polynomial_roundtrip(self):
        # Direct Bernstein-to-power expansion, not the implementation lowerer.
        for p in ([3],[-2,3],[1,-2,3],[1,0,-5,0,1]):
            for degree in (len(p)-1,len(p)+2):
                controls=list(map(Q,bernstein(p,degree)))
                recovered=[Q(0)]*(degree+1)
                for j,c in enumerate(controls):
                    for k in range(degree-j+1):
                        recovered[j+k]+=c*comb(degree,j)*comb(degree-j,k)*(-1)**k
                self.assertEqual(a.trim(recovered),a.trim(p))
        pieces=[physical_piece(a.pmul(power([-1,1],2),power([-1,0,2],2))),
                physical_piece(a.pmul(power([0,1],3),power([-1,0,2],2)))]
        source=encode(pieces); lower=m.lower_source(source)
        self.assertEqual(lower['source_boundaries'],['0','1','2'])
        for row,expected in zip(lower['spans'],pieces):
            for axis,key in enumerate(('cos_polynomials','sin_polynomials')):
                self.assertEqual(row['material'][key],{str(h):list(map(str,p)) for h,p in expected[axis].items()})
        self.assertNotEqual(source['cos_splines']['0']['degree'],source['sin_splines']['2']['degree'])

    def test_different_channel_knot_sets_and_repeated_knots_exact_union(self):
        source=encode([({0:[0,1],1:[1]},{2:[1]}),({0:[1,1],1:[1]},{2:[1]})])
        source['cos_splines']['1']={'degree':0,'knots':['0','1/2','2'],'controls':['1','2']}
        source['sin_splines']['2']={'degree':0,'knots':['0','2'],'controls':['1']}
        lower=m.lower_source(source)
        self.assertEqual(lower['source_boundaries'],['0','1/2','1','2'])
        self.assertEqual([x['material']['cos_polynomials']['0'] for x in lower['spans']],
                         [['0','1/2'],['1/2','1/2'],['1','1']])
        self.assertEqual([x['material']['cos_polynomials']['1'] for x in lower['spans']],[['1'],['2'],['2']])
        self.assertTrue(all(Q(x['parent_map']['positive_scale'])>0 for x in lower['spans']))
        self.assertFalse(lower['source_knots_are_physical_roots_by_default'])

    def test_cropped_source_preserves_original_controls_and_exact_maps(self):
        source=encode([({0:[0,0,1]},{2:[1]}),({0:[1,2,1]},{2:[1]})])
        original=copy.deepcopy(source)
        source['parameter_lo']='1/4';source['parameter_hi']='7/4'
        lower=m.lower_source(source)
        self.assertEqual(lower['source_boundaries'],['1/4','1','7/4'])
        self.assertEqual([x['material']['cos_polynomials']['0'] for x in lower['spans']],
                         [['1/16','3/8','9/16'],['1','3/2','9/16']])
        self.assertEqual(lower['source_spec']['cos_splines'],original['cos_splines'])
        self.assertEqual([x['parent_map']['positive_scale'] for x in lower['spans']],['3/4','3/4'])

    def test_phase_global_map_identity_and_exact_limits(self):
        source=fixture(); transformed=affine_source(source)
        before,after=m.lower_source(source),m.lower_source(transformed)
        self.assertEqual(after['source_boundaries'],['2','5','8'])
        for old,new in zip(before['spans'],after['spans']):
            self.assertEqual(old['one_sided_amplitude_limits'],new['one_sided_amplitude_limits'])
            for t in (Q(0),Q(1,3),Q(1)):
                u=Q(old['parent_map']['offset'])+Q(old['parent_map']['positive_scale'])*t
                v=Q(new['parent_map']['offset'])+Q(new['parent_map']['positive_scale'])*t
                self.assertEqual(Q(source['phase_turn_offset'])+Q(source['phase_turn_rate'])*u,
                                 Q(transformed['phase_turn_offset'])+Q(transformed['phase_turn_rate'])*v)
        self.assertNotEqual(before['source_binding_sha256'],after['source_binding_sha256'])

    def test_float_boolean_unknown_field_bad_knots_and_projection_rejected(self):
        source=fixture()
        changes=[(['phase_turn_rate'],True),(['phase_turn_rate'],0.25),(['source_parameter_id'],''),
                 (['parameter_lo'],'2'),(['cos_splines','0','degree'],True),
                 (['cos_splines','1','controls',0],0.01),(['cos_splines','0','knots',0],'9')]
        for path,value in changes:
            with self.subTest(path=path),self.assertRaises((ValueError,TypeError)):
                m.lower_source(mutate(source,path,value))
        for key,value in (('certificate',{}),('epsilon','1/100'),('second_phase_law',{}),('parameter_projection','another')):
            bad=copy.deepcopy(source);bad[key]=value
            with self.assertRaises((ValueError,TypeError)):m.lower_source(bad)
        bad=copy.deepcopy(source);bad['sin_splines']['0']=bad['sin_splines']['2']
        with self.assertRaises(ValueError):m.lower_source(bad)

    def test_source_encoding_is_not_modified_by_lowering(self):
        source=fixture();saved=copy.deepcopy(source)
        lower=m.lower_source(source)
        self.assertEqual(source,saved)
        self.assertIs(lower['caller_lowering_trusted'],False)
        self.assertEqual([x['span_index'] for x in lower['spans']],[0,1])
        for span in lower['spans']:
            self.assertEqual(span['source_interval'],span['material']['parent_source_interval'])
            self.assertEqual(span['material']['source_parameter_id'],source['source_parameter_id'])


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceLoweringTests))
    if not result.wasSuccessful():
        raise AssertionError('v52 original-source lowering controls failed')


if __name__=='__main__':run()
