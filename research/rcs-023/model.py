#!/usr/bin/env python3
"""RCS-023 conservative uncertainty/error-budget algebra.

All bounds are deterministic Decimal millimetres.  The programme default is
interval/Minkowski composition.  Statistical RSS is diagnostic-only and is
unavailable without explicit independence evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from typing import Iterable, Mapping, Sequence
import math

getcontext().prec = 50
D = Decimal

COMPOSABLE_ERROR_CHANNELS = (
    "source_quantization",
    "trajectory_fit",
    "frame_translation",
    "frame_rotation",
    "tool_envelope",
    "numerical_algorithm",
    "fallback_representation",
    "reconciliation",
)

NON_ERROR_POLICY_CHANNELS = (
    "manufacturing_requirement",
    "contact_policy",
    "export_validation",
)

CHANNELS = COMPOSABLE_ERROR_CHANNELS + NON_ERROR_POLICY_CHANNELS

PROGRAMME_STATUS = (
    "decisively_no_material_change",
    "decisively_positive_material_change",
    "bounded_representation_inexact",
    "accepted_pending",
    "error_budget_breach",
    "refused_accuracy_unproven",
    "export_eligible",
)


class BudgetError(ValueError):
    """Raised when a trace attempts an unsafe/undefined budget operation."""


def dec(value: Decimal | str | int | float) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def decimal_text(value: Decimal) -> str:
    """Canonical non-exponent decimal text for machine-readable evidence."""
    if value == 0:
        return "0"
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@dataclass(frozen=True)
class Interval:
    low_mm: Decimal
    high_mm: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "low_mm", dec(self.low_mm))
        object.__setattr__(self, "high_mm", dec(self.high_mm))
        if self.low_mm > self.high_mm:
            raise BudgetError("interval lower bound exceeds upper bound")

    @classmethod
    def symmetric(cls, half_width_mm: Decimal | str | int | float) -> "Interval":
        half = dec(half_width_mm)
        if half < 0:
            raise BudgetError("symmetric half-width must be non-negative")
        return cls(-half, half)

    @classmethod
    def point(cls, value_mm: Decimal | str | int | float) -> "Interval":
        value = dec(value_mm)
        return cls(value, value)

    def __add__(self, other: "Interval") -> "Interval":
        return Interval(self.low_mm + other.low_mm, self.high_mm + other.high_mm)

    def scale(self, factor: Decimal | str | int | float) -> "Interval":
        f = dec(factor)
        a = self.low_mm * f
        b = self.high_mm * f
        return Interval(min(a, b), max(a, b))

    def shifted(self, nominal_mm: Decimal | str | int | float) -> "Interval":
        n = dec(nominal_mm)
        return Interval(self.low_mm + n, self.high_mm + n)

    @property
    def max_abs_mm(self) -> Decimal:
        return max(abs(self.low_mm), abs(self.high_mm))

    @property
    def width_mm(self) -> Decimal:
        return self.high_mm - self.low_mm

    def contains_zero(self) -> bool:
        return self.low_mm <= 0 <= self.high_mm

    def to_json(self) -> dict[str, str]:
        return {
            "low_mm": decimal_text(self.low_mm),
            "high_mm": decimal_text(self.high_mm),
            "max_abs_mm": decimal_text(self.max_abs_mm),
        }


ZERO = Interval.point(0)


@dataclass(frozen=True)
class Contribution:
    stage: str
    channel: str
    bound: Interval
    basis: str
    correlation: str = "unknown_or_conservative"
    provenance_ref: str | None = None

    def __post_init__(self) -> None:
        if self.channel not in CHANNELS:
            raise BudgetError(f"unknown uncertainty channel: {self.channel}")
        if self.channel not in COMPOSABLE_ERROR_CHANNELS:
            raise BudgetError(f"policy/requirement channel is not composable numerical error: {self.channel}")
        if not self.stage.strip() or not self.basis.strip():
            raise BudgetError("contribution stage and basis are required")

    def to_json(self, cumulative: Interval) -> dict[str, object]:
        return {
            "stage": self.stage,
            "channel": self.channel,
            "increment": self.bound.to_json(),
            "cumulative": cumulative.to_json(),
            "basis": self.basis,
            "correlation": self.correlation,
            "provenance_ref": self.provenance_ref,
        }


@dataclass
class BudgetTrace:
    trace_id: str
    durable_context: Mapping[str, object]
    contributions: list[Contribution] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_durable_context(self.durable_context)
        if not self.trace_id:
            raise BudgetError("trace_id is required")

    @property
    def interval(self) -> Interval:
        result = ZERO
        for item in self.contributions:
            result = result + item.bound
        return result

    def add(self, contribution: Contribution) -> None:
        self.contributions.append(contribution)

    def add_symmetric(
        self,
        *,
        stage: str,
        channel: str,
        half_width_mm: Decimal | str | int | float,
        basis: str,
        correlation: str = "unknown_or_conservative",
        provenance_ref: str | None = None,
    ) -> None:
        self.add(
            Contribution(
                stage=stage,
                channel=channel,
                bound=Interval.symmetric(half_width_mm),
                basis=basis,
                correlation=correlation,
                provenance_ref=provenance_ref,
            )
        )

    def add_rotation_bound(
        self,
        *,
        stage: str,
        radius_mm: Decimal | str | int | float,
        angle_nrad: Decimal | str | int | float,
        basis: str,
        provenance_ref: str | None = None,
    ) -> Decimal:
        radius = dec(radius_mm)
        angle = dec(angle_nrad)
        if radius < 0 or angle < 0:
            raise BudgetError("rotation radius/angle bounds must be non-negative")
        # For theta >= 0, chord displacement 2 r sin(theta/2) <= r theta.
        displacement = radius * angle * D("1e-9")
        self.add_symmetric(
            stage=stage,
            channel="frame_rotation",
            half_width_mm=displacement,
            basis=basis + "; conservative r*theta chord upper bound",
            provenance_ref=provenance_ref,
        )
        return displacement

    def mark_unresolved(self, reason: str) -> None:
        if not reason.strip():
            raise BudgetError("unresolved reason must be non-empty")
        self.unresolved.append(reason)

    def stages_json(self) -> list[dict[str, object]]:
        cumulative = ZERO
        out: list[dict[str, object]] = []
        for item in self.contributions:
            cumulative = cumulative + item.bound
            out.append(item.to_json(cumulative))
        return out

    def to_json(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "durable_context": dict(self.durable_context),
            "composition": "conservative_interval_minkowski_sum",
            "stages": self.stages_json(),
            "final_bound": self.interval.to_json(),
            "unresolved": list(self.unresolved),
        }


def validate_durable_context(context: Mapping[str, object]) -> None:
    """Keep provider-private identity out of durable programme evidence."""
    forbidden_fragments = (
        "topods",
        "kernel_handle",
        "provider_private",
        "process_id",
        "pointer",
    )
    for key in context:
        lowered = str(key).lower()
        if any(fragment in lowered for fragment in forbidden_fragments):
            raise BudgetError(f"provider-private identity forbidden in durable context: {key}")


def compose_conservative(intervals: Iterable[Interval]) -> Interval:
    result = ZERO
    for item in intervals:
        result = result + item
    return result


def rss_symmetric(
    bounds_mm: Sequence[Decimal | str | int | float],
    *,
    independence_evidence: str | None,
) -> Decimal:
    """Diagnostic RSS; prohibited as a correctness bound without evidence."""
    if not independence_evidence or not independence_evidence.strip():
        raise BudgetError("RSS requires explicit independence evidence")
    vals = [dec(v) for v in bounds_mm]
    if any(v < 0 for v in vals):
        raise BudgetError("RSS half-widths must be non-negative")
    # sqrt() is only diagnostic output, not used for programme acceptance.
    return D(str(math.sqrt(sum(float(v * v) for v in vals))))


def correlated_linear_bound(
    source_half_width_mm: Decimal | str | int | float,
    coefficients: Sequence[Decimal | str | int | float],
    *,
    shared_source_proof: str | None,
) -> Decimal:
    """Bound a proven shared source e * sum(coefficients).

    This is the only cancellation helper: callers must prove every term derives
    from the *same* bounded source.  Independent/unknown errors must use
    conservative interval composition instead.
    """
    if not shared_source_proof or not shared_source_proof.strip():
        raise BudgetError("correlated cancellation requires shared-source proof")
    half = dec(source_half_width_mm)
    if half < 0:
        raise BudgetError("source half-width must be non-negative")
    coeff_sum = sum((dec(c) for c in coefficients), D(0))
    return abs(coeff_sum) * half


def classify_contact(
    nominal_signed_gap_mm: Decimal | str | int | float,
    uncertainty: Interval,
) -> dict[str, object]:
    """Classify signed gap: negative=overlap, positive=clearance."""
    physical = uncertainty.shifted(nominal_signed_gap_mm)
    if physical.high_mm < 0:
        status = "decisively_positive_material_change"
        relation = "overlap"
    elif physical.low_mm > 0:
        status = "decisively_no_material_change"
        relation = "clear"
    else:
        status = "accepted_pending"
        relation = "contact_or_side_ambiguous"
    return {"status": status, "relation": relation, "physical_gap": physical.to_json()}


def classify_positive_removal(
    commanded_depth_mm: Decimal | str | int | float,
    uncertainty: Interval,
) -> dict[str, object]:
    depth = dec(commanded_depth_mm)
    if depth <= 0:
        raise BudgetError("positive-removal classifier requires depth > 0")
    physical = uncertainty.shifted(depth)
    if physical.low_mm > 0:
        status = "decisively_positive_material_change"
    else:
        # Never turn explicit positive intent into no material change merely
        # because the numerical uncertainty overlaps zero.
        status = "accepted_pending"
    return {
        "status": status,
        "commanded_positive_intent_preserved": True,
        "physical_depth": physical.to_json(),
    }


def semantic_no_change(*, proof: str | None) -> dict[str, object]:
    if not proof or not proof.strip():
        return {"status": "accepted_pending", "proof": None}
    return {"status": "decisively_no_material_change", "proof": proof}


def representation_status(
    *,
    representation_bound_mm: Decimal | str | int | float,
    representation_budget_mm: Decimal | str | int | float,
    reconciled: bool,
) -> str:
    bound = dec(representation_bound_mm)
    budget = dec(representation_budget_mm)
    if bound < 0 or budget < 0:
        raise BudgetError("representation bounds must be non-negative")
    if bound > budget:
        return "error_budget_breach"
    if not reconciled:
        return "bounded_representation_inexact"
    return "export_eligible"


def export_decision(
    trace: BudgetTrace,
    *,
    max_surface_deviation_mm: Decimal | str | int | float,
    max_dimension_error_mm: Decimal | str | int | float,
    reconciliation_complete: bool,
) -> dict[str, object]:
    surface = dec(max_surface_deviation_mm)
    dimension = dec(max_dimension_error_mm)
    if surface < 0 or dimension < 0:
        raise BudgetError("export budgets must be non-negative")
    final = trace.interval.max_abs_mm
    effective = min(surface, dimension)
    if trace.unresolved or not reconciliation_complete:
        status = "refused_accuracy_unproven"
    elif final > effective:
        status = "error_budget_breach"
    else:
        status = "export_eligible"
    return {
        "status": status,
        "final_max_abs_mm": decimal_text(final),
        "rsc005_mapping": {
            "max_surface_deviation_mm": decimal_text(surface),
            "max_dimension_error_mm": decimal_text(dimension),
            "effective_geometric_budget_mm": decimal_text(effective),
            "rule": "final propagated geometric uncertainty must be <= each declared RCS-005 geometric budget; unresolved channels refuse export",
        },
        "reconciliation_complete": reconciliation_complete,
        "unresolved": list(trace.unresolved),
    }


def affine_pipeline_bound(stages: Sequence[tuple[str, Decimal | str | int | float, Decimal | str | int | float]]) -> Decimal:
    """Propagate local symmetric error through ordered positive affine gains.

    Each tuple is (name, downstream_gain_at_stage, local_half_width_mm).
    The supplied gain is the already-known sensitivity from that stage to final
    output.  The function intentionally preserves stage order/sensitivity.
    """
    total = D(0)
    for _name, gain, local in stages:
        g = dec(gain)
        e = dec(local)
        if g < 0 or e < 0:
            raise BudgetError("affine gains/error bounds must be non-negative")
        total += g * e
    return total
