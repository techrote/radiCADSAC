#!/usr/bin/env python3
"""Finite, source-bound physical zero sets for the fifty frozen V54 gaps.

Every admitted source is replayed through the qualified v2 runtime. This module
translates actual proof fields and checks their composition on the original
closed parameter interval. It is not a root solver for caller supplied sources,
a discontinuity policy, a generic route repair, or production authorization.
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
BASE_MAIN = "fcf956849345a9333f83bf0dd11a1dc7fcd82aa2"
SCHEMA = "radicadsac-mc038-fifty-source-zero-set-consumer/1.0"
REPORT = HERE / "pb00701-fifty-source-zero-set-consumer.json"
V2_MODEL = TASK_DIR + "pb00701_post_v54_evidence_reconciliation_v2.py"
V2_BLOB = "8dede56cebbbd5540b52a280b9a31191c8901fbb"
V2_REPORT = TASK_DIR + "pb00701-post-v54-evidence-reconciliation-v2.json"
V2_REPORT_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
V2_REPORT_VALUE_SHA256 = "b23be343e1ee029ae05ba75da38742f53c984702c07f39a8fb949ab317a140f3"
RUNTIME_FILE = TASK_DIR + "pb00701_pinned_source_runtime.py"
RUNTIME_BLOB = "058c06e4a1e0aee0297880622ee1157a46ef9067"
MAX_BYTES = 2 * 1024 * 1024
MAX_CODE_BYTES = 128 * 1024
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 8192
MAX_ROOTS_PER_SOURCE = 8
MAX_ORIGINAL_PIECES = 2
FINITE = "FINITE_ORIGINAL_SOURCE_ZERO_SET"
CONTINUUM = "CLOSED_CONTINUUM_ZERO_COMPONENT"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
V41_ID = "harvested:verify_pb00701_v13:c426f65b5c10"
AUX_PINS = {
    "V27_THREE": (TASK_DIR + "pb00701-v27-three-frozen-refusals-witness.json",
                  "f4961533fab39d423f01983dd05b70f6a599615b"),
    "V6_KNOT": (TASK_DIR + "pb00701-v6-tail100-knot-post-v54-witness.json",
                "6a5763483bda5103f16617ea269360d4eba26c66"),
    "V9_V43": (TASK_DIR + "pb00701-v9-v43-full-source-witness.json",
               "1882c231f346d0f4622086b6aeee246bb520624b"),
}
# These literal manifests are generated once from the qualified v2 bytes.
# No path, source admission, or producer authority is learned from caller data.
V2_PINS = {'handoffs/current-authority.json': 'fa0233323a0804d8a5d3eb7cd892a274a6173fab',
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
SOURCES = {
  "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0": {
    "family": "knot",
    "original_row_sha256": "145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc",
    "qualified_receipt_sha256": "165fa1d194c7cac36311921d79eb6363f48e1338c9146d8ef01035905acd1597",
    "source_sha256": "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1"
  },
  "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100": {
    "family": "five",
    "original_row_sha256": "0801317d3452c77733a129148d58eaac2f06aa9cd26396a44892e82c524e1db2",
    "qualified_receipt_sha256": "dc5c65386c151a94fcef0d1abfe183d7c5bb92a98dd90f8da7366da6c4bbde86",
    "source_sha256": "f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5"
  },
  "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0": {
    "family": "stationary",
    "original_row_sha256": "9ee0aed1b32cb85389f372e291a1eb80b9666d2c480d1bfbfa9fb62254dc78d8",
    "qualified_receipt_sha256": "80c4c1dfb11c0dc9a406e9bf53b70fc0ce836ab82d35bd761a3d5b7df3b5236f",
    "source_sha256": "f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff"
  },
  "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100": {
    "family": "stationary",
    "original_row_sha256": "a656298a7843e5dfff9bcf4d6262e18331c12f37cb23381d94bd8487f0ab57ca",
    "qualified_receipt_sha256": "16d580e1e0149fdde54bc385311545d8cc1bb6ba62f9758df66a28b711dfdfd2",
    "source_sha256": "a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd"
  },
  "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0": {
    "family": "ratio_prefix",
    "original_row_sha256": "c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd",
    "qualified_receipt_sha256": "b061a5ee10484c7d6420fc853f22a2b005ec8c9d2acf9342509a5d0e0705c980",
    "source_sha256": "57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c"
  },
  "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100": {
    "family": "ratio_prefix",
    "original_row_sha256": "cdd45c443caa2e240e4b87736b227070371f7d4a94ac69c98987a3bc9d293632",
    "qualified_receipt_sha256": "1369d12914461602a4ea0ce9788989577bfce934d77c781e7b0d2a8cec394b1f",
    "source_sha256": "21a0dde2ee6783f4465ab0c23dbef08fc400a4c8f2169cc5b851a3b0c3f5e23b"
  },
  "composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0": {
    "family": "ratio_prefix",
    "original_row_sha256": "cf16b962fba955f1bf66b2412beb9c15e10aa263f3197172cc2961737bd6b804",
    "qualified_receipt_sha256": "1d1e4c1308c436747ac5d5a3d77f7778caf69e49273b965b7c81370c592ae6c0",
    "source_sha256": "1535f364cd4d3c1a3bf34f57f394ad70a17ad1327880a0a47f25f3ecff5c7560"
  },
  "composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100": {
    "family": "ratio_prefix",
    "original_row_sha256": "dd2744103931e0c754809f3db0376aa7a5aa986af2644fc7ae4ba7dd9348fce1",
    "qualified_receipt_sha256": "43895ac1d2464f4b184f19624974d3fd2a27129f6f7c1c7c45e393288fb604d8",
    "source_sha256": "f70a884ea00042d46f517577ab598d8c85152ad511d48ea0bb8b2e6d7c55d0d5"
  },
  "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0": {
    "family": "component_prefix",
    "original_row_sha256": "d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3",
    "qualified_receipt_sha256": "af27014ad137cea169a390deee86740ac27e503c9c2f3814e5fd506a364e773a",
    "source_sha256": "ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5"
  },
  "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100": {
    "family": "component_prefix",
    "original_row_sha256": "748ed522c8a2f7cc3d6bdb17cc2322d4d4fd3121378c3b5a0dc829861f88aa15",
    "qualified_receipt_sha256": "93110e60d6c42e7ddbbc16e523e603eb43efba2ccaca82b7b9c82c14a446240a",
    "source_sha256": "65b71861fed07c4b609364dd79c8c1700abe72ca8bcb8f70aec0a54af90d94f7"
  },
  "composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0": {
    "family": "component_prefix",
    "original_row_sha256": "9a69a5d28c6808a54591cb8b72af59d752a1861ae860875fc858388d114c74af",
    "qualified_receipt_sha256": "f4d96da1d2dc47ed1646a3bd85cad8402d29f7c3fcf904945d60d6b6301ffc70",
    "source_sha256": "c7abfbbba43a61fbcfc72fc3833a0dc764b6c0d10a29ee4f6faf178c7db12b9b"
  },
  "composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100": {
    "family": "multiplier_tails",
    "original_row_sha256": "094b31ab55141488e39589ab6e0deda02b21066f06ba8568110609a23cd0a003",
    "qualified_receipt_sha256": "75a0e5383c4765f3ffc88a673c4c78f98207b89b08d58e6cd2bc2e4d90de2952",
    "source_sha256": "a7131bea021c5c71d0da2682cd6d4c1a982e8c86196c818ad3f69a926afda2e5"
  },
  "composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100": {
    "family": "multiplier_tails",
    "original_row_sha256": "1940ec5f6aafb641a25fcda3f8941ff7dd9f2afc2bf13056da6920159c3f0e18",
    "qualified_receipt_sha256": "e5e426e05ea0cc1223c14ae440a39d49f0b4b9fa35cf653d07f95dee5fa7c68f",
    "source_sha256": "bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2"
  },
  "composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100": {
    "family": "multiplier_tails",
    "original_row_sha256": "3954e79fceefbcd6e4b5932197f0314dbd4b90891b8fbad8410f9572f746725d",
    "qualified_receipt_sha256": "507fbcc1a2d3fce6f265614723c25236fe7db2d38e8a1c2dbd9c258f698e57e6",
    "source_sha256": "8e41009417dd65f9a47a04b492dd9a91b88a7682f12f45305ce64ac38dffd7b7"
  },
  "composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100": {
    "family": "component_prefix",
    "original_row_sha256": "843557d83755db09aedfce1d145d2a41945ebe65accffa0b6077afee8d94c4b0",
    "qualified_receipt_sha256": "8cad2250d5b1f18a9d95299899835c4eae4fd8cdb5e5bdc2dd53313676b138da",
    "source_sha256": "89ff16b64ab62d1b3cd543e3c52c4f0f8c570dc29b3448545b391a8d798da9d6"
  },
  "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0": {
    "family": "component_prefix",
    "original_row_sha256": "a0e6a03211083aea1ad7db4aefd0cf813d9ec13780564d01f8ee8b556ccbc59e",
    "qualified_receipt_sha256": "aa9a979bade06a690f5561c75671df95473239d0b77881255567444340b7b61a",
    "source_sha256": "f4927df0e4db8a02af0905219d07fd1fdf4dfd8a50c0ef426323e633d6880d94"
  },
  "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100": {
    "family": "multiplier_tails",
    "original_row_sha256": "41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a",
    "qualified_receipt_sha256": "2e84108223556f18bbf73582158654342ef37d979a6ac1f52d844556b81fcb80",
    "source_sha256": "e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f"
  },
  "composite:PB00701_V18_EXACT_LAURENT_MODULE_FACTOR:tail100": {
    "family": "multiplier_tails",
    "original_row_sha256": "7c1304de8afc41ba322fb653f20a1f8b6c3e0ea27af8a7864e44058d6b4d60d1",
    "qualified_receipt_sha256": "139be7c40f10ef1a11f6a9f1b2791fc5942842ed1c5de7f72260023d686947bb",
    "source_sha256": "ed61c9b827417327b9dda32ec0469ba5f0eab9622fb531d4b1bc959a312aa4a1"
  },
  "composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0": {
    "family": "bernstein_sectors",
    "original_row_sha256": "06f88535a67c3d521d831f2205b69c3466ff4a2723cdb53b37c5e430b24c04c8",
    "qualified_receipt_sha256": "d432e3b055495f323ce712faf556d699f4dda909f1ad96844de631fa62a8e756",
    "source_sha256": "2c0db76bcf217c98b53d8b45ee537aec4da818c649df2436c27860a4d8c17111"
  },
  "composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail100": {
    "family": "bernstein_sectors",
    "original_row_sha256": "fa9de27d0eead12eb2c8cee6e49b4b51ba6508e1b1c9dbc8b6e5620c2d15ddf6",
    "qualified_receipt_sha256": "4b5b8425f8597af5c27a4ee799a4f5b77b0aed882c6621b7d66f5af181bf9dea",
    "source_sha256": "2b1f53109ad708bd6eab37e83529e1001a7cadfa82fe630ddf230d94f2132d29"
  },
  "composite:PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "1b9853fb48e5fe91dab9856c75f43fb3591f1272367f895e7f382d00a58c9edd",
    "qualified_receipt_sha256": "9d28e7ed95b4bcfbb364984b8dce94021cb6f2a325c897c994d17303c23c2c8e",
    "source_sha256": "4304ce6d31b385ce3e3c1af3f31e677d91099f244a7befdcff9170367d4aace9"
  },
  "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0": {
    "family": "exact_zero_children",
    "original_row_sha256": "e52a27e5c3dcdf984919cdcd7bb925c52d2865550035da357cd87178b9fbfc89",
    "qualified_receipt_sha256": "2366aba33e418f75d2ef28ce430c3d606bf34af0d886c3a08e7201e943340a46",
    "source_sha256": "e8d2451833854ee7eaf73d4fb70b78b86ba72194b2688876f3bb9ee6ab132ffd"
  },
  "composite:PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "696718a819afa68c7a7122e9fba85eae3b5a8b8be905f94836f666fd74d9298b",
    "qualified_receipt_sha256": "dbd640abf650e33753b798f6fdaa771575bf85b7cc1b59519050f85529a1365e",
    "source_sha256": "e565ddf6bb0bab080128aeda16be5ea60466b3b971aa98d0408ea9a96da3d052"
  },
  "composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0": {
    "family": "exact_zero_children",
    "original_row_sha256": "90642204b36339c0bea36a1196c4b1045f4b0fa360d25493eb59b23881579ab8",
    "qualified_receipt_sha256": "a4d2b2291ceffdd6592dcba17fee83b0b6e1c9e81c02af0a5a804624d56bfd54",
    "source_sha256": "d7bf5969875c5ae44fa83f80d217fe17b02aca4db58545dc943c43e744ef68b6"
  },
  "composite:PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS:tail0": {
    "family": "bernstein_sectors",
    "original_row_sha256": "333c1bf98905cd41773c7da92efd33f36dc2f1e1bc947b285d9175a4926a25ad",
    "qualified_receipt_sha256": "24b6527f207e3b00b70c72543a48676c026b15481f6cb47f268267bf38e5f8a5",
    "source_sha256": "a9bb78a5415d1c45f54be7838f77739c8854cf329a97b36576f2a2fedf4ed3e4"
  },
  "composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0": {
    "family": "trig_fixed",
    "original_row_sha256": "ec76b07111b15331c2d509b04c66ee209b5ec0a5c508accbf77eabb99454b0ca",
    "qualified_receipt_sha256": "af1094f0e75b7fc1597378e00c7c052a5d70756a4900fca6ed7113b1bb13ed92",
    "source_sha256": "bdefb90689be6c6e29ffcd77611c40add0ee7d05099e94e3916174b6f74048dd"
  },
  "composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100": {
    "family": "trig_fixed",
    "original_row_sha256": "a76882b242c1ff03924ea96aa4290ade41b6dc9d6599c0bec06a537eb5c02260",
    "qualified_receipt_sha256": "2a9804f584fd6ee5bbda9194af6570302701fb386cd6b118bc2204f41739bd71",
    "source_sha256": "64b130ec50dbe5ae8a8eb2d2335c4a08d2c652f7e458b0bb88ff2b941603a23a"
  },
  "composite:PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "4bb9b1fd7c9b5e6ae47c3f52cfd1eb6374136c4621ba3220d44b2456c1a0964a",
    "qualified_receipt_sha256": "9283e07b1ed023eb4b88dde61d3b75bf9a6b784a309f6df6d7dee6aef1488cc7",
    "source_sha256": "7f2984f588215067297eeabe4f5b6c57d993c3ce2c33374e551982ed43de3093"
  },
  "composite:PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "7312b290c7d1246f15cefe92b5d1694b6dcac5f6143b2dfd270b7cd1920f64a2",
    "qualified_receipt_sha256": "5a8fceb73894ac8c280b843ff1df8bdc7350c42d51f0c58ffb9d25aca4557df9",
    "source_sha256": "ea2259d594a90d9523a46250e5ed8023dd081a3bf283bf8c2b410f0b18cfa25a"
  },
  "composite:PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "b3df7d07a1386f1e0b64c611d67def143692b95ef10da6a8c6b104ce83a9e1d0",
    "qualified_receipt_sha256": "f447ee5b9274cc968c10afe9f2f25d4b1b345c70356a89e5bff2fdc8365a5ae0",
    "source_sha256": "7e637ad3528fa5d55ae7cdd9aee3b3d8f2716d089203896a24d80a823f1e969d"
  },
  "composite:PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "5437a61eaf745a9c5ef5f4405934815db26d147c9d3524a8db66a1146e7d298a",
    "qualified_receipt_sha256": "78e686b0cacd2c945971c5b2c2421684b7ed92841930b2902f7b44a64f950442",
    "source_sha256": "404a68c1f2624abb29b700250807b43c466cab18c049c8e78a1049ce5fee10da"
  },
  "composite:PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "0caac73bf90d76a5c83f1faa60c2122959a1ad3109e53318c3e975505db1830d",
    "qualified_receipt_sha256": "2f2e9a959fecc6dd5bc15a7df4ba5cf9a46593f8d38299854a2420ccea33dd4d",
    "source_sha256": "6e7d4ae0dcd4303243772ec7cb1914c590ed91b6b5b27af5262f24ee8e493f19"
  },
  "composite:PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "2a7abe39076a67f824b394913e225054168c7a5e4d8e35cd2fa36a8618b8a2e8",
    "qualified_receipt_sha256": "69f86435cd3894db193dbdca3be72be566ea8d6be810036a5dc053187325493c",
    "source_sha256": "78cb3259190ca810d825690303e33b69f7a63f6ca7bc4fba7d705e470a90695f"
  },
  "composite:PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "a9d612e237f7277daa3d85f4218fc774cdf391a1761da33e1eb980bf4a35f286",
    "qualified_receipt_sha256": "7746a9120bfe090d14b20757a4e9481cd96bc501a4dc4ae35115413653284231",
    "source_sha256": "cde19c3ac184e59bf8914f130c3e9b1a988b529467e39bc6b8493764a0feb0fa"
  },
  "composite:PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "a8d5801d40c97979d8a49124ddb286c59be91b41bb0cf52c9047e60163e12982",
    "qualified_receipt_sha256": "618e9e21631e55e2f72898c48b183d786f970526356aa029052a7f0ea69ce833",
    "source_sha256": "9b7429ae290de259b2990b39740f40495c02b407e4e906e7eece77ea65c43f03"
  },
  "composite:PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "7a5ae576818a753fb0b0afb1f09058b58b468da8fc884f528166c05bf1c0b176",
    "qualified_receipt_sha256": "89052942bf45e00c853ff74fda259df60c5bd4655af9c0fc30ccc541a26c3567",
    "source_sha256": "daeafb37dd81d27fbba1c97dd09b14767531e37046237449aab3eaa9adfc1061"
  },
  "composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0": {
    "family": "exact_zero_children",
    "original_row_sha256": "8291b11b51d2109451ba852185bf6d9504c9d7e46473bf01be5924508ded5fad",
    "qualified_receipt_sha256": "0c6aaa139eaf1ae63bca81d1882081dba88bf6e741c97703fc74504eaad91c24",
    "source_sha256": "90a5df370094bcd8cef37be171f9bb12264c15a32237300b5435dc8871c6c2bf"
  },
  "composite:PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "c0e0cea514ac59ef80d492b8feb255efd2a7883926a8f95ff9ddb9e472901b97",
    "qualified_receipt_sha256": "d5bbc400b5037e3b65c0a1e24f435c8b1bc6c8ffe251b08d74ba04c3b6c5031a",
    "source_sha256": "95a977a9d300218fa2bd45cd54b752f2bb976b3c73c934d3c1aa715a25d6faed"
  },
  "composite:PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "98057a188fdf320d0238600f3b8a4c10dcb60f9a569010b44cda06a32970a9c4",
    "qualified_receipt_sha256": "287d6b1509966b23f399ccf3ea1635de6c240d0dfccbb05a025112e3277bb785",
    "source_sha256": "28cd4b4be4c74e6404b1a307d2217b2dc5a8b708b28c5ad75309c35e48092efd"
  },
  "composite:PB00701_V48_MIXED_ROOT_SINGLE_CUT:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "90bee5b127f42eca93118f3b5effdb46f305824271cb703e9d990ffa8d956058",
    "qualified_receipt_sha256": "5224412d5e96819ef2cd6848b578d6c7547febe235f481167299c2dff11c0b5e",
    "source_sha256": "0435a131c257bb5d453932f3692a45f787f83c9cc073fb38c879570f1f60ebfd"
  },
  "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0": {
    "family": "five",
    "original_row_sha256": "2a26a89bcce4070571f41cf377697fc6f258c4c9e04819c14096103f720861cf",
    "qualified_receipt_sha256": "c1516208442e37831c8f621560ff6af3e61bcf3711a0aeb33fbc3a6ffe503705",
    "source_sha256": "9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af"
  },
  "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100": {
    "family": "five",
    "original_row_sha256": "19fe46322a75273920c5bfa1a7874b1d229f74fa43ad1231375aee42fae02c82",
    "qualified_receipt_sha256": "3b229d23059a13084a9e339290773878cea6cba8d6a72cb864af6bc9aac60857",
    "source_sha256": "8e3af5a5e74c3fc3f364607f5c3c4b03cd1adc2e2dd6e16bfc03ddf870de0d2b"
  },
  "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0": {
    "family": "ordered_children",
    "original_row_sha256": "406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279",
    "qualified_receipt_sha256": "342f49bd2b04f97a1dad8a314c6e48a9e1410d549cb97bada52bd9d46968300e",
    "source_sha256": "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2"
  },
  "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100": {
    "family": "five",
    "original_row_sha256": "6e122da708ff0c68a339e0bfa5daba1e5321cb79e15af9e27b63712fb1348b63",
    "qualified_receipt_sha256": "4e7d00ac273d4c009045a99c757e17f92f020bd08583f97b5ac7b0370ba17734",
    "source_sha256": "cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a"
  },
  "harvested:verify_pb00701_v13:c426f65b5c10": {
    "family": "trig_fixed",
    "original_row_sha256": "13097451121a66ee0440091a422bb4845907e7a6fa175d011ca08ae3966fea07",
    "qualified_receipt_sha256": "a0622be3aeaf44f4cfc4049597e64a44a3ceb933135f7857370d52094fe62d39",
    "source_sha256": "e8425a4701f74195d99b91ea345663dbe4bc4d8b69b09dac426370e3ddcd1111"
  },
  "harvested:verify_pb00701_v44:ffaea08e30c9": {
    "family": "v44",
    "original_row_sha256": "7423adadf8c52ff28d47d9f63effbc5a2a7a630bdaf7efe6f8eeb1d2a85c5600",
    "qualified_receipt_sha256": "739a2df0445b512d0bdb85323dcadd3d860be493dc9a078859ea71f7c0556299",
    "source_sha256": "d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2"
  },
  "harvested:verify_pb00701_v52:2250401ce435": {
    "family": "v23_bernstein",
    "original_row_sha256": "545b621c525b85657edfe2191981406f82d5e00a8a0ea11316004e6e466bc153",
    "qualified_receipt_sha256": "b59be5520111bd7ae52f0571ae1339804fb0acefca51f843a58f9bf45c615d03",
    "source_sha256": "4a3ee3f47b9347429c13830abef382301c7963b0af518f0977390c2d3ffba040"
  },
  "harvested:verify_pb00701_v53:cb01c327d5f1": {
    "family": "continuum",
    "original_row_sha256": "8ff7c86adc4803c6c284752a746eeedd517e3053aefbcc33b164912edf92cc7c",
    "qualified_receipt_sha256": "aafe9d4eebf77432562197119cd9d14a94072554458b47c34d3c0d8f685a7263",
    "source_sha256": "a02ab8d83473f81d47b20c205083403babfc07059ca82303f1e6c92ab7481423"
  },
  "harvested:verify_pb00701_v9:1a5fd052a155": {
    "family": "five",
    "original_row_sha256": "1e43de38d286e69dcd1295def05c2710878e3232da1d49cfea5c95c69822219f",
    "qualified_receipt_sha256": "a468a70d1700dd7070818c719a220ff318a3474e9e3c57d58d15e9544933da2a",
    "source_sha256": "710259612833cfe40e73ae528e0d0e944a87123c9bb4b3f4f76cef33c45bcf4d"
  },
  "harvested:verify_pb00701_v9:4e7b85fa122a": {
    "family": "refusal_cone",
    "original_row_sha256": "62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad",
    "qualified_receipt_sha256": "aa14d554144058963103cdf66d6f4a3e1d6e634266d37e108bbad015d5d02f4a",
    "source_sha256": "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10"
  }
}
DEPENDENCY_PINS = dict(V2_PINS, **{
    V2_MODEL: V2_BLOB, V2_REPORT: V2_REPORT_BLOB, RUNTIME_FILE: RUNTIME_BLOB})


class Refusal(ValueError):
    """Typed nontruth. A failed proof never denotes an empty finite zero set."""
    def __init__(self, reason, code="UNESTABLISHED"):
        self.code = code
        super().__init__(reason)

    def as_record(self):
        return {"status": "REFUSED", "code": self.code,
                "proof_established": False, "finite_zero_set_claimed": False,
                "reason": str(self)[:512]}


def need(condition, reason, code="UNESTABLISHED"):
    if not condition:
        raise Refusal(reason, code)


def bounded_bytes(value):
    """Preflight built-in JSON trees before serialization; aliases are refused."""
    stack = [(value, 0)]
    seen = set()
    nodes = 0
    estimate = 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        need(nodes <= MAX_NODES and depth <= MAX_DEPTH,
             "JSON node/depth budget", "RESOURCE_REFUSAL")
        if type(item) in (dict, list):
            need(id(item) not in seen, "Cyclic or aliased JSON container", "RESOURCE_REFUSAL")
            seen.add(id(item))
            need(len(item) <= 1024, "JSON container budget", "RESOURCE_REFUSAL")
            estimate += 2 + len(item) * 2
            if type(item) is dict:
                for key, child in item.items():
                    need(type(key) is str and len(key) <= 256,
                         "Exact bounded JSON key required", "RESOURCE_REFUSAL")
                    estimate += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth + 1))
            else:
                stack.extend((child, depth + 1) for child in item)
        elif type(item) is str:
            need(len(item) <= MAX_STRING, "JSON string budget", "RESOURCE_REFUSAL")
            estimate += len(json.dumps(item, ensure_ascii=True))
        elif type(item) is int:
            need(item.bit_length() <= 256, "JSON integer budget", "RESOURCE_REFUSAL")
            estimate += 80
        else:
            need(item is None or type(item) is bool,
                 "Exact JSON scalar required; floats and aliases are unsupported",
                 "RESOURCE_REFUSAL")
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


def rational(value):
    """ASCII syntax/operand bounds precede Fraction; reduced form is then checked."""
    need(type(value) is str and 0 < len(value) <= 128,
         "Bounded exact rational token required", "RESOURCE_REFUSAL")
    need(re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value, flags=re.ASCII) is not None,
         "Canonical integer/ratio syntax required", "RESOURCE_REFUSAL")
    parts = value.split("/")
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    need(numerator.bit_length() <= 256 and denominator.bit_length() <= 256,
         "Rational operand bit budget", "RESOURCE_REFUSAL")
    result = Fraction(numerator, denominator)
    need(str(result) == value, "Noncanonical rational token", "RESOURCE_REFUSAL")
    return result


def count(value, maximum=MAX_ROOTS_PER_SOURCE):
    need(type(value) is int and 0 <= value <= maximum,
         "Exact bounded nonnegative count required", "RESOURCE_REFUSAL")
    return value


def sign(value, zero=False):
    if type(value) is str:
        need(value in ("NEGATIVE", "POSITIVE") or (zero and value == "ZERO"),
             "Strict sign token required")
        return {"NEGATIVE": -1, "POSITIVE": 1, "ZERO": 0}[value]
    need(type(value) is int and value in ((-1, 0, 1) if zero else (-1, 1)),
         "Exact physical sign required")
    return value


def rational_sign(value):
    q = rational(value)
    return (q > 0) - (q < 0)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "Duplicate JSON key", "RESOURCE_REFUSAL")
        result[key] = value
    return result


def _json_integer(token):
    need(len(token) <= 79, "JSON integer token budget", "RESOURCE_REFUSAL")
    n = int(token)
    need(n.bit_length() <= 256, "JSON integer bit budget", "RESOURCE_REFUSAL")
    return n


def parse_json_bytes(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES,
         "JSON file byte budget", "RESOURCE_REFUSAL")
    def no_float(_):
        raise Refusal("Nonexact JSON number", "RESOURCE_REFUSAL")
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_int=_json_integer,
                           parse_float=no_float, parse_constant=no_float)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise Refusal("Invalid bounded JSON", "RESOURCE_REFUSAL") from error
    bounded_bytes(value)
    return value


def _read_bounded(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "File byte budget: " + str(path), "RESOURCE_REFUSAL")
    return raw


def git_blob_bytes(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "Blob byte budget", "RESOURCE_REFUSAL")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _checked_buffer(relative_path, expected_blob, limit=MAX_BYTES):
    need(relative_path in DEPENDENCY_PINS and DEPENDENCY_PINS[relative_path] == expected_blob,
         "Unregistered checked-buffer path", "UNSUPPORTED_SOURCE")
    path = ROOT / relative_path
    need(path.resolve() == path.absolute(), "Pinned path is a symlink alias")
    raw = _read_bounded(path, limit)
    need(git_blob_bytes(raw) == expected_blob, "Pinned buffer Git blob mismatch: " + relative_path)
    return raw


def qualified_v2_module():
    """Direct compilation of the same bounded verified source buffer, no cache."""
    raw = _checked_buffer(V2_MODEL, V2_BLOB, MAX_CODE_BYTES)
    module = types.ModuleType("_qualified_pb00701_v2_" + V2_BLOB)
    module.__file__ = str(ROOT / V2_MODEL)
    exec(compile(raw, module.__file__, "exec", dont_inherit=True, optimize=0), module.__dict__)
    need(module.RUNTIME_GIT_BLOB == RUNTIME_BLOB and module.RUNTIME_FILE == RUNTIME_FILE,
         "Qualified runtime identity drift")
    need(module.PINS == V2_PINS, "Qualified dependency manifest drift")
    return module


def source_metadata(row):
    bounded_bytes(row)
    need(type(row) is dict and type(row.get("id")) is str and row["id"] in SOURCES,
         "Original source is outside the finite allowlist", "UNSUPPORTED_SOURCE")
    cid = row["id"]
    admitted = SOURCES[cid]
    need(type(row.get("spec")) is dict, "Original source spec is missing")
    spec = row["spec"]
    need(digest(spec) == admitted["source_sha256"] and
         digest(row) == admitted["original_row_sha256"], "Original source or whole-row identity changed")
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    need(lo < hi, "Original source interval is empty")
    edges = {lo, hi}
    for channel in ("cos_splines", "sin_splines"):
        for spline in spec[channel].values():
            edges.update(rational(x) for x in spline["knots"])
    edges = sorted(edges)
    need(edges[0] == lo and edges[-1] == hi and
         1 <= len(edges)-1 <= MAX_ORIGINAL_PIECES, "Original piece scope exceeded", "RESOURCE_REFUSAL")
    for key in ("phase_turn_offset", "phase_turn_rate"):
        rational(spec[key])
    return {
        "case_id": cid, "origin": row["origin"], "provenance_kind": row["kind"],
        "source_sha256": admitted["source_sha256"],
        "original_row_sha256": admitted["original_row_sha256"],
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
        "phase_turn_law": {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]},
        "original_source_piece_edges": [str(x) for x in edges],
        "historical_v54_disposition": row["expected"]["v54_disposition"],
    }


def _bind_receipt(case_id, original, receipt):
    meta = source_metadata(original)
    bounded_bytes(receipt)
    need(type(case_id) is str and case_id == meta["case_id"], "Source ID does not bind original")
    admitted = SOURCES[case_id]
    need(digest(receipt) == admitted["qualified_receipt_sha256"],
         "Fresh receipt differs from the qualified original-source receipt")
    need(receipt["producer"] == admitted["family"] and
         receipt["level"] == "COMPLETE_SOURCE_SPECIFIC" and
         receipt["complete_original_source_zero_set"] is True,
         "Complete original-source proof is missing")
    for field in ("source_sha256", "original_row_sha256", "source_parameter_id",
                  "source_interval", "phase_turn_law", "original_source_piece_edges"):
        need(bounded_bytes(receipt[field]) == bounded_bytes(meta[field]),
             "Original receipt binding mismatch: " + field)
    need(receipt["covered_original_source_interval"] == meta["source_interval"] and
         meta["historical_v54_disposition"] in ("BLOCKED", ORDER_GAP),
         "Partial or historically certified source cannot enter this population")
    code_path = TASK_DIR + receipt["producer_code"]
    need(code_path in V2_PINS and V2_PINS[code_path] == receipt["producer_git_blob"],
         "Producer code identity is not in the qualified closure")
    return meta


def replay_qualified_sources():
    """Fresh no-caller-input proof context; saved records never replace replay."""
    try:
        saved = parse_json_bytes(_checked_buffer(V2_REPORT, V2_REPORT_BLOB))
        auxiliary = {}
        for key, (path, blob) in AUX_PINS.items():
            raw = _checked_buffer(path, blob)
            auxiliary[key] = {"path": path, "git_blob": blob,
                              "report": parse_json_bytes(raw)}
        module = qualified_v2_module()
        actual = module.replay_sources()
        # The qualified module's bounded serializer safely copies its trusted
        # data graph into trees before the consumer's stricter alias policy.
        copied = {key: json.loads(module.bounded_bytes(actual[key]))
                  for key in ("indexed", "prior", "receipts", "views", "runtime_attestation")}
        v2_report = json.loads(module.bounded_bytes(module.report_from_replay(actual)))
        need(bounded_bytes(v2_report) == bounded_bytes(saved),
             "Fresh qualified v2 replay differs from its pinned saved report")
        need(set(copied["receipts"]) == set(SOURCES) == set(copied["views"]),
             "Fresh source population differs from the exact fifty IDs")
        snapshot = copied["runtime_attestation"]
        observed = {entry["path"]: entry["git_blob"] for entry in snapshot["snapshots"]}
        need(observed == V2_PINS, "Fresh snapshot is not the qualified dependency closure")
        for key, aux in auxiliary.items():
            path = aux["path"]
            need(observed[path] == aux["git_blob"] and
                 type(snapshot["read_counts"].get(path)) is int and
                 snapshot["read_counts"][path] > 0,
                 "Auxiliary record was not consumed by the actual fresh producer")
            aux["replayed_read_count"] = snapshot["read_counts"][path]
        copied.update(auxiliary=auxiliary, v2_report=v2_report,
                      v2_report_sha256=digest(v2_report))
        return copied
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Actual qualified replay exhausted its resources", "RESOURCE_REFUSAL") from error
    except Exception as error:
        raise Refusal("Actual qualified replay failed: " + type(error).__name__ + ": " + str(error)[:200]) from error


def _event(coordinate, location, order, left, right, path, piece=None):
    return {"coordinate": coordinate, "location": location, "order": order,
            "left_sign": None if left is None else sign(left),
            "right_sign": None if right is None else sign(right),
            "source_piece_index": piece, "proof_path": path}


def _rational_event(value, location, order, left, right, path, piece=None):
    rational(value)
    return _event({"kind": "RATIONAL", "value": value}, location, order,
                  left, right, path, piece)


def _implicit_event(bracket, order, left, right, path, piece):
    need(type(bracket) is list and len(bracket) == 2, "Strict open bracket required")
    a, b = map(rational, bracket)
    need(a < b, "Empty implicit bracket")
    return _event({"kind": "IMPLICIT_STRICT_OPEN", "lower": bracket[0],
                   "upper": bracket[1], "unique": True}, "SPAN_INTERIOR",
                  {"kind": "SMOOTH", "value": order}, left, right, path, piece)


def _point(coordinate, value_sign, path, evidence, inward=None):
    rational(coordinate)
    value_sign = sign(value_sign, zero=True)
    need(inward is not None or value_sign != 0, "Zero exterior needs its one-sided sign")
    return {"coordinate": coordinate, "value_sign": value_sign,
            "is_zero": value_sign == 0,
            "inward_sign": sign(value_sign if inward is None else inward),
            "proof_path": path, "evidence": clone(evidence)}


def _knot(coordinate, value_sign, left, right, path, evidence):
    rational(coordinate)
    value_sign = sign(value_sign, zero=True)
    return {"coordinate": coordinate, "value_sign": value_sign,
            "is_zero": value_sign == 0, "left_sign": sign(left),
            "right_sign": sign(right), "continuous": True,
            "proof_path": path, "evidence": clone(evidence)}


def _piece_of(bracket, meta):
    a, b = map(rational, bracket)
    edges = list(map(rational, meta["original_source_piece_edges"]))
    matches = [i for i in range(len(edges)-1) if edges[i] <= a < b <= edges[i+1]]
    need(len(matches) == 1, "Root bracket crosses or misses original source pieces")
    return matches[0]


def _finite(events, endpoints, knots, closed, opened, spans, signs, field):
    return {"kind": "FINITE", "events": events, "endpoints": endpoints, "knots": knots,
            "closed_count": closed, "source_open_count": opened,
            "span_open_counts": spans, "cell_signs": [sign(x) for x in signs],
            "complete": True, "proof_cuts_event_neutral": True, "event_field": field}


def _aux_report(key, auxiliary):
    need(type(auxiliary) is dict and key in auxiliary, "Missing replayed auxiliary producer record")
    aux = auxiliary[key]
    bounded_bytes(aux)
    path, blob = AUX_PINS[key]
    need(aux["path"] == path and aux["git_blob"] == blob and
         type(aux.get("replayed_read_count")) is int and aux["replayed_read_count"] > 0,
         "Auxiliary record detached from its fresh runtime read")
    # JSON formatting is fixed by this existing qualified report's exact bytes.
    # Its decoded value is pinned independently of caller-supplied aux metadata.
    need(digest(aux["report"]) == AUX_VALUE_SHA256[key],
         "Auxiliary proof data changed after the checked-buffer read")
    return aux["report"]


AUX_VALUE_SHA256 = {'V27_THREE': '2686463ac3a25c2dddb57f66c138900af1c268cfdcadb29a398ad8fb2f061395',
 'V6_KNOT': '103fa1fbeaec918adaba5fe33197dadb684bb5efd17205ff4365e918a7145b71',
 'V9_V43': 'ef3515469b368d700e74e14726abde99ef65a35f9b4cb028a200c2cfdb7a365b'}


def _five(meta, view, auxiliary):
    cid = meta["case_id"]
    key = view["producer"]
    need(key in AUX_PINS, "Unknown five-source subproducer")
    report = _aux_report(key, auxiliary)
    events, endpoints, knots = [], [], []
    if key == "V27_THREE":
        need(cid in report["sources"], "Auxiliary source identity mismatch")
        entry = report["sources"][cid]
        need(entry["original_source_sha256"] == meta["source_sha256"], "Auxiliary source hash mismatch")
        proof = entry["physical_event_proof"]
        projection = []
        for i, raw in enumerate(proof["events"]):
            if raw["location"] == "SOURCE_LEFT_ENDPOINT":
                order = {"kind": "ONE_SIDED", "side": "RIGHT", "value": raw["one_sided_order"]}
                e = _rational_event(raw["t"], "SOURCE_LEFT_ENDPOINT", order, None,
                                    raw["right_sign"], f"events[{i}]")
                normalized_order = {"kind": "ONE_SIDED", "right": raw["one_sided_order"]}
                classification = "BOUNDARY"
            else:
                need(raw["location"] == "SPAN_OPEN", "Unsupported auxiliary event location")
                t = rational(raw["t"])
                edges = list(map(rational, meta["original_source_piece_edges"]))
                pieces = [j for j in range(len(edges)-1) if edges[j] < t < edges[j+1]]
                need(len(pieces) == 1, "Auxiliary rational root is not span-open")
                e = _rational_event(raw["t"], "SPAN_INTERIOR",
                                    {"kind": "SMOOTH", "value": raw["order"]},
                                    raw["left_sign"], raw["right_sign"],
                                    f"events[{i}]", pieces[0])
                normalized_order = {"kind": "INTEGER", "value": raw["order"]}
                classification = raw["kind"]
            events.append(e)
            projection.append({"coordinate": {"kind": "RATIONAL", "value": raw["t"]},
                "location": raw["location"], "classification": classification,
                "order": normalized_order, "left_sign": raw.get("left_sign"),
                "right_sign": raw["right_sign"]})
        values = proof["source_endpoint_values"]
        for i, coordinate in enumerate(meta["source_interval"]):
            value = values[coordinate]
            if value == "1+sqrt(2)/2":
                need(cid == "harvested:verify_pb00701_v9:1a5fd052a155" and coordinate == "1",
                     "Unregistered exact radical endpoint expression")
                value_sign, basis = 1, {"exact_value": value, "strict_rational_lower_bound": "1"}
            else:
                value_sign, basis = rational_sign(value), {"exact_value": value}
            inward = events[0]["right_sign"] if value_sign == 0 and i == 0 else None
            endpoints.append(_point(coordinate, value_sign, "physical_event_proof.source_endpoint_values",
                                    basis, inward))
        if len(meta["original_source_piece_edges"]) == 3:
            k = proof["source_knot"]
            need(k["zero"] is False and rational_sign(k["value"]) != 0,
                 "Unproved auxiliary nonzero knot")
            ks = rational_sign(k["value"])
            knots.append(_knot(k["t"], ks, ks, ks, "physical_event_proof.source_knot", k))
        closed, opened = proof["closed_source_root_count"], proof["source_interior_root_count"]
        spans, signs = proof["strict_span_open_root_counts"], proof["maximal_open_signs"]
    elif key == "V6_KNOT":
        proof = report["proof"]
        need(proof["original_source_sha256"] == meta["source_sha256"] and
             proof["original_source_parameter"] == meta["source_parameter_id"] and
             proof["original_source_interval"] == meta["source_interval"],
             "Auxiliary knot source identity mismatch")
        k = proof["source_knot"]
        need(k["exact_zero"] is True and k["distinct_physical_event_count"] == 1 and
             type(k["distinct_physical_event_count"]) is int and
             k["global_smooth_multiplicity_claimed"] is False, "Knot scope inflated")
        order = {"kind": "KNOT_SIDED", "left": k["left_one_sided_vanishing_order"],
                 "right": k["right_one_sided_vanishing_order"],
                 "global_smooth_multiplicity_claimed": False}
        events.append(_rational_event(k["coordinate"], "SOURCE_KNOT", order,
                                      k["left_inward_sign"], k["right_inward_sign"], "events[0]"))
        knots.append(_knot(k["coordinate"], 0, k["left_inward_sign"], k["right_inward_sign"],
                           "proof.source_knot", k))
        for coord, field in zip(meta["source_interval"], ("at_0", "at_2")):
            value = proof["exact_exterior_values"][field]
            endpoints.append(_point(coord, rational_sign(value), "proof.exact_exterior_values",
                                    {"exact_value": value}))
        projection = [{"coordinate": {"kind": "RATIONAL", "value": k["coordinate"]},
            "location": "SOURCE_KNOT", "classification": k["event"],
            "order": {"kind": "ONE_SIDED", "left": order["left"], "right": order["right"]},
            "left_sign": k["left_inward_sign"], "right_sign": k["right_inward_sign"]}]
        closed, opened = proof["physical_root_count_closed"], proof["physical_root_count_strict_source_interior"]
        spans, signs = proof["span_open_root_counts"], proof["maximal_open_physical_signs"]
    else:
        proof = report["proof"]
        need(proof["source_case_id"] == cid and proof["source_sha256"] == meta["source_sha256"] and
             proof["original_source_parameter"] == meta["source_parameter_id"] and
             proof["interval"] == meta["source_interval"] and
             proof["phase_turn_law"] == meta["phase_turn_law"], "Auxiliary crossing source mismatch")
        e = proof["only_physical_event"]
        need(e["kind"] == "IMPLICIT_UNIQUE_SOURCE_ROOT" and
             e["algebraic_or_rational_root_claimed"] is False, "Implicit source locator changed kind")
        events.append(_implicit_event(e["strict_bracket"], e["multiplicity"], e["left_sign"],
                                      e["right_sign"], "events[0]",
                                      _piece_of(e["strict_bracket"], meta)))
        projection = [{"coordinate": {"kind": "IMPLICIT_STRICT_BRACKET",
            "lower": e["strict_bracket"][0], "upper": e["strict_bracket"][1],
            "source_root_unique_by_producer_theorem": True},
            "location": "SPAN_OPEN", "classification": "CROSSING",
            "order": {"kind": "INTEGER", "value": e["multiplicity"]},
            "left_sign": e["left_sign"], "right_sign": e["right_sign"]}]
        k = proof["true_source_knot"]
        need(k["is_physical_zero"] is False and k["is_exactly_continuous"] is True,
             "Auxiliary nonzero knot proof missing")
        knots.append(_knot(k["at"], k["source_sign"], k["source_sign"], k["source_sign"],
                           "proof.true_source_knot", k))
        for coord, field in zip(meta["source_interval"], ("at_0", "at_2")):
            value = proof["whole_source_exterior_values"][field]
            endpoints.append(_point(coord, rational_sign(value), "proof.whole_source_exterior_values",
                                    {"exact_value": value}))
        closed = opened = proof["whole_source_open_root_count"]
        spans, signs = proof["span_open_root_counts"], proof["maximal_source_sign_cells"]
    for actual, expected in ((projection, view["events"]), (closed, view["closed_root_count"]),
                             (opened, view["strict_source_open_root_count"]),
                             (spans, view["strict_span_open_root_counts"]),
                             (signs, view["maximal_open_signs"])):
        need(bounded_bytes(actual) == bounded_bytes(expected),
             "Auxiliary proof projection differs from the actual fresh five-source view")
    for point in endpoints + knots:
        path = point["proof_path"].split(".")
        if key == "V27_THREE":
            path = ["sources", cid] + path
        point["proof_origin"] = {
            "kind": "CHECKED_AUXILIARY_REPORT", "auxiliary_key": key,
            "report_path": AUX_PINS[key][0], "report_git_blob": AUX_PINS[key][1],
            "canonical_report_sha256": AUX_VALUE_SHA256[key], "field_path": path}
    return _finite(events, endpoints, knots, closed, opened, clone(spans), signs, "events")


def _point_receipt(raw, coordinate, path):
    need(raw["coordinate"] == coordinate and raw["status"] == "EXACT_NONZERO_RATIONAL_POINT" and
         type(raw["first_nonzero_derivative_order"]) is int and
         raw["first_nonzero_derivative_order"] == 0 and
         raw["exact_vanishing_derivatives"] == [] and
         sign(raw["first_nonzero_derivative_sign"]) == sign(raw["value_sign"]),
         "Exterior exact point is not a proved nonzero value")
    return _point(coordinate, raw["value_sign"], path, raw)


def _v41_exteriors(original):
    """Export the two exact values already covered by V41's closed sign zones."""
    meta = source_metadata(original)
    s = original["spec"]
    need(meta["case_id"] == V41_ID and meta["source_interval"] == ["0", "1"] and
         s["phase_turn_offset"] == "0" and s["phase_turn_rate"] == "1/4" and
         set(s["cos_splines"]) == {"1", "3"} and set(s["sin_splines"]) == {"1", "4"},
         "V41 exterior source premises changed")
    for channel in ("cos_splines", "sin_splines"):
        for spline in s[channel].values():
            need(type(spline["degree"]) is int and spline["degree"] == 1 and
                 spline["knots"] == ["0", "0", "1", "1"] and len(spline["controls"]) == 2,
                 "V41 exterior controls are not original clamped affine channels")
    # At phase0: cos1=cos3=1, sin1=sin4=0.
    # At phase1/4: cos1=cos3=0, sin1=1, sin4=0.
    left = rational(s["cos_splines"]["1"]["controls"][0]) + rational(s["cos_splines"]["3"]["controls"][0])
    right = rational(s["sin_splines"]["1"]["controls"][-1])
    need(left < 0 and right < 0, "V41 exact exteriors are not strictly negative")
    points = [_point(t, rational_sign(str(v)), "original_clamped_endpoint_controls_and_V41_closed_zones",
                     {"exact_value": str(v), "phase_turn": phase})
              for t, v, phase in (("0", left, "0"), ("1", right, "1/4"))]
    for i, point in enumerate(points):
        point["proof_origin"] = {
            "kind": "ORIGINAL_SOURCE_ENDPOINT_IDENTITY", "source_case_id": meta["case_id"],
            "source_sha256": meta["source_sha256"], "original_row_sha256": meta["original_row_sha256"],
            "lemma": "V41_CLAMPED_AFFINE_CHANNELS_AT_ZERO_AND_QUARTER_TURN",
            "source_field_paths": [["spec", "phase_turn_offset"], ["spec", "phase_turn_rate"]] +
                [["spec", channel, harmonic, "controls", i]
                 for channel, harmonic in (("cos_splines", "1"), ("cos_splines", "3"),
                                           ("sin_splines", "1"), ("sin_splines", "4"))]}
    return points


def _adapt_source(case_id, original, receipt, view, auxiliary):
    """Translate actual attested fields; an aggregate count is never an event."""
    meta = _bind_receipt(case_id, original, receipt)
    bounded_bytes(view)
    need(digest(view) == receipt["replayed_result_sha256"],
         "Actual fresh raw view digest does not match its original-source receipt")
    family = receipt["producer"]
    if family == "continuum":
        z = view["zero_set"]
        need(receipt["scope"] == "COMPLETE_CLOSED_CONTINUUM_ZERO_SET" and
             z["kind"] == CONTINUUM and z["every_closed_source_point_is_zero"] is True and
             z["isolated_root_count"] is None and z["isolated_finite_root_list_applicable"] is False and
             z["ordered_sign_cells_applicable"] is False and
             z["closed_source_interval"] == meta["source_interval"],
             "Continuum must not be replaced by an empty finite set")
        need(view["original_source_edges"] == meta["original_source_piece_edges"] and
             len(view["original_open_span_identity"]) == len(meta["original_source_piece_edges"])-1,
             "Continuum source coverage is incomplete")
        for i, span in enumerate(view["original_open_span_identity"]):
            need(span["identity_status"] == "IDENTITY_ZERO" and
                 span["source_interval"] == meta["original_source_piece_edges"][i:i+2],
                 "Continuum original span identity is missing")
        return {"kind": CONTINUUM, "interval": clone(meta["source_interval"]),
                "every_closed_source_point_is_zero": True, "isolated_root_count": None,
                "finite_event_list_applicable": False, "events": None,
                "nonzero_sign_cells_applicable": False, "maximal_nonzero_cells": None,
                "vanishing_orders_applicable": False, "complete": True,
                "event_field": "zero_set"}
    need(receipt["scope"] == "COMPLETE_FINITE_SOURCE_ZERO_SET", "Finite/continuum receipt mismatch")
    if family == "five":
        return _five(meta, view, auxiliary)
    events, endpoints, knots = [], [], []
    edges = meta["original_source_piece_edges"]
    if family == "knot":
        k = view["shared_source_knot"]
        local = k["span_local_records"]
        need(view["global_source_knot_deduplication_established"] is True and
             view["global_multispan_root_count_established"] is True and
             k["global_smooth_multiplicity_claimed"] is False and
             count(local["same_source_coordinate_root_records"]) == 2 and
             count(local["deduplicated_distinct_source_root_events"]) == 1 and
             k["coordinate"] == k["source_coordinate"],
             "The two local knot records do not establish one source event")
        need(local["left_span_right_endpoint_multiplicity"] == k["left_one_sided_order"] and
             local["right_span_left_endpoint_multiplicity"] == k["right_one_sided_order"],
             "Knot sided orders do not bind local records")
        order = {"kind": "KNOT_SIDED", "left": k["left_one_sided_order"],
                 "right": k["right_one_sided_order"], "global_smooth_multiplicity_claimed": False}
        events.append(_rational_event(k["coordinate"], "SOURCE_KNOT", order,
                                      k["left_sign"], k["right_sign"], "shared_source_knot"))
        knots.append(_knot(k["coordinate"], 0, k["left_sign"], k["right_sign"], "shared_source_knot", k))
        endpoints = [_point_receipt(view[key], t, key) for key, t in
                     zip(("left_exterior_point", "right_exterior_point"), meta["source_interval"])]
        spans = [count(p["distinct_roots_open"]) for p in view["span_local_root_summaries"]]
        need(all(x == 0 for x in spans), "Knot-only adapter lacks strict-span event descriptors")
        return _finite(events, endpoints, knots, view["global_distinct_roots_closed_source"], 1,
                       spans, [k["left_sign"], k["right_sign"]], "shared_source_knot")
    if family == "stationary":
        for i, e in enumerate(view["ordered_physical_zero_events"]):
            d = e["descriptor"]
            need(e["coordinate_kind"] == "EXACT_RATIONAL" and d["kind"] == "RATIONAL_ROOT" and
                 d["source_value"] == e["coordinate"] and d["multiplicity"] == e["multiplicity"] and
                 sign(d["left_sign"]) == sign(e["left_sign"]) and sign(d["right_sign"]) == sign(e["right_sign"]),
                 "Unsupported stationary root descriptor")
            events.append(_rational_event(e["coordinate"], "SPAN_INTERIOR",
                {"kind": "SMOOTH", "value": e["multiplicity"]}, e["left_sign"], e["right_sign"],
                f"ordered_physical_zero_events[{i}]", e["span_index"]))
        for key in ("left_physical_endpoint", "right_physical_endpoint"):
            p = view[key]
            need(type(p["multiplicity"]) is int and p["multiplicity"] == 0,
                 "Stationary exterior unexpectedly claims a zero")
            endpoints.append(_point(p["position"], sign(p["relation"]), key, p, p["inward_sign"]))
        for k in view["true_source_knots"]:
            need(k["is_physical_zero"] is False and k["left_one_sided_order"] == 0 and
                 type(k["left_one_sided_order"]) is int and k["right_one_sided_order"] == 0 and
                 type(k["right_one_sided_order"]) is int, "Stationary knot is not nonzero")
            knots.append(_knot(k["position"], k["left_inward_sign"], k["left_inward_sign"],
                               k["right_inward_sign"], "true_source_knots", k))
        n = view["distinct_open_physical_zeros"]
        return _finite(events, endpoints, knots, n, n, [sum(e["source_piece_index"] == i for e in events)
                       for i in range(len(edges)-1)],
                       [c["sign"] for c in view["maximal_open_sign_cells"]], "ordered_physical_zero_events")
    if family == "trig_fixed":
        for i, e in enumerate(view["ordered_implicit_root_events"]):
            need(e["source_case_id"] == case_id and
                 e["descriptor"] == "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_PHYSICAL_SOURCE",
                 "Implicit trigonometric event is detached from original source")
            piece = _piece_of(e["strict_bracket"], meta)
            need(e["source_span"] == edges[piece:piece+2], "Trigonometric original piece mismatch")
            events.append(_implicit_event(e["strict_bracket"], e["smooth_physical_multiplicity"],
                e["left_sign"], e["right_sign"], f"ordered_implicit_root_events[{i}]", piece))
        for k in view["true_source_knots"]:
            need(k["is_physical_zero"] is False, "Unexpected trigonometric knot zero")
            knots.append(_knot(k["position"], k["left_sign"], k["left_sign"], k["right_sign"],
                               "true_source_knots", k))
        if case_id == V41_ID:
            endpoints = _v41_exteriors(original)
        else:
            closure = receipt["supplemental_closed_endpoint_evidence"]
            need(type(closure) is dict and closure["source_case_id"] == case_id and
                 closure["source_sha256"] == meta["source_sha256"] and
                 closure["source_interval"] == meta["source_interval"] and
                 closure["old_open_root_receipt_unchanged"] is True and
                 closure["root_count_copied_from_previous_complete_label"] is False,
                 "Actual V27 closed-endpoint supplement is missing")
            for i, e in enumerate(closure["endpoints"]):
                a = rational(e["value"]["rational"])
                b = rational(e["value"]["sqrt_3_coefficient"])
                lower = rational(e["strict_positive_rational_lower_bound"])
                need(a == lower and a > 0 and b >= 0 and e["is_physical_zero"] is False and
                     sign(e["sign"]) == 1, "V27 exterior exact positive premise failed")
                point = _point(e["position"], 1, "supplemental_closed_endpoint_evidence.endpoints", e)
                point["proof_origin"] = {
                    "kind": "FRESH_V2_SOURCE_RECEIPT", "source_case_id": case_id,
                    "qualified_v2_model_git_blob": V2_BLOB,
                    "receipt_sha256": SOURCES[case_id]["qualified_receipt_sha256"],
                    "field_path": ["supplemental_closed_endpoint_evidence", "endpoints", i]}
                endpoints.append(point)
        n = view["distinct_open_roots_proved_for_this_fixed_source"]
        return _finite(events, endpoints, knots, n, n,
            [sum(e["source_piece_index"] == i for e in events) for i in range(len(edges)-1)],
            [c["sign"] for c in view["maximal_open_physical_sign_cells"]], "ordered_implicit_root_events")
    if family == "v44":
        need(view["all_proof_cuts_are_event_neutral"] is True and
             view["algebraic_cut_is_physical_event"] is False and
             view["root_count_conserved_across_proof_cells"] is True,
             "V44 proof cut was promoted to a physical zero")
        for cut in view["proof_cut_relations"]:
            need(cut["proof_cut_is_physical_event"] is False and sign(cut["physical_value_sign"]) in (-1, 1),
                 "V44 proof cut lacks its nonzero physical sign")
        p = view["physical_root"]
        events.append(_implicit_event(p["strict_isolation"], p["smooth_multiplicity"],
            p["left_sign"], p["right_sign"], "physical_root", 0))
        endpoints = [_point(t, s, "physical_endpoint_signs", {"strict_sign": s})
                     for t, s in zip(meta["source_interval"], view["physical_endpoint_signs"])]
        n = view["complete_physical_root_count"]
        return _finite(events, endpoints, [], n, n, [n], [p["left_sign"], p["right_sign"]], "physical_root")
    if family == "refusal_cone":
        lower = rational(view["strict_lower_bound"])
        need(view["sign"] == "POSITIVE_ON_CLOSED_SOURCE_SPAN" and lower > 0 and
             view["source_interval"] == meta["source_interval"],
             "Closed-source strict positivity is missing")
        endpoints = [_point(t, 1, "strict_lower_bound", {"lower_bound": str(lower)})
                     for t in meta["source_interval"]]
        return _finite([], endpoints, [], 0, 0, [0], [1], "strict_lower_bound")
    if family == "v23_bernstein":
        p = view["source_specific_proof"]
        z = p["physical_event_proof"]
        lower = p["strict_lower_bound"]
        need(z["complete_for_original_closed_source"] is True and z["continuum_zero_component"] is False and
             lower["factor"] == "t^2" and lower["valid_on_closed_interval"] == meta["source_interval"] and
             rational(lower["coefficient"]) > 0 and rational(p["left_endpoint_value"]) == 0 and
             rational(p["left_endpoint_first_derivative"]) == 0 and rational(p["left_endpoint_second_derivative"]) > 0,
             "Endpoint order-two and closed-source positivity premises missing")
        for i, e in enumerate(z["events"]):
            need(e["coordinate"]["kind"] == "RATIONAL" and e["location"] == "SOURCE_EXTERIOR_LEFT_ENDPOINT",
                 "Unsupported Bernstein exterior event")
            events.append(_rational_event(e["coordinate"]["value"], "SOURCE_LEFT_ENDPOINT",
                {"kind": "ONE_SIDED", "side": "RIGHT", "value": e["analytic_order"]},
                e["left_sign"], e["right_sign"], f"source_specific_proof.physical_event_proof.events[{i}]"))
        endpoints = [_point(meta["source_interval"][0], 0, "source_specific_proof",
                            {"value": p["left_endpoint_value"], "second_derivative": p["left_endpoint_second_derivative"]}, 1),
                     _point(meta["source_interval"][1], 1, "source_specific_proof.strict_lower_bound", lower)]
        return _finite(events, endpoints, [], z["closed_distinct_root_count"], z["open_distinct_root_count"],
                       [0], [c["sign"] for c in z["sign_cells"]], "source_specific_proof.physical_event_proof.events")
    if family == "ordered_children":
        spans = []
        for i, p in enumerate(view["original_spans"]):
            proof = p["interval_proof"]
            need(p["source_span_index"] == i and p["original_interval"] == edges[i:i+2] and
                 proof["source_interval"] == p["original_interval"] and
                 proof["status"] == "RESEARCH_ONLY_CHECKED" and proof["is_truth_value"] is True,
                 "Missing actual original span replay")
            spans.append(proof["complete_simple_root_count"])
        for i, e in enumerate(view["ordered_root_events"]):
            piece = e["source_span_index"]
            need(type(piece) is int and e["source_interval"] == edges[piece:piece+2] and
                 e["descriptor"] == "UNIQUE_SIMPLE_ZERO_OF_PINNED_ORIGINAL_SOURCE",
                 "Child root does not cover its original source piece")
            events.append(_implicit_event(e["strict_bracket"], e["smooth_multiplicity"],
                e["left_sign"], e["right_sign"], f"ordered_root_events[{i}]", piece))
        for i, t in enumerate(meta["source_interval"]):
            proof = view["original_spans"][0 if i == 0 else -1]["interval_proof"]
            s = proof["endpoint_signs"][i]
            need(sign(s) == sign(view["exterior_endpoint_signs"][i]), "Exterior child value does not bind interval proof")
            span_index = 0 if i == 0 else len(view["original_spans"])-1
            endpoints.append(_point(t, s, f"original_spans[{span_index}].interval_proof.endpoint_signs", {"strict_sign": s}))
        for k in view["true_source_knots"]:
            need(k["channel_continuous"] is True and k["is_physical_zero"] is False and
                 k["is_physical_event"] is False, "Original child knot continuity/nonzero proof missing")
            knots.append(_knot(k["position"], k["left_sign"], k["left_sign"], k["right_sign"], "true_source_knots", k))
        need(view["complete_original_source_zero_set"] is True and
             view["certificate_partition_cuts_are_not_physical_events"] is True,
             "A supplied child cannot prove whole-source completeness")
        n = view["complete_closed_root_count"]
        return _finite(events, endpoints, knots, n, n, spans,
                       [c["sign"] for c in view["maximal_open_physical_sign_cells"]], "ordered_root_events")
    if family == "exact_zero_children":
        need(view["complete_original_source_zero_set"] is True and
             view["whole_source_completeness_proof"]["entire_original_closed_interval_covered"] is True and
             [s["interval"] for s in view["source_spans"]] == [edges[i:i+2] for i in range(len(edges)-1)],
             "Exact point proof lacks whole-source coverage")
        for i, e in enumerate(view["physical_events"]):
            if e["kind"] == "EXACT_PHYSICAL_SOURCE_KNOT_ZERO":
                need(e["global_smooth_multiplicity_claimed"] is False and
                     e["exact_sided_derivatives_unequal"] is True and len(e["local_point_receipts"]) == 2,
                     "Nonsmooth knot was assigned a global smooth order")
                order = {"kind": "KNOT_SIDED", "left": e["left_one_sided_order"],
                         "right": e["right_one_sided_order"], "global_smooth_multiplicity_claimed": False}
                for j, point in enumerate(e["local_point_receipts"]):
                    need(point["coordinate"] == e["coordinate"] and
                         point["source_binding_sha256"] == view["source_spans"][j]["source_binding_sha256"] and
                         point["one_sided_order"] == order["left" if j == 0 else "right"],
                         "Knot local point receipts do not deduplicate at the original coordinate")
                location, piece = "SOURCE_KNOT", None
            else:
                need(e["kind"] == "EXACT_SMOOTH_INTERIOR_ZERO", "Unknown exact child event")
                order, location = {"kind": "SMOOTH", "value": e["smooth_multiplicity"]}, "SPAN_INTERIOR"
                t = rational(e["coordinate"])
                pieces = [j for j in range(len(edges)-1) if rational(edges[j]) < t < rational(edges[j+1])]
                need(len(pieces) == 1, "Smooth exact event is not in an original open piece")
                piece = pieces[0]
            events.append(_rational_event(e["coordinate"], location, order, e["left_sign"], e["right_sign"],
                                          f"physical_events[{i}]", piece))
        endpoints = [_point_receipt(p, t, "exterior_endpoint_receipts") for p, t in
                     zip(view["exterior_endpoint_receipts"], meta["source_interval"])]
        k = view["source_knot_receipt"]
        if k["status"] == "EXACT_SINGLE_SOURCE_KNOT_ZERO":
            need(k["global_smooth_multiplicity_claimed"] is False and count(k["physical_zero_events"]) == 1,
                 "Exact knot event scope changed")
            knots.append(_knot(k["coordinate"], 0, k["left_sign"], k["right_sign"], "source_knot_receipt", k))
        else:
            need(k["status"] == "EXACT_NONZERO_SOURCE_KNOT" and count(k["physical_zero_events"]) == 0,
                 "Exact source knot has no typed nonzero decision")
            knots.append(_knot(k["coordinate"], k["sign"], k["sign"], k["sign"], "source_knot_receipt", k))
        n = view["complete_finite_physical_event_count"]
        spans = [sum(e["source_piece_index"] == i for e in events if e["location"] == "SPAN_INTERIOR")
                 for i in range(len(edges)-1)]
        return _finite(events, endpoints, knots, n, n, spans, view["ordered_nonzero_signs"], "physical_events")
    # The remaining four families export complete finite physical_event_proof.
    p = view["source_specific_proof"]["physical_event_proof"] if family == "bernstein_sectors" else view["physical_event_proof"]
    need(p["complete_for_original_closed_source"] is True and p["continuum_zero_component"] is False and
         p["source_interval"] == meta["source_interval"], "Complete closed physical event proof missing")
    for i, e in enumerate(p["events"]):
        if family == "component_prefix":
            need(e["event_kind"] == "IMPLICIT_UNIQUE_ORIGINAL_SOURCE_ROOT" and
                 e["rational_or_algebraic_root_coordinate_claimed"] is False,
                 "Carrier event changed locator semantics")
            bracket, order = e["strict_source_bracket"], e["multiplicity"]
            left, right, piece = e["physical_sign_before"], e["physical_sign_after"], e["source_piece_index"]
        elif family == "ratio_prefix":
            c = e["coordinate"]
            need(c["kind"] == "IMPLICIT_ORIGINAL_SOURCE_ROOT" and c["source_case_id"] == case_id and
                 c["original_source_sha256"] == meta["source_sha256"] and
                 c["source_parameter_id"] == meta["source_parameter_id"] and
                 c["defining_predicate"] == "ORIGINAL_SOURCE_F_EQUALS_ZERO",
                 "Ratio implicit source binding changed")
            bracket, order = c["strict_open_isolating_interval"], e["analytic_order"]
            left, right, piece = e["left_sign"], e["right_sign"], e["source_piece_index"]
        elif family == "bernstein_sectors":
            c = e["coordinate"]
            need(c["kind"] == "IMPLICIT_ORIGINAL_SOURCE_ROOT" and
                 c["original_source_sha256"] == meta["source_sha256"] and
                 c["source_parameter_id"] == meta["source_parameter_id"] and
                 c["defining_predicate"] == "ORIGINAL_SOURCE_F_EQUALS_ZERO" and
                 c["isolating_interval_open"] is True,
                 "Sector implicit source binding changed")
            bracket, order = c["isolating_interval"], e["analytic_order"]
            left, right, piece = e["left_sign"], e["right_sign"], _piece_of(bracket, meta)
        elif family == "multiplier_tails":
            c = e["coordinate"]
            need(c["kind"] == "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE" and
                 c["source_sha256"] == meta["source_sha256"] and
                 c["source_parameter_id"] == meta["source_parameter_id"],
                 "Multiplier implicit source binding changed")
            bracket, order = c["strict_bracket"], e["smooth_physical_multiplicity"]
            left, right, piece = e["left_sign"], e["right_sign"], c["source_piece_index"]
        else:
            raise Refusal("No registered finite adapter", "UNSUPPORTED_SOURCE")
        event_prefix = "source_specific_proof." if family == "bernstein_sectors" else ""
        events.append(_implicit_event(bracket, order, left, right, f"{event_prefix}physical_event_proof.events[{i}]", piece))
    if family == "component_prefix":
        prefix, tail = view["prefix_proof"]["endpoint_values"], view["tail_proof"]["endpoint_values"]
        need(prefix[1] == tail[0], "Carrier source endpoint values are discontinuous at the knot")
        endpoints = [_point(t, rational_sign(v), path, {"exact_value": v}) for t, v, path in (
            (meta["source_interval"][0], prefix[0], "prefix_proof.endpoint_values"),
            (meta["source_interval"][1], tail[1], "tail_proof.endpoint_values"))]
        k = p["source_knot"]
        need(k["continuous"] is True and k["is_physical_event"] is False and
             k["point_value"] == prefix[1] and k["adjacent_equal_sign_cells_merged"] is True and
             p["proof_cuts_are_physical_events"] is False, "Carrier nonzero knot composition failed")
        ks = rational_sign(k["point_value"])
        need(ks == sign(k["sign"]), "Carrier knot value/sign mismatch")
        knots.append(_knot(k["at"], ks, ks, ks, "physical_event_proof.source_knot", k))
        signs = p["maximal_source_sign_cells"]
    elif family == "ratio_prefix":
        for e in p["exterior_endpoints"]:
            need(e["is_zero_event"] is False and rational_sign(e["exact_value"]) == sign(e["value_sign"]),
                 "Ratio exterior exact value/sign disagreement")
            endpoints.append(_point(e["parameter"], e["value_sign"], "physical_event_proof.exterior_endpoints", e))
        k = p["original_source_knot"]
        need(k["source_continuous"] is True and k["is_zero_event"] is False and
             k["exact_left_value"] == k["exact_right_value"] and
             rational_sign(k["exact_left_value"]) == sign(k["value_sign"]), "Ratio original knot proof failed")
        knots.append(_knot(k["parameter"], k["value_sign"], k["value_sign"], k["value_sign"],
                           "physical_event_proof.original_source_knot", k))
        for cut in p["proof_cuts"]:
            need(cut["is_zero_event"] is False and
                 rational_sign(cut["exact_source_value"]) == sign(cut["value_sign"]),
                 "Ratio pole or sign witness promoted to a zero")
        need(p["strict_ordered_root_brackets"] == [e["coordinate"]["strict_open_isolating_interval"] for e in p["events"]],
             "Ratio strict event list/order mismatch")
        signs = [c["sign"] for c in p["maximal_sign_cells"]]
    elif family == "bernstein_sectors":
        for e in p["exterior_endpoints"]:
            bound = rational(e["bound"])
            s = sign(e["sign"])
            need(e["is_zero_event"] is False and ((s == 1 and e["bound_type"] in ("LOWER", "EXACT") and bound > 0) or
                 (s == -1 and e["bound_type"] in ("UPPER", "EXACT") and bound < 0)), "Sector exterior bound does not prove strict sign")
            endpoints.append(_point(e["parameter"], s, "source_specific_proof.physical_event_proof.exterior_endpoints", e))
        for k in p["interior_source_knots"]:
            need(k["source_continuous"] is True and k["is_zero_event"] is False,
                 "Sector source knot is not proved continuous/nonzero")
            knots.append(_knot(k["parameter"], k["value_sign"], k["left_sign"], k["right_sign"],
                               "source_specific_proof.physical_event_proof.interior_source_knots", k))
        for cut in p["proof_cuts"]:
            need(cut["is_zero_event"] is False and sign(cut["value_sign"]) in (-1, 1),
                 "Sector proof cut is not event-neutral")
        signs = [c["sign"] for c in p["maximal_sign_cells"]]
    else:
        for e in p["exterior_endpoints"]:
            need(e["is_physical_zero"] is False and rational_sign(e["value"]) == sign(e["sign"]),
                 "Multiplier exterior exact value/sign disagreement")
            endpoints.append(_point(e["position"], e["sign"], "physical_event_proof.exterior_endpoints", e))
        k = p["original_source_knot"]
        need(k["channel_continuous"] is True and k["is_physical_event"] is False and
             rational_sign(k["value"]) == sign(k["left_sign"]) == sign(k["right_sign"]) and
             p["proof_cuts_and_bracket_endpoints_are_not_root_coordinates"] is True,
             "Multiplier physical knot or proof-cut semantics changed")
        knots.append(_knot(k["position"], k["left_sign"], k["left_sign"], k["right_sign"],
                           "physical_event_proof.original_source_knot", k))
        signs = [c["sign"] for c in p["maximal_open_sign_cells"]]
    n = p["closed_distinct_root_count"]
    return _finite(events, endpoints, knots, n, p.get("open_distinct_root_count", n),
        [sum(e["source_piece_index"] == i for e in events) for i in range(len(edges)-1)], signs,
        "source_specific_proof.physical_event_proof.events" if family == "bernstein_sectors" else "physical_event_proof.events")


def _resolve_path(value, components):
    need(type(components) is list and 0 < len(components) <= 16,
         "Bounded provenance path required", "RESOURCE_REFUSAL")
    for component in components:
        if type(component) is int:
            need(0 <= component <= 1024 and type(value) is list and component < len(value),
                 "Provenance list path does not resolve")
        else:
            need(type(component) is str and len(component) <= 256 and
                 type(value) is dict and component in value,
                 "Provenance object path does not resolve")
        value = value[component]
    return value


def _dot_path(path):
    need(type(path) is str and 0 < len(path) <= 2048,
         "Bounded provenance path text required", "RESOURCE_REFUSAL")
    parts = path.split(".")
    need(len(parts) <= 16, "Provenance path depth", "RESOURCE_REFUSAL")
    result = []
    for part in parts:
        match = re.fullmatch(r"([A-Za-z_][A-Za-z_0-9]*)(?:\[([0-9]{1,4})\])?", part, flags=re.ASCII)
        need(match is not None, "Unsupported provenance path syntax")
        result.append(match.group(1))
        if match.group(2) is not None:
            result.append(int(match.group(2)))
    return result


def adapt_source(case_id, original, receipt, view, auxiliary):
    semantic = _adapt_source(case_id, original, receipt, view, auxiliary)
    if semantic["kind"] == "FINITE":
        for event in semantic["events"]:
            _resolve_path(view, _dot_path(event["proof_path"]))
        for point in semantic["endpoints"] + semantic["knots"]:
            origin = point.get("proof_origin")
            if origin is None:
                _resolve_path(view, _dot_path(point["proof_path"]))
            elif origin["kind"] == "CHECKED_AUXILIARY_REPORT":
                _resolve_path(_aux_report(origin["auxiliary_key"], auxiliary), origin["field_path"])
            elif origin["kind"] == "FRESH_V2_SOURCE_RECEIPT":
                _resolve_path(receipt, origin["field_path"])
            else:
                need(origin["kind"] == "ORIGINAL_SOURCE_ENDPOINT_IDENTITY", "Unknown point provenance owner")
                for path in origin["source_field_paths"]:
                    _resolve_path(original, path)
    return semantic


def _proof_reference(receipt, path):
    return {"producer": receipt["producer"], "producer_code": receipt["producer_code"],
            "producer_git_blob": receipt["producer_git_blob"],
            "replayed_result_sha256": receipt["replayed_result_sha256"], "field_path": path}


def _point_proof(meta, receipt, point):
    origin = point.get("proof_origin")
    if origin is None:
        need(receipt["producer"] != "five", "Auxiliary point must name its actual report owner")
        proof = _proof_reference(receipt, point["proof_path"])
        proof["kind"] = "FRESH_PRODUCER_VIEW"
    else:
        proof = clone(origin)
        kind = proof["kind"]
        if kind == "CHECKED_AUXILIARY_REPORT":
            key = proof["auxiliary_key"]
            need(receipt["producer"] == "five" and key in AUX_PINS and
                 proof["report_path"] == AUX_PINS[key][0] and
                 proof["report_git_blob"] == AUX_PINS[key][1] and
                 proof["canonical_report_sha256"] == AUX_VALUE_SHA256[key],
                 "Auxiliary point reference does not bind the checked report")
            expected = point["proof_path"].split(".")
            if key == "V27_THREE":
                expected = ["sources", meta["case_id"]] + expected
            need(proof["field_path"] == expected, "Auxiliary point field path changed owner")
        elif kind == "FRESH_V2_SOURCE_RECEIPT":
            need(receipt["producer"] == "trig_fixed" and meta["case_id"] != V41_ID and
                 proof["source_case_id"] == meta["case_id"] and
                 proof["qualified_v2_model_git_blob"] == V2_BLOB and
                 proof["receipt_sha256"] == SOURCES[meta["case_id"]]["qualified_receipt_sha256"],
                 "Endpoint supplement reference is not the qualified v2 source receipt")
            _resolve_path(receipt, proof["field_path"])
        else:
            need(kind == "ORIGINAL_SOURCE_ENDPOINT_IDENTITY" and meta["case_id"] == V41_ID and
                 proof["source_case_id"] == meta["case_id"] and
                 proof["source_sha256"] == meta["source_sha256"] and
                 proof["original_row_sha256"] == meta["original_row_sha256"],
                 "Endpoint identity reference does not bind the original source")
    proof["evidence"] = clone(point["evidence"])
    return proof


def _source_record(meta, receipt, zeros, field):
    record = clone(meta)
    record.update(status="ESTABLISHED_FOR_PINNED_ORIGINAL_SOURCE",
                  evidence_class="DETERMINISTIC_MODEL",
                  producer_evidence=_proof_reference(receipt, field),
                  zero_set=zeros, historical_disposition_changed=False,
                  generic_owner_route_repaired=False, production_authorized=False)
    bounded_bytes(record)
    return record


def _order_bounds(event):
    c = event["coordinate"]
    if c["kind"] == "RATIONAL":
        q = rational(c["value"])
        return q, q, True
    return rational(c["lower"]), rational(c["upper"]), False


def _root_boundary(event):
    return {"kind": "PHYSICAL_ZERO_EVENT", "event_id": event["event_id"],
            "source_case_id": event["source_case_id"], "source_sha256": event["source_sha256"]}


def assemble_source(case_id, original, receipt, semantic):
    """Conditional composition of already attested source-specific primitives.

    This helper validates topology, parity, order, coverage and point signs.
    Calling it with invented semantic primitives cannot grant public evidence;
    public consumers always obtain those primitives from fresh pinned replay.
    """
    meta = _bind_receipt(case_id, original, receipt)
    bounded_bytes(semantic)
    need(semantic.get("complete") is True, "Incomplete source cannot be normalized")
    if semantic.get("kind") == CONTINUUM:
        need(SOURCES[case_id]["family"] == "continuum" and
             receipt["scope"] == "COMPLETE_CLOSED_CONTINUUM_ZERO_SET" and
             semantic["interval"] == meta["source_interval"] and
             semantic["every_closed_source_point_is_zero"] is True and
             semantic["isolated_root_count"] is None and
             semantic["finite_event_list_applicable"] is False and semantic["events"] is None and
             semantic["nonzero_sign_cells_applicable"] is False and semantic["maximal_nonzero_cells"] is None and
             semantic["vanishing_orders_applicable"] is False,
             "Continuum was given finite event, count, order or sign-cell semantics")
        zeros = {k: clone(v) for k, v in semantic.items() if k not in ("complete", "event_field")}
        zeros.update(complete_for_original_closed_source=True, closed_interval=True,
                     cardinality="UNCOUNTABLY_INFINITE")
        return _source_record(meta, receipt, zeros, semantic["event_field"])
    need(semantic.get("kind") == "FINITE" and SOURCES[case_id]["family"] != "continuum" and
         receipt["scope"] == "COMPLETE_FINITE_SOURCE_ZERO_SET" and
         semantic.get("proof_cuts_event_neutral") is True,
         "Finite type or event-neutral proof-cut premise missing")
    edges = list(map(rational, meta["original_source_piece_edges"]))
    lo, hi = edges[0], edges[-1]
    pieces = len(edges)-1
    raw_events = semantic["events"]
    need(type(raw_events) is list and len(raw_events) <= MAX_ROOTS_PER_SOURCE,
         "Finite source event budget exceeded", "RESOURCE_REFUSAL")
    need(count(semantic["closed_count"]) == len(raw_events), "Closed root count disagrees with event list")
    events, bounds = [], []
    per_span = [0] * pieces
    endpoint_events = {}
    knot_events = {}
    for i, e in enumerate(raw_events):
        need(type(e) is dict and set(e) == {"coordinate", "location", "order", "left_sign",
             "right_sign", "source_piece_index", "proof_path"}, "Event semantic fields changed")
        need(type(e["proof_path"]) is str and e["proof_path"], "Event lacks actual producer field path")
        c = e["coordinate"]
        need(type(c) is dict, "Exact source coordinate descriptor required")
        if c.get("kind") == "RATIONAL":
            need(set(c) == {"kind", "value"}, "Rational event is not an exact point")
            a = b = rational(c["value"])
            point = True
        else:
            need(c.get("kind") == "IMPLICIT_STRICT_OPEN" and
                 set(c) == {"kind", "lower", "upper", "unique"} and c["unique"] is True,
                 "Unsupported or nonunique implicit coordinate")
            a, b = rational(c["lower"]), rational(c["upper"])
            need(a < b, "Implicit event has an empty open bracket")
            point = False
        need(lo <= a <= b <= hi, "Physical event lies outside the original closed source")
        if bounds:
            pa, pb, pp = bounds[-1]
            need(pb < a or (pb == a and not (pp and point)),
                 "Physical zero events are not strictly ordered or are duplicated")
        bounds.append((a, b, point))
        location, order = e["location"], e["order"]
        need(type(order) is dict, "Typed vanishing order required")
        left, right = e["left_sign"], e["right_sign"]
        if location == "SPAN_INTERIOR":
            need(left is not None and right is not None, "Interior root lacks two physical signs")
            left, right = sign(left), sign(right)
            candidates = [j for j in range(pieces) if
                          (edges[j] < a < edges[j+1] if point else edges[j] <= a < b <= edges[j+1])]
            need(len(candidates) == 1 and type(e["source_piece_index"]) is int and
                 e["source_piece_index"] == candidates[0], "Root was moved across original source pieces")
            piece = candidates[0]
            need(set(order) == {"kind", "value"} and order["kind"] == "SMOOTH" and
                 1 <= count(order["value"]), "Strict-span zero needs a smooth positive integer order")
            need(right == left * (-1 if order["value"] % 2 else 1),
                 "Smooth root order parity disagrees with its physical side signs")
            per_span[piece] += 1
            source_pieces = [piece]
        elif location == "SOURCE_KNOT":
            need(point and a in edges[1:-1] and e["source_piece_index"] is None,
                 "Knot event is not one actual original source knot")
            need(left is not None and right is not None, "Knot zero lacks two inward signs")
            left, right = sign(left), sign(right)
            need(set(order) == {"kind", "left", "right", "global_smooth_multiplicity_claimed"} and
                 order["kind"] == "KNOT_SIDED" and order["global_smooth_multiplicity_claimed"] is False and
                 1 <= count(order["left"]) and 1 <= count(order["right"]),
                 "Source knot needs separate one-sided orders, without global smooth multiplicity")
            j = edges.index(a)
            need(a not in knot_events, "Two local endpoint records became two physical knot events")
            knot_events[a] = i
            source_pieces = [j-1, j]
        else:
            need(location in ("SOURCE_LEFT_ENDPOINT", "SOURCE_RIGHT_ENDPOINT") and
                 point and e["source_piece_index"] is None, "Unknown physical event location")
            side = "LEFT" if location == "SOURCE_LEFT_ENDPOINT" else "RIGHT"
            need(a == (lo if side == "LEFT" else hi) and side not in endpoint_events,
                 "Exterior event does not bind the original exterior point")
            need(set(order) == {"kind", "side", "value"} and order["kind"] == "ONE_SIDED" and
                 order["side"] == ("RIGHT" if side == "LEFT" else "LEFT") and 1 <= count(order["value"]),
                 "Exterior zero needs an inward one-sided order")
            if side == "LEFT":
                need(left is None and right is not None, "Left exterior has a fabricated outside sign")
                right = sign(right)
            else:
                need(right is None and left is not None, "Right exterior has a fabricated outside sign")
                left = sign(left)
            endpoint_events[side] = i
            source_pieces = [0 if side == "LEFT" else pieces-1]
        normalized_order = clone(order)
        if location.startswith("SOURCE_") and location.endswith("_ENDPOINT"):
            normalized_order.update(outside_order=None, global_smooth_multiplicity_claimed=False)
        coordinate = clone(c) if point else {
            "kind": "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE",
            "source_case_id": case_id, "source_sha256": meta["source_sha256"],
            "source_parameter_id": meta["source_parameter_id"], "source_piece_index": source_pieces[0],
            "source_span": meta["original_source_piece_edges"][source_pieces[0]:source_pieces[0]+2],
            "strict_open_bracket": [c["lower"], c["upper"]],
            "defining_predicate": "ORIGINAL_SOURCE_F_EQUALS_ZERO",
            "uniqueness_evidence": _proof_reference(receipt, e["proof_path"]),
            "exact_algebraic_root_coordinate_claimed": False}
        normalized = {
            "event_id": "ROOT_" + str(i), "source_case_id": case_id,
            "source_sha256": meta["source_sha256"], "coordinate": coordinate,
            "location": location, "source_piece_indices": source_pieces,
            "classification": "BOUNDARY" if left is None or right is None else
                              ("CROSSING" if left != right else "TOUCHING"),
            "order": normalized_order, "left_sign": left, "right_sign": right,
            "proof_path": e["proof_path"]}
        events.append(normalized)
    source_open_count = len(events)-len(endpoint_events)
    need(count(semantic["source_open_count"]) == source_open_count,
         "Whole-source open root count must include knot zeros and exclude exterior zeros")
    need(type(semantic["span_open_counts"]) is list and len(semantic["span_open_counts"]) == pieces and
         [count(x) for x in semantic["span_open_counts"]] == per_span,
         "Original strict-span root counts disagree with physical events")
    need(type(semantic["endpoints"]) is list and len(semantic["endpoints"]) == 2,
         "Both original closed exteriors need explicit point evidence")
    endpoints = []
    for side, q, raw in zip(("LEFT", "RIGHT"), (lo, hi), semantic["endpoints"]):
        need(rational(raw["coordinate"]) == q, "Exterior point evidence has the wrong original coordinate")
        s = sign(raw["value_sign"], zero=True)
        inward = sign(raw["inward_sign"])
        need(raw["is_zero"] is (s == 0), "Exterior zero flag disagrees with its proved value")
        if s == 0:
            need(side in endpoint_events, "Exterior zero was omitted from the complete event list")
            event = events[endpoint_events[side]]
            need(inward == event["right_sign" if side == "LEFT" else "left_sign"],
                 "Exterior inward sign disagrees with its event")
            event_ref = event["event_id"]
        else:
            need(side not in endpoint_events and inward == s,
                 "Nonzero exterior was counted as a root or has an inconsistent inward sign")
            event_ref = None
        endpoints.append({"side": side, "coordinate": str(q), "value_sign": s,
                          "is_zero": s == 0, "inward_sign": inward,
                          "outside_sign": None, "outside_order": None, "event_ref": event_ref,
                          "proof": _point_proof(meta, receipt, raw)})
    need(type(semantic["knots"]) is list and len(semantic["knots"]) == pieces-1,
         "True original knot coverage is incomplete or includes artificial proof cuts")
    knots = []
    for j, (q, raw) in enumerate(zip(edges[1:-1], semantic["knots"]), 1):
        need(rational(raw["coordinate"]) == q and raw["continuous"] is True,
             "True knot coordinate or original continuity premise failed")
        value, left, right = sign(raw["value_sign"], zero=True), sign(raw["left_sign"]), sign(raw["right_sign"])
        need(raw["is_zero"] is (value == 0), "Knot zero flag disagrees with its value evidence")
        if value == 0:
            need(q in knot_events, "A zero knot has no deduplicated physical event")
            event = events[knot_events[q]]
            need(event["left_sign"] == left and event["right_sign"] == right,
                 "Knot event signs disagree with local source sides")
            event_ref = event["event_id"]
        else:
            need(q not in knot_events and value == left == right,
                 "A nonzero continuous knot must have equal strict side signs")
            event_ref = None
        knots.append({"coordinate": str(q), "source_piece_indices": [j-1, j],
                      "value_sign": value, "is_zero": value == 0,
                      "left_sign": left, "right_sign": right, "continuous": True,
                      "event_ref": event_ref, "global_smooth_multiplicity_claimed": False,
                      "proof": _point_proof(meta, receipt, raw)})
    # Partition only at physical zeros. Bracket bounds and nonzero knots never
    # enter this boundary list, and equal signs across a touch do not merge.
    interior = [e for e in events if e["location"] in ("SPAN_INTERIOR", "SOURCE_KNOT")]
    left_event = events[endpoint_events["LEFT"]] if "LEFT" in endpoint_events else None
    right_event = events[endpoint_events["RIGHT"]] if "RIGHT" in endpoint_events else None
    left_boundary = _root_boundary(left_event) if left_event else {
        "kind": "SOURCE_EXTERIOR", "side": "LEFT", "coordinate": str(lo)}
    right_boundary = _root_boundary(right_event) if right_event else {
        "kind": "SOURCE_EXTERIOR", "side": "RIGHT", "coordinate": str(hi)}
    current_sign = endpoints[0]["inward_sign"]
    cells = []
    for i in range(len(interior)+1):
        left_event = interior[i-1] if i else None
        right_event = interior[i] if i < len(interior) else None
        lb = _root_boundary(left_event) if left_event else clone(left_boundary)
        rb = _root_boundary(right_event) if right_event else clone(right_boundary)
        if right_event is not None:
            need(right_event["left_sign"] == current_sign, "Consecutive event side signs are inconsistent")
        else:
            need(endpoints[1]["inward_sign"] == current_sign, "Final cell sign disagrees with closed exterior evidence")
        first_piece = (left_event["source_piece_indices"][-1] if left_event else 0)
        last_piece = (right_event["source_piece_indices"][0] if right_event else pieces-1)
        need(first_piece <= last_piece, "Physical cell is empty or reverses original source pieces")
        crossed = []
        for j in range(first_piece+1, last_piece+1):
            knot = knots[j-1]
            need(knot["is_zero"] is False and knot["value_sign"] == current_sign,
                 "A cell crossed a zero knot or contradicted its nonzero value")
            crossed.append(knot["coordinate"])
        cells.append({"cell_id": "CELL_" + str(i), "left_boundary": lb, "right_boundary": rb,
                      "left_included": i == 0 and endpoints[0]["is_zero"] is False,
                      "right_included": i == len(interior) and endpoints[1]["is_zero"] is False,
                      "sign": current_sign, "source_piece_indices": list(range(first_piece, last_piece+1)),
                      "crossed_nonzero_source_knots": crossed})
        if right_event is not None:
            current_sign = right_event["right_sign"]
    need(type(semantic["cell_signs"]) is list and
         [sign(x) for x in semantic["cell_signs"]] == [cell["sign"] for cell in cells],
         "Maximal connected nonzero cells disagree with the actual proof sign sequence")
    need(len(cells) == 1+source_open_count, "Connected nonzero component count failed")
    zeros = {"kind": FINITE, "complete_for_original_closed_source": True,
             "finite_event_list_applicable": True, "nonzero_sign_cells_applicable": True,
             "isolated_root_count": len(events), "source_open_root_count": source_open_count,
             "strict_span_open_root_counts": per_span, "events": events,
             "exterior_points": endpoints, "true_source_knots": knots,
             "maximal_nonzero_cells": cells,
             "nonzero_knots_and_proof_cuts_are_not_partition_boundaries": True,
             "global_cross_source_zero_deduplication_performed": False}
    return _source_record(meta, receipt, zeros, semantic["event_field"])


def _normalized_cases(replay):
    need(type(replay) is dict and set(replay["receipts"]) == set(SOURCES) == set(replay["views"]),
         "Incomplete or substituted fifty-source replay context")
    records = []
    for cid in sorted(SOURCES):
        original, receipt, view = replay["indexed"][cid], replay["receipts"][cid], replay["views"][cid]
        semantic = adapt_source(cid, original, receipt, view, replay["auxiliary"])
        records.append(assemble_source(cid, original, receipt, semantic))
    return records


def replay_sources():
    """Data-only fresh originals, proof receipts/views and normalized records.

    This no-input context is available to a separately reviewed dependent leaf;
    it neither refines roots nor accepts caller supplied source or proof inputs.
    """
    context = replay_qualified_sources()
    context["normalized_source_cases"] = _normalized_cases(context)
    return context


def report_from_replay(replay):
    """Internal formatter; all source bindings and semantic assemblies rechecked."""
    sources = _normalized_cases(replay)
    if "normalized_source_cases" in replay:
        need(bounded_bytes(sources) == bounded_bytes(replay["normalized_source_cases"]),
             "Fresh context normalized records changed after assembly")
    v2 = replay["v2_report"]
    need(digest(v2) == replay["v2_report_sha256"] == V2_REPORT_VALUE_SHA256 and
         len(v2["source_cases"]) == 50 and
         {r["case_id"] for r in v2["source_cases"]} == set(SOURCES),
         "Qualified census context identity changed")
    need(bounded_bytes(replay["runtime_attestation"]) ==
         bounded_bytes(v2["executed_byte_custody"]["snapshot"]),
         "Fresh runtime attestation detached from qualified replay")
    need(set(replay["auxiliary"]) == set(AUX_PINS), "Auxiliary producer set changed")
    for key, aux in replay["auxiliary"].items():
        _aux_report(key, replay["auxiliary"])
        need(aux["replayed_read_count"] == replay["runtime_attestation"]["read_counts"][aux["path"]],
             "Auxiliary runtime read count changed after replay")
    finite = [s for s in sources if s["zero_set"]["kind"] == FINITE]
    continuum = [s for s in sources if s["zero_set"]["kind"] == CONTINUUM]
    all_events = [e for s in finite for e in s["zero_set"]["events"]]
    locations = Counter(e["location"] for e in all_events)
    coordinate_kinds = Counter(e["coordinate"]["kind"] for e in all_events)
    summary = {
        "original_source_count": len(sources), "finite_source_count": len(finite),
        "continuum_source_count": len(continuum),
        "producer_family_count": len({s["producer_evidence"]["producer"] for s in sources}),
        "sum_of_per_source_distinct_isolated_zeros": len(all_events),
        "rational_zero_coordinates": coordinate_kinds["RATIONAL"],
        "implicit_original_source_zero_locators": coordinate_kinds["UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE"],
        "source_exterior_zero_events": locations["SOURCE_LEFT_ENDPOINT"]+locations["SOURCE_RIGHT_ENDPOINT"],
        "true_source_knot_zero_events": locations["SOURCE_KNOT"],
        "strict_span_interior_zero_events": locations["SPAN_INTERIOR"],
        "finite_root_free_sources": sum(s["zero_set"]["isolated_root_count"] == 0 for s in finite),
        "maximal_connected_nonzero_cells": sum(len(s["zero_set"]["maximal_nonzero_cells"]) for s in finite),
        "nonzero_original_source_knots": sum(not k["is_zero"] for s in finite for k in s["zero_set"]["true_source_knots"]),
        "nonzero_finite_exterior_points": sum(not e["is_zero"] for s in finite for e in s["zero_set"]["exterior_points"]),
    }
    need(len(finite) == 49 and len(continuum) == 1 and summary["producer_family_count"] == 14,
         "Finite/continuum exact population changed")
    auxiliary_receipts = [{key: clone(aux[key]) for key in ("path", "git_blob", "replayed_read_count")}
                          for _, aux in sorted(replay["auxiliary"].items())]
    result = {
        "schema": SCHEMA, "status": "FINITE_ORIGINAL_SOURCE_ZERO_SETS_NORMALIZED_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL", "qualified_base_main": BASE_MAIN,
        "qualified_v2": {"model": V2_MODEL, "model_git_blob": V2_BLOB,
                         "report": V2_REPORT, "report_git_blob": V2_REPORT_BLOB,
                         "fresh_report_sha256": replay["v2_report_sha256"],
                         "runtime": RUNTIME_FILE, "runtime_git_blob": RUNTIME_BLOB},
        "executed_byte_custody": {
            "v2_wrapper_compiled_from_same_bounded_verified_buffer": True,
            "qualified_v2_actual_replay_executed": True,
            "each_raw_view_digest_equals_its_fresh_source_receipt": True,
            "fresh_report_canonically_equals_pinned_v2_report": True,
            "auxiliary_endpoint_records_consumed_by_actual_five_producers": auxiliary_receipts,
            "v2_runtime_snapshot_manifest_sha256": replay["runtime_attestation"]["snapshot_manifest_sha256"],
            "dependency_path_count": len(DEPENDENCY_PINS),
            "python_and_standard_library_trusted": True, "hostile_python_sandbox_claimed": False},
        "scope": {
            "exact_historical_unresolved_source_allowlist": 50,
            "maximum_isolated_roots_per_source": MAX_ROOTS_PER_SOURCE,
            "maximum_original_pieces_per_source": MAX_ORIGINAL_PIECES,
            "all_coordinates_use_original_source_parameter": True,
            "sum_of_per_source_zeros_is_not_a_union_of_parameter_values_across_sources": True,
            "implicit_locators_are_not_algebraic_or_rational_root_coordinate_claims": True,
            "zero_touches_separate_connected_nonzero_components": True,
            "continuum_has_no_isolated_event_list_or_nonzero_sign_cells": True,
            "arbitrary_source_root_arithmetic": False, "discontinuity_policy_established": False,
            "generic_owner_routes_repaired": False, "universal_event_interface_established": False,
            "root_refinement_implemented": False},
        "summary": summary, "by_producer_family": dict(sorted(Counter(
            s["producer_evidence"]["producer"] for s in sources).items())),
        "source_cases": sources, "historical_v54": clone(v2["historical_v54"]),
        "gates": clone(v2["gates"])}
    bounded_bytes(result)
    return result


def expected_report():
    try:
        return report_from_replay(replay_sources())
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Source normalization exhausted its bounded resources", "RESOURCE_REFUSAL") from error
    except Exception as error:
        raise Refusal("Source normalization failed: " + type(error).__name__ + ": " + str(error)[:200]) from error


def consume_original_source(case_id):
    """Return one admitted normalized source, or explicit typed nontruth."""
    try:
        need(type(case_id) is str and len(case_id) <= 256,
             "Exact bounded source ID required", "RESOURCE_REFUSAL")
        need(case_id in SOURCES, "No qualified original-source proof for this ID", "UNSUPPORTED_SOURCE")
        context = replay_sources()
        selected = [r for r in context["normalized_source_cases"] if r["case_id"] == case_id]
        need(len(selected) == 1, "Admitted source was lost after fresh normalization")
        return clone(selected[0])
    except Refusal as error:
        return error.as_record()
    except (MemoryError, RecursionError):
        return Refusal("Source proof exhausted resources", "RESOURCE_REFUSAL").as_record()
    except Exception as error:
        return Refusal("Source proof failed: " + type(error).__name__ + ": " + str(error)[:200]).as_record()


def read_report(path=REPORT):
    need(type(path) in (str, type(REPORT)), "Report path must be an exact path or string", "RESOURCE_REFUSAL")
    text = str(path)
    need(0 < len(text) <= 4096 and "\0" not in text,
         "Report path text budget or syntax", "RESOURCE_REFUSAL")
    try:
        return parse_json_bytes(_read_bounded(Path(text), MAX_BYTES))
    except OSError as error:
        raise Refusal("Unable to read bounded report file") from error


def _compare_with_replayed_bytes(candidate, expected_bytes):
    need(type(expected_bytes) is bytes and len(expected_bytes) <= MAX_BYTES,
         "Bounded expected report bytes required", "RESOURCE_REFUSAL")
    need(bounded_bytes(candidate) == expected_bytes,
         "Submitted report differs from freshly established original-source zero sets")
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
    report = expected_report()
    if options.write_report:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if options.contract:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(report))
        print("PASS: 50 original sources normalized from fresh qualified proof fields")
        print(json.dumps(report["summary"], sort_keys=True))
        print("PASS: historical 121/20/30, all 26 operations and all gates preserved")


if __name__ == "__main__":
    main()

