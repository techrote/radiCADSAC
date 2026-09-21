#!/usr/bin/env python3
from __future__ import annotations
from copy import deepcopy

GENERAL = "GENERAL_CERTIFIED_ROUTE"
INVALID = "INVALID_SOURCE"
SETUP_EVENT = "NON_CUTTING_SETUP_EVENT"

_FAST_IDS = {
    "FP-MILL-ANALYTIC-TRANSLATION",
    "FP-FORM-BOX-UNION",
    "FP-LATHE-AXISYMMETRIC",
    "FP-LATHE-PHASE-BOUNDED",
}
_GENERAL_TERMINALS = {
    "SUCCESS_CERTIFIED",
    "PB-007-01",
    "PB-007-02",
    "PB-007-03",
    "UNCERTIFIED",
    "RESOURCE_REFUSAL",
    "SEMANTIC_BLOCKER",
}


def _bound(request: dict) -> bool:
    return (
        request.get("source_bound") is True
        and request.get("common_frame_bound") is True
        and bool(request.get("body_id"))
        and bool(request.get("input_revision"))
        and request.get("engagement_bound") is True
        and request.get("setup_bound") is True
        and request.get("no_engaged_teleport") is True
        and request.get("transform_contract") == "RIGHT_HANDED_PARENT_FROM_CHILD"
    )


def _common_fast(request: dict) -> bool:
    return (
        _bound(request)
        and request.get("exact_source_kind") == "EXACT_RATIONAL"
        and request.get("body_transition_required") is False
        and request.get("singular_or_exact_zero_output_boundary") is False
    )


def _mill(request: dict) -> bool:
    return (
        _common_fast(request)
        and request.get("operation_family") in {"mill_flat", "mill_corner_radius", "mill_ball_round"}
        and request.get("fixed_axis") is True
        and request.get("motion_kind") in {"stationary", "line", "polyline"}
        and request.get("complete_finite_cutter_region") is True
        and request.get("mc058_uncertainty") == "ZERO"
    )


def _form(request: dict) -> bool:
    if not (
        _common_fast(request)
        and request.get("operation_family") in {"mill_form", "mill_accessible_undercut"}
        and request.get("fixed_axis") is True
        and request.get("motion_kind") in {"stationary", "line", "polyline"}
        and request.get("cutter_codec") == "EXACT_RATIONAL_BOX_UNION_V1"
        and request.get("complete_finite_cutter_region") is True
        and request.get("complete_holder_region") is True
        and request.get("mc058_uncertainty") == "ZERO"
    ):
        return False
    if request.get("operation_family") == "mill_accessible_undercut":
        return request.get("access_witness") == "COMPLETE_TOOL_CLEAR"
    return True


def _lathe_axisymmetric(request: dict) -> bool:
    return (
        _common_fast(request)
        and request.get("operation_family") in {"lathe_conventional", "lathe_form_tool"}
        and request.get("axisymmetric_target_certificate") is True
        and request.get("coaxial_setup") is True
        and request.get("phase_independent_meridian") is True
        and request.get("full_phase_orbit") is True
        and request.get("meridian_codec") == "EXACT_RATIONAL_RECTANGLES_V1"
        and request.get("phase_sensitive") is False
    )


def _lathe_phase(request: dict) -> bool:
    return (
        _common_fast(request)
        and request.get("operation_family") in {"lathe_threading_synchronized", "lathe_eccentric_turning"}
        and request.get("shared_exact_time_parameter") is True
        and request.get("unwrapped_spindle_phase") is True
        and request.get("phase_constructor") == "CERTIFIED_FINITE_EXACT_SUBTYPE"
        and request.get("transcendental_event_status") == "NONE"
        and request.get("complete_finite_cutter_region") is True
    )


def eligible_fast_paths(request: dict) -> list[str]:
    predicates = {
        "FP-MILL-ANALYTIC-TRANSLATION": _mill,
        "FP-FORM-BOX-UNION": _form,
        "FP-LATHE-AXISYMMETRIC": _lathe_axisymmetric,
        "FP-LATHE-PHASE-BOUNDED": _lathe_phase,
    }
    return [name for name, predicate in predicates.items() if predicate(request)]


def select_route(request: dict) -> str:
    if request.get("material_changing") is False and request.get("operation_family") == "reclamp":
        return SETUP_EVENT if _bound(request) else INVALID
    if not _bound(request):
        return INVALID
    candidates = eligible_fast_paths(request)
    if len(candidates) == 1:
        return candidates[0]
    return GENERAL


def _terminal_from_general(value: str) -> str:
    if value not in _GENERAL_TERMINALS:
        raise ValueError(f"invalid general-route terminal {value!r}")
    return value


def dispatch(
    request: dict,
    *,
    fast_result: str | None = None,
    certificate: str | None = None,
    general_result: str = "UNCERTIFIED",
) -> dict:
    before = deepcopy(request)
    route = select_route(request)
    result = {
        "selected_route": route,
        "terminal": None,
        "fast_invocations": 0,
        "general_invocations": 0,
        "fallback_reason": None,
    }
    if route == INVALID:
        result["terminal"] = INVALID
    elif route == SETUP_EVENT:
        result["terminal"] = SETUP_EVENT
    elif route == GENERAL:
        result["general_invocations"] = 1
        result["terminal"] = _terminal_from_general(general_result)
    else:
        assert route in _FAST_IDS
        result["fast_invocations"] = 1
        if fast_result == "SUCCESS" and certificate == "ACCEPTED":
            result["terminal"] = "FAST_SUCCESS_CERTIFIED"
        else:
            result["general_invocations"] = 1
            result["fallback_reason"] = (
                "SUCCESS_WITHOUT_INDEPENDENT_MATERIAL_CERTIFICATE"
                if fast_result == "SUCCESS"
                else (fast_result or "FAST_RESULT_UNAVAILABLE")
            )
            result["terminal"] = _terminal_from_general(general_result)
    assert request == before, "dispatch mutated canonical request"
    assert result["fast_invocations"] <= 1 and result["general_invocations"] <= 1
    return result
