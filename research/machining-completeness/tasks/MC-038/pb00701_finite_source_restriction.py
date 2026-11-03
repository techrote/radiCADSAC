#!/usr/bin/env python3
"""Bounded source-preserving restriction/recomposition of fifty qualified zero sets.

Research only. The public path executes the entire qualified default-12 refiner
and its upstream original-source proofs before any requested child is admitted.
Conditional fixed-source helpers cannot replace that fresh proof path.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK_DIR = "research/machining-completeness/tasks/MC-038/"
BASE_MAIN = "9eea5786f93c71090d4a3d4c7478d65a3f066d42"
SCHEMA = "radicadsac-mc038-finite-source-restriction/1.0"
REPORT = HERE / "pb00701-finite-source-restriction.json"
REFINER_MODEL = TASK_DIR + "pb00701_selected_implicit_root_refinement.py"
REFINER_MODEL_BLOB = "47dfd31a204d6edfb5fb2a82d7ce84c565aca7da"
REFINER_REPORT = TASK_DIR + "pb00701-selected-implicit-root-refinement.json"
REFINER_REPORT_BLOB = "a9f0fa0ecc4ab6189f84471147f5a93f58478331"
PARENT_REPORT_VALUE_SHA256 = "9703c8222f04ce231613bdd4585724f08401a83c2618ab01a362ba71cd57168f"
REFINER_REPORT_VALUE_SHA256 = '1538f4d87aa86b6efe5194b0fe694742eb33c525fc1a0869c065a41ad6a749f7'
REFINER_PINS = {'handoffs/current-authority.json': 'fa0233323a0804d8a5d3eb7cd892a274a6173fab',
 'research/machining-completeness/programme-v1.json': 'dee7045a1790b2870744df8ae7693429bd1d81a6',
 'research/machining-completeness/tasks/MC-002/domain-contract-v1.json': '23de82f5240a72509f7afe4acd5948b65bc4ff13',
 'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
 'research/machining-completeness/tasks/MC-038/pb00701-bernstein-sector-source-witnesses.json': '5b60a1ec744ffcd086c128766c966d305c26f1c9',
 'research/machining-completeness/tasks/MC-038/pb00701-component-prefix-composition.json': '94bf8f8193c190158640063790ca2bbe58306079',
 'research/machining-completeness/tasks/MC-038/pb00701-continuum-zero-source-witness.json': '6ce9bc63714695b67fb019bee3ad95430c1ea922',
 'research/machining-completeness/tasks/MC-038/pb00701-exact-zero-child-source-completion-witness.json': 'ed0a09595a4e73f7fdb9853d9151b8c7b6fea05f',
 'research/machining-completeness/tasks/MC-038/pb00701-fifty-source-zero-set-consumer.json': '8213026ed2a5205d2cfff44e45c26e89deab4ee9',
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json': '5841c331579489b25caef38cd412bdbf286f9134',
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-coverage-v54.json': '600ba29786f50397f29fd435fc5e2c57076088f9',
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-inventory-v54.json': '8649c20ab77e199f9c3fa351b8b6742218f27abb',
 'research/machining-completeness/tasks/MC-038/pb00701-five-source-evidence-replay.json': '4c619ee7011fa2d7a65f3391ff95cd8e7eecf3b0',
 'research/machining-completeness/tasks/MC-038/pb00701-multiplier-tail-source-completion-witness.json': 'caa9f5c31d6b43248a7e7fe7dcf68f54a8103dc9',
 'research/machining-completeness/tasks/MC-038/pb00701-ordered-child-source-completion-witness.json': '8e662094df4106b2a79711c565cd865008fadc8c',
 'research/machining-completeness/tasks/MC-038/pb00701-post-v54-evidence-reconciliation-v2.json': 'e52d3baf3692a011cf86234eeaa992ef407d99fd',
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
 'research/machining-completeness/tasks/MC-038/pb00701_fifty_source_zero_set_consumer.py': 'd5eef89ab168a2acc2588f13a6d87ab88b998d40',
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
 'research/machining-completeness/tasks/MC-038/pb00701_pinned_source_runtime.py': '058c06e4a1e0aee0297880622ee1157a46ef9067',
 'research/machining-completeness/tasks/MC-038/pb00701_pinned_trig_child_views.py': 'c4a4d865226d01858d93685aa770987b14460e0b',
 'research/machining-completeness/tasks/MC-038/pb00701_pointwise_component_cone_model.py': 'a303bba600fa83a1b55c8e113ce1ec7d06f68590',
 'research/machining-completeness/tasks/MC-038/pb00701_pointwise_derivative_envelope_model.py': 'a0bbc30f5a26e2f2991c96640cf4410763ef2eb4',
 'research/machining-completeness/tasks/MC-038/pb00701_post_v54_evidence_reconciliation.py': '33efd291bdd9265ca6ecce7124a46f2a003b59f1',
 'research/machining-completeness/tasks/MC-038/pb00701_post_v54_evidence_reconciliation_v2.py': '8dede56cebbbd5540b52a280b9a31191c8901fbb',
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
PINS = dict(REFINER_PINS, **{REFINER_MODEL: REFINER_MODEL_BLOB, REFINER_REPORT: REFINER_REPORT_BLOB})
DIRECT_INPUTS = {'research/machining-completeness/tasks/MC-038/pb00701-selected-implicit-root-refinement.json': {'bytes': 1755761,
                                                                                                 'git_blob': 'a9f0fa0ecc4ab6189f84471147f5a93f58478331',
                                                                                                 'path': 'research/machining-completeness/tasks/MC-038/pb00701-selected-implicit-root-refinement.json',
                                                                                                 'sha256': '83c59b69b0a0912997fa01f428aadbb45fb6731764241ddf9ab83efaae818b6f'},
 'research/machining-completeness/tasks/MC-038/pb00701_selected_implicit_root_refinement.py': {'bytes': 69079,
                                                                                               'git_blob': '47dfd31a204d6edfb5fb2a82d7ce84c565aca7da',
                                                                                               'path': 'research/machining-completeness/tasks/MC-038/pb00701_selected_implicit_root_refinement.py',
                                                                                               'sha256': '77907c4ab2acd27f0bc4169a5183b191412c144bcbd1c9fccf61f3063f35d70d'}}
SOURCE_RECORD_SHA256S = {'composite:DELEGATED_V6_CONSTANT_MODULATION:tail0': '852225d82a1c2e409851df8ce1aa1b3d6c6252f39b201d6be64ad332bdb32641',
 'composite:DELEGATED_V6_CONSTANT_MODULATION:tail100': '290f9930416f606667fdafd4d7a775701237062130197231d7016b7dea7b942c',
 'composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0': '3638a594aa84909b13667319fb7cb9af68ccf9065e60a1402807d6f6f49f54a3',
 'composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100': '8931d991118930a9ce2b4f02def79f9c7d046b727d5eae4e4f8ea35e40cd6cad',
 'composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0': '85a64b886ca99059a4e496b72cf56a256768d17e4a0a4749c1154a493460cc32',
 'composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100': 'c0373e0041af85e441f6ac83d08b4e247135268919f313b36f147e539841f370',
 'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0': 'ca69b4665a5a41d9b162b8ddc196f53fc5f41af3b2356fed8fc5640dd9cfb5f6',
 'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100': '221ae00e944a5c22ca248c6aa77a258a58329a757961e5ec445d0c3c91d883a7',
 'composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0': '83ae85052eb97623871b2e50a72adefb3d7522776f921633597cc4d393105059',
 'composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100': 'adfd550a6c573bc44c46f2340b951580123ec7da23268dc795d30b86f7e408b1',
 'composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0': 'f0d060bbf87cf09af35af2d3e1b1904ed636552a8a09e1832faf3f4f283ef2e1',
 'composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100': '3f935f759487867a43c2cde67bf78dd488685a25765bcd8fec5001589caaf987',
 'composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100': '71041e3418885fd3a814fae11a7e6fb84edc6270780485bcc3d58a126f541b5c',
 'composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100': 'a6c00316f76d925c12a19d38fdd6bfc29963438c2d3de79e5deac0ec696d0ebf',
 'composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100': 'c9a0d0b3554e7808096d05349f24ba0788a172c61ac41fe5cd136e6231e3518c',
 'composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0': '66ead0de93510be833fd5bb6f75782de831b841bd5c35da7613442f2683abdfb',
 'composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100': '85649fcab915b1e41aa15179e906b88eb8824057cf683345ebc8f6d1a05e3e27',
 'composite:PB00701_V18_EXACT_LAURENT_MODULE_FACTOR:tail100': 'ee748bc1ff66404683fb9b75111290f03d62e5e197e4c38815f076ec0e969429',
 'composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0': 'fd126e42a712c5dfcde6e77b603c19d7380dccb7ddac1e9262b6be867c8f59e5',
 'composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail100': '26707e932a5dd711a13f1cf76a8855789b45e7495f80140f097d42ef5b7f605f',
 'composite:PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR:tail0': '880edc1c3453d0702cd449d28fcfea44b8a41b5bb8dcb1e9216d46d1d114826b',
 'composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0': '83818c3511dd04463413d4e2ff33528e7e0889bd8e1a811e3708d6135a755377',
 'composite:PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR:tail0': '1dba166bbd5c565436ca2620dc20b48955f14b474b89efc49f60bbb0463fd199',
 'composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0': '614c38b33e6fc189660b6df38b1874a5a1e9cb90a8ea69d2e0b22a112574a341',
 'composite:PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS:tail0': '5dd03ef09d4dc1bd9bdcc8e55429a481c64c8d77eb4b7a9965c6852472cd593b',
 'composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0': '42c64b8bf0fd566149b31fc26fd22125d050281a5bb6f8512d1857413f0e3835',
 'composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100': '65329069791c33e6152db8fca32d506c1f3130b7567e7f45e564000d4178b9fa',
 'composite:PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION:tail0': 'f6a365d9277f357ffed9f5edb27909875adb37eeab9515ce6c9241c247fce7ca',
 'composite:PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION:tail0': '91b78fbbfba880e7c9371fe5b4b2dae2c387897ba2557c702dd6c6c3367f287c',
 'composite:PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR:tail0': '4749c6dc2f154b16f4b180765e57b5d59ad6f441297865f315ca8f1579064100',
 'composite:PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR:tail0': '7d2278a2193ac22fe05cd39dfbe28267705a66940cea6bafc0a4fcdb0c9350db',
 'composite:PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR:tail0': '120a6f245f735c089ed58ee9858beda89b27fbe8d924166f5df7bfb95feb5515',
 'composite:PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR:tail0': '9f101fae08ba10680f7a0317c69d95460bf3783edef117e60e19578d6e9d332d',
 'composite:PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR:tail0': '4d0d5763207128b0ca98769f244df5d1aafb3f84164b84dd803f173d91b842a9',
 'composite:PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE:tail0': '6b0f0b57692b879e4bb39b23d017ac4a4e2e7c952498e655f57fe662774e7ed6',
 'composite:PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE:tail0': 'fc2b4610e2ffd0521d9394be8544e9c929d7ba2fbb30482719aeb63263dd35e0',
 'composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0': '716770da42c53a7c73b64744f8b8dba2e2cc46698ea05012159599920b814390',
 'composite:PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE:tail0': 'e031f43dd0028e4e6e0a9835d4e12f7d2784c4d814a8e7c82eb3e59a6e37fdf9',
 'composite:PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF:tail0': 'd25767dec1f864f16520d69737a912b0091785196aaafab854529b3ff40b47da',
 'composite:PB00701_V48_MIXED_ROOT_SINGLE_CUT:tail0': '8536de3f2b1b68c81a0b9b6c83674c6eac1242f50ebfa21bab370f67101cf6c1',
 'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0': '4b0e6014ab55de73502b6a6c42f43152f79bf59deb0bfb0c2a4b41bbe1c30858',
 'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100': '58bf05ec548354c1f98ff23180daea99afd18c593c7f2ca263bf35e9fd3ef7d3',
 'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0': '4643de86a338de085fcc6756d3a1d43ee672294006dfaed3310bfde927b905ce',
 'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100': '521d3878909c6dd386583deb366090f5640f177d4ebd9a58ca2ec0ea31003c98',
 'harvested:verify_pb00701_v13:c426f65b5c10': '5965c91c7bcfcc548c7e687258bff6974003694c7f3e8528b714f14f5a159a7e',
 'harvested:verify_pb00701_v44:ffaea08e30c9': 'c9bb739cc8b67d9be36d647ea6484433c76eca27fd4a36b6f7a983ccfc2fc08c',
 'harvested:verify_pb00701_v52:2250401ce435': '0bcd171a5eaa2736f32724d19bd6d5505a30d074934475f01baf22e1931b81b5',
 'harvested:verify_pb00701_v53:cb01c327d5f1': '69ca27c377ec3093fa382158d491e6aafb9b6be01ace872db2335731f018a812',
 'harvested:verify_pb00701_v9:1a5fd052a155': 'b5580572a23d544705e841e5268f995ae00cb06a8859d214a8fb73780a0253d0',
 'harvested:verify_pb00701_v9:4e7b85fa122a': '194452c8b8b178be867ccf323517d18ae74b410a31e2a07e5bfa44e1fdfaae0b'}
SOURCE_INTERVALS = {'composite:DELEGATED_V6_CONSTANT_MODULATION:tail0': ['0', '2'],
 'composite:DELEGATED_V6_CONSTANT_MODULATION:tail100': ['0', '2'],
 'composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0': ['0', '2'],
 'composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100': ['0', '2'],
 'composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0': ['0', '2'],
 'composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100': ['0', '2'],
 'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0': ['0', '2'],
 'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100': ['0', '2'],
 'composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0': ['0', '2'],
 'composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100': ['0', '2'],
 'composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0': ['0', '2'],
 'composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100': ['0', '2'],
 'composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100': ['0', '2'],
 'composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100': ['0', '2'],
 'composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100': ['0', '2'],
 'composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0': ['0', '2'],
 'composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100': ['0', '2'],
 'composite:PB00701_V18_EXACT_LAURENT_MODULE_FACTOR:tail100': ['0', '2'],
 'composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0': ['0', '2'],
 'composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail100': ['0', '2'],
 'composite:PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR:tail0': ['0', '2'],
 'composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0': ['0', '2'],
 'composite:PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR:tail0': ['0', '2'],
 'composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0': ['0', '2'],
 'composite:PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS:tail0': ['0', '2'],
 'composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0': ['0', '2'],
 'composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100': ['0', '2'],
 'composite:PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION:tail0': ['0', '2'],
 'composite:PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION:tail0': ['0', '2'],
 'composite:PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR:tail0': ['0', '2'],
 'composite:PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR:tail0': ['0', '2'],
 'composite:PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR:tail0': ['0', '2'],
 'composite:PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR:tail0': ['0', '2'],
 'composite:PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR:tail0': ['0', '2'],
 'composite:PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE:tail0': ['0', '2'],
 'composite:PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE:tail0': ['0', '2'],
 'composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0': ['0', '2'],
 'composite:PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE:tail0': ['0', '2'],
 'composite:PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF:tail0': ['0', '2'],
 'composite:PB00701_V48_MIXED_ROOT_SINGLE_CUT:tail0': ['0', '2'],
 'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0': ['0', '2'],
 'composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100': ['0', '2'],
 'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0': ['0', '2'],
 'composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100': ['0', '2'],
 'harvested:verify_pb00701_v13:c426f65b5c10': ['0', '1'],
 'harvested:verify_pb00701_v44:ffaea08e30c9': ['0', '1'],
 'harvested:verify_pb00701_v52:2250401ce435': ['0', '1'],
 'harvested:verify_pb00701_v53:cb01c327d5f1': ['0', '1'],
 'harvested:verify_pb00701_v9:1a5fd052a155': ['0', '1'],
 'harvested:verify_pb00701_v9:4e7b85fa122a': ['0', '1']}
MAX_BYTES = 8 * 1024 * 1024
MAX_CODE_BYTES = 256 * 1024
MAX_NODES = 262144
MAX_DEPTH = 40
MAX_STRING = 8192
MAX_INPUT_BITS = 128
MAX_RECEIPT_BITS = 256
MAX_CUTS = 6
_FractionType = Fraction


class Refusal(ValueError):
    def __init__(self, reason, code="UNESTABLISHED"):
        super().__init__(reason)
        self.code = code
        self.reason = str(reason)[:512]

    def as_record(self):
        return {"status": "REFUSED", "code": self.code, "reason": self.reason,
                "proof_established": False, "all_requested_children_established": False,
                "parent_zero_set_replaced": False, "production_authorized": False}


def need(condition, reason, code="UNESTABLISHED"):
    if not condition:
        raise Refusal(reason, code)


def bounded_bytes(value):
    """Iterative exact JSON preflight before recursive serialization."""
    stack = [(value, 0)]
    seen = set()
    nodes = estimate = 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        need(nodes <= MAX_NODES and depth <= MAX_DEPTH,
             "JSON node/depth budget", "RESOURCE_REFUSAL")
        if type(item) in (dict, list):
            need(id(item) not in seen, "Cyclic or aliased JSON container", "RESOURCE_REFUSAL")
            seen.add(id(item))
            need(len(item) <= 1024, "JSON container budget", "RESOURCE_REFUSAL")
            estimate += 2 + len(item)*2
            if type(item) is dict:
                for key, child in item.items():
                    need(type(key) is str and len(key) <= 256, "Exact bounded JSON key", "RESOURCE_REFUSAL")
                    estimate += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth+1))
            else:
                stack.extend((child, depth+1) for child in item)
        elif type(item) is str:
            need(len(item) <= MAX_STRING, "JSON string budget", "RESOURCE_REFUSAL")
            estimate += len(json.dumps(item, ensure_ascii=True))
        elif type(item) is int:
            need(item.bit_length() <= 256, "JSON integer budget", "RESOURCE_REFUSAL")
            estimate += 80
        else:
            need(item is None or type(item) is bool, "Exact JSON scalar required", "RESOURCE_REFUSAL")
            estimate += 5
        need(estimate <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(raw) <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    return raw


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def clone(value):
    return json.loads(bounded_bytes(value))


def _rational_parts(value, max_bits=MAX_INPUT_BITS):
    need(type(value) is str and 0 < len(value) <= 128,
         "Bounded exact rational token required", "RESOURCE_REFUSAL")
    need(re.fullmatch(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?", value, flags=re.ASCII) is not None,
         "Canonical ASCII rational syntax required", "RESOURCE_REFUSAL")
    parts = value.split("/")
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    need(numerator.bit_length() <= max_bits and denominator.bit_length() <= max_bits,
         "Rational operand bit budget", "RESOURCE_REFUSAL")
    need(gcd(abs(numerator), denominator) == 1 and (len(parts) == 1 or denominator > 1),
         "Reduced canonical rational token required", "RESOURCE_REFUSAL")
    return numerator, denominator


def rational(value, max_bits=MAX_INPUT_BITS):
    return Fraction(*_rational_parts(value, max_bits))


def _pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "Duplicate JSON key", "RESOURCE_REFUSAL")
        result[key] = value
    return result


def _json_integer(token):
    need(len(token) <= 80, "JSON integer token budget", "RESOURCE_REFUSAL")
    result = int(token)
    need(result.bit_length() <= 256, "JSON integer operand budget", "RESOURCE_REFUSAL")
    return result


def _nonexact_json(token):
    raise Refusal("Nonexact JSON number: " + token[:40], "RESOURCE_REFUSAL")


def parse_json_bytes(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "JSON byte budget", "RESOURCE_REFUSAL")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=_json_integer, parse_float=_nonexact_json, parse_constant=_nonexact_json)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError, OverflowError) as error:
        raise Refusal("Malformed or exhausted JSON input", "RESOURCE_REFUSAL") from error
    bounded_bytes(value)
    return value


def _read_bounded(path, limit):
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit+1)
    except (OSError, ValueError) as error:
        raise Refusal("Bounded file read failed: " + type(error).__name__) from error
    need(len(raw) <= limit, "File byte budget", "RESOURCE_REFUSAL")
    return raw


def git_blob_bytes(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _checked_buffer(path, blob, limit=MAX_BYTES):
    need(type(path) is str and path in PINS and PINS[path] == blob,
         "Unregistered input buffer")
    full = ROOT / path
    need(full.resolve() == full.absolute(), "Pinned path is a symlink alias")
    raw = _read_bounded(full, limit)
    need(git_blob_bytes(raw) == blob, "Pinned input buffer drift: " + path)
    if path in DIRECT_INPUTS:
        need(len(raw) == DIRECT_INPUTS[path]["bytes"] and
             hashlib.sha256(raw).hexdigest() == DIRECT_INPUTS[path]["sha256"],
             "Direct input byte count or SHA256 drift: " + path)
    return raw


def _compile_checked(raw, relative, blob):
    need(type(raw) is bytes and len(raw) <= MAX_CODE_BYTES, "Code byte budget", "RESOURCE_REFUSAL")
    need(relative in PINS and PINS[relative] == blob and git_blob_bytes(raw) == blob,
         "Executed code does not match checked source")
    need(relative in DIRECT_INPUTS and len(raw) == DIRECT_INPUTS[relative]["bytes"] and
         hashlib.sha256(raw).hexdigest() == DIRECT_INPUTS[relative]["sha256"],
         "Executed direct buffer lost exact byte/SHA256 identity")
    module = types.ModuleType("_finite_restriction_checked_" + blob)
    module.__file__ = str(ROOT / relative)
    exec(compile(raw, module.__file__, "exec", dont_inherit=True, optimize=0), module.__dict__)
    module._checked_source_git_blob = blob
    return module


def qualified_refiner_module(raw=None):
    if raw is None:
        raw = _checked_buffer(REFINER_MODEL, REFINER_MODEL_BLOB, MAX_CODE_BYTES)
    module = _compile_checked(raw, REFINER_MODEL, REFINER_MODEL_BLOB)
    need(module.PINS == REFINER_PINS, "Qualified refiner dependency closure changed")
    return module


def _provider(provider=None):
    if provider is None:
        provider = qualified_refiner_module()
    need(type(provider) is types.ModuleType and
         getattr(provider, "_checked_source_git_blob", None) == REFINER_MODEL_BLOB and
         provider.PINS == REFINER_PINS, "Point provider is not the checked qualified refiner")
    return provider


def _invoke(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Requested proof computation exhausted resources", "RESOURCE_REFUSAL") from error
    except Exception as error:
        code = getattr(error, "code", "UNESTABLISHED")
        need(type(code) is str and len(code) <= 80, "Malformed upstream refusal code")
        raise Refusal("Requested proof computation failed: " + type(error).__name__ + ": " +
                      str(error)[:200], code) from error


def _capture_inputs():
    return {path: _checked_buffer(path, PINS[path], MAX_CODE_BYTES if path.endswith(".py") else MAX_BYTES)
            for path in (REFINER_MODEL, REFINER_REPORT)}


def _input_custody(buffers):
    return [{"path": path, "git_blob": PINS[path], "bytes": len(buffers[path]),
             "sha256": hashlib.sha256(buffers[path]).hexdigest()} for path in sorted(buffers)]


def _source(source, original=None):
    """Bind before parsing: callable helpers admit only exact qualified records."""
    bounded_bytes(source)
    need(type(source) is dict and type(source.get("case_id")) is str,
         "Exact original source record required")
    cid = source["case_id"]
    need(cid in SOURCE_RECORD_SHA256S and digest(source) == SOURCE_RECORD_SHA256S[cid],
         "Source record differs from the qualified original zero-set theorem")
    need(SOURCE_INTERVALS.get(cid) == source["source_interval"],
         "Immutable request-domain table disagrees with the qualified original source")
    if original is not None:
        bounded_bytes(original)
        need(type(original) is dict and original.get("id") == cid and
             digest(original) == source["original_row_sha256"] and
             digest(original.get("spec")) == source["source_sha256"],
             "Original whole row or coefficient specification changed")
        spec = original["spec"]
        need(spec["source_parameter_id"] == source["source_parameter_id"] and
             [spec["parameter_lo"], spec["parameter_hi"]] == source["source_interval"] and
             {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]} == source["phase_turn_law"],
             "Original parameter, interval or global phase changed")
    return cid


def _case_id(case_id):
    need(type(case_id) is str and len(case_id) <= 256 and case_id in SOURCE_RECORD_SHA256S,
         "Requested source ID is outside the qualified finite cohort", "UNSUPPORTED_SOURCE")
    return case_id


def _cut_tokens(cuts):
    need(type(cuts) is list and len(cuts) <= MAX_CUTS,
         "Cuts must be an exact list of at most six canonical rationals", "RESOURCE_REFUSAL")
    # Validate every token before even the first Fraction constructor.
    parts = [_rational_parts(token) for token in cuts]
    need(all(a[0]*b[1] < b[0]*a[1] for a, b in zip(parts, parts[1:])),
         "Cuts must be strictly increasing without duplicates")
    return [Fraction(numerator, denominator) for numerator, denominator in parts]


def _cuts(source, cuts):
    qs = _cut_tokens(cuts)
    lo, hi = map(rational, source["source_interval"])
    need(all(lo < q < hi for q in qs), "Every cut must be strictly inside the original source")
    return [lo, *qs, hi]


def _preflight_request(case_id, cuts):
    _case_id(case_id)
    qs = _cut_tokens(cuts)
    lo, hi = map(rational, SOURCE_INTERVALS[case_id])
    need(all(lo < q < hi for q in qs),
         "Requested cuts must be strictly inside the original source before proof execution")


def _sign(value):
    need(type(value) is int and value in (-1, 1), "Strict exact integer sign required")
    return value


def _event(source, event):
    bounded_bytes(event)
    zeros = source["zero_set"]
    need(zeros["kind"] == "FINITE_ORIGINAL_SOURCE_ZERO_SET" and type(event) is dict and
         type(event.get("event_id")) is str, "A finite bound original event is required")
    matches = [e for e in zeros["events"] if e["event_id"] == event["event_id"]]
    need(len(matches) == 1 and bounded_bytes(matches[0]) == bounded_bytes(event),
         "Event, uniqueness premise, source identity or physical order changed")
    return event


def default_cuts(source):
    _source(source)
    lo, hi = map(rational, source["source_interval"])
    qs = {lo+(hi-lo)*Fraction(i, 4) for i in (1, 2, 3)}
    qs.update(map(rational, source["original_source_piece_edges"][1:-1]))
    zeros = source["zero_set"]
    if zeros["kind"] == "FINITE_ORIGINAL_SOURCE_ZERO_SET":
        implicit = [e for e in zeros["events"] if e["coordinate"]["kind"] != "RATIONAL"]
        if implicit:
            a, b = map(rational, implicit[0]["coordinate"]["strict_open_bracket"])
            qs.add((a+b)/2)
    result = list(map(str, sorted(qs)))
    _cuts(source, result)
    return result


def point_receipt(provider, prepared, coordinate):
    """Actual original-source evaluation hook; no alternative proof path."""
    return _invoke(_provider(provider).point_receipt, prepared, coordinate)


def compare_event_with_cut(source, original, event, cut, *, provider=None, prepared=None):
    """Conditional relation -1: root<cut, 0: equality, +1: root>cut.

    Complete unique simple-root authority comes from the bound parent event.
    A point sign is used only strictly inside that event's original open bracket.
    """
    cid = _source(source, original)
    _event(source, event)
    q = rational(cut)
    lo, hi = map(rational, source["source_interval"])
    need(lo <= q <= hi, "Comparison coordinate lies outside the original source")
    coordinate = event["coordinate"]
    result = {"source_case_id": cid, "source_sha256": source["source_sha256"],
              "event_id": event["event_id"], "parent_event_sha256": digest(event), "cut": str(q)}
    if coordinate["kind"] == "RATIONAL":
        root = rational(coordinate["value"])
        relation = (root > q)-(root < q)
        method = "EXACT_RATIONAL_COMPARISON"
        evidence = {"root": str(root), "cut": str(q)}
    else:
        need(coordinate["kind"] == "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE" and
             bounded_bytes(event["order"]) == b'{"kind":"SMOOTH","value":1}' and
             event["location"] == "SPAN_INTERIOR" and
             coordinate["source_case_id"] == cid and coordinate["source_sha256"] == source["source_sha256"] and
             coordinate["source_parameter_id"] == source["source_parameter_id"],
             "Implicit comparison lacks the bound unique simple original-root premise")
        left, right = _sign(event["left_sign"]), _sign(event["right_sign"])
        need(left == -right, "Implicit comparison requires opposite physical side signs")
        a, b = map(rational, coordinate["strict_open_bracket"])
        need(a < b, "Original strict open bracket is empty")
        if q <= a or q >= b:
            relation = 1 if q <= a else -1
            method = "STRICT_ORIGINAL_BRACKET_BOUND"
            evidence = {"cut": str(q), "strict_open_bracket": [str(a), str(b)],
                        "equals_open_bracket_boundary": q == a or q == b,
                        "open_bound_equality_is_not_root_equality": True}
        else:
            provider = _provider(provider)
            if prepared is None:
                prepared = _invoke(provider.prepare_source_spec, original["spec"])
            _invoke(provider._prepared_source, prepared)
            need(prepared.source_sha256 == source["source_sha256"] and
                 prepared.source_parameter_id == source["source_parameter_id"] and
                 [str(prepared.left), str(prepared.right)] == source["source_interval"] and
                 {"offset": str(prepared.offset), "rate": str(prepared.rate)} == source["phase_turn_law"] and
                 list(map(str, prepared.edges)) == source["original_source_piece_edges"],
                 "Prepared point evaluator lost exact original source/phase/span binding")
            receipt = point_receipt(provider, prepared, q)
            bounded_bytes(receipt)
            sign = _invoke(provider._check_point, receipt, prepared, q)
            need(sign in (left, right), "Point has neither inherited strict side sign")
            relation = 1 if sign == left else -1
            method = "STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS"
            evidence = {"point_receipt": clone(receipt), "parent_event_sha256": digest(event),
                        "parent_uniqueness_evidence": clone(coordinate["uniqueness_evidence"]),
                        "original_strict_open_bracket": [str(a), str(b)],
                        "strictly_inside_original_bracket": True,
                        "unique_simple_root_inherited": True,
                        "coefficient_continuity_checked_by_original_source_evaluator": True}
    result.update(relation=relation, method=method, evidence=evidence)
    return result


def _comparison_table(source, original, bounds, provider):
    zeros = source["zero_set"]
    if zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT":
        return [], {}
    coordinates = sorted(set(bounds) | set(map(rational, source["original_source_piece_edges"])))
    events = zeros["events"]
    prepared = None
    # Prepare once only if an actual requested comparison is inside an implicit bracket.
    for event in events:
        coordinate = event["coordinate"]
        if coordinate["kind"] != "RATIONAL":
            a, b = map(rational, coordinate["strict_open_bracket"])
            if any(a < q < b for q in coordinates):
                prepared = _invoke(provider.prepare_source_spec, original["spec"])
                break
    receipts = [compare_event_with_cut(source, original, event, str(q),
                                      provider=provider, prepared=prepared)
                for event in events for q in coordinates]
    table = {(r["event_id"], r["cut"]): r["relation"] for r in receipts}
    for q in coordinates:
        row = [table[(event["event_id"], str(q))] for event in events]
        need(row == sorted(row) and row.count(0) <= 1,
             "Comparison premises contradict the inherited ordered distinct zero set")
    return receipts, table


def _binding(source):
    return {"source_case_id": source["case_id"], "source_sha256": source["source_sha256"],
            "original_row_sha256": source["original_row_sha256"],
            "source_parameter_id": source["source_parameter_id"],
            "phase_turn_law": clone(source["phase_turn_law"]),
            "original_source_interval": clone(source["source_interval"]),
            "original_source_piece_edges": clone(source["original_source_piece_edges"]),
            "parent_source_record_sha256": digest(source)}


def _root_boundary(source, event):
    return {"kind": "PHYSICAL_ZERO_EVENT", "event_id": event["event_id"],
            "source_case_id": source["case_id"], "source_sha256": source["source_sha256"]}


def _project_event(source, event, a, b, table):
    at_left = table[(event["event_id"], str(a))] == 0
    at_right = table[(event["event_id"], str(b))] == 0
    need(not (at_left and at_right), "A positive-length child cannot have one zero at both exteriors")
    location = "CHILD_LEFT_ENDPOINT" if at_left else "CHILD_RIGHT_ENDPOINT" if at_right else "CHILD_INTERIOR"
    order = event["order"]
    if at_left or at_right:
        side = "RIGHT" if at_left else "LEFT"
        if order["kind"] == "KNOT_SIDED":
            value = order[side.lower()]
        elif order["kind"] == "ONE_SIDED":
            need(order["side"] == side, "Original exterior supplies no outside germ")
            value = order["value"]
        else:
            need(order["kind"] == "SMOOTH", "Unknown original vanishing-order type")
            value = order["value"]
        need(type(value) is int and value > 0, "Exact positive inward vanishing order required")
        child_order = {"kind": "ONE_SIDED", "side": side, "value": value,
                       "outside_order": None, "global_smooth_multiplicity_claimed": False}
    else:
        need(order["kind"] != "ONE_SIDED", "Original exterior was moved inside a child")
        child_order = clone(order)
    coordinate = event["coordinate"]
    if coordinate["kind"] == "RATIONAL":
        locator = clone(coordinate)
    else:
        x, y = map(rational, coordinate["strict_open_bracket"])
        low, high = max(x, a), min(y, b)
        need(low < high and not (at_left or at_right), "Implicit child locator must remain strict and interior")
        locator = {"kind": "RESTRICTED_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE",
                   "source_case_id": source["case_id"], "parent_event_id": event["event_id"],
                   "source_sha256": source["source_sha256"],
                   "source_parameter_id": source["source_parameter_id"],
                   "source_piece_index": coordinate["source_piece_index"],
                   "source_span": clone(coordinate["source_span"]),
                   "strict_open_bracket": [str(low), str(high)],
                   "unique_simple_root_inherited": True,
                   "exact_rational_or_algebraic_root_coordinate_claimed": False}
    return {"original_event": clone(event), "parent_event_id": event["event_id"],
            "parent_event_sha256": digest(event), "parent_coordinate": clone(coordinate),
            "original_location": event["location"], "original_order": clone(order),
            "child_locator": locator, "child_location": location, "child_order": child_order,
            "left_sign": None if at_left else event["left_sign"],
            "right_sign": None if at_right else event["right_sign"]}


def _children(source, bounds, table):
    """Deterministic closed restrictions conditional on checked comparison premises."""
    zeros = source["zero_set"]
    edges = list(map(rational, source["original_source_piece_edges"]))
    if zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT":
        return [dict(_binding(source), child_id="CHILD_"+str(i), child_index=i,
                     interval=[str(a), str(b)], closed_interval=True,
                     source_piece_indices=[j for j, (x, y) in enumerate(zip(edges, edges[1:]))
                                           if max(a, x) < min(b, y)],
                     kind="CLOSED_CONTINUUM_ZERO_COMPONENT", every_child_point_is_zero=True,
                     cardinality="UNCOUNTABLY_INFINITE", finite_event_list_applicable=False,
                     closed_root_count=None, events=None, maximal_nonzero_cells=None,
                     endpoint_states=None, original_exterior_points=None, original_true_source_knots=None,
                     vanishing_orders_applicable=False, nonzero_sign_cells_applicable=False)
                for i, (a, b) in enumerate(zip(bounds, bounds[1:]))]
    events = zeros["events"]
    parents = zeros["maximal_nonzero_cells"]
    by_id = {e["event_id"]: e for e in events}
    interior = [e for e in events if e["location"] in ("SPAN_INTERIOR", "SOURCE_KNOT")]
    inside_index = {e["event_id"]: i for i, e in enumerate(interior)}
    cut_ids = {str(q): "CUT_"+str(i) for i, q in enumerate(bounds[1:-1])}
    knots = {k["coordinate"]: k for k in zeros["true_source_knots"]}

    def relation(event, q):
        return table[(event["event_id"], str(q))]

    def point_node(q):
        equal = [e for e in events if relation(e, q) == 0]
        if equal:
            return _root_boundary(source, equal[0])
        if q in (bounds[0], bounds[-1]):
            return {"kind": "SOURCE_EXTERIOR", "side": "LEFT" if q == bounds[0] else "RIGHT",
                    "coordinate": str(q)}
        return {"kind": "RATIONAL_PARTITION_CUT", "cut_id": cut_ids[str(q)], "coordinate": str(q),
                "source_case_id": source["case_id"], "source_sha256": source["source_sha256"]}

    def parent_cell_after(node):
        if node["kind"] == "PHYSICAL_ZERO_EVENT":
            eid = node["event_id"]
            return inside_index[eid]+1 if eid in inside_index else 0
        q = rational(node["coordinate"])
        return sum(relation(e, q) < 0 for e in interior)

    def node_less_q(node, q):
        if node["kind"] == "PHYSICAL_ZERO_EVENT":
            return relation(by_id[node["event_id"]], q) < 0
        return rational(node["coordinate"]) < q

    def q_less_node(q, node):
        if node["kind"] == "PHYSICAL_ZERO_EVENT":
            return relation(by_id[node["event_id"]], q) > 0
        return q < rational(node["coordinate"])

    children = []
    for i, (a, b) in enumerate(zip(bounds, bounds[1:])):
        selected = [e for e in events if relation(e, a) >= 0 and relation(e, b) <= 0]
        child_events = [_project_event(source, e, a, b, table) for e in selected]
        strict = [e for e in selected if relation(e, a) > 0 and relation(e, b) < 0]
        nodes = [point_node(a), *[_root_boundary(source, e) for e in strict], point_node(b)]
        child_pieces = [j for j, (x, y) in enumerate(zip(edges, edges[1:])) if max(a, x) < min(b, y)]
        cells = []
        for j, (left, right) in enumerate(zip(nodes, nodes[1:])):
            parent = parents[parent_cell_after(left)]
            pieces = sorted(set(child_pieces) & set(parent["source_piece_indices"]))
            need(bool(pieces), "Nonzero child component has no original source piece")
            crossed = [k for k in parent["crossed_nonzero_source_knots"]
                       if node_less_q(left, rational(k)) and q_less_node(rational(k), right)]
            cells.append({"cell_id": "CELL_"+str(j), "parent_cell_id": parent["cell_id"],
                          "left_boundary": clone(left), "right_boundary": clone(right),
                          "left_included": left["kind"] != "PHYSICAL_ZERO_EVENT",
                          "right_included": right["kind"] != "PHYSICAL_ZERO_EVENT",
                          "sign": _sign(parent["sign"]), "source_piece_indices": pieces,
                          "crossed_nonzero_source_knots": crossed})
        endpoint_states = []
        for side, q, cell in (("LEFT", a, cells[0]), ("RIGHT", b, cells[-1])):
            equal = [e for e in selected if relation(e, q) == 0]
            projection = next((e for e in child_events if equal and e["parent_event_id"] == equal[0]["event_id"]), None)
            location = ("ORIGINAL_LEFT_EXTERIOR" if q == bounds[0] else
                        "ORIGINAL_RIGHT_EXTERIOR" if q == bounds[-1] else
                        "ORIGINAL_SOURCE_KNOT" if str(q) in knots else "ARTIFICIAL_PARTITION_CUT")
            inward_sign = (projection["right_sign"] if side == "LEFT" else projection["left_sign"]) if equal else cell["sign"]
            endpoint_states.append({"side": side, "coordinate": str(q), "included": True,
                "original_point_location": location, "is_zero": bool(equal),
                "event_ref": equal[0]["event_id"] if equal else None,
                "value_sign": 0 if equal else cell["sign"], "inward_sign": _sign(inward_sign),
                "inward_order": projection["child_order"]["value"] if equal else 0,
                "outside_order": None, "outside_sign": None,
                "global_smooth_multiplicity_claimed": False})
        child = dict(_binding(source), child_id="CHILD_"+str(i), child_index=i,
                     interval=[str(a), str(b)], closed_interval=True, source_piece_indices=child_pieces,
                     kind="FINITE_RESTRICTED_ORIGINAL_SOURCE_ZERO_SET", finite_event_list_applicable=True,
                     closed_root_count=len(child_events), events=child_events, maximal_nonzero_cells=cells,
                     endpoint_states=endpoint_states,
                     original_exterior_points=[clone(p) for p in zeros["exterior_points"]
                                               if a <= rational(p["coordinate"]) <= b],
                     original_true_source_knots=[clone(k) for k in zeros["true_source_knots"]
                                                if a <= rational(k["coordinate"]) <= b],
                     vanishing_orders_applicable=True, nonzero_sign_cells_applicable=True)
        children.append(child)
    return children


def _deduplicate(records, key):
    result = {}
    for record in records:
        identity = record[key]
        if identity in result:
            need(bounded_bytes(record) == bounded_bytes(result[identity]),
                 "Shared closed children disagree about an original physical record")
        else:
            result[identity] = clone(record)
    return result


def _reconstruct_finite(source, bounds, children):
    """Rebuild from actual validated children, never by returning the parent."""
    occurrences = defaultdict(list)
    fragments = defaultdict(list)
    actual_events = []
    actual_exteriors = []
    actual_knots = []
    for index, child in enumerate(children):
        for projection in child["events"]:
            actual_events.append(projection["original_event"])
            occurrences[projection["parent_event_id"]].append((index, projection))
        for fragment in child["maximal_nonzero_cells"]:
            fragments[fragment["parent_cell_id"]].append((index, fragment))
        actual_exteriors.extend(child["original_exterior_points"])
        actual_knots.extend(child["original_true_source_knots"])
    event_map = _deduplicate(actual_events, "event_id")
    events = list(event_map.values())
    need([e["event_id"] for e in events] == ["ROOT_"+str(i) for i in range(len(events))],
         "Actual child events do not reconstruct distinct original event order")
    duplicates = 0
    for event in events:
        seen = occurrences[event["event_id"]]
        on_cut = (event["coordinate"]["kind"] == "RATIONAL" and
                  rational(event["coordinate"]["value"]) in bounds[1:-1])
        need(len(seen) == 1+int(on_cut), "Closed event occurrence law failed")
        if on_cut:
            duplicates += 1
            need(seen[1][0] == seen[0][0]+1 and
                 [projection["child_location"] for _, projection in seen] ==
                 ["CHILD_RIGHT_ENDPOINT", "CHILD_LEFT_ENDPOINT"],
                 "A cut zero must have adjacent opposite inward child germs")
        need(all(projection["parent_event_sha256"] == digest(event) for _, projection in seen),
             "Actual child original-event identities disagree")
    exterior_map = _deduplicate(actual_exteriors, "side")
    need(set(exterior_map) == {"LEFT", "RIGHT"}, "Actual children lost an original exterior record")
    exteriors = [exterior_map["LEFT"], exterior_map["RIGHT"]]
    knot_map = _deduplicate(actual_knots, "coordinate")
    knots = [knot_map[key] for key in sorted(knot_map, key=rational)]
    cells = []
    joins = 0
    for parent_cell_id, group in fragments.items():
        first, last = group[0][1], group[-1][1]
        need(parent_cell_id == "CELL_"+str(len(cells)), "Actual cell fragments do not preserve source order")
        signs = {_sign(fragment["sign"]) for _, fragment in group}
        need(len(signs) == 1, "Actual fragments of one original nonzero component disagree in sign")
        pieces = set()
        crossed = set()
        for _, fragment in group:
            pieces.update(fragment["source_piece_indices"])
            crossed.update(fragment["crossed_nonzero_source_knots"])
        for (left_index, left), (right_index, right) in zip(group, group[1:]):
            boundary = left["right_boundary"]
            need(right_index == left_index+1 and bounded_bytes(boundary) == bounded_bytes(right["left_boundary"]),
                 "Original nonzero cell fragments have a gap, overlap or reordered join")
            need(boundary["kind"] == "RATIONAL_PARTITION_CUT" and
                 left["right_included"] is True and right["left_included"] is True and
                 boundary["coordinate"] == children[left_index]["interval"][1] ==
                 children[right_index]["interval"][0] and
                 boundary["source_case_id"] == source["case_id"] and
                 boundary["source_sha256"] == source["source_sha256"],
                 "Only the same source's shared included nonzero cut can join cell fragments")
            q = boundary["coordinate"]
            if q in knot_map:
                knot = knot_map[q]
                need(knot["is_zero"] is False and knot["continuous"] is True and
                     knot["left_sign"] == knot["right_sign"] == next(iter(signs)),
                     "A zero or discontinuous knot cannot be merged into a nonzero component")
                crossed.add(q)
            joins += 1
        need(first["left_boundary"]["kind"] != "RATIONAL_PARTITION_CUT" and
             last["right_boundary"]["kind"] != "RATIONAL_PARTITION_CUT",
             "A restricted artificial cut survived complete recomposition")
        cells.append({"cell_id": parent_cell_id, "left_boundary": clone(first["left_boundary"]),
                      "right_boundary": clone(last["right_boundary"]),
                      "left_included": first["left_included"], "right_included": last["right_included"],
                      "sign": next(iter(signs)), "source_piece_indices": sorted(pieces),
                      "crossed_nonzero_source_knots": sorted(crossed, key=rational)})
    span_counts = [sum(e["location"] == "SPAN_INTERIOR" and e["source_piece_indices"] == [i]
                       for e in events) for i in range(len(source["original_source_piece_edges"])-1)]
    rebuilt = {"kind": "FINITE_ORIGINAL_SOURCE_ZERO_SET", "finite_event_list_applicable": True,
               "complete_for_original_closed_source": True, "isolated_root_count": len(events),
               "source_open_root_count": sum(e["location"] in ("SPAN_INTERIOR", "SOURCE_KNOT") for e in events),
               "strict_span_open_root_counts": span_counts, "events": events, "exterior_points": exteriors,
               "true_source_knots": knots, "maximal_nonzero_cells": cells,
               "nonzero_sign_cells_applicable": True,
               "nonzero_knots_and_proof_cuts_are_not_partition_boundaries": True,
               "global_cross_source_zero_deduplication_performed": False}
    child_zero_sum = sum(child["closed_root_count"] for child in children)
    child_cell_sum = sum(len(child["maximal_nonzero_cells"]) for child in children)
    need(child_zero_sum-duplicates == len(events), "Closed finite zero-count conservation failed")
    need(child_cell_sum-joins == len(cells), "Finite nonzero cell-fragment conservation failed")
    return rebuilt, {"child_sum": child_zero_sum, "cut_duplicates": duplicates, "parent_distinct": len(events)}, \
        {"child_sum": child_cell_sum, "nonzero_joins": joins, "parent_cells": len(cells)}


def recompose_source(source, original, cuts, children, comparisons, *, provider=None):
    """Validate actual child semantics, then reconstruct the bound original zero set.

    This is conditional on a fresh qualified parent supplied by the public path.
    Every source/row/event is additionally bound to its fixed qualified identity.
    """
    _source(source, original)
    bounded_bytes(children)
    bounded_bytes(comparisons)
    bounds = _cuts(source, cuts)
    provider = _provider(provider)
    checked_comparisons, table = _comparison_table(source, original, bounds, provider)
    need(bounded_bytes(comparisons) == bounded_bytes(checked_comparisons),
         "Comparison relation or strict original point/uniqueness evidence changed")
    expected_children = _children(source, bounds, table)
    need(bounded_bytes(children) == bounded_bytes(expected_children),
         "Actual child membership, order, germ, endpoint, source binding, coverage or cell intersection changed")
    need(type(children) is list and len(children) == len(bounds)-1,
         "Every positive-length closed child must be present exactly once")
    need(children[0]["interval"][0] == source["source_interval"][0] and
         children[-1]["interval"][1] == source["source_interval"][1] and
         all(a["interval"][1] == b["interval"][0] for a, b in zip(children, children[1:])),
         "Actual child intervals do not exactly cover the original source")
    if source["zero_set"]["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT":
        rebuilt = {"kind": "CLOSED_CONTINUUM_ZERO_COMPONENT", "cardinality": "UNCOUNTABLY_INFINITE",
                   "interval": [children[0]["interval"][0], children[-1]["interval"][1]],
                   "closed_interval": True, "complete_for_original_closed_source": True,
                   "every_closed_source_point_is_zero": True, "events": None,
                   "isolated_root_count": None, "maximal_nonzero_cells": None,
                   "finite_event_list_applicable": False, "nonzero_sign_cells_applicable": False,
                   "vanishing_orders_applicable": False}
        closed_counts = cell_counts = None
    else:
        rebuilt, closed_counts, cell_counts = _reconstruct_finite(source, bounds, children)
    need(bounded_bytes(rebuilt) == bounded_bytes(source["zero_set"]),
         "Actual child reconstruction differs from the fresh bound original zero set")
    return {"recomposed_zero_set": rebuilt, "recomposed_zero_set_sha256": digest(rebuilt),
            "closed_count_conservation": clone(closed_counts), "cell_rejoin_conservation": clone(cell_counts),
            "reconstructed_from_actual_children": True, "canonical_parent_zero_set_equal": True,
            "exact_closed_interval_coverage": True, "conditional_on_fresh_qualified_parent": True,
            "parent_event_coordinates_preserved": True, "parent_zero_set_replaced": False}


def partition_source(source, original, cuts, *, provider=None):
    """Conditional fixed-source helper; does not itself establish a fresh replay."""
    _source(source, original)
    bounds = _cuts(source, cuts)
    provider = _provider(provider)
    comparisons, table = _comparison_table(source, original, bounds, provider)
    children = _children(source, bounds, table)
    recomposition = recompose_source(source, original, cuts, children, comparisons, provider=provider)
    result = dict(_binding(source), kind="CONTINUUM_RESTRICTION_AND_RECOMPOSITION" if
                  source["zero_set"]["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT" else
                  "FINITE_RESTRICTION_AND_RECOMPOSITION", cuts=clone(cuts),
                  comparison_receipts=comparisons, children=children, recomposition=recomposition,
                  conditional_on_fresh_qualified_parent=True, no_reparameterization=True,
                  artificial_cuts_create_no_physical_events=True)
    bounded_bytes(result)
    return result


def _validate_partition(source, original, cuts, candidate, provider):
    bounded_bytes(candidate)
    need(type(candidate) is dict and set(candidate) == set(_binding(source)) | {
         "kind", "cuts", "comparison_receipts", "children", "recomposition",
         "conditional_on_fresh_qualified_parent", "no_reparameterization", "artificial_cuts_create_no_physical_events"},
         "Partition fields changed")
    binding = _binding(source)
    for key, value in binding.items():
        need(bounded_bytes(candidate[key]) == bounded_bytes(value), "Partition original binding changed: "+key)
    kind = ("CONTINUUM_RESTRICTION_AND_RECOMPOSITION" if
            source["zero_set"]["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT" else
            "FINITE_RESTRICTION_AND_RECOMPOSITION")
    need(candidate["kind"] == kind and bounded_bytes(candidate["cuts"]) == bounded_bytes(cuts),
         "Partition type or requested cuts changed")
    need(all(candidate[key] is True for key in ("conditional_on_fresh_qualified_parent",
         "no_reparameterization", "artificial_cuts_create_no_physical_events")),
         "Partition lost a required conditional/original-source premise")
    recomposition = recompose_source(source, original, cuts, candidate["children"],
                                    candidate["comparison_receipts"], provider=provider)
    need(bounded_bytes(candidate["recomposition"]) == bounded_bytes(recomposition),
         "Recomposition does not follow from the actual child records")
    return clone(candidate)


def replay_qualified_refinements():
    """Execute all69 default12 refinements and every upstream proof exactly once."""
    buffers = _capture_inputs()
    saved = parse_json_bytes(buffers[REFINER_REPORT])
    need(digest(saved) == REFINER_REPORT_VALUE_SHA256, "Qualified refiner report value changed")
    provider = qualified_refiner_module(buffers[REFINER_MODEL])
    context = _invoke(provider.replay_refinements, 12)
    report = _invoke(provider.report_from_replay, context)
    need(bounded_bytes(report) == bounded_bytes(saved),
         "Actual fresh refiner/upstream proof differs from the qualified saved report")
    return {"refiner_context": context, "refiner_report": report,
            "input_custody": _input_custody(buffers)}


def _qualified_context(context):
    """Internal retained-context validation, never public arbitrary-proof admission."""
    need(type(context) is dict and set(context) == {"refiner_context", "refiner_report", "input_custody"},
         "Qualified context fields changed")
    need(digest(context["refiner_report"]) == REFINER_REPORT_VALUE_SHA256,
         "Retained qualified refiner report changed")
    need(bounded_bytes(context["input_custody"]) ==
         bounded_bytes([DIRECT_INPUTS[path] for path in sorted(DIRECT_INPUTS)]),
         "Refiner same-buffer path/blob/byte-count/SHA256 custody changed")
    provider = qualified_refiner_module()
    report = _invoke(provider.report_from_replay, context["refiner_context"])
    need(digest(report) == REFINER_REPORT_VALUE_SHA256 and report["requested_steps"] == 12,
         "Retained refiner premises no longer derive the qualified default12 report")
    baseline = report["parent_baseline"]
    need(digest(baseline) == PARENT_REPORT_VALUE_SHA256, "Qualified original-source baseline changed")
    indexed = context["refiner_context"]["indexed"]
    sources = baseline["source_cases"]
    need({s["case_id"]: digest(s) for s in sources} == SOURCE_RECORD_SHA256S,
         "Qualified original-source population or binding table changed")
    for source in sources:
        _source(source, indexed[source["case_id"]])
    return provider, baseline, indexed


def restrict_from_context(context, case_id, cuts):
    """Internal composition from a retained fresh context, not a public proof input."""
    _preflight_request(case_id, cuts)
    provider, baseline, indexed = _qualified_context(context)
    source = next(s for s in baseline["source_cases"] if s["case_id"] == case_id)
    return partition_source(source, indexed[case_id], cuts, provider=provider)


def restrict_original_source(case_id, cuts):
    """Public bounded source-ID/cuts interface; every failure is atomic nontruth."""
    try:
        _preflight_request(case_id, cuts)
        context = _invoke(replay_qualified_refinements)
        partition = _invoke(restrict_from_context, context, case_id, cuts)
        return {"status": "ESTABLISHED_CLOSED_RESTRICTIONS_OF_PINNED_ORIGINAL_SOURCE",
                "proof_established": True, "all_requested_children_established": True,
                "qualified_refiner_report_sha256": REFINER_REPORT_VALUE_SHA256,
                "qualified_parent_report_sha256": PARENT_REPORT_VALUE_SHA256,
                "partition": partition, "parent_zero_set_replaced": False, "production_authorized": False}
    except Refusal as error:
        return error.as_record()


def replay_restrictions():
    context = _invoke(replay_qualified_refinements)
    provider, baseline, indexed = _qualified_context(context)
    partitions = [partition_source(source, indexed[source["case_id"]], default_cuts(source), provider=provider)
                  for source in baseline["source_cases"]]
    return {"qualified_context": context, "partitions": partitions}


def _summary(partitions):
    counts = Counter()
    methods = Counter()
    counts["original_sources"] = len(partitions)
    for partition in partitions:
        children = partition["children"]
        cuts = partition["cuts"]
        counts["closed_children"] += len(children)
        counts["all_interior_cuts"] += len(cuts)
        counts["maximum_cuts_per_source"] = max(counts["maximum_cuts_per_source"], len(cuts))
        if partition["kind"] == "CONTINUUM_RESTRICTION_AND_RECOMPOSITION":
            counts["continuum_sources"] += 1
            counts["continuum_children"] += len(children)
            continue
        counts["finite_sources"] += 1
        counts["finite_children"] += len(children)
        counts["finite_interior_cuts"] += len(cuts)
        reconstruction = partition["recomposition"]
        closed = reconstruction["closed_count_conservation"]
        cell = reconstruction["cell_rejoin_conservation"]
        counts["child_closed_finite_zero_occurrences"] += closed["child_sum"]
        counts["physical_zeros_on_interior_cuts"] += closed["cut_duplicates"]
        counts["recomposed_finite_physical_zeros"] += closed["parent_distinct"]
        counts["restricted_maximal_nonzero_cells"] += cell["child_sum"]
        counts["admissible_nonzero_cell_joins"] += cell["nonzero_joins"]
        counts["recomposed_maximal_nonzero_cells"] += cell["parent_cells"]
        counts["nonzero_finite_cuts"] += len(cuts)-closed["cut_duplicates"]
        point_source = False
        for receipt in partition["comparison_receipts"]:
            methods[receipt["method"]] += 1
            if receipt["method"] == "STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS":
                point_source = True
                counts["strict_point_comparisons"] += 1
            elif receipt["method"] == "STRICT_ORIGINAL_BRACKET_BOUND" and receipt["evidence"]["equals_open_bracket_boundary"]:
                counts["strict_open_bound_equalities_not_root_equalities"] += 1
        counts["sources_needing_point_comparison"] += int(point_source)
        for child in children:
            for event in child["events"]:
                if event["child_location"] == "CHILD_INTERIOR":
                    counts["child_relative_interior_zero_occurrences"] += 1
                else:
                    counts["child_relative_boundary_zero_occurrences"] += 1
                if event["parent_coordinate"]["kind"] != "RATIONAL" and \
                        event["child_locator"]["strict_open_bracket"] != event["parent_coordinate"]["strict_open_bracket"]:
                    counts["implicit_child_locators_clipped"] += 1
    need(counts["child_closed_finite_zero_occurrences"]-counts["physical_zeros_on_interior_cuts"] ==
         counts["recomposed_finite_physical_zeros"], "Derived finite population zero conservation failed")
    need(counts["restricted_maximal_nonzero_cells"]-counts["admissible_nonzero_cell_joins"] ==
         counts["recomposed_maximal_nonzero_cells"], "Derived finite population cell conservation failed")
    return dict(sorted(counts.items())), dict(sorted(methods.items()))


def report_from_replay(replay):
    need(type(replay) is dict and set(replay) == {"qualified_context", "partitions"},
         "Restriction replay fields changed")
    bounded_bytes(replay["partitions"])
    provider, baseline, indexed = _qualified_context(replay["qualified_context"])
    candidates = replay["partitions"]
    sources = baseline["source_cases"]
    need(type(candidates) is list and len(candidates) == len(sources),
         "A requested original source partition was omitted or duplicated")
    partitions = [_validate_partition(source, indexed[source["case_id"]], default_cuts(source), candidate, provider)
                  for source, candidate in zip(sources, candidates)]
    summary, methods = _summary(partitions)
    result = {"schema": SCHEMA, "status": "ALL_FIFTY_ORIGINAL_SOURCE_RESTRICTIONS_RECOMPOSED_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL", "qualified_base_main": BASE_MAIN,
        "proof_established": True, "all_requested_children_established": True,
        "qualified_upstream": {"refiner_model": REFINER_MODEL, "refiner_model_git_blob": REFINER_MODEL_BLOB,
            "refiner_report": REFINER_REPORT, "refiner_report_git_blob": REFINER_REPORT_BLOB,
            "fresh_refiner_report_sha256": REFINER_REPORT_VALUE_SHA256,
            "fresh_parent_report_sha256": PARENT_REPORT_VALUE_SHA256, "requested_refinement_steps": 12},
        "executed_byte_custody": {"direct_input_buffers": clone(replay["qualified_context"]["input_custody"]),
            "actual_full_default12_refiner_replay_executed": True,
            "fresh_refiner_report_canonically_equals_qualified_saved_report": True,
            "project_code_compiled_from_same_bounded_verified_buffers": True,
            "dependency_path_count": len(PINS), "python_and_standard_library_trusted": True,
            "hostile_python_sandbox_claimed": False},
        "scope": {"parent_complete_zero_sets_preserved": True,
            "original_parameter_and_global_phase_preserved": True,
            "original_event_coordinates_unchanged": True, "child_locators_are_separate_restrictions": True,
            "actual_child_records_reconstruct_parent": True, "closed_continuum_type_preserved": True,
            "artificial_cuts_create_no_physical_events": True, "failed_requests_return_atomic_nontruth": True,
            "generic_owner_route_repaired": False, "arbitrary_source_or_proof_admission": False,
            "new_root_completeness_theorem": False, "native_geometry_evidence": False,
            "parent_zero_set_replaced": False},
        "budgets": {"maximum_interior_cuts": MAX_CUTS, "input_rational_bits": MAX_INPUT_BITS,
            "receipt_rational_bits": MAX_RECEIPT_BITS, "report_bytes": MAX_BYTES,
            "json_value_nodes": MAX_NODES, "json_depth": MAX_DEPTH,
            "point_evaluation_limits_inherited_from_qualified_refiner": True},
        "parent_baseline": clone(baseline), "partitions": partitions,
        "summary": summary, "comparison_methods": methods, "gates": clone(baseline["gates"])}
    bounded_bytes(result)
    return result


def expected_report():
    return _invoke(report_from_replay, _invoke(replay_restrictions))


def read_report(path=REPORT):
    need(type(path) in (str, type(REPORT)), "Exact bounded report path required", "RESOURCE_REFUSAL")
    text = str(path)
    need(0 < len(text) <= 4096 and "\0" not in text, "Report path text budget", "RESOURCE_REFUSAL")
    return parse_json_bytes(_read_bounded(Path(path), MAX_BYTES))


def _compare_with_replayed_bytes(candidate, expected_bytes):
    need(type(expected_bytes) is bytes and len(expected_bytes) <= MAX_BYTES,
         "Bounded expected report required", "RESOURCE_REFUSAL")
    need(bounded_bytes(candidate) == expected_bytes,
         "Submitted restrictions differ from a fresh complete original-source replay")
    return True


def validate_report(candidate):
    bounded_bytes(candidate)
    return _compare_with_replayed_bytes(candidate, bounded_bytes(expected_report()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--contract", action="store_true")
    options = parser.parse_args()
    if not (options.write_report or options.contract):
        parser.error("choose --write-report and/or --contract")
    result = expected_report()
    if options.write_report:
        REPORT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True)+"\n")
    if options.contract:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(result))
        print("PASS: all fifty original-source closed restrictions reconstruct their complete parent zero sets")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()


