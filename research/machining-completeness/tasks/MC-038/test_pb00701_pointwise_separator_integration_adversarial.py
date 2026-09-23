#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction as F
import copy

import pb00701_pointwise_separator_integration_model as model
import pb00701_source_adaptive_separator_model as v30
import test_pb00701_source_adaptive_separator_adversarial as v30test


def run():
    # V31's exact diagnostic now obtains a source-owned v32 separator.  The
    # retained selected-harmonic amplitude derivatives (2 and 3) still make the
    # unchanged v30 full-residual orthant fail.  This is evidence of the next
    # limiting theorem, not permission to drop those residuals.
    diagnostic = model.integrate_pointwise_separator(
        {1: [2, 3]},
        {1: [1, 2]},
        F(1, 16),
        1,
        "SIN",
        1,
    )
    assert diagnostic["status"] == "BLOCKED", diagnostic
    assert diagnostic["reason"] == "V32_SEPARATOR_CERTIFIED_BUT_PRESERVED_V30_RESIDUAL_ORTHANT_BLOCKED"
    sep = diagnostic["v32_separator_certificate"]
    assert sep["status"] == "CERTIFIED" and model.v32.verify_binding(sep)
    assert F(sep["rational_separator"]) != F(5, 12)
    assert model.v32._compare_rational_alpha(F(sep["rational_separator"])) > 0
    residual = diagnostic["preserved_v30_residual_certificate"]
    assert residual["status"] == "BLOCKED", residual
    assert residual["reason"] == "SOURCE_ADAPTIVE_PROJECTIVE_RESIDUAL_STRICT_DOMINANCE_NOT_CERTIFIED"
    assert diagnostic["selected_harmonic_amplitude_derivatives_retained"] is True
    assert diagnostic["residual_contract_weakened"] is False

    # A second exact family exposes the same separation/residual distinction.
    # C=S=G has pointwise projective ratio exactly one, but G varies enough that
    # v30's separate global Bernstein floor/ceiling ratio is 16/49 < tan(pi/8).
    # V32 cancels the exact common factor and synthesizes a separator; the old
    # independent |C'|+|S'| envelope remains the blocker.
    g = [F(1), F(3, 2), F(9, 16)]  # (1+3s/4)^2
    old_sep = v30._source_adaptive_separator_certificate(g, g, "SIN", "COS")
    assert old_sep["status"] == "BLOCKED", old_sep
    assert old_sep["source_projective_ceiling"] == "16/49"
    common_factor = model.integrate_pointwise_separator(
        {1: g},
        {1: g},
        F(1, 16),
        1,
        "SIN",
        1,
    )
    assert common_factor["status"] == "BLOCKED", common_factor
    cf_sep = common_factor["v32_separator_certificate"]
    assert cf_sep["status"] == "CERTIFIED" and model.v32.verify_binding(cf_sep)
    assert cf_sep["reduced_dominant_polynomial"] == ["1"]
    assert cf_sep["reduced_transverse_polynomial"] == ["1"]
    assert common_factor["preserved_v30_residual_certificate"]["status"] == "BLOCKED"

    # Exact algebraic ordering controls remain exact and straddle sqrt(2)-1.
    assert model.v32._compare_rational_alpha(F(70, 169)) < 0
    assert model.v32._compare_rational_alpha(F(169, 408)) > 0

    # Orientation symmetry: the integration reaches the same source-owned
    # separator stage before the full residual boundary for COS dominance.
    cos_diagnostic = model.integrate_pointwise_separator(
        {1: [1, 2]},
        {1: [2, 3]},
        F(-1, 16),
        1,
        "COS",
        1,
    )
    assert cos_diagnostic["status"] == "BLOCKED", cos_diagnostic
    assert cos_diagnostic["v32_separator_certificate"]["status"] == "CERTIFIED"

    # Caller metadata and source-coordinate substitutions are not authority.
    try:
        model.integrate_pointwise_separator(
            {1: [2, 3]}, {1: [1, 2]}, F(1, 16), 1, "SIN", 1,
            caller_assertions={"separator": "5/12", "root_ordering": "above"},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("forged v33 integration metadata accepted")
    mismatch = model.integrate_pointwise_separator(
        {1: [2, 3]}, {1: [1, 2]}, F(1, 16), 1, "SIN", 1,
        source_parameter_id="independent-u",
    )
    assert mismatch["status"] == "SEMANTIC_BLOCKER"
    refused = model.integrate_pointwise_separator(
        {1: [2, 3]}, {1: [1, 2]}, F(1, 16), 1, "SIN", 1,
        force_resource_refusal=True,
    )
    assert refused["status"] == "RESOURCE_REFUSAL" and refused["is_truth_value"] is False

    # Binary floats remain rejected by the exact source machinery.
    try:
        model.integrate_pointwise_separator({1: [2.0, 3]}, {1: [1, 2]}, F(1, 16), 1, "SIN", 1)
    except TypeError:
        pass
    else:
        raise AssertionError("binary float accepted as exact v33 authority")

    # Complete v30 success precedence remains unchanged; v33 is not installed as
    # a replacement classifier in this blocker result.
    historical = v30test._fixture()
    historical_v30 = v30.classify_required_analytic_event(historical)
    assert historical_v30["status"] == "CERTIFIED", historical_v30
    historical_again = v30.classify_required_analytic_event(copy.deepcopy(historical))
    assert historical_again == historical_v30

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v33 pointwise separator integration adversarial diagnostics: PASS")


if __name__ == "__main__":
    run()
