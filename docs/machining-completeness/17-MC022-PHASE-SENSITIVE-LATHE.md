# MC-022 phase-sensitive and synchronized lathe sweeps

Status: **finite source-faithful timed constructors established; general transcendental event/membership blockers remain open.**

MC-022 covers the lathe operations that MC-021 must reject from its axisymmetric full-orbit quotient: synchronized/threading histories and eccentric turning whose material result depends on spindle/feed phase.

## Shared-time rule

Every admitted phase-sensitive source piece retains one exact chronology. Tool/cutter state, axial/radial feed and **unwrapped spindle phase** are evaluated from the same exact time parameter. A provider may subdivide that chronology at exact semantic boundaries, but it may not replace it with the Cartesian product of independently chosen path and phase values.

Modulo-one phase is sufficient only for periodic geometric comparison at a known source time. It is not allowed to erase turn count, chronology, engagement order or synchronization.

Saved source operations, exact engagement endpoints, setup/tool/target identities and semantic knots remain immutable. Derived sweep representations do not become journal authority.

## Synchronized/threading constructor

The bounded exact control uses affine rational timed segments. A body-fixed azimuth `theta` aligns with machine angle zero when

```text
phase(t) + theta = integer turns
```

For nonzero affine spindle advance over a finite interval, the relevant integer range is finite, so all isolated alignment times are exact rationals and can be enumerated without angular sampling. Feed and cutter-band membership are evaluated at those same exact times.

A continuously aligned zero-advance phase interval is not represented by its two endpoints. The isolated-alignment helper fails closed so downstream interval processing must preserve the complete source interval. This prevents a stationary-phase interval with changing feed from being silently under-sampled.

The implementation is checked against the independently produced MC-013 F09 phase-turning oracle, including correlated midpoint, same-phase/wrong-feed, exact start/end and signed-neighbour witnesses.

## Eccentric turning constructor

Eccentric turning retains the finite symbolic placement law

```text
base + R(2*pi*phase(t))*offset
```

with exact rational unwrapped phase tied to the same source time. Cardinal quarter-turn controls can be evaluated exactly in rational Cartesian coordinates. Arbitrary phases stay symbolic or enter the certified analytic route; decimal trigonometry and finite angular sampling are not exact predicate authority.

The constructor is finite because the source history is finite. That does not imply an unconditional exact decision method for every subsequent transcendental equality or membership query.

## Analytic-event boundary

MC-022 preserves the MC-007 fail-closed distinction:

- certified value separation gives `SEPARATED`;
- value uncertainty plus a derivative enclosure separated from zero may certify a `TRANSVERSAL` crossing;
- a leaf where value and derivative can both contain zero remains `TRANSCENDENTAL_EVENT_BLOCKER`.

`PB-007-01` therefore remains **OPEN** for general tangential, multiple-root and singular transcendental event decisions. `PB-007-02` remains **OPEN** for the unconditional general coupled spindle/feed/eccentric sweep-membership route.

Those states are not timeouts or implementation accidents. A blocker may not be converted into empty sweep, no-op, success or removal from the supported-domain denominator.

## Finite-cutter error transfer

MC-058 remains the approximation/enclosure authority. A downstream timed representation must preserve

```text
e_total = e_inherited + e_translation + rho*e_rotation + e_tool
```

where `rho` covers the complete effective cutting region. Error does not reset at a timed-piece boundary, and centreline error is insufficient when cutter extent or orientation error contributes.

## Protected semantics and programme boundary

Historical `research/rcs-*`, source/audio/provenance records, canonical-journal meaning, positive-volume material and durable body/lineage identity are unchanged. The phase/timing parameterization never becomes manufactured-body identity authority.

MC-022 is deterministic research/model evidence, not native geometry qualification. No paid/native campaign ran. `PO-02`, `PO-04`, `PO-05` and `PO-06` remain OPEN. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.

The machine-readable contract is `research/machining-completeness/tasks/MC-022/phase-sensitive-lathe-contract-v1.json`; the bounded executable control is `phase_sensitive_lathe.py`; `verify.py` provides exact, boundary, independent-oracle and adversarial checks.
