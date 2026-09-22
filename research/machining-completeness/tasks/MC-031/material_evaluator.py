#!/usr/bin/env python3
"""Source-bound sweep-to-material integration for MC-031.

This module is deliberately a bounded authority-path integration layer.  It
loads and invokes the accepted MC-018..023 constructors directly; it does not
copy their geometry, replace them with labels, or promote adaptive sampling,
mesh/voxel accelerators, binary floating point, epsilon, timeout or backend
topology identity to material truth.

Point classification is only one ingredient of regularized material removal.
A closed cutter-sweep boundary is not itself positive-volume removal, so an
independently supplied exact positive-volume witness is required before an
INSIDE sweep classification may remove material.  Zero witness is touching
only.  General coupled phase/eccentric membership and universal form-source
encoding remain the inherited PB-007-02/PB-007-03 blockers.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from typing import Iterable, Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def _load(task: str, filename: str):
    path = ROOT / "research" / "machining-completeness" / "tasks" / task / filename
    name = f"radicadsac_{task.lower().replace('-', '_')}_{filename[:-3]}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load qualified constructor {path}")
    module = importlib.util.module_from_spec(spec)
    # dataclasses and some runtime annotations require the module to be visible
    # during execution.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MC018 = _load("MC-018", "fixed_axis_sweep.py")
MC019 = _load("MC-019", "ball_round_sweep.py")
MC020 = _load("MC-020", "form_undercut_sweep.py")
MC021 = _load("MC-021", "rotational_reduction.py")
MC022 = _load("MC-022", "phase_sensitive_lathe.py")
MC023 = _load("MC-023", "multi_setup.py")
MC026 = _load("MC-026", "selection_model.py")

PRIMARY = "PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT"
COMMON_FRAME = "workpiece_common"

TERMINAL_STATUSES = {
    "DECIDED",
    "CERTIFIED",
    "BLOCKED",
    "UNCERTIFIED",
    "RESOURCE_REFUSAL",
    "SEMANTIC_BLOCKER",
}

MILL_FLAT = {
    "mill_face",
    "mill_slot_pocket_freehand",
    "mill_drill_plunge",
    "mill_simultaneous_xyz",
    "mill_retrace_self_cross_stationary",
    "mill_cutthrough_multibody",
}
MILL_BALL = {"mill_ball_rounded_xyz"}
MILL_FORM = {
    "mill_form_chamfer_countersink",
    "mill_accessible_undercut",
    "mill_thread_helix_fixed_axis",
}
LATHE_PHASE = {"lathe_threading_synchronized", "lathe_eccentric_turning"}
LATHE_FORM = {"lathe_form_turning"}
LATHE_AXIS = {
    "lathe_od_turning",
    "lathe_facing",
    "lathe_shoulder",
    "lathe_taper_chamfer_profile",
    "lathe_id_boring_internal",
    "lathe_axial_drilling",
    "lathe_grooving",
    "lathe_parting_cutthrough",
    "lathe_exact_retrace_finish",
}
SETUP_HISTORY = {
    "reclamp_reorient_continue",
    "lathe_mill_lathe_history",
    "machine_separated_retained_body",
    "complete_body_removal",
}
BODY_TRANSITION_OPS = {
    "lathe_parting_cutthrough",
    "mill_cutthrough_multibody",
    "machine_separated_retained_body",
    "complete_body_removal",
}

# This manifest is an integration mapping, not a substitute geometry model.  A
# verifier checks it against MC-026's frozen 26-operation denominator, and the
# evaluator below imports/calls every named owner rather than reimplementing it.
CONSTRUCTOR_COVERAGE = {
    "lathe_od_turning": ("MC-021",),
    "lathe_facing": ("MC-021",),
    "lathe_shoulder": ("MC-021",),
    "lathe_taper_chamfer_profile": ("MC-021",),
    "lathe_id_boring_internal": ("MC-021",),
    "lathe_axial_drilling": ("MC-021",),
    "lathe_grooving": ("MC-021",),
    "lathe_parting_cutthrough": ("MC-021", "MC-023"),
    "lathe_form_turning": ("MC-020", "MC-021"),
    "lathe_threading_synchronized": ("MC-022",),
    "lathe_eccentric_turning": ("MC-022",),
    "lathe_exact_retrace_finish": ("MC-021",),
    "mill_face": ("MC-018",),
    "mill_slot_pocket_freehand": ("MC-018",),
    "mill_drill_plunge": ("MC-018",),
    "mill_ball_rounded_xyz": ("MC-019",),
    "mill_form_chamfer_countersink": ("MC-020",),
    "mill_accessible_undercut": ("MC-020",),
    "mill_thread_helix_fixed_axis": ("MC-020",),
    "mill_simultaneous_xyz": ("MC-018",),
    "mill_retrace_self_cross_stationary": ("MC-018",),
    "mill_cutthrough_multibody": ("MC-018", "MC-023"),
    "reclamp_reorient_continue": ("MC-023",),
    "lathe_mill_lathe_history": ("MC-021", "MC-018", "MC-023"),
    "machine_separated_retained_body": ("MC-023",),
    "complete_body_removal": ("MC-023",),
}


def q(value) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("material authority values must not be bool/binary float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"unsupported exact rational type: {type(value).__name__}")


def coverage_manifest() -> dict[str, tuple[str, ...]]:
    required = set(MC026.REQUIRED_OPERATIONS)
    mapped = set(CONSTRUCTOR_COVERAGE)
    if required != mapped:
        missing = sorted(required - mapped)
        extra = sorted(mapped - required)
        raise AssertionError(f"constructor denominator drift; missing={missing}, extra={extra}")
    qualified = {"MC-018", "MC-019", "MC-020", "MC-021", "MC-022", "MC-023"}
    for op, owners in CONSTRUCTOR_COVERAGE.items():
        if not owners or any(owner not in qualified for owner in owners):
            raise AssertionError(f"{op}: unqualified constructor owner")
    return dict(CONSTRUCTOR_COVERAGE)


def _terminal(status: str, **fields) -> dict:
    if status not in TERMINAL_STATUSES:
        raise ValueError(f"unknown terminal status: {status}")
    return {"status": status, **fields}


def _validate_binding(request: Mapping[str, object]) -> dict | None:
    op = request.get("operation_id")
    if op not in MC026.REQUIRED_OPERATIONS:
        return _terminal("SEMANTIC_BLOCKER", reason="OPERATION_OUTSIDE_FROZEN_DOMAIN")
    if request.get("source_bound") is not True:
        return _terminal("SEMANTIC_BLOCKER", reason="SOURCE_NOT_CANONICALLY_BOUND")
    if request.get("common_frame") != COMMON_FRAME:
        return _terminal("SEMANTIC_BLOCKER", reason="COMMON_FRAME_NOT_BOUND")
    if not request.get("input_revision"):
        return _terminal("SEMANTIC_BLOCKER", reason="MISSING_INPUT_REVISION")
    if not request.get("body_id"):
        return _terminal("SEMANTIC_BLOCKER", reason="MISSING_DURABLE_BODY_ID")
    if request.get("durable_identity_source") != "canonical_journal":
        return _terminal("SEMANTIC_BLOCKER", reason="BACKEND_TOPOLOGY_IS_NOT_DURABLE_IDENTITY")
    return None


def certified_error_bound(terms: Mapping[str, object]) -> Fraction:
    """Compose the full MC-058/MC-023 finite-cutter error without reset."""
    if not isinstance(terms, Mapping):
        raise TypeError("error_terms mapping is mandatory")
    required = ("inherited", "translation", "support_radius", "rotation_radians", "tool")
    missing = [key for key in required if key not in terms]
    if missing:
        raise ValueError(f"missing error terms: {','.join(missing)}")
    values = [q(terms[key]) for key in required]
    if any(value < 0 for value in values):
        raise ValueError("error terms must be non-negative")
    return MC023.actual_sweep_error_bound(*values)


def _positive_volume(request: Mapping[str, object]) -> Fraction:
    if "positive_volume_witness" not in request:
        raise ValueError("positive-volume witness is mandatory for removal")
    witness = q(request["positive_volume_witness"])
    if witness < 0:
        raise ValueError("positive-volume witness cannot be negative")
    return witness


def _removed_from_classification(classification: str, request: Mapping[str, object]) -> dict:
    if classification == "UNCERTIFIED":
        return _terminal(
            "UNCERTIFIED",
            relation="SWEEP_MEMBERSHIP_UNCERTIFIED",
            is_truth_value=False,
        )
    if classification == "OUTSIDE":
        return _terminal("DECIDED", relation="NOT_IN_SWEEP", removed=False)
    if classification != "INSIDE":
        raise ValueError(f"unknown sweep classifier result: {classification}")
    witness = _positive_volume(request)
    if witness == 0:
        return _terminal(
            "DECIDED",
            relation="TOUCHING_ONLY_NO_MATERIAL_TRANSITION",
            removed=False,
            positive_volume_witness="0",
        )
    return _terminal(
        "DECIDED",
        relation="REMOVED_POSITIVE_VOLUME",
        removed=True,
        positive_volume_witness=str(witness),
    )


def _mill_flat(request: Mapping[str, object]) -> dict:
    tool = request.get("tool")
    leaves = tuple(request.get("leaves") or ())
    if not isinstance(tool, (MC018.FlatEndMill, MC018.CornerRadiusEndMill)):
        return _terminal("SEMANTIC_BLOCKER", reason="MC018_TOOL_OBJECT_REQUIRED")
    if not leaves or not all(isinstance(leaf, MC018.Leaf) for leaf in leaves):
        return _terminal("SEMANTIC_BLOCKER", reason="MC018_SOURCE_LEAVES_REQUIRED")
    MC018.swept_path(leaves)
    classification = MC018.certified_classify(request.get("point"), tool, leaves)
    return _removed_from_classification(classification, request)


def _mill_ball(request: Mapping[str, object]) -> dict:
    tool = request.get("tool")
    leaves = tuple(request.get("leaves") or ())
    if not isinstance(tool, MC019.BallRoundEndMill):
        return _terminal("SEMANTIC_BLOCKER", reason="MC019_TOOL_OBJECT_REQUIRED")
    if not leaves or not all(isinstance(leaf, MC019.Leaf) for leaf in leaves):
        return _terminal("SEMANTIC_BLOCKER", reason="MC019_SOURCE_LEAVES_REQUIRED")
    MC019.swept_path(leaves)
    classification = MC019.certified_classify(request.get("point"), tool, leaves)
    return _removed_from_classification(classification, request)


def _mill_form(request: Mapping[str, object]) -> dict:
    if request.get("source_codec_complete") is not True:
        return _terminal(
            "BLOCKED",
            reason="UNIVERSAL_FORM_SOURCE_CODEC_NOT_ESTABLISHED",
            blocker="PB-007-03",
            is_truth_value=False,
        )
    tool = request.get("tool")
    leaves = tuple(request.get("leaves") or ())
    if not isinstance(tool, MC020.Tool):
        return _terminal("SEMANTIC_BLOCKER", reason="MC020_TOOL_OBJECT_REQUIRED")
    if not leaves or not all(isinstance(leaf, MC020.Leaf) for leaf in leaves):
        return _terminal("SEMANTIC_BLOCKER", reason="MC020_SOURCE_LEAVES_REQUIRED")
    MC020.swept_path(leaves)
    if request.get("operation_id") == "mill_accessible_undercut":
        approach = request.get("approach_points")
        obstacles = request.get("obstacles")
        if approach is None or obstacles is None:
            return _terminal("SEMANTIC_BLOCKER", reason="COMPLETE_TOOL_ACCESS_WITNESS_REQUIRED")
        if not MC020.access_is_clear(tool, approach, obstacles):
            return _terminal("SEMANTIC_BLOCKER", reason="COMPLETE_TOOL_OR_HOLDER_ACCESS_BLOCKED")
    classification = MC020.certified_classify(request.get("point"), tool, leaves)
    return _removed_from_classification(classification, request)


def _lathe_axisymmetric(request: Mapping[str, object]) -> dict:
    if request.get("operation_id") in LATHE_FORM:
        if request.get("source_codec_complete") is not True:
            return _terminal(
                "BLOCKED",
                reason="UNIVERSAL_FORM_SOURCE_CODEC_NOT_ESTABLISHED",
                blocker="PB-007-03",
                is_truth_value=False,
            )
        form_tool = request.get("form_tool")
        if not isinstance(form_tool, MC020.Tool) or form_tool.kind != "lathe_form_tool":
            return _terminal("SEMANTIC_BLOCKER", reason="MC020_LATHE_FORM_TOOL_REQUIRED")
    meta = request.get("axisymmetry_meta")
    if not isinstance(meta, Mapping):
        return _terminal("SEMANTIC_BLOCKER", reason="MC021_AXISYMMETRY_ADMISSION_EVIDENCE_REQUIRED")
    failures = MC021.admission_failures(meta)
    if failures:
        return _terminal(
            "BLOCKED",
            reason="GENERAL_COUPLED_PHASE_OR_NONAXISYMMETRIC_MEMBERSHIP_NOT_ESTABLISHED",
            blocker="PB-007-02",
            admission_failures=failures,
            is_truth_value=False,
        )
    rects = tuple(request.get("meridian_rects") or ())
    motion = request.get("motion")
    if not rects or not all(isinstance(rect, MC021.MeridianRect) for rect in rects):
        return _terminal("SEMANTIC_BLOCKER", reason="MC021_MERIDIAN_SWEEP_REQUIRED")
    if not isinstance(motion, MC021.Line2):
        return _terminal("SEMANTIC_BLOCKER", reason="MC021_SHARED_PARAMETER_MOTION_REQUIRED")
    r = q(request.get("r"))
    z = q(request.get("z"))
    hit = MC021.union_sweep_contains(rects, motion, r, z)
    return _removed_from_classification("INSIDE" if hit else "OUTSIDE", request)


def _phase_lathe(request: Mapping[str, object]) -> dict:
    op = request.get("operation_id")
    if request.get("bounded_phase_subtype") is not True:
        return _terminal(
            "BLOCKED",
            reason="GENERAL_COUPLED_SPINDLE_FEED_ECCENTRIC_MEMBERSHIP_NOT_ESTABLISHED",
            blocker="PB-007-02",
            is_truth_value=False,
        )
    if op == "lathe_eccentric_turning":
        law = request.get("eccentric_law")
        if not isinstance(law, MC022.EccentricLaw):
            return _terminal("SEMANTIC_BLOCKER", reason="MC022_ECCENTRIC_LAW_REQUIRED")
        # Construct the actual accepted symbolic placement to prove this request
        # enters through MC-022.  MC-022 intentionally supplies no universal
        # point-membership decision for the full eccentric history.
        law.symbolic_center(request.get("sample_t"))
        return _terminal(
            "BLOCKED",
            reason="ECCENTRIC_SYMBOLIC_SWEEP_MEMBERSHIP_REMAINS_GENERAL_COUPLED_CASE",
            blocker="PB-007-02",
            is_truth_value=False,
        )

    segment = request.get("timed_segment")
    if not isinstance(segment, MC022.TimedSegment):
        return _terminal("SEMANTIC_BLOCKER", reason="MC022_TIMED_SEGMENT_REQUIRED")
    event_bounds = request.get("event_bounds")
    if event_bounds is not None:
        if not isinstance(event_bounds, (tuple, list)) or len(event_bounds) != 4:
            return _terminal("SEMANTIC_BLOCKER", reason="INVALID_CERTIFIED_EVENT_BOUNDS")
        event = MC022.classify_certified_event(*event_bounds)
        if event == "TRANSCENDENTAL_EVENT_BLOCKER":
            return _terminal(
                "BLOCKED",
                reason="UNRESOLVED_TRANSCENDENTAL_EVENT",
                blocker="PB-007-01",
                is_truth_value=False,
            )
    hit = MC022.synchronized_band_removes(
        segment,
        request.get("body_theta_turns"),
        request.get("z"),
        request.get("radius"),
        request.get("axial_half_width"),
        request.get("final_radius"),
    )
    return _removed_from_classification("INSIDE" if hit else "OUTSIDE", request)


def compose_history(state, steps: Iterable[Mapping[str, object]]):
    """Execute a finite MC-023 preview without inferring topology/lineage."""
    if not isinstance(state, MC023.Workpiece):
        raise TypeError("MC023 Workpiece required")
    current = state
    for step in steps:
        kind = step.get("kind")
        if kind == "cut":
            cut = step.get("cut")
            if not isinstance(cut, MC023.Cut):
                raise TypeError("MC023 Cut required")
            if cut.provider not in {"MC-018", "MC-019", "MC-020", "MC-021", "MC-022"}:
                raise ValueError("cut provider must name a qualified sweep owner")
            current = MC023.apply_cut(current, cut)
        elif kind == "reclamp":
            setup = step.get("setup")
            if not isinstance(setup, MC023.Setup):
                raise TypeError("MC023 Setup required")
            if setup.inherited_error < current.setup.inherited_error:
                raise ValueError("re-clamp may not reset inherited error")
            op_id = step.get("operation_id")
            if not op_id:
                raise ValueError("re-clamp operation_id required")
            current = MC023.reclamp(current, op_id, setup)
        else:
            raise ValueError("history step must be cut or reclamp")
    return current


def _setup_or_history(request: Mapping[str, object]) -> dict:
    state = request.get("state")
    steps = tuple(request.get("history_steps") or ())
    if not isinstance(state, MC023.Workpiece):
        return _terminal("SEMANTIC_BLOCKER", reason="MC023_WORKPIECE_REQUIRED")
    if not steps:
        return _terminal("SEMANTIC_BLOCKER", reason="FINITE_MC023_HISTORY_REQUIRED")
    try:
        result = compose_history(state, steps)
    except (TypeError, ValueError) as exc:
        return _terminal("SEMANTIC_BLOCKER", reason="INVALID_MC023_HISTORY", detail=str(exc))
    op = request.get("operation_id")
    response = _terminal(
        "CERTIFIED",
        relation="FINITE_HISTORY_PREVIEW",
        input_revision=state.revision,
        output_revision=result.revision,
        durable_body_ids=[body.body_id for body in result.bodies],
        lineage_ids=[body.lineage_id for body in result.bodies],
        body_transition_committed=False,
    )
    if op in BODY_TRANSITION_OPS:
        response.update(
            status="BLOCKED",
            reason="DURABLE_CONNECTIVITY_TRANSITION_REQUIRES_MC033_CERTIFICATE",
            blocker="PB-007-04",
            next_owner="MC-033",
            is_truth_value=False,
        )
    return response


def evaluate_removed_point(request: Mapping[str, object]) -> dict:
    """Evaluate one source-bound material query through the qualified owner.

    Results are finite typed terminals.  A point result is not silently upgraded
    into a durable body/connectivity result; MC-033 owns that transition.
    """
    if not isinstance(request, Mapping):
        return _terminal("SEMANTIC_BLOCKER", reason="REQUEST_MAPPING_REQUIRED")
    binding_failure = _validate_binding(request)
    if binding_failure is not None:
        return binding_failure
    try:
        error = certified_error_bound(request.get("error_terms"))
    except (TypeError, ValueError) as exc:
        return _terminal("SEMANTIC_BLOCKER", reason="INVALID_OR_INCOMPLETE_ERROR_CERTIFICATE", detail=str(exc))

    op = request["operation_id"]
    try:
        if op in MILL_FLAT:
            result = _mill_flat(request)
        elif op in MILL_BALL:
            result = _mill_ball(request)
        elif op in MILL_FORM:
            result = _mill_form(request)
        elif op in LATHE_AXIS or op in LATHE_FORM:
            result = _lathe_axisymmetric(request)
        elif op in LATHE_PHASE:
            result = _phase_lathe(request)
        elif op in SETUP_HISTORY:
            result = _setup_or_history(request)
        else:
            return _terminal("SEMANTIC_BLOCKER", reason="MISSING_CONSTRUCTOR_ROUTING")
    except (TypeError, ValueError, RuntimeError, ArithmeticError) as exc:
        return _terminal("SEMANTIC_BLOCKER", reason="QUALIFIED_CONSTRUCTOR_REJECTED_REQUEST", detail=str(exc))

    result["selected_primary"] = PRIMARY
    result["qualified_owners"] = list(CONSTRUCTOR_COVERAGE[op])
    result["certified_error_bound"] = str(error)
    result["body_id"] = request["body_id"]
    result["input_revision"] = request["input_revision"]
    result["common_frame"] = COMMON_FRAME
    if op in BODY_TRANSITION_OPS and result.get("status") in {"DECIDED", "CERTIFIED"}:
        result["durable_transition_owner"] = "MC-033"
        result["body_transition_committed"] = False
    return result


def material_after(initial_state: str, result: Mapping[str, object]) -> dict:
    """Regularized monotone removal: machining never adds material."""
    if initial_state not in {"MATERIAL", "VOID"}:
        raise ValueError("initial state must be MATERIAL or VOID")
    status = result.get("status")
    if status not in TERMINAL_STATUSES:
        raise ValueError("unknown evaluator terminal")
    if status not in {"DECIDED", "CERTIFIED"}:
        return {"status": status, "material_state": "UNCERTIFIED", "source_result": dict(result)}
    relation = result.get("relation")
    if relation == "REMOVED_POSITIVE_VOLUME":
        return {"status": "DECIDED", "material_state": "VOID"}
    if relation in {
        "NOT_IN_SWEEP",
        "TOUCHING_ONLY_NO_MATERIAL_TRANSITION",
        "FINITE_HISTORY_PREVIEW",
    }:
        return {"status": "DECIDED", "material_state": initial_state}
    return {"status": "UNCERTIFIED", "material_state": "UNCERTIFIED", "reason": "RELATION_NOT_MATERIAL_COMMITTABLE"}


def resource_refusal(reason: str = "MATERIAL_EVALUATOR_BUDGET_EXHAUSTED") -> dict:
    return _terminal("RESOURCE_REFUSAL", reason=reason, is_truth_value=False)


def bind_material_certificate(
    *,
    input_digest: str,
    canonical_digest: str,
    sweep_digest: str,
    body_id: str,
    input_revision: str,
    configuration_digest: str,
    challenge_id: str,
    result: Mapping[str, object],
) -> dict:
    payload = {
        "schema": "radicadsac-mc031-material-certificate/1.0",
        "input_digest": input_digest,
        "canonical_digest": canonical_digest,
        "sweep_digest": sweep_digest,
        "body_id": body_id,
        "input_revision": input_revision,
        "configuration_digest": configuration_digest,
        "challenge_id": challenge_id,
        "result": dict(result),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["binding_sha256"] = sha256(raw).hexdigest()
    return payload


def verify_material_certificate(certificate: Mapping[str, object], **expected) -> bool:
    if not isinstance(certificate, Mapping):
        return False
    payload = {key: value for key, value in certificate.items() if key != "binding_sha256"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    if sha256(raw).hexdigest() != certificate.get("binding_sha256"):
        return False
    return all(certificate.get(key) == value for key, value in expected.items())


def terminal_status(result: Mapping[str, object]) -> str:
    status = result.get("status") if isinstance(result, Mapping) else None
    if status not in TERMINAL_STATUSES:
        raise ValueError("non-terminal or unknown material result")
    return status
