#!/usr/bin/env python3
"""Independent exact original-source and receipt mutation tests for V27 pair."""
import copy, unittest
from fractions import Fraction as F
import pb00701_v27_sign_trit_boundary_20261105 as m

class V27Tests(unittest.TestCase):
 def test_01_authoritative_corpus_and_receipt(self):
  x=m.execute(); self.assertEqual(x['claim'],'C_BOUNDED_ORIGINAL_PAIR_ENDPOINT_SIGN_INFORMATION_LOSS')
  self.assertEqual(x['historical_case_ids_newly_closed'],[])
  self.assertEqual(x['before'],x['after'])
  self.assertEqual(set(x['pair']),{'tail0','tail100'})
 def test_02_canonical_source_hashes(self):
  for kind,(expected,_) in m.CASES.items():
   self.assertEqual(m.sha(m.expected_spec(kind)),expected)
 def test_03_identity_extraction(self):
  self.assertEqual(m.source_parts(m.expected_spec('tail0'),'tail0'),0)
  self.assertEqual(m.source_parts(m.expected_spec('tail100'),'tail100'),100)
 def test_04_cardinal_exact_signs(self):
  a=m.values(F(0));b=m.values(F(100))
  self.assertEqual([a[t][2] for t in ['0','1','2']],[1,-1,1])
  self.assertEqual([b[t][2] for t in ['0','1','2']],[1,-1,1])
  self.assertEqual(a['9/8'],('-101/100','0',-1))
  self.assertEqual(b['9/8'],('1149/100','0',1))
 def test_05_tangency_or_repeated_source_does_not_enter_grammar(self):
  for kind in m.CASES:
   s=m.expected_spec(kind)
   s['sin_splines']['1']['controls']=['0','0','0','0']
   with self.assertRaises(m.Refusal):m.source_parts(s,kind)
 def test_06_noncanonical_spline_or_phase_rejected(self):
  for kind in m.CASES:
   s=m.expected_spec(kind)
   for key,value in [('phase_turn_rate','0'),('source_parameter_id','u')]:
    t=copy.deepcopy(s);t[key]=value
    with self.assertRaises(m.Refusal):m.source_parts(t,kind)
   t=copy.deepcopy(s);t['cos_splines']['0']['controls'][0]='5/1'
   with self.assertRaises(m.Refusal):m.source_parts(t,kind)
 def test_07_invalid_cosine_channel_rejected(self):
  for kind in m.CASES:
   s=m.expected_spec(kind)
   s['cos_splines']['2']['controls'][1]='0'
   with self.assertRaises(m.Refusal):m.source_parts(s,kind)
 def test_08_exact_algebraic_sign(self):
  self.assertEqual(m.algebraic_sign(F(999,200),F(-3)),-1)
  self.assertEqual(m.algebraic_sign(F(100),F(-1)),1)
  self.assertEqual(m.algebraic_sign(0,0),0)
  self.assertEqual(m.algebraic_sign(-1,0),-1)
 def test_09_derivative_strict_margin(self):
  self.assertGreater(F(100)-(F(8)+F(2,75))*F(22,7),0)
 def test_10_close_root_preservation_in_refusal_surface(self):
  t=F(9,8)-F(1,2**70)
  self.assertNotIn(str(t),m.values(0))
  z=m.execute();q=copy.deepcopy(z);q['differing_rational_interior_coordinate']=str(t)
  with self.assertRaises(m.Refusal):m.check_record(z,q)
 def test_11_unsupported_zero_interval_forgery_rejected(self):
  z=m.execute();q=copy.deepcopy(z);q['total_simple_crossings_each']=0
  with self.assertRaises(m.Refusal):m.check_record(z,q)
 def test_12_census_promotion_forgery_rejected(self):
  z=m.execute();q=copy.deepcopy(z);q['after']['historical_missing_ordered_premises']=28
  with self.assertRaises(m.Refusal):m.check_record(z,q)
 def test_13_case_row_or_evidence_mutation_rejected(self):
  c=m.readp(m.CORPUS,m.CORPUS_BLOB)
  e=m.readp(m.REGISTER,m.REGISTER_BLOB)
  c=copy.deepcopy(c)
  for row in c['cases']:
   if row['id']==m.PREFIX+'tail0':
    row['spec']['phase_turn_rate']='-1/2';break
  with self.assertRaises(m.Refusal):m.receipt(c,e)
 def test_14_wrong_evidence_class_refused(self):
  z=m.execute();q=copy.deepcopy(z);q['evidence_class']='NATIVE_GEOMETRY'
  with self.assertRaises(m.Refusal):m.check_record(z,q)

if __name__=='__main__': unittest.main()
