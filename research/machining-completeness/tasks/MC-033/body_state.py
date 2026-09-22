#!/usr/bin/env python3
"""MC-033 programme-owned durable material-body and lineage state machine.

This module commits body/lineage transitions only from source-bound, cryptographically
bound certificate objects. It deliberately does not infer durable identity from
backend/kernel topology, component order, size, proximity, tessellation IDs, or
floating tolerances. Regularized machining is pure removal: it may preserve a body,
split it, or exhaust it; it never merges previously distinct durable bodies or revives
an exhausted body.

The implementation is a bounded state/certificate layer. It consumes independently
certified material/connectivity facts; it does not claim to solve the still-open
universal topology/connectivity proof obligation (PB-007-04 / PO-07).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from hashlib import sha256
import json
from typing import Iterable, Mapping

ACTIVE = "ACTIVE"
EXHAUSTED = "EXHAUSTED"
SUPERSEDED = "SUPERSEDED"
BODY_STATUSES = {ACTIVE, EXHAUSTED, SUPERSEDED}

COMMITTED = "COMMITTED"
NONCOMMIT_TERMINALS = {"BLOCKED", "UNCERTIFIED", "RESOURCE_REFUSAL", "SEMANTIC_BLOCKER"}

TRANSITION_KINDS = {"CONTINUE", "SPLIT", "DISAPPEAR", "TOUCH_ONLY"}
IDENTITY_AUTHORITY = "canonical_journal"
COMMON_FRAME = "workpiece_common"

MATERIAL_SCHEMA = "radicadsac-mc031-material-certificate/1.0"
EVENT_SCHEMA = "radicadsac-mc032-event-certificate/1.0"
TRANSITION_SCHEMA = "radicadsac-mc033-lineage-transition/1.0"
CONNECTIVITY_SCHEMA = "radicadsac-mc033-connectivity-certificate/1.0"


def q(value) -> Fraction:
    """Exact authority scalar. Binary float/bool are never correctness authority."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("body-state authority values must not be bool/binary float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"unsupported exact rational type: {type(value).__name__}")


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def digest_json(value: object) -> str:
    return sha256(_canonical_json(value)).hexdigest()


def bind_certificate(payload: Mapping[str, object]) -> dict:
    """Return a copy of *payload* with a deterministic binding SHA-256."""
    out = dict(payload)
    out.pop("binding_sha256", None)
    out["binding_sha256"] = digest_json(out)
    return out


def verify_bound_certificate(certificate: Mapping[str, object], schema: str) -> bool:
    if not isinstance(certificate, Mapping) or certificate.get("schema") != schema:
        return False
    binding = certificate.get("binding_sha256")
    if not isinstance(binding, str):
        return False
    payload = {k: v for k, v in certificate.items() if k != "binding_sha256"}
    return digest_json(payload) == binding


@dataclass(frozen=True)
class DurableBody:
    body_id: str
    lineage_id: str
    status: str
    born_revision: str
    current_revision: str
    material_certificate_digest: str
    parent_body_id: str | None = None
    ended_revision: str | None = None

    def __post_init__(self) -> None:
        if not self.body_id or not self.lineage_id:
            raise ValueError("durable body and lineage IDs are mandatory")
        if self.status not in BODY_STATUSES:
            raise ValueError("invalid durable body status")
        if not self.born_revision or not self.current_revision:
            raise ValueError("body revisions are mandatory")
        if not self.material_certificate_digest:
            raise ValueError("material certificate digest is mandatory")
        if self.status == ACTIVE and self.ended_revision is not None:
            raise ValueError("active body cannot have ended_revision")
        if self.status != ACTIVE and not self.ended_revision:
            raise ValueError("inactive durable body must record ended_revision")


@dataclass(frozen=True)
class LineageEdge:
    transition_id: str
    parent_body_id: str
    parent_lineage_id: str
    child_body_id: str
    child_lineage_id: str
    revision: str

    def __post_init__(self) -> None:
        if not all((self.transition_id, self.parent_body_id, self.parent_lineage_id,
                    self.child_body_id, self.child_lineage_id, self.revision)):
            raise ValueError("lineage edge fields are mandatory")
        if self.parent_body_id == self.child_body_id:
            raise ValueError("same durable body continuity is not a lineage edge")


@dataclass(frozen=True)
class ContactRelation:
    revision: str
    body_a: str
    body_b: str
    certificate_digest: str

    def __post_init__(self) -> None:
        if not self.revision or not self.certificate_digest:
            raise ValueError("contact relation must be source/certificate bound")
        if not self.body_a or not self.body_b or self.body_a == self.body_b:
            raise ValueError("contact relation requires two distinct durable bodies")


@dataclass(frozen=True)
class BodyState:
    revision: str
    bodies: tuple[DurableBody, ...]
    lineage_edges: tuple[LineageEdge, ...] = ()
    contacts: tuple[ContactRelation, ...] = ()
    journal: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.revision:
            raise ValueError("state revision is mandatory")
        body_ids = [b.body_id for b in self.bodies]
        if len(body_ids) != len(set(body_ids)):
            raise ValueError("durable body IDs are globally unique and never reused")
        lineage_ids = [b.lineage_id for b in self.bodies]
        if len(lineage_ids) != len(set(lineage_ids)):
            raise ValueError("lineage node IDs are globally unique")

    def body(self, body_id: str) -> DurableBody:
        hits = [body for body in self.bodies if body.body_id == body_id]
        if len(hits) != 1:
            raise ValueError("durable target body must resolve exactly once")
        return hits[0]

    def active_body(self, body_id: str) -> DurableBody:
        body = self.body(body_id)
        if body.status != ACTIVE:
            raise ValueError("target durable body is not active material")
        return body

    def active_body_ids(self) -> tuple[str, ...]:
        return tuple(body.body_id for body in self.bodies if body.status == ACTIVE)

    def material_state(self) -> str:
        return "EMPTY_MATERIAL" if not self.active_body_ids() else "NONEMPTY_MATERIAL"


@dataclass(frozen=True)
class CommitResult:
    status: str
    state: BodyState
    reason: str | None = None
    transition_id: str | None = None

    @property
    def committed(self) -> bool:
        return self.status == COMMITTED


def initial_state(*, revision: str, bodies: Iterable[Mapping[str, str]]) -> BodyState:
    """Construct an explicit source-owned initial state; no backend IDs are consulted."""
    records = []
    for item in bodies:
        if item.get("identity_authority") != IDENTITY_AUTHORITY:
            raise ValueError("initial durable identity must come from canonical_journal")
        records.append(DurableBody(
            body_id=str(item["body_id"]),
            lineage_id=str(item["lineage_id"]),
            status=ACTIVE,
            born_revision=revision,
            current_revision=revision,
            material_certificate_digest=str(item["material_certificate_digest"]),
        ))
    return BodyState(revision=revision, bodies=tuple(records))


def _validate_upstream_material(certificate: Mapping[str, object], *, body_id: str,
                                input_revision: str) -> str | None:
    if not verify_bound_certificate(certificate, MATERIAL_SCHEMA):
        return "INVALID_MC031_MATERIAL_CERTIFICATE_BINDING"
    if certificate.get("body_id") != body_id or certificate.get("input_revision") != input_revision:
        return "STALE_OR_WRONG_MC031_BODY_REVISION_BINDING"
    result = certificate.get("result")
    if not isinstance(result, Mapping) or result.get("status") not in {"DECIDED", "CERTIFIED"}:
        return "MC031_RESULT_NOT_COMMITTABLE"
    return None


def _validate_upstream_event(certificate: Mapping[str, object], *, input_revision: str) -> str | None:
    if not verify_bound_certificate(certificate, EVENT_SCHEMA):
        return "INVALID_MC032_EVENT_CERTIFICATE_BINDING"
    decision = certificate.get("decision")
    if not isinstance(decision, Mapping) or decision.get("status") not in {"DECIDED", "CERTIFIED"}:
        return "MC032_EVENT_NOT_COMMITTABLE"
    if decision.get("input_revision") not in (None, input_revision):
        return "STALE_MC032_EVENT_REVISION"
    return None


def _validate_connectivity(certificate: Mapping[str, object], *, kind: str,
                           target_body_id: str, input_revision: str,
                           material_digest: str, event_digest: str | None) -> str | None:
    if not verify_bound_certificate(certificate, CONNECTIVITY_SCHEMA):
        return "INVALID_CONNECTIVITY_CERTIFICATE_BINDING"
    if certificate.get("proof_status") != "PROVED":
        return "CONNECTIVITY_NOT_INDEPENDENTLY_PROVED"
    if certificate.get("checker_authority") in {None, "candidate", "provider", "backend_topology"}:
        return "CONNECTIVITY_CHECKER_NOT_INDEPENDENT"
    expected = {
        "transition_kind": kind,
        "target_body_id": target_body_id,
        "input_revision": input_revision,
        "material_certificate_digest": material_digest,
    }
    for key, value in expected.items():
        if certificate.get(key) != value:
            return f"CONNECTIVITY_CERTIFICATE_{key.upper()}_MISMATCH"
    if event_digest is not None and certificate.get("event_certificate_digest") != event_digest:
        return "CONNECTIVITY_EVENT_BINDING_MISMATCH"
    if certificate.get("identity_authority") != IDENTITY_AUTHORITY:
        return "CONNECTIVITY_CERTIFICATE_USES_NONCANONICAL_IDENTITY"
    return None


def _output_plan(certificate: Mapping[str, object]) -> list[Mapping[str, object]]:
    outputs = certificate.get("outputs")
    if not isinstance(outputs, list):
        raise ValueError("transition outputs must be an explicit list")
    if any(not isinstance(item, Mapping) for item in outputs):
        raise ValueError("transition output entries must be mappings")
    return outputs


def _validate_common(certificate: Mapping[str, object], state: BodyState) -> tuple[str | None, DurableBody | None]:
    if not verify_bound_certificate(certificate, TRANSITION_SCHEMA):
        return "INVALID_MC033_TRANSITION_CERTIFICATE_BINDING", None
    if certificate.get("status") in NONCOMMIT_TERMINALS:
        return str(certificate.get("status")), None
    if certificate.get("status") != "CERTIFIED":
        return "TRANSITION_NOT_CERTIFIED", None
    if certificate.get("kind") not in TRANSITION_KINDS:
        return "UNSUPPORTED_OR_FORBIDDEN_TRANSITION_KIND", None
    if certificate.get("identity_authority") != IDENTITY_AUTHORITY:
        return "BACKEND_OR_HEURISTIC_IDENTITY_AUTHORITY_FORBIDDEN", None
    if certificate.get("common_frame") != COMMON_FRAME:
        return "COMMON_FRAME_NOT_BOUND", None
    if certificate.get("input_revision") != state.revision:
        return "STALE_OR_WRONG_INPUT_REVISION", None
    output_revision = certificate.get("output_revision")
    if not isinstance(output_revision, str) or not output_revision or output_revision == state.revision:
        return "DISTINCT_OUTPUT_REVISION_REQUIRED", None
    target_id = certificate.get("target_body_id")
    if not isinstance(target_id, str) or not target_id:
        return "TARGET_BODY_ID_REQUIRED", None
    try:
        target = state.active_body(target_id)
    except ValueError:
        return "TARGET_BODY_NOT_ACTIVE_OR_NOT_UNIQUE", None
    if certificate.get("target_lineage_id") != target.lineage_id:
        return "TARGET_LINEAGE_MISMATCH", None
    if any(certificate.get(name) in (None, "") for name in (
        "transition_id", "operation_id", "source_digest", "canonical_digest",
        "challenge_id", "configuration_digest"
    )):
        return "INCOMPLETE_SOURCE_OR_CHALLENGE_BINDING", None
    return None, target


def commit_transition(state: BodyState, certificate: Mapping[str, object]) -> CommitResult:
    """Validate and commit one immutable transition; rejection preserves *state* exactly."""
    if not isinstance(state, BodyState) or not isinstance(certificate, Mapping):
        return CommitResult("SEMANTIC_BLOCKER", state, "STATE_AND_CERTIFICATE_REQUIRED")

    common_error, target = _validate_common(certificate, state)
    if common_error in NONCOMMIT_TERMINALS:
        return CommitResult(common_error, state, "UPSTREAM_NON_SUCCESS_TERMINAL")
    if common_error:
        return CommitResult("SEMANTIC_BLOCKER", state, common_error)
    assert target is not None

    material = certificate.get("material_certificate")
    if not isinstance(material, Mapping):
        return CommitResult("SEMANTIC_BLOCKER", state, "MC031_MATERIAL_CERTIFICATE_REQUIRED")
    material_error = _validate_upstream_material(material, body_id=target.body_id, input_revision=state.revision)
    if material_error:
        return CommitResult("SEMANTIC_BLOCKER", state, material_error)
    material_digest = digest_json(material)
    if certificate.get("material_certificate_digest") != material_digest:
        return CommitResult("SEMANTIC_BLOCKER", state, "MATERIAL_CERTIFICATE_DIGEST_MISMATCH")

    kind = str(certificate["kind"])
    event = certificate.get("event_certificate")
    event_digest = None
    if kind in {"SPLIT", "DISAPPEAR", "TOUCH_ONLY"}:
        if not isinstance(event, Mapping):
            return CommitResult("SEMANTIC_BLOCKER", state, "MC032_EVENT_CERTIFICATE_REQUIRED")
        event_error = _validate_upstream_event(event, input_revision=state.revision)
        if event_error:
            return CommitResult("SEMANTIC_BLOCKER", state, event_error)
        event_digest = digest_json(event)
        if certificate.get("event_certificate_digest") != event_digest:
            return CommitResult("SEMANTIC_BLOCKER", state, "EVENT_CERTIFICATE_DIGEST_MISMATCH")

    connectivity = certificate.get("connectivity_certificate")
    if not isinstance(connectivity, Mapping):
        return CommitResult("SEMANTIC_BLOCKER", state, "INDEPENDENT_CONNECTIVITY_CERTIFICATE_REQUIRED")
    connectivity_error = _validate_connectivity(
        connectivity,
        kind=kind,
        target_body_id=target.body_id,
        input_revision=state.revision,
        material_digest=material_digest,
        event_digest=event_digest,
    )
    if connectivity_error:
        status = "BLOCKED" if connectivity_error == "CONNECTIVITY_NOT_INDEPENDENTLY_PROVED" else "SEMANTIC_BLOCKER"
        return CommitResult(status, state, connectivity_error)
    connectivity_digest = digest_json(connectivity)
    if certificate.get("connectivity_certificate_digest") != connectivity_digest:
        return CommitResult("SEMANTIC_BLOCKER", state, "CONNECTIVITY_CERTIFICATE_DIGEST_MISMATCH")

    try:
        removed = q(certificate.get("positive_new_removal", "0"))
        if removed < 0:
            raise ValueError("negative removal witness")
        outputs = _output_plan(certificate)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        return CommitResult("SEMANTIC_BLOCKER", state, f"INVALID_EXACT_TRANSITION_DATA:{exc}")

    if kind == "CONTINUE":
        return _commit_continue(state, target, certificate, outputs, removed, material_digest)
    if kind == "SPLIT":
        return _commit_split(state, target, certificate, outputs, removed, material_digest, connectivity_digest)
    if kind == "DISAPPEAR":
        return _commit_disappear(state, target, certificate, outputs, removed, material_digest)
    if kind == "TOUCH_ONLY":
        return _commit_touch(state, target, certificate, outputs, removed, connectivity_digest)
    return CommitResult("SEMANTIC_BLOCKER", state, "UNREACHABLE_TRANSITION_KIND")


def _validate_output_entry(item: Mapping[str, object], *, parent: DurableBody,
                           existing_ids: set[str], existing_lineages: set[str]) -> tuple[str | None, Fraction | None]:
    required = ("body_id", "lineage_id", "role", "component_certificate_id",
                "material_certificate_digest", "identity_authority", "positive_volume_witness")
    if any(item.get(key) in (None, "") for key in required):
        return "INCOMPLETE_OUTPUT_IDENTITY_OR_COMPONENT_BINDING", None
    if item.get("identity_authority") != IDENTITY_AUTHORITY:
        return "OUTPUT_IDENTITY_NOT_CANONICAL", None
    try:
        positive = q(item["positive_volume_witness"])
    except (TypeError, ValueError, ZeroDivisionError):
        return "INVALID_OUTPUT_VOLUME_WITNESS", None
    if positive <= 0:
        return "OUTPUT_BODY_MUST_HAVE_POSITIVE_VOLUME_WITNESS", None
    role = item.get("role")
    body_id = str(item["body_id"])
    lineage_id = str(item["lineage_id"])
    if role == "CONTINUATION":
        if body_id != parent.body_id or lineage_id != parent.lineage_id:
            return "CONTINUATION_MUST_RETAIN_PARENT_BODY_AND_LINEAGE", None
    elif role == "DESCENDANT":
        if body_id == parent.body_id or lineage_id == parent.lineage_id:
            return "DESCENDANT_MUST_USE_FRESH_BODY_AND_LINEAGE_IDS", None
        if body_id in existing_ids or lineage_id in existing_lineages:
            return "DURABLE_ID_OR_LINEAGE_REUSE_FORBIDDEN", None
    else:
        return "OUTPUT_ROLE_MUST_BE_CONTINUATION_OR_DESCENDANT", None
    return None, positive


def _next_state(state: BodyState, *, output_revision: str, bodies: tuple[DurableBody, ...],
                transition_id: str, edges: tuple[LineageEdge, ...] = (),
                contacts: tuple[ContactRelation, ...] = ()) -> BodyState:
    return BodyState(
        revision=output_revision,
        bodies=bodies,
        lineage_edges=state.lineage_edges + edges,
        contacts=state.contacts + contacts,
        journal=state.journal + (transition_id,),
    )


def _commit_continue(state: BodyState, target: DurableBody, cert: Mapping[str, object],
                     outputs: list[Mapping[str, object]], removed: Fraction,
                     material_digest: str) -> CommitResult:
    if len(outputs) != 1:
        return CommitResult("SEMANTIC_BLOCKER", state, "CONTINUE_REQUIRES_EXACTLY_ONE_OUTPUT")
    item = outputs[0]
    error, _ = _validate_output_entry(item, parent=target,
                                      existing_ids={b.body_id for b in state.bodies},
                                      existing_lineages={b.lineage_id for b in state.bodies})
    if error or item.get("role") != "CONTINUATION":
        return CommitResult("SEMANTIC_BLOCKER", state, error or "CONTINUE_OUTPUT_MUST_BE_CONTINUATION")
    if item.get("material_certificate_digest") != material_digest:
        return CommitResult("SEMANTIC_BLOCKER", state, "CONTINUE_MATERIAL_BINDING_MISMATCH")
    output_revision = str(cert["output_revision"])
    updated = replace(target, current_revision=output_revision,
                      material_certificate_digest=material_digest)
    bodies = tuple(updated if body.body_id == target.body_id else body for body in state.bodies)
    next_state = _next_state(state, output_revision=output_revision, bodies=bodies,
                             transition_id=str(cert["transition_id"]))
    return CommitResult(COMMITTED, next_state, transition_id=str(cert["transition_id"]))


def _commit_split(state: BodyState, target: DurableBody, cert: Mapping[str, object],
                  outputs: list[Mapping[str, object]], removed: Fraction,
                  material_digest: str, connectivity_digest: str) -> CommitResult:
    if removed <= 0:
        return CommitResult("SEMANTIC_BLOCKER", state, "SPLIT_REQUIRES_POSITIVE_NEW_REMOVAL")
    if len(outputs) < 2:
        return CommitResult("SEMANTIC_BLOCKER", state, "SPLIT_REQUIRES_AT_LEAST_TWO_POSITIVE_OUTPUT_BODIES")
    output_body_ids = [str(item.get("body_id", "")) for item in outputs]
    output_lineages = [str(item.get("lineage_id", "")) for item in outputs]
    if len(output_body_ids) != len(set(output_body_ids)) or len(output_lineages) != len(set(output_lineages)):
        return CommitResult("SEMANTIC_BLOCKER", state, "SPLIT_OUTPUT_IDS_MUST_BE_UNIQUE")

    existing_ids = {b.body_id for b in state.bodies}
    existing_lineages = {b.lineage_id for b in state.bodies}
    continuation_count = 0
    for item in outputs:
        error, _ = _validate_output_entry(item, parent=target, existing_ids=existing_ids,
                                          existing_lineages=existing_lineages)
        if error:
            return CommitResult("SEMANTIC_BLOCKER", state, error)
        if item["role"] == "CONTINUATION":
            continuation_count += 1
        elif item["material_certificate_digest"] != material_digest:
            return CommitResult("SEMANTIC_BLOCKER", state, "DESCENDANT_MATERIAL_BINDING_MISMATCH")
    if continuation_count > 1:
        return CommitResult("SEMANTIC_BLOCKER", state, "AT_MOST_ONE_PARENT_CONTINUATION_ALLOWED")

    connectivity = cert["connectivity_certificate"]
    if connectivity.get("component_count") != len(outputs):
        return CommitResult("SEMANTIC_BLOCKER", state, "CERTIFIED_COMPONENT_COUNT_MISMATCH")
    if connectivity.get("complete_remainder_partition") is not True:
        return CommitResult("BLOCKED", state, "REMAINDER_PARTITION_NOT_PROVED_COMPLETE")
    if connectivity.get("pairwise_interior_disjoint") is not True:
        return CommitResult("BLOCKED", state, "REMAINDER_COMPONENT_INTERIORS_NOT_PROVED_DISJOINT")
    certified_components = set(connectivity.get("component_certificate_ids") or [])
    planned_components = {str(item["component_certificate_id"]) for item in outputs}
    if certified_components != planned_components:
        return CommitResult("SEMANTIC_BLOCKER", state, "OUTPUT_COMPONENT_CERTIFICATE_SET_MISMATCH")

    output_revision = str(cert["output_revision"])
    new_records: list[DurableBody] = []
    edges: list[LineageEdge] = []
    if continuation_count:
        continuation = next(item for item in outputs if item["role"] == "CONTINUATION")
        replacement = replace(target, current_revision=output_revision,
                              material_certificate_digest=str(continuation["material_certificate_digest"]))
    else:
        replacement = replace(target, status=SUPERSEDED, current_revision=output_revision,
                              material_certificate_digest=material_digest, ended_revision=output_revision)

    for item in outputs:
        if item["role"] == "CONTINUATION":
            continue
        child = DurableBody(
            body_id=str(item["body_id"]),
            lineage_id=str(item["lineage_id"]),
            status=ACTIVE,
            born_revision=output_revision,
            current_revision=output_revision,
            material_certificate_digest=str(item["material_certificate_digest"]),
            parent_body_id=target.body_id,
        )
        new_records.append(child)
        edges.append(LineageEdge(
            transition_id=str(cert["transition_id"]),
            parent_body_id=target.body_id,
            parent_lineage_id=target.lineage_id,
            child_body_id=child.body_id,
            child_lineage_id=child.lineage_id,
            revision=output_revision,
        ))

    bodies = tuple(replacement if body.body_id == target.body_id else body for body in state.bodies) + tuple(new_records)
    next_state = _next_state(state, output_revision=output_revision, bodies=bodies,
                             transition_id=str(cert["transition_id"]), edges=tuple(edges))
    return CommitResult(COMMITTED, next_state, transition_id=str(cert["transition_id"]))


def _commit_disappear(state: BodyState, target: DurableBody, cert: Mapping[str, object],
                      outputs: list[Mapping[str, object]], removed: Fraction,
                      material_digest: str) -> CommitResult:
    if outputs:
        return CommitResult("SEMANTIC_BLOCKER", state, "DISAPPEAR_MUST_HAVE_NO_POSITIVE_OUTPUT_BODY")
    try:
        residual = q(cert.get("residual_positive_volume", "0"))
    except (TypeError, ValueError, ZeroDivisionError):
        return CommitResult("SEMANTIC_BLOCKER", state, "INVALID_RESIDUAL_VOLUME")
    if residual != 0:
        return CommitResult("SEMANTIC_BLOCKER", state, "POSITIVE_RESIDUAL_CANNOT_BE_ROUNDED_TO_EMPTY")
    connectivity = cert["connectivity_certificate"]
    if connectivity.get("exact_empty_material") is not True:
        return CommitResult("BLOCKED", state, "EXACT_EMPTY_MATERIAL_NOT_INDEPENDENTLY_PROVED")
    if connectivity.get("component_count") != 0:
        return CommitResult("SEMANTIC_BLOCKER", state, "EMPTY_STATE_MUST_HAVE_ZERO_COMPONENTS")
    output_revision = str(cert["output_revision"])
    exhausted = replace(target, status=EXHAUSTED, current_revision=output_revision,
                        material_certificate_digest=material_digest, ended_revision=output_revision)
    bodies = tuple(exhausted if body.body_id == target.body_id else body for body in state.bodies)
    next_state = _next_state(state, output_revision=output_revision, bodies=bodies,
                             transition_id=str(cert["transition_id"]))
    return CommitResult(COMMITTED, next_state, transition_id=str(cert["transition_id"]))


def _commit_touch(state: BodyState, target: DurableBody, cert: Mapping[str, object],
                  outputs: list[Mapping[str, object]], removed: Fraction,
                  connectivity_digest: str) -> CommitResult:
    if removed != 0:
        return CommitResult("SEMANTIC_BLOCKER", state, "TOUCH_ONLY_MUST_HAVE_ZERO_NEW_REMOVAL")
    if outputs:
        return CommitResult("SEMANTIC_BLOCKER", state, "TOUCH_ONLY_CANNOT_CREATE_OR_REPLACE_BODY_IDS")
    event = cert["event_certificate"]
    decision = event.get("decision", {})
    if decision.get("relation") != "TOUCHING_ONLY_NO_MATERIAL_TRANSITION":
        return CommitResult("SEMANTIC_BLOCKER", state, "EVENT_CERTIFICATE_IS_NOT_TOUCH_ONLY")
    other_id = cert.get("other_body_id")
    if not isinstance(other_id, str) or not other_id:
        return CommitResult("SEMANTIC_BLOCKER", state, "TOUCH_ONLY_REQUIRES_OTHER_DURABLE_BODY")
    if other_id == target.body_id:
        return CommitResult("SEMANTIC_BLOCKER", state, "SELF_CONTACT_IS_NOT_BODY_IDENTITY_EVIDENCE")
    try:
        state.active_body(other_id)
    except ValueError:
        return CommitResult("SEMANTIC_BLOCKER", state, "OTHER_TOUCH_BODY_NOT_ACTIVE")
    output_revision = str(cert["output_revision"])
    updated = replace(target, current_revision=output_revision)
    bodies = tuple(updated if body.body_id == target.body_id else body for body in state.bodies)
    contact = ContactRelation(output_revision, target.body_id, other_id, connectivity_digest)
    next_state = _next_state(state, output_revision=output_revision, bodies=bodies,
                             transition_id=str(cert["transition_id"]), contacts=(contact,))
    return CommitResult(COMMITTED, next_state, transition_id=str(cert["transition_id"]))


def finite_history(initial: BodyState, certificates: Iterable[Mapping[str, object]]) -> CommitResult:
    """Commit an ordered finite history; first non-success stops without partial next-step mutation."""
    state = initial
    last_id = None
    for certificate in certificates:
        result = commit_transition(state, certificate)
        if not result.committed:
            return result
        state = result.state
        last_id = result.transition_id
    return CommitResult(COMMITTED, state, transition_id=last_id)
