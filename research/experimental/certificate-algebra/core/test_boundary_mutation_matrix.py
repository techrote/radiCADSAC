"""B1-D18: deterministic whole-consumer primitive mutation matrix.

Runs actual public replay and E1/E2/E3/E4/E5 verification entrypoints,
not isolated hash/equality helpers. Research Python model; no producer custody.
"""
from __future__ import annotations

import copy
import random
import unittest
from fractions import Fraction as Q

from certificate_algebra import Piece, Refusal, base_record, replay
from closed_nonzero import verify_closed_base, verify_closed_journal
from product_cone import product, verify_product
from refined_product import derive as refined_derive, verify as refined_verify
from rational_quotient import derive as quotient_derive, verify as quotient_verify
from quotient_sided_germ import derive as germ_derive, verify as germ_verify


MUTANTS = (None, True, False, [], {}, -3, 0, 1, 10**400,
           "", "0", "-0", "0/0", "1/2", "x"*5000,
           ["x"]*10, {"foo": "bar"})


def _locations(value, loc=()):
    yield loc
    if type(value) is dict:
        for key, child in value.items():
            yield from _locations(child, loc + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _locations(child, loc + (index,))


def _replace_value(original, location, replacement):
    result = copy.deepcopy(original)
    if not location:
        return copy.deepcopy(replacement)
    cursor = result
    for key in location[:-1]:
        cursor = cursor[key]
    cursor[location[-1]] = copy.deepcopy(replacement)
    return result


class ActualConsumerMutationMatrixTests(unittest.TestCase):
    def test_primitive_substitutions_across_actual_b1_consumers(self):
        # One real nonzero source, plus independently rederived E1/E3/E4/E5
        # records. Every submitted candidate begins as a valid real receipt.
        source = base_record((Piece(Q(0), Q(1), (Q(1), Q(1))),))
        pin = source["hash"]
        journal = {"schema": "b1-journal-v1", "base": source, "steps": []}
        _, product_receipt, _ = product(source, source,
                                         left_pin=pin, right_pin=pin)
        _, refined_receipt, _ = refined_derive(source, source,
                                               left_pin=pin, right_pin=pin)
        quotient_receipt, _ = quotient_derive(source, source,
                                              numerator_pin=pin, denominator_pin=pin)
        germ_receipt, _ = germ_derive(source, source, quotient_receipt,
                                     numerator_pin=pin, denominator_pin=pin,
                                     time="1/2")
        consumers = (
            ("B1 parent replay", journal, lambda x: replay(x)),
            ("E2 closed base", source,
             lambda x: verify_closed_base(x, source_pin=pin)),
            ("E2 closed journal", journal,
             lambda x: verify_closed_journal(x, base_pin=pin, final_pin=pin)),
            ("E1 product", product_receipt,
             lambda x: verify_product(source, source, x, left_pin=pin, right_pin=pin)),
            ("E3 refined product", refined_receipt,
             lambda x: refined_verify(source, source, x, left_pin=pin, right_pin=pin)),
            ("E4 quotient", quotient_receipt,
             lambda x: quotient_verify(source, source, x,
                                      numerator_pin=pin, denominator_pin=pin)),
            ("E5 sided germ", germ_receipt,
             lambda x: germ_verify(source, source, quotient_receipt, x,
                                   numerator_pin=pin, denominator_pin=pin,
                                   time="1/2")),
        )
        rng = random.Random(23114)
        tested = 0
        for name, valid, verify in consumers:
            verify(copy.deepcopy(valid))  # Real positive control.
            locations = tuple(_locations(valid))
            changed = 0
            for _ in range(500):
                loc = rng.choice(locations)
                replacement = rng.choice(MUTANTS)
                mutated = _replace_value(valid, loc, replacement)
                if mutated == valid:
                    continue
                changed += 1
                try:
                    verify(mutated)
                except Refusal:
                    pass
                except Exception as exc:
                    self.fail(f"{name} untyped {type(exc).__name__} at {loc}: {exc}")
                else:
                    self.fail(f"{name} ACCEPTED changed primitive at {loc}")
            self.assertGreaterEqual(changed, 350, name)
            tested += changed
        self.assertGreaterEqual(tested, 2450)


if __name__ == "__main__":
    unittest.main()
