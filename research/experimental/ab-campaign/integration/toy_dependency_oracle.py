#!/usr/bin/env python3
"""Finite adversaries for B5 dependency-certificate seam (model only).

Does not execute CyberSand native code or certify a production solver.
"""
from itertools import product
import unittest

WIDTH = 6


def radius_one_dependencies(i):
    return frozenset(j for j in (i - 1, i, i + 1) if 0 <= j < WIDTH)


def local_next(state, i):
    # Deliberately simple deterministic local rule.
    return (sum(state[j] for j in radius_one_dependencies(i)) % 2)


def local_all(state):
    return tuple(local_next(state, i) for i in range(WIDTH))


def reuse(old_state, new_state, old_outputs, dependency):
    changed = {i for i in range(WIDTH) if old_state[i] != new_state[i]}
    return tuple(old_outputs[i] if changed.isdisjoint(dependency[i])
                 else local_next(new_state, i) for i in range(WIDTH))


class DependencyCertificateTests(unittest.TestCase):
    def test_all_one_bit_updates_reuse_exactly(self):
        dependency = tuple(radius_one_dependencies(i) for i in range(WIDTH))
        for state in product((0, 1), repeat=WIDTH):
            old = local_all(state)
            for change_at in range(WIDTH):
                new_state = tuple(1 - v if i == change_at else v
                                  for i, v in enumerate(state))
                self.assertEqual(local_all(new_state),
                                 reuse(state, new_state, old, dependency))

    def test_global_pressure_like_dependency_breaks_locality(self):
        # A remote cell contributes to a shared global field. A local halo
        # is not a valid dependency certificate for this derived quantity.
        old = (0,) * WIDTH
        new = (0, 0, 0, 0, 0, 1)
        far_cell = 0
        local_dependencies = radius_one_dependencies(far_cell)
        self.assertTrue(set(range(WIDTH)).difference(local_dependencies))
        self.assertTrue({5}.isdisjoint(local_dependencies))
        global_field = lambda state: sum(state) % 3
        self.assertNotEqual(global_field(old), global_field(new))

    def test_two_step_influence_exceeds_one_cell_halo(self):
        old = (0,) * WIDTH
        new = (0, 0, 0, 1, 0, 0)
        self.assertEqual(local_next(old, 1), local_next(new, 1))
        second_old = local_all(local_all(old))
        second_new = local_all(local_all(new))
        self.assertNotEqual(second_old[1], second_new[1])

    def test_aba_requires_history_or_epoch_when_observable(self):
        # Same visible cell value, but two events occurred and matter to
        # a history-dependent observer. Cell-state equality is insufficient.
        before = (0, 0)
        after = (0, 2)  # (visible value, accumulated events)
        self.assertEqual(before[0], after[0])
        self.assertNotEqual(before[1], after[1])


if __name__ == "__main__":
    unittest.main()
