#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import pb00701_algebraic_separator_foundation_model as v32  # noqa: E402

V33_ROUTE = "EXACT_V32_SEPARATOR_V30_RESIDUAL_ORTHANT_INTEGRATION"


def integrate_pointwise_separator(
    cos_polys,
    sin_polys,
    phase_rate,
    harmonic,
    dominant,
    dominant_sign,
    *,
    source_parameter_id="s",
    caller_assertions=None,
    force_resource_refusal=False,
):
    """Integrate the v32 source-owned separator into the unchanged v30 residual proof.

    This helper deliberately does not weaken the residual envelope.  A successful
    result means v32 synthesized and source-bound the separator and every existing
    v30 projective/residual orthant remained strictly positive.  Failure of the
    residual orthants remains PB-007-01 evidence rather than being laundered into
    event authority.
    """
    if caller_assertions:
        raise ValueError("caller separator/root/critical-value/margin assertions are non-authoritative")
    if source_parameter_id != "s":
        return {
            "status": "SEMANTIC_BLOCKER",
            "reason": "SOURCE_PARAMETER_MISMATCH",
            "blocker": "PB-007-01",
        }
    if force_resource_refusal:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": "PB00701_V33_FORCED_EXACT_RESOURCE_REFUSAL",
            "is_truth_value": False,
        }

    harmonic = int(harmonic)
    dominant_sign = int(dominant_sign)
    rate = v30.q(phase_rate)
    c = v30._trim(cos_polys.get(harmonic, [0]))
    s = v30._trim(sin_polys.get(harmonic, [0]))
    if harmonic <= 0 or rate == 0 or dominant_sign not in (-1, 1) or c == [0] or s == [0]:
        return {
            "status": "BLOCKED",
            "reason": "V33_SELECTED_HARMONIC_STRUCTURE_NOT_ELIGIBLE",
            "blocker": "PB-007-01",
        }

    if dominant == "SIN":
        d, t = s, c
    elif dominant == "COS":
        d, t = c, s
    else:
        raise ValueError("dominant must be SIN or COS")

    separator = v32.synthesize_separator(
        d,
        t,
        dominant_sign,
        source_parameter_id=source_parameter_id,
    )
    if separator.get("status") != "CERTIFIED":
        return {
            "status": separator.get("status", "BLOCKED"),
            "reason": separator.get("reason", "V32_SOURCE_OWNED_SEPARATOR_NOT_CERTIFIED"),
            "blocker": None if separator.get("status") == "RESOURCE_REFUSAL" else "PB-007-01",
            "v32_separator_certificate": separator,
            **({"is_truth_value": False} if separator.get("status") == "RESOURCE_REFUSAL" else {}),
        }
    if not v32.verify_binding(separator):
        return {
            "status": "SEMANTIC_BLOCKER",
            "reason": "V32_SOURCE_BINDING_VERIFICATION_FAILED",
            "blocker": "PB-007-01",
        }

    combined = v30._projective_orthant_certificate(
        cos_polys,
        sin_polys,
        rate,
        harmonic,
        dominant,
        dominant_sign,
        separator["rational_separator"],
    )
    if combined is None:
        return {
            "status": "BLOCKED",
            "reason": "V30_PROJECTIVE_RESIDUAL_ORTHANT_UNAVAILABLE",
            "blocker": "PB-007-01",
            "v32_separator_certificate": separator,
        }
    if combined.get("status") != "CERTIFIED":
        return {
            "status": combined.get("status", "BLOCKED"),
            "reason": "V32_SEPARATOR_CERTIFIED_BUT_PRESERVED_V30_RESIDUAL_ORTHANT_BLOCKED",
            "blocker": None if combined.get("status") == "RESOURCE_REFUSAL" else "PB-007-01",
            "v32_separator_certificate": separator,
            "preserved_v30_residual_certificate": combined,
            "selected_harmonic_amplitude_derivatives_retained": True,
            "residual_contract_weakened": False,
            **({"is_truth_value": False} if combined.get("status") == "RESOURCE_REFUSAL" else {}),
        }

    return {
        "status": "CERTIFIED",
        "relation": V33_ROUTE,
        "v32_separator_certificate": separator,
        "preserved_v30_residual_certificate": combined,
        "selected_harmonic_amplitude_derivatives_retained": True,
        "residual_contract_weakened": False,
        "caller_metadata_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
        "finite_termination": "v32 finite algebraic separator synthesis followed by finite v30 exact sign-orthant enumeration",
    }


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V33_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
