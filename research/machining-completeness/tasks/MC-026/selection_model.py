#!/usr/bin/env python3
from __future__ import annotations

PRIMARY = "PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT"
CHALLENGER = "EXACT_CELL_SEMIALGEBRAIC_CONTROL"
INVALID = "INVALID_DOMAIN_OPERATION"
ALLOWED_GENERAL_TERMINALS = {
    "SUCCESS_CERTIFIED",
    "PB-007-01",
    "PB-007-02",
    "PB-007-03",
    "UNCERTIFIED",
    "RESOURCE_REFUSAL",
    "SEMANTIC_BLOCKER",
}
REQUIRED_OPERATIONS = {
    "lathe_od_turning","lathe_facing","lathe_shoulder","lathe_taper_chamfer_profile",
    "lathe_id_boring_internal","lathe_axial_drilling","lathe_grooving","lathe_parting_cutthrough",
    "lathe_form_turning","lathe_threading_synchronized","lathe_eccentric_turning","lathe_exact_retrace_finish",
    "mill_face","mill_slot_pocket_freehand","mill_drill_plunge","mill_ball_rounded_xyz",
    "mill_form_chamfer_countersink","mill_accessible_undercut","mill_thread_helix_fixed_axis",
    "mill_simultaneous_xyz","mill_retrace_self_cross_stationary","mill_cutthrough_multibody",
    "reclamp_reorient_continue","lathe_mill_lathe_history","machine_separated_retained_body",
    "complete_body_removal",
}
PHASE_OPS = {"lathe_threading_synchronized", "lathe_eccentric_turning"}
FORM_OPS = {"lathe_form_turning", "mill_form_chamfer_countersink", "mill_accessible_undercut", "mill_thread_helix_fixed_axis"}
BODY_TRANSITION_OPS = {"lathe_parting_cutthrough", "mill_cutthrough_multibody", "machine_separated_retained_body", "complete_body_removal"}
SETUP_OPS = {"reclamp_reorient_continue", "lathe_mill_lathe_history", "machine_separated_retained_body"}

def fast_candidate(operation_id: str) -> str | None:
    if operation_id not in REQUIRED_OPERATIONS:
        return None
    if operation_id in SETUP_OPS or operation_id in {"complete_body_removal"}:
        return None
    if operation_id.startswith("mill_"):
        if operation_id in {"mill_form_chamfer_countersink", "mill_accessible_undercut", "mill_thread_helix_fixed_axis"}:
            return "FP-FORM-BOX-UNION"
        return "FP-MILL-ANALYTIC-TRANSLATION"
    if operation_id.startswith("lathe_"):
        if operation_id in PHASE_OPS:
            return "FP-LATHE-PHASE-BOUNDED"
        return "FP-LATHE-AXISYMMETRIC"
    return None

def plan(request: dict) -> dict:
    op = request.get("operation_id")
    if op not in REQUIRED_OPERATIONS:
        return {"terminal": INVALID, "fast": None, "primary": None, "challenger": None}
    if not request.get("source_bound", True):
        return {"terminal": "INVALID_SOURCE", "fast": None, "primary": None, "challenger": None}
    if not request.get("common_frame_bound", True):
        return {"terminal": "INVALID_SOURCE", "fast": None, "primary": None, "challenger": None}
    f = fast_candidate(op) if request.get("fast_predicate_satisfied", False) else None
    challenger = CHALLENGER if request.get("semialgebraic_proved", False) else None
    return {
        "terminal": None,
        "fast": f,
        "primary": PRIMARY,
        "challenger": challenger,
        "requires_critical_event_service": bool(request.get("exact_zero_or_singular", False) or op in PHASE_OPS),
        "requires_body_state_machine": bool(op in BODY_TRANSITION_OPS or op in SETUP_OPS),
        "open_source_codec_gap": "PB-007-03" if op in FORM_OPS else None,
        "cycles_allowed": False,
        "max_fast_invocations": 1,
        "max_general_invocations": 1,
    }

def dispatch(
    request: dict,
    *,
    fast_result: str | None = None,
    fast_certificate: str | None = None,
    general_result: str = "UNCERTIFIED",
    challenger_result: str | None = None,
    accelerator_result: str | None = None,
) -> dict:
    p = plan(request)
    if p["terminal"] is not None:
        return {**p, "fast_invocations": 0, "general_invocations": 0, "challenger_evidence": challenger_result}
    fast_invocations = 0
    if p["fast"] is not None:
        fast_invocations = 1
        if fast_result == "SUCCESS" and fast_certificate == "ACCEPTED":
            return {
                **p,
                "terminal": "FAST_SUCCESS_CERTIFIED",
                "fast_invocations": 1,
                "general_invocations": 0,
                "challenger_evidence": challenger_result if p["challenger"] else None,
                "accelerator_is_authority": False,
            }
    if general_result not in ALLOWED_GENERAL_TERMINALS:
        raise ValueError(f"invalid general terminal: {general_result}")
    return {
        **p,
        "terminal": general_result,
        "fast_invocations": fast_invocations,
        "general_invocations": 1,
        "challenger_evidence": challenger_result if p["challenger"] else None,
        "accelerator_observation": accelerator_result,
        "accelerator_is_authority": False,
    }
