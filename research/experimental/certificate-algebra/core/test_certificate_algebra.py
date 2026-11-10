"""Independent standard-library adversarial and finite-family tests for B1-C1/C2."""
import copy
import unittest
from dataclasses import replace as dataclass_replace
from fractions import Fraction as Q

from certificate_algebra import (
    Piece, Refusal, EvidenceMeter, affine, base_record, bernstein,
    concatenate, events, kind, piece, prove, replay, replace, split,
    verify_base, Verified, Certificate, snapshot_hash,
)


def verified(*ps):
    m = EvidenceMeter()
    raw = base_record(tuple(ps))
    return verify_base(raw["pieces"],raw["receipts"],m)


class CertificateAlgebraTests(unittest.TestCase):
    def test_unverified_dataclass_cannot_inject_false_sign_into_transform(self):
        # A public dataclass was previously enough to skip check_leaf and make
        # split/affine proclaim POS for 1-2u, whose true interior root is 1/2.
        p = Piece(Q(0), Q(1), (Q(1), Q(-2)))
        false = Certificate(p.hash, "POS", (Q(1), Q(1)))
        with self.assertRaises(Refusal):
            Verified((p,), (false,), 0, snapshot_hash((p,), 0))
        with self.assertRaises(Refusal):
            verify_base([p.source()], [false.record()], EvidenceMeter())
        # The actual verified public base/journal path continues to work.
        genuine = Piece(Q(0), Q(1), (Q(1),))
        checked = verified(genuine)
        with self.assertRaises(Refusal):
            dataclass_replace(checked, pieces=(p,), certs=(false,))
        self.assertEqual([c.sign for c in split(checked, 0, Q(1, 3), EvidenceMeter()).certs],
                         ["POS", "POS"])

    def test_tangent_crossing_and_identity_continuum(self):
        # x^2 at 0, -x^2 at 1, identity-zero [2,3]: signs and zero sets exact.
        s = verified(Piece(Q(0),Q(1),(Q(0),Q(1),Q(-1))),
                     Piece(Q(1),Q(2),(Q(0),Q(1),Q(-1))),
                     Piece(Q(2),Q(3),(Q(0),)))
        e = events(s)
        self.assertEqual(e["identity_intervals"],[["2","3"]])
        self.assertEqual(e["isolated_points"],[{"time":"0","kind":"BOUNDARY","left":None,"right":"POS"},
                                                 {"time":"1","kind":"TOUCH","left":"POS","right":"POS"}])
        full = verified(Piece(Q(0),Q(1),(Q(0),)),Piece(Q(1),Q(2),(Q(0),)))
        self.assertEqual(events(full)["identity_intervals"],[["0","2"]])
        cross = verified(Piece(Q(0),Q(1),(Q(-1),Q(1))),Piece(Q(1),Q(2),(Q(0),Q(1))))
        self.assertEqual(events(cross)["isolated_points"][0]["kind"],"CROSS")
        reverse = affine(cross,Q(5),Q(-1),EvidenceMeter())
        self.assertEqual(events(reverse)["isolated_points"][0],
                         {"time":"4","kind":"CROSS","left":"POS","right":"NEG"})

    def test_infinite_family_constructive_sampling_independent_exact_evaluation(self):
        # Parametric infinite family 1+c*u*(1-u), c>=0 rational.
        for a in range(1,15):
            for d in range(1,9):
                c=Q(a,d)
                p=Piece(Q(-5),Q(7),(Q(1),c,-c))
                self.assertEqual(kind(bernstein(p)),"POS")
                s=verified(p)
                self.assertEqual(events(s),{"identity_intervals":[],"isolated_points":[]})
                for k in range(1,11):
                    t=Q(-5)+12*Q(k,11)
                    self.assertGreater(p.at(t),0)

    def test_subdivide_and_reversal_exact_all_rational_points(self):
        s=verified(Piece(Q(-3),Q(7),(Q(1),Q(8),Q(-8))))
        for cut in [Q(1,19),Q(3),Q(9,2)]:
            m=EvidenceMeter()
            child=split(s,0,cut,m)
            self.assertEqual(m.full_leaf_checks,0)
            self.assertEqual(child.pieces[0].right,child.pieces[1].left)
            for k in range(0,41):
                t=Q(-3)+10*Q(k,40)
                found=next(p for p in child.pieces if p.left<=t<=p.right)
                self.assertEqual(found.at(t),s.pieces[0].at(t))
            r=affine(child,Q(13,5),Q(-7,3),EvidenceMeter())
            self.assertEqual([c.sign for c in r.certs],["POS","POS"])
            for k in range(0,41):
                t=Q(-3)+10*Q(k,40)
                x=(t-Q(13,5))/Q(-7,3)
                transformed=next(p for p in r.pieces if p.left<=x<=p.right)
                self.assertEqual(transformed.at(x),s.pieces[0].at(t))
            roundtrip=affine(r,-Q(13,5)/Q(-7,3),1/Q(-7,3),EvidenceMeter())
            self.assertEqual([(p.left,p.right,p.coeff) for p in roundtrip.pieces],[(p.left,p.right,p.coeff) for p in child.pieces])

    def test_single_owned_update_reuses_unchanged_receipts(self):
        ps=tuple(Piece(Q(i),Q(i+1),(Q(1),)) for i in range(32))
        s=verified(*ps)
        meter=EvidenceMeter()
        for k in range(64):
            s2=replace(s,k%32,(Q(1),Q(k+1,16),-Q(k+1,16)),meter)
            self.assertEqual([c.source_hash for j,c in enumerate(s2.certs) if j!=k%32],
                             [c.source_hash for j,c in enumerate(s.certs) if j!=k%32])
            s=s2
        self.assertEqual(meter.full_leaf_checks,64)
        self.assertEqual(meter.seam_checks,124)
        self.assertEqual(events(s),{"identity_intervals":[],"isolated_points":[]})
        # Baseline full rescan costs 32 initial + 32 * 64 after updates.
        self.assertEqual(32+meter.full_leaf_checks,96)
        self.assertEqual(32*(1+64),2080)

    def test_independent_journal_replay_and_tamper(self):
        ps=(Piece(Q(0),Q(1),(Q(1),Q(2),Q(-2))),Piece(Q(1),Q(2),(Q(1),)))
        b=base_record(ps)
        log={"schema":"b1-journal-v1","base":b,"steps":[]}
        s,_=replay(log)
        def add(d,fn):
            nonlocal s
            op={"before":s.hash,**d}
            out=fn(s)
            op["after"]=out.hash
            log["steps"].append(op)
            s=out
        add({"op":"split","index":0,"cut":"1/2"},lambda st: split(st,0,Q(1,2),EvidenceMeter()))
        add({"op":"affine","offset":"3","rate":"-2"},lambda st: affine(st,Q(3),Q(-2),EvidenceMeter()))
        add({"op":"replace","index":1,"coeff":["1","3/2","-1"]},lambda st: replace(st,1,(Q(1),Q(3,2),Q(-1)),EvidenceMeter()))
        fresh,meter=replay(log)
        self.assertEqual(fresh.hash,s.hash)
        self.assertEqual(meter.full_leaf_checks,3) # two base + one changed only
        self.assertEqual(meter.transform_checks,4) # split 1 + affine 3 pieces
        # The exact count on every path is checked below; no invented speedup timing.
        for modify in [lambda l:l["base"]["pieces"][0]["coeff"].__setitem__(0,"-1"),
                       lambda l:l["base"]["receipts"][0].__setitem__("sign","NEG"),
                       lambda l:l["steps"][0].__setitem__("cut","3/2"),
                       lambda l:l["steps"][1].__setitem__("rate","2"),
                       lambda l:l["steps"][2].__setitem__("before","0"*64),
                       lambda l:l["steps"][2].__setitem__("coeff",["-1"])]:
            wrong=copy.deepcopy(log)
            modify(wrong)
            with self.assertRaises(Refusal): replay(wrong)

    def test_unsafe_cases_fail_closed(self):
        bad=[Piece(Q(0),Q(1),(Q(-1,2),Q(1))),  # genuine interior root
             Piece(Q(0),Q(1),(Q(1,4),Q(-1),Q(1)))] # quadratic tangent zero at 1/2
        for p in bad:
            with self.assertRaises(Refusal): prove(p,EvidenceMeter())
        with self.assertRaises(Refusal): verified(Piece(Q(0),Q(1),(Q(1),)),Piece(Q(1),Q(2),(Q(2),)))
        with self.assertRaises(Refusal): piece({"left":"0","right":"1","coeff":["0.0"]})
        with self.assertRaises(Refusal): piece({"left":"-0","right":"1","coeff":["1"]})
        with self.assertRaises(Refusal): piece({"left":"0","right":"1","coeff":["2/2"]})
        with self.assertRaises(Refusal): piece({"left":"0","right":"1","coeff":["1"],"forged":1})
        with self.assertRaises(Refusal): Piece(Q(0),Q(1),(Q(1),Q(0)))

    def test_transform_closures_refuse_oversized_verified_snapshots(self):
        # Base admission allows exactly 512 cells, but the old split and
        # concatenate closures minted 513-cell Verified states. Journal replay
        # would inherit the same budget bypass.
        ps = tuple(Piece(Q(i), Q(i + 1), (Q(1),)) for i in range(512))
        boundary = verified(*ps)
        self.assertEqual(len(boundary.pieces), 512)
        with self.assertRaisesRegex(Refusal, "cardinality"):
            split(boundary, 0, Q(1, 2), EvidenceMeter())
        neighbor = verified(Piece(Q(512), Q(513), (Q(1),)))
        with self.assertRaisesRegex(Refusal, "cardinality"):
            concatenate(boundary, neighbor, EvidenceMeter())
        # The actual untrusted journal replay must enforce the same budget;
        # a consistent 513-piece `after` hash cannot authorize enlargement.
        source = base_record(ps)
        l = Piece(Q(0), Q(1, 2), (Q(1),))
        r = Piece(Q(1, 2), Q(1), (Q(1),))
        oversized_hash = snapshot_hash((l, r) + ps[1:], 0)
        log = {"schema": "b1-journal-v1", "base": source,
               "steps": [{"before": source["hash"], "after": oversized_hash,
                          "op": "split", "index": 0, "cut": "1/2"}]}
        with self.assertRaisesRegex(Refusal, "cardinality"):
            replay(log)
        # A legitimate smaller closure must remain available.
        small = verified(Piece(Q(0), Q(1), (Q(1),)))
        self.assertEqual(len(split(small, 0, Q(1, 2), EvidenceMeter()).pieces), 2)
        self.assertEqual(len(concatenate(small, verified(Piece(Q(1), Q(2), (Q(1),))), EvidenceMeter()).pieces), 2)

    def test_explicit_concatenation_is_only_static_continuous(self):
        left=verified(Piece(Q(0),Q(1),(Q(1),)))
        right=verified(Piece(Q(1),Q(3),(Q(1),Q(2),Q(-2))))
        c=concatenate(left,right,EvidenceMeter())
        self.assertEqual(len(c.pieces),2)
        self.assertEqual(events(c)["isolated_points"],[])
        bad=verified(Piece(Q(1),Q(3),(Q(2),)))
        with self.assertRaises(Refusal): concatenate(left,bad,EvidenceMeter())

if __name__=="__main__": unittest.main()
