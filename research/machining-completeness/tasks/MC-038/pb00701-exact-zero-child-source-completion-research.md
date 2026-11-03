# MC-038 / PB-007-01 — complete original sources with exact child zeros

**Date:** 3 November 2026. **Evidence class:** deterministic exact-arithmetic
model. **Status:** bounded research candidate; distinct review, literal-head CI,
guarded landing and merged-main qualification are recorded separately under
[MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100).

**Source authority:** `e0514500aeca59afa4924dcc2da3ca0c2688d9ac`.
The frozen corpus, historical owner dispositions and prior evidence inventory
are unchanged. This leaf adds three complete source-specific mathematical
witnesses; it does not update the global evidence registry or programme gates.

## Purpose and falsifiable question

The qualified post-v54 inventory supplies one V6 ordered child for each of three
original two-span sources. Their other span and physical knot composition remain
absent from that inventory. The existing transverse interval engine correctly
refuses a zero exactly at a source endpoint or at a rational isolation cut.

Can exact rational-phase point identities, combined with source-bound whole-span
derivative and sign inequalities, establish the complete original zero sets
without changing that engine's contract or treating a local point proof as a
global completeness proof?

The decisive falsifiers are a changed original source/phase, invalid analytic
coefficient identity, derivative margin that is no longer strict, unproved
continuity, wrong exact point/jet, omitted or duplicated physical knot, false
globally smooth multiplicity, missing source interval, or refused/resource-limited
evidence promoted to truth. Each such condition refuses the new witness.

## Exact original cases and results

Every source has original parameter `source-time-t`, interval `[0,2]` and actual
source edges `[0,1,2]`. The complete original IDs are:

- `composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0`
- `composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0`
- `composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0`

| Original owner | Complete physical zero set | Maximal nonzero signs | Exact event semantics |
|---|---|---|---|
| V23 | `{1}` | negative, positive | One physical source-knot zero; left/right analytic orders one; unequal sided derivatives |
| V25 | `{1}` | negative, positive | One physical source-knot zero; left/right analytic orders one; unequal sided derivatives |
| V40 | `{1/2}` | positive, negative | One smooth simple root inside the first original span; true knot at 1 is nonzero |

There are three physical zero events in total, two nonsmooth source-knot events
and one smooth interior event. Both exterior endpoints of every source are
nonzero. No continuum is represented by a finite root list.

The machine witness records full source-specification and whole-row SHA-256,
original parameter/phase, old owner observations and refusal, lowered global
polynomial coefficients, exact point receipts, physical events and maximal sign
cells. The old `CERTIFIED` child observations remain provenance only.

## V23: strict increase across one nonsmooth knot zero

Set `e=1/1000`, `omega=pi/6` and `theta=omega*t`. Exact lowering of the original
B-splines gives, on the first span,

`F=-501/1000 + e*t*cos(2*theta) + (1+e*t)*sin(theta)`.

On `[1,2]`, replace `e*t` and `1+e*t` by their actual constant endpoint values
`e` and `1+e`. Equality of every original harmonic amplitude at the knot proves
continuity; equal signs alone would not suffice.

At `t=1`, both `cos(2*theta)` and `sin(theta)` equal `1/2`, so both source
pieces have exact value zero. On the first span,

`F'=e*cos(2*theta)+e*sin(theta)+omega*((1+e*t)*cos(theta)-2*e*t*sin(2*theta))`.

The first two terms are nonnegative. Across the two actual phase sectors,
`cos(theta)>=1/2`, `|sin(2*theta)|<=1`, and the amplitudes satisfy the stated
nonnegative bounds. The second span has the same trigonometric derivative
terms and no amplitude-derivative terms. Thus on each span,

`F' >= (1/2-2*e)*omega > (1/2-2*e)/2 = 249/1000 > 0`.

The strict last step uses the independently certified rational enclosure
`pi>3`. Strict increase on both continuous pieces and exact zero at 1 establish
negativity before 1, positivity after 1 and the absence of every other zero.

The exact first derivatives at the knot are

- left: `1/1000 + 999*pi*sqrt(3)/12000`;
- right: `999*pi*sqrt(3)/12000`.

Both are positive and unequal. The exact point/jet primitive confirms order one
on each analytic side. The witness counts one physical knot event and explicitly
does not assign one globally smooth analytic multiplicity to the joined source.

## V25: a second exact knot zero with distinct sided derivatives

Set `e=1/1000`, `omega=pi/6`, `theta=omega*(t-1)`. On `[0,1]`, exact lowering gives

`F=-51/1000 + (-1/20+t/10)*cos(theta) + 4*sin(theta) + e*cos(2*theta)`.

On `[1,2]`, the cosine amplitude is the actual constant `1/20`. The other
amplitudes remain constant on both pieces. At the true knot, `theta=0` and
`-51/1000+1/20+1/1000=0` exactly.

On both spans, `cos(theta)>=1/2`, the cosine amplitude has absolute value at
most `1/20`, and `|sin|<=1`. The first span's additional amplitude derivative
contributes the nonnegative term `(1/10)*cos(theta)`. Consequently,

`F' >= omega*(2-1/20-2/1000) = (487/250)*omega > 487/500 > 0`.

The complete source again has only the knot zero and signs negative then
positive. Sided derivatives are `1/10+2*pi/3` and `2*pi/3`; the point/jet
primitive independently checks exact vanishing, positive first derivatives and
unequal jets. A single physical event retains both sided orders.

## V40: an exact interior root at a refused isolation cut

Set `e=1/100000000`, `omega=pi/4`, `theta=pi/8+omega*t`. The actual first span is

`F=A*cos(theta)+B*sin(theta)-e*cos(2*theta)`,

where `A=19/20+t/10` and `B=-21/20+t/10`. At `t=1/2`, `A=1`, `B=-1`, and
`theta=pi/4`. The first harmonic terms cancel exactly, and `cos(2*theta)=0`.
The exact point primitive confirms that this is a zero with first derivative
strictly negative.

On the entire first span, `A>=19/20`, `B<=-19/20`, and sine and cosine are
positive with `cos(theta)+sin(theta)>=1`. Using the certified bounds
`3/4<omega<11/14`,

`F' <= (1/10-19*omega/20)*(cos(theta)+sin(theta))+2*omega*e`

`   < -49/80 + 11/700000000 < 0`.

The coefficient of `cos+sin` must be negative before replacing that sum by its
lower bound; the executable sufficient-condition helper checks this premise.
The zero at `1/2` is therefore the unique first-span zero and is simple.

The second span has actual constant amplitudes `A=21/20`, `B=-19/20` and the
same residual. Its phase interval `[3*pi/8,5*pi/8]` lies in `[pi/3,2*pi/3]`, so
`cos(theta)<=1/2` and `sin(theta)>=sqrt(3)/2>4/5`. The last inequality follows
from the exact rational comparison `3/4>16/25`. Therefore,

`F <= 21/40-19/25+e = -47/200+1/100000000 < 0`.

The true source knot at 1 is continuous and nonzero. The second maximal
negative sign cell crosses that knot; it is not split into an extra event.
The rational cut `1/2` is a physical event because its zero is proved exactly,
not because a subdivision algorithm happened to cut there.

## Implementation, custody and refusal boundaries

The new model pins the complete lowerer dependency chain, including MC-032's
event engine; the rational-phase point and interval primitives; the prior
reconciliation guard and report; frozen corpus/inventory/coverage/auditor; and
programme, domain and current authority. A finite private module graph compiles
each exact bounded buffer after checking its Git blob. Normal project imports
and the event model's dynamic MC-032 import resolve within that graph; stale
bytecode and preloaded project modules are ignored. The point primitive and
its interval dependency share one private runtime identity. Module-local import
and `sys` facades leave global import hooks, `sys.modules` and `sys.path`
unchanged. The verifier also checks a fixed model blob and directly compiles
the same bounded model buffer. Dependency pins are checked again after proof.

The frozen corpus, inventory, coverage, prior report and authority inputs are
decoded from the same bounded buffers whose hashes were verified. The unchanged
auditor receives these checked objects directly; its old file-loading helper is
not used. The prior reconciliation module supplies bounded JSON/canonical and
source-metadata primitives, while this leaf's original-input loader enforces
the same historical, domain and authority obligations using checked buffers.

For these three selected sources, the first actual span starts at zero and
the second has constant amplitudes, so the unchanged lowerer's coordinates
give the original global-parameter polynomials directly. This does not claim
arbitrary nonzero-start polynomial conversion. Every coefficient, harmonic and affine phase is
checked against the exact analytic identity used by the proof. Channel values
are checked at the true source knot before any composition. The original
source and whole-row hashes separately prevent substituting a convenient source
with a similar owner label or point value.

The [rational-phase point primitive](pb00701_rational_phase_point.py) proves
the exact local zeros using root-of-unity field arithmetic and verifies the
first nonzero derivative sign with rational enclosures. Its local evidence is
combined with the new whole-span derivative/sign arguments to establish
completeness. Two exact sided derivative jets are compared before reporting the
nonsmooth knot events. The [interval primitive](pb00701_transverse_trig_interval.py)
independently supplies its certified pi enclosure.

Caller source rows are bounded typed JSON and must equal the pinned original
record byte-canonically before any old rational constructor or B-spline parser
is reached. Caller witness data is also bounded before fresh proof execution.
Floats, custom objects, excessive depth/nodes/bytes, cycles, huge integers,
duplicate keys and boolean/integer aliases cannot become accepted evidence.
The narrow conditional derivative helpers accept already-constructed bounded
`Fraction` values only and refuse a missing sign or strict-margin premise.

The unchanged transverse engine is replayed on each first span with
`max_depth=12,max_nodes=2000`. Its exact-zero refusals are retained as negative
controls, never converted into old-engine success. An unexpected change in
those controls or a producer refusal aborts this witness. No unsupported source
is silently dropped from the historical denominator.

## Validation and reproduction

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_exact_zero_child_source_completion.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_repo.py
python3 tools/validate_machining_completeness.py
```

The new verifier reexecutes the actual source proofs and compares the saved
machine witness with their fresh result. Its 32 adversarial test methods cover
strict-boundary counterexamples to all three derivative helpers, exact source
mutation before legacy parsing, actual knot discontinuity, gaps/overlaps and
phase mismatch, omitted harmonics, point-local versus complete evidence,
sided-order/global-multiplicity confusion, knot double counting, a false spline
knot at the exact cut root, omitted or swapped sources, signs and bounds,
authority promotion, pin drift, producer/resource refusals and bounded JSON.
The runtime dependency checks include the exact transitive lowerer/point module
paths, and retained negative controls must match their precise status and reason.
Six custody regressions additionally exercise the verifier bootstrap and both
ordinary/transitive and dynamic project imports against real accepted stale
bytecode and preloaded modules, checked-buffer execution after path replacement,
same-buffer JSON decoding, exact dependency whitelists, unchanged global import
state, and drift/resource refusal before compilation or unlisted input reads.

For intentional reviewed regeneration:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_exact_zero_child_source_completion.py --write-report
```

The focused workflow uses one bounded Python job and the literal PR head. Its
path filters cover the five owned files and the entire pinned dependency
closure. No native matrix or expensive campaign is added. Exact-head review/CI,
guarded merge, reviewed/synthetic/landed tree equality and independently
successful merged-main checks remain separate acceptance gates.

## Remaining obligations and project implications

These are complete witnesses for three exact original sources. They do not
establish a general terminating analytic isolator, a universal root-event
consumer, arbitrary discontinuous source-knot semantics or capability for
unsupported source families. The old transverse engine and owner routes retain
their existing refusals and contracts. Registration of these new producers and
any current-state count changes belong to a subsequent qualified integration.

Historical V54 remains 121 original sources, 20 route refusals and 30 missing
ordered premises. All PB-007 obligations remain open, MC-B and MC-1 remain
`NOT_ESTABLISHED`, and production remains unauthorized. The 26-operation domain,
source/phase/provenance, canonical journal, material bodies, lineage and
refusal/`UNCERTIFIED` semantics remain unchanged.

MSAC still requires useful machining-led engineering creation and reversible
manufacturing intent. OpenSimachinist still requires native material/topology
realization, reconstruction, complete proof consumption and conventional usable
engineering STEP. These deterministic source proofs make no native or STEP
qualification claim.
