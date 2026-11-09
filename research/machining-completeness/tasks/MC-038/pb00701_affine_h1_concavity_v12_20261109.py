#!/usr/bin/env python3
"""MC-038 restricted original V12 affine-H1 concavity certificate; no gate claims."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
V54 = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
V12_ID = "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0"
V12_SPEC_SHA = "ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5"
V12_ROW_SHA = "d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3"
SCHEMA = "radicadsac-pb00701-original-v12-affine-h1-concavity/1.0"
RECEIPT = HERE / "pb00701-affine-h1-concavity-v12-20261109.json"
FIELDS = ("h0","h1","c0","c1","s0","s1")
TOKEN = re.compile(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")

class RefusedNontruth(ValueError):
    pass

def require(condition: bool, reason: str):
    if not condition:
        raise RefusedNontruth(reason)

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",",":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def rational(x: str) -> Q:
    require(type(x) is str and len(x) <= 160 and TOKEN.fullmatch(x) is not None,
            "NONCANONICAL_RATIONAL_TOKEN")
    try:
        v = Q(x)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise RefusedNontruth("INVALID_RATIONAL") from exc
    require(str(v) == x, "NONCANONICAL_RATIONAL")
    require(max(v.numerator.bit_length(), v.denominator.bit_length()) <= 512,
            "INPUT_BIT_BUDGET")
    return v

def sign_sqrt2(a: Q, b: Q) -> int:
    """Exact sign(a+b*sqrt(2)); rational equality only when both vanish."""
    if a == 0:
        return (b > 0) - (b < 0)
    if b == 0 or (a > 0) == (b > 0):
        return (a > 0) - (a < 0)
    delta = a*a - 2*b*b
    require(delta != 0, "SQRT2_RATIONALITY_INVARIANT")
    return ((a > 0) - (a < 0)) if delta > 0 else ((b > 0) - (b < 0))

def affine(source: dict) -> dict:
    """Sufficient strictly concave two-root theorem, not a general root solver."""
    require(type(source) is dict and set(source) == set(FIELDS), "AFFINE_FIELDS")
    h0,h1,c0,c1,s0,s1 = [rational(source[k]) for k in FIELDS]
    cmin = min(c0,c0+c1)
    smin = min(s0,s0+s1)
    m = min(c1,-s1)
    M = max(Q(0), -cmin, -smin)
    # theta = pi*t/2, 0 <= t <= 1. pi < 4 implies omega < 2.
    # F'' <= omega*(-2*m + omega*M)*(sin(theta)+cos(theta)) < 0
    # if m>M. H0 is affine and contributes zero to F''.
    require(m > M, "STRICT_CONCAVITY_BOUND_NOT_PROVEN")
    left = h0+c0
    right = h0+h1+s0+s1
    midpoint_a = h0+h1/2
    midpoint_b = (c0+c1/2+s0+s1/2)/2  # F(1/2) = a+b*sqrt(2)
    require(left < 0 and right < 0, "STRICT_NEGATIVE_ENDPOINTS_NOT_PROVEN")
    require(sign_sqrt2(midpoint_a,midpoint_b) > 0,
            "STRICT_POSITIVE_MIDPOINT_NOT_PROVEN")
    return {
        "schema": SCHEMA,
        "source_spec": dict(source),
        "source_spec_sha256": hashlib.sha256(canonical(source)).hexdigest(),
        "evidence_class": "DETERMINISTIC_MODEL",
        "status": "COMPLETE_RESTRICTED_TWO_SIMPLE_ROOTS",
        "phase_turns": ["0", "1/4"],
        "strict_concavity": {
            "min_slope_c1_minus_s1": str(m),
            "coefficient_negative_lower_bound_M": str(M),
            "exact_sufficient_inequality": "m > M; 0 < pi/2 < 2",
        },
        "strict_endpoint_values": [str(left), str(right)],
        "strict_midpoint_a_plus_b_sqrt2": [str(midpoint_a), str(midpoint_b)],
        "ordered_event_brackets": [["0","1/2"],["1/2","1"]],
        "orders": [1,1],
        "maximal_open_signs": ["NEGATIVE","POSITIVE","NEGATIVE"],
        "proof": "SECOND_DERIVATIVE_STRICT_NEGATIVE_AND_IVT_ROLLE",
        "historical_new_closures": 0,
        "required_pb_po_discharges": 0,
        "mc_b": "NOT_ESTABLISHED",
        "mc_1": "NOT_ESTABLISHED",
        "production_authorized": False
    }

def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def pinned_committed_bytes(path: Path, worktree: bytes, expected_blob: str,
                           limit: int) -> bytes:
    """Check actual HEAD:path object, its bytes and only LF/CRLF checkout changes."""
    try:
        root = Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=path.parent,
            stderr=subprocess.DEVNULL).decode("utf-8").strip()).resolve()
        rel = path.resolve().relative_to(root).as_posix()
        oid = subprocess.check_output(
            ["git", "rev-parse", "--verify", "HEAD:" + rel], cwd=root,
            stderr=subprocess.DEVNULL).decode("ascii").strip()
        require(oid == expected_blob, "PINNED_GIT_BLOB_MISMATCH")
        kind = subprocess.check_output(
            ["git", "cat-file", "-t", oid], cwd=root,
            stderr=subprocess.DEVNULL).decode("ascii").strip()
        require(kind == "blob", "PINNED_OBJECT_NOT_BLOB")
        size = int(subprocess.check_output(
            ["git", "cat-file", "-s", oid], cwd=root,
            stderr=subprocess.DEVNULL).strip())
        require(size <= limit, "RAW_BYTE_LIMIT")
        committed = subprocess.check_output(
            ["git", "cat-file", "blob", oid], cwd=root,
            stderr=subprocess.DEVNULL)
    except RefusedNontruth:
        raise
    except (OSError, ValueError, UnicodeDecodeError,
            subprocess.CalledProcessError) as exc:
        raise RefusedNontruth("GIT_OBJECT_CUSTODY_UNAVAILABLE") from exc
    require(len(committed) == size and git_blob_sha(committed) == expected_blob,
            "PINNED_GIT_BLOB_MISMATCH")
    require(worktree.replace(b"\r\n", b"\n") ==
            committed.replace(b"\r\n", b"\n"), "CHECKOUT_BYTES_MISMATCH")
    return committed

def strict_json(path: Path, limit: int = 400_000, expected_blob: str | None = None):
    with path.open("rb") as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, "RAW_BYTE_LIMIT")
    committed = (pinned_committed_bytes(path, raw, expected_blob, limit)
                 if expected_blob is not None else None)
    def pairs(seq):
        out = {}
        for k,v in seq:
            require(k not in out, "DUPLICATE_JSON_KEY")
            out[k]=v
        return out
    def number(token):
        require(len(token) <= 16, "INTEGER_TOKEN_LIMIT")
        return int(token)
    def noninteger(_):
        raise RefusedNontruth("NONINTEGER_JSON_NUMBER")
    def decode(data):
        try:
            return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                              parse_int=number, parse_float=noninteger,
                              parse_constant=noninteger)
        except RefusedNontruth:
            raise
        except (UnicodeDecodeError, ValueError, RecursionError,
                OverflowError) as exc:
            raise RefusedNontruth("INVALID_JSON") from exc
    checkout = decode(raw)
    if committed is not None:
        require(checkout == decode(committed), "ORIGINAL_SEMANTICS_MISMATCH")
    return checkout

def frozen_spec():
    # Independent hardcoded source assertion; original frozen V54+V2 rehashed
    # separately at runtime when the authoritative repository is present.
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": {"degree":0, "knots":["0","1","2"], "controls":["0","0"]},
            "1": {"degree":1, "knots":["0","0","1","1","2","2"],
                  "controls":["-1/3","2/3","2/3","2/3"]}},
        "sin_splines": {
            "1": {"degree":1, "knots":["0","0","1","1","2","2"],
                  "controls":["2/3","-1/3","-1/3","-1/3"]}}
    }

def original_contract(check_files: bool = True):
    spec = frozen_spec()
    require(hashlib.sha256(canonical(spec)).hexdigest() == V12_SPEC_SHA,
            "HARDCODED_SOURCE_SHA_MISMATCH")
    if check_files:
        corpus = strict_json(V54, expected_blob=V54_BLOB)
        evidence = strict_json(V2, expected_blob=V2_BLOB)
        cases = corpus["cases"]
        require(type(cases) is list and len(cases)==121, "ORIGINAL_121")
        rows = [x for x in cases if x.get("id")==V12_ID]
        require(len(rows)==1 and rows[0]["spec"]==spec and
                hashlib.sha256(canonical(rows[0])).hexdigest()==V12_ROW_SHA,
                "FROZEN_ORIGINAL_V12_DRIFT")
        v2 = evidence["source_cases"]
        require(type(v2) is list and len(v2)==50, "V2_50")
        matches = [x for x in v2 if x.get("case_id")==V12_ID]
        require(len(matches)==1 and
                matches[0]["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC" and
                matches[0]["source_sha256"]==V12_SPEC_SHA and
                matches[0]["evidence"]["original_row_sha256"]==V12_ROW_SHA,
                "V12_V2_BINDING_DRIFT")
        refused = sum(row["expected"]["v54_disposition"]=="BLOCKED" for row in cases)
        missing = sum(row["expected"]["v54_disposition"]==
                      "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE" for row in cases)
        require((refused,missing)==(20,30), "FROZEN_DENOMINATOR_DRIFT")
    c=spec["cos_splines"]["1"]["controls"]
    s=spec["sin_splines"]["1"]["controls"]
    require(spec["cos_splines"]["0"]["controls"]==["0","0"] and
            c==["-1/3","2/3","2/3","2/3"] and
            s==["2/3","-1/3","-1/3","-1/3"] and
            spec["phase_turn_offset"]=="0" and spec["phase_turn_rate"]=="1/4",
            "SPLINE_EXTRACTION_REFUSED")
    # Degree-1 clamped B-spline; first [0,1] piece interpolates controls 0,1.
    a = {"h0":"0","h1":"0","c0":str(Q(c[0])),"c1":str(Q(c[1])-Q(c[0])),
         "s0":str(Q(s[0])),"s1":str(Q(s[1])-Q(s[0]))}
    first=affine(a)
    # At knot t=1 both H1 fields are 2/3,-1/3 and H0=0.
    # Tail [1,2] has constant C>0,S<0; in quadrant II cos<=0, sin>=0.
    # At the two boundaries at least one term is strictly negative;
    # throughout the interior both terms are strictly negative.
    require(c[1:]==["2/3"]*3 and s[1:]==["-1/3"]*3,
            "TAIL_NOT_CONSTANT")
    require(first["strict_endpoint_values"][1]=="-1/3",
            "SOURCE_KNOT_POINT_DISCONTINUITY")
    require(Q(c[2])>0 and Q(s[2])<0, "TAIL_QUADRANT_SIGN_REFUSED")
    return {
        "schema":"radicadsac-pb00701-original-v12-complete-source-concavity/1.0",
        "original_case_id":V12_ID,
        "original_source_sha256":V12_SPEC_SHA,
        "original_row_sha256":V12_ROW_SHA,
        "v54_git_blob":V54_BLOB,
        "v2_git_blob":V2_BLOB,
        "first_piece":first,
        "tail": {"parameter_interval":["1","2"],"h0":"0","c":"2/3","s":"-1/3",
                 "method":"QUADRANT_II_STRICT_NEGATIVE",
                 "knot_at_1":"CONTINUOUS_NONZERO_NEGATIVE"},
        "whole_source": {
            "ordered_event_brackets":[["0","1/2"],["1/2","1"]],
            "orders":[1,1],
            "maximal_open_signs":["NEGATIVE","POSITIVE","NEGATIVE"],
            "root_count":2,
            "zero_at_knot":False
        },
        "historical_before_after":{"originals":121,"v54_refused":20,
                                   "v54_missing_ordered":30,"v2_complete":50},
        "historical_new_closures":0,
        "required_pb_po_discharges":0,
        "mc_b":"NOT_ESTABLISHED",
        "mc_1":"NOT_ESTABLISHED",
        "production_authorized":False
    }

def verify_receipt(receipt: dict, check_files: bool = True):
    require(type(receipt) is dict and
            canonical(receipt)==canonical(original_contract(check_files)),
            "RECEIPT_CLAIM_SUBSTITUTION")
    return True

class ProofTests(unittest.TestCase):
    def test_original_first_piece_and_whole_source(self):
        x=original_contract(False)
        self.assertEqual(x["whole_source"]["root_count"],2)
        self.assertEqual(x["first_piece"]["strict_concavity"]["min_slope_c1_minus_s1"],"1")
        self.assertEqual(x["first_piece"]["strict_concavity"]["coefficient_negative_lower_bound_M"],"1/3")
        self.assertEqual(x["first_piece"]["strict_midpoint_a_plus_b_sqrt2"],["0","1/6"])
        self.assertEqual(x["whole_source"]["maximal_open_signs"],
                         ["NEGATIVE","POSITIVE","NEGATIVE"])
    def test_nonzero_h0_positive_wronskian_orthogonal_admission(self):
        # C=t-3/5, S=2/5-t, h=3/10; W=C*S'-S*C'=+1/5,
        # so counter-rotating W<=0 in earlier #444 does NOT apply.
        spec={"h0":"3/10","h1":"0","c0":"-3/5","c1":"1",
              "s0":"2/5","s1":"-1"}
        x=affine(spec)
        self.assertEqual(x["orders"],[1,1])
        self.assertEqual(x["strict_endpoint_values"],["-3/10","-3/10"])
        self.assertEqual(Q(spec["c0"])*Q(spec["s1"])-
                         Q(spec["s0"])*Q(spec["c1"]),Q(1,5))
    def test_nonzero_affine_h0_admission(self):
        x=affine({"h0":"1/10","h1":"-1/10","c0":"-1/3",
                  "c1":"1","s0":"2/3","s1":"-1"})
        self.assertEqual(x["orders"],[1,1])
    def test_concavity_and_endpoint_refusals(self):
        a={"h0":"0","h1":"0","c0":"-1/3","c1":"1","s0":"2/3","s1":"-1"}
        for k,v in (("c1","1/4"),("s1","-1/4"),("h0","1"),
                    ("c0","-3/2"),("s0","-3/2")):
            with self.subTest(k=k), self.assertRaises(RefusedNontruth):
                affine({**a,k:v})
    def test_strict_midpoint_failure_and_exact_zero(self):
        a={"h0":"0","h1":"0","c0":"-1/3","c1":"1","s0":"2/3","s1":"-1"}
        with self.assertRaisesRegex(RefusedNontruth,"STRICT_POSITIVE_MIDPOINT"):
            affine({**a, "h0":"-1/4"})
        self.assertEqual(sign_sqrt2(Q(0),Q(0)),0)
        self.assertEqual(sign_sqrt2(Q(1),-Q(1)), -1)
        self.assertEqual(sign_sqrt2(Q(3,2),-Q(1)), 1)
        self.assertEqual(sign_sqrt2(-Q(3,2),Q(1)), -1)
        self.assertEqual(sign_sqrt2(-Q(1),Q(1)), 1)
    def test_wrong_types_and_rational_canonicality(self):
        a={"h0":"0","h1":"0","c0":"-1/3","c1":"1","s0":"2/3","s1":"-1"}
        for value in (0,0.0,"+1","1.0","1/0","01","-0","1/2/3"):
            with self.subTest(value=value), self.assertRaises(RefusedNontruth):
                affine({**a,"h0":value})
        with self.assertRaises(RefusedNontruth):
            affine({**a, "unexpected":"0"})
        with self.assertRaises(RefusedNontruth):
            affine({**a, "c0":str(2**513)})
    def test_frozen_source_hash_and_tail_knots(self):
        src=frozen_spec()
        self.assertEqual(hashlib.sha256(canonical(src)).hexdigest(),V12_SPEC_SHA)
        self.assertEqual(original_contract(False)["tail"]["knot_at_1"],
                         "CONTINUOUS_NONZERO_NEGATIVE")
    def test_canonical_replay_forgery_refusals(self):
        import copy
        original=original_contract(False)
        self.assertTrue(verify_receipt(original,False))
        for field,replacement in (("required_pb_po_discharges",True),
                                  ("historical_new_closures",1),
                                  ("production_authorized",True),
                                  ("mc_b","ESTABLISHED")):
            bad=copy.deepcopy(original)
            bad[field]=replacement
            with self.assertRaisesRegex(RefusedNontruth,"RECEIPT_CLAIM_SUBSTITUTION"):
                verify_receipt(bad,False)
        bad=copy.deepcopy(original)
        bad["first_piece"]["orders"]=[2,1]
        with self.assertRaises(RefusedNontruth):
            verify_receipt(bad,False)
    def test_duplicate_receipt_keys_and_bounded_json(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"t.json"
            path.write_text('{"a":1,"a":2}',encoding="utf-8")
            with self.assertRaises(RefusedNontruth):
                strict_json(path)
            path.write_text('{"single":"ok"}', encoding="utf-8")
            self.assertEqual(strict_json(path), {"single":"ok"})
            path.write_bytes(b" " * 401_000)
            with self.assertRaises(RefusedNontruth):
                strict_json(path)

    def test_actual_frozen_v54_v2_git_checkout_custody(self):
        """Original frozen source blobs, LF/CRLF, altered checkout and forged HEAD."""
        import tempfile
        originals = ((V54, V54_BLOB), (V2, V2_BLOB))
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            def git(*args):
                return subprocess.run(["git", *args], cwd=repo, check=True,
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.PIPE)
            git("init", "-q")
            git("config", "user.name", "MC-038 custody test")
            git("config", "user.email", "mc038@example.invalid")
            git("config", "core.autocrlf", "false")
            for source, pin in originals:
                committed = pinned_committed_bytes(
                    source, source.read_bytes(), pin, 400_000)
                require(git_blob_sha(committed) == pin, "PINNED_GIT_BLOB_MISMATCH")
                (repo/source.name).write_bytes(committed)
            git("add", V54.name, V2.name)
            git("commit", "-qm", "Seed exact original Git blob bytes")
            for source, pin in originals:
                path = repo/source.name
                raw = path.read_bytes()
                self.assertEqual(git_blob_sha(raw), pin)
                canonical_original = strict_json(path, expected_blob=pin)
                self.assertEqual(canonical_original,
                                 strict_json(source, expected_blob=pin))
                path.write_bytes(raw.replace(b"\n", b"\r\n"))
                self.assertEqual(strict_json(path, expected_blob=pin),
                                 canonical_original)
                for tampered in (
                    raw.replace(b'"schema"', b'"scheMa"', 1),
                    raw.replace(b"\n", b"\r\r\n"),
                    raw.replace(b'"schema":', b'"schema": 0, "schema":', 1)):
                    self.assertNotEqual(tampered, raw)
                    path.write_bytes(tampered)
                    with self.assertRaisesRegex(RefusedNontruth,
                                                "CHECKOUT_BYTES_MISMATCH"):
                        strict_json(path, expected_blob=pin)
                path.write_bytes(raw)
            bad = repo/V54.name
            bad.write_bytes(bad.read_bytes().replace(b'"schema"',
                                                     b'"scheMa"', 1))
            git("add", V54.name)
            git("commit", "-qm", "Adversarial changed committed source")
            with self.assertRaisesRegex(RefusedNontruth,
                                        "PINNED_GIT_BLOB_MISMATCH"):
                strict_json(bad, expected_blob=V54_BLOB)
            self.assertEqual(strict_json(repo/V2.name, expected_blob=V2_BLOB),
                             strict_json(V2, expected_blob=V2_BLOB))
            with self.assertRaisesRegex(RefusedNontruth,
                                        "PINNED_GIT_BLOB_MISMATCH"):
                strict_json(repo/V2.name, expected_blob=V54_BLOB)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true")
    group.add_argument("--contract",action="store_true")
    group.add_argument("--demo",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        run=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ProofTests))
        if not run.wasSuccessful():
            raise SystemExit(1)
    elif args.contract:
        verify_receipt(strict_json(RECEIPT,200_000),check_files=True)
        print("PASS original frozen V12, strict concavity, two simple events, tail, no gate promotion")
    else:
        print(json.dumps(original_contract(False),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
