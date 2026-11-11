"""D19 direct source-boundary regression: Unicode digit-like harmonic keys.

The receipt-integrity primitive validator correctly accepts builtin Unicode
strings as strings. The phase consumer must then REFUSE every non-ASCII
harmonic key without leaking int()'s ValueError from its A1 preflight.
"""
import unittest
from phase_bridge import Refusal, canonical, prove_equivalent, verify, digest
from test_phase_bridge import make


class UnicodeHarmonicKeyTests(unittest.TestCase):
    def test_nonascii_harmonic_keys_refuse_at_real_source_consumer(self):
        for key in ('²', '₃', '٣', '１', 'Ⅳ', '⁴', '\u0660'):
            with self.subTest(key=repr(key)):
                source = make('A1-470')
                source['terms'][key] = [['1'], ['0']]
                with self.assertRaises(Refusal):
                    canonical(source)
                with self.assertRaises(Refusal):
                    prove_equivalent(source, source)
        # Real verification must never admit a receipt for a source that
        # contains an unrecognized harmonic key, even under matching pins.
        legitimate = make('A1-470')
        valid = prove_equivalent(legitimate, legitimate)
        invalid = make('A1-470')
        invalid['terms']['²'] = [['1'], ['0']]
        with self.assertRaises(Refusal):
            verify(invalid, invalid, valid,
                   pinned_source_hash=digest(invalid),
                   pinned_target_hash=digest(invalid))

    def test_ascii_harmonics_still_admit_and_gaps_refuse(self):
        valid = make('A1-470', terms={
            '0': [['-1'], ['0']], '1': [['0'], ['1']],
            '2': [['1/2'], ['0']]})
        self.assertEqual(canonical(valid)['terms']['2'][0], ['1/2'])
        broken = make('A1-470', terms={
            '0': [['-1'], ['0']], '2': [['1/2'], ['0']]})
        with self.assertRaises(Refusal):
            canonical(broken)

if __name__ == '__main__':
    unittest.main()
