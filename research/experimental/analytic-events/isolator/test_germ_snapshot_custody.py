"""Original-parent F2/F3 source/receipt digest interleaving adversaries.

This test deliberately mutates the *caller's* plain Python source just as the
real admitted() calls json.dumps. Both producer and verifier must bind their
parsed root topology to the same owned input representation.
"""
import sys
import unittest
from test_algebraic_degree import doc as degree_doc
from test_kronecker_irreducibility import doc as kronecker_doc
import algebraic_degree as f2
import kronecker_irreducibility as f3


class GermSourceCustodyTests(unittest.TestCase):
    def check_current_parent(self, module, factory, args):
        original = factory()
        old_h0 = list(original["H0"])
        valid = module.certify(original, *args)
        self.assertEqual(valid["result"], "EXACT_ZERO")
        self.assertTrue(module.verify(original, valid))
        altered = factory()
        altered["H0"] = ["0/1"]
        zero_hash = module.admitted(altered)[2]
        self.assertNotEqual(valid["source_sha256"], zero_hash)
        self.assertEqual(module.certify(altered, *args)["result"], "IDENTICAL_ZERO_PIECE")

        def run_under_mutation(fn):
            source = factory()
            hits = []
            def trace(frame, event, arg):
                if (event == "call" and frame.f_code.co_name == "dumps"
                        and frame.f_globals.get("__name__") == "json"
                        and frame.f_back is not None
                        and frame.f_back.f_code.co_name == "admitted"):
                    source["H0"] = ["0/1"]
                    hits.append(True)
                    sys.settrace(None)
                return trace
            sys.settrace(trace)
            try:
                result = fn(source)
            finally:
                sys.settrace(None)
            self.assertEqual(len(hits), 1, "real original admitted() digest boundary not reached")
            self.assertEqual(source["H0"], ["0/1"])
            return result

        # A torn read used to emit original exact root with the zero-source
        # digest. That specific false identity binding must now be impossible.
        raced = run_under_mutation(lambda s: module.certify(s, *args))
        self.assertEqual(raced["result"], "EXACT_ZERO")
        self.assertEqual(raced["source_sha256"], valid["source_sha256"])
        self.assertNotEqual(raced["source_sha256"], zero_hash)

        # Even a caller presenting the known false digest cannot persuade the
        # REAL verify() at the same mutation point to authorize it.
        forged = dict(raced, source_sha256=zero_hash)
        self.assertFalse(run_under_mutation(lambda s: module.verify(s, forged)))
        # Immutable capture is not a host writer fence: a receipt for the
        # captured original is still legitimate if the caller mutates later.
        self.assertTrue(run_under_mutation(lambda s: module.verify(s, raced)))
        self.assertEqual(factory()["H0"], old_h0)

    def test_f2_prime_modular_germ_snapshot(self):
        self.check_current_parent(f2, lambda: degree_doc((-1, -1, 0, 1)),
                                  ((-1, -1, 0, 1), 2, ("1/1", "2/1")))

    def test_f3_kronecker_germ_snapshot(self):
        self.check_current_parent(f3, lambda: kronecker_doc((1, 0, -10, 0, 1)),
                                  ((1, 0, -10, 0, 1), ("3/1", "4/1")))


if __name__ == "__main__":
    unittest.main()
