# PB-007-01 v46 report — exact algebraic-irrational endpoints

Evidence class: deterministic model plus scoped mathematical argument. Issue #257.
Reviewed baseline: `e5efc6e441483b2ba594928b84aaa76cc7af1dc3` (v45).

## Result and falsification boundary

The implementation adds an endpoint-only interface for the existing finite
commensurate rational-affine phase grammar. Gelfond–Schneider with base -1,
exponent twice the algebraic irrational phase turn, and logarithm i*pi gives
transcendence of the phase exponential. Exact algebraic-coefficient Laurent
collection then decides equality. Physical multiplicity is the minimum finite
amplitude vanishing order, not the orientation-root multiplicity. Only a proved
nonzero endpoint enters sign refinement using rational Machin, interval Horner,
and Taylor/Lagrange/Lipschitz bounds. Nonvanishing and convergence give finite
termination without making a precision cap or timeout truth authority.

The separate checker regenerates source and field bindings, recomputes every
bound, and audits scalar series/remainders using direct rational summation. It
does not call the sign search to validate a finite certificate. The all-zero
identity and zero-rate/rational-phase predecessor cases are kept separate.

## Verification

Run `python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v46.py --contract --self-test`.
The suite includes mathematical endpoint tests and actual v44/v45 source
integration. It covers near cancellation, exact zero and orders 1–4, unequal
orders across all channels, nonzero scaling, conjugates, both rate directions,
non-unit/global intervals, shared child endpoints, non-event orientation cuts,
forged fields/jets/Laurent/remainders/source metadata, nonexact inputs, resource
refusal, predecessor preservation and frozen coverage. All historical files are
pinned and unchanged; full acceptance requires focused and static GitHub CI.

Local attempt note: the first arithmetic smoke test incorrectly required the
one-term Machin *enclosure upper endpoint* to be less than 22/7. That coarse
bound is wider even though pi itself is less than 22/7. The test now checks the
proved coarse bound (3,4), and the stronger upper bound at n>=2. No series,
remainder, sign acceptance predicate or theorem was changed. The twelve local
core methods then passed with an independent noncommitted rational-polynomial
helper. This is not a substitute for repository integration evidence.

## Preserved obligations and next repair

The genuine v44 source gains a physical endpoint decision while its entire
predecessor whole-span result remains BLOCKED. The endpoint certificates neither
count child interior roots nor prove a child derivative sign. Independent Q(alpha)
bisections remain representations, not an integrated multi-generator partition.
Next: exact whole-closed-child derivative/root authority on algebraic intervals,
then source-bound event/multiplicity composition. Do not retry MC-B from an
endpoint-only result.

PB-007-01 remains OPEN; PB-007-02 remains dependent; PB-007-03 remains OPEN;
PB-007-04 remains OPEN_PROPAGATED; PO-04/05/08 remain OPEN; MC-B and MC-1 remain
NOT_ESTABLISHED. The denominator stays at 26 operations. All protected
source/audio/provenance and downstream semantics remain intact. No native,
paid, production or expensive campaign ran.

Proof, assumptions and primary sources:
`docs/machining-completeness/70-PB00701-ALGEBRAIC-ENDPOINT.md`.
