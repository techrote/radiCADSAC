#!/usr/bin/env python3
"""Bounded refinement of already proved implicit original-source zeros.

Public operations always execute the qualified fifty-source consumer. The
coefficient/point/bracket helpers establish conditional numerical facts only;
none admit caller sources or establish a new uniqueness/completeness theorem.
"""
from __future__ import annotations

import argparse
from collections import Counter, namedtuple
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
BASE_MAIN = "828df02d3d61b57bd46b0c4a796ce58685d9c987"
SCHEMA = "radicadsac-mc038-selected-implicit-root-refinement/1.0"
REPORT = HERE / "pb00701-selected-implicit-root-refinement.json"
PARENT_MODEL = TASK_DIR + "pb00701_fifty_source_zero_set_consumer.py"
PARENT_MODEL_BLOB = "d5eef89ab168a2acc2588f13a6d87ab88b998d40"
PARENT_REPORT = TASK_DIR + "pb00701-fifty-source-zero-set-consumer.json"
PARENT_REPORT_BLOB = "8213026ed2a5205d2cfff44e45c26e89deab4ee9"
PARENT_REPORT_VALUE_SHA256 = "9703c8222f04ce231613bdd4585724f08401a83c2618ab01a362ba71cd57168f"
TRIG_FILE = TASK_DIR + "pb00701_transverse_trig_interval.py"
TRIG_BLOB = "2320f92efe4316d865a89f6d848737e2c000ca4d"
CORPUS_FILE = TASK_DIR + "pb00701-finite-owner-corpus-v54.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
PARENT_PINS = {'handoffs/current-authority.json': 'fa0233323a0804d8a5d3eb7cd892a274a6173fab',
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
PINS = dict(PARENT_PINS, **{PARENT_MODEL: PARENT_MODEL_BLOB, PARENT_REPORT: PARENT_REPORT_BLOB})
DIRECT_INPUTS = {'research/machining-completeness/tasks/MC-038/pb00701-fifty-source-zero-set-consumer.json': {'bytes': 485348,
                                                                                              'git_blob': '8213026ed2a5205d2cfff44e45c26e89deab4ee9',
                                                                                              'path': 'research/machining-completeness/tasks/MC-038/pb00701-fifty-source-zero-set-consumer.json',
                                                                                              'sha256': '1191087a92ac4ac1618b1ce2580953d8db1a685f49e1bf0fb680c94b12515773'},
 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json': {'bytes': 228334,
                                                                                       'git_blob': '5841c331579489b25caef38cd412bdbf286f9134',
                                                                                       'path': 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json',
                                                                                       'sha256': '6ebe84ecc946c47d2878551dece7df37eb3041701574dfcb22e1666859d1697f'},
 'research/machining-completeness/tasks/MC-038/pb00701_fifty_source_zero_set_consumer.py': {'bytes': 117355,
                                                                                            'git_blob': 'd5eef89ab168a2acc2588f13a6d87ab88b998d40',
                                                                                            'path': 'research/machining-completeness/tasks/MC-038/pb00701_fifty_source_zero_set_consumer.py',
                                                                                            'sha256': '3658ac2de2c80aaab23fc1c4b5a650035ed156d8281591295ec6d0d16b88aa67'},
 'research/machining-completeness/tasks/MC-038/pb00701_transverse_trig_interval.py': {'bytes': 10617,
                                                                                      'git_blob': '2320f92efe4316d865a89f6d848737e2c000ca4d',
                                                                                      'path': 'research/machining-completeness/tasks/MC-038/pb00701_transverse_trig_interval.py',
                                                                                      'sha256': 'd3db869d05ee4b2b531a14c85d652ecc9b2fedb5faaf303d3e47691383560ca9'}}
MAX_BYTES = 2 * 1024 * 1024
MAX_CODE_BYTES = 256 * 1024
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 8192
MAX_INPUT_BITS = 128
MAX_RECEIPT_BITS = 256
MAX_INTERMEDIATE_BITS = 65536
MAX_PHASE_BITS = 512
MAX_DEGREE = 7
MAX_CONTROLS = 16
MAX_KNOTS = 24
MAX_CHANNELS = 16
MAX_HARMONIC = 7
MAX_STEPS = 12
DYADIC_BITS = 80
DYADIC_SCALE = 1 << DYADIC_BITS
_FractionType = Fraction
ZERO, ONE, TWO = Fraction(0), Fraction(1), Fraction(2)

PreparedSpline = namedtuple("PreparedSpline", "degree knots controls left right")
PreparedChannel = namedtuple("PreparedChannel", "kind harmonic spline")
KnotAgreement = namedtuple("KnotAgreement", "kind harmonic coordinate left_limit right_limit")
PreparedSource = namedtuple("PreparedSource", "source_sha256 source_parameter_id left right offset rate edges channels continuity trig_provider")


class Refusal(ValueError):
    def __init__(self, reason, code="UNESTABLISHED"):
        super().__init__(reason)
        self.code = code
        self.reason = str(reason)[:512]

    def as_record(self):
        return {"status": "REFUSED", "code": self.code, "reason": self.reason,
                "proof_established": False, "all_selected_events_refined": False,
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


def _qcheck(value, limit=MAX_INTERMEDIATE_BITS):
    need(type(value) is _FractionType and value.numerator.bit_length() <= limit and
         value.denominator.bit_length() <= limit, "Exact rational intermediate budget", "RESOURCE_REFUSAL")
    return value


def _coordinate(value):
    q = _qcheck(value, MAX_INPUT_BITS) if type(value) is _FractionType else rational(value)
    need(abs(q) <= TWO, "Point outside bounded original coordinate range", "RESOURCE_REFUSAL")
    return q


def _safe(a, b, operation):
    _qcheck(a); _qcheck(b)
    an, ad = a.numerator.bit_length(), a.denominator.bit_length()
    bn, bd = b.numerator.bit_length(), b.denominator.bit_length()
    if operation in ("add", "sub"):
        nbits, dbits = max(an+bd, bn+ad)+1, ad+bd
    elif operation == "mul":
        nbits, dbits = an+bn, ad+bd
    else:
        need(operation == "div" and b != ZERO, "Invalid exact arithmetic division")
        nbits, dbits = an+bd, ad+bn
    need(max(nbits, dbits) <= MAX_INTERMEDIATE_BITS,
         "Arithmetic operand growth exceeds finite budget", "RESOURCE_REFUSAL")
    result = a+b if operation == "add" else a-b if operation == "sub" else a*b if operation == "mul" else a/b
    return _qcheck(result)


def _sum(values):
    result = ZERO
    for value in values:
        result = _safe(result, value, "add")
    return result


def _strict_sign(interval):
    lo, hi = interval
    need(lo <= hi, "Reversed exact enclosure")
    return 1 if lo > ZERO else -1 if hi < ZERO else 0


def _sign(value):
    need(type(value) is int and value in (-1, 1), "Strict exact sign required")
    return value


def _steps(value):
    need(type(value) is int and 0 <= value <= MAX_STEPS,
         "Requested bisections must be an exact integer in 0..12", "RESOURCE_REFUSAL")
    return value


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
    module = types.ModuleType("_selected_refinement_checked_" + blob)
    module.__file__ = str(ROOT / relative)
    exec(compile(raw, module.__file__, "exec", dont_inherit=True, optimize=0), module.__dict__)
    module._checked_source_git_blob = blob
    return module


def qualified_parent_module(raw=None):
    if raw is None:
        raw = _checked_buffer(PARENT_MODEL, PARENT_MODEL_BLOB, MAX_CODE_BYTES)
    module = _compile_checked(raw, PARENT_MODEL, PARENT_MODEL_BLOB)
    need(module.DEPENDENCY_PINS == PARENT_PINS, "Qualified parent dependency manifest changed")
    return module


def qualified_trig_module(raw=None):
    if raw is None:
        raw = _checked_buffer(TRIG_FILE, TRIG_BLOB, MAX_CODE_BYTES)
    return _compile_checked(raw, TRIG_FILE, TRIG_BLOB)


def _capture_inputs():
    return {path: _checked_buffer(path, PINS[path], MAX_CODE_BYTES if path.endswith(".py") else MAX_BYTES)
            for path in (PARENT_MODEL, PARENT_REPORT, CORPUS_FILE, TRIG_FILE)}


def _pair_lt(a, b):
    return a[0]*b[1] < b[0]*a[1]


def _pair_abs_le_two(a):
    return abs(a[0]) <= 2*a[1]


def _preflight_source(spec):
    """All raw syntax, shape and spline structure before any Fraction call."""
    bounded_bytes(spec)
    need(type(spec) is dict and set(spec) == {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
         "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"}, "Exact source spec fields required")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and 0 < len(spec["source_parameter_id"]) <= 256,
         "Unsupported original source grammar or parameter")
    numbers = {key: _rational_parts(spec[key]) for key in
               ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate")}
    lo, hi = numbers["parameter_lo"], numbers["parameter_hi"]
    need(_pair_lt(lo, hi) and all(_pair_abs_le_two(value) for value in numbers.values()),
         "Source domain or phase exceeds bounded grammar", "RESOURCE_REFUSAL")
    channels = []
    for field, kind in (("cos_splines", "cos"), ("sin_splines", "sin")):
        mapping = spec[field]
        need(type(mapping) is dict and len(mapping) <= MAX_CHANNELS, "Harmonic channel count", "RESOURCE_REFUSAL")
        for harmonic, spline in mapping.items():
            need(type(harmonic) is str and re.fullmatch(r"[0-7]", harmonic, flags=re.ASCII) is not None,
                 "Canonical bounded harmonic required", "RESOURCE_REFUSAL")
            need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"}, "Exact spline fields required")
            degree = spline["degree"]
            controls, knots = spline["controls"], spline["knots"]
            need(type(degree) is int and 0 <= degree <= MAX_DEGREE, "Spline degree budget", "RESOURCE_REFUSAL")
            need(type(controls) is list and degree+1 <= len(controls) <= MAX_CONTROLS and
                 type(knots) is list and 2 <= len(knots) <= MAX_KNOTS and
                 len(knots) == len(controls)+degree+1, "Spline cardinality or list budget", "RESOURCE_REFUSAL")
            cp = tuple(_rational_parts(x) for x in controls)
            kp = tuple(_rational_parts(x) for x in knots)
            need(all(not _pair_lt(b, a) for a, b in zip(kp, kp[1:])), "Spline knots are not nondecreasing")
            need(kp[:degree+1] == (lo,)*(degree+1) and kp[-degree-1:] == (hi,)*(degree+1) and
                 kp[degree] == lo and kp[len(cp)] == hi,
                 "Spline is not fully clamped on the exact original source domain")
            need(max(Counter(kp).values()) <= degree+1, "Excessive original knot multiplicity")
            channels.append((kind, int(harmonic), degree, kp, cp))
    need(1 <= len(channels) <= MAX_CHANNELS, "Combined harmonic channel budget", "RESOURCE_REFUSAL")
    return numbers, sorted(channels, key=lambda c: (c[0], c[1]))


def _prepared_spline(spline):
    need(type(spline) is PreparedSpline and type(spline.degree) is int and 0 <= spline.degree <= MAX_DEGREE,
         "Bounded prepared spline required", "RESOURCE_REFUSAL")
    p = spline.degree
    need(type(spline.knots) is tuple and type(spline.controls) is tuple and
         p+1 <= len(spline.controls) <= MAX_CONTROLS and len(spline.knots) <= MAX_KNOTS and
         len(spline.knots) == len(spline.controls)+p+1, "Prepared spline cardinality", "RESOURCE_REFUSAL")
    for x in spline.knots+spline.controls+(spline.left, spline.right):
        _qcheck(x, MAX_INPUT_BITS)
    need(-TWO <= spline.left < spline.right <= TWO and
         spline.knots[:p+1] == (spline.left,)*(p+1) and
         spline.knots[-p-1:] == (spline.right,)*(p+1) and
         all(a <= b for a, b in zip(spline.knots, spline.knots[1:])) and
         max(Counter(spline.knots).values()) <= p+1, "Prepared spline structure changed")
    return spline


def spline_value(prepared_spline, t, side="PHYSICAL"):
    """Exact bounded Cox-de Boor point value or one-sided inward limit."""
    s = _prepared_spline(prepared_spline)
    t = _coordinate(t)
    need(type(side) is str and side in ("PHYSICAL", "LEFT_LIMIT", "RIGHT_LIMIT"), "Unknown coefficient side")
    need(s.left <= t <= s.right, "Coefficient point is outside its original source domain")
    if side == "PHYSICAL" and t == s.right:
        return s.controls[-1]
    need(not (side == "LEFT_LIMIT" and t == s.left) and
         not (side == "RIGHT_LIMIT" and t == s.right), "An outside source limit is not admitted")
    left = side == "LEFT_LIMIT"
    weights = [ONE if (a < t <= b if left else a <= t < b) else ZERO
               for a, b in zip(s.knots, s.knots[1:])]
    for degree in range(1, s.degree+1):
        next_weights = []
        for i in range(len(weights)-1):
            a = _safe(s.knots[i+degree], s.knots[i], "sub")
            b = _safe(s.knots[i+degree+1], s.knots[i+1], "sub")
            first = ZERO if a == ZERO else _safe(_safe(_safe(t, s.knots[i], "sub"), a, "div"), weights[i], "mul")
            second = ZERO if b == ZERO else _safe(_safe(_safe(s.knots[i+degree+1], t, "sub"), b, "div"), weights[i+1], "mul")
            next_weights.append(_safe(first, second, "add"))
        weights = next_weights
    need(len(weights) == len(s.controls) and all(w >= ZERO for w in weights) and _sum(weights) == ONE,
         "B-spline partition of unity or sided endpoint convention failed")
    return _sum(_safe(c, w, "mul") for c, w in zip(s.controls, weights))


def _source_continuity(channels):
    result = []
    for channel in channels:
        s = _prepared_spline(channel.spline)
        for knot in sorted(set(s.knots))[1:-1]:
            left = spline_value(s, knot, "LEFT_LIMIT")
            right = spline_value(s, knot, "RIGHT_LIMIT")
            need(left == right, "Coefficient discontinuity at an original source knot")
            result.append(KnotAgreement(channel.kind, channel.harmonic, knot, left, right))
        need(spline_value(s, s.left) == s.controls[0] and
             spline_value(s, s.right, "LEFT_LIMIT") == s.controls[-1] and
             spline_value(s, s.right) == s.controls[-1], "Clamped exterior coefficient convention failed")
    return tuple(result)


def prepare_source_spec(spec, *, _trig_provider=None):
    """Conditional bounded source preparation; no corpus/root theorem admission."""
    numbers, channels = _preflight_source(spec)
    q = {key: Fraction(*value) for key, value in numbers.items()}
    lo, hi = q["parameter_lo"], q["parameter_hi"]
    prepared = tuple(PreparedChannel(kind, harmonic,
        PreparedSpline(degree, tuple(Fraction(*x) for x in knots), tuple(Fraction(*x) for x in controls), lo, hi))
        for kind, harmonic, degree, knots, controls in channels)
    continuity = _source_continuity(prepared)
    edges = tuple(sorted({x for channel in prepared for x in channel.spline.knots}))
    provider = qualified_trig_module() if _trig_provider is None else _trig_provider
    need(type(provider) is types.ModuleType and getattr(provider, "_checked_source_git_blob", None) == TRIG_BLOB,
         "Point evaluator lacks the checked trig source")
    return PreparedSource(digest(spec), spec["source_parameter_id"], lo, hi,
                          q["phase_turn_offset"], q["phase_turn_rate"], edges, prepared, continuity, provider)


def _prepared_source(source):
    need(type(source) is PreparedSource and type(source.channels) is tuple and
         1 <= len(source.channels) <= MAX_CHANNELS and type(source.edges) is tuple and
         2 <= len(source.edges) <= MAX_CHANNELS*MAX_KNOTS and type(source.continuity) is tuple and
         len(source.continuity) <= MAX_CHANNELS*MAX_KNOTS,
         "Bounded prepared source required", "RESOURCE_REFUSAL")
    need(type(source.source_parameter_id) is str and 0 < len(source.source_parameter_id) <= 256 and
         type(source.source_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", source.source_sha256),
         "Prepared source identity metadata changed")
    for q in (source.left, source.right, source.offset, source.rate)+source.edges:
        _qcheck(q, MAX_INPUT_BITS)
    need(-TWO <= source.left < source.right <= TWO and abs(source.offset) <= TWO and abs(source.rate) <= TWO,
         "Prepared source coordinate/phase budget", "RESOURCE_REFUSAL")
    need(source.edges[0] == source.left and source.edges[-1] == source.right and
         all(a < b for a, b in zip(source.edges, source.edges[1:])), "Prepared source edges changed")
    identities = set()
    for c in source.channels:
        need(type(c) is PreparedChannel and type(c.kind) is str and c.kind in ("cos", "sin") and type(c.harmonic) is int and
             0 <= c.harmonic <= MAX_HARMONIC and (c.kind, c.harmonic) not in identities,
             "Prepared harmonic identity changed")
        identities.add((c.kind, c.harmonic))
        s = _prepared_spline(c.spline)
        need(s.left == source.left and s.right == source.right, "Coefficient source domain changed")
    need(source.edges == tuple(sorted({k for c in source.channels for k in c.spline.knots})),
         "Prepared source edges are not the exact original channel-knot union")
    for k in source.continuity:
        need(type(k) is KnotAgreement and type(k.kind) is str and type(k.harmonic) is int and
             (k.kind, k.harmonic) in identities, "Prepared continuity identity changed")
        _qcheck(k.coordinate, MAX_INPUT_BITS)
        _qcheck(k.left_limit); _qcheck(k.right_limit)
    spec = {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": source.source_parameter_id,
            "parameter_lo": str(source.left), "parameter_hi": str(source.right),
            "phase_turn_offset": str(source.offset), "phase_turn_rate": str(source.rate),
            "cos_splines": {}, "sin_splines": {}}
    for c in source.channels:
        spec[c.kind+"_splines"][str(c.harmonic)] = {
            "degree": c.spline.degree, "knots": list(map(str, c.spline.knots)),
            "controls": list(map(str, c.spline.controls))}
    need(digest(spec) == source.source_sha256, "Prepared coefficients/phase no longer match their source identity")
    return source


def _raw_point_interval(prepared_source, t):
    source = _prepared_source(prepared_source)
    t = _coordinate(t)
    need(source.left <= t <= source.right, "Original source point is out of domain")
    phase = _safe(source.offset, _safe(source.rate, t, "mul"), "add")
    _qcheck(phase, MAX_PHASE_BITS)
    provider = source.trig_provider
    need(type(provider) is types.ModuleType and getattr(provider, "_checked_source_git_blob", None) == TRIG_BLOB,
         "Original point lost its checked trig provider")
    plo, phi = provider.pi_bounds()
    _qcheck(plo, 330); _qcheck(phi, 330)
    pi_sum, pi_difference = plo+phi, phi-plo
    _qcheck(pi_sum, 330); _qcheck(pi_difference, 302)
    # With <=512-bit turns, fixed <=330-bit pi sum, and maximum power28,
    # the helper's shared polynomial denominator plus factorial/remainder
    # terms stay below 32768 bits; even unreduced binary products fit65536.
    result = (ZERO, ZERO)
    for c in source.channels:
        amplitude = spline_value(c.spline, t)
        turns = _safe(Fraction(c.harmonic), phase, "mul")
        _qcheck(turns, MAX_PHASE_BITS)
        cosine, sine = provider.trig(turns)
        interval = cosine if c.kind == "cos" else sine
        need(type(interval) is tuple and len(interval) == 2, "Invalid exact trig enclosure")
        for value in interval:
            _qcheck(value, 32768)
        need(interval[0] <= interval[1], "Reversed exact trig enclosure")
        scaled = tuple(_safe(value, amplitude, "mul") for value in interval)
        if amplitude < ZERO:
            scaled = scaled[::-1]
        result = tuple(_safe(a, b, "add") for a, b in zip(result, scaled))
    return result


def _outward_receipt(interval):
    lo, hi = interval
    _qcheck(lo); _qcheck(hi)
    sign = _strict_sign(interval)
    need(sign != 0, "Exact point enclosure includes zero", "UNRESOLVED_POINT_SIGN")
    need(max(lo.numerator.bit_length(), hi.numerator.bit_length())+DYADIC_BITS <= MAX_INTERMEDIATE_BITS,
         "Outward rounding operand budget", "RESOURCE_REFUSAL")
    low_integer = (lo.numerator*DYADIC_SCALE)//lo.denominator
    high_integer = -((-hi.numerator*DYADIC_SCALE)//hi.denominator)
    rounded = (Fraction(low_integer, DYADIC_SCALE), Fraction(high_integer, DYADIC_SCALE))
    for value in rounded:
        _qcheck(value, MAX_RECEIPT_BITS)
    need(rounded[0] <= lo <= hi <= rounded[1], "Outward interval failed containment")
    need(_strict_sign(rounded) == sign, "Outward dyadic interval includes zero", "UNRESOLVED_POINT_SIGN")
    return sign, rounded


def point_receipt(prepared_source, t):
    """Strict original-global-parameter point proof, conditional on preparation."""
    t = _coordinate(t)
    sign, rounded = _outward_receipt(_raw_point_interval(prepared_source, t))
    return {"source_spec_sha256": prepared_source.source_sha256, "coordinate": str(t),
            "sign": sign, "outward_dyadic_interval": list(map(str, rounded)),
            "dyadic_bits": DYADIC_BITS, "strict": True,
            "exact_source_enclosure_is_contained": True, "coordinate_is_original_parameter": True}


def _check_point(receipt, source, t):
    bounded_bytes(receipt)
    need(type(receipt) is dict and set(receipt) == {"source_spec_sha256", "coordinate", "sign",
         "outward_dyadic_interval", "dyadic_bits", "strict", "exact_source_enclosure_is_contained",
         "coordinate_is_original_parameter"}, "Point receipt fields changed")
    need(receipt["source_spec_sha256"] == source.source_sha256 and receipt["coordinate"] == str(t) and
         type(receipt["dyadic_bits"]) is int and receipt["dyadic_bits"] == DYADIC_BITS and
         receipt["strict"] is True and receipt["exact_source_enclosure_is_contained"] is True and
         receipt["coordinate_is_original_parameter"] is True, "Point receipt lost its source/strictness binding")
    interval = receipt["outward_dyadic_interval"]
    need(type(interval) is list and len(interval) == 2, "Point needs two outward bounds")
    lo, hi = (rational(q, MAX_RECEIPT_BITS) for q in interval)
    need(DYADIC_SCALE % lo.denominator == 0 and DYADIC_SCALE % hi.denominator == 0,
         "Point receipt is not on the fixed outward dyadic grid")
    need(_strict_sign((lo, hi)) == _sign(receipt["sign"]), "Point receipt is not strictly signed")
    return receipt["sign"]


def _bracket(source, bracket):
    need(type(bracket) in (list, tuple) and len(bracket) == 2, "Two strict bracket endpoints required")
    a, b = map(_coordinate, bracket)
    need(source.left <= a < b <= source.right, "Bracket is outside the original source domain")
    pieces = [i for i, (lo, hi) in enumerate(zip(source.edges, source.edges[1:])) if lo <= a < b <= hi]
    need(len(pieces) == 1, "Bracket crosses an original source knot or lacks one source span")
    return a, b, pieces[0]


def refine_bracket(prepared_source, initial_bracket, left_sign, right_sign, steps):
    """Conditional restriction under an external unique-simple-root theorem.

    This helper cannot supply that theorem or any accepted source/cohort status.
    Public refinement always binds a freshly replayed parent event first.
    """
    steps = _steps(steps)
    source = _prepared_source(prepared_source)
    need(_source_continuity(source.channels) == source.continuity,
         "Prepared source continuity premise changed")
    left_sign, right_sign = _sign(left_sign), _sign(right_sign)
    need(left_sign == -right_sign, "Inherited endpoint signs are not opposite")
    a, b, piece = _bracket(source, initial_bracket)
    initial = [str(a), str(b)]
    width = _safe(b, a, "sub")
    lp, rp = point_receipt(source, a), point_receipt(source, b)
    need(_check_point(lp, source, a) == left_sign and _check_point(rp, source, b) == right_sign,
         "Original endpoint signs disagree with the inherited unique-root event")
    initial_points = [clone(lp), clone(rp)]
    trace = []
    for step in range(1, steps+1):
        before = [str(a), str(b)]
        mid = _safe(_safe(a, b, "add"), TWO, "div")
        _qcheck(mid, MAX_INPUT_BITS)
        mp = point_receipt(source, mid)
        midpoint_sign = _check_point(mp, source, mid)
        if midpoint_sign == left_sign:
            a, lp, kept = mid, mp, "RIGHT"
        else:
            need(midpoint_sign == right_sign, "Midpoint has neither inherited strict sign")
            b, rp, kept = mid, mp, "LEFT"
        need(_safe(b, a, "sub") == _safe(width, Fraction(1 << step), "div"),
             "Refinement failed exact halved width")
        trace.append({"step": step, "before_bracket": before, "midpoint": str(mid),
                      "midpoint_receipt": clone(mp), "kept_half": kept,
                      "after_bracket": [str(a), str(b)], "width": str(b-a)})
    return {"conditional_on_unique_simple_root": True, "requested_steps": steps,
            "initial_bracket": initial, "final_bracket": [str(a), str(b)],
            "original_source_piece_index": piece, "source_span": list(map(str, source.edges[piece:piece+2])),
            "initial_width": str(width), "final_width": str(b-a),
            "initial_endpoint_receipts": initial_points, "final_endpoint_receipts": [clone(lp), clone(rp)],
            "trace": trace, "source_continuity_checked": True, "all_points_in_original_parameter": True,
            "no_exact_root_coordinate_claimed": True, "proof_cuts_create_no_physical_events": True}


def _select_bound_events(parent_report, indexed):
    """Finite admission from the exact qualified baseline, before numeric work."""
    need(digest(parent_report) == PARENT_REPORT_VALUE_SHA256,
         "Parent zero-set report is not the qualified complete original-source view")
    bounded_bytes(indexed)
    need(type(indexed) is dict and len(indexed) == 121, "Original frozen corpus population changed")
    sources = parent_report["source_cases"]
    need(type(sources) is list and len(sources) == 50, "Parent original-source cohort changed")
    selected = []
    seen_sources = set()
    finite = continuum = rational_events = implicit_events = 0
    for source in sources:
        cid = source["case_id"]
        need(type(cid) is str and cid in indexed and cid not in seen_sources, "Original source identity is missing or duplicated")
        seen_sources.add(cid)
        row = indexed[cid]
        need(type(row) is dict and row.get("id") == cid, "Original row ID does not bind source")
        spec = row["spec"]
        need(digest(row) == source["original_row_sha256"] and digest(spec) == source["source_sha256"],
             "Original whole-row or source bytes changed")
        need(spec["source_parameter_id"] == source["source_parameter_id"] and
             [spec["parameter_lo"], spec["parameter_hi"]] == source["source_interval"] and
             {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]} == source["phase_turn_law"] and
             row["origin"] == source["origin"] and row["kind"] == source["provenance_kind"],
             "Original parameter, phase or provenance changed")
        need(source["status"] == "ESTABLISHED_FOR_PINNED_ORIGINAL_SOURCE" and
             source["historical_disposition_changed"] is False and source["production_authorized"] is False,
             "Parent original-source theorem is not established in the qualified research scope")
        zeros = source["zero_set"]
        need(zeros["complete_for_original_closed_source"] is True, "Parent source theorem is incomplete")
        if zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT":
            need(zeros["events"] is None and zeros["isolated_root_count"] is None and
                 zeros["finite_event_list_applicable"] is False, "Continuum was converted to a finite cohort")
            continuum += 1
            continue
        need(zeros["kind"] == "FINITE_ORIGINAL_SOURCE_ZERO_SET" and
             type(zeros["events"]) is list, "Parent finite zero-set type changed")
        finite += 1
        need(type(zeros["isolated_root_count"]) is int and zeros["isolated_root_count"] == len(zeros["events"]),
             "Parent physical event count changed")
        for ordinal, event in enumerate(zeros["events"]):
            need(event["event_id"] == "ROOT_"+str(ordinal) and event["source_case_id"] == cid and
                 event["source_sha256"] == source["source_sha256"], "Parent source-scoped event identity changed")
            coordinate = event["coordinate"]
            if coordinate["kind"] == "RATIONAL":
                rational_events += 1
                continue
            need(coordinate["kind"] == "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE" and
                 event["location"] == "SPAN_INTERIOR" and
                 bounded_bytes(event["order"]) == b'{"kind":"SMOOTH","value":1}',
                 "Selected event lacks the inherited unique simple implicit-root premise")
            need(coordinate["source_case_id"] == cid and coordinate["source_sha256"] == source["source_sha256"] and
                 coordinate["source_parameter_id"] == source["source_parameter_id"] and
                 type(coordinate["source_piece_index"]) is int and
                 event["source_piece_indices"] == [coordinate["source_piece_index"]] and
                 coordinate["exact_algebraic_root_coordinate_claimed"] is False and
                 coordinate["defining_predicate"] == "ORIGINAL_SOURCE_F_EQUALS_ZERO",
                 "Implicit locator lost original source/piece binding")
            piece = coordinate["source_piece_index"]
            edges = source["original_source_piece_edges"]
            need(0 <= piece < len(edges)-1 and coordinate["source_span"] == edges[piece:piece+2],
                 "Implicit locator was moved to another original span")
            proof = coordinate["uniqueness_evidence"]
            for key in ("producer", "producer_code", "producer_git_blob", "replayed_result_sha256"):
                need(proof[key] == source["producer_evidence"][key], "Unique-root evidence has the wrong proof owner")
            need(proof["field_path"] == event["proof_path"] and proof["field_path"], "Unique-root event reference changed")
            left, right = _sign(event["left_sign"]), _sign(event["right_sign"])
            need(left == -right, "A simple implicit locator lacks opposite physical side signs")
            selected.append({
                "case_id": cid, "event_id": event["event_id"], "event_ordinal": ordinal,
                "source_sha256": source["source_sha256"], "original_row_sha256": source["original_row_sha256"],
                "source_parameter_id": source["source_parameter_id"], "source_interval": clone(source["source_interval"]),
                "phase_turn_law": clone(source["phase_turn_law"]),
                "original_source_piece_index": piece, "original_source_span": clone(coordinate["source_span"]),
                "parent_source_record_sha256": digest(source), "parent_event_sha256": digest(event),
                "parent_coordinate": clone(coordinate), "parent_uniqueness_evidence": clone(proof),
                "inherited_order": clone(event["order"]), "parent_left_sign": left, "parent_right_sign": right,
                "unique_simple_root_inherited": True})
            implicit_events += 1
    need((finite, continuum, rational_events, implicit_events) == (49, 1, 12, 69) and
         len({e["case_id"] for e in selected}) == 28, "Derived qualified event cohort changed")
    need(len({(e["case_id"], e["event_id"]) for e in selected}) == len(selected), "Duplicate selected physical event")
    return selected


def _preparation_receipt(cid, row, source):
    return {"case_id": cid, "source_sha256": source.source_sha256, "original_row_sha256": digest(row),
            "source_parameter_id": source.source_parameter_id,
            "source_interval": [str(source.left), str(source.right)],
            "phase_turn_law": {"offset": str(source.offset), "rate": str(source.rate)},
            "original_source_piece_edges": list(map(str, source.edges)),
            "coefficient_channel_count": len(source.channels),
            "maximum_coefficient_degree": max(c.spline.degree for c in source.channels),
            "coefficient_knot_agreements": [
                {"kind": k.kind, "harmonic": k.harmonic, "coordinate": str(k.coordinate),
                 "left_limit": str(k.left_limit), "right_limit": str(k.right_limit)} for k in source.continuity],
            "every_coefficient_knot_has_equal_one_sided_limits": True,
            "coefficient_continuity_proves_original_source_continuity": True,
            "fully_clamped_terminal_value_is_last_control": True,
            "global_phase_uses_original_source_parameter": True}


def _refined_coordinate(binding, kernel):
    return {"kind": "REFINED_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE",
            "source_case_id": binding["case_id"], "source_sha256": binding["source_sha256"],
            "source_parameter_id": binding["source_parameter_id"],
            "source_piece_index": binding["original_source_piece_index"],
            "source_span": clone(binding["original_source_span"]),
            "source_event_id": binding["event_id"], "parent_event_sha256": binding["parent_event_sha256"],
            "strict_open_bracket": clone(kernel["final_bracket"]),
            "initial_parent_bracket": clone(binding["parent_coordinate"]["strict_open_bracket"]),
            "unique_simple_root_inherited": True,
            "exact_rational_or_algebraic_root_coordinate_claimed": False}


def _bind_prepared(binding, row, source):
    need(source.source_sha256 == binding["source_sha256"] and digest(row) == binding["original_row_sha256"] and
         source.source_parameter_id == binding["source_parameter_id"] and
         [str(source.left), str(source.right)] == binding["source_interval"] and
         {"offset": str(source.offset), "rate": str(source.rate)} == binding["phase_turn_law"],
         "Prepared evaluator is not the admitted original source")
    a, b, piece = _bracket(source, binding["parent_coordinate"]["strict_open_bracket"])
    need(piece == binding["original_source_piece_index"] and
         list(map(str, source.edges[piece:piece+2])) == binding["original_source_span"],
         "Prepared source does not preserve original parent span")
    return a, b, piece


def _refine_bound_event(binding, row, source, steps):
    _bind_prepared(binding, row, source)
    kernel = refine_bracket(source, binding["parent_coordinate"]["strict_open_bracket"],
                            binding["parent_left_sign"], binding["parent_right_sign"], steps)
    result = clone(binding)
    result.update(coordinate=_refined_coordinate(binding, kernel), refinement=kernel)
    return result


def _corpus_index(corpus):
    need(type(corpus) is dict and type(corpus.get("cases")) is list and len(corpus["cases"]) == 121,
         "Original frozen corpus grammar changed")
    indexed = {}
    for row in corpus["cases"]:
        need(type(row) is dict and type(row.get("id")) is str and row["id"] not in indexed,
             "Original frozen corpus has duplicate/malformed identities")
        indexed[row["id"]] = row
    return indexed


def replay_refinements(steps=12):
    """One actual fresh parent replay and an atomic complete selected operation."""
    steps = _steps(steps)
    try:
        buffers = _capture_inputs()
        saved_parent = parse_json_bytes(buffers[PARENT_REPORT])
        need(digest(saved_parent) == PARENT_REPORT_VALUE_SHA256, "Qualified parent value hash changed")
        indexed = _corpus_index(parse_json_bytes(buffers[CORPUS_FILE]))
        parent = qualified_parent_module(buffers[PARENT_MODEL])
        trig = qualified_trig_module(buffers[TRIG_FILE])
        parent_context = parent.replay_sources()
        parent_report = parent.report_from_replay(parent_context)
        need(bounded_bytes(parent_report) == bounded_bytes(saved_parent),
             "Actual fresh parent proof differs from its qualified saved report")
        need(bounded_bytes(indexed) == bounded_bytes(parent_context["indexed"]),
             "Independently retained original corpus differs from the actual parent replay")
        selected = _select_bound_events(parent_report, indexed)
        prepared = {}
        preparations = []
        refinements = []
        for binding in selected:
            cid = binding["case_id"]
            row = indexed[cid]
            if cid not in prepared:
                prepared[cid] = prepare_source_spec(row["spec"], _trig_provider=trig)
                preparations.append(_preparation_receipt(cid, row, prepared[cid]))
            refinements.append(_refine_bound_event(binding, row, prepared[cid], steps))
        need(len(refinements) == len(selected), "A selected event was omitted after a failed refinement")
        custody = [{"path": path, "git_blob": PINS[path], "bytes": len(buffers[path]),
                    "sha256": hashlib.sha256(buffers[path]).hexdigest()}
                   for path in sorted(buffers)]
        return {"requested_steps": steps, "indexed": indexed, "parent_context": parent_context,
                "parent_report": parent_report, "parent_report_sha256": digest(parent_report),
                "selected_events": selected, "source_preparations": preparations,
                "refinements": refinements, "input_custody": custody}
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Parent/refinement computation exhausted resources", "RESOURCE_REFUSAL") from error
    except Exception as error:
        raise Refusal("Actual parent/refinement computation failed: " + type(error).__name__ + ": " + str(error)[:200]) from error


def _validate_kernel(kernel, binding, source, steps):
    """Recheck structural interval invariants; submitted reports still replay."""
    bounded_bytes(kernel)
    need(type(kernel) is dict and set(kernel) == {"conditional_on_unique_simple_root", "requested_steps",
         "initial_bracket", "final_bracket", "original_source_piece_index", "source_span", "initial_width",
         "final_width", "initial_endpoint_receipts", "final_endpoint_receipts", "trace", "source_continuity_checked",
         "all_points_in_original_parameter", "no_exact_root_coordinate_claimed", "proof_cuts_create_no_physical_events"},
         "Refinement kernel fields changed")
    for key in ("conditional_on_unique_simple_root", "source_continuity_checked", "all_points_in_original_parameter",
                "no_exact_root_coordinate_claimed", "proof_cuts_create_no_physical_events"):
        need(kernel[key] is True, "Refinement lost a required conditional/source premise: " + key)
    need(_steps(kernel["requested_steps"]) == steps and
         kernel["initial_bracket"] == binding["parent_coordinate"]["strict_open_bracket"] and
         type(kernel["original_source_piece_index"]) is int and
         kernel["original_source_piece_index"] == binding["original_source_piece_index"] and
         kernel["source_span"] == binding["original_source_span"], "Refinement request or original locator changed")
    a, b, _ = _bracket(source, kernel["initial_bracket"])
    initial_width = b-a
    need(kernel["initial_width"] == str(initial_width), "Initial exact width changed")
    initial_points = kernel["initial_endpoint_receipts"]
    need(type(initial_points) is list and len(initial_points) == 2, "Both original strict endpoint receipts required")
    lp, rp = initial_points
    left, right = binding["parent_left_sign"], binding["parent_right_sign"]
    need(_check_point(lp, source, a) == left and _check_point(rp, source, b) == right and left == -right,
         "Initial endpoint receipts contradict the parent physical signs")
    trace = kernel["trace"]
    need(type(trace) is list and len(trace) == steps, "A requested trace step was dropped or added")
    for step, item in enumerate(trace, 1):
        need(type(item) is dict and set(item) == {"step", "before_bracket", "midpoint", "midpoint_receipt",
             "kept_half", "after_bracket", "width"} and type(item["step"]) is int and item["step"] == step,
             "Refinement step identity changed")
        need(item["before_bracket"] == [str(a), str(b)], "Trace is not a consecutive nested bracket sequence")
        mid = (a+b)/2
        need(item["midpoint"] == str(mid), "Trace did not use the exact original-parameter midpoint")
        mp = item["midpoint_receipt"]
        sign = _check_point(mp, source, mid)
        if sign == left:
            need(item["kept_half"] == "RIGHT", "Wrong half kept for the midpoint sign")
            a, lp = mid, mp
        else:
            need(sign == right and item["kept_half"] == "LEFT", "Wrong half kept for the midpoint sign")
            b, rp = mid, mp
        need(item["after_bracket"] == [str(a), str(b)] and item["width"] == str(b-a) and
             b-a == initial_width/(1 << step), "Trace width or containment does not follow exact bisection")
        _bracket(source, item["after_bracket"])
    need(kernel["final_bracket"] == [str(a), str(b)] and kernel["final_width"] == str(b-a) and
         b-a == initial_width/(1 << steps) and
         bounded_bytes(kernel["final_endpoint_receipts"]) == bounded_bytes([clone(lp), clone(rp)]),
         "Final bracket/endpoints are not the inherited strict trace result")


def report_from_replay(replay):
    """Internal formatter, not a substitute for the public fresh proof path."""
    need(type(replay) is dict and set(replay) == {"requested_steps", "indexed", "parent_context", "parent_report",
         "parent_report_sha256", "selected_events", "source_preparations", "refinements", "input_custody"},
         "Checked refinement context fields changed")
    steps = _steps(replay["requested_steps"])
    parent_report = replay["parent_report"]
    need(digest(parent_report) == replay["parent_report_sha256"] == PARENT_REPORT_VALUE_SHA256,
         "Qualified parent context was replaced")
    selected = _select_bound_events(parent_report, replay["indexed"])
    need(bounded_bytes(selected) == bounded_bytes(replay["selected_events"]),
         "Selected source/event cohort was omitted, duplicated, substituted or reordered")
    need(bounded_bytes(replay["parent_context"]["normalized_source_cases"]) ==
         bounded_bytes(parent_report["source_cases"]) and
         bounded_bytes(replay["parent_context"]["indexed"]) == bounded_bytes(replay["indexed"]),
         "Fresh parent original/source context detached from the qualified baseline")
    refinements = replay["refinements"]
    bounded_bytes(refinements)
    need(type(refinements) is list and len(refinements) == len(selected), "Complete selected refinement set is missing")
    trig = qualified_trig_module()
    prepared = {}
    preparations = []
    for binding, result in zip(selected, refinements):
        need(type(result) is dict and set(result) == set(binding) | {"coordinate", "refinement"},
             "Bound refinement record fields changed")
        for key, value in binding.items():
            need(bounded_bytes(result[key]) == bounded_bytes(value), "Selected original/event binding changed: " + key)
        cid = binding["case_id"]
        row = replay["indexed"][cid]
        if cid not in prepared:
            prepared[cid] = prepare_source_spec(row["spec"], _trig_provider=trig)
            preparations.append(_preparation_receipt(cid, row, prepared[cid]))
        source = prepared[cid]
        _bind_prepared(binding, row, source)
        _validate_kernel(result["refinement"], binding, source, steps)
        need(bounded_bytes(result["coordinate"]) == bounded_bytes(_refined_coordinate(binding, result["refinement"])),
             "Refined coordinate lost its original implicit-root identity")
    need(bounded_bytes(preparations) == bounded_bytes(replay["source_preparations"]),
         "Original coefficient preparation/continuity evidence changed")
    custody = replay["input_custody"]
    bounded_bytes(custody)
    need(bounded_bytes(custody) == bounded_bytes([DIRECT_INPUTS[path] for path in sorted(DIRECT_INPUTS)]),
         "Direct checked-buffer path/blob/byte-count/SHA256 custody changed")
    point_decisions = sum(2+len(r["refinement"]["trace"]) for r in refinements)
    need(point_decisions == len(selected)*(steps+2), "A strict point decision was skipped")
    result = {
        "schema": SCHEMA, "status": "ALL_SELECTED_IMPLICIT_ORIGINAL_ROOTS_REFINED_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL", "qualified_base_main": BASE_MAIN,
        "requested_steps": steps,
        "qualified_parent": {"model": PARENT_MODEL, "model_git_blob": PARENT_MODEL_BLOB,
                             "report": PARENT_REPORT, "report_git_blob": PARENT_REPORT_BLOB,
                             "fresh_report_sha256": replay["parent_report_sha256"]},
        "executed_byte_custody": {"direct_input_buffers": clone(custody),
            "parent_actual_no_argument_replay_executed": True,
            "parent_report_canonically_equals_qualified_saved_report": True,
            "independent_original_corpus_equals_fresh_parent_originals": True,
            "project_code_compiled_from_same_bounded_verified_buffers": True,
            "trig_code": TRIG_FILE, "trig_git_blob": TRIG_BLOB,
            "dependency_path_count": len(PINS), "python_and_standard_library_trusted": True,
            "hostile_python_sandbox_claimed": False},
        "scope": {"all_selected_events_refined": True, "failed_events_silently_dropped": False,
            "parent_complete_zero_sets_preserved": True, "parent_rational_events_refined": False,
            "parent_continuum_type_preserved": True, "refinement_creates_no_physical_events": True,
            "simplicity_and_uniqueness_are_inherited_from_parent": True,
            "arbitrary_source_or_event_admission": False, "new_root_completeness_theorem": False,
            "exact_rational_or_algebraic_root_coordinates_established": False,
            "generic_owner_routes_repaired": False, "native_geometry_evidence": False},
        "budgets": {"maximum_steps": MAX_STEPS, "coefficient_degree": MAX_DEGREE,
            "controls_per_spline": MAX_CONTROLS, "knots_per_spline": MAX_KNOTS,
            "combined_harmonic_channels": MAX_CHANNELS, "maximum_harmonic": MAX_HARMONIC,
            "input_rational_bits": MAX_INPUT_BITS, "receipt_rational_bits": MAX_RECEIPT_BITS,
            "intermediate_rational_bits": MAX_INTERMEDIATE_BITS, "derived_phase_bits": MAX_PHASE_BITS,
            "outward_dyadic_bits": DYADIC_BITS, "report_bytes": MAX_BYTES,
            "json_value_nodes": MAX_NODES, "json_depth": MAX_DEPTH},
        "parent_baseline": clone(parent_report), "source_preparations": clone(preparations),
        "refinements": clone(refinements),
        "summary": {"selected_implicit_locators": len(refinements), "selected_original_sources": len(prepared),
            "strict_point_decisions": point_decisions, "completed_bisections": sum(len(r["refinement"]["trace"]) for r in refinements),
            "width_divisor": 1 << steps, "parent_original_sources": len(parent_report["source_cases"]),
            "parent_isolated_physical_zeros": parent_report["summary"]["sum_of_per_source_distinct_isolated_zeros"],
            "parent_rational_zero_coordinates": parent_report["summary"]["rational_zero_coordinates"],
            "parent_continuum_sources": parent_report["summary"]["continuum_source_count"],
            "parent_maximal_connected_nonzero_cells": parent_report["summary"]["maximal_connected_nonzero_cells"]},
        "gates": clone(parent_report["gates"])}
    bounded_bytes(result)
    return result


def expected_report(steps=12):
    _steps(steps)
    try:
        return report_from_replay(replay_refinements(steps))
    except Refusal:
        raise
    except (MemoryError, RecursionError) as error:
        raise Refusal("Complete refinement exhausted resources", "RESOURCE_REFUSAL") from error
    except Exception as error:
        raise Refusal("Complete refinement failed: " + type(error).__name__ + ": " + str(error)[:200]) from error


def refine_selected(steps=12):
    try:
        return expected_report(steps)
    except Refusal as error:
        return error.as_record()


def read_report(path=REPORT):
    need(type(path) in (str, type(REPORT)), "Exact bounded report path required", "RESOURCE_REFUSAL")
    text = str(path)
    need(0 < len(text) <= 4096 and "\0" not in text, "Report path text budget", "RESOURCE_REFUSAL")
    return parse_json_bytes(_read_bounded(Path(path), MAX_BYTES))


def _compare_with_replayed_bytes(candidate, expected_bytes):
    need(type(expected_bytes) is bytes and len(expected_bytes) <= MAX_BYTES, "Bounded expected report required", "RESOURCE_REFUSAL")
    need(bounded_bytes(candidate) == expected_bytes, "Submitted refinement differs from a fresh complete requested replay")
    return True


def validate_report(candidate, steps=12):
    _steps(steps)
    bounded_bytes(candidate)
    return _compare_with_replayed_bytes(candidate, bounded_bytes(expected_report(steps)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--contract", action="store_true")
    options = parser.parse_args()
    if not (options.write_report or options.contract):
        parser.error("choose --write-report and/or --contract")
    result = expected_report(options.steps)
    if options.write_report:
        REPORT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True)+"\n")
    if options.contract:
        _compare_with_replayed_bytes(read_report(), bounded_bytes(result))
        print("PASS: every selected implicit original-source root has its requested strict dyadic refinement")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
