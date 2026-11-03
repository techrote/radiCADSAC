#!/usr/bin/env python3
"""Fresh, source-bound complete-evidence census for the fifty frozen V54 gaps.

This finite registry does not repair a historical owner route, prove a universal
root grammar or authorize native geometry. Public reports are bounded data;
only immutable original source snapshots reach unchanged proof producers.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK_DIR = "research/machining-completeness/tasks/MC-038/"
SCHEMA = "radicadsac-mc038-post-v54-evidence-reconciliation/2.0"
REPORT = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
MACHINE = REPORT
BASE_MAIN = "4fa423eaf71be603a19981bf8b73ddcf4672481b"
PRIOR_REPORT = TASK_DIR + "pb00701-post-v54-evidence-reconciliation.json"
RUNTIME_FILE = TASK_DIR + "pb00701_pinned_source_runtime.py"
RUNTIME_GIT_BLOB = "058c06e4a1e0aee0297880622ee1157a46ef9067"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
COMPLETE = "COMPLETE_SOURCE_SPECIFIC"
TAIL = "PARTIAL_REFUSED_TAIL_ONLY"
CHILD = "PARTIAL_ORDERED_CHILD"
UNREGISTERED = "NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS"
LEVELS = (COMPLETE, TAIL, CHILD, UNREGISTERED)
FINITE = "COMPLETE_FINITE_SOURCE_ZERO_SET"
CONTINUUM = "COMPLETE_CLOSED_CONTINUUM_ZERO_SET"
MAX_BYTES = 1024 * 1024
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 8192

# Explicit immutable dependency manifest; no path is learned from caller data.
PINS = {'handoffs/current-authority.json': 'fa0233323a0804d8a5d3eb7cd892a274a6173fab',
 'research/machining-completeness/programme-v1.json': 'dee7045a1790b2870744df8ae7693429bd1d81a6',
 'research/machining-completeness/tasks/MC-002/domain-contract-v1.json': '23de82f5240a72509f7afe4acd5948b65bc4ff13',
 'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
 'research/machining-completeness/tasks/MC-038/pb00701-bernstein-sector-source-witnesses.json': '5b60a1ec744ffcd086c128766c966d305c26f1c9',
 'research/machining-completeness/tasks/MC-038/pb00701-component-prefix-composition.json': '94bf8f8193c190158640063790ca2bbe58306079',
 'research/machining-completeness/tasks/MC-038/pb00701-continuum-zero-source-witness.json': '6ce9bc63714695b67fb019bee3ad95430c1ea922',
 'research/machining-completeness/tasks/MC-038/pb00701-exact-zero-child-source-completion-witness.json': 'ed0a09595a4e73f7fdb9853d9151b8c7b6fea05f',
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json': '5841c331579489b25caef38cd412bdbf286f9134',
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-coverage-v54.json': '600ba29786f50397f29fd435fc5e2c57076088f9',
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-inventory-v54.json': '8649c20ab77e199f9c3fa351b8b6742218f27abb',
 'research/machining-completeness/tasks/MC-038/pb00701-five-source-evidence-replay.json': '4c619ee7011fa2d7a65f3391ff95cd8e7eecf3b0',
 'research/machining-completeness/tasks/MC-038/pb00701-multiplier-tail-source-completion-witness.json': 'caa9f5c31d6b43248a7e7fe7dcf68f54a8103dc9',
 'research/machining-completeness/tasks/MC-038/pb00701-ordered-child-source-completion-witness.json': '8e662094df4106b2a79711c565cd865008fadc8c',
 'research/machining-completeness/tasks/MC-038/pb00701-post-v54-evidence-reconciliation.json': '9f62dd6edc37206317eec054b2969bade02d7728',
 'research/machining-completeness/tasks/MC-038/pb00701-ratio-prefix-composition.json': '738c529f783ff76b074047d20fc219874f44a279',
 'research/machining-completeness/tasks/MC-038/pb00701-v23-bernstein-source-witness.json': 'f5de44d4e7e17d076bc575609d62aeb934d8f4b9',
 'research/machining-completeness/tasks/MC-038/pb00701-v27-three-frozen-refusals-witness.json': 'f4961533fab39d423f01983dd05b70f6a599615b',
 'research/machining-completeness/tasks/MC-038/pb00701-v6-tail100-knot-post-v54-witness.json': '6a5763483bda5103f16617ea269360d4eba26c66',
 'research/machining-completeness/tasks/MC-038/pb00701-v9-v43-full-source-witness.json': '1882c231f346d0f4622086b6aeee246bb520624b',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_child_map_model.py': 'c055e7f392a921b386a1a99cc70b5004121ae7f6',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_certificate.py': '92258bbad7fa4cfa1be5413a7253369e73abc318',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py': '77c18cb5c8c0700072c65969c973e8f3c4c12a99',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_interval_model.py': '859cb6ee600486198f53bfcc9660e2b482bb54d0',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_monotone_cut_model.py': '07b092f9c7df8b3325c2b15d17ca7abe9781cb10',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_orientation_cut_model.py': 'a56d6487963d269405ab82f3db4cce58a0165520',
 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_phase_cell_model.py': '117dafa3073dd2a5dc00c288089fd88d41628fae',
 'research/machining-completeness/tasks/MC-038/pb00701_bernstein_sector_source_witnesses.py': 'd71f25124c9780bdd4c77ff16e6d7c9cb63d4385',
 'research/machining-completeness/tasks/MC-038/pb00701_chebyshev_multiplier_model.py': 'd07abb52bf6a7236d49a80774c40be3459f03fb5',
 'research/machining-completeness/tasks/MC-038/pb00701_common_factor_model.py': 'eb96654d96717b34d05fd46f875abf0581c492d3',
 'research/machining-completeness/tasks/MC-038/pb00701_component_cone_phase_anchor_model.py': 'fc1f940f5b9b2b6fd8570b36a91c4389453e29b2',
 'research/machining-completeness/tasks/MC-038/pb00701_component_partition_model.py': 'da8d48b44e866aa52746f9d551c5a1617225b308',
 'research/machining-completeness/tasks/MC-038/pb00701_component_prefix_composition.py': '530e552bb41c020456fdf0f17506cb18577896f3',
 'research/machining-completeness/tasks/MC-038/pb00701_continuum_zero_source.py': '6fff0737c2f7bf8178dd7437c0981f7f3cd50cd0',
 'research/machining-completeness/tasks/MC-038/pb00701_correlated_closed_handoff_model.py': 'd47b8dd8fe8b4b91fd12c1e76974a5a4e85b03b2',
 'research/machining-completeness/tasks/MC-038/pb00701_coupled_bspline_model.py': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
 'research/machining-completeness/tasks/MC-038/pb00701_direct_rotated_coordinate_model.py': 'f943ee9b0c093bb84d559beb403d83e07646c316',
 'research/machining-completeness/tasks/MC-038/pb00701_dual_ratio_model.py': '7644219ae12011d3c5493104e6d752cf87bc6923',
 'research/machining-completeness/tasks/MC-038/pb00701_even_trig_multiplier_model.py': '9c3e579f73aee1645b829c8cfe1f5f14674eeb86',
 'research/machining-completeness/tasks/MC-038/pb00701_event_model.py': '104c0e7a459cd7da5025853b246faff244a5948e',
 'research/machining-completeness/tasks/MC-038/pb00701_exact_zero_child_source_completion.py': '668eef22876afdeec0931a6ccb6a48573b053203',
 'research/machining-completeness/tasks/MC-038/pb00701_finite_multiplier_model.py': 'd2e48bbd5177c74678255c91c3600efdfc221461',
 'research/machining-completeness/tasks/MC-038/pb00701_five_source_evidence_replay.py': 'a8aedb83772984831d5aa5c3b9b8d1cead04c345',
 'research/machining-completeness/tasks/MC-038/pb00701_l1_sign_orthant_envelope_model.py': 'f97e5c18e27fd8021362f24b62a11c889b5b6ce1',
 'research/machining-completeness/tasks/MC-038/pb00701_mixed_quadrature_phase_anchor_model.py': '925a51b89a477b388e4824eaae2675059ee47c33',
 'research/machining-completeness/tasks/MC-038/pb00701_monotone_ratio_model.py': '322035132bb05a9dbdf58f2d1f022394ce94e92f',
 'research/machining-completeness/tasks/MC-038/pb00701_multiharmonic_monotone_anchor_model.py': '38db0b5f1f4549f7ea632db27a5347b3aadd7b1a',
 'research/machining-completeness/tasks/MC-038/pb00701_multiharmonic_multiplier_model.py': '83cafe7e8e49ec923d5cd388ae3d45b4f2483b9a',
 'research/machining-completeness/tasks/MC-038/pb00701_multiplier_tail_source_completion.py': 'c5a3118b7eb486e5289d5a75c85d099d3e9d802b',
 'research/machining-completeness/tasks/MC-038/pb00701_multiterm_multiplier_model.py': '7eb80ea1a660b5a935e67c45355784cba4d7c34f',
 'research/machining-completeness/tasks/MC-038/pb00701_nonconstant_phase_anchor_model.py': '1eb91cd3274256fdff7b1e3d296508bdcf7a87e2',
 'research/machining-completeness/tasks/MC-038/pb00701_ordered_child_source_completion.py': '549251696e43f22122f8ba957baa2befcd8d77a8',
 'research/machining-completeness/tasks/MC-038/pb00701_orientation_root_partition_model.py': '2f96622b5c69655279d66fe2b36f8f3e03414660',
 'research/machining-completeness/tasks/MC-038/pb00701_orientation_transition_bridge_model.py': 'a0930d7bfddd619bf930a51bbfa14570e2450fe5',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_correlated_common_factor_model.py': 'dc7110fb46f585e8849b7fd3b0dc43f393fdbd87',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_correlated_proportional_common_factor_model.py': '7cecbbb120cc751f434cf49209e3a70cead85c3f',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_correlated_two_polynomial_shared_factor_model.py': '485ad89d9b5ff9847095f48880cc9a9cb3be96ce',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_correlated_varying_ratio_shared_factor_model.py': 'e4b9ecefed12a92c3d72da4edf0a12f45ce05e3d',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_dominance_model.py': 'bd0ee3d04a05134778905d690985d78acf347c84',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_sector_anchor_model.py': '923e9d63e3950a705923b9b5e619fee43c2819eb',
 'research/machining-completeness/tasks/MC-038/pb00701_phase_sector_partition_model.py': '6211e658621af7100c2509dcafdaeaf348e48d46',
 'research/machining-completeness/tasks/MC-038/pb00701_pinned_trig_child_views.py': 'c4a4d865226d01858d93685aa770987b14460e0b',
 'research/machining-completeness/tasks/MC-038/pb00701_pointwise_component_cone_model.py': 'a303bba600fa83a1b55c8e113ce1ec7d06f68590',
 'research/machining-completeness/tasks/MC-038/pb00701_pointwise_derivative_envelope_model.py': 'a0bbc30f5a26e2f2991c96640cf4410763ef2eb4',
 'research/machining-completeness/tasks/MC-038/pb00701_post_v54_evidence_reconciliation.py': '33efd291bdd9265ca6ecce7124a46f2a003b59f1',
 'research/machining-completeness/tasks/MC-038/pb00701_pythagorean_phase_cell_model.py': '3c792284922a481c9c2edad4f61f3f4f1afbe63a',
 'research/machining-completeness/tasks/MC-038/pb00701_ratio_prefix_composition.py': 'bdb72a2f5426ed792d2f9f1ed783187be5f7ada3',
 'research/machining-completeness/tasks/MC-038/pb00701_rational_phase_point.py': '9fc344e045fa800fb24d30902a641e534a1e197b',
 'research/machining-completeness/tasks/MC-038/pb00701_rational_turn_model.py': 'a1316ff0f71b2d7aa80807843a74fd8280779cb2',
 'research/machining-completeness/tasks/MC-038/pb00701_signed_a_direct_rotated_coordinate_model.py': 'd8cf3c4f3abaf1299bae2e4fd7120b17724a2df1',
 'research/machining-completeness/tasks/MC-038/pb00701_signed_b_anti_diagonal_model.py': '2f642ac0b6f222dd8ec2cf3a54ffa3c07bb27abe',
 'research/machining-completeness/tasks/MC-038/pb00701_source_adaptive_separator_model.py': 'd920a5b670d14ac4a54b0ed879e83532f2114b95',
 'research/machining-completeness/tasks/MC-038/pb00701_source_laurent_factor_model.py': '4e656c95a13858ee8ed496149d200a0a321a61a0',
 'research/machining-completeness/tasks/MC-038/pb00701_stationary_knot_composition.py': 'd0fbe7e189066fd9398958f1b1814b8147a6a64e',
 'research/machining-completeness/tasks/MC-038/pb00701_transverse_trig_interval.py': '2320f92efe4316d865a89f6d848737e2c000ca4d',
 'research/machining-completeness/tasks/MC-038/pb00701_two_span_source_knot_root_set.py': '516591fdbe25f4e0b1da00bc8aa70250de74b42c',
 'research/machining-completeness/tasks/MC-038/pb00701_v23_bernstein_source.py': '9b83c4485f8251b0649af6402acc9d777e281a96',
 'research/machining-completeness/tasks/MC-038/pb00701_v27_endpoint_multiplicity.py': 'a6ad0144a241d1e914d8862f4f1e0c8600a1a923',
 'research/machining-completeness/tasks/MC-038/pb00701_v41_algebraic_cut_order.py': 'e15944ee0fd7819b818c8c556f2c079039d042b7',
 'research/machining-completeness/tasks/MC-038/pb00701_v44_algebraic_cut_root_partition.py': '5d38a42fd8e23dc7930788e2b0c080caf567e851',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_affine_identity_frontier.py': '9fd150e97bce84fdb3c4bad075c9938f4df9136c',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py': '12c6efeb667a954ffc5a7e27849ae815d466580a',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_stationary_polynomial_order.py': '0954c5e1ad63ec1c8dd2acb3202882650b02c516',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v27_fixed_source_order.py': '006272b173a66bfb53cc4ddf0f5597857a42362b',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v27_three_frozen_refusals.py': 'c88bc20500e67d419ab82ea19ba8762434f2aff8',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v41_v13_fixed_source_order.py': '358dd4071ef968635bcd85f61dfa1965e51abda1',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_refusal_cone.py': '2a8079ee2cf012bc2a12794c4c5ff19ebd760007',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v10_tail0_crossings.py': '5bf6f85f1432b513ba89d17f5e4da17d1bce212d',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v10_tail_crossing.py': 'ada50468fe840625bd652c5a0042e0e3d75607d6',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v11_tail_contrast.py': 'a978284ce2672ce05d0ae45a9e2a9043c227a4f2',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v12_tail_contrast.py': '2b2e85f662f4cb2a97b82e264e007c38cada69fd',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v13_even_factor.py': '998130ba26f553237ac261017f3edc13f5f57700',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v16_chebyshev_crossing.py': '74bbdb48125f4168308fb6ffcbac4e5a08049c5d',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v17_positive_turn.py': 'e245b13045a96f549747baae1b25556da6cc9808',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v6_tail100_knot.py': '73b3f68bb4ecb8b4f69d073ebb0ee4621796d1a5',
 'research/machining-completeness/tasks/MC-038/verify_pb00701_v9_v43_full_source.py': '2cde41b799d5468ad84e7e482580fd4351b1d638'}
ALIASES = {'mc038_pinned_affine_identity': 'research/machining-completeness/tasks/MC-038/verify_pb00701_affine_identity_frontier.py',
 'mc038_pinned_five_finite_views': 'research/machining-completeness/tasks/MC-038/pb00701_five_source_evidence_replay.py',
 'mc038_source_bound_V27_THREE': 'research/machining-completeness/tasks/MC-038/verify_pb00701_v27_three_frozen_refusals.py',
 'mc038_source_bound_V6_KNOT': 'research/machining-completeness/tasks/MC-038/verify_pb00701_v6_tail100_knot.py',
 'mc038_source_bound_V9_V43': 'research/machining-completeness/tasks/MC-038/verify_pb00701_v9_v43_full_source.py',
 'pb00701_affine_identity_landed': 'research/machining-completeness/tasks/MC-038/verify_pb00701_affine_identity_frontier.py',
 'pb00701_v45_mc032': 'research/machining-completeness/tasks/MC-032/event_engine.py',
 'pinned_mc038_stationary': 'research/machining-completeness/tasks/MC-038/verify_pb00701_stationary_polynomial_order.py',
 'radicadsac_mc032_event_engine': 'research/machining-completeness/tasks/MC-032/event_engine.py',
 'reconciliation_verify_pb00701_post_v54_frontier': 'research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py',
 'v23_pinned_frontier': 'research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py',
 'v27_source_order_lowerer': 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_refusal_cone.py',
 'v41_v13_pinned_lowerer': 'research/machining-completeness/tasks/MC-038/verify_pb00701_v43_refusal_cone.py'}
FIVE_IDS = {'composite:DELEGATED_V6_CONSTANT_MODULATION:tail100',
 'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0',
 'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100',
 'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100',
 'harvested:verify_pb00701_v9:1a5fd052a155'}
CONTINUUM_ID = 'harvested:verify_pb00701_v53:cb01c327d5f1'
KNOT_ID = 'composite:DELEGATED_V6_CONSTANT_MODULATION:tail0'
V44_ID = 'harvested:verify_pb00701_v44:ffaea08e30c9'
V41_ID = 'harvested:verify_pb00701_v13:c426f65b5c10'
POSITIVE_ID = 'harvested:verify_pb00701_v9:4e7b85fa122a'
V23_ID = 'harvested:verify_pb00701_v52:2250401ce435'

PRODUCERS = {'bernstein_sectors': ('pb00701_bernstein_sector_source_witnesses.py',
                       'd71f25124c9780bdd4c77ff16e6d7c9cb63d4385'),
 'component_prefix': ('pb00701_component_prefix_composition.py', '530e552bb41c020456fdf0f17506cb18577896f3'),
 'continuum': ('pb00701_continuum_zero_source.py', '6fff0737c2f7bf8178dd7437c0981f7f3cd50cd0'),
 'exact_zero_children': ('pb00701_exact_zero_child_source_completion.py',
                         '668eef22876afdeec0931a6ccb6a48573b053203'),
 'five': ('pb00701_five_source_evidence_replay.py', 'a8aedb83772984831d5aa5c3b9b8d1cead04c345'),
 'knot': ('pb00701_two_span_source_knot_root_set.py', '516591fdbe25f4e0b1da00bc8aa70250de74b42c'),
 'multiplier_tails': ('pb00701_multiplier_tail_source_completion.py',
                      'c5a3118b7eb486e5289d5a75c85d099d3e9d802b'),
 'ordered_children': ('pb00701_ordered_child_source_completion.py',
                      '549251696e43f22122f8ba957baa2befcd8d77a8'),
 'ratio_prefix': ('pb00701_ratio_prefix_composition.py', 'bdb72a2f5426ed792d2f9f1ed783187be5f7ada3'),
 'refusal_cone': ('verify_pb00701_v43_refusal_cone.py', '2a8079ee2cf012bc2a12794c4c5ff19ebd760007'),
 'stationary': ('pb00701_stationary_knot_composition.py', 'd0fbe7e189066fd9398958f1b1814b8147a6a64e'),
 'trig_fixed': ('pb00701_pinned_trig_child_views.py', 'c4a4d865226d01858d93685aa770987b14460e0b'),
 'v23_bernstein': ('pb00701_v23_bernstein_source.py', '9b83c4485f8251b0649af6402acc9d777e281a96'),
 'v44': ('pb00701_v44_algebraic_cut_root_partition.py', '5d38a42fd8e23dc7930788e2b0c080caf567e851')}

SAVED_REPORTS = {'bernstein_sectors': ('pb00701-bernstein-sector-source-witnesses.json',
                       '5b60a1ec744ffcd086c128766c966d305c26f1c9'),
 'component_prefix': ('pb00701-component-prefix-composition.json',
                      '94bf8f8193c190158640063790ca2bbe58306079'),
 'continuum': ('pb00701-continuum-zero-source-witness.json', '6ce9bc63714695b67fb019bee3ad95430c1ea922'),
 'exact_zero_children': ('pb00701-exact-zero-child-source-completion-witness.json',
                         'ed0a09595a4e73f7fdb9853d9151b8c7b6fea05f'),
 'five': ('pb00701-five-source-evidence-replay.json', '4c619ee7011fa2d7a65f3391ff95cd8e7eecf3b0'),
 'multiplier_tails': ('pb00701-multiplier-tail-source-completion-witness.json',
                      'caa9f5c31d6b43248a7e7fe7dcf68f54a8103dc9'),
 'ordered_children': ('pb00701-ordered-child-source-completion-witness.json',
                      '8e662094df4106b2a79711c565cd865008fadc8c'),
 'ratio_prefix': ('pb00701-ratio-prefix-composition.json', '738c529f783ff76b074047d20fc219874f44a279'),
 'v23_bernstein': ('pb00701-v23-bernstein-source-witness.json', 'f5de44d4e7e17d076bc575609d62aeb934d8f4b9')}

OLD_FAMILIES = ('five', 'continuum', 'knot', 'trig_fixed', 'stationary', 'v44', 'refusal_cone', 'v23_bernstein')

NEW_FAMILIES = {'bernstein_sectors': ('source_witnesses', 'case_id'),
 'component_prefix': ('source_cases', 'source_case_id'),
 'exact_zero_children': ('source_specific_proofs', 'case_id'),
 'multiplier_tails': ('source_cases', 'case_id'),
 'ordered_children': ('source_cases', 'case_id'),
 'ratio_prefix': ('source_cases', 'source_case_id')}

FAMILY_IDS = {'bernstein_sectors': ['composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0',
                       'composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail100',
                       'composite:PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS:tail0'],
 'component_prefix': ['composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0',
                      'composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100',
                      'composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0',
                      'composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100',
                      'composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0'],
 'continuum': ['harvested:verify_pb00701_v53:cb01c327d5f1'],
 'exact_zero_children': ['composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0',
                         'composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0',
                         'composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0'],
 'five': ['composite:DELEGATED_V6_CONSTANT_MODULATION:tail100',
          'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0',
          'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100',
          'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100',
          'harvested:verify_pb00701_v9:1a5fd052a155'],
 'knot': ['composite:DELEGATED_V6_CONSTANT_MODULATION:tail0'],
 'multiplier_tails': ['composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100',
                      'composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100',
                      'composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100',
                      'composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100',
                      'composite:PB00701_V18_EXACT_LAURENT_MODULE_FACTOR:tail100'],
 'ordered_children': ['composite:PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR:tail0',
                      'composite:PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR:tail0',
                      'composite:PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION:tail0',
                      'composite:PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION:tail0',
                      'composite:PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR:tail0',
                      'composite:PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR:tail0',
                      'composite:PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR:tail0',
                      'composite:PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR:tail0',
                      'composite:PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR:tail0',
                      'composite:PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE:tail0',
                      'composite:PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE:tail0',
                      'composite:PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE:tail0',
                      'composite:PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF:tail0',
                      'composite:PB00701_V48_MIXED_ROOT_SINGLE_CUT:tail0',
                      'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0'],
 'ratio_prefix': ['composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0',
                  'composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100',
                  'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0',
                  'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100'],
 'refusal_cone': ['harvested:verify_pb00701_v9:4e7b85fa122a'],
 'stationary': ['composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0',
                'composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100'],
 'trig_fixed': ['composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0',
                'composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100',
                'harvested:verify_pb00701_v13:c426f65b5c10'],
 'v23_bernstein': ['harvested:verify_pb00701_v52:2250401ce435'],
 'v44': ['harvested:verify_pb00701_v44:ffaea08e30c9']}

V27_IDS = frozenset(FAMILY_IDS["trig_fixed"]) - {V41_ID}


class Refusal(ValueError):
    """Invalid evidence or resource exhaustion is nontruth, never coverage."""


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def bounded_bytes(value):
    """Preflight without recursive serialization or numeric coercion.

    In particular, booleans and integers remain distinct under canonical JSON;
    floats, arbitrary classes, cycles and huge/deep inputs never reach producers.
    """
    stack = [(value, 0, False)]
    active = set()
    visited = 0
    byte_budget = 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        visited += 1
        need(visited <= MAX_NODES and depth <= MAX_DEPTH,
             "RESOURCE_REFUSAL: JSON node/depth budget")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 1024,
                 "RESOURCE_REFUSAL: JSON cycle/container budget")
            active.add(id(obj))
            byte_budget += 2 + 2 * len(obj)
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, child in obj.items():
                    need(type(key) is str and len(key) <= MAX_STRING,
                         "RESOURCE_REFUSAL: JSON key budget")
                    byte_budget += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth + 1, False))
            else:
                stack.extend((child, depth + 1, False) for child in obj)
        elif type(obj) is str:
            need(len(obj) <= MAX_STRING, "RESOURCE_REFUSAL: JSON string budget")
            byte_budget += len(json.dumps(obj, ensure_ascii=True))
        elif type(obj) is int:
            need(obj.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer budget")
            byte_budget += len(str(obj))
        else:
            need(obj is None or type(obj) is bool,
                 "NONEXACT_JSON_SCALAR: floats and custom classes prohibited")
            byte_budget += 5
        need(byte_budget <= MAX_BYTES, "RESOURCE_REFUSAL: JSON aggregate byte budget")
    data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(data) <= MAX_BYTES, "RESOURCE_REFUSAL: JSON byte budget")
    return data


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def read_json(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    need(len(data) <= MAX_BYTES, "RESOURCE_REFUSAL: JSON file byte budget")
    try:
        result = json.loads(data, object_pairs_hook=unique_pairs,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                Refusal("NONFINITE_JSON_SCALAR")))
    except (RecursionError, ValueError, UnicodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    bounded_bytes(result)
    return result


def bounded_rational_token(value):
    """Bound ASCII integer/ratio syntax before Fraction; then check canonicality."""
    need(type(value) is str and 0 < len(value) <= 128 and
         re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value) is not None,
         "INVALID_OR_OVERSIZED_CANONICAL_RATIONAL_TOKEN")
    pieces = value.split("/")
    numerator = int(pieces[0])
    denominator = int(pieces[1]) if len(pieces) == 2 else 1
    need(numerator.bit_length() <= 256 and denominator.bit_length() <= 256,
         "RESOURCE_REFUSAL: rational token bit budget")
    result = Fraction(numerator, denominator)
    need(str(result) == value, "NONCANONICAL_RATIONAL_TOKEN")
    return result


def source_metadata(row):
    bounded_bytes(row)
    spec = row["spec"]
    # These rationals come ONLY from the byte-pinned frozen corpus. No caller
    # report is fed to Fraction or any historical source parser.
    edges = {spec["parameter_lo"], spec["parameter_hi"]}
    for channel in ("cos_splines", "sin_splines"):
        for spline in spec[channel].values():
            edges.update(spline["knots"])
    edges = sorted(edges, key=bounded_rational_token)
    return {
        "source_sha256": digest(spec),
        "original_row_sha256": digest(row),
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
        "phase_turn_law": {"offset": spec["phase_turn_offset"],
                           "rate": spec["phase_turn_rate"]},
        "original_source_piece_edges": edges,
    }


def bind_view(view, row, *, hash_field="source_sha256"):
    meta = source_metadata(row)
    need(view[hash_field] == meta["source_sha256"], "PRODUCER_ORIGINAL_SOURCE_HASH_MISMATCH")
    for field in ("source_parameter_id", "source_interval", "phase_turn_law"):
        if field in view:
            need(bounded_bytes(view[field]) == bounded_bytes(meta[field]),
                 "PRODUCER_SOURCE_PARAMETER_INTERVAL_OR_PHASE_MISMATCH")
    return meta


def _replay_old(runtime, indexed, add):
    def producer(key):
        return runtime.load(TASK_DIR + PRODUCERS[key][0])
    def pinned_saved(key, value):
        _pinned_saved(runtime, key, value)

    five = producer("five").expected_report()
    pinned_saved("five", five)
    views = five["source_attested_views"]
    need(len(views) == 5 and {v["case_id"] for v in views} == FIVE_IDS,
         "FIVE_SOURCE_UNION_IDENTITY_DRIFT")
    for view in views:
        cid = view["case_id"]
        meta = bind_view(view, indexed[cid])
        need(view["source_specific_mathematics_only"] is True and
             view["generic_route_repaired"] is False and
             type(view["closed_root_count"]) is int and
             len(view["events"]) == view["closed_root_count"],
             "FIVE_SOURCE_FINITE_EVENT_PROOF_MISSING")
        add("five", cid, view, COMPLETE, meta["source_interval"], "COMPLETE_FINITE_SOURCE_ZERO_SET")

    union = producer("continuum").expected_record()
    pinned_saved("continuum", union)
    selected = union["separate_source_zero_set_views"]
    need(set(selected["selected_prior_finite_case_ids"]) == FIVE_IDS and
         selected["selected_continuum_original_case_id"] == CONTINUUM_ID and
         selected["finite_event_semantics_never_used_for_continuum"] is True,
         "FINITE_CONTINUUM_UNION_IDENTITY_DRIFT")
    view = selected["continuum"]
    meta = bind_view(view, indexed[CONTINUUM_ID])
    zeros = view["zero_set"]
    need(view["status"] == "COMPLETE_CLOSED_CONTINUUM_ZERO_SOURCE_RESEARCH"
         and zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT"
         and zeros["every_closed_source_point_is_zero"] is True
         and zeros["closed_source_interval"] == meta["source_interval"]
         and zeros["isolated_root_count"] is None
         and zeros["isolated_finite_root_list_applicable"] is False,
         "CONTINUUM_REPLACED_BY_FINITE_EVENT_OR_NONTRUTH")
    add("continuum", CONTINUUM_ID, view, COMPLETE, meta["source_interval"],
        "COMPLETE_CLOSED_CONTINUUM_ZERO_SET")

    view = producer("knot").analyze_frozen_case(KNOT_ID)
    meta = bind_view(view, indexed[KNOT_ID])
    need(view["status"] == "EXACT_SOURCE_BOUND_TWO_SPAN_KNOT_ROOT_SET_RESEARCH"
         and view["frozen_case_id"] == KNOT_ID
         and view["global_source_knot_deduplication_established"] is True
         and view["global_multispan_root_count_established"] is True
         and type(view["global_distinct_roots_closed_source"]) is int
         and view["global_distinct_roots_closed_source"] == 1,
         "TWO_SPAN_FULL_SOURCE_PROOF_NOT_ESTABLISHED")
    add("knot", KNOT_ID, view, COMPLETE, meta["source_interval"], "COMPLETE_FINITE_SOURCE_ZERO_SET")

    mod = producer("trig_fixed")
    proofs = mod.replay_original_proofs()
    expected_ids = {"composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0",
                    "composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100",
                    V41_ID}
    need(set(mod.CASES) == expected_ids, "FIXED_TRIG_PRODUCER_SCOPE_DRIFT")
    for cid in sorted(expected_ids):
        reference = mod.reference_view(cid, proofs)
        need(reference["original_source_binding_sha256"] == mod.source_binding(indexed[cid]),
             "FIXED_TRIG_SOURCE_ROW_BINDING_MISMATCH")
        view = mod.compose(reference)
        need(view["status"] == "PINNED_TRIGONOMETRIC_CHILD_VIEWS_RECONCILED_RESEARCH_ONLY"
             and view["source_case_id"] == cid
             and view["source_binding_sha256"] == mod.source_binding(indexed[cid])
             and type(view["distinct_open_roots_proved_for_this_fixed_source"]) is int
             and view["distinct_open_roots_proved_for_this_fixed_source"] == 2,
             "FIXED_TRIG_SOURCE_COMPOSITION_NOT_ESTABLISHED")
        add("trig_fixed", cid, view, COMPLETE, source_metadata(indexed[cid])["source_interval"],
            "COMPLETE_FINITE_SOURCE_ZERO_SET")

    stationary = producer("stationary").replay_frozen_stationary_cases()
    selected_stationary = [v for v in stationary if v["historical_v54_disposition"] == ORDER_GAP]
    expected_ids = {"composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0",
                    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100"}
    need(len(stationary) == 3 and len(selected_stationary) == 2 and
         {v["source_case_id"] for v in selected_stationary} == expected_ids,
         "STATIONARY_CERTIFIED_SOURCE_MUST_NOT_ENTER_50_CASE_DENOMINATOR")
    for view in selected_stationary:
        cid = view["source_case_id"]
        meta = bind_view(view, indexed[cid], hash_field="original_source_sha256")
        need(view["status"] == "CONDITIONAL_EXACT_STATIONARY_POLYNOMIAL_KNOT_COMPOSITION"
             and view["left_physical_endpoint"]["relation"] == "NEGATIVE"
             and view["right_physical_endpoint"]["relation"] == "POSITIVE"
             and len(view["ordered_physical_zero_events"]) == 1
             and type(view["distinct_open_physical_zeros"]) is int
             and view["distinct_open_physical_zeros"] == 1,
             "STATIONARY_FULL_SOURCE_PROOF_NOT_ESTABLISHED")
        add("stationary", cid, view, COMPLETE, meta["source_interval"],
            "COMPLETE_FINITE_SOURCE_ZERO_SET")

    view = producer("v44").prove()
    meta = bind_view(view, indexed[V44_ID])
    need(view["status"] == "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH"
         and view["frozen_case_id"] == V44_ID
         and type(view["complete_physical_root_count"]) is int
         and view["complete_physical_root_count"] == 1
         and view["root_count_conserved_across_proof_cells"] is True
         and view["all_proof_cuts_are_event_neutral"] is True,
         "V44_FULL_SOURCE_ROOT_PARTITION_NOT_ESTABLISHED")
    add("v44", V44_ID, view, COMPLETE, meta["source_interval"], "COMPLETE_FINITE_SOURCE_ZERO_SET")

    proof = producer("refusal_cone").contract()
    matches = [v for v in proof["probe_cases"] if v["id"] == POSITIVE_ID]
    need(len(matches) == 1, "HARVESTED_V43_POSITIVE_SOURCE_MISSING")
    view = matches[0]
    need(view["sign"] == "POSITIVE_ON_CLOSED_SOURCE_SPAN" and
         view["strict_lower_bound"] == "7/24", "V43_CLOSED_SOURCE_POSITIVITY_NOT_ESTABLISHED")
    add("refusal_cone", POSITIVE_ID, view, COMPLETE, view["source_interval"],
        "COMPLETE_FINITE_SOURCE_ZERO_SET")

    view = producer("v23_bernstein").expected_report()
    pinned_saved("v23_bernstein", view)
    meta = bind_view(view, indexed[V23_ID], hash_field="original_source_sha256")
    need(view["case_id"] == V23_ID and
         bounded_bytes(view["original_source"]) == bounded_bytes(indexed[V23_ID]["spec"])
         and bounded_bytes(view["historical_observation"]) ==
             bounded_bytes(indexed[V23_ID]["expected"]),
         "V23_ORIGINAL_SOURCE_OR_REFUSAL_BINDING_MISMATCH")
    events = view["source_specific_proof"]["physical_event_proof"]
    need(events["complete_for_original_closed_source"] is True and
         type(events["closed_distinct_root_count"]) is int and
         events["closed_distinct_root_count"] == 1 and
         events["open_distinct_root_count"] == 0 and
         events["continuum_zero_component"] is False and
         events["events"][0]["analytic_order"] == 2,
         "V23_CLOSED_SOURCE_EVENT_PROOF_MISSING")
    add("v23_bernstein", V23_ID, view, COMPLETE, meta["source_interval"],
        "COMPLETE_FINITE_SOURCE_ZERO_SET")



def _runtime_module():
    """Hash and compile the very same helper buffer, bypassing import caches."""
    path = ROOT / RUNTIME_FILE
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: runtime source byte budget")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(actual == RUNTIME_GIT_BLOB, "PINNED_RUNTIME_SOURCE_DRIFT")
    module = types.ModuleType("_mc038_reconciliation_v2_pinned_runtime")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def read_report(path=REPORT):
    return read_json(path)


def original_corpus(runtime):
    raw = runtime.read_json(TASK_DIR + "pb00701-finite-owner-corpus-v54.json")
    inventory = runtime.read_json(TASK_DIR + "pb00701-finite-owner-inventory-v54.json")
    coverage = runtime.read_json(TASK_DIR + "pb00701-finite-owner-coverage-v54.json")
    audit = runtime.load(TASK_DIR + "verify_pb00701_post_v54_frontier.py")
    census = audit.audit(raw, inventory, coverage)
    need(census["cases"] == 121 and census["v54_dispositions"]["BLOCKED"] == 20
         and census["v54_dispositions"][ORDER_GAP] == 30,
         "HISTORICAL_121_20_30_DENOMINATOR_CHANGED")
    authority = runtime.read_json("handoffs/current-authority.json")
    programme = runtime.read_json("research/machining-completeness/programme-v1.json")
    domain = runtime.read_json("research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
    need(authority["capability_status"] == programme["capability_status"] == "NOT_ESTABLISHED"
         and authority["production_authorized"] is False
         and programme["production_authorized"] is False,
         "PROGRAMME_AUTHORITY_PROMOTION")
    need({g["id"]: g["state"] for g in programme["gates"]}["MC-B"] == "NOT_ESTABLISHED",
         "MC_B_PROMOTION")
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "MACHINING_DOMAIN_CHANGED")
    indexed = {row["id"]: row for row in raw["cases"]}
    need(len(indexed) == len(raw["cases"]) == 121, "DUPLICATE_ORIGINAL_SOURCE_ID")
    return indexed


def _pinned_saved(runtime, key, recomputed):
    filename, sha = SAVED_REPORTS[key]
    need(PINS[TASK_DIR + filename] == sha, "SAVED_REPORT_MANIFEST_DISAGREEMENT")
    need(bounded_bytes(runtime.read_json(TASK_DIR + filename)) == bounded_bytes(recomputed),
         "SAVED_PRODUCER_REPORT_DISAGREES_WITH_SOURCE_REPLAY: " + key)


def v27_closed_endpoint_guard(row):
    """Supplement the old open-root receipt with two actual closed exteriors.

    The selected source has fully clamped degree-zero/one channels. Their first
    and last controls therefore are the exact exterior values. At the original
    affine phases the only nonrational term is a positive multiple of sqrt(3).
    No sampled value, previous COMPLETE label or alleged event count is used.
    """
    bounded_bytes(row)
    cid, spec = row["id"], row["spec"]
    need(cid in V27_IDS, "V27_EXACT_ORIGINAL_ID_REQUIRED")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
         and spec["source_parameter_id"] == "source-time-t"
         and [spec["parameter_lo"], spec["parameter_hi"]] == ["0", "2"],
         "V27_ORIGINAL_INTERVAL_OR_PARAMETER_CHANGED")
    offset, rate = bounded_rational_token(spec["phase_turn_offset"]), bounded_rational_token(spec["phase_turn_rate"])
    turns = [offset, offset + 2 * rate]
    need(offset == Fraction(1, 2) and rate == Fraction(-2, 3)
         and turns == [Fraction(1, 2), Fraction(-5, 6)], "V27_ORIGINAL_PHASE_CHANGED")
    need(set(spec["cos_splines"]) == {"0", "2"} and set(spec["sin_splines"]) == {"1"},
         "V27_ORIGINAL_HARMONICS_CHANGED")

    def endpoints(spline):
        degree = spline["degree"]
        need(type(degree) is int and degree in (0, 1), "V27_ENDPOINT_SPLINE_DEGREE")
        need(spline["knots"] == ["0"] * (degree + 1) + ["1"] * (degree + 1)
             + ["2"] * (degree + 1)
             and len(spline["controls"]) == 2 * (degree + 1),
             "V27_ACTUAL_CLAMPED_ENDPOINT_PREMISE_MISSING")
        return (bounded_rational_token(spline["controls"][0]),
                bounded_rational_token(spline["controls"][-1]))

    c0 = endpoints(spec["cos_splines"]["0"])
    c2 = endpoints(spec["cos_splines"]["2"])
    s1 = endpoints(spec["sin_splines"]["1"])
    tail = 100 if cid.endswith(":tail100") else 0
    need(c0 == (Fraction(5), Fraction(5 + tail)) and
         c2 == (Fraction(1, 100), Fraction(1, 100)) and
         s1 == (Fraction(2), Fraction(6)), "V27_ORIGINAL_ENDPOINT_COEFFICIENTS_CHANGED")
    # Trig evaluations follow exactly from the original phase modulo one turn:
    # sin(pi)=0, cos(2pi)=1; sin(pi/3)=sqrt(3)/2, cos(2pi/3)=-1/2.
    need(turns[0] % 1 == Fraction(1, 2) and turns[1] % 1 == Fraction(1, 6)
         and (2 * turns[0]) % 1 == 0 and (2 * turns[1]) % 1 == Fraction(1, 3),
         "V27_EXACT_TRIG_ENDPOINT_LAW_MISSING")
    rational = (c0[0] + c2[0], c0[1] - c2[1] / 2)
    radical = (Fraction(0), s1[1] / 2)
    need(rational[0] == Fraction(501, 100) and rational[1] == Fraction(999 + 200 * tail, 200)
         and radical[1] == 3 and all(a > 0 and b >= 0 for a, b in zip(rational, radical)),
         "V27_CLOSED_EXTERIOR_STRICT_POSITIVITY_NOT_PROVED")
    return {
        "source_case_id": cid, **source_metadata(row),
        "method": "EXACT_CLAMPED_SOURCE_ENDPOINTS_AND_RATIONAL_TURN_TRIG_VALUES",
        "endpoints": [
            {"position": str(t), "phase_turn": str(turn),
             "value": {"rational": str(a), "sqrt_3_coefficient": str(b)},
             "strict_positive_rational_lower_bound": str(a),
             "sign": "POSITIVE", "is_physical_zero": False}
            for t, turn, a, b in zip((0, 2), turns, rational, radical)],
        "closed_exterior_root_count": 0,
        "old_open_root_receipt_unchanged": True,
        "root_count_copied_from_previous_complete_label": False,
    }


def evidence_entry(key, case_id, row, result, interval, kind):
    """Private complete-source adapter; public report input never reaches it."""
    need(key in PRODUCERS and case_id in FAMILY_IDS[key], "UNREGISTERED_PRODUCER_SOURCE_PAIR")
    need(row["id"] == case_id and row["expected"]["v54_disposition"] in ("BLOCKED", ORDER_GAP),
         "EVIDENCE_OUTSIDE_FROZEN_UNRESOLVED_DENOMINATOR")
    meta = source_metadata(row)
    need(bounded_bytes(interval) == bounded_bytes(meta["source_interval"]),
         "PARTIAL_INTERVAL_CANNOT_BE_COMPLETE_SOURCE")
    need(kind == (CONTINUUM if case_id == CONTINUUM_ID else FINITE),
         "FINITE_CONTINUUM_KIND_CONFUSION")
    return {
        "producer": key,
        "producer_code": PRODUCERS[key][0], "producer_git_blob": PRODUCERS[key][1],
        "level": COMPLETE, "scope": kind,
        "covered_original_source_interval": list(interval),
        "replayed_result_sha256": digest(result),
        **meta,
        "complete_original_source_zero_set": True,
        "supplemental_closed_endpoint_evidence":
            v27_closed_endpoint_guard(row) if case_id in V27_IDS else None,
    }


def new_source_receipt(key, view, row):
    """Check each selected actual producer's source and completeness contract."""
    bounded_bytes(view)
    need(key in NEW_FAMILIES, "NOT_A_REGISTERED_NEW_COMPLETE_FAMILY")
    _, id_field = NEW_FAMILIES[key]
    cid = view[id_field]
    need(cid == row["id"], "NEW_PRODUCER_SOURCE_ID_MISMATCH")
    field = "original_source_sha256" if "original_source_sha256" in view else "source_sha256"
    meta = bind_view(view, row, hash_field=field)
    need(view["original_row_sha256"] == meta["original_row_sha256"],
         "NEW_PRODUCER_WHOLE_ROW_BINDING_MISMATCH")
    if "original_source" in view:
        need(bounded_bytes(view["original_source"]) == bounded_bytes(row["spec"]),
             "NEW_PRODUCER_ORIGINAL_SOURCE_BYTES_CHANGED")
    if "historical_observation" in view:
        need(bounded_bytes(view["historical_observation"]) == bounded_bytes(row["expected"]),
             "NEW_PRODUCER_HISTORICAL_OBSERVATION_CHANGED")
    if "historical_v54_disposition" in view:
        need(view["historical_v54_disposition"] == row["expected"]["v54_disposition"],
             "NEW_PRODUCER_HISTORICAL_DISPOSITION_CHANGED")
    if key == "ordered_children":
        need(view["status"] == "COMPLETE_PINNED_ORIGINAL_SOURCE_PROOF_RESEARCH_ONLY"
             and view["complete_closed_zero_set_kind"] == "FINITE"
             and view["complete_original_source_zero_set"] is True
             and type(view["complete_closed_root_count"]) is int
             and 0 <= view["complete_closed_root_count"] == len(view["ordered_root_events"])
             and view["certificate_partition_cuts_are_not_physical_events"] is True,
             "ORDERED_CHILD_WHOLE_SOURCE_PROOF_MISSING")
    elif key == "exact_zero_children":
        need(view["complete_original_source_zero_set"] is True
             and type(view["complete_finite_physical_event_count"]) is int
             and view["complete_finite_physical_event_count"] == len(view["physical_events"])
             == len(view["physical_zero_set"]) == 1
             and view["historical_disposition_changed"] is False
             and view["production_authorized"] is False,
             "EXACT_ZERO_WHOLE_SOURCE_PROOF_MISSING")
    else:
        proof = view["source_specific_proof"] if key == "bernstein_sectors" else view
        if key == "bernstein_sectors":
            need(proof["source_parameter_id"] == meta["source_parameter_id"]
                 and bounded_bytes(proof["phase_turn_law"]) == bounded_bytes(meta["phase_turn_law"]),
                 "BERNSTEIN_SECTOR_ORIGINAL_PHASE_CHANGED")
        events = proof["physical_event_proof"]
        need(events["complete_for_original_closed_source"] is True
             and events["continuum_zero_component"] is False
             and bounded_bytes(events["source_interval"]) == bounded_bytes(meta["source_interval"])
             and type(events["closed_distinct_root_count"]) is int
             and 0 <= events["closed_distinct_root_count"] == len(events["events"]),
             "NEW_FINITE_FULL_CLOSED_SOURCE_PROOF_MISSING")
    return evidence_entry(key, cid, row, view, meta["source_interval"], FINITE)


def validate_registry(receipts, indexed, prior):
    """Reject an incomplete/overlapping union before reporting a new census."""
    original_ids = {cid for cid, row in indexed.items()
                    if row["expected"]["v54_disposition"] in ("BLOCKED", ORDER_GAP)}
    need(set(PRODUCERS) == set(FAMILY_IDS) == set(OLD_FAMILIES) | set(NEW_FAMILIES)
         and not (set(OLD_FAMILIES) & set(NEW_FAMILIES)), "PRODUCER_REGISTRY_KEYS_CHANGED")
    registered_ids = [cid for values in FAMILY_IDS.values() for cid in values]
    need(len(registered_ids) == len(set(registered_ids)) == 50
         and set(registered_ids) == original_ids and set(receipts) == original_ids,
         "REGISTRY_MUST_BE_DISJOINT_AND_EXACTLY_ALL_50_ORIGINAL_IDS")
    prior_rows = prior["source_cases"]
    previous = {row["case_id"]: row for row in prior_rows}
    need(prior["schema"] == "radicadsac-mc038-post-v54-evidence-reconciliation/1.0"
         and len(previous) == len(prior_rows) == 50 and set(previous) == original_ids,
         "PRIOR_V1_ID_CENSUS_CHANGED")
    need(Counter(row["registered_evidence_level"] for row in prior_rows) ==
         Counter({COMPLETE: 15, TAIL: 9, CHILD: 18, UNREGISTERED: 8}),
         "PRIOR_V1_EVIDENCE_LEVELS_CHANGED")
    old_preserved = 0
    for cid in sorted(original_ids):
        row, receipt, before = indexed[cid], receipts[cid], previous[cid]
        meta = source_metadata(row)
        key = next(key for key, ids in FAMILY_IDS.items() if cid in ids)
        need(receipt["producer"] == key and receipt["producer_code"] == PRODUCERS[key][0]
             and receipt["producer_git_blob"] == PRODUCERS[key][1],
             "REGISTRY_PRODUCER_OR_SOURCE_ASSIGNMENT_CHANGED")
        for field, expected in meta.items():
            need(bounded_bytes(receipt[field]) == bounded_bytes(expected)
                 and bounded_bytes(before[field]) == bounded_bytes(expected),
                 "REGISTRY_OR_PRIOR_ORIGINAL_SOURCE_BINDING_CHANGED")
        need(before["historical_v54_disposition"] == row["expected"]["v54_disposition"]
             and before["historical_observed_source_status"] == row["expected"]["observed"]["status"]
             and bounded_bytes(before["historical_spans"]) == bounded_bytes(row["expected"]["observed"]["spans"]),
             "PRIOR_ORIGINAL_HISTORICAL_OBSERVATION_CHANGED")
        need(receipt["level"] == COMPLETE and receipt["complete_original_source_zero_set"] is True
             and bounded_bytes(receipt["covered_original_source_interval"]) == bounded_bytes(meta["source_interval"])
             and receipt["scope"] == (CONTINUUM if cid == CONTINUUM_ID else FINITE),
             "INCOMPLETE_OR_UNTYPED_SOURCE_RECEIPT")
        need(type(receipt["replayed_result_sha256"]) is str and
             len(receipt["replayed_result_sha256"]) == 64 and
             all(c in "0123456789abcdef" for c in receipt["replayed_result_sha256"]),
             "FRESH_PRODUCER_RECEIPT_DIGEST_MISSING")
        closure = v27_closed_endpoint_guard(row) if cid in V27_IDS else None
        need(bounded_bytes(receipt["supplemental_closed_endpoint_evidence"]) == bounded_bytes(closure),
             "V27_EXECUTED_CLOSED_ENDPOINT_CLOSURE_MISSING")
        if key in OLD_FAMILIES:
            need(before["registered_evidence_level"] == COMPLETE
                 and before["evidence"]["producer"] == key
                 and before["evidence"]["replayed_result_sha256"] == receipt["replayed_result_sha256"],
                 "OLD_COMPLETE_FRESH_PROOF_RESULT_CHANGED_FROM_V1")
            old_preserved += 1
        else:
            need(before["registered_evidence_level"] != COMPLETE,
                 "NEW_FAMILY_CANNOT_OVERLAP_PRIOR_COMPLETE_SOURCE")
    need(old_preserved == 15, "PRIOR_FIFTEEN_COMPLETE_RECEIPTS_NOT_PRESERVED")
    return True


def replay_sources():
    """One fresh finite replay; return data-only views for reviewed consumers.

    This is an internal proof-data interface. It accepts no report or source
    arguments. The context closes all private module registrations on failure
    as well as success; a failed producer aborts, with no saved-PASS fallback.
    """
    for filename, sha in list(PRODUCERS.values()) + list(SAVED_REPORTS.values()):
        need(PINS.get(TASK_DIR + filename) == sha, "REGISTERED_PRODUCER_OR_REPORT_MANIFEST_DISAGREEMENT")
    runtime_module = _runtime_module()
    with runtime_module.PinnedRuntime(ROOT, PINS, ALIASES) as runtime:
        indexed = original_corpus(runtime)
        prior = runtime.read_json(PRIOR_REPORT)
        receipts, views = {}, {}

        def add(key, cid, result, level, interval, kind):
            need(level == COMPLETE, "PARTIAL_EVIDENCE_CANNOT_ENTER_COMPLETE_REGISTRY")
            need(cid not in receipts, "DUPLICATE_SOURCE_RECEIPT_OR_OVERLAPPING_UNION")
            receipts[cid] = evidence_entry(key, cid, indexed[cid], result, interval, kind)
            views[cid] = result

        _replay_old(runtime, indexed, add)
        for key, (container, id_field) in NEW_FAMILIES.items():
            filename, sha = PRODUCERS[key]
            need(PINS[TASK_DIR + filename] == sha, "PRODUCER_MANIFEST_DISAGREEMENT")
            fresh = runtime.load(TASK_DIR + filename).expected_report()
            _pinned_saved(runtime, key, fresh)
            selected = fresh[container]
            need(type(selected) is list and len(selected) == len(FAMILY_IDS[key])
                 and {view[id_field] for view in selected} == set(FAMILY_IDS[key]),
                 "NEW_COMPLETE_FAMILY_ORIGINAL_SOURCE_COHORT_CHANGED")
            for view in selected:
                cid = view[id_field]
                need(cid not in receipts, "DUPLICATE_SOURCE_RECEIPT_OR_OVERLAPPING_UNION")
                receipts[cid] = new_source_receipt(key, view, indexed[cid])
                views[cid] = view
        validate_registry(receipts, indexed, prior)
        return {"indexed": indexed, "prior": prior, "receipts": receipts,
                "views": views, "runtime_attestation": runtime.attestation()}


def report_from_replay(replay):
    """Format an internal fresh replay without executing a second proof pass."""
    indexed, prior, receipts = replay["indexed"], replay["prior"], replay["receipts"]
    validate_registry(receipts, indexed, prior)
    previous = {row["case_id"]: row for row in prior["source_cases"]}
    rows = []
    for cid in sorted(receipts):
        row, before = indexed[cid], previous[cid]
        rows.append({
            "case_id": cid, "origin": row["origin"], "provenance_kind": row["kind"],
            **source_metadata(row),
            "historical_v54_disposition": row["expected"]["v54_disposition"],
            "historical_observed_source_status": row["expected"]["observed"]["status"],
            "historical_spans": row["expected"]["observed"]["spans"],
            "prior_v1_registered_evidence_level": before["registered_evidence_level"],
            "registered_evidence_level": COMPLETE,
            "evidence": receipts[cid],
            "prior_complete_result_digest_preserved":
                True if before["registered_evidence_level"] == COMPLETE else None,
            "remaining_requirement": "General analytic coverage, generic route/composition and native obligations remain open.",
            "historical_disposition_changed": False,
        })
    prior_counts = Counter(row["prior_v1_registered_evidence_level"] for row in rows)
    report = {
        "schema": SCHEMA, "task": "MC-038", "evidence_class": "DETERMINISTIC_MODEL",
        "purpose": "FINITE_ORIGINAL_SOURCE_COMPLETE_EVIDENCE_CENSUS_NOT_GENERAL_ROUTE_ACCEPTANCE",
        "source_registry_baseline_main": BASE_MAIN,
        "frozen_corpus_git_blob": PINS[TASK_DIR + "pb00701-finite-owner-corpus-v54.json"],
        "prior_v1_report": {"path": PRIOR_REPORT, "git_blob": PINS[PRIOR_REPORT],
                            "historical_file_unchanged": True},
        "historical_v54": {"original_source_cases": 121, "route_refusals": 20,
                           "missing_ordered_span_premises": 30, "dispositions_changed": False},
        "registry_scope": {
            "all_50_historical_unresolved_ids_enumerated": True,
            "all_50_have_fresh_complete_source_specific_evidence": True,
            "all_registered_producers_reexecuted_from_pinned_original_sources": True,
            "all_possible_post_v54_proofs_exhaustively_discovered": False,
            "all_original_analytic_sources_covered": False,
            "new_general_root_event_or_composition_theorem": False,
            "normalized_universal_root_event_consumer": False,
            "generic_owner_routes_repaired": False,
        },
        "executed_byte_custody": {
            "runtime": RUNTIME_FILE, "runtime_git_blob": RUNTIME_GIT_BLOB,
            "same_checked_source_buffers_compiled": True,
            "same_checked_data_buffers_decoded": True,
            "snapshot": replay["runtime_attestation"],
            "python_and_standard_library_trusted": True,
            "hostile_python_security_sandbox_claimed": False,
        },
        "producer_registry": [
            {"producer": key, "code": filename, "code_git_blob": sha,
             "selected_original_source_ids": FAMILY_IDS[key],
             "saved_report": ({"path": SAVED_REPORTS[key][0], "git_blob": SAVED_REPORTS[key][1]}
                              if key in SAVED_REPORTS else None)}
            for key, (filename, sha) in sorted(PRODUCERS.items())],
        "summary": {
            "total_historical_unresolved_source_cases": len(rows),
            "by_registered_evidence_level": {level: sum(row["registered_evidence_level"] == level for row in rows) for level in LEVELS},
            "prior_v1_by_registered_evidence_level": {level: prior_counts[level] for level in LEVELS},
            "newly_completed_original_sources": sum(row["prior_v1_registered_evidence_level"] != COMPLETE for row in rows),
            "prior_complete_result_digests_preserved": sum(row["prior_complete_result_digest_preserved"] is True for row in rows),
            "complete_finite_sources": sum(row["evidence"]["scope"] == FINITE for row in rows),
            "complete_continuum_sources": sum(row["evidence"]["scope"] == CONTINUUM for row in rows),
            "historical_route_refusals_with_complete_source_evidence": sum(row["historical_v54_disposition"] == "BLOCKED" for row in rows),
            "historical_missing_ordered_premises_with_complete_source_evidence": sum(row["historical_v54_disposition"] == ORDER_GAP for row in rows),
            "selected_producer_families": len(PRODUCERS),
            "supplemented_executable_closed_endpoint_sources": len(V27_IDS),
        },
        "source_cases": rows,
        "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN_PROPAGATED",
                  "PB-007-04": "OPEN_PROPAGATED", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                  "native_geometry_or_STEP_qualified": False, "production_authorized": False,
                  "required_machining_operations": 26},
    }
    bounded_bytes(report)
    return report


def expected_report():
    return report_from_replay(replay_sources())


def _compare_with_replayed_bytes(submitted, expected_bytes):
    need(bounded_bytes(submitted) == expected_bytes,
         "REPORT_DISAGREES_WITH_PINNED_ORIGINAL_SOURCE_PRODUCER_REPLAY")
    return True


def validate_report(submitted):
    bounded_bytes(submitted)
    return _compare_with_replayed_bytes(submitted, bounded_bytes(expected_report()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.write_report):
        parser.error("choose --contract or --write-report")
    expected = expected_report()
    if options.write_report:
        REPORT.write_text(json.dumps(expected, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if options.contract:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(expected))
        print("PASS: all 50 original gaps have freshly replayed complete source evidence; general gates unchanged")
        print(json.dumps(expected["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
