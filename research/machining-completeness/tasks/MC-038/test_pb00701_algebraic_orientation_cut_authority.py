#!/usr/bin/env python3
from fractions import Fraction
from pathlib import Path
import copy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_algebraic_orientation_cut_model as model


def run_authority_controls():
    base = model.exact_algebraic_orientation_roots([-1, 0, 2], "AUTH")
    cert = base["irrational_open_roots"][0]

    bad_interval = copy.deepcopy(cert)
    bad_interval["isolating_interval"] = ["1/100", "1/50"]
    try:
        model.validate_algebraic_root_certificate(bad_interval)
    except (AssertionError, ValueError, TypeError):
        pass
    else:
        raise AssertionError("invalid isolation accepted")

    bad_poly = copy.deepcopy(cert)
    bad_poly["defining_square_free_polynomial"] = [-1, 0, 3]
    try:
        model.validate_algebraic_root_certificate(bad_poly)
    except (AssertionError, ValueError, TypeError):
        pass
    else:
        raise AssertionError("invalid defining polynomial accepted")

    try:
        model.exact_algebraic_orientation_roots([-1.0, 0, 2], "FLOAT")
    except (AssertionError, ValueError, TypeError):
        pass
    else:
        raise AssertionError("binary float accepted as exact authority")

    saved = model._sturm_open_root_count
    try:
        def refuse(*_args, **_kwargs):
            raise MemoryError("test")
        model._sturm_open_root_count = refuse
        result = model.exact_algebraic_orientation_roots(
            [Fraction(-1), Fraction(0), Fraction(2)], "REFUSAL"
        )
        assert result["status"] == "RESOURCE_REFUSAL", result
        assert result["is_truth_value"] is False
    finally:
        model._sturm_open_root_count = saved


if __name__ == "__main__":
    run_authority_controls()
